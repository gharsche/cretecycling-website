#!/usr/bin/env python3
"""Baut die Rechtstexte-Unterseiten aus docs/{,en,el}/*.md nach website/*.html.

    python3 scripts/build_legal.py

Quelle der Wahrheit sind die Markdown-Dateien: docs/*.md (DE), docs/en/*.md (EN),
docs/el/*.md (EL). Jede Seite enthält drei .lang-doc-Blöcke plus den
Sprach-Umschalter (Chips + Inline-JS inkl. Hash-Mapping #agb -> #agb-en/-el).
Der Umschalter ist Teil dieses Skripts, ein erneuter Lauf ist verlustfrei
(idempotent) — HTML-Handarbeit an den Blöcken geht sonst verloren, Änderung
immer in den .md-Quellen machen.
Das CSS stammt aus website/index.html (<style>-Block), plus Zusatzregeln für
Fließtext, Tabellen und die feste Chip-Optik auf hellem Grund.
Bei DRAFT=True werden Platzhalter-Hinweise sichtbar angezeigt; vor dem
Livegang auf False setzen (dann bricht das Skript bei offenen [Platzhaltern] ab).
"""
import html, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS, WEB = ROOT / "docs", ROOT / "website"
DRAFT = False
LANGS = ["de", "en", "el"]

CHROME = {
    "de": {"docAria": "Rechtstexte"},
    "en": {"docAria": "Legal documents"},
    "el": {"docAria": "Νομικά έγγραφα"},
}

PAGES = [
    dict(file="impressum-datenschutz.html", title="Impressum & Datenschutz",
         sources=["impressum", "datenschutz"],
         eyebrow={"de": "Rechtliches", "en": "Legal", "el": "Νομικά"},
         h1={"de": "Impressum & Datenschutz", "en": "Imprint & Privacy Policy",
             "el": "Στοιχεία Εταιρείας & Πολιτική Απορρήτου"},
         titles={"de": "\U0001F434 Impressum & Datenschutz — CreteCycling",
                 "en": "\U0001F434 Imprint & Privacy Policy — CreteCycling",
                 "el": "\U0001F434 Στοιχεία Εταιρείας & Πολιτική Απορρήτου — CreteCycling"},
         labels={"de": {"impressum": "Impressum", "datenschutz": "Datenschutz"},
                 "en": {"impressum": "Legal notice", "datenschutz": "Privacy policy"},
                 "el": {"impressum": "Στοιχεία εταιρείας", "datenschutz": "Πολιτική απορρήτου"}}),
    dict(file="agb-storno.html", title="AGB & Stornobedingungen",
         sources=["agb", "stornobedingungen"],
         eyebrow={"de": "Rechtliches", "en": "Legal", "el": "Νομικά"},
         h1={"de": "AGB & Stornobedingungen", "en": "Terms & Cancellation Policy",
             "el": "Όροι Χρήσης & Πολιτική Ακύρωσης"},
         titles={"de": "\U0001F434 AGB & Stornobedingungen — CreteCycling",
                 "en": "\U0001F434 Terms & Cancellation Policy — CreteCycling",
                 "el": "\U0001F434 Όροι Χρήσης & Πολιτική Ακύρωσης — CreteCycling"},
         labels={"de": {"agb": "AGB", "stornobedingungen": "Stornobedingungen"},
                 "en": {"agb": "Terms and conditions", "stornobedingungen": "Cancellation policy"},
                 "el": {"agb": "Γενικοί Όροι", "stornobedingungen": "Όροι Ακύρωσης"}}),
]

def md_path(src, lang):
    return (DOCS if lang == "de" else DOCS / lang) / f"{src}.md"

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
               r'<a href="\2" rel="noopener" target="_blank">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"(?<![\w>@/])([\w.+-]+@[\w-]+\.[\w.]+)",
               r'<a href="mailto:\1">\1</a>', t)
    t = re.sub(r"\[([^\]\n]+)\](?!\()", r'<mark class="ph">[\1]</mark>', t)
    return t

def slug(s):
    # Konvention der ausgelieferten Seiten: griechische Akzente werden
    # entfernt (πεδίο->πεδιο), deutsche Umlaute bleiben (übergabe).
    s = s.lower()
    out = []
    for ch in s:
        if 0x370 <= ord(ch) <= 0x3FF:
            d = unicodedata.normalize("NFD", ch)
            ch = "".join(c for c in d if not unicodedata.combining(c))
        out.append(ch)
    s = re.sub(r"[^\w\s-]", "", "".join(out)).strip()
    return re.sub(r"\s+", "-", s)

