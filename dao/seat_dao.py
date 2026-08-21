from models.seat import Seat
from config.database import db


class SeatDAO:

    def get_all(self):
        return Seat.query.filter_by(
            is_active=True
        ).all()

    def get_by_id(self, seat_id):
        return Seat.query.get(seat_id)

    def get_by_venue(self, venue_id):
        return Seat.query.filter_by(
            venue_id=venue_id,
            is_active=True
        ).all()

    def get_by_category(self, venue_id, category):
        return Seat.query.filter_by(
            venue_id=venue_id,
            category=category,
            is_active=True
        ).all()

    def get_by_seat_number(self, venue_id, seat_number):
        return Seat.query.filter_by(
            venue_id=venue_id,
            seat_number=seat_number
        ).first()

    def save(self, seat):
        db.session.add(seat)
        db.session.commit()
        return seat

    def save_all(self, seats):
        db.session.add_all(seats)
        db.session.commit()
        return seats

    def update(self, seat):
        db.session.commit()
        return seat

    def delete(self, seat):
        seat.is_active = False
        db.session.commit()
        return seat