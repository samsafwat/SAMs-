"""Render a reel spec (JSON) to a finished 1080x1920 MP4.

usage:
  python3 reels/engine/render.py SPEC.json OUT_DIR [--audio-dir DIR] [--presenter-video FILE]
                                                   [--stills 1.0,5.5,...] [--fps 30]

--audio-dir        one narration clip per scene, named 01.wav/01.mp3, 02.wav ... (scene order).
                   Each scene lasts as long as its clip (+ a short gap). Without it, scene
                   lengths are estimated from word count and the reel is silent apart from music.
--presenter-video  a lip-synced talking-head clip of the whole narration (same timeline);
                   its frames replace the still presenter photo.
Per scene, a "video" field (path relative to the spec) on a presenter/cta scene does the same
for that scene only, and its audio track becomes that scene's narration when no clip exists.
This is the cheap route: pay for lip-sync on the 2 presenter scenes, not the whole reel.
--stills           render only these timestamps to PNG (fast design check), no video.
                   "auto" = the middle of each scene.

Output: OUT_DIR/reel.mp4, OUT_DIR/cover.jpg, OUT_DIR/timeline.json
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sfx import build_bed  # noqa: E402

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
GAP = 0.25
TAIL = 1.8


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def estimate(text, lang):
    words = len((text or "").split())
    return max(2.2, words / (2.3 if lang == "ar" else 2.7) + 0.3)


def find_clip(audio_dir, i):
    if not audio_dir:
        return None
    for ext in ("wav", "mp3", "m4a"):
        f = audio_dir / f"{i + 1:02d}.{ext}"
        if f.exists():
            return f
    return None


def build_timeline(spec, audio_dir, spec_dir):
    t = 0.15
    for i, sc in enumerate(spec["scenes"]):
        clip = find_clip(audio_dir, i)
        if not clip and sc.get("video"):
            clip = (spec_dir / sc["video"]).resolve()
        d = duration(clip) if clip else sc.get("dur") or estimate(sc.get("say"), spec.get("lang"))
        sc["_clip"] = str(clip) if clip else None
        sc["start"], sc["speechEnd"], sc["end"] = t, t + d, t + d + GAP
        t = sc["end"]
    spec["total"] = t + spec.get("tail", TAIL)
    return spec


def draw(pg, t):
    """Render frame t and wait until any image it swapped in (lip-sync frames) is decoded."""
    pg.evaluate("t => { render(t); return Promise.all([...document.images].map(i => i.complete && i.naturalWidth"
                " ? null : i.decode().catch(() => null))) }", t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("out")
    ap.add_argument("--audio-dir")
    ap.add_argument("--presenter-video")
    ap.add_argument("--stills")
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()

    spec_path = pathlib.Path(a.spec).resolve()
    out = pathlib.Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    spec = json.loads(spec_path.read_text())
    spec = build_timeline(spec, pathlib.Path(a.audio_dir).resolve() if a.audio_dir else None, spec_path.parent)

    if spec.get("presenter"):
        p = (spec_path.parent / spec["presenter"]).resolve()
        spec["presenter"] = p.as_uri() if p.exists() else None
    for i, sc in enumerate(spec["scenes"]):
        if sc.get("video"):
            v = (spec_path.parent / sc["video"]).resolve()
            fdir = out / f"frames_{i + 1:02d}"
            shutil.rmtree(fdir, ignore_errors=True)
            fdir.mkdir()
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(v), "-vf", f"fps={a.fps},scale=1020:-2",
                            "-q:v", "3", str(fdir / "%05d.jpg")], check=True)
            sc["frames"] = {"pattern": fdir.as_uri() + "/%05d.jpg", "fps": a.fps, "count": len(list(fdir.glob("*.jpg")))}
    if a.presenter_video:
        fdir = out / "presenter_frames"
        shutil.rmtree(fdir, ignore_errors=True)
        fdir.mkdir()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.presenter_video, "-vf", f"fps={a.fps},scale=1020:-2",
                        "-q:v", "3", str(fdir / "%05d.jpg")], check=True)
        spec["presenterFrames"] = {"pattern": fdir.as_uri() + "/%05d.jpg", "fps": a.fps,
                                   "count": len(list(fdir.glob("*.jpg")))}

    (out / "timeline.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False))

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.add_init_script(f"window.SPEC={json.dumps(spec, ensure_ascii=False)};")
        pg.goto((HERE / "reel.html").as_uri())
        pg.wait_for_function("window.READY === true", timeout=15000)

        if a.stills:
            times = ([round((sc["start"] + sc["speechEnd"]) / 2, 2) for sc in spec["scenes"]] if a.stills == "auto"
                     else [float(x) for x in a.stills.split(",")])
            for s in times:
                draw(pg, s)
                pg.screenshot(path=str(out / f"still_{s:05.2f}.png"))
            print("stills written to", out)
            return

        n = int(spec["total"] * a.fps)
        silent = out / "video_only.mp4"
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", str(silent)],
                               stdin=subprocess.PIPE)
        for i in range(n):
            draw(pg, i / a.fps)
            frame = pg.screenshot(type="jpeg", quality=92)
            enc.stdin.write(frame)
            if i == int(min(spec["scenes"][0]["end"] * 0.6, 2.0) * a.fps):
                (out / "cover.jpg").write_bytes(frame)
            if i % 300 == 0:
                print(f"frame {i}/{n}", flush=True)
        enc.stdin.close()
        enc.wait()

    bed = out / "bed.wav"
    build_bed(spec, bed)
    clips = [(sc["_clip"], sc["start"]) for sc in spec["scenes"] if sc["_clip"]]
    final = out / "reel.mp4"
    if clips:
        inputs, parts = [], []
        for k, (c, start) in enumerate(clips):
            inputs += ["-i", c]
            ms = int(start * 1000)
            parts.append(f"[{k + 2}:a]aresample=44100,aformat=channel_layouts=mono,adelay={ms}|{ms}[n{k}]")
        mix = "".join(f"[n{k}]" for k in range(len(clips)))
        fc = ";".join(parts) + f";{mix}amix=inputs={len(clips)}:normalize=0,apad=whole_dur={spec['total']:.3f}[voice];" \
             "[voice]asplit[v1][v2];[1:a]volume=0.55[bedq];[bedq][v1]sidechaincompress=threshold=0.02:ratio=8:release=300[duck];" \
             "[duck][v2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[aout]"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(bed), *inputs,
               "-filter_complex", fc, "-map", "0:v", "-map", "[aout]"]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(bed),
               "-af", "loudnorm=I=-14:TP=-1.5", "-map", "0:v", "-map", "1:a"]
    subprocess.run(cmd + ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    silent.unlink(missing_ok=True)
    print(f"done: {final}  ({spec['total']:.1f}s)")


if __name__ == "__main__":
    main()
