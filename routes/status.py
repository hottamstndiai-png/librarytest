from flask import Blueprint, request, jsonify
from datetime import datetime
from extensions import db
from models import Book, BorrowRecord, User
from routes.auth import require_login

bp = Blueprint('status', __name__, url_prefix='/api')


@bp.route('/status/user/<int:user_id>', methods=['GET'])
def get_user_status(user_id):
    """ユーザーの貸出状況を取得"""
    user = require_login()
    if not user:
        return jsonify({"error": "Login required"}), 401

    # Check if target user exists
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"error": "User not found"}), 404

    # Get active borrow records for this user
    active_records = BorrowRecord.query.filter_by(
        user_id=user_id,
        return_date=None
    ).all()

    # Build response with book details
    borrows = []
    for record in active_records:
        book = Book.query.get(record.book_id)
        borrow_info = record.to_dict()
        borrow_info['book'] = book.to_dict() if book else None
        borrows.append(borrow_info)

    return jsonify({
        "user_id": user_id,
        "username": target_user.username,
        "active_borrows": len(borrows),
        "borrows": borrows
    }), 200


@bp.route('/status/book/<int:book_id>', methods=['GET'])
def get_book_status(book_id):
    """本の貸出状況を取得"""
    user = require_login()
    if not user:
        return jsonify({"error": "Login required"}), 401

    # Check if book exists
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Get current borrow record if any
    active_record = BorrowRecord.query.filter_by(
        book_id=book_id,
        return_date=None
    ).first()

    response = {
        "book": book.to_dict()
    }

    if active_record:
        borrower = User.query.get(active_record.user_id)
        response["borrowed_by"] = {
            "user_id": borrower.user_id,
            "username": borrower.username
        }
        response["borrow_record"] = active_record.to_dict()
    else:
        response["borrowed_by"] = None
        response["borrow_record"] = None

    return jsonify(response), 200


@bp.route('/status/overdue', methods=['GET'])
def get_overdue_books():
    """期限切れの貸出一覧を取得"""
    user = require_login()
    if not user:
        return jsonify({"error": "Login required"}), 401

    # Get all active borrow records
    active_records = BorrowRecord.query.filter_by(return_date=None).all()

    # Filter overdue records
    overdue_records = []
    current_time = datetime.utcnow()

    for record in active_records:
        if record.due_date < current_time:
            book = Book.query.get(record.book_id)
            borrower = User.query.get(record.user_id)

            record_info = record.to_dict()
            record_info['book'] = book.to_dict() if book else None
            record_info['user'] = {
                'user_id': borrower.user_id,
                'username': borrower.username
            } if borrower else None

            # Calculate days overdue
            days_overdue = (current_time - record.due_date).days
            record_info['days_overdue'] = days_overdue

            overdue_records.append(record_info)

    return jsonify({
        "overdue_count": len(overdue_records),
        "overdue_records": overdue_records
    }), 200


@bp.route('/status/history', methods=['GET'])
def get_borrow_history():
    """貸出履歴を取得 (全ユーザーまたは特定ユーザー)"""
    user = require_login()
    if not user:
        return jsonify({"error": "Login required"}), 401

    # Get query parameter
    target_user_id = request.args.get('user_id', type=int)

    query = BorrowRecord.query

    # Filter by user if specified
    if target_user_id:
        query = query.filter_by(user_id=target_user_id)

    # Get all records (including returned books)
    records = query.order_by(BorrowRecord.borrow_date.desc()).all()

    history = []
    for record in records:
        book = Book.query.get(record.book_id)
        borrower = User.query.get(record.user_id)

        record_info = record.to_dict()
        record_info['book'] = book.to_dict() if book else None
        record_info['user'] = {
            'user_id': borrower.user_id,
            'username': borrower.username
        } if borrower else None

        history.append(record_info)

    return jsonify({
        "total_records": len(history),
        "history": history
    }), 200
