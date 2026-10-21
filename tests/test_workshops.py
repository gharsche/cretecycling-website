import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import unittest
from src.workshops.registration import Registration

class WorkshopsTest(unittest.TestCase):
    def test_registration_and_full(self):
        r = Registration()
        r.register("w1", "Anna", capacity=2)
        r.register("w1", "Ben", capacity=2)
        self.assertTrue(r.waitlist_needed("w1", 2))
        with self.assertRaises(ValueError):
            r.register("w1", "Cleo", capacity=2)

    def test_double_registration_ok(self):
        r = Registration()
        r.register("w1", "Anna", capacity=1)
        r.register("w1", "Anna", capacity=1)
        self.assertEqual(len(r.signed_up["w1"]), 1)

if __name__ == "__main__":
    unittest.main()
