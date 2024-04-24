import logging
import multiprocessing
import unittest
import pytest
import paho.mqtt.client as mqtt
from src.can_service import TRANSPORT_PROTOCOL, infoLogger, errorLogger, customLogger
from src.config_util import Config
from src.mqtt_utils import MQTTClient
from tests.mock_util import mock_config_end, mock_config_start

APP_CONF_FILE_PATH = "configuration/app_conf.json"
class TestMqttUtils(object):
    TC = unittest.TestCase()

    def test_client_init(self):
        mock_config_start()

        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()
        flag = multiprocessing.Event()

        client = MQTTClient(
            "temp-can-sensor-mqtt-client",
            transport_protocol=TRANSPORT_PROTOCOL,
            protocol_version=mqtt.MQTTv5,
            mqtt_username=config.mqtt_broker_username,
            mqtt_pass=config.mqtt_broker_password,
            broker_address=config.mqtt_broker_address,
            broker_port=config.mqtt_broker_port,
            keepalive=config.temp_settings_interval,
            infoLogger=infoLogger,
            errorLogger=errorLogger,
            flag=flag,
            sensor_type="TEMP")
        paho_client = mqtt.Client(client_id="temp-can-sensor-mqtt-client",
                                  transport=TRANSPORT_PROTOCOL,
                                  protocol=mqtt.MQTTv5)
        paho_client.username_pw_set(config.mqtt_broker_username, config.mqtt_broker_password)
        # what about the paho.mqtt.Client object?
        self.TC.assertEqual(client.broker_address, config.mqtt_broker_address)
        self.TC.assertEqual(client.broker_port, config.mqtt_broker_port)
        self.TC.assertEqual(client.keepalive, config.temp_settings_interval)
        self.TC.assertEqual(client.infoLogger, infoLogger)
        self.TC.assertEqual(client.errorLogger, errorLogger)
        self.TC.assertEqual(client.flag, flag)
        self.TC.assertEqual(client.sensor_type, "TEMP")
        mock_config_end()

    def test_set_on_connect(self):
        mock_config_start()
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()
        flag = multiprocessing.Event()

        client = MQTTClient(
            "temp-can-sensor-mqtt-client",
            transport_protocol=TRANSPORT_PROTOCOL,
            protocol_version=mqtt.MQTTv5,
            mqtt_username=config.mqtt_broker_username,
            mqtt_pass=config.mqtt_broker_password,
            broker_address=config.mqtt_broker_address,
            broker_port=config.mqtt_broker_port,
            keepalive=config.temp_settings_interval,
            infoLogger=infoLogger,
            errorLogger=errorLogger,
            flag=flag,
            sensor_type="TEMP")

        def on_connect_sensor(client, userdata, flags, rc, props):
            pass
        client.set_on_connect(on_connect_sensor)
        self.TC.assertEqual(client.client.on_connect, on_connect_sensor)
        mock_config_end()

    def test_set_on_publish(self):
        mock_config_start()
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()
        flag = multiprocessing.Event()

        client = MQTTClient(
            "temp-can-sensor-mqtt-client",
            transport_protocol=TRANSPORT_PROTOCOL,
            protocol_version=mqtt.MQTTv5,
            mqtt_username=config.mqtt_broker_username,
            mqtt_pass=config.mqtt_broker_password,
            broker_address=config.mqtt_broker_address,
            broker_port=config.mqtt_broker_port,
            keepalive=config.temp_settings_interval,
            infoLogger=infoLogger,
            errorLogger=errorLogger,
            flag=flag,
            sensor_type="TEMP")

        def on_publish(topic, payload, qos):
            pass
        client.set_on_publish(on_publish)
        self.TC.assertEqual(client.client.on_publish, on_publish)
        mock_config_end()

    def test_set_on_message(self):
        mock_config_start()
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()
        flag = multiprocessing.Event()

        client = MQTTClient(
            "temp-can-sensor-mqtt-client",
            transport_protocol=TRANSPORT_PROTOCOL,
            protocol_version=mqtt.MQTTv5,
            mqtt_username=config.mqtt_broker_username,
            mqtt_pass=config.mqtt_broker_password,
            broker_address=config.mqtt_broker_address,
            broker_port=config.mqtt_broker_port,
            keepalive=config.temp_settings_interval,
            infoLogger=infoLogger,
            errorLogger=errorLogger,
            flag=flag,
            sensor_type="TEMP")

        def on_message_handler(client, userdata, message):
            pass
        client.set_on_message(on_message_handler)
        self.TC.assertEqual(client.client.on_message, on_message_handler)
        mock_config_end()

    def test_set_on_subscribe(self):
        mock_config_start()
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()
        flag = multiprocessing.Event()

        client = MQTTClient(
            "temp-can-sensor-mqtt-client",
            transport_protocol=TRANSPORT_PROTOCOL,
            protocol_version=mqtt.MQTTv5,
            mqtt_username=config.mqtt_broker_username,
            mqtt_pass=config.mqtt_broker_password,
            broker_address=config.mqtt_broker_address,
            broker_port=config.mqtt_broker_port,
            keepalive=config.temp_settings_interval,
            infoLogger=infoLogger,
            errorLogger=errorLogger,
            flag=flag,
            sensor_type="TEMP")

        def on_subscribe(client1, userdata, flags, rc, props):
            pass
        client.set_on_subscribe(on_subscribe)
        self.TC.assertEqual(client.client.on_subscribe, on_subscribe)

        mock_config_end()
