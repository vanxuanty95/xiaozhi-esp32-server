# RAGFlow Integration Guide

This tutorial is mainly divided into two parts

- Part 1: How to deploy RAGFlow
- Part 2: How to configure RAGFlow interface in the management console

If you are very familiar with RAGFlow and have already deployed RAGFlow, you can skip Part 1 and go directly to Part 2. But if you want someone to guide you to deploy RAGFlow so that it can share `mysql` and `redis` basic services with `xiaozhi-esp32-server` to reduce resource costs, you need to start from Part 1.

# Part 1: How to Deploy RAGFlow
## Step 1: Confirm if MySQL and Redis are Available

RAGFlow needs to depend on the `mysql` database. If you have deployed the `Management Console` before, it means you have installed `mysql`. You can share it.

You can try using the `telnet` command on the host machine to see if you can normally access the `3306` port of `mysql`.
``` shell
telnet 127.0.0.1 3306

telnet 127.0.0.1 6379
```
If you can access the `3306` port and `6379` port, please ignore the following content and go directly to Step 2.

If you cannot access, you need to recall how your `mysql` was installed.

If your mysql was installed by yourself using an installation package, it means your `mysql` has network isolation. You may need to solve the problem of accessing the `3306` port of `mysql` first.

If your `mysql` was installed through this project's `docker-compose_all.yml`. You need to find the `docker-compose_all.yml` file you used to create the database at that time and modify the following content

Before modification
``` yaml
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    expose:
      - "3306:3306"
  xiaozhi-esp32-server-redis:
    ...
    expose:
      - 6379
```

After modification
``` yaml
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    ports:
      - "3306:3306"
  xiaozhi-esp32-server-redis:
    ...
    ports:
      - "6379:6379"
```

Note: Change `expose` under `xiaozhi-esp32-server-db` and `xiaozhi-esp32-server-redis` to `ports`. After modification, you need to restart. The following are the commands to restart mysql:

``` shell
# Enter the folder where your docker-compose_all.yml is located, for example, mine is xiaozhi-server
cd xiaozhi-server
docker compose -f docker-compose_all.yml down
docker compose -f docker-compose.yml up -d
```

After startup, use the `telnet` command on the host machine again to see if you can normally access the `3306` port of `mysql`.
``` shell
telnet 127.0.0.1 3306

telnet 127.0.0.1 6379
```
Normally, you should be able to access it this way.

## Step 2: Create Database and Tables
If your host machine can normally access the mysql database, create a database named `rag_flow` and a user `rag_flow` with password `infini_rag_flow` on mysql.

``` sql
-- Create database
CREATE DATABASE IF NOT EXISTS rag_flow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user and grant privileges
CREATE USER IF NOT EXISTS 'rag_flow'@'%' IDENTIFIED BY 'infini_rag_flow';
GRANT ALL PRIVILEGES ON rag_flow.* TO 'rag_flow'@'%';

-- Refresh privileges
FLUSH PRIVILEGES;
```

## Step 3: Download RAGFlow Project

You need to find a folder on your computer to store the RAGFlow project. For example, I use the `/home/system/xiaozhi` folder.

You can use the `git` command to download the RAGFlow project to this folder. This tutorial uses version `v0.22.0` for installation and deployment.
```
git clone https://ghfast.top/https://github.com/infiniflow/ragflow.git
cd ragflow
git checkout v0.22.0
```
After downloading, enter the `docker` folder.
``` shell
cd docker
```
Modify the `docker-compose.yml` file under the `ragflow/docker` folder, remove the `depends_on` configuration of the `ragflow-cpu` and `ragflow-gpu` services to remove the dependency of the `ragflow-cpu` service on `mysql`.

This is before modification:
``` yaml
  ragflow-cpu:
    depends_on:
      mysql:
        condition: service_healthy
    profiles:
      - cpu
  ...
  ragflow-gpu:
    depends_on:
      mysql:
        condition: service_healthy
    profiles:
      - gpu
```
This is after modification:
``` yaml
  ragflow-cpu:
    profiles:
      - cpu
  ...
  ragflow-gpu:
    profiles:
      - gpu
```

Next, modify the `docker-compose-base.yml` file under the `ragflow/docker` folder to remove the `mysql` and `redis` configurations.

For example, before deletion:
``` yaml
services:
  minio:
    image: quay.io/minio/minio:RELEASE.2025-06-13T11-33-47Z
    ...
  mysql:
    image: mysql:8.0
    ...
  redis:
    image: redis:6.2-alpine
    ...
```

After deletion
``` yaml
services:
  minio:
    image: quay.io/minio/minio:RELEASE.2025-06-13T11-33-47Z
    ...
```
## Step 4: Modify Environment Variable Configuration

Edit the `.env` file under the `ragflow/docker` folder, find the following configurations, search one by one, modify one by one! Search one by one, modify one by one!

For the modification of the `.env` file below, 60% of people will ignore the `MYSQL_USER` configuration causing RAGFlow to fail to start. Therefore, it needs to be emphasized three times:

First emphasis: If your `.env` file does not have the `MYSQL_USER` configuration, please add this item to the configuration file!

Second emphasis: If your `.env` file does not have the `MYSQL_USER` configuration, please add this item to the configuration file!

Third emphasis: If your `.env` file does not have the `MYSQL_USER` configuration, please add this item to the configuration file!

