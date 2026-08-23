from models.user import User
from config.database import db
from models.booking import Booking
from models.booking_item import BookingItem
from models.coupon import Coupon
from models.event import Event
from models.payment import Payment
from models.review import Review
from models.user_document import UserDocument
from models.user_event_preference import UserEventPreference
from models.venue import Venue
from dao.event_dao import EventDAO
from dao.venue_dao import VenueDAO


class UserDAO:

    def get_all(self):
        return User.query.all()

    def get_by_id(self, user_id):
        return User.query.get(user_id)

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_by_role(self, role):
        return User.query.filter_by(role=role).all()

    def search(self, keyword):
        return User.query.filter(
            User.name.ilike(f"%{keyword}%")
        ).all()

    def save(self, user):
        db.session.add(user)
        db.session.commit()
        return user

    def update(self, user):
        db.session.commit()
        return user

    def delete(self, user):
        """Permanently delete a user and all data that references the user."""
        try:
            # Delete events and venues first; their DAOs also remove ticket data.
            for event in Event.query.filter_by(created_by=user.id).all():
                EventDAO().delete(event)
            for venue in Venue.query.filter_by(created_by=user.id).all():
                VenueDAO().delete(venue)

            booking_ids = [
                booking_id for (booking_id,) in db.session.query(Booking.id)
                .filter(Booking.user_id == user.id).all()
            ]
            if booking_ids:
                db.session.query(Review).filter(Review.booking_id.in_(booking_ids)).delete(
                    synchronize_session=False
                )
                db.session.query(Payment).filter(Payment.booking_id.in_(booking_ids)).delete(
                    synchronize_session=False
                )
                db.session.query(BookingItem).filter(BookingItem.booking_id.in_(booking_ids)).delete(
                    synchronize_session=False
                )
                db.session.query(Booking).filter(Booking.id.in_(booking_ids)).delete(
                    synchronize_session=False
                )

            # Coupons and approvals made by this user must no longer reference it.
            coupon_ids = [
                coupon_id for (coupon_id,) in db.session.query(Coupon.id)
                .filter(Coupon.created_by == user.id).all()
            ]
            if coupon_ids:
                db.session.query(Booking).filter(Booking.coupon_id.in_(coupon_ids)).update(
                    {Booking.coupon_id: None}, synchronize_session=False
                )
                db.session.query(Coupon).filter(Coupon.id.in_(coupon_ids)).delete(
                    synchronize_session=False
                )
            db.session.query(Event).filter(Event.approved_by == user.id).update(
                {Event.approved_by: None}, synchronize_session=False
            )
            db.session.query(UserDocument).filter(UserDocument.verified_by == user.id).update(
                {UserDocument.verified_by: None}, synchronize_session=False
            )

            db.session.query(Review).filter(Review.user_id == user.id).delete(
                synchronize_session=False
            )
            db.session.query(UserDocument).filter(UserDocument.user_id == user.id).delete(
                synchronize_session=False
            )
            db.session.query(UserEventPreference).filter(UserEventPreference.user_id == user.id).delete(
                synchronize_session=False
            )
            db.session.delete(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def deactivate(self, user):
        user.is_active = False
        db.session.commit()
        return user