def render(md, prefix):
    out, lines, i = [], md.splitlines(), 0
    ids = set()
    while i < len(lines):
        ln = lines[i]
        if not ln.strip() or ln.strip() == "---":
            i += 1; continue
        m = re.match(r"(#{1,3}) (.+)", ln)
        if m:
            lvl = len(m.group(1)) + 1
            txt = m.group(2)
            hid = prefix if lvl == 2 else f"{prefix}-{slug(txt)}"[:60]
            while hid in ids: hid += "-x"
            ids.add(hid)
            out.append(f'<h{lvl} id="{hid}">{inline(txt)}</h{lvl}>'); i += 1; continue
        if ln.startswith(">"):
            blk = []
            while i < len(lines) and lines[i].startswith(">"):
                blk.append(lines[i].lstrip("> ").strip()); i += 1
            if DRAFT:
                out.append('<aside class="draft"><b>Entwurf:</b> ' + inline(" ".join(blk)) + "</aside>")
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[2:]]
            t = ['<div class="tbl"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
            for r in body:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append("".join(t) + "</tbody></table></div>"); continue
        if re.match(r"(- |\d+\. )", ln):
            ordered = ln[0].isdigit(); items = []
            while i < len(lines) and re.match(r"(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i])); i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        para = []
        while i < len(lines) and lines[i].strip() and lines[i].strip() != "---" \
                and not re.match(r"(#|>|\||- |\d+\. )", lines[i]):
            para.append(lines[i].strip()); i += 1
        out.append("<p>" + "<br>".join(inline(p) for p in para) + "</p>")
    return "\n".join(out)

I18N_JS = """<script>
(function(){
  var TITLES = __TITLES__;
  var BOOK = {de:"Jetzt buchen", en:"Book now", el:"Κλείστε τώρα"};
  var LABEL = {de:"Sprache", en:"Language", el:"Γλώσσα"};
  function norm(x){ x=(x||"de").slice(0,2).toLowerCase(); return (x==="en"||x==="el")?x:"de"; }
  function pick(){
    var q = norm(new URLSearchParams(location.search).get("lang"));
    if (q) return q;
    return norm(localStorage.getItem("cc-lang") || navigator.language);
  }
  function apply(lang){
    var blocks = document.querySelectorAll(".lang-doc");
    var target = document.querySelector('.lang-doc[data-lang="'+lang+'"]');
    if (target && target.textContent.trim().length < 50) lang = "de"; // placeholder not filled yet
    blocks.forEach(function(b){ b.hidden = b.getAttribute("data-lang") !== lang; });
    document.documentElement.lang = lang === "el" ? "el" : lang;
    document.title = TITLES[lang];
    var book = document.getElementById("bookCta"); if (book) book.textContent = BOOK[lang];
    var grp = document.querySelector(".lang-switch"); if (grp) grp.setAttribute("aria-label", LABEL[lang]);
    document.querySelectorAll(".lang-switch button").forEach(function(b){
      b.setAttribute("aria-pressed", String(b.dataset.lang === lang)); });
    localStorage.setItem("cc-lang", lang);
    var h = location.hash.slice(1);
    if (h) { var base = h.replace(/-(de|en|el)$/, ""); var want = lang === "de" ? base : base + "-" + lang; if (h !== want && document.getElementById(want)) history.replaceState(null, "", "#" + want); }
    history.replaceState(null, "", location.pathname + (lang === "de" ? "" : "?lang=" + lang) + location.hash);
  }
  document.querySelectorAll(".lang-switch button").forEach(function(b){
    b.addEventListener("click", function(){ apply(b.dataset.lang); }); });
  apply(pick());
})();
</script>"""

EXTRA_CSS = """
header.nav{background:rgba(246,236,214,.96);backdrop-filter:blur(10px);box-shadow:0 1px 0 rgba(74,46,26,.14)}
header.nav .logo{color:var(--umber)} header.nav .logo b{color:var(--terra)}
.doc{padding:7rem 0 4rem}
.doc .wrap{width:min(820px,92%)}
.doc .doclinks{display:flex;gap:.6rem;flex-wrap:wrap;margin:1rem 0 2.5rem}
.doc .doclinks a{padding:.5rem 1.1rem;border-radius:999px;background:#fff;border:1.5px solid #d8c49a;text-decoration:none;font-weight:700;font-size:.92rem;color:var(--terra-d)}
.doc .doclinks a:hover{border-color:var(--terra)}
.doc section{background:#fff;border-radius:var(--r);box-shadow:var(--shadow);padding:clamp(1.4rem,4vw,2.6rem);margin-bottom:2rem;scroll-margin-top:90px}
.doc h2{font-size:clamp(1.6rem,3.5vw,2.2rem);color:var(--terra-d);margin-bottom:1rem}
.doc h3{font-size:1.2rem;margin:1.8rem 0 .5rem;color:var(--olive-d)}
.doc h4{font-size:1.02rem;margin:1.2rem 0 .4rem}
.doc p,.doc ul,.doc ol{margin:.6rem 0}
.doc ul,.doc ol{padding-left:1.4rem}
.doc li{margin:.25rem 0}
.doc .tbl{overflow-x:auto;margin:1rem 0}
.doc table{border-collapse:collapse;width:100%;font-size:.95rem}
.doc th,.doc td{text-align:left;padding:.55rem .8rem;border-bottom:1px solid var(--sand-d)}
.doc th{background:var(--sand);font-size:.82rem;text-transform:uppercase;letter-spacing:.05em;color:var(--mute)}
.doc a{color:var(--terra-d)}
.doc code{background:var(--sand);padding:.1em .35em;border-radius:6px}
mark.ph{background:#f6dc9a;color:#4a2e1a;padding:0 .25em;border-radius:5px}
aside.draft{background:#f6e7bd;border-left:5px solid var(--ochre);padding:.7rem 1rem;border-radius:10px;margin:1rem 0;font-size:.9rem}
.lang-switch button{border:1px solid rgba(74,46,26,.25);background:#fff;color:var(--umber);border-radius:999px;padding:.5rem .95rem;min-height:2.4rem;font:inherit;font-weight:800;font-size:.92rem;letter-spacing:.02em;cursor:pointer;line-height:1}
.lang-switch button[aria-pressed="true"]{background:var(--ochre);border-color:var(--ochre);color:#3a2616}
"""

def main():
    index = (WEB / "index.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
    favicon = re.search(r'<link rel="icon"[^>]+>', index).group(0)
    logo_svg = re.search(r'<a class="logo"[^>]*>\s*(<svg.*?</svg>|<img[^>]*>)', index, re.S).group(1)
    extra = EXTRA_CSS + ("" if DRAFT else "aside.draft{display:none}")
    chips = ('<div class="lang-switch" role="group" aria-label="Sprache">'
             '<button type="button" data-lang="de" aria-pressed="true">DE</button>'
             '<button type="button" data-lang="en" aria-pressed="false">EN</button>'
             '<button type="button" data-lang="el" aria-pressed="false">EL</button></div>')
    nav = ('<header class="nav"><div class="wrap">'
           f'<a class="logo" href="index.html" aria-label="CreteCycling Startseite">{logo_svg}<span>Crete<b>Cycling</b></span></a>'
           f'{chips}<a class="btn btn-ochre" id="bookCta" href="index.html#kontakt">Jetzt buchen</a></div></header>')
    open_ph = []
    for p in PAGES:
        blocks = []
        for lang in LANGS:
            secs, tabs = [], []
            for s in p["sources"]:
                md = md_path(s, lang).read_text(encoding="utf-8")
                open_ph += [(lang, s, m) for m in re.findall(r"(?<!\])\[([^\]\n]+)\](?!\()", md)]
                prefix = s if lang == "de" else f"{s}-{lang}"
                body = render(md, prefix)
                h = re.search(r"<h2[^>]*>(.*?)</h2>", body)
                label = p["labels"][lang].get(s) or re.sub(" — .*", "", re.sub("<[^>]+>", "", h.group(1)))
                tabs.append(f'<a href="#{prefix}">{label}</a>')
                secs.append(f'<section aria-labelledby="{prefix}">\n{body}\n</section>')
            inner = (f'<p class="eyebrow">{p["eyebrow"][lang]}</p>\n'
                     f'<h1 style="font-size:clamp(2rem,5vw,3rem)">{html.escape(p["h1"][lang])}</h1>\n'
                     f'<nav class="doclinks" aria-label="{CHROME[lang]["docAria"]}">{"".join(tabs)}</nav>\n'
                     + "\n".join(secs))
            src_list = " + ".join(f"docs/{lang}/{s}.md" for s in p["sources"])
            comment = "" if lang == "de" else f"<!-- Quelle: {src_list} (nicht manuell bearbeiten) -->"
            hidden = "" if lang == "de" else " hidden"
            blocks.append(f'<div class="lang-doc" data-lang="{lang}"{hidden}>{comment}\n{inner}\n</div>')
        footer = ('<footer><div class="wrap"><div><b>CreteCycling</b> — Sissi, Kreta \U0001F1EC\U0001F1F7</div>'
                  '<div><a href="index.html">Startseite</a> · <a href="impressum-datenschutz.html#impressum">Impressum</a> · '
                  '<a href="impressum-datenschutz.html#datenschutz">Datenschutz</a> · '
                  '<a href="agb-storno.html#agb">AGB</a> · <a href="agb-storno.html#stornobedingungen">Storno</a></div></div></footer>')
        titles_js = "{" + ",".join(f'"{l}":"{t}"' for l, t in p["titles"].items()) + "}"
        js = I18N_JS.replace("__TITLES__", titles_js)
        page = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{p['title']} — CreteCycling</title>
<meta name="robots" content="noindex" >
<meta name="theme-color" content="#4a2e1a">
{favicon}
<style>{css}{extra}</style>
</head>
<body>
{nav}
<main class="doc"><div class="wrap">
{chr(10).join(blocks)}
</div></main>
{footer}
{js}
</body>
</html>
"""
        if not DRAFT:
            page = page.replace('<meta name="robots" content="noindex" >\n', "")
        (WEB / p["file"]).write_text(page, encoding="utf-8")
        print("geschrieben:", WEB / p["file"])
    if open_ph:
        print(f"\n{len(open_ph)} offene [Platzhalter]:")
        for lang, s, m in open_ph: print(f"  {lang}/{s}: [{m}]")
        if not DRAFT: sys.exit("Abbruch: Platzhalter offen (DRAFT=False)")

if __name__ == "__main__":
    main()
