import unittest
import logging
from parameterized import parameterized

from src.data_service import parse_incoming_data, \
    handle_temperature_data, handle_load_data, handle_fuel_data, \
    EMPTY_PAYLOAD, customLogger


class TestDataService(unittest.TestCase):
    @parameterized.expand([
        [[
            '[ value=-2.0 , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=-2.0 , time=15.04.2024 14:01:17 , unit=C ]'
        ]],
        [[
            '[ value=-1.0 , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=-3.4 , time=15.04.2024 14:01:17 , unit=C ]',
            '[ value=10 , time=15.04.2024 14:01:17 , unit=C ]'
        ]]
    ])
    def test_handle_temperature_data_correct(self, data):
        value = 0
        for temp in data:
            value += float(temp.split(',')[0].split('=')[1])

        payload = handle_temperature_data(data, '%d.%m.%Y %H:%M:%S')
        self.assertEqual(payload["value"], round(value / len(data), 2))
        self.assertEqual(payload["unit"], 'C')

    @parameterized.expand([
        [[
            '[ value=-aasd , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=[] , time=15.04.2024 14:01:17 , unit=C ]',
            '[ value=123 , time=15.04.2024 14:01:17 , unit=C ]',
        ]]
    ])
    def test_handle_temperature_data_wrong_value(self, data):
        value = 0
        for temp in data:
            try:
                value += float(temp.split(',')[0].split('=')[1])
            except:
                value += 0

        payload = handle_temperature_data(data, '%d.%m.%Y %H:%M:%S')
        self.assertEqual(payload["value"], round(value / len(data), 2))

    @parameterized.expand([
        [[
            '[ value=-aasd , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=[] , time=15.04.2024 14:01:17 , unit=lkjas ]',
            '[ value=123 , time=15.04.2024 14:01:17 , unit=[] ]',
        ]]
    ])
    def test_handle_temperature_data_wrong_unit(self, data):
        # NOTE(stekap):
        # If turns out that the unit that is assigned
        # to payload is always the last unit,
        # including the possibility of it being 'unknown'.
        # Not sure why it works like this, but it doesn't make much sense.
        unit = "unknown"
        for temp in data:
            unit = temp.split(',')[2].split('=')[1].split(' ')[0]

        payload = handle_temperature_data(data, '%d.%m.%Y %H:%M:%S')
        self.assertEqual(payload["unit"], unit)

    @parameterized.expand([
        ["%d.%m.%Y %f %a %qq %% %a %g %l %H:%M:%S"],
        ["asdffb -. asdf"]
    ])
    def dont_test_handle_temperature_data_wrong_time_format(self, time_format):
        data = [
            '[ value=-2.0 , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=-2.0 , time=15.04.2024 14:01:17 , unit=C ]'
        ]
        has_error = False
        try:
            payload = handle_temperature_data(data, time_format)
            if payload["time"] == time_format:
                has_error = True
        except:
            has_error = True

        if not has_error:
            self.fail("Invalid time format not caught.")

    @parameterized.expand([
        [[
            '[ value=81.123 , time=15.04.2024 14:01:06 , unit=kg ]',
            '[ value=123.123 , time=15.04.2024 14:01:17 , unit=kg ]',
            '[ value=1192.2 , time=15.04.2024 14:01:17 , unit=kg ]'
        ]]
    ])
    def test_handle_load_data_correct(self, data):
        value = 0
        for temp in data:
            value += float(temp.split(',')[0].split('=')[1])

        payload = handle_load_data(data, '%d.%m.%Y %H:%M:%S')
        self.assertEqual(payload["value"], round(value, 2))
        self.assertEqual(payload["unit"], 'kg')

    @parameterized.expand([
        [[
            '[ value=aasdf , time=15.04.2024 14:01:06 , unit=kg ]',
            '[ value=[] , time=15.04.2024 14:01:17 , unit=kg ]',
            '[ value=-12s2 , time=15.04.2024 14:01:17 , unit=kg ]'
        ]]
    ])
    def test_handle_load_data_wrong_value(self, data):

        value = 0
        for temp in data:
            try:
                value += float(temp.split(',')[0].split('=')[1])
            except:
                value += 0

        payload = handle_load_data(data, '%d.%m.%Y %H:%M:%S')
        self.assertEqual(payload["value"], round(value, 2))

    @parameterized.expand([
        [[
            '[ value=aasdf , time=15.04.2024 14:01:06 , unit=1-1 ]',
            '[ value=[] , time=15.04.2024 14:01:17 , unit=lkj1 ]',
            '[ value=-12s2 , time=15.04.2024 14:01:17 , unit=[] ]'
        ]]
    ])
    def test_handle_load_data_wrong_unit(self, data):
        # NOTE(stekap):
        # If turns out that the unit that is assigned
        # to payload is always the last unit,
        # including the possibility of it being 'unknown'.
        # Not sure why it works like this, but it doesn't make much sense.
        unit = "unknown"
        for temp in data:
            unit = temp.split(',')[2].split('=')[1].split(' ')[0]

        payload = handle_load_data(data, '%d.%m.%Y %H:%M:%S')
        self.assertEqual(payload["unit"], unit)

    @parameterized.expand([
        ["%d.%m.%Y %f %a %qq %% %a %g %l %H:%M:%S"],
        ["asdffb -. asdf"]
    ])
    def dont_test_handle_load_data_wrong_time_format(self, time_format):
        data = [
            '[ value=1233.0 , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=1233.0 , time=15.04.2024 14:01:17 , unit=C ]'
        ]
        has_error = False
        try:
            payload = handle_load_data(data, time_format)
            if payload["time"] == time_format:
                has_error = True
        except:
            has_error = True

        if not has_error:
            self.fail("Invalid time format not caught.")

    @parameterized.expand([
        ['[ value=0 , time=15.04.2024 14:01:06 , unit=l ]', 0],
        ['[ value=81.123 , time=15.04.2024 14:01:06 , unit=l ]', 10],
        ['[ value=123.123 , time=15.04.2024 14:01:17 , unit=l ]', 100],
        ['[ value=1192.2 , time=15.04.2024 14:01:17 , unit=l ]', 1000],
        ['[ value=1192.2 , time=15.04.2024 14:01:17 , unit=l ]', 2000],
    ])
    def test_handle_fuel_data(self, data, limit):
        value = float(data.split(',')[0].split('=')[1])
        unit = data.split(',')[2].split('=')[1].split(' ')[0]

        if value == 0:
            payload = handle_fuel_data(data, limit, "%d.%m.%Y %H:%M:%S", None)
            self.assertEqual(payload, EMPTY_PAYLOAD)
            return

        # This is used in order to test logger output
        # even though given branch tries to
        # contact other part of the system.
        if value <= limit:
            with self.assertLogs(customLogger, logging.INFO) as custom_logger:
                try:
                    handle_fuel_data(data, limit, "%d.%m.%Y %H:%M:%S", None)
                except:
                    self.assertEqual(custom_logger.output,
                                     [
                                         "INFO:customConsoleLogger:Fuel is below the designated limit! Sounding "
                                         "the alarm"])
        else:
            payload = handle_fuel_data(data, limit, "%d.%m.%Y %H:%M:%S", None)
            self.assertEqual(payload["value"], round(value, 2))
            self.assertEqual(payload["unit"], unit)
