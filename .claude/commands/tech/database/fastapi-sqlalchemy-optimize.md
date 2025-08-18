# /fastapi-sqlalchemy-optimize - エンタープライズバックエンド最適化

## 概要
FastAPI + SQLAlchemy + PostgreSQLエンタープライズバックエンドシステムの包括的最適化コマンドです。**システム開発部主導**で部門協調による高性能化・規制対応・統合化を実現します。

## 🎯 部門別責任分担

### システム開発部（実装責任）
- FastAPI最適化・非同期処理改善
- SQLAlchemy ORM最適化・クエリチューニング
- データベースパフォーマンス実装
- API設計・エンドポイント最適化

### 品質保証部（検証責任）
- パフォーマンステスト・負荷テスト
- データ整合性検証・トランザクション検証
- セキュリティテスト・脆弱性検査
- 品質メトリクス監視・回帰テスト

### 経営企画部（戦略責任）
- データベースアーキテクチャ戦略
- 監視・可観測性戦略
- スケーラビリティ設計
- ROI効果測定・パフォーマンス分析

### 人事部（運用責任）
- 運用手順・マニュアル作成
- トレーニング・技術継承
- コンプライアンス管理
- 障害対応・運用監視

## 🚀 基本使用法

```bash
# 部門協調による包括的最適化（推奨）
/fastapi-sqlalchemy-optimize comprehensive

# システム開発部: API・ORM最適化
/fastapi-sqlalchemy-optimize performance --focus="fastapi,sqlalchemy,async"

# 品質保証部: 品質・テスト最適化
/fastapi-sqlalchemy-optimize quality --focus="testing,security,validation"

# 経営企画部: アーキテクチャ・戦略最適化
/fastapi-sqlalchemy-optimize strategy --focus="architecture,monitoring,scaling"
```

## 📋 最適化カテゴリー

### 1. FastAPI最適化（システム開発部）

#### 非同期処理最適化
```python
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List, Optional
import uvloop

# 高性能非同期ループ設定
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# アプリケーション起動最適化
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時処理
    await initialize_database_pool()
    await setup_redis_connection()
    await start_background_services()
    
    yield
    
    # 終了時処理
    await cleanup_database_pool()
    await close_redis_connection()

app = FastAPI(
    title="Enterprise API",
    version="2.0.0",
    lifespan=lifespan
)

# ミドルウェア最適化
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 接続プール最適化
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # PgBouncer使用時
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 高速バルク操作API
@app.post("/api/bulk-operations/")
async def bulk_create_items(
    items: List[ItemCreate],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # バルク挿入最適化
    items_data = [item.dict() for item in items]
    
    # 大量データは分割処理
    if len(items_data) > 1000:
        background_tasks.add_task(process_bulk_items, items_data)
        return {"status": "accepted", "message": "Bulk processing started"}
    
    # 小量データは即座に処理
    result = await db.execute(
        insert(Item).values(items_data)
    )
    await db.commit()
    
    return {"status": "completed", "inserted": len(items_data)}

# キャッシュ統合
from functools import lru_cache
import redis.asyncio as redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True,
    max_connections=20
)

@lru_cache(maxsize=128)
def get_settings():
    return Settings()

async def cached_query(cache_key: str, query_func, ttl: int = 300):
    # Redis キャッシュ確認
    cached_result = await redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    
    # キャッシュ未命中時はDBクエリ実行
    result = await query_func()
    
    # 結果をキャッシュに保存
    await redis_client.setex(
        cache_key, 
        ttl, 
        json.dumps(result, default=str)
    )
    
    return result
```

#### レスポンス最適化
```python
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
import orjson

# 高速JSON レスポンス
class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return orjson.dumps(content, default=str)

app = FastAPI(default_response_class=ORJSONResponse)

# ストリーミングレスポンス
@app.get("/api/large-dataset/")
async def stream_large_dataset(db: AsyncSession = Depends(get_db)):
    async def generate():
        async with db.stream(select(LargeTable)) as result:
            async for row in result:
                yield orjson.dumps(row._asdict()) + b'\n'
    
    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )

# ページネーション最適化
@app.get("/api/items/")
async def get_items(
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * size
    
    # カウントクエリとデータクエリを並列実行
    count_task = asyncio.create_task(
        db.scalar(select(func.count(Item.id)))
    )
    items_task = asyncio.create_task(
        db.execute(
            select(Item)
            .offset(offset)
            .limit(size)
            .options(selectinload(Item.related_data))
        )
    )
    
    total, items_result = await asyncio.gather(count_task, items_task)
    items = items_result.scalars().all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": (total + size - 1) // size
    }
```

### 2. SQLAlchemy ORM最適化（システム開発部）

#### 効率的モデル設計
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, selectinload, joinedload
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

Base = declarative_base()

