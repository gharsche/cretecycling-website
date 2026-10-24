#!/usr/bin/env python3
"""Baut den Tourenblog aus docs/blog/{,en,el}/*.md nach website/blog/.

    python3 scripts/build_blog.py

Quelle der Wahrheit sind die Markdown-Dateien:
  docs/blog/*.md (DE), docs/blog/en/*.md (EN), docs/blog/el/*.md (EL).
Jede Datei hat ein Frontmatter (--- ... ---) mit slug, date, route, distance_km,
elevation_m, duration_h, bike, group, badge, title, meta_description.
Der Rumpf ist der Tourbericht-Fliesstext.

Generiert:
  website/blog/index.html          - Blog-Index mit Kartenraster
  website/blog/tour-{slug}.html   - Detailseite pro Tour

Das CSS stammt aus website/index.html (<style>-Block), plus Zusatzregeln.
I18N fuer UI-Elemente via data-i18n + JS-Dictionary.
Artikel-Fliesstext via .lang-doc-Bloecken (show/hide, wie build_legal.py).
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
WEB = ROOT / "website"
LANGS = ["de", "en", "el"]

# ── Frontmatter-Parser ───────────────────────────────────────────────

def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)", text, re.S)
    if not m:
        return {}, text
    fm, body = m.group(1), m.group(2)
    meta = {}
    for line in fm.strip().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, body.strip()

# ── Markdown-Renderer ────────────────────────────────────────────────

def md_path(slug, lang):
    p = DOCS / "blog" if lang == "de" else DOCS / "blog" / lang
    return p / f"{slug}.md"

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
               r'<a href="\2" rel="noopener" target="_blank">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"(?<![\w>@/])([\w.+-]+@[\w-]+\.[\w.]+)",
               r'<a href="mailto:\1">\1</a>', t)
    return t

def render_md(md):
    """Rendert Markdown zu einfachem HTML (p, h2, meta-line, callout)."""
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        m = re.match(r"^(#{1,2}) (.+)", ln)
        if m:
            lvl = len(m.group(1))
            if lvl == 1:
                i += 1; continue  # H1 wird im Frontmatter/title gerendert
            out.append(f"<h2>{inline(m.group(2))}</h2>"); i += 1; continue
        m = re.match(r"^\*\*(.+)\*\*\s*$", ln)
        if m:
            out.append(f'<p class="meta-line">{inline(m.group(1))}</p>'); i += 1; continue
        m = re.match(r"^\*(.+)\*\s*$", ln)
        if m:
            out.append(f'<p class="callout">{inline(m.group(1))}</p>'); i += 1; continue
        para = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
            para.append(lines[i].strip()); i += 1
        if para:
            out.append("<p>" + " ".join(inline(p) for p in para) + "</p>")
    return "\n".join(out)

# ── I18N-Strings (dotted keys matching data-i18n attributes) ─────────

I18N = {
    "nav.tours": {"de": "Touren", "en": "Tours", "el": "Περιηγήσεις"},
    "nav.blog": {"de": "Blog", "en": "Blog", "el": "Ιστολόγιο"},
    "nav.book": {"de": "Buchen", "en": "Book", "el": "Κράτηση"},
    "blog.eyebrow": {"de": "Erlebte Touren", "en": "Real Rides", "el": "Πραγματικές Βόλτες"},
    "blog.title": {"de": "Blog", "en": "Blog", "el": "Ιστολόγιο"},
    "blog.lead": {
        "de": "Berichte von Touren, die wir wirklich gefahren sind — mit Fotos, Höhenmetern und ehrlichem Feedback. Und weil jede Tour Geschichten schreibt, können Teilnehmer unten auf jeder Seite ihre Eindrücke in die Kommentare legen.",
        "en": "Reports from tours we actually rode — with photos, elevation and honest feedback. Every tour writes stories, so participants can leave their impressions in the comments on each page.",
        "el": "Αναφορές από διαδρομές που κάναμε στ' αλήθεια — με φωτογραφίες, υψόμετρο και ειλικρινή σχόλια. Κάθε διαδρομή γράφει ιστορίες, οπότε οι συμμετέχοντες μπορούν να αφήσουν τις εντυπώσεις τους στα σχόλια κάτω από κάθε σελίδα.",
    },
    "cta.read": {"de": "Tourbericht lesen →", "en": "Read the tour report →", "el": "Διαβάστε την αναφορά →"},
    "crumb.back": {"de": "← Zurück zum Blog", "en": "← Back to the blog", "el": "← Επιστροφή στο ιστολόγιο"},
    "td.title": {"de": "Tourdaten", "en": "Tour data", "el": "Στοιχεία διαδρομής"},
    "td.date": {"de": "Datum", "en": "Date", "el": "Ημερομηνία"},
    "td.route": {"de": "Route", "en": "Route", "el": "Διαδρομή"},
    "td.dist": {"de": "Distanz", "en": "Distance", "el": "Απόσταση"},
    "td.elev": {"de": "Höhenmeter", "en": "Elevation", "el": "Υψόμετρο"},
    "td.time": {"de": "Dauer", "en": "Duration", "el": "Διάρκεια"},
    "td.bike": {"de": "Bike", "en": "Bike", "el": "Ποδήλατο"},
    "td.group": {"de": "Gruppe", "en": "Group", "el": "Ομάδα"},
    "td.cta": {"de": "Diese Tour buchen", "en": "Book this tour", "el": "Κλείσε αυτή τη διαδρομή"},
    "com.title": {"de": "Kommentare der Teilnehmer", "en": "Participant comments", "el": "Σχόλια συμμετεχόντων"},
    "com.lead": {
        "de": "Warst du auf dieser Tour? Erzähl uns deine Perspektive — Fotos aus dem Rucksack erlaubt.",
        "en": "Were you on this tour? Tell us your perspective — photos from the backpack allowed.",
        "el": "Ήσουν σε αυτή τη διαδρομή; Μοιράσου την οπτική σου — φωτογραφίες από το σάκο επιτρέπονται.",
    },
    "com.consent.strong": {"de": "Kommentare werden von GitHub (Giscus) bereitgestellt.", "en": "Comments are provided by GitHub (Giscus).", "el": "Τα σχόλια παρέχονται από το GitHub (Giscus)."},
    "com.consent.body": {
        "de": "Mit dem Laden werden Daten zu github.com übertragen. Erst nach deiner Einwilligung sichtbar.",
        "en": "Loading transfers data to github.com. Visible only after your consent.",
        "el": "Η φόρτωση μεταφέρει δεδομένα στο github.com. Ορατά μόνο μετά τη συναίνεσή σου.",
    },
    "com.btn": {"de": "▶ Kommentare laden", "en": "▶ Load comments", "el": "▶ Φόρτωση σχολίων"},
    "com.mod": {
        "de": "Moderation: Wir freuen uns über ehrliches Feedback. Beleidigungen und Spam löschen wir; Löschung deines eigenen Kommentars bitte an",
        "en": "Moderation: we welcome honest feedback. We delete insults and spam; to delete your own comment, please write to",
        "el": "Επιτήρηση σχολίων: δεχόμαστε ειλικρινή σχόλια. Ύβρεις και spam διαγράφονται· για διαγραφή του δικού σου σχολίου, γράψε στο",
    },
    "footer.tag": {"de": "Rad fahren auf Kreta · Sissi, Kreta", "en": "Cycling on Crete · Sissi, Crete", "el": "Ποδήλατο στην Κρήτη · Σίσι, Κρήτη"},
    "footer.privacy": {"de": "Impressum & Datenschutz", "en": "Imprint & Privacy", "el": "Εκδότης & Απόρρητο"},
    "footer.hint": {
        "de": "Kommentare werden von GitHub (Giscus) bereitgestellt, erst nach Einwilligung geladen.",
        "en": "Comments are provided by GitHub (Giscus) and load only after your consent.",
        "el": "Τα σχόλια παρέχονται από το GitHub (Giscus) και φορτώνουν μόνο μετά τη συναίνεσή σου.",
    },
    "unit.km": {"de": "km", "en": "km", "el": "χλμ."},
    "unit.m": {"de": "m", "en": "m", "el": "μ."},
    "unit.h": {"de": "Std.", "en": "hrs", "el": "ώρες"},
}

def T(key, lang):
    v = I18N.get(key, {})
    return v.get(lang, v.get("de", ""))

# ── SVG-Icons ────────────────────────────────────────────────────────

SVG_ICONS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="i-cal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 11h18"/></symbol>
<symbol id="i-clock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></symbol>
<symbol id="i-route" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="5" r="2.5"/><path d="M8.5 19H15a3.5 3.5 0 0 0 0-7H9a3.5 3.5 0 0 1 0-7h6.5"/></symbol>
<symbol id="i-up" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18l6-9 4 5 7-10"/><path d="M20 4h-4M20 4v4"/></symbol>
<symbol id="i-gh" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5A11.5 11.5 0 0 0 .5 12a11.5 11.5 0 0 0 7.86 10.93c.57.1.78-.25.78-.55v-2c-3.2.7-3.88-1.54-3.88-1.54-.53-1.34-1.28-1.7-1.28-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.04 1.77 2.72 1.26 3.39.96.1-.76.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.79 0c2.2-1.5 3.17-1.18 3.17-1.18.63 1.59.23 2.76.12 3.05.74.81 1.18 1.84 1.18 3.1 0 4.42-2.69 5.4-5.25 5.68.42.36.78 1.06.78 2.14v3.17c0 .31.2.66.79.55A11.5 11.5 0 0 0 23.5 12 11.5 11.5 0 0 0 12 .5z"/></symbol>
</defs></svg>"""

