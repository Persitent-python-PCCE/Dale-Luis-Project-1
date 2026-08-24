import pytest
from models.user import User
from models.event_category import EventCategory
from models.venue import Venue
from models.event import Event
from models.booking import Booking
from models.payment import Payment
from config.database import db
from flask_jwt_extended import create_access_token
from datetime import datetime, date, time

@pytest.fixture
def auth_roles(app):
    customer = User(name="Cust", email="cust@test.com", pass_hash="hash", role="CUSTOMER")
    customer2 = User(name="Cust2", email="cust2@test.com", pass_hash="hash", role="CUSTOMER")
    manager = User(name="Mgr", email="mgr@test.com", pass_hash="hash", role="EVENT_MANAGER")
    admin = User(name="Admin", email="admin@test.com", pass_hash="hash", role="ADMIN")
    db.session.add_all([customer, customer2, manager, admin])
    db.session.commit()

    cust_token = create_access_token(identity=str(customer.id), additional_claims={"role": "CUSTOMER"})
    cust2_token = create_access_token(identity=str(customer2.id), additional_claims={"role": "CUSTOMER"})
    mgr_token = create_access_token(identity=str(manager.id), additional_claims={"role": "EVENT_MANAGER"})
    admin_token = create_access_token(identity=str(admin.id), additional_claims={"role": "ADMIN"})

    return {
        "customer": customer, "customer2": customer2, "manager": manager, "admin": admin,
        "cust_token": cust_token, "cust2_token": cust2_token, "mgr_token": mgr_token, "admin_token": admin_token
    }

def test_customer_cannot_create_event(client, auth_roles):
    res = client.post(
        "/api/events",
        json={"name": "Forbidden Event"},
        headers={"Authorization": f"Bearer {auth_roles['cust_token']}"}
    )
    assert res.status_code == 403
    assert res.json["message"] == "Unauthorized"

def test_manager_cannot_approve_event(client, auth_roles):
    category = EventCategory(name="Cat", description="Desc")
    venue = Venue(name="V", address="A", city="C", capacity=100, created_by=auth_roles["admin"].id)
    db.session.add_all([category, venue])
    db.session.commit()

    event = Event(
        name="Pending Event", description="D", category_id=category.id, venue_id=venue.id,
        start_date=date(2026, 9, 1), end_date=date(2026, 9, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10, premium_price=10, regular_price=10,
        created_by=auth_roles["manager"].id, status="UPCOMING", approval_status="PENDING"
    )
    db.session.add(event)
    db.session.commit()
    event_id = event.id

    res = client.put(
        f"/api/events/{event_id}/approve",
        headers={"Authorization": f"Bearer {auth_roles['mgr_token']}"}
    )
    assert res.status_code == 403
    assert res.json["message"] == "Unauthorized"

def test_admin_can_approve_event(client, auth_roles):
    category = EventCategory(name="Cat", description="Desc")
    venue = Venue(name="V", address="A", city="C", capacity=100, created_by=auth_roles["admin"].id)
    db.session.add_all([category, venue])
    db.session.commit()

    event = Event(
        name="Pending Event", description="D", category_id=category.id, venue_id=venue.id,
        start_date=date(2026, 9, 1), end_date=date(2026, 9, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10, premium_price=10, regular_price=10,
        created_by=auth_roles["manager"].id, status="UPCOMING", approval_status="PENDING"
    )
    db.session.add(event)
    db.session.commit()
    event_id = event.id

    res = client.put(
        f"/api/events/{event_id}/approve",
        headers={"Authorization": f"Bearer {auth_roles['admin_token']}"}
    )
    assert res.status_code == 200
    assert res.json["event"]["approval_status"] == "APPROVED"

def test_customer_cannot_access_other_customer_booking(client, auth_roles):
    category = EventCategory(name="Cat", description="Desc")
    venue = Venue(name="V", address="A", city="C", capacity=100, created_by=auth_roles["admin"].id)
    db.session.add_all([category, venue])
    db.session.commit()

    event = Event(
        name="Event", description="D", category_id=category.id, venue_id=venue.id,
        start_date=date(2026, 9, 1), end_date=date(2026, 9, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10, premium_price=10, regular_price=10,
        created_by=auth_roles["manager"].id, status="UPCOMING", approval_status="APPROVED"
    )
    db.session.add(event)
    db.session.commit()

    booking = Booking(
        user_id=auth_roles["customer"].id, event_id=event.id, booking_reference="BK-CUST1",
        total_amount=10.0, final_amount=10.0, status="CONFIRMED"
    )
    db.session.add(booking)
    db.session.commit()
    booking_id = booking.id

    # Customer 2 attempts to get Customer 1's booking
    res = client.get(
        f"/api/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {auth_roles['cust2_token']}"}
    )
    assert res.status_code == 403
    assert res.json["message"] == "You cannot access this booking"

    # Admin gets Customer 1's booking -> Allowed
    res_admin = client.get(
        f"/api/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {auth_roles['admin_token']}"}
    )
    assert res_admin.status_code == 200

def test_customer_cannot_access_other_customer_payment(client, auth_roles):
    category = EventCategory(name="Cat", description="Desc")
    venue = Venue(name="V", address="A", city="C", capacity=100, created_by=auth_roles["admin"].id)
    db.session.add_all([category, venue])
    db.session.commit()

    event = Event(
        name="Event", description="D", category_id=category.id, venue_id=venue.id,
        start_date=date(2026, 9, 1), end_date=date(2026, 9, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10, premium_price=10, regular_price=10,
        created_by=auth_roles["manager"].id, status="UPCOMING", approval_status="APPROVED"
    )
    db.session.add(event)
    db.session.commit()

    booking = Booking(
        user_id=auth_roles["customer"].id, event_id=event.id, booking_reference="BK-PAY1",
        total_amount=10.0, final_amount=10.0, status="CONFIRMED"
    )
    db.session.add(booking)
    db.session.commit()

    payment = Payment(
        booking_id=booking.id, transaction_id="TX-PAY1", payment_method="MOCK",
        amount=10.0, status="SUCCESS", paid_at=datetime.utcnow()
    )
    db.session.add(payment)
    db.session.commit()
    payment_id = payment.id

    # Customer 2 attempts to get Customer 1's payment
    res = client.get(
        f"/api/payments/{payment_id}",
        headers={"Authorization": f"Bearer {auth_roles['cust2_token']}"}
    )
    assert res.status_code == 403
    assert res.json["message"] == "You cannot access this payment"
