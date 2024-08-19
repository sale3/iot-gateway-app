import unittest
from parameterized import parameterized
from src.stats_service import Stats, OverallStats


class TestStatsService(unittest.TestCase):
    @parameterized.expand([
        [2, 3, 4],
        [0, 0, 0],
        [-1, 123, 1],
    ])
    def test_stats_update_data_correct(self, bytes, forwarded, requests):
        stats = Stats()

        # Initial state
        stats.update_data(bytes, forwarded, requests)
        self.assertEqual(stats.dataBytes, bytes)
        self.assertEqual(stats.dataBytesForwarded, forwarded)
        self.assertEqual(stats.dataRequests, requests)

        # Non-initial state
        stats.update_data(bytes, forwarded, requests)
        self.assertEqual(stats.dataBytes, 2 * bytes)
        self.assertEqual(stats.dataBytesForwarded, 2 * forwarded)
        self.assertEqual(stats.dataRequests, 2 * requests)

    @parameterized.expand([
        [1, 2, 'f'],
        ['as', 2, 2],
        [-1, 'asdf', 2],
        [[], 1, 2]
    ])
    def test_stats_update_data_wrong(self, bytes, forwarded, requests):
        stats = Stats()
        self.assertRaises(TypeError, stats.update_data, bytes, forwarded, requests)

    @parameterized.expand([
        ["%d.%m.%Y %f %a %qq %% %a %g %l %H:%M:%S"],
        ["asdffb -. asdf"]
    ])
    def dont_test_overall_stats_wrong_time_format(self,
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
            self.fail("Invalid time format not caught.")

    @parameterized.expand([
        [Stats(), Stats(), Stats()]
    ])
    def test_overall_stats_combine_stats(self, temp_stats, load_stats, fuel_stats):
        overall_stats = OverallStats("%d.%m.%Y %H:%M:%S")
        payload = overall_stats.combine_stats(temp_stats, load_stats, fuel_stats)
        self.assertIsNotNone(payload)
