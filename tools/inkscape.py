"""Run Inkscape (native or Flatpak) for bounding-box queries and PNG export."""
import shutil
import subprocess


def command():
    if shutil.which("inkscape"):
        return ["inkscape"]
    if shutil.which("flatpak"):
        r = subprocess.run(["flatpak", "info", "org.inkscape.Inkscape"], capture_output=True)
        if r.returncode == 0:
            return ["flatpak", "run", "org.inkscape.Inkscape"]
    raise SystemExit("Inkscape not found. Install it (e.g. `sudo apt install inkscape` or the Flatpak).")


def query_all(svg):
    """{id: (x, y, w, h)} in document pixels for every element."""
    r = subprocess.run(command() + ["--query-all", str(svg)], capture_output=True, text=True, check=True)
    out = {}
    for line in r.stdout.splitlines():
        parts = line.split(",")
        if len(parts) == 5:
            out[parts[0]] = tuple(map(float, parts[1:]))
    return out


def export_png(svg, png, width):
    # Note: the Flatpak build can't see /tmp, so svg/png should live inside the project folder.
    subprocess.run(command() + [str(svg), "--export-type=png", f"--export-filename={png}",
                                f"--export-width={int(width)}", "--export-background-opacity=0"],
                   capture_output=True, check=True)
