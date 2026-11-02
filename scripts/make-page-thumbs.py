# Screenshots every embedded page (type "profile-site") of every lesson in cover/menu.html
# and saves a 320px-wide JPG to cover/assets/page-thumbs/<slug>.jpg for the thumbnail strip
# and slide picker. Re-run after changing any lesson's embedded pages.
#
#   pip install playwright pillow
#   python scripts/make-page-thumbs.py            (all pages)
#   python scripts/make-page-thumbs.py --missing  (only pages without a thumbnail yet)
import io
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
PORT = 4182
BASE = f"http://localhost:{PORT}/"
WAIT_MS = 3500


def wait_for_server():
    for _ in range(50):
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
        wait_for_server()
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            page = browser.new_page(viewport={"width": 1600, "height": 900})
            page.goto(BASE + "menu.html")
            # Same list and slug function the viewer uses; lessons with their own content thumbs are skipped.
            items = page.evaluate("""() => {
                const seen = new Set(), out = [];
                for (const lesson of Object.values(lessons)) {
                    if (lesson.contentThumbDir) continue;
                    for (const p of lessonPages(lesson)) {
                        if (p.type !== "profile-site" || !p.href || seen.has(p.href)) continue;
                        seen.add(p.href);
                        out.push({ href: p.href, slug: pageThumbSlug(p.href) });
                    }
                }
                return out;
            }""")
            made = 0
            for item in items:
                target = OUT / f"{item['slug']}.jpg"
                if only_missing and target.exists():
                    continue
                # A fresh page per item: hash-routed pages (#lesson/N) do not reload on goto with a new hash.
                shot = browser.new_page(viewport={"width": 1600, "height": 900})
                shot.goto(BASE + item["href"], wait_until="load")
                shot.wait_for_timeout(WAIT_MS)
                png = shot.screenshot()
                shot.close()
                img = Image.open(io.BytesIO(png)).convert("RGB")
                img = img.resize((320, round(img.height * 320 / img.width)), Image.LANCZOS)
                img.save(target, "JPEG", quality=80, optimize=True)
                made += 1
                print(f"{target.name}  <-  {item['href'][:80]}")
            browser.close()
        keep = {f"{i['slug']}.jpg" for i in items}
        stale = [f for f in OUT.glob("*.jpg") if f.name not in keep]
        for f in stale:
            f.unlink()
        print(f"{made} thumbnails written, {len(stale)} stale removed, {len(items)} pages total")
    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    main()
