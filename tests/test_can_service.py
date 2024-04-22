import logging
import multiprocessing
import threading
import time
import unittest

import can
import pytest

from src.can_service import read_can, CAN_GENERAL_SETTINGS, INTERFACE, CHANNEL, BITRATE, init_mqtt_clients, \
    on_subscribe_temp_alarm, on_subscribe_load_alarm, on_subscribe_fuel_alarm, on_connect_temp_sensor, \
    on_connect_load_sensor, on_connect_fuel_sensor
from src.config_util import Config
from src.sensor_devices import InitFlags

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
customLogger = logging.getLogger('customConsoleLogger')
errorLogger = logging.getLogger('customErrorLogger')
APP_CONF_FILE_PATH = "src/configuration/app_conf.json"

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

        can_sensor = threading.Thread(
            target=read_can,
            args=(
                execution_flag,
                config_flag,
                init_flags,
                can_lock))
        can_sensor.start()


        time.sleep(1)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            print(custom_logger.output)
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN process shutdown!"], custom_logger.output)
        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN BUS has been shut down."], error_logger.output)

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

        on_subscribe_temp_alarm(None, None, None, 0, None)
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Temperature alarm client successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Temperature alarm client successfully established connection with MQTT broker!"], custom_logger.output)

        on_subscribe_temp_alarm(None, None, None, 1, None)
        with self.TC.assertLogs(errorLogger, logging.INFO) as error_logger:
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Temperature alarm client failed to establish connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Temperature alarm client failed to establish connection with MQTT broker!"], custom_logger.output)

    def test_on_subscribe_load_alarm(self):

        on_subscribe_load_alarm(None, None, None, 0, None)
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Load alarm client successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Load alarm client successfully established connection with MQTT broker!"], custom_logger.output)

        on_subscribe_load_alarm(None, None, None, 1, None)
        with self.TC.assertLogs(errorLogger, logging.INFO) as error_logger:
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Load alarm client failed to establish connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Load alarm client failed to establish connection with MQTT broker!"], custom_logger.output)

    def test_on_subscribe_load_alarm(self):

        on_subscribe_fuel_alarm(None, None, None, 0, None)
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Fuel alarm client successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Fuel alarm client successfully established connection with MQTT broker!"], custom_logger.output)

        on_subscribe_fuel_alarm(None, None, None, 1, None)
        with self.TC.assertLogs(errorLogger, logging.INFO) as error_logger:
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Fuel alarm client failed to establish connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Fuel alarm client failed to establish connection with MQTT broker!"], custom_logger.output)

    def test_on_connect_temp_sensor(self):
        with self.TC.assertRaises(AttributeError):
            on_connect_temp_sensor(None, None, None, 0, None)
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Temperature sensor successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Temperature sensor successfully established connection with MQTT broker!"], custom_logger.output)

        on_connect_temp_sensor(None, None, None, 1, None)
        with self.TC.assertLogs(errorLogger, logging.INFO) as error_logger:
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Temperature sensor successfully established connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Temperature sensor successfully established connection with MQTT broker!"], custom_logger.output)

    def test_on_connect_load_sensor(self):
        with self.TC.assertRaises(AttributeError):
            on_connect_load_sensor(None, None, None, 0, None)
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Load sensor successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Load sensor successfully established connection with MQTT broker!"], custom_logger.output)

        on_connect_load_sensor(None, None, None, 1, None)
        with self.TC.assertLogs(errorLogger, logging.INFO) as error_logger:
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Load sensor successfully established connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Load sensor successfully established connection with MQTT broker!"], custom_logger.output)

    def test_on_connect_fuel_sensor(self):
        with self.TC.assertRaises(AttributeError):
            on_connect_fuel_sensor(None, None, None, 0, None)
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            self.TC.assertEqual(["INFO:customInfoLogger:CAN Fuel sensor successfully established connection with MQTT broker!"], info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            self.TC.assertEqual(["DEBUG:customConsoleLogger:CAN Fuel sensor successfully established connection with MQTT broker!"], custom_logger.output)

        on_connect_fuel_sensor(None, None, None, 1, None)
        with self.TC.assertLogs(errorLogger, logging.INFO) as error_logger:
            self.TC.assertEqual(["ERROR:customErrorLogger:CAN Fuel sensor successfully established connection with MQTT broker!"], error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            self.TC.assertEqual(["CRITICAL:customConsoleLogger:CAN Fuel sensor successfully established connection with MQTT broker!"], custom_logger.output)