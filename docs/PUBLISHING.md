# Launch checklist

Everything here is ready; this is the order to do it in on the day.

## Before pushing

1. `python3 tools/make_release.py all` — rebuild both zips at the current version.
2. Check the version: `wheel_of_year/__init__.py`. Bump to `1.0.0` for the public launch.
3. Update `CHANGELOG.md` — the top section becomes the release notes.
4. Check nothing personal is staged: `git status` should show no photographs, no `config.toml`,
   no `build/`, no `releases/`.

## The repository

```bash
gh repo create RunicMyst/wheel-of-the-year-wallpaper --public \
    --description "A desktop wallpaper that tracks the Wheel of the Year: Sabbats, zodiac, Norse months and the moon" \
    --source . --push
```

Suggested topics (Settings → Topics): `wallpaper`, `kde-plasma`, `windows`, `python`,
`pagan`, `wheel-of-the-year`, `norse`, `astronomy`, `moon-phases`.

## The release

```bash
gh release create v1.0.0 \
    "releases/Wheel of the Year - Windows 10-11 v1.0.0.zip" \
    "releases/Wheel of the Year - Linux v1.0.0.zip" \
    --title "Wheel of the Year v1.0.0" --notes-file CHANGELOG.md
```

(Trim the notes to the newest section first, or write them in the web form instead.)

## Afterwards

- Point the people already testing at the Releases page rather than emailing zips.
- Watch for the first macOS tester - there's an issue template for it.
- Fixes: bump the version, rebuild, `gh release create` again. People unzip over the top; their
  photos and settings are kept.
