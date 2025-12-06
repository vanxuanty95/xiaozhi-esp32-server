# MCP Access Point Usage Guide

This tutorial uses Brother Xia's open source MCP calculator function as an example to introduce how to integrate your own custom MCP service into your access point.

The premise of this tutorial is that your `xiaozhi-server` has already enabled the MCP access point function. If you haven't enabled it yet, you can enable it first according to [this tutorial](./mcp-endpoint-enable.md).

# How to Integrate a Simple MCP Function for an Agent, Such as Calculator Function

### If You Are Deploying All Modules
If you are deploying all modules, you can enter the management console, agent management, click `Configure Role`, on the right side of `Intent Recognition`, there is an `Edit Functions` button.

Click this button. In the popup page, at the bottom, there will be `MCP Access Point`. Normally, it will display this agent's `MCP Access Point Address`. Next, let's extend a calculator function based on MCP technology for this agent.

This `MCP Access Point Address` is very important, you will use it later.

### If You Are Deploying Single Module
If you are deploying a single module, and you have already configured the MCP access point address in the configuration file, then normally, when the single module deployment starts, it will output the following log.
```
250705[__main__]-INFO-Initialize component: vad successful SileroVAD
250705[__main__]-INFO-Initialize component: asr successful FunASRServer
250705[__main__]-INFO-OTA interface is          http://192.168.1.25:8002/xiaozhi/ota/
250705[__main__]-INFO-Vision analysis interface is     http://192.168.1.25:8002/mcp/vision/explain
250705[__main__]-INFO-MCP access point is        ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
250705[__main__]-INFO-Websocket address is    ws://192.168.1.25:8000/xiaozhi/v1/
250705[__main__]-INFO-=======The above address is a websocket protocol address, please do not access it with a browser=======
250705[__main__]-INFO-If you want to test websocket, please open test_page.html in the test directory with Google Chrome
250705[__main__]-INFO-=============================================================
```

As above, the `ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc` in the output `MCP access point is` is your `MCP Access Point Address`.

This `MCP Access Point Address` is very important, you will use it later.

## Step 1: Download Brother Xia's MCP Calculator Project Code

Open Brother Xia's [Calculator Project](https://github.com/78/mcp-calculator) in browser,

After opening, find a green button on the page that says `Code`, click it, and then you will see a `Download ZIP` button.

Click it to download the source code zip file of this project. After downloading to your computer, extract it. At this time, its name may be `mcp-calculatorr-main`
You need to rename it to `mcp-calculator`. Next, we use command line to enter the project directory and install dependencies


```bash
# Enter project directory
cd mcp-calculator

conda remove -n mcp-calculator --all -y
conda create -n mcp-calculator python=3.10 -y
conda activate mcp-calculator

pip install -r requirements.txt
```

## Step 2: Start

Before starting, first copy the MCP access point address from your management console's agent.

For example, my agent's mcp address is
```
ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

Start entering commands

```bash
export MCP_ENDPOINT=ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

After entering, start the program

```bash
python mcp_pipe.py calculator.py
```

### If You Are Deploying with Management Console
If you are deploying with management console, after starting, enter the management console again, click refresh MCP access status, and you will see your extended function list.

### If You Are Deploying Single Module
If you are deploying a single module, when the device connects, it will output similar logs, indicating success

```
250705 -INFO-Initializing MCP access point: wss://2662r3426b.vicp.fun/mcp_e 
250705 -INFO-Sending MCP access point initialization message
250705 -INFO-MCP access point connection successful
250705 -INFO-MCP access point initialization successful
250705 -INFO-Unified tool handler initialization complete
250705 -INFO-MCP access point server information: name=Calculator, version=1.9.4
250705 -INFO-Number of tools supported by MCP access point: 1
250705 -INFO-All MCP access point tools have been obtained, client ready
250705 -INFO-Tool cache refreshed
250705 -INFO-Current supported function list: [ 'get_time', 'get_lunar', 'play_music', 'get_weather', 'handle_exit_intent', 'calculator']
```
If it contains `'calculator'`, it means the device can call the calculator tool based on intent recognition.
