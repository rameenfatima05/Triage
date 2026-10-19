"""Recency-weighted appearance model with uncertainty, classifier, knapsack planner, and backtest. Subject-agnostic: pass a subject cfg."""
import math, random
LAM = 0.25                                # recency decay per year
Z = 1.28                                  # 80% interval

def fit(papers, cfg, lam=LAM):
    TOPICS, CHOICE = cfg["topics"], cfg["choice"]
    ymax = max(p["year"] for p in papers)
    W = [math.exp(-lam*(ymax-p["year"])) for p in papers]
    order = sorted(range(len(papers)), key=lambda i:(papers[i]["year"],papers[i]["group"]))
    recent = set(order[-3:])
    sw = sum(W); neff = sw**2/sum(w*w for w in W)
    out = {}
    for t,(name,ch,hrs) in TOPICS.items():
        a, m = [], []
        for p in papers:
            its = [i for i in p["items"] if i["topic"]==t]
            a.append(1 if its else 0); m.append(sum(i["marks"]*CHOICE.get(i["slot"],1) for i in its))
        prob = (sum(w*x for w,x in zip(W,a))+1)/(sw+2)
        half = Z*math.sqrt(prob*(1-prob)/(neff+2))
        mm = [x for x in m if x>0]; avg = sum(mm)/len(mm) if mm else 0
        years = sorted({papers[i]["year"] for i in range(len(papers)) if a[i]})
        out[t] = dict(id=t,name=name,chapter=ch,hours_needed=hrs,p=prob,ci=[max(0,prob-half),min(1,prob+half)],
            appearances=sum(a),papers=len(papers),avg_marks=avg,expected_marks=prob*avg,last_seen=years[-1] if years else None,
            drift=sum(a)>=2 and not any(a[i] for i in recent),neff=neff,is_new=t in cfg["new_ids"])
    return out

