# 開発環境セットアップガイド

## 🚀 クイックスタート

### 前提条件
- Python 3.8以上
- SQL Server 2016以上
- Git
- Visual Studio Code（推奨）

### 初期セットアップ手順
```bash
# リポジトリのクローン
git clone <repository-url>
cd fastAPIProject

# Python仮想環境の作成
python -m venv venv

# 仮想環境の有効化（Windows）
venv\Scripts\activate.bat

# 仮想環境の有効化（Linux/Mac）
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
copy .env.example .env
# .envファイルを編集して適切な値を設定

# データベースマイグレーション
alembic upgrade head

# 開発サーバーの起動
python main.py
```

## 📋 依存関係管理

### requirements.txt
```txt
# Core Framework
fastapi==0.79.0
uvicorn[standard]==0.18.2
python-multipart==0.0.5

# Database
sqlalchemy==1.4.39
pyodbc==4.0.34
alembic==1.8.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==0.20.0

# Data Processing
pandas==2.0.2
numpy==1.24.3
openpyxl==3.0.10

# Utilities
pyyaml==6.0
python-dateutil==2.8.2
requests==2.28.1

# Development
pytest==7.1.2
pytest-asyncio==0.19.0
pytest-cov==3.0.0
black==22.6.0
flake8==4.0.1
mypy==0.971
```

## 🔧 環境設定

### 環境変数（.env）
```env
# Application
APP_NAME=FastAPIProject
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=9995
WORKERS=1

# Database
DATABASE_DRIVER=ODBC Driver 17 for SQL Server
DATABASE_SERVER=localhost
DATABASE_NAME=production_db
DATABASE_USER=sa
DATABASE_PASSWORD=your_password
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:9997"]

# File Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# External Services
TIMEPRO_API_URL=http://example.com/api
SMILE_API_URL=http://example.com/api
```

### データベース接続設定
```python
# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

# 接続文字列の構築
DATABASE_URL = (
    f"mssql+pyodbc://{os.getenv('DATABASE_USER')}:"
    f"{os.getenv('DATABASE_PASSWORD')}@"
    f"{os.getenv('DATABASE_SERVER')}/"
    f"{os.getenv('DATABASE_NAME')}?"
    f"driver={os.getenv('DATABASE_DRIVER')}"
)

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=int(os.getenv('DATABASE_POOL_SIZE', 5)),
    max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', 10)),
    pool_pre_ping=True,
    echo=os.getenv('DEBUG', 'False').lower() == 'true'
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依存性注入用関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 🏗️ プロジェクト構造

```
fastAPIProject/
├── .env                        # 環境変数
├── .env.example               # 環境変数サンプル
├── .gitignore                 # Git除外設定
├── requirements.txt           # Python依存関係
├── main.py                    # アプリケーションエントリーポイント
├── alembic.ini               # Alembic設定
├── logging_config.yaml       # ログ設定
├── tests/                    # テストディレクトリ
│   ├── __init__.py
│   ├── conftest.py          # pytest設定
│   └── test_*.py
├── alembic/                  # マイグレーション
│   ├── versions/
│   └── env.py
├── core/                     # コア機能
│   ├── __init__.py
│   ├── config.py            # アプリケーション設定
│   ├── security.py          # セキュリティ関連
│   └── database.py          # データベース設定
├── middleware/               # ミドルウェア
│   ├── __init__.py
│   ├── cors.py
│   └── logging.py
├── utils/                    # ユーティリティ
│   ├── __init__.py
│   └── validators.py
└── api/                      # 各API実装
    ├── __init__.py
    ├── syukkachecksheetapi/
    ├── prdctrl/
    ├── zaikokanriapi/
    └── auth/
```

## 🛠️ 開発ツール設定

### VS Code設定（.vscode/settings.json）
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.tabSize": 4
  }
}
```

### 推奨VS Code拡張機能
- Python (Microsoft)
- Pylance
- Python Test Explorer
- SQLTools
- Thunder Client (API Testing)
- GitLens

## 🧪 テスト環境

### pytest設定（pytest.ini）
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --asyncio-mode=strict
```

### テスト用データベース設定
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app
from core.database import Base, get_db

# テスト用データベース
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

## 🔍 デバッグ設定

### VS Code launch.json
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "9995"
      ],
      "jinja": true,
      "justMyCode": true,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": true
    }
  ]
}
```

## 📝 コーディング規約

### Python Style Guide
- PEP 8準拠
- 最大行長: 88文字（Black標準）
- インポート順序: 標準ライブラリ → サードパーティ → ローカル

### 型ヒント
```python
from typing import List, Optional, Dict, Any
from datetime import datetime

def process_data(
    items: List[Dict[str, Any]], 
    filter_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """データ処理関数"""
    pass
```

## 🚦 Git ワークフロー

### ブランチ戦略
```bash
main          # 本番環境
├── develop   # 開発環境
    ├── feature/feature-name    # 機能開発
    ├── bugfix/bug-name        # バグ修正
    └── hotfix/hotfix-name     # 緊急修正
```

### コミットメッセージ規約
```
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
style: コードスタイル修正
refactor: リファクタリング
test: テスト追加・修正
chore: ビルド・補助ツール変更
```

## 🔒 セキュリティチェックリスト

- [ ] 環境変数に機密情報を設定
- [ ] .envファイルを.gitignoreに追加
- [ ] SQLインジェクション対策（ORM使用）
- [ ] CORS設定の確認
- [ ] 認証・認可の実装
- [ ] 入力値バリデーション
- [ ] エラーメッセージの適切化
- [ ] ログに機密情報を出力しない