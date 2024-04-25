import unittest
import os
import shutil

from src.config_util import ConfFlags, ConfHandler, \
    start_config_observer, read_conf, write_conf, \
    get_temp_interval, get_load_interval, get_fuel_level_limit, \
    Config, CONF_PATH, CONF_DIR

from tests.mock_util import mock_config_start, mock_config_end


class TestConfigUtil(unittest.TestCase):

    def assert_flags_set(self, conf_flags):
        self.assertTrue(conf_flags.fuel_flag.is_set())
        self.assertTrue(conf_flags.temp_flag.is_set())
        self.assertTrue(conf_flags.load_flag.is_set())
        self.assertTrue(conf_flags.can_flag.is_set())
        self.assertTrue(conf_flags.execution_flag.is_set())

    def test_conf_flags_set_all(self):
        flags = ConfFlags()
        flags.set_all()
        self.assert_flags_set(flags)

    def test_conf_handler__init__(self):
        super()
        flags = ConfFlags()
        conf_handler = ConfHandler(flags)
        self.assertEqual(flags, conf_handler.conf_flags)

    def test_conf_handler_on_modified(self):
        flags = ConfFlags()
        conf_handler = ConfHandler(flags)
        conf_handler.on_modified(None)
        self.assert_flags_set(conf_handler.conf_flags)

    def test_conf_handler_on_any_event(self):
        ConfHandler(ConfFlags()).on_any_event(None)

    def test_start_config_observer_created(self):
        mock_config_start()
        observer = start_config_observer(ConfFlags())
        self.assertIsNotNone(observer)
        mock_config_end()

    def test_read_conf_correct(self):
        mock_config_start()
        self.assertIsNotNone(read_conf())
        mock_config_end()

    def test_read_conf_wrong(self):
        self.assertIsNone(read_conf())

    def test_write_conf_correct(self):
        mock_config_start()
        conf = read_conf()
        os.remove(CONF_PATH)
        write_ret = write_conf(conf)
        self.assertEqual(conf, write_ret)
        self.assertTrue(os.path.exists(CONF_PATH))
        shutil.rmtree(CONF_DIR)

    def test_write_conf_wrong(self):
        mock_config_start()
        conf = read_conf()
        mock_config_end()
        write_ret = write_conf(conf)
        self.assertIsNone(write_ret)

    def test_legacy_config_parameter_getters(self):
        mock_config_start()
        config = Config(CONF_PATH)
        config.try_open()
        self.assertEqual(config.temp_settings_interval, get_temp_interval(config))
        self.assertEqual(config.load_settings_interval, get_load_interval(config))
        self.assertEqual(config.fuel_settings_interval, get_fuel_level_limit(config))
        mock_config_end()

