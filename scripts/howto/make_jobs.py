"""Build jobs.json for the real Claude Desktop recordings and prepare one fresh workspace per job.

Prompts are read verbatim from the site pages (ex-*.html #prompt, slide-233/234 #p1..#p7).
Each job gets C:/Users/User/Documents/AI-Expo-Demo/jobs/<slug>/baan-lamun (a copy of the workspace
Claude Desktop created in the setup-workspace recording) with the sample inputs copied in.
"""
import html
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MOTION = ROOT / "cover/assets/motion/setup-work-space"
SAMPLES = ROOT / "cover/assets/playbook-samples"
DATA = ROOT / "scripts/howto/data"
DEMO = pathlib.Path(r"C:\Users\User\Documents\AI-Expo-Demo")
TEMPLATE = DEMO / "baan-lamun-ai-expo-demo"
JOBS = DEMO / "jobs"


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def by_id(page, el_id):
    s = (MOTION / page).read_text(encoding="utf-8")
    m = re.search(rf'id="{el_id}"[^>]*>(.*?)</p>', s, re.S)
    return text_of(m.group(1))


def data_field(slug, field):
    f = DATA / f"{slug}.js"
    if not f.exists():
        return None
    m = re.search(rf'\b{field}:\s*"([^"]*)"', f.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def sample_files(slug, sub=None):
    d = SAMPLES / slug / (sub or "")
    return [p for p in sorted(d.iterdir()) if p.is_file() and p.suffix.lower() not in (".zip", ".py") and not p.name.endswith("listing.txt")]


jobs = []

def add(slug, prompt, inputs, folder="input", out=None, attach="ws", followups=None):
    jobs.append({"slug": slug, "prompt": prompt, "inputs": [str(p) for p in inputs], "folder": folder,
                 "out": out or "output", "attach": attach, "followups": followups or []})

# --- Setup menu
add("setup-firstjob", by_id("slide-233.html", "p1") if 'id="p1"' in (MOTION / "slide-233.html").read_text(encoding="utf-8") else
    "สรุปไฟล์ใน input/ ให้เหลือ 5 บรรทัด พร้อมตาราง ใครทำอะไร เมื่อไร แล้วเก็บไว้ใน output/", sample_files("setup-firstjob"))
add("setup-slips", by_id("slide-234.html", "p2"), sample_files("238-4"))
add("setup-handwriting", by_id("slide-234.html", "p3"), sample_files("setup-handwriting"))
add("setup-audio", by_id("slide-234.html", "p4"), [p for p in sample_files("setup-audio") if p.suffix == ".mp3"])
add("setup-calendar", by_id("slide-234.html", "p5"), sample_files("setup-calendar"))
add("setup-convert", by_id("slide-234.html", "p6").replace("[Word / Excel / PDF]", "Word"), sample_files("setup-convert"))
add("setup-merge", by_id("slide-234.html", "p7"), sample_files("setup-merge"))
add("setup-organize", by_id("slide-234.html", "p1"), sample_files("setup-organize", "Downloads-before"),
    folder="Downloads", out="Downloads", attach="folder", followups=["ตกลง"])

# --- AI Work Playbook (ids in menu order)
for ex in ["236-1", "236-2", "237-1", "237-3", "238-1", "238-2", "239-2", "239-5", "240-2", "240-6", "241-1", "241-2"]:
    folder = data_field(ex, "folder") or "input"
    out = data_field(ex, "outputFolder") or "output"
    add(ex, by_id(f"ex-{ex}.html", "prompt"), sample_files(ex, "output") if ex == "241-2" else sample_files(ex), folder=folder, out=out)

if "--check" in sys.argv:
    for j in jobs:
        print(j["slug"], "|", j["folder"], "->", j["out"], "|", len(j["inputs"]), "files |", j["prompt"][:70])
    sys.exit()

for j in jobs:
    jd = JOBS / j["slug"]
    if jd.exists():
        shutil.rmtree(jd)
    if j["attach"] == "folder":
        target = jd / j["folder"]
        target.mkdir(parents=True)
        j["attachPath"] = str(target)
    else:
        ws = jd / "baan-lamun"
        shutil.copytree(TEMPLATE, ws)
        target = ws / j["folder"]
        target.mkdir(exist_ok=True)
        j["attachPath"] = str(ws)
    for f in j["inputs"]:
        shutil.copy2(f, target / pathlib.Path(f).name)
    j["showPath"] = str(target)
    j["watchPath"] = str(pathlib.Path(j["attachPath"]) / j["out"]) if j["attach"] == "ws" else str(target)

(ROOT / "scripts/howto/jobs.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(jobs)} jobs prepared under {JOBS}")
