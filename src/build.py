import re, os, sys, shutil, html
SRC = sys.argv[1]; OUT = sys.argv[2]
src = open(SRC).read()
css = src.split("<style>",1)[1].split("</style>",1)[0]
symbol = re.search(r'<symbol id="lantern".*?</symbol>', src, re.S).group(0)
DOMAIN = "https://alzheimerslantern.com"
NAME = "Alzheimer's Lantern"

# views
views = {}
for m in re.finditer(r'<div data-view="([\w-]+)"[^>]*>(.*?)(?=\n  <!-- [A-Z ]+ -->|\n</main>)', src, re.S):
    body = m.group(2).rstrip()
    assert body.endswith("</div>"), m.group(1)
    views[m.group(1)] = body[:-6]
LINKS = {"#home":"/","#guides":"/guides/","#membership":"/membership/","#about":"/about/","#friday-letter":"/friday-letter/","#disclaimer":"/disclaimer/","#what-is-alzheimers":"/guides/what-is-alzheimers/","#what-is-dementia":"/guides/what-is-dementia/"}
def fix(s):
    for k,v in LINKS.items(): s = s.replace(f'href="{k}"', f'href="{v}"')
    s = s.replace('<span data-name>The Caring Lantern</span>', NAME).replace("<span data-name>Alzheimer's Lantern</span>", NAME)
    return s

HELP = """<h2 class="h3">Need help right now?</h2>
<ul>
<li>Alzheimer's Association 24/7 Helpline: <span class="num">1-800-272-3900</span></li>
<li>Eldercare Locator, to find local services: <span class="num">1-800-677-1116</span></li>
<li>If you're overwhelmed or in emotional crisis, call or text <span class="num">988</span></li>
<li>If someone is lost, hurt, or in danger, call <span class="num">911</span></li>
</ul>"""

CATS = [
  ("Understanding Alzheimer's", "What's happening in the brain, the stages, and how diagnosis works.", [
    ("What is Alzheimer's disease?", "What it does to the brain, early signs, stages, and treatment, in plain English.", "", "/guides/what-is-alzheimers/"),
    ("What is dementia?", "What the word really means, how it differs from Alzheimer's, and the main types.", "", "/guides/what-is-dementia/"),
    ("10 early signs of Alzheimer's", "How to tell everyday forgetfulness from warning signs, with a printable checklist.", "Printable"),
    ("The stages, explained simply", "What early, middle, and late stage usually look like, and what helps at each.", ""),
    ("MCI or dementia: what's the difference?", "Mild cognitive impairment, what it means, and what to watch for.", ""),
    ("New Alzheimer's treatments in plain English", "What the newer drugs do, who they're for, and questions to ask.", "")]),
  ("Just diagnosed", "The first weeks after a diagnosis, for the person and the family.", [
    ("Your first 30 days after a diagnosis", "A week-by-week list of calls, paperwork, and conversations.", "Printable"),
    ("Questions to ask the doctor", "A one-page list to bring to the next appointment.", "Printable"),
    ("Telling family and friends", "Who to tell, when, and words that make it easier.", "")]),
  ("Daily care", "Bathing, eating, sleep, and the moments that are hardest.", [
    ("Sundowning: why evenings are hard", "Simple changes to light, routine, and noise that calm late-day confusion.", ""),
    ("Bathing without a battle", "Step-by-step ways to make bath time safer and less upsetting.", ""),
    ("What to say when they ask for someone who has died", "Kind answers that comfort instead of reopening grief.", ""),
    ("Communication that works", "Short sentences, one choice at a time, and other tested techniques.", "")]),
  ("Safety", "Always free. Wandering, driving, falls, and when to call for help.", [
    ("Wandering: prevention and what to do", "Steps to take today, and exactly what to do if someone goes missing.", "Always free"),
    ("When to stop driving", "Warning signs, and how to have the conversation.", "Always free"),
    ("Home safety, room by room", "A walk-through checklist for kitchen, bathroom, stairs, and doors.", "Printable")]),
  ("Money and legal", "Planning ahead while your loved one can still take part.", [
    ("Power of attorney and advance directives", "What each document does and when to set them up.", ""),
    ("Paying for care: Medicare and Medicaid basics", "What's covered, what isn't, and where to get free advice.", ""),
    ("Home care, assisted living, or memory care?", "How the options compare in care level and typical cost.", "")]),
  ("Caring for yourself", "You matter too. Rest, support, and asking for help.", [
    ("Caregiver burnout: signs and first steps", "How to notice it early, and small ways to get relief.", ""),
    ("Finding respite care", "Adult day programs, in-home help, and short stays.", ""),
    ("Support groups near you and online", "Where to find people who understand.", "")]),
]
def guide(g, h="h3"):
    t,d,tag = g[:3]; link = g[3] if len(g)>3 else ""
    pill = f'<span class="pill{" free" if tag=="Always free" else ""}">{tag}</span>' if tag else ""
    if link: return f'<article class="guide"><{h}><a href="{link}">{html.escape(t)}</a></{h}><p class="muted">{html.escape(d)}</p><p class="meta">{pill}<a href="{link}">Read now</a></p></article>'
    return f'<article class="guide"><{h}>{html.escape(t)}</{h}><p class="muted">{html.escape(d)}</p><p class="meta">{pill}Coming soon</p></article>'

