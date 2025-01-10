from project import database
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
import flask_login

class Product(database.Model):

    __tablename__ = 'products'

    id = mapped_column(Integer(), primary_key=True)
    name = mapped_column(String(100))
    price = mapped_column(Float)

    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price
       

    def __repr__(self):
        return f'{self.name} - {self.price}.'
    
class User(flask_login.UserMixin, database.Model):

    __tablename__ = 'users'

    id = mapped_column(Integer(), primary_key=True)
    email = mapped_column(String(), unique=True)
    password_hashed = mapped_column(String(256))

    def __init__(self, email: str, password_plaintext: str):
        self.email = email
        self.password_hashed = self._generate_password_hash(password_plaintext)

    def is_password_correct(self, passsword_plaintext: str):
        return check_password_hash(self.password_hashed, passsword_plaintext)
    
    @staticmethod
    def _generate_password_hash(password_plaintext):
        return generate_password_hash(password_plaintext)
    
    def __repr__(self):
        return f'<User: {self.email}>'