``` env
# Port settings
SVR_WEB_HTTP_PORT=8008           # HTTP port
SVR_WEB_HTTPS_PORT=8009          # HTTPS port
# MySQL configuration - modify to your local MySQL information
MYSQL_HOST=host.docker.internal  # Use host.docker.internal to let container access host services
MYSQL_PORT=3306                  # Local MySQL port
MYSQL_USER=rag_flow              # Username created above, if this item doesn't exist, add this item
MYSQL_PASSWORD=infini_rag_flow   # Password set above
MYSQL_DBNAME=rag_flow            # Database name

# Redis configuration - modify to your local Redis information
REDIS_HOST=host.docker.internal  # Use host.docker.internal to let container access host services
REDIS_PORT=6379                  # Local Redis port
REDIS_PASSWORD=                  # If your Redis doesn't have a password set, fill it like this, otherwise fill in the password
```

Note: If your Redis doesn't have a password set, you also need to modify `service_conf.yaml.template` under the `ragflow/docker` folder, replace `infini_rag_flow` with an empty string.

Before modification
``` shell
redis:
  db: 1
  password: '${REDIS_PASSWORD:-infini_rag_flow}'
  host: '${REDIS_HOST:-redis}:6379'
```
After modification
``` shell
redis:
  db: 1
  password: '${REDIS_PASSWORD:-}'
  host: '${REDIS_HOST:-redis}:6379'
```

## Step 5: Start RAGFlow Service
Execute command:
``` shell
docker-compose -f docker-compose.yml up -d
```
After successful execution, you can use the `docker logs -n 20 -f docker-ragflow-cpu-1` command to view the logs of the `docker-ragflow-cpu-1` service.

If there are no errors in the logs, it means the RAGFlow service has started successfully.

# Step 5: Register Account
You can access `http://127.0.0.1:8008` in your browser, click `Sign Up`, and register an account.

After successful registration, you can click `Sign In` to log in to the RAGFlow service. If you want to close the registration service of the RAGFlow service and don't want others to register accounts, you can set the `REGISTER_ENABLED` configuration item to `0` in the `.env` file under the `ragflow/docker` folder.

``` dotenv
REGISTER_ENABLED=0
```
After modification, restart the RAGFlow service.
``` shell
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d
```

# Step 6: Configure RAGFlow Service Models
You can access `http://127.0.0.1:8008` in your browser, click `Sign In`, and log in to the RAGFlow service. Click the `avatar` in the upper right corner of the page to enter the settings page.
First, in the left navigation bar, click `Model Providers` to enter the model configuration page. Under the `Available Models` search box on the right, select `LLM`, select the model provider you use from the list, click `Add`, and enter your key;
Then, select `TEXT EMBEDDING`, select the model provider you use from the list, click `Add`, and enter your key.
Finally, refresh the page, click the LLM and Embedding in the `Set Default Model` list respectively, and select the model you use. Please confirm that your key has enabled the corresponding service. For example, if the Embedding model I use is from xxx provider, I need to go to this provider's official website to check if this model needs to purchase a resource package to use.


# Part 2: Configure RAGFlow Service

# Step 1: Log in to RAGFlow Service
You can access `http://127.0.0.1:8008` in your browser, click `Sign In`, and log in to the RAGFlow service.

Then click the `avatar` in the upper right corner to enter the settings page. In the left navigation bar, click the `API` function, then click the "API Key" button. A dialog box appears,

In the dialog box, click the "Create new Key" button to generate an API Key. Copy this `API Key`, you will use it later.

# Step 2: Configure to Management Console
Make sure your management console version is `0.8.7` or above. Log in to the management console with a super administrator account.

First, you need to enable the knowledge base function. In the top navigation bar, click `Parameter Dictionary`, in the dropdown menu, click the `System Feature Configuration` page. Check `Knowledge Base` on the page, click `Save Configuration`. You can see the `Knowledge Base` function in the navigation bar.

In the top navigation bar, click `Model Configuration`, in the left navigation bar, click `Knowledge Base`. Find `RAG_RAGFlow` in the list, click the `Edit` button.

In `Service Address`, fill in `http://your RAGFlow service's LAN IP:8008`, for example, if my RAGFlow service's LAN IP is `192.168.1.100`, then I fill in `http://192.168.1.100:8008`.

In `API Key`, fill in the `API Key` you copied earlier.

Finally, click the save button.

# Step 2: Create a Knowledge Base
Log in to the management console with a super administrator account. In the top navigation bar, click `Knowledge Base`, click the `Add` button at the bottom left of the list. Fill in a name and description for the knowledge base. Click save.

To improve the LLM's understanding and recall ability of the knowledge base, it is recommended to fill in a meaningful name and description when creating the knowledge base. For example, if you want to create a knowledge base about `Company Introduction`, then the knowledge base name can be `Company Introduction`, and the description can be `Information about the company such as basic company information, service items, contact phone, address, etc.`.

After saving, you can see this knowledge base in the knowledge base list. Click the `View` button of the knowledge base you just created to enter the knowledge base details page.

In the knowledge base details page, click the `Add` button at the bottom left to upload documents to the knowledge base.

After uploading, you can see the uploaded documents in the knowledge base details page. At this time, you can click the `Parse` button of the document to parse the document.

After parsing is complete, you can view the parsed slice information. You can click the `Retrieval Test` button in the knowledge base details page to test the knowledge base's retrieval/recall function.

# Step 3: Let Xiaozhi Use RAGFlow Knowledge Base
Log in to the management console. In the top navigation bar, click `Agent`, find the agent you want to configure, click the `Configure Role` button.

On the left side of intent recognition, click the `Edit Functions` button, a dialog box pops up. Select the knowledge base you want to add in the dialog box. Save.
