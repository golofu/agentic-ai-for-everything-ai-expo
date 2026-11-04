"""Replace the 'open the file' ending of a clip: python -I scripts/howto/fix_open.py <slug> [--drop]
--drop : just remove the ending (e.g. placeholder files that can't be opened)
else   : cut <slug>-open-fixed.mkv (from record-open.ps1) and append it as the new ending.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REC = pathlib.Path(r"C:\Users\User\AppData\Local\Temp\claude\785b8701d42b026f\8724ba23-8dc5-42db-aebc-2ec74bc49f15\scratchpad\rec")
slug = sys.argv[1]
spec = json.loads((REC / f"{slug}.spec.json").read_text(encoding="utf-8"))
if spec["segments"][-1]["cap"].startswith("เปิดไฟล์ดูผลงานจริง"):
    spec["segments"] = spec["segments"][:-1]
edit = [sys.executable, "-I", str(ROOT / "scripts/howto/edit.py")]
main_out = ROOT / spec["out"]

if "--drop" in sys.argv:
    (REC / f"{slug}.spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    subprocess.run(edit + [str(REC / f"{slug}.spec.json")], check=True)
    sys.exit()

ev = json.loads((REC / f"{slug}-open.events.json").read_text(encoding="utf-8-sig"))
base = dict(spec, out=f"cover/assets/videos/_base-{slug}.mp4")
(REC / f"{slug}.base.json").write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
subprocess.run(edit + [str(REC / f"{slug}.base.json")], check=True)
tail = {"src": str(REC / f"{slug}-open-fixed.mkv"), "out": f"cover/assets/videos/_tail-{slug}.mp4", "width": spec["width"],
        "segments": [{"in": ev["shown"] + 1.5, "out": ev["end"] - 0.3, "speed": 1, "cap": "เปิดไฟล์ดูผลงานจริง ตรวจก่อนส่งต่อ"}],
        "blur": [{"x": 1440, "y": 790, "w": 475, "h": 235, "in": 0, "out": 99999}], "poster": 0.5}
(REC / f"{slug}.tail.json").write_text(json.dumps(tail, ensure_ascii=False, indent=1), encoding="utf-8")
subprocess.run(edit + [str(REC / f"{slug}.tail.json")], check=True)
a, b = ROOT / base["out"], ROOT / tail["out"]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a), "-i", str(b), "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-movflags", "+faststart", str(main_out)], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "3", "-i", str(b), "-frames:v", "1", "-q:v", "3", str(main_out.with_name(main_out.stem + "-poster.jpg"))], check=True)
for f in (a, b, a.with_name(a.stem + "-poster.jpg"), b.with_name(b.stem + "-poster.jpg")):
    f.unlink(missing_ok=True)
print(f"fixed {main_out}")
