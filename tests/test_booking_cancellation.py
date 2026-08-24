import pytest
from models.user import User
from models.event_category import EventCategory
from models.venue import Venue
from models.seat import Seat
from models.event import Event
from models.booking import Booking
from config.database import db
from flask_jwt_extended import create_access_token
from datetime import date, time

@pytest.fixture
def cancel_setup(app):
    admin = User(name="Admin", email="admin@test.com", pass_hash="hash", role="ADMIN")
    manager = User(name="Manager", email="mgr@test.com", pass_hash="hash", role="EVENT_MANAGER")
    customer1 = User(name="Cust1", email="c1@test.com", pass_hash="hash", role="CUSTOMER")
    customer2 = User(name="Cust2", email="c2@test.com", pass_hash="hash", role="CUSTOMER")
    db.session.add_all([admin, manager, customer1, customer2])
    db.session.commit()

    venue = Venue(name="Venue", address="Addr", city="City", capacity=100, created_by=admin.id)
    category = EventCategory(name="Category", description="Desc")
    db.session.add_all([venue, category])
    db.session.commit()

    seat = Seat(venue_id=venue.id, seat_number="C1", row_name="C", category="REGULAR", base_price=50.0, is_active=True)
    db.session.add(seat)
    db.session.commit()

    event = Event(
        name="Rock Concert", description="Desc", category_id=category.id, venue_id=venue.id,
        start_date=date(2026, 11, 1), end_date=date(2026, 11, 1), start_time=time(20, 0), end_time=time(23, 0),
        maximum_capacity=100, vip_price=50.0, premium_price=50.0, regular_price=50.0,
        created_by=manager.id, status="UPCOMING", approval_status="APPROVED"
    )
    db.session.add(event)
    db.session.commit()

    cust1_token = create_access_token(identity=str(customer1.id), additional_claims={"role": "CUSTOMER"})
    cust2_token = create_access_token(identity=str(customer2.id), additional_claims={"role": "CUSTOMER"})
    mgr_token = create_access_token(identity=str(manager.id), additional_claims={"role": "EVENT_MANAGER"})

    return {
        "admin": admin, "manager": manager, "customer1": customer1, "customer2": customer2,
        "venue": venue, "category": category, "seat": seat, "event": event,
        "cust1_token": cust1_token, "cust2_token": cust2_token, "mgr_token": mgr_token
    }

def test_customer_cancel_own_confirmed_booking(client, cancel_setup):
    res_b = client.post("/api/bookings", json={"event_id": cancel_setup["event"].id, "seat_ids": [cancel_setup["seat"].id]}, headers={"Authorization": f"Bearer {cancel_setup['cust1_token']}"})
    b_id = res_b.json["booking"]["id"]
    client.post("/api/payments", json={"booking_id": b_id, "payment_method": "MOCK", "result": "SUCCESS"}, headers={"Authorization": f"Bearer {cancel_setup['cust1_token']}"})

    res_cancel = client.put(f"/api/bookings/{b_id}/cancel", headers={"Authorization": f"Bearer {cancel_setup['cust1_token']}"})
    assert res_cancel.status_code == 200
    assert res_cancel.json["booking"]["status"] == "CANCELLED"

def test_customer_cancel_other_customer_booking_fails(client, cancel_setup):
    res_b = client.post("/api/bookings", json={"event_id": cancel_setup["event"].id, "seat_ids": [cancel_setup["seat"].id]}, headers={"Authorization": f"Bearer {cancel_setup['cust1_token']}"})
    b_id = res_b.json["booking"]["id"]
    client.post("/api/payments", json={"booking_id": b_id, "payment_method": "MOCK", "result": "SUCCESS"}, headers={"Authorization": f"Bearer {cancel_setup['cust1_token']}"})

    res_cancel = client.put(f"/api/bookings/{b_id}/cancel", headers={"Authorization": f"Bearer {cancel_setup['cust2_token']}"})
    assert res_cancel.status_code == 400
    assert "You cannot cancel this booking" in res_cancel.json["message"]

def test_cancel_pending_unconfirmed_booking_fails(client, cancel_setup):
    res_b = client.post("/api/bookings", json={"event_id": cancel_setup["event"].id, "seat_ids": [cancel_setup["seat"].id]}, headers={"Authorization": f"Bearer {cancel_setup['cust1_token']}"})
    b_id = res_b.json["booking"]["id"]

    res_cancel = client.put(f"/api/bookings/{b_id}/cancel", headers={"Authorization": f"Bearer {cancel_setup['cust1_token']}"})
    assert res_cancel.status_code == 400
    assert "Only confirmed bookings can be cancelled" in res_cancel.json["message"]

def test_event_manager_cancels_event_cancels_bookings_and_notifies(client, cancel_setup):
    res_b = client.post("/api/bookings", json={"event_id": cancel_setup["event"].id, "seat_ids": [cancel_setup["seat"].id]}, headers={"Authorization": f"Bearer {cancel_setup['cust1_token']}"})
    b_id = res_b.json["booking"]["id"]
    client.post("/api/payments", json={"booking_id": b_id, "payment_method": "MOCK", "result": "SUCCESS"}, headers={"Authorization": f"Bearer {cancel_setup['cust1_token']}"})

    res_update = client.put(
        f"/api/events/{cancel_setup['event'].id}",
        json={"status": "CANCELLED"},
        headers={"Authorization": f"Bearer {cancel_setup['mgr_token']}"}
    )
    assert res_update.status_code == 200

    booking = Booking.query.get(b_id)
    assert booking.status == "CANCELLED"
    assert booking.payment.refund_status == "COMPLETED"
