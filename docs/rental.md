# Fahrradverleih — Ablauf

1. **Anfrage**: Modell + Zeitraum (E-Bike, Trekking, MTB, Kind).
2. **Preis**: Tagessätze, automatisch 10 % ab 3 Tagen, 20 % ab 7 Tagen (`src/rental/pricing.py`).
3. **Kaution**: 50–200 € je Modell bei Übergabe.
4. **Übergabe**: Protokoll (Zustand, Zubehör), Bike im System auf `rented`.
5. **Rückgabe**: Status prüfen → Kaution zurück oder Schaden dokumentieren.
