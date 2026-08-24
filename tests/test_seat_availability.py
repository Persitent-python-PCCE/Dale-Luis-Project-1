import pytest
from models.user import User
from models.event_category import EventCategory
from models.venue import Venue
from models.seat import Seat
from models.event import Event
from models.booking import Booking
from models.booking_item import BookingItem
from dao.seat_dao import SeatDAO
from dao.booking_item_dao import BookingItemDAO
from service.booking_service import BookingService
from config.database import db
from datetime import date, time

@pytest.fixture
def seat_setup(app):
    admin = User(name="Admin", email="admin@test.com", pass_hash="hash", role="ADMIN")
    manager = User(name="Manager", email="mgr@test.com", pass_hash="hash", role="EVENT_MANAGER")
    customer = User(name="Customer", email="cust@test.com", pass_hash="hash", role="CUSTOMER")
    db.session.add_all([admin, manager, customer])
    db.session.commit()

    venue = Venue(name="Arena", address="St", city="City", capacity=100, created_by=admin.id)
    category = EventCategory(name="Category", description="Desc")
    db.session.add_all([venue, category])
    db.session.commit()

    seat_vip = Seat(venue_id=venue.id, seat_number="V1", row_name="V", category="VIP", base_price=150.0, is_active=True)
    seat_premium = Seat(venue_id=venue.id, seat_number="P1", row_name="P", category="PREMIUM", base_price=100.0, is_active=True)
    seat_regular = Seat(venue_id=venue.id, seat_number="R1", row_name="R", category="REGULAR", base_price=50.0, is_active=True)
    seat_inactive = Seat(venue_id=venue.id, seat_number="X1", row_name="X", category="REGULAR", base_price=50.0, is_active=False)
    db.session.add_all([seat_vip, seat_premium, seat_regular, seat_inactive])
    db.session.commit()

    event = Event(
        name="Concert", description="Desc", category_id=category.id, venue_id=venue.id,
        start_date=date(2026, 9, 1), end_date=date(2026, 9, 1), start_time=time(18, 0), end_time=time(21, 0),
        maximum_capacity=100, vip_price=150.0, premium_price=100.0, regular_price=50.0,
        created_by=manager.id, status="UPCOMING", approval_status="APPROVED"
    )
    db.session.add(event)
    db.session.commit()

    return {
        "admin": admin, "manager": manager, "customer": customer,
        "venue": venue, "category": category, "event": event,
        "seat_vip": seat_vip, "seat_premium": seat_premium, "seat_regular": seat_regular, "seat_inactive": seat_inactive
    }

def test_seat_price_calculation_by_category(seat_setup):
    booking_service = BookingService(None, BookingItemDAO(), None, SeatDAO())

    vip_price = booking_service.get_seat_price(seat_setup["event"], "VIP")
    premium_price = booking_service.get_seat_price(seat_setup["event"], "PREMIUM")
    regular_price = booking_service.get_seat_price(seat_setup["event"], "REGULAR")

    assert vip_price == 150.0
    assert premium_price == 100.0
    assert regular_price == 50.0

    with pytest.raises(ValueError):
        booking_service.get_seat_price(seat_setup["event"], "INVALID_CAT")

def test_seat_available_when_not_booked(seat_setup):
    booking_item_dao = BookingItemDAO()
    is_booked = booking_item_dao.is_seat_booked(seat_setup["event"].id, seat_setup["seat_vip"].id)
    assert is_booked is False

def test_seat_unavailable_when_booked(seat_setup):
    booking = Booking(
        user_id=seat_setup["customer"].id, event_id=seat_setup["event"].id, booking_reference="BK-SEAT1",
        total_amount=150.0, final_amount=150.0, status="CONFIRMED"
    )
    db.session.add(booking)
    db.session.commit()

    item = BookingItem(
        booking_id=booking.id, event_id=seat_setup["event"].id, seat_id=seat_setup["seat_vip"].id,
        seat_number=seat_setup["seat_vip"].seat_number, seat_category=seat_setup["seat_vip"].category,
        unit_price=150.0, ticket_status="VALID", qr_token="TOKEN123"
    )
    db.session.add(item)
    db.session.commit()

    booking_item_dao = BookingItemDAO()
    is_booked = booking_item_dao.is_seat_booked(seat_setup["event"].id, seat_setup["seat_vip"].id)
    assert is_booked is True

def test_venue_seats_retrieval(seat_setup):
    seat_dao = SeatDAO()
    venue_seats = seat_dao.get_by_venue(seat_setup["venue"].id)
    # 3 active seats out of 4 total
    assert len(venue_seats) == 3
