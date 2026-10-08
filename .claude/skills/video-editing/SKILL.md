---
name: video-editing
description: Edit existing video/audio files with ffmpeg — trim, cut, concatenate, resize/reframe (16:9 ↔ 9:16 ↔ 1:1), crop, speed up/slow down, extract or replace audio, normalize loudness, mix music under voice, burn in subtitles, add a logo/watermark or text, fades and crossfades, make GIFs, thumbnails, contact sheets, and compress/convert for YouTube, Instagram, TikTok, or web. Use when the input is real footage the user already has. For designed motion graphics or videos built from scratch use /hyperframes (HTML+GSAP) or /remotion-create (React).
---

# Video editing with ffmpeg

`ffmpeg` and `ffprobe` are installed. Work non-destructively: never overwrite the
source; write to a new file (e.g. `out/<name>-<step>.mp4`).

## 1. Always probe first

```bash
ffprobe -v error -show_entries format=duration,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels -of compact "$IN"
```

Note duration, resolution, fps, whether there is an audio stream, and rotation
metadata. Decisions below depend on it.

## 2. Defaults for output

Unless the user asks otherwise, encode delivery files with:

```
-c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart
```

- `-crf 18` = near-lossless, `23` = smaller. Raise CRF to compress.
- Keep `-pix_fmt yuv420p` so files play everywhere (QuickTime, phones, browsers).
- Use `-c copy` only for lossless cuts on keyframes (fast, but cut points snap to keyframes).

## 3. Recipes

### Trim / cut
```bash
# Frame-accurate (re-encodes): from 00:01:05 for 30s
ffmpeg -ss 00:01:05 -i "$IN" -t 30 <defaults> out.mp4
# Fast, lossless (keyframe-aligned)
ffmpeg -ss 00:01:05 -i "$IN" -t 30 -c copy out.mp4
# Remove a middle section (keep 0–10s and 20s–end)
ffmpeg -i "$IN" -filter_complex \
 "[0:v]trim=0:10,setpts=PTS-STARTPTS[v0];[0:a]atrim=0:10,asetpts=PTS-STARTPTS[a0];\
  [0:v]trim=start=20,setpts=PTS-STARTPTS[v1];[0:a]atrim=start=20,asetpts=PTS-STARTPTS[a1];\
  [v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" <defaults> out.mp4
```

### Concatenate
Same codec/size/fps → concat demuxer (lossless):
```bash
printf "file '%s'\n" clip1.mp4 clip2.mp4 clip3.mp4 > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp4
```
Mixed sources → normalize each input first (`scale`, `fps`, `format`, `aresample`) and use the `concat` filter.

### Crossfade between two clips
```bash
# D = duration of clip1, fade 1s
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
 "[0:v][1:v]xfade=transition=fade:duration=1:offset=$(echo "$D-1"|bc)[v];[0:a][1:a]acrossfade=d=1[a]" \
 -map "[v]" -map "[a]" <defaults> out.mp4
```
Other transitions: `wipeleft`, `slideup`, `circleopen`, `dissolve`, `smoothleft`, `zoomin`.

### Fade in/out
```bash
ffmpeg -i "$IN" -vf "fade=t=in:d=0.5,fade=t=out:st=$(echo "$DUR-0.5"|bc):d=0.5" \
 -af "afade=t=in:d=0.5,afade=t=out:st=$(echo "$DUR-0.5"|bc):d=0.5" <defaults> out.mp4
```

### Resize / reframe for platforms
| Target | Size |
|---|---|
| YouTube / landscape | 1920x1080 |
| Reels / TikTok / Shorts | 1080x1920 |
| Square feed | 1080x1080 |
| Instagram portrait | 1080x1350 |

```bash
# Fit inside with padding (letterbox), no distortion
ffmpeg -i "$IN" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1" <defaults> out.mp4
# Fill and center-crop (landscape → vertical)
ffmpeg -i "$IN" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" <defaults> out.mp4
# Blurred-background vertical (popular for repurposing landscape)
ffmpeg -i "$IN" -filter_complex \
 "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];\
  [0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]" -map "[v]" -map 0:a? <defaults> out.mp4
```

### Speed
```bash
# 2x faster (atempo range is 0.5–2.0; chain for more: atempo=2,atempo=2)
ffmpeg -i "$IN" -filter_complex "[0:v]setpts=PTS/2[v];[0:a]atempo=2[a]" -map "[v]" -map "[a]" <defaults> out.mp4
```

