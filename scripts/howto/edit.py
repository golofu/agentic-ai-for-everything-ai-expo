"""Cut a real screen recording into a teaching clip: python -I scripts/howto/edit.py <spec.json>

spec = {
  "src": "raw recording (mkv/mp4, 1920x1028)",
  "out": "cover/assets/videos/howto-<id>.mp4",
  "width": 1280,
  "segments": [ {"in": 0, "out": 24, "speed": 1, "cap": "Thai caption shown for the whole segment"} ],
  "blur": [ {"x":555,"y":740,"w":810,"h":225, "in": 0, "out": 24} ]   # times in SOURCE seconds
}
Only cuts, speed-ups, blur boxes (privacy) and caption bars are added; the footage itself is untouched.
Captions are drawn as PNGs with Chrome (correct Thai shaping) and overlaid by ffmpeg.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]

CAP_HTML = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@600&display=swap" rel="stylesheet">
<style>html,body{margin:0;background:transparent}
div{display:inline-block;font:600 40px/1.35 'Noto Sans Thai';color:#fff;background:rgba(32,31,29,.92);
padding:14px 34px;border-radius:18px;max-width:1700px;text-align:center}
em{font-style:normal;color:#f3a37f}</style></head><body><div id="c"></div></body></html>"""


def render_caps(texts, tmp):
    paths = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1800, "height": 300})
        pg.set_content(CAP_HTML)
        pg.wait_for_function("document.fonts.ready.then(() => true)")
        pg.wait_for_timeout(400)
        for i, t in enumerate(texts):
            f = tmp / f"cap{i}.png"
            pg.evaluate("t => document.getElementById('c').innerHTML = t", t)
            pg.wait_for_timeout(50)
            pg.locator("#c").screenshot(path=str(f), omit_background=True)
            paths.append(f)
        b.close()
    return paths


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    src = spec["src"]
    out = ROOT / spec["out"]
    W = spec.get("width", 1280)
    segs = spec["segments"]
    blurs = spec.get("blur", [])
    tmp = pathlib.Path(tempfile.mkdtemp())
    caps = render_caps([s.get("cap", "") or " " for s in segs], tmp)

    # source -> blurred source (blur boxes keyed to source time), then cut segments, then captions
    fc = []
    base = "[0:v]"
    for i, bx in enumerate(blurs):
        en = f"between(t,{bx.get('in', 0)},{bx.get('out', 1e9)})"
        fc.append(f"{base}split[b{i}a][b{i}b];[b{i}b]crop={bx['w']}:{bx['h']}:{bx['x']}:{bx['y']},boxblur=18:2[b{i}c];"
                  f"[b{i}a][b{i}c]overlay={bx['x']}:{bx['y']}:enable='{en}'[bl{i}]")
        base = f"[bl{i}]"
    n = len(segs)
    fc.append(f"{base}split={n}" + "".join(f"[s{i}]" for i in range(n)))
    t_out = 0.0
    for i, s in enumerate(segs):
        sp = s.get("speed", 1)
        fc.append(f"[s{i}]trim={s['in']}:{s['out']},setpts=(PTS-STARTPTS)/{sp},fps=30,scale={W}:-2[v{i}]")
    fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[cat]")
    cur = "[cat]"
    for i, s in enumerate(segs):
        dur = (s["out"] - s["in"]) / s.get("speed", 1)
        if s.get("cap"):
            fc.append(f"[{i + 1}:v]scale=iw*{W}/1920:-1[c{i}];{cur}[c{i}]overlay=(W-w)/2:H-h-{int(28 * W / 1280)}:shortest=1:enable='between(t,{t_out:.2f},{t_out + dur:.2f})'[o{i}]")
            cur = f"[o{i}]"
        t_out += dur
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src]
    for c in caps:
        cmd += ["-loop", "1", "-i", str(c)]
    cmd += ["-filter_complex", ";".join(fc), "-map", cur, "-t", f"{t_out:.2f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "medium", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    poster = out.with_name(out.stem + "-poster.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t_out * spec.get('poster', 0.85):.2f}", "-i", str(out), "-frames:v", "1", "-q:v", "3", str(poster)], check=True)
    print(f"wrote {out} ({t_out:.1f}s) + poster")


if __name__ == "__main__":
    main()
