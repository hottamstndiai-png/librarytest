from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from extensions import db
from models import Book, BorrowRecord, User
from routes.auth import require_login
from config import Config

bp = Blueprint('borrow', __name__, url_prefix='/api')


@bp.route('/borrow', methods=['POST'])
def borrow_book():
    """本の貸出 (全ユーザー)"""
    user = require_login()
    if not user:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()
    if not data or not data.get('book_id'):
        return jsonify({"error": "book_id is required"}), 400

    book_id = data['book_id']

    # Check if book exists
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Check if book is available
    if book.status != 'available':
        return jsonify({"error": "Book is not available"}), 400

    # Check if user has reached maximum borrow limit
    active_borrows = BorrowRecord.query.filter_by(
        user_id=user.user_id,
        return_date=None
    ).count()

    if active_borrows >= Config.MAX_BOOKS_PER_USER:
        return jsonify({
            "error": f"Maximum {Config.MAX_BOOKS_PER_USER} books can be borrowed at a time"
        }), 400

    # Create borrow record
    borrow_date = datetime.utcnow()
    due_date = borrow_date + timedelta(days=Config.LOAN_PERIOD_DAYS)

    borrow_record = BorrowRecord(
        user_id=user.user_id,
        book_id=book_id,
        borrow_date=borrow_date,
        due_date=due_date
    )

    # Update book status
    book.status = 'borrowed'

    try:
        db.session.add(borrow_record)
        db.session.commit()
        return jsonify({
            "message": "Book borrowed successfully",
            "record": borrow_record.to_dict(),
            "book": book.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to borrow book: {str(e)}"}), 500


@bp.route('/return', methods=['POST'])
def return_book():
    """本の返却 (全ユーザー)"""
    user = require_login()
    if not user:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()
    if not data or not data.get('book_id'):
        return jsonify({"error": "book_id is required"}), 400

    book_id = data['book_id']

    # Find active borrow record for this user and book
    borrow_record = BorrowRecord.query.filter_by(
        user_id=user.user_id,
        book_id=book_id,
        return_date=None
    ).first()

    if not borrow_record:
        return jsonify({"error": "No active borrow record found for this book"}), 404

    # Get book
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Update borrow record
    borrow_record.return_date = datetime.utcnow()

    # Update book status
    book.status = 'available'

    try:
        db.session.commit()
        return jsonify({
            "message": "Book returned successfully",
            "record": borrow_record.to_dict(),
            "book": book.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to return book: {str(e)}"}), 500
