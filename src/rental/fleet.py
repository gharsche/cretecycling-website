"""Fuhrpark: Bikes, Status, Verfügbarkeit."""
from dataclasses import dataclass, field
from datetime import date

AVAILABLE = "available"
RENTED = "rented"
MAINTENANCE = "maintenance"

@dataclass
class Bike:
    id: str
    model: str          # e_bike | gravel | mtb | kid
    status: str = AVAILABLE
    service_due: date | None = None

class Fleet:
    def __init__(self, bikes: list[Bike] = None):
        self.bikes = {b.id: b for b in (bikes or [])}

    def add(self, bike: Bike) -> None:
        self.bikes[bike.id] = bike

    def available(self) -> list[Bike]:
        return [b for b in self.bikes.values() if b.status == AVAILABLE]

    def rent_out(self, bike_id: str) -> None:
        b = self.bikes[bike_id]
        if b.status != AVAILABLE:
            raise ValueError(f"Bike {bike_id} ist nicht verfügbar ({b.status})")
        b.status = RENTED

    def return_bike(self, bike_id: str, needs_service: bool = False) -> None:
        b = self.bikes[bike_id]
        b.status = MAINTENANCE if needs_service else AVAILABLE
