from models.user import User
import bcrypt
from utils.validators import validate_email, validate_phone

class UserService:
    def __init__(self, user_dao):
        self.user_dao = user_dao
    
    def get_all_users(self):
        return self.user_dao.get_all()
    
    def register(self,data):
        name= data.get("name")
        email= data.get("email")
        password = data.get("password")
        phone = data.get("phone")
        role = data.get("role")
        
        if not name or not email or not password:
            raise ValueError("Name, email, password are required")
        
        email = validate_email(email)
        phone = validate_phone(phone)
        
        allowed_roles = ["CUSTOMER", "EVENT_MANAGER"]
        
        if role not in allowed_roles:
            raise ValueError("Invalid Role")
        
        exisnting_user = self.user_dao.get_by_email(email)
        
        if exisnting_user:
            raise ValueError("Email already registered")
        
        pass_bytes = password.encode("utf-8")
        
        sal = bcrypt.gensalt()
        
        pass_hash = bcrypt.hashpw(pass_bytes, sal)
        
        pass_hash = pass_hash.decode("utf-8")
        
        user = User(
            name=name,
            email=email,
            pass_hash=pass_hash,
            phone=phone,
            role=role
        )
        
        return self.user_dao.save(user)
    
    def login(self,email,password):
        user = self.user_dao.get_by_email(email)
        
        if user is None:
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        stored_hash = user.pass_hash.encode("utf-8")
        pass_bytes = password.encode("utf-8")
        
        if not bcrypt.checkpw(pass_bytes, stored_hash):
            raise ValueError("Invalid email or password")
        
        return user
    
    def get_user(self,id):
        user = self.user_dao.get_by_id(id)
        
        if user is None:
            raise ValueError("User not found")
        
        return user
    
    def get_by_email(self,email):
        return self.user_dao.get_by_email(email)
    
    def search_users(self,keyword):
        return self.user_dao.search(keyword)
    
    def get_user_by_role(self,role):
        allowed_roles = ["CUSTOMER","ADMIN","EVENT_MANAGER"]

        if role not in allowed_roles:
            raise ValueError("Invalid role")

        return self.user_dao.get_by_role(role)
    
    def change_role(self,id,new_role):
        user = self.get_user(id)
        
        allowed_roles = ["CUSTOMER", "EVENT_MANAGER", "ADMIN"]
        
        if new_role not in allowed_roles:
            raise ValueError("Invalid Role")

        user.role= new_role
        
        return self.user_dao.update(user)
    
    
    def deactivate_user(self,id):
        user = self.get_user(id)
        
        return self.user_dao.deactivate(user)
    
    def activate_user(self,id):
        user = self.get_user(id)
        
        if user.is_active:
            raise ValueError("User is already active")
        
        user.is_active = True
        
        return self.user_dao.update(user)
    
    def delete_user(self,id):
        user = self.get_user(id)
        
        self.user_dao.delete(user)

    def update_user_profile(self, id, data):
        user = self.get_user(id)

        if "name" in data and data["name"]:
            user.name = data["name"].strip()

        if "phone" in data:
            user.phone = validate_phone(data["phone"])

        if "email" in data and data["email"]:
            new_email = validate_email(data["email"])
            if new_email != user.email:
                existing = self.user_dao.get_by_email(new_email)
                if existing and existing.id != user.id:
                    raise ValueError("Email is already in use by another account")
                user.email = new_email

        if "password" in data and data["password"]:
            pass_bytes = data["password"].encode("utf-8")
            sal = bcrypt.gensalt()
            pass_hash = bcrypt.hashpw(pass_bytes, sal).decode("utf-8")
            user.pass_hash = pass_hash

        return self.user_dao.update(user)

    def update_user(self, id, data):
        return self.update_user_profile(id, data)
