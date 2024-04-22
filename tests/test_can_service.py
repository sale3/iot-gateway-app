import logging
import multiprocessing
import threading
import time
import unittest
from pathlib import Path

import can
import pytest
from src.can_service import read_can, init_mqtt_clients, \
    on_subscribe_temp_alarm, on_subscribe_load_alarm, on_subscribe_fuel_alarm, on_connect_temp_sensor, \
    on_connect_load_sensor, on_connect_fuel_sensor, CANListener
from src.config_util import CAN_GENERAL_SETTINGS, INTERFACE, CHANNEL, BITRATE
from src.config_util import Config
from src.sensor_devices import InitFlags
from src.can_service import infoLogger, customLogger, errorLogger

logging.config.fileConfig('logging.conf')
testInfoLogger = logging.getLogger('testInfoLogger')
testCustomLogger = logging.getLogger('testConsoleLogger')
testErrorLogger = logging.getLogger('testErrorLogger')

APP_CONF_FILE_PATH = "configuration/app_conf.json"


class TestCanService(object):
    TC = unittest.TestCase()

    @pytest.mark.parametrize('interface, channel, bitrate', [
        ('asdasd', 'asdadasd', 'asdasdasd'),
        ('pcan', 'asdasdff', 1200),
        ('pcan', 'PCAN_USBBUS1', 123),
        ('pcan', 'asdasda', 500000)
    ])
    def test_bus_connection_failure(self, interface, channel, bitrate):
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        saved_interface = config.config[CAN_GENERAL_SETTINGS][INTERFACE]
        saved_channel = config.config[CAN_GENERAL_SETTINGS][CHANNEL]
        saved_bitrate = config.config[CAN_GENERAL_SETTINGS][BITRATE]

        config.config[CAN_GENERAL_SETTINGS][INTERFACE] = interface
        config.config[CAN_GENERAL_SETTINGS][CHANNEL] = channel
        config.config[CAN_GENERAL_SETTINGS][BITRATE] = bitrate

        config.write()

        execution_flag = multiprocessing.Event()
        config_flag = multiprocessing.Event()
        can_lock = threading.Lock()
        init_flags = InitFlags()

        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            can_sensor = threading.Thread(
                target=read_can,
                args=(
                    execution_flag,
                    config_flag,
                    init_flags,
                    can_lock))
            can_sensor.start()
            time.sleep(2)
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN process shutdown!"], [custom_logger.output[len(custom_logger.output) - 1]])
            execution_flag.set()
            execution_flag.clear()
        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            can_sensor = threading.Thread(
                target=read_can,
                args=(
                    execution_flag,
                    config_flag,
                    init_flags,
                    can_lock))
            can_sensor.start()
            time.sleep(2)
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN BUS has been shut down."], [error_logger.output[len(error_logger.output) - 1]])
            execution_flag.set()
            execution_flag.clear()

        execution_flag.set()
        config.config[CAN_GENERAL_SETTINGS][INTERFACE] = saved_interface
        config.config[CAN_GENERAL_SETTINGS][CHANNEL] = saved_channel
        config.config[CAN_GENERAL_SETTINGS][BITRATE] = saved_bitrate

        config.write()

    def test_init_mqtt_failure(self):
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        bus = can.Bus(interface="pcan",
                  channel="PCAN_USBBUS1",
                  bitrate=50000)
        execution_flag = multiprocessing.Event()
        temp_client, load_client, fuel_client = init_mqtt_clients(bus, True, True, True, config, execution_flag)
        self.TC.assertIsNone(temp_client)
        self.TC.assertIsNone(load_client)
        self.TC.assertIsNone(fuel_client)

    def test_on_subscribe_temp_alarm(self):


        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            on_subscribe_temp_alarm(None, None, None, 0, None)
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Temperature alarm client successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            on_subscribe_temp_alarm(None, None, None, 0, None)
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Temperature alarm client successfully established connection with MQTT broker!"], custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_subscribe_temp_alarm(None, None, None, 1, None)
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Temperature alarm client failed to establish connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_subscribe_temp_alarm(None, None, None, 1, None)
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Temperature alarm client failed to establish connection with MQTT broker!"], custom_logger.output)

    def test_on_subscribe_load_alarm(self):

        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            on_subscribe_load_alarm(None, None, None, 0, None)
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Load alarm client successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            on_subscribe_load_alarm(None, None, None, 0, None)
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Load alarm client successfully established connection with MQTT broker!"], custom_logger.output)


        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_subscribe_load_alarm(None, None, None, 1, None)
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Load alarm client failed to establish connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_subscribe_load_alarm(None, None, None, 1, None)
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Load alarm client failed to establish connection with MQTT broker!"], custom_logger.output)

    def test_on_subscribe_fuel_alarm(self):

        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            on_subscribe_fuel_alarm(None, None, None, 0, None)
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Fuel alarm client successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            on_subscribe_fuel_alarm(None, None, None, 0, None)
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Fuel alarm client successfully established connection with MQTT broker!"], custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_subscribe_fuel_alarm(None, None, None, 1, None)
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Fuel alarm client failed to establish connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_subscribe_fuel_alarm(None, None, None, 1, None)
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Fuel alarm client failed to establish connection with MQTT broker!"], custom_logger.output)

    def test_on_connect_temp_sensor(self):
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_temp_sensor(None, None, None, 0, None)
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Temperature sensor successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_temp_sensor(None, None, None, 0, None)
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Temperature sensor successfully established connection with MQTT broker!"], custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_connect_temp_sensor(None, None, None, 1, None)
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Temperature sensor failed to establish connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            on_connect_temp_sensor(None, None, None, 1, None)
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Temperature sensor failed to establish connection with MQTT broker!"], custom_logger.output)

    def test_on_connect_load_sensor(self):
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_load_sensor(None, None, None, 0, None)
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Load sensor successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_load_sensor(None, None, None, 0, None)
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Load sensor successfully established connection with MQTT broker!"], custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_connect_load_sensor(None, None, None, 1, None)
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Load sensor failed to establish connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_connect_load_sensor(None, None, None, 1, None)
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Load sensor failed to establish connection with MQTT broker!"], custom_logger.output)

    def test_on_connect_fuel_sensor(self):
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_fuel_sensor(None, None, None, 0, None)
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Fuel sensor successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_fuel_sensor(None, None, None, 0, None)
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Fuel sensor successfully established connection with MQTT broker!"], custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_connect_fuel_sensor(None, None, None, 1, None)
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Fuel sensor failed to establish connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_connect_fuel_sensor(None, None, None, 1, None)
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Fuel sensor failed to establish connection with MQTT broker!"], custom_logger.output)

    def test_can_listener(self):
        can_listener = CANListener(None, None, None)

        self.TC.assertIsNone(can_listener.temp_client, None)
        self.TC.assertIsNone(can_listener.load_client, None)
        self.TC.assertIsNone(can_listener.fuel_client, None)

        can_listener.set_temp_client(None)
        self.TC.assertIsNone(can_listener.temp_client)

        can_listener.set_load_client(None)
        self.TC.assertIsNone(can_listener.load_client)

        can_listener.set_fuel_client(None)
        self.TC.assertIsNone(can_listener.fuel_client)

