import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False

    # Business rules
    MAX_BOOKS_PER_USER = 3
    MAX_BOOKS_SAME_TITLE = 3
    LOAN_PERIOD_DAYS = 14
