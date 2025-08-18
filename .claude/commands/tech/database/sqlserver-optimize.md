# /sqlserver-optimize - SQL Server エンタープライズ最適化専用コマンド

## 概要
Microsoft SQL Server のエンタープライズ環境に特化した包括的な最適化コマンドです。Always On、インメモリOLTP、列ストア、パーティショニングなどの高度な機能を活用します。

## 使用方法
```bash
/sqlserver-optimize [feature] [action] [options]

# 使用例
/sqlserver-optimize query analyze --execution-plan
/sqlserver-optimize index missing --auto-create
/sqlserver-optimize alwayson configure --availability-group
/sqlserver-optimize inmemory enable --tables=hot_tables
/sqlserver-optimize columnstore create --fact-tables
```

## SQL Server 専用最適化機能

### 1. クエリストア分析と自動チューニング
```sql
-- クエリストア有効化
ALTER DATABASE [EnterpriseDB] 
SET QUERY_STORE = ON (
    OPERATION_MODE = READ_WRITE,
    CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30),
    DATA_FLUSH_INTERVAL_SECONDS = 900,
    MAX_STORAGE_SIZE_MB = 1000,
    INTERVAL_LENGTH_MINUTES = 60,
    SIZE_BASED_CLEANUP_MODE = AUTO,
    QUERY_CAPTURE_MODE = AUTO,
    MAX_PLANS_PER_QUERY = 200
);

-- 自動チューニング有効化
ALTER DATABASE [EnterpriseDB] 
SET AUTOMATIC_TUNING (FORCE_LAST_GOOD_PLAN = ON);

-- 遅いクエリの特定
WITH SlowQueries AS (
    SELECT 
        q.query_id,
        qt.query_text_id,
        qt.query_sql_text,
        SUM(rs.count_executions) AS total_executions,
        AVG(rs.avg_duration) AS avg_duration_us,
        AVG(rs.avg_cpu_time) AS avg_cpu_time_us,
        AVG(rs.avg_logical_io_reads) AS avg_logical_reads,
        MAX(rs.max_duration) AS max_duration_us
    FROM sys.query_store_query q
    JOIN sys.query_store_query_text qt ON q.query_text_id = qt.query_text_id
    JOIN sys.query_store_plan p ON q.query_id = p.query_id
    JOIN sys.query_store_runtime_stats rs ON p.plan_id = rs.plan_id
    WHERE rs.last_execution_time > DATEADD(day, -7, GETUTCDATE())
    GROUP BY q.query_id, qt.query_text_id, qt.query_sql_text
)
SELECT TOP 20
    query_sql_text,
    total_executions,
    avg_duration_us / 1000 AS avg_duration_ms,
    avg_cpu_time_us / 1000 AS avg_cpu_ms,
    avg_logical_reads,
    max_duration_us / 1000 AS max_duration_ms,
    avg_duration_us * total_executions AS total_impact
FROM SlowQueries
ORDER BY total_impact DESC;
```

### 2. インメモリOLTP最適化
```sql
-- メモリ最適化ファイルグループ追加
ALTER DATABASE [EnterpriseDB] 
ADD FILEGROUP [MemoryOptimized] CONTAINS MEMORY_OPTIMIZED_DATA;

ALTER DATABASE [EnterpriseDB] 
ADD FILE (
    NAME = 'MemoryOptimizedData',
    FILENAME = 'C:\Data\EnterpriseDB_MemOpt.ndf'
) TO FILEGROUP [MemoryOptimized];

-- ホットテーブルのインメモリ化
CREATE TABLE dbo.HotTransactions (
    TransactionID BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY NONCLUSTERED,
    CustomerID INT NOT NULL INDEX IX_CustomerID NONCLUSTERED,
    Amount DECIMAL(19,4) NOT NULL,
    TransactionDate DATETIME2 NOT NULL,
    Status TINYINT NOT NULL,
    
    INDEX IX_TransactionDate NONCLUSTERED (TransactionDate)
) WITH (
    MEMORY_OPTIMIZED = ON,
    DURABILITY = SCHEMA_AND_DATA
);

-- ネイティブコンパイルストアドプロシージャ
CREATE PROCEDURE dbo.ProcessTransaction
    @CustomerID INT,
    @Amount DECIMAL(19,4)
WITH NATIVE_COMPILATION, SCHEMABINDING
AS BEGIN ATOMIC WITH (
    TRANSACTION ISOLATION LEVEL = SNAPSHOT,
    LANGUAGE = N'Japanese'
)
    INSERT INTO dbo.HotTransactions (CustomerID, Amount, TransactionDate, Status)
    VALUES (@CustomerID, @Amount, SYSDATETIME(), 1);
END;
```

