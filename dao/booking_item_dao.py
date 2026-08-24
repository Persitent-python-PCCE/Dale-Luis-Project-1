from models.booking_item import BookingItem
from models.booking import Booking
from config.database import db


class BookingItemDAO:

    def get_by_id(self, item_id):
        return BookingItem.query.get(item_id)

    def get_by_booking(self, booking_id):
        return BookingItem.query.filter_by(
            booking_id=booking_id
        ).all()

    def get_by_event(self, event_id):
        return BookingItem.query.filter_by(
            event_id=event_id
        ).all()

    def get_by_seat(self, seat_id):
        return BookingItem.query.filter_by(
            seat_id=seat_id
        ).all()

    def is_seat_booked(self, event_id, seat_id):

        result = (
            db.session.query(BookingItem)
            .join(
                Booking,
                BookingItem.booking_id == Booking.id
            )
            .filter(
                BookingItem.event_id == event_id,
                BookingItem.seat_id == seat_id,

                Booking.status.in_(["PENDING", "CONFIRMED"]),
                BookingItem.ticket_status == "VALID"
            )


            .with_for_update()
            .first()
        )

        return result is not None

    def get_booked_seats(self, event_id):

        return (
            db.session.query(BookingItem.seat_id)
            .join(
                Booking,
                BookingItem.booking_id == Booking.id
            )
            .filter(
                BookingItem.event_id == event_id,
                Booking.status == "CONFIRMED",
                BookingItem.ticket_status == "VALID"
            )
            .all()
        )

    def save(self, booking_item):
        db.session.add(booking_item)
        db.session.commit()
        return booking_item

    def save_all(self, booking_items):
        db.session.add_all(booking_items)
        db.session.commit()
        return booking_items

    def update(self, booking_item):
        db.session.commit()
        return booking_item

    def cancel(self, booking_item):
        booking_item.ticket_status = "CANCELLED"
        db.session.commit()
        return booking_item
