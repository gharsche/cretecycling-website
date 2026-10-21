"""Benachrichtigungen: Buchungsbestätigungen, Erinnerungen."""
from dataclasses import dataclass, field

@dataclass
class Notification:
    to: str
    subject: str
    body: str

@dataclass
class Outbox:
    sent: list[Notification] = field(default_factory=list)

    def send(self, n: Notification) -> None:
        self.sent.append(n)   # in Produktion: E-Mail/Telegram-Versand

    def booking_confirmation(self, to, what, day):
        self.send(Notification(to, f"Bestätigung: {what}", f"{what} am {day} ist gebucht. Wir sehen uns in Sissi!"))

    def rental_reminder(self, to, bike_id, return_day):
        self.send(Notification(to, f"Rückgabe {bike_id}", f"Bitte gib Bike {bike_id} am {return_day} zurück."))
