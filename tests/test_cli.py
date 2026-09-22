import unittest

from lan_speed_tester.cli import build_parser


class CLITests(unittest.TestCase):
    def test_server_defaults(self):
        args = build_parser().parse_args(["server"])
        self.assertEqual(args.host, "0.0.0.0")
        self.assertEqual(args.port, 5000)

    def test_test_defaults(self):
        args = build_parser().parse_args(["test", "192.168.1.10"])
        self.assertEqual(args.host, "192.168.1.10")
        self.assertEqual(args.port, 5000)
        self.assertEqual(args.duration, 5.0)


if __name__ == "__main__":
    unittest.main()
