from flask import Flask, jsonify, render_template
from flask_cors import CORS
from extensions import db, sess
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False

    # Enable CORS for browser access
    CORS(app, supports_credentials=True)

    # Initialize extensions with app
    db.init_app(app)
    sess.init_app(app)

    # Import models after db initialization
    from models import User, Book, BorrowRecord

    # Import routes
    from routes import auth, books, borrow, status

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(borrow.bp)
    app.register_blueprint(status.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api')
    def api_status():
        return jsonify({"message": "Library Management System API", "status": "running"})

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
