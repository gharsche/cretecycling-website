"""Anmeldung zu Workshops."""
class Registration:
    def __init__(self):
        self.signed_up = {}   # workshop_id -> set(participant)

    def register(self, workshop_id: str, participant: str, capacity: int) -> None:
        people = self.signed_up.setdefault(workshop_id, set())
        if participant in people:
            return
        if len(people) >= capacity:
            raise ValueError(f"Workshop {workshop_id} ist ausgebucht")
        people.add(participant)

    def waitlist_needed(self, workshop_id: str, capacity: int) -> bool:
        return len(self.signed_up.get(workshop_id, set())) >= capacity
