"""All app logic with no web-framework dependency (so it is unit-testable). api.py is a thin wrapper."""
import json, os, re, shutil
import pipeline, subjects as S
from model import plan as _plan
import extract as X
MAX_FILES, MAX_MB, EXT = 10, 10, (".pdf", ".png", ".jpg", ".jpeg", ".webp")
class ServiceError(Exception):
    def __init__(self, code, msg): super().__init__(msg); self.code, self.msg = code, msg

def subject(sid):
    try: return S.get(sid)
    except KeyError: raise ServiceError(404, f"Unknown subject '{sid}'. Available: {', '.join(S.SUBJECTS)}")
def _sdir(sub, session):
    if not re.fullmatch(r"[A-Za-z0-9_-]{6,40}", session or ""): raise ServiceError(422, "session must be 6-40 letters, digits, - or _")
    return os.path.join(S.DATA, "sessions", sub["id"], session)
def results(sid="class9_math", session=None):
    sub = subject(sid)
    if session is None:
        return json.load(open(sub["results_path"], encoding="utf-8")) if os.path.exists(sub["results_path"]) else pipeline.build(sub, save_to=sub["results_path"])
    f = os.path.join(_sdir(sub, session), "results.json")
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else results(sid)
def get_plan(sid, hours, session=None, include_new=True, new_share=0.3):
    if not 0.5 <= hours <= 40: raise ServiceError(422, "hours must be between 0.5 and 40")
    if not 0 <= new_share <= 0.6: raise ServiceError(422, "new_share must be between 0 and 0.6")
    return _plan(results(sid, session)["topics"], hours, include_new=include_new, new_share=new_share)
def reset_session(sid, session):
    shutil.rmtree(_sdir(subject(sid), session), ignore_errors=True); return {"reset": True}

def validate_files(files):
    """files: list of (filename, size_bytes)."""
    if not files: raise ServiceError(422, "Upload at least one page.")
    if len(files) > MAX_FILES: raise ServiceError(413, f"At most {MAX_FILES} pages per paper.")
    for n, size in files:
        if not n.lower().endswith(EXT): raise ServiceError(415, f"{n}: only PDF, PNG, JPG or WEBP are supported.")
        if size > MAX_MB*1024*1024: raise ServiceError(413, f"{n}: larger than {MAX_MB} MB.")

def analyze(sid, session, year, group, paths, extractor=None):
    """Adds one paper to THIS session's copy of the data. The shared base dataset is never modified."""
    sub = subject(sid); d = _sdir(sub, session)
    if not 2000 <= year <= 2040: raise ServiceError(422, "year looks wrong")
    if group not in (1, 2): raise ServiceError(422, "group must be 1 or 2")
    try: new = (extractor or X.extract)(paths, year, group, sub)
    except X.ExtractError as e: raise ServiceError(503 if "API_KEY" in str(e) else (502 if "Grok API" in str(e) else 422), str(e))
    pf = os.path.join(d, "papers.json")
    base = json.load(open(pf, encoding="utf-8")) if os.path.exists(pf) else pipeline.load_papers(sub)
    papers = [p for p in base if (p["year"], p["group"]) != (year, group)] + [new]
    os.makedirs(d, exist_ok=True); json.dump(papers, open(pf, "w", encoding="utf-8"))
    r = pipeline.build(sub, papers, save_to=os.path.join(d, "results.json"), extraction=new["source"])
    return dict(papers=r["papers"], extraction=new["source"], needs_review=len(new["needs_review"]),
                warnings=new.get("quality", {}).get("warnings", []), backtest=r["backtest"])
