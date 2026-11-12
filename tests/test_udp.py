import unittest

from lan_speed_tester.udp import UDPEchoServer, run_udp_probe_test


class UDPDiagnosticsTests(unittest.TestCase):
    def test_udp_echo_server_and_probe_metrics(self):
        server = UDPEchoServer(host="127.0.0.1", port=0)
        _host, port = server.start()

        try:
            result = run_udp_probe_test(
                host="127.0.0.1",
                port=port,
                probe_count=10,
                interval_seconds=0.005,
                timeout_seconds=0.5,
            )
        finally:
            server.stop()

        self.assertEqual(result.packets_sent, 10)
        self.assertGreater(result.packets_received, 0)
        self.assertEqual(
            result.packets_lost,
            result.packets_sent - result.packets_received,
        )
        self.assertGreaterEqual(result.packet_loss_percent, 0.0)
        self.assertLessEqual(result.packet_loss_percent, 100.0)
        self.assertIsNotNone(result.latency)
        self.assertGreaterEqual(result.jitter_ms, 0.0)

    def test_udp_result_is_json_serializable(self):
        server = UDPEchoServer(host="127.0.0.1", port=0)
        _host, port = server.start()

        try:
            result = run_udp_probe_test(
                host="127.0.0.1",
                port=port,
                probe_count=2,
                interval_seconds=0.005,
                timeout_seconds=0.5,
            )
        finally:
            server.stop()

        payload = result.to_dict()
        self.assertEqual(payload["protocol"], "udp")
        self.assertEqual(payload["packets_sent"], 2)
        self.assertIn("packet_loss_percent", payload)


if __name__ == "__main__":
    unittest.main()
