"""Desktop integration: screen size, taskbar space and setting the wallpaper.

The lock screen and the login screen are a separate project ("Linux Sign-In and Lock Screen"),
so this app leaves both of them alone.

Supported: Windows 10/11, KDE Plasma, GNOME (and GNOME-based desktops such as Cinnamon/Budgie
where gsettings works). Anything else still gets the image saved to disk.
"""
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

WINDOWS = sys.platform == "win32"


def display_ready():
    """Is there a desktop session to talk to yet?

    At boot our timer can run before Plasma is up. KDE's own tools abort (and dump core) when
    they can't reach a display, so we check first - and fill in the display variables if the
    socket is there but systemd started us without them.
    """
    if WINDOWS:
        return True
    if os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY"):
        return True
    runtime = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
    for sock in sorted(runtime.glob("wayland-[0-9]*")):
        if not sock.name.endswith(".lock"):
            os.environ["WAYLAND_DISPLAY"] = sock.name
            return True
    return False


def wait_for_display(seconds=120):
    """Give the desktop a chance to finish starting (used when we run at boot)."""
    for _ in range(max(1, seconds // 5)):
        if display_ready():
            return True
        time.sleep(5)
    return display_ready()


def _run(cmd):
    """Run a desktop helper and return its output, quietly tolerating failure."""
    return _run_full(cmd).stdout


def _run_full(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return subprocess.CompletedProcess(cmd, 1, "", "did not run")


def desktop_name():
    if WINDOWS:
        return "windows"
    d = (os.environ.get("XDG_CURRENT_DESKTOP", "") + ":" + os.environ.get("DESKTOP_SESSION", "")).lower()
    if "kde" in d or "plasma" in d or shutil.which("plasma-apply-wallpaperimage"):
        return "kde"
    if shutil.which("gsettings"):
        return "gnome"
    return "other"


# ---------------------------------------------------------------- Windows

def _win():
    import ctypes
    from ctypes import wintypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # report real pixels, not scaled ones
    except (AttributeError, OSError):
        pass
    return ctypes, wintypes


def _win_screen():
    ctypes, _ = _win()
    u = ctypes.windll.user32
    w, h = u.GetSystemMetrics(0), u.GetSystemMetrics(1)
    try:
        scale = u.GetDpiForSystem() / 96
    except AttributeError:
        scale = 1.0
    return w, h, scale


def _win_edges():
    ctypes, wintypes = _win()
    u = ctypes.windll.user32
    work = wintypes.RECT()
    u.SystemParametersInfoW(0x0030, 0, ctypes.byref(work), 0)  # SPI_GETWORKAREA
    w, h = u.GetSystemMetrics(0), u.GetSystemMetrics(1)
    edges = {"left": work.left, "top": work.top, "right": w - work.right, "bottom": h - work.bottom}
    return {k: v for k, v in edges.items() if v > 0}


def _win_set_wallpaper(path):
    import winreg
    ctypes, _ = _win()
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "WallpaperStyle", 0, winreg.REG_SZ, "10")  # Fill
        winreg.SetValueEx(k, "TileWallpaper", 0, winreg.REG_SZ, "0")
    ok = ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, str(path), 0x01 | 0x02)  # SPI_SETDESKWALLPAPER
    return bool(ok)


# ---------------------------------------------------------------- KDE Plasma

def _qdbus():
    return next((q for q in ("qdbus6", "qdbus", "qdbus-qt6") if shutil.which(q)), None)


def _kde_screen():
    out = re.sub(r"\x1b\[[0-9;]*m", "", _run(["kscreen-doctor", "-o"]))
    mode = re.search(r"\d+:(\d+)x(\d+)@[\d.]+\*", out)
    scale = re.search(r"Scale:\s*([\d.]+)", out)
    return (int(mode.group(1)), int(mode.group(2)), float(scale.group(1)) if scale else 1.0) if mode else None


def _kde_edges(scale):
    q = _qdbus()
    if not q:
        return {}
    js = ('var p=panels();var o=[];for(var i=0;i<p.length;i++){'
          'o.push(p[i].location+"|"+p[i].height+"|"+p[i].hiding)}print(o.join("\\n"))')
    edges = {}
    for line in _run([q, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", js]).splitlines():
        parts = line.strip().split("|")
        if len(parts) == 3 and parts[1].isdigit() and parts[2] != "autohide":
            edges[parts[0]] = max(edges.get(parts[0], 0), int(int(parts[1]) * scale + 0.5))
    return edges


# ---------------------------------------------------------------- GNOME

def _gnome_set(schema, path):
    uri = path.as_uri()
    _run(["gsettings", "set", schema, "picture-uri", uri])
    _run(["gsettings", "set", schema, "picture-uri-dark", uri])
    _run(["gsettings", "set", schema, "picture-options", "zoom"])
    return True


# ---------------------------------------------------------------- public

def screen():
    """(width, height, scale) of the main screen in real pixels, or None if unknown."""
    if WINDOWS:
        return _win_screen()
    if not display_ready():
        return None   # no session yet: the caller falls back to the remembered size
    if desktop_name() == "kde":
        return _kde_screen()
    m = re.search(r"current (\d+) x (\d+)", _run(["xrandr", "--current"]))
    return (int(m.group(1)), int(m.group(2)), 1.0) if m else None


def reserved_edges(scale):
    """Screen space taken by taskbars/panels, in real pixels: {"bottom": 68, ...}."""
    if WINDOWS:
        return _win_edges()
    if not display_ready():
        return {}
    if desktop_name() == "kde":
        return _kde_edges(scale)
    if desktop_name() == "gnome":
        return {"top": int(32 * scale)}  # GNOME's top bar
    return {}


def set_wallpaper(path):
    if not display_ready():
        return False
    name = desktop_name()
    if name == "windows":
        return _win_set_wallpaper(path)
    if name == "kde":
        return _run_full(["plasma-apply-wallpaperimage", str(path)]).returncode == 0
    if name == "gnome":
        return _gnome_set("org.gnome.desktop.background", path)
    return False
