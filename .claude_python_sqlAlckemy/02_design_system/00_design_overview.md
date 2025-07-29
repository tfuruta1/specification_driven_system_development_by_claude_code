# デザインシステム概要

## 🎨 FastAPI + SQLAlchemy デザインパターン

### 設計思想
本プロジェクトでは、Clean Architecture の原則に基づき、ビジネスロジックとインフラストラクチャを明確に分離した設計を採用しています。

## 📁 パッケージ構造

```
api_module/
├── __init__.py
├── main.py              # FastAPIルーター定義
├── dependencies.py      # 依存性注入
├── models.py           # SQLAlchemyモデル（Domain Layer）
├── schemas.py          # Pydanticスキーマ（Interface Layer）
├── crud.py            # データアクセス層（Infrastructure Layer）
├── service.py         # ビジネスロジック層（Application Layer）
├── exceptions.py      # カスタム例外
└── utils.py           # ユーティリティ関数
```

## 🏗️ アーキテクチャパターン

### 1. Repository Pattern
```python
# crud.py - リポジトリパターンの実装
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

class BaseRepository:
    """基底リポジトリクラス"""
    model = None
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, id: int) -> Optional[model]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[model]:
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj_in: dict) -> model:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj_in: dict) -> Optional[model]:
        db_obj = self.get(id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

class ProductRepository(BaseRepository):
    """製品リポジトリ"""
    model = Product
    
    def get_by_code(self, product_code: str) -> Optional[Product]:
        return self.db.query(Product).filter(
            Product.product_code == product_code
        ).first()
    
    def search(
        self, 
        keyword: Optional[str] = None,
        product_type: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> List[Product]:
        query = self.db.query(Product)
        
        if keyword:
            query = query.filter(
                or_(
                    Product.product_name.contains(keyword),
                    Product.product_code.contains(keyword)
                )
            )
        
        if product_type:
            query = query.filter(Product.product_type == product_type)
        
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        return query.all()
```

### 2. Service Layer Pattern
```python
# service.py - サービス層の実装
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from .crud import ProductRepository, ProductionResultRepository
from .schemas import ProductionResultCreate, ProductionSummary
from .exceptions import BusinessRuleViolationException

class ProductionService:
    """生産管理サービス"""
    
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.production_repo = ProductionResultRepository(db)
    
    def start_production(
        self,
        work_order_no: str,
        product_id: int,
        line_id: int,
        worker_id: int,
        planned_quantity: int
    ) -> ProductionResult:
        """生産開始処理"""
        # ビジネスルールの検証
        product = self.product_repo.get(product_id)
        if not product or not product.is_active:
            raise BusinessRuleViolationException(
                "無効な製品が指定されています"
            )
        
        # 既存の生産チェック
        existing = self.production_repo.get_active_by_line(line_id)
        if existing:
            raise BusinessRuleViolationException(
                f"ライン {line_id} は既に使用中です"
            )
        
        # 生産実績の作成
        production_data = {
            "work_order_no": work_order_no,
            "product_id": product_id,
            "line_id": line_id,
            "worker_id": worker_id,
            "planned_quantity": planned_quantity,
            "actual_quantity": 0,
            "defect_quantity": 0,
            "start_time": datetime.utcnow(),
            "status": "IN_PROGRESS"
        }
        
        return self.production_repo.create(production_data)
    
    def get_daily_summary(self, target_date: date) -> ProductionSummary:
        """日次生産サマリー取得"""
        results = self.production_repo.get_by_date(target_date)
        
        total_planned = sum(r.planned_quantity for r in results)
        total_actual = sum(r.actual_quantity for r in results)
        total_defect = sum(r.defect_quantity for r in results)
        
        efficiency = (total_actual / total_planned * 100) if total_planned > 0 else 0
        
        return ProductionSummary(
            date=target_date,
            total_planned=total_planned,
            total_actual=total_actual,
            total_defect=total_defect,
            efficiency=efficiency,
            production_count=len(results)
        )
```