# ── Flag-SVGs ────────────────────────────────────────────────────────

def flag_svg(lang):
    if lang == "de":
        return '<svg viewBox="0 0 30 18" width="20" height="12" aria-hidden="true"><rect width="30" height="6" fill="#000"/><rect y="6" width="30" height="6" fill="#d00"/><rect y="12" width="30" height="6" fill="#ffce00"/></svg>'
    if lang == "en":
        return '<svg viewBox="0 0 60 30" width="22" height="11" aria-hidden="true"><clipPath id="ukc0"><rect width="60" height="30"/></clipPath><g clip-path="url(#ukc0)"><rect width="60" height="30" fill="#012169"/><path d="M0,0L60,30M60,0L0,30" stroke="#fff" stroke-width="7"/><path d="M0,0L60,30M60,0L0,30" stroke="#c8102e" stroke-width="3"/><rect x="25" width="10" height="30" fill="#fff"/><rect x="27" width="6" height="30" fill="#c8102e"/><rect y="10" width="60" height="10" fill="#fff"/><rect y="12" width="60" height="6" fill="#c8102e"/></g></svg>'
    return '<svg viewBox="0 0 27 18" width="20" height="13" aria-hidden="true"><rect width="27" height="18" fill="#fff"/><rect width="27" height="2" fill="#005eb8"/><rect y="4" width="27" height="2" fill="#005eb8"/><rect y="8" width="27" height="2" fill="#005eb8"/><rect y="12" width="27" height="2" fill="#005eb8"/><rect y="16" width="27" height="2" fill="#005eb8"/><rect width="10" height="10" fill="#005eb8"/><rect x="4" width="2" height="10" fill="#fff"/><rect y="4" width="10" height="2" fill="#fff"/></svg>'

