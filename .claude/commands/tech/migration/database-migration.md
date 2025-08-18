# /database-migration - データベース移行エンタープライズ専用コマンド

## 概要
異なるデータベース間の大規模データ移行に特化した包括的な移行コマンドです。ゼロダウンタイム移行、スキーマ自動変換、CDC（Change Data Capture）、インクリメンタル同期を完全サポートします。

## 使用方法
```bash
/database-migration [action] [options]

# 使用例
/database-migration analyze --source=sqlserver --target=postgresql
/database-migration migrate --zero-downtime --cdc --parallel=16
/database-migration sync --incremental --real-time
/database-migration validate --checksum --row-count
/database-migration rollback --point-in-time="2024-01-15 10:00:00"
```

## データベース移行専用機能

### 1. ゼロダウンタイム移行エンジン
```python
# migration/zero_downtime_migrator.py
import asyncio
import asyncpg
import pyodbc
import pymysql
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class MigrationConfig:
    source_type: str  # sqlserver, mysql, oracle, postgresql
    target_type: str
    source_connection: Dict[str, Any]
    target_connection: Dict[str, Any]
    batch_size: int = 10000
    parallel_workers: int = 16
    use_cdc: bool = True
    sync_mode: str = 'full'  # full, incremental, real-time

class ZeroDowntimeMigrator:
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.source_conn = None
        self.target_conn = None
        self.migration_state = {
            'phase': 'initial',
            'progress': 0,
            'start_time': None,
            'checkpoints': []
        }
        
    async def execute_migration(self):
        """ゼロダウンタイム移行の実行"""
        
        try:
            # Phase 1: 初期スナップショット
            await self._phase1_initial_snapshot()
            
            # Phase 2: CDC セットアップ
            await self._phase2_setup_cdc()
            
            # Phase 3: 初期データコピー
            await self._phase3_bulk_copy()
            
            # Phase 4: 増分同期
            await self._phase4_incremental_sync()
            
            # Phase 5: 最終同期とカットオーバー
            await self._phase5_cutover()
            
            # Phase 6: 検証
            await self._phase6_validation()
            
        except Exception as e:
            await self._handle_migration_error(e)
            raise
    
    async def _phase1_initial_snapshot(self):
        """初期スナップショット作成"""
        self.migration_state['phase'] = 'snapshot'
        self.migration_state['start_time'] = datetime.now()
        
        # トランザクション分離レベル設定
        if self.config.source_type == 'sqlserver':
            await self._setup_sqlserver_snapshot()
        elif self.config.source_type == 'postgresql':
            await self._setup_postgresql_snapshot()
        elif self.config.source_type == 'mysql':
            await self._setup_mysql_snapshot()
        
        # スナップショット情報記録
        self.migration_state['checkpoints'].append({
            'type': 'snapshot',
            'timestamp': datetime.now(),
            'lsn': await self._get_current_lsn()
        })
    
    async def _phase2_setup_cdc(self):
        """Change Data Capture設定"""
        if not self.config.use_cdc:
            return
        
        self.migration_state['phase'] = 'cdc_setup'
        
        if self.config.source_type == 'sqlserver':
            await self._setup_sqlserver_cdc()
        elif self.config.source_type == 'postgresql':
            await self._setup_postgresql_logical_replication()
        elif self.config.source_type == 'mysql':
            await self._setup_mysql_binlog()
    
    async def _setup_sqlserver_cdc(self):
        """SQL Server CDC設定"""
        cdc_sql = """
        -- データベースレベルでCDC有効化
        EXEC sys.sp_cdc_enable_db;
        
        -- 各テーブルでCDC有効化
        DECLARE @tables TABLE (schema_name NVARCHAR(128), table_name NVARCHAR(128));
        INSERT INTO @tables
        SELECT SCHEMA_NAME(schema_id), name 
        FROM sys.tables 
        WHERE is_ms_shipped = 0;
        
        DECLARE @schema NVARCHAR(128), @table NVARCHAR(128);
        DECLARE table_cursor CURSOR FOR SELECT * FROM @tables;
        
        OPEN table_cursor;
        FETCH NEXT FROM table_cursor INTO @schema, @table;
        
        WHILE @@FETCH_STATUS = 0
        BEGIN
            EXEC sys.sp_cdc_enable_table
                @source_schema = @schema,
                @source_name = @table,
                @role_name = NULL,
                @supports_net_changes = 1;
            
            FETCH NEXT FROM table_cursor INTO @schema, @table;
        END
        
        CLOSE table_cursor;
        DEALLOCATE table_cursor;
        """
        
        async with self.source_conn.cursor() as cursor:
            await cursor.execute(cdc_sql)
    
    async def _phase3_bulk_copy(self):
        """並列バルクコピー"""
        self.migration_state['phase'] = 'bulk_copy'
        
        # テーブルリスト取得
        tables = await self._get_table_list()
        
        # 並列処理用のキュー作成
        table_queue = asyncio.Queue()
        for table in tables:
            await table_queue.put(table)
        
        # ワーカータスク起動
        workers = []
        for i in range(self.config.parallel_workers):
            worker = asyncio.create_task(
                self._bulk_copy_worker(table_queue, i)
            )
            workers.append(worker)
        
        # 完了待機
        await table_queue.join()
        
        # ワーカー停止
        for worker in workers:
            worker.cancel()
    
    async def _bulk_copy_worker(self, queue: asyncio.Queue, worker_id: int):
        """バルクコピーワーカー"""
        while True:
            try:
                table = await queue.get()
                await self._copy_table_data(table, worker_id)
                queue.task_done()
                
                # 進捗更新
                self.migration_state['progress'] += 1
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                queue.task_done()
    
    async def _copy_table_data(self, table: Dict, worker_id: int):
        """テーブルデータコピー"""
        
        # 分割キー決定
        partition_key = await self._determine_partition_key(table)
        
        if partition_key:
            # パーティション並列コピー
            await self._parallel_partition_copy(table, partition_key)
        else:
            # 通常のバッチコピー
            await self._batch_copy(table)
    
    async def _parallel_partition_copy(self, table: Dict, partition_key: str):
        """パーティション並列コピー"""
        
        # パーティション範囲取得
        min_val, max_val = await self._get_partition_range(table, partition_key)
        
        # 範囲分割
        partitions = self._calculate_partitions(min_val, max_val, self.config.parallel_workers)
        
        # 並列コピー
        tasks = []
        for start, end in partitions:
            task = asyncio.create_task(
                self._copy_partition(table, partition_key, start, end)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def _phase4_incremental_sync(self):
        """増分同期"""
        if not self.config.use_cdc:
            return
        
        self.migration_state['phase'] = 'incremental_sync'
        
        # CDC変更の取得と適用
        last_lsn = self.migration_state['checkpoints'][-1]['lsn']
        
        while not self._is_cutover_ready():
            changes = await self._get_cdc_changes(last_lsn)
            
            if changes:
                await self._apply_changes(changes)
                last_lsn = changes[-1]['lsn']
                
                # チェックポイント記録
                self.migration_state['checkpoints'].append({
                    'type': 'incremental',
                    'timestamp': datetime.now(),
                    'lsn': last_lsn
                })
            
            await asyncio.sleep(1)  # ポーリング間隔

# スキーマ変換エンジン
class SchemaConverter:
    """異種DB間のスキーマ自動変換"""
    
    def __init__(self, source_type: str, target_type: str):
        self.source_type = source_type
        self.target_type = target_type
        self.type_mappings = self._load_type_mappings()
        
    def _load_type_mappings(self) -> Dict:
        """データ型マッピング定義"""
        
        # SQL Server → PostgreSQL
        if self.source_type == 'sqlserver' and self.target_type == 'postgresql':
            return {
                'bigint': 'bigint',
                'int': 'integer',
                'smallint': 'smallint',
                'tinyint': 'smallint',
                'bit': 'boolean',
                'decimal': 'decimal',
                'numeric': 'numeric',
                'money': 'money',
                'float': 'double precision',
                'real': 'real',
                'datetime': 'timestamp',
                'datetime2': 'timestamp',
                'date': 'date',
                'time': 'time',
                'char': 'char',
                'varchar': 'varchar',
                'nvarchar': 'varchar',
                'text': 'text',
                'ntext': 'text',
                'binary': 'bytea',
                'varbinary': 'bytea',
                'uniqueidentifier': 'uuid',
                'xml': 'xml',
                'json': 'jsonb'
            }
        
        # MySQL → PostgreSQL
        elif self.source_type == 'mysql' and self.target_type == 'postgresql':
            return {
                'tinyint': 'smallint',
                'smallint': 'smallint',
                'mediumint': 'integer',
                'int': 'integer',
                'bigint': 'bigint',
                'float': 'real',
                'double': 'double precision',
                'decimal': 'decimal',
                'date': 'date',
                'datetime': 'timestamp',
                'timestamp': 'timestamp',
                'time': 'time',
                'year': 'smallint',
                'char': 'char',
                'varchar': 'varchar',
                'tinytext': 'text',
                'text': 'text',
                'mediumtext': 'text',
                'longtext': 'text',
                'blob': 'bytea',
                'mediumblob': 'bytea',
                'longblob': 'bytea',
                'enum': 'varchar',
                'set': 'varchar[]',
                'json': 'jsonb'
            }
        
        return {}
    
    async def convert_schema(self, source_schema: Dict) -> str:
        """スキーマ変換実行"""
        
        target_ddl = []
        
        for table in source_schema['tables']:
            # テーブル作成文生成
            create_table = await self._convert_table(table)
            target_ddl.append(create_table)
            
            # インデックス変換
            for index in table.get('indexes', []):
                create_index = await self._convert_index(index, table['name'])
                target_ddl.append(create_index)
            
            # 制約変換
            for constraint in table.get('constraints', []):
                alter_table = await self._convert_constraint(constraint, table['name'])
                target_ddl.append(alter_table)
        
        # ビュー変換
        for view in source_schema.get('views', []):
            create_view = await self._convert_view(view)
            target_ddl.append(create_view)
        
        # ストアドプロシージャ変換（可能な場合）
        for proc in source_schema.get('procedures', []):
            create_function = await self._convert_procedure(proc)
            if create_function:
                target_ddl.append(create_function)
        
        return '\n\n'.join(target_ddl)
    
    async def _convert_table(self, table: Dict) -> str:
        """テーブル定義変換"""
        
        columns = []
        for col in table['columns']:
            # データ型変換
            source_type = col['data_type'].lower()
            target_type = self.type_mappings.get(source_type, source_type)
            
            # 列定義生成
            col_def = f"{col['name']} {target_type}"
            
            # サイズ指定
            if col.get('length'):
                col_def += f"({col['length']})"
            elif col.get('precision') and col.get('scale'):
                col_def += f"({col['precision']}, {col['scale']})"
            
            # NULL制約
            if not col.get('nullable', True):
                col_def += " NOT NULL"
            
            # デフォルト値
            if col.get('default'):
                default_val = self._convert_default_value(col['default'])
                col_def += f" DEFAULT {default_val}"
            
            columns.append(col_def)
        
        # PRIMARY KEY
        if table.get('primary_key'):
            pk_cols = ', '.join(table['primary_key']['columns'])
            columns.append(f"PRIMARY KEY ({pk_cols})")
        
        # CREATE TABLE文生成
        return f"""CREATE TABLE {table['name']} (
    {',\n    '.join(columns)}
);"""
```

