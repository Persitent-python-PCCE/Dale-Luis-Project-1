from models.user_event_preference import UserEventPreference

class UserEventPreferenceService:
    def __init__(self, preference_dao):
        self.preference_dao = preference_dao

    def get_user_preferences(self, user_id):
        return self.preference_dao.get_by_user(user_id)

    def save_preferences(self,user_id,category_ids):
        if not category_ids:
            raise ValueError("Select at least one category")

        self.preference_dao.delete_all_for_user(user_id)

        preferences = []

        for category_id in category_ids:
            preference = UserEventPreference(user_id=user_id,category_id=category_id)

            preferences.append(preference)

        return self.preference_dao.save_all(preferences)

    def add_preference(self,user_id,category_id):
        existing = self.preference_dao.get_by_user_and_category(user_id,category_id)

        if existing:
            raise ValueError("Preference already exists")

        preference = UserEventPreference(user_id=user_id,category_id=category_id)

        return self.preference_dao.save(preference)

    def remove_preference(self,user_id,category_id):
        preference = self.preference_dao.get_by_user_and_category(user_id,category_id)

        if preference is None:
            raise ValueError("Preference not found")

        self.preference_dao.delete(preference)