LANG_LABELS = {
    "de": {"de": "Auf Deutsch wechseln", "en": "Switch to German", "el": "Μετάβαση στα Γερμανικά"},
    "en": {"de": "Auf Englisch wechseln", "en": "Switch to English", "el": "Μετάβαση στα Αγγλικά"},
    "el": {"de": "Auf Griechisch wechseln", "en": "Switch to Greek", "el": "Μετάβαση στα Ελληνικά"},
}

# ── CSS ──────────────────────────────────────────────────────────────

EXTRA_CSS = """
/* Blog-spezifische Stile */
header.nav{position:sticky;top:0;z-index:50;background:rgba(246,236,214,.94);backdrop-filter:blur(10px);box-shadow:0 1px 0 rgba(74,46,26,.14)}
header.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:68px;gap:1rem}
header.nav .logo{color:var(--terra-d);text-decoration:none;font-weight:800;font-size:1.25rem;display:flex;align-items:center;gap:.55rem;letter-spacing:-.02em}
header.nav .logo img{width:40px;height:40px;border-radius:10px;object-fit:cover;border:1.5px solid rgba(74,46,26,.25)}
header.nav .logo b{color:var(--olive-d)}
header.nav ul{display:flex;gap:1.6rem;list-style:none;padding:0}
header.nav ul a{text-decoration:none;font-weight:600;font-size:.95rem;color:var(--ink);opacity:.92}
header.nav ul a[aria-current="page"]{color:var(--terra-d);text-decoration:underline;text-decoration-color:var(--ochre);text-underline-offset:6px;text-decoration-thickness:3px;opacity:1}
header.nav ul a:hover{opacity:1;text-decoration:underline;text-decoration-color:var(--ochre);text-underline-offset:6px;text-decoration-thickness:3px}
header.nav .btn{padding:.55rem 1.1rem;font-size:.9rem}
.lang-switch{display:flex;align-items:center;gap:.35rem;flex-wrap:wrap}
.lang-switch button{border:1px solid rgba(74,46,26,.25);background:#fff;color:var(--umber);border-radius:999px;padding:.45rem .7rem;min-width:2.8rem;min-height:2.8rem;font:inherit;font-weight:800;cursor:pointer;display:inline-flex;align-items:center;justify-content:center}
.lang-switch button[aria-pressed="true"]{background:var(--ochre);border-color:var(--ochre);color:#3a2616}
.lang-switch button svg{width:1.5rem;height:auto;max-height:1.1rem;object-fit:contain}
@media(max-width:860px){header.nav ul{display:none}}
/* Blog page header */
.pagehead{background:linear-gradient(180deg,#fff 0%,var(--sand) 100%);border-bottom:1px solid var(--sand-d);padding:clamp(2.5rem,6vw,4.5rem) 0 clamp(2rem,5vw,3rem)}
.pagehead h1{font-size:clamp(2.1rem,5vw,3.4rem);font-weight:900;margin:.4rem 0 .8rem}
/* Meta chips */
.chiprow{display:flex;flex-wrap:wrap;gap:.5rem}
.chip{background:#fff;border:1px solid rgba(91,106,51,.3);padding:.4rem .9rem;border-radius:999px;font-size:.88rem;font-weight:600;display:inline-flex;align-items:center;gap:.4rem}
.chip svg{width:15px;height:15px;color:var(--olive-d);flex:none}
/* Blog card grid */
.blog-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1.4rem;margin-top:2.2rem}
@media(max-width:760px){.blog-grid{grid-template-columns:1fr}}
.post{background:#fff;border-radius:var(--r);box-shadow:var(--shadow);overflow:hidden;text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:transform .2s}
.post:hover{transform:translateY(-5px)}
.post .thumb{aspect-ratio:16/9;position:relative}
.post .thumb .badge{position:absolute;top:14px;left:14px;background:var(--ochre);font-size:.72rem;font-weight:800;padding:.25rem .7rem;border-radius:999px;color:#3a2616}
.post .body{padding:1.4rem 1.5rem 1.5rem;display:flex;flex-direction:column;gap:.7rem;flex:1}
.post h3{font-size:1.3rem}
.post p{color:var(--mute);font-size:.94rem}
.post .chiprow{margin-top:auto;padding-top:.6rem}
.post .more{font-weight:800;color:var(--terra-d);font-size:.9rem}
/* Article / detail page */
.banner{height:clamp(220px,36vw,420px);position:relative}
.banner .crumb{position:absolute;left:0;right:0;bottom:0;background:rgba(46,27,14,.55);backdrop-filter:blur(4px);color:#fff}
.banner .crumb .wrap{padding:.6rem 0;font-size:.88rem;font-weight:600}
.banner .crumb a{color:var(--ochre)}
article.blog-article{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:2.5rem;align-items:start}
@media(max-width:900px){article.blog-article{grid-template-columns:1fr}}
article.blog-article h1{font-size:clamp(2rem,4.5vw,3rem);font-weight:900;margin:.5rem 0 1rem}
.prose p{margin-bottom:1.1rem;max-width:62ch}
.prose .meta-line{font-weight:700;color:var(--terra-d);font-size:.95rem;margin-bottom:1.2rem}
.prose .callout{font-style:italic;color:var(--mute);border-left:3px solid var(--ochre);padding-left:1rem;margin:1.5rem 0}
.prose h2{font-size:1.5rem;margin:2rem 0 .8rem}
aside.tourdata{background:#fff;border:2px solid var(--sand-d);border-radius:var(--r);padding:1.4rem;position:sticky;top:88px}
aside.tourdata h2{font-size:1.05rem;margin-bottom:1rem;text-transform:uppercase;letter-spacing:.1em;color:var(--terra)}
aside.tourdata dl{display:grid;grid-template-columns:auto 1fr;gap:.55rem .8rem;font-size:.92rem}
aside.tourdata dt{color:var(--mute);font-weight:600}
aside.tourdata dd{font-weight:800;text-align:right}
aside.tourdata .btn{width:100%;justify-content:center;margin-top:1.2rem}
/* Comments / consent */
.comments{border-top:2px dashed #d8c49a;margin-top:3rem;padding-top:2.2rem}
.consent{background:#fff;border:2px solid var(--sand-d);border-radius:var(--r);padding:1.6rem;display:flex;flex-wrap:wrap;gap:1rem;align-items:center}
.consent p{flex:1;min-width:240px;font-size:.92rem;color:var(--mute)}
.consent strong{color:var(--ink)}
.consent svg{width:44px;height:44px;color:#2f6f7c;flex:none}
.commentframe{background:#fff;border-radius:var(--r);box-shadow:var(--shadow);padding:1.5rem;margin-top:1.5rem}
.modnote{margin-top:1.2rem;font-size:.85rem;color:var(--mute)}
.modnote a{color:var(--terra-d);font-weight:700}
footer.blog-footer{background:var(--umber);color:#f4e6c8;padding:2.5rem 0;font-size:.9rem;margin-top:clamp(3rem,8vw,6rem)}
footer.blog-footer a{color:var(--ochre)}
footer.blog-footer .wrap{display:flex;flex-wrap:wrap;gap:1rem;justify-content:space-between}
"""

