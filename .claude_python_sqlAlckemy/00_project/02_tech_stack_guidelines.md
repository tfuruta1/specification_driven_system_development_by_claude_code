# 技術スタックガイドライン

## 📚 コア技術スタック

### バックエンドフレームワーク
- **FastAPI 0.79.0**
  - 高速な非同期処理
  - 自動APIドキュメント生成
  - 型ヒントによる開発効率向上
  - Pydanticとの強力な統合

### データベース
- **SQL Server**
  - エンタープライズグレードのRDBMS
  - 高い信頼性とパフォーマンス
  - 既存システムとの互換性

- **SQLAlchemy**
  - パワフルなORM
  - データベース抽象化層
  - マイグレーション管理
  - 複雑なクエリのサポート

### 認証・セキュリティ
- **python-jose**
  - JWT認証実装
  - トークンベース認証
  - セキュアなAPI保護

### データ処理
- **pandas 2.0.2**
  - 大量データの効率的処理
  - データ分析・変換
  - Excel/CSVファイル処理

- **numpy 1.24.3**
  - 数値計算処理
  - 統計分析サポート

### サーバー・デプロイメント
- **uvicorn 0.18.2**
  - 高性能ASGIサーバー
  - 非同期処理対応
  - プロダクション対応

- **IIS (Internet Information Services)**
  - Windows Server環境でのホスティング
  - エンタープライズ環境での実績

### データベース接続
- **pyodbc**
  - SQL Serverへの安定接続
  - ネイティブドライバサポート
  - 高速なデータアクセス

## 🏗️ アーキテクチャパターン

### 1. レイヤードアーキテクチャ
```
┌─────────────────────┐
│   Presentation      │ ← FastAPI Routes
├─────────────────────┤
│   Business Logic    │ ← Service Layer
├─────────────────────┤
│   Data Access       │ ← Repository/CRUD
├─────────────────────┤
│   Database          │ ← SQL Server
└─────────────────────┘
```

### 2. マイクロサービスパターン
- 各APIは独立したサービスとして設計
- 疎結合で高凝集なモジュール
- サービス間の明確な境界

### 3. リポジトリパターン
- データアクセスロジックの抽象化
- テスタビリティの向上
- データソースの変更に対する柔軟性

## 📁 標準プロジェクト構造

```
api_name/
├── main.py          # FastAPIルーター定義
├── crud.py          # データベース操作（CRUD）
├── models.py        # SQLAlchemyモデル
├── schemas.py       # Pydanticスキーマ
├── database.py      # DB接続設定
├── service.py       # ビジネスロジック
├── dependencies.py  # 依存性注入
└── utils.py         # ユーティリティ関数
```

## 🔧 開発ガイドライン

### 1. 型ヒントの活用
```python
from typing import List, Optional
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
```

### 2. 非同期処理の実装
```python
@router.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    return await crud.get_item(db, item_id)
```

### 3. エラーハンドリング
```python
from fastapi import HTTPException

if not item:
    raise HTTPException(
        status_code=404,
        detail="Item not found"
    )
```

### 4. データバリデーション
- Pydanticスキーマによる入力検証
- SQLAlchemyモデルでのDB制約
- カスタムバリデーターの実装

## 🚀 パフォーマンス最適化

### 1. データベース最適化
- インデックスの適切な設定
- N+1問題の回避
- バッチ処理の活用

### 2. キャッシング戦略
- Redis等の導入検討
- 適切なキャッシュ期間設定
- キャッシュ無効化戦略

### 3. 非同期処理
- I/Oバウンドタスクの非同期化
- バックグラウンドタスクの活用
- 並列処理の実装

## 🔒 セキュリティ要件

### 1. 認証・認可
- JWT トークンベース認証
- ロールベースアクセス制御（RBAC）
- APIキー管理

### 2. データ保護
- 機密データの暗号化
- SQLインジェクション対策
- XSS対策

### 3. 通信セキュリティ
- HTTPS通信の強制
- CORS設定の適切な管理
- レート制限の実装

## 📊 モニタリング・ログ

### 1. ログ管理
- 構造化ログの実装
- ログレベルの適切な設定
- ログローテーション

### 2. メトリクス収集
- レスポンスタイム監視
- エラー率追跡
- リソース使用状況監視

### 3. アラート設定
- 異常検知の自動化
- 適切な通知設定
- インシデント対応フロー