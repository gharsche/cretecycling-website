"""Ausleihe & Rückgabe mit Kaution und Übergabeprotokoll."""
from dataclasses import dataclass, field
from datetime import date

DEPOSIT = {"e_bike": 200.0, "gravel": 100.0, "mtb": 150.0}

@dataclass
class Rental:
    bike_id: str
    customer: str
    start: date
    days: int
    deposit: float
    status: str = "active"     # active | returned | damaged

    def checkin(self, damaged: bool = False) -> float:
        """Rückgabe; gibt zurückerstattete Kaution zurück."""
        self.status = "damaged" if damaged else "returned"
        return 0.0 if damaged else self.deposit
