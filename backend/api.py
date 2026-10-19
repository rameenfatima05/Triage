"""uvicorn api:app --reload   ->  http://localhost:8000/docs
All routes take optional ?subject= (default class9_math). Uploads go to a per-?session= copy, never the shared data."""
import os, shutil, tempfile
from typing import Optional, List
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import service as svc
import subjects as S
app = FastAPI(title="Triage backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
def _wrap(fn, *a, **k):
    try: return fn(*a, **k)
    except svc.ServiceError as e: raise HTTPException(e.code, e.msg)
@app.get("/health")
def health():
    import extract
    return {"ok": True, "reader": "demo" if os.getenv("TRIAGE_MOCK_EXTRACT")=="1" else (extract.provider() or "none (set a key)")}
@app.get("/subjects")
def subjects(): return [dict(id=k, title=v["title"], topics=len(v["topics"]), new_topics=len(v["new_ids"])) for k, v in S.SUBJECTS.items()]
@app.get("/topics")
def topics(subject: str = "class9_math", session: Optional[str] = None): return _wrap(svc.results, subject, session)
@app.get("/plan")
def get_plan(hours: float = 8, subject: str = "class9_math", session: Optional[str] = None, include_new: bool = True, new_share: float = 0.3):
    return _wrap(svc.get_plan, subject, hours, session, include_new, new_share)
@app.get("/backtest")
def get_backtest(subject: str = "class9_math"): return _wrap(svc.results, subject)["backtest"]
@app.delete("/session")
def reset(session: str, subject: str = "class9_math"): return _wrap(svc.reset_session, subject, session)
@app.post("/analyze")
def analyze(year: int = Form(...), group: int = Form(...), session: str = Form(...), subject: str = Form("class9_math"), files: List[UploadFile] = File(...)):
    sizes = []
    for f in files: f.file.seek(0, 2); sizes.append((f.filename or "", f.file.tell())); f.file.seek(0)
    _wrap(svc.validate_files, sizes)
    tmp, paths = tempfile.mkdtemp(), []
    try:
        for i, f in enumerate(files):
            d = os.path.join(tmp, f"{i}_{os.path.basename(f.filename)}")
            with open(d, "wb") as out: shutil.copyfileobj(f.file, out)
            paths.append(d)
        return _wrap(svc.analyze, subject, session, year, group, paths)
    finally: shutil.rmtree(tmp, ignore_errors=True)
