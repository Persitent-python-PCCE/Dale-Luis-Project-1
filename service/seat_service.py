from models.seat import Seat

class SeatService:
    
    def __init__(self, seat_dao):
        self.seat_dao = seat_dao
        
    
    def get_seat(self,id):
        seat = self.seat_dao.get_by_id(id)

        if seat is None:
            raise ValueError("Seat not found")

        return seat
    
    def get_venue_seats(self, venue_id):
        return self.seat_dao.get_by_venue(venue_id)
    
    def get_seats_by_category(self,venue_id,category):
        return self.seat_dao.get_by_category(venue_id,category)
    
    def create_seat(self, data):

        required = ["venue_id", "seat_number", "row_name", "category", "base_price"]

        for field in required:
            if not data.get(field):
                raise ValueError(f"{field} is required")

        existing = self.seat_dao.get_by_seat_number(
            data["venue_id"],
            data["seat_number"]
        )

        if existing:
            raise ValueError("Seat already exists")

        seat = Seat(
            venue_id=data["venue_id"],
            seat_number=data["seat_number"],
            row_name=data["row_name"],
            base_price=data["base_price"],
            category=data["category"]
        )

        return self.seat_dao.save(seat)
    
    def create_multiple_seats(self,venue_id,seats):
        seat_objects = []

        for seat_data in seats:

            for field in ("seat_number", "row_name", "category", "base_price"):
                if not seat_data.get(field):
                    raise ValueError(f"{field} is required")

            if self.seat_dao.get_by_seat_number(venue_id, seat_data["seat_number"]):
                raise ValueError(f"Seat {seat_data['seat_number']} already exists")

            seat = Seat(
                venue_id=venue_id,
                seat_number=seat_data["seat_number"],
                row_name=seat_data["row_name"],
                base_price=seat_data["base_price"],
                category=seat_data["category"]
            )

            seat_objects.append(seat)

        return self.seat_dao.save_all(seat_objects)
    
    def update_seat(self, id, data):
        seat = self.get_seat(id)

        if "seat_number" in data:
            seat.seat_number = data["seat_number"]

        if "category" in data:
            seat.category = data["category"]

        if "row_name" in data:
            seat.row_name = data["row_name"]

        if "base_price" in data:
            seat.base_price = data["base_price"]

        return self.seat_dao.update(seat)
    
    def delete_seat(self, id):
        seat = self.get_seat(id)

        return self.seat_dao.delete(seat)
