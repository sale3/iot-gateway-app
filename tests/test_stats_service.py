import unittest
import pytest
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
        self.TC.assertRaises(TypeError, stats.update_data, bytes, forwarded, requests)

    @pytest.mark.parametrize('temp_stats_arr,load_stats_arr,fuel_stats_arr', [
        ([1, [], 1], [2, 2, 2], [3, 3, 3]),
        ([1, 1, 1], [2, 2, 2], [3, 'asd', 3]),
        ([1, 1, 1], [2, '2', 2], [3, 3, 3])
    ])
    def dont_test_overall_stats_combine_stats_wrong_stats_input(self,
                                                           temp_stats_arr,
                                                           load_stats_arr,
                                                           fuel_stats_arr):
        temp_stats = Stats()
        temp_stats.dataBytes = temp_stats_arr[0]
        temp_stats.dataRequests = temp_stats_arr[1]
        temp_stats.dataBytesForwarded = temp_stats_arr[2]

        load_stats = Stats()
        load_stats.dataBytes = load_stats_arr[0]
        load_stats.dataRequests = load_stats_arr[1]
        load_stats.dataBytesForwarded = load_stats_arr[2]

        fuel_stats = Stats()
        fuel_stats.dataBytes = fuel_stats_arr[0]
        fuel_stats.dataRequests = fuel_stats_arr[1]
        fuel_stats.dataBytesForwarded = fuel_stats_arr[2]

        time_format = "dd.MM.yyyy HH:mm:ss"

        overall_stats = OverallStats(time_format)
        self.TC.assertRaises(TypeError,
                             overall_stats.combine_stats,
                             temp_stats,
                             load_stats,
                             fuel_stats)

    @pytest.mark.parametrize('time_format', [
        "%d.%m.%Y %f %a %qq %g %l %H:%M:%S",
        "asdffb -. asdf"
    ])
    def test_overall_stats_wrong_time_format(self,
                                             time_format):
        dummy_stats = Stats()
        dummy_stats.update_data(0, 0, 0)

        has_error = False
        try:
            overall_stats = OverallStats(time_format)
            if overall_stats.startTime == time_format:
                has_error = True
            overall_stats.combine_stats(dummy_stats,
                                        dummy_stats,
                                        dummy_stats)
        except ValueError:
            has_error = True

        if not has_error:
            self.TC.fail("Invalid time format not caught.")
