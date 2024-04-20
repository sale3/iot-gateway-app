import logging
import multiprocessing
import threading
import time
import unittest
import pytest

from src.can_service import read_can, CAN_GENERAL_SETTINGS, INTERFACE, CHANNEL, BITRATE
from src.config_util import Config
from src.sensor_devices import InitFlags

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('testInfoLogger')
customLogger = logging.getLogger('testConsoleLogger')
errorLogger = logging.getLogger('testErrorLogger')
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

        can_sensor = threading.Thread(
            target=read_can,
            args=(
                execution_flag,
                config_flag,
                init_flags,
                can_lock))
        can_sensor.start()

        time.sleep(3)

        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            self.TC.assertEqual(custom_logger.output,
                                ["DEBUG:customConsoleLogger:CAN BUS has been shut down."])
        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            self.TC.assertEqual(error_logger.output,
                                ["DEBUG:customErrorLogger:CAN BUS has been shut down."])

        execution_flag.set()
        config.config['can_general_settings']['interface'] = saved_interface
        config.config['can_general_settings']['channel'] = saved_channel
        config.config['can_general_settings']['bitrate'] = saved_bitrate

        config.write()

    def test_stop_can(self):
        pass

