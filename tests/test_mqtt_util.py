import unittest
import pytest
import logging
import json
import os

from src.mqtt_util import MQTTConf, gcb_init_client
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

        f = open("ffff.txt", "w")
        f.write(json.dumps(conf.config, indent=4))
        f.close()

        conf.config[GATEWAY_CLOUD_BROKER][ADDRESS] = config_dict["gcb_address"]
        conf.config[GATEWAY_CLOUD_BROKER][PORT] = config_dict["gcb_port"]
        conf.config[GATEWAY_CLOUD_BROKER][USERNAME] = config_dict["gcb_iot_username"]
        conf.config[GATEWAY_CLOUD_BROKER][PASSWORD] = config_dict["gcb_iot_password"]
        ret = MQTTConf.from_app_config(conf, broker)

        if broker == "gateway_cloud_broker":
            self.TC.assertIsNotNone(ret)
        else:
            self.TC.assertIsNone(ret)

    @pytest.mark.parametrize('client_id,username,password', [
        ("client_id", "username", "password"),
    ])
    def test_gcb_init_client_correct(self, client_id, username, password):
        ret = gcb_init_client(client_id, username, password)
        self.TC.assertIsNotNone(ret)

