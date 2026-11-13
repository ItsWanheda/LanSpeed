import csv
import json
import tempfile
import unittest
from pathlib import Path

from lan_speed_tester.history import HistoryStore


class HistoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "history.sqlite3"
        self.store = HistoryStore(self.database)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_list_get_and_compare(self):
        first_id = self.store.save(
            "benchmark",
            {
                "host": "192.168.1.10",
                "port": 8765,
                "summary": {
                    "download": {"average_mbps": 100.0},
                    "upload": {"average_mbps": 40.0},
                },
            },
        )
        second_id = self.store.save(
            "benchmark",
            {
                "host": "192.168.1.10",
                "port": 8765,
                "summary": {
                    "download": {"average_mbps": 125.0},
                    "upload": {"average_mbps": 30.0},
                },
            },
        )

        self.assertEqual(len(self.store.list_results()), 2)
        self.assertEqual(self.store.get(first_id)["result"]["host"], "192.168.1.10")

        comparison = self.store.compare(first_id, second_id)
        self.assertEqual(comparison["download"]["delta_mbps"], 25.0)
        self.assertEqual(comparison["download"]["change_percent"], 25.0)
        self.assertEqual(comparison["upload"]["delta_mbps"], -10.0)

    def test_export_json_csv_and_standalone_html(self):
        self.store.save(
            "test",
            {
                "host": "<script>alert(1)</script>",
                "port": 8765,
                "download": {"throughput_mbps": 88.5},
                "upload": {"throughput_mbps": 44.25},
            },
        )
        json_path = self.store.export(
            Path(self.temp_dir.name) / "history.json", "json"
        )
        csv_path = self.store.export(
            Path(self.temp_dir.name) / "history.csv", "csv"
        )
        html_path = self.store.export(
            Path(self.temp_dir.name) / "history.html", "html"
        )

        data = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["download_mbps"], 88.5)

        with csv_path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[0]["upload_mbps"], "44.25")

        html_report = html_path.read_text(encoding="utf-8")
        self.assertIn("<!doctype html>", html_report.lower())
        self.assertIn("&lt;script&gt;", html_report)
        self.assertNotIn("<script>alert(1)</script>", html_report)

    def test_missing_comparison_entry_raises(self):
        with self.assertRaises(KeyError):
            self.store.compare(1, 2)

    def test_invalid_limits_and_formats_are_rejected(self):
        with self.assertRaises(ValueError):
            self.store.list_results(0)
        with self.assertRaises(ValueError):
            self.store.export(
                Path(self.temp_dir.name) / "history.txt",
                "xml",
            )


if __name__ == "__main__":
    unittest.main()
