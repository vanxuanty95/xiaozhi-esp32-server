import json
import hmac
import base64
import hashlib
import asyncio
import websockets
import opuslib_next
import gc
from time import mktime
from datetime import datetime
from urllib.parse import urlencode
from typing import List
from config.logger import setup_logging
from wsgiref.handlers import format_date_time
from core.providers.asr.base import ASRProviderBase
from core.providers.asr.dto.dto import InterfaceType

TAG = __name__
logger = setup_logging()

# Frame status constants
STATUS_FIRST_FRAME = 0  # First frame identifier
STATUS_CONTINUE_FRAME = 1  # Middle frame identifier
STATUS_LAST_FRAME = 2  # Last frame identifier


class ASRProvider(ASRProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__()
        self.interface_type = InterfaceType.STREAM
        self.config = config
        self.text = ""
        self.decoder = opuslib_next.Decoder(16000, 1)
        self.asr_ws = None
        self.forward_task = None
        self.is_processing = False
        self.server_ready = False
        self.last_frame_sent = False  # Mark whether final frame has been sent
        self.best_text = ""  # Save best recognition result
        self.has_final_result = False  # Mark whether final recognition result has been received

        # Xunfei configuration
        self.app_id = config.get("app_id")
        self.api_key = config.get("api_key")
        self.api_secret = config.get("api_secret")

        if not all([self.app_id, self.api_key, self.api_secret]):
            raise ValueError("Must provide app_id, api_key and api_secret")

        # Recognition parameters
        self.iat_params = {
            "domain": config.get("domain", "slm"),
            "language": config.get("language", "zh_cn"),
            "accent": config.get("accent", "mandarin"),
            "dwa": config.get("dwa", "wpgs"),
            "result": {"encoding": "utf8", "compress": "raw", "format": "plain"},
        }

        self.output_dir = config.get("output_dir", "tmp/")
        self.delete_audio_file = delete_audio_file

    def create_url(self) -> str:
        """Generate authentication URL"""
        url = "ws://iat.cn-huabei-1.xf-yun.com/v1"
        # Generate RFC1123 format timestamp
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # Concatenate string
        signature_origin = "host: " + "iat.cn-huabei-1.xf-yun.com" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v1 " + "HTTP/1.1"

        # Perform hmac-sha256 encryption
        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding="utf-8")

        authorization_origin = (
            'api_key="%s", algorithm="%s", headers="%s", signature="%s"'
            % (self.api_key, "hmac-sha256", "host date request-line", signature_sha)
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
            encoding="utf-8"
        )

        # Combine authentication parameters into dictionary
        v = {
            "authorization": authorization,
            "date": date,
            "host": "iat.cn-huabei-1.xf-yun.com",
        }

        # Concatenate authentication parameters, generate url
        url = url + "?" + urlencode(v)
        return url

    async def open_audio_channels(self, conn):
        await super().open_audio_channels(conn)

    async def receive_audio(self, conn, audio, audio_have_voice):
        # Call parent method first to handle basic logic
        await super().receive_audio(conn, audio, audio_have_voice)

        # Store audio data for voiceprint recognition
        if not hasattr(conn, "asr_audio_for_voiceprint"):
            conn.asr_audio_for_voiceprint = []
        conn.asr_audio_for_voiceprint.append(audio)

        # If there's voice this time, and connection hasn't been established before
        if audio_have_voice and self.asr_ws is None and not self.is_processing:
            try:
                await self._start_recognition(conn)
            except Exception as e:
                logger.bind(tag=TAG).error(f"Failed to establish ASR connection: {str(e)}")
                await self._cleanup(conn)
                return

        # Send current audio data
        if self.asr_ws and self.is_processing and self.server_ready:
            try:
                pcm_frame = self.decoder.decode(audio, 960)
                await self._send_audio_frame(pcm_frame, STATUS_CONTINUE_FRAME)
            except Exception as e:
                logger.bind(tag=TAG).warning(f"Error occurred while sending audio data: {e}")
                await self._cleanup(conn)

    async def _start_recognition(self, conn):
        """Start recognition session"""
        try:
            self.is_processing = True
            # Establish WebSocket connection
            ws_url = self.create_url()
            logger.bind(tag=TAG).info(f"Connecting to ASR service: {ws_url[:50]}...")

            self.asr_ws = await websockets.connect(
                ws_url,
                max_size=1000000000,
                ping_interval=None,
                ping_timeout=None,
                close_timeout=10,
            )

            logger.bind(tag=TAG).info("ASR WebSocket connection established")
            self.server_ready = False
            self.last_frame_sent = False
            self.best_text = ""
            self.forward_task = asyncio.create_task(self._forward_results(conn))

            # Send first frame audio
            if conn.asr_audio and len(conn.asr_audio) > 0:
                first_audio = conn.asr_audio[-1] if conn.asr_audio else b""
                pcm_frame = (
                    self.decoder.decode(first_audio, 960) if first_audio else b""
                )
                await self._send_audio_frame(pcm_frame, STATUS_FIRST_FRAME)
                self.server_ready = True
                logger.bind(tag=TAG).info("First frame sent, starting recognition")

                # Send cached audio data
                for cached_audio in conn.asr_audio[-10:]:
                    try:
                        pcm_frame = self.decoder.decode(cached_audio, 960)
                        await self._send_audio_frame(pcm_frame, STATUS_CONTINUE_FRAME)
                    except Exception as e:
                        logger.bind(tag=TAG).info(f"Error occurred while sending cached audio data: {e}")
                        break

        except Exception as e:
            logger.bind(tag=TAG).error(f"Failed to establish ASR connection: {str(e)}")
            if hasattr(e, "__cause__") and e.__cause__:
                logger.bind(tag=TAG).error(f"Error reason: {str(e.__cause__)}")
            if self.asr_ws:
                await self.asr_ws.close()
                self.asr_ws = None
            self.is_processing = False
            raise

    async def _send_audio_frame(self, audio_data: bytes, status: int):
        """Send audio frame"""
        if not self.asr_ws:
            return

        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        frame_data = {
            "header": {"status": status, "app_id": self.app_id},
            "parameter": {"iat": self.iat_params},
            "payload": {
                "audio": {"audio": audio_b64, "sample_rate": 16000, "encoding": "raw"}
            },
        }

        await self.asr_ws.send(json.dumps(frame_data, ensure_ascii=False))

        # Mark whether final frame has been sent
        if status == STATUS_LAST_FRAME:
            self.last_frame_sent = True
            logger.bind(tag=TAG).info("Final frame marked as sent")

    async def _forward_results(self, conn):
        """Forward recognition results"""
        try:
            while self.asr_ws and not conn.stop_event.is_set():
                # Get current connection audio data
                audio_data = getattr(conn, "asr_audio_for_voiceprint", [])
                try:
                    # If final frame has been sent, increase timeout to wait for complete result
                    timeout = 3.0 if self.last_frame_sent else 30.0
                    response = await asyncio.wait_for(
                        self.asr_ws.recv(), timeout=timeout
                    )
                    result = json.loads(response)
                    logger.bind(tag=TAG).debug(f"Received ASR result: {result}")

                    header = result.get("header", {})
                    payload = result.get("payload", {})
                    code = header.get("code", 0)
                    status = header.get("status", 0)

                    if code != 0:
                        logger.bind(tag=TAG).error(
                            f"Recognition error, error code: {code}, message: {header.get('message', '')}"
                        )
                        if code in [10114, 10160]:  # Connection issue
                            break
                        continue

                    # Process recognition result
                    if payload and "result" in payload:
                        text_data = payload["result"]["text"]
                        if text_data:
                            # Decode base64 text
                            decoded_text = base64.b64decode(text_data).decode("utf-8")
                            text_json = json.loads(decoded_text)

                            # Extract text content
                            text_ws = text_json.get("ws", [])
                            result_text = ""
                            for i in text_ws:
                                for j in i.get("cw", []):
                                    w = j.get("w", "")
                                    result_text += w

                            # Update recognition text - real-time update strategy
                            # Only check if empty string, no longer filter any punctuation
                            # This ensures all recognized content, including punctuation, can be updated in real-time
                            if result_text and result_text.strip():
                                # Real-time update: normally update all, improve response speed
                                should_update = True

                                # Save best text
                                # 1. If recognition completed status or result received after final frame, save with priority
                                # 2. Otherwise save longest meaningful text
                                # Cancel filtering of punctuation, only check if empty
                                # This preserves all recognized content, including various punctuation marks
                                is_valid_text = len(result_text.strip()) > 0

                                if (
                                    self.last_frame_sent or status == 2
                                ) and is_valid_text:
                                    self.best_text = result_text
                                    self.has_final_result = True  # Mark final result received
                                    logger.bind(tag=TAG).debug(
                                        f"Saved final recognition result: {self.best_text}"
                                    )
                                elif (
                                    len(result_text) > len(self.best_text)
                                    and is_valid_text
                                    and not self.has_final_result
                                ):
                                    self.best_text = result_text
                                    logger.bind(tag=TAG).debug(
                                        f"Saved intermediate best text: {self.best_text}"
                                    )

                                # If final frame has been sent, only filter empty text
                                if self.last_frame_sent:
                                    # Only reject completely empty results
                                    if not result_text.strip():
                                        should_update = False
                                        logger.bind(tag=TAG).warning(
                                            f"Rejected empty text after final frame"
                                        )

                                if should_update:
                                    # Process streaming recognition results, avoid simple replacement causing content loss
                                    # 1. If in intermediate state (not after final frame), may need to replace with more complete recognition
                                    # 2. If result received after final frame, may be supplement to previous text
                                    if self.last_frame_sent:
                                        # Results received after final frame may be supplementary content like punctuation
                                        # Check if text needs to be merged instead of replaced
                                        # If current text is pure punctuation and there's already content before, should append instead of replace
                                        if len(
                                            self.text
                                        ) > 0 and result_text.strip() in [
                                            "。",
                                            ".",
                                            "?",
                                            "？",
                                            "!",
                                            "！",
                                            ",",
                                            "，",
                                            ";",
                                            "；",
                                        ]:
                                            # For punctuation, append to existing text
                                            self.text = (
                                                self.text.rstrip().rstrip("。.")
                                                + result_text
                                            )
                                        else:
                                            # Other cases maintain replacement logic
                                            self.text = result_text
                                    else:
                                        # Intermediate state replace with new recognition result
                                        self.text = result_text

                                    logger.bind(tag=TAG).info(
                                        f"Real-time update recognition text: {self.text} (Final frame sent: {self.last_frame_sent})"
                                    )

                    # Recognition completed, but if final frame hasn't been sent, continue waiting
                    if status == 2:
                        logger.bind(tag=TAG).info(
                            f"Recognition completion status reached, current recognition text: {self.text}"
                        )

                        # If final frame hasn't been sent, continue waiting
                        if not self.last_frame_sent:
                            logger.bind(tag=TAG).info(
                                "Recognition completed but final frame not sent, continuing to wait..."
                            )
                            continue

                        # Final frame sent and completion status received, use best strategy to select final result
                        # Prioritize using latest result in recognition completion status, not just based on length
                        if self.best_text:
                            # If current text was received after final frame sent or in recognition completion status, use with priority
                            if (
                                self.last_frame_sent or status == 2
                            ) and self.text.strip():
                                logger.bind(tag=TAG).info(
                                    f"Using latest recognition result in completion status: {self.text}"
                                )
                            elif len(self.best_text) > len(self.text):
                                logger.bind(tag=TAG).info(
                                    f"Using longer best text as final result: {self.text} -> {self.best_text}"
                                )
                                self.text = self.best_text

                        logger.bind(tag=TAG).info(f"Got final complete text: {self.text}")
                        conn.reset_vad_states()
                        if len(audio_data) > 15:  # Ensure sufficient audio data
                            # Prepare to process result
                            pass
                        break

                except asyncio.TimeoutError:
                    if self.last_frame_sent:
                        # Use best text on timeout as well
                        if self.best_text and len(self.best_text) > len(self.text):
                            logger.bind(tag=TAG).info(
                                f"Timeout, using best text: {self.text} -> {self.best_text}"
                            )
                            self.text = self.best_text
                        logger.bind(tag=TAG).info(
                            f"Timeout after final frame, using result: {self.text}"
                        )
                        break
                    # If final frame hasn't been sent, continue waiting
                    continue
                except websockets.ConnectionClosed:
                    logger.bind(tag=TAG).info("ASR service connection closed")
                    self.is_processing = False
                    break
                except Exception as e:
                    logger.bind(tag=TAG).error(f"Error occurred while processing ASR result: {str(e)}")
                    if hasattr(e, "__cause__") and e.__cause__:
                        logger.bind(tag=TAG).error(f"Error reason: {str(e.__cause__)}")
                    self.is_processing = False
                    break

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error occurred in ASR result forwarding task: {str(e)}")
            if hasattr(e, "__cause__") and e.__cause__:
                logger.bind(tag=TAG).error(f"Error reason: {str(e.__cause__)}")
        finally:
            if self.asr_ws:
                await self.asr_ws.close()
                self.asr_ws = None
            self.is_processing = False
            if conn:
                if hasattr(conn, "asr_audio_for_voiceprint"):
                    conn.asr_audio_for_voiceprint = []
                if hasattr(conn, "asr_audio"):
                    conn.asr_audio = []
                if hasattr(conn, "has_valid_voice"):
                    conn.has_valid_voice = False

    async def handle_voice_stop(self, conn, asr_audio_task: List[bytes]):
        """Handle voice stop, send last frame and process recognition result"""
        try:
            # Send last frame first to indicate audio end
            if self.asr_ws and self.is_processing:
                try:
                    # Take last valid audio frame as last frame data
                    last_frame = b""
                    if asr_audio_task:
                        last_audio = asr_audio_task[-1]
                        last_frame = self.decoder.decode(last_audio, 960)
                    await self._send_audio_frame(last_frame, STATUS_LAST_FRAME)
                    logger.bind(tag=TAG).info("Last frame sent")

                    # After sending final frame, give _forward_results appropriate time to process final result
                    await asyncio.sleep(0.25)

                    logger.bind(tag=TAG).info(f"Preparing to process final recognition result: {self.text}")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"Failed to send last frame: {e}")

            # Call parent class handle_voice_stop method to process recognition result
            await super().handle_voice_stop(conn, asr_audio_task)
        except Exception as e:
            logger.bind(tag=TAG).error(f"Failed to handle voice stop: {e}")
            import traceback

            logger.bind(tag=TAG).debug(f"Exception details: {traceback.format_exc()}")

    def stop_ws_connection(self):
        if self.asr_ws:
            asyncio.create_task(self.asr_ws.close())
            self.asr_ws = None
        self.is_processing = False

    async def _cleanup(self, conn):
        """Clean up resources"""
        logger.bind(tag=TAG).info(
            f"Starting ASR session cleanup | Current state: processing={self.is_processing}, server_ready={self.server_ready}"
        )

        # Send last frame
        if self.asr_ws and self.is_processing:
            try:
                await self._send_audio_frame(b"", STATUS_LAST_FRAME)
                await asyncio.sleep(0.1)
                logger.bind(tag=TAG).info("Last frame sent")
            except Exception as e:
                logger.bind(tag=TAG).error(f"Failed to send last frame: {e}")

        # State reset
        self.is_processing = False
        self.server_ready = False
        self.last_frame_sent = False
        self.best_text = ""
        self.has_final_result = False
        logger.bind(tag=TAG).info("ASR state reset")

        # Clean up task
        if self.forward_task and not self.forward_task.done():
            self.forward_task.cancel()
            try:
                await asyncio.wait_for(self.forward_task, timeout=1.0)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.bind(tag=TAG).debug(f"forward_task cancellation exception: {e}")
            finally:
                self.forward_task = None

        # Close connection
        if self.asr_ws:
            try:
                logger.bind(tag=TAG).debug("Closing WebSocket connection")
                await asyncio.wait_for(self.asr_ws.close(), timeout=2.0)
                logger.bind(tag=TAG).debug("WebSocket connection closed")
            except Exception as e:
                logger.bind(tag=TAG).error(f"Failed to close WebSocket connection: {e}")
            finally:
                self.asr_ws = None

        # Clean up connection audio cache
        if conn:
            if hasattr(conn, "asr_audio_for_voiceprint"):
                conn.asr_audio_for_voiceprint = []
            if hasattr(conn, "asr_audio"):
                conn.asr_audio = []
            if hasattr(conn, "has_valid_voice"):
                conn.has_valid_voice = False

        logger.bind(tag=TAG).info("ASR session cleanup completed")

    async def speech_to_text(self, opus_data, session_id, audio_format):
        """Get recognition result"""
        result = self.text
        self.text = ""
        return result, None

    async def close(self):
        """Resource cleanup method"""
        if self.asr_ws:
            await self.asr_ws.close()
            self.asr_ws = None
        if self.forward_task:
            self.forward_task.cancel()
            try:
                await self.forward_task
            except asyncio.CancelledError:
                pass
            self.forward_task = None
        self.is_processing = False
        
        # Explicitly release decoder resources
        if hasattr(self, 'decoder') and self.decoder is not None:
            try:
                del self.decoder
                self.decoder = None
                logger.bind(tag=TAG).debug("Xunfei decoder resources released")
            except Exception as e:
                logger.bind(tag=TAG).debug(f"Error releasing Xunfei decoder resources: {e}")

        # Clean up audio buffers for all connections
        if hasattr(self, "_connections"):
            for conn in self._connections.values():
                if hasattr(conn, "asr_audio_for_voiceprint"):
                    conn.asr_audio_for_voiceprint = []
                if hasattr(conn, "asr_audio"):
                    conn.asr_audio = []
                if hasattr(conn, "has_valid_voice"):
                    conn.has_valid_voice = False
