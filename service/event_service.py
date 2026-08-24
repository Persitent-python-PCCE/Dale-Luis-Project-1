from models.event import Event
from models.booking import Booking
from models.notification import Notification
from config.database import db
from datetime import datetime, date, time
from utils.file_upload import delete_poster

class EventService:
    
    def __init__(self,event_dao,category_dao,venue_dao):
        self.event_dao = event_dao
        self.category_dao = category_dao
        self.venue_dao = venue_dao
        
    def get_all_events(self):
        return self.event_dao.get_approved_events()

    def get_event(self, id):
        event = self.event_dao.get_by_id(id)

        if event is None:
            raise ValueError("Event not found")

        return event
    
    def get_manager_events(self, manager_id):
        return self.event_dao.get_by_creator(manager_id)
    
    def search_events(self, name):
        return self.event_dao.search_by_name(name)

    def filter_events(self, search=None, category_id=None, event_date=None):
        return self.event_dao.filter_approved_events(search, category_id, event_date)
    
    def get_events_by_category(self,category_id):
        return self.event_dao.get_by_category(category_id)
    
    def get_events_by_venue(self, venue_id):
        return self.event_dao.get_by_venue(venue_id)
    
    def get_events_by_status(self, status):
        return self.event_dao.get_by_status(status)
    
    def create_event(self, data, manager_id):
        required = [
            "name",
            "category_id",
            "venue_id",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "description",
            "maximum_capacity",
            "vip_price",
            "premium_price",
            "regular_price",
        ]

        for field in required:
            if not data.get(field):
                raise ValueError(f"{field} is required")

        category = self.category_dao.get_by_id(data["category_id"])
        if category is None:
            raise ValueError("Category not found")

        venue = self.venue_dao.get_by_id(data["venue_id"])
        if venue is None:
            raise ValueError("Venue not found")

        start_date = data["start_date"]
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)

        end_date = data["end_date"]
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)

        start_time = data["start_time"]
        if isinstance(start_time, str):
            start_time = time.fromisoformat(start_time)

        end_time = data["end_time"]
        if isinstance(end_time, str):
            end_time = time.fromisoformat(end_time)

        is_18_plus = data.get("is_18_plus", False)
        if isinstance(is_18_plus, str):
            is_18_plus = is_18_plus.lower() in ("true", "1", "yes", "on")
        else:
            is_18_plus = bool(is_18_plus)

        event = Event(
            name=data["name"],
            description=data.get("description"),
            poster_path=data.get("poster_path"),
            category_id=data["category_id"],
            venue_id=data["venue_id"],
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            maximum_capacity=data["maximum_capacity"],
            vip_price=data["vip_price"],
            premium_price=data["premium_price"],
            regular_price=data["regular_price"],
            is_18_plus=is_18_plus,
            created_by=manager_id,
            status="UPCOMING",
            approval_status="PENDING"
        )

        return self.event_dao.save(event)
    
    def update_event(self, id, data, manager_id, is_admin=False):
        event = self.get_event(id)

        if event.created_by != manager_id and not is_admin:
            raise ValueError("You can only edit your own events")

        if "name" in data:
            event.name = data["name"]

        if "description" in data:
            event.description = data["description"]

        if "poster_path" in data and data["poster_path"] != event.poster_path:
            if event.poster_path:
                delete_poster(event.poster_path)
            event.poster_path = data["poster_path"]

        if "is_18_plus" in data:
            val = data["is_18_plus"]
            if isinstance(val, str):
                event.is_18_plus = val.lower() in ("true", "1", "yes", "on")
            else:
                event.is_18_plus = bool(val)

        if "category_id" in data:
            event.category_id = data["category_id"]

        if "venue_id" in data:
            event.venue_id = data["venue_id"]

        if "maximum_capacity" in data:
            event.maximum_capacity = data["maximum_capacity"]

        if "vip_price" in data:
            event.vip_price = data["vip_price"]

        if "premium_price" in data:
            event.premium_price = data["premium_price"]

        if "regular_price" in data:
            event.regular_price = data["regular_price"]

        if "start_date" in data:
            val = data["start_date"]
            event.start_date = date.fromisoformat(val) if isinstance(val, str) else val

        if "end_date" in data:
            val = data["end_date"]
            event.end_date = date.fromisoformat(val) if isinstance(val, str) else val

        if "start_time" in data:
            val = data["start_time"]
            event.start_time = time.fromisoformat(val) if isinstance(val, str) else val

        if "end_time" in data:
            val = data["end_time"]
            event.end_time = time.fromisoformat(val) if isinstance(val, str) else val

        event_was_cancelled = event.status == "CANCELLED"

        if "status" in data:
            status = data["status"]
            if status not in {"UPCOMING", "COMPLETED", "CANCELLED"}:
                raise ValueError("Invalid event status")
            event.status = status

        if event.status == "CANCELLED" and not event_was_cancelled:
            self._cancel_bookings_and_notify_customers(event)

        return self.event_dao.update(event)

    @staticmethod
    def _cancel_bookings_and_notify_customers(event):
        """Cancel confirmed bookings and initiate their mock-payment refunds."""
        confirmed_bookings = Booking.query.filter_by(
            event_id=event.id,
            status="CONFIRMED",
        ).all()

        for booking in confirmed_bookings:
            booking.status = "CANCELLED"
            booking.cancelled_at = datetime.utcnow()
            booking.cancellation_reason = "Event cancelled by the event manager"

            payment = booking.payment
            if payment and payment.status == "SUCCESS":
                payment.refund_status = "COMPLETED"
                payment.refund_amount = payment.amount
                payment.refunded_at = datetime.utcnow()

            db.session.add(Notification(
                user_id=booking.user_id,
                booking_id=booking.id,
                event_id=event.id,
                message=(
                    f"{event.name} has been cancelled. Your ticket payment "
                    "will be refunded."
                ),
            ))
    
    def delete_event(self, id, manager_id, is_admin=False):
        event = self.get_event(id)

        if event.created_by != manager_id and not is_admin:
            raise ValueError(
                "You can only delete your own events"
            )

        if event.poster_path:
            delete_poster(event.poster_path)

        return self.event_dao.delete(event)
    
    def get_pending_events(self):
        return self.event_dao.get_pending_events()
    
    def approve_event(self,id,admin_id):
        event = self.get_event(id)

        if event.approval_status != "PENDING":
            raise ValueError("Event is not pending approval")
            
        return self.event_dao.approve(event,admin_id)

    def reject_event(self,id,admin_id,reason):
        event = self.get_event(id)

        if event.approval_status != "PENDING":
            raise ValueError("Event is not pending approval")

        return self.event_dao.reject(event,admin_id,reason)
