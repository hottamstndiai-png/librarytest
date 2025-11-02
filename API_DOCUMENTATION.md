# API ドキュメント

## 認証 API

### POST /api/register
新しいユーザーアカウントを作成します。

**リクエスト:**
```json
{
  "username": "string",
  "password": "string"
}
```

**レスポンス (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "user_id": 1,
    "username": "yamada",
    "is_admin": false,
    "created_at": "2025-10-23T10:00:00"
  }
}
```

**エラー:**
- 400: Username and password are required
- 409: Username already exists

---

### POST /api/login
既存のユーザーでログインします。

**リクエスト:**
```json
{
  "username": "string",
  "password": "string"
}
```

**レスポンス (200):**
```json
{
  "message": "Login successful",
  "user": {
    "user_id": 1,
    "username": "yamada",
    "is_admin": false,
    "created_at": "2025-10-23T10:00:00"
  }
}
```

**エラー:**
- 400: Username and password are required
- 401: Invalid username or password

**Note:** ログイン成功後、セッションCookieが設定されます。

---

### POST /api/logout
現在のセッションをログアウトします。

**レスポンス (200):**
```json
{
  "message": "Logout successful"
}
```

---

### GET /api/me
現在ログインしているユーザー情報を取得します。

**認証:** 必要

**レスポンス (200):**
```json
{
  "user": {
    "user_id": 1,
    "username": "yamada",
    "is_admin": false,
    "created_at": "2025-10-23T10:00:00"
  }
}
```

**エラー:**
- 401: Not logged in
- 404: User not found

---

## 本管理 API

### POST /api/books
新しい本を登録します。

**認証:** 管理者のみ

**リクエスト:**
```json
{
  "title": "string",
  "author": "string"
}
```

**レスポンス (201):**
```json
{
  "message": "Book added successfully",
  "book": {
    "book_id": 1,
    "title": "Pythonプログラミング入門",
    "author": "山田太郎",
    "status": "available",
    "created_at": "2025-10-23T10:00:00"
  }
}
```

**エラー:**
- 400: Title and author are required
- 400: Maximum 3 copies of the same title allowed
- 403: Admin authentication required

---

### DELETE /api/books/:id
指定されたIDの本を削除します。

**認証:** 管理者のみ

**パラメータ:**
- `id` (path): 本のID

**レスポンス (200):**
```json
{
  "message": "Book deleted successfully"
}
```

**エラー:**
- 400: Cannot delete a book that is currently borrowed
- 403: Admin authentication required
- 404: Book not found

---

### GET /api/books
本の一覧を取得します。

**認証:** 必要

**クエリパラメータ:**
- `status` (optional): "available" または "borrowed"
- `title` (optional): タイトルで部分一致検索

**レスポンス (200):**
```json
{
  "books": [
    {
      "book_id": 1,
      "title": "Pythonプログラミング入門",
      "author": "山田太郎",
      "status": "available",
      "created_at": "2025-10-23T10:00:00"
    }
  ],
  "count": 1
}
```

**エラー:**
- 401: Login required

---

### GET /api/books/:id
指定されたIDの本の詳細を取得します。

**認証:** 必要

**パラメータ:**
- `id` (path): 本のID

**レスポンス (200):**
```json
{
  "book": {
    "book_id": 1,
    "title": "Pythonプログラミング入門",
    "author": "山田太郎",
    "status": "available",
    "created_at": "2025-10-23T10:00:00"
  }
}
```

**エラー:**
- 401: Login required
- 404: Book not found

---

## 貸出・返却 API

### POST /api/borrow
本を借ります。

**認証:** 必要

**リクエスト:**
```json
{
  "book_id": 1
}
```

**レスポンス (201):**
```json
{
  "message": "Book borrowed successfully",
  "record": {
    "record_id": 1,
    "user_id": 1,
    "book_id": 1,
    "borrow_date": "2025-10-23T10:00:00",
    "due_date": "2025-11-06T10:00:00",
    "return_date": null,
    "is_overdue": false
  },
  "book": {
    "book_id": 1,
    "title": "Pythonプログラミング入門",
    "author": "山田太郎",
    "status": "borrowed",
    "created_at": "2025-10-23T10:00:00"
  }
}
```

**エラー:**
- 400: book_id is required
- 400: Book is not available
- 400: Maximum 3 books can be borrowed at a time
- 401: Login required
- 404: Book not found

---

### POST /api/return
借りている本を返却します。

**認証:** 必要

**リクエスト:**
```json
{
  "book_id": 1
}
```

**レスポンス (200):**
```json
{
  "message": "Book returned successfully",
  "record": {
    "record_id": 1,
    "user_id": 1,
    "book_id": 1,
    "borrow_date": "2025-10-23T10:00:00",
    "due_date": "2025-11-06T10:00:00",
    "return_date": "2025-10-25T10:00:00",
    "is_overdue": false
  },
  "book": {
    "book_id": 1,
    "title": "Pythonプログラミング入門",
    "author": "山田太郎",
    "status": "available",
    "created_at": "2025-10-23T10:00:00"
  }
}
```

**エラー:**
- 400: book_id is required
- 401: Login required
- 404: No active borrow record found for this book
- 404: Book not found

---

## 状況確認 API

### GET /api/status/user/:id
指定されたユーザーの現在の貸出状況を取得します。

**認証:** 必要

**パラメータ:**
- `id` (path): ユーザーID

**レスポンス (200):**
```json
{
  "user_id": 1,
  "username": "yamada",
  "active_borrows": 2,
  "borrows": [
    {
      "record_id": 1,
      "user_id": 1,
      "book_id": 1,
      "borrow_date": "2025-10-23T10:00:00",
      "due_date": "2025-11-06T10:00:00",
      "return_date": null,
      "is_overdue": false,
      "book": {
        "book_id": 1,
        "title": "Pythonプログラミング入門",
        "author": "山田太郎",
        "status": "borrowed",
        "created_at": "2025-10-23T10:00:00"
      }
    }
  ]
}
```

**エラー:**
- 401: Login required
- 404: User not found

---

### GET /api/status/book/:id
指定された本の現在の貸出状況を取得します。

**認証:** 必要

**パラメータ:**
- `id` (path): 本のID

**レスポンス (200) - 貸出中の場合:**
```json
{
  "book": {
    "book_id": 1,
    "title": "Pythonプログラミング入門",
    "author": "山田太郎",
    "status": "borrowed",
    "created_at": "2025-10-23T10:00:00"
  },
  "borrowed_by": {
    "user_id": 1,
    "username": "yamada"
  },
  "borrow_record": {
    "record_id": 1,
    "user_id": 1,
    "book_id": 1,
    "borrow_date": "2025-10-23T10:00:00",
    "due_date": "2025-11-06T10:00:00",
    "return_date": null,
    "is_overdue": false
  }
}
```

**レスポンス (200) - 利用可能な場合:**
```json
{
  "book": {
    "book_id": 1,
    "title": "Pythonプログラミング入門",
    "author": "山田太郎",
    "status": "available",
    "created_at": "2025-10-23T10:00:00"
  },
  "borrowed_by": null,
  "borrow_record": null
}
```

**エラー:**
- 401: Login required
- 404: Book not found

---

### GET /api/status/overdue
返却期限を過ぎている本の一覧を取得します。

**認証:** 必要

**レスポンス (200):**
```json
{
  "overdue_count": 1,
  "overdue_records": [
    {
      "record_id": 1,
      "user_id": 1,
      "book_id": 1,
      "borrow_date": "2025-10-01T10:00:00",
      "due_date": "2025-10-15T10:00:00",
      "return_date": null,
      "is_overdue": true,
      "days_overdue": 8,
      "book": {
        "book_id": 1,
        "title": "Pythonプログラミング入門",
        "author": "山田太郎",
        "status": "borrowed",
        "created_at": "2025-10-01T10:00:00"
      },
      "user": {
        "user_id": 1,
        "username": "yamada"
      }
    }
  ]
}
```

**エラー:**
- 401: Login required

---

### GET /api/status/history
貸出履歴を取得します。

**認証:** 必要

**クエリパラメータ:**
- `user_id` (optional): 特定のユーザーの履歴のみ取得

**レスポンス (200):**
```json
{
  "total_records": 5,
  "history": [
    {
      "record_id": 5,
      "user_id": 1,
      "book_id": 1,
      "borrow_date": "2025-10-23T10:00:00",
      "due_date": "2025-11-06T10:00:00",
      "return_date": "2025-10-25T10:00:00",
      "is_overdue": false,
      "book": {
        "book_id": 1,
        "title": "Pythonプログラミング入門",
        "author": "山田太郎",
        "status": "available",
        "created_at": "2025-10-23T10:00:00"
      },
      "user": {
        "user_id": 1,
        "username": "yamada"
      }
    }
  ]
}
```

**エラー:**
- 401: Login required

---

## エラーレスポンス形式

すべてのエラーレスポンスは以下の形式で返されます:

```json
{
  "error": "Error message describing what went wrong"
}
```

## HTTPステータスコード

- `200 OK`: リクエスト成功
- `201 Created`: リソース作成成功
- `400 Bad Request`: リクエストが不正
- `401 Unauthorized`: 認証が必要
- `403 Forbidden`: 権限不足
- `404 Not Found`: リソースが見つからない
- `409 Conflict`: リソースの競合（例: ユーザー名の重複）
- `500 Internal Server Error`: サーバー内部エラー
