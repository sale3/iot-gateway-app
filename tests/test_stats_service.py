import time
import unittest
import pytest
from tests.mock_util import create_mock
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

    @pytest.mark.parametrize('time_format', [
        "%d.%m.%Y %f %a %qq %% -.as %a %g %l %H:%M:%S",
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
        except:
            has_error = True

        if not has_error:
            self.TC.fail("Invalid time format not caught.")
