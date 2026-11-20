#!/usr/bin/env python3
"""
Removes stale Cursor inlineDiff rows from state.vscdb where the referenced
file no longer exists on disk. Safe to run with Cursor closed.
"""

import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import unquote, urlparse

DB = Path.home() / "Library/Application Support/Cursor/User/globalStorage/state.vscdb"


def uri_to_path(uri: str) -> Optional[Path]:
    try:
        parsed = urlparse(uri)
        if parsed.scheme != "file":
            return None
        return Path(unquote(parsed.path))
    except Exception:
        return None


def main(dry_run: bool = False) -> None:
    if not DB.exists():
        print(f"Database not found: {DB}")
        sys.exit(1)

    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT key, value FROM cursorDiskKV WHERE key LIKE 'inlineDiff:%'"
    ).fetchall()

    if not rows:
        print("No inlineDiff rows found.")
        con.close()
        return

    stale_keys = []
    for key, value in rows:
        try:
            data = json.loads(value)
            uri = data.get("uri", {}).get("external", "")
        except (json.JSONDecodeError, AttributeError):
            uri = ""

        path = uri_to_path(uri)
        exists = path is not None and path.exists()
        status = "OK  " if exists else "STALE"
        print(f"  [{status}] {key}\n         {uri or '(no uri)'}")

        if not exists:
            stale_keys.append(key)

    print(f"\n{len(stale_keys)} stale / {len(rows)} total")

    if not stale_keys:
        print("Nothing to delete.")
        con.close()
        return

    if dry_run:
        print("Dry run — nothing deleted. Re-run without --dry-run to delete.")
        con.close()
        return

    con.executemany(
        "DELETE FROM cursorDiskKV WHERE key = ?",
        [(k,) for k in stale_keys],
    )
    con.commit()
    con.close()
    print("Deleted.")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
