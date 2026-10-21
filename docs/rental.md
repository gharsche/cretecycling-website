# Fahrradverleih — Ablauf & Referenz

## Überblick

Der Verleihbereich verwaltet den Fuhrpark (E-Bikes, Gravel, MTB), berechnet Tarife mit Mehrtagesrabatten,-handhabt Kaution und Übergabeprotokoll.

**Module:** `src/rental/` — `fleet.py` · `pricing.py` · `checkout.py`
**Tests:** `tests/test_rental.py`

---

## Fuhrpark (`fleet.py`)

Jedes Bike hat einen Status: `available` → `rented` → `maintenance` → `available`.

| Feld | Werte |
|---|---|
| `id` | Eindeutige Bike-ID (z. B. `EB-01`) |
| `model` | `e_bike` · `gravel` · `mtb` |
| `status` | `available` · `rented` · `maintenance` |
| `service_due` | Optional, Datum der nächsten Wartung |

**Verfügbare Bikes abfragen:** `Fleet.available()` → Liste aller Bikes mit Status `available`.

**Ausleihe:** `Fleet.rent_out(bike_id)` setzt den Status auf `rented`. Falls nicht verfügbar, wirft `ValueError`.

**Rückgabe:** `Fleet.return_bike(bike_id, needs_service=False)` — bei `needs_service=True` geht das Bike auf `maintenance`, sonst zurück auf `available`.

---

## Tarife (`pricing.py`)

Tagessätze je Modell:

| Modell | Tagessatz |
|---|---|
| E-Bike | 35 € |
| Gravel | 30 € |
| MTB | 30 € |
| Kind | 15 € |

Mehrtagesrabatte:

| Dauer | Rabatt auf Gesamtpreis |
|---|---|
| ab 3 Tagen | 10 % |
| ab 7 Tagen | 20 % |

**Berechnung:** `rental_price(model, days)` → gerundet auf 2 Dezimalstellen.

Beispiele:
- E-Bike, 2 Tage → 70,00 €
- E-Bike, 5 Tage → 157,50 € (10 % Rabatt)
- E-Bike, 8 Tage → 224,00 € (20 % Rabatt)

---

## Kaution & Übergabe (`checkout.py`)

Kaution je Modell, fällig bei Übergabe:

| Modell | Kaution |
|---|---|
| E-Bike | 200 € |
| Gravel | 100 € |
| MTB | 150 € |
| Kind | 50 € |

**Ablauf:**

1. **Anfrage** — Modell + Zeitraum vom Kunden
2. **Preisberechnung** — `rental_price(model, days)`
3. **Übergabe** — Kaution erheben, Übergabeprotokoll (Zustand, Zubehör), Bike im System auf `rented`
4. **Rückgabe** — `Rental.checkin(damaged=False)`:
   - Ohne Schaden: Kaution wird vollständig zurückerstattet
   - Mit Schaden (`damaged=True`): Status auf `damaged`, Kaution einbehalten

**Statuswerte eines Rental:** `active` → `returned` | `damaged`

---

## FAQ

**Was passiert bei Schaden?** Status `damaged`, Kaution wird einbehalten. Das Bike geht anschließend auf `maintenance`.

**Wartung?** Bei `return_bike(needs_service=True)` oder wenn `service_due` erreicht ist, geht das Bike auf `maintenance` und steht nicht zur Ausleihe.
