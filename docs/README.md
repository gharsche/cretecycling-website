# CreteCycling — Dokumentation

CreteCycling bietet **Fahrradverleih, geführte Touren und Workshops** — direkt am Meer in Sissi, Kreta.

## Inhaltsverzeichnis

| Dokument | Inhalt |
|---|---|
| [Fahrradverleih](rental.md) | Fuhrpark, Tarife, Kaution, Übergabe & Rückgabe |
| [Geführte Touren](tours.md) | Tour-Katalog, Buchung, Guide-Zuweisung |
| [Workshops](workshops.md) | Formate, Anmeldung, Warteliste |
| [Brand Guide](brand-guide.md) | Tone of Voice, Farben, Logo |
| [Booking-Guide](booking-guide.md) | Gesamter Buchungs-Ablauf über alle drei Bereiche |

## Rechtstexte (Quelle der Wahrheit für `website/*.html`)

| Dokument (DE, maßgeblich) | EN | EL |
|---|---|---|
| [AGB](agb.md) | [en/agb.md](en/agb.md) | [el/agb.md](el/agb.md) |
| [Stornobedingungen](stornobedingungen.md) | [en/stornobedingungen.md](en/stornobedingungen.md) | [el/stornobedingungen.md](el/stornobedingungen.md) |
| [Impressum](impressum.md) | [en/impressum.md](en/impressum.md) | [el/impressum.md](el/impressum.md) |
| [Datenschutz](datenschutz.md) | [en/datenschutz.md](en/datenschutz.md) | [el/datenschutz.md](el/datenschutz.md) |

EN/EL sind Übersetzungen der DE-Texte ohne eigene inhaltliche Änderungen; Rechtliches vor Livegang prüfen.

## Architektur

```
src/
├── rental/       → fleet.py · pricing.py · checkout.py
├── tours/        → catalog.py · booking.py · guides.py
├── workshops/    → events.py · registration.py
└── automation/   → notifications.py
```

Jeder Bereich hat eigene Module und eigene Tests unter `tests/`.
Benachrichtigungen (Bestätigungen, Erinnerungen) laufen zentral über `src/automation/notifications.py`.