### 3. 列ストアインデックス最適化
```sql
-- クラスター化列ストアインデックス作成
CREATE CLUSTERED COLUMNSTORE INDEX CCI_FactSales
ON dbo.FactSales
WITH (DROP_EXISTING = OFF, COMPRESSION_DELAY = 0);

-- 非クラスター化列ストア（リアルタイム分析用）
CREATE NONCLUSTERED COLUMNSTORE INDEX NCCI_Orders
ON dbo.Orders (
    OrderID,
    CustomerID,
    OrderDate,
    TotalAmount,
    Status
) WHERE OrderDate >= '2024-01-01';

-- 列ストア保守
ALTER INDEX CCI_FactSales ON dbo.FactSales
REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON);

-- デルタストア分析
SELECT 
    OBJECT_NAME(object_id) AS TableName,
    index_id,
    partition_number,
    state_desc,
    total_rows,
    deleted_rows,
    size_in_bytes / 1024.0 / 1024.0 AS size_mb
FROM sys.dm_db_column_store_row_group_physical_stats
WHERE state_desc = 'OPEN'
ORDER BY total_rows DESC;
```

### 4. Always On 可用性グループ最適化
```sql
-- 可用性グループ作成
CREATE AVAILABILITY GROUP [AG_Enterprise]
WITH (
    AUTOMATED_BACKUP_PREFERENCE = SECONDARY,
    FAILURE_CONDITION_LEVEL = 3,
    HEALTH_CHECK_TIMEOUT = 30000,
    DB_FAILOVER = ON,
    DTC_SUPPORT = PER_DB
)
FOR DATABASE [EnterpriseDB]
REPLICA ON 
    N'SQL-Primary' WITH (
        ENDPOINT_URL = N'TCP://SQL-Primary.domain.com:5022',
        AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
        FAILOVER_MODE = AUTOMATIC,
        BACKUP_PRIORITY = 50,
        SEEDING_MODE = AUTOMATIC,
        PRIMARY_ROLE(ALLOW_CONNECTIONS = ALL)
    ),
    N'SQL-Secondary' WITH (
        ENDPOINT_URL = N'TCP://SQL-Secondary.domain.com:5022',
        AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
        FAILOVER_MODE = AUTOMATIC,
        BACKUP_PRIORITY = 50,
        SEEDING_MODE = AUTOMATIC,
        SECONDARY_ROLE(ALLOW_CONNECTIONS = READ_ONLY)
    );

-- 読み取り専用ルーティング設定
ALTER AVAILABILITY GROUP [AG_Enterprise]
MODIFY REPLICA ON N'SQL-Primary'
WITH (PRIMARY_ROLE (READ_ONLY_ROUTING_LIST = ('SQL-Secondary', 'SQL-Primary')));
```

### 5. パーティション関数と自動管理
```sql
-- パーティション関数作成
CREATE PARTITION FUNCTION PF_Monthly (DATETIME2)
AS RANGE RIGHT FOR VALUES (
    '2024-01-01', '2024-02-01', '2024-03-01',
    '2024-04-01', '2024-05-01', '2024-06-01',
    '2024-07-01', '2024-08-01', '2024-09-01',
    '2024-10-01', '2024-11-01', '2024-12-01'
);

-- パーティションスキーム作成
CREATE PARTITION SCHEME PS_Monthly
AS PARTITION PF_Monthly
TO ([FG_2024_01], [FG_2024_02], [FG_2024_03],
    [FG_2024_04], [FG_2024_05], [FG_2024_06],
    [FG_2024_07], [FG_2024_08], [FG_2024_09],
    [FG_2024_10], [FG_2024_11], [FG_2024_12], [PRIMARY]);

-- パーティションテーブル作成
CREATE TABLE dbo.TransactionHistory (
    TransactionID BIGINT IDENTITY(1,1) NOT NULL,
    TransactionDate DATETIME2 NOT NULL,
    CustomerID INT NOT NULL,
    Amount DECIMAL(19,4) NOT NULL,
    CONSTRAINT PK_TransactionHistory 
        PRIMARY KEY CLUSTERED (TransactionDate, TransactionID)
) ON PS_Monthly(TransactionDate);

-- パーティション自動管理ジョブ
CREATE PROCEDURE dbo.ManagePartitions
AS
BEGIN
    DECLARE @NextMonth DATE = DATEADD(MONTH, 1, GETDATE());
    DECLARE @PartitionValue VARCHAR(10) = FORMAT(@NextMonth, 'yyyy-MM-01');
    
    -- 新しいファイルグループ作成
    EXEC('ALTER DATABASE [EnterpriseDB] ADD FILEGROUP [FG_' + 
         FORMAT(@NextMonth, 'yyyy_MM') + ']');
    
    -- パーティション関数拡張
    ALTER PARTITION SCHEME PS_Monthly NEXT USED [PRIMARY];
    ALTER PARTITION FUNCTION PF_Monthly() SPLIT RANGE (@PartitionValue);
    
    -- 古いパーティション削除（13ヶ月以上前）
    -- ...
END;
```

