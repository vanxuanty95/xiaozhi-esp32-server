# Xiaozhi ESP32 - Open Source Server and HomeAssistant Integration Guide

[TOC]

-----

## Introduction

This document will guide you on how to integrate ESP32 devices with HomeAssistant.

## Prerequisites

- `HomeAssistant` has been installed and configured
- The model I chose this time is: free ChatGLM, which supports functioncall function calls

## Operations Before Starting (Required)

### 1. Get HA Network Address Information

Please visit your Home Assistant network address. For example, if my HA address is 192.168.4.7 and the port is the default 8123, open in browser

```
http://192.168.4.7:8123
```

> Manual method to query HA IP address**（Only when xiaozhi-esp32-server and HA are deployed on the same network device [e.g., same wifi]）**:
>
> 1. Enter Home Assistant (frontend).
>
> 2. Click **Settings** in the lower left corner → **System** → **Network**.
>
> 3. Scroll to the bottom `Home Assistant Website` area, in `Local Network`, click the `eye` button to see the currently used IP address (such as `192.168.1.10`) and network interface. Click `Copy Link` to copy directly.
>
>    ![image-20250504051716417](images/image-ha-integration-01.png)

Or, if you have already set up a directly accessible Home Assistant OAuth address, you can also directly access it in the browser

```
http://homeassistant.local:8123
```

### 2. Log in to `Home Assistant` to Get Development Key

Log in to `HomeAssistant`, click `Lower left corner avatar -> Personal`, switch to the `Security` navigation bar, scroll to the bottom `Long-lived Access Tokens` to generate api_key, and copy and save it. All subsequent methods need to use this api key and it only appears once (tip: You can save the generated QR code image, and you can scan the QR code later to extract the api key again).

## Method 1: Xiaozhi Community Co-built HA Call Function

### Function Description

- If you need to add new devices later, this method requires manually restarting the `xiaozhi-esp32-server server` to update device information**（Important**).

- You need to ensure that `Xiaomi Home` has been integrated in HomeAssistant and that Xiaomi devices have been imported into `HomeAssistant`.

- You need to ensure that the `xiaozhi-esp32-server Management Console` can be used normally.

- My `xiaozhi-esp32-server Management Console` and `HomeAssistant` are deployed on the same machine on another port, version is `0.3.10`

  ```
  http://192.168.4.7:8002
  ```


### Configuration Steps

#### 1. Log in to `HomeAssistant` to Organize Device List to Control

Log in to `HomeAssistant`, click `Settings in the lower left corner`, then enter `Devices & Services`, then click `Entities` at the top.

Then search for switches you want to control in entities. After results appear, click one of the results in the list, and a switch interface will appear.

In the switch interface, we try clicking the switch to see if it will turn on/off with our clicks. If it can be operated, it means it's normally connected.

Then find the settings button on the switch panel, click it, and you can view the `Entity Identifier` of this switch.

We open a notepad and organize a piece of data in this format:

Location + English comma + Device name + English comma + `Entity Identifier` + English semicolon

For example, I'm at the company, I have a toy light, its identifier is switch.cuco_cn_460494544_cp1_on_p_2_1, then write this piece of data like this

```
Company,Toy Light,switch.cuco_cn_460494544_cp1_on_p_2_1;
```

Of course, in the end I may need to operate two lights, my final result is:

```
Company,Toy Light,switch.cuco_cn_460494544_cp1_on_p_2_1;
Company,Desk Lamp,switch.iot_cn_831898993_socn1_on_p_2_1;
```

This string of characters, we call it "Device List String" and need to save it well, it will be useful later.

#### 2. Log in to `Management Console`

![image-20250504051716417](images/image-ha-integration-06.png)

Use administrator account to log in to `Management Console`. In `Agent Management`, find your agent, then click `Configure Role`.

Set intent recognition to `External LLM Intent Recognition` or `LLM Autonomous Function Call`. At this time, you will see an `Edit Functions` button on the right. Click the `Edit Functions` button, and a `Function Management` dialog will pop up.

In the `Function Management` dialog, you need to check `HomeAssistant Device Status Query` and `HomeAssistant Device Status Modification`.

After checking, click `HomeAssistant Device Status Query` in `Selected Functions`, then configure your `HomeAssistant` address, key, and device list string in `Parameter Configuration`.

After editing, click `Save Configuration`, at this time the `Function Management` dialog will be hidden, then click save agent configuration again.

After saving successfully, you can wake up the device to operate.

#### 3. Wake Up Device to Control

Try saying to esp32, "Turn on XXX light"

## Method 2: Xiaozhi Uses Home Assistant's Voice Assistant as LLM Tool

### Function Description

