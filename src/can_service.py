"""
can_service
============
Module that provides functionality for CAN bus communication.

Classes
-------
CANListener: A class that accepts messages from the CAN bus

Functions
---------
read_can(execution_flag, config_flag, init_flags, can_lock)
    Thread execution function from sensor_devices main() for CAN communication
stop_can(notifier, bus, protocol_client)
    Used for stopping all CAN functionalities
init_mqtt_clients(bus, config, flag)
    Used for initializing MQTT clients that publish read CAN messages
on_publish(topic, payload, qos)
    Event handler for published messages to a MQTT topic
on_subscribe_protocol(client, userdata, flags, rc, props)
    Event handler for protocol client MQTT subscription

Constants
---------
app_conf_file_path: str
    Path to the configuration file
transport_protocol: str
    JSON key for MQTT transport protocol
protocol_topic: str
    MQTT topic for protocol data
data_pattern: str
    Format by which data is sent to MQTT brokers
protocol_data_pattern: str
    Format by which protocol data is sent to MQTT brokers
qos: int
    Quality of service of MQTT.
"""
import can
import logging.config
import paho.mqtt.client as mqtt
import logging
import time
import threading
import struct
import json
from threading import Thread
import mqtt_util
import signal
from multiprocessing import Event
from signal_control import BetterSignalHandler
from mqtt_utils import MQTTClient
from can.listener import Listener
from can.interface import Bus
from config_util import Config
from can_protocol import get_data_by_can_id, get_data_by_id

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger("customConsoleLogger")

APP_CONF_FILE_PATH = "configuration/app_conf.json"
TRANSPORT_PROTOCOL = "tcp"
PROTOCOL_TOPIC = "sensors/protocol"
PROTOCOL_INPUT_TOPIC = "sensors/protocol-input"
PROTOCOL_VALUE_TOPIC = "gateway/protocol-value"
PROTOCOL_DATA_PATTERN = "[ value={} , time={} , data_id={} ]"
TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
INTERVAL = "period"
MQTT_USER = "username"
MQTT_PASSWORD = "password"
MQTT_BROKER = "mqtt_broker"
ADDRESS = "address"
PORT = "port"

QOS = 2
TEMP_ALARM_TOPIC = "alarms/temperature"
LOAD_ALARM_TOPIC = "alarms/load"
FUEL_ALARM_TOPIC = "alarms/fuel"
lock = threading.Lock()
processed_ids = {}


def parse_input_protocol_data(flag, value, protocol_data_from_db, bus):
    """
    Sends periodic CAN messages based on protocol data and user input.
    Stop sending when the specified condition is met.

    Args:
    ----
    flag: threading.Event
        An event used to signal when to stop the operation.
    value: float
        The value to be included in the CAN message.
    protocol_data_from_db: ProtocolDataEntity
        Contains protocol data information.
    bus: object
        The CAN bus object used to send messages.
    """
    customLogger.debug("Thread with name " + protocol_data_from_db.name + " started!")

    interval = protocol_data_from_db.transmit_interval
    hex_string = '0x' + str(protocol_data_from_db.can_id)

    value += protocol_data_from_db.offset_value
    if protocol_data_from_db.divisor != 0:
        value /= protocol_data_from_db.divisor
    if protocol_data_from_db.multiplier != 0:
        value *= protocol_data_from_db.multiplier
    byte_array = struct.pack('d', value)
    extracted_value = extract_bits(byte_array, protocol_data_from_db.start_bit,
                                   protocol_data_from_db.num_bits)
    # Value is divided by 10.0 because the idea is to work with double values
    # Script generates integer values (multiplied by 10)
    # So, division by 10.0 is used to correct that problem
    extracted_double_value = extracted_value / 10.0
    extracted_value_byte_array = struct.pack('d', extracted_double_value)
    can_message = can.Message(
        arbitration_id=int(hex_string, 16), data=extracted_value_byte_array, is_extended_id=False,
        is_remote_frame=False
    )
    task = bus.send_periodic(can_message, interval)

    # While application is still running or thread is not stopped
    while not flag.is_set() and processed_ids[protocol_data_from_db.id]["stopped"] is False:
        pass

    # After user removed protocol from the device, delete it from processed_ids
    del processed_ids[protocol_data_from_db.id]
    task.stop()
    customLogger.debug("Thread with name " + protocol_data_from_db.name + " stopped!")


