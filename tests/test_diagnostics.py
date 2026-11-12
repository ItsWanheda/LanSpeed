import math
import unittest

from lan_speed_tester.diagnostics import (
    LatencyStatistics,
    calculate_jitter_ms,
)


class DiagnosticsTests(unittest.TestCase):
    def test_latency_statistics(self):
        stats = LatencyStatistics.from_samples([10, 20, 30, 40, 50])

        self.assertEqual(stats.sample_count, 5)
        self.assertEqual(stats.min_ms, 10)
        self.assertEqual(stats.max_ms, 50)
        self.assertEqual(stats.average_ms, 30)
        self.assertEqual(stats.median_ms, 30)
        self.assertEqual(stats.p95_ms, 50)
        self.assertEqual(stats.p99_ms, 50)
        self.assertEqual(stats.jitter_ms, 10)

    def test_single_sample_has_zero_jitter(self):
        stats = LatencyStatistics.from_samples([12.5])
        self.assertEqual(stats.jitter_ms, 0.0)

    def test_jitter_uses_consecutive_sample_variation(self):
        self.assertEqual(calculate_jitter_ms([10, 30, 20]), 15)

    def test_empty_samples_are_rejected(self):
        with self.assertRaises(ValueError):
            LatencyStatistics.from_samples([])

    def test_invalid_samples_are_rejected(self):
        for samples in ([1, -1], [1, math.nan], [math.inf]):
            with self.subTest(samples=samples):
                with self.assertRaises(ValueError):
                    LatencyStatistics.from_samples(samples)


if __name__ == "__main__":
    unittest.main()
