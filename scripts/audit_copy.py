#!/usr/bin/env python3
"""audit_copy.py — Text-Invarianten der Startseite und Rechtstexte (read-only).

Drei Pruefungen, die der Zahlen-Guard in build_legal.py strukturell nicht faengt:

1. static-vs-I18N (DE): Sichtbarkeits-Schluessel (lead/title/eyebrow/slogan/cta/
   book/submit/to/line) aus I18N.de muessen woertlich im statischen HTML vor dem
   ersten <script> stehen — sonst zeigt der No-JS-/PDF-Renderer einen anderen
   Text als die deutsche Uebersetzung (Klasse "Vier Modelle", Okt 2026).
2. Phrase-Blocklist: ausgeregelte Formulierungen duerfen nirgends mehr stehen
   (Gruppengröße 8, Helm-Immer-inklusive-Phrasen, Modellanzahl 4).
   Bewusst EXAKT-Phrasen, keine losen Naehermuster — "Werkzeug & Wasser immer
   inklusive · Helm im Verleih 3 €/Tag" ist der freigegebene korrekte Wortlaut.
3. Storno-Fristen: 24 und 48 (h) müssen in agb.md jeder Sprache vorkommen.

Exit 0 = sauber, 1 = Funde. Schreibt nichts.
"""
import html as htmlmod, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB, DOCS = ROOT / "website", ROOT / "docs"
fail = []

# --- 1) static-vs-I18N (index.html, DE) ---
idx = (WEB / "index.html").read_text(encoding="utf-8")
pre = htmlmod.unescape(idx.split("<script", 1)[0])  # Entities (&amp;) wie der Browser auflösen

def extract_de():
    m = re.search(r"de: \{", idx)
    if not m:
        return None
    i = m.end() - 1  # am '{' von de:
    depth = 0
    for j in range(i, len(idx)):
        if idx[j] == "{":
            depth += 1
        elif idx[j] == "}":
            depth -= 1
            if depth == 0:
                return idx[i + 1:j]
    return None

de = extract_de()
if de is None:
    fail.append("audit_copy: I18N.de nicht auffindbar — Prüfung 1 ausgefallen (Skript prüfen!)")
else:
    VISIBLE_KEYS = {"lead", "title", "eyebrow", "slogan", "cta", "book", "submit", "to", "line", "flyer"}
    for key, val in re.findall(r'(\w+): "((?:[^"\\]|\\.)*)"', de):
        if key not in VISIBLE_KEYS or len(val) < 6:
            continue
        v = val.encode().decode("unicode_escape") if "\\" in val else val
        if v not in pre:
            fail.append(f'index.html: I18N.de["{key}"] = "{v[:60]}…" fehlt im statischen Markup — No-JS/PDF zeigt anderen Text' if len(v) > 60 else f'index.html: I18N.de["{key}"] = "{v}" fehlt im statischen Markup — No-JS/PDF zeigt anderen Text')

# --- 2) Phrase-Blocklist (exakte Formulierungen) ueber docs/ + website/*.html ---
BLOCK = ["max. 8", "Standard: 8", "max_group=8", "Vier Modelle", "Four Models",
         "four models",
         "Helm & Werkzeug immer inklusive",
         "Helm und Werkzeug immer inklusive",
         "Helm immer inklusive",
         "Helmet & tools always included",
         "Helmet always included"]
for f in list(DOCS.rglob("*.md")) + list(WEB.glob("*.html")):
    txt = f.read_text(encoding="utf-8", errors="replace")
    for phrase in BLOCK:
        start = 0
        while (k := txt.find(phrase, start)) >= 0:
            line = txt[:k].count("\n") + 1
            snip = txt.splitlines()[line - 1].strip()[:90]
            fail.append(f"{f.relative_to(ROOT)}:{line}: Blocklist '{phrase}': {snip}")
            start = k + 1

# --- 3) Storno-Fristen 24/48 in jeder AGB-Sprache ---
for lang in ("", "en/", "el/"):
    p = DOCS / lang / "agb.md"
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8")
    nums = {x for x in re.findall(r"(\d+)\s*(?:h\b|Std|Stunde|ώρες|hours)", t)}
    for want in ("24", "48"):
        if want not in nums:
            fail.append(f"agb {lang or 'de'}: Frist {want} h nicht gefunden (Prüfung 3)")

if fail:
    print(f"AUDIT: {len(fail)} Fund(e):")
    for x in fail:
        print("  -", x)
    sys.exit(1)
print("AUDIT: sauber (Prüfungen 1–3 bestanden)")
