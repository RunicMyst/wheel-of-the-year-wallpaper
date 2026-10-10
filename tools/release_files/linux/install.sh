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
    rm -f "$SHORTCUTS"/*.desktop "$SHORTCUTS/Pictures" "$SHORTCUTS/Settings.toml" 2>/dev/null
    rmdir "$SHORTCUTS" 2>/dev/null
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
Exec=xdg-open "$DIR/backgrounds"
Icon=folder-pictures
Terminal=false
Categories=Utility;
LAUNCH
chmod +x "$DIR/Pictures.desktop"

# All three in one folder on the desktop, so everything is in the same place.
#
# Plain links where possible: KDE asks "what do you wish to do with this file?" before running
# a launcher that isn't directly on the desktop, and a link to a folder or a text file opens
# straight away with no questions.
if [[ -d "$DESKTOP_DIR" ]]; then
    mkdir -p "$SHORTCUTS"
    rm -f "$SHORTCUTS/Settings.desktop" "$SHORTCUTS/Pictures.desktop"      # older versions
    ln -sfn "$DIR/backgrounds" "$SHORTCUTS/Pictures"
    ln -sfn "$DIR/config.toml" "$SHORTCUTS/Settings.toml"
    sed 's/^Name=.*/Name=Update Wallpaper Now/' "$DIR/Update Now.desktop" > "$SHORTCUTS/Update Wallpaper Now.desktop"
    chmod +x "$SHORTCUTS/Update Wallpaper Now.desktop"
    gio set "$SHORTCUTS/Update Wallpaper Now.desktop" metadata::trusted true 2>/dev/null || true
    # tidy away the loose icons older versions put straight on the desktop
    rm -f "$DESKTOP_DIR/Wheel of the Year Settings.desktop" "$DESKTOP_DIR/Wheel of the Year Update Now.desktop" \
          "$DESKTOP_DIR/Wheel of the Year Pictures.desktop"
fi

# Also in the application menu, where launching never prompts: search "Wheel of the Year".
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$APPS"
sed 's/^Name=.*/Name=Wheel of the Year Settings/' "$DIR/Settings.desktop" > "$APPS/wheel-of-the-year-settings.desktop"
sed 's/^Name=.*/Name=Wheel of the Year Update Now/' "$DIR/Update Now.desktop" > "$APPS/wheel-of-the-year-update.desktop"
sed 's/^Name=.*/Name=Wheel of the Year Pictures/' "$DIR/Pictures.desktop" > "$APPS/wheel-of-the-year-pictures.desktop"
update-desktop-database "$APPS" 2>/dev/null || true

systemctl --user daemon-reload
systemctl --user enable --now "$NAME.timer"
systemctl --user start "$NAME.service" || true
tail -n 3 "$DIR/build/log.txt" 2>/dev/null || true
echo
echo "Wheel of the Year @VERSION@"
echo "Installed. The wallpaper refreshes every night at 00:01 and shortly after you log in."
echo "If you move this folder, run ./install.sh again."
echo "On your desktop there is now a \"Wheel of the Year\" folder holding:"
echo "  Pictures          - the folders it reads"
echo "  Settings.toml     - change how it looks"
echo "  Update Wallpaper Now - redraw it straight away"
echo "They are in the application menu too: search for \"Wheel of the Year\"."
