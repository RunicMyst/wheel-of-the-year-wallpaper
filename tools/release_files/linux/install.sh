#!/usr/bin/env bash
# Wheel of the Year wallpaper - install or remove the daily refresh (Linux).
#   ./install.sh            install, and set today's wallpaper right away
#   ./install.sh --remove   stop the daily refresh
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
NAME=wheel-of-the-year
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
SHORTCUTS="$DESKTOP_DIR/Wheel of the Year"      # one folder on the desktop holding all three

if [[ "${1:-}" == "--remove" ]]; then
    systemctl --user disable --now "$NAME.timer" 2>/dev/null || true
    rm -f "$UNIT_DIR/$NAME.service" "$UNIT_DIR/$NAME.timer" "$DIR/Settings.desktop" "$DIR/Update Now.desktop" "$DIR/Pictures.desktop"
    # Only the links we made, by name - anything of the user's own in there is left alone, and
    # the folder itself only goes if that leaves it empty.
    rm -f "$SHORTCUTS/Settings.desktop" "$SHORTCUTS/Update Wallpaper Now.desktop" \
          "$SHORTCUTS/Settings.toml" "$SHORTCUTS/Pictures.desktop" "$SHORTCUTS/Program folder" 2>/dev/null
    rm -f "$SHORTCUTS/Pictures/Backgrounds" "$SHORTCUTS/Pictures/Wedges" \
          "$SHORTCUTS/Pictures/Sabbat ring" "$SHORTCUTS/Pictures/Ring symbols" \
          "$SHORTCUTS/Pictures/Centre" 2>/dev/null
    rm -f "$SHORTCUTS/Pictures" 2>/dev/null          # a plain symlink in 1.0.0 and earlier
    rmdir "$SHORTCUTS/Pictures" "$SHORTCUTS" 2>/dev/null || true
    rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/applications/wheel-of-the-year-"*.desktop
    rm -f "$DESKTOP_DIR/Wheel of the Year Settings.desktop" "$DESKTOP_DIR/Wheel of the Year Update Now.desktop" \
          "$DESKTOP_DIR/Wheel of the Year Pictures.desktop"   # loose icons from older versions
    systemctl --user daemon-reload
    echo "Removed. Your current wallpaper stays until you change it."
    exit 0
fi

python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' \
    || { echo "Needs Python 3.11 or newer."; exit 1; }
python3 -c "import PIL" 2>/dev/null || {
    echo "Needs Pillow. Install it with one of:"
    echo "  Debian/Ubuntu/Kubuntu/Mint:  sudo apt install python3-pil"
    echo "  Fedora:                      sudo dnf install python3-pillow"
    echo "  Arch/Manjaro:                sudo pacman -S python-pillow"
    exit 1; }

# What the Pictures launcher opens: the four-folder view in the desktop folder when there is a
# desktop, otherwise the install folder itself.
PICS_VIEW="$DIR"
[[ -d "$DESKTOP_DIR" ]] && PICS_VIEW="$SHORTCUTS/Pictures"

# First install: start from the default settings. Later updates keep the ones you have.
[[ -f "$DIR/config.toml" ]] || cp "$DIR/config.default.toml" "$DIR/config.toml"

mkdir -p "$UNIT_DIR"
cat > "$UNIT_DIR/$NAME.service" <<UNIT
[Unit]
Description=Wheel of the Year wallpaper
After=graphical-session.target

[Service]
Type=oneshot
ExecStart=/usr/bin/env python3 "$DIR/app/wheel-of-the-year.py"
UNIT
cat > "$UNIT_DIR/$NAME.timer" <<UNIT
[Unit]
Description=Refresh the Wheel of the Year wallpaper daily

[Timer]
OnCalendar=*-*-* 00:01:00
OnStartupSec=90
Persistent=true

[Install]
WantedBy=timers.target
UNIT
# A Settings launcher with a gear icon, so nobody has to know what opens a .toml file.
cat > "$DIR/Settings.desktop" <<LAUNCH
[Desktop Entry]
Type=Application
Name=Settings (Wheel of the Year)
Comment=Open config.toml to change how the wallpaper looks
Exec=xdg-open "$DIR/config.toml"
Icon=$DIR/app/assets/icons/settings.png
Terminal=false
Categories=Settings;
LAUNCH
chmod +x "$DIR/Settings.desktop"

# Update now: redraw the wallpaper straight away after adding pictures or changing settings.
cat > "$DIR/Update Now.desktop" <<LAUNCH
[Desktop Entry]
Type=Application
Name=Update Wallpaper Now (Wheel of the Year)
Comment=Redraw today's wallpaper with your latest pictures and settings
Exec="$DIR/update-now.sh"
Icon=$DIR/app/assets/icons/update.png
Terminal=false
Categories=Utility;
LAUNCH
chmod +x "$DIR/Update Now.desktop"

