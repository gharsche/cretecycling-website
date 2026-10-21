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
