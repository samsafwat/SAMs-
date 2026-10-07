---
name: whatsapp-webhook
description: Set up, run, and debug a webhook that receives inbound WhatsApp messages and delivery/read status updates from the WhatsApp Business Cloud API, and read the logged events. Use when the user wants to receive or read WhatsApp replies, see whether a message was delivered or read, or connect the Meta app's webhook.
---

# WhatsApp: receive messages and statuses

Meta pushes inbound messages and status updates (`sent`, `delivered`, `read`, `failed`)
to an HTTPS webhook. `scripts/whatsapp_webhook.py` is a small stdlib receiver:

- `GET /webhook` does the verification handshake using `WHATSAPP_VERIFY_TOKEN`.
- `POST /webhook` checks `X-Hub-Signature-256` with `WHATSAPP_APP_SECRET`, prints one JSON
  line per event and appends it to `webhook_events.jsonl` (git-ignored).

## Setup (one time)

1. In `.env`, set `WHATSAPP_VERIFY_TOKEN` to a random string (e.g. `openssl rand -hex 16`)
   and `WHATSAPP_APP_SECRET` from App settings > Basic.
2. Start the receiver: `python3 scripts/whatsapp_webhook.py --port 8080`
3. Expose it over public HTTPS, for example:
   `cloudflared tunnel --url http://localhost:8080` or `ngrok http 8080`.
4. Meta for Developers > your app > WhatsApp > Configuration > Webhook > Edit:
   callback URL `https://<public-host>/webhook`, verify token = the same string. Save.
5. Under Webhook fields, **subscribe to `messages`** (that field carries both inbound
   messages and statuses).
6. Test: send a WhatsApp message to the business number; a line with `"event": "message"`
   should appear.

For production, run it on a host with a stable HTTPS URL (any VPS/container behind a TLS
proxy) instead of a tunnel, and keep `WHATSAPP_APP_SECRET` set so forged requests get 401.

## Reading events

```bash
tail -n 20 webhook_events.jsonl
# Replies from one number
grep '"from": "201001234567"' webhook_events.jsonl
# What happened to a message sent earlier
grep 'wamid.XXXX' webhook_events.jsonl
# Failures with error details
grep '"status": "failed"' webhook_events.jsonl
```

Event shapes:

```json
{"event":"message","from":"2010...","name":"Sam","id":"wamid...","type":"text","text":"Hi","media_id":null,"timestamp":"..."}
{"event":"status","id":"wamid...","recipient":"2010...","status":"delivered","errors":null,"timestamp":"..."}
```

For `image`/`document`/`audio` messages, `media_id` is set. Fetch it with
`python3 scripts/whatsapp.py get-media <media_id>`. That returns a short-lived `url`, which
must be downloaded with the same bearer token:
`curl -H "Authorization: Bearer $WHATSAPP_TOKEN" -o file "<url>"`.
Button replies show the button title in `text`.

An inbound message opens the 24-hour window, so replying with `whatsapp-send` free-form
text works right after. Use `mark-read` with the message `id` to show blue ticks.

## Troubleshooting

- **Verification fails in the dashboard**: receiver not reachable over HTTPS, wrong path
  (must end `/webhook`), or verify token mismatch. Check with
  `curl "https://<host>/webhook?hub.mode=subscribe&hub.verify_token=<token>&hub.challenge=ok"`,
  which should print `ok`.
- **Verified but no events**: `messages` field not subscribed, or the app is in dev mode
  and the sender isn't an added tester.
- **401s in tunnel logs**: `WHATSAPP_APP_SECRET` is wrong (it's the *app* secret, not the token).
- **Duplicate events**: Meta retries when it doesn't get a fast 200. The receiver replies
  before processing, but downstream code should still dedupe on `id`.
