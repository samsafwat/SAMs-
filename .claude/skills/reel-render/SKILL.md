---
name: reel-render
description: Render a SAM reel spec into the final 9:16 MP4 with the repo's motion-graphics engine (reels/engine), and quality-check stills and cover before publishing. Use when rendering, previewing or fixing the look of a reel, or adding a new scene type to the engine.
---

# Reel render: engine + QA

Engine docs: `reels/engine/README.md` (spec format, scene fields). Brand photo:
`reels/brand/presenter.png` (git-ignored; see `reels/brand/README.md`).

## Setup (once per session)

```bash
python3 -m venv .venv && .venv/bin/pip install -q playwright numpy
```

Chromium is preinstalled at `/opt/pw-browsers` in cloud sessions; never run `playwright install`.
`ffmpeg` must be on PATH. If `presenter.png` is missing, either make it (brand README) or
remove `presenter` scenes and the `presenter` field from the spec for today.

## 1. Stills first (30 seconds)

```bash
.venv/bin/python reels/engine/render.py reels/specs/<date>-<lang>.json out/<date>-<lang> --audio-dir out/<date>-<lang>/audio --stills auto
```

`--stills auto` writes one PNG per scene (the middle of each). Look at every one with the Read
tool (tile them first to save time:
`ffmpeg -pattern_type glob -i 'out/<d>/still_*.png' -vf "scale=270:480,tile=7x1" out/<d>/sheet.jpg`).

QA list — fix the spec and re-run stills until all pass:

- No text runs off the frame or overlaps other text (captions sit at y≈1590–1750).
- Hook reads in under 1 second; the accent line is the twist.
- Arabic stills are right-to-left, Cairo font, English tool names readable.
- The presenter's face isn't cut by text or the ring.
- Nothing in the bottom 200 px or the top 150 px is essential (platform UI covers it).
- Spelling of tool names and URLs matches the official site.

## 2. Full render (~5 min per 40 s reel)

Same command without `--stills`. Outputs `reel.mp4`, `cover.jpg`, `timeline.json`.
Then check: `ffprobe` shows 1080×1920, 30 fps, AAC audio, 25–60 s; look at `cover.jpg`.

## Changing the look

All visuals live in `reels/engine/reel.html` (scene builders in the `T` object, shared styles
at the top). Keep `render(t)` deterministic (no CSS animations, timers or `Math.random`).
After any change, render both `reels/specs/sample-en.json` and `sample-ar.json` stills and check
them before using it on a real reel. Music/SFX timing is in `reels/engine/sfx.py`.
