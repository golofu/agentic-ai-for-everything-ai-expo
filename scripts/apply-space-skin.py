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
