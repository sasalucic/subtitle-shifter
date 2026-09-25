from flask import Flask, render_template, request, jsonify
from pathlib import Path
import os
import re
import shutil

APP_VERSION = "1.0.0"
app = Flask(__name__)

MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", "/media")).resolve()
PORT = int(os.environ.get("PORT", "5070"))
PREVIEW_LINES = int(os.environ.get("PREVIEW_LINES", "80"))
BACKUP_SUFFIX = ".bak"
TIMECODE_RE = re.compile(r"(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2}),(?P<ms>\d{3})")


def safe_resolve(relative_path: str) -> Path:
    p = (MEDIA_ROOT / (relative_path or "")).resolve()
    if p != MEDIA_ROOT and MEDIA_ROOT not in p.parents:
        raise ValueError("Neispravna putanja.")
    return p


def read_subtitle(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1250", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Nepoznat encoding titla.")


def list_srt_files():
    if not MEDIA_ROOT.exists():
        return []
    files = []
    for p in MEDIA_ROOT.rglob("*.srt"):
        try:
            rel = p.relative_to(MEDIA_ROOT)
            stat = p.stat()
        except (ValueError, OSError):
            continue
        files.append({
            "path": rel.as_posix(),
            "name": p.name,
            "folder": "" if str(rel.parent) == "." else rel.parent.as_posix(),
            "size": stat.st_size,
            "has_backup": Path(str(p) + BACKUP_SUFFIX).exists(),
        })
    return sorted(files, key=lambda x: x["path"].casefold())


def shifted_timecode(match, delta_ms: int) -> str:
    h = int(match.group("h")); m = int(match.group("m")); s = int(match.group("s")); ms = int(match.group("ms"))
    total = max(0, ((h * 3600 + m * 60 + s) * 1000 + ms) + delta_ms)
    h, rem = divmod(total, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def ensure_backup(path: Path) -> Path:
    backup = Path(str(path) + BACKUP_SUFFIX)
    if not backup.exists():
        shutil.copy2(path, backup)
    return backup


@app.get("/")
def index():
    return render_template("index.html", version=APP_VERSION)


@app.get("/api/files")
def api_files():
    return jsonify({"ok": True, "root": str(MEDIA_ROOT), "files": list_srt_files(), "version": APP_VERSION})


@app.get("/api/preview")
def api_preview():
    try:
        p = safe_resolve(request.args.get("path", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if not p.exists() or p.suffix.lower() != ".srt":
        return jsonify({"ok": False, "error": "SRT fajl nije pronađen."}), 404
    try:
        text = read_subtitle(p)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Ne mogu pročitati titl: {e}"}), 500
    return jsonify({"ok": True, "preview": "\n".join(text.splitlines()[:PREVIEW_LINES]), "has_backup": Path(str(p) + BACKUP_SUFFIX).exists()})


@app.post("/api/shift")
def api_shift():
    data = request.get_json(silent=True) or {}
    try:
        delta_ms = int(data.get("delta_ms"))
        p = safe_resolve(data.get("path", ""))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Neispravan zahtjev."}), 400
    if not p.exists() or p.suffix.lower() != ".srt":
        return jsonify({"ok": False, "error": "SRT fajl nije pronađen."}), 404
    try:
        text = read_subtitle(p)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Ne mogu pročitati titl: {e}"}), 500
    count = len(TIMECODE_RE.findall(text))
    if count == 0:
        return jsonify({"ok": False, "error": "Nisu pronađeni SRT timestampovi."}), 400
    try:
        backup = ensure_backup(p)
        shifted = TIMECODE_RE.sub(lambda m: shifted_timecode(m, delta_ms), text)
        p.write_text(shifted, encoding="utf-8")
    except PermissionError:
        return jsonify({"ok": False, "error": "Nemam pravo pisanja nad ovim fajlom. Provjeri Docker volume permissions."}), 403
    except OSError as e:
        return jsonify({"ok": False, "error": f"Greška pri pisanju: {e}"}), 500
    return jsonify({"ok": True, "message": f"Pomjereno za {delta_ms / 1000:.3f} s", "timestamps_changed": count, "backup": backup.name})


@app.post("/api/restore")
def api_restore():
    data = request.get_json(silent=True) or {}
    try:
        p = safe_resolve(data.get("path", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    backup = Path(str(p) + BACKUP_SUFFIX)
    if not backup.exists():
        return jsonify({"ok": False, "error": "Backup ne postoji za ovaj titl."}), 404
    try:
        shutil.copy2(backup, p)
    except PermissionError:
        return jsonify({"ok": False, "error": "Nemam pravo pisanja nad ovim fajlom."}), 403
    except OSError as e:
        return jsonify({"ok": False, "error": f"Greška pri vraćanju backupa: {e}"}), 500
    return jsonify({"ok": True, "message": "Originalni titl vraćen iz .bak fajla."})


@app.get("/health")
def health():
    return jsonify({"ok": True, "version": APP_VERSION, "media_root": str(MEDIA_ROOT), "media_root_exists": MEDIA_ROOT.exists()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
