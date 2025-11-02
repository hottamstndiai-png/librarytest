from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrow_records = db.relationship('BorrowRecord', back_populates='user', lazy=True)

    def to_dict(self, include_sensitive=False):
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data


class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='available', nullable=False)  # 'available' or 'borrowed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrow_records = db.relationship('BorrowRecord', back_populates='book', lazy=True)

    def to_dict(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BorrowRecord(db.Model):
    __tablename__ = 'borrow_records'

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', back_populates='borrow_records')
    book = db.relationship('Book', back_populates='borrow_records')

    def to_dict(self):
        return {
            'record_id': self.record_id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'is_overdue': self.is_overdue()
        }

    def is_overdue(self):
        if self.return_date:
            return False
        return datetime.utcnow() > self.due_date
