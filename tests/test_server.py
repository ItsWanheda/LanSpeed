import threading
import time
import unittest

from lan_speed_tester.client import ClientConfig, LANSpeedClient
from lan_speed_tester.server import LANSpeedServer
from lan_speed_tester.udp import run_udp_probe_test


class ServerDiagnosticsIntegrationTests(unittest.TestCase):
    def test_server_starts_tcp_and_udp_on_same_port(self):
        server = LANSpeedServer(host="127.0.0.1", port=0)
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()

        try:
            deadline = time.monotonic() + 3.0
            while not server._running and time.monotonic() < deadline:
                time.sleep(0.01)

            self.assertTrue(server._running)
            self.assertGreater(server.port, 0)

            udp_result = run_udp_probe_test(
                host="127.0.0.1",
                port=server.port,
                probe_count=5,
                interval_seconds=0.005,
                timeout_seconds=0.5,
            )
            self.assertGreater(udp_result.packets_received, 0)

            config = ClientConfig(
                host="127.0.0.1",
                port=server.port,
                duration=1.0,
                chunk_size=1024,
                timeout=1.0,
            )
            with LANSpeedClient(config) as client:
                latency = client.measure_latency()

            self.assertGreaterEqual(latency.latency_ms, 0.0)
        finally:
            server.stop()
            thread.join(timeout=3.0)

        self.assertFalse(thread.is_alive())


if __name__ == "__main__":
    unittest.main()
