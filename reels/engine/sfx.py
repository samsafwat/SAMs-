"""Synthesize a music + SFX bed timed to a built reel timeline.

Everything is generated with numpy (no samples, no licensing questions):
a four-chord pad with sidechain pump, kick/hat groove, whooshes on scene cuts,
impacts on hooks/stats/punchlines and dings on list items and steps.
"""
import wave

import numpy as np

SR = 44100


def build_bed(spec, out_path, seed=7):
    T = spec["total"]
    N = int(T * SR)
    out = np.zeros(N)
    rng = np.random.default_rng(seed)
    t_all = np.arange(N) / SR

    def add(sig, at, gain=1.0):
        i = int(at * SR)
        j = min(N, i + len(sig))
        if 0 <= i < N:
            out[i:j] += sig[: j - i] * gain

    def env(n, a=0.005, r=0.2):
        t = np.arange(n) / SR
        return np.minimum(1, t / a) * np.exp(-t / r)

    def kick():
        n = int(0.4 * SR)
        t = np.arange(n) / SR
        f = 50 + 110 * np.exp(-t * 30)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.12)

    def hat():
        n = int(0.06 * SR)
        x = np.diff(np.concatenate([[0], rng.standard_normal(n)]))
        return x * env(n, 0.001, 0.015) * 0.3

    def whoosh(d=0.5, up=True):
        n = int(d * SR)
        k = np.linspace(0, 1, n)
        y = np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same")
        return y * np.sin(np.pi * (k ** (0.6 if up else 1.6))) * 0.6

    def impact():
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        return np.sin(2 * np.pi * (40 + 60 * np.exp(-t * 8)) * t) * np.exp(-t * 3) + rng.standard_normal(n) * np.exp(-t * 18) * 0.5

    def ding(f=1320):
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 9) * 0.35

    # pad: Am - F - C - G with a sidechain pump on the beat
    bpm = spec.get("bpm", 104)
    beat = 60 / bpm
    bar = beat * 4
    chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [130.8, 196, 261.6], [196, 246.9, 293.7]]
    pad = np.zeros(N)
    for b in range(int(T / bar) + 1):
        s, e = int(b * bar * SR), min(N, int((b + 1) * bar * SR))
        if s >= N:
            break
        tt = t_all[s:e]
        for f in chords[b % 4]:
            pad[s:e] += np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2 * tt + 0.3)
        k = np.linspace(0, 1, e - s)
        pad[s:e] *= np.minimum(1, k * 8) * np.minimum(1, (1 - k) * 8)
    out += pad * 0.045 * (1 - 0.6 * np.exp(-((t_all % beat) / 0.12)))

    scenes = spec["scenes"]
    groove_from = scenes[1]["start"] if len(scenes) > 1 else 0
    at = groove_from
    while at < T - 1.5:
        add(kick(), at, 0.55)
        add(hat(), at + beat / 2, 0.8)
        at += beat

    for i, sc in enumerate(scenes):
        s, d = sc["start"], sc["end"] - sc["start"]
        if i > 0:
            add(whoosh(0.55), s - 0.35, 0.7)
        kind = sc["type"]
        if kind == "hook":
            add(impact(), s, 0.9)
            if sc.get("strike"):
                add(whoosh(0.35, False), s + d * 0.75, 0.5)
        elif kind == "stat":
            add(impact(), s, 0.7)
        elif kind == "list":
            n = len(sc.get("items", []))
            seg = (d - 0.5) / max(n, 1)
            for j in range(n):
                add(ding(1320 + j * 110), s + 0.4 + seg * j + 0.3)
        elif kind == "steps":
            n = len(sc.get("items", []))
            seg = (d - 0.6) / max(n, 1)
            for j in range(n):
                add(whoosh(0.3, False), s + 0.5 + seg * j, 0.5)
                add(ding(990), s + 0.7 + seg * j, 0.8)
        elif kind == "strikes":
            n = len(sc.get("items", []))
            seg = d / (n + 1.3)
            for j in range(n):
                add(whoosh(0.25, False), s + seg * j + 0.3, 0.45)
            add(impact(), s + seg * n, 0.7)
        elif kind == "tool":
            add(ding(1480), s + 0.5, 0.9)
        elif kind == "cta":
            add(ding(1760), s + 0.5, 1.0)

    fo = int(1.5 * SR)
    out[-fo:] *= np.linspace(1, 0, fo)
    out = out / (np.max(np.abs(out)) or 1) * 0.5
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
