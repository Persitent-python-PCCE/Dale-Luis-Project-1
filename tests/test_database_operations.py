import pytest
from models.user import User
from models.event_category import EventCategory
from models.venue import Venue
from models.seat import Seat
from models.event import Event
from models.booking import Booking
from models.booking_item import BookingItem
from models.payment import Payment
from dao.user_dao import UserDAO
from dao.event_dao import EventDAO
from dao.venue_dao import VenueDAO
from dao.seat_dao import SeatDAO
from dao.booking_dao import BookingDAO
from dao.booking_item_dao import BookingItemDAO
from dao.payment_dao import PaymentDAO
from dao.event_category_dao import EventCategoryDAO
from datetime import datetime, date, time

@pytest.fixture
def dao_setup(app):
    return {
        "user_dao": UserDAO(),
        "event_dao": EventDAO(),
        "venue_dao": VenueDAO(),
        "seat_dao": SeatDAO(),
        "booking_dao": BookingDAO(),
        "booking_item_dao": BookingItemDAO(),
        "payment_dao": PaymentDAO(),
        "category_dao": EventCategoryDAO()
    }

def test_user_dao_operations(app, dao_setup):
    user_dao = dao_setup["user_dao"]
    with app.app_context():
        user = User(name="DAO User", email="dao@example.com", pass_hash="hash", role="CUSTOMER")
        saved_user = user_dao.save(user)
        assert saved_user.id is not None

        by_id = user_dao.get_by_id(saved_user.id)
        assert by_id.email == "dao@example.com"

        by_email = user_dao.get_by_email("dao@example.com")
        assert by_email.id == saved_user.id

        results = user_dao.search("DAO")
        assert len(results) == 1

        user_dao.deactivate(saved_user)
        assert saved_user.is_active is False

def test_venue_and_seat_dao_operations(app, dao_setup):
    user_dao = dao_setup["user_dao"]
    venue_dao = dao_setup["venue_dao"]
    seat_dao = dao_setup["seat_dao"]

    with app.app_context():
        user = User(name="Admin User", email="admin_dao@example.com", pass_hash="hash", role="ADMIN")
        user_dao.save(user)

        venue = Venue(name="DAO Arena", address="123 Street", city="City", capacity=500, created_by=user.id)
        saved_venue = venue_dao.save(venue)
        assert saved_venue.id is not None

        seat1 = Seat(venue_id=saved_venue.id, seat_number="D1", row_name="D", category="VIP", base_price=100.0, is_active=True)
        seat2 = Seat(venue_id=saved_venue.id, seat_number="D2", row_name="D", category="REGULAR", base_price=50.0, is_active=True)
        seat_dao.save(seat1)
        seat_dao.save(seat2)

        venue_seats = seat_dao.get_by_venue(saved_venue.id)
        assert len(venue_seats) == 2

def test_event_dao_operations(app, dao_setup):
    user_dao = dao_setup["user_dao"]
    category_dao = dao_setup["category_dao"]
    venue_dao = dao_setup["venue_dao"]
    event_dao = dao_setup["event_dao"]

    with app.app_context():
        user = User(name="Mgr User", email="mgr_dao@example.com", pass_hash="hash", role="EVENT_MANAGER")
        user_dao.save(user)

        category = EventCategory(name="DAO Cat", description="Desc")
        category_dao.save(category)

        venue = Venue(name="DAO Hall", address="Addr", city="City", capacity=200, created_by=user.id)
        venue_dao.save(venue)

        event = Event(
            name="DAO Event", description="Desc", category_id=category.id, venue_id=venue.id,
            start_date=date(2026, 12, 1), end_date=date(2026, 12, 1), start_time=time(10, 0), end_time=time(12, 0),
            maximum_capacity=200, vip_price=20.0, premium_price=20.0, regular_price=20.0,
            created_by=user.id, status="UPCOMING", approval_status="PENDING"
        )
        saved_event = event_dao.save(event)

        event_dao.approve(saved_event, user.id)
        assert saved_event.approval_status == "APPROVED"

        approved = event_dao.get_approved_events()
        assert len(approved) == 1

def test_booking_and_payment_dao_operations(app, dao_setup):
    user_dao = dao_setup["user_dao"]
    category_dao = dao_setup["category_dao"]
    venue_dao = dao_setup["venue_dao"]
    seat_dao = dao_setup["seat_dao"]
    event_dao = dao_setup["event_dao"]
    booking_dao = dao_setup["booking_dao"]
    payment_dao = dao_setup["payment_dao"]

    with app.app_context():
        user = User(name="Customer User", email="cust_dao@example.com", pass_hash="hash", role="CUSTOMER")
        user_dao.save(user)

        category = EventCategory(name="Cat", description="Desc")
        category_dao.save(category)

        venue = Venue(name="Hall", address="Addr", city="City", capacity=100, created_by=user.id)
        venue_dao.save(venue)

        seat = Seat(venue_id=venue.id, seat_number="E1", row_name="E", category="REGULAR", base_price=10.0, is_active=True)
        seat_dao.save(seat)

        event = Event(
            name="Event", description="D", category_id=category.id, venue_id=venue.id,
            start_date=date(2026, 12, 1), end_date=date(2026, 12, 1), start_time=time(10, 0), end_time=time(12, 0),
            maximum_capacity=100, vip_price=10.0, premium_price=10.0, regular_price=10.0,
            created_by=user.id, status="UPCOMING", approval_status="APPROVED"
        )
        event_dao.save(event)

        booking = Booking(
            user_id=user.id, event_id=event.id, booking_reference="BK-DAO1",
            total_amount=10.0, final_amount=10.0, status="PENDING"
        )
        item = BookingItem(
            booking=booking, event_id=event.id, seat_id=seat.id, seat_number=seat.seat_number,
            seat_category=seat.category, unit_price=10.0, ticket_status="VALID", qr_token="TOKEN_DAO"
        )
        saved_booking = booking_dao.save_with_items(booking, [item])
        assert saved_booking.id is not None

        payment = Payment(
            booking_id=saved_booking.id, transaction_id="TX-DAO1", payment_method="MOCK",
            amount=10.0, status="SUCCESS", paid_at=datetime.utcnow()
        )
        saved_payment = payment_dao.save(payment)
        by_booking = payment_dao.get_by_booking(saved_booking.id)
        assert by_booking.id == saved_payment.id
