import pytest
from models.user import User
from models.event_category import EventCategory
from models.venue import Venue
from models.event import Event
from config.database import db
from flask_jwt_extended import create_access_token
from datetime import date, time

@pytest.fixture
def event_setup(app):
    db.session.expire_on_commit = False
    admin = User(name="Admin", email="admin@test.com", pass_hash="hash", role="ADMIN")
    manager1 = User(name="Manager 1", email="m1@test.com", pass_hash="hash", role="EVENT_MANAGER")
    manager2 = User(name="Manager 2", email="m2@test.com", pass_hash="hash", role="EVENT_MANAGER")
    db.session.add_all([admin, manager1, manager2])
    db.session.commit()

    category = EventCategory(name="Concerts", description="Live music concerts")
    venue = Venue(name="Grand Arena", address="100 Main", city="Metropolis", capacity=1000, created_by=admin.id)
    db.session.add_all([category, venue])
    db.session.commit()

    mgr1_token = create_access_token(identity=str(manager1.id), additional_claims={"role": "EVENT_MANAGER"})
    mgr2_token = create_access_token(identity=str(manager2.id), additional_claims={"role": "EVENT_MANAGER"})
    admin_token = create_access_token(identity=str(admin.id), additional_claims={"role": "ADMIN"})

    return {
        "admin": admin, "manager1": manager1, "manager2": manager2,
        "category": category, "venue": venue,
        "mgr1_token": mgr1_token, "mgr2_token": mgr2_token, "admin_token": admin_token
    }

def test_create_event_success(client, event_setup):
    payload = {
        "name": "Summer Fest 2026",
        "category_id": event_setup["category"].id,
        "venue_id": event_setup["venue"].id,
        "start_date": "2026-08-01",
        "end_date": "2026-08-02",
        "start_time": "12:00",
        "end_time": "22:00",
        "description": "Annual summer music festival",
        "maximum_capacity": 800,
        "vip_price": 150.0,
        "premium_price": 100.0,
        "regular_price": 50.0
    }
    res = client.post(
        "/api/events",
        json=payload,
        headers={"Authorization": f"Bearer {event_setup['mgr1_token']}"}
    )
    assert res.status_code == 201
    assert "Event created successfully" in res.json["message"]
    assert res.json["event"]["name"] == "Summer Fest 2026"
    assert res.json["event"]["approval_status"] == "PENDING"

def test_create_event_missing_required_fields(client, event_setup):
    payload = {
        "name": "Incomplete Event",
        "category_id": event_setup["category"].id
    }
    res = client.post(
        "/api/events",
        json=payload,
        headers={"Authorization": f"Bearer {event_setup['mgr1_token']}"}
    )
    assert res.status_code == 400

def test_read_events(client, event_setup):
    event = Event(
        name="Approved Show", description="Desc", category_id=event_setup["category"].id, venue_id=event_setup["venue"].id,
        start_date=date(2026, 9, 1), end_date=date(2026, 9, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10, premium_price=10, regular_price=10,
        created_by=event_setup["manager1"].id, status="UPCOMING", approval_status="APPROVED"
    )
    db.session.add(event)
    db.session.commit()
    event_id = event.id

    # Read list
    res_list = client.get("/api/events")
    assert res_list.status_code == 200
    assert len(res_list.json["events"]) >= 1

    # Read single event by ID
    res_single = client.get(f"/api/events/{event_id}")
    assert res_single.status_code == 200
    assert res_single.json["event"]["name"] == "Approved Show"

def test_update_event_creator_vs_non_creator_vs_admin(client, event_setup):
    event = Event(
        name="Original Title", description="Desc", category_id=event_setup["category"].id, venue_id=event_setup["venue"].id,
        start_date=date(2026, 9, 1), end_date=date(2026, 9, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10, premium_price=10, regular_price=10,
        created_by=event_setup["manager1"].id, status="UPCOMING", approval_status="APPROVED"
    )
    db.session.add(event)
    db.session.commit()
    event_id = event.id

    # Manager 1 (creator) updates event -> Success
    res_creator = client.put(
        f"/api/events/{event_id}",
        json={"name": "Manager 1 Updated Title"},
        headers={"Authorization": f"Bearer {event_setup['mgr1_token']}"}
    )
    assert res_creator.status_code == 200
    assert res_creator.json["event"]["name"] == "Manager 1 Updated Title"

    # Manager 2 (non-creator) tries to update event -> Error
    res_non_creator = client.put(
        f"/api/events/{event_id}",
        json={"name": "Hacked Title"},
        headers={"Authorization": f"Bearer {event_setup['mgr2_token']}"}
    )
    assert res_non_creator.status_code == 400
    assert "You can only edit your own events" in res_non_creator.json["message"]

    # Admin updates event -> Success
    res_admin = client.put(
        f"/api/events/{event_id}",
        json={"name": "Admin Override Title"},
        headers={"Authorization": f"Bearer {event_setup['admin_token']}"}
    )
    assert res_admin.status_code == 200
    assert res_admin.json["event"]["name"] == "Admin Override Title"

def test_delete_event(client, event_setup):
    event = Event(
        name="Event to Delete", description="Desc", category_id=event_setup["category"].id, venue_id=event_setup["venue"].id,
        start_date=date(2026, 9, 1), end_date=date(2026, 9, 1), start_time=time(10, 0), end_time=time(12, 0),
        maximum_capacity=100, vip_price=10, premium_price=10, regular_price=10,
        created_by=event_setup["manager1"].id, status="UPCOMING", approval_status="APPROVED"
    )
    db.session.add(event)
    db.session.commit()
    event_id = event.id

    # Manager 2 cannot delete Manager 1's event
    res_fail = client.delete(
        f"/api/events/{event_id}",
        headers={"Authorization": f"Bearer {event_setup['mgr2_token']}"}
    )
    assert res_fail.status_code == 400

    # Manager 1 deletes own event
    res_success = client.delete(
        f"/api/events/{event_id}",
        headers={"Authorization": f"Bearer {event_setup['mgr1_token']}"}
    )
    assert res_success.status_code == 200
    assert res_success.json["message"] == "Event deleted successfully"
