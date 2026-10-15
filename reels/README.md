# Sam's 365-day AI reels

This pipeline produces one reel a day for a year (2026-10-16 to 2027-10-15). The reels position Sam as a leader who learns and teaches AI and digital transformation with Claude, Manus, Google Flow, Google Labs and Gemini. Every reel follows the same shape:

| Part | Content |
|---|---|
| 0–3 s | A strong Arabic hook plus an English keyword chip |
| Middle | A tool demo, a prompt to copy, myth vs fact, a business case, a concept or a mindset lesson. Arabic-first, with English keywords |
| Last 4 s | Sam's quote, signed **— Sam** |

## Files
| Path | Purpose |
|---|---|
| `brand.json` | The quote, signature, colors, platforms, publish time and timezone, plus Sam's photo and Higgsfield element. **Edit the quote here.** |
| `content/themes.py` | 52 weekly themes, plus 5 reserves for when a topic goes stale |
| `content/build_calendar.py` | Builds the calendar: 52 themes × 7 daily formats, plus a finale on day 365 |
| `calendar/calendar_365.json`, `.csv`, `CALENDAR.md` | The full year: hook, scenes, voiceover, caption and hashtags for each day |
| `render/render_reel.py` | Renders a 1080×1920 MP4: neon HUD look, Sam's photo, Arabic shaping, glitch-in hook, outro, music bed and an optional lip-sync overlay |
| `scripts/today.py` | Picks today's entry and warns about repeated hooks |
| `../.claude/skills/daily-reel/SKILL.md` | The daily runbook: research trends, script, lip sync, render, quality check, host, publish, log |

## Daily formats (they rotate)
1. **Tool of the Day** — step-by-step demo
2. **Prompt Recipe** — a prompt to copy and paste
3. **Myth vs Fact**
4. **Transformation Case** — a real business use case
5. **AI Trend Radar** — rewritten each day from a live web search
6. **AI Concept in 30s**
7. **Leader Mindset**

## Commands
```bash
python3 reels/content/build_calendar.py          # rebuild the calendar after editing themes or brand.json
python3 reels/render/render_reel.py --day 1      # render any day to reels/output/
python3 reels/scripts/today.py                   # today's entry, saved to reels/work/
```

## One-time setup (Sam)
1. **Photo:** add a clear, front-facing photo as `reels/assets/sam.jpg`. Until then, the local render shows a holographic placeholder. The cloud lip-sync tools already use the Higgsfield element `Sam-SAMs-AI`.
2. **Publishing:** connect Instagram (Business or Creator), the Facebook Page, LinkedIn and Threads in Metricool: <https://app.metricool.com/brands/connections?blogId=7226124>
3. **Lip sync and voice:** add credits to Magnific or Higgsfield. With 0 credits the reels still publish, with text and music but no talking head. An Arabic cloned voice in Magnific (My Voices) gives the most natural result.

Rendered reels and `publish_log.jsonl` are kept on the `reels-output` branch. Raw GitHub URLs on that branch are the public media links Metricool publishes from.
