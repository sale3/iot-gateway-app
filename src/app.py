"""Main gateway application.

app
============
Module that contains main iot gateway logic.

Functions
---------
signup_periodically(key, username, password, time_pattern, url, interval)
    Periodically initiates device signup on cloud services.
on_connect_protocol_data_handler(client, userdata, flags, return_code,props)
    Logic executed after successfully connecting protocol data sensor to MQTT broker.
collect_protocol_data(config, flag, gcb_queue)
    Collects protocol data and periodically initiates data processing and forwarding.
main()
    Iot gateway app entrypoint.

Constants
---------
CONF_PATH: str
    App config file path.
USER: str
    Device username.
PASSWORD: str
    Device password.
SERVER_URL: str
    Cloud services' URL.
AUTH_INTERVAL: int
    Time lapse between signup requests.
TIME_FORMAT: str
    Time format.
SERVER_TIME_FORMAT: str
    Server's time format.
FUEL_LEVEL_LIMIT:
    Critical level of fuel.
TEMP_INTERVAL: int
    Time lapse between temperature cloud service requests.
LOAD_INTERVAL = "load_interval"
    Time lapse between load cloud service requests.
API_KEY: str
    Cloud platform API key.
TRANSPORT_PROTOCOL: str
    Transport protocol for MQTT.
HTTP_UNAUTHORIZED: int
TEMP_ALARM_TOPIC: str
    MQTT alarm topic for temperature alarms
LOAD_ALARM_TOPIC: str
    MQTT alarm topic for load alarms
FUEL_ALARM_TOPIC: str
    MQTT alarm topic for fuel alarms
    Http status code.
PROTOCOL_TOPIC: str
    MQTT protocol data topic
HTTP_OK: int
    Http status code.
HTTP_NO_CONTENT: int
    Http status code.
QOS: int
    Quality of service of MQTT.
mqtt_broker_local: str
    Reference of local mqtt broker
"""

import auth
import data_service
import time
import logging.config
import paho.mqtt.client as mqtt
import atexit
import re
import signal
from threading import Thread, Event
from mqtt_util import MQTTConf, GcbService, \
    GCB_PROTOCOL_TOPIC
from src.can_protocol import start_protocol_mqtt, processed_ids, get_data_by_id
from config_util import ConfFlags, \
    start_config_observer
from mqtt_utils import MQTTClient
from config_util import Config
from data_service import EMPTY_PAYLOAD
from signal_control import BetterSignalHandler

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

CONF_PATH = "configuration/app_conf.json"
USER = "username"
PASSWORD = "password"
SERVER_URL = "server_url"
AUTH_INTERVAL = "auth_interval"
TIME_FORMAT = "time_format"
SERVER_TIME_FORMAT = "server_time_format"

CAN_GENERAL_SETTINGS = "can_general_settings"
INTERFACE = "interface"
CHANNEL = "channel"
BITRATE = "bitrate"

API_KEY = "api_key"
MQTT_BROKER = "mqtt_broker"
MQTT_BROKER_LOCAL = "mqtt_broker_local"
ADDRESS = "address"
PORT = "port"
TRANSPORT_PROTOCOL = "tcp"
PROTOCOL_TOPIC = "sensors/protocol"
HTTP_UNAUTHORIZED = 401
HTTP_OK = 200
HTTP_NO_CONTENT = 204
QOS = 2

TEMP_ALARM_TOPIC = "alarms/temperature"
LOAD_ALARM_TOPIC = "alarms/load"
FUEL_ALARM_TOPIC = "alarms/fuel"

protocol_data = {}


def signup_periodically(key, username, password, time_pattern, url, interval):
    """
    Periodically requests device signup.

    Parameters
    ----------
    key: str
        API key.
    username: str
        Device's username,
    password: str
        Device's password,
    time_pattern: str
        Device's time pattern.
    url: str
        Cloud services URL.
    interval: int
        Time lapse between consecutive requests.

    Returns
    -------
    jwt: str
        JSON web token for accessing cloud services.
    """
    jwt = None
    while jwt is None:
        customLogger.debug("Trying to sign up!")
        jwt = auth.register(key, username, password, time_pattern, url)
        time.sleep(interval)
    customLogger.debug("Successful sign up!")
    return jwt


