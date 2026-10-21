"""Tour-Katalog: Route, Level, Dauer, Kapazität."""
from dataclasses import dataclass

@dataclass
class Tour:
    id: str
    name: str
    level: str          # easy | moderate | hard
    duration_hours: float
    price: float
    max_group: int
