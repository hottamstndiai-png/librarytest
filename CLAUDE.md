# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Library Management System (図書貸し出しシステム) - a simple internal book lending system for companies. It provides both a REST API and a web interface for managing book loans.

**Key Business Rules:**
- Users can borrow up to 3 books simultaneously
- Loan period is 14 days
- Maximum 3 copies per book title
- Admins can add/delete books; regular users can only borrow/return

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create initial admin account (username: admin, password: admin123)
python init_admin.py admin admin123

# Seed test data (creates users: tanaka/sato/suzuki with password: password123)
python seed_data.py
```

### Running
```bash
# Start development server (http://localhost:5000)
python app.py

# Web UI is at http://localhost:5000/
# API status at http://localhost:5000/api

# IMPORTANT: Only run one instance at a time
# If port 5000 is already in use, kill existing process:
# On Windows: netstat -ano | findstr :5000 then taskkill /PID <pid> /F
# On Unix: lsof -ti:5000 | xargs kill -9
```

### Testing
```bash
# Example API test - login and save session
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"tanaka","password":"password123"}' \
  -c cookies.txt

# Borrow a book
curl -X POST http://localhost:5000/api/borrow \
  -H "Content-Type: application/json" \
  -d '{"book_id":1}' \
  -b cookies.txt

# Check user's borrow status
curl http://localhost:5000/api/status/user/2 -b cookies.txt
```

## Architecture

### Application Factory Pattern
The app uses Flask's application factory pattern (`create_app()` in `app.py`) to avoid circular imports. Extensions are initialized in `extensions.py` and bound to the app in `create_app()`.

**Critical Import Order:**
1. `extensions.py` - Initializes `db` and `sess` without app context
2. `models.py` - Imports `db` from extensions
3. `app.py` - Creates app, initializes extensions with app context, imports models
4. `routes/*.py` - Import `db` from extensions, not from app

**Why:** This prevents circular import errors. Never import `db` from `app.py` in other modules.

**The extensions.py Pattern:**
```python
# extensions.py - Shared extension instances
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()  # No app binding yet
sess = Session()

# app.py - Bind extensions to app
def create_app():
    app = Flask(__name__)
    db.init_app(app)  # Bind here, not at import time
    sess.init_app(app)

    from models import User  # Import AFTER init
    return app

# models.py - Import from extensions, NOT app
from extensions import db  # ✅ Correct
# from app import db  # ❌ Causes circular import

class User(db.Model):
    pass
```

This is THE most important architectural pattern in this codebase. Violating it will cause `ImportError`.

### Database Schema
Three main models with relationships:
- **User** (users) - username, password_hash, is_admin
- **Book** (books) - title, author, status ('available'/'borrowed')
- **BorrowRecord** (borrow_records) - tracks loans with borrow_date, due_date, return_date

**Key relationships:**
- User has many BorrowRecords
- Book has many BorrowRecords
- BorrowRecord belongs to User and Book

### Route Organization (Blueprint Architecture)
Routes are organized by domain in separate blueprint modules under `routes/`:

- **auth.py** (`/api/*`) - register, login, logout, current user
  - Uses bcrypt for password hashing
  - Cookie-based session management
  - Provides `require_login()` and `require_admin()` helper functions

- **books.py** (`/api/books/*`) - CRUD operations for books
  - GET /books - list (with optional status/title filters)
  - POST /books - create (admin only, enforces MAX_BOOKS_SAME_TITLE)
  - DELETE /books/:id - delete (admin only, prevents deletion of borrowed books)

- **borrow.py** (`/api/borrow`, `/api/return`) - loan operations
  - POST /borrow - enforces MAX_BOOKS_PER_USER and checks availability
  - POST /return - marks return_date and updates book status

- **status.py** (`/api/status/*`) - reporting endpoints
  - GET /status/user/:id - active borrows for user
  - GET /status/book/:id - who borrowed a specific book
  - GET /status/overdue - all overdue loans
  - GET /status/history - loan history (filterable by user_id)

### Business Logic Location
- **Validation rules** in route handlers (e.g., max books check in routes/borrow.py:34)
- **Business constants** in config.py (MAX_BOOKS_PER_USER, MAX_BOOKS_SAME_TITLE, LOAN_PERIOD_DAYS)
- **Derived logic** as model methods (e.g., BorrowRecord.is_overdue() in models.py:72)

### Frontend Architecture
Single-page application in `templates/index.html` with vanilla JavaScript:

**Features:**
- Tab-based navigation (books list, my borrows, history, admin)
- User authentication (login/register forms with test account info displayed)
- Real-time search box for book titles
- Multi-level filtering:
  - Status filter (all/available/borrowed)
  - Author filter (dynamically generated from available books)
  - Text search (filters by title)
  - All filters work in combination
- View modes: grid view vs. grouped-by-author sections
- Book borrowing/returning with visual feedback
- Overdue warnings (red highlighting for overdue books)
- Admin panel (only visible to admin users)

**Key frontend patterns:**
- All data loaded once, filtered client-side for performance
- API calls use `fetch()` with `credentials: 'include'` for cookie-based auth
- Display functions separate concerns: `displayBooksAsList()` vs `displayBooksByAuthor()`
- State management via global variables (allBooks, currentStatusFilter, currentAuthorFilter, currentViewMode)
- Filter buttons dynamically get .active class for visual feedback
- Gradient design (purple theme: #667eea → #764ba2)

## Common Modifications

### Adding a new API endpoint
1. Add route function in appropriate blueprint file under `routes/`
2. Import and use `require_login()` or `require_admin()` from routes/auth.py for auth
3. Use `db.session.add()` / `db.session.commit()` for database changes
4. Always wrap in try/except and rollback on error

### Modifying business rules
Update constants in `config.py` (e.g., change loan period from 14 to 21 days)

### Adding a new database field
1. Add column to model in `models.py`
2. Update `to_dict()` method if field should be in API responses
3. Delete `library.db` and restart app (auto-creates schema)
4. For production: use Flask-Migrate for migrations

### Extending the web UI
- Filters/search: modify `displayBooks()` function in templates/index.html
- New tab: add to tab navigation and create new tab-content div
- Styling: CSS is inline in `<style>` tag at top of templates/index.html

## Important Files
- **API_DOCUMENTATION.md** - Complete API reference with request/response examples
- **seed_data.py** - Example of creating users/books programmatically
- **init_admin.py** - Template for admin user creation scripts
- **library.db** - SQLite database (auto-created on first run, delete to reset)
- **flask_session/** - Session storage directory (auto-created, safe to delete when server is stopped)

## Database Management

### Resetting the Database
```bash
# Stop the server first
# Delete database and session data
rm library.db
rm -rf flask_session/

# Restart and reinitialize
python app.py  # Creates empty schema
python seed_data.py  # Optional: add test data
```

### Database Location
- SQLite file: `library.db` in project root
- Schema auto-created on first run via `db.create_all()` in app.py:46
- No migrations configured (use Flask-Migrate for production)
