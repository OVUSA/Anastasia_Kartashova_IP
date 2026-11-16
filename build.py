#!/usr/bin/env python3
"""Static site build:  python build.py  ->  dist/  (upload that folder to the host).

Where to edit:
  content.json  all text and contacts
  style.css     appearance
  form.js       contact-form behaviour
  assets/       images
  build.py      page structure: one function per section, each returns an HTML string

dist/ is generated and wiped on every build: never edit it by hand.
"""
import datetime
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
STATIC_FILES = ("style.css", "form.js")  # copied to dist/ as-is

SITE = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
CONTACTS = SITE["contacts"]
BASE_URL = SITE["site_url"].rstrip("/") + "/"

# Yandex Metrika loader; __ID__ is replaced with the counter id.
METRIKA_SNIPPET = (
    '<script>(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};'
    "m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,"
    'a.parentNode.insertBefore(k,a)})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");'
    'ym(__ID__,"init",{clickmap:true,trackLinks:true,accurateTrackBounce:true});</script>'
)


def esc(text: str) -> str:
    """Escape text for HTML content and attribute values."""
    return html.escape(text)


# ---------- helpers ----------
def section(section_id: str, body: str, *, tight: bool = False) -> str:
    """Standard page section; `tight` drops the top padding (see .tight in style.css)."""
    css = ' class="tight"' if tight else ""
    return f'<section id="{section_id}"{css}><div class="wrap">{body}</div></section>'


def json_ld() -> str:
    """Structured data for search engines, serialised safe for embedding in <script>."""
    address = SITE["address"]
    data = {"@context": "https://schema.org", "@graph": [
        {"@type": "ProfessionalService", "name": SITE["brand"], "alternateName": SITE["legal"],
         "description": SITE["description"], "url": BASE_URL, "image": BASE_URL + "assets/logo.png",
         "email": CONTACTS["email"], "telephone": CONTACTS["phone"],
         "address": {"@type": "PostalAddress", "addressLocality": address["locality"],
                     "addressRegion": address["region"], "addressCountry": "RU"},
         "areaServed": "RU", "founder": {"@type": "Person", "name": SITE["owner"]}},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": item["q"],
             "acceptedAnswer": {"@type": "Answer", "text": item["a"]}}
            for item in SITE["faq"]]},
    ]}
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


# ---------- components ----------
def head() -> str:
    verification = SITE.get("yandex_verification")
    metrika_id = SITE.get("metrika_id")
    verification_tag = f'<meta name="yandex-verification" content="{esc(verification)}">' if verification else ""
    metrika_tag = METRIKA_SNIPPET.replace("__ID__", str(int(metrika_id))) if metrika_id else ""
    return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(SITE["title"])}</title>
<meta name="description" content="{esc(SITE["description"])}">
<meta name="keywords" content="{esc(SITE["keywords"])}">
<link rel="canonical" href="{BASE_URL}">
<meta name="theme-color" content="#093a26">
<meta property="og:type" content="website"><meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{esc(SITE["title"])}"><meta property="og:description" content="{esc(SITE["description"])}">
<meta property="og:url" content="{BASE_URL}"><meta property="og:image" content="{BASE_URL}assets/logo.png">
{verification_tag}
<link rel="icon" type="image/png" href="assets/favicon.png">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">{json_ld()}</script>
{metrika_tag}</head>'''


def nav() -> str:
    cfg = SITE["nav"]
    links = "".join(f'<li><a href="#{item["target"]}">{esc(item["label"])}</a></li>' for item in cfg["items"])
    return f'''<header class="nav"><div class="wrap"><a class="brand" href="#top"><img src="assets/mark.png" alt="" width="34" height="34">{esc(SITE["brand"])}</a>
<nav aria-label="{esc(cfg["aria"])}"><ul>{links}</ul></nav></div></header>'''


def hero() -> str:
    cfg = SITE["hero"]
    return f'''<section class="hero" id="top"><div class="wrap">
<img src="assets/logo.png" alt="{esc(cfg["logo_alt"])}" width="300" height="340">
<h1>{esc(cfg["h1"])}</h1><p>{esc(cfg["lead"])}</p>
<div class="actions"><a class="btn" href="#contact">{esc(cfg["cta"])}</a><a class="btn ghost" href="#services">{esc(cfg["cta2"])}</a></div></div></section>'''


def service_card(service: dict) -> str:
    points = "".join(f"<li>{esc(p)}</li>" for p in service["points"])
    dark = " dark" if service.get("dark") else ""
    return (f'<article class="card{dark}" id="{service["id"]}"><h3>{esc(service["title"])}</h3>'
            f'<p class="muted">{esc(service["text"])}</p><ul>{points}</ul></article>')


def services() -> str:
    cards = "".join(service_card(s) for s in SITE["services"])
    return section("services", f'<h2>{esc(SITE["services_title"])}</h2><div class="grid">{cards}</div>')


def cases() -> str:
    items = "".join(f'<li class="case">{esc(c)}</li>' for c in SITE["cases"])
    return section("cases", f'''<h2>{esc(SITE["cases_title"])}</h2>
