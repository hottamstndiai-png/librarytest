from flask import Blueprint, request, jsonify, session
import bcrypt
from extensions import db
from models import User

bp = Blueprint('auth', __name__, url_prefix='/api')


@bp.route('/register', methods=['POST'])
def register():
    """ユーザー自己登録"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    username = data['username']
    password = data['password']

    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409

    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create new user
    new_user = User(
        username=username,
        password_hash=password_hash,
        is_admin=False  # Regular users cannot self-register as admin
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": "User registered successfully",
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@bp.route('/login', methods=['POST'])
def login():
    """ログイン"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    username = data['username']
    password = data['password']

    # Find user
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({"error": "Invalid username or password"}), 401

    # Set session
    session['user_id'] = user.user_id
    session['username'] = user.username
    session['is_admin'] = user.is_admin

    return jsonify({
        "message": "Login successful",
        "user": user.to_dict()
    }), 200


@bp.route('/logout', methods=['POST'])
def logout():
    """ログアウト"""
    session.clear()
    return jsonify({"message": "Logout successful"}), 200


@bp.route('/me', methods=['GET'])
def get_current_user():
    """現在ログインしているユーザー情報を取得"""
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200


# Helper function for authentication check
def require_login():
    """Check if user is logged in"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])


def require_admin():
    """Check if user is admin"""
    user = require_login()
    if not user:
        return None
    if not user.is_admin:
        return None
    return user
