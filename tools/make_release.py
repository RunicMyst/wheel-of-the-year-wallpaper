#!/usr/bin/env python3
"""Maintainer tool: assemble the ready-to-run folders in releases/ from this workshop.

    python3 tools/make_release.py linux   [--with-my-photos]
    python3 tools/make_release.py windows [--with-my-photos]   (also writes a .zip to send)
    python3 tools/make_release.py all

Re-running updates the program (app/), scripts and READMEs of an existing release but never
touches its pictures (backgrounds/, wedges/, center/) or its config.toml - so bug fixes can be
rolled out to a copy that is already in use.
"""
import argparse
import json
import re
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "tools" / "release_files"
OUT = ROOT / "releases"
DOWNLOADS = ROOT / "build" / "cache" / "downloads"
NAMES = {"linux": "Wheel of the Year - Linux", "windows": "Wheel of the Year - Windows 10-11"}
SABBATS = ["Samhain", "Yule", "Imbolc", "Ostara", "Beltane", "Litha", "Lughnasadh", "Mabon"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]
# every module the wallpaper needs at run time (checked below, so a new one can't be forgotten)
RUNTIME = ["__init__.py", "__main__.py", "astro.py", "calendar.py", "compose.py", "config.py",
           "desktop.py", "folders.py", "location.py", "wheel.py"]
SLOTS = ["Samhain-Yule", "Yule-Imbolc", "Ostara-Beltane", "Litha-Lughnasadh"]
PY_SERIES = "3.13"
PICS = {".jpg", ".jpeg", ".png", ".webp"}


def version():
    text = (ROOT / "wheel_of_year" / "__init__.py").read_text()
    return re.search(r'__version__ = "([^"]+)"', text).group(1)


def stamp(text):
    return text.replace("@VERSION@", version())


