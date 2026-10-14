---
name: reel-script
description: Write the SAM reel scripts as engine specs — an English version and a natural Egyptian Arabic version — plus per-platform captions, titles and hashtags. Use after a topic is chosen, or when asked to write, rewrite or translate a reel script.
---

# Reel script: specs + captions

Input: the research brief from `reel-research`. Read `reels/strategy.md` (hook formulas, scene
grammar, script rules) and `reels/engine/README.md` (exact scene fields) before writing.

## 1. English spec → `reels/specs/<date>-en.json`

Copy the structure of `reels/specs/sample-en.json`. Set `id`, `lang: "en"`,
`watermark` (from config), `presenter: "../brand/presenter.png"`, `topic`, `sources`.

Build 5–7 scenes following the typical arc in the strategy. Checklist:

- `hook.big`: 1–3 lines, ≤ 4 words each; the line that carries the twist is `accentLine`.
- Spoken `say` per scene: 8–25 words, conversational, one sentence or two short ones.
  Total 80–110 words.
- `steps` ≤ 3 items (4 at most), each `t` ≤ 5 words; detail goes in `s`.
- On-screen text never just repeats the narration word for word; it summarises it.
- Mark 1–2 key words per scene with `*asterisks*` for accent colour — not more.
- Use a `presenter` scene at least 3 days a week (alternate with `tool`/`stat` in slot 2).
- `cta`: alternate "Follow SAM for one AI trick a day" and "Save this / send it to a friend
  who needs it" by day.

## 2. Egyptian Arabic spec → `reels/specs/<date>-ar.json`

Write it **natively in Egyptian colloquial**, not as a literal translation and not in
Modern Standard Arabic. Same scene types and order, so visuals match.

- Spoken style: "بطّل"، "ببلاش"، "خلّي"، "دوس"، "حركة"، "هتحتاجه"، "بص".
- Keep tool names, buttons and URLs in English letters exactly as the UI shows them.
- Hook lines can be shorter than English; Arabic headline type is set larger.
- Watermark from `brand.watermark_ar`; CTA button "＋ تابع SAM".

## 3. Captions → `reels/specs/<date>-post.json`

```json
{
  "en": {"caption": "hook line\n\n3 short value lines\n\nCTA", "hashtags": ["#AI","#AITools","#NotebookLM"],
         "youtube_title": "≤ 70 chars, keyword first", "tiktok_title": "…", "first_comment": "Source: https://…"},
  "ar": {"caption": "…", "hashtags": ["#ذكاء_اصطناعي","#AI"], "youtube_title": "…", "tiktok_title": "…", "first_comment": "…"}
}
```

Captions: first line works without "more" being tapped; 3–5 hashtags (one broad, two niche,
one tool name); the source link goes in `first_comment`, not the caption. X/Threads get the
caption trimmed to the first two lines.

## 4. Self-check before handing on

Read both specs back and check: every factual claim is in the research `facts`; no scene's
`say` exceeds 25 words; no on-screen line is longer than ~32 characters (English) or ~26
(Arabic); the hook pays off within the reel.
