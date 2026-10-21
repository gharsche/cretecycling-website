# CreteCycling IKE

Fahrradverleih, geführte Touren und Workshops — Basis in Sissi, Kreta.

## Bereiche
- `src/rental/` — Fahrradverleih (Fuhrpark, Tarife, Ausleihe/Rückgabe)
- `src/tours/` — Geführte Touren (Katalog, Buchung, Guide-Zuweisung)
- `src/workshops/` — Workshops (Termine, Anmeldung)
- `src/automation/` — Benachrichtigungen & Cron-Jobs
- `website/` — Öffentliche Landing Page (GitHub Pages)
- `docs/` — Doku je Geschäftsbereich

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
python -m unittest discover tests
```
