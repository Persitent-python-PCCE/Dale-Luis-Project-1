from models.venue import Venue
from models.event import Event
from models.seat import Seat
from dao.event_dao import EventDAO
from config.database import db


class VenueDAO:

    def get_all(self):
        return Venue.query.filter_by(
            is_active=True
        ).all()

    def get_by_id(self, venue_id):
        return Venue.query.get(venue_id)

    def search(self, keyword):
        return Venue.query.filter(
            Venue.name.ilike(f"%{keyword}%")
        ).all()

    def get_by_city(self, city):
        return Venue.query.filter_by(
            city=city,
            is_active=True
        ).all()

    def save(self, venue):
        db.session.add(venue)
        db.session.commit()
        return venue

    def update(self, venue):
        db.session.commit()
        return venue

    def delete(self, venue):
        """Permanently delete a venue, all its events, and its seats."""
        try:
            events = Event.query.filter_by(venue_id=venue.id).all()
            event_dao = EventDAO()
            for event in events:
                event_dao.delete(event)

            db.session.query(Seat).filter(Seat.venue_id == venue.id).delete(
                synchronize_session=False
            )
            db.session.delete(venue)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
