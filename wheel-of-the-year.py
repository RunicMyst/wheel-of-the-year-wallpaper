#!/usr/bin/env python3
"""Launcher: render today's Wheel of the Year wallpaper (see `--help`)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wheel_of_year.__main__ import main  # noqa: E402

sys.exit(main())
