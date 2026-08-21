from models.event_category import EventCategory

class EventCategoryService:
    
    def __init__(self, category_dao):
        self.category_dao = category_dao
        
    def get_all_categories(self):
        return self.category_dao.get_all()
    
    def get_category(self, id):
        category = self.category_dao.get_by_id(id)
        
        if category is None:
            raise ValueError("Category not found")
        
        return category
    
    def get_by_name(self, name):
        return self.category_dao.get_by_name(name)
    
    def create_category(self, data):
        name = data.get("name")

        if not name:
            raise ValueError("Category name is required")

        existing = self.category_dao.get_by_name(name)

        if existing:
            raise ValueError("Category already exists")

        category = EventCategory(name=name,description=data.get("description"))

        return self.category_dao.save(category)
    
    def update_category(self, id, data):

        category = self.get_category(id)

        if "name" in data:
            category.name = data["name"]

        if "description" in data:
            category.description = data["description"]

        return self.category_dao.update(category)
    
    def delete_category(self,id):

        category = self.get_category(id)

        return self.category_dao.delete(category)