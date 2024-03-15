# models.py
import uuid
from datetime import datetime
from flask_login import UserMixin
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import secrets

# set the variables for class instantiation
login_manager = LoginManager()
ma = Marshmallow()
db = SQLAlchemy()

# Function that Flask-Login will use to load the current user.
# It takes in the user ID and returns the corresponding User object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# define the database schema for the 'users' table.
class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    g_auth_verify = db.Column(db.Boolean, default=False)
    token = db.Column(db.String, default='', unique=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    google_id = db.Column(db.String(225), nullable=True)
    name = db.Column(db.String(225), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    def __init__(self, email, g_auth_verify=False):
        self.id = self.set_id()
        self.email = email
        self.token = self.set_token(24)
        self.g_auth_verify = g_auth_verify

    def set_token(self, length):
        return str(uuid.uuid4())
    
    def set_id(self):
        return str(uuid.uuid4())
    
    def __repr__(self):
        return f'User {self.email} has been added to the database'