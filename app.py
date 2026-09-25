from flask import Flask, render_template, request, jsonify
from pathlib import Path
import os, re, shutil

APP_VERSION = "1.1.0"
app = Flask(__name__)
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", "/media")).resolve()
PORT = int(os.environ.get("PORT", "5070"))
PREVIEW_LINES = int(os.environ.get("PREVIEW_LINES", "80"))
BACKUP_SUFFIX = ".bak"
TIMECODE_RE = re.compile(r"(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2}),(?P<ms>\d{3})")

def safe_resolve(rel):
    p=(MEDIA_ROOT/(rel or "")).resolve()
    if p != MEDIA_ROOT and MEDIA_ROOT not in p.parents:
        raise ValueError("INVALID_PATH")
    return p

def read_subtitle(path):
    for enc in ("utf-8-sig","utf-8","cp1250","latin-1"):
        try: return path.read_text(encoding=enc)
        except UnicodeDecodeError: pass
    raise UnicodeError("UNKNOWN_ENCODING")

def list_srt_files():
    if not MEDIA_ROOT.exists(): return []
    out=[]
    for p in MEDIA_ROOT.rglob("*.srt"):
        try:
            rel=p.relative_to(MEDIA_ROOT); st=p.stat()
        except (ValueError,OSError):
            continue
        out.append({"path":rel.as_posix(),"name":p.name,"folder":"" if str(rel.parent)=="." else rel.parent.as_posix(),"size":st.st_size,"has_backup":Path(str(p)+BACKUP_SUFFIX).exists()})
    return sorted(out,key=lambda x:x["path"].casefold())

def shift_tc(m,delta):
    h,mi,s,ms=map(int,(m.group("h"),m.group("m"),m.group("s"),m.group("ms")))
    total=max(0,((h*3600+mi*60+s)*1000+ms)+delta)
    h,rem=divmod(total,3600000); mi,rem=divmod(rem,60000); s,ms=divmod(rem,1000)
    return f"{h:02}:{mi:02}:{s:02},{ms:03}"

def ensure_backup(p):
    b=Path(str(p)+BACKUP_SUFFIX)
    if not b.exists(): shutil.copy2(p,b)
    return b

def err(code,status=400,detail=None):
    d={"ok":False,"error_code":code}
    if detail: d["detail"]=detail
    return jsonify(d),status

@app.get("/")
def index(): return render_template("index.html",version=APP_VERSION)

@app.get("/api/files")
def files(): return jsonify({"ok":True,"root":str(MEDIA_ROOT),"files":list_srt_files(),"version":APP_VERSION})

@app.get("/api/preview")
def preview():
    try: p=safe_resolve(request.args.get("path",""))
    except ValueError: return err("INVALID_PATH",400)
    if not p.exists() or p.suffix.lower()!=".srt": return err("SRT_NOT_FOUND",404)
    try: txt=read_subtitle(p)
    except Exception as e: return err("READ_FAILED",500,str(e))
    return jsonify({"ok":True,"preview":"\n".join(txt.splitlines()[:PREVIEW_LINES]),"has_backup":Path(str(p)+BACKUP_SUFFIX).exists()})

@app.post("/api/shift")
def shift():
    d=request.get_json(silent=True) or {}
    try: delta=int(d.get("delta_ms")); p=safe_resolve(d.get("path",""))
    except (TypeError,ValueError): return err("INVALID_REQUEST",400)
    if not p.exists() or p.suffix.lower()!=".srt": return err("SRT_NOT_FOUND",404)
    try: txt=read_subtitle(p)
    except Exception as e: return err("READ_FAILED",500,str(e))
    count=len(TIMECODE_RE.findall(txt))
    if not count: return err("NO_TIMESTAMPS",400)
    try:
        backup=ensure_backup(p)
        p.write_text(TIMECODE_RE.sub(lambda m:shift_tc(m,delta),txt),encoding="utf-8")
    except PermissionError: return err("WRITE_PERMISSION",403)
    except OSError as e: return err("WRITE_FAILED",500,str(e))
    return jsonify({"ok":True,"delta_ms":delta,"timestamps_changed":count,"backup":backup.name})

@app.post("/api/restore")
def restore():
    d=request.get_json(silent=True) or {}
    try: p=safe_resolve(d.get("path",""))
    except ValueError: return err("INVALID_PATH",400)
    b=Path(str(p)+BACKUP_SUFFIX)
    if not b.exists(): return err("BACKUP_NOT_FOUND",404)
    try: shutil.copy2(b,p)
    except PermissionError: return err("WRITE_PERMISSION",403)
    except OSError as e: return err("RESTORE_FAILED",500,str(e))
    return jsonify({"ok":True})

@app.get("/health")
def health(): return jsonify({"ok":True,"version":APP_VERSION,"media_root":str(MEDIA_ROOT),"media_root_exists":MEDIA_ROOT.exists()})

if __name__=="__main__": app.run(host="0.0.0.0",port=PORT)
