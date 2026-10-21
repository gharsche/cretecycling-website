import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import unittest
from src.tours.catalog import Tour
from src.tours.booking import TourBooking
from src.tours.guides import GuidePool

class ToursTest(unittest.TestCase):
    def test_booking_capacity(self):
        b = TourBooking()
        b.book("knossos-sunset", "2026-10-24", 6, max_group=8)
        self.assertEqual(b.free_spots("knossos-sunset", "2026-10-24", 8), 2)
        with self.assertRaises(ValueError):
            b.book("knossos-sunset", "2026-10-24", 3, max_group=8)

    def test_guide_assignment(self):
        g = GuidePool(["Eleni", "Nikos"])
        self.assertEqual(g.assign("t1", "2026-10-24"), "Eleni")
        self.assertEqual(g.assign("t2", "2026-10-24"), "Nikos")
        with self.assertRaises(ValueError):
            g.assign("t3", "2026-10-24")

if __name__ == "__main__":
    unittest.main()
