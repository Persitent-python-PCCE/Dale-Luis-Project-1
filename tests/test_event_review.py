import pytest
from datetime import date, time
from models.user import User
from models.event_category import EventCategory
from models.venue import Venue
from models.seat import Seat
from models.event import Event
from models.review import Review
from config.database import db
from flask_jwt_extended import create_access_token


@pytest.fixture
def review_setup(app):
    admin = User(name="Admin User", email="admin_rev@test.com", pass_hash="hash", role="ADMIN")
    manager = User(name="Manager User", email="mgr_rev@test.com", pass_hash="hash", role="EVENT_MANAGER")
    customer = User(name="Reviewer Customer", email="reviewer@test.com", pass_hash="hash", role="CUSTOMER")
    other_customer = User(name="Other Customer", email="other_rev@test.com", pass_hash="hash", role="CUSTOMER")
    db.session.add_all([admin, manager, customer, other_customer])
    db.session.commit()

    venue = Venue(name="Review Hall", address="200 St", city="City", capacity=200, created_by=admin.id)
    category = EventCategory(name="Tech", description="Tech events")
    db.session.add_all([venue, category])
    db.session.commit()

    seat = Seat(venue_id=venue.id, seat_number="B1", row_name="B", category="REGULAR", base_price=50.0, is_active=True)
    db.session.add(seat)
    db.session.commit()

    event = Event(
        name="Tech Conference 2026", description="Annual Tech Conference", category_id=category.id, venue_id=venue.id,
        start_date=date(2026, 11, 1), end_date=date(2026, 11, 1), start_time=time(9, 0), end_time=time(17, 0),
        maximum_capacity=200, vip_price=150.0, premium_price=100.0, regular_price=50.0,
        created_by=manager.id, status="UPCOMING", approval_status="APPROVED"
    )
    db.session.add(event)
    db.session.commit()

    cust_token = create_access_token(identity=str(customer.id), additional_claims={"role": "CUSTOMER"})
    other_cust_token = create_access_token(identity=str(other_customer.id), additional_claims={"role": "CUSTOMER"})

    return {
        "customer": customer,
        "other_customer": other_customer,
        "event": event,
        "seat": seat,
        "cust_token": cust_token,
        "other_cust_token": other_cust_token
    }


def _create_confirmed_booking(client, event_id, seat_id, token):
    res_b = client.post(
        "/api/bookings",
        json={"event_id": event_id, "seat_ids": [seat_id]},
        headers={"Authorization": f"Bearer {token}"}
    )
    booking_id = res_b.json["booking"]["id"]
    client.post(
        "/api/payments",
        json={"booking_id": booking_id, "payment_method": "CARD", "result": "SUCCESS"},
        headers={"Authorization": f"Bearer {token}"}
    )
    return booking_id


def test_customer_add_review_api_success(client, review_setup):
    booking_id = _create_confirmed_booking(
        client, review_setup["event"].id, review_setup["seat"].id, review_setup["cust_token"]
    )

    review_payload = {
        "rating": 5,
        "comment": "Amazing tech conference!"
    }
    res = client.post(
        f"/api/events/{review_setup['event'].id}/reviews",
        json=review_payload,
        headers={"Authorization": f"Bearer {review_setup['cust_token']}"}
    )

    assert res.status_code == 201
    data = res.json
    assert data["message"] == "Review added"
    assert data["review"]["rating"] == 5
    assert data["review"]["review_text"] == "Amazing tech conference!"

    # Verify review saved in database table
    db_review = Review.query.filter_by(
        user_id=review_setup["customer"].id,
        event_id=review_setup["event"].id
    ).first()
    assert db_review is not None
    assert db_review.rating == 5
    assert db_review.review_text == "Amazing tech conference!"
    assert db_review.comment == "Amazing tech conference!"
    assert db_review.booking_id == booking_id


def test_customer_add_review_web_success(client, review_setup):
    booking_id = _create_confirmed_booking(
        client, review_setup["event"].id, review_setup["seat"].id, review_setup["cust_token"]
    )

    client.set_cookie("access_token_cookie", review_setup["cust_token"])
    res = client.post(
        f"/events/{review_setup['event'].id}/reviews/add",
        data={"rating": "4", "comment": "Great content and speakers"},
        headers={"Authorization": f"Bearer {review_setup['cust_token']}"}
    )

    assert res.status_code == 302
    assert f"/events/{review_setup['event'].id}" in res.location

    db_review = Review.query.filter_by(
        user_id=review_setup["customer"].id,
        event_id=review_setup["event"].id
    ).first()
    assert db_review is not None
    assert db_review.rating == 4
    assert db_review.review_text == "Great content and speakers"


def test_add_review_without_confirmed_booking_fails(client, review_setup):
    # Customer has no booking for the event
    review_payload = {
        "rating": 5,
        "comment": "Trying to review without booking"
    }
    res = client.post(
        f"/api/events/{review_setup['event'].id}/reviews",
        json=review_payload,
        headers={"Authorization": f"Bearer {review_setup['other_cust_token']}"}
    )

    assert res.status_code == 400
    assert "You can only review an event you have attended" in res.json["message"]

    db_review = Review.query.filter_by(
        user_id=review_setup["other_customer"].id,
        event_id=review_setup["event"].id
    ).first()
    assert db_review is None


def test_add_duplicate_review_fails(client, review_setup):
    _create_confirmed_booking(
        client, review_setup["event"].id, review_setup["seat"].id, review_setup["cust_token"]
    )

    review_payload = {"rating": 5, "comment": "First review"}
    res1 = client.post(
        f"/api/events/{review_setup['event'].id}/reviews",
        json=review_payload,
        headers={"Authorization": f"Bearer {review_setup['cust_token']}"}
    )
    assert res1.status_code == 201

    # Attempt second review
    res2 = client.post(
        f"/api/events/{review_setup['event'].id}/reviews",
        json={"rating": 4, "comment": "Second review attempt"},
        headers={"Authorization": f"Bearer {review_setup['cust_token']}"}
    )
    assert res2.status_code == 400
    assert "You have already reviewed this event" in res2.json["message"]


def test_add_review_invalid_rating_fails(client, review_setup):
    _create_confirmed_booking(
        client, review_setup["event"].id, review_setup["seat"].id, review_setup["cust_token"]
    )

    res = client.post(
        f"/api/events/{review_setup['event'].id}/reviews",
        json={"rating": 6, "comment": "Invalid rating"},
        headers={"Authorization": f"Bearer {review_setup['cust_token']}"}
    )
    assert res.status_code == 400
    assert "Rating must be between 1 and 5" in res.json["message"]
