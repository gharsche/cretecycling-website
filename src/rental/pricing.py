"""Tagessätze und Mehrtagestarife."""
DAILY_RATES = {"e_bike": 35.0, "gravel": 30.0, "mtb": 30.0}

MULTIDAY_DISCOUNT = {  # Tage -> Rabatt auf Tage > 1
    3: 0.10,   # ab 3 Tagen 10 % auf den Gesamtpreis
    7: 0.20,   # ab 7 Tagen 20 %
}

def rental_price(model: str, days: int) -> float:
    if model not in DAILY_RATES:
        raise ValueError(f"Unbekanntes Modell: {model}")
    if days < 1:
        raise ValueError("Mindestens 1 Tag")
    base = DAILY_RATES[model] * days
    discount = 0.0
    for threshold in sorted(MULTIDAY_DISCOUNT, reverse=True):
        if days >= threshold:
            discount = MULTIDAY_DISCOUNT[threshold]
            break
    return round(base * (1 - discount), 2)
