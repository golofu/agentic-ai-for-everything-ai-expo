"""Copy course slides into the talk site and inline the space skin.

Re-run after the source courses change:  python scripts/apply-space-skin.py
- local Work slides (assets/motion/*, assets/html-presentation) get the skin inlined in place
- Creative menu, Vibe decks and the speaker profile pages are fetched from their live sites,
  given a <base href> back to that site for assets, and skinned
"""
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent / "cover"
SKIN = (ROOT / "assets" / "space-skin.js").read_text(encoding="utf-8")
MARK = "<!-- space-skin -->"
TAG = f"{MARK}<script>{SKIN}</script>"


def skin(html, base=None):
    html = re.sub(re.escape(MARK) + r"<script>.*?</script>", "", html, flags=re.S)
    head = re.search(r"<head[^>]*>", html, flags=re.I)
    insert = (f'<base href="{base}">' if base else "") + TAG
    return html[:head.end()] + insert + html[head.end():]


TALK_TEXT_FIXES = [('href="../assets/skills/vibe-code-skills.zip?v=2" download="vibe-code-skills.zip"', 'href="https://agentic-ai-for-everything.vercel.app/assets/skills/vibe-code-way-6-skills.zip" download="vibe-code-way-6-skills.zip"'), ('ดาวน์โหลดรวม 8 skill (ไฟล์เดียว .zip)', 'ดาวน์โหลดรวม 6 skill (ไฟล์เดียว .zip)'), ('ได้โฟลเดอร์ 8 โฟลเดอร์ + README.md', 'ได้โฟลเดอร์ 6 โฟลเดอร์ + README.md'), ('ลากทั้ง 8 โฟลเดอร์ไปวางทีเดียว', 'ลากทั้ง 6 โฟลเดอร์ไปวางทีเดียว'), ('(โหลดรวม 8 ตัว)', '(โหลดรวม 6 ตัว)'), (' ที่ Prompt บท 02 สร้างไว้ให้แล้ว', ' ที่สร้างไว้แล้ว'), ('วิธีสั่ง (prompt จริงจากบท 07)', 'วิธีสั่ง'), ('<div class="abs kick r" style="right:6cqw;top:5cqw">คอร์ส 1 วัน</div>', ''), ('<div class="kick">บท 04 · ความหมายในหน้าเดียว ·', '<div class="kick">ความหมายในหน้าเดียว ·'), ('<div class="kick">บท 04 · ติดตั้งครั้งเดียว</div>', '<div class="kick">ติดตั้งครั้งเดียว</div>'), ('VIBE CODE · บท 04 Vibe Code Way', 'VIBE CODE · Vibe Code Way'), ('<div class="kick">บท 04</div><h2', '<div class="kick">Vibe Code</div><h2'), ('มีจุดเซฟ ย้อนกลับได้ (บท 02)', 'มีจุดเซฟ ย้อนกลับได้'), ('ทำครั้งเดียวต่อเครื่อง (บท 02)', 'ทำครั้งเดียวต่อเครื่อง'), ('ได้ DESIGN.md (บท 07)', 'ได้ DESIGN.md'), ('ครั้งเดียวต่อเครื่อง ก่อนเริ่มงานแรก (ทำไปแล้วในบท 02 สไลด์ 8)', 'ครั้งเดียวต่อเครื่อง ก่อนเริ่มงานแรก'), ('"เริ่มเก็บจุดเซฟ" จากบท 02 สไลด์ 8', '"เริ่มเก็บจุดเซฟ" จากหน้าถัดไป'), (' · เรียนละเอียด + 5 ตัวอย่างเว็บ/เกมในบท 05', ''), (' วิธีละเอียด เครื่องมือ 3 ตัว และหลัก 8 ข้อ อยู่ในบท 07', ''), ('(ใน workspace บท 03 คือ BRIEF.md + SPEC.md)', '(ใน workspace คือ BRIEF.md + SPEC.md)'), ('create เซฟทุกส่วนที่ใช้ได้, push github ส่งจุดเซฟขึ้นคลาวด์', 'create เซฟทุกส่วนที่ใช้ได้'), ('ยังไม่ใช่งานเสร็จ ต้องไปขั้น test ทุกครั้ง แล้ววนกลับมา create ก้อนถัดไป', 'ยังไม่ใช่งานเสร็จ ลองใช้ก้อนนี้ให้ผ่านก่อน แล้วสั่ง create ก้อนถัดไป')]


