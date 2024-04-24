import logging
import unittest
import pytest
from src.app import infoLogger, customLogger, errorLogger, on_connect_fuel_handler, on_connect_load_handler, \
    on_connect_temp_handler


class TestApp(object):
    TC = unittest.TestCase()

    def test_on_connect_temp_handler(self):
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_temp_handler(None, None, None, 0, None)
            self.TC.assertEqual(
                ["INFO:customInfoLogger:Temperature data handler successfully established connection with MQTT broker!"],
                info_logger.output)
        with self.TC.assertLogs(customLogger, logging.INFO) as custom_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_temp_handler(None, None, None, 0, None)
            self.TC.assertEqual(
                ["INFO:customConsoleLogger:Temperature data handler successfully established connection with MQTT broker!"],
                custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_connect_temp_handler(None, None, None, 1, None)
            self.TC.assertEqual(
                ["ERROR:customErrorLogger:Temperature data handler failed to establish connection with MQTT broker!"],
                error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_connect_temp_handler(None, None, None, 1, None)
            self.TC.assertEqual(
                ["CRITICAL:customConsoleLogger:Temperature data handler failed to establish connection with MQTT broker!"],
                custom_logger.output)

    def test_on_connect_load_handler(self):
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_load_handler(None, None, None, 0, None)
            self.TC.assertEqual(
                ["INFO:customInfoLogger:Arm load data handler successfully established connection with MQTT broker!"],
                info_logger.output)
        with self.TC.assertLogs(customLogger, logging.INFO) as custom_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_load_handler(None, None, None, 0, None)
            self.TC.assertEqual(
                ["INFO:customConsoleLogger:Arm load data handler successfully established connection with MQTT broker!"],
                custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_connect_load_handler(None, None, None, 1, None)
            self.TC.assertEqual(
                ["ERROR:customErrorLogger:Arm load data handler failed to establish connection with MQTT broker!"],
                error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_connect_load_handler(None, None, None, 1, None)
            self.TC.assertEqual(
                ["CRITICAL:customConsoleLogger:Arm load data handler failed to establish connection with MQTT broker!"],
                custom_logger.output)

    def test_on_connect_fuel_handler(self):
        with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_fuel_handler(None, None, None, 0, None)
            self.TC.assertEqual(
                ["INFO:customInfoLogger:Fuel data handler successfully established connection with MQTT broker!"],
                info_logger.output)
        with self.TC.assertLogs(customLogger, logging.INFO) as custom_logger:
            with self.TC.assertRaises(AttributeError):
                on_connect_fuel_handler(None, None, None, 0, None)
            self.TC.assertEqual(
                ["INFO:customConsoleLogger:Fuel data handler successfully established connection with MQTT broker!"],
                custom_logger.output)

        with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
            on_connect_fuel_handler(None, None, None, 1, None)
            self.TC.assertEqual(
                ["ERROR:customErrorLogger:Fuel data handler failed to establish connection with MQTT broker!"],
                error_logger.output)
        with self.TC.assertLogs(customLogger, logging.CRITICAL) as custom_logger:
            on_connect_fuel_handler(None, None, None, 1, None)
            self.TC.assertEqual(
                ["CRITICAL:customConsoleLogger:Fuel data handler failed to establish connection with MQTT broker!"],
                custom_logger.output)
