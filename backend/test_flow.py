"""python test_flow.py   - runs without FastAPI or an API key."""
import hashlib, json, os, shutil, tempfile
os.environ["TRIAGE_MOCK_EXTRACT"] = "1"
import service as svc, subjects as S, pipeline, extract as X
from model import fit, classify, plan
C9 = S.get("class9_math"); ok = []
def check(name, cond, extra=""):
    ok.append(cond); print(("PASS " if cond else "FAIL ")+name+(f"  {extra}" if extra and not cond else ""))
md5 = lambda f: hashlib.md5(open(f,"rb").read()).hexdigest()

r = svc.results("class9_math")
check("backtest unchanged (6/10/15h = 18/28/39.5)", [x["ours"] for x in r["backtest"]["results"]]==[18.0,28.0,39.5], r["backtest"]["results"])
check("new-syllabus topics present and categorised 'new'", sum(t["category"]=="new" for t in r["topics"])==len(C9["new_ids"])==20)
check("new topics have no confidence/marks claimed", all(t["confidence"] is None and t["expected_marks"]==0 for t in r["topics"] if t["category"]=="new"))
check("every topic has a study_hint", all("study_hint" in t for t in r["topics"]))

for h in (1,3,6,10,20):
    p = svc.get_plan("class9_math", h); mins = sum(s["minutes"] for s in p["study"])
    check(f"plan {h}h stays within budget", mins + p["break_minutes"] <= h*60 + 1, f"{mins}+{p['break_minutes']}")
p10, p10n = svc.get_plan("class9_math",10), svc.get_plan("class9_math",10,include_new=False)
check("new topics get minutes but add no predicted marks", p10["new_syllabus_minutes"]>0 and p10n["new_syllabus_minutes"]==0)
check("new topics span several chapters (breadth)", len({s["name"] for s in p10["study"] if s["category"]=="new"})>=3)
check("note warns they are not predictions", "not predictions" in p10["note"])

# a new topic upgrades itself once a paper contains it
papers = pipeline.load_papers(C9) + [dict(year=2025, group=1, source="t", items=[dict(slot="o",q="1.1",topic="prob_single",marks=1)])]
st = classify(fit(papers, C9))
check("new topic becomes a normal topic once it appears in a paper", st["prob_single"]["category"]!="new" and st["prob_single"]["appearances"]==1)

# sessions: shared data never changes
before = md5(C9["papers_path"]); sess = "testsession123"
a = svc.analyze("class9_math", sess, 2025, 1, ["x.jpg"])
check("analyze returns a mock warning", a["extraction"]=="demo_mock" and any("DEMO MODE" in w for w in a["warnings"]))
check("shared papers.json untouched by upload", md5(C9["papers_path"])==before)
check("session has 8 papers, base still 7", svc.results("class9_math",sess)["papers"]==8 and svc.results("class9_math")["papers"]==7)
check("other sessions unaffected", svc.results("class9_math","othersess456")["papers"]==7)
svc.reset_session("class9_math", sess); check("reset removes session", svc.results("class9_math",sess)["papers"]==7)

def err(fn, code):
    try: fn(); return False
    except svc.ServiceError as e: return e.code==code
check("bad year rejected", err(lambda: svc.analyze("class9_math","sess123456",1999,1,["x.jpg"]),422))
check("bad group rejected", err(lambda: svc.analyze("class9_math","sess123456",2024,3,["x.jpg"]),422))
check("bad session id rejected", err(lambda: svc.results("class9_math","../etc"),422))
check("unknown subject -> 404", err(lambda: svc.results("nope"),404))
check("hours out of range", err(lambda: svc.get_plan("class9_math",99),422))
check("no files rejected", err(lambda: svc.validate_files([]),422))
check("wrong extension rejected", err(lambda: svc.validate_files([("a.exe",10)]),415))
check("oversize rejected", err(lambda: svc.validate_files([("a.jpg",11*1024*1024)]),413))
check("too many files rejected", err(lambda: svc.validate_files([("a.jpg",1)]*11),413))
os.environ["TRIAGE_MOCK_EXTRACT"]="0"; os.environ.pop("ANTHROPIC_API_KEY",None)
check("no API key -> clear 503", err(lambda: svc.analyze("class9_math","sess123456",2025,1,["x.jpg"]),503))
os.environ["TRIAGE_MOCK_EXTRACT"]="1"

