# -*- coding: utf-8 -*-
"""Build Sam's 365-day reel calendar from 52 weekly themes x 7 daily formats.

Usage: python3 reels/content/build_calendar.py
Writes reels/calendar/calendar_365.json, calendar_365.csv and CALENDAR.md.
"""
import csv
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from themes import THEMES  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRAND = json.load(open(os.path.join(ROOT, "brand.json"), encoding="utf-8"))

PILLARS = [
    ("tool_demo", "أداة اليوم", "Tool of the Day"),
    ("prompt_recipe", "وصفة Prompt", "Prompt Recipe"),
    ("myth_fact", "خرافة ولا حقيقة؟", "Myth vs Fact"),
    ("use_case", "التحول الرقمي في الواقع", "Transformation Case"),
    ("trend_watch", "رادار الـ AI", "AI Trend Radar"),
    ("concept_30s", "مفهوم في 30 ثانية", "AI Concept in 30s"),
    ("leader_mindset", "عقلية القائد", "Leader Mindset"),
]

# Hook formulas for the first 3 seconds: curiosity gap, bold claim, pattern break.
HOOKS = {
    "prompt_recipe": [
        "احفظ الـ Prompt ده لـ {tool}… هيوفّرلك ساعات",
        "انسخ الـ Prompt ده والصقه في {tool} حالًا",
        "الـ Prompt ده بيخلّي {tool} يشتغل كخبير",
        "سطر واحد في {tool} بيفرق بين نتيجة عادية ونتيجة مبهرة",
    ],
    "myth_fact": [
        "90% من الناس مصدّقين ده عن {kw}… وهو غلط",
        "\"{myth}\"… متأكد؟",
        "أشهر كدبة عن {kw}",
        "لو لسه مصدّق إن {myth_short}… لازم تشوف ده",
    ],
    "trend_watch": [
        "حصل النهارده في عالم {kw}… ومحدش واخد باله",
        "الخبر ده هيغيّر طريقة شغلك مع {tool}",
        "آخر تحديث في {kw}… في 30 ثانية",
        "ترند {tool} ده لازم تلحقه قبل الكل",
    ],
    "concept_30s": [
        "{concept} في 30 ثانية… ومن غير تعقيد",
        "الكل بيقول {concept}… بس محدش بيشرحها صح",
        "لو فهمت {concept}، هتفهم الـ AI كله",
        "كلمة واحدة لازم تعرفها: {concept}",
    ],
    "leader_mindset": [
        "القادة الناجحين بيعملوا كده مع {tool}",
        "السؤال ده عن {kw} بيفرق القائد عن المدير",
        "درس {kw} ده خدته بعد سنين… خده في 30 ثانية",
        "مش {tool} اللي بيفرق… ده اللي بيفرق",
    ],
}

CTAS = [
    "جرّبها النهارده واكتبلي النتيجة في الكومنتات 👇",
    "احفظ الفيديو وابعته لحد محتاجه 🔖",
    "تابعني عشان كل يوم خطوة جديدة في رحلة الـ AI 🚀",
    "اكتب \"AI\" في الكومنتات وأنا أبعتلك الخطوات ✍️",
    "شارك الفيديو مع فريقك وابدأوا النهارده 🤝",
]

TOOL_TAGS = {
    "Claude": ["#Claude", "#Anthropic"],
    "Manus": ["#Manus", "#AIAgents"],
    "Google Flow": ["#GoogleFlow", "#Veo", "#GoogleLabs"],
    "NotebookLM": ["#NotebookLM", "#GoogleLabs"],
    "Gemini": ["#Gemini", "#Google"],
    "Google": ["#GoogleLabs", "#Google"],
}


def tool_hashtags(tool):
    tags = []
    for key, vals in TOOL_TAGS.items():
        if key.lower() in tool.lower():
            tags += vals
    if not tags:
        tags = ["#" + re.sub(r"[^A-Za-z0-9]", "", tool)]
    return tags


def short(text, n=6):
    words = text.rstrip(".،").split()
    return " ".join(words[:n]) + ("…" if len(words) > n else "")


def fmt(s, t):
    return s.format(tool=t["tool"], kw=t["kw"], concept=t["concept"],
                    myth=t["myth"].rstrip("."), myth_short=short(t["myth"], 5))


