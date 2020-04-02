from directory import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash

class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer(), primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    password = Column(String(128), unique=False, nullable=False)

    # sqlalchemy.orm '@validates decorator' is a default decorator for apply validation on fields of tables, that's very useful :)
    @validates('password')
    def validates_password(self, key, value): # key => fieldname 
        if len(value)<6:
            raise ValueError("password should be atleast 6 characters.") # raise for return error (bad request)
        return generate_password_hash(value) # return by default set thit value to our field :)

    @validates('username')
    def validates_username(self, key, value):
        if not value.isidentifier():
            raise ValueError("username is invalid")
        return value