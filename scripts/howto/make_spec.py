"""Turn <slug>.events.json from record-job.ps1 into an edit.py spec, then cut the clip.
python -I scripts/howto/make_spec.py <slug> [--no-cut]
Captions name the real step; waiting time is sped up and the speed-up is stated in the caption.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REC = pathlib.Path(r"C:\Users\User\AppData\Local\Temp\claude\785b8701d42b026f\8724ba23-8dc5-42db-aebc-2ec74bc49f15\scratchpad\rec")
slug = sys.argv[1]
ev = json.loads((REC / f"{slug}.events.json").read_text(encoding="utf-8-sig"))
job = next(j for j in json.loads((ROOT / "scripts/howto/jobs.json").read_text(encoding="utf-8")) if j["slug"] == slug)
folder = job["folder"]
out = job["out"]
ws = "Downloads" if job["attach"] == "folder" else "baan-lamun"


def seg(a, b, cap, speed=1.0):
    return {"in": round(a, 2), "out": round(b, 2), "speed": speed, "cap": cap}


def work(a, b, cap):
    dur = b - a
    sp = max(1.0, round(dur / 22, 1))
    note = f" (เร่ง {sp:g} เท่า)" if sp > 1.2 else ""
    return seg(a, b, cap + note, sp)


segs = [
    seg(ev["files"] + 4.0, ev["files-end"], f"ไฟล์ตั้งต้นอยู่ในโฟลเดอร์ <em>{folder}/</em>" if job["inputs"] else f"เปิดโฟลเดอร์ <em>{folder}</em>"),
    seg(ev["pick"], ev["allow-end"], f"Claude Desktop: <em>Project or folder</em> → <em>Add folder</em> → เลือก <em>{ws}</em>", 1.5),
    seg(ev["prompt"], ev["send"] + 1.2, "วางคำสั่งจากหน้าตัวอย่าง แล้วกดส่ง"),
]
done = ev.get("done") or ev.get("timeout")
segs.append(work(ev["send"] + 1.2, done, "Claude เปิดไฟล์และลงมือทำเอง"))
if "followup" in ev:
    segs.append(seg(done, ev["followup"], "Claude เสนอแผนก่อน แล้วรอเราพิมพ์ <em>ตกลง</em>", 1.0))
    d2 = ev.get("done2") or ev.get("timeout2")
    segs.append(seg(ev["followup"], ev["followup"] + 3, "พิมพ์ <em>ตกลง</em> แล้วส่ง"))
    segs.append(work(ev["followup"] + 3, d2, "Claude จัดไฟล์ตามแผน"))
    done = d2
segs.append(seg(done, ev["reply-end"] + 2, "อ่านคำตอบของ Claude ด้วย ว่าทำอะไรไป และอะไรที่ยังขาด"))
segs.append(seg(ev["result"] + 1.5, ev["result-explorer-end"], f"ไฟล์ใหม่มารออยู่ใน <em>{out}/</em> แล้ว" if ev.get("newFiles") else f"ไม่มีไฟล์ใหม่ใน <em>{out}/</em> ดูเหตุผลในคำตอบของ Claude"))
if ev.get("open"):
    segs.append(seg(ev["result-explorer-end"] + 1, ev["end"] - 0.8, "เปิดไฟล์ดูผลงานจริง ตรวจก่อนส่งต่อ"))

spec = {
    "src": str(REC / f"{slug}-fixed.mkv"),
    "out": f"cover/assets/videos/howto-{slug}.mp4",
    "width": 1280,
    "segments": segs,
    "blur": [
        {"x": 555, "y": 735, "w": 815, "h": 230, "in": 0, "out": ev["allow-end"]},   # Recent artifacts on the home screen
        {"x": 557, "y": 262, "w": 385, "h": 290, "in": ev["pick"], "out": ev["pick"] + 4},    # the user's project list in the folder menu
        {"x": 1440, "y": 790, "w": 475, "h": 235, "in": 0, "out": 99999},                    # desktop notifications corner
    ],
    "poster": 0.8,
}
f = REC / f"{slug}.spec.json"
f.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
if "--no-cut" not in sys.argv:
    subprocess.run([sys.executable, "-I", str(ROOT / "scripts/howto/edit.py"), str(f)], check=True)