def classify(stats):
    dens = sorted(s["expected_marks"]/s["hours_needed"] for s in stats.values() if s["appearances"])
    med = dens[len(dens)//2] if dens else 0
    for s in stats.values():
        d = s["expected_marks"]/s["hours_needed"]; n,N = s["appearances"],s["papers"]
        if s.get("is_new") and n==0:
            s["category"]="new"; s["confidence"]=None; s["expected_marks"]=0.0; s["note"]="no past papers"
            s["reason"]="New in the 2023 syllabus, so no past paper covers it yet. We can't predict it; it is included for breadth until a paper shows how it is examined."
            continue
        if s["drift"]:
            s["category"]="park"; s["reason"]=f"Last seen {s['last_seen']} and missing from your newest papers. May have left the syllabus."
        elif s["p"]>=0.6 and d>=0.6*med and s["hours_needed"]<=2.5:
            s["category"]="lock"; s["reason"]=f"In {n} of {N} papers (last {s['last_seen']}), about {s['avg_marks']:.1f} marks each time for {s['hours_needed']}h of study."
        elif s["p"]>=0.45:
            s["category"]="care"; s["reason"]=f"Common ({n} of {N} papers) but costly: {s['hours_needed']}h for about {s['avg_marks']:.1f} marks. Do it after your Lock It In topics."
        else:
            s["category"]="park"; s["reason"]=("Seen only once so far." if n<=1 else f"Seen in {n} of {N} papers, low return for the time.") if n else "Never appeared in your papers."
        s["confidence"]=round(s["p"]*100); s["note"]="small sample" if s["neff"]<4 else ""
    return stats

def plan(topics, hours, break_ratio=1/6, include_new=True, new_share=0.3):
    """Knapsack over predicted topics. 'new' topics (no history) get a reserved share of hours, spread across chapters (breadth first)."""
    news = [t for t in topics if t["category"]=="new"] if include_new else []
    usable = hours*(1-break_ratio); budget = usable*new_share if news else 0.0
    by_ch = {}
    for t in sorted(news, key=lambda t:t["hours_needed"]): by_ch.setdefault(t["chapter"],[]).append(t)
    new_pick, left, moved = [], budget, True
    while moved:
        moved = False
        for ch in by_ch:
            if by_ch[ch] and by_ch[ch][0]["hours_needed"]<=left+1e-9:
                t = by_ch[ch].pop(0); new_pick.append(t); left -= t["hours_needed"]; moved = True
    cap = int((usable - sum(t["hours_needed"] for t in new_pick))*4)
    items = [t for t in topics if t["category"] in ("lock","care")]
    val = lambda t: t["expected_marks"]*(1 if t["category"]=="lock" else 0.7)
    wt = lambda t: max(1,round(t["hours_needed"]*4))
    dp = [[0.0]*(cap+1) for _ in range(len(items)+1)]
    for i,t in enumerate(items,1):
        for c in range(cap+1):
            dp[i][c] = dp[i-1][c]
            if wt(t)<=c: dp[i][c] = max(dp[i][c], dp[i-1][c-wt(t)]+val(t))
    c, pick = cap, []
    for i in range(len(items),0,-1):
        if dp[i][c]!=dp[i-1][c]: pick.append(items[i-1]); c -= wt(items[i-1])
    pick.sort(key=lambda t:-t["expected_marks"]/t["hours_needed"])
    ids = {t["id"] for t in pick} | {t["id"] for t in new_pick}
    mk = lambda t: dict(id=t["id"],name=t["name"],category=t["category"],minutes=round(t["hours_needed"]*60),reason=t["reason"],study_hint=t.get("study_hint",""),book=t.get("book"))
    def why(t):
        if t["category"]=="park": return t["reason"]
        if t["category"]=="new": return "Not reached in your new-syllabus share of hours at this budget."
        return "No time left at this budget."
    return dict(hours=hours,break_minutes=round(hours*60*break_ratio),
        study=[mk(t) for t in pick]+[mk(t) for t in new_pick],
        parked=[dict(id=t["id"],name=t["name"],why=why(t),study_hint=t.get("study_hint","")) for t in topics if t["id"] not in ids],
        expected_marks=round(sum(t["expected_marks"] for t in pick),1),
        new_syllabus_minutes=round(sum(t["hours_needed"] for t in new_pick)*60),
        note=("New-syllabus topics are included for breadth only; they are not predictions." if new_pick else ""))

def covered_marks(paper, studied, cfg):
    M, caps = cfg["marks"], cfg["caps"]; tot, groups = 0, {}
    for i in paper["items"]:
        if i["topic"] not in studied: continue
        s = i["slot"]
        if s not in caps: tot += M.get(s,0)
        else: groups.setdefault((s,i["q"] if s=="s" else "L"),[]).append(i)
    for (s,_),v in groups.items(): tot += min(caps[s],len(v))*M[s]
    return tot

def backtest(papers, test_year, cfg, hours=(6,10,15), trials=300):
    train = [p for p in papers if p["year"]<test_year]; test = [p for p in papers if p["year"]==test_year]
    if not train or not test: return None
    topics = [t for t in classify(fit(train,cfg)).values() if t["category"]!="new"]; rng = random.Random(0)
    freq = sorted(topics,key=lambda t:-t["appearances"]); res = []
    def fill(order,h):
        left, s = h*(5/6), set()
        for t in order:
            if t["hours_needed"]<=left: s.add(t["id"]); left -= t["hours_needed"]
        return s
    avg = lambda S: sum(covered_marks(p,S,cfg) for p in test)/len(test)
    for h in hours:
        ours = {x["id"] for x in plan(topics,h,include_new=False)["study"]}
        rnd = sum(avg(fill(rng.sample(topics,len(topics)),h)) for _ in range(trials))/trials
        res.append(dict(hours=h,ours=round(avg(ours),1),frequency_only=round(avg(fill(freq,h)),1),random=round(rnd,1),out_of=cfg["exam_total"]))
    return dict(trained_on=sorted({p["year"] for p in train}),tested_on=test_year,results=res,
        assumption="Studying a topic earns all its marks; capped where the exam lets students skip parts. Measures the OLD syllabus exam, not the new book.")
