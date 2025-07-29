# SQLAlchemy設計パターン

## 🗄️ SQLAlchemy基本設定

### データベース接続設定
```python
# core/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
import os
from typing import Generator

# 接続文字列構築
def get_database_url() -> str:
    """データベースURL取得"""
    if os.getenv("ENVIRONMENT") == "test":
        return "sqlite:///./test.db"
    
    return (
        f"mssql+pyodbc://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_SERVER')}/"
        f"{os.getenv('DB_NAME')}?"
        f"driver={os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')}"
    )

# エンジン作成
engine = create_engine(
    get_database_url(),
    # コネクションプール設定
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,  # 1時間でコネクション再生成
    pool_pre_ping=True,  # 接続前にpingでチェック
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    # SQL Server固有の設定
    connect_args={
        "connect_timeout": 30,
        "application_name": "FastAPI App",
        "autocommit": False
    }
)

# イベントリスナー：接続時の設定
@event.listens_for(engine, "connect")
def set_sql_mode(dbapi_connection, connection_record):
    """SQL Server接続時の設定"""
    cursor = dbapi_connection.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.execute("SET NOCOUNT ON")
    cursor.close()

# セッションファクトリ
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # コミット後もオブジェクトを使用可能に
)

# ベースクラス
Base = declarative_base()

# 依存性注入用
def get_db() -> Generator[Session, None, None]:
    """データベースセッション取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 📊 モデル設計パターン

### ベースモデルとMixin
```python
# models/base.py
from sqlalchemy import Column, Integer, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

class TimestampMixin:
    """タイムスタンプMixin"""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class SoftDeleteMixin:
    """論理削除Mixin"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        """論理削除実行"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

class BaseModel(Base, TimestampMixin):
    """共通ベースモデル"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    @declared_attr
    def __tablename__(cls):
        """テーブル名自動生成"""
        return cls.__name__.lower() + 's'
    
    def to_dict(self):
        """辞書変換"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
```

### リレーションシップパターン
```python
# models/relationships.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from .base import BaseModel

# 多対多の中間テーブル
product_category_association = Table(
    'product_categories',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('category_id', Integer, ForeignKey('categories.id')),
    UniqueConstraint('product_id', 'category_id')
)

class Product(BaseModel):
    """製品モデル"""
    __tablename__ = 'products'
    
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    
    # 多対多リレーション
    categories = relationship(
        'Category',
        secondary=product_category_association,
        back_populates='products',
        lazy='selectin'  # 自動的にJOIN
    )
    
    # 一対多リレーション
    production_results = relationship(
        'ProductionResult',
        back_populates='product',
        cascade='all, delete-orphan',  # 親削除時に子も削除
        lazy='dynamic'  # クエリオブジェクトとして取得
    )
    
    # 一対一リレーション
    specification = relationship(
        'ProductSpecification',
        back_populates='product',
        uselist=False,  # 単一オブジェクト
        cascade='all, delete-orphan'
    )

class ProductionResult(BaseModel):
    """生産実績モデル"""
    __tablename__ = 'production_results'
    
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # 逆参照
    product = relationship(
        'Product',
        back_populates='production_results'
    )
    
    # 自己参照（階層構造）
    parent_id = Column(Integer, ForeignKey('production_results.id'))
    children = relationship(
        'ProductionResult',
        backref=backref('parent', remote_side='ProductionResult.id')
    )
```

## 🔍 クエリパターン

### 高度なクエリテクニック
```python
# repositories/advanced_queries.py
from sqlalchemy import and_, or_, func, case, text
from sqlalchemy.orm import Session, joinedload, selectinload, contains_eager
from sqlalchemy.sql import label
from typing import List, Optional, Tuple
from datetime import datetime, date

