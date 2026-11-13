import unittest

from lan_speed_tester.cli import build_parser


class CLITests(unittest.TestCase):
    def test_server_defaults(self):
        args = build_parser().parse_args(["server"])
        self.assertEqual(args.host, "0.0.0.0")
        self.assertEqual(args.port, 8765)

    def test_test_defaults(self):
        args = build_parser().parse_args(["test", "192.168.1.10"])
        self.assertEqual(args.host, "192.168.1.10")
        self.assertEqual(args.port, 8765)
        self.assertEqual(args.duration, 10.0)
        self.assertFalse(args.json)

    def test_ping_defaults(self):
        args = build_parser().parse_args(["ping", "192.168.1.10"])
        self.assertEqual(args.count, 10)
        self.assertEqual(args.interval, 1.0)
        self.assertEqual(args.port, 8765)

    def test_udp_test_defaults(self):
        args = build_parser().parse_args(["udp-test", "192.168.1.10"])
        self.assertEqual(args.probes, 100)
        self.assertEqual(args.interval, 0.02)
        self.assertEqual(args.timeout, 1.0)
        self.assertEqual(args.port, 8765)

    def test_benchmark_profile_defaults(self):
        args = build_parser().parse_args(["benchmark", "192.168.1.10"])
        self.assertEqual(args.profile, "normal")
        self.assertIsNone(args.streams)
        self.assertIsNone(args.repeat)
        self.assertIsNone(args.duration)
        self.assertIsNone(args.chunk_size)
        self.assertFalse(args.json)

    def test_benchmark_overrides(self):
        args = build_parser().parse_args([
            "benchmark",
            "192.168.1.10",
            "--profile",
            "intensive",
            "--streams",
            "6",
            "--repeat",
            "2",
            "--duration",
            "1.5",
        ])
        self.assertEqual(args.profile, "intensive")
        self.assertEqual(args.streams, 6)
        self.assertEqual(args.repeat, 2)
        self.assertEqual(args.duration, 1.5)


if __name__ == "__main__":
    unittest.main()
