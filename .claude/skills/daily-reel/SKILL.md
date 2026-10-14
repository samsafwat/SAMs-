---
name: daily-reel
description: Produce and publish today's SAM reel end to end — pick a fresh AI tip, write English and Egyptian Arabic scripts, voice them with Sam's cloned voice, render the motion-graphics reel, and schedule it on every connected social network. Use when asked to "make today's reel", "run the daily reel", or when the daily routine fires.
---

# Daily reel: the whole pipeline

Run the stages below in order. Each stage has its own skill with the details; this file is the
checklist and the rules that hold across stages. Work from the repo root.

Read first: `reels/config.json` (settings), `reels/strategy.md` (what good looks like),
`reels/learnings.md` if it exists (what the numbers taught us), and the last 30 lines of
`reels/history.jsonl` (what was already covered).

| # | Stage | Skill | Output |
|---|-------|-------|--------|
| 1 | Find today's tip | `reel-research` | a verified topic + sources |
| 2 | Write both scripts | `reel-script` | `reels/specs/<date>-en.json`, `-ar.json`, `<date>-post.json` |
| 3 | Voice + lip-sync | `reel-voice` | `out/<date>-<lang>/audio/NN.wav`, presenter clips |
| 4 | Render + QA | `reel-render` | `out/<date>-<lang>/reel.mp4`, `cover.jpg` |
| 5 | Publish | `reel-publish` | scheduled posts on each network, planner links |
| 6 | Log | (below) | a line in `reels/history.jsonl` |

`<date>` is today in the configured timezone, `YYYY-MM-DD`.

## Rules across stages

- **Never publish something you haven't looked at.** After rendering, view the stills and the
  cover image (Read tool) and check them against the QA list in `reel-render`.
- **Facts are verified or cut.** A claim you could not confirm on an official source today does
  not go in the script.
- **Degrade, don't stop.** If a paid or blocked step fails, fall back and say so in the report:
  - no Higgsfield credits / voice not cloned yet → render without narration (captions + music
    still carry the reel), and drop the "this voice is cloned" lines;
  - lip-sync too expensive for today's budget (`max_credits_per_day`) → still presenter photo;
  - no social network connected in Metricool → stop after rendering and deliver the files.
- **Mode.** `config.mode == "review"`: schedule posts as Metricool drafts (`draft: true`) and
  report the planner links so Sam approves them. `"auto"`: schedule for real. Start in review
  mode; switch only when Sam says so.
- **Spend.** Run every paid generation with `get_cost: true` first. Stop and report if today's
  total would exceed `higgsfield.max_credits_per_day`.
- Don't commit rendered videos to the default branch. Final MP4s go to the media host (see
  `reel-publish`); specs and the history log are committed.

## 6. Log and report

Append one JSON line to `reels/history.jsonl`:

```json
{"date":"2026-10-14","pillar":"free-tool","topic":"NotebookLM Audio Overviews","tool":"NotebookLM","hook":"Stop reading PDFs","sources":["https://…"],"langs":["en","ar"],"voiced":true,"lipsync":["cta"],"credits":38,"posts":{"instagram":"https://…planner…"},"mode":"review"}
```

Commit `reels/specs/<date>-*.json` and `reels/history.jsonl` on the working branch and push.

Finish with a short report: the topic and hook, the two video files (send them with
SendUserFile when available), where each post is scheduled (planner links), credits spent, and
anything that degraded and why.