# Straight to the pictures: the folders are easy to confuse with any other copy.
cat > "$DIR/Pictures.desktop" <<LAUNCH
[Desktop Entry]
Type=Application
Name=Wheel of the Year Pictures
Comment=Open the folders the wallpaper actually reads
Exec=xdg-open "$PICS_VIEW"
Icon=folder-pictures
Terminal=false
Categories=Utility;
LAUNCH
chmod +x "$DIR/Pictures.desktop"

# The application menu first, because the desktop folder links to these copies.
#
# A .desktop file only counts as a launcher where the desktop environment trusts it, and on KDE
# that means one of the applications directories - a copy sitting in a folder of our own is shown
# as a plain file called "...desktop" and asks what to do with it when opened. A symbolic link to
# the trusted copy launches straight away, so that is what goes in the desktop folder below.
# (The old "gio set metadata::trusted" is a GNOME convention; KDE answers "not supported".)
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$APPS"
sed 's/^Name=.*/Name=Wheel of the Year Settings/' "$DIR/Settings.desktop" > "$APPS/wheel-of-the-year-settings.desktop"
sed 's/^Name=.*/Name=Wheel of the Year Update Now/' "$DIR/Update Now.desktop" > "$APPS/wheel-of-the-year-update.desktop"
sed 's/^Name=.*/Name=Wheel of the Year Pictures/' "$DIR/Pictures.desktop" > "$APPS/wheel-of-the-year-pictures.desktop"
chmod +x "$APPS"/wheel-of-the-year-*.desktop
update-desktop-database "$APPS" 2>/dev/null || true

# Everything in one folder on the desktop, so it is all in the same place.
if [[ -d "$DESKTOP_DIR" ]]; then
    mkdir -p "$SHORTCUTS/Pictures"
    rm -f "$SHORTCUTS/Settings.desktop" "$SHORTCUTS/Pictures.desktop" \
          "$SHORTCUTS/Update Wallpaper Now.desktop" "$SHORTCUTS/Settings.toml"   # older versions
    [[ -L "$SHORTCUTS/Pictures" ]] && rm -f "$SHORTCUTS/Pictures" && mkdir -p "$SHORTCUTS/Pictures"

    # All four picture folders, not just the backgrounds. The ring symbols matter more than they
    # look: with festival_only they are what lights between one Sabbat and the next.
    rm -f "$SHORTCUTS/Pictures/Ring symbols"    # called that briefly in 1.0.1
    ln -sfn "$DIR/backgrounds"  "$SHORTCUTS/Pictures/Backgrounds"
    ln -sfn "$DIR/wedges"       "$SHORTCUTS/Pictures/Wedges"
    ln -sfn "$DIR/sabbat-ring"  "$SHORTCUTS/Pictures/Sabbat ring"
    ln -sfn "$DIR/center"       "$SHORTCUTS/Pictures/Centre"

    # Straight to the install folder too: the README, the CHANGELOG, build/log.txt (the file to
    # send if something goes wrong) and install.sh all live there, and it is easily lost track of.
    ln -sfn "$DIR" "$SHORTCUTS/Program folder"

    ln -sfn "$APPS/wheel-of-the-year-settings.desktop" "$SHORTCUTS/Settings.desktop"
    ln -sfn "$APPS/wheel-of-the-year-update.desktop"   "$SHORTCUTS/Update Wallpaper Now.desktop"

    # tidy away the loose icons older versions put straight on the desktop
    rm -f "$DESKTOP_DIR/Wheel of the Year Settings.desktop" "$DESKTOP_DIR/Wheel of the Year Update Now.desktop" \
          "$DESKTOP_DIR/Wheel of the Year Pictures.desktop"
fi

systemctl --user daemon-reload
systemctl --user enable --now "$NAME.timer"
systemctl --user start "$NAME.service" || true
tail -n 3 "$DIR/build/log.txt" 2>/dev/null || true
echo
echo "Wheel of the Year @VERSION@"
echo "Installed. The wallpaper refreshes every night at 00:01 and shortly after you log in."
echo "If you move this folder, run ./install.sh again."
echo "On your desktop there is now a \"Wheel of the Year\" folder holding:"
echo "  Pictures          - Backgrounds, Wedges, Sabbat ring and Centre"
echo "  Settings          - change how it looks"
echo "  Program folder    - the install itself: README, log, install.sh"
echo "  Update Wallpaper Now - redraw it straight away"
echo "They are in the application menu too: search for \"Wheel of the Year\"."
