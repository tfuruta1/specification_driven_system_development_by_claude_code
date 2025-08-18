# /sqlalchemy-optimize - SQLAlchemy エンタープライズ最適化専用コマンド

## 概要
FastAPI + SQLAlchemy を使用したエンタープライズシステムの包括的なデータベース最適化コマンドです。エンタープライズ特有の要求（コンプライアンス、監査、大規模データ処理）に完全対応します。

## 使用方法
```bash
/sqlalchemy-optimize [optimization_type] [options]

# 使用例
/sqlalchemy-optimize performance --ai-collaboration
/sqlalchemy-optimize enterprise-transactions --with-audit
/sqlalchemy-optimize n-plus-one --auto-fix
/sqlalchemy-optimize connection-pool --monitor
/sqlalchemy-optimize async-patterns --convert
```

## 最適化タイプ

### 1. パフォーマンス最適化
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload, joinedload, subqueryload
from sqlalchemy.pool import NullPool, QueuePool, StaticPool

class SQLAlchemyOptimizer:
    def __init__(self, database_url: str):
        # エンタープライズ向け接続プール設定
        self.engine = create_async_engine(
            database_url,
            pool_size=20,           # 基本プールサイズ
            max_overflow=40,        # 最大オーバーフロー
            pool_timeout=30,        # タイムアウト
            pool_recycle=3600,      # 接続リサイクル
            pool_pre_ping=True,     # 接続ヘルスチェック
            echo_pool=True,         # プールログ出力
            connect_args={
                "server_settings": {
                    "application_name": "enterprise_app",
                    "jit": "off"
                },
                "command_timeout": 60,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5
            }
        )
```

### 2. N+1問題の自動検出と修正
```python
class NPlusOneOptimizer:
    def detect_n_plus_one(self, query):
        """N+1問題を検出"""
        # クエリログ分析
        query_patterns = self.analyze_query_logs()
        
        # 疑わしいパターンの検出
        suspicious_patterns = []
        for pattern in query_patterns:
            if pattern['count'] > 10 and pattern['similarity'] > 0.9:
                suspicious_patterns.append({
                    'query': pattern['query'],
                    'count': pattern['count'],
                    'recommendation': self.generate_fix(pattern)
                })
        
        return suspicious_patterns
    
    def auto_fix_n_plus_one(self, model_class):
        """N+1問題を自動修正"""
        # リレーションシップの分析
        relationships = inspect(model_class).relationships
        
        # 最適なローディング戦略の選択
        for rel in relationships:
            if rel.collection:
                # コレクションの場合
                if self.estimate_size(rel) < 100:
                    # 小規模: selectinload
                    rel.lazy = 'selectin'
                else:
                    # 大規模: subqueryload
                    rel.lazy = 'subquery'
            else:
                # 単一オブジェクトの場合
                rel.lazy = 'joined'
        
        return model_class
```

### 3. エンタープライズトランザクション管理
```python
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

class EnterpriseTransactionManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.retry_policy = {
            'max_retries': 3,
            'backoff_factor': 2,
            'max_backoff': 60
        }
    
    @asynccontextmanager
    async def distributed_transaction(self, isolation_level='REPEATABLE READ'):
        """分散トランザクション管理"""
        async with self.session_factory() as session:
            await session.execute(
                text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
            )
            
            try:
                yield session
                await session.commit()
                
                # 監査ログ記録
                await self.audit_log(session, 'COMMIT')
                
            except Exception as e:
                await session.rollback()
                await self.audit_log(session, 'ROLLBACK', str(e))
                
                # リトライ可能なエラーか判定
                if self.is_retryable(e):
                    raise RetryableError(e)
                raise
    
    async def saga_transaction(self, operations):
        """SAGAパターンによる分散トランザクション"""
        completed = []
        
        try:
            for operation in operations:
                result = await operation['execute']()
                completed.append({
                    'operation': operation,
                    'result': result
                })
                
        except Exception as e:
            # 補償トランザクション実行
            for completed_op in reversed(completed):
                await completed_op['operation']['compensate'](
                    completed_op['result']
                )
            raise
