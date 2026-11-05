"""Blank every embedded slide the talk menu does not show, so the talk site never hands out a full course.

Run after scripts/apply-space-skin.py and after any change to the menu page lists:
    python scripts/strip-unused.py
Slides are emptied, not deleted, so slide numbers (#lesson/N, #N) stay the same.
<style> and <script> inside a blanked slide are kept, because shared CSS/JS can live in any slide.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "cover"
menu = (ROOT / "menu.html").read_text(encoding="utf-8")

used = {}
for f, h in re.findall(r'href: "((?:creative/menu|vibe/deck-0\d)\.html)\?embed=1#([^"]+)"', menu):
    used.setdefault(f, set()).add(h)

# AI Presentation (HTML) deck: shown pages are listed in menu.html (talk cut keeps 2-13, 18 and 20-26)
deck_keep = set(range(2, 14)) | {18} | set(range(20, 27))
m = re.search(r'\.filter\(page => !\[([0-9, ]+)\]\.includes\(page\.number\)\)', menu)
if m:
    dropped = {int(x) for x in m.group(1).split(",")}
    deck_keep = (set(range(2, 20)) - dropped) | set(range(20, 27))


def keep_assets(block):
    return "".join(re.findall(r"<style\b.*?</style>|<script\b.*?</script>", block, flags=re.S))


def blank_sections(html, pattern, keep):
    """pattern matches whole slide elements; keep(index, match) -> bool"""
    counts = {}
    out, last, blanked = [], 0, 0
    for mt in re.finditer(pattern, html, flags=re.S):
        key = mt.groupdict().get("lesson") or ""
        counts[key] = counts.get(key, 0) + 1
        out.append(html[last:mt.start()])
        if keep(key, counts[key]):
            out.append(mt.group(0))
        else:
            # keep the slide's <header> (titles feed the page's own nav) and an empty .stage so page scripts keep working
            hdr = re.search(r"<header>.*?</header>", mt.group(0), flags=re.S)
            shell = (hdr.group(0) if hdr else "") + ('<div class="stage"></div>' if 'class="stage' in mt.group(0) else "")
            out.append(mt.group("open") + shell + keep_assets(mt.group(0)) + mt.group("close"))
            blanked += 1
        last = mt.end()
    out.append(html[last:])
    return "".join(out), blanked


report = []
# Creative course copy: <section class="demo" data-lesson="X"> ... </section>
p = ROOT / "creative" / "menu.html"
html = p.read_text(encoding="utf-8")
keep_c = used.get("creative/menu.html", set())
html, n = blank_sections(
    html,
    r'(?P<open><section class="demo" data-lesson="(?P<lesson>[^"]+)">)(?:(?!<section class="demo").)*?(?P<close></section>)',
    lambda lesson, i: f"{lesson}/{i}" in keep_c,
)
# the copy's "← กลับหน้าแรก" link resolves (via <base>) to the full course home: hide it
if 'id="talk-hide-home"' not in html:
    html = html.replace("</head>", '<style id="talk-hide-home">.home-link { display: none !important; }</style></head>', 1)
p.write_text(html, encoding="utf-8", newline="\n")
report.append(f"creative/menu.html: {n} slides blanked, {len(keep_c)} kept")

# Vibe decks: <section class="slide" ...> ... </section>
for name in ("deck-01", "deck-02", "deck-04"):
    p = ROOT / "vibe" / f"{name}.html"
    if not p.exists():
        continue
    keep_v = {int(x) for x in used.get(f"vibe/{name}.html", set())}
    html = p.read_text(encoding="utf-8")
    html, n = blank_sections(
        html,
        r'(?P<open><section class="slide"[^>]*>)(?:(?!<section class="slide").)*?(?P<close></section>)',
        lambda _l, i: i in keep_v,
    )
    p.write_text(html, encoding="utf-8", newline="\n")
    report.append(f"vibe/{name}.html: {n} slides blanked, {len(keep_v)} kept")

# AI Presentation (HTML) deck
p = ROOT / "assets" / "html-presentation" / "index.html"
html = p.read_text(encoding="utf-8")
html, n = blank_sections(
    html,
    r'(?P<open><section class="slide[^"]*"[^>]*>)(?:(?!<section class="slide).)*?(?P<close></section>)',
    lambda _l, i: i in deck_keep,
)
p.write_text(html, encoding="utf-8", newline="\n")
report.append(f"html-presentation: {n} slides blanked, kept {sorted(deck_keep)}")

print("\n".join(report))