def page(slug, title, desc, body):
    path = "/" if slug=="home" else f"/{slug}/"
    nav = "".join(f'<a href="{u}"{" aria-current=\"page\"" if s==slug else ""}{" class=\"cta\"" if s=="friday-letter" else ""}>{l}</a>'
        for s,u,l in [("home","/","Home"),("guides","/guides/","Free guides"),("membership","/membership/","Membership"),("about","/about/","About"),("friday-letter","/friday-letter/","Get the Friday letter")])
    full_title = NAME if slug=="home" else f"{title} | {NAME}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{DOMAIN}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{html.escape(NAME)}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{DOMAIN}{path}">
<meta property="og:image" content="{DOMAIN}/assets/social-card.png">
<meta name="theme-color" content="#5b2a86">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap">
<link rel="stylesheet" href="/assets/style.css">
<script>try{{if(localStorage.getItem("bigText")==="1")document.documentElement.classList.add("big")}}catch(e){{}}</script>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{symbol}</defs></svg>
<a class="skip" href="#main">Skip to main content</a>
<header class="site-head">
  <div class="inner">
    <a class="brand" href="/"><svg aria-hidden="true"><use href="#lantern"/></svg><span>{NAME}</span></a>
    <button class="menu-btn" id="menuBtn" type="button" aria-expanded="false" aria-controls="mainnav"><span class="bars" aria-hidden="true"></span>Menu</button>
    <nav class="nav" id="mainnav" aria-label="Main">{nav}
      <button class="textsize" id="textsize" type="button" aria-pressed="false">A+ Larger text</button>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
  <div class="inner">
    <div class="stack" style="gap:10px">
      <a class="brand" href="/"><svg aria-hidden="true"><use href="#lantern"/></svg><span>{NAME}</span></a>
      <p class="muted">We are not medical professionals. Everything on this site is general information, not medical advice. Always talk to your doctor. In an emergency, call 911. <a href="/disclaimer/">Read our full disclaimer</a>.</p>
      <p class="muted">{NAME} is an independent site and is not affiliated with the Alzheimer's Association or any other organization.</p>
      <p>Alzheimer's Association 24/7 Helpline: <span class="num">1-800-272-3900</span> (US). In an emergency, call <span class="num">911</span>.</p>
    </div>
    <div>
      <h2 class="h3">Explore</h2>
      <ul><li><a href="/guides/">Free guides</a></li><li><a href="/membership/">Membership</a></li><li><a href="/about/">About us</a></li><li><a href="/friday-letter/">Friday letter</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/disclaimer/">Disclaimer</a></li></ul>
    </div>
    <div>
      <h2 class="h3">Follow along</h2>
      <ul class="social">
        <li><a data-social="facebook" href="#">Facebook</a></li>
        <li><a data-social="instagram" href="#">Instagram</a></li>
        <li><a data-social="tiktok" href="#">TikTok</a></li>
        <li><a data-social="substack" href="#">Substack</a></li>
      </ul>
      <p class="fine" style="margin-top:12px">&copy; <span id="yr">2026</span> {NAME}</p>
    </div>
  </div>