class OptimizedItem(Base):
    __tablename__ = "items"
    
    # 最適化されたプライマリキー
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), index=True)
    
    # JSON フィールド最適化
    metadata = Column(JSONB, nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 最適化されたリレーションシップ
    category = relationship(
        "Category", 
        back_populates="items",
        lazy="select"
    )
    
    # 複合インデックス
    __table_args__ = (
        Index('ix_items_category_created', 'category_id', 'created_at'),
        Index('ix_items_name_category', 'name', 'category_id'),
    )

# リポジトリパターン実装
class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def find_with_optimized_loading(
        self, 
        category_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[OptimizedItem]:
        query = select(OptimizedItem)
        
        if category_id:
            query = query.where(OptimizedItem.category_id == category_id)
        
        # 最適化されたeager loading
        query = query.options(
            selectinload(OptimizedItem.category)
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def bulk_update_optimized(
        self, 
        updates: List[dict]
    ) -> int:
        # バルク更新最適化
        if not updates:
            return 0
        
        stmt = update(OptimizedItem).where(
            OptimizedItem.id == bindparam('item_id')
        ).values(
            name=bindparam('name'),
            updated_at=func.now()
        )
        
        await self.db.execute(stmt, updates)
        await self.db.commit()
        
        return len(updates)
```

#### クエリ最適化
```python
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import aliased

class OptimizedQueryService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def complex_analytics_query(
        self, 
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        # サブクエリ最適化
        subquery = select(
            OptimizedItem.category_id,
            func.count(OptimizedItem.id).label('item_count'),
            func.sum(
                case(
                    (OptimizedItem.metadata['price'].astext.cast(Integer) > 100, 1),
                    else_=0
                )
            ).label('expensive_items')
        ).where(
            and_(
                OptimizedItem.created_at >= start_date,
                OptimizedItem.created_at <= end_date
            )
        ).group_by(OptimizedItem.category_id).subquery()
        
        # メインクエリ（JOIN最適化）
        query = select(
            Category.name.label('category_name'),
            subquery.c.item_count,
            subquery.c.expensive_items,
            func.round(
                (subquery.c.expensive_items.cast(float) / subquery.c.item_count * 100), 2
            ).label('expensive_percentage')
        ).select_from(
            Category.__table__.join(
                subquery, 
                Category.id == subquery.c.category_id
            )
        ).order_by(subquery.c.item_count.desc())
        
        result = await self.db.execute(query)
        return [dict(row) for row in result]
    
    async def optimized_search(
        self, 
        search_term: str,
        filters: dict = None
    ) -> List[OptimizedItem]:
        # フルテキスト検索最適化
        query = select(OptimizedItem)
        
        if search_term:
            # PostgreSQL フルテキスト検索
            query = query.where(
                or_(
                    OptimizedItem.name.ilike(f'%{search_term}%'),
                    OptimizedItem.metadata['description'].astext.ilike(f'%{search_term}%')
                )
            )
        
        # 動的フィルタ適用
        if filters:
            for key, value in filters.items():
                if hasattr(OptimizedItem, key):
                    query = query.where(getattr(OptimizedItem, key) == value)
        
        # インデックス活用の確認
        result = await self.db.execute(query)
        return result.scalars().all()
```

### 3. データベース最適化（経営企画部）

#### 接続プール・監視設定
```python
from sqlalchemy.pool import QueuePool
import logging

# 本番環境用エンジン設定
production_engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
    echo=False,
    echo_pool=True,  # 開発時のみ
    future=True
)

# 監視とロギング
logging.basicConfig(level=logging.INFO)
db_logger = logging.getLogger('sqlalchemy.engine')

# パフォーマンス監視
class DatabaseMonitor:
    def __init__(self):
        self.query_times = []
        self.slow_queries = []
    
    async def log_query_performance(self, query: str, duration: float):
        self.query_times.append(duration)
        
        if duration > 1.0:  # 1秒以上のクエリ
            self.slow_queries.append({
                'query': query,
                'duration': duration,
                'timestamp': datetime.now()
            })
    
    def get_performance_stats(self) -> dict:
        if not self.query_times:
            return {}
        
        return {
            'avg_query_time': sum(self.query_times) / len(self.query_times),
            'max_query_time': max(self.query_times),
            'slow_queries_count': len(self.slow_queries),
            'total_queries': len(self.query_times)
        }
```

## 📊 パフォーマンスメトリクス

### 目標指標
- **API応答時間**: 平均100ms以下
- **データベースクエリ**: 平均50ms以下
- **スループット**: 1000 req/sec以上
- **メモリ使用量**: 最適化により50%削減

### 監視指標
- **接続プール使用率**: 80%以下
- **スロークエリ率**: 5%以下
- **エラー率**: 1%以下
- **可用性**: 99.9%以上

## 🔧 実装手順

### Phase 1: 現状分析（品質保証部主導）
```bash
# パフォーマンス分析
/analyze performance --scope="fastapi,sqlalchemy,database"

# ボトルネック特定
/analyze bottleneck --focus="api_endpoints,db_queries,connection_pool"
```

### Phase 2: 最適化実装（システム開発部主導）
```bash
# FastAPI最適化
/enhance fastapi --focus="async,middleware,response_optimization"

# SQLAlchemy最適化
/enhance sqlalchemy --focus="orm,queries,relationships"

# データベース最適化
/enhance database --focus="indexes,connection_pool,caching"
```

### Phase 3: インフラ最適化（経営企画部主導）
```bash
# アーキテクチャ設計
/architecture backend --focus="scalability,monitoring,high_availability"

# 監視・可観測性
/devops monitoring --focus="performance_metrics,alerting,logging"
```

### Phase 4: 品質保証（品質保証部主導）
```bash
# パフォーマンステスト
/test performance --scope="load,stress,endurance"

# セキュリティテスト
/test security --focus="api_security,data_protection"
```

## 🎯 継続改善

### 自動化監視
- APM統合（New Relic、DataDog等）
- データベース監視・最適化提案
- 自動スケーリング・負荷分散

### 定期最適化
- 月次: パフォーマンス分析・改善
- 四半期: アーキテクチャ見直し
- 年次: 技術スタック評価・更新

---

**🎯 目標**: FastAPI + SQLAlchemyエンタープライズバックエンドで、最高のパフォーマンスと信頼性を部門協調により実現する。