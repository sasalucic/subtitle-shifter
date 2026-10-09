from flask import Flask, render_template, request, jsonify
from pathlib import Path
import os
import re
import shutil
import sqlite3
import tempfile

APP_VERSION = "1.2.3"

app = Flask(__name__)

MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", "/media")).resolve()
PORT = int(os.environ.get("PORT", "5070"))
PREVIEW_LINES = int(os.environ.get("PREVIEW_LINES", "80"))
STREAMPORT_DB = Path(os.environ.get("STREAMPORT_DB", "/streamport/streamport.db"))
STREAMPORT_SUBTITLE_DIR = os.environ.get("STREAMPORT_SUBTITLE_DIR", "STREAMPORT_TITLOVI").strip("/")
BACKUP_SUFFIX = ".bak"
SUPPORTED_EXTENSIONS = {".srt", ".vtt"}

TIMECODE_RE = re.compile(
    r"(?<!\d)(?:(?P<h>\d{1,3}):)?(?P<m>\d{2}):(?P<s>\d{2})(?P<sep>[,.])(?P<ms>\d{3})(?!\d)"
)

STREAMPORT_VTT_RE = re.compile(
    r"^(?P<media_id>\d+)\.(?P<language>[A-Za-z0-9_-]+)\.(?P<subtitle_id>\d+)\.vtt$",
    re.IGNORECASE,
)


def safe_resolve(relative_path: str) -> Path:
    p = (MEDIA_ROOT / (relative_path or "")).resolve()
    if p != MEDIA_ROOT and MEDIA_ROOT not in p.parents:
        raise ValueError("INVALID_PATH")
    return p


