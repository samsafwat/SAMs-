# Reel engine

Turns a JSON spec into a finished 1080×1920 MP4: motion graphics, word-by-word captions,
synthesized music/SFX bed, and (optionally) narration and lip-synced presenter clips.

```bash
python3 -m venv .venv && .venv/bin/pip install playwright numpy   # Chromium is preinstalled in cloud sessions
.venv/bin/python reels/engine/render.py reels/specs/sample-en.json out/sample --stills 1.5,6,12   # design check
.venv/bin/python reels/engine/render.py reels/specs/sample-en.json out/sample --audio-dir out/sample/audio
```

Outputs `reel.mp4`, `cover.jpg` (frame from the hook, used as thumbnail) and `timeline.json`.
A 40 s reel renders in ~5 minutes on 4 CPUs.

## Spec

```jsonc
{
  "id": "2026-10-14-en",
  "lang": "en",                      // "ar" switches to right-to-left + Cairo font
  "watermark": "✳ @SAM · GEN AI TIPS",
  "presenter": "../brand/presenter.png",   // transparent cut-out, relative to the spec
  "accent": "#d97757",               // optional
  "topic": "…", "sources": ["https://…"],  // for fact-checking and the history log
  "scenes": [ { "type": "hook", "say": "spoken narration for this scene", ... } ]
}
```

Each scene lasts as long as its narration clip (`--audio-dir`, files `01.wav`, `02.mp3`, …),
else `dur` if given, else an estimate from the word count of `say`. Captions come from `say`.
In any text field, `*word*` renders in the accent colour.

| type | fields |
|------|--------|
| `hook` | `big` (array of lines, ≤ 4 words each), `accentLine` (index, default 1), `sub`, `strike` (words struck through at the end), `size`, `top` |
| `presenter` | `title`, `chips` (array), `video` (optional lip-sync clip) |
| `tool` | `kicker`, `tag`, `name`, `line`, `url` |
| `steps` | `title`, `items`: `[{"t": "step", "s": "detail"}]` (max 4) |
| `list` | `title`, `items` (max 5 strings) |
| `strikes` | `items` (struck one by one), `punch` |
| `stat` | `number` (e.g. `"10x"`, `"$0"`, `"87%"`; counts up), `label`, `source` |
| `quote` | `text` (words appear one by one), `author` |
| `voice` | `big` (2 lines), `sub` — animated waveform |
| `cta` | `top`, `button`, `sub`, `save`, `video` (optional lip-sync clip) |

Headlines marked to fit (`hook` lines, tool `name`, stat `number`) shrink automatically to fit
the frame.

Fonts: Inter Display (system) for Latin, Cairo (bundled in `fonts/`, SIL OFL) for Arabic.
