from models.review import Review
from config.database import db


class ReviewDAO:

    def get_all(self):
        return Review.query.all()

    def get_by_id(self, review_id):
        return Review.query.get(review_id)

    def get_by_event(self, event_id):
        return Review.query.filter_by(
            event_id=event_id
        ).all()

    def get_by_user(self, user_id):
        return Review.query.filter_by(
            user_id=user_id
        ).all()

    def get_user_event_review(self, user_id, event_id):
        return Review.query.filter_by(
            user_id=user_id,
            event_id=event_id
        ).first()

    def save(self, review):
        db.session.add(review)
        db.session.commit()
        return review

    def update(self, review):
        db.session.commit()
        return review

    def delete(self, review):
        db.session.delete(review)
        db.session.commit()