<ul class="cases">{items}</ul><p class="note muted">{esc(SITE["cases_note"])}</p>''', tight=True)


def about() -> str:
    cfg = SITE["about"]
    paragraphs = "".join(f"<p>{esc(p)}</p>" for p in cfg["paragraphs"])
    links = "".join(f'<a href="{esc(link["url"])}" target="_blank" rel="noopener">{esc(link["label"])}</a>'
                    for link in cfg["links"])
    photo_alt = f'{SITE["owner"]}, {SITE["brand"]}'
    return section("about", f'''<div class="about"><img src="assets/mark.png" alt="{esc(photo_alt)}" width="340" height="332" loading="lazy">
<div><h2>{esc(cfg["title"])}</h2>{paragraphs}
<div class="charity"><h3>{esc(cfg["charity_title"])}</h3><p class="muted">{esc(cfg["charity"])}</p><div class="links">{links}</div></div></div></div>''')


def faq() -> str:
    items = "".join(f'<details><summary>{esc(item["q"])}</summary><p>{esc(item["a"])}</p></details>'
                    for item in SITE["faq"])
    return section("faq", f'<h2>{esc(SITE["faq_title"])}</h2>{items}', tight=True)


def contact_form() -> str:
    """Either a Yandex Forms iframe, or our own form handled by form.js."""
    cfg = SITE["form"]
    if cfg.get("yandex_forms_url"):
        return (f'<iframe class="yform" src="{esc(cfg["yandex_forms_url"])}" '
                f'title="{esc(cfg["title"])}" loading="lazy" frameborder="0"></iframe>')

    if not cfg.get("endpoint"):
        print("WARNING: content.json -> form has neither endpoint nor yandex_forms_url; "
              "the form will not send anything.", file=sys.stderr)

    if "web3forms" in cfg["endpoint"] and not cfg.get("access_key"):
        print("WARNING: content.json -> form.endpoint is Web3Forms but form.access_key is empty; "
              "Web3Forms will reject every submission.", file=sys.stderr)

    access_key = (f'<input type="hidden" name="access_key" value="{esc(cfg["access_key"])}">'
                  if cfg.get("access_key") else "")
    messages = json.dumps({key: cfg[key] for key in ("sending", "success", "error", "button")},
                          ensure_ascii=False)
    return f'''<form class="cform" id="cform" action="{esc(cfg.get("endpoint", ""))}" method="POST" data-msgs="{esc(messages)}">
{access_key}<input type="hidden" name="subject" value="Заявка с сайта {esc(SITE["brand"])}">
<label>{esc(cfg["name_label"])}<input name="name" type="text" autocomplete="name" required maxlength="120"></label>
<label>{esc(cfg["email_label"])}<input name="email" type="email" autocomplete="email" required maxlength="200"></label>
<label>{esc(cfg["message_label"])}<textarea name="message" rows="5" required maxlength="4000"></textarea></label>
<input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true"><input class="hp" type="checkbox" name="botcheck" tabindex="-1" aria-hidden="true">
<button class="btn" type="submit">{esc(cfg["button"])}</button><p class="fstatus" role="status" aria-live="polite"></p></form>
<script src="form.js" defer></script>'''


def contact() -> str:
    title = esc(SITE["form"]["title"])
    return section("contact", f'<div class="contact"><h2>{title}</h2>\n{contact_form()}\n</div>', tight=True)


def footer() -> str:
    year = datetime.date.today().year
    return f'''<footer><div class="wrap"><p>{esc(SITE["legal"])} · {esc(SITE["legal_extra"])}</p><p>{esc(SITE["city"])} · {esc(CONTACTS["phone"])}</p><p>© {year} {esc(SITE["brand"])}</p></div></footer>'''


# ---------- build ----------
def render_page() -> str:
    sections = hero() + services() + cases() + about() + faq() + contact()
    return head() + "<body>" + nav() + "<main>" + sections + "</main>" + footer() + "</body></html>"


def robots_txt() -> str:
    return f"User-agent: *\nAllow: /\nHost: {BASE_URL}\nSitemap: {BASE_URL}sitemap.xml\n"


def sitemap_xml() -> str:
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"<url><loc>{BASE_URL}</loc><lastmod>{datetime.date.today()}</lastmod></url></urlset>\n")


def build() -> None:
    for required in (*STATIC_FILES, "assets"):
        if not (ROOT / required).exists():
            sys.exit(f"ERROR: '{required}' is missing from the project folder. "
                     "Make sure it was uploaded to the repository.")

    # Render first: if a section fails, the previous dist/ is left untouched.
    page = render_page()

    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(exist_ok=True)  # may survive rmtree if a local server is running inside it
    (DIST / "index.html").write_text(page, encoding="utf-8")
    (DIST / "robots.txt").write_text(robots_txt(), encoding="utf-8")
    (DIST / "sitemap.xml").write_text(sitemap_xml(), encoding="utf-8")
    for name in STATIC_FILES:
        shutil.copy(ROOT / name, DIST / name)
    shutil.copytree(ROOT / "assets", DIST / "assets", dirs_exist_ok=True)


def warn_about_placeholders() -> None:
    if "example" in SITE["site_url"]:
        print("WARNING: content.json -> site_url is still a placeholder; "
              "canonical link, sitemap and og:url will point to the wrong address.", file=sys.stderr)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy codepage
    sys.stderr.reconfigure(encoding="utf-8")
    warn_about_placeholders()
    build()
    print(f"Done: {DIST / 'index.html'}")


if __name__ == "__main__":
    main()
