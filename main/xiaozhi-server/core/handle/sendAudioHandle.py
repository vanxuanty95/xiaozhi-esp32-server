import json
import time
import asyncio
from core.utils import textUtils
from core.utils.util import audio_to_data
from core.providers.tts.dto.dto import SentenceType
from core.utils.audioRateController import AudioRateController

TAG = __name__


async def sendAudioMessage(conn, sentenceType, audios, text):
    if conn.tts.tts_audio_first_sentence:
        conn.logger.bind(tag=TAG).info(f"Sending first segment of speech: {text}")
        conn.tts.tts_audio_first_sentence = False
        await send_tts_message(conn, "start", None)

    if sentenceType == SentenceType.FIRST:
        await send_tts_message(conn, "sentence_start", text)

    await sendAudio(conn, audios)
    # Send sentence start message
    if sentenceType is not SentenceType.MIDDLE:
        conn.logger.bind(tag=TAG).info(f"Sending audio message: {sentenceType}, {text}")

    # Send end message (if it's the last text)
    if sentenceType == SentenceType.LAST:
        await send_tts_message(conn, "stop", None)
        conn.client_is_speaking = False
        if conn.close_after_chat:
            await conn.close()


async def _send_to_mqtt_gateway(conn, opus_packet, timestamp, sequence):
    """
    Send opus data packet with 16-byte header to mqtt_gateway
    Args:
        conn: Connection object
        opus_packet: Opus data packet
        timestamp: Timestamp
        sequence: Sequence number
    """
    # Add 16-byte header to opus data packet
    header = bytearray(16)
    header[0] = 1  # type
    header[2:4] = len(opus_packet).to_bytes(2, "big")  # payload length
    header[4:8] = sequence.to_bytes(4, "big")  # sequence
    header[8:12] = timestamp.to_bytes(4, "big")  # timestamp
    header[12:16] = len(opus_packet).to_bytes(4, "big")  # opus length

    # Send complete packet with header
    complete_packet = bytes(header) + opus_packet
    await conn.websocket.send(complete_packet)


# Play audio - use AudioRateController for precise flow control
async def sendAudio(conn, audios, frame_duration=60):
    """
    Send audio packets, use AudioRateController for precise flow control

    Args:
        conn: Connection object
        audios: Single opus packet (bytes) or opus packet list
        frame_duration: Frame duration (milliseconds), default 60ms

    Improvements:
    1. Use single time base to avoid cumulative errors
    2. Recalculate elapsed_ms each time queue is checked, more precise
    3. Support high concurrency without time deviation
    """
    if audios is None or len(audios) == 0:
        return

    # Get send delay configuration
    send_delay = conn.config.get("tts_audio_send_delay", -1) / 1000.0

    if isinstance(audios, bytes):
        # Single opus packet processing
        await _sendAudio_single(conn, audios, send_delay, frame_duration)
    else:
        # Audio list processing (e.g., file-based audio)
        await _sendAudio_list(conn, audios, send_delay, frame_duration)


async def _sendAudio_single(conn, opus_packet, send_delay, frame_duration=60):
    """
    Send single opus packet
    Use AudioRateController for flow control
    """
    # Reset flow control state, on first read and when session changes
    if not hasattr(conn, "audio_rate_controller") or conn.audio_flow_control.get("sentence_id") != conn.sentence_id:
        if hasattr(conn, "audio_rate_controller"):
            conn.audio_rate_controller.reset()
        else:
            conn.audio_rate_controller = AudioRateController(frame_duration)
            conn.audio_rate_controller.reset()

        conn.audio_flow_control = {
            "packet_count": 0,
            "sequence": 0,
            "sentence_id": conn.sentence_id,
        }

    if conn.client_abort:
        return

    conn.last_activity_time = time.time() * 1000

    rate_controller = conn.audio_rate_controller
    flow_control = conn.audio_flow_control
    packet_count = flow_control["packet_count"]

    # Pre-buffer: first 5 packets sent directly, no delay
    pre_buffer_count = 5

    if packet_count < pre_buffer_count or send_delay > 0:
        # Pre-buffer phase or fixed delay mode, send directly
        await _do_send_audio(conn, opus_packet, flow_control, frame_duration)
        conn.client_is_speaking = True

        if send_delay > 0 and packet_count >= pre_buffer_count:
            await asyncio.sleep(send_delay)
    else:
        # Use flow controller for precise rate control
        rate_controller.add_audio(opus_packet)

        async def send_callback(packet):
            await _do_send_audio(conn, packet, flow_control, frame_duration)

        await rate_controller.check_queue(send_callback)
        conn.client_is_speaking = True

    # Update flow control state
    flow_control["packet_count"] += 1
    flow_control["sequence"] += 1


