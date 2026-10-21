"""Workshop-Termine und Kapazität."""
from dataclasses import dataclass

@dataclass
class Workshop:
    id: str
    title: str              # z.B. "Bike-Grundwartung", "E-Bike Sicherheit"
    day: str                # ISO-Datum
    capacity: int
    price: float