def on_connect_protocol_data_handler(client, userdata, flags, return_code, props):
    """
    Logic executed after successfully connecting protocol data sensor to MQTT broker.

    Parameters
    ----------
    client: mqtt.client
    userdata: object
    flags:
    rc: int
    props:
    """
    if return_code == 0:
        infoLogger.info(
            "Protocol data handler successfully established connection with MQTT broker!")
        customLogger.info(
            "Protocol data handler successfully established connection with MQTT broker!")
        client.subscribe(PROTOCOL_TOPIC, qos=QOS)
    else:
        errorLogger.error(
            "Protocol data handler failed to establish connection with MQTT broker!")
        customLogger.critical(
            "Protocol data handler failed to establish connection with MQTT broker!")


# iot data aggregation and forwarding to cloud
def collect_protocol_data(config, flag, gcb_queue):
    """
    Protocol data handler logic.

    Establishes connection with MQTT broker. Listens for incoming messages. Receives the message and starts
    a new thread if it wasn't started. Appends data in the dictionary for a certain thread.

    Parameters
    ----------
    config: Config
        Configuration object
    flag: multithreading.Event
        Object used for stopping protocol data process.
    gcb_queue: queue.Queue
        Belongs to some GcbService instance and is used to queue payload that is to
        be sent via mqtt.
    """
    sensors_broker_client = MQTTClient(
        "protocol-data-handler-mqtt-client",
        transport_protocol=TRANSPORT_PROTOCOL,
        protocol_version=mqtt.MQTTv5,
        mqtt_username=config.mqtt_broker_username,
        mqtt_pass=config.mqtt_broker_password,
        broker_address=config.mqtt_broker_address,
        broker_port=config.mqtt_broker_port,
        keepalive=config.temp_settings_interval * 3,
        infoLogger=infoLogger,
        errorLogger=errorLogger,
        flag=flag,
        sensor_type="PROTOCOL",
    )

    def on_message_handler(client, userdata, message):
        # Extract data id and value
        data = message.payload.decode("utf-8")
        data_id_pattern = r"data_id=(\d+)"
        value_pattern = r"value=(\d+)"

        # Regex search
        data_id_match = re.search(data_id_pattern, data)
        data_id_str = data_id_match.group(1)
        data_id = int(data_id_str)
        value_match = re.search(value_pattern, data)
        value_str = value_match.group(1)
        value = float(value_str)

        protocol_data_entity = get_data_by_id(data_id)

        # If protocol data identifier is not in processed_ids
        # Start a new thread
        if protocol_data_entity.id not in processed_ids:
            # Dictionary key is supposed to be ProtocolDataEntity id
            # Value for each key is thread started and information whether the thread is active
            protocol_data[protocol_data_entity.id] = []
            thread = Thread(target=parse_protocol_data, args=(config, flag, protocol_data_entity,
                                                              gcb_queue, sensors_broker_client))
            processed_ids[protocol_data_entity.id] = {"thread": thread, "stopped": False}
            thread.start()
        # Append new data so that protocol data thread can work with it
        # This data is later removed and aggregated
        protocol_data[protocol_data_entity.id].append(value)
        customLogger.info("Received protocol data: " + str(data))

    # On program exit, disconnect Protocol MQTT broker
    def cleanup():
        sensors_broker_client.disconnect()

    # Register cleanup function
    atexit.register(cleanup)

    sensors_broker_client.set_on_connect(on_connect_protocol_data_handler)
    sensors_broker_client.set_on_message(on_message_handler)
    sensors_broker_client.connect()


