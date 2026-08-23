import uuid
from models.booking import Booking
from models.booking_item import BookingItem
from config.database import db

class BookingService:
    def __init__(self,booking_dao,booking_item_dao,event_dao,seat_dao):
        self.booking_dao = booking_dao
        self.booking_item_dao = booking_item_dao
        self.event_dao = event_dao
        self.seat_dao = seat_dao
        
    def create_booking(self,user_id,event_id,seat_ids):
        if not seat_ids:
            raise ValueError("At least one seat is required")

        if len(seat_ids) != len(set(seat_ids)):
            raise ValueError("A seat can only be selected once")

        try:
            # The row locks below are held by this session until the single
            # commit in save_with_items().
            event = self.event_dao.get_by_id(event_id)

            if event is None:
                raise ValueError("Event not found")

            if event.approval_status != "APPROVED":
                raise ValueError("Event is not available for booking")

            if event.status != "UPCOMING":
                raise ValueError("Event is not available for booking")

            seats = self.seat_dao.get_and_lock_seats(seat_ids)

            if len(seats) != len(seat_ids):
                raise ValueError("One or more seats were not found")
        
            total_amount = 0
            booking_items = []

            for seat in seats:

                if not seat.is_active:
                    raise ValueError(f"Seat {seat.seat_number} is inactive")

                if seat.venue_id != event.venue_id:
                    raise ValueError(f"Seat {seat.seat_number} does not belong to this event venue")

                if self.booking_item_dao.is_seat_booked(event_id,seat.id):
                    raise ValueError(f"Seat {seat.seat_number} is already booked")
            
                price = self.get_seat_price(event,seat.category)


                total_amount += price
            
                booking_items.append({"seat": seat,"price": price})

            booking_reference = ("BK-" +uuid.uuid4().hex[:10].upper())

            booking = Booking(
                user_id=user_id,
                event_id=event_id,
                booking_reference=booking_reference,
                total_amount=total_amount,
                final_amount=total_amount,
                status="PENDING"
            )

            items = []

            for item in booking_items:
                seat = item["seat"]
                booking_item = BookingItem(
                    booking=booking,
                    event_id=event_id,
                    seat_id=seat.id,
                    seat_number=seat.seat_number,
                    seat_category=seat.category,
                    unit_price=item["price"],
                    ticket_status="VALID",
                    qr_token=uuid.uuid4().hex
                )

                items.append(booking_item)

            booking = self.booking_dao.save_with_items(booking,items)
            return booking


        except Exception:
            db.session.rollback()
            raise
    
    def get_seat_price(self,event,category):
        if category == "VIP":
            return event.vip_price

        if category == "PREMIUM":
            return event.premium_price

        if category == "REGULAR":
            return event.regular_price

        raise ValueError("Invalid seat category")
    
    def get_booking(self, id):
        booking = self.booking_dao.get_by_id(id)

        if booking is None:
            raise ValueError("Booking not found")

        return booking
    
    def get_user_bookings(self, user_id):
        return self.booking_dao.get_by_user(user_id)
    
    def get_event_bookings(self, event_id):
        return self.booking_dao.get_by_event(event_id)
    
    def cancel_booking(self,id,user_id):
        try:
            booking = self.booking_dao.get_and_lock_by_id(id)

            if booking is None:
                raise ValueError("Booking not found")
            if booking.user_id != user_id:
                raise ValueError("You cannot cancel this booking")
            if booking.status != "CONFIRMED":
                raise ValueError("Only confirmed bookings can be cancelled")

            booking.status = "CANCELLED"
            db.session.commit()
            return booking
        except Exception:
            db.session.rollback()
            raise
