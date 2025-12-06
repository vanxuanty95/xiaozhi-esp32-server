# Voiceprint Recognition Enablement Guide

This tutorial contains 3 parts
- 1. How to deploy the voiceprint recognition service
- 2. How to configure the voiceprint recognition interface when deploying all modules
- 3. How to configure voiceprint recognition in the most simplified deployment

# 1. How to Deploy the Voiceprint Recognition Service

## Step 1: Download Voiceprint Recognition Project Source Code

Open [Voiceprint Recognition Project Address](https://github.com/xinnan-tech/voiceprint-api) in browser

After opening, find a green button on the page that says `Code`, click it, and then you will see a `Download ZIP` button.

Click it to download the source code zip file of this project. After downloading to your computer, extract it. At this time, its name may be `voiceprint-api-main`
You need to rename it to `voiceprint-api`.

## Step 2: Create Database and Tables

Voiceprint recognition needs to depend on the `mysql` database. If you have deployed the `Management Console` before, it means you have installed `mysql`. You can share it.

You can try using the `telnet` command on the host machine to see if you can normally access the `3306` port of `mysql`.
```
telnet 127.0.0.1 3306
```
If you can access port 3306, please ignore the following content and go directly to Step 3.

If you cannot access, you need to recall how your `mysql` was installed.

If your mysql was installed by yourself using an installation package, it means your `mysql` has network isolation. You may need to solve the problem of accessing the `3306` port of `mysql` first.

If your `mysql` was installed through this project's `docker-compose_all.yml`. You need to find the `docker-compose_all.yml` file you used to create the database at that time and modify the following content

Before modification
```
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    expose:
      - "3306:3306"
```

After modification
```
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    ports:
      - "3306:3306"
```

Note: Change `expose` under `xiaozhi-esp32-server-db` to `ports`. After modification, you need to restart. The following are the commands to restart mysql:

```
# Enter the folder where your docker-compose_all.yml is located, for example, mine is xiaozhi-server
cd xiaozhi-server
docker compose -f docker-compose_all.yml down
docker compose -f docker-compose.yml up -d
```

After startup, use the `telnet` command on the host machine again to see if you can normally access the `3306` port of `mysql`.
```
telnet 127.0.0.1 3306
```
Normally, you should be able to access it this way.

## Step 3: Create Database and Tables
If your host machine can normally access the mysql database, create a database named `voiceprint_db` and a `voiceprints` table on mysql.

```
CREATE DATABASE voiceprint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE voiceprint_db;

CREATE TABLE voiceprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    speaker_id VARCHAR(255) NOT NULL UNIQUE,
    feature_vector LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_speaker_id (speaker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Step 4: Configure Database Connection

Enter the `voiceprint-api` folder and create a folder named `data`.

Copy `voiceprint.yaml` from the `voiceprint-api` root directory to the `data` folder and rename it to `.voiceprint.yaml`

Next, you need to focus on configuring the database connection in `.voiceprint.yaml`.

```
mysql:
  host: "127.0.0.1"
  port: 3306
  user: "root"
  password: "your_password"
  database: "voiceprint_db"
```

Note! Since your voiceprint recognition service is deployed using docker, `host` needs to be filled in with your `mysql machine's LAN ip`.

Note! Since your voiceprint recognition service is deployed using docker, `host` needs to be filled in with your `mysql machine's LAN ip`.

Note! Since your voiceprint recognition service is deployed using docker, `host` needs to be filled in with your `mysql machine's LAN ip`.

## Step 5: Start Program
This project is a very simple project, it is recommended to run it using docker. However, if you don't want to run it using docker, you can refer to [this page](https://github.com/xinnan-tech/voiceprint-api/blob/main/README.md) to run from source code. The following is the method to run with docker

```
# Enter this project's source code root directory
cd voiceprint-api

# Clear cache
docker compose -f docker-compose.yml down
docker stop voiceprint-api
docker rm voiceprint-api
docker rmi ghcr.nju.edu.cn/xinnan-tech/voiceprint-api:latest

# Start docker container
docker compose -f docker-compose.yml up -d
# View logs
docker logs -f voiceprint-api
```

At this time, the log will output logs similar to the following
```
250711 INFO-🚀 Start: Production environment service startup (Uvicorn), listening address: 0.0.0.0:8005
250711 INFO-============================================================
250711 INFO-Voiceprint interface address: http://127.0.0.1:8005/voiceprint/health?key=abcd
250711 INFO-============================================================
```

Please copy out the voiceprint interface address:

Since you are deploying with docker, you must not directly use the address above!

Since you are deploying with docker, you must not directly use the address above!

Since you are deploying with docker, you must not directly use the address above!

First copy the address and put it in a draft. You need to know what your computer's LAN ip is. For example, if my computer's LAN ip is `192.168.1.25`, then
My original interface address
```
http://127.0.0.1:8005/voiceprint/health?key=abcd

```
needs to be changed to
```
http://192.168.1.25:8005/voiceprint/health?key=abcd
```

After modification, please use a browser to directly access the `Voiceprint Interface Address`. When the browser shows code similar to this, it means it's successful.
```
{"total_voiceprints":0,"status":"healthy"}
```

Please keep the modified `Voiceprint Interface Address` well, it will be needed in the next step.

# 2. How to Configure Voiceprint Recognition When Deploying All Modules

## Step 1: Configure Interface
First, you need to enable the voiceprint recognition function. In the management console, click `Parameter Dictionary` at the top, in the dropdown menu, click the `System Feature Configuration` page. Check `Voiceprint Recognition` on the page, click `Save Configuration`. You can see the `Voiceprint Recognition` button on the new agent card.

If you are deploying all modules, use administrator account to log in to the management console, click `Parameter Dictionary` at the top, select `Parameter Management` function.

Then search for parameter `server.voice_print`, at this time, its value should be `null`.
Click the edit button, paste the `Voiceprint Interface Address` obtained in the previous step into `Parameter Value`. Then save.

If it can be saved successfully, everything is going well, you can go to the agent to check the effect. If it's not successful, it means the management console cannot access voiceprint recognition. It's very likely a network firewall issue, or the correct LAN ip was not filled in.

## Step 2: Set Agent Memory Mode

Enter your agent's role configuration, set memory to `Local Short-term Memory`, and be sure to enable `Report Text + Voice`.

## Step 3: Chat with Your Agent

Power on your device, then chat with it at normal speed and tone.

## Step 4: Set Voiceprint

In the management console, `Agent Management` page, in the agent panel, there is a `Voiceprint Recognition` button, click it. At the bottom there is an `Add Button`. You can register voiceprint for what someone says.
In the popup dialog, it is recommended to fill in the `Description` attribute, which can be this person's occupation, personality, hobbies. This helps the agent analyze and understand the speaker.

## Step 3: Chat with Your Agent

Power on your device, ask it, "Do you know who I am?" If it can answer, it means the voiceprint recognition function is working normally.

# 3. How to Configure Voiceprint Recognition in the Most Simplified Deployment

## Step 1: Configure Interface
Open the `xiaozhi-server/data/.config.yaml` file (create if it doesn't exist), then add/modify the following content:

```
# Voiceprint recognition configuration
voiceprint:
  # Voiceprint interface address
  url: your voiceprint interface address
  # Speaker configuration: speaker_id, name, description
  speakers:
    - "test1,Zhang San,Zhang San is a programmer"
    - "test2,Li Si,Li Si is a product manager"
    - "test3,Wang Wu,Wang Wu is a designer"
```

Paste the `Voiceprint Interface Address` obtained in the previous step into `url`. Then save.

Add `speakers` parameter as needed. Note that this `speaker_id` parameter will be used later for voiceprint registration.

## Step 2: Register Voiceprint
If you have already started the voiceprint service, access `http://localhost:8005/voiceprint/docs` in your local browser to view the API documentation. Here we only explain how to use the API for registering voiceprint.

The API address for registering voiceprint is `http://localhost:8005/voiceprint/register`, request method is POST.

The request header needs to include Bearer Token authentication, the token is the part after `?key=` in the `Voiceprint Interface Address`. For example, if my voiceprint registration address is `http://127.0.0.1:8005/voiceprint/health?key=abcd`, then my token is `abcd`.

The request body contains speaker ID (speaker_id) and WAV audio file (file). Request example is as follows:

```
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "speaker_id=your_speaker_id_here" \
  -F "file=@/path/to/your/file" \
  http://localhost:8005/voiceprint/register
```

Here `file` is the audio file of the speaker speaking that needs to be registered, `speaker_id` needs to be consistent with the `speaker_id` in Step 1's configure interface. For example, if I need to register Zhang San's voiceprint, and Zhang San's `speaker_id` filled in `.config.yaml` is `test1`, then when I register Zhang San's voiceprint, the `speaker_id` filled in the request body is `test1`, and `file` is the audio file of Zhang San speaking a paragraph.

 ## Step 3: Start Service

Start the Xiaozhi server and voiceprint service to use normally.
