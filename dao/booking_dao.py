from models.booking import Booking
from config.database import db


class BookingDAO:

    def get_all(self):
        return Booking.query.all()

    def get_by_id(self, booking_id):
        return Booking.query.get(booking_id)

    def get_by_reference(self, reference):
        return Booking.query.filter_by(
            booking_reference=reference
        ).first()

    def get_by_user(self, user_id):
        return Booking.query.filter_by(
            user_id=user_id
        ).all()

    def get_by_event(self, event_id):
        return Booking.query.filter_by(
            event_id=event_id
        ).all()

    def get_confirmed_by_user(self, user_id):
        return Booking.query.filter_by(
            user_id=user_id,
            status="CONFIRMED"
        ).all()

    def save(self, booking):
        db.session.add(booking)
        db.session.commit()
        return booking

    def save_with_items(self, booking, booking_items):
        """Persist a booking and its tickets as one transaction."""
        try:
            db.session.add(booking)
            db.session.add_all(booking_items)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return booking

    def update(self, booking):
        db.session.commit()
        return booking

    def cancel(self, booking):
        booking.status = "CANCELLED"
        db.session.commit()
        return booking
