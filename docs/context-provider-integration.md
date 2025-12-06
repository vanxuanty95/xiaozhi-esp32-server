# Context Provider Usage Tutorial

## Overview

`Context Provider` is to add [data sources] to the context of Xiaozhi's system prompt.

`Context Provider` gets data from external systems at the moment Xiaozhi wakes up and dynamically injects it into the LLM's system prompt (System Prompt).
This allows it to perceive the state of something in the world when waking up.

It is fundamentally different from MCP and memory: `Context Provider` forces Xiaozhi to perceive world data; `Memory (Mem)` lets it know what was discussed before; `MCP (function call)` is used when a certain capability/knowledge needs to be called.

Through this function, at the moment Xiaozhi wakes up, it "perceives":
- Human health sensor status (body temperature, blood pressure, blood oxygen status, etc.)
- Real-time data from business systems (server load, todo data, stock information, etc.)
- Any text information that can be obtained through HTTP API

**Note**: This function only makes it convenient for Xiaozhi to perceive the state of things when waking up. If you want Xiaozhi to get the state of things in real-time after waking up, it is recommended to combine this function with MCP tool calls.

## How It Works

1. **Configure Sources**: User configures one or more HTTP API addresses.
2. **Trigger Request**: When the system builds the Prompt, if it finds that the template contains the `{{ dynamic_context }}` placeholder, it will request all configured APIs.
3. **Auto Injection**: The system will automatically format the data returned by the API as a Markdown list and replace the `{{ dynamic_context }}` placeholder.

## API Specification

For Xiaozhi to correctly parse the data, your API needs to meet the following specifications:

- **Request Method**: `GET`
- **Request Header**: The system will automatically add the `device_id` field to the Request Header.
- **Response Format**: Must return JSON format and include `code` and `data` fields.

### Response Examples

**Case 1: Return Key-Value Pairs**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "Living Room Temperature": "26℃",
    "Living Room Humidity": "45%",
    "Main Door Status": "Closed"
  }
}
```
*Injection Effect:*
```markdown
<context>
- **Living Room Temperature:** 26℃
- **Living Room Humidity:** 45%
- **Main Door Status:** Closed
</context>
```

**Case 2: Return List**
```json
{
  "code": 0,
  "data": [
    "You have 10 todo items",
    "Current car speed is 100km per hour"
  ]
}
```
*Injection Effect:*
```markdown
<context>
- You have 10 todo items
- Current car speed is 100km per hour
</context>
```

## Configuration Guide

### Method 1: Management Console Configuration (All Modules Deployment)

1. Log in to the management console and enter the **Role Configuration** page.
2. Find the **Context Provider** configuration item (click the "Edit Source" button).
3. Click **Add** and enter your API address.
4. If the API requires authentication, you can add `Authorization` or other Headers in the **Request Headers** section.
5. Save configuration.

### Method 2: Configuration File Configuration (Single Module Deployment)

Edit the `xiaozhi-server/data/.config.yaml` file and add the `context_providers` configuration section:

```yaml
# Context provider configuration
context_providers:
  - url: "http://api.example.com/data"
    headers:
      Authorization: "Bearer your-token"
  - url: "http://another-api.com/data"
```

## Enable Function

By default, the system's prompt template file (`data/.agent-base-prompt.txt`) already has the `{{ dynamic_context }}` placeholder preset, so you don't need to add it manually.

**Example:**

```markdown
<context>
【Important! The following information is provided in real-time, no need to call tools to query, please use directly:】
- **Device ID:** {{device_id}}
- **Current Time:** {{current_time}}
...
{{ dynamic_context }}
</context>
```

**Note**: If you don't need to use this function, you can choose **not to configure any context providers**, or **delete** the `{{ dynamic_context }}` placeholder from the prompt template file.

## Appendix: Mock Test Service Example

For your convenience in testing and development, we provide a simple Python Mock Server script. You can run this script locally to simulate API interfaces.

**mock_api_server.py**

```python
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

# Set port number
PORT = 8081

class MockRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse path and parameters
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        response_data = {}
        status_code = 200

        print(f"Received request: {path}, parameters: {query}")

        # Case 1: Simulate health data (return dictionary Dict)
        # Path parameter style: /health
        # device_id obtained from Header
        if path == "/health":
            device_id = self.headers.get("device_id", "unknown_device")
            print(f"device_id: {device_id}")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "Test Device ID": device_id,
                    "Heart Rate": "80 bpm",
                    "Blood Pressure": "120/80 mmHg",
                    "Status": "Good"
                }
            }

        # Case 2: Simulate news list (return list List)
        # No parameters: /news/list
        elif path == "/news/list":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": [
                    "Today's Headlines: Python 3.14 Released",
                    "Tech News: AI Assistant Changes Life",
                    "Local News: Heavy rain tomorrow, remember to bring an umbrella"
                ]
            }

        # Case 3: Simulate weather brief (return string String)
        # No parameters: /weather/simple
        elif path == "/weather/simple":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": "Today is sunny turning cloudy, temperature 20-25 degrees, air quality excellent, suitable for travel."
            }

        # Case 4: Simulate device details (Query parameter style)
        # Parameter style: /device/info
        # device_id obtained from Header
        elif path == "/device/info":
            device_id = self.headers.get("device_id", "unknown_device")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "Query Method": "Header parameter",
                    "Device ID": device_id,
                    "Battery": "85%",
                    "Firmware": "v2.0.1"
                }
            }
        
        # Case 5: 404 Not Found
        else:
            status_code = 404
            response_data = {"error": "Interface does not exist"}

        # Send response
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

# Start service
# Allow address reuse to prevent errors from rapid restart
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), MockRequestHandler) as httpd:
    print(f"==================================================")
    print(f"Mock API Server started: http://localhost:{PORT}")
    print(f"Available interface list:")
    print(f"1. [Dictionary] http://localhost:{PORT}/health")
    print(f"2. [List] http://localhost:{PORT}/news/list")
    print(f"3. [Text] http://localhost:{PORT}/weather/simple")
    print(f"4. [Parameter] http://localhost:{PORT}/device/info")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nService stopped")
```
