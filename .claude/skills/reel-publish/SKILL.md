---
name: reel-publish
description: Publish a rendered SAM reel to Instagram, TikTok, YouTube Shorts, Facebook, LinkedIn, Threads and X through Metricool — hosting the MP4 at a public URL, per-network captions and AI-content labels, best posting times, and review (draft) vs auto mode. Use when scheduling or posting a reel, or checking what is scheduled.
---

# Reel publish: Metricool

Metricool MCP tools (load with ToolSearch): `getBrandSettings`, `getBestTimeToPostByNetwork`,
`createScheduledPost`, `getScheduledPosts`, `updateScheduledPost`. Settings:
`reels/config.json` → `metricool`, `platforms`, `mode`, `timezone`.

## Preconditions

`getBrandSettings` must list the brand with networks connected. If it says no network is
connected, stop and give Sam the connection link from the error
(app.metricool.com → Brand → Connections). Only schedule to networks that are connected.

## 1. Host the video at a public URL

Metricool needs a public URL for the MP4 and the cover. Default host: the `reels-media` branch
of this public repo (the reels are public anyway). Never put anything private there.

```bash
git fetch origin reels-media || true
git worktree add /tmp/reels-media reels-media 2>/dev/null || git worktree add --orphan -b reels-media /tmp/reels-media
mkdir -p /tmp/reels-media/<date>
cp out/<date>-en/reel.mp4 /tmp/reels-media/<date>/en.mp4 ; cp out/<date>-en/cover.jpg /tmp/reels-media/<date>/en.jpg
cp out/<date>-ar/reel.mp4 /tmp/reels-media/<date>/ar.mp4 ; cp out/<date>-ar/cover.jpg /tmp/reels-media/<date>/ar.jpg
git -C /tmp/reels-media add . && git -C /tmp/reels-media commit -m "reel <date>" && git -C /tmp/reels-media push -u origin reels-media
```

URL: `https://raw.githubusercontent.com/<repo>/reels-media/<date>/<lang>.mp4`. Check it returns
200 with `curl -sI` before scheduling.

## 2. When

For each network, `getBestTimeToPostByNetwork` over the next 24 h in the configured timezone;
take the best slot at least 30 minutes from now. Fallbacks: Arabic 19:30, English 17:00 local.
Don't put both languages on the same account within 3 hours of each other.

## 3. Schedule one post per language

`createScheduledPost` with `blogId` = `metricool.blog_id[<lang>]`, `info` built from
`reels/specs/<date>-post.json` and the media URL:

- `providers`: the connected networks from `platforms`.
- `media`: [video URL]; `videoThumbnailUrl`: cover URL (only where supported — omit it if the
  tool rejects it with `VIDEO_THUMBNAIL_NOT_APPLICABLE`).
- `text`: caption + hashtags; `firstCommentText`: the source line.
- **AI labels (always):** `instagramData: {type: "REEL", isAiGenerated: true}`,
  `tiktokData: {title, isAigc: true}`, `youtubeData: {type: "short", title, madeForKids: false, isAiGeneratedContent: true}`,
  `facebookData: {type: "REEL", title}`, `linkedinData: {}`, `threadsData: {}`, `twitterData: {}`.
- **Review mode** (`mode: "review"`): `draft: true`. Sam approves in Metricool.
  **Auto mode**: `draft: false`, `autoPublish: true`.

Relay errors as returned (e.g. X length limits) and continue with the other networks.

## 4. Report

Per language: networks, scheduled time, `plannerUrl` for each post. Put them in the history line.
