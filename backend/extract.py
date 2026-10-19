"""Scan -> structured questions with a vision model: Claude (ANTHROPIC_API_KEY) or Grok (XAI_API_KEY). TRIAGE_MOCK_EXTRACT=1 = labelled demo stand-in.
Heavy imports are lazy so the rest of the backend runs without them."""
import base64, copy, io, json, os, re
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4")          # check the exact vision-capable model name in your xAI console
XAI_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1") + "/chat/completions"
MAX_SIDE = 1800
PROMPT = """These are pages of one {desc}, scanned (may have watermarks).
List EVERY question part. Return ONLY a JSON array, no prose, no markdown. Each item:
{{"slot":"o|s|l|p","q":"question number","text":"English text, max 15 words","topic":"<topic id>"}}
{slot_help}
topic MUST be one of these ids, or "other" if none fits:
{ids}"""
class ExtractError(Exception): pass

def provider():
    """TRIAGE_PROVIDER=anthropic|xai wins; otherwise whichever key is set (Anthropic first)."""
    p = os.getenv("TRIAGE_PROVIDER", "").lower()
    if p in ("anthropic", "xai"): return p
    if os.getenv("ANTHROPIC_API_KEY"): return "anthropic"
    if os.getenv("XAI_API_KEY"): return "xai"
    return None

def _post_json(url, payload, key, timeout=120):
    import urllib.request, urllib.error
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type":"application/json","Authorization":f"Bearer {key}","User-Agent":"triage-backend/3"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise ExtractError(f"Grok API error {e.code}: {e.read().decode(errors='ignore')[:200]}") from e
    except Exception as e: raise ExtractError(f"Could not reach the Grok API: {e}") from e

def _ask_grok(images, prompt):
    content = [{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+base64.b64encode(b).decode(),"detail":"high"}} for b in images]
    content.append({"type":"text","text":prompt})
    out = _post_json(XAI_URL, {"model":GROK_MODEL,"temperature":0,"max_tokens":8000,"messages":[{"role":"user","content":content}]}, os.environ["XAI_API_KEY"])
    try: return out["choices"][0]["message"]["content"]
    except Exception as e: raise ExtractError("Unexpected reply from the Grok API.") from e

def _ask_claude(images, prompt):
    from anthropic import Anthropic
    content = [{"type":"image","source":{"type":"base64","media_type":"image/jpeg","data":base64.b64encode(b).decode()}} for b in images]
    content.append({"type":"text","text":prompt})
    return Anthropic().messages.create(model=MODEL, max_tokens=8000, messages=[{"role":"user","content":content}]).content[0].text

def _jpeg(img):
    from PIL import Image
    img = img.convert("RGB"); img.thumbnail((MAX_SIDE, MAX_SIDE))
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=85); return buf.getvalue()
def _images(path):
    if path.lower().endswith(".pdf"):
        import fitz
        from PIL import Image
        for pg in fitz.open(path):
            zoom = min(2.5, MAX_SIDE/max(pg.rect.width, pg.rect.height))
            pm = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            yield _jpeg(Image.open(io.BytesIO(pm.tobytes("png"))))
    else:
        from PIL import Image
        try: yield _jpeg(Image.open(path))
        except Exception as e: raise ExtractError(f"Could not open {os.path.basename(path)} as an image or PDF.") from e

def parse_items(text):
    """Tolerant JSON-array parser: strips fences/prose around the array."""
    a, b = text.find("["), text.rfind("]")
    if a < 0 or b <= a: raise ValueError("no JSON array")
    data = json.loads(text[a:b+1])
    if not isinstance(data, list): raise ValueError("not a list")
    return [d for d in data if isinstance(d, dict)]

def clean(raw_items, cfg):
    items, review = [], []
    for it in raw_items:
        if it.get("slot") not in cfg["marks"]: continue
        it = dict(it); it["marks"] = cfg["marks"][it["slot"]]
        if it.get("topic") not in cfg["topics"]: review.append(dict(it)); it["topic"] = "other"
        items.append(it)
    return items, review

def quality(items, cfg):
    got = {}
    for i in items: got[i["slot"]] = got.get(i["slot"], 0) + 1
    warn = [f"Found {got.get(s,0)} of about {n} '{s}' questions - a page may be missing or unreadable."
            for s, n in cfg.get("expected_counts", {}).items() if got.get(s, 0) < 0.7*n]
    return dict(counts=got, warnings=warn)

def extract(paths, year, group, cfg):
    if os.getenv("TRIAGE_MOCK_EXTRACT") == "1": return mock_extract(year, group, cfg)
    prov = provider()
    if prov is None: raise ExtractError("Set ANTHROPIC_API_KEY or XAI_API_KEY (Grok) to read new papers.")
    if prov == "xai" and not os.getenv("XAI_API_KEY"): raise ExtractError("TRIAGE_PROVIDER=xai but XAI_API_KEY is not set.")
    if prov == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"): raise ExtractError("TRIAGE_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set.")
    images = [b for p in ([paths] if isinstance(paths, str) else paths) for b in _images(p)]
    if not images: raise ExtractError("No readable pages in the upload.")
    ids = "\n".join(f"{k}: {v[0]}" for k, v in cfg["topics"].items())
    prompt = PROMPT.format(desc=cfg["paper_desc"], slot_help=cfg["slot_help"], ids=ids)
    ask, last = (_ask_grok if prov == "xai" else _ask_claude), None
    for attempt in range(2):
        try: raw = parse_items(ask(images, prompt)); break
        except ExtractError: raise
        except Exception as e: last = e
    else: raise ExtractError(f"The model's answer could not be parsed ({last}). Try clearer photos.")
    items, review = clean(raw, cfg)
    if len(items) < 10: raise ExtractError("Could not read enough questions from this upload. Try clearer, full-page photos.")
    return dict(year=year, group=group, items=items, needs_review=review, source=f"{prov}_vision", quality=quality(items, cfg))

def mock_extract(year, group, cfg):
    """Demo stand-in (TRIAGE_MOCK_EXTRACT=1): returns a copy of an already-labelled paper. It does NOT read the upload."""
    base = json.load(open(cfg["papers_path"], encoding="utf-8")); src = max(base, key=lambda p:(p["year"], p["group"]))
    return dict(year=year, group=group, items=copy.deepcopy(src["items"]), needs_review=[], source="demo_mock",
                quality=dict(counts={}, warnings=["DEMO MODE: this paper was not actually read; labels were copied from a stored paper."]))
