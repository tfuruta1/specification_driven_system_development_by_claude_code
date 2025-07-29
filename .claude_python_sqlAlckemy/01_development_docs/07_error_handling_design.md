# エラーハンドリング設計書

## 🎯 エラーハンドリング方針

### 基本原則
1. **早期検出・早期対処**: バリデーションを入口で実施
2. **詳細なエラー情報**: デバッグ可能な情報を提供
3. **一貫性のあるレスポンス**: 統一されたエラー形式
4. **セキュリティ考慮**: 機密情報の非露出
5. **ログとの連携**: 追跡可能なエラー記録

## 🏗️ エラー階層構造

### カスタム例外クラス
```python
# core/exceptions.py
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    """API例外の基底クラス"""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    error_message: str = "内部エラーが発生しました"
    
    def __init__(
        self, 
        detail: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        detail = detail or self.error_message
        super().__init__(
            status_code=self.status_code,
            detail={
                "error_code": self.error_code,
                "message": detail,
                "details": kwargs
            },
            headers=headers
        )

# ビジネスロジック例外
class BusinessException(BaseAPIException):
    """ビジネスロジック例外の基底クラス"""
    status_code = status.HTTP_400_BAD_REQUEST

class ValidationException(BusinessException):
    """バリデーションエラー"""
    error_code = "VALIDATION_ERROR"
    error_message = "入力値が不正です"

class ResourceNotFoundException(BusinessException):
    """リソース未発見エラー"""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "RESOURCE_NOT_FOUND"
    error_message = "指定されたリソースが見つかりません"

class ResourceConflictException(BusinessException):
    """リソース競合エラー"""
    status_code = status.HTTP_409_CONFLICT
    error_code = "RESOURCE_CONFLICT"
    error_message = "リソースが競合しています"

class BusinessRuleViolationException(BusinessException):
    """ビジネスルール違反"""
    error_code = "BUSINESS_RULE_VIOLATION"
    error_message = "ビジネスルール違反です"

# システム例外
class SystemException(BaseAPIException):
    """システム例外の基底クラス"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

class DatabaseException(SystemException):
    """データベースエラー"""
    error_code = "DATABASE_ERROR"
    error_message = "データベースエラーが発生しました"

class ExternalServiceException(SystemException):
    """外部サービスエラー"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "EXTERNAL_SERVICE_ERROR"
    error_message = "外部サービスとの通信に失敗しました"

# 認証・認可例外
class SecurityException(BaseAPIException):
    """セキュリティ例外の基底クラス"""
    status_code = status.HTTP_401_UNAUTHORIZED

class AuthenticationException(SecurityException):
    """認証エラー"""
    error_code = "AUTHENTICATION_FAILED"
    error_message = "認証に失敗しました"

class AuthorizationException(SecurityException):
    """認可エラー"""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "AUTHORIZATION_FAILED"
    error_message = "アクセス権限がありません"

class TokenExpiredException(AuthenticationException):
    """トークン期限切れ"""
    error_code = "TOKEN_EXPIRED"
    error_message = "認証トークンの有効期限が切れています"
```

## 🔍 エラーハンドリング実装

### グローバルエラーハンドラー
```python
# middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """グローバル例外ハンドラー"""
    request_id = str(uuid.uuid4())
    
    # リクエスト情報をログ
    logger.error(
        f"Unhandled exception occurred",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc()
        }
    )
    
    # クライアントへのレスポンス
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "予期しないエラーが発生しました",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """バリデーションエラーハンドラー"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "入力値にエラーがあります",
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTPException ハンドラー"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

# アプリケーションへの登録
from fastapi import FastAPI

def register_exception_handlers(app: FastAPI):
    """例外ハンドラーの登録"""
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
```