def parse_protocol_data(config, flag, protocol_data_entity, gcb_queue, client):
    """
    Thread function to aggregate protocol data and send it to cloud.

    Parameters
    ----------
    config: Config
        Configuration object
    flag: multithreading.Event
        Object used for stopping protocol data process.
    protocol_data_entity: ProtocolDataEntity
        Object which parses data based on class attributes.
    gcb_queue: queue.Queue
        Belongs to some GcbService instance and is used to queue payload that is to
        be sent via mqtt.
    """
    interval = protocol_data_entity.transmit_interval
    # If program still runs or protocol data is not stopped
    # Protocol data is stopped in protocol_mqtt module if user remove the protocol from device
    while not flag.is_set() and processed_ids[protocol_data_entity.id]["stopped"] is False:
        data = []
        # Extract data for a certain protocol data
        for i in protocol_data[protocol_data_entity.id]:
            data.append(i)
        # Clear extracted data so there are no duplicates
        protocol_data[protocol_data_entity.id].clear()
        if len(data) > 0:
            # Aggregate data
            payload = data_service.handle_protocol_data(protocol_data_entity, data, config.time_format)
            if payload != EMPTY_PAYLOAD:
                if protocol_data_entity.mode == "OUTPUT":
                    # Send data to cloud
                    GcbService.push_message(gcb_queue, GCB_PROTOCOL_TOPIC, payload)
                    if ("engine temperature" in protocol_data_entity.name.lower()) and payload["value"] > 95:
                        customLogger.info(
                            "Temperature of " + str(payload["value"]) + " C is too high! Sounding the alarm!")
                        client.publish(TEMP_ALARM_TOPIC, True, QOS)
                    if ("fuel level" in protocol_data_entity.name.lower()) and payload["value"] < 10:
                        customLogger.info(
                            "Fuel level of " + str(payload["value"]) + " l is too low! Sounding the alarm!")
                        client.publish(FUEL_ALARM_TOPIC, True, QOS)
                    if "load" in protocol_data_entity.name.lower() and payload["value"] > 1000:
                        customLogger.info("Load of " + str(payload["value"]) + " kg is too high! Sounding the alarm!")
                        client.publish(LOAD_ALARM_TOPIC, True, QOS)
                    customLogger.info("PROTOCOL DATA PUBLISHED TO CLOUD")
            else:
                infoLogger.warning("There is no sensor data to handle!")
        time.sleep(interval)

    # After user removed protocol from the device, delete it from processed_ids
    del processed_ids[protocol_data_entity.id]
    customLogger.debug("Protocol data with name " + protocol_data_entity.name + " stopped!")


def main():
    """Start IoT gateway app entrypoint."""
    # used for restarting device due to jwt expiration

    # used as an indicator for termination request for main loop
    main_execution_flag = Event()

    while not main_execution_flag.is_set():
        config = Config(CONF_PATH, errorLogger, customLogger)
        config.try_open()
        # if config is read successfully, start app logic
        if config is not None:
            infoLogger.info("IoT Gateway app started!")
            customLogger.debug("IoT Gateway app started!")

            conf_flags = ConfFlags()
            conf_observer = start_config_observer(conf_flags)

            gcb_service = GcbService(config.iot_username,
                                     config.iot_username + "_gcb_client_id",
                                     MQTTConf.from_app_config(config, "gateway_cloud_broker"))
            gcb_service.start()

            # iot cloud platform login

            jwt = auth.login(config.iot_username,
                             config.iot_password,
                             config.server_url + "/auth/login")
            # if failed, periodically request signup
            if jwt is None:
                customLogger.error(
                    "Login failed! Trying to sign up periodically!")
                jwt = signup_periodically(
                    config.api_key,
                    config.iot_username,
                    config.iot_password,
                    config.server_time_format,
                    config.server_url + "/auth/signup",
                    config.auth_interval)
            else:
                customLogger.debug("Login successful!")
            # now JWT required for Cloud platform auth is stored in jwt var
            customLogger.info("Received JWT: " + jwt)
            # starting stats collecting

            # using shared memory Queue objects for returning stats data from
            # processes
            customLogger.debug("Initializing devices stats data!")

            protocol_handler_flag = Event()

            BetterSignalHandler([signal.SIGINT,
                                 signal.SIGTERM],
                                [protocol_handler_flag,
                                 main_execution_flag])

            customLogger.debug("Starting workers!")
            # creates and starts protocol data handling worker

            protocol_data_handler = Thread(
                target=collect_protocol_data,
                args=(
                    config,
                    protocol_handler_flag,
                    gcb_service.queue
                )
            )
            protocol_data_handler.start()
            time.sleep(1)

            # Protocol MQTT module is reponsible for gateway-cloud protocol communication
            start_protocol_mqtt(main_execution_flag)

            # waiting fow worker to stop
            protocol_data_handler.join()
            customLogger.debug("Workers stopped!")

            conf_observer.stop()
            conf_observer.join()

            gcb_service.stop()
        else:
            customLogger.critical("Cant read config file! Aborting...")


if __name__ == '__main__':
    main()