async def _sendAudio_list(conn, audios, send_delay, frame_duration=60):
    """
    Send audio list (e.g., file-based audio)
    """
    if not audios:
        return

    rate_controller = AudioRateController(frame_duration)
    rate_controller.reset()

    flow_control = {
        "packet_count": 0,
        "sequence": 0,
    }

    # Pre-buffer: first 5 packets sent directly
    pre_buffer_frames = min(5, len(audios))
    for i in range(pre_buffer_frames):
        if conn.client_abort:
            return
        await _do_send_audio(conn, audios[i], flow_control, frame_duration)
        conn.client_is_speaking = True

    remaining_audios = audios[pre_buffer_frames:]

    # Process remaining audio frames
    for i, opus_packet in enumerate(remaining_audios):
        if conn.client_abort:
            break

        conn.last_activity_time = time.time() * 1000

        if send_delay > 0:
            # Fixed delay mode
            await asyncio.sleep(send_delay)
        else:
            # Use flow controller for precise delay
            rate_controller.add_audio(opus_packet)

            async def send_callback(packet):
                await _do_send_audio(conn, packet, flow_control, frame_duration)

            await rate_controller.check_queue(send_callback)
            conn.client_is_speaking = True
            continue

        await _do_send_audio(conn, opus_packet, flow_control, frame_duration)
        conn.client_is_speaking = True


async def _do_send_audio(conn, opus_packet, flow_control, frame_duration=60):
    """
    Execute actual audio sending
    """
    packet_index = flow_control.get("packet_count", 0)
    sequence = flow_control.get("sequence", 0)

    if conn.conn_from_mqtt_gateway:
        # Calculate timestamp (based on playback position)
        start_time = time.time()
        timestamp = int(start_time * 1000) % (2**32)
        await _send_to_mqtt_gateway(conn, opus_packet, timestamp, sequence)
    else:
        # Send opus data packet directly
        await conn.websocket.send(opus_packet)

    # Update flow control state
    flow_control["packet_count"] = packet_index + 1
    flow_control["sequence"] = sequence + 1


async def send_tts_message(conn, state, text=None):
    """Send TTS status message"""
    if text is None and state == "sentence_start":
        return
    message = {"type": "tts", "state": state, "session_id": conn.session_id}
    if text is not None:
        message["text"] = textUtils.check_emoji(text)

    # TTS playback ended
    if state == "stop":
        # Play notification sound
        tts_notify = conn.config.get("enable_stop_tts_notify", False)
        if tts_notify:
            stop_tts_notify_voice = conn.config.get(
                "stop_tts_notify_voice", "config/assets/tts_notify.mp3"
            )
            audios = audio_to_data(stop_tts_notify_voice, is_opus=True)
            await sendAudio(conn, audios)
        # Clear server speaking status
        conn.clearSpeakStatus()

    # Send message to client
    await conn.websocket.send(json.dumps(message))


async def send_stt_message(conn, text):
    """Send STT status message"""
    end_prompt_str = conn.config.get("end_prompt", {}).get("prompt")
    if end_prompt_str and end_prompt_str == text:
        await send_tts_message(conn, "start")
        return

    # Parse JSON format, extract actual user speech content
    display_text = text
    try:
        # Try to parse JSON format
        if text.strip().startswith("{") and text.strip().endswith("}"):
            parsed_data = json.loads(text)
            if isinstance(parsed_data, dict) and "content" in parsed_data:
                # If it's JSON format containing speaker information, only display content part
                display_text = parsed_data["content"]
                # Save speaker information to conn object
                if "speaker" in parsed_data:
                    conn.current_speaker = parsed_data["speaker"]
    except (json.JSONDecodeError, TypeError):
        # If not JSON format, use original text directly
        display_text = text
    stt_text = textUtils.get_string_no_punctuation_or_emoji(display_text)
    await conn.websocket.send(
        json.dumps({"type": "stt", "text": stt_text, "session_id": conn.session_id})
    )
    await send_tts_message(conn, "start")
