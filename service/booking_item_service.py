class BookingItemService:

    def __init__(self, booking_item_dao):
        self.booking_item_dao = booking_item_dao
        
    def get_item(self, id):
        item = self.booking_item_dao.get_by_id(id)

        if item is None:
            raise ValueError("Booking item not found")

        return item
    
    def get_booking_items(self, booking_id):
        return self.booking_item_dao.get_by_booking(booking_id)

    def get_event_items(self, event_id):
        return self.booking_item_dao.get_by_event(event_id)

    def get_booked_seats(self, event_id):
        return self.booking_item_dao.get_booked_seats(event_id)

    def is_seat_booked(self,event_id,seat_id):
        return self.booking_item_dao.is_seat_booked(event_id,seat_id)