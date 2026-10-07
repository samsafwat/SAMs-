#!/usr/bin/env python3
"""Small CLI for the WhatsApp Business Cloud API (Meta Graph API).

Standard library only. Configuration comes from environment variables
(optionally loaded from a .env file in the repo root):

  WHATSAPP_TOKEN            System-user or temporary access token (required)
  WHATSAPP_PHONE_NUMBER_ID  Sender phone number ID (required for messaging/media)
  WHATSAPP_WABA_ID          WhatsApp Business Account ID (required for templates)
  WHATSAPP_API_VERSION      Graph API version, default v23.0

Examples:
  scripts/whatsapp.py send-text 201001234567 "Hello from SAMs"
  scripts/whatsapp.py send-template 201001234567 hello_world --lang en_US
  scripts/whatsapp.py send-media 201001234567 image --link https://example.com/a.jpg --caption "Hi"
  scripts/whatsapp.py upload-media ./brochure.pdf
  scripts/whatsapp.py list-templates
  scripts/whatsapp.py create-template order_update UTILITY en_US "Your order {{1}} has shipped." --example 12345
  scripts/whatsapp.py mark-read wamid.HBgM...
  scripts/whatsapp.py phone-info
"""

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path=REPO_ROOT / ".env"):
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env(name, required=True, default=None):
    value = os.environ.get(name, default)
    if required and not value:
        sys.exit(f"error: {name} is not set (see .env.example)")
    return value


def base_url():
    return f"https://graph.facebook.com/{env('WHATSAPP_API_VERSION', default='v23.0')}"


def request(method, path, payload=None, query=None, body=None, content_type=None):
    url = f"{base_url()}/{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    headers = {"Authorization": f"Bearer {env('WHATSAPP_TOKEN')}"}
    data = body
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    elif content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit(f"error: HTTP {e.code} from {method} {path}\n{detail}")


def normalize_number(number):
    # The API wants digits only, including country code, no '+' or spaces.
    return "".join(ch for ch in number if ch.isdigit())


def send_message(to, msg_type, content, reply_to=None):
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": normalize_number(to),
        "type": msg_type,
        msg_type: content,
    }
    if reply_to:
        payload["context"] = {"message_id": reply_to}
    return request("POST", f"{env('WHATSAPP_PHONE_NUMBER_ID')}/messages", payload)


def cmd_send_text(args):
    return send_message(
        args.to, "text", {"body": args.body, "preview_url": args.preview_url}, args.reply_to
    )


def cmd_send_template(args):
    template = {"name": args.name, "language": {"code": args.lang}}
    if args.param:
        template["components"] = [
            {"type": "body", "parameters": [{"type": "text", "text": p} for p in args.param]}
        ]
    if args.components:
        template["components"] = json.loads(args.components)
    return send_message(args.to, "template", template)


def cmd_send_media(args):
    if bool(args.link) == bool(args.id):
        sys.exit("error: pass exactly one of --link or --id")
    media = {"link": args.link} if args.link else {"id": args.id}
    if args.caption and args.type in ("image", "video", "document"):
        media["caption"] = args.caption
    if args.filename and args.type == "document":
        media["filename"] = args.filename
    return send_message(args.to, args.type, media, args.reply_to)


def cmd_send_buttons(args):
    if not 1 <= len(args.button) <= 3:
        sys.exit("error: reply buttons need 1-3 --button values")
    interactive = {
        "type": "button",
        "body": {"text": args.body},
        "action": {
            "buttons": [
                {"type": "reply", "reply": {"id": f"btn_{i}", "title": title[:20]}}
                for i, title in enumerate(args.button, 1)
            ]
        },
    }
    return send_message(args.to, "interactive", interactive)


def cmd_mark_read(args):
    payload = {"messaging_product": "whatsapp", "status": "read", "message_id": args.message_id}
    return request("POST", f"{env('WHATSAPP_PHONE_NUMBER_ID')}/messages", payload)


def cmd_upload_media(args):
    path = Path(args.file)
    mime = args.mime or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    boundary = uuid.uuid4().hex
    parts = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="messaging_product"\r\n\r\nwhatsapp\r\n'.encode(),
        f'--{boundary}\r\nContent-Disposition: form-data; name="type"\r\n\r\n{mime}\r\n'.encode(),
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode()
        + path.read_bytes()
        + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return request(
        "POST",
        f"{env('WHATSAPP_PHONE_NUMBER_ID')}/media",
        body=b"".join(parts),
        content_type=f"multipart/form-data; boundary={boundary}",
    )


