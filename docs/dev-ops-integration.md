# All Modules Source Code Deployment Automatic Upgrade Method

This tutorial is for enthusiasts who deploy all modules from source code, on how to automatically pull source code, automatically compile, and automatically start ports through automatic commands. Achieve the most efficient system upgrade.

This project's test platform `https://2662r3426b.vicp.fun` has been using this method since it was opened, with good results.

The tutorial can refer to the video tutorial published by Bilibili blogger `Bile Labs`: [《Open Source Xiaozhi Server xiaozhi-server Automatic Update and Latest Version MCP Access Point Configuration Tutorial》](https://www.bilibili.com/video/BV15H37zHE7Q)

# Starting Conditions
- Your computer/server is a Linux operating system
- You have successfully run through the entire process
- You like to follow the latest features, but find manual deployment a bit troublesome each time, and look forward to having an automatic update method

The second condition must be met, because some files involved in this tutorial, such as JDK, Node.js environment, Conda environment, etc., are only available after you have run through the entire process. If you haven't run through it, when I mention a certain file, you may not know what it means.

# Tutorial Effects
- Solve the problem of not being able to pull the latest project source code in China
- Automatically pull code and compile frontend files
- Automatically pull code and compile java files, automatically kill port 8002, automatically start port 8002
- Automatically pull python code, automatically kill port 8000, automatically start port 8000

# Step 1: Choose Your Project Directory

For example, I planned my project directory to be, this is a newly created blank directory. If you don't want to make mistakes, you can do the same as me
```
/home/system/xiaozhi
```

# Step 2: Clone This Project
At this moment, first execute the first command to pull the source code. This command is suitable for servers and computers on domestic networks, no need to use a VPN

```
cd /home/system/xiaozhi
git clone https://ghproxy.net/https://github.com/xinnan-tech/xiaozhi-esp32-server.git
```

After execution, your project directory will have an additional folder `xiaozhi-esp32-server`, which is the project source code

# Step 3: Copy Basic Files

If you have successfully run through the entire process before, you won't be unfamiliar with the FunASR model file `xiaozhi-server/models/SenseVoiceSmall/model.pt` and your private configuration file `xiaozhi-server/data/.config.yaml`.

At this moment, you need to copy the `model.pt` file to the new directory. You can do this
```
# Create required directories
mkdir -p /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/

cp your original .config.yaml full path /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/.config.yaml
cp your original model.pt full path /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/models/SenseVoiceSmall/model.pt
```

# Step 4: Create Three Automatic Compilation Files

## 4.1 Automatically Compile manager-web Module
In the `/home/system/xiaozhi/` directory, create a file named `update_8001.sh` with the following content

```
cd /home/system/xiaozhi/xiaozhi-esp32-server
git fetch --all
git reset --hard
git pull origin main


cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web
npm install
npm run build
rm -rf /home/system/xiaozhi/manager-web
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web/dist /home/system/xiaozhi/manager-web
```

After saving, execute the permission command
```
chmod 777 update_8001.sh
```
After execution, continue

## 4.2 Automatically Compile and Run manager-api Module
In the `/home/system/xiaozhi/` directory, create a file named `update_8002.sh` with the following content

```
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main


cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api
rm -rf target
mvn clean package -Dmaven.test.skip=true
cd /home/system/xiaozhi/

# Find process number occupying port 8002
PID=$(sudo netstat -tulnp | grep 8002 | awk '{print $7}' | cut -d'/' -f1)

rm -rf /home/system/xiaozhi/xiaozhi-esp32-api.jar
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api/target/xiaozhi-esp32-api.jar /home/system/xiaozhi/xiaozhi-esp32-api.jar

# Check if process number is found
if [ -z "$PID" ]; then
  echo "No process found occupying port 8002"
else
  echo "Found process occupying port 8002, process number: $PID"
  # Kill process
  kill -9 $PID
  kill -9 $PID
  echo "Process $PID killed"
fi

nohup java -jar xiaozhi-esp32-api.jar --spring.profiles.active=dev &

tail tail -f nohup.out
```

After saving, execute the permission command
```
chmod 777 update_8002.sh
```
After execution, continue

## 4.3 Automatically Compile and Run Python Project
In the `/home/system/xiaozhi/` directory, create a file named `update_8000.sh` with the following content

```
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main

# Find process number occupying port 8000
PID=$(sudo netstat -tulnp | grep 8000 | awk '{print $7}' | cut -d'/' -f1)

# Check if process number is found
if [ -z "$PID" ]; then
  echo "No process found occupying port 8000"
else
  echo "Found process occupying port 8000, process number: $PID"
  # Kill process
  kill -9 $PID
  kill -9 $PID
  echo "Process $PID killed"
fi
cd main/xiaozhi-server
# Initialize conda environment
source ~/.bashrc
conda activate xiaozhi-esp32-server
pip install -r requirements.txt
nohup python app.py >/dev/null &
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

After saving, execute the permission command
```
chmod 777 update_8000.sh
```
After execution, continue

# Daily Updates

After all the above scripts are created, for daily updates, we only need to execute the following commands in order to achieve automatic update and startup

```
cd /home/system/xiaozhi
# Update and start Java program
./update_8001.sh
# Update web program
./update_8002.sh
# Update and start python program
./update_8000.sh


# Later if you want to view java logs, execute the following command
tail -f nohup.out
# Later if you want to view python logs, execute the following command
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

# Notes
The test platform `https://2662r3426b.vicp.fun` uses nginx for reverse proxy. Detailed nginx.conf configuration can be [referenced here](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)

## Common Issues

### 1. Why don't I see port 8001?
Answer: 8001 is used in the development environment, for running the frontend port. If you are deploying on a server, it is not recommended to use `npm run serve` to start port 8001 to run the frontend. Instead, compile it into html files like this tutorial, and then use nginx to manage access.

### 2. Do I need to manually update SQL statements every time I update?
Answer: No, because the project uses **Liquibase** to manage database versions, it will automatically execute new sql scripts.
