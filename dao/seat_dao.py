from models.seat import Seat
from config.database import db


class SeatDAO:

    def get_all(self):
        return Seat.query.filter_by(
            is_active=True
        ).all()

    def get_by_id(self, id):
        return Seat.query.get(id)
    
    def get_by_event_and_seat_number(self,event_id,seat_number):
        
        return Seat.query.filter_by(
            event_id=event_id,
            seat_number=seat_number).first()
    
    def get_and_lock_seat(self,seat_id):
        seat = Seat.query.filter_by(id = seat_id).with_for_update().first()
        
        return seat
    
    def get_and_lock_seats(self,seat_ids):
        seats = (
            Seat.query
            .filter(Seat.id.in_(sorted(seat_ids)))
            .order_by(Seat.id)
            .with_for_update()
            .all()
        )

        return seats

    def get_by_venue(self, venue_id):
        return Seat.query.filter_by(
            venue_id=venue_id,
            is_active=True
        ).order_by(Seat.id).all()

    def ensure_venue_seats(self, venue_id, target_capacity):
        if not target_capacity or target_capacity <= 0:
            target_capacity = 50

        existing_seats = Seat.query.filter_by(venue_id=venue_id).all()
        existing_numbers = {s.seat_number for s in existing_seats}

        if len(existing_seats) < target_capacity:
            seats_per_row = 10 if target_capacity <= 100 else 20
            new_seats = []

            for idx in range(1, target_capacity + 1):
                row_idx = (idx - 1) // seats_per_row
                seat_in_row = ((idx - 1) % seats_per_row) + 1

                if row_idx < 26:
                    row_letter = chr(65 + row_idx)
                else:
                    row_letter = f"R{row_idx + 1}"

                seat_number = f"{row_letter}{seat_in_row}"

                if seat_number in existing_numbers:
                    continue

                if row_idx == 0:
                    category = "VIP"
                    base_price = 150.0
                elif row_idx in (1, 2):
                    category = "PREMIUM"
                    base_price = 100.0
                else:
                    category = "REGULAR"
                    base_price = 50.0

                new_seat = Seat(
                    venue_id=venue_id,
                    seat_number=seat_number,
                    row_name=row_letter,
                    category=category,
                    base_price=base_price,
                    is_active=True,
                )
                new_seats.append(new_seat)
                existing_numbers.add(seat_number)

            if new_seats:
                db.session.add_all(new_seats)
                db.session.commit()

        return Seat.query.filter_by(venue_id=venue_id, is_active=True).order_by(Seat.id).all()

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
