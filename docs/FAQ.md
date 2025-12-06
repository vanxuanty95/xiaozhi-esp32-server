# Common Issues ❓

### 1. Why does Xiaozhi recognize many Korean, Japanese, and English words when I speak? 🇰🇷

Suggestion: Check if `models/SenseVoiceSmall` already has the `model.pt`
file. If not, you need to download it. See here [Download Speech Recognition Model Files](Deployment.md#model-files)

### 2. Why does "TTS task error file does not exist" appear? 📁

Suggestion: Check if you have correctly installed the `libopus` and `ffmpeg` libraries using `conda`.

If not installed, install them

```
conda install conda-forge::libopus
conda install conda-forge::ffmpeg
```

### 3. TTS Often Fails, Often Times Out ⏰

Suggestion: If `EdgeTTS` often fails, please first check if you are using a proxy (VPN). If you are, please try closing the proxy and try again;  
If you are using Volcano Engine's Doubao TTS, when it often fails, it is recommended to use the paid version, because the test version only supports 2 concurrent connections.

### 4. Can Connect to Self-Built Server Using Wifi, but 4G Mode Cannot Connect 🔐

Reason: Brother Xia's firmware requires secure connection in 4G mode.

Solution: Currently there are two methods to solve this. Choose one:

1. Modify code. Refer to this video to solve https://www.bilibili.com/video/BV18MfTYoE85

2. Use nginx to configure SSL certificate. Refer to tutorial https://icnt94i5ctj4.feishu.cn/docx/GnYOdMNJOoRCljx1ctecsj9cnRe

### 5. How to Improve Xiaozhi Conversation Response Speed? ⚡

This project's default configuration is a low-cost solution. It is recommended for beginners to first use the default free models to solve the "can run" problem, then optimize "run fast".  
If you need to improve response speed, you can try replacing various components. Since version `0.5.2`, the project supports streaming configuration. Compared to earlier versions, response speed has improved by about `2.5 seconds`, significantly improving user experience.

| Module Name | Beginner All-Free Setup | Streaming Configuration |
|:---:|:---:|:---:|
| ASR(Speech Recognition) | FunASR(Local) | 👍FunASR(Local GPU Mode) |
| LLM(Large Model) | ChatGLMLLM(Zhipu glm-4-flash) | 👍AliLLM(qwen3-235b-a22b-instruct-2507) or 👍DoubaoLLM(doubao-1-5-pro-32k-250115) |
| VLLM(Vision Large Model) | ChatGLMVLLM(Zhipu glm-4v-flash) | 👍QwenVLVLLM(Qwen qwen2.5-vl-3b-instructh) |
| TTS(Speech Synthesis) | ✅LinkeraiTTS(Lingxi Streaming) | 👍HuoshanDoubleStreamTTS(Volcano Double Streaming Speech Synthesis) or 👍AliyunStreamTTS(Alibaba Cloud Streaming Speech Synthesis) |
| Intent(Intent Recognition) | function_call(Function Call) | function_call(Function Call) |
| Memory(Memory Function) | mem_local_short(Local Short-term Memory) | mem_local_short(Local Short-term Memory) |

If you care about the time consumption of each component, please check [Xiaozhi Component Performance Test Report](https://github.com/xinnan-tech/xiaozhi-performance-research). You can actually test in your environment according to the test methods in the report.

### 6. I Speak Very Slowly, and Xiaozhi Always Interrupts During Pauses 🗣️

Suggestion: In the configuration file, find the following part and increase the value of `min_silence_duration_ms` (for example, change it to `1000`):

```yaml
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700  # If speech pauses are long, you can increase this value
```

### 7. Deployment Related Tutorials
1. [How to Perform Most Simplified Deployment](./Deployment.md)<br/>
2. [How to Perform All Modules Deployment](./Deployment_all.md)<br/>
3. [How to Deploy MQTT Gateway to Enable MQTT+UDP Protocol](./mqtt-gateway-integration.md)<br/>
4. [How to Automatically Pull Latest Code of This Project and Automatically Compile and Start](./dev-ops-integration.md)<br/>
5. [How to Integrate with Nginx](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)<br/>

### 9. Firmware Compilation Related Tutorials
1. [How to Compile Xiaozhi Firmware Yourself](./firmware-build.md)<br/>
2. [How to Modify OTA Address Based on Firmware Compiled by Brother Xia](./firmware-setting.md)<br/>

### 10. Extension Related Tutorials
1. [How to Enable Mobile Number Registration for Management Console](./ali-sms-integration.md)<br/>
2. [How to Integrate HomeAssistant to Achieve Smart Home Control](./homeassistant-integration.md)<br/>
3. [How to Enable Vision Model to Achieve Photo Recognition](./mcp-vision-integration.md)<br/>
4. [How to Deploy MCP Access Point](./mcp-endpoint-enable.md)<br/>
5. [How to Connect to MCP Access Point](./mcp-endpoint-integration.md)<br/>
6. [How to Get Device Information Using MCP Method](./mcp-get-device-info.md)<br/>
7. [How to Enable Voiceprint Recognition](./voiceprint-integration.md)<br/>
8. [News Plugin Source Configuration Guide](./newsnow_plugin_config.md)<br/>
9. [Knowledge Base RAGFlow Integration Guide](./ragflow-integration.md)<br/>
10. [How to Deploy Context Provider](./context-provider-integration.md)<br/>

### 11. Voice Cloning, Local Voice Deployment Related Tutorials
1. [How to Clone Voice in Management Console](./huoshan-streamTTS-voice-cloning.md)<br/>
2. [How to Deploy and Integrate index-tts Local Voice](./index-stream-integration.md)<br/>
3. [How to Deploy and Integrate fish-speech Local Voice](./fish-speech-integration.md)<br/>
4. [How to Deploy and Integrate PaddleSpeech Local Voice](./paddlespeech-deploy.md)<br/>

### 12. Performance Testing Tutorials
1. [Component Speed Testing Guide](./performance_tester.md)<br/>
2. [Regular Public Test Results](https://github.com/xinnan-tech/xiaozhi-performance-research)<br/>

### 13. For More Issues, You Can Contact Us for Feedback 💬

You can submit your issues in [issues](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues).
