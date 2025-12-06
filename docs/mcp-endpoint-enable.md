# MCP Access Point Deployment and Usage Guide

This tutorial contains 3 parts
- 1. How to deploy the MCP access point service
- 2. How to configure MCP access point when deploying all modules
- 3. How to configure MCP access point when deploying single module

# 1. How to Deploy the MCP Access Point Service

## Step 1: Download MCP Access Point Project Source Code

Open [MCP Access Point Project Address](https://github.com/xinnan-tech/mcp-endpoint-server) in browser

After opening, find a green button on the page that says `Code`, click it, and then you will see a `Download ZIP` button.

Click it to download the source code zip file of this project. After downloading to your computer, extract it. At this time, its name may be `mcp-endpoint-server-main`
You need to rename it to `mcp-endpoint-server`.

## Step 2: Start Program
This project is a very simple project, it is recommended to run it using docker. However, if you don't want to run it using docker, you can refer to [this page](https://github.com/xinnan-tech/mcp-endpoint-server/blob/main/README_dev.md) to run from source code. The following is the method to run with docker

```
# Enter this project's source code root directory
cd mcp-endpoint-server

# Clear cache
docker compose -f docker-compose.yml down
docker stop mcp-endpoint-server
docker rm mcp-endpoint-server
docker rmi ghcr.nju.edu.cn/xinnan-tech/mcp-endpoint-server:latest

# Start docker container
docker compose -f docker-compose.yml up -d
# View logs
docker logs -f mcp-endpoint-server
```

At this time, the log will output logs similar to the following
```
250705 INFO-=====The following addresses are Management Console/Single Module MCP Access Point addresses====
250705 INFO-Management Console MCP Parameter Configuration: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
250705 INFO-Single Module Deployment MCP Access Point: ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
250705 INFO-=====Please select and use according to specific deployment, do not leak to anyone======
```

Please copy out the two interface addresses:

Since you are deploying with docker, you must not directly use the address above!

Since you are deploying with docker, you must not directly use the address above!

Since you are deploying with docker, you must not directly use the address above!

First copy the address and put it in a draft. You need to know what your computer's LAN ip is. For example, if my computer's LAN ip is `192.168.1.25`, then
My original interface address
```
Management Console MCP Parameter Configuration: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
Single Module Deployment MCP Access Point: ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
```
needs to be changed to
```
Management Console MCP Parameter Configuration: http://192.168.1.25:8004/mcp_endpoint/health?key=abc
Single Module Deployment MCP Access Point: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

After modification, please use a browser to directly access the `Management Console MCP Parameter Configuration`. When the browser shows code similar to this, it means it's successful.
```
{"result":{"status":"success","connections":{"tool_connections":0,"robot_connections":0,"total_connections":0}},"error":null,"id":null,"jsonrpc":"2.0"}
```

Please keep the above two `Interface Addresses` well, they will be needed in the next step.

# 2. How to Configure MCP Access Point When Deploying All Modules
First, you need to enable the MCP access point function. In the management console, click `Parameter Dictionary` at the top, in the dropdown menu, click the `System Feature Configuration` page. Check `MCP Access Point` on the page, click `Save Configuration`. In the `Role Configuration` page, click the `Edit Functions` button, and you can see the `MCP Access Point` function.

If you are deploying all modules, use administrator account to log in to the management console, click `Parameter Dictionary` at the top, select `Parameter Management` function.

Then search for parameter `server.mcp_endpoint`, at this time, its value should be `null`.
Click the edit button, paste the `Management Console MCP Parameter Configuration` obtained in the previous step into `Parameter Value`. Then save.

If it can be saved successfully, everything is going well, you can go to the agent to check the effect. If it's not successful, it means the management console cannot access the MCP access point. It's very likely a network firewall issue, or the correct LAN ip was not filled in.

# 3. How to Configure MCP Access Point When Deploying Single Module

If you are deploying a single module, find your configuration file `data/.config.yaml`.
Search for `mcp_endpoint` in the configuration file. If not found, add the `mcp_endpoint` configuration. Similar to this
```
server:
  websocket: ws://your ip or domain:port/xiaozhi/v1/
  http_port: 8002
log:
  log_level: INFO

# There may be more configurations here..

mcp_endpoint: your access point websocket address
```
At this time, please paste the `Single Module Deployment MCP Access Point` obtained in `How to Deploy the MCP Access Point Service` into `mcp_endpoint`. Similar to this

```
server:
  websocket: ws://your ip or domain:port/xiaozhi/v1/
  http_port: 8002
log:
  log_level: INFO

# There may be more configurations here

mcp_endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

After configuration, starting the single module will output the following log.
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

As above, if it can output something similar to `MCP access point is` with `ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc`, it means the configuration is successful.

