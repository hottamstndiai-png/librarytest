"""Flask extensions initialization"""
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

# Initialize extensions
db = SQLAlchemy()
sess = Session()
