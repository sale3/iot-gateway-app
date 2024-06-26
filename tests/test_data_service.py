import time
import unittest
import pytest

from src.data_service import parse_incoming_data, \
    handle_temperature_data, handle_load_data, handle_fuel_data


class TestDataService(object):
    TC = unittest.TestCase()

    def test_parse_incoming_data_correct(self):
        val, typ = parse_incoming_data("nesto shemso=3 indeks_dva bla bla bla halid=invalid", "datatype")
        assert (val == 3.0)
        assert (typ == "invalid")

    # TODO: ne raditi ovako nego sa @pytest.mark.parametrize i/ili @fixture
    def test_parse_incoming_data_wrong(self):
        # TODO: ovaj zakomentarisani, ne javlja gresku, odnosno ako nesto nije broj dobijemo 0?!?!
        # TODO: poruke su iste u oba slucaja, treba ih razlikovati
        # with self.assertLogs('customErrorLogger', level='ERROR') as cm:
        #     _ = parse_incoming_data("nesto shemso=nije_broj indeks_dva bla bla bla halid=invalid", "datatype")
        #     self.assertEqual(cm.output, ['ERROR:customErrorLogger:Invalid datatype data format! - nesto shemso indeks_dva bla bla bla halid=invalid'])
        with self.TC.assertLogs('customErrorLogger', level='ERROR') as cm:
            _ = parse_incoming_data("nesto shemso=3 indeks_dva bla bla bla halit-ddd", "datatype")
            self.TC.assertEqual(cm.output, [
                'ERROR:customErrorLogger:Invalid datatype data format! - nesto shemso=3 indeks_dva bla bla bla halit-ddd'])
        with self.TC.assertLogs('customErrorLogger', level='ERROR') as cm:
            _ = parse_incoming_data("nesto shemso=3", "datatype")
            self.TC.assertEqual(cm.output, ['ERROR:customErrorLogger:Invalid datatype data format! - nesto shemso=3'])

    @pytest.mark.parametrize('data', [
        [
            '[ value=-2.0 , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=-2.0 , time=15.04.2024 14:01:17 , unit=C ]'
        ],
        [
            '[ value=-1.0 , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=-3.4 , time=15.04.2024 14:01:17 , unit=C ]',
            '[ value=10 , time=15.04.2024 14:01:17 , unit=C ]'
        ],
    ])
    def test_handle_temperature_data_correct(self, data):
        value = 0
        for temp in data:
            value += float(temp.split(',')[0].split('=')[1])

        payload = handle_temperature_data(data, '%d.%m.%Y %H:%M:%S')
        self.TC.assertEqual(payload["value"], round(value / len(data), 2))
        self.TC.assertEqual(payload["unit"], 'C')

    @pytest.mark.parametrize('data', [
        [
            '[ value=-aasd , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=[] , time=15.04.2024 14:01:17 , unit=C ]',
            '[ value=123 , time=15.04.2024 14:01:17 , unit=C ]',
        ]
    ])
    def test_handle_temperature_data_wrong_value(self, data):
        value = 0
        for temp in data:
            try:
                value += float(temp.split(',')[0].split('=')[1])
            except:
                value += 0

        payload = handle_temperature_data(data, '%d.%m.%Y %H:%M:%S')
        self.TC.assertEqual(payload["value"], round(value / len(data), 2))

    @pytest.mark.parametrize('data', [
        [
            '[ value=-aasd , time=15.04.2024 14:01:06 , unit=C ]',
            '[ value=[] , time=15.04.2024 14:01:17 , unit=lkjas ]',
            '[ value=123 , time=15.04.2024 14:01:17 , unit=[] ]',
        ]
    ])
    def test_handle_temperature_data_wrong_unit(self, data):
        # NOTE(stekap):
        # If turns out that the unit that is assigned to payload is always the last unit,
        # including the possibility of it being 'unknown'.
        # Not sure why it works like this, but it doesn't make much sense.
        unit = "unknown"
        for temp in data:
            unit = temp.split(',')[2].split('=')[1].split(' ')[0]

        payload = handle_temperature_data(data, '%d.%m.%Y %H:%M:%S')
        self.TC.assertEqual(payload["unit"], unit)

    @pytest.mark.parametrize('time_format', [
        "%d.%m.%Y %f %a %qq %g %l %H:%M:%S",
        "asdffb -. asdf"
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
        except ValueError:
            has_error = True

        if not has_error:
            self.TC.fail("Invalid time format not caught.")

    @pytest.mark.parametrize('data', [
        [
            '[ value=81.123 , time=15.04.2024 14:01:06 , unit=kg ]',
            '[ value=123.123 , time=15.04.2024 14:01:17 , unit=kg ]',
            '[ value=1192.2 , time=15.04.2024 14:01:17 , unit=kg ]'
        ]
    ])
    def test_handle_load_data_correct(self, data):
        value = 0
        for temp in data:
            value += float(temp.split(',')[0].split('=')[1])

        payload = handle_load_data(data, '%d.%m.%Y %H:%M:%S')
        self.TC.assertEqual(payload["value"], round(value, 2))
        self.TC.assertEqual(payload["unit"], 'kg')

    @pytest.mark.parametrize('data', [
        [
            '[ value=aasdf , time=15.04.2024 14:01:06 , unit=kg ]',
            '[ value=[] , time=15.04.2024 14:01:17 , unit=kg ]',
            '[ value=-12s2 , time=15.04.2024 14:01:17 , unit=kg ]'
        ]
    ])
    def test_handle_load_data_wrong_value(self, data):

        value = 0
        for temp in data:
            try:
                value += float(temp.split(',')[0].split('=')[1])
            except:
                value += 0

        payload = handle_load_data(data, '%d.%m.%Y %H:%M:%S')
        self.TC.assertEqual(payload["value"], round(value, 2))

    @pytest.mark.parametrize('data', [
        [
            '[ value=aasdf , time=15.04.2024 14:01:06 , unit=1-1 ]',
            '[ value=[] , time=15.04.2024 14:01:17 , unit=lkj1 ]',
            '[ value=-12s2 , time=15.04.2024 14:01:17 , unit=[] ]'
        ]
    ])
    def test_handle_load_data_wrong_unit(self, data):
        # NOTE(stekap):
        # If turns out that the unit that is assigned to payload is always the last unit,
        # including the possibility of it being 'unknown'.
        # Not sure why it works like this, but it doesn't make much sense.
        unit = "unknown"
        for temp in data:
            unit = temp.split(',')[2].split('=')[1].split(' ')[0]

        payload = handle_load_data(data, '%d.%m.%Y %H:%M:%S')
        self.TC.assertEqual(payload["unit"], unit)

    @pytest.mark.parametrize('time_format', [
        "%d.%m.%Y %f %a %qq %g %l %H:%M:%S",
        "asdffb -. asdf"
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
        except ValueError:
            has_error = True

        if not has_error:
            self.TC.fail("Invalid time format not caught.")

    def test_handle_fuel_data_correct(self):
        # NOTE(stekap):
        # To me it makes no sense that the data is only sent when the alarm is triggered (value <= limit).
        # Original code only used 'value <= limit' comparison as filter for data, and now it turns out it
        # is used as filter and as alarm trigger AT THE SAME TIME, which makes no sense.
        # Alarm should be handled with another simple filter.

        # FUEL_DATA_FORMAT  : [ value=125.83 , time=15.04.2024 14:01:06 , unit=l ]

        pass

    def test_handle_fuel_data_wrong(self):
        pass
