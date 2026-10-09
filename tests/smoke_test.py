#!/usr/bin/env python3
"""Offline smoke test for subtitle discovery and StreamPort mapping."""
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

with tempfile.TemporaryDirectory(prefix="subtitle-shifter-test-") as td:
    root = Path(td)
    media = root / "media"
    subs = media / "STREAMPORT_TITLOVI"
    data = root / "streamport"
    subs.mkdir(parents=True)
    data.mkdir()

    db = data / "streamport.db"
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE media (
        id INTEGER PRIMARY KEY, path TEXT NOT NULL, title TEXT, kind TEXT,
        series TEXT DEFAULT '', season INTEGER DEFAULT 0, episode INTEGER DEFAULT 0,
        episode_title TEXT DEFAULT '', year TEXT DEFAULT '')""")
    con.execute("INSERT INTO media VALUES (42, '/media/tv/example.mkv', 'Example Show', 'episode', 'Example Show', 1, 2, 'Example Episode', '2026')")
    con.commit()
    con.close()

    vtt = subs / "42.en.1234567.vtt"
    vtt.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nHello\n", encoding="utf-8")

    junk = media / "unrelated"
    junk.mkdir()
    for i in range(100):
        (junk / f"file-{i}.bin").write_bytes(b"x")

    os.environ["MEDIA_ROOT"] = str(media)
    os.environ["STREAMPORT_DB"] = str(db)
    os.environ["STREAMPORT_SUBTITLE_DIR"] = "STREAMPORT_TITLOVI"

    import app
    client = app.app.test_client()
    payload = client.get("/api/files").get_json()
    assert payload["ok"] is True
    assert len(payload["files"]) == 1
    item = payload["files"][0]
    assert item["display_name"] == "Example Show — S01E02 — Example Episode"

print("OK: smoke test passed")
