"""Guide-Zuweisung."""
class GuidePool:
    def __init__(self, guides: list[str]):
        self.guides = list(guides)
        self.assignments = {}   # (tour_id, day) -> guide

    def assign(self, tour_id: str, day: str, preferred: str | None = None) -> str:
        key = (tour_id, day)
        if key in self.assignments:
            return self.assignments[key]
        guide = preferred if preferred in self.guides and self._free(preferred, day) else None
        if guide is None:
            guide = next((g for g in self.guides if self._free(g, day)), None)
        if guide is None:
            raise ValueError(f"Kein Guide frei am {day}")
        self.assignments[key] = guide
        return guide

    def _free(self, guide: str, day: str) -> bool:
        return not any(d == day and g == guide for (_, d), g in self.assignments.items())
