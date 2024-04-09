import unittest
import pytest
import time
from src.stats_service import Stats, OverallStats


class TestStatsService(object):
    TC = unittest.TestCase()

    @pytest.mark.parametrize('bytes,forwarded,requests', [
        (2, 3, 4),
        (0, 0, 0),
        (-1, 123, 1),
    ])
    def test_stats_update_data_correct(self, bytes, forwarded, requests):
        stats = Stats()

        # Initial state
        stats.update_data(bytes, forwarded, requests)
        self.TC.assertEqual(stats.dataBytes, bytes)
        self.TC.assertEqual(stats.dataBytesForwarded, forwarded)
        self.TC.assertEqual(stats.dataRequests, requests)

        # Non-initial state
        stats.update_data(bytes, forwarded, requests)
        self.TC.assertEqual(stats.dataBytes, 2 * bytes)
        self.TC.assertEqual(stats.dataBytesForwarded, 2 * forwarded)
        self.TC.assertEqual(stats.dataRequests, 2 * requests)

    @pytest.mark.parametrize('bytes,forwarded,requests', [
        (1, 2, 'f'),
        ('as', 2, 2),
        (-1, 'asdf', 2),
        ([], 1, 2)
    ])
    def test_stats_update_data_wrong(self, bytes, forwarded, requests):
        stats = Stats()
        self.TC.assertRaises(Exception, stats.update_data, bytes, forwarded, requests)

    @pytest.mark.parametrize('temp_stats_arr,load_stats_arr,fuel_stats_arr,time_format', [
        ([1, 1, 1], [2, 2, 2], [3, 3, 3], "%d.%m.%Y %f %a %qq %g %l %H:%M:%S")
    ])
    def test_overall_stats_combine_stats_wrong(self,
                                               temp_stats_arr,
                                               load_stats_arr,
                                               fuel_stats_arr,
                                               time_format):
        """
        self.tempDataBytes = temp_stats.dataBytes
        self.tempDataBytesForwarded = temp_stats.dataBytesForwarded
        self.tempDataRequests = temp_stats.dataRequests
        self.loadDataBytes = load_stats.dataBytes
        self.loadDataBytesForwarded = load_stats.dataBytesForwarded
        self.loadDataRequests = load_stats.dataRequests
        self.fuelDataBytes = fuel_stats.dataBytes
        self.fuelDataBytesForwarded = fuel_stats.dataBytesForwarded
        self.fuelDataRequests = fuel_stats.dataRequests

        self.endTime = time.strftime(self.time_pattern, time.localtime())
        payload = {"startTime": self.startTime,
                   "endTime": self.endTime,
                   "tempDataBytes": self.tempDataBytes,
                   "tempDataBytesForwarded": self.tempDataBytesForwarded,
                   "tempDataRequests": self.tempDataRequests,
                   "loadDataBytes": self.loadDataBytes,
                   "loadDataBytesForwarded": self.loadDataBytesForwarded,
                   "loadDataRequests": self.loadDataRequests,
                   "fuelDataBytes": self.fuelDataBytes,
                   "fuelDataBytesForwarded": self.fuelDataBytesForwarded,
                   "fuelDataRequests": self.fuelDataRequests}
        return payload
        """
        temp_stats = Stats()
        temp_stats.update_data(temp_stats_arr[0], temp_stats_arr[1], temp_stats_arr[2])
        load_stats = Stats()
        load_stats.update_data(load_stats_arr[0], load_stats_arr[1], load_stats_arr[2])
        fuel_stats = Stats()
        fuel_stats.update_data(fuel_stats_arr[0], fuel_stats_arr[1], fuel_stats_arr[2])

        overall_stats = OverallStats(time_format)
        resp = overall_stats.combine_stats(temp_stats, load_stats, fuel_stats)

        if resp["endTime"] == time_format:
            self.TC.fail("Time format string not supported")
        else:
            self.TC.assertRaises(ValueError, overall_stats.combine_stats, temp_stats, load_stats, fuel_stats)

        f = open("ffff.txt", "w")
        f.write(time.strftime("", time.localtime()))
        f.close()