### 2. リアルタイム同期とCDC
```python
# sync/realtime_sync.py
import asyncio
from typing import Dict, Any, List
import aiokafka
from debezium import DebeziumConnector

class RealtimeDatabaseSync:
    """リアルタイムデータベース同期"""
    
    def __init__(self, source_config: Dict, target_config: Dict):
        self.source_config = source_config
        self.target_config = target_config
        self.cdc_connector = None
        self.kafka_consumer = None
        self.sync_metrics = {
            'events_processed': 0,
            'lag_ms': 0,
            'errors': 0
        }
        
    async def start_sync(self):
        """リアルタイム同期開始"""
        
        # Debezium CDC コネクター設定
        await self._setup_debezium()
        
        # Kafka コンシューマー設定
        await self._setup_kafka_consumer()
        
        # 同期ループ開始
        await self._sync_loop()
    
    async def _setup_debezium(self):
        """Debezium設定"""
        
        config = {
            "name": "db-sync-connector",
            "config": {
                "connector.class": self._get_connector_class(),
                "database.hostname": self.source_config['host'],
                "database.port": self.source_config['port'],
                "database.user": self.source_config['user'],
                "database.password": self.source_config['password'],
                "database.dbname": self.source_config['database'],
                "database.server.name": "dbserver1",
                "table.include.list": "public.*",
                "plugin.name": "pgoutput",  # PostgreSQL の場合
                "slot.name": "debezium",
                "publication.name": "dbz_publication",
                "snapshot.mode": "initial",
                "heartbeat.interval.ms": "1000",
                "poll.interval.ms": "100"
            }
        }
        
        self.cdc_connector = DebeziumConnector(config)
        await self.cdc_connector.start()
    
    async def _setup_kafka_consumer(self):
        """Kafka コンシューマー設定"""
        
        self.kafka_consumer = aiokafka.AIOKafkaConsumer(
            'dbserver1.*',  # すべてのテーブルのトピック
            bootstrap_servers='localhost:9092',
            group_id='db-sync-group',
            enable_auto_commit=False,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        await self.kafka_consumer.start()
    
    async def _sync_loop(self):
        """同期ループ"""
        
        batch = []
        batch_size = 1000
        batch_timeout = 1.0  # 秒
        last_batch_time = asyncio.get_event_loop().time()
        
        async for msg in self.kafka_consumer:
            try:
                # CDCイベント処理
                event = msg.value
                
                # イベントタイプ判定
                if event['op'] == 'c':  # CREATE
                    operation = self._prepare_insert(event)
                elif event['op'] == 'u':  # UPDATE
                    operation = self._prepare_update(event)
                elif event['op'] == 'd':  # DELETE
                    operation = self._prepare_delete(event)
                else:
                    continue
                
                batch.append(operation)
                
                # バッチ実行判定
                current_time = asyncio.get_event_loop().time()
                if len(batch) >= batch_size or \
                   (current_time - last_batch_time) >= batch_timeout:
                    
                    await self._execute_batch(batch)
                    await self.kafka_consumer.commit()
                    
                    batch = []
                    last_batch_time = current_time
                
                # メトリクス更新
                self.sync_metrics['events_processed'] += 1
                self.sync_metrics['lag_ms'] = msg.timestamp - current_time * 1000
                
            except Exception as e:
                self.sync_metrics['errors'] += 1
                await self._handle_sync_error(e, msg)
    
    def _prepare_insert(self, event: Dict) -> Dict:
        """INSERT操作準備"""
        return {
            'type': 'insert',
            'table': event['source']['table'],
            'data': event['after']
        }
    
    def _prepare_update(self, event: Dict) -> Dict:
        """UPDATE操作準備"""
        return {
            'type': 'update',
            'table': event['source']['table'],
            'key': self._extract_key(event),
            'data': event['after']
        }
    
    def _prepare_delete(self, event: Dict) -> Dict:
        """DELETE操作準備"""
        return {
            'type': 'delete',
            'table': event['source']['table'],
            'key': self._extract_key(event)
        }
    
    async def _execute_batch(self, batch: List[Dict]):
        """バッチ実行"""
        
        # トランザクション開始
        async with self.target_conn.transaction():
            for operation in batch:
                if operation['type'] == 'insert':
                    await self._execute_insert(operation)
                elif operation['type'] == 'update':
                    await self._execute_update(operation)
                elif operation['type'] == 'delete':
                    await self._execute_delete(operation)

# 高度な検証エンジン
class MigrationValidator:
    """移行データ検証"""
    
    def __init__(self, source_conn, target_conn):
        self.source_conn = source_conn
        self.target_conn = target_conn
        self.validation_results = {
            'row_counts': {},
            'checksums': {},
            'schema_diffs': [],
            'data_samples': {}
        }
        
    async def validate_migration(self) -> Dict:
        """包括的移行検証"""
        
        # 1. 行数検証
        await self._validate_row_counts()
        
        # 2. チェックサム検証
        await self._validate_checksums()
        
        # 3. スキーマ検証
        await self._validate_schema()
        
        # 4. データサンプリング検証
        await self._validate_data_samples()
        
        # 5. 制約検証
        await self._validate_constraints()
        
        # 6. パフォーマンス検証
        await self._validate_performance()
        
        return self.validation_results
    
    async def _validate_row_counts(self):
        """行数検証"""
        
        tables = await self._get_table_list()
        
        for table in tables:
            source_count = await self._get_row_count(self.source_conn, table)
            target_count = await self._get_row_count(self.target_conn, table)
            
            self.validation_results['row_counts'][table] = {
                'source': source_count,
                'target': target_count,
                'match': source_count == target_count,
                'diff': abs(source_count - target_count)
            }
    
    async def _validate_checksums(self):
        """チェックサム検証"""
        
        tables = await self._get_table_list()
        
        for table in tables:
            # 各列のチェックサム計算
            source_checksum = await self._calculate_checksum(self.source_conn, table)
            target_checksum = await self._calculate_checksum(self.target_conn, table)
            
            self.validation_results['checksums'][table] = {
                'source': source_checksum,
                'target': target_checksum,
                'match': source_checksum == target_checksum
            }
    
    async def _calculate_checksum(self, conn, table: str) -> str:
        """テーブルチェックサム計算"""
        
        # MD5ハッシュ使用（データベース依存）
        if self._get_db_type(conn) == 'postgresql':
            query = f"""
            SELECT MD5(CAST((array_agg(t.* ORDER BY t.*)) AS text))
            FROM {table} t
            """
        elif self._get_db_type(conn) == 'mysql':
            query = f"CHECKSUM TABLE {table}"
        elif self._get_db_type(conn) == 'sqlserver':
            query = f"""
            SELECT CHECKSUM_AGG(BINARY_CHECKSUM(*)) 
            FROM {table}
            """
        
        result = await conn.fetchone(query)
        return str(result[0]) if result else 'NULL'
```