### 3. Dependency Injection Pattern
```python
# dependencies.py - 依存性注入の実装
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .database import SessionLocal
from .models import User
from .config import settings

# データベースセッション
def get_db() -> Generator[Session, None, None]:
    """データベースセッション取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 認証
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """現在のユーザー取得"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
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
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

# 権限チェック
def require_role(required_role: str):
    """ロール要求デコレータ"""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role.name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# サービス取得
def get_production_service(
    db: Session = Depends(get_db)
) -> ProductionService:
    """生産サービス取得"""
    return ProductionService(db)
```

### 4. Router Pattern
```python
# main.py - ルーター実装
from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional
from datetime import date
from .dependencies import get_db, get_current_user, get_production_service
from .schemas import (
    ProductionResultResponse,
    ProductionResultCreate,
    ProductionSummaryResponse
)
from .service import ProductionService

router = APIRouter(
    prefix="/production",
    tags=["production"]
)

@router.post(
    "/start",
    response_model=ProductionResultResponse,
    summary="生産開始",
    description="新しい生産を開始します"
)
async def start_production(
    request: ProductionResultCreate,
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user)
):
    """生産開始エンドポイント"""
    result = service.start_production(
        work_order_no=request.work_order_no,
        product_id=request.product_id,
        line_id=request.line_id,
        worker_id=current_user.id,
        planned_quantity=request.planned_quantity
    )
    return result

@router.get(
    "/summary/daily",
    response_model=ProductionSummaryResponse,
    summary="日次サマリー取得"
)
async def get_daily_summary(
    target_date: date = Query(..., description="対象日付"),
    service: ProductionService = Depends(get_production_service),
    _: User = Depends(get_current_user)
):
    """日次生産サマリー取得"""
    return service.get_daily_summary(target_date)

@router.get(
    "/results/{result_id}",
    response_model=ProductionResultResponse,
    summary="生産実績詳細取得"
)
async def get_production_result(
    result_id: int = Path(..., gt=0, description="生産実績ID"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """生産実績詳細取得"""
    repo = ProductionResultRepository(db)
    result = repo.get(result_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production result not found"
        )
    
    return result
```

## 🔄 データフロー設計

### Request → Response フロー
```
1. Client Request
   ↓
2. FastAPI Router (Validation via Pydantic)
   ↓
3. Dependencies (Auth, DB Session)
   ↓
4. Service Layer (Business Logic)
   ↓
5. Repository Layer (Data Access)
   ↓
6. SQLAlchemy ORM (Database)
   ↓
7. Response Serialization (Pydantic)
   ↓
8. Client Response
```

## 📐 設計原則

### SOLID原則の適用
1. **単一責任の原則（SRP）**
   - 各クラスは単一の責任を持つ
   - サービス層はビジネスロジックのみ
   - リポジトリ層はデータアクセスのみ

2. **オープン・クローズドの原則（OCP）**
   - 拡張に対して開いている
   - 修正に対して閉じている
   - 基底クラスとインターフェースの活用

3. **リスコフの置換原則（LSP）**
   - 派生クラスは基底クラスと置換可能
   - 一貫したインターフェース設計

4. **インターフェース分離の原則（ISP）**
   - 小さく特化したインターフェース
   - 不要な依存の排除

5. **依存性逆転の原則（DIP）**
   - 高レベルモジュールは低レベルに依存しない
   - 抽象に依存する設計

## 🎯 ベストプラクティス

### 1. 型安全性
- すべての関数に型ヒントを付与
- Pydanticによる実行時検証
- mypyによる静的型チェック

### 2. エラーハンドリング
- ドメイン固有の例外定義
- 一貫したエラーレスポンス
- 詳細なログ記録

### 3. テスタビリティ
- 依存性注入による疎結合
- モックしやすい設計
- 単体テストの容易性

### 4. パフォーマンス
- N+1問題の回避
- 適切なインデックス設計
- 非同期処理の活用