from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Book
from routes.auth import require_admin, require_login
from config import Config

bp = Blueprint('books', __name__, url_prefix='/api')


@bp.route('/books', methods=['POST'])
def add_book():
    """本の登録 (管理者のみ)"""
    admin = require_admin()
    if not admin:
        return jsonify({"error": "Admin authentication required"}), 403

    data = request.get_json()

    if not data or not data.get('title') or not data.get('author'):
        return jsonify({"error": "Title and author are required"}), 400

    title = data['title']
    author = data['author']

    # Check how many copies of this title already exist
    existing_count = Book.query.filter_by(title=title).count()
    if existing_count >= Config.MAX_BOOKS_SAME_TITLE:
        return jsonify({
            "error": f"Maximum {Config.MAX_BOOKS_SAME_TITLE} copies of the same title allowed"
        }), 400

    # Create new book
    new_book = Book(
        title=title,
        author=author,
        status='available'
    )

    try:
        db.session.add(new_book)
        db.session.commit()
        return jsonify({
            "message": "Book added successfully",
            "book": new_book.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add book: {str(e)}"}), 500


@bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """本の削除 (管理者のみ)"""
    admin = require_admin()
    if not admin:
        return jsonify({"error": "Admin authentication required"}), 403

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Check if book is currently borrowed
    if book.status == 'borrowed':
        return jsonify({"error": "Cannot delete a book that is currently borrowed"}), 400

    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete book: {str(e)}"}), 500


@bp.route('/books', methods=['GET'])
def list_books():
    """本の一覧取得 (全ユーザー)"""
    user = require_login()
    if not user:
        return jsonify({"error": "Login required"}), 401

    # Get query parameters for filtering
    status = request.args.get('status')  # 'available' or 'borrowed'
    title = request.args.get('title')

    query = Book.query

    if status:
        query = query.filter_by(status=status)
    if title:
        query = query.filter(Book.title.contains(title))

    books = query.all()
    return jsonify({
        "books": [book.to_dict() for book in books],
        "count": len(books)
    }), 200


@bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """本の詳細取得 (全ユーザー)"""
    user = require_login()
    if not user:
        return jsonify({"error": "Login required"}), 401

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({"book": book.to_dict()}), 200
