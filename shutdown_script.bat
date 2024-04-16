@echo off
setlocal EnableDelayedExpansion

title Windows Shutdown Script

set sensors_mosquitto_window_title=Sensors Mosquitto
set gateway_mosquitto_window_title=Gateway Mosquitto
set sensor_dispatcher_window_title=Sensor Dispatcher
set cloud_window_title=Cloud App
set gateway_window_title=IoT Gateway
set rest_window_title=REST API

set main_console_window_title=Windows Activation Script

taskkill /FI "WINDOWTITLE equ %sensors_mosquitto_window_title%" /F >nul 2>&1
if %errorlevel% equ 0 ( echo %sensors_mosquitto_window_title% shut down! )

taskkill /FI "WINDOWTITLE eq %gateway_mosquitto_window_title%" /F >nul 2>&1
if %errorlevel% equ 0 ( echo %gateway_mosquitto_window_title% shut down! )

taskkill /FI "WINDOWTITLE eq %sensor_dispatcher_window_title%" /F >nul 2>&1
if %errorlevel% equ 0 ( echo %sensor_dispatcher_window_title% shut down! )

taskkill /FI "WINDOWTITLE eq %cloud_window_title%" /F >nul 2>&1
if %errorlevel% equ 0 ( echo %cloud_window_title% shut down! )

taskkill /FI "WINDOWTITLE eq %gateway_window_title%" /F >nul 2>&1
if %errorlevel% equ 0 ( echo %gateway_window_title% shut down! )

taskkill /FI "WINDOWTITLE eq %rest_window_title%" /F >nul 2>&1
if %errorlevel% equ 0 ( echo %rest_window_title% shut down! )

netstat -ano | findstr 0.0.0.0:3000 > react.txt

set react_process=
for /f "usebackq delims=" %%a in ("react.txt") do (
    set "react_process=!react_process!%%a"
)

for /f "tokens=5" %%a in ("!react_process!") do (
	set "pid=%%a"
)
set "pid=%pid:~-5%"

taskkill /PID %pid% /F >nul 2>&1
if %errorlevel% equ 0 ( echo React App shut down! )

del react.txt