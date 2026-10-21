"""Plätze, Gruppen, Verfügbarkeit."""
class TourBooking:
    def __init__(self):
        self._spots = {}   # (tour_id, date_iso) -> {booked, guests}

    def book(self, tour_id: str, day: str, guests: int, max_group: int) -> None:
        key = (tour_id, day)
        booked = self._spots.get(key, 0)
        if booked + guests > max_group:
            raise ValueError(f"Tour {tour_id} am {day} ist voll ({booked}/{max_group})")
        self._spots[key] = booked + guests

    def free_spots(self, tour_id: str, day: str, max_group: int) -> int:
        return max_group - self._spots.get((tour_id, day), 0)