- This method has a relatively serious disadvantage - **This method cannot use the function_call plugin capabilities of the Xiaozhi open source ecosystem**, because using Home Assistant as Xiaozhi's LLM tool will transfer intent recognition capability to Home Assistant. But **this method can experience native Home Assistant operation functions, and Xiaozhi's chat capability remains unchanged**. If you really mind, you can use [Method 3](##Method 3: Use Home Assistant's MCP Service (Recommended)) which is also supported by Home Assistant, which can maximize the experience of Home Assistant functions.

### Configuration Steps:

#### 1. Configure Home Assistant's LLM Voice Assistant.

**You need to configure Home Assistant's voice assistant or LLM tool in advance.**

#### 2. Get Home Assistant's Voice Assistant Agent ID.

1. Enter the Home Assistant page. Click `Developer Tools` on the left.
2. In the opened `Developer Tools`, click the `Actions` tab (as shown in operation 1), in the `Actions` option bar on the page, find or enter `conversation.process (Conversation - Process)` and select `Conversation (conversation): Process` (as shown in operation 2).

![image-20250504043539343](images/image-ha-integration-02.png)

3. Check the `Agent` option on the page, in the `Conversation Agent` that becomes always on, select the voice assistant name you configured in step 1. As shown, what I configured is `ZhipuAi` and select it.

![image-20250504043854760](images/image-ha-integration-03.png)

4. After selecting, click `Enter YAML Mode` at the bottom left of the form.

![image-20250504043951126](images/image-ha-integration-04.png)

5. Copy the agent-id value, for example, in the figure mine is `01JP2DYMBDF7F4ZA2DMCF2AGX2` (for reference only).

![image-20250504044046466](images/image-ha-integration-05.png)

6. Switch to the `config.yaml` file of the Xiaozhi open source server `xiaozhi-esp32-server`, in the LLM configuration, find Home Assistant, set your Home Assistant network address, Api key and the agent_id you just queried.
7. Modify the `LLM` of the `selected_module` attribute in the `config.yaml` file to `HomeAssistant`, and `Intent` to `nointent`.
8. Restart the Xiaozhi open source server `xiaozhi-esp32-server` to use normally.

## Method 3: Use Home Assistant's MCP Service (Recommended)

### Function Description

- You need to integrate and install the HA integration - [Model Context Protocol Server](https://www.home-assistant.io/integrations/mcp_server/) in Home Assistant in advance.

- This method and Method 2 are both solutions provided by HA officially. Different from Method 2, you can normally use the open source co-built plugins of the Xiaozhi open source server `xiaozhi-esp32-server`, while allowing you to freely use any LLM model that supports function_call functionality.

### Configuration Steps

#### 1. Install Home Assistant's MCP Service Integration.

Official integration website - [Model Context Protocol Server](https://www.home-assistant.io/integrations/mcp_server/)..

Or follow the manual operations below.

> - Go to the Home Assistant page **[Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations)**.
>
> - In the lower right corner, select the **[Add Integration](https://my.home-assistant.io/redirect/config_flow_start?domain=mcp_server)** button.
>
> - Select **Model Context Protocol Server** from the list.
>
> - Follow the on-screen instructions to complete the setup.

#### 2. Configure Xiaozhi Open Source Server MCP Configuration Information


Enter the `data` directory and find the `.mcp_server_settings.json` file.

If your `data` directory doesn't have a `.mcp_server_settings.json` file,
- Please copy the `mcp_server_settings.json` file from the `xiaozhi-server` folder root directory to the `data` directory and rename it to `.mcp_server_settings.json`
- Or [download this file](https://github.com/xinnan-tech/xiaozhi-esp32-server/blob/main/main/xiaozhi-server/mcp_server_settings.json), download it to the `data` directory, and rename it to `.mcp_server_settings.json`


Modify this part of the content in `"mcpServers"`:

```json
"Home Assistant": {
      "command": "mcp-proxy",
      "args": [
        "http://YOUR_HA_HOST/mcp_server/sse"
      ],
      "env": {
        "API_ACCESS_TOKEN": "YOUR_API_ACCESS_TOKEN"
      }
},
```

Note:

1. **Replace Configuration:**
   - Replace `YOUR_HA_HOST` in `args` with your HA service address. If your service address already contains https/http (for example `http://192.168.1.101:8123`), you only need to fill in `192.168.1.101:8123`.
   - Replace `YOUR_API_ACCESS_TOKEN` in `API_ACCESS_TOKEN` in `env` with the development key api key you obtained earlier.
2. **If you add configuration and there are no new `mcpServers` configurations after the `"mcpServers"` bracket, you need to remove the last comma `,`**, otherwise parsing may fail.

**Final effect reference (for reference only)**:

```json
 "mcpServers": {
    "Home Assistant": {
      "command": "mcp-proxy",
      "args": [
        "http://192.168.1.101:8123/mcp_server/sse"
      ],
      "env": {
        "API_ACCESS_TOKEN": "abcd.efghi.jkl"
      }
    }
  }
```

#### 3. Configure Xiaozhi Open Source Server System Configuration

1. **Select any LLM model that supports function_call as Xiaozhi's LLM chat assistant (but don't select Home Assistant as LLM tool)**. The model I chose this time is: free ChatGLM, which supports functioncall function calls, but sometimes the calls are not very stable. If you want to pursue stability, it is recommended to set LLM to: DoubaoLLM, and the specific model_name used is: doubao-1-5-pro-32k-250115.

2. Switch to the `config.yaml` file of the Xiaozhi open source server `xiaozhi-esp32-server`, set your LLM model configuration, and adjust the `Intent` of the `selected_module` configuration to `function_call`.

3. Restart the Xiaozhi open source server `xiaozhi-esp32-server` to use normally.
