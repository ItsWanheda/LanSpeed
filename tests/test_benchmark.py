import json
import threading
import time
import unittest

from lan_speed_tester.benchmark import (
    BENCHMARK_PROFILES,
    run_benchmark_suite,
)
from lan_speed_tester.server import LANSpeedServer


class BenchmarkIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = LANSpeedServer(host="127.0.0.1", port=0)
        cls.server_thread = threading.Thread(
            target=cls.server.start,
            daemon=True,
        )
        cls.server_thread.start()

        deadline = time.monotonic() + 5.0
        while not cls.server._running and time.monotonic() < deadline:
            time.sleep(0.01)

        if not cls.server._running:
            cls.server.stop()
            raise RuntimeError("LANSpeed server did not start for benchmark tests")

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        cls.server_thread.join(timeout=3.0)

    def test_profiles_have_increasing_intensity(self):
        quick = BENCHMARK_PROFILES["quick"]
        normal = BENCHMARK_PROFILES["normal"]
        intensive = BENCHMARK_PROFILES["intensive"]

        self.assertLessEqual(quick.streams, normal.streams)
        self.assertLessEqual(normal.streams, intensive.streams)
        self.assertLessEqual(quick.repeats, normal.repeats)
        self.assertLessEqual(normal.repeats, intensive.repeats)
        self.assertLessEqual(
            quick.duration_seconds,
            normal.duration_seconds,
        )
        self.assertLessEqual(
            normal.duration_seconds,
            intensive.duration_seconds,
        )

    def test_repeated_multi_stream_benchmark_and_progress(self):
        progress_events = []

        result = run_benchmark_suite(
            host="127.0.0.1",
            port=self.server.port,
            profile="quick",
            stream_count=2,
            repeat_count=2,
            duration_seconds=0.15,
            chunk_size=4096,
            timeout=3.0,
            progress_callback=(
                lambda run_number, run_count, direction, stream_id,
                total_bytes, elapsed: progress_events.append(
                    (run_number, direction, stream_id, total_bytes, elapsed)
                )
            ),
        )

        self.assertEqual(result.repeat_count, 2)
        self.assertEqual(result.stream_count, 2)
        self.assertEqual(len(result.runs), 2)

        for run in result.runs:
            self.assertEqual(len(run.streams), 2)
            self.assertGreater(run.download.bytes_transferred, 0)
            self.assertGreater(run.upload.bytes_transferred, 0)
            self.assertGreater(run.download.throughput_mbps, 0)
            self.assertGreater(run.upload.throughput_mbps, 0)

            self.assertEqual(
                run.download.bytes_transferred,
                sum(
                    stream.download.bytes_transferred
                    for stream in run.streams
                ),
            )
            self.assertEqual(
                run.upload.bytes_transferred,
                sum(
                    stream.upload.bytes_transferred
                    for stream in run.streams
                ),
            )

        directions = {event[1] for event in progress_events}
        self.assertEqual(directions, {"download", "upload"})
        self.assertTrue(any(event[2] == 2 for event in progress_events))

        payload = result.to_dict()
        encoded = json.dumps(payload)
        self.assertIn('"summary"', encoded)
        self.assertIn('"median_mbps"', encoded)
        self.assertEqual(len(payload["runs"]), 2)

    def test_invalid_benchmark_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            run_benchmark_suite(
                host="127.0.0.1",
                profile="unknown",
            )

        with self.assertRaises(ValueError):
            run_benchmark_suite(
                host="127.0.0.1",
                profile="quick",
                stream_count=0,
            )

        with self.assertRaises(ValueError):
            run_benchmark_suite(
                host="127.0.0.1",
                profile="quick",
                repeat_count=0,
            )


if __name__ == "__main__":
    unittest.main()
