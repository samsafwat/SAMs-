---
name: reel-analytics
description: Weekly performance review of SAM reels from Metricool — views, retention, saves, shares and follows per pillar, hook style and language — written up as concrete changes to the content mix in reels/learnings.md. Use when asked how the reels are doing, for the weekly review, or before planning next week's topics.
---

# Reel analytics: learn weekly

Metricool tools (ToolSearch): `getAnalyticsAvailableMetrics`, `getAnalyticsDataByMetrics`,
`getScheduledPosts`, `getBrandSettings`. Join results to `reels/history.jsonl` by date and
network to know each reel's pillar, hook and language.

## Pull (last 7 days, plus the 4 weeks before for comparison)

Per reel and network: views/plays, average watch time or retention (if the network reports it),
likes, comments, **saves**, **shares**, follows gained. Ask `getAnalyticsAvailableMetrics` first
for the exact metric names per network; don't guess them.

## Read it

Rank reels by **shares + saves per 1,000 views** (what the algorithms reward for educational
content) and separately by follows gained. Then compare by: pillar, hook formula, presenter vs
no presenter, language, posting hour, length.

Only call something a pattern if it shows up in at least 3 reels. With fewer than 2 weeks of
data, report numbers and say it's too early for conclusions.

## Write `reels/learnings.md`

Append a dated section (newest first):

```markdown
## Week of 2026-10-19
- Top reel: … (why we think it worked)
- Keep: … / Stop: … / Try next week: … (max 3 each, specific)
- Pillar mix change: e.g. "Workflow Tues → twice a week; Mindset Fri → every other week"
```

`reel-script` and `reel-research` read this file, so phrase each point as an instruction.

## Report to Sam

Five lines: total views and follows this week vs last, the top reel and the weakest one, and the
three changes for next week. Offer to show the full table.
