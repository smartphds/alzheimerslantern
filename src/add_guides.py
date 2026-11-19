"""Turn src/guides/*.md into guide pages inside src/preview.html.

Each .md file starts with 'key: value' lines, then a line '---', then the body.
Keys: slug, title, category, blurb, lede, minutes, tag (optional), reviewed.
Body: '## heading', '- bullet', blank-line paragraphs, **bold**, *italic*, [text](link).
Links to other guides use [text](#slug). Run, then run build.py.
"""
import re, json, glob, html, sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(ROOT, "preview.html")

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s

def body_html(md):
    out, para, items = [], [], []
    def flush():
        nonlocal para, items
        if para: out.append(f"<p>{inline(' '.join(para))}</p>"); para = []
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"); items = []
    sources = False
    for line in md.splitlines():
        l = line.rstrip()
        if not l.strip(): flush(); continue
        if l.startswith("## "):
            flush(); h = l[3:].strip()
            if h.lower() == "sources":
                sources = True; out.append('<h2 class="h3">Sources</h2>')
            else: out.append(f"<h2>{inline(h)}</h2>")
        elif l.startswith("- "):
            if para: flush()
            items.append(l[2:].strip())
        else:
            if items: flush()
            para.append(l.strip())
    flush()
    h = "\n        ".join(out)
    return h.replace('<h2 class="h3">Sources</h2>\n        <ul>', '<h2 class="h3">Sources</h2>\n        <ul class="sources">')

def parse(path):
    raw = open(path).read()
    head, body = raw.split("\n---\n", 1)
    meta = dict(l.split(": ", 1) for l in head.strip().splitlines())
    return meta, body

def view(m, body):
    return f'''  <!-- GUIDE -->
  <div data-view="{m['slug']}" hidden>
    <section>
      <article class="inner stack read article">
        <p class="crumb"><a href="#guides">Free guides</a> › {html.escape(m['category'])}</p>
        <h1>{html.escape(m['title'])}</h1>
        <p class="lede muted">{inline(m['lede'])}</p>
        <p class="muted byline">By the Alzheimer's Lantern team · Last reviewed {m.get('reviewed','November 19, 2026')} · {m['minutes']}-minute read</p>
        <p class="notice"><strong>We are not medical professionals.</strong> This guide is general information, not medical advice. Please talk to a doctor about your own situation. In an emergency, call 911. <a href="#disclaimer">Read our full disclaimer</a>.</p>
        {body_html(body)}
        <p class="muted">Want calm, practical help like this every week? <a href="#friday-letter">Get the Friday letter</a>. It's free.</p>
      </article>
    </section>
  </div>'''

src = open(PREV).read()
files = sorted(glob.glob(os.path.join(ROOT, "guides", "*.md")))
guides = [parse(f) for f in files]
block = "  <!-- GUIDES BEGIN -->\n" + "\n".join(view(m, b) for m, b in guides) + "\n  <!-- GUIDES END -->"
if "<!-- GUIDES BEGIN -->" in src:
    src = re.sub(r"  <!-- GUIDES BEGIN -->.*?  <!-- GUIDES END -->", lambda _: block, src, flags=re.S)
else:
    src = src.replace("\n  <!-- DISCLAIMER -->", "\n" + block + "\n  <!-- DISCLAIMER -->", 1)

# CATS: link existing entries by title, add new ones to their category
a = src.index("const CATS = ") + len("const CATS = "); b = src.index("];", a) + 1
js = re.sub(r'(\{\s*|,\s*)(title|blurb|guides):', r'\1"\2":', src[a:b])
cats = json.loads(js)
for m, _ in guides:
    cat = next((c for c in cats if c["title"] == m["category"]), None)
    if cat is None:
        cat = {"title": m["category"], "blurb": m.get("catblurb", ""), "guides": []}; cats.append(cat)
    g = next((g for c in cats for g in c["guides"] if g[0] == m["title"]), None)
    if g is None:
        cat["guides"].append([m["title"], m["blurb"], m.get("tag", ""), m["slug"]])
    else:
        g[:] = [g[0], m.get("blurb", g[1]), m.get("tag", g[2]), m["slug"]]
lines = []
for c in cats:
    gl = ",\n".join("    " + json.dumps(g, ensure_ascii=False) for g in c["guides"])
    lines.append(f'  {{ title: {json.dumps(c["title"], ensure_ascii=False)}, blurb: {json.dumps(c["blurb"], ensure_ascii=False)}, guides: [\n{gl} ]}}')
src = src[:a] + "[\n" + ",\n".join(lines) + "\n]" + src[b:]
# routing list
pages = re.findall(r'data-view="([\w-]+)"', src)
src = re.sub(r"const PAGES = \[.*?\];", "const PAGES = " + json.dumps(list(dict.fromkeys(pages))) + ";", src, count=1)
open(PREV, "w").write(src)
print(f"{len(guides)} guides written")
