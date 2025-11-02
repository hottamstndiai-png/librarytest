# 図書貸し出しシステム (Library Management System)

社内向けのシンプルな図書貸し出し管理システムです。

## 機能

### ユーザー機能
- **ユーザー登録**: 社員が自分でアカウントを作成可能
- **ログイン/ログアウト**: IDとパスワードによる認証
- **本の貸出**: 1人あたり最大3冊、2週間まで
- **本の返却**: 借りた本を返却
- **状況確認**: 自分や他のユーザーの貸出状況を確認

### 管理者機能
- **本の登録**: 新しい本をシステムに追加（同一タイトル3冊まで）
- **本の削除**: 本をシステムから削除
- **期限切れ確認**: 返却期限を過ぎた本の一覧表示

## 技術スタック

- **バックエンド**: Python 3.x, Flask
- **データベース**: SQLite
- **認証**: Cookieベースのセッション管理
- **パスワード**: bcryptでハッシュ化

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 初期管理者アカウントの作成

```bash
python init_admin.py admin admin123
```

または対話的に作成:

```bash
python init_admin.py
```

### 3. テストデータの投入（オプション）

```bash
python seed_data.py
```

このコマンドで以下のデータが作成されます:
- 管理者アカウント: `admin / admin123`
- テストユーザー: `tanaka`, `sato`, `suzuki` (パスワード: `password123`)
- サンプルの本6冊

### 4. アプリケーションの起動

```bash
python app.py
```

サーバーは `http://localhost:5000` で起動します。

## API エンドポイント

### 認証

| メソッド | エンドポイント | 説明 | 認証 |
|---------|--------------|------|------|
| POST | `/api/register` | ユーザー登録 | 不要 |
| POST | `/api/login` | ログイン | 不要 |
| POST | `/api/logout` | ログアウト | 不要 |
| GET | `/api/me` | 現在のユーザー情報取得 | 必要 |

### 本の管理

| メソッド | エンドポイント | 説明 | 認証 |
|---------|--------------|------|------|
| POST | `/api/books` | 本を登録 | 管理者 |
| DELETE | `/api/books/:id` | 本を削除 | 管理者 |
| GET | `/api/books` | 本の一覧取得 | ユーザー |
| GET | `/api/books/:id` | 本の詳細取得 | ユーザー |

### 貸出・返却

| メソッド | エンドポイント | 説明 | 認証 |
|---------|--------------|------|------|
| POST | `/api/borrow` | 本を借りる | ユーザー |
| POST | `/api/return` | 本を返却 | ユーザー |

### 状況確認

| メソッド | エンドポイント | 説明 | 認証 |
|---------|--------------|------|------|
| GET | `/api/status/user/:id` | ユーザーの貸出状況 | ユーザー |
| GET | `/api/status/book/:id` | 本の貸出状況 | ユーザー |
| GET | `/api/status/overdue` | 期限切れ一覧 | ユーザー |
| GET | `/api/status/history` | 貸出履歴 | ユーザー |

## 使用例

### ユーザー登録

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "yamada", "password": "password123"}'
```

### ログイン

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "yamada", "password": "password123"}' \
  -c cookies.txt
```

### 本を借りる

```bash
curl -X POST http://localhost:5000/api/borrow \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1}' \
  -b cookies.txt
```

### 本を返す

```bash
curl -X POST http://localhost:5000/api/return \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1}' \
  -b cookies.txt
```

### 貸出状況を確認

```bash
curl http://localhost:5000/api/status/user/1 -b cookies.txt
```

## ビジネスルール

- 1ユーザーあたり最大3冊まで同時に借りられます
- 貸出期間は2週間（14日）です
- 同一タイトルの本は最大3冊まで登録できます
- 管理者のみ本の登録・削除が可能です
- 借りられている本は削除できません

## プロジェクト構造

```
librarytest/
├── app.py              # メインアプリケーション
├── config.py           # 設定ファイル
├── models.py           # データベースモデル
├── requirements.txt    # 依存関係
├── init_admin.py       # 管理者アカウント作成スクリプト
├── seed_data.py        # テストデータ投入スクリプト
├── routes/
│   ├── __init__.py
│   ├── auth.py         # 認証ルート
│   ├── books.py        # 本管理ルート
│   ├── borrow.py       # 貸出・返却ルート
│   └── status.py       # 状況確認ルート
└── README.md
```

## ライセンス

このプロジェクトは社内利用を目的としています。
