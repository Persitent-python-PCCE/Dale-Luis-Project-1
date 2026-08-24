import pytest
from models.user import User
from models.event_category import EventCategory
from models.venue import Venue
from models.seat import Seat
from models.event import Event
from config.database import db
from flask_jwt_extended import create_access_token
from datetime import date, time

@pytest.fixture
def booking_setup(app):
    admin = User(name="Admin", email="admin@test.com", pass_hash="hash", role="ADMIN")
    manager = User(name="Manager", email="mgr@test.com", pass_hash="hash", role="EVENT_MANAGER")
    customer = User(name="Customer", email="customer@test.com", pass_hash="hash", role="CUSTOMER")
    db.session.add_all([admin, manager, customer])
    db.session.commit()

    venue = Venue(name="Arena", address="100 St", city="City", capacity=500, created_by=admin.id)
    category = EventCategory(name="Pop", description="Pop music")
    db.session.add_all([venue, category])
    db.session.commit()

    seat1 = Seat(venue_id=venue.id, seat_number="A1", row_name="A", category="VIP", base_price=200.0, is_active=True)
    seat2 = Seat(venue_id=venue.id, seat_number="A2", row_name="A", category="REGULAR", base_price=50.0, is_active=True)
    db.session.add_all([seat1, seat2])
    db.session.commit()

    event = Event(
        name="Pop Star Concert", description="Live show", category_id=category.id, venue_id=venue.id,
        start_date=date(2026, 10, 10), end_date=date(2026, 10, 10), start_time=time(19, 0), end_time=time(22, 0),
        maximum_capacity=500, vip_price=200.0, premium_price=100.0, regular_price=50.0,
        created_by=manager.id, status="UPCOMING", approval_status="APPROVED"
    )
    db.session.add(event)
    db.session.commit()

    cust_token = create_access_token(identity=str(customer.id), additional_claims={"role": "CUSTOMER"})

    return {
        "customer": customer, "event": event, "seat1": seat1, "seat2": seat2, "cust_token": cust_token
    }

def test_create_and_pay_successful_booking(client, booking_setup):
    # 1. Create booking for seats A1 (VIP: 200) and A2 (REGULAR: 50) -> total 250.0
    booking_payload = {
        "event_id": booking_setup["event"].id,
        "seat_ids": [booking_setup["seat1"].id, booking_setup["seat2"].id]
    }
    res_booking = client.post(
        "/api/bookings",
        json=booking_payload,
        headers={"Authorization": f"Bearer {booking_setup['cust_token']}"}
    )
    assert res_booking.status_code == 201
    booking = res_booking.json["booking"]
    assert booking["status"] == "PENDING"
    assert booking["final_amount"] == 250.0
    assert len(booking["items"]) == 2

    booking_id = booking["id"]

    # 2. Process mock payment for the pending booking
    payment_payload = {
        "booking_id": booking_id,
        "payment_method": "MOCK",
        "result": "SUCCESS"
    }
    res_payment = client.post(
        "/api/payments",
        json=payment_payload,
        headers={"Authorization": f"Bearer {booking_setup['cust_token']}"}
    )
    assert res_payment.status_code == 200
    assert res_payment.json["payment"]["status"] == "SUCCESS"

    # 3. Verify booking status changed to CONFIRMED
    res_get_booking = client.get(
        f"/api/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {booking_setup['cust_token']}"}
    )
    assert res_get_booking.status_code == 200
    assert res_get_booking.json["status"] == "CONFIRMED"

def test_ticket_qr_generation(client, booking_setup):
    booking_payload = {"event_id": booking_setup["event"].id, "seat_ids": [booking_setup["seat1"].id]}
    res_b = client.post("/api/bookings", json=booking_payload, headers={"Authorization": f"Bearer {booking_setup['cust_token']}"})
    b_id = res_b.json["booking"]["id"]
    ticket_id = res_b.json["booking"]["items"][0]["id"]

    client.post("/api/payments", json={"booking_id": b_id, "payment_method": "CARD", "result": "SUCCESS"}, headers={"Authorization": f"Bearer {booking_setup['cust_token']}"})

    res_qr = client.get(
        f"/bookings/{b_id}/tickets/{ticket_id}/qr",
        headers={"Authorization": f"Bearer {booking_setup['cust_token']}"}
    )
    assert res_qr.status_code == 200
    assert res_qr.mimetype == "image/png"
