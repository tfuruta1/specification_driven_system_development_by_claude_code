# FastAPI設計パターン

## 🚀 FastAPI基本パターン

### アプリケーション初期化
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # 起動時処理
    logger.info("Starting up...")
    # データベース接続プールの初期化
    # キャッシュの初期化
    # 外部サービスとの接続確立
    yield
    # 終了時処理
    logger.info("Shutting down...")
    # リソースのクリーンアップ
    # 接続のクローズ

# アプリケーションインスタンス作成
app = FastAPI(
    title="製造業品質管理システムAPI",
    description="FastAPI + SQLAlchemy による統合管理システム",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:9997"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📋 ルーター設計パターン

### モジュラールーター構成
```python
# routers/__init__.py
from fastapi import APIRouter
from .shipment import router as shipment_router
from .production import router as production_router
from .inventory import router as inventory_router
from .auth import router as auth_router

# APIバージョニング
api_v1 = APIRouter(prefix="/api/v1")

# サブルーターの登録
api_v1.include_router(
    shipment_router,
    prefix="/shipment",
    tags=["shipment"]
)
api_v1.include_router(
    production_router,
    prefix="/production",
    tags=["production"]
)
api_v1.include_router(
    inventory_router,
    prefix="/inventory",
    tags=["inventory"]
)
api_v1.include_router(
    auth_router,
    prefix="/auth",
    tags=["authentication"]
)
```

### ルーターの実装パターン
```python
# routers/production.py
from fastapi import APIRouter, Depends, Query, Path, Body
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()

# パスパラメータとクエリパラメータ
@router.get("/results/{result_id}")
async def get_production_result(
    result_id: int = Path(
        ...,
        gt=0,
        description="生産実績ID",
        example=1234
    ),
    include_details: bool = Query(
        False,
        description="詳細情報を含めるか"
    )
):
    """生産実績取得"""
    pass

# リスト取得with フィルタリング
@router.get("/results")
async def list_production_results(
    skip: int = Query(0, ge=0, description="スキップ数"),
    limit: int = Query(50, ge=1, le=100, description="取得件数"),
    date_from: Optional[date] = Query(None, description="開始日"),
    date_to: Optional[date] = Query(None, description="終了日"),
    line_id: Optional[int] = Query(None, description="ライン番号"),
    status: Optional[str] = Query(None, regex="^(READY|IN_PROGRESS|COMPLETED)$")
):
    """生産実績一覧取得"""
    pass

# POSTリクエストwith バリデーション
@router.post("/results", status_code=201)
async def create_production_result(
    data: ProductionResultCreate = Body(
        ...,
        example={
            "work_order_no": "WO-2024-001",
            "product_id": 100,
            "line_id": 1,
            "planned_quantity": 1000
        }
    )
):
    """生産実績作成"""
    pass

# バッチ処理エンドポイント
@router.post("/results/batch")
async def batch_create_results(
    data: List[ProductionResultCreate] = Body(
        ...,
        min_items=1,
        max_items=100
    )
):
    """生産実績一括作成"""
    pass
```

## 🔐 認証・認可パターン

### JWT認証実装
```python
# auth/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# パスワードハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# セキュリティスキーム
security = HTTPBearer()

class AuthService:
    """認証サービス"""
    
    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """パスワード検証"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """パスワードハッシュ化"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """アクセストークン生成"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode,
            AuthService.SECRET_KEY,
            algorithm=AuthService.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """トークンデコード"""
        try:
            payload = jwt.decode(
                token,
                AuthService.SECRET_KEY,
                algorithms=[AuthService.ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

# 認証依存性
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """現在のユーザー取得"""
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

# ロールベース認可
def require_roles(*roles: str):
    """ロール要求デコレータ"""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
```

## 🔄 非同期処理パターン

### バックグラウンドタスク
```python
from fastapi import BackgroundTasks
import asyncio

async def send_notification_email(email: str, message: str):
    """メール送信処理（非同期）"""
    await asyncio.sleep(1)  # メール送信のシミュレーション
    print(f"Email sent to {email}: {message}")

@router.post("/production/complete/{result_id}")
async def complete_production(
    result_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """生産完了処理"""
    # 生産完了処理
    result = complete_production_process(result_id)
    
    # バックグラウンドで通知送信
    background_tasks.add_task(
        send_notification_email,
        current_user.email,
        f"生産 {result.work_order_no} が完了しました"
    )
    
    return {"message": "Production completed", "result_id": result_id}

# 非同期バッチ処理
async def process_batch_async(items: List[dict]):
    """非同期バッチ処理"""
    tasks = []
    for item in items:
        task = asyncio.create_task(process_single_item(item))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]
    
    return {
        "successful": len(successful),
        "failed": len(failed),
        "results": successful,
        "errors": [str(e) for e in failed]
    }
```

## 📄 レスポンスモデルパターン

### 統一レスポンス形式
```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')

class ResponseBase(BaseModel, Generic[T]):
    """基本レスポンスモデル"""
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(ResponseBase[T]):
    """ページネーションレスポンス"""
    total: int
    page: int
    limit: int
    pages: int

class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    error: ErrorDetail
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

# 使用例
@router.get(
    "/products",
    response_model=PaginatedResponse[List[ProductResponse]]
)
async def list_products(
    page: int = 1,
    limit: int = 50
):
    """製品一覧取得"""
    products, total = get_products_with_count(page, limit)
    
    return PaginatedResponse(
        data=products,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )
```

## 🎯 ミドルウェアパターン

### カスタムミドルウェア
```python
from fastapi import Request, Response
from time import time
import uuid

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """処理時間計測ミドルウェア"""
    start_time = time()
    request_id = str(uuid.uuid4())
    
    # リクエストIDをコンテキストに追加
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    return response

# ロギングミドルウェア
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """リクエストロギング"""
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }
    )
    
    response = await call_next(request)
    
    logger.info(
        f"Response: {response.status_code}",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "status_code": response.status_code
        }
    )
    
    return response
```

## 🔧 依存性注入パターン

### 階層的な依存性
```python
# 設定の依存性
def get_settings() -> Settings:
    """アプリケーション設定取得"""
    return Settings()

# データベースセッションの依存性
def get_db(settings: Settings = Depends(get_settings)) -> Generator:
    """データベースセッション取得"""
    db = SessionLocal(settings.database_url)
    try:
        yield db
    finally:
        db.close()

# リポジトリの依存性
def get_product_repository(
    db: Session = Depends(get_db)
) -> ProductRepository:
    """製品リポジトリ取得"""
    return ProductRepository(db)

# サービスの依存性
def get_production_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    db: Session = Depends(get_db)
) -> ProductionService:
    """生産サービス取得"""
    return ProductionService(db, product_repo)

# エンドポイントでの使用
@router.post("/production/start")
async def start_production(
    request: ProductionStartRequest,
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user)
):
    """生産開始"""
    return service.start_production(request, current_user)
```