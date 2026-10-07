#!/usr/bin/env python3
"""Minimal WhatsApp Cloud API webhook receiver (standard library only).

  GET  /webhook  answers Meta's verification handshake using WHATSAPP_VERIFY_TOKEN.
  POST /webhook  checks X-Hub-Signature-256 against WHATSAPP_APP_SECRET (if set),
                 prints each inbound message / status update as one JSON line,
                 and appends it to webhook_events.jsonl.

Run:   scripts/whatsapp_webhook.py --port 8080
Expose it publicly (e.g. `cloudflared tunnel --url http://localhost:8080` or ngrok)
and register https://<host>/webhook in the Meta app dashboard.
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from whatsapp import REPO_ROOT, load_dotenv  # noqa: E402

LOG_FILE = REPO_ROOT / "webhook_events.jsonl"
MEDIA_TYPES = {"image", "video", "audio", "document", "sticker"}


def summarize(payload):
    """Flatten a webhook payload into simple message/status events."""
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            names = {c["wa_id"]: c.get("profile", {}).get("name") for c in value.get("contacts", [])}
            for msg in value.get("messages", []):
                kind = msg.get("type")
                content = msg.get(kind, {})
                if kind == "interactive":
                    content = content.get(content.get("type"), content)
                yield {
                    "event": "message",
                    "from": msg.get("from"),
                    "name": names.get(msg.get("from")),
                    "id": msg.get("id"),
                    "type": kind,
                    "text": content.get("body") or content.get("title") or content.get("caption"),
                    "media_id": content.get("id") if kind in MEDIA_TYPES else None,
                    "timestamp": msg.get("timestamp"),
                }
            for status in value.get("statuses", []):
                yield {
                    "event": "status",
                    "id": status.get("id"),
                    "recipient": status.get("recipient_id"),
                    "status": status.get("status"),
                    "errors": status.get("errors"),
                    "timestamp": status.get("timestamp"),
                }


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, body=b""):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        expected = os.environ.get("WHATSAPP_VERIFY_TOKEN")
        if (
            url.path == "/webhook"
            and q.get("hub.mode") == "subscribe"
            and expected
            and hmac.compare_digest(q.get("hub.verify_token", ""), expected)
        ):
            self._reply(200, q.get("hub.challenge", "").encode())
        else:
            self._reply(403)

    def do_POST(self):
        if urlparse(self.path).path != "/webhook":
            return self._reply(404)
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        secret = os.environ.get("WHATSAPP_APP_SECRET")
        if secret:
            sig = "sha256=" + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, self.headers.get("X-Hub-Signature-256", "")):
                return self._reply(401)
        # Acknowledge fast; Meta retries anything that isn't a quick 200.
        self._reply(200)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return
        with LOG_FILE.open("a") as log:
            for event in summarize(payload):
                line = json.dumps(event, ensure_ascii=False)
                print(line, flush=True)
                log.write(line + "\n")

    def log_message(self, *args):
        pass


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8080)))
    args = parser.parse_args()
    if not os.environ.get("WHATSAPP_VERIFY_TOKEN"):
        sys.exit("error: WHATSAPP_VERIFY_TOKEN is not set (see .env.example)")
    if not os.environ.get("WHATSAPP_APP_SECRET"):
        print("warning: WHATSAPP_APP_SECRET not set, signatures are NOT verified", file=sys.stderr)
    print(f"listening on :{args.port}/webhook", file=sys.stderr)
    HTTPServer(("", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
