"""User picture folders: backgrounds/<Sabbat>, wedges/NN-<Month>, center/.

Every picture in a folder is used, one per day in turn (sorted by file name, so the order is
stable). Empty or missing folders simply mean "use the default".
"""
import re

from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def pictures(folder):
    if not folder.is_dir():
        return []
    return sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTS),
                  key=lambda p: p.name.lower())


def readable(path):
    """True if Pillow can actually read this file (a .jpg that isn't one, a half-copied
    download or a phone HEIC renamed to .jpg would otherwise stop the whole run)."""
    try:
        with Image.open(path) as im:
            im.verify()
        return True
    except Exception:
        return False


def pick(folder, day, fallback=None, notes=None):
    """Today's picture from `folder`, or from `fallback` if that folder is empty.

    Rotates daily, and quietly steps over any file it can't read (noting it for the log).
    """
    pics = pictures(folder) or (pictures(fallback) if fallback else [])
    for i in range(len(pics)):
        choice = pics[(day.toordinal() + i) % len(pics)]
        if readable(choice):
            return choice
        if notes is not None:
            notes.append(f"skipped {choice.name} in {choice.parent.name}: not a picture I can read")
    return None


def wedge_art(root, day, notes=None):
    """{English month: picture} for every wedge folder that has pictures."""
    out = {}
    if root.is_dir():
        for d in sorted(root.iterdir()):
            if not d.is_dir():
                continue
            m = re.fullmatch(r"\d+-(\w+)", d.name)
            if not m:
                if notes is not None and pictures(d):
                    notes.append(f"ignored the folder {d.name}: wedge folders are named like 10-October")
                continue
            if p := pick(d, day, notes=notes):
                out[m.group(1).capitalize()] = p
    return out


def side_override(path):
    """'left'/'right' if the file name ends with _wheel-left / _wheel-right."""
    m = re.search(r"_wheel-(left|right)$", path.stem, re.I)
    return m.group(1).lower() if m else None


SLOTS = ["Samhain-Yule", "Yule-Imbolc", "Ostara-Beltane", "Litha-Lughnasadh"]


def slot_art(root, day, notes=None):
    """{slot name: picture} for the four unnamed Sabbat-ring slots (folders sabbat-ring/<A-B>)."""
    return {s: p for s in SLOTS if (p := pick(root / s, day, notes=notes))}
