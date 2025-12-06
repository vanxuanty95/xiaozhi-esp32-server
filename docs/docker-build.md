# Local Docker Image Compilation Method

This project now uses GitHub's automatic Docker compilation function. This document is prepared for friends who need to compile Docker images locally.

1. Install docker
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
2. Compile docker image
```
# Enter project root directory
# Compile server
docker build -t xiaozhi-esp32-server:server_latest -f ./Dockerfile-server .
# Compile web
docker build -t xiaozhi-esp32-server:web_latest -f ./Dockerfile-web .

# After compilation is complete, you can use docker-compose to start the project
# docker-compose.yml you need to modify to your compiled image version
cd main/xiaozhi-server
docker compose up -d
```
