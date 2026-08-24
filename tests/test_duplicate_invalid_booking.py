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
def dup_setup(app):
    admin = User(name="Admin", email="admin@test.com", pass_hash="hash", role="ADMIN")
    manager = User(name="Manager", email="mgr@test.com", pass_hash="hash", role="EVENT_MANAGER")
    customer1 = User(name="Cust1", email="cust1@test.com", pass_hash="hash", role="CUSTOMER")
    customer2 = User(name="Cust2", email="cust2@test.com", pass_hash="hash", role="CUSTOMER")
    db.session.add_all([admin, manager, customer1, customer2])
    db.session.commit()

    venue1 = Venue(name="Venue 1", address="Addr 1", city="City", capacity=100, created_by=admin.id)
    venue2 = Venue(name="Venue 2", address="Addr 2", city="City", capacity=100, created_by=admin.id)
    category = EventCategory(name="Category", description="Desc")
    db.session.add_all([venue1, venue2, category])
    db.session.commit()

    seat_v1 = Seat(venue_id=venue1.id, seat_number="S1", row_name="S", category="REGULAR", base_price=10.0, is_active=True)
    seat_v2 = Seat(venue_id=venue2.id, seat_number="S2", row_name="S", category="REGULAR", base_price=10.0, is_active=True)
    seat_inactive = Seat(venue_id=venue1.id, seat_number="S3", row_name="S", category="REGULAR", base_price=10.0, is_active=False)
    db.session.add_all([seat_v1, seat_v2, seat_inactive])
    db.session.commit()

    approved_event = Event(
        name="Approved Event", description="Desc", category_id=category.id, venue_id=venue1.id,
        start_date=date(2026, 10, 1), end_date=date(2026, 10, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10.0, premium_price=10.0, regular_price=10.0,
        created_by=manager.id, status="UPCOMING", approval_status="APPROVED"
    )
    pending_event = Event(
        name="Pending Event", description="Desc", category_id=category.id, venue_id=venue1.id,
        start_date=date(2026, 10, 1), end_date=date(2026, 10, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10.0, premium_price=10.0, regular_price=10.0,
        created_by=manager.id, status="UPCOMING", approval_status="PENDING"
    )
    cancelled_event = Event(
        name="Cancelled Event", description="Desc", category_id=category.id, venue_id=venue1.id,
        start_date=date(2026, 10, 1), end_date=date(2026, 10, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10.0, premium_price=10.0, regular_price=10.0,
        created_by=manager.id, status="CANCELLED", approval_status="APPROVED"
    )
    db.session.add_all([approved_event, pending_event, cancelled_event])
    db.session.commit()

    cust1_token = create_access_token(identity=str(customer1.id), additional_claims={"role": "CUSTOMER"})
    cust2_token = create_access_token(identity=str(customer2.id), additional_claims={"role": "CUSTOMER"})

    return {
        "approved_event": approved_event, "pending_event": pending_event, "cancelled_event": cancelled_event,
        "seat_v1": seat_v1, "seat_v2": seat_v2, "seat_inactive": seat_inactive,
        "cust1_token": cust1_token, "cust2_token": cust2_token
    }

def test_booking_empty_seat_list(client, dup_setup):
    payload = {"event_id": dup_setup["approved_event"].id, "seat_ids": []}
    res = client.post("/api/bookings", json=payload, headers={"Authorization": f"Bearer {dup_setup['cust1_token']}"})
    assert res.status_code == 400
    assert "At least one seat is required" in res.json["message"]

def test_booking_duplicate_seats_in_same_request(client, dup_setup):
    payload = {"event_id": dup_setup["approved_event"].id, "seat_ids": [dup_setup["seat_v1"].id, dup_setup["seat_v1"].id]}
    res = client.post("/api/bookings", json=payload, headers={"Authorization": f"Bearer {dup_setup['cust1_token']}"})
    assert res.status_code == 400
    assert "A seat can only be selected once" in res.json["message"]

def test_booking_already_booked_seat(client, dup_setup):
    res1 = client.post("/api/bookings", json={"event_id": dup_setup["approved_event"].id, "seat_ids": [dup_setup["seat_v1"].id]}, headers={"Authorization": f"Bearer {dup_setup['cust1_token']}"})
    assert res1.status_code == 201

    res2 = client.post("/api/bookings", json={"event_id": dup_setup["approved_event"].id, "seat_ids": [dup_setup["seat_v1"].id]}, headers={"Authorization": f"Bearer {dup_setup['cust2_token']}"})
    assert res2.status_code == 400
    assert "already booked" in res2.json["message"]

def test_booking_pending_unapproved_event(client, dup_setup):
    payload = {"event_id": dup_setup["pending_event"].id, "seat_ids": [dup_setup["seat_v1"].id]}
    res = client.post("/api/bookings", json=payload, headers={"Authorization": f"Bearer {dup_setup['cust1_token']}"})
    assert res.status_code == 400
    assert "Event is not available for booking" in res.json["message"]

def test_booking_cancelled_event(client, dup_setup):
    payload = {"event_id": dup_setup["cancelled_event"].id, "seat_ids": [dup_setup["seat_v1"].id]}
    res = client.post("/api/bookings", json=payload, headers={"Authorization": f"Bearer {dup_setup['cust1_token']}"})
    assert res.status_code == 400
    assert "Event is not available for booking" in res.json["message"]

def test_booking_seat_from_wrong_venue(client, dup_setup):
    payload = {"event_id": dup_setup["approved_event"].id, "seat_ids": [dup_setup["seat_v2"].id]}
    res = client.post("/api/bookings", json=payload, headers={"Authorization": f"Bearer {dup_setup['cust1_token']}"})
    assert res.status_code == 400
    assert "does not belong to this event venue" in res.json["message"]

def test_booking_inactive_seat(client, dup_setup):
    payload = {"event_id": dup_setup["approved_event"].id, "seat_ids": [dup_setup["seat_inactive"].id]}
    res = client.post("/api/bookings", json=payload, headers={"Authorization": f"Bearer {dup_setup['cust1_token']}"})
    assert res.status_code == 400
    assert "is inactive" in res.json["message"]