```

### 4. 監査とコンプライアンス
```python
class AuditMixin:
    """監査機能Mixin"""
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime)  # 論理削除
    
    # 監査証跡
    audit_trail = Column(JSON, default=list)
    
    # 電子署名
    digital_signature = Column(String(500))
    
    # データ系譜
    data_lineage = Column(JSON)
    
    @validates('*')
    def validate_and_audit(self, key, value):
        """全フィールドの変更を監査"""
        if hasattr(self, '_original_values'):
            old_value = self._original_values.get(key)
            if old_value != value:
                self.audit_trail.append({
                    'field': key,
                    'old_value': str(old_value),
                    'new_value': str(value),
                    'changed_at': datetime.utcnow().isoformat(),
                    'changed_by': self.get_current_user_id()
                })
        return value
```

### 5. パーティショニングとシャーディング
```python
class PartitioningStrategy:
    """テーブルパーティショニング戦略"""
    
    @staticmethod
    def create_range_partitions(table_name, partition_column, interval='MONTH'):
        """範囲パーティション作成"""
        sql = f"""
        CREATE TABLE {table_name}_y{{year}}_m{{month}} 
        PARTITION OF {table_name}
        FOR VALUES FROM ('{year}-{month:02d}-01') 
        TO ('{year}-{month:02d}-01'::date + INTERVAL '1 {interval}')
        """
        
        # 過去12ヶ月分のパーティション作成
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            partition_sql = sql.format(
                year=date.year,
                month=date.month
            )
            session.execute(text(partition_sql))
    
    @staticmethod
    def create_hash_sharding(table_name, shard_count=10):
        """ハッシュベースシャーディング"""
        for i in range(shard_count):
            shard_table = f"{table_name}_shard_{i}"
            # シャードテーブル作成
            create_shard_table(shard_table)
            
            # シャーディングルール設定
            add_shard_rule(
                lambda record: hash(record.id) % shard_count == i,
                shard_table
            )
```

### 6. 高度なキャッシング戦略
```python
from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer

class CachingStrategy:
    def __init__(self):
        self.cache = Cache(
            Cache.REDIS,
            endpoint="localhost",
            port=6379,
            serializer=JsonSerializer(),
            namespace="sqlalchemy"
        )
    
    @cached(ttl=300, key_builder=lambda *args, **kwargs: f"query:{args[1]}")
    async def cached_query(self, session, query_key):
        """クエリ結果のキャッシング"""
        result = await session.execute(query_key)
        return result.scalars().all()
    
    async def invalidate_cache(self, pattern):
        """キャッシュ無効化"""
        keys = await self.cache.raw("keys", f"{pattern}*")
        if keys:
            await self.cache.raw("del", *keys)
    
    def cache_warming(self, queries):
        """キャッシュウォーミング"""
        async def warm():
            async with AsyncSession(self.engine) as session:
                for query in queries:
                    await self.cached_query(session, query)
        
        asyncio.create_task(warm())
```

## マルチAI協調分析

### Gemini CLI連携
```python
async def analyze_with_gemini(database_metrics):
    """Gemini CLIによるパフォーマンス分析"""
    analysis_request = {
        "query_patterns": database_metrics['slow_queries'],
        "index_usage": database_metrics['index_stats'],
        "lock_contention": database_metrics['lock_analysis'],
        "cache_hit_ratio": database_metrics['cache_stats']
    }
    
    # Gemini分析実行
    recommendations = await gemini_analyze(analysis_request)
    
    return {
        'optimization_suggestions': recommendations['optimizations'],
        'index_recommendations': recommendations['indexes'],
        'query_rewrites': recommendations['queries']
    }
```

## 出力レポート
```markdown
# SQLAlchemy最適化レポート

## パフォーマンス改善
- クエリ実行時間: 250ms → 45ms (82%改善)
- N+1問題: 23件検出 → 0件 (100%解決)
- 接続プール効率: 45% → 92%
- キャッシュヒット率: 35% → 85%

## エンタープライズ機能
✅ 監査ログ: 全トランザクション記録
✅ コンプライアンス: SOX/GDPR準拠
✅ 暗号化: フィールドレベル暗号化実装
✅ パーティション: 月次パーティション設定

## 推奨事項
1. インデックス追加: 5件
2. クエリ書き換え: 12件
3. パーティション追加: 3テーブル
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: SQLAlchemy + エンタープライズ要件

---
*このコマンドはSQLAlchemyのエンタープライズ最適化に特化しています。*