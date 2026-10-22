# Geführte Touren — Ablauf & Referenz

## Überblick

Geführte Touren mit lokalen Guides — vom entspannten Coastal Ride bis zur anspruchsvollen Berg-Route. Kleine Gruppen, max. 4 Personen (AGB § 3.2, Buchungsformular: `guests max="4"`).

**Module:** `src/tours/` — `catalog.py` · `booking.py` · `guides.py`
**Tests:** `tests/test_tours.py`

---

## Tour-Katalog (`catalog.py`)

Jede Tour ist ein `Tour`-Objekt:

| Feld | Werte |
|---|---|
| `id` | Eindeutige Tour-ID |
| `name` | Anzeige-Name |
| `level` | `easy` · `moderate` · `hard` |
| `duration_hours` | Dauer in Stunden |
| `price` | Preis pro Person |
| `max_group` | Max. Teilnehmer — aktuell 4 (kleine Gruppen, 1 Guide pro Gruppe) |

Treffpunkt: Sissi Hafen.
Standard-Ausrüstung inklusive: Helm, Werkzeug-Kit, Wasser.

---

## Buchung (`booking.py`)

`TourBooking` verwaltet Plätze je Tour und Tag.

**Buchen:** `TourBooking.book(tour_id, day, guests, max_group)`
- Prüft, ob genug Plätze frei sind
- Bei Überschreitung: `ValueError` mit Hinweis auf Auslastung

**Freie Plätze:** `TourBooking.free_spots(tour_id, day, max_group)` → verbleibende Plätze.

Beispiel:
```python
booking.book("coastal-easy", "2026-06-15", 3, max_group=4)   # 1 Platz frei
booking.free_spots("coastal-easy", "2026-06-15", max_group=4) # → 1
```

---

## Guide-Zuweisung (`guides.py`)

`GuidePool` teilt Guides automatisch zu.

**Zuweisung:** `GuidePool.assign(tour_id, day, preferred=None)`
1. Wenn Tour bereits einen Guide hat → diesen zurückgeben
2. Bevorzugter Guide (falls frei)
3. Erster freier Guide aus dem Pool
4. Wenn niemand frei → `ValueError`

Ein Guide gilt als frei, wenn er an dem Tag noch keiner anderen Tour zugewiesen ist (1 Tour pro Guide pro Tag).

---

## Beispiele für Touren

| ID | Name | Level | Dauer | Preis |
|---|---|---|---|---|
| `coastal-easy` | Coastal Cruise | easy | 3 h | 45 € |
| `hills-moderate` | Olive Grove Loop | moderate | 5 h | 65 € |
| `mountains-hard` | Lasithi Challenge | hard | 7 h | 90 € |

---

## FAQ

**Kann ich eine Tour stornieren?** Ja — Guide wird freigegeben, Plätze zurückgesetzt. Stornierungsfrist: 24 h vor Tourbeginn für volle Rückerstattung.

**Was bei Regen?** Bei Starkregen wird die Tour verschoben oder storniert — volle Rückerstattung. Leichter Regen: Tour findet mit Regen-Option statt.
