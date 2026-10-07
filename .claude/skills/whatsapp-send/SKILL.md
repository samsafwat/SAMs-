---
name: whatsapp-send
description: Send WhatsApp messages through the WhatsApp Business Cloud API — text, approved templates, images/video/audio/documents, quick-reply buttons, read receipts, and checking the sender number's status. Use when the user asks to send, message, notify, or reply to someone on WhatsApp, or to check the WhatsApp number's quality or limits.
---

# WhatsApp: send messages

All calls go through `scripts/whatsapp.py` (stdlib Python, no install needed). It reads
`WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` (and optionally `WHATSAPP_API_VERSION`) from the
environment or from `.env` at the repo root. If a variable is missing the script says so —
point the user to `.env.example`; never ask them to paste the token into chat.

## Pick the right message type

WhatsApp only allows **free-form** messages (text, media, buttons) inside the 24-hour
customer service window that opens when the recipient last messaged the business.
Outside that window, or for the first contact, you **must** send an approved **template**.
If a free-form send fails with error `131047` ("Re-engagement message"), switch to a template.

## Commands

Phone numbers: international format, digits only is fine (`201001234567`); the script strips
`+`, spaces and dashes.

```bash
# Text (inside 24h window)
python3 scripts/whatsapp.py send-text 201001234567 "Your table is ready"
python3 scripts/whatsapp.py send-text 201001234567 "See https://example.com" --preview-url
python3 scripts/whatsapp.py send-text 201001234567 "Yes, confirmed" --reply-to wamid.XXXX

# Template (any time) — --param fills body {{1}}, {{2}}, ... in order
python3 scripts/whatsapp.py send-template 201001234567 hello_world --lang en_US
python3 scripts/whatsapp.py send-template 201001234567 order_update --lang en_US --param 12345
# Header/button variables: pass the full components array
python3 scripts/whatsapp.py send-template 201001234567 promo --lang ar \
  --components '[{"type":"header","parameters":[{"type":"image","image":{"link":"https://..."}}]},{"type":"body","parameters":[{"type":"text","text":"Sam"}]}]'

# Media: by public URL or by media ID from upload-media
python3 scripts/whatsapp.py send-media 201001234567 image --link https://example.com/menu.jpg --caption "Menu"
python3 scripts/whatsapp.py upload-media ./invoice.pdf          # -> {"id": "..."}
python3 scripts/whatsapp.py send-media 201001234567 document --id <MEDIA_ID> --filename invoice.pdf

# Quick-reply buttons (1–3, titles ≤ 20 chars)
python3 scripts/whatsapp.py send-buttons 201001234567 "Confirm your booking?" --button Yes --button No

# Mark an inbound message read (shows blue ticks)
python3 scripts/whatsapp.py mark-read wamid.XXXX

# Sender number health: quality rating, messaging tier, verified name
python3 scripts/whatsapp.py phone-info
```

A successful send returns `{"messages":[{"id":"wamid..."}]}`. That only means *accepted*;
delivery/read/failed arrive later as webhook status events (see the `whatsapp-webhook` skill).

## Rules

- Confirm the recipient and the exact text with the user before sending — a sent message
  can't be recalled. For bulk sends, show the recipient list and count first.
- Only message people who opted in. Marketing templates to people who didn't can get the
  number's quality rating lowered or the number restricted.
- Media limits: image 5 MB (jpeg/png), video 16 MB (mp4/3gp), audio 16 MB, document 100 MB,
  sticker webp. `--link` URLs must be public HTTPS.

## Common errors

| Code | Meaning | Fix |
|------|---------|-----|
| 190 | Token expired/invalid | Regenerate; use a permanent system-user token |
| 131030 | Recipient not in allowed list | Test numbers only: add it under API Setup > "To" |
| 131047 | Outside 24h window | Send a template instead |
| 132001 | Template doesn't exist for that language | Check `list-templates`; match `--lang` |
| 132000 | Wrong number of template params | Match `--param` count to `{{n}}` count |
| 131026 | Recipient can't receive (not on WhatsApp, old app) | Use another channel |
| 130429 / 131056 | Rate limit / pair rate limit | Back off and retry later |
