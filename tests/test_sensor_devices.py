import unittest
import logging
from src.sensor_devices import infoLogger, customLogger, errorLogger, on_publish, on_connect_temp_sensor, \
    on_connect_load_sensor, on_connect_fuel_sensor, read_conf, TEMP_SENSOR, INTERVAL, MIN, AVG, ARM_SENSOR, ARM_MIN_T, \
    ARM_MAX_T, MAX, FUEL_SENSOR, FUEL_CAPACITY, FUEL_CONSUMPTION, FUEL_EFFICIENCY, FUEL_REFILL, MQTT_BROKER, ADDRESS, \
    PORT, MQTT_USER, MQTT_PASSWORD


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
        read_conf()
        self.TC.assertNoLogs(errorLogger, logging.CRITICAL)
        self.TC.assertNoLogs(customLogger, logging.CRITICAL)

    def test_read_conf_default(self):
        config = read_conf()
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