# extraction parsing helpers (the Claude call itself is NOT tested here - no key/network)
raw = X.parse_items('Here you go:\n```json\n[{"slot":"o","q":"1.1","topic":"log_def"},{"slot":"x","topic":"zzz"}]\n```')
items, review = X.clean(raw, C9)
check("parser strips fences/prose; bad slots dropped; unknown topic -> review", len(items)==1 and len(review)==0)
items2, review2 = X.clean([dict(slot="o",q="1",topic="made_up")], C9)
check("unknown topic goes to review list", len(review2)==1 and items2[0]["topic"]=="other")
check("quality warns when pages look missing", len(X.quality([dict(slot="o")]*3, C9)["warnings"])>=3)

# other subjects: one folder, no code changes
tmp = tempfile.mkdtemp(); d = os.path.join(tmp,"toy_physics"); os.makedirs(d)
json.dump(dict(title="Toy Physics", topics={"motion":["Motion","Kinematics",1.0],"heat":["Heat","Thermo",1.5],"light":["Light","Optics",1.0]},
    marks={"o":1,"s":2}, exam_total=20, book={"motion":{"unit":1,"section":"1.1","exercise":"1.1","page":5}}, units={"1":["Kinematics",1]}), open(os.path.join(d,"subject.json"),"w"))
yrs=[(2021,"motion heat"),(2022,"motion light"),(2023,"motion heat"),(2024,"motion heat")]
json.dump([dict(year=y,group=1,source="toy",items=[dict(slot="o",q=str(i),topic=t,marks=1) for i,t in enumerate(ts.split())]) for y,ts in yrs], open(os.path.join(d,"papers.json"),"w"))
reg = S.load_all(tmp); toy = reg["toy_physics"]; tr = pipeline.build(toy)
check("JSON subject loads and runs end to end", tr["papers"]==4 and tr["backtest"]["tested_on"]==2024 and len(tr["topics"])==3)
check("topic missing from the book map is flagged absent", [t for t in tr["topics"] if t["id"]=="heat"][0]["category"]=="park")
shutil.rmtree(tmp)

# Grok path with a mocked HTTP call (the real xAI endpoint is NOT reachable from the build sandbox)
from PIL import Image
img = os.path.join(tempfile.mkdtemp(),"p.jpg"); Image.new("RGB",(400,600),"white").save(img)
good = json.dumps([dict(slot="o",q=f"1.{i}",topic="log_def") for i in range(12)])
seen = {}
def fake(url, payload, key, timeout=120):
    seen.update(url=url, key=key, model=payload["model"], kinds=[c["type"] for c in payload["messages"][0]["content"]])
    return {"choices":[{"message":{"content":"Sure!\n```json\n"+good+"\n```"}}]}
real_post = X._post_json; X._post_json = fake
os.environ.update(TRIAGE_MOCK_EXTRACT="0", XAI_API_KEY="xai-test"); os.environ.pop("ANTHROPIC_API_KEY",None); os.environ.pop("TRIAGE_PROVIDER",None)
check("provider auto-picks xai when only XAI_API_KEY set", X.provider()=="xai")
g = svc.analyze("class9_math","grokses123",2025,1,[img])
check("grok path: parsed, tagged source=xai_vision", g["extraction"]=="xai_vision")
check("grok request: url, bearer key, image+text parts", seen["url"].endswith("/chat/completions") and seen["key"]=="xai-test" and seen["kinds"]==["image_url","text"], seen)
svc.reset_session("class9_math","grokses123")
X._post_json = lambda *a, **k: (_ for _ in ()).throw(X.ExtractError("Grok API error 401: bad key"))
check("grok API failure surfaces as 502", err(lambda: svc.analyze("class9_math","grokses123",2025,1,[img]),502))
X._post_json = real_post
os.environ.update(TRIAGE_PROVIDER="xai"); os.environ.pop("XAI_API_KEY")
check("provider forced to xai without a key -> 503", err(lambda: svc.analyze("class9_math","grokses123",2025,1,[img]),503))
os.environ.pop("TRIAGE_PROVIDER"); os.environ["TRIAGE_MOCK_EXTRACT"]="1"
print(f"\n{sum(ok)}/{len(ok)} passed"); raise SystemExit(0 if all(ok) else 1)
