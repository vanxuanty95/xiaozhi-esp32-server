# Configure Custom Server Based on Firmware Compiled by Brother Xia

## Step 1: Confirm Version
Burn Brother Xia's pre-compiled [firmware version 1.6.1 or above](https://github.com/78/xiaozhi-esp32/releases)

## Step 2: Prepare Your OTA Address
If you are using all modules deployment according to the tutorial, you should have an OTA address.

At this moment, please open your OTA address in a browser, for example my OTA address
```
https://2662r3426b.vicp.fun/xiaozhi/ota/
```

If it displays "OTA interface is running normally, websocket cluster count: X". Then proceed.

If it displays "OTA interface is not running normally", it's probably because you haven't configured the `Websocket` address in the `Management Console`. Then:

- 1. Log in to the Management Console as super administrator

- 2. Click `Parameter Management` in the top menu

- 3. Find the `server.websocket` item in the list, enter your `Websocket` address. For example, mine is

```
wss://2662r3426b.vicp.fun/xiaozhi/v1/
```

After configuration, refresh your OTA interface address in the browser to see if it's normal. If it's still not normal, confirm again whether Websocket is started normally and whether the Websocket address is configured.

## Step 3: Enter Network Configuration Mode
Enter the device's network configuration mode, click "Advanced Options" at the top of the page, enter your server's `ota` address inside, click save. Restart the device
![Please refer to - OTA Address Settings](../docs/images/firmware-setting-ota.png)

## Step 4: Wake Up Xiaozhi and Check Log Output

Wake up Xiaozhi and see if the logs are outputting normally.


## Common Issues
The following are some common issues for reference:

[1. Why does Xiaozhi recognize many Korean, Japanese, and English words when I speak?](./FAQ.md)

[2. Why does "TTS task error file does not exist" appear?](./FAQ.md)

[3. TTS often fails, often times out](./FAQ.md)

[4. Can connect to self-built server using Wifi, but 4G mode cannot connect](./FAQ.md)

[5. How to improve Xiaozhi conversation response speed?](./FAQ.md)

[6. I speak very slowly, and Xiaozhi always interrupts during pauses](./FAQ.md)

[7. I want to control lights, air conditioners, remote power on/off, etc. through Xiaozhi](./FAQ.md)
