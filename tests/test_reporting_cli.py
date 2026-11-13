import unittest

from lan_speed_tester.cli import build_parser


class ReportingCLITests(unittest.TestCase):
    def test_history_list_command(self):
        args = build_parser().parse_args(["history", "list", "--limit", "5"])
        self.assertEqual(args.command, "history")
        self.assertEqual(args.history_action, "list")
        self.assertEqual(args.limit, 5)

    def test_history_compare_command(self):
        args = build_parser().parse_args(["history", "compare", "3", "8"])
        self.assertEqual(args.first_id, 3)
        self.assertEqual(args.second_id, 8)

    def test_history_export_command(self):
        args = build_parser().parse_args([
            "history", "export", "--format", "csv", "--output", "out.csv"
        ])
        self.assertEqual(args.format, "csv")
        self.assertEqual(args.output, "out.csv")

    def test_interface_command(self):
        args = build_parser().parse_args(["interfaces", "--json"])
        self.assertEqual(args.command, "interfaces")
        self.assertTrue(args.json)


if __name__ == "__main__":
    unittest.main()
