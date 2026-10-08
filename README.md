# SAMs-

Claude Code skills for WhatsApp (WhatsApp Business Cloud API) and for video editing,
motion graphics and video creation.

## WhatsApp

| Skill | What it does |
|-------|--------------|
| `whatsapp-send` | Send text, templates, media and buttons; mark messages read; check the sender number's health |
| `whatsapp-templates` | Create, list and delete message templates; draft copy that passes Meta review |
| `whatsapp-webhook` | Receive inbound messages and delivery/read statuses |

Skills live in `.claude/skills/` and load automatically when Claude Code runs in this repo.
They call `scripts/whatsapp.py` and `scripts/whatsapp_webhook.py`, which need only
Python 3.8+ (no packages to install).

## Setup

1. In [Meta for Developers](https://developers.facebook.com/apps), create a **Business** app
   and add the **WhatsApp** product.
2. Under WhatsApp > API Setup, note the **Phone number ID** and **WhatsApp Business Account ID**.
   The test number works right away for up to 5 recipient numbers you add there.
3. Create a permanent token: Business Settings > Users > System users > add one, assign the
   app and WhatsApp account, and generate a token with `whatsapp_business_messaging` and
   `whatsapp_business_management`.
4. `cp .env.example .env` and fill in the values. `.env` is git-ignored.
5. Check it works:

   ```bash
   python3 scripts/whatsapp.py phone-info
   python3 scripts/whatsapp.py send-template <your_number> hello_world --lang en_US
   ```

6. To receive replies, follow the `whatsapp-webhook` skill's setup steps.

Then ask Claude things like "send the order_shipped template to 2010…", "make a booking
reminder template in Arabic and English", or "did my last message get read?".

## CLI reference

```
python3 scripts/whatsapp.py --help
python3 scripts/whatsapp.py <command> --help
```

## Video editing, motion graphics and video creation

| Skill | What it does |
|-------|--------------|
| `video-editing` | Edit existing footage with ffmpeg: trim, join, crossfade, reframe for 9:16/1:1, speed, audio cleanup and music ducking, subtitles, logos, GIFs, compression |
| `hyperframes` | Entry point for HTML + GSAP video (HeyGen HyperFrames); routes to the skills below |
| `motion-graphics` | Kinetic type, stat count-ups, logo stings, lower thirds, animated maps and charts |
| `general-video`, `faceless-explainer` | Narrated, multi-scene explainers from a brief or script |
| `product-launch-video` | Promo / launch videos from a product URL or brief |
| `music-to-video` | Beat-synced lyric videos, slideshows and promos from a music track |
| `embedded-captions`, `talking-head-recut` | Styled animated captions and overlay graphics on talking-head video |
| `slideshow`, `pr-to-video` | Interactive decks; code-change explainer videos from a GitHub PR |
| `hyperframes-*`, `media-use` | Core authoring, animation, audio/TTS, CLI preview and render, asset handling |
| `remotion-*` | Programmatic video in React with Remotion: create, captions, maps, render, studio |

The HyperFrames and Remotion skills come from their official repos
([heygen-com/hyperframes](https://github.com/heygen-com/hyperframes),
[remotion-dev/skills](https://github.com/remotion-dev/skills)) and are pinned in
`skills-lock.json`. Update them with `npx skills update -p`.

Requirements: `ffmpeg` and Node.js 22+ (both pre-installed in Claude Code cloud sessions).
Rendering runs through `npx hyperframes` or `npx remotion`, which fetch their packages on first use.

Ask Claude things like "cut the first 12 seconds and make a 9:16 version for Reels",
"make a 10-second logo sting for SAMs", "turn this track into a lyric video", or
"add animated captions to interview.mp4".