def extract_bits(byte_array, start_bit, length):
    """
    Converts byte array to bits and extract bits from start bit to start
    bit plus number of bits.

    Args:
    ----
        byte_array: bytearray
            The byte array containing the CAN message data.
        start_bit: int
            The starting bit position of the field to extract (0-indexed, LSB first).
        length: int
            The length of the field in bits.

    Returns:
    -------
        int: The extracted bit field value.
    """
    # Convert byte array to bits
    bits = ''.join(f'{byte:08b}' for byte in byte_array)
    reversed_bits = bits[::-1]
    # Extract bits
    extracted_bits_reversed = reversed_bits[start_bit:start_bit + length]
    extracted_bits = extracted_bits_reversed[::-1]
    # Convert bits to integer
    integer_value = int(extracted_bits, 2)
    return integer_value


def read_can(execution_flag, can_lock):
    """
    Thread execution function from sensor_devices main() for CAN communication
    It connects to an instance of CAN bus, which is then tied to a Notifier object, which listens to the bus for
    incoming messages

    Args:
    ----
        execution_flag: multithreading.Event
            Token used for stopping CAN thread.
        config_flag: multithreading.Event
            Token used for detecting configuration changes
        init_flags: InitFlags
            Object that keeps track of initiated threads
        can_lock: multithreading.Lock
            Used to prevent race condition

    """
    customLogger.debug("CAN process started!")

    period = 2

    # if the counter reaches 5, 10 seconds have passed, and then the check is made whether the bus
    # is idle
    period_counter = 0
    # the mechanism for bus idleness detection is relied upon a basic check for the
    # number of received messages. If the number of received messages is equal to the number of the previous check
    # (the previous check 10 seconds ago), then the bus is idle, and is not transmitting any messages.
    previous_message_counter = 0
    bus = None
    can_listener = None
    initial = True
    notifier = None
    protocol_client = None

    try:
        while not execution_flag.is_set():
            if initial:

                config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
                config.try_open()
                stop_can(notifier, bus, protocol_client)

                interface_value = config.can_interface
                channel_value = config.can_channel
                bitrate_value = config.can_bitrate

                bus = Bus(interface=interface_value,
                          channel=channel_value,
                          bitrate=bitrate_value)
                protocol_client = init_mqtt_clients(
                    bus, config, execution_flag)
                notifier = can.Notifier(bus, [], timeout=period)
                can_listener = CANListener(protocol_client)
                notifier.add_listener(can_listener)
                initial = False
            time.sleep(period)
            period_counter += 1

            if can_listener is not None:
                if period_counter == 5:
                    period_counter = 0
                    if can_listener.message_counter == previous_message_counter:
                        customLogger.debug("CAN BUS is not active.")
                previous_message_counter = can_listener.message_counter

    except Exception:
        errorLogger.error("CAN BUS has been shut down.")
        customLogger.debug("CAN BUS has been shut down.")

    can_lock.acquire()
    can_lock.release()

    stop_can(notifier, bus, protocol_client)
    execution_flag.clear()
    customLogger.debug("CAN process shutdown!")


def stop_can(notifier, bus, protocol_client):
    """
    Used for stopping all CAN functionalities

    Args:
    ----
        notifier: can.Notifier
            Object that listens to incoming CAN messages
        bus: can.Bus
            CAN bus
        protocol_client: mqtt_utils.MQTTClient
            Protocol data MQTT broker client

    """
    if notifier is not None:
        notifier.stop(timeout=5)
    if protocol_client is not None:
        protocol_client.disconnect()
    if bus is not None:
        bus.shutdown()


