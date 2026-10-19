import json, os
from model import fit, classify, backtest
import subjects as S

def hint(b):
    if b["status"]=="absent": return "Not in the new textbook"
    if b["status"]=="unknown": return ""
    ex = f" · Exercise {b['exercise']}" if b["exercise"] else ""
    pg = f" (p.{b['page']})" if b["page"] else ""
    return f"Study Unit {b['unit']}{ex}{pg}" + (" · check book" if b["status"]=="partial" or b.get("verify") else "")

def chapter_rollup(topics, units):
    ch = {u:dict(unit=u,name=n,page=p,expected_marks=0.0,topics=[]) for u,(n,p) in units.items()}
    gone = dict(expected_marks=0.0,topics=[])
    for t in topics:
        b = t["book"]; tgt = gone if b["status"]=="absent" else ch.get(b["unit"])
        if tgt is None: continue
        tgt["expected_marks"] += t["expected_marks"]; tgt["topics"].append(t["id"])
    by_id = {t["id"]:t for t in topics}
    for c in ch.values():
        c["expected_marks"] = round(c["expected_marks"],1)
        seen = any(by_id[i]["appearances"]>0 for i in c["topics"])
        c["evidence"] = "past-paper evidence" if seen else "no past-paper evidence (new in this syllabus)"
    gone["expected_marks"] = round(gone["expected_marks"],1)
    return dict(units=sorted(ch.values(), key=lambda c:-c["expected_marks"]), not_in_new_book=gone)

def load_papers(subject):
    return json.load(open(subject["papers_path"], encoding="utf-8"))

def build(subject, papers=None, save_to=None, extraction="seed"):
    papers = papers or load_papers(subject); stats = classify(fit(papers, subject))
    for s in stats.values():   # topics with no section in the textbook are parked, whatever the old papers say
        if subject["book"](s["id"])["status"]=="absent" and s["category"]!="new":
            s["was_category"]=s["category"]; s["category"]="park"
            s["reason"]="Not found in the new 2023 textbook. Likely removed by the syllabus change, so old-paper frequency may not carry over."
    key = lambda s:(s["category"]=="new", -s["expected_marks"]/s["hours_needed"])
    top = sorted(stats.values(), key=key)
    topics = []
    for s in top:
        b = subject["book"](s["id"]); d = {k:round(v,3) if isinstance(v,float) else v for k,v in s.items() if k!="neff"}
        d["book"]=b; d["study_hint"]=hint(b); topics.append(d)
    res = dict(subject=subject["title"], subject_id=subject["id"], papers=len(papers), years=sorted({p["year"] for p in papers}),
        sources=sorted({p.get("source","scan") for p in papers}), extraction=extraction,
        backtest=backtest(papers, max(p["year"] for p in papers), subject), topics=topics)
    res["chapters"] = chapter_rollup(topics, subject["units"])
    if save_to:
        os.makedirs(os.path.dirname(save_to), exist_ok=True); json.dump(res, open(save_to,"w",encoding="utf-8"), indent=1, ensure_ascii=False)
    return res

if __name__ == "__main__":
    for sid, sub in S.SUBJECTS.items():
        if not os.path.exists(sub["papers_path"]): print("skip", sid, "(no papers.json)"); continue
        r = build(sub, save_to=sub["results_path"]); c = {}
        for t in r["topics"]: c[t["category"]] = c.get(t["category"],0)+1
        print(sid, c)
        if r["backtest"]: print(json.dumps(r["backtest"]["results"]))