# ── Helpers ──────────────────────────────────────────────────────────

def fmt_date(iso_str, lang):
    try:
        y, m, d = iso_str.split("-")
        if lang == "de":
            return f"{d}.{m}.{y}"
        elif lang == "el":
            return f"{d}/{m}/{y}"
        else:
            months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            return f"{int(d)} {months[int(m)]} {y}"
    except Exception:
        return iso_str

def gradients_for(badge):
    return {
        "E-Bike": "linear-gradient(160deg,#2f6f7c 0%,#68a5ad 45%,#e2a93b 100%)",
        "Mountainbike": "linear-gradient(160deg,#5b6a33 0%,#7d8c4a 50%,#ead9b3 100%)",
        "MTB": "linear-gradient(160deg,#5b6a33 0%,#7d8c4a 50%,#ead9b3 100%)",
        "Gravel": "linear-gradient(160deg,#8a3b1b 0%,#b4532a 55%,#e2a93b 100%)",
        "Familie": "linear-gradient(160deg,#2f6f7c 0%,#4a90a0 40%,#f6ecd6 100%)",
    }.get(badge, "linear-gradient(160deg,#2f6f7c 0%,#68a5ad 45%,#e2a93b 100%)")

# ── Nav / Footer / Head ───────────────────────────────────────────────

