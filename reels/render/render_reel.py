# -*- coding: utf-8 -*-
"""Render one of Sam's daily reels (1080x1920 MP4) from the calendar.

Usage:
  python3 reels/render/render_reel.py --day 1
  python3 reels/render/render_reel.py --entry today.json --avatar reels/assets/sam.jpg \
      --voice voice.mp3 --avatar-video talking_head.mp4 --out reels/output/day-001.mp4

Layout: 0-3s hook (glitch-in, big Arabic line + English keyword chip),
content scenes with neon HUD, last 4s outro with Sam's quote and signature.
Arabic-first text, English keywords in Orbitron. Needs ffmpeg, numpy and Pillow
built with raqm (complex text layout).
"""
import argparse
import json
import math
import os
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO = os.path.dirname(ROOT)
BRAND = json.load(open(os.path.join(ROOT, "brand.json"), encoding="utf-8"))
FONTS = os.path.join(ROOT, "assets", "fonts")
W, H = BRAND["reel"]["width"], BRAND["reel"]["height"]
FPS = BRAND["reel"]["fps"]
HOOK_S = BRAND["reel"]["hook_seconds"]
OUTRO_S = 4.0
C = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in BRAND["colors"].items()}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def has_arabic(s):
    return any("؀" <= ch <= "ۿ" for ch in s)


def shape(s):
    return s  # Pillow's raqm layout does Arabic shaping + bidi natively


def noemoji(s):
    return "".join(ch for ch in s if ord(ch) < 0x2190).strip()  # bundled fonts have no emoji


def tdir(s):
    return "rtl" if has_arabic(s) else "ltr"


def wrap(text, fnt, max_w, draw):
    """Wrap in logical order, then shape each line (keeps RTL correct)."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(shape(trial), font=fnt, direction=tdir(trial)) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(text, fnt, max_w, fill, line_gap=1.25, align="center", glow=None):
    """Render wrapped (possibly Arabic) text to a transparent RGBA image."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = wrap(noemoji(text), fnt, max_w, tmp)
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * line_gap)
    img = Image.new("RGBA", (max_w + 80, lh * len(lines) + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        s = shape(ln)
        tw = d.textlength(s, font=fnt, direction=tdir(s))
        if align == "center":
            x = (img.width - tw) / 2
        elif align == "right" or has_arabic(ln):
            x = img.width - 40 - tw
        else:
            x = 40
        d.text((x, 30 + i * lh), s, font=fnt, fill=fill, direction=tdir(s))
    if glow:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        g.putalpha(0)
        layer = Image.new("RGBA", img.size, glow + (0,))
        layer.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(14)))
        img = Image.alpha_composite(layer, img)
    return img


