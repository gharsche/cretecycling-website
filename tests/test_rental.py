import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import unittest
from datetime import date
from src.rental.fleet import Bike, Fleet, MAINTENANCE
from src.rental.pricing import rental_price
from src.rental.checkout import Rental, DEPOSIT

class RentalTest(unittest.TestCase):
    def test_pricing_multiday_discount(self):
        self.assertEqual(rental_price("trekking", 2), 50.0)
        self.assertEqual(rental_price("trekking", 3), 67.5)   # 75 - 10 %
        self.assertEqual(rental_price("e_bike", 7), 196.0)    # 245 - 20 %

    def test_unknown_model(self):
        with self.assertRaises(ValueError):
            rental_price("car", 1)

    def test_fleet_lifecycle(self):
        f = Fleet([Bike("B1", "trekking"), Bike("B2", "e_bike")])
        f.rent_out("B1")
        self.assertEqual(len(f.available()), 1)
        with self.assertRaises(ValueError):
            f.rent_out("B1")
        f.return_bike("B1", needs_service=True)
        self.assertEqual(f.bikes["B1"].status, MAINTENANCE)

    def test_checkout_deposit_refund(self):
        r = Rental("B2", "Anna", date(2026, 10, 22), 3, DEPOSIT["e_bike"])
        self.assertEqual(r.checkin(), 200.0)
        r2 = Rental("B2", "Ben", date(2026, 10, 22), 1, DEPOSIT["trekking"])
        self.assertEqual(r2.checkin(damaged=True), 0.0)

if __name__ == "__main__":
    unittest.main()
