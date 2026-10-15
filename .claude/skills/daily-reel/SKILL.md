---
name: daily-reel
description: Produce and publish today's reel in Sam's 365-day AI & Digital Transformation series. It researches today's AI trends, finalizes the bilingual (Arabic-first, English keywords) script, makes a lip-sync talking head from Sam's photo when credits allow, renders the branded 1080x1920 reel, hosts it, and schedules it to Instagram, Facebook, LinkedIn and Threads via Metricool. Use when asked to make, render or publish today's reel, or when the daily scheduled task fires.
---

# Daily reel runbook

Run every step in order. Never skip publishing because an optional step (voice, lip sync) failed: fall back and keep going. Report what was skipped and why at the end.

## Fixed rules for every reel
- **Hook in the first 3 seconds:** one punchy Arabic line of 12 words or fewer, plus the English keyword chip. Use a curiosity gap, a bold number or a myth-buster. No greetings and no "in this video".
- **Language:** mainly Arabic (clear, simple, Egyptian-friendly), with tool names and AI keywords in English, alternating in every scene (for example "الـ Context Window").
- **Middle:** illustrate how to use the tool or skill directly, as concrete steps, a prompt to copy, or a before/after. Teach simply.
- **Ending:** Sam's quote from `reels/brand.json` (`quote_en`, plus `quote_ar` if set) signed `— Sam`. The renderer adds it automatically. Never change the quote text yourself.
- **Voiceover:** 85 words or fewer, so the reel is about 30 seconds.
- **Accuracy:** verify every tool claim with a web search done today. Tools change fast, so fix stale steps before rendering.
- **Positioning:** Sam is a forward-looking leader who learns in public and teaches AI and digital transformation (Claude, Manus, Google Flow, Google Labs, Gemini, NotebookLM, and the rest).

## 1. Prepare
```bash
cd "$(git rev-parse --show-toplevel)"
test -d reels || { git fetch origin main && git checkout origin/main -- reels .claude 2>/dev/null; }
test -d reels || { git fetch origin claude/whatsapp-skills-setup-vht8hc && git checkout FETCH_HEAD -- reels .claude; }
python3 -c "import numpy, PIL; from PIL import features; assert features.check('raqm')" || pip install -q numpy pillow
git fetch origin reels-output 2>/dev/null && git show FETCH_HEAD:reels/publish_log.jsonl > reels/publish_log.jsonl 2>/dev/null || true
python3 reels/scripts/today.py
```
`today.py` prints the entry path (`reels/work/day-NNN.json`). Edit that file in place in the next steps.

## 2. Research today's trends (always)
Use WebSearch (mode "standard"; switch to "extended" only if results are thin) and send these together:
- `Anthropic Claude news this week`, `Manus AI agent update`, `Google Flow Veo update`, `Google Labs new experiment`, `Gemini update this week`
- `<entry.tool> <entry.keyword> latest`

Then update the entry:
- If **`needs_live_trend` is true** (format `trend_watch`), replace every scene marked `[يتحدّث يوميًا]`, the `hook_ar`, the `voiceover_ar` and the caption with the single most useful news item for professionals. The three scenes are: what happened, why it matters to you, and what to do today. Add the source link at the end of the caption.
- **Otherwise**, keep the planned topic and check that its steps are still accurate. Add one caption line `🆕 اليوم في الـ AI: …` with the top trend. Swap the hook only if a trend makes it clearly stronger.
- If the planned topic is obsolete (the tool was renamed or discontinued), swap in a matching theme from `RESERVE_THEMES` in `reels/content/themes.py`.
- If `today.py` warned that the hook was recently used, rewrite the hook.

## 3. Voice and lip sync (optional; needs credits)
Sam's photo:
- local file: `reels/assets/sam.jpg`
- Higgsfield element: `Sam-SAMs-AI` (`d0c324cc-2e57-43b3-9a68-4301f9799885`)
- public URL: `avatar.photo_url` in `brand.json`

