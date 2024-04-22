import unittest
from src.rest_api import start_rest_api


class TestRestApi(unittest.TestCase):
    TC = unittest.TestCase()

    def test_start_rest_api_setup_without_run(self):
        try:
            start_rest_api("xxx", -1)
        except:
            pass