def write(path, text, windows=False):
    text = stamp(text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n" if windows else "\n").encode("utf-8"))


def check_runtime():
    """Fail loudly if a module was added to wheel_of_year/ but not to RUNTIME."""
    have = {f.name for f in (ROOT / "wheel_of_year").glob("*.py")}
    missing = have - set(RUNTIME)
    if missing:
        raise SystemExit(f"tools/make_release.py: add these to RUNTIME first: {', '.join(sorted(missing))}")


def copy_app(dest):
    check_runtime()
    app = dest / "app"
    if (app / "wheel_of_year").exists():
        shutil.rmtree(app / "wheel_of_year")
    if (app / "assets").exists():
        shutil.rmtree(app / "assets")
    (app / "wheel_of_year").mkdir(parents=True)
    for f in RUNTIME:
        shutil.copy2(ROOT / "wheel_of_year" / f, app / "wheel_of_year" / f)
    shutil.copytree(ROOT / "assets", app / "assets")
    shutil.copy2(ROOT / "wheel-of-the-year.py", app / "wheel-of-the-year.py")


def user_folders(dest, windows, with_photos):
    readme = "README.txt" if windows else "README.md"
    for name, sub in (("backgrounds", SABBATS), ("wedges", [f"{i:02d}-{m}" for i, m in enumerate(MONTHS, 1)]),
                      ("sabbat-ring", SLOTS), ("center", [])):
        base = dest / name
        write(base / readme, (FILES / "common" / f"{name}_README.md").read_text(encoding="utf-8"), windows)
        for s in sub:
            (base / s).mkdir(parents=True, exist_ok=True)
        base.mkdir(parents=True, exist_ok=True)
    if with_photos:  # only into Sabbat folders that are still empty - never overwrite
        for s in SABBATS:
            target = dest / "backgrounds" / s
            if any(p.suffix.lower() in PICS for p in target.iterdir()):
                continue
            for p in (ROOT / "backgrounds" / s).glob("*"):
                if p.is_file() and p.suffix.lower() in PICS:
                    shutil.copy2(p, target / p.name)
    write(dest / "config.default.toml", (FILES / "common" / "config.toml").read_text(encoding="utf-8"), windows)
    shutil.copy2(ROOT / "docs" / "examples" / "example-plain-wedges.jpg", dest / "example.jpg")
    # what changed between versions, in the release so people can see before installing
    changes = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    write(dest / ("Whats New.txt" if windows else "CHANGELOG.md"), changes, windows)


def download(url, name):
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    f = DOWNLOADS / name
    if not f.exists():
        print("downloading", url)
        req = urllib.request.Request(url, headers={"User-Agent": "wheel-of-the-year-release/1.0"})
        f.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return f


def windows_python(app):
    """Embeddable CPython for Windows x64 + Pillow, unpacked into app/python."""
    listing = urllib.request.urlopen("https://www.python.org/ftp/python/", timeout=60).read().decode()
    versions = sorted({tuple(map(int, v.split("."))) for v in re.findall(rf'href="({re.escape(PY_SERIES)}\.\d+)/"', listing)},
                      reverse=True)
    for v in versions:
        ver = ".".join(map(str, v))
        try:
            embed = download(f"https://www.python.org/ftp/python/{ver}/python-{ver}-embed-amd64.zip",
                             f"python-{ver}-embed-amd64.zip")
            break
        except Exception:
            continue
    tag = "cp" + PY_SERIES.replace(".", "")
    meta = json.loads(urllib.request.urlopen("https://pypi.org/pypi/pillow/json", timeout=60).read())
    wheel = next(u for u in meta["urls"] if u["filename"].endswith(f"{tag}-{tag}-win_amd64.whl"))
    whl = download(wheel["url"], wheel["filename"])

    py = app / "python"
    if py.exists():
        shutil.rmtree(py)
    zipfile.ZipFile(embed).extractall(py)
    site = py / "Lib" / "site-packages"
    zipfile.ZipFile(whl).extractall(site)
    pth = next(py.glob("python*._pth"))
    pth.write_text(pth.read_text().rstrip() + "\nLib\\site-packages\n")
    print(f"bundled Python {ver} + {wheel['filename']}")


def make_zip(kind, dest):
    """Zip a release for sending. Never includes pictures: they may be someone else's
    copyright, and a local copy may hold the maintainer's own photos."""
    for old in OUT.glob(f"{NAMES[kind]}*.zip"):
        old.unlink()
    zip_path = OUT / f"{NAMES[kind]} v{version()}.zip"
    skipped = []
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(dest.rglob("*")):
            rel = p.relative_to(dest)
            if rel.parts[0] == "build" or rel.name == "config.toml":
                continue  # test logs/pictures, and the local copy's own settings
            if p.is_file() and p.suffix.lower() in PICS and rel.parts[0] != "app" and rel.name != "example.jpg":
                skipped.append(str(rel))
                continue
            z.write(p, Path(NAMES[kind]) / rel)
    if skipped:
        print(f"  left {len(skipped)} picture(s) out of the zip: {', '.join(skipped[:3])}"
              + (" ..." if len(skipped) > 3 else ""))
    print(f"zip: {zip_path.relative_to(ROOT)}  ({zip_path.stat().st_size / 1e6:.1f} MB)")


def make(kind, with_photos):
    dest = OUT / NAMES[kind]
    dest.mkdir(parents=True, exist_ok=True)
    copy_app(dest)
    windows = kind == "windows"
    user_folders(dest, windows, with_photos)
    if windows:
        for f in ("install.ps1", "uninstall.ps1"):
            write(dest / "app" / f, (FILES / "windows" / "app" / f).read_text(encoding="utf-8"), True)
        write(dest / "README.txt", (FILES / "windows" / "README.txt").read_text(encoding="utf-8"), True)
        ps = 'powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0app\\{}"'
        write(dest / "Install.cmd", "@echo off\n" + ps.format("install.ps1") + "\npause\n", True)
        write(dest / "Uninstall.cmd", "@echo off\n" + ps.format("uninstall.ps1") + "\npause\n", True)
        write(dest / "Update Wallpaper Now.cmd",
              '@echo off\necho Drawing today\'s wallpaper...\n"%~dp0app\\python\\python.exe" "%~dp0app\\wheel-of-the-year.py" %*\npause\n', True)
        if not (dest / "app" / "python" / "python.exe").exists() or "--fresh-python" in sys.argv:
            windows_python(dest / "app")
        for old in OUT.glob(f"{NAMES[kind]}*.zip"):
            old.unlink()
        make_zip(kind, dest)
    else:
        for f in ("install.sh", "update-now.sh"):
            write(dest / f, (FILES / "linux" / f).read_text(encoding="utf-8"))
            (dest / f).chmod(0o755)
        write(dest / "README.md", (FILES / "linux" / "README.md").read_text(encoding="utf-8"))
        make_zip(kind, dest)
    print(f"ready: {dest.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["linux", "windows", "all"])
    ap.add_argument("--with-my-photos", action="store_true",
                    help="copy the workshop's background photos into empty Sabbat folders of the release")
    ap.add_argument("--fresh-python", action="store_true", help="re-download the bundled Windows Python")
    a = ap.parse_args()
    for kind in (["linux", "windows"] if a.kind == "all" else [a.kind]):
        make(kind, a.with_my_photos)


if __name__ == "__main__":
    main()
