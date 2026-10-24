---
name: reel-voice
description: Voice the SAM reel scripts with Sam's cloned voice (ElevenLabs by default, Higgsfield as fallback) and make lip-synced presenter clips through Higgsfield — voice setup, per-scene narration in English and Egyptian Arabic, cost checks, and downloads into the render folder. Use when narrating a reel, cloning or re-cloning Sam's voice, or making a talking-head clip from his photo.
---

# Reel voice: cloned narration + lip-sync

`reels/config.json → voice.provider` picks the narration engine: `elevenlabs` (default) or
`higgsfield`. Lip-sync is always Higgsfield (the ElevenLabs connector has no video).

## Narration with ElevenLabs (default)

Tools (ToolSearch): `creative_list_voices`, `creative_create_flow`, `creative_generate_speech`,
`creative_get_flow_run_status`.

1. **Voice id.** `voice.elevenlabs_voice_id` in config. If it's `null`, look for Sam's clone with
   `creative_list_voices` (search `voice.voice_name`, i.e. "SAM Voice"); pick only a voice whose
   name matches exactly and is in his own workspace (not `is_library_voice: true`), save the id
   to config and commit. If there is none, the clone hasn't been made: Sam creates it once in the
   ElevenLabs app (Voices → Add a new voice → Instant Voice Clone, upload the voice sample, name
   it "SAM Voice"). This connector cannot clone. Until then, degrade (no narration).
2. One `creative_create_flow` per reel ("SAM reel <date> <lang>"), then one
   `creative_generate_speech` per scene on that flow: `prompt` = the scene's `say`,
   `voice_id` from config, `model_id` = `voice.elevenlabs_model` (`eleven_v3` handles Egyptian
   Arabic and audio tags like `[excited]`), `generations_count: 1`. Price the first call with
   `estimate_only: true`. Never re-call to retry a running generation.
3. Poll `creative_get_flow_run_status` (wait `poll_after_seconds`) until `all_completed`; download
   each result URL with `curl -L` to `out/<date>-<lang>/audio/NN.mp3` (NN = scene number).
   If the download host is blocked by the sandbox proxy, name the host and stop narration.
4. Arabic: write `say` in Egyptian colloquial; add `[excited]` or `[warm]` at the start of the
   hook and CTA lines for energy. Check one clip by ear-proxy (duration sane: 1–15 s).

The Higgsfield sections below apply when `voice.provider` is `higgsfield`, and for lip-sync.

Higgsfield MCP tools (load them with ToolSearch: `generate_audio_batch`, `generate_video`,
`jobs_wait`, `balance`, `media_upload`, `media_confirm`, `create_voice_from_confirmed_audio`,
`list_voices`). Settings live in `reels/config.json` → `higgsfield`.

## Preconditions (check every run)

1. `balance` — credits available. Today's budget is `max_credits_per_day`.
2. Network: the sandbox must reach `upload.higgsfield.ai` (uploads) and the host in each result
   URL (downloads, a `*.cloudfront.net` / `cdn.higgsfield.ai` address). If a download is
   blocked by the proxy, say which host and point Sam to the environment's network settings.
3. (Higgsfield narration only) `higgsfield.voice_id` is set. If it's `null`, the voice hasn't been cloned yet — see below.

If any of these fail, follow the "degrade" rules in `daily-reel` (render without narration).

## One-time: clone Sam's voice

Only with Sam's sample in hand (never commit the sample to git; this repo is public).
Use 1–3 minutes of clean speech, ideally one clip per language.

1. `media_upload` (filename `sam_voice.mp3`) → `curl -X PUT -H "Content-Type: audio/mpeg" --data-binary @file '<upload_url>'` → `media_confirm` (type `audio`).
2. `create_voice_from_confirmed_audio` with `name: "SAM Voice"`.
3. Poll `list_voices` until it shows `status: completed` / `is_audio_eligible: true`.
4. Write the id into `reels/config.json` → `higgsfield.voice_id` and commit.

## Narration with Higgsfield (fallback)

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
