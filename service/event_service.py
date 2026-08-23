from models.event import Event

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

        event = Event(
            name=data["name"],
            description=data.get("description"),
            poster_path=data.get("poster_path"),
            category_id=data["category_id"],
            venue_id=data["venue_id"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            maximum_capacity=data["maximum_capacity"],
            vip_price=data["vip_price"],
            premium_price=data["premium_price"],
            regular_price=data["regular_price"],
            created_by=manager_id,
            status="UPCOMING",
            approval_status="PENDING"
        )

        return self.event_dao.save(event)
    
    def update_event(self,id,data,manager_id):
        event = self.get_event(id)

        if event.created_by != manager_id:
            raise ValueError("You can only edit your own events")

        if "name" in data:
            event.name = data["name"]

        if "description" in data:
            event.description = data["description"]

        if "poster_path" in data:
            event.poster_path = data["poster_path"]

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
            event.start_date = data["start_date"]

        if "end_date" in data:
            event.end_date = data["end_date"]

        if "start_time" in data:
            event.start_time = data["start_time"]

        if "end_time" in data:
            event.end_time = data["end_time"]

        event.approval_status = "PENDING"

        return self.event_dao.update(event)
    
    def delete_event(self, id, manager_id, is_admin=False):
        event = self.get_event(id)

        if event.created_by != manager_id and not is_admin:
            raise ValueError(
                "You can only delete your own events"
            )

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
