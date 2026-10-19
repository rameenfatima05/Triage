"""Subject registry. Class 9 Math is built in. Any other subject/class = one folder: subjects/<id>/subject.json (+ papers.json).
See subjects/_template/subject.json."""
import json, os
from taxonomy import TOPICS as T9
from taxonomy_new import NEW_TOPICS
from book_map import book_for as book9, UNITS as U9
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
SLOT_HELP = ("slot: o=objective MCQ, s=short part (each 2 marks), l=long part (each 4 marks), p=compulsory theorem question (8 marks).\n"
             'For slot s use q="2","3" or "4"; for l use q like "5a".')
ABSENT = dict(unit=None,unit_name=None,section=None,exercise=None,page=None,status="absent",verify=False)
UNKNOWN = dict(ABSENT, status="unknown")

def _class9():
    return dict(id="class9_math", title="Mathematics, Class 9 (Science, Rawalpindi)", paper_desc="Punjab Board Class 9 Mathematics paper (English + Urdu)",
        topics={**T9, **NEW_TOPICS}, new_ids=set(NEW_TOPICS), units=U9, book=book9,
        marks={"o":1,"s":2,"l":4,"p":8}, choice={"o":1,"s":6/9,"l":4/8,"p":1}, caps={"s":6,"l":4}, exam_total=75,
        expected_counts={"o":15,"s":27,"l":8,"p":1}, slot_help=SLOT_HELP,
        papers_path=os.path.join(DATA,"papers.json"), results_path=os.path.join(DATA,"results.json"), editable_book=True)

def _from_json(folder):
    j = json.load(open(os.path.join(folder,"subject.json"), encoding="utf-8"))
    sid = os.path.basename(folder)
    topics = {k:tuple(v) for k,v in j["topics"].items()}; new = {k:tuple(v) for k,v in j.get("new_topics",{}).items()}
    units = {int(k):tuple(v) for k,v in j.get("units",{}).items()}; bk = j.get("book")
    def book_for(tid):
        if bk is None: return dict(UNKNOWN)
        b = bk.get(tid)
        if not b: return dict(ABSENT)
        u = b.get("unit"); return dict(unit=u, unit_name=units.get(u,("",0))[0] if u else None, section=b.get("section"),
            exercise=b.get("exercise"), page=b.get("page"), status=b.get("status","found"), verify=b.get("verify",False))
    marks = j.get("marks",{"o":1,"s":2,"l":4,"p":8})
    return dict(id=sid, title=j["title"], paper_desc=j.get("paper_desc", j["title"]+" past paper"), topics={**topics,**new}, new_ids=set(new),
        units=units, book=book_for, marks=marks, choice=j.get("choice",{k:1 for k in marks}), caps=j.get("caps",{}), exam_total=j.get("exam_total",75),
        expected_counts=j.get("expected_counts",{}), slot_help=j.get("slot_help",SLOT_HELP),
        papers_path=os.path.join(folder,"papers.json"), results_path=os.path.join(DATA,f"results_{sid}.json"), editable_book=False)

def load_all(extra_dir=None):
    reg = {"class9_math": _class9()}
    root = extra_dir or os.path.join(BASE,"subjects")
    if os.path.isdir(root):
        for d in sorted(os.listdir(root)):
            f = os.path.join(root,d)
            if d.startswith("_") or not os.path.exists(os.path.join(f,"subject.json")): continue
            reg[d] = _from_json(f)
    return reg
SUBJECTS = load_all()
def get(sid):
    if sid not in SUBJECTS: raise KeyError(sid)
    return SUBJECTS[sid]