### 3. インテリジェントロールバック
```python
# rollback/intelligent_rollback.py
class IntelligentRollback:
    """インテリジェント移行ロールバック"""
    
    def __init__(self, migration_context: Dict):
        self.context = migration_context
        self.rollback_points = []
        self.rollback_strategy = None
        
    async def create_rollback_point(self, name: str):
        """ロールバックポイント作成"""
        
        point = {
            'name': name,
            'timestamp': datetime.now(),
            'database_snapshot': await self._create_snapshot(),
            'migration_state': dict(self.context['state']),
            'cdc_position': await self._get_cdc_position()
        }
        
        self.rollback_points.append(point)
        
        # ディスクに永続化
        await self._persist_rollback_point(point)
    
    async def rollback_to_point(self, point_name: str):
        """指定ポイントへのロールバック"""
        
        # ロールバックポイント検索
        point = next((p for p in self.rollback_points if p['name'] == point_name), None)
        
        if not point:
            raise ValueError(f"Rollback point '{point_name}' not found")
        
        # ロールバック戦略決定
        self.rollback_strategy = self._determine_strategy(point)
        
        # ロールバック実行
        if self.rollback_strategy == 'snapshot':
            await self._rollback_via_snapshot(point)
        elif self.rollback_strategy == 'reverse_cdc':
            await self._rollback_via_reverse_cdc(point)
        elif self.rollback_strategy == 'compensating':
            await self._rollback_via_compensating_transactions(point)
    
    async def _rollback_via_reverse_cdc(self, point: Dict):
        """CDC逆適用によるロールバック"""
        
        # CDC履歴取得
        cdc_history = await self._get_cdc_history_since(point['cdc_position'])
        
        # 逆順で適用
        for event in reversed(cdc_history):
            if event['op'] == 'c':  # CREATE → DELETE
                await self._execute_delete(event)
            elif event['op'] == 'u':  # UPDATE → 元に戻す
                await self._execute_update_reverse(event)
            elif event['op'] == 'd':  # DELETE → INSERT
                await self._execute_insert(event['before'])
```

## 出力レポート
```markdown
# データベース移行レポート

## 移行概要
✅ ソース: SQL Server 2019 (500GB)
✅ ターゲット: PostgreSQL 14
✅ 移行方式: ゼロダウンタイム（CDC）
✅ 総移行時間: 4時間23分
✅ ダウンタイム: 0秒

## 移行結果
- テーブル数: 256
- 総レコード数: 8.5億
- スキーマ変換: 100%成功
- データ整合性: 100%一致

## パフォーマンス
- 平均転送速度: 1.9GB/分
- 並列度: 16
- CDC遅延: <100ms
- メモリ使用量: 最大8GB

## 検証結果
- 行数一致: 256/256テーブル
- チェックサム一致: 256/256テーブル
- 制約検証: すべて成功
- インデックス: 最適化済み
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: エンタープライズデータベース移行

---
*このコマンドはエンタープライズデータベース移行に特化しています。*