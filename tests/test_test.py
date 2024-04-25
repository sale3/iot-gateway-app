import unittest


class TestTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_test(self):
        number = 5 + 5
        self.assertEqual(number, 10)