def cmd_get_media(args):
    return request("GET", args.media_id)


def cmd_list_templates(args):
    query = {"limit": args.limit, "fields": "name,status,category,language,components"}
    if args.status:
        query["status"] = args.status
    return request("GET", f"{env('WHATSAPP_WABA_ID')}/message_templates", query=query)


def cmd_create_template(args):
    body = {"type": "BODY", "text": args.body}
    if args.example:
        body["example"] = {"body_text": [args.example]}
    components = [body]
    if args.header:
        components.insert(0, {"type": "HEADER", "format": "TEXT", "text": args.header})
    if args.footer:
        components.append({"type": "FOOTER", "text": args.footer})
    payload = {
        "name": args.name,
        "category": args.category,
        "language": args.lang,
        "components": components,
    }
    return request("POST", f"{env('WHATSAPP_WABA_ID')}/message_templates", payload)


def cmd_delete_template(args):
    return request(
        "DELETE", f"{env('WHATSAPP_WABA_ID')}/message_templates", query={"name": args.name}
    )


def cmd_phone_info(args):
    fields = "display_phone_number,verified_name,quality_rating,code_verification_status,messaging_limit_tier"
    return request("GET", env("WHATSAPP_PHONE_NUMBER_ID"), query={"fields": fields})


def build_parser():
    p = argparse.ArgumentParser(description="WhatsApp Business Cloud API helper")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("send-text", help="send a free-form text (24h service window only)")
    s.add_argument("to")
    s.add_argument("body")
    s.add_argument("--preview-url", action="store_true")
    s.add_argument("--reply-to", help="wamid of the message to quote")
    s.set_defaults(func=cmd_send_text)

    s = sub.add_parser("send-template", help="send an approved template message")
    s.add_argument("to")
    s.add_argument("name")
    s.add_argument("--lang", default="en_US")
    s.add_argument("--param", action="append", help="body {{n}} value, repeat in order")
    s.add_argument("--components", help="raw components JSON (overrides --param)")
    s.set_defaults(func=cmd_send_template)

    s = sub.add_parser("send-media", help="send image/video/audio/document/sticker")
    s.add_argument("to")
    s.add_argument("type", choices=["image", "video", "audio", "document", "sticker"])
    s.add_argument("--link")
    s.add_argument("--id", help="media ID from upload-media")
    s.add_argument("--caption")
    s.add_argument("--filename")
    s.add_argument("--reply-to")
    s.set_defaults(func=cmd_send_media)

    s = sub.add_parser("send-buttons", help="send up to 3 quick-reply buttons")
    s.add_argument("to")
    s.add_argument("body")
    s.add_argument("--button", action="append", default=[])
    s.set_defaults(func=cmd_send_buttons)

    s = sub.add_parser("mark-read", help="mark an inbound message as read")
    s.add_argument("message_id")
    s.set_defaults(func=cmd_mark_read)

    s = sub.add_parser("upload-media", help="upload a file, returns a media ID")
    s.add_argument("file")
    s.add_argument("--mime")
    s.set_defaults(func=cmd_upload_media)

    s = sub.add_parser("get-media", help="get the download URL for a media ID")
    s.add_argument("media_id")
    s.set_defaults(func=cmd_get_media)

    s = sub.add_parser("list-templates")
    s.add_argument("--status", choices=["APPROVED", "PENDING", "REJECTED", "PAUSED", "DISABLED"])
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_list_templates)

    s = sub.add_parser("create-template", help="submit a text template for review")
    s.add_argument("name", help="lowercase letters, digits and underscores")
    s.add_argument("category", choices=["UTILITY", "MARKETING", "AUTHENTICATION"])
    s.add_argument("lang", help="e.g. en_US, ar")
    s.add_argument("body", help="body text, variables as {{1}}, {{2}}...")
    s.add_argument("--example", action="append", help="sample value per variable, in order")
    s.add_argument("--header")
    s.add_argument("--footer")
    s.set_defaults(func=cmd_create_template)

    s = sub.add_parser("delete-template")
    s.add_argument("name")
    s.set_defaults(func=cmd_delete_template)

    s = sub.add_parser("phone-info", help="show sender number status and quality")
    s.set_defaults(func=cmd_phone_info)
    return p


def main():
    load_dotenv()
    args = build_parser().parse_args()
    print(json.dumps(args.func(args), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
