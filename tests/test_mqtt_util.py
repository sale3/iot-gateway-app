import unittest
import pytest
import logging

from tests.mock_data import create_mock

from src.mqtt_util import MQTTConf, GcbService, \
    gcb_publisher_on_connect, gcb_subscriber_on_connect, gcb_on_message, \
    gcb_init_client, gcb_init_publisher, gcb_init_subscriber, \
    errorLogger, infoLogger, customLogger
from src.config_util import Config, CONF_PATH, \
    GATEWAY_CLOUD_BROKER, ADDRESS, PORT, USERNAME, PASSWORD


class TestMqttUtil(object):
    TC = unittest.TestCase()

    @pytest.mark.parametrize('config_dict,broker', [
        (
                {
                    "gcb_address": "localhost",
                    "gcb_port": 1884,
                    "gcb_iot_username": "username",
                    "gcb_iot_password": "password"
                },
                "gateway_cloud_broker"
        ),
        (
                {
                    "gcb_address": "localhost",
                    "gcb_port": 1884,
                    "gcb_iot_username": "username",
                    "gcb_iot_password": "password"
                },
                "random_broker"
        )
    ])
    def test_mqtt_conf_from_app_config_correct(self, config_dict, broker):
        conf = Config(f"src/{CONF_PATH}",
                      logging.getLogger('customErrorLogger'),
                      logging.getLogger('customConsoleLogger'))
        conf.try_open()

        conf.config[GATEWAY_CLOUD_BROKER][ADDRESS] = config_dict["gcb_address"]
        conf.config[GATEWAY_CLOUD_BROKER][PORT] = config_dict["gcb_port"]
        conf.config[GATEWAY_CLOUD_BROKER][USERNAME] = config_dict["gcb_iot_username"]
        conf.config[GATEWAY_CLOUD_BROKER][PASSWORD] = config_dict["gcb_iot_password"]
        ret = MQTTConf.from_app_config(conf, broker)

        if broker == "gateway_cloud_broker":
            self.TC.assertIsNotNone(ret)
        else:
            self.TC.assertIsNone(ret)

    @pytest.mark.parametrize('rc', [
        0, 1, 2, -1, 'a', []
    ])
    def test_gcb_publisher_on_connect(self, rc):
        if rc == 0:
            with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
                gcb_publisher_on_connect(0, 0, 0, rc, 0)
                self.TC.assertEqual(info_logger.output,
                                    ["INFO:customInfoLogger:Successfully established connection with MQTT broker!"])
        else:
            with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
                gcb_publisher_on_connect(0, 0, 0, rc, 0)
                self.TC.assertEqual(error_logger.output,
                                    ["ERROR:customErrorLogger:Failed to establish connection with MQTT broker!"])

    @pytest.mark.parametrize('rc', [
        0, 1, 2, -1, 'a', []
    ])
    def test_gcb_subscriber_on_connect(self, rc):
        if rc == 0:
            with self.TC.assertLogs(infoLogger, logging.INFO) as info_logger:
                gcb_subscriber_on_connect(0, 0, 0, rc, 0)
                self.TC.assertEqual(info_logger.output,
                                    ["INFO:customInfoLogger:Successfully established connection with MQTT broker!"])
        else:
            with self.TC.assertLogs(errorLogger, logging.ERROR) as error_logger:
                gcb_subscriber_on_connect(0, 0, 0, rc, 0)
                self.TC.assertEqual(error_logger.output,
                                    ["ERROR:customErrorLogger:Failed to establish connection with MQTT broker!"])

    @pytest.mark.parametrize('message', [
        "test_message"
    ])
    def test_gcb_on_message_correct(self, message):
        # mock object because function does attribute access via "." operator
        mock = create_mock(payload=bytes(message, 'utf-8'))
        with self.TC.assertLogs(customLogger, logging.DEBUG) as custom_logger:
            gcb_on_message(None, None, mock)
            self.TC.assertEqual(custom_logger.output,
                                [
                                    f"DEBUG:customConsoleLogger:GATEWAY_CLOUD_BROKER RECEIVED: {str(mock.payload.decode('utf-8'))}"])

    @pytest.mark.parametrize('message', [
        123, [], "123", {"a": 123, "b": "123"}, {"payload": 123}, {"payload": "asdfasd"}
    ])
    def test_gcb_on_message_wrong(self, message):
        self.TC.assertRaises(Exception, gcb_on_message, None, None, message)

    @pytest.mark.parametrize('client_id,username,password', [
        # From paho mqtt source code, there is no restriction on password type, but there
        # is on username type which must be string (since encode is called on it).
        ("client_id", "username", "password"),
        (1234, "username", "password"),
        ("client_id", "username", 123124),
        ("client_id", "username", [])
    ])
    def test_gcb_init_functions_correct(self, client_id, username, password):
        self.TC.assertIsNotNone(gcb_init_client(client_id, username, password))
        self.TC.assertIsNotNone(gcb_init_publisher(client_id, username, password))
        self.TC.assertIsNotNone(gcb_init_subscriber(client_id, username, password))

    @pytest.mark.parametrize('client_id,username,password', [
        ("client_id", 123, "password"),
        ("client_id", [], "password")
    ])
    def test_gcb_init_functions_wrong(self, client_id, username, password):
        self.TC.assertRaises(AttributeError, gcb_init_client, client_id, username, password)
        self.TC.assertRaises(AttributeError, gcb_init_publisher, client_id, username, password)
        self.TC.assertRaises(AttributeError, gcb_init_subscriber, client_id, username, password)

    @pytest.mark.parametrize('topic,data', [
        ("topic", "data"),
        (123, "data"),
        ("topic", 123)
    ])
    def test_gcb_service_push_message_correct(self, topic, data):
        mqtt_conf = MQTTConf("localhost", 1884, "username", "password")
        gcb_service = GcbService("username", "client_id", mqtt_conf)
        GcbService.push_message(gcb_service.queue, topic, data)
        self.TC.assertEqual(gcb_service.queue.qsize(), 1)
        self.TC.assertEqual({"topic": topic, "data": data}, gcb_service.queue.get())

    def test_gcb_service_publishing_procedure_stopping(self):
        mqtt_conf = MQTTConf("localhost", 1884, "username", "password")
        gcb_service = GcbService("username", "client_id", mqtt_conf)
        gcb_service.stop_flag.set()
        gcb_service.__publishing_procedure__()
        self.TC.assertTrue(not gcb_service.stop_flag.is_set())

    def test_gcb_service_stop(self):
        mqtt_conf = MQTTConf("localhost", 1884, "username", "password")
        gcb_service = GcbService("username", "client_id", mqtt_conf)
        gcb_service.stop()
        self.TC.assertTrue(gcb_service.stop_flag.is_set())

