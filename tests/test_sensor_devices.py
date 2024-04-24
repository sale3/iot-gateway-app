import threading
import unittest
import logging
from multiprocessing import Event

import pytest

from src.config_util import ConfFlags, start_config_observer, Config
from src.sensor_devices import infoLogger, customLogger, errorLogger, on_publish, on_connect_temp_sensor, \
    on_connect_load_sensor, on_connect_fuel_sensor, read_conf, TEMP_SENSOR, INTERVAL, MIN, AVG, ARM_SENSOR, ARM_MIN_T, \
    ARM_MAX_T, MAX, FUEL_SENSOR, FUEL_CAPACITY, FUEL_CONSUMPTION, FUEL_EFFICIENCY, FUEL_REFILL, MQTT_BROKER, ADDRESS, \
    PORT, MQTT_USER, MQTT_PASSWORD, InitFlags, sensors_devices, APP_CONF_FILE_PATH, LOAD_SETTINGS, MODE, FUEL_SETTINGS, \
    TEMP_SETTINGS, CONF_FILE_PATH
from tests.mock_util import mock_config_end, mock_config_start


class TestSensorDevices(object):
    TC = unittest.TestCase()

    def test_on_publish(self):
        on_publish(None, None, None)

    def test_on_connect_temp_sensor(self):
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            on_connect_temp_sensor(None, None, None, 0, None)
            self.TC.assertEqual([
                                    "INFO:customInfoLogger:Temperature sensor successfully established connection with MQTT broker!"],
                                info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            on_connect_temp_sensor(None, None, None, 0, None)
            self.TC.assertEqual([
                                    "DEBUG:customConsoleLogger:Temperature sensor successfully established connection with MQTT broker!"],
                                custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_connect_temp_sensor(None, None, None, 1, None)
            self.TC.assertEqual([
                                    "ERROR:customErrorLogger:Temperature sensor failed to establish connection with MQTT broker!"],
                                error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_connect_temp_sensor(None, None, None, 1, None)
            self.TC.assertEqual([
                                    "CRITICAL:customConsoleLogger:Temperature sensor failed to establish connection with MQTT broker!"],
                                custom_logger.output)

    def test_on_connect_load_sensor(self):
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            on_connect_load_sensor(None, None, None, 0, None)
            self.TC.assertEqual([
                                    "INFO:customInfoLogger:Arm load sensor successfully established connection with MQTT broker!"],
                                info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            on_connect_load_sensor(None, None, None, 0, None)
            self.TC.assertEqual([
                                    "DEBUG:customConsoleLogger:Arm load sensor successfully established connection with MQTT broker!"],
                                custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_connect_load_sensor(None, None, None, 1, None)
            self.TC.assertEqual([
                                    "ERROR:customErrorLogger:Arm load sensor failed to establish connection with MQTT broker!"],
                                error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_connect_load_sensor(None, None, None, 1, None)
            self.TC.assertEqual([
                                    "CRITICAL:customConsoleLogger:Arm load sensor failed to establish connection with MQTT broker!"],
                                custom_logger.output)

    def test_on_connect_fuel_sensor(self):
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            on_connect_fuel_sensor(None, None, None, 0, None)
            self.TC.assertEqual([
                                    "INFO:customInfoLogger:Fuel sensor successfully established connection with MQTT broker!"],
                                info_logger.output)
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            on_connect_fuel_sensor(None, None, None, 0, None)
            self.TC.assertEqual([
                                    "DEBUG:customConsoleLogger:Fuel sensor successfully established connection with MQTT broker!"],
                                custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_connect_fuel_sensor(None, None, None, 1, None)
            self.TC.assertEqual([
                                    "ERROR:customErrorLogger:Fuel sensor failed to establish connection with MQTT broker!"],
                                error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_connect_fuel_sensor(None, None, None, 1, None)
            self.TC.assertEqual([
                                    "CRITICAL:customConsoleLogger:Fuel sensor failed to establish connection with MQTT broker!"],
                                custom_logger.output)

    def test_read_conf(self):
        mock_config_start()
        read_conf(CONF_FILE_PATH)
        self.TC.assertNoLogs(errorLogger, logging.CRITICAL)
        self.TC.assertNoLogs(customLogger, logging.CRITICAL)
        mock_config_end()

    def test_read_conf_default(self):
        config = read_conf("asdasdasda")
        default_config = {
            TEMP_SENSOR: {
                INTERVAL: 5,
                MIN: -10,
                AVG: 100},
            ARM_SENSOR: {
                ARM_MIN_T: 10,
                ARM_MAX_T: 100,
                MIN: 0,
                MAX: 800},
            FUEL_SENSOR: {
                INTERVAL: 5,
                FUEL_CAPACITY: 300,
                FUEL_CONSUMPTION: 3000,
                FUEL_EFFICIENCY: 0.6,
                FUEL_REFILL: 0.02},
            MQTT_BROKER: {
                ADDRESS: "localhost",
                PORT: 1883,
                MQTT_USER: "iot-device",
                MQTT_PASSWORD: "password"}}
        self.TC.assertEqual(default_config, config)

    @pytest.mark.parametrize('is_temp_sim, is_load_sim, is_fuel_sim', [
        (False, False, False),
        (True, False, False),
        (True, True, False),
        (True, True, True)
    ])
    def test_sensors_devices(self, is_temp_sim, is_load_sim, is_fuel_sim):
        mock_config_start()
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        temp_mode = config.temp_mode
        load_mode = config.load_mode
        fuel_mode = config.fuel_mode

        if is_temp_sim is True:
            config.config[TEMP_SETTINGS][MODE] = "SIMULATOR"
        else:
            config.config[TEMP_SETTINGS][MODE] = "CAN"
        if is_load_sim is True:
            config.config[LOAD_SETTINGS][MODE] = "SIMULATOR"
        else:
            config.config[LOAD_SETTINGS][MODE] = "CAN"
        if is_fuel_sim is True:
            config.config[FUEL_SETTINGS][MODE] = "SIMULATOR"
        else:
            config.config[FUEL_SETTINGS][MODE] = "CAN"

        config.write()

        temp_simulation_flag = Event()
        load_simulation_flag = Event()
        fuel_simulation_flag = Event()
        can_flag = Event()

        temp_lock = threading.Lock()
        load_lock = threading.Lock()
        fuel_lock = threading.Lock()
        can_lock = threading.Lock()

        app_config_flags = ConfFlags()
        init_flags = InitFlags()

        sensors = sensors_devices(
            temp_simulation_flag,
            load_simulation_flag,
            fuel_simulation_flag,
            can_flag,
            app_config_flags,
            init_flags,
            can_lock,
            temp_lock,
            load_lock,
            fuel_lock)

        if is_temp_sim:
            result = [thread for thread in sensors if thread.name == "Temperature Simulator"]
            self.TC.assertEqual(result[0], sensors[sensors.index(result[0])])
        if is_load_sim:
            result = [thread for thread in sensors if thread.name == "Load Simulator"]
            self.TC.assertEqual(result[0], sensors[sensors.index(result[0])])
        if is_fuel_sim:
            result = [thread for thread in sensors if thread.name == "Fuel Simulator"]
            self.TC.assertEqual(result[0], sensors[sensors.index(result[0])])

        if is_temp_sim is False or is_load_sim is False or is_fuel_sim is False:
            result = [thread for thread in sensors if thread.name == "CAN Thread"]
            self.TC.assertEqual(result[0], sensors[sensors.index(result[0])])

        temp_simulation_flag.set()
        load_simulation_flag.set()
        fuel_simulation_flag.set()
        can_flag.set()

        config.config[TEMP_SETTINGS][MODE] = temp_mode
        config.config[LOAD_SETTINGS][MODE] = load_mode
        config.config[FUEL_SETTINGS][MODE] = fuel_mode

        config.write()
        mock_config_end()
