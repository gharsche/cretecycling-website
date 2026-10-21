# Booking-Guide — Gesamter Buchungs-Ablauf

Dieser Guide beschreibt den Buchungs-Ablauf über alle drei Bereiche (Verleih, Touren, Workshops) und wie sie zusammenwirken.

---

## 1. Verleih (Fahrrad)

```
Anfrage (Modell + Zeitraum)
  → Verfügbarkeit prüfen (fleet.available())
  → Preis berechnen (pricing.rental_price())
  → Übergabe: Kaution + Protokoll (checkout.Rental)
  → Bike auf rented (fleet.rent_out())
  → Rückgabe: checkin() → Kaution zurück oder Schaden
```

**Status-Kette:** `available` → `rented` → `available` (oder `maintenance` bei Wartung)

---

## 2. Touren

```
Tour auswählen (catalog.Tour)
  → Freie Plätze prüfen (booking.free_spots())
  → Plätze buchen (booking.book())
  → Guide zuweisen (guides.assign())
  → Bestätigung senden (notifications.booking_confirmation())
  → 24 h vorher: Erinnerung
```

**Status:** Plätze je (tour_id, day). Guide je (tour_id, day) — 1 Guide pro Tour pro Tag.

---

## 3. Workshops

```
Workshop auswählen (events.Workshop)
  → Kapazität prüfen (registration.register())
  → Wenn voll: Warteliste
  → Bestätigung senden
  → 24 h vorher: Erinnerung
```

**Status:** Teilnehmer je workshop_id. Bei `waitlist_needed() == True` → Warteliste aktiv.

---

## Geteilte Komponenten

| Komponente | Wo | Nutzen |
|---|---|---|
| `notifications.py` | `src/automation/` | Bestätigungen & Erinnerungen für alle Bereiche |
| `Outbox` | `src/automation/` | Zentrale Versand-Queue — in Produktion: E-Mail/Telegram |

Alle drei Bereiche nutzen dieselbe Notification-Infrastruktur. Eine Buchung in jedem Bereich löst `Outbox.booking_confirmation()` aus, eine Rückgabe löst `Outbox.rental_reminder()` aus.
