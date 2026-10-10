#!/usr/bin/env bash
# Redraw today's wallpaper right now (e.g. after adding pictures or changing settings).
# Double-click the "Update Now" icon, or run this from a terminal.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out="$(python3 "$DIR/app/wheel-of-the-year.py" "$@" 2>&1)"
status=$?
echo "$out"

# When double-clicked there's no terminal to read, so say something on screen.
if [[ -t 1 ]]; then exit $status; fi
if command -v notify-send >/dev/null; then
    if [[ $status -eq 0 ]]; then
        summary="$(echo "$out" | grep -o '^v[^|]*' | head -1)"
        notify-send -a "Wheel of the Year" -i "$DIR/app/assets/icons/update.png" \
            "Wallpaper updated" "${summary:-The wallpaper has been redrawn.}"
    else
        notify-send -u critical -a "Wheel of the Year" \
            "Couldn't update the wallpaper" "See build/log.txt in the Wheel of the Year folder."
    fi
fi
exit $status