</footer>
<script src="/assets/site.js"></script>
</body>
</html>
"""

pages = {}
# HOME
home = fix(views["home"])
home = re.sub(r'<div class="guides" id="homeGuides"></div>', '<div class="guides">' + "".join(guide(g) for g in [CATS[0][2][0],CATS[1][2][0],CATS[2][2][0],CATS[3][2][0]]) + '</div>', home)
home = home.replace('<div class="help" data-help></div>', f'<div class="help">{HELP}</div>')
pages["home"] = ("Home", "Plain-language Alzheimer's guides, printable checklists, and a calm letter every Friday for families, caregivers, and people living with a diagnosis.", home)
# GUIDES
g = fix(views["guides"]).replace('<div class="help" data-help></div>', f'<div class="help">{HELP}</div>')
cats = "".join(f'<div><div class="cat-head"><h2>{html.escape(t)}</h2><p class="muted">{html.escape(b)}</p></div><div class="guides">{"".join(guide(x) for x in gs)}</div></div>' for t,b,gs in CATS)
g = g.replace('<div class="inner cats" id="cats"></div>', f'<div class="inner cats">{cats}</div>')
pages["guides"] = ("Free guides", "Free, plain-language Alzheimer's guides on early signs, diagnosis, daily care, safety, money and legal planning, and caregiver self-care.", g)
pages["membership"] = ("Membership", "Alzheimer's Lantern membership opens in 2027: care planners, symptom and medication logs, family sharing, courses, and live expert Q&A.", fix(views["membership"]))
pages["about"] = ("About", "Why we built Alzheimer's Lantern, how we write and review our guides, and what we promise families.", fix(views["about"]))
fl = fix(views["friday-letter"])
fl = fl.replace('<form class="card" id="signup" novalidate>', '<form class="card" id="signup" novalidate data-endpoint="">')
pages["friday-letter"] = ("The Friday letter", "Get one calm, useful Alzheimer's letter every Friday evening: practical tips, research in plain English, and printable checklists. Free.", fl)
pages["privacy"] = ("Privacy", "How Alzheimer's Lantern handles your email address and personal information.", """
    <section>
      <div class="inner stack read">
        <h1>Privacy</h1>
        <p class="muted">Last updated November 18, 2026</p>
        <h2>What we collect</h2>
        <p>When you sign up for the Friday letter, we collect your first name (optional), your email address, and, if you choose, whether you are a caregiver, living with a diagnosis, or a care professional. We use this only to send you the letter and to choose helpful topics.</p>
        <h2>What we never do</h2>
        <p>We never sell or rent your email address. We don't put advertising trackers on this site. We don't ask for health details about you or your family on this site.</p>
        <h2>Who handles your email</h2>
        <p>Our letters are sent through an email service provider that stores your address on our behalf. Every letter has an unsubscribe link, and unsubscribing removes you from future letters right away.</p>
        <h2>Your choices</h2>
        <p>You can ask us to show, correct, or delete the information we hold about you at any time by replying to any Friday letter.</p>
        <h2>Changes</h2>
        <p>If we change this policy, we'll update the date above and mention it in the Friday letter.</p>
      </div>
    </section>""")
pages["disclaimer"] = ("Disclaimer", "We are not medical professionals. Alzheimer's Lantern shares general information, not medical advice. Always talk to your doctor.", fix(views["disclaimer"]))
for slug, title, desc in [("what-is-alzheimers","What is Alzheimer's disease?","A plain-English guide to Alzheimer's disease: what it does to the brain, early signs, stages, risk factors, diagnosis, and treatment."),("what-is-dementia","What is dementia?","What dementia really means, how it differs from Alzheimer's, the main types, and treatable causes of memory problems, in plain English.")]:
    pages["guides/"+slug] = (title, desc, fix(views[slug]).replace('<div class="help" data-help></div>', f'<div class="help">{HELP}</div>'))
pages["404"] = ("Page not found", "This page could not be found.", """
    <section>
      <div class="inner stack read">
        <h1>We couldn't find that page</h1>
        <p class="lede muted">It may have moved, or the link may have a typo.</p>
        <div class="btns"><a class="btn primary" href="/">Go to the home page</a><a class="btn ghost" href="/guides/">Browse free guides</a></div>
      </div>
    </section>""")

if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT+"/assets")
for slug,(t,d,b) in pages.items():
    if slug=="home": p=OUT+"/index.html"
    elif slug=="404": p=OUT+"/404.html"
    else:
        os.makedirs(f"{OUT}/{slug}", exist_ok=True); p=f"{OUT}/{slug}/index.html"
    open(p,"w").write(page(slug,t,d,b))

# CSS: strip preview-only bits, add skip link + .h3 + social
css = re.sub(r'/\* draft ribbon \*/.*?\n\.draft \.inner[^\n]*\n', '', css, flags=re.S)
css += """
.skip { position: absolute; left: -9999px; top: 0; background: var(--plum); color: var(--on-plum); padding: 10px 16px; z-index: 20; border-radius: 0 0 8px 0; }
.skip:focus { left: 0; }
.h3 { font-family: var(--display); font-weight: 600; font-size: 1.05rem; margin: 0 0 8px; }
.help .h3 { font-size: 1.3rem; }
.social a[aria-disabled="true"] { color: var(--muted); text-decoration: none; }
"""
open(OUT+"/assets/style.css","w").write(css.strip()+"\n")