def build_nav(active_blog=False):
    blog_href = "index.html" if active_blog else "../index.html#blog"
    current = ' aria-current="page"' if active_blog else ""
    buttons = "".join(
        f'<button type="button" data-lang="{l}" aria-pressed="{"true" if l == "de" else "false"}"'
        f' aria-label="{LANG_LABELS[l]["de"]}" title="{LANG_LABELS[l]["de"]}">{flag_svg(l)}</button>'
        for l in LANGS
    )
    return f"""<header class="nav"><div class="wrap">
<a class="logo" href="../index.html" aria-label="CreteCycling Startseite">
<img src="../assets/logo-cretecycling.jpg" width="40" height="40" alt="CreteCycling Logo"><span>Crete<b>Cycling</b></span></a>
<nav aria-label="Hauptnavigation"><ul>
<li><a href="../index.html#touren" data-i18n="nav.tours">Touren</a></li>
<li><a href="index.html"{current} data-i18n="nav.blog">Blog</a></li>
<li><a href="../index.html#kontakt" data-i18n="nav.book">Buchen</a></li>
</ul></nav>
<div class="lang-switch" role="group" aria-label="Sprache">{buttons}</div>
</div></header>"""

def build_footer():
    return f"""<footer class="blog-footer"><div class="wrap">
<p><strong>CreteCycling</strong> — <span data-i18n="footer.tag">{T("footer.tag", "de")}</span></p>
<p><a href="../impressum-datenschutz.html" data-i18n="footer.privacy">{T("footer.privacy", "de")}</a> · <a href="../agb-storno.html">AGB &amp; Storno</a> · <span data-i18n="footer.hint">{T("footer.hint", "de")}</span></p>
</div></footer>"""

def build_head(title, description, css, extra_css):
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — CreteCycling</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="#4a2e1a">
<link rel="icon" type="image/jpeg" href="../assets/favicon-64.jpg">
<style>{css}{extra_css}</style>
</head>
<body>
{SVG_ICONS}"""

# ── I18N-JS ──────────────────────────────────────────────────────────

def build_i18n_js():
    parts = []
    for k, v in I18N.items():
        parts.append(f"{json.dumps(k, ensure_ascii=False)}:{json.dumps(v, ensure_ascii=False)}")
    return """<script>
