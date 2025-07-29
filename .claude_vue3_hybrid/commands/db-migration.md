# /db-migration - SQL Server ⇔ Supabase テーブル変換マイグレーション生成

## 概要

SQL ServerとSupabase間でのテーブル構造変換マイグレーションを自動生成するコマンドです。
データベースシステム間の型変換、制約条件変換、インデックス変換を包括的に処理します。

## 使用方法

```bash
# 基本的な使用方法
/db-migration [source_type] [target_type] [table_name] [options]

# 使用例
/db-migration sqlserver supabase users --with-data
/db-migration supabase sqlserver products --constraints-only
/db-migration sqlserver supabase orders --batch-mode
```

## パラメータ

### 必須パラメータ
- `source_type`: 変換元データベース (`sqlserver` | `supabase`)
- `target_type`: 変換先データベース (`sqlserver` | `supabase`)
- `table_name`: 対象テーブル名

### オプション
- `--with-data`: データも含めて変換
- `--constraints-only`: 制約のみ変換
- `--indexes-only`: インデックスのみ変換
- `--batch-mode`: 複数テーブル一括変換
- `--schema-file`: スキーマファイル指定
- `--output-dir`: 出力ディレクトリ指定

## 変換マッピング

### データ型変換表

#### SQL Server → Supabase (PostgreSQL)

| SQL Server | Supabase | 備考 |
|------------|----------|------|
| `INT` | `INTEGER` | 32bit整数 |
| `BIGINT` | `BIGINT` | 64bit整数 |
| `VARCHAR(n)` | `VARCHAR(n)` | 可変長文字列 |
| `NVARCHAR(n)` | `VARCHAR(n)` | Unicode対応 |
| `TEXT` | `TEXT` | 長文テキスト |
| `DATETIME` | `TIMESTAMP` | 日時 |
| `DATETIME2` | `TIMESTAMPTZ` | タイムゾーン付き |
| `BIT` | `BOOLEAN` | 真偽値 |
| `DECIMAL(p,s)` | `NUMERIC(p,s)` | 精密数値 |
| `FLOAT` | `REAL` | 単精度浮動小数点 |
| `REAL` | `DOUBLE PRECISION` | 倍精度浮動小数点 |
| `UNIQUEIDENTIFIER` | `UUID` | UUID |
| `VARBINARY(MAX)` | `BYTEA` | バイナリデータ |

#### Supabase (PostgreSQL) → SQL Server

| Supabase | SQL Server | 備考 |
|----------|------------|------|
| `INTEGER` | `INT` | 32bit整数 |
| `BIGINT` | `BIGINT` | 64bit整数 |
| `VARCHAR(n)` | `NVARCHAR(n)` | Unicode対応 |
| `TEXT` | `NVARCHAR(MAX)` | 長文テキスト |
| `TIMESTAMP` | `DATETIME2` | 日時 |
| `TIMESTAMPTZ` | `DATETIMEOFFSET` | タイムゾーン付き |
| `BOOLEAN` | `BIT` | 真偽値 |
| `NUMERIC(p,s)` | `DECIMAL(p,s)` | 精密数値 |
| `REAL` | `REAL` | 単精度浮動小数点 |
| `DOUBLE PRECISION` | `FLOAT` | 倍精度浮動小数点 |
| `UUID` | `UNIQUEIDENTIFIER` | UUID |
| `BYTEA` | `VARBINARY(MAX)` | バイナリデータ |

## 生成される成果物

### 1. マイグレーションファイル

```sql
-- migrations/001_users_sqlserver_to_supabase.sql

-- ================================
-- SQL Server → Supabase 変換
-- テーブル: users
-- 生成日時: 2025-01-29 10:30:00
-- ================================

-- 1. テーブル作成 (Supabase)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    birth_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. インデックス作成
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_name ON users(user_name);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 3. Row Level Security (RLS) 設定
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 4. RLS ポリシー
CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id);

-- 5. リアルタイム有効化
ALTER PUBLICATION supabase_realtime ADD TABLE users;

-- 6. トリガー関数 (updated_at自動更新)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2. 逆変換マイグレーション

```sql
-- migrations/001_users_supabase_to_sqlserver_rollback.sql

-- ================================
-- Supabase → SQL Server 逆変換
-- テーブル: users
-- ================================