def build_day(day, date, week, pillar_idx):
    t = THEMES[week]
    pid, p_ar, p_en = PILLARS[pillar_idx]
    variant = week % 4
    cta = CTAS[(day - 1) % len(CTAS)]

    if pid == "tool_demo":
        hook = t["hooks"][0]
        scenes = [
            {"ar": t["title"], "en": t["tool"]},
            {"ar": "١. " + t["demo"][0], "en": "Step 1"},
            {"ar": "٢. " + t["demo"][1], "en": "Step 2"},
            {"ar": "٣. " + t["demo"][2], "en": "Step 3"},
        ]
        voice = f"{hook}. النهارده هوريك {t['tool']} خطوة بخطوة. أولًا، {t['demo'][0]}. تانيًا، {t['demo'][1]}. وأخيرًا، {t['demo'][2]}."
    elif pid == "prompt_recipe":
        hook = fmt(HOOKS[pid][variant], t)
        scenes = [
            {"ar": f"المشكلة: إجابات عامة من {t['tool']}", "en": "Generic Output"},
            {"ar": "الـ Prompt:", "en": t["prompt"], "mono": True},
            {"ar": "ليه بينجح؟ " + t["concept_ar"].split("،")[0].split(".")[0], "en": t["concept"]},
        ]
        voice = f"{hook}. المشكلة إن أغلب الناس بيكتبوا سؤال عام فياخدوا إجابة عامة. جرّب الـ Prompt ده: حدّد الدور والمهمة وشكل النتيجة. وده بينجح لأن {t['concept_ar']}"
    elif pid == "myth_fact":
        hook = fmt(HOOKS[pid][variant], t)
        scenes = [
            {"ar": "❌ خرافة: " + t["myth"], "en": "MYTH"},
            {"ar": "✅ حقيقة: " + t["fact"], "en": "FACT"},
            {"ar": t["usecase"], "en": t["kw"]},
        ]
        voice = f"{hook}. الخرافة: {t['myth']} الحقيقة: {t['fact']} والدليل: {t['usecase']}"
    elif pid == "use_case":
        hook = t["hooks"][1]
        scenes = [
            {"ar": "الحالة: " + t["usecase"], "en": "Use Case"},
            {"ar": "إزاي؟ " + t["demo"][0], "en": t["tool"]},
            {"ar": "وبعدين: " + t["demo"][2], "en": t["kw"]},
            {"ar": "الدرس: " + t["fact"], "en": "Digital Transformation"},
        ]
        voice = f"{hook}. {t['usecase']} إزاي؟ {t['demo'][0]}، وبعدين {t['demo'][2]}. والدرس: {t['fact']}"
    elif pid == "trend_watch":
        hook = fmt(HOOKS[pid][variant], t)
        scenes = [
            {"ar": "[يتحدّث يوميًا] أهم خبر النهارده في " + t["kw"], "en": "AI NEWS"},
            {"ar": "[يتحدّث يوميًا] يعني إيه ده ليك؟", "en": "Why it matters"},
            {"ar": "[يتحدّث يوميًا] تعمل إيه النهارده؟", "en": "Action"},
        ]
        voice = "[TREND] يتكتب يوميًا بعد البحث عن آخر الأخبار: الخبر، ليه مهم، وتعمل إيه النهارده."
    elif pid == "concept_30s":
        hook = fmt(HOOKS[pid][variant], t)
        scenes = [
            {"ar": t["concept_ar"], "en": t["concept"]},
            {"ar": "مثال: " + t["usecase"], "en": "Example"},
            {"ar": "جرّب: " + t["demo"][0], "en": t["tool"]},
        ]
        voice = f"{hook}. {t['concept_ar']} مثال بسيط: {t['usecase']} وعشان تجرّب بنفسك: {t['demo'][0]}."
    else:  # leader_mindset
        hook = fmt(HOOKS[pid][variant], t)
        scenes = [
            {"ar": t["mindset"], "en": "Leadership"},
            {"ar": "خطوة عملية: " + t["demo"][0], "en": t["kw"]},
            {"ar": "تذكّر: " + t["fact"], "en": "AI Transformation"},
        ]
        voice = f"{hook}. {t['mindset']} خطوة عملية تبدأ بيها النهارده: {t['demo'][0]}. وتذكّر: {t['fact']}"

    voice = voice + " " + cta.rstrip(" 👇🔖🚀✍️🤝")
    hashtags = BRAND["base_hashtags"] + tool_hashtags(t["tool"]) + ["#" + re.sub(r"[^A-Za-z0-9]", "", t["kw"])]
    caption = (
        f"{hook}\n\n"
        f"📌 {p_ar} | {p_en}: {t['title']}\n"
        + "\n".join(f"• {s['ar']}" for s in scenes if not s.get("mono"))
        + (f"\n\n💡 Prompt:\n{t['prompt']}" if pid == "prompt_recipe" else "")
        + f"\n\n{cta}\n\n"
        f"\"{BRAND['quote_en']}\" {BRAND['signature']}\n\n"
        + " ".join(dict.fromkeys(hashtags))
    )
    return {
        "day": day,
        "date": date.isoformat(),
        "week": week + 1,
        "pillar": pid,
        "pillar_ar": p_ar,
        "pillar_en": p_en,
        "tool": t["tool"],
        "keyword": t["kw"],
        "theme_title": t["title"],
        "concept": t["concept"],
        "hook_ar": hook,
        "hook_keyword_en": t["kw"] if pid != "concept_30s" else t["concept"],
        "scenes": scenes,
        "prompt": t["prompt"],
        "voiceover_ar": voice,
        "cta": cta,
        "outro_quote": BRAND["quote_en"],
        "signature": BRAND["signature"],
        "caption": caption,
        "hashtags": list(dict.fromkeys(hashtags)),
        "platforms": BRAND["platforms"],
        "needs_live_trend": pid == "trend_watch",
        "status": "planned",
    }


