from models.event import Event
from models.booking import Booking
from models.booking_item import BookingItem
from models.payment import Payment
from models.review import Review
from config.database import db
from datetime import datetime


class EventDAO:

    def get_all(self):
        return Event.query.all()

    def get_by_id(self, event_id):
        return Event.query.get(event_id)

    def get_approved_events(self):
        return Event.query.filter_by(
            approval_status="APPROVED",
            status="UPCOMING",
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

    def filter_approved_events(self, search=None, category_id=None, event_date=None):
        query = Event.query.filter_by(approval_status="APPROVED", status="UPCOMING")

        if search:
            query = query.filter(Event.name.ilike(f"%{search}%"))
        if category_id:
            query = query.filter(Event.category_id == category_id)
        if event_date:
            query = query.filter(Event.start_date == event_date)

        return query.order_by(Event.start_date, Event.start_time).all()

    def get_pending_events(self):
        return Event.query.filter_by(
            approval_status="PENDING",
            status="UPCOMING",
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
        try:
            booking_ids = [
                booking_id for (booking_id,) in db.session.query(Booking.id)
                .filter(Booking.event_id == event.id)
                .all()
            ]

            db.session.query(Review).filter(Review.event_id == event.id).delete(
                synchronize_session=False
            )
            if booking_ids:
                db.session.query(Payment).filter(Payment.booking_id.in_(booking_ids)).delete(
                    synchronize_session=False
                )
                db.session.query(BookingItem).filter(
                    BookingItem.booking_id.in_(booking_ids)
                ).delete(synchronize_session=False)
            db.session.query(BookingItem).filter(BookingItem.event_id == event.id).delete(
                synchronize_session=False
            )
            db.session.query(Booking).filter(Booking.event_id == event.id).delete(
                synchronize_session=False
            )
            db.session.delete(event)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

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