-- 1. テーブル作成 (SQL Server)
CREATE TABLE users (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_name NVARCHAR(50) NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    full_name NVARCHAR(100),
    birth_date DATE,
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- 2. インデックス作成
CREATE NONCLUSTERED INDEX IX_users_email ON users(email);
CREATE NONCLUSTERED INDEX IX_users_user_name ON users(user_name);
CREATE NONCLUSTERED INDEX IX_users_created_at ON users(created_at);

-- 3. トリガー (updated_at自動更新)
CREATE TRIGGER tr_users_updated_at
    ON users
    AFTER UPDATE
AS
BEGIN
    UPDATE users 
    SET updated_at = GETDATE()
    WHERE id IN (SELECT id FROM inserted)
END;
```

### 3. データ移行スクリプト

```sql
-- migrations/data/001_users_data_migration.sql

-- ================================
-- データ移行スクリプト
-- SQL Server → Supabase
-- ================================

-- 1. 一時テーブル作成
CREATE TEMP TABLE temp_users_migration (
    old_id INT,
    new_id UUID,
    user_name VARCHAR(50),
    email VARCHAR(100),
    -- その他フィールド
);

-- 2. データ変換・挿入
INSERT INTO temp_users_migration (old_id, new_id, user_name, email, ...)
SELECT 
    id as old_id,
    gen_random_uuid() as new_id,
    user_name,
    email,
    -- データ型変換処理
FROM source_users;

-- 3. 本テーブルに挿入
INSERT INTO users (id, user_name, email, ...)
SELECT new_id, user_name, email, ...
FROM temp_users_migration;

-- 4. 関連テーブルの外部キー更新
-- (別途生成される関連テーブル用スクリプト)
```

## 高度な変換機能

### 1. 制約条件変換

```sql
-- SQL Server制約をSupabase制約に変換

-- CHECK制約の変換
-- SQL Server:
ALTER TABLE products ADD CONSTRAINT CK_products_price CHECK (price > 0);

-- Supabase:
ALTER TABLE products ADD CONSTRAINT CK_products_price CHECK (price > 0);

-- 外部キー制約の変換
-- SQL Server:
ALTER TABLE orders ADD CONSTRAINT FK_orders_customer_id 
FOREIGN KEY (customer_id) REFERENCES customers(id)
ON DELETE CASCADE;

-- Supabase:
ALTER TABLE orders ADD CONSTRAINT FK_orders_customer_id 
FOREIGN KEY (customer_id) REFERENCES customers(id)
ON DELETE CASCADE;
```

### 2. 複合型・配列型の処理

```sql
-- SQL Server の XML → Supabase の JSONB
-- SQL Server:
CREATE TABLE documents (
    id INT IDENTITY PRIMARY KEY,
    metadata XML
);

-- Supabase:
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    metadata JSONB
);

-- 変換関数
CREATE OR REPLACE FUNCTION xml_to_jsonb(xml_data TEXT)
RETURNS JSONB AS $$
-- XML→JSON変換ロジック
$$ LANGUAGE plpgsql;
```

### 3. 認証・セキュリティ設定

```sql
-- SQL Serverロール → SupabaseRLS変換

-- SQL Server:
CREATE ROLE app_user;
GRANT SELECT, INSERT, UPDATE ON users TO app_user;

-- Supabase RLS equivalent:
CREATE POLICY "app_user_policy"
    ON users FOR ALL
    USING (
        auth.role() = 'authenticated' AND
        -- 追加の条件
    );
```

## 変換設定ファイル

### schema-mapping.json

```json
{
  "database_mappings": {
    "sqlserver_to_supabase": {
      "default_schema": "public",
      "type_mappings": {
        "INT": "INTEGER",
        "BIGINT": "BIGINT",
        "VARCHAR": "VARCHAR",
        "NVARCHAR": "VARCHAR",
        "DATETIME": "TIMESTAMP",
        "DATETIME2": "TIMESTAMPTZ",
        "BIT": "BOOLEAN",
        "DECIMAL": "NUMERIC",
        "UNIQUEIDENTIFIER": "UUID"
      },
      "constraint_mappings": {
        "PRIMARY KEY": "PRIMARY KEY",
        "FOREIGN KEY": "FOREIGN KEY",
        "UNIQUE": "UNIQUE",
        "CHECK": "CHECK"
      },
      "function_mappings": {
        "GETDATE()": "NOW()",
        "NEWID()": "gen_random_uuid()",
        "LEN()": "LENGTH()",
        "SUBSTRING()": "SUBSTR()"
      }
    }
  },
  "supabase_features": {
    "enable_rls": true,
    "enable_realtime": true,
    "auto_timestamps": true,
    "uuid_primary_keys": true
  },
  "sqlserver_features": {
    "identity_columns": true,
    "triggers_for_timestamps": true,
    "nonclustered_indexes": true
  }
}
```

## 実行例

### 単一テーブル変換

```bash
# SQL Server → Supabase
/db-migration sqlserver supabase users --with-data

# 出力ファイル:
# migrations/001_users_sqlserver_to_supabase.sql
# migrations/001_users_supabase_to_sqlserver_rollback.sql
# migrations/data/001_users_data_migration.sql
```

### 複数テーブル一括変換

```bash
# バッチモードで複数テーブル変換
/db-migration sqlserver supabase --batch-mode --schema-file=schema.json

# 対象テーブル一覧を対話式で選択
# または schema.json に定義されたテーブル群を一括変換
```

## エラーハンドリング

### 非対応型・機能の警告

```sql
-- 警告コメント付きで出力
-- WARNING: SQL Server HIERARCHYID type is not directly supported in PostgreSQL
-- Consider using ltree extension or alternative approach
-- ORIGINAL: hierarchy_path HIERARCHYID
hierarchy_path TEXT; -- MANUAL CONVERSION REQUIRED

-- WARNING: SQL Server table-valued functions need manual conversion
-- ORIGINAL: SELECT * FROM dbo.GetUsersByRole(@role)
-- Consider using PostgreSQL set-returning functions
```

### 依存関係チェック

```sql
-- 依存関係エラーの対処
-- ERROR: Cannot create table 'orders' before 'customers'
-- AUTO-RESOLVED: Reordering table creation based on foreign key dependencies

-- 1. customers テーブル作成
CREATE TABLE customers (...);

-- 2. orders テーブル作成 (customers テーブル後)
CREATE TABLE orders (...);
```

## 設定・カスタマイズ

### .env設定

```env
# データベース接続情報
SQLSERVER_HOST=localhost
SQLSERVER_DATABASE=MyApp
SQLSERVER_USER=sa
SQLSERVER_PASSWORD=password

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# マイグレーション設定
MIGRATION_OUTPUT_DIR=./migrations
BACKUP_BEFORE_MIGRATION=true
GENERATE_ROLLBACK_SCRIPTS=true
```

このコマンドにより、異なるデータベースシステム間での確実なテーブル構造変換が可能になります。