def build_finale(day, date):
    t = THEMES[-1]
    hook = "يوم 365… وده أهم درس اتعلّمته في سنة AI"
    scenes = [
        {"ar": "365 يوم = 365 خطوة لقدّام", "en": "365 DAYS"},
        {"ar": "أدوات اتعلّمناها: Claude و Manus و Google Flow و NotebookLM و Gemini", "en": "AI Toolkit"},
        {"ar": t["mindset"], "en": "Continuous Learning"},
    ]
    voice = f"{hook}. سنة كاملة اتعلّمنا فيها مع بعض Claude و Manus و Google Flow و Google Labs. {t['mindset']} شكرًا إنك كنت جزء من الرحلة."
    entry = build_day(day, date, 51, 6)
    entry.update(pillar="finale", pillar_ar="الختام", pillar_en="Finale", hook_ar=hook,
                 scenes=scenes, voiceover_ar=voice, hook_keyword_en="365 DAYS OF AI")
    entry["caption"] = entry["caption"].replace(entry["caption"].split("\n")[0], hook, 1)
    return entry


def main():
    start = dt.date.fromisoformat(BRAND["start_date"])
    days = []
    for i in range(BRAND["days"]):
        date = start + dt.timedelta(days=i)
        if i == 364:
            days.append(build_finale(i + 1, date))
        else:
            days.append(build_day(i + 1, date, i // 7, i % 7))

    out = os.path.join(ROOT, "calendar")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "calendar_365.json"), "w", encoding="utf-8") as f:
        json.dump(days, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "calendar_365.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["day", "date", "week", "pillar", "tool", "keyword", "hook_ar", "scenes", "voiceover_ar", "caption"])
        for d in days:
            w.writerow([d["day"], d["date"], d["week"], d["pillar_en"], d["tool"], d["keyword"], d["hook_ar"],
                        " | ".join(s["ar"] for s in d["scenes"]), d["voiceover_ar"], d["caption"]])
    with open(os.path.join(out, "CALENDAR.md"), "w", encoding="utf-8") as f:
        f.write("# 365-Day Reel Calendar — Sam\n\n")
        f.write(f"Start {days[0]['date']} · End {days[-1]['date']} · 52 weekly themes × 7 formats.\n\n")
        for wk in range(0, 53):
            block = [d for d in days if d["week"] == wk + 1]
            if not block:
                continue
            f.write(f"\n## Week {wk + 1} — {block[0]['theme_title']} ({block[0]['tool']})\n\n")
            f.write("| Day | Date | Format | Hook (first 3s) |\n|---|---|---|---|\n")
            for d in block:
                f.write(f"| {d['day']} | {d['date']} | {d['pillar_en']} | {d['hook_ar'].replace('|', '/')} |\n")
    print(f"Wrote {len(days)} days to {out}")


if __name__ == "__main__":
    main()
