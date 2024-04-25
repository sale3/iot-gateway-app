import logging
import unittest
from src.can_service import errorLogger, customLogger
from src.config_util import Config, TEMP_SETTINGS, MODE, LOAD_SETTINGS, FUEL_SETTINGS, INTERFACE, CAN_GENERAL_SETTINGS, \
    CHANNEL, BITRATE, MQTT_BROKER, USERNAME, PASSWORD, ADDRESS, PORT, SERVER_URL, API_KEY, SERVER_TIME_FORMAT, \
    AUTH_INTERVAL, INTERVAL, TIME_FORMAT, LEVEL_LIMIT, GATEWAY_CLOUD_BROKER, REST_API, HOST
from tests.mock_util import mock_config_start, mock_config_end

APP_CONF_FILE_PATH = "configuration/app_conf.json"


class TestConfigUtil(unittest.TestCase):

    def setUp(self):
        mock_config_start()

    def tearDown(self):
        mock_config_end()

    def test_config_init(self):
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        self.assertEqual(config.error_logger, errorLogger)
        self.assertEqual(config.custom_logger, customLogger)
        self.assertEqual(config.path, APP_CONF_FILE_PATH)

    def test_config_read(self):
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()
        self.assertNoLogs(errorLogger, logging.CRITICAL)
        self.assertNoLogs(customLogger, logging.CRITICAL)

    def test_config_read_default(self):
        config = Config("asdasdasdsad", errorLogger, customLogger)
        config.try_open()
        default_config = {
            FUEL_SETTINGS: {
                LEVEL_LIMIT: 200, MODE: "SIMULATOR", INTERVAL: 20}, TEMP_SETTINGS: {
                INTERVAL: 20, MODE: "SIMULATOR"}, LOAD_SETTINGS: {
                INTERVAL: 20, MODE: "SIMULATOR"}, SERVER_URL: "", MQTT_BROKER: {
                USERNAME: "", PASSWORD: ""
            }}
        self.assertEqual(default_config, config.config)

    def test_config_write(self):
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        new_temp_mode = "something"
        temp_mode = config.temp_mode

        config.config["temp_settings"]["mode"] = new_temp_mode
        config.write()
        config.config["temp_settings"]["mode"] = temp_mode

        config.try_open()
        self.assertEqual(config.temp_mode, new_temp_mode)

        config.write()

    def test_temp_mode_property(self):
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        mode = config.config[TEMP_SETTINGS][MODE]
        mode_property = config.temp_mode
        self.assertEqual(mode, mode_property)

    def test_load_mode_property(self):
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        mode = config.config[LOAD_SETTINGS][MODE]
        mode_property = config.load_mode
        self.assertEqual(mode, mode_property)

    def test_fuel_mode_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        mode = config.config[FUEL_SETTINGS][MODE]
        mode_property = config.fuel_mode
        self.assertEqual(mode, mode_property)

    def test_can_interface_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        interface = config.config[CAN_GENERAL_SETTINGS][INTERFACE]
        interface_property = config.can_interface
        self.assertEqual(interface, interface_property)

    def test_can_channel_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        channel = config.config[CAN_GENERAL_SETTINGS][CHANNEL]
        channel_property = config.can_channel
        self.assertEqual(channel, channel_property)

    def test_can_bitrate_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        bitrate = config.config[CAN_GENERAL_SETTINGS][BITRATE]
        bitrate_property = config.can_bitrate
        self.assertEqual(bitrate, bitrate_property)

    def test_mqtt_broker_username_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        username = config.config[MQTT_BROKER][USERNAME]
        username_property = config.mqtt_broker_username
        self.assertEqual(username, username_property)

    def test_mqtt_broker_password_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        password = config.config[MQTT_BROKER][PASSWORD]
        password_property = config.mqtt_broker_password
        self.assertEqual(password, password_property)

    def test_mqtt_broker_address_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        address = config.config[MQTT_BROKER][ADDRESS]
        address_property = config.mqtt_broker_address
        self.assertEqual(address, address_property)

    def test_mqtt_broker_port_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        port = config.config[MQTT_BROKER][PORT]
        port_property = config.mqtt_broker_port
        self.assertEqual(port, port_property)

    def test_server_url_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        server_url = config.config[SERVER_URL]
        server_url_property = config.server_url
        self.assertEqual(server_url, server_url_property)

    def test_iot_username_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        iot_username = config.config[USERNAME]
        iot_username_property = config.iot_username
        self.assertEqual(iot_username, iot_username_property)

    def test_iot_password_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        iot_password = config.config[PASSWORD]
        iot_password_property = config.iot_password
        self.assertEqual(iot_password, iot_password_property)

    def test_api_key_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        api_key = config.config[API_KEY]
        api_key_property = config.api_key
        self.assertEqual(api_key, api_key_property)

    def test_server_time_format_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        server_time_format = config.config[SERVER_TIME_FORMAT]
        server_time_format_property = config.server_time_format
        self.assertEqual(server_time_format, server_time_format_property)

    def test_auth_interval_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        auth_interval = config.config[AUTH_INTERVAL]
        auth_interval_property = config.auth_interval
        self.assertEqual(auth_interval, auth_interval_property)

    def test_temp_settings_interval_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        temp_settings_interval = config.config[TEMP_SETTINGS][INTERVAL]
        temp_settings_interval_property = config.temp_settings_interval
        self.assertEqual(temp_settings_interval, temp_settings_interval_property)

    def test_load_settings_interval_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        load_settings_interval = config.config[LOAD_SETTINGS][INTERVAL]
        load_settings_interval_property = config.load_settings_interval
        self.assertEqual(load_settings_interval, load_settings_interval_property)

    def test_fuel_settings_interval_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        fuel_settings_interval = config.config[FUEL_SETTINGS][INTERVAL]
        fuel_settings_interval_property = config.fuel_settings_interval
        self.assertEqual(fuel_settings_interval, fuel_settings_interval_property)

    def test_time_format_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        time_format = config.config[TIME_FORMAT]
        time_format_property = config.time_format
        self.assertEqual(time_format, time_format_property)

    def test_fuel_settings_level_limit_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        fuel_settings_level_limit = config.config[FUEL_SETTINGS][LEVEL_LIMIT]
        fuel_settings_level_limit_property = config.fuel_settings_level_limit
        self.assertEqual(fuel_settings_level_limit, fuel_settings_level_limit_property)

    def test_gateway_cloud_broker_iot_username_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        gateway_cloud_broker_iot_username = config.config[GATEWAY_CLOUD_BROKER][USERNAME]
        gateway_cloud_broker_iot_username_property = config.gateway_cloud_broker_iot_username
        self.assertEqual(gateway_cloud_broker_iot_username, gateway_cloud_broker_iot_username_property)

    def test_gateway_cloud_broker_iot_password_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        gateway_cloud_broker_iot_password = config.config[GATEWAY_CLOUD_BROKER][PASSWORD]
        gateway_cloud_broker_iot_password_property = config.gateway_cloud_broker_iot_password
        self.assertEqual(gateway_cloud_broker_iot_password, gateway_cloud_broker_iot_password_property)

    def test_gateway_cloud_broker_address_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        gateway_cloud_broker_address = config.config[GATEWAY_CLOUD_BROKER][ADDRESS]
        gateway_cloud_broker_address_property = config.gateway_cloud_broker_address
        self.assertEqual(gateway_cloud_broker_address, gateway_cloud_broker_address_property)

    def test_gateway_cloud_broker_port_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        gateway_cloud_broker_port = config.config[GATEWAY_CLOUD_BROKER][PORT]
        gateway_cloud_broker_port_property = config.gateway_cloud_broker_port
        self.assertEqual(gateway_cloud_broker_port, gateway_cloud_broker_port_property)

    def test_temp_settings_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        temp_settings = config.config[TEMP_SETTINGS]
        temp_settings_property = config.temp_settings
        self.assertEqual(temp_settings, temp_settings_property)

    def test_load_settings_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        load_settings = config.config[LOAD_SETTINGS]
        load_settings_property = config.load_settings
        self.assertEqual(load_settings, load_settings_property)

    def test_fuel_settings_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        fuel_settings = config.config[FUEL_SETTINGS]
        fuel_settings_property = config.fuel_settings
        self.assertEqual(fuel_settings, fuel_settings_property)

    def test_rest_api_host_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        rest_api_host = config.config[REST_API][HOST]
        rest_api_host_property = config.rest_api_host
        self.assertEqual(rest_api_host, rest_api_host_property)

    def test_rest_api_port_property(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        rest_api_port = config.config[REST_API][PORT]
        rest_api_port_property = config.rest_api_port
        self.assertEqual(rest_api_port, rest_api_port_property)

    def test_temp_settings_setter(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        temp_settings = config.config[TEMP_SETTINGS]
        temp_settings[MODE] = "something"

        config.temp_settings = temp_settings
        self.assertEqual(config.temp_settings, temp_settings)

    def test_load_settings_setter(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        load_settings = config.config[LOAD_SETTINGS]
        load_settings[MODE] = "something"

        config.load_settings = load_settings
        self.assertEqual(config.load_settings, load_settings)

    def test_fuel_settings_setter(self):
        
        config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
        config.try_open()

        fuel_settings = config.config[FUEL_SETTINGS]
        fuel_settings[MODE] = "something"

        config.fuel_settings = fuel_settings
        self.assertEqual(config.fuel_settings, fuel_settings)

