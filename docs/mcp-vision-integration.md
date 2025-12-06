# Vision Model Usage Guide
This tutorial is divided into two parts:
- Part 1: Run xiaozhi-server in single module mode to enable vision model
- Part 2: How to enable vision model when running all modules

Before enabling the vision model, you need to prepare three things:
- You need to prepare a device with a camera, and this device has already implemented camera calling functionality in Brother Xia's repository. For example, `Lichuang·Practical ESP32-S3 Development Board`
- Your device firmware version is upgraded to 1.6.6 or above
- You have successfully run the basic conversation module

## Run xiaozhi-server in Single Module Mode to Enable Vision Model

### Step 1: Confirm Network
Since the vision model will start port 8003 by default.

If you are running with docker, please confirm whether your `docker-compose.yml` has port `8003` exposed. If not, update to the latest `docker-compose.yml` file

If you are running from source code, confirm whether the firewall allows port `8003`

### Step 2: Select Your Vision Model
Open your `data/.config.yaml` file, set your `selected_module.VLLM` to a vision model. Currently we support vision models with `openai` type interfaces. `ChatGLMVLLM` is one of the models compatible with `openai`.

```
selected_module:
  VAD: ..
  ASR: ..
  LLM: ..
  VLLM: ChatGLMVLLM
  TTS: ..
  Memory: ..
  Intent: ..
```

Assuming we use `ChatGLMVLLM` as the vision model, we need to first log in to the [Zhipu AI](https://bigmodel.cn/usercenter/proj-mgmt/apikeys) website to apply for a key. If you have already applied for a key before, you can reuse this key.

Add this configuration in your configuration file. If you already have this configuration, set your api_key.

```
VLLM:
  ChatGLMVLLM:
    api_key: your api_key
```

### Step 3: Start xiaozhi-server Service
If you are using source code, enter the command to start
```
python app.py
```
If you are running with docker, restart the container
```
docker restart xiaozhi-esp32-server
```

After startup, it will output logs with the following content.

```
2025-06-01 **** - OTA interface is           http://192.168.4.7:8003/xiaozhi/ota/
2025-06-01 **** - Vision analysis interface is        http://192.168.4.7:8003/mcp/vision/explain
2025-06-01 **** - Websocket address is       ws://192.168.4.7:8000/xiaozhi/v1/
2025-06-01 **** - =======The above address is a websocket protocol address, please do not access it with a browser=======
2025-06-01 **** - If you want to test websocket, please open test_page.html in the test directory with Google Chrome
2025-06-01 **** - =============================================================
```

After startup, use a browser to open the `Vision Analysis Interface` link in the log. See what it outputs? If you are on Linux and don't have a browser, you can execute this command:
```
curl -i your vision analysis interface
```

Normally it will display like this
```
MCP Vision interface is running normally, vision explanation interface address is: http://xxxx:8003/mcp/vision/explain
```

Please note that if you are deploying on a public network or with docker, you must modify this configuration in your `data/.config.yaml`
```
server:
  vision_explain: http://your ip or domain:port/mcp/vision/explain
```

Why? Because the vision explanation interface needs to be distributed to the device. If your address is a LAN address or a docker internal address, the device cannot access it.

Assuming your public network address is `111.111.111.111`, then `vision_explain` should be configured like this

```
server:
  vision_explain: http://111.111.111.111:8003/mcp/vision/explain
```

If your MCP Vision interface is running normally, and you have also tried to access the distributed `Vision Explanation Interface Address` normally with a browser, please continue to the next step

### Step 4: Device Wake Up and Enable

Say to the device "Please open the camera and tell me what you see"

Pay attention to the xiaozhi-server log output to see if there are any errors.


## How to Enable Vision Model When Running All Modules

### Step 1: Confirm Network
Since the vision model will start port 8003 by default.

If you are running with docker, please confirm whether your `docker-compose_all.yml` has mapped port `8003`. If not, update to the latest `docker-compose_all.yml` file

If you are running from source code, confirm whether the firewall allows port `8003`

### Step 2: Confirm Your Configuration File

Open your `data/.config.yaml` file and confirm whether the structure of your configuration file is the same as `data/config_from_api.yaml`. If it's different or missing something, please add it.

### Step 3: Configure Vision Model Key

We need to first log in to the [Zhipu AI](https://bigmodel.cn/usercenter/proj-mgmt/apikeys) website to apply for a key. If you have already applied for a key before, you can reuse this key.

Log in to the `Management Console`, click `Model Configuration` in the top menu, click `Vision Large Language Model` in the left sidebar, find `VLLM_ChatGLMVLLM`, click the edit button, in the dialog box, enter your key in `API Key`, click save.

After saving successfully, go to the agent you want to test, click `Configure Role`, in the opened content, check whether `Vision Large Language Model (VLLM)` has selected the vision model just now. Click save.

### Step 3: Start xiaozhi-server Module
If you are using source code, enter the command to start
```
python app.py
```
If you are running with docker, restart the container
```
docker restart xiaozhi-esp32-server
```

After startup, it will output logs with the following content.

```
2025-06-01 **** - Vision analysis interface is        http://192.168.4.7:8003/mcp/vision/explain
2025-06-01 **** - Websocket address is       ws://192.168.4.7:8000/xiaozhi/v1/
2025-06-01 **** - =======The above address is a websocket protocol address, please do not access it with a browser=======
2025-06-01 **** - If you want to test websocket, please open test_page.html in the test directory with Google Chrome
2025-06-01 **** - =============================================================
```

After startup, use a browser to open the `Vision Analysis Interface` link in the log. See what it outputs? If you are on Linux and don't have a browser, you can execute this command:
```
curl -i your vision analysis interface
```

Normally it will display like this
```
MCP Vision interface is running normally, vision explanation interface address is: http://xxxx:8003/mcp/vision/explain
```

Please note that if you are deploying on a public network or with docker, you must modify this configuration in your `data/.config.yaml`
```
server:
  vision_explain: http://your ip or domain:port/mcp/vision/explain
```

Why? Because the vision explanation interface needs to be distributed to the device. If your address is a LAN address or a docker internal address, the device cannot access it.

Assuming your public network address is `111.111.111.111`, then `vision_explain` should be configured like this

```
server:
  vision_explain: http://111.111.111.111:8003/mcp/vision/explain
```

If your MCP Vision interface is running normally, and you have also tried to access the distributed `Vision Explanation Interface Address` normally with a browser, please continue to the next step

### Step 4: Device Wake Up and Enable

Say to the device "Please open the camera and tell me what you see"

Pay attention to the xiaozhi-server log output to see if there are any errors.