### Audio
```bash
ffmpeg -i "$IN" -vn -c:a libmp3lame -q:a 2 audio.mp3              # extract
ffmpeg -i "$IN" -an -c:v copy silent.mp4                            # remove
ffmpeg -i "$IN" -i new.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest out.mp4   # replace
ffmpeg -i "$IN" -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k out.mp4  # normalize (-14 LUFS for social/YouTube)
# Music bed under voice, ducked automatically
ffmpeg -i "$IN" -i music.mp3 -filter_complex \
 "[1:a]volume=0.25[m];[m][0:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[duck];\
  [0:a][duck]amix=inputs=2:duration=first:dropout_transition=2[a]" -map 0:v -map "[a]" -c:v copy -c:a aac out.mp4
```

### Text, logos, subtitles
```bash
# Burn in SRT subtitles
ffmpeg -i "$IN" -vf "subtitles=subs.srt:force_style='FontName=Inter,FontSize=18,Outline=2,MarginV=40'" <defaults> out.mp4
# Soft subtitles (toggleable, no re-encode)
ffmpeg -i "$IN" -i subs.srt -c copy -c:s mov_text out.mp4
# Logo watermark, bottom-right, 40px margin, 15% of video width
ffmpeg -i "$IN" -i logo.png -filter_complex "[1][0]scale2ref=w=iw*0.15:h=ow/mdar[lg][v];[v][lg]overlay=W-w-40:H-h-40" <defaults> out.mp4
# Simple text title for the first 3s
ffmpeg -i "$IN" -vf "drawtext=text='Hello':fontcolor=white:fontsize=72:x=(w-tw)/2:y=(h-th)/2:enable='lt(t,3)':box=1:boxcolor=black@0.4:boxborderw=20" <defaults> out.mp4
```
Need styled/animated captions or kinetic text? Use `/embedded-captions` or `/remotion-captions` instead of drawtext.
Need a transcript/SRT first? See `/embedded-captions` (transcription) or `/remotion-captions`.

### Stills, GIFs, previews
```bash
ffmpeg -ss 5 -i "$IN" -frames:v 1 -q:v 2 thumb.jpg                       # thumbnail at 5s
ffmpeg -i "$IN" -vf "fps=1/10,scale=320:-1,tile=4x4" -frames:v 1 sheet.jpg  # contact sheet
# High-quality GIF (palette)
ffmpeg -ss 2 -t 4 -i "$IN" -vf "fps=15,scale=600:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" out.gif
# Image sequence → video
ffmpeg -framerate 30 -i frames/%04d.png <defaults> out.mp4
```

### Color and stabilization
```bash
ffmpeg -i "$IN" -vf "eq=contrast=1.08:saturation=1.15:brightness=0.02" <defaults> out.mp4
ffmpeg -i "$IN" -vf "lut3d=look.cube" <defaults> out.mp4
# Stabilize (deshake is built in; vidstab if available: ffmpeg -filters | grep vidstab)
ffmpeg -i "$IN" -vf deshake <defaults> out.mp4
```

### Compress to a target size
```bash
# target ~ 25 MB: video kbps = (25*8192 / duration_s) - 128
ffmpeg -y -i "$IN" -c:v libx264 -b:v ${KBPS}k -pass 1 -an -f null /dev/null && \
ffmpeg -i "$IN" -c:v libx264 -b:v ${KBPS}k -pass 2 -c:a aac -b:a 128k -movflags +faststart out.mp4
```

## 4. Verify before handing back

1. `ffprobe` the output: duration, resolution, audio present as expected.
2. Grab 3–4 frames (`-ss` at start/middle/end) and look at them with the Read tool to check framing, text, and overlays.
3. Report output path, duration, size (`du -h`), and what changed.

## 5. Choosing the right tool

| The ask | Use |
|---|---|
| Edit footage the user has (cut, join, resize, audio, subs) | this skill |
| Animated captions on a talking-head clip | `/embedded-captions`, `/talking-head-recut` |
| Motion graphics, kinetic type, logo sting, lower thirds | `/motion-graphics` (HyperFrames) |
| Explainer / promo / product launch video from a brief or URL | `/faceless-explainer`, `/product-launch-video`, `/general-video` |
| Beat-synced video from music | `/music-to-video` |
| Programmatic/data-driven video in React | `/remotion-create`, `/remotion-best-practices` |