1. Check `mcp__Magnific__account_balance` and `mcp__Higgsfield__balance`. If both are 0, skip to step 4 (text and music version).
2. **Magnific path:**
   1. `audio_tts` (an Arabic voice from `audio_voices_list`; use Sam's cloned voice if one exists under `scope: mine`) with `voiceover_ar`.
   2. `creations_upload_image` on `avatar.photo_url`.
   3. `video_speak` (mode `omnihuman`) with that image and the TTS audio.
   4. `creations_wait`.
3. **Higgsfield path:** `generate_video` with a model that supports elements and native audio (`seedance_2_0` or `cinematic_studio_3_0`). Put `<<<d0c324cc-2e57-43b3-9a68-4301f9799885>>>` in the prompt with the Arabic lines in quotes, `aspect_ratio: "9:16"`. Preflight with `get_cost: true` first.
4. Download the talking-head MP4 and the voice MP3 into `reels/work/`. If the CDN is blocked by the network, skip the overlay and keep going.

## 4. Render
```bash
python3 reels/render/render_reel.py --entry reels/work/day-NNN.json \
  [--voice reels/work/day-NNN.mp3] [--avatar-video reels/work/day-NNN-talk.mp4] \
  --out reels/output/day-NNN.mp4
```

## 5. Quality check (look at the frames)
```bash
for s in 1.5 8 15; do ffmpeg -y -loglevel error -ss $s -i reels/output/day-NNN.mp4 -frames:v 1 -vf scale=540:-1 reels/work/qa_$s.png; done
ffmpeg -y -loglevel error -sseof -1.5 -i reels/output/day-NNN.mp4 -frames:v 1 -vf scale=540:-1 reels/work/qa_end.png
```
Open the PNGs with Read and check:
- the hook is readable at 1.5s
- the Arabic is connected (no boxes or broken letters)
- the content scenes fit the frame
- the last frame shows the quote and `— Sam`

Fix the issue and re-render if anything fails.

## 6. Host the MP4 publicly
The repo `samsafwat/SAMs-` is public. Commit the reel to the `reels-output` branch:
```bash
git fetch origin reels-output 2>/dev/null
git worktree add /tmp/ro FETCH_HEAD 2>/dev/null || git worktree add --orphan -b reels-output /tmp/ro
mkdir -p /tmp/ro/reels/output && cp reels/output/day-NNN.mp4 /tmp/ro/reels/output/
cd /tmp/ro && git add reels/output/day-NNN.mp4 && git commit -m "Reel day NNN" && git push origin HEAD:reels-output
```
Public URL: `https://raw.githubusercontent.com/samsafwat/SAMs-/reels-output/reels/output/day-NNN.mp4`. Verify that `curl -sI` on it returns 200. If the push is refused, upload with `mcp__Magnific__creations_request_upload` + `creations_finalize_upload` and use that asset URL.

## 7. Publish (Metricool)
1. `getBrandSettings` returns `blogId`, the timezone and the connected networks. If none of instagram, facebook, linkedin or threads is connected, stop and report "connect networks in Metricool". Don't fail silently.
2. Call `createScheduledPost` once with every connected network among those four:
   - `media`: [hosted URL]
   - `text`: entry caption (Threads truncates long text; keep the first 500 characters meaningful)
   - `publicationDate`: today at `publish_time_local` in the brand timezone, or 10 minutes from now if that time has passed
   - `autoPublish`: true
   - `instagramData`: `{"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}`
   - `facebookData`: `{"type":"REEL"}`
   - `linkedinData`: `{"type":"post"}`
   - `threadsData`: `{}`
   - `videoCoverMilliseconds`: 1500 (the hook frame)

## 8. Log and report
Append one JSON line to `reels/publish_log.jsonl`:
```json
{"day": N, "date": "...", "hook_ar": "...", "video_url": "...", "planner_url": "...", "lip_sync": true, "trend": "..."}
```
Commit it to `reels-output` together with the MP4. Finish with a short report: day, hook, trend used, lip sync yes/no, publish status and links, and anything skipped.
