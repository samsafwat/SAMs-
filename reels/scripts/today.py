# -*- coding: utf-8 -*-
"""Pick today's calendar entry and write it to reels/work/day-NNN.json.

Usage: python3 reels/scripts/today.py [--date YYYY-MM-DD] [--day N]
Prints the entry path, the day number and whether a live trend refresh is needed.
Also warns if the hook was already used in the last 60 published days.
"""
import argparse
import datetime as dt
import json
import os
import zoneinfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRAND = json.load(open(os.path.join(ROOT, "brand.json"), encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--day", type=int)
    a = ap.parse_args()
    cal = json.load(open(os.path.join(ROOT, "calendar", "calendar_365.json"), encoding="utf-8"))
    if a.day:
        entry = cal[a.day - 1]
    else:
        today = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(zoneinfo.ZoneInfo(BRAND["timezone"])).date()
        idx = (today - dt.date.fromisoformat(BRAND["start_date"])).days
        if not 0 <= idx < len(cal):
            raise SystemExit(f"{today} is outside the calendar ({cal[0]['date']} .. {cal[-1]['date']})")
        entry = cal[idx]

    log_path = os.path.join(ROOT, "publish_log.jsonl")
    recent = []
    if os.path.exists(log_path):
        recent = [json.loads(line) for line in open(log_path, encoding="utf-8") if line.strip()][-60:]
    if any(r.get("hook_ar") == entry["hook_ar"] for r in recent):
        print("WARNING: hook used in the last 60 days, rewrite it")

    work = os.path.join(ROOT, "work")
    os.makedirs(work, exist_ok=True)
    path = os.path.join(work, f"day-{entry['day']:03d}.json")
    if not os.path.exists(path):  # keep any edits already made today
        json.dump(entry, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"entry": path, "day": entry["day"], "date": entry["date"], "pillar": entry["pillar"],
                      "tool": entry["tool"], "needs_live_trend": entry["needs_live_trend"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
