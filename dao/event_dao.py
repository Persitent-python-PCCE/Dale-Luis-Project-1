from models.event import Event
from config.database import db
from datetime import datetime


class EventDAO:

    def get_all(self):
        return Event.query.all()

    def get_by_id(self, event_id):
        return Event.query.get(event_id)

    def get_approved_events(self):
        return Event.query.filter_by(
            approval_status="APPROVED"
        ).all()

    def get_by_creator(self, user_id):
        return Event.query.filter_by(
            created_by=user_id
        ).all()

    def get_by_category(self, category_id):
        return Event.query.filter_by(
            category_id=category_id,
            approval_status="APPROVED"
        ).all()

    def get_by_venue(self, venue_id):
        return Event.query.filter_by(
            venue_id=venue_id
        ).all()

    def search_by_name(self, name):
        return Event.query.filter(
            Event.name.ilike(f"%{name}%"),
            Event.approval_status == "APPROVED"
        ).all()

    def get_pending_events(self):
        return Event.query.filter_by(
            approval_status="PENDING"
        ).all()

    def get_by_status(self, status):
        return Event.query.filter_by(
            status=status,
            approval_status="APPROVED"
        ).all()

    def save(self, event):
        db.session.add(event)
        db.session.commit()
        return event

    def update(self, event):
        db.session.commit()
        return event

    def delete(self, event):
        db.session.delete(event)
        db.session.commit()

    def approve(self, event, admin_id):
        event.approval_status = "APPROVED"
        event.approved_by = admin_id
        event.approved_at = datetime.utcnow()

        db.session.commit()

        return event

    def reject(self, event, admin_id, reason):
        event.approval_status = "REJECTED"
        event.approved_by = admin_id
        event.approved_at = datetime.utcnow()
        event.rejection_reason = reason

        db.session.commit()

        return event