### 6. 統計情報とインデックス保守
```sql
-- インテリジェント保守プロシージャ
CREATE PROCEDURE dbo.IntelligentMaintenance
AS
BEGIN
    -- 断片化分析と再構築/再編成
    DECLARE @SQL NVARCHAR(MAX);
    
    WITH FragmentedIndexes AS (
        SELECT 
            OBJECT_NAME(ips.object_id) AS TableName,
            i.name AS IndexName,
            ips.avg_fragmentation_in_percent,
            ips.page_count,
            CASE 
                WHEN ips.avg_fragmentation_in_percent > 30 THEN 'REBUILD'
                WHEN ips.avg_fragmentation_in_percent > 10 THEN 'REORGANIZE'
                ELSE 'SKIP'
            END AS Action
        FROM sys.dm_db_index_physical_stats(
            DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
        INNER JOIN sys.indexes i ON ips.object_id = i.object_id 
            AND ips.index_id = i.index_id
        WHERE ips.avg_fragmentation_in_percent > 10
            AND ips.page_count > 1000
    )
    SELECT @SQL = STRING_AGG(
        CASE Action
            WHEN 'REBUILD' THEN 
                'ALTER INDEX [' + IndexName + '] ON [' + TableName + 
                '] REBUILD WITH (ONLINE = ON, MAXDOP = 4);'
            WHEN 'REORGANIZE' THEN 
                'ALTER INDEX [' + IndexName + '] ON [' + TableName + 
                '] REORGANIZE;'
        END, CHAR(13)
    )
    FROM FragmentedIndexes
    WHERE Action != 'SKIP';
    
    EXEC sp_executesql @SQL;
    
    -- 統計情報更新
    EXEC sp_updatestats;
END;
```

## パフォーマンス監視とアラート

### DMVを使用した監視
```sql
-- リアルタイムパフォーマンス監視ビュー
CREATE VIEW dbo.PerformanceMonitor AS
SELECT 
    -- CPU使用率
    (SELECT TOP 1 SQLProcessUtilization FROM (
        SELECT 
            record.value('(./Record/@id)[1]', 'int') AS record_id,
            record.value('(./Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]', 'int') AS SQLProcessUtilization
        FROM (
            SELECT CONVERT(XML, record) AS record 
            FROM sys.dm_os_ring_buffers 
            WHERE ring_buffer_type = N'RING_BUFFER_SCHEDULER_MONITOR'
        ) AS x
    ) AS y ORDER BY record_id DESC) AS CPU_Usage,
    
    -- メモリ使用量
    (SELECT 
        physical_memory_in_use_kb / 1024 AS Memory_Used_MB,
        large_page_allocations_kb / 1024 AS Large_Pages_MB,
        locked_page_allocations_kb / 1024 AS Locked_Pages_MB,
        memory_utilization_percentage AS Memory_Utilization
    FROM sys.dm_os_process_memory) AS Memory_Info,
    
    -- 待機統計
    (SELECT TOP 5
        wait_type,
        wait_time_ms / 1000.0 AS wait_time_sec,
        waiting_tasks_count
    FROM sys.dm_os_wait_stats
    WHERE wait_type NOT IN (
        'SLEEP_TASK', 'BROKER_TASK_STOP', 'BROKER_TO_FLUSH',
        'SQLTRACE_BUFFER_FLUSH', 'CLR_AUTO_EVENT', 'CLR_MANUAL_EVENT'
    )
    ORDER BY wait_time_ms DESC
    FOR JSON AUTO) AS Top_Waits;
```

## 出力レポート
```markdown
# SQL Server 最適化レポート

## 実施項目
✅ クエリストア: 有効化・自動チューニング設定
✅ インメモリOLTP: 3テーブル移行完了
✅ 列ストア: 5テーブルに適用
✅ Always On: 可用性グループ構成
✅ パーティション: 月次パーティション実装

## パフォーマンス改善
- 平均クエリ実行時間: 450ms → 85ms (81%改善)
- CPU使用率: 75% → 35% (53%削減)
- メモリ効率: 60% → 85% (42%向上)
- I/O待機時間: 250ms → 45ms (82%削減)

## 高可用性
- RPO: 0秒（同期コミット）
- RTO: <30秒（自動フェイルオーバー）
- 読み取りスケールアウト: 有効
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: SQL Server エンタープライズ機能

---
*このコマンドはSQL Serverのエンタープライズ機能に特化しています。*