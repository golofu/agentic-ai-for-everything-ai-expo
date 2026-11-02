# Screenshots every embedded page (type "profile-site") of every lesson in cover/menu.html
# and saves a 320px-wide JPG to cover/assets/page-thumbs/<slug>.jpg for the thumbnail strip
# and slide picker. Re-run after changing any lesson's embedded pages.
#
#   pip install playwright pillow
#   python scripts/make-page-thumbs.py            (all pages)
#   python scripts/make-page-thumbs.py --missing  (only pages without a thumbnail yet)
import io
import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
COVER = ROOT / "cover"
OUT = COVER / "assets" / "page-thumbs"
def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = free_port()  # never reuse a server another tool left running
BASE = f"http://127.0.0.1:{PORT}/"
TALK_EDITED_MOTION = ["skill/demo-create-1.html", "skill/demo-create-2.html", "skill/demo-create-3.html", "skill/slide-094.html"]
MANIFEST = OUT / "manifest.json"  # files this script wrote last time; only these may be deleted as stale
WAIT_MS = 3500


def wait_for_server(server):
    for _ in range(50):
        if server.poll() is not None:
            raise SystemExit("thumbnail server exited before it was ready")
        try:
            urllib.request.urlopen(BASE + "menu.html", timeout=1)
            return
        except Exception:
            time.sleep(0.2)
    raise SystemExit(f"server on port {PORT} did not start")


def main():
    only_missing = "--missing" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=COVER,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_for_server(server)
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            page = browser.new_page(viewport={"width": 1600, "height": 900})
            page.goto(BASE + "menu.html")
            # Same list and slug function the viewer uses; lessons with their own content thumbs are skipped.
            # Same list and slug function the viewer uses; lessons with their own content thumbs are skipped.
            # Each thumbnail is shot from inside the viewer (same frame size the audience sees), because
            # embedded pages lay out differently at full window size than in the viewer's frame.
            items = page.evaluate("""() => {
                const seen = new Set(), out = [];
                for (const [key, lesson] of Object.entries(lessons)) {
                    if (lesson.contentThumbDir) continue;
                    lessonPages(lesson).forEach((p, index) => {
                        if (p.type === "profile-site" && p.href && !seen.has(p.href)) {
                            seen.add(p.href);
                            out.push({ key, index, href: p.href, file: `page-thumbs/${pageThumbSlug(p.href)}.jpg` });
                        } else if (p.motion && TALK_EDITED_MOTION.includes(p.motion) && !seen.has(p.motion)) {
                            // Motion pages edited for the talk: their course thumbnails show the old layout.
                            seen.add(p.motion);
                            out.push({ key, index, href: p.motion, file: "motion/" + p.motion.replace(/([^/]+)\.html$/, "thumbs/$1.jpg") });
                        }
                    });
                }
                return out;
            }""".replace("TALK_EDITED_MOTION", json.dumps(TALK_EDITED_MOTION)))
            made = 0
            written = set()
            for item in items:
                target = COVER / "assets" / item["file"]
                if only_missing and target.exists():
                    continue
                page.goto(BASE + "menu.html#" + item["key"])
                page.reload()
                page.wait_for_timeout(800)
                page.evaluate(f"showSlide({item['index']})")
                page.wait_for_timeout(WAIT_MS)
                png = page.locator(".slide-frame").first.screenshot()
                img = Image.open(io.BytesIO(png)).convert("RGB")
                img = img.resize((320, round(img.height * 320 / img.width)), Image.LANCZOS)
                img.save(target, "JPEG", quality=80, optimize=True)
                made += 1
                if item["file"].startswith("page-thumbs/"):
                    written.add(target.name)
                print(f"{item['file']}  <-  {item['href'][:80]}")
            browser.close()
        keep = {Path(i["file"]).name for i in items if i["file"].startswith("page-thumbs/")}
        previous = set(json.loads(MANIFEST.read_text(encoding="utf-8"))) if MANIFEST.exists() else set()
        stale = [OUT / name for name in sorted(previous - keep) if (OUT / name).exists()]
        for f in stale:
            f.unlink()
        # Own only what this script wrote (now or before), never a same-named file it found and skipped.
        owned = (previous | written) & keep
        MANIFEST.write_text(json.dumps(sorted(owned), indent=1), encoding="utf-8")
        print(f"{made} thumbnails written, {len(stale)} stale removed, {len(items)} pages total")
    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    main()
