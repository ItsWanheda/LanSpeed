import unittest

from lan_speed_tester.interfaces import discover_interfaces


class InterfaceDiscoveryTests(unittest.TestCase):
    def test_discovery_returns_documented_shape(self):
        result = discover_interfaces()
        self.assertIn(result["source"], ("psutil", "python-standard-library"))
        self.assertIn(result["detail_level"], ("per-interface", "best-effort-host-addresses"))
        self.assertIsInstance(result["interfaces"], list)

        if result["source"] == "psutil":
            for interface in result["interfaces"]:
                self.assertIn("name", interface)
                self.assertIn("addresses", interface)
                self.assertIsInstance(interface["addresses"], list)
        else:
            self.assertIn("host_addresses", result)
            self.assertIn("note", result)


if __name__ == "__main__":
    unittest.main()