def chip(text, fnt, fg, bg, pad=(34, 16)):
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    s = shape(text)
    tw = int(tmp.textlength(s, font=fnt, direction=tdir(s)))
    asc, desc = fnt.getmetrics()
    img = Image.new("RGBA", (tw + pad[0] * 2, asc + desc + pad[1] * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=img.height // 2, fill=bg + (70,), outline=fg + (255,), width=3)
    d.text((pad[0], pad[1] - 2), s, font=fnt, fill=fg, direction=tdir(s))
    return img


def mono_box(text, max_w):
    fnt = font("Cairo-700.ttf", 40)
    body = text_block(text, fnt, max_w - 80, C["neon_cyan"] + (255,), line_gap=1.2, align="left")
    img = Image.new("RGBA", (max_w, body.height + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=28, fill=(8, 14, 40, 220), outline=C["neon_violet"] + (255,), width=3)
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([28 + i * 34, 22, 48 + i * 34, 42], fill=col)
    img.alpha_composite(body, (20, 40))
    return img


# ---------- static layers ----------

def make_background():
    y = np.linspace(0, 1, H)[:, None]
    top, bot = np.array(C["bg_top"]), np.array(C["bg_bottom"])
    grad = (top * (1 - y) + bot * y)[:, None, :].repeat(W, axis=1)
    img = Image.fromarray(grad.reshape(H, W, 3).astype(np.uint8)).convert("RGBA")
    # soft neon glows
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-300, 200, 600, 1100], fill=C["neon_violet"] + (70,))
    gd.ellipse([600, 900, 1500, 1800], fill=C["neon_cyan"] + (50,))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    return Image.alpha_composite(img, glow)


def make_avatar(path, size=520):
    ring = Image.new("RGBA", (size + 120, size + 120), (0, 0, 0, 0))
    cx = cy = ring.width // 2
    if path and os.path.exists(path):
        ph = Image.open(path).convert("RGB")
        s = min(ph.size)
        ph = ph.crop(((ph.width - s) // 2, max(0, (ph.height - s) // 4), (ph.width - s) // 2 + s, max(0, (ph.height - s) // 4) + s))
        ph = ph.resize((size, size), Image.LANCZOS).convert("RGBA")
    else:  # holographic placeholder until Sam's photo is added
        ph = Image.new("RGBA", (size, size), (14, 22, 60, 255))
        d = ImageDraw.Draw(ph)
        d.ellipse([size * .32, size * .16, size * .68, size * .52], fill=C["neon_cyan"] + (180,))
        d.pieslice([size * .14, size * .55, size * .86, size * 1.25], 180, 360, fill=C["neon_violet"] + (180,))
        f = font("Orbitron-900.ttf", 64)
        d.text((size / 2, size * .86), "SAM", font=f, fill=(255, 255, 255, 230), anchor="mm")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
    ph.putalpha(mask)
    halo = Image.new("RGBA", ring.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([30, 30, ring.width - 30, ring.height - 30], fill=C["neon_cyan"] + (120,))
    ring = Image.alpha_composite(ring, halo.filter(ImageFilter.GaussianBlur(26)))
    ring.alpha_composite(ph, (cx - size // 2, cy - size // 2))
    return ring


def draw_hud(d, t, cx, cy, r):
    for k, (col, speed, span) in enumerate([(C["neon_cyan"], 40, 110), (C["neon_magenta"], -28, 70), (C["neon_violet"], 18, 160)]):
        rr = r + 18 + k * 16
        a0 = (t * speed + k * 90) % 360
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a0 + span, fill=col + (255,), width=5 - k)
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0 + 180, a0 + 180 + span / 3, fill=col + (200,), width=3)


def draw_grid(d, t):
    horizon = int(H * 0.70)
    col = C["neon_violet"]
    for i in range(14):
        z = ((i + (t * 1.6) % 1) / 14) ** 2
        y = horizon + int(z * (H - horizon))
        d.line([(0, y), (W, y)], fill=col + (int(40 + 120 * z),), width=2)
    for i in range(-12, 13):
        d.line([(W / 2 + i * 22, horizon), (W / 2 + i * 190, H)], fill=col + (70,), width=2)


# ---------- timeline ----------

def build_layers(entry, avatar_path):
    pill = entry["pillar_ar"]  # one direction per chip; English shows in the keyword chip
    layers = {
        "bg": make_background(),
        "avatar": make_avatar(avatar_path),
        "pill": chip(pill, font("Cairo-700.ttf", 36), C["neon_cyan"], C["neon_violet"]),
        "brand": text_block("SAM | AI TRANSFORMATION", font("Orbitron-700.ttf", 30), 900, C["muted"] + (255,)),
        "day": chip(f"DAY {entry['day']:03d}/365", font("Orbitron-700.ttf", 30), C["neon_magenta"], C["neon_magenta"]),
        "hook": text_block(entry["hook_ar"], font("Cairo-900.ttf", 86), 960, C["text"] + (255,), line_gap=1.15, glow=C["neon_magenta"]),
        "hook_kw": chip(entry["hook_keyword_en"].upper(), font("Orbitron-900.ttf", 44), C["neon_cyan"], C["neon_cyan"]),
        "scenes": [],
    }
    for sc in entry["scenes"]:
        if sc.get("mono"):
            body = mono_box(sc["en"], 960)
            head = text_block(sc["ar"], font("Cairo-900.ttf", 64), 960, C["text"] + (255,))
            layers["scenes"].append((head, body, None))
        else:
            body = text_block(sc["ar"], font("Cairo-700.ttf", 62), 940, C["text"] + (255,), line_gap=1.3)
            kw = chip(sc["en"][:42].upper(), font("Orbitron-700.ttf", 40), C["neon_cyan"], C["neon_violet"])
            layers["scenes"].append((kw, body, None))
    q = entry["outro_quote"]
    layers["quote"] = text_block(f"“{q}”", font("Cairo-900.ttf", 76), 1000, C["text"] + (255,), line_gap=1.1, glow=C["neon_cyan"])
    layers["sig"] = text_block(entry["signature"], font("Orbitron-900.ttf", 84), 900, C["neon_cyan"] + (255,), glow=C["neon_violet"])
    layers["cta"] = text_block(entry["cta"], font("Cairo-700.ttf", 46), 940, C["muted"] + (255,))
    return layers


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def paste(frame, img, cx, y, alpha=1.0, dx=0):
    if alpha <= 0:
        return
    if alpha < 1:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda a: int(a * alpha)))
    frame.alpha_composite(img, (int(cx - img.width / 2 + dx), int(y)))


def render(entry, avatar_path, voice_path, out_path, avatar_video=None):
    layers = build_layers(entry, avatar_path)
    n = len(layers["scenes"])
    voice_len = 0.0
    if voice_path:
        voice_len = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", voice_path]).strip())
    total = max(HOOK_S + n * 5.5 + OUTRO_S, voice_len + OUTRO_S + 0.5)
    scene_len = (total - HOOK_S - OUTRO_S) / max(n, 1)
    frames = int(total * FPS)
    rnd = random.Random(entry["day"])
    particles = [(rnd.random() * W, rnd.random() * H, rnd.uniform(20, 80), rnd.choice(["neon_cyan", "neon_violet", "neon_magenta"])) for _ in range(60)]

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    silent = out_path + ".video.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    av = layers["avatar"]
    for fi in range(frames):
        t = fi / FPS
        frame = layers["bg"].copy()
        d = ImageDraw.Draw(frame, "RGBA")
        draw_grid(d, t)
        for (px, py, sp, col) in particles:
            yy = (py - t * sp) % H
            d.ellipse([px - 3, yy - 3, px + 3, yy + 3], fill=C[col] + (160,))
        in_outro = t >= total - OUTRO_S
        # avatar (bigger during hook and outro)
        scale = 1.0 if (t < HOOK_S or in_outro) else 0.62
        a_img = av if scale == 1.0 else av.resize((int(av.width * scale), int(av.height * scale)), Image.BILINEAR)
        a_y = 250 if scale == 1.0 else 190
        paste(frame, a_img, W / 2, a_y, alpha=ease(t / 0.5))
        r = int(260 * scale)
        draw_hud(d, t, W // 2, a_y + a_img.height // 2, r)
        paste(frame, layers["brand"], W / 2, 70)
        paste(frame, layers["day"], W / 2, 140)

        if t < HOOK_S:  # ---- HOOK: glitch-in within first 0.4s
            p = ease(t / 0.35)
            jitter = 0 if t > 0.4 else rnd.randint(-18, 18)
            if t < 0.4:
                ghost = layers["hook"].copy()
                ghost.putalpha(ghost.getchannel("A").point(lambda a: a // 2))
                frame.alpha_composite(Image.merge("RGBA", (ghost.getchannel("R"), ghost.getchannel("A").point(lambda a: 0), ghost.getchannel("A").point(lambda a: 0), ghost.getchannel("A"))),
                                      (int(W / 2 - ghost.width / 2 + 14), 960))
            paste(frame, layers["hook"], W / 2, 950 + (1 - p) * 60, alpha=p, dx=jitter)
            paste(frame, layers["hook_kw"], W / 2, 950 + layers["hook"].height + 30, alpha=ease((t - 0.5) / 0.4))
        elif not in_outro:  # ---- CONTENT SCENES
            si = min(int((t - HOOK_S) / scene_len), n - 1)
            local = t - HOOK_S - si * scene_len
            a_in, a_out = ease(local / 0.45), ease((scene_len - local) / 0.3)
            alpha = min(a_in, a_out)
            paste(frame, layers["pill"], W / 2, 590, alpha=alpha)
            head, body, _ = layers["scenes"][si]
            slide = (1 - a_in) * 120
            paste(frame, head, W / 2, 700, alpha=alpha, dx=slide)
            paste(frame, body, W / 2, 700 + head.height + 30, alpha=alpha, dx=-slide)
            # progress dots
            for k in range(n):
                col = C["neon_cyan"] if k == si else C["muted"]
                x = W / 2 + (k - (n - 1) / 2) * 44
                d.ellipse([x - 9, 1700, x + 9, 1718], fill=col + (255 if k == si else 120,))
        else:  # ---- OUTRO: quote + signature
            lt = t - (total - OUTRO_S)
            paste(frame, layers["quote"], W / 2, 900 + (1 - ease(lt / 0.6)) * 50, alpha=ease(lt / 0.6))
            sig_y = 900 + layers["quote"].height + 20
            paste(frame, layers["sig"], W / 2, sig_y, alpha=ease((lt - 0.6) / 0.6))
            line_w = int(560 * ease((lt - 0.9) / 0.8))
            d.line([(W / 2 - line_w / 2, sig_y + layers["sig"].height + 6), (W / 2 + line_w / 2, sig_y + layers["sig"].height + 6)], fill=C["neon_magenta"] + (255,), width=6)
            paste(frame, layers["cta"], W / 2, 1620, alpha=ease((lt - 1.2) / 0.6))
        # global progress bar
        d.rectangle([0, H - 14, int(W * t / total), H], fill=C["neon_cyan"] + (255,))
        ff.stdin.write(frame.convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()

    # audio: voice (if any) over a soft synth pad with a hook whoosh
    pad = f"aevalsrc='0.05*sin(2*PI*110*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.04*sin(2*PI*164.8*t)+0.03*sin(2*PI*220*t)':s=44100:d={total}"
    whoosh = "anoisesrc=d=0.6:c=pink:a=0.25,afade=t=in:d=0.25,afade=t=out:st=0.3:d=0.3"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-f", "lavfi", "-i", pad, "-f", "lavfi", "-i", whoosh]
    if voice_path:
        cmd += ["-i", voice_path]
        mix = "[1:a][2:a][3:a]amix=inputs=3:duration=first:weights='0.5 1 2.2'[a]"
    else:
        mix = "[1:a][2:a]amix=inputs=2:duration=first:weights='1 1'[a]"
    cmd += ["-filter_complex", mix, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path]
    subprocess.check_call(cmd)
    os.remove(silent)

    if avatar_video:  # overlay a lip-sync talking head in the avatar circle
        tmp = out_path + ".tmp.mp4"
        flt = ("[1:v]scale=520:520:force_original_aspect_ratio=increase,crop=520:520,format=rgba,"
               "geq=r='r(X,Y)':a='if(lte(hypot(X-260,Y-260),258),255,0)'[ah];"
               f"[0:v][ah]overlay=x=(W-w)/2:y=310:enable='lt(t,{HOOK_S})+gte(t,{total - OUTRO_S})'[v]")
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", out_path, "-i", avatar_video, "-filter_complex", flt,
                               "-map", "[v]", "-map", "0:a", "-c:a", "copy", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", tmp])
        os.replace(tmp, out_path)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int)
    ap.add_argument("--entry", help="JSON file with a single (possibly trend-updated) calendar entry")
    ap.add_argument("--avatar", default=os.path.join(REPO, BRAND["avatar"]["local_photo"]))
    ap.add_argument("--voice")
    ap.add_argument("--avatar-video")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.entry:
        entry = json.load(open(a.entry, encoding="utf-8"))
    else:
        cal = json.load(open(os.path.join(ROOT, "calendar", "calendar_365.json"), encoding="utf-8"))
        entry = cal[a.day - 1]
    out = a.out or os.path.join(ROOT, "output", f"day-{entry['day']:03d}.mp4")
    secs = render(entry, a.avatar, a.voice, out, a.avatar_video)
    print(f"Rendered {out} ({secs:.1f}s)")


if __name__ == "__main__":
    main()
