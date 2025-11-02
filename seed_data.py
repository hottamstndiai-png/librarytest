"""
テスト用サンプルデータ投入スクリプト
Usage: python seed_data.py
"""
import bcrypt
from datetime import datetime, timedelta
from app import app
from extensions import db
from models import User, Book, BorrowRecord


def seed_database():
    """テストデータを投入"""
    with app.app_context():
        # Initialize database
        db.create_all()

        print("=== Seeding Database ===\n")

        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_admin=True
            )
            db.session.add(admin)
            print("Created admin user: admin / admin123")
        else:
            print("Admin user already exists")

        # Create sample users
        sample_users = [
            ('tanaka', 'password123', False),
            ('sato', 'password123', False),
            ('suzuki', 'password123', False)
        ]

        created_users = []
        for username, password, is_admin in sample_users:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                user = User(
                    username=username,
                    password_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    is_admin=is_admin
                )
                db.session.add(user)
                created_users.append(username)

        if created_users:
            print(f"Created users: {', '.join(created_users)}")
        else:
            print("Sample users already exist")

        # Create sample books
        sample_books = [
            ('Pythonプログラミング入門', '山田太郎'),
            ('Pythonプログラミング入門', '山田太郎'),  # Same title, different copy
            ('データベース設計の基礎', '佐藤花子'),
            ('Web開発実践ガイド', '鈴木一郎'),
            ('機械学習入門', '田中次郎'),
            ('アルゴリズムとデータ構造', '高橋三郎'),
        ]

        created_books = []
        for title, author in sample_books:
            book = Book(
                title=title,
                author=author,
                status='available'
            )
            db.session.add(book)
            created_books.append(title)

        if created_books:
            print(f"Created {len(created_books)} books")

        # Commit all changes
        try:
            db.session.commit()
            print("\nDatabase seeded successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"\nError seeding database: {str(e)}")
            return False

        # Display summary
        print("\n=== Database Summary ===")
        print(f"Total users: {User.query.count()}")
        print(f"Total books: {Book.query.count()}")
        print(f"Available books: {Book.query.filter_by(status='available').count()}")

        # Display user accounts
        print("\n=== User Accounts ===")
        users = User.query.all()
        for user in users:
            role = "Admin" if user.is_admin else "User"
            print(f"- {user.username} (ID: {user.user_id}, Role: {role})")

        # Display books
        print("\n=== Books ===")
        books = Book.query.all()
        for book in books:
            print(f"- [{book.book_id}] {book.title} by {book.author} ({book.status})")

        return True


if __name__ == '__main__':
    success = seed_database()
    exit(0 if success else 1)