### サービス層でのエラーハンドリング
```python
# services/production_service.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DatabaseError
from core.exceptions import (
    ResourceNotFoundException,
    ResourceConflictException,
    DatabaseException,
    BusinessRuleViolationException
)
import logging

logger = logging.getLogger(__name__)

class ProductionService:
    """生産管理サービス"""
    
    def start_production(
        self, 
        db: Session,
        work_order_no: str,
        line_id: int,
        worker_id: int
    ) -> ProductionResult:
        """生産開始処理"""
        try:
            # 作業指示の存在確認
            work_order = db.query(WorkOrder).filter_by(
                work_order_no=work_order_no
            ).first()
            
            if not work_order:
                raise ResourceNotFoundException(
                    f"作業指示番号 {work_order_no} が見つかりません",
                    work_order_no=work_order_no
                )
            
            # ビジネスルールチェック
            if work_order.status != "READY":
                raise BusinessRuleViolationException(
                    "この作業指示は開始できる状態ではありません",
                    current_status=work_order.status,
                    expected_status="READY"
                )
            
            # 生産ラインの利用可能性チェック
            if self._is_line_busy(db, line_id):
                raise ResourceConflictException(
                    f"生産ライン {line_id} は使用中です",
                    line_id=line_id
                )
            
            # 生産開始処理
            production_result = ProductionResult(
                work_order_no=work_order_no,
                line_id=line_id,
                worker_id=worker_id,
                start_time=datetime.utcnow(),
                status="IN_PROGRESS"
            )
            
            db.add(production_result)
            db.commit()
            db.refresh(production_result)
            
            logger.info(
                f"Production started successfully",
                extra={
                    "work_order_no": work_order_no,
                    "result_id": production_result.id
                }
            )
            
            return production_result
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error: {str(e)}")
            raise DatabaseException(
                "データの整合性エラーが発生しました",
                detail=str(e)
            )
        except DatabaseError as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise DatabaseException(
                "データベース操作中にエラーが発生しました"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error in start_production: {str(e)}")
            raise
```

## 📝 エラーレスポンス形式

### 標準エラーレスポンス
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "人間が読めるエラーメッセージ",
        "details": {
            "field": "詳細情報"
        },
        "request_id": "uuid-string",
        "timestamp": "2024-01-15T12:00:00Z"
    }
}
```

### バリデーションエラーレスポンス
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "入力値にエラーがあります",
        "errors": [
            {
                "field": "shipment_date",
                "message": "出荷日は今日以降の日付を指定してください",
                "type": "value_error"
            },
            {
                "field": "items.0.result",
                "message": "結果は OK, NG, NA のいずれかを指定してください",
                "type": "enum"
            }
        ],
        "timestamp": "2024-01-15T12:00:00Z"
    }
}
```

## 🔒 セキュリティ考慮事項

### エラー情報の制限
```python
# 本番環境では詳細なエラー情報を隠蔽
import os

def sanitize_error_message(error: Exception, is_production: bool) -> str:
    """エラーメッセージのサニタイズ"""
    if is_production:
        # 本番環境では一般的なメッセージ
        return "処理中にエラーが発生しました"
    else:
        # 開発環境では詳細情報
        return str(error)

IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"
```

### SQLインジェクション対策
```python
# 悪い例
query = f"SELECT * FROM products WHERE name = '{user_input}'"

# 良い例
query = db.query(Product).filter(Product.name == user_input)
```

## 📊 エラーモニタリング

### ロギング設定
```yaml
# logging_config.yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: '%(asctime)s %(name)s %(levelname)s %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout
  
  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: json
    filename: logs/error.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  app:
    level: INFO
    handlers: [console, error_file]
    propagate: false

root:
  level: INFO
  handlers: [console]
```

### メトリクス収集
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# エラーカウンター
error_counter = Counter(
    'api_errors_total',
    'Total number of API errors',
    ['error_code', 'endpoint', 'method']
)

# レスポンスタイム
response_time = Histogram(
    'api_response_time_seconds',
    'API response time in seconds',
    ['endpoint', 'method', 'status']
)

# 使用例
def track_error(error_code: str, endpoint: str, method: str):
    error_counter.labels(
        error_code=error_code,
        endpoint=endpoint,
        method=method
    ).inc()
```

## 🔄 リトライ戦略

### 外部サービス呼び出し
```python
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx

class ExternalService:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry_error_callback=lambda retry_state: logger.error(
            f"Retry failed after {retry_state.attempt_number} attempts"
        )
    )
    async def call_external_api(self, endpoint: str) -> dict:
        """外部API呼び出し（リトライ付き）"""
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint)
            response.raise_for_status()
            return response.json()
```

## ✅ エラーハンドリングチェックリスト

- [ ] すべての例外がキャッチされている
- [ ] 適切なHTTPステータスコードを返している
- [ ] エラーメッセージが一貫している
- [ ] 機密情報が露出していない
- [ ] エラーがログに記録されている
- [ ] リトライ可能なエラーにリトライ機構がある
- [ ] エラーメトリクスが収集されている