# Personal helper: replace thumbnail copies in backgrounds/ with full-size originals (same file names).
# Works for files named by Wallhaven id or c<Wikimedia page id>. Run from the project folder; safe to re-run.
# Thumbnails are backed up to build/work/thumb_backup/ first.
import json, re, shutil, sys, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image
UA = {"User-Agent": "wheel-of-the-year-wallpaper/0.1 (personal use)"}
ROOTS = [Path(d) for d in ("backgrounds", "wedges", "sabbat-ring", "center")]
BK = Path("build/work/thumb_backup")

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()

for f in sorted(f for R in ROOTS if R.is_dir() for f in R.rglob("*")):
    if f.suffix.lower() not in (".jpg", ".png") or f.name.startswith("MY-"): continue
    if Image.open(f).width > 1000: continue
    ident = re.sub(r"^.*__", "", f.stem)
    data = None
    try:
        if ident.startswith("c") and ident[1:].isdigit():
            q = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
                {"action": "query", "format": "json", "pageids": ident[1:], "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 3840})))
            ii = next(iter(q["query"]["pages"].values()))["imageinfo"][0]; url = ii.get("thumburl") or ii["url"]
            time.sleep(8); data = get(url); time.sleep(8)
        else:
            for ext in ("jpg", "png"):
                try:
                    data = get(f"https://w.wallhaven.cc/full/{ident[:2]}/wallhaven-{ident}.{ext}"); break
                except Exception:
                    pass
            time.sleep(1)
    except Exception as e:
        print("FAIL", f, e); continue
    if not data:
        print("FAIL", f, "not found"); continue
    dest = BK / f; dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists(): shutil.copy2(f, dest)
    tmp = f.with_suffix(".part"); tmp.write_bytes(data)
    im = Image.open(tmp); im.load()
    if im.mode not in ("RGB", "L"): im = im.convert("RGB")
    im.save(f, quality=95) if f.suffix.lower() == ".jpg" else im.save(f)
    tmp.unlink()
    print("OK  ", f, im.size)
