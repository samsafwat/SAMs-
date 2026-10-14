---
name: reel-research
description: Find and verify today's AI tool tip for the SAM reel — rotating content pillars, checking it hasn't been covered, and confirming every claim on an official source. Use when picking a topic for a reel or building a backlog of reel ideas.
---

# Reel research: today's tip

Goal: one tip that is **useful tonight, true today, and not yet on the channel**.

## 1. Pick the pillar

Weekday → pillar table in `reels/strategy.md`. If `reels/learnings.md` says a pillar is
under-performing, still keep it in rotation but pick its strongest angle.

## 2. Gather candidates (5–8)

Search the web (WebSearch; WebFetch for the page itself) with the pillar in mind. Good sources,
in order of trust:

1. Official changelogs, release notes, help-center pages and blogs of the tool (OpenAI, Anthropic,
   Google, Microsoft, Meta, Adobe, Canva, Notion, Perplexity, ElevenLabs, Runway, Higgsfield…).
2. The tool's own docs/pricing pages (for "free" and limits claims).
3. Hacker News / Product Hunt / reputable tech press — only to *find* things; confirm on (1)/(2).

Skip: rumours, leaks, paid-only features presented as free, anything region-locked away from
Egypt unless the reel says so, and tools that need a credit card to try.

## 3. Deduplicate

Read `reels/history.jsonl`. Reject a candidate if the same tool **and** the same feature appeared
in the last 60 days. Same tool, different feature is fine after 14 days.

## 4. Score and choose

Score 1–5 each and pick the highest total:

- **Try-tonight**: can a non-technical viewer do it in under 2 minutes?
- **Surprise**: would most people say "I didn't know that"?
- **Payoff**: does it save real time or money, with a concrete number you can state?
- **Visual**: can the steps be shown as 3 short on-screen steps?
- **Bilingual**: does it work for an Arabic-speaking audience too?

## 5. Verify

For the chosen tip, open the official page and confirm: the feature exists now, the exact UI
labels (button names), whether it's free/paid, and any number you'll say. Keep the URLs.
If you can't confirm something, drop that claim.

## Output

Hand to `reel-script`:

```json
{"pillar":"free-tool","tool":"NotebookLM","feature":"Audio Overviews","why":"turns PDFs into a 2-host podcast",
 "steps":["Create a notebook","Add sources","Audio Overview → Generate"],
 "pro_tricks":["Customize focus","Interactive mode: ask the hosts"],
 "facts":[{"claim":"free with a Google account","source":"https://…"}],
 "url":"notebooklm.google.com","sources":["https://…"]}
```

When asked for a backlog, produce 14 of these (two weeks, following the pillar rotation) and
save them to `reels/backlog.json`; the daily run takes from the backlog first if an entry is
still verified true.
