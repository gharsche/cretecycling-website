# Workshops — Ablauf & Referenz

## Überblick

Praktische Workshops rund ums Fahrrad — von Grundwartung bis Erste Hilfe unterwegs. Begrenzte Kapazität, bei Ausbuchung Warteliste.

**Module:** `src/workshops/` — `events.py` · `registration.py`
**Tests:** `tests/test_workshops.py`

---

## Formate (`events.py`)

Jeder Workshop ist ein `Workshop`-Objekt:

| Feld | Werte |
|---|---|
| `id` | Eindeutige Workshop-ID |
| `title` | Titel (z. B. "Bike-Grundwartung") |
| `day` | ISO-Datum |
| `capacity` | Max. Teilnehmer |
| `price` | Preis pro Teilnehmer |

Typische Formate:

| Workshop | Inhalt |
|---|---|
| Bike-Grundwartung | Kette, Bremsen, Schaltung — Wartung für Jedermann |
| E-Bike-Sicherheit | Akku-Pflege, Reichweiten-Management, Sicherheitstipps |
| Erste Hilfe unterwegs | Pannenservice, Notfall-Kit, Verhalten bei Unfällen |

---

## Anmeldung (`registration.py`)

`Registration` verwaltet Anmeldungen je Workshop.

**Anmelden:** `Registration.register(workshop_id, participant, capacity)`
- Wenn noch Platz frei: Teilnehmer wird hinzugefügt
- Wenn ausgebucht: `ValueError`
- Doppel-Anmeldung desselben Teilnehmers wird ignoriert (idempotent)

**Warteliste prüfen:** `Registration.waitlist_needed(workshop_id, capacity)` → `True` wenn Kapazität erreicht.

Beispiel:
```python
reg.register("ws-maint-01", "Anna", capacity=10)   # angemeldet
reg.register("ws-maint-01", "Ben",  capacity=10)   # angemeldet
reg.waitlist_needed("ws-maint-01", capacity=10)     # False (8 frei)
```

---

## Benachrichtigungen

Nach erfolgreicher Anmeldung:
1. **Sofort:** Buchungsbestätigung via `notifications.py`
2. **24 h vorher:** Erinnerung mit Ort, Zeit und Mitbring-Liste

Beide laufen zentral über `src/automation/notifications.py` → `Outbox.booking_confirmation()`.

---

## FAQ

**Was bei Absage?** Bei Absage durch CreteCycling: volle Rückerstattung. Bei Absage durch Teilnehmer: bis 48 h vorher volle Rückerstattung, danach 50 %.

**Warteliste?** Wenn ein Workshop ausgebucht ist, können sich Interessenten auf die Warteliste setzen lassen. Bei Stornierung eines Teilnehmers rückt der nächste automatisch nach und wird benachrichtigt.