def init_mqtt_clients(
        bus,
        config,
        flag):
    """
    Used for stopping all CAN functionalities

    Args:
    ----
        bus: can.Bus
            CAN bus
        config: Config
            Class holding configuration parameters
            In this case, used for MQTT
        flag: Flag
            Used for stopping MQTT client
    """
    def on_message_protocol_alarm(client, userdata, msg):
        try:
            topic = msg.topic
            print("Topic is " + topic)
            if topic == PROTOCOL_INPUT_TOPIC:
                payload = msg.payload.decode('utf-8')
                data = json.loads(payload)
                type = data["type"]
                action = data["action"]

                if type == "can_message":
                    if action == "send":
                        data_id = data["dataId"]
                        protocol_data_from_db = get_data_by_id(data_id)
                        value = data["value"]
                        customLogger.info(
                            f"Received protocol input set message: type={type}, "
                            f"action={action}, dataId={data_id}, value={value}")
                        # Start a new thread which will send data periodically
                        if protocol_data_from_db.id not in processed_ids:
                            thread = Thread(target=parse_input_protocol_data, args=(flag, value,
                                                                                    protocol_data_from_db, bus,))
                            processed_ids[protocol_data_from_db.id] = {"thread": thread,
                                                                       "stopped": False, "value": value}
                            thread.start()
                        customLogger.info("Received protocol input data: " + str(data))
                    elif action == "stop":
                        # Stop data sending if user wants to
                        data_id = data["dataId"]
                        processed_ids[data_id]["stopped"] = True
                    elif action == "remove":
                        # If protocol is removed from the device stop all relevant threads
                        protocol_data_ids = data["protocol_data_ids"]
                        for id in protocol_data_ids:
                            if id in processed_ids:
                                processed_ids[id]["stopped"] = True
                    elif action == "get_current_values":
                        # Data returned to cloud so user has the latest info about sending
                        filtered_data = [
                            {"id": 0, "dataId": id_, "value": data["value"]}
                            for id_, data in processed_ids.items()
                            if not data["stopped"]
                        ]
                        message = json.dumps(filtered_data)
                        gateway_client = mqtt_util.gcb_init_publisher(
                            "protocol-input-value-publisher-client-id",
                            config.gateway_cloud_broker_iot_username,
                            config.gateway_cloud_broker_iot_password)
                        mqtt_util.gcb_connect(gateway_client, config.gateway_cloud_broker_address,
                                              config.gateway_cloud_broker_port)
                        gateway_client.publish(PROTOCOL_VALUE_TOPIC, message, 2)
                        gateway_client.loop_start()
                        # Without sleep client disconnects too fast and doesn't send MQTT message
                        time.sleep(1)
                        gateway_client.loop_stop()
                        gateway_client.disconnect()
            elif topic == TEMP_ALARM_TOPIC:
                can_message = can.Message(arbitration_id=0x120,
                                          data=[bool(msg.payload)],
                                          is_extended_id=False,
                                          is_remote_frame=False)
                bus.send(msg=can_message, timeout=5)
                customLogger.info(
                    "Temperature alarm registered! Forwarding to CAN!")
            elif topic == LOAD_ALARM_TOPIC:
                can_message = can.Message(arbitration_id=0x121,
                                          data=[bool(msg.payload)],
                                          is_extended_id=False,
                                          is_remote_frame=False)
                bus.send(msg=can_message, timeout=5)
                customLogger.info("Load alarm registered! Forwarding to CAN!")
            elif topic == FUEL_ALARM_TOPIC:
                can_message = can.Message(arbitration_id=0x122,
                                          data=[bool(msg.payload)],
                                          is_extended_id=False,
                                          is_remote_frame=False)
                bus.send(msg=can_message, timeout=5)
                customLogger.info("Fuel alarm registered! Forwarding to CAN!")
        except json.JSONDecodeError:
            customLogger.error("Failed to decode JSON from MQTT message payload.")
        except Exception as e:
            customLogger.error(f"An error occurred: {e}")

    protocol_client = MQTTClient(
        "protocol-data-can-sensor-mqtt-client",
        transport_protocol=TRANSPORT_PROTOCOL,
        protocol_version=mqtt.MQTTv5,
        mqtt_username=config.mqtt_broker_username,
        mqtt_pass=config.mqtt_broker_password,
        broker_address=config.mqtt_broker_address,
        broker_port=config.mqtt_broker_port,
        keepalive=config.fuel_settings_interval,
        infoLogger=infoLogger,
        errorLogger=errorLogger,
        flag=flag,
        sensor_type="PROTOCOL")

    protocol_client.set_on_connect(on_connect_protocol_sensor)
    protocol_client.set_on_publish(on_publish)
    protocol_client.set_on_subscribe(on_subscribe_protocol)
    protocol_client.set_on_message(on_message_protocol_alarm)
    protocol_client.connect()

    return protocol_client


def on_publish(topic, payload, qos):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        topic: str
            The topic that the message was sent to
        payload: bytearray
            Message published
        qos: int
            Quality of Service of MQTT broker

    """
    pass


def on_subscribe_protocol(client, userdata, flags, rc, props):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        client: paho.mqtt.client.Client
        userdata:
        flags:
        rc:
        props:

    """
    if rc == 0:
        infoLogger.info(
            "Protocol client successfully established connection with MQTT broker!")
        customLogger.debug(
            "Protocol client successfully established connection with MQTT broker!")
    else:
        errorLogger.error(
            "Protocol client failed to establish connection with MQTT broker!")
        customLogger.critical(
            "Protocol client failed to establish connection with MQTT broker!")


