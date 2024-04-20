@echo off
setlocal EnableDelayedExpansion

echo Resetting Database...
psql -U postgres -c "DROP DATABASE \"iot-platform-database\""
echo Database deleted!

title Windows Activation Script

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
	shift
	shift
) else (
	echo Error - Postgres username parameter naming error
	goto end
)
if /I "%~1" == "-postgres_password" (
    set postgres_password=%2
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
<<<<<<< HEAD
psql -U postgres -c "CREATE DATABASE \"iot-platform-database\""
=======
psql -U postgres -c "CREATE DATABASE \"iot-platform-database\"" > nul 2> nul
>>>>>>> 419bb0cf9cdeda47925db2942536d054a3edb43f
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"iot-platform-database\" TO postgres" > nul 2> nul
echo Database ready!


echo Starting Cloud App...
cd cloud
start "Cloud App" java -jar app.jar
cd ..
echo Cloud App ready!

cd src

echo Starting Sensors Client...
<<<<<<< HEAD
start "Sensors Client" python.exe "sensor_devices.py"
=======
start "Sensor Dispatcher" python.exe "sensor_devices.py"
>>>>>>> 419bb0cf9cdeda47925db2942536d054a3edb43f
echo Sensors Started!

echo Starting IoT Gateway...
start "IoT Gateway" python.exe "app.py"
echo IoT Gateway started!

start "REST API" python.exe "rest_api.py"

REM cd ..
REM dir
REM cd ..
REM dir
REM cd iot-cloud-dashboard
REM dir
npm start --prefix ..\iot-cloud-dashboard

echo System is running!
goto clean_end

:end
echo Exiting script!
exit /b 1

:clean_end