class ProductionRepository:
    """生産リポジトリ"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_with_relations(self, product_id: int) -> Optional[Product]:
        """関連データを含めて取得（N+1問題回避）"""
        return self.db.query(Product)\
            .options(
                joinedload(Product.categories),
                selectinload(Product.production_results)
            )\
            .filter(Product.id == product_id)\
            .first()
    
    def get_production_summary(self, start_date: date, end_date: date) -> List[dict]:
        """生産サマリー取得（集計クエリ）"""
        summary = self.db.query(
            Product.product_name,
            func.sum(ProductionResult.actual_quantity).label('total_quantity'),
            func.avg(ProductionResult.efficiency).label('avg_efficiency'),
            func.count(ProductionResult.id).label('production_count')
        )\
        .join(ProductionResult)\
        .filter(
            and_(
                ProductionResult.start_time >= start_date,
                ProductionResult.start_time <= end_date
            )
        )\
        .group_by(Product.product_name)\
        .having(func.sum(ProductionResult.actual_quantity) > 0)\
        .order_by(func.sum(ProductionResult.actual_quantity).desc())\
        .all()
        
        return [
            {
                'product_name': row.product_name,
                'total_quantity': row.total_quantity,
                'avg_efficiency': float(row.avg_efficiency or 0),
                'production_count': row.production_count
            }
            for row in summary
        ]
    
    def search_products_with_rank(self, keyword: str) -> List[Tuple[Product, float]]:
        """全文検索with ランキング"""
        # SQL Server全文検索
        search_query = self.db.query(
            Product,
            func.freetexttable(
                Product.__tablename__,
                'product_name',
                keyword
            ).label('rank')
        )\
        .filter(
            text(f"CONTAINS(product_name, :keyword)")
        )\
        .params(keyword=f'"{keyword}*"')\
        .order_by(text('rank DESC'))
        
        return search_query.all()
    
    def get_defect_analysis(self, product_id: int) -> dict:
        """不良分析（CASE文使用）"""
        analysis = self.db.query(
            func.sum(
                case(
                    (DefectRecord.defect_type == 'appearance', DefectRecord.quantity),
                    else_=0
                )
            ).label('appearance_defects'),
            func.sum(
                case(
                    (DefectRecord.defect_type == 'dimension', DefectRecord.quantity),
                    else_=0
                )
            ).label('dimension_defects'),
            func.sum(DefectRecord.quantity).label('total_defects')
        )\
        .join(ProductionResult)\
        .filter(ProductionResult.product_id == product_id)\
        .first()
        
        return {
            'appearance_defects': analysis.appearance_defects or 0,
            'dimension_defects': analysis.dimension_defects or 0,
            'total_defects': analysis.total_defects or 0
        }
```

### バルク操作パターン
```python
# repositories/bulk_operations.py
from sqlalchemy import bindparam
from sqlalchemy.dialects.mssql import insert
from typing import List, Dict

class BulkRepository:
    """バルク操作リポジトリ"""
    
    def bulk_insert_products(self, products: List[Dict]) -> int:
        """製品一括挿入"""
        stmt = insert(Product).values(products)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount
    
    def bulk_update_stock(self, updates: List[Dict]) -> int:
        """在庫一括更新"""
        stmt = Product.__table__.update()\
            .where(Product.id == bindparam('_id'))\
            .values(current_stock=bindparam('stock'))
        
        result = self.db.execute(
            stmt,
            [
                {'_id': item['id'], 'stock': item['stock']}
                for item in updates
            ]
        )
        self.db.commit()
        return result.rowcount
    
    def bulk_upsert(self, items: List[Dict]) -> None:
        """UPSERT操作（SQL Server MERGE）"""
        # SQL ServerのMERGE文を使用
        merge_sql = text("""
            MERGE products AS target
            USING (VALUES :values) AS source (product_code, product_name, price)
            ON target.product_code = source.product_code
            WHEN MATCHED THEN
                UPDATE SET 
                    product_name = source.product_name,
                    price = source.price,
                    updated_at = GETDATE()
            WHEN NOT MATCHED THEN
                INSERT (product_code, product_name, price)
                VALUES (source.product_code, source.product_name, source.price);
        """)
        
        self.db.execute(merge_sql, {'values': items})
        self.db.commit()
```

## 🔄 トランザクション管理

### トランザクションパターン
```python
# services/transaction_patterns.py
from contextlib import contextmanager
from sqlalchemy.orm import Session
from functools import wraps
import logging

logger = logging.getLogger(__name__)

@contextmanager
def transaction_scope(db: Session):
    """トランザクションスコープ管理"""
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction rollback: {str(e)}")
        raise
    finally:
        db.close()

def transactional(func):
    """トランザクショナルデコレータ"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with transaction_scope(self.db) as session:
            return func(self, *args, **kwargs)
    return wrapper

class InventoryService:
    """在庫サービス"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @transactional
    def transfer_stock(
        self,
        from_location: int,
        to_location: int,
        item_id: int,
        quantity: float
    ) -> None:
        """在庫移動（トランザクション保証）"""
        # 移動元の在庫確認・減算
        from_stock = self.db.query(Stock)\
            .filter_by(location_id=from_location, item_id=item_id)\
            .with_for_update()\
            .first()
        
        if not from_stock or from_stock.quantity < quantity:
            raise ValueError("在庫が不足しています")
        
        from_stock.quantity -= quantity
        
        # 移動先の在庫加算
        to_stock = self.db.query(Stock)\
            .filter_by(location_id=to_location, item_id=item_id)\
            .with_for_update()\
            .first()
        
        if to_stock:
            to_stock.quantity += quantity
        else:
            to_stock = Stock(
                location_id=to_location,
                item_id=item_id,
                quantity=quantity
            )
            self.db.add(to_stock)
        
        # 移動履歴記録
        transfer = StockTransfer(
            from_location_id=from_location,
            to_location_id=to_location,
            item_id=item_id,
            quantity=quantity
        )
        self.db.add(transfer)
        
        # @transactionalデコレータによって自動的にコミット
```

## 🎯 パフォーマンス最適化

### インデックス戦略
```python
# models/indexes.py
from sqlalchemy import Index, text

class ProductionResult(BaseModel):
    """生産実績モデル（インデックス付き）"""
    __tablename__ = 'production_results'
    
    work_order_no = Column(String(50), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)
    
    # 複合インデックス
    __table_args__ = (
        Index('idx_production_date_product', 'start_time', 'product_id'),
        Index('idx_work_order_status', 'work_order_no', 'status'),
        # 部分インデックス（SQL Server filtered index）
        Index(
            'idx_active_production',
            'product_id',
            'start_time',
            mssql_where=text("status = 'IN_PROGRESS'")
        ),
    )
```

### 遅延読み込みとイーガーローディング
```python
# repositories/loading_strategies.py
from sqlalchemy.orm import lazyload, joinedload, selectinload, subqueryload

class OptimizedRepository:
    """最適化されたリポジトリ"""
    
    def get_orders_with_details(self, order_ids: List[int]) -> List[Order]:
        """注文と詳細を効率的に取得"""
        # selectinload: 別クエリでIN句を使用（推奨）
        return self.db.query(Order)\
            .options(
                selectinload(Order.items)\
                    .selectinload(OrderItem.product)
            )\
            .filter(Order.id.in_(order_ids))\
            .all()
    
    def get_product_hierarchy(self, root_id: int) -> Product:
        """階層構造の取得"""
        # 再帰的な読み込み
        return self.db.query(Product)\
            .options(
                selectinload(Product.children, recursion_depth=3)
            )\
            .filter(Product.id == root_id)\
            .first()
```