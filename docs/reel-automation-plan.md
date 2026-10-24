# SAM daily reel automation — plan

**Goal:** one reel every day, in English and in Egyptian Arabic, published to Instagram,
TikTok, YouTube Shorts, Facebook, LinkedIn, Threads and X. Each reel is a 30–45 s motion-graphics
video with one simple, verified, "I didn't know that" AI tip, narrated in Sam's cloned voice,
with a lip-synced Sam on screen for the intro or call to action.

**Honest expectations:** nothing can guarantee virality or millions of followers. What
automation buys is the thing most creators fail at: posting something good every single day
for months, and learning from the numbers every week. The plan below is built around that.

## How a day runs

```
06:45  Routine fires (fresh cloud session in this repo) → runs the `daily-reel` skill
         1 reel-research   find + verify today's tip (pillar of the day, not covered before)
         2 reel-script     EN spec + Egyptian Arabic spec + captions/titles/hashtags
         3 reel-voice      cloned-voice narration per scene; lip-sync for presenter/CTA scenes
         4 reel-render     stills QA → full render → reel.mp4 + cover.jpg (per language)
         5 reel-publish    host MP4s → schedule on every connected network via Metricool
         6 log             reels/history.jsonl, commit, report to Sam
~07:30  Review mode: posts sit as drafts in Metricool; Sam approves on his phone (2 minutes)
17:00 / 19:30  Best-time slots (from Metricool) — English / Arabic go live
Sunday 10:00   Second routine runs `reel-analytics` → reels/learnings.md (feeds next week)
```

## What's in this repo

| Piece | Path | Role |
|-------|------|------|
| Reel engine | `reels/engine/` | JSON spec → 1080×1920 MP4: 10 animated scene types, word-by-word captions, RTL Arabic, synthesized music + SFX, narration mixing with ducking, optional lip-sync clips |
| Brand bible | `reels/strategy.md` | positioning, 7 weekday pillars, hook formulas, script and caption rules |
| Settings | `reels/config.json` | handle, languages, timezone, review/auto mode, platforms, Higgsfield ids, daily credit cap, Metricool brand ids, media host |
| Samples | `reels/specs/sample-*.json` | reference specs in both languages |
| Skills | `.claude/skills/daily-reel`, `reel-research`, `reel-script`, `reel-voice`, `reel-render`, `reel-publish`, `reel-analytics` | the playbook each stage follows |
| Memory | `reels/history.jsonl`, `reels/learnings.md` | what was published; what the numbers say (created by the pipeline) |

## Connectors used

| Connector | Used for | Status today |
|-----------|----------|--------------|
| ElevenLabs | narration in Sam's cloned voice (EN + Egyptian Arabic) | connected; clone "SAM Voice" not created yet |
| Higgsfield | lip-sync (and fallback narration) | connected; **0 credits** |
| Metricool | scheduling to all networks, best times, analytics | connected; **no social network linked** |
| GitHub | code, specs, history; `reels-media` branch hosts the public MP4s | connected |
| WhatsApp (repo skills) | optional: send Sam the daily preview | needs `.env` from Meta |

Not needed: browser automation of social apps (logging a bot into Instagram/TikTok breaks their
terms and gets accounts restricted — Metricool uses the official APIs), and the Zoom Video SDK
(it's for building live video-call apps, not producing reels).

## Setup — only Sam can do these

1. **Connect your social accounts in Metricool** (Brand → Connections): Instagram (Business or
   Creator, linked to a Facebook Page), TikTok, YouTube, Facebook Page, LinkedIn, Threads, X.
   Decide whether English and Arabic go to the **same accounts or separate ones** (recommended:
   separate Instagram/TikTok accounts per language, same YouTube channel); put the brand ids in
   `reels/config.json → metricool.blog_id`.
2. **Higgsfield credits** (see costs below), then say "clone my voice" so the voice id is saved.
3. **Network access for the cloud environment** — add to Allowed domains:
   `upload.higgsfield.ai`, `cdn.higgsfield.ai`, `d2ol7oe51mr4n9.cloudfront.net`,
   `d1xarpci4ikg0w.cloudfront.net` (Higgsfield uploads/downloads). Steps:
   https://code.claude.com/docs/en/cloud-environments#network-access
4. **Presenter photo:** your cut-out photo must exist in fresh sessions. Either allow committing
   `reels/brand/presenter.png` to this public repo (it's on your public reels anyway), or keep
   it private and let the routine skip presenter scenes.
5. **Delete the leftover branch** `tmp-media-x7k2` on GitHub (Branches page).
6. **Approve turning on the routines** (daily 06:45 and Sunday analytics).

## Costs (Higgsfield, from live price checks)

| Item | Credits |
|------|---------|
| Narration, per scene line | ~0.5 → ~6/day for 6 scenes × 2 languages |
| Lip-sync video | ~7 per second (210 per 30 s clip) |

| Option | Per day | Per month | Plan that covers it |
|--------|---------|-----------|---------------------|
| Voice only, no lip-sync | ~6 | ~180 | PLUS (1,000 credits) |
| Voice + lip-sync on the CTA (≈5 s) in both languages | ~76 | ~2,300 | ULTRA (3,000 credits) |
| Voice + lip-sync on intro and CTA, both languages | ~146 | ~4,400 | ULTRA + top-ups |

Default cap in config: 120 credits/day (voice + one lip-sync scene per language).
Metricool: the free plan has posting limits; daily posting to 7 networks needs a paid plan.

## Growth playbook (what the automation can't do alone)

- **First 2 weeks in review mode**, then switch `mode` to `auto` once you trust it.
- **Series names** viewers recognise: "AI trick of the day #N", "Free tool Sunday".
- **Instagram Trial Reels** for risky hooks (shown to non-followers first).
- **Reply to comments in the first hour**; pin the best question and answer it in a reel.
- **Collaborate** weekly with an Egyptian tech/education creator (Instagram collab posts double
  the reach of one reel).
- **Repurpose** every 5 reels into a carousel and a LinkedIn post.
- Give it **90 days** before judging; change one variable a week based on `reels/learnings.md`.

## Guardrails

- Every claim verified on an official source; sources go in the first comment.
- AI-generated content is labelled on every platform that asks (cloned voice, generated video).
- Your raw voice sample never goes in git; the clone lives in Higgsfield by id.
- Spending is capped per day and checked before each paid call.
