---
name: reel-voice
description: Voice the SAM reel scripts with Sam's cloned voice and make lip-synced presenter clips through Higgsfield — one-time voice cloning, per-scene narration in English and Egyptian Arabic, cost checks, and downloads into the render folder. Use when narrating a reel, cloning or re-cloning Sam's voice, or making a talking-head clip from his photo.
---

# Reel voice: cloned narration + lip-sync

Higgsfield MCP tools (load them with ToolSearch: `generate_audio_batch`, `generate_video`,
`jobs_wait`, `balance`, `media_upload`, `media_confirm`, `create_voice_from_confirmed_audio`,
`list_voices`). Settings live in `reels/config.json` → `higgsfield`.

## Preconditions (check every run)

1. `balance` — credits available. Today's budget is `max_credits_per_day`.
2. Network: the sandbox must reach `upload.higgsfield.ai` (uploads) and the host in each result
   URL (downloads, a `*.cloudfront.net` / `cdn.higgsfield.ai` address). If a download is
   blocked by the proxy, say which host and point Sam to the environment's network settings.
3. `higgsfield.voice_id` is set. If it's `null`, the voice hasn't been cloned yet — see below.

If any of these fail, follow the "degrade" rules in `daily-reel` (render without narration).

## One-time: clone Sam's voice

Only with Sam's sample in hand (never commit the sample to git; this repo is public).
Use 1–3 minutes of clean speech, ideally one clip per language.

1. `media_upload` (filename `sam_voice.mp3`) → `curl -X PUT -H "Content-Type: audio/mpeg" --data-binary @file '<upload_url>'` → `media_confirm` (type `audio`).
2. `create_voice_from_confirmed_audio` with `name: "SAM Voice"`.
3. Poll `list_voices` until it shows `status: completed` / `is_audio_eligible: true`.
4. Write the id into `reels/config.json` → `higgsfield.voice_id` and commit.

## Narration (each language)

1. One request per scene, using that scene's `say`, via `generate_audio_batch`:
   `model: seed_audio`, `voice_type: element`, `voice_id: <config>`, `format: wav`,
   `sample_rate: 44100`. Run once with `get_cost: true` first and add it to today's total.
2. `jobs_wait` until done; download each result to `out/<date>-<lang>/audio/NN.wav`
   (NN = scene number, 01-based), with `curl -L -o`.
3. Listen-check proxy: `ffprobe` each file; a clip shorter than 1 s or longer than 15 s means
   something went wrong — regenerate that scene once.
4. Arabic: the text is Egyptian colloquial; if pronunciation of English tool names is off,
   write them the way they're said in Arabic letters in `say` for TTS only, but keep the
   on-screen text in English.
5. If `seed_audio` mispronounces Arabic badly, retry the Arabic set with
   `model: text2speech_v2`, `variant: elevenlabs`, same voice element.

## Lip-sync (only the presenter scenes)

Lip-sync is the expensive part (~7 credits per second of video). Only scenes whose type is in
`lipsync_scenes` get it, usually the `presenter` intro and the `cta` (≈ 8–12 s total).

For each such scene:

1. `generate_video` with `model: seedance_2_5`, `mode: omni_reference`, `aspect_ratio: "9:16"`,
   `resolution: "720p"`, `duration`: the scene's audio length rounded up (min 4),
   `medias`: `[{role: start_image, value: <presenter_media_id>}, {role: audio_references, value: <that scene's audio job id>}]`,
   prompt: "The man in the photo speaks directly to camera, natural head movement, lips synced exactly to the reference audio, keep his face, glasses and shirt unchanged, same background". Set `get_cost: true` first. If the tool offers a preset instead, retry with `declined_preset_id`.
2. Download to `out/<date>-<lang>/clips/NN.mp4` and set that scene's `"video": "../../out/<date>-<lang>/clips/NN.mp4"` in the spec (path relative to the spec file).
3. If the day's budget can't cover it, skip lip-sync; the still cut-out is used.

The renderer uses the scene's narration clip for audio and the video only for the picture, so a
slight length mismatch is fine (the last frame holds).