def on_connect_protocol_sensor(client, userdata, flags, rc, props):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        client: paho.mqtt.client.Client
        userdata:
        flags:
        rc:
        props:

    """
    if rc == 0:
        infoLogger.info(
            "CAN Protocol sensor successfully established connection with MQTT broker!")
        customLogger.debug(
            "CAN Protocol sensor successfully established connection with MQTT broker!")
        client.subscribe(PROTOCOL_INPUT_TOPIC, qos=QOS)
        client.subscribe(TEMP_ALARM_TOPIC, qos=QOS)
        client.subscribe(FUEL_ALARM_TOPIC, qos=QOS)
        client.subscribe(LOAD_ALARM_TOPIC, qos=QOS)
    else:
        errorLogger.error(
            "CAN Protocol sensor failed to establish connection with MQTT broker!")
        customLogger.critical(
            "CAN Protocol sensor failed to establish connection with MQTT broker!")


class CANListener (Listener):
    """
    A class that accepts messages from the CAN bus.

    This class inherits the functionality of can.listener.Listener

    Inherits:
    --------
        can.listener.Listener: Base class for CAN bus listener functionality

    Methods:
    -------
        __init__(temp_client, load_client, fuel_client): Class constructor for initializing class objects
        set_protocol_client(client): Setter for the protocol MQTT broker client
        on_message_received(msg): Event handler for receiving messages from the CAN bus
    """

    def __init__(self, protocol_client):
        """
        Constructor for initializing CANListener object

        Args:
        ----
            protocol_client: MQTT protocol data broker client

        """
        super().__init__()

        if protocol_client is not None:
            protocol_client.connect()
        self.protocol_client = protocol_client

        # counter that counts received messages
        self.message_counter = 0

    def set_protocol_client(self, client):
        """
        Setter for the protocol data MQTT broker client

        Args:
        ----
            client: MQTT protocol data broker client

        """
        if client is None:
            if self.protocol_client is not None:
                self.protocol_client.disconnect()
        self.protocol_client = client

    def on_message_received(self, msg):
        """
        Event handler for receiving messages from the CAN bus

        Args:
        ----
            msg: bytearray
                Received message from the CAN bus

        """
        self.message_counter += 1
        if self.message_counter > 5:
            self.message_counter = 0
        # msg.data is a byte array, need to turn it into a single value
        int_value = int.from_bytes(msg.data, byteorder="big", signed=True)
        value = int_value / 10.0
        if self.protocol_client is not None:
            self.protocol_client.try_reconnect()
            # Extract CAN ID value to search for it in the database
        hex_string_without_prefix = hex(msg.arbitration_id)[2:]
        integer_value = int(hex_string_without_prefix, 10)
        # Get all protocol data based on CAN ID (ProtocolDataEntity objects)
        rows = get_data_by_can_id(integer_value)

        with lock:
            for protocol_data_entity in rows:
                # Only OUTPUT messages are parsed, INPUT sent from cloud
                if protocol_data_entity.mode == "OUTPUT":
                    # Extract value from relevant bits (range from start bit to start bit + num of bits)
                    extracted_value = extract_bits(msg.data, protocol_data_entity.start_bit,
                                                   protocol_data_entity.num_bits)
                    extracted_double_value = extracted_value / 10.0
                    # Send message to app module via MQTT
                    self.protocol_client.publish(
                        PROTOCOL_TOPIC, PROTOCOL_DATA_PATTERN.format(
                            "{:.2f}".format(extracted_double_value), str(
                                time.strftime(
                                    TIME_FORMAT, time.localtime())),
                            protocol_data_entity.id), QOS)
                    customLogger.info(
                        "Protocol data: " + PROTOCOL_DATA_PATTERN.format(
                            "{:.2f}".format(value),
                            str(
                                time.strftime(
                                    TIME_FORMAT,
                                    time.localtime())), protocol_data_entity.id))


def main():
    """
    Start can app entrypoint.
    Initializes can_lock to prevent race conditioning.
    Initializes main_execution_flag to prevent stop the thread on app shutdown.
    Starts thread which reads received can data.
    """
    can_lock = threading.Lock()
    main_execution_flag = Event()
    BetterSignalHandler([signal.SIGINT,
                         signal.SIGTERM],
                        [main_execution_flag])
    can_thread = threading.Thread(
        target=read_can,
        args=(
            main_execution_flag,
            can_lock,))
    can_thread.start()


if __name__ == '__main__':
    main()