def trim_talk_deck(html):
    """Reapply the nine-step talk edit after fetching; safe to run twice."""
    html = html.replace("14 ขั้น", "9 ขั้น").replace(" / 14", " / 9")
    html = html.replace("จาก Prompt ถึง deploy", "จาก Prompt ถึง Create")
    html = re.sub(r' *<section class="slide"[^>]*>\s*<div[^>]*><div class="kick">ขั้น (?:10|11|12|13|14) / 9</div>.*?</section>', '', html, flags=re.S)
    html = re.sub(r'<i class="[^"]*" title="(?:10|11|12|13|14) [^"]*">\d+</i>', '', html)
    html = re.sub(r'^.*<div class="vn [^"\n]*"[^\n]*<b>(?:10|11|12|13|14)</b>[^\n]*\n', '', html, flags=re.M)
    html = re.sub(r'^.*<path class="va" style="--i:(?:8|9|10|11|12|13)"[^\n]*\n', '', html, flags=re.M)
    html = re.sub(r'(<path id="vtravel" d=")[^"]*', r'\g<1>M13.8 18.0 L31.9 18.0 L50.0 18.0 L68.1 18.0 L86.2 18.0 L86.2 29.8 L68.1 29.8 L50.0 29.8 L31.9 29.8', html)
    html = re.sub(r'^.*<div class="vn end"[^\n]*\n', '', html, flags=re.M)
    html = re.sub(r'^.*<div class="row"><code>(?:scrutinize|debug-mantra)</code>[^\n]*\n', '', html, flags=re.M)
    html = html.replace('01 / 16', '01 / 12')
    for a, b in TALK_TEXT_FIXES:
        html = html.replace(a, b)
    # Preserve step 9 copy, hiding only the out-of-scope next-step indicator.
    marker = '<style id="talk-nine-steps">.slide:nth-of-type(12) .nx{display:none}</style>'
    if marker not in html:
        html = html.replace('</head>', marker + '\n</head>')
    if len(re.findall(r' *<section class="slide"', html)) != 12:
        raise ValueError('deck-04 structure changed: expected 12 talk slides')
    if len(re.findall(r'<div class="vn ', html)) != 9:
        raise ValueError('deck-04 structure changed: expected nine overview steps')
    return html


def fetch(url):
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8")


local = [p for d in ["motion", "html-presentation"] for p in (ROOT / "assets" / d).rglob("*.html")]
for path in local:
    path.write_text(skin(path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")

remote = {
    "creative/menu.html": ("https://ai-for-creative-work.vercel.app/menu.html", "https://ai-for-creative-work.vercel.app/"),
    "vibe/deck-01.html": ("https://vibe-code-weblink.vercel.app/decks/deck-01.html", "https://vibe-code-weblink.vercel.app/decks/"),
    "vibe/deck-04.html": ("https://vibe-code-weblink.vercel.app/decks/deck-04.html", "https://vibe-code-weblink.vercel.app/decks/"),
    "vibe/deck-02.html": ("https://vibe-code-weblink.vercel.app/decks/deck-02.html", "https://vibe-code-weblink.vercel.app/decks/"),
    "profile-site/index.html": ("https://handoff-profile-web.vercel.app/", "https://handoff-profile-web.vercel.app/"),
    "profile-site/ai-creative.html": ("https://handoff-profile-web.vercel.app/ai-creative.html", "https://handoff-profile-web.vercel.app/"),
    "profile-site/vibe-coding.html": ("https://handoff-profile-web.vercel.app/vibe-coding.html", "https://handoff-profile-web.vercel.app/"),
}
for target, (url, base) in remote.items():
    html = fetch(url)
    if target == "vibe/deck-04.html":
        html = trim_talk_deck(html)
    # The talk site is public, so the course copyright gate (which redirects to the course cover) is dropped here.
    html = re.sub(r'\s*<script src="assets/course-consent\.js[^"]*"></script>', "", html)
    html = html.replace("html.course-awaiting-consent { visibility: hidden; }", "")
    out = ROOT / target
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(skin(html, base), encoding="utf-8", newline="\n")

print(f"skinned {len(local)} local pages and {len(remote)} copied pages")
