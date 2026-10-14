# SAMs-

Claude Code skills for **daily AI-tips reels** (research → script → cloned voice → motion
graphics → multi-platform publishing) and for **WhatsApp** (WhatsApp Business Cloud API).

## Daily reels

Plan and setup checklist: [`docs/reel-automation-plan.md`](docs/reel-automation-plan.md).

| Skill | What it does |
|-------|--------------|
| `daily-reel` | Runs the whole pipeline for today's reel, in English and Egyptian Arabic |
| `reel-research` | Finds a fresh, verified AI tool tip for the day's content pillar |
| `reel-script` | Writes both language specs plus captions, titles and hashtags |
| `reel-voice` | Cloned-voice narration and lip-synced presenter clips (Higgsfield) |
| `reel-render` | Renders the spec with `reels/engine` and runs visual QA |
| `reel-publish` | Hosts the MP4s and schedules them on every network (Metricool) |
| `reel-analytics` | Weekly review that rewrites the content mix in `reels/learnings.md` |

Try the engine: `python3 reels/engine/render.py reels/specs/sample-en.json out/sample`
(see [`reels/engine/README.md`](reels/engine/README.md)).

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
