# How to Get Device Information Using MCP Method

This tutorial will guide you on how to get device information using the MCP method.

Step 1: Customize your `agent-base-prompt.txt` file

Copy the content of the `agent-base-prompt.txt` file in the xiaozhi-server directory to your `data` directory, and rename it to `.agent-base-prompt.txt`.

Step 2: Modify the `data/.agent-base-prompt.txt` file, find the `<context>` tag, and add the following code content in the tag content:
```
- **Device ID：** {{device_id}}
```

After adding, the `<context>` tag content in your `data/.agent-base-prompt.txt` file should be roughly as follows:
```
<context>
【Important! The following information is provided in real-time, no need to call tools to query, please use directly:】
- **Device ID：** {{device_id}}
- **Current Time：** {{current_time}}
- **Today's Date：** {{today_date}} ({{today_weekday}})
- **Today's Lunar Calendar：** {{lunar_date}}
- **User's City：** {{local_address}}
- **Local Next 7 Days Weather：** {{weather_info}}
</context>
```

Step 3: Modify the `data/.config.yaml` file, find the `agent-base-prompt` configuration, the content before modification is as follows:
```
prompt_template: agent-base-prompt.txt
```
Change to
```
prompt_template: data/.agent-base-prompt.txt
```

Step 4: Restart your xiaozhi-server service.

Step 5: Add a parameter named `device_id`, type `string`, description `Device ID` in your MCP method.

Step 6: Wake up Xiaozhi again, let it call the MCP method, and check if your MCP method can get the `Device ID`.
