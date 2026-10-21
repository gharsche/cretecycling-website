import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import unittest
from src.automation.notifications import Outbox

class AutomationTest(unittest.TestCase):
    def test_outbox(self):
        o = Outbox()
        o.booking_confirmation("anna@example.com", "Knossos Sunset Tour", "2026-10-24")
        o.rental_reminder("ben@example.com", "B1", "2026-10-27")
        self.assertEqual(len(o.sent), 2)
        self.assertIn("Rückgabe", o.sent[1].subject)

if __name__ == "__main__":
    unittest.main()
