# Weather Plugin Usage Guide

## Overview

The weather plugin `get_weather` is one of the core functions of Xiaozhi ESP32 Voice Assistant, supporting voice queries for weather information across the country. The plugin is based on HeWeather API, providing real-time weather and 7-day weather forecast functions.

## API Key Application Guide

### 1. Register HeWeather Account

1. Visit [HeWeather Console](https://console.qweather.com/)
2. Register an account and complete email verification
3. Log in to the console

### 2. Create Application to Get API Key

1. After entering the console, click ["Project Management"](https://console.qweather.com/project?lang=zh) on the right → "Create Project"
2. Fill in project information:
   - **Project Name**: e.g., "Xiaozhi Voice Assistant"
3. Click Save
4. After project creation is complete, click "Create Credential" in this project
5. Fill in credential information:
    - **Credential Name**: e.g., "Xiaozhi Voice Assistant"
    - **Identity Authentication Method**: Select "API Key"
6. Click Save
7. Copy the `API Key` in the credential, this is the first key configuration information

### 3. Get API Host

1. Click ["Settings"](https://console.qweather.com/setting?lang=zh) in the console → "API Host"
2. View the exclusive `API Host` address assigned to you, this is the second key configuration information

The above operations will give you two important configuration pieces of information: `API Key` and `API Host`

## Configuration Methods (Choose One)

### Method 1. If You Are Using Management Console Deployment (Recommended)

1. Log in to the Management Console
2. Enter the "Role Configuration" page
3. Select the agent to configure
4. Click the "Edit Functions" button
5. Find the "Weather Query" plugin in the right parameter configuration area
6. Check "Weather Query"
7. Fill in the first key configuration `API Key` you copied into `Weather Plugin API Key`
8. Fill in the second key configuration `API Host` you copied into `Developer API Host`
9. Save configuration, then save agent configuration

### Method 2. If You Are Only Deploying Single Module xiaozhi-server

Configure in `data/.config.yaml`:

1. Fill in the first key configuration `API Key` you copied into `api_key`
2. Fill in the second key configuration `API Host` you copied into `api_host`
3. Fill in your city into `default_location`, for example `Guangzhou`

```yaml
plugins:
  get_weather:
    api_key: "Your HeWeather API Key"
    api_host: "Your HeWeather API Host Address"
    default_location: "Your Default Query City"
```