def read_subtitle(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1250", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, "UNKNOWN_ENCODING")


def is_supported_subtitle(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def parse_streamport_vtt(rel: Path):
    if rel.suffix.lower() != ".vtt":
        return None
    if STREAMPORT_SUBTITLE_DIR and STREAMPORT_SUBTITLE_DIR not in rel.parts:
        return None

    match = STREAMPORT_VTT_RE.match(rel.name)
    if not match:
        return None

    return {
        "media_id": int(match.group("media_id")),
        "language": match.group("language").lower(),
        "subtitle_id": int(match.group("subtitle_id")),
    }


def _query_streamport_media(db_path: Path, media_ids, uri_mode: str = "direct"):
    rows_by_id = {}
    if uri_mode == "direct":
        target = f"file:{db_path}?mode=ro"
        kwargs = {"uri": True, "timeout": 2.0}
    elif uri_mode == "immutable":
        target = f"file:{db_path}?mode=ro&immutable=1"
        kwargs = {"uri": True, "timeout": 2.0}
    else:
        target = str(db_path)
        kwargs = {"timeout": 2.0}

    with sqlite3.connect(target, **kwargs) as con:
        con.row_factory = sqlite3.Row
        for start in range(0, len(media_ids), 900):
            chunk = media_ids[start:start + 900]
            placeholders = ",".join("?" for _ in chunk)
            rows = con.execute(
                f"""
                SELECT id, title, kind, series, season, episode,
                       episode_title, year, path
                FROM media
                WHERE id IN ({placeholders})
                """,
                chunk,
            ).fetchall()
            for row in rows:
                rows_by_id[int(row["id"])] = dict(row)
    return rows_by_id


STREAMPORT_LOOKUP_STATE = {"mode": None, "error": None}


def load_streamport_media(media_ids):
    media_ids = sorted(set(media_ids))
    if not media_ids:
        STREAMPORT_LOOKUP_STATE.update(mode=None, error=None)
        return {}
    if not STREAMPORT_DB.is_file():
        STREAMPORT_LOOKUP_STATE.update(mode=None, error=f"Database not found: {STREAMPORT_DB}")
        return {}

    errors = []

    # Normal read-only connection first.
    try:
        rows = _query_streamport_media(STREAMPORT_DB, media_ids, "direct")
        STREAMPORT_LOOKUP_STATE.update(mode="direct-ro", error=None)
        return rows
    except (sqlite3.Error, OSError) as e:
        errors.append(f"direct-ro: {e}")

    # WAL databases on a read-only bind mount can fail because SQLite wants
    # shared-memory/locking access. immutable=1 avoids those writes.
    try:
        rows = _query_streamport_media(STREAMPORT_DB, media_ids, "immutable")
        STREAMPORT_LOOKUP_STATE.update(mode="immutable-ro", error=None)
        return rows
    except (sqlite3.Error, OSError) as e:
        errors.append(f"immutable-ro: {e}")

    # Final fallback: copy the DB (+ WAL if present) to writable /tmp and query
    # the snapshot there. StreamPort's files themselves stay strictly read-only.
    try:
        with tempfile.TemporaryDirectory(prefix="subtitle-shifter-streamport-") as td:
            td = Path(td)
            snap_db = td / "streamport.db"
            shutil.copy2(STREAMPORT_DB, snap_db)
            wal = Path(str(STREAMPORT_DB) + "-wal")
            if wal.is_file():
                shutil.copy2(wal, Path(str(snap_db) + "-wal"))
            rows = _query_streamport_media(snap_db, media_ids, "snapshot")
        STREAMPORT_LOOKUP_STATE.update(mode="tmp-snapshot", error=None)
        return rows
    except (sqlite3.Error, OSError, shutil.Error) as e:
        errors.append(f"tmp-snapshot: {e}")

    STREAMPORT_LOOKUP_STATE.update(mode=None, error=" | ".join(errors))
    return {}


def streamport_display_name(media):
    if not media:
        return None

    title = (media.get("series") or media.get("title") or "").strip()
    if media.get("kind") == "episode":
        try:
            season = int(media.get("season") or 0)
            episode = int(media.get("episode") or 0)
            title = f"{title} — S{season:02d}E{episode:02d}"
        except (TypeError, ValueError):
            pass

        episode_title = (media.get("episode_title") or "").strip()
        if episode_title:
            title = f"{title} — {episode_title}"

    return title or None


def list_subtitle_files():
    if not MEDIA_ROOT.exists():
        return []

    discovered = []
    streamport_ids = []

    # Scan only supported subtitle extensions. Avoid walking every file in large
    # media libraries (music, video, downloads, etc.) and filtering afterward.
    for pattern in ("*.srt", "*.vtt"):
        for p in MEDIA_ROOT.rglob(pattern):
            if not p.is_file():
                continue

            try:
                rel = p.relative_to(MEDIA_ROOT)
                stat = p.stat()
            except (ValueError, OSError):
                continue

            streamport = parse_streamport_vtt(rel)
            if streamport:
                streamport_ids.append(streamport["media_id"])

            discovered.append((p, rel, stat, streamport))

    media_map = load_streamport_media(streamport_ids)
    files = []

    for p, rel, stat, streamport in discovered:
        item = {
            "path": rel.as_posix(),
            "name": p.name,
            "display_name": p.name,
            "folder": "" if str(rel.parent) == "." else rel.parent.as_posix(),
            "size": stat.st_size,
            "type": p.suffix.lower().lstrip(".").upper(),
            "has_backup": Path(str(p) + BACKUP_SUFFIX).exists(),
            "streamport": False,
        }

        if streamport:
            media = media_map.get(streamport["media_id"])
            display_name = streamport_display_name(media)
            item.update(
                {
                    "streamport": True,
                    "streamport_media_id": streamport["media_id"],
                    "streamport_subtitle_id": streamport["subtitle_id"],
                    "subtitle_language": streamport["language"],
                    "display_name": display_name or p.name,
                    "media_kind": media.get("kind") if media else None,
                    "media_title": (media.get("series") or media.get("title")) if media else None,
                    "season": media.get("season") if media else None,
                    "episode": media.get("episode") if media else None,
                    "episode_title": media.get("episode_title") if media else None,
                }
            )

        files.append(item)

    files.sort(key=lambda x: (x.get("display_name") or x["path"]).casefold())
    return files


def shifted_timecode(match, delta_ms: int) -> str:
    h_raw = match.group("h")
    h = int(h_raw) if h_raw is not None else 0
    m = int(match.group("m"))
    s = int(match.group("s"))
    ms = int(match.group("ms"))
    sep = match.group("sep")

    total = ((h * 3600 + m * 60 + s) * 1000 + ms) + delta_ms
    total = max(0, total)

    h2, rem = divmod(total, 3_600_000)
    m2, rem = divmod(rem, 60_000)
    s2, ms2 = divmod(rem, 1000)

    if h_raw is None and h2 == 0:
        return f"{m2:02}:{s2:02}{sep}{ms2:03}"

    width = max(2, len(h_raw or ""))
    return f"{h2:0{width}d}:{m2:02}:{s2:02}{sep}{ms2:03}"


def ensure_backup(path: Path) -> Path:
    backup = Path(str(path) + BACKUP_SUFFIX)
    if not backup.exists():
        shutil.copy2(path, backup)
    return backup


def api_error(code: str, status: int = 400, detail: str | None = None):
    payload = {"ok": False, "error_code": code}
    if detail:
        payload["detail"] = detail
    return jsonify(payload), status


@app.get("/")
def index():
    return render_template("index.html", version=APP_VERSION)


@app.get("/api/files")
def api_files():
    return jsonify(
        {
            "ok": True,
            "root": str(MEDIA_ROOT),
            "files": list_subtitle_files(),
            "version": APP_VERSION,
            "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
            "streamport_db_available": STREAMPORT_DB.is_file(),
            "streamport_lookup_mode": STREAMPORT_LOOKUP_STATE.get("mode"),
            "streamport_lookup_error": STREAMPORT_LOOKUP_STATE.get("error"),
        }
    )


@app.get("/api/preview")
def api_preview():
    try:
        p = safe_resolve(request.args.get("path", ""))
    except ValueError:
        return api_error("INVALID_PATH", 400)

    if not p.exists() or not is_supported_subtitle(p):
        return api_error("SUBTITLE_NOT_FOUND", 404)

    try:
        text = read_subtitle(p)
    except Exception as e:
        return api_error("READ_FAILED", 500, str(e))

    return jsonify(
        {
            "ok": True,
            "preview": "\n".join(text.splitlines()[:PREVIEW_LINES]),
            "has_backup": Path(str(p) + BACKUP_SUFFIX).exists(),
            "type": p.suffix.lower().lstrip(".").upper(),
        }
    )


@app.post("/api/shift")
def api_shift():
    data = request.get_json(silent=True) or {}

    try:
        delta_ms = int(data.get("delta_ms"))
        p = safe_resolve(data.get("path", ""))
    except (TypeError, ValueError):
        return api_error("INVALID_REQUEST", 400)

    if not p.exists() or not is_supported_subtitle(p):
        return api_error("SUBTITLE_NOT_FOUND", 404)

    try:
        text = read_subtitle(p)
    except Exception as e:
        return api_error("READ_FAILED", 500, str(e))

    matches = list(TIMECODE_RE.finditer(text))
    if not matches:
        return api_error("NO_TIMESTAMPS", 400)

    try:
        backup = ensure_backup(p)
        shifted = TIMECODE_RE.sub(lambda m: shifted_timecode(m, delta_ms), text)
        p.write_text(shifted, encoding="utf-8")
    except PermissionError:
        return api_error("WRITE_PERMISSION", 403)
    except OSError as e:
        return api_error("WRITE_FAILED", 500, str(e))

    return jsonify(
        {
            "ok": True,
            "delta_ms": delta_ms,
            "timestamps_changed": len(matches),
            "backup": backup.name,
            "type": p.suffix.lower().lstrip(".").upper(),
        }
    )


@app.post("/api/restore")
def api_restore():
    data = request.get_json(silent=True) or {}

    try:
        p = safe_resolve(data.get("path", ""))
    except ValueError:
        return api_error("INVALID_PATH", 400)

    if not is_supported_subtitle(p):
        return api_error("SUBTITLE_NOT_FOUND", 404)

    backup = Path(str(p) + BACKUP_SUFFIX)

    if not backup.exists():
        return api_error("BACKUP_NOT_FOUND", 404)

    try:
        shutil.copy2(backup, p)
    except PermissionError:
        return api_error("WRITE_PERMISSION", 403)
    except OSError as e:
        return api_error("RESTORE_FAILED", 500, str(e))

    return jsonify({"ok": True})


@app.get("/health")
def health():
    return jsonify(
        {
            "ok": True,
            "version": APP_VERSION,
            "media_root": str(MEDIA_ROOT),
            "media_root_exists": MEDIA_ROOT.exists(),
            "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
            "streamport_db": str(STREAMPORT_DB),
            "streamport_db_available": STREAMPORT_DB.is_file(),
            "streamport_lookup_mode": STREAMPORT_LOOKUP_STATE.get("mode"),
            "streamport_lookup_error": STREAMPORT_LOOKUP_STATE.get("error"),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
