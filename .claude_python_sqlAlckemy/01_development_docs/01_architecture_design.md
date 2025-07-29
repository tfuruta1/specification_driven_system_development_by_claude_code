# アーキテクチャ設計書

## 🏗️ システムアーキテクチャ概要

### マイクロサービスアーキテクチャ
本システムは、機能ごとに独立したマイクロサービスとして構成され、統合エントリーポイントを通じて一元的にアクセス可能な設計となっています。

```
┌─────────────────────────────────────────────────────────┐
│                    クライアント層                         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTTPS
┌────────────────────▼────────────────────────────────────┐
│              統合APIゲートウェイ (main.py)               │
│                  http://localhost:9995                   │
└────────────────────┬────────────────────────────────────┘
                     │ Internal Routing
     ┌───────────────┼───────────────┬──────────────┐
     │               │               │              │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│出荷管理 │    │生産管理 │    │在庫管理 │    │認証管理 │
│  API    │    │  API    │    │  API    │    │  API    │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │               │               │              │
     └───────────────┴───────────────┴──────────────┘
                     │ SQLAlchemy ORM
              ┌──────▼──────┐
              │ SQL Server  │
              └─────────────┘
```

## 📋 レイヤードアーキテクチャ

### 1. プレゼンテーション層（Routes）
- **責務**: HTTPリクエスト/レスポンスの処理
- **実装**: FastAPIルーター
- **特徴**: 
  - RESTful API設計
  - 自動バリデーション
  - OpenAPI仕様準拠

### 2. ビジネスロジック層（Services）
- **責務**: ビジネスルールの実装
- **実装**: サービスクラス
- **特徴**:
  - ドメインロジックの集約
  - トランザクション管理
  - 複雑な業務処理

### 3. データアクセス層（Repository/CRUD）
- **責務**: データベース操作の抽象化
- **実装**: CRUDモジュール
- **特徴**:
  - SQLAlchemy ORM活用
  - クエリ最適化
  - データ整合性保証

### 4. データモデル層（Models/Schemas）
- **責務**: データ構造の定義
- **実装**: 
  - SQLAlchemyモデル（DB）
  - Pydanticスキーマ（API）
- **特徴**:
  - 型安全性
  - バリデーション
  - シリアライゼーション

## 🔧 コンポーネント設計

### 1. 統合APIゲートウェイ
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="製造業品質管理システムAPI")

# 各サービスのルーター登録
app.include_router(syukka_router, prefix="/syukkachecksheetapi")
app.include_router(prdctrl_router, prefix="/prdctrl")
app.include_router(zaiko_router, prefix="/zaikokanriapi")
```

### 2. 個別マイクロサービス構造
```
service_name/
├── main.py          # サービスルーター
├── models.py        # SQLAlchemyモデル
├── schemas.py       # Pydanticスキーマ
├── crud.py          # データベース操作
├── service.py       # ビジネスロジック
├── database.py      # DB接続設定
├── dependencies.py  # 依存性注入
├── exceptions.py    # カスタム例外
└── utils.py         # ユーティリティ
```

## 🔄 データフロー設計

### 1. リクエスト処理フロー
```
Client Request
    ↓
API Gateway (Authentication/Routing)
    ↓
Service Router (Path Operations)
    ↓
Dependencies (DB Session, Auth Check)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Database
```

### 2. レスポンス処理フロー
```
Database Result
    ↓
Model to Schema Conversion
    ↓
Business Logic Processing
    ↓
Response Serialization
    ↓
HTTP Response
```

## 🔐 セキュリティアーキテクチャ

### 1. 認証フロー
```python
# JWT認証フロー
1. ユーザーログイン
2. 認証情報検証
3. JWTトークン生成
4. クライアントへトークン返却
5. 以降のリクエストでトークン検証
```

### 2. 認可設計
- ロールベースアクセス制御（RBAC）
- APIレベルでの権限チェック
- リソースレベルでのアクセス制御

## 🚀 スケーラビリティ設計

### 1. 水平スケーリング
- サービスの独立性による個別スケーリング
- ロードバランサーによる負荷分散
- ステートレスな設計

### 2. 垂直スケーリング
- 非同期処理による効率化
- データベース接続プーリング
- キャッシング戦略

## 📊 データベース設計方針

### 1. 正規化戦略
- 第3正規形を基本とする
- パフォーマンスのための適切な非正規化
- インデックス戦略

### 2. トランザクション管理
```python
# SQLAlchemyセッション管理
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 🔍 監視・ロギング設計

### 1. ロギング戦略
- 構造化ログ（YAML設定）
- ログレベル管理
- ログローテーション

### 2. メトリクス収集
- レスポンスタイム
- エラー率
- スループット
- リソース使用率

## 🛠️ エラーハンドリング

### 1. 例外処理階層
```python
BaseException
├── BusinessException
│   ├── ValidationException
│   ├── NotfoundException
│   └── ConflictException
├── SystemException
│   ├── DatabaseException
│   └── ExternalServiceException
└── SecurityException
    ├── AuthenticationException
    └── AuthorizationException
```

### 2. エラーレスポンス標準化
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "エラーメッセージ",
        "details": {},
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

## 🔄 デプロイメントアーキテクチャ

### 1. 開発環境
- ローカル開発サーバー（uvicorn）
- SQLite/開発用DBサーバー
- ホットリロード対応

### 2. 本番環境
- IIS + FastAPI
- SQL Server
- ロードバランサー
- SSL/TLS通信