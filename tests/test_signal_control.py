import unittest
import signal
from threading import Event
from parameterized import parameterized

from src.signal_control import BetterSignalHandler


class TestSignalControl(unittest.TestCase):
    @parameterized.expand([
        [[signal.SIGINT, signal.SIGTERM], [Event(), Event(), Event()]]
    ])
    def test_better_signal_handler_init_correct(self, sigs, flags):
        signal_handler = BetterSignalHandler(sigs, flags)

        # Check that new handler is assigned to every mentioned signal.
        for sig in signal_handler.sigs:
            self.assertEqual(signal_handler.handler, signal.getsignal(sig))

    @parameterized.expand([
        [[123, 123], [123, 123]],
        [[[], 123], [123, []]],
        [["asdf"], ["asdf"]]
    ])
    def test_better_signal_handler_init_wrong(self, sigs, flags):
        self.assertRaises(Exception, BetterSignalHandler.__init__, sigs, flags)

    def test_better_signal_handler_handler(self):
        signal_handler = BetterSignalHandler([signal.SIGINT, signal.SIGTERM],
                                             [Event(), Event(), Event()])

        signal_handler.handler(None, None)

        # Check that all flags are set.
        for flag in signal_handler.flags:
            self.assertTrue(flag.is_set())

        # Check that all signal handlers are returned to original.
        for sig, original_handler in zip(signal_handler.sigs, signal_handler.original_handlers):
            self.assertEqual(signal.getsignal(sig), original_handler)
