---
name: whatsapp-templates
description: Create, list, check approval status of, and delete WhatsApp Business message templates (utility, marketing, authentication), and draft template copy that passes Meta review. Use when the user wants a new WhatsApp template, asks why a template was rejected, or needs to know which templates are approved.
---

# WhatsApp: message templates

Templates are the only way to start a conversation or message someone outside the 24-hour
window. They're owned by the WhatsApp Business Account, so these commands need
`WHATSAPP_WABA_ID` and `WHATSAPP_TOKEN` (env or `.env`).

## Commands

```bash
python3 scripts/whatsapp.py list-templates                    # all
python3 scripts/whatsapp.py list-templates --status APPROVED
python3 scripts/whatsapp.py list-templates --status REJECTED   # see rejected_reason

python3 scripts/whatsapp.py create-template order_shipped UTILITY en_US \
  "Hi {{1}}, your order {{2}} has shipped and should arrive by {{3}}." \
  --example Sam --example 10482 --example "Oct 12" \
  --header "Order update" --footer "Reply STOP to opt out"

python3 scripts/whatsapp.py delete-template order_shipped     # deletes all languages
```

`create-template` covers text header/body/footer. For image/video/document headers,
buttons (quick reply, URL, phone, copy code) or authentication OTP templates, build the
`components` JSON per Meta's template docs and POST it with a short Python snippet that
imports `request` from `scripts/whatsapp.py`, or create it in WhatsApp Manager.

New templates start `PENDING`; review usually takes minutes, sometimes up to 24h. Re-run
`list-templates` to check. Only `APPROVED` templates can be sent.

## Drafting templates that get approved

1. **Name**: lowercase, digits, underscores only (`booking_reminder_v2`). Names can't be reused
   for ~30 days after deletion, so version them.
2. **Category** — choose honestly; Meta re-categorizes misfiled ones:
   - `UTILITY`: tied to an existing transaction or request (order, booking, account alert).
   - `MARKETING`: promotions, offers, newsletters, re-engagement — anything else.
   - `AUTHENTICATION`: one-time passcodes only, using Meta's fixed OTP format.
3. **Variables** `{{1}}, {{2}}…` must be sequential, can't sit at the very start or end of the
   body, can't be adjacent (`{{1}} {{2}}`), and each needs an `--example` value.
4. Keep a reasonable ratio of fixed text to variables. A body that is mostly `{{n}}` gets rejected.
5. No misleading content, no threats, no asking for full card numbers or passwords.
6. One template per language: same `name`, different `lang` (e.g. `en_US` and `ar`).
   Arabic and other RTL text works as-is.
7. Marketing templates: give the recipient a way to opt out (footer or quick-reply button).

Before submitting, show the user the final name, category, language, body and examples
and get a go-ahead. Templates go to Meta for review.

## Rejection reasons → fixes

| Reason | Fix |
|--------|-----|
| `INVALID_FORMAT` | Variable placement or formatting; check rule 3 |
| `TAG_CONTENT_MISMATCH` | Category doesn't match the content; usually utility → marketing |
| `PROMOTIONAL` | Utility template contains promo language; remove it or use MARKETING |
| `ABUSIVE_CONTENT` / `SCAM` | Rewrite; avoid urgency/threat phrasing and shortened links |
| `INCORRECT_CATEGORY` | Resubmit under the suggested category |
