"""Persistent local history and report exports for LANSpeed."""

from __future__ import annotations

import csv
import html
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def default_history_path() -> Path:
    """Return the per-user default SQLite history location."""
    return Path.home() / ".lanspeed" / "history.sqlite3"


class HistoryStore:
    """Store completed test results in a local SQLite database."""

    def __init__(self, database: str | Path | None = None) -> None:
        self.path = Path(database).expanduser() if database else default_history_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10.0)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS test_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    host TEXT,
                    port INTEGER,
                    download_mbps REAL,
                    upload_mbps REAL,
                    result_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_test_history_created_at "
                "ON test_history(created_at)"
            )

    @staticmethod
    def _metrics(payload: dict[str, Any]) -> tuple[float | None, float | None]:
        download = payload.get("download")
        upload = payload.get("upload")
        summary = payload.get("summary", {})
        if isinstance(download, dict):
            download = download.get("throughput_mbps")
        else:
            download = None
        if isinstance(upload, dict):
            upload = upload.get("throughput_mbps")
        else:
            upload = None
        if download is None and isinstance(summary, dict):
            download = summary.get("download", {}).get("average_mbps")
        if upload is None and isinstance(summary, dict):
            upload = summary.get("upload", {}).get("average_mbps")
        return download, upload

    def save(self, test_type: str, payload: dict[str, Any]) -> int:
        """Persist a JSON-serializable test result and return its row ID."""
        if not test_type:
            raise ValueError("test_type is required")
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary")
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        download, upload = self._metrics(payload)
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO test_history
                    (created_at, test_type, host, port,
                     download_mbps, upload_mbps, result_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    test_type,
                    payload.get("host"),
                    payload.get("port"),
                    download,
                    upload,
                    encoded,
                ),
            )
            return int(cursor.lastrowid)

    def list_results(self, limit: int = 20) -> list[dict[str, Any]]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, test_type, host, port,
                       download_mbps, upload_mbps
                FROM test_history ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get(self, result_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM test_history WHERE id = ?", (result_id,)
            ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["result"] = json.loads(result.pop("result_json"))
        return result

    def compare(self, first_id: int, second_id: int) -> dict[str, Any]:
        first = self.get(first_id)
        second = self.get(second_id)
        if first is None or second is None:
            missing = first_id if first is None else second_id
            raise KeyError(f"history entry {missing} was not found")

        def delta(key: str) -> dict[str, float | None]:
            before, after = first[key], second[key]
            if before is None or after is None:
                return {"first_mbps": before, "second_mbps": after, "delta_mbps": None, "change_percent": None}
            difference = after - before
            percent = (difference / before * 100.0) if before else None
            return {
                "first_mbps": before,
                "second_mbps": after,
                "delta_mbps": round(difference, 3),
                "change_percent": round(percent, 2) if percent is not None else None,
            }

        return {
            "first": {key: first[key] for key in ("id", "created_at", "test_type", "host", "port")},
            "second": {key: second[key] for key in ("id", "created_at", "test_type", "host", "port")},
            "download": delta("download_mbps"),
            "upload": delta("upload_mbps"),
        }

    def export(self, output: str | Path, format_name: str = "json") -> Path:
        """Export all saved records to JSON, CSV, or a standalone HTML report."""
        target = Path(output).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        records = self._all_records()
        if format_name == "json":
            target.write_text(
                json.dumps(records, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        elif format_name == "csv":
            fields = [
                "id", "created_at", "test_type", "host", "port",
                "download_mbps", "upload_mbps", "result_json",
            ]
            with target.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                for record in records:
                    row = {key: record.get(key) for key in fields}
                    row["result_json"] = json.dumps(
                        record["result"], ensure_ascii=False, separators=(",", ":")
                    )
                    writer.writerow(row)
        elif format_name == "html":
            target.write_text(self._html_report(records), encoding="utf-8")
        else:
            raise ValueError("format must be one of: json, csv, html")
        return target

    def _all_records(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM test_history ORDER BY id ASC"
            ).fetchall()
        records = []
        for row in rows:
            item = dict(row)
            item["result"] = json.loads(item.pop("result_json"))
            records.append(item)
        return records

    @staticmethod
    def _html_report(records: Iterable[dict[str, Any]]) -> str:
        rows = []
        for record in records:
            values = (
                record.get("id"),
                record.get("created_at"),
                record.get("test_type"),
                record.get("host") or "-",
                record.get("download_mbps"),
                record.get("upload_mbps"),
            )
            cells = "".join(
                f"<td>{html.escape(str(value if value is not None else '-'))}</td>"
                for value in values
            )
            rows.append(f"<tr>{cells}</tr>")
        body = "\n".join(rows) or '<tr><td colspan="6">No saved tests yet.</td></tr>'
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LANSpeed Test History</title>
<style>
:root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
body {{ max-width: 1100px; margin: 40px auto; padding: 0 20px; }}
h1 {{ margin-bottom: 8px; }}
p {{ opacity: .75; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 24px; }}
th, td {{ padding: 12px; border-bottom: 1px solid #8886; text-align: left; }}
th {{ background: #8882; }}
tr:hover {{ background: #8881; }}
</style>
</head>
<body>
<h1>LANSpeed Test History</h1>
<p>{len(rows)} saved result(s). Generated by LANSpeed.</p>
<table>
<thead><tr><th>ID</th><th>Date (UTC)</th><th>Test</th><th>Host</th><th>Download Mbps</th><th>Upload Mbps</th></tr></thead>
<tbody>{body}</tbody>
</table>
</body>
</html>
"""
