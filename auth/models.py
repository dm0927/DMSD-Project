from flask_login import UserMixin
import json
class User(UserMixin):
    def __init__(self, id, name, address, phone, email):
        self.id = id
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.authenticated = False
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated
    def is_active(self):
        return True
    def get_id(self):
        return self.id
    def __str__(self):
        return json.dumps(self.__dict__)