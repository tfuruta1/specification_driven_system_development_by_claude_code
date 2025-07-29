# API設計書

## 🌐 API設計原則

### RESTful設計
- リソース指向URL設計
- 適切なHTTPメソッドの使用
- ステートレスな通信
- 統一されたレスポンス形式

### バージョニング戦略
- URLパスベースのバージョニング
- 例: `/api/v1/resources`
- 後方互換性の維持

## 📍 エンドポイント設計

### 1. 出荷管理API

#### 出荷チェックシート
```python
# 一覧取得
GET /syukkachecksheetapi/checksheets
Query Parameters:
  - page: int = 1
  - limit: int = 50
  - shipment_date_from: date
  - shipment_date_to: date
  - customer_id: int
  - status: str

Response: 200 OK
{
  "items": [
    {
      "checksheet_id": 1,
      "shipment_no": "SH2024001",
      "customer_name": "顧客A",
      "product_name": "製品X",
      "shipment_date": "2024-01-15",
      "status": "completed"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 50
}

# 詳細取得
GET /syukkachecksheetapi/checksheets/{checksheet_id}

Response: 200 OK
{
  "checksheet_id": 1,
  "shipment_no": "SH2024001",
  "customer": {
    "customer_id": 10,
    "customer_name": "顧客A"
  },
  "product": {
    "product_id": 100,
    "product_name": "製品X",
    "product_code": "PRD-X001"
  },
  "items": [
    {
      "item_id": 1,
      "check_point": "外観検査",
      "result": "OK",
      "note": null
    }
  ],
  "inspector": {
    "employee_id": 50,
    "full_name": "検査太郎"
  },
  "status": "completed",
  "created_at": "2024-01-15T10:00:00Z"
}

# 新規作成
POST /syukkachecksheetapi/checksheets
Request Body:
{
  "shipment_no": "SH2024002",
  "customer_id": 10,
  "product_id": 100,
  "shipment_date": "2024-01-16",
  "items": [
    {
      "check_point": "外観検査",
      "result": "OK"
    }
  ]
}

Response: 201 Created
{
  "checksheet_id": 2,
  "message": "チェックシートが作成されました"
}

# 更新
PUT /syukkachecksheetapi/checksheets/{checksheet_id}

# 削除
DELETE /syukkachecksheetapi/checksheets/{checksheet_id}
```

### 2. 生産管理API

#### 生産実績
```python
# バッチ実績取得
GET /prdctrl/production-results/batch
Query Parameters:
  - work_order_nos: str (comma separated)
  - date_from: datetime
  - date_to: datetime
  - line_ids: str (comma separated)

Response: 200 OK
{
  "results": [
    {
      "work_order_no": "WO2024001",
      "product": {
        "product_id": 100,
        "product_name": "製品X"
      },
      "line": {
        "line_id": 1,
        "line_name": "生産ライン1"
      },
      "planned_quantity": 1000,
      "actual_quantity": 980,
      "defect_quantity": 20,
      "efficiency": 98.0,
      "start_time": "2024-01-15T08:00:00Z",
      "end_time": "2024-01-15T17:00:00Z"
    }
  ],
  "summary": {
    "total_planned": 5000,
    "total_actual": 4900,
    "total_defect": 100,
    "overall_efficiency": 98.0
  }
}

# リアルタイム実績登録
POST /prdctrl/production-results/realtime
Request Body:
{
  "work_order_no": "WO2024001",
  "line_id": 1,
  "worker_id": 100,
  "quantity": 50,
  "defects": [
    {
      "defect_type_id": 1,
      "quantity": 2,
      "cause": "材料不良"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}

Response: 200 OK
{
  "result_id": 1000,
  "current_total": 500,
  "current_efficiency": 96.0
}

# 不良分析
GET /prdctrl/defect-analysis
Query Parameters:
  - period: str (daily|weekly|monthly)
  - date: date
  - product_id: int
  - line_id: int

Response: 200 OK
{
  "period": "daily",
  "date": "2024-01-15",
  "defect_summary": [
    {
      "defect_type": "外観不良",
      "count": 50,
      "percentage": 40.0,
      "trend": "increasing"
    },
    {
      "defect_type": "寸法不良",
      "count": 30,
      "percentage": 24.0,
      "trend": "stable"
    }
  ],
  "total_defects": 125,
  "defect_rate": 2.5
}
```

