## Prerequisites
- Python3 (recommended version: 3.12)
- PostgreSQL Server (running on port 5432)
- Mosquitto Broker (recommended version: 2.0.11)
- JDK (recommended version: 17 or above)
- NodeJS (recommended version: 12 or above)
- React (recommended version: 18.2.0 or above)
- A way to connect to the CAN node, e.g. Putty

## Start CAN
CAN script (generator.sh) is a shell script executable on a Linux kernel. It will periodically send simulated sensor data across an existing CAN bus. Plug in the CAN bus to the appropriate device and the current machine via PEAK System CAN-USB converter. The script can be transfered to the device via a program like WinSCP. Run the script on the CAN device as follows
```
shell path\to\script\generator.sh
```


## Set Environment Variables
Environment variables can be set globally, or for a specific terminal session
For a specific terminal session

- Connection String
    ```
    set "POSTGRESQL_URL=jdbc:postgresql://localhost:5432/iot-platform-database"
    ```
- Username
    ```
    set "POSTGRESQL_USER=your_postgres_username"
    ```
- Password
   ```
    set "POSTGRESQL_PASSWORD=your_postgres_password"
    ```

- Cloud MQTT client ID
   ```
   set "CLOUD_MQTT_CLIENT_ID=my_test_cloud_client"
   ```
-   Environment variables for the React App
    ```
    set "REACT_APP_API_URL=http://localhost:8080/iot-cloud-platform"
    ```

- Additional variables
    ```
    set "HISTORY=1"
    ```

## Mosquitto Brokers Setup
Two broker must run at the same time, one on port 1883 and the other on 1884 and  'users' file must be specified, with username and password mappings in the following format

    iot-device:hashed_password
    
File named 'users' must be inside 'config' folder which has to be manually created inside the directory where mosquitto is installed.

Log files must be inside 'log' folder which has to be manually created inside the directory where mosquitto is installed.

Two config file must be made with the following configurations
    
    allow_anonymous false
    listener 1883
    persistence true
    persistence_file mosquitto1.db
    persistence_location data
    log_dest file log/mosquitto1.log
    password_file config/users

The other configuration file will differ on line 2 (port will be 1884), line 4 (persistence_file will be mosquitto2.db) and line 6 (log_dest file will be log/mosquitto2.log).

Navigate to the directory where the mosquitto is installed, and run both of the brokers with 
```
start "Sensors Mosquitto" mosquitto -c mosquitto1.conf
start "Gateway Mosquitto" mosquitto -c mosquitto2.conf
```

## Creating Postgres Database
```
psql -U postgres -c "CREATE DATABASE \"iot-platform-database\"" > nul 2> nul
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"iot-platform-database\" TO postgres" > nul 2> nul
```
WARNING: This specific database name must be used!

## Installing Python Requirements
Navigate to the root folder of the project, then install python requirements using pip
```
pip install -r requirements.txt
```

## Run
First option is to run the system using script:
```
exe_script.bat -postgres_username you_postgres_username -postgres_password your_postgres_password
```

If the 'exe_script.bat' script is used for running the system , it is required to manually create 'mosquitto' folder in the root folder of this repository.

```
mkdir mosquitto
cd mosquitto
```

Inside 'mosquitto' folder, 'mosquitto1.conf' and 'mosquitto2.conf' files have to be created. Content of these files was described [previously](#mosquitto-brokers-setup). 

```
touch mosquitto1.conf
touch mosquitto2.conf
```

Also, inside 'mosquitto' folder it is required to create 'config' folder which contains 'users' file. Content of this file was described [previously](#mosquitto-brokers-setup).
```
mkdir config
cd config
touch users
```

Last step for 'mosquitto' folder is to create nested 'log' folder. In this step, assumption is that user is positioned in the mosquitto folder.
```
mkdir log
```

For everything to work as expected, it is supposed to create 'cloud' folder inside the root folder of this repository. Newly created folder should contain JAR file 
of the Spring Boot cloud repository, and the JAR file should be named 'app'. In this step, assumption is that user is positioned in the root folder of this repository.
```
mkdir cloud
```



Second option is to run the system manually:
```
start "Cloud Service" java -jar app.jar
start "Sensor Dispatcher" python.exe sensor_devices.py
start "IoT Gateway" python.exe app.py
start "REST API" python rest_api.py
```
WARNING: These specific process name must be used, so that the shutdown script can recognize them!
Install npm on your machine. If you already have it installed, run
```
npm install react-scripts
```
inside of the dashboard folder. For the execution script to be executed successfully (which does include booting up the dashboard), the dashboard folder will have to be in the same root folder as the gateway app.

Run the dashboard with
```
npm start
```
inside the dashboard folder.
## OPTIONAL - Starting the dashboard for data visualization from the cloud

## Shutdown
Shut down the system using
```
shutdown_script.bat
```