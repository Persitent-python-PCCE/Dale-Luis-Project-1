from models.venue import Venue

class VenueService:
    def __init__(self, venue_dao):
        self.venue_dao = venue_dao
        
    def get_all_venues(self):
        return self.venue_dao.get_all()
    
    def get_venue(self, id):
        venue = self.venue_dao.get_by_id(id)

        if venue is None:
            raise ValueError("Venue not found")

        return venue
    
    def search_venues(self, keyword):
        return self.venue_dao.search(keyword)

    def get_by_city(self, city):
        return self.venue_dao.get_by_city(city)
    
    def create_venue(self, data, admin_id):
        if not data.get("name"):
            raise ValueError("Venue name is required")

        for field in ("address", "city", "capacity"):
            if data.get(field) is None or data.get(field) == "":
                raise ValueError(f"{field} is required")

        venue = Venue(
            name=data["name"],
            address=data.get("address"),
            city=data["city"],
            state=data.get("state"),
            pincode=data.get("pincode"),
            capacity=data.get("capacity"),
            description=data.get("description"),
            created_by=admin_id
        )

        return self.venue_dao.save(venue)
    
    def update_venue(self, id, data):
        venue = self.get_venue(id)

        if "name" in data:
            venue.name = data["name"]

        if "address" in data:
            venue.address = data["address"]

        if "city" in data:
            venue.city = data["city"]

        if "state" in data:
            venue.state = data["state"]

        if "capacity" in data:
            venue.capacity = data["capacity"]

        if "pincode" in data:
            venue.pincode = data["pincode"]

        if "description" in data:
            venue.description = data["description"]

        return self.venue_dao.update(venue)
    
    def delete_venue(self, id):
        venue = self.get_venue(id)

        return self.venue_dao.delete(venue)