### 3. 在庫管理API

#### 在庫操作
```python
# 在庫検索（QRコード対応）
GET /zaikokanriapi/items/search
Query Parameters:
  - qr_code: str
  - item_code: str
  - item_name: str
  - category_id: int

Response: 200 OK
{
  "items": [
    {
      "item_id": 1,
      "item_code": "ITM001",
      "item_name": "部品A",
      "current_stock": 150.0,
      "unit": "個",
      "location": "A-1-1",
      "qr_code": "QR123456",
      "status": "normal"
    }
  ]
}

# 在庫移動
POST /zaikokanriapi/transactions
Request Body:
{
  "item_id": 1,
  "transaction_type": "OUT",
  "quantity": 10,
  "reference_no": "WO2024001",
  "reference_type": "production",
  "note": "生産ライン1向け払出"
}

Response: 201 Created
{
  "transaction_id": 5000,
  "new_stock_level": 140.0,
  "timestamp": "2024-01-15T11:00:00Z"
}

# 在庫アラート
GET /zaikokanriapi/alerts

Response: 200 OK
{
  "alerts": [
    {
      "alert_type": "low_stock",
      "item": {
        "item_id": 5,
        "item_name": "部品E"
      },
      "current_stock": 20,
      "min_stock_level": 50,
      "severity": "high"
    },
    {
      "alert_type": "over_stock",
      "item": {
        "item_id": 10,
        "item_name": "部品J"
      },
      "current_stock": 1000,
      "max_stock_level": 800,
      "severity": "medium"
    }
  ],
  "total_alerts": 2
}
```

### 4. 認証API

#### 認証エンドポイント
```python
# ログイン
POST /auth/login
Request Body:
{
  "username": "user001",
  "password": "secure_password"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "employee_id": 100,
    "full_name": "山田太郎",
    "role": "production_manager"
  }
}

# トークンリフレッシュ
POST /auth/refresh
Headers:
  Authorization: Bearer {refresh_token}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

## 🔒 認証・認可

### JWT認証フロー
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user_id

# エンドポイントでの使用
@router.get("/protected-resource")
async def get_protected_resource(
    current_user: int = Depends(get_current_user)
):
    return {"user_id": current_user, "data": "protected data"}
```

## 📝 共通レスポンス形式

### 成功レスポンス
```json
{
  "status": "success",
  "data": {
    // リソースデータ
  },
  "metadata": {
    "timestamp": "2024-01-15T12:00:00Z",
    "version": "1.0"
  }
}
```

### エラーレスポンス
```json
{
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "指定されたリソースが見つかりません",
    "details": {
      "resource_id": 123
    }
  },
  "metadata": {
    "timestamp": "2024-01-15T12:00:00Z",
    "request_id": "req_123456"
  }
}
```

## 🚦 ステータスコード

| コード | 説明 | 使用場面 |
|--------|------|----------|
| 200 | OK | 正常な取得・更新 |
| 201 | Created | リソース作成成功 |
| 204 | No Content | 削除成功 |
| 400 | Bad Request | 不正なリクエスト |
| 401 | Unauthorized | 認証エラー |
| 403 | Forbidden | 認可エラー |
| 404 | Not Found | リソース不在 |
| 409 | Conflict | リソース競合 |
| 422 | Unprocessable Entity | バリデーションエラー |
| 500 | Internal Server Error | サーバーエラー |

## 🔄 データフォーマット

### 日時フォーマット
- ISO 8601形式（UTC）
- 例: `2024-01-15T12:00:00Z`

### ページネーション
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 500,
    "pages": 10
  }
}
```

### ソート・フィルタリング
```
GET /api/v1/resources?sort=created_at:desc,name:asc&filter[status]=active&filter[category]=production
```

## 📊 API仕様書

### OpenAPI/Swagger
- 自動生成される対話的ドキュメント
- アクセス: `http://localhost:9995/docs`
- ReDoc: `http://localhost:9995/redoc`

### 仕様書の自動生成
```python
from fastapi import FastAPI

app = FastAPI(
    title="製造業品質管理システムAPI",
    description="製造業向け統合管理システムのRESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)