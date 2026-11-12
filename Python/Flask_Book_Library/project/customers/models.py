from project import db, app
import re
from sqlalchemy.orm import validates

# Customer model
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    city = db.Column(db.String(64))
    age = db.Column(db.Integer)

    @validates('name', 'city')
    def validate_xss(self, key, value):
        if not value:
            return value
        xss_pattern = re.compile(r'<[^>]*>|javascript:|onerror=|onload=|onmouseover=', re.IGNORECASE)
        if xss_pattern.search(str(value)):
            raise ValueError(f"Wykryto niedozwolone znaki HTML/JS w polu: {key}")
        return str(value).strip()

    def __init__(self, name, city, age):
        self.name = name
        self.city = city
        self.age = age

    def __repr__(self):
        return f"Customer(ID: {self.id}, Name: {self.name}, City: {self.city}, Age: {self.age})"


with app.app_context():
    db.create_all()
