from models.event_category import EventCategory
from config.database import db


class EventCategoryDAO:

    def get_all(self):
        return EventCategory.query.filter_by(
            is_active=True
        ).all()

    def get_by_id(self, category_id):
        return EventCategory.query.get(category_id)

    def get_by_name(self, name):
        return EventCategory.query.filter_by(
            name=name
        ).first()

    def save(self, category):
        db.session.add(category)
        db.session.commit()
        return category

    def update(self, category):
        db.session.commit()
        return category

    def delete(self, category):
        category.is_active = False
        db.session.commit()
        return category