(function(){
var T={""" + ",".join(parts) + """};
var lang=(new URLSearchParams(location.search).get("lang")||localStorage.getItem("cc-lang")||"de").slice(0,2).toLowerCase();
if(!T["nav.blog"][lang])lang="de";
function apply(l){
  lang=l;document.documentElement.lang=l;
  document.querySelectorAll("[data-i18n]").forEach(function(el){
    var k=el.getAttribute("data-i18n");var v=T[k]&&T[k][l];
    if(v)el.textContent=v;
  });
  document.querySelectorAll(".lang-switch button").forEach(function(b){
    b.setAttribute("aria-pressed",String(b.dataset.lang===l));
  });
  localStorage.setItem("cc-lang",l);
  var h=location.hash.slice(1);
  if(h){var base=h.replace(/-(de|en|el)$/,"");var want=lang==="de"?base:base+"-"+lang;if(h!==want&&document.getElementById(want))history.replaceState(null,"","#"+want);}
  history.replaceState(null,"",location.pathname+(l==="de"?"":"?lang="+l)+location.hash);
}
document.querySelectorAll(".lang-switch button").forEach(function(b){
  b.addEventListener("click",function(){apply(b.dataset.lang);});
});
apply(lang);
window.__ccLang=lang;
window.__ccApply=apply;
})();
</script>"""

# ── Blog-Index ──────────────────────────────────────────────────────

def collect_tours():
    tours = []
    for f in sorted((DOCS / "blog").glob("*.md")):
        slug = f.stem
        metas, bodies = {}, {}
        for lang in LANGS:
            p = md_path(slug, lang)
            if not p.exists():
                print(f"Warnung: {p} fehlt", file=sys.stderr); continue
            meta, body = parse_frontmatter(p.read_text(encoding="utf-8"))
            metas[lang] = meta; bodies[lang] = body
        if "de" not in metas:
            continue
        tours.append({"slug": slug, "meta": metas, "body": bodies})
    return tours

def build_blog_index(tours):
    index_src = (WEB / "index.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", index_src, re.S).group(1)

    cards = []
    for tour in tours:
        slug = tour["slug"]
        meta_de = tour["meta"]["de"]
        badge = meta_de.get("badge", "")
        grad = gradients_for(badge)

        # Card content: drei lang-doc Bloecke
        card_blocks = []
        for lang in LANGS:
            m = tour["meta"].get(lang, tour["meta"]["de"])
            title = m.get("title", slug)
            badge_l = m.get("badge", badge)
            body = tour["body"].get(lang, tour["body"].get("de", ""))
            lines = [l for l in body.splitlines() if l.strip() and not l.startswith("#")]
            teaser = lines[0].strip() if lines else ""
            if len(teaser) > 120:
                teaser = teaser[:117] + "…"

            dist = m.get("distance_km", ""); elev = m.get("elevation_m", "")
            dur = m.get("duration_h", ""); dstr = fmt_date(m.get("date", ""), lang)
            ukm = T("unit.km", lang); um = T("unit.m", lang); uh = T("unit.h", lang)

            chips = (f'<span class="chip"><svg><use href="#i-cal"/></svg>{dstr}</span>'
                     f'<span class="chip"><svg><use href="#i-route"/></svg>{dist} {ukm}</span>'
                     f'<span class="chip"><svg><use href="#i-up"/></svg>{elev} {um}</span>'
                     f'<span class="chip"><svg><use href="#i-clock"/></svg>{dur} {uh}</span>')

            hidden = "" if lang == "de" else " hidden"
            card_blocks.append(
                f'<div class="lang-doc" data-lang="{lang}"{hidden}>'
                f'<span class="badge">{html.escape(badge_l)}</span>'
                f'<h3>{html.escape(title)}</h3>'
                f'<p>{html.escape(teaser)}</p>'
                f'<div class="chiprow">{chips}</div></div>'
            )

        cards.append(f"""<a class="post" href="tour-{slug}.html">
<div class="thumb" style="background:{grad}" role="img" aria-label="Tourfoto: {html.escape(meta_de.get('route', slug))}">
</div>
<div class="body">
{chr(10).join(card_blocks)}
<span class="more" data-i18n="cta.read">{T("cta.read", "de")}</span>
</div></a>""")

    head = build_head("Blog", "Berichte und Fotos durchgefuehrter Touren von CreteCycling in Sissi, Kreta. Teilnehmer koennen Kommentare hinterlassen.", css, EXTRA_CSS)
    nav = build_nav(active_blog=True)
    footer = build_footer()
    js = build_i18n_js()

    html_out = f"""{head}
{nav}
<main>
<div class="pagehead"><div class="wrap">
<span class="eyebrow" data-i18n="blog.eyebrow">{T("blog.eyebrow", "de")}</span>
<h1 data-i18n="blog.title">{T("blog.title", "de")}</h1>
<p class="lead" data-i18n="blog.lead">{T("blog.lead", "de")}</p>
</div></div>
<section><div class="wrap">
<div class="blog-grid">
{chr(10).join(cards)}
</div>
</div></section>
</main>
{footer}
{js}
</body>
</html>"""
    out = WEB / "blog" / "index.html"
    out.write_text(html_out, encoding="utf-8")
    print(f"geschrieben: {out}")

# ── Blog-Detailseite ─────────────────────────────────────────────────

def build_tour_page(tour):
    slug = tour["slug"]
    meta_all = tour["meta"]; body_all = tour["body"]
    meta_de = meta_all["de"]
    title_de = meta_de.get("title", slug)
    desc_de = meta_de.get("meta_description", "")
    badge = meta_de.get("badge", "")
    grad = gradients_for(badge)

    index_src = (WEB / "index.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", index_src, re.S).group(1)
    head = build_head(title_de, desc_de, css, EXTRA_CSS)
    nav = build_nav(active_blog=False)
    footer = build_footer()
    js = build_i18n_js()

    # Drei lang-doc Bloecke fuer Artikel
    article_blocks = []
    for lang in LANGS:
        m = meta_all.get(lang, meta_all["de"])
        body = body_all.get(lang, body_all.get("de", ""))
        rendered = render_md(body)
        title_l = m.get("title", title_de)
        dstr = fmt_date(m.get("date", ""), lang)
        dist = m.get("distance_km", ""); elev = m.get("elevation_m", "")
        dur = m.get("duration_h", ""); route = m.get("route", "")
        ukm = T("unit.km", lang); um = T("unit.m", lang); uh = T("unit.h", lang)

        chips = (f'<span class="chip"><svg><use href="#i-route"/></svg>{dist} {ukm}</span>'
                 f'<span class="chip"><svg><use href="#i-up"/></svg>{elev} {um}</span>'
                 f'<span class="chip"><svg><use href="#i-clock"/></svg>{dur} {uh}</span>'
                 f'<span class="chip"><svg><use href="#i-cal"/></svg>{dstr}</span>')

        hidden = "" if lang == "de" else " hidden"
        article_blocks.append(
            f'<div class="lang-doc" data-lang="{lang}"{hidden}>\n'
            f'<span class="eyebrow">{html.escape(dstr)}</span>\n'
            f'<h1>{html.escape(title_l)}</h1>\n'
            f'<div class="chiprow" style="margin-bottom:1.6rem">{chips}</div>\n'
            f'<div class="prose">\n{rendered}\n</div>\n</div>'
        )

    # Sidebar (feste Werte DE, Sprachwechsel via data-i18n + JS update)
    date_de = fmt_date(meta_de.get("date", ""), "de")
    dist_de = meta_de.get("distance_km", "")
    elev_de = meta_de.get("elevation_m", "")
    dur_de = meta_de.get("duration_h", "")
    route_de = meta_de.get("route", "")
    bike_de = meta_de.get("bike", "")
    group_de = meta_de.get("group", "")

    sidebar = f"""<aside class="tourdata">
<h2 data-i18n="td.title">{T("td.title", "de")}</h2>
<dl>
<dt data-i18n="td.date">{T("td.date", "de")}</dt><dd class="dv-date">{date_de}</dd>
<dt data-i18n="td.route">{T("td.route", "de")}</dt><dd>{html.escape(route_de)}</dd>
<dt data-i18n="td.dist">{T("td.dist", "de")}</dt><dd class="dv-dist">{dist_de} {T("unit.km", "de")}</dd>
<dt data-i18n="td.elev">{T("td.elev", "de")}</dt><dd class="dv-elev">{elev_de} {T("unit.m", "de")}</dd>
<dt data-i18n="td.time">{T("td.time", "de")}</dt><dd class="dv-time">{dur_de} {T("unit.h", "de")}</dd>
<dt data-i18n="td.bike">{T("td.bike", "de")}</dt><dd>{html.escape(bike_de)}</dd>
<dt data-i18n="td.group">{T("td.group", "de")}</dt><dd>{html.escape(group_de)}</dd>
</dl>
<a class="btn btn-ochre" href="../index.html#kontakt" data-i18n="td.cta">{T("td.cta", "de")}</a>
</aside>"""

    comments = f"""<div class="comments">
<h2 style="font-size:1.6rem" data-i18n="com.title">{T("com.title", "de")}</h2>
<p class="lead" style="font-size:1rem;margin:.6rem 0 1.4rem" data-i18n="com.lead">{T("com.lead", "de")}</p>
<div class="consent" id="consentBox">
<svg aria-hidden="true"><use href="#i-gh"/></svg>
<p><strong data-i18n="com.consent.strong">{T("com.consent.strong", "de")}</strong> <span data-i18n="com.consent.body">{T("com.consent.body", "de")}</span></p>
<button class="btn btn-terra" id="loadComments" type="button" data-i18n="com.btn">{T("com.btn", "de")}</button>
</div>
<div class="commentframe" id="giscusMount" hidden></div>
<p class="modnote"><span data-i18n="com.mod">{T("com.mod", "de")}</span> <a href="mailto:info@cretecycling.eu">info@cretecycling.eu</a>.</p>
</div>"""

    giscus_script = """<script>
document.getElementById("loadComments").addEventListener("click", function(){
  document.getElementById("consentBox").hidden = true;
  var mount = document.getElementById("giscusMount");
  mount.hidden = false;
  var s = document.createElement("script");
  s.src = "https://giscus.app/client.js";
  s.setAttribute("data-repo", "gharsche/cretecycling-website");
  s.setAttribute("data-mapping", "pathname");
  s.setAttribute("data-category", "Blog-Kommentare");
  s.setAttribute("data-strict", "0");
  s.setAttribute("data-reactions-enabled", "1");
  s.setAttribute("data-emit-metadata", "0");
  s.setAttribute("data-input-position", "top");
  s.setAttribute("data-theme", "light");
  s.setAttribute("data-lang", window.__ccLang === "el" ? "el" : window.__ccLang === "en" ? "en" : "de");
  s.setAttribute("data-loading", "lazy");
  s.crossOrigin = "anonymous";
  s.async = "true";
  mount.innerHTML = "";
  mount.appendChild(s);
});
</script>"""

    html_out = f"""{head}
{nav}
<main>
<div class="banner" style="background:{grad}" role="img" aria-label="Tourfoto: {html.escape(route_de)}">
<div class="crumb"><div class="wrap"><a href="index.html" data-i18n="crumb.back">{T("crumb.back", "de")}</a></div></div>
</div>
<section><div class="wrap">
<article class="blog-article">
<div>
{chr(10).join(article_blocks)}
{comments}
</div>
{sidebar}
</article>
</div></section>
</main>
{footer}
{js}
{giscus_script}
{SIDEBAR_UPDATE_JS}
</body>
</html>"""
    out = WEB / "blog" / f"tour-{slug}.html"
    out.write_text(html_out, encoding="utf-8")
    print(f"geschrieben: {out}")

# ── Sidebar-Wert-Update bei Sprachwechsel ─────────────────────────────

# Die Sidebar-Werte (Datum, Distanz, Dauer) muessen bei Sprachwechsel
# aktualisiert werden. Das passiert im JS-apply, das auch data-i18n
# Elemente setzt. Die .dv-* Klassen werden in einem zusaetzlichen
# Script-Block aktualisiert, das die Werte aus den .lang-doc-Bloecken
# liest.

SIDEBAR_UPDATE_JS = """<script>
// Nach Sprachwechsel: Sidebar-Werte aus dem aktiven lang-doc-Block lesen
(function(){
  var origApply = window.__ccApply;
  if(!origApply) return;
  window.__ccApply = function(l){
    origApply(l);
    // Datum aus dem aktiven .lang-doc .eyebrow
    var active = document.querySelector('.lang-doc[data-lang="'+l+'"]');
    if(!active) return;
    var eyebrow = active.querySelector('.eyebrow');
    var dateDd = document.querySelector('.dv-date');
    if(eyebrow && dateDd) dateDd.textContent = eyebrow.textContent;
    // Distanz/Elev/Dauer aus den chips im aktiven Block
    var chips = active.querySelectorAll('.chip');
    var distDd = document.querySelector('.dv-dist');
    var elevDd = document.querySelector('.dv-elev');
    var timeDd = document.querySelector('.dv-time');
    if(chips.length >= 3 && distDd) {
      distDd.textContent = chips[0].textContent.trim();
      elevDd.textContent = chips[1].textContent.trim();
      timeDd.textContent = chips[2].textContent.trim();
    }
  };
  // Initiale Anwendung
  var lang = window.__ccLang || 'de';
  window.__ccApply(lang);
})();
</script>"""

# ── Main ─────────────────────────────────────────────────────────────

def main():
    tours = collect_tours()
    if not tours:
        sys.exit("Abbruch: keine Blog-Posts in docs/blog/ gefunden")
    build_blog_index(tours)
    for tour in tours:
        build_tour_page(tour)

if __name__ == "__main__":
    main()
