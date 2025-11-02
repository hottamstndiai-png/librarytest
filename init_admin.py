"""
初期管理者アカウント作成スクリプト
Usage: python init_admin.py
"""
import sys
import bcrypt
from app import app
from extensions import db
from models import User


def create_admin(username, password):
    """管理者アカウントを作成"""
    with app.app_context():
        # Check if database is initialized
        db.create_all()

        # Check if admin already exists
        existing_admin = User.query.filter_by(username=username).first()
        if existing_admin:
            print(f"Error: User '{username}' already exists.")
            return False

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create admin user
        admin = User(
            username=username,
            password_hash=password_hash,
            is_admin=True
        )

        try:
            db.session.add(admin)
            db.session.commit()
            print(f"Admin account created successfully!")
            print(f"Username: {username}")
            print(f"User ID: {admin.user_id}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin: {str(e)}")
            return False


if __name__ == '__main__':
    print("=== Library System Admin Account Creator ===\n")

    # Get admin credentials
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")

    if not username or not password:
        print("Error: Username and password are required.")
        sys.exit(1)

    success = create_admin(username, password)
    sys.exit(0 if success else 1)
