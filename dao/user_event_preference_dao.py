from models.user_event_preference import UserEventPreference
from config.database import db


class UserEventPreferenceDAO:

    def get_by_user(self, user_id):
        return UserEventPreference.query.filter_by(
            user_id=user_id
        ).all()

    def get_by_user_and_category(
        self,
        user_id,
        category_id
    ):
        return UserEventPreference.query.filter_by(
            user_id=user_id,
            category_id=category_id
        ).first()

    def save(self, preference):
        db.session.add(preference)
        db.session.commit()
        return preference

    def save_all(self, preferences):
        db.session.add_all(preferences)
        db.session.commit()
        return preferences

    def delete(self, preference):
        db.session.delete(preference)
        db.session.commit()

    def delete_all_for_user(self, user_id):

        UserEventPreference.query.filter_by(
            user_id=user_id
        ).delete()

        db.session.commit()