from models.venue import Venue
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
        venue.is_active = False
        db.session.commit()
        return venue 