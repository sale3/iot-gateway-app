@echo off
setlocal EnableDelayedExpansion
title Windows Iot Gateway Activation Script

set postgres_username=
set postgres_password=

if "%~1" == "" (
	echo Error - No parameters provided
	goto end
) 

set argC=0
for %%x in (%*) do Set /A argC+=1

if NOT "%argC%" == "4" (
	echo Error - Not all parameters provided
	goto end
)

if /I "%~1" == "-postgres_username" (
	set postgres_username=%2
	echo POSTGRES_USERNAME1: !postgres_username!
	shift
	shift
) else (
	echo Error - Postgres username parameter naming error
	goto end
)
if /I "%~1" == "-postgres_password" (
    set postgres_password=%2
	echo POSTGRES_PASSWORD1: !postgres_password!
    shift
    shift
) else (
	echo Error - Postgres password parameter naming error
	goto end
)

echo Starting mosquitto brokers...
cd mosquitto
start "Sensors Mosquitto" mosquitto -c mosquitto1.conf
start "Gateway Mosquitto" mosquitto -c mosquitto2.conf
cd ..
echo Mosquitto brokers started!

set "POSTGRESQL_URL=jdbc:postgresql://localhost:5432/iot-platform-database"
set "POSTGRESQL_USER=!postgres_username!"
set "POSTGRESQL_PASSWORD=!postgres_password!"
set "CLOUD_MQTT_CLIENT_ID=my_test_cloud_client"
set "REACT_APP_API_URL=http://localhost:8080/iot-cloud-platform"
set "HISTORY=1"

echo Setting up database...
psql -U postgres -c "CREATE DATABASE \"iot-platform-database\"" > nul 2> nul
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"iot-platform-database\" TO postgres" > nul 2> nul
echo Database ready!


echo Starting Cloud App...
cd cloud
start "Cloud App" java -jar app.jar
cd ..
echo Cloud App ready!

cd src

echo Starting Sensors Client...
start "Sensors Client" python.exe "sensor_devices.py"
echo Sensors Started!

echo Starting IoT Gateway...
start "IoT Gateway" python.exe "app.py"
echo IoT Gateway started!

start "REST API" python.exe "rest_api.py"

cd ..
cd ..
cd iot-cloud-dashboard
npm start

echo System is running!
goto clean_end


:end
echo Exiting script!
exit /b 1

:clean_end