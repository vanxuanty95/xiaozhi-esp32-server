# ESP32 Firmware Compilation

## Step 1: Prepare Your OTA Address

If you are using version 0.3.12 of this project, whether it's simple server deployment or all modules deployment, there will be an OTA address.

Since simple server deployment and all modules deployment have different OTA address setup methods, please choose the specific method below:

### If You Are Using Simple Server Deployment
At this moment, please open your OTA address in a browser, for example my OTA address
```
http://192.168.1.25:8003/xiaozhi/ota/
```
If it displays "OTA interface is running normally, websocket address sent to device is: ws://xxx:8000/xiaozhi/v1/"

You can use the project's built-in `test_page.html` to test whether you can connect to the websocket address output by the OTA page.

If you cannot access it, you need to modify the `server.websocket` address in the configuration file `.config.yaml`, restart and test again until `test_page.html` can access normally.

After success, please proceed to Step 2

### If You Are Using All Modules Deployment
At this moment, please open your OTA address in a browser, for example my OTA address
```
http://192.168.1.25:8002/xiaozhi/ota/
```

If it displays "OTA interface is running normally, websocket cluster count: X". Then proceed to Step 2.

If it displays "OTA interface is not running normally", it's probably because you haven't configured the `Websocket` address in the `Management Console`. Then:

- 1. Log in to the Management Console as super administrator

- 2. Click `Parameter Management` in the top menu

- 3. Find the `server.websocket` item in the list, enter your `Websocket` address. For example, mine is

```
ws://192.168.1.25:8000/xiaozhi/v1/
```

After configuration, refresh your OTA interface address in the browser to see if it's normal. If it's still not normal, confirm again whether Websocket is started normally and whether the Websocket address is configured.

## Step 2: Configure Environment
First configure the project environment according to this tutorial [《Windows搭建 ESP IDF 5.3.2开发环境以及编译小智》](https://icnynnzcwou8.feishu.cn/wiki/JEYDwTTALi5s2zkGlFGcDiRknXf)

## Step 3: Open Configuration File
After configuring the compilation environment, download Brother Xia's xiaozhi-esp32 project source code,

Download Brother Xia's [xiaozhi-esp32 project source code](https://github.com/78/xiaozhi-esp32) from here.

After downloading, open the `xiaozhi-esp32/main/Kconfig.projbuild` file.

## Step 4: Modify OTA Address

Find the `default` content of `OTA_URL`, change `https://api.tenclass.net/xiaozhi/ota/`
   to your own address, for example, my interface address is `http://192.168.1.25:8002/xiaozhi/ota/`, change the content to this.

Before modification:
```
config OTA_URL
    string "Default OTA URL"
    default "https://api.tenclass.net/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```
After modification:
```
config OTA_URL
    string "Default OTA URL"
    default "http://192.168.1.25:8002/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```

## Step 4: Set Compilation Parameters

Set compilation parameters

```
# Enter xiaozhi-32 root directory from terminal command line
cd xiaozhi-esp32
# For example, I'm using esp32s3 board, so set compilation target to esp32s3, if your board is another model, please replace with corresponding model
idf.py set-target esp32s3
# Enter menu configuration
idf.py menuconfig
```

After entering menu configuration, enter `Xiaozhi Assistant`, set `BOARD_TYPE` to your board's specific model
Save and exit, return to terminal command line.

## Step 5: Compile Firmware

```
idf.py build
```

## Step 6: Package bin Firmware

```
cd scripts
python release.py
```

After the packaging command above is executed, it will generate the firmware file `merged-binary.bin` in the `build` directory under the project root directory.
This `merged-binary.bin` is the firmware file to be burned to the hardware.

Note: If after executing the second command, you get a "zip" related error, please ignore this error, as long as the firmware file `merged-binary.bin` is generated in the `build` directory
, it won't have much impact on you, please continue.

## Step 7: Burn Firmware
   Connect the esp32 device to the computer, use Chrome browser, open the following URL

```
https://espressif.github.io/esp-launchpad/
```

Open this tutorial, [Flash工具/Web端烧录固件（无IDF开发环境）](https://ccnphfhqs21z.feishu.cn/wiki/Zpz4wXBtdimBrLk25WdcXzxcnNS).
Scroll to: `方式二：ESP-Launchpad 浏览器WEB端烧录`, start from `3. 烧录固件/下载到开发板`, follow the tutorial to operate.

After successful burning and successful networking, wake up Xiaozhi with the wake word, pay attention to the console information output by the server.

## Common Issues
The following are some common issues for reference:

[1. Why does Xiaozhi recognize many Korean, Japanese, and English words when I speak?](./FAQ.md)

[2. Why does "TTS task error file does not exist" appear?](./FAQ.md)

[3. TTS often fails, often times out](./FAQ.md)

[4. Can connect to self-built server using Wifi, but 4G mode cannot connect](./FAQ.md)

[5. How to improve Xiaozhi conversation response speed?](./FAQ.md)

[6. I speak very slowly, and Xiaozhi always interrupts during pauses](./FAQ.md)

[7. I want to control lights, air conditioners, remote power on/off, etc. through Xiaozhi](./FAQ.md)
