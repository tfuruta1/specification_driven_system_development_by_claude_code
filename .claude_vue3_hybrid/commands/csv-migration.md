# /csv-migration - タブ区切りCSVインポート・エクスポート用マイグレーション作成

## 概要

SQL ServerとSupabaseの両方に対応したタブ区切りCSV形式のデータインポート・エクスポート用マイグレーションを自動生成するコマンドです。
大量データの効率的な移行とバックアップを支援します。

## 使用方法

```bash
# 基本的な使用方法
/csv-migration [mode] [database_type] [table_name] [csv_file] [options]

# 使用例
/csv-migration import sqlserver users users_data.csv --delimiter=tab
/csv-migration export supabase products products_export.csv --with-headers
/csv-migration bulk-import sqlserver --config=import_config.json
/csv-migration bulk-export supabase --all-tables
```

## パラメータ

### 必須パラメータ
- `mode`: 動作モード (`import` | `export` | `bulk-import` | `bulk-export`)
- `database_type`: データベースタイプ (`sqlserver` | `supabase`)
- `table_name`: 対象テーブル名
- `csv_file`: CSVファイルパス

### オプション
- `--delimiter=tab`: 区切り文字指定 (tab|comma|semicolon)
- `--with-headers`: ヘッダー行を含める
- `--encoding=utf8`: 文字エンコーディング
- `--batch-size=1000`: バッチサイズ指定
- `--skip-validation`: バリデーション省略
- `--create-table`: テーブル自動作成
- `--truncate-before`: インポート前にテーブルクリア
- `--config`: 設定ファイル指定

## 生成される成果物

### 1. SQLServerインポート用スクリプト

```sql
-- csv_imports/sqlserver/import_users.sql

-- ================================
-- SQL Server CSV インポート
-- テーブル: users
-- ファイル: users_data.csv
-- 生成日時: 2025-01-29 10:30:00
-- ================================

-- 1. 一時テーブル作成
CREATE TABLE #temp_users_import (
    user_id NVARCHAR(50),
    user_name NVARCHAR(100),
    email NVARCHAR(255),
    full_name NVARCHAR(200),
    birth_date NVARCHAR(20),
    is_active NVARCHAR(10),
    created_at NVARCHAR(30),
    department NVARCHAR(100)
);

-- 2. CSVファイルからBULK INSERT
BULK INSERT #temp_users_import
FROM 'C:\data\users_data.csv'
WITH (
    FIELDTERMINATOR = '\t',    -- タブ区切り
    ROWTERMINATOR = '\n',      -- 改行
    FIRSTROW = 2,              -- ヘッダー行をスキップ
    CODEPAGE = '65001',        -- UTF-8
    ERRORFILE = 'C:\logs\import_errors.txt',
    MAXERRORS = 10
);

-- 3. データ型変換・バリデーション
WITH validated_data AS (
    SELECT 
        CASE 
            WHEN ISNUMERIC(user_id) = 1 THEN CAST(user_id AS INT)
            ELSE NULL 
        END AS user_id,
        
        LTRIM(RTRIM(user_name)) AS user_name,
        
        CASE 
            WHEN email LIKE '%@%' THEN LOWER(LTRIM(RTRIM(email)))
            ELSE NULL 
        END AS email,
        
        LTRIM(RTRIM(full_name)) AS full_name,
        
        CASE 
            WHEN ISDATE(birth_date) = 1 THEN CAST(birth_date AS DATE)
            ELSE NULL 
        END AS birth_date,
        
        CASE 
            WHEN LOWER(LTRIM(RTRIM(is_active))) IN ('true', '1', 'yes', 'y') THEN 1
            WHEN LOWER(LTRIM(RTRIM(is_active))) IN ('false', '0', 'no', 'n') THEN 0
            ELSE 1  -- デフォルト値
        END AS is_active,
        
        CASE 
            WHEN ISDATE(created_at) = 1 THEN CAST(created_at AS DATETIME2)
            ELSE GETDATE()  -- デフォルト値
        END AS created_at,
        
        LTRIM(RTRIM(department)) AS department,
        
        -- バリデーションエラーチェック
        CASE 
            WHEN ISNUMERIC(user_id) = 0 THEN 'Invalid user_id: ' + user_id
            WHEN email NOT LIKE '%@%' THEN 'Invalid email: ' + email
            WHEN LEN(LTRIM(RTRIM(user_name))) = 0 THEN 'Empty user_name'
            ELSE NULL
        END AS validation_error
        
    FROM #temp_users_import
)

-- 4. エラーレコードをログテーブルに記録
INSERT INTO import_error_log (table_name, error_message, raw_data, import_date)
SELECT 
    'users',
    validation_error,
    CONCAT(user_id, '\t', user_name, '\t', email, '\t', full_name),
    GETDATE()
FROM validated_data 
WHERE validation_error IS NOT NULL;

-- 5. 正常データを本テーブルに挿入
INSERT INTO users (user_id, user_name, email, full_name, birth_date, is_active, created_at, department)
SELECT 
    user_id,
    user_name,
    email,
    full_name,
    birth_date,
    is_active,
    created_at,
    department
FROM validated_data
WHERE validation_error IS NULL;

-- 6. インポート結果サマリー
SELECT 
    COUNT(*) AS total_records,
    SUM(CASE WHEN validation_error IS NULL THEN 1 ELSE 0 END) AS successful_imports,
    SUM(CASE WHEN validation_error IS NOT NULL THEN 1 ELSE 0 END) AS failed_imports
FROM validated_data;

-- 7. 一時テーブル削除
DROP TABLE #temp_users_import;

PRINT 'CSV インポート完了: users テーブル';
```

### 2. Supabaseインポート用スクリプト

```sql
-- csv_imports/supabase/import_users.sql

-- ================================
-- Supabase CSV インポート
-- テーブル: users
-- ファイル: users_data.csv
-- ================================

-- 1. 一時テーブル作成
CREATE TEMP TABLE temp_users_import (
    user_id TEXT,
    user_name TEXT,
    email TEXT,
    full_name TEXT,
    birth_date TEXT,
    is_active TEXT,
    created_at TEXT,
    department TEXT
);

-- 2. CSVファイルからCOPY (PostgreSQL機能)
\COPY temp_users_import FROM 'users_data.csv' WITH (FORMAT csv, DELIMITER E'\t', HEADER true, ENCODING 'UTF8');

-- 3. データ型変換・バリデーション関数
CREATE OR REPLACE FUNCTION validate_and_convert_users()
RETURNS TABLE (
    user_id INTEGER,
    user_name VARCHAR(100),
    email VARCHAR(255),
    full_name VARCHAR(200),
    birth_date DATE,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    department VARCHAR(100),
    validation_error TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE 
            WHEN temp.user_id ~ '^[0-9]+$' THEN temp.user_id::INTEGER
            ELSE NULL 
        END AS user_id,
        
        TRIM(temp.user_name)::VARCHAR(100) AS user_name,
        
        CASE 
            WHEN temp.email ~ '^[^@]+@[^@]+\.[^@]+$' THEN LOWER(TRIM(temp.email))::VARCHAR(255)
            ELSE NULL 
        END AS email,
        
        TRIM(temp.full_name)::VARCHAR(200) AS full_name,
        
        CASE 
            WHEN temp.birth_date ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' 
            THEN temp.birth_date::DATE
            ELSE NULL 
        END AS birth_date,
        
        CASE 
            WHEN LOWER(TRIM(temp.is_active)) IN ('true', '1', 'yes', 'y', 't') THEN TRUE
            WHEN LOWER(TRIM(temp.is_active)) IN ('false', '0', 'no', 'n', 'f') THEN FALSE
            ELSE TRUE  -- デフォルト値
        END AS is_active,
        
        CASE 
            WHEN temp.created_at ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' 
            THEN temp.created_at::TIMESTAMPTZ
            ELSE NOW()  -- デフォルト値
        END AS created_at,
        
        TRIM(temp.department)::VARCHAR(100) AS department,
        
        -- バリデーションエラーチェック
        CASE 
            WHEN NOT (temp.user_id ~ '^[0-9]+$') THEN 'Invalid user_id: ' || temp.user_id
            WHEN NOT (temp.email ~ '^[^@]+@[^@]+\.[^@]+$') THEN 'Invalid email: ' || temp.email
            WHEN LENGTH(TRIM(temp.user_name)) = 0 THEN 'Empty user_name'
            ELSE NULL
        END AS validation_error
        
    FROM temp_users_import temp;
END;
$$ LANGUAGE plpgsql;

-- 4. エラーログテーブル作成（存在しない場合）
CREATE TABLE IF NOT EXISTS import_error_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    error_message TEXT,
    raw_data TEXT,
    import_date TIMESTAMPTZ DEFAULT NOW()
);

-- 5. データ変換実行
WITH converted_data AS (
    SELECT * FROM validate_and_convert_users()
)

-- エラーレコードをログ記録
INSERT INTO import_error_log (table_name, error_message, raw_data)
SELECT 
    'users',
    validation_error,
    user_id || E'\t' || user_name || E'\t' || email || E'\t' || full_name
FROM converted_data 
WHERE validation_error IS NOT NULL;

-- 6. 正常データを本テーブルに挿入
WITH converted_data AS (
    SELECT * FROM validate_and_convert_users()
)
INSERT INTO users (user_id, user_name, email, full_name, birth_date, is_active, created_at, department)
SELECT 
    user_id,
    user_name,
    email,
    full_name,
    birth_date,
    is_active,
    created_at,
    department
FROM converted_data
WHERE validation_error IS NULL;

-- 7. インポート結果サマリー
WITH converted_data AS (
    SELECT * FROM validate_and_convert_users()
)
SELECT 
    COUNT(*) AS total_records,
    COUNT(*) FILTER (WHERE validation_error IS NULL) AS successful_imports,
    COUNT(*) FILTER (WHERE validation_error IS NOT NULL) AS failed_imports
FROM converted_data;

-- 8. 一時テーブル・関数削除
DROP TABLE temp_users_import;
DROP FUNCTION validate_and_convert_users();

-- 完了メッセージ
DO $$
BEGIN
    RAISE NOTICE 'CSV インポート完了: users テーブル';
END $$;
```

### 3. SQLServerエクスポート用スクリプト

```sql
-- csv_exports/sqlserver/export_users.sql

-- ================================
-- SQL Server CSV エクスポート
-- テーブル: users
-- ファイル: users_export.csv
-- ================================

-- 1. エクスポート用ビュー作成
CREATE VIEW v_users_export AS
SELECT 
    user_id,
    user_name,
    email,
    full_name,
    FORMAT(birth_date, 'yyyy-MM-dd') AS birth_date,
    CASE WHEN is_active = 1 THEN 'true' ELSE 'false' END AS is_active,
    FORMAT(created_at, 'yyyy-MM-dd HH:mm:ss') AS created_at,
    department,
    -- 追加の計算フィールド
    DATEDIFF(YEAR, birth_date, GETDATE()) AS age,
    CASE 
        WHEN created_at >= DATEADD(MONTH, -1, GETDATE()) THEN 'new'
        WHEN created_at >= DATEADD(YEAR, -1, GETDATE()) THEN 'recent'
        ELSE 'old'
    END AS user_category
FROM users
WHERE is_active = 1  -- アクティブユーザーのみ
ORDER BY created_at DESC;

-- 2. BCP コマンド生成（バッチファイル出力）
DECLARE @bcp_command NVARCHAR(4000);
SET @bcp_command = 'bcp "SELECT * FROM ' + DB_NAME() + '.dbo.v_users_export" queryout "C:\exports\users_export.csv" -c -t"\t" -r"\n" -S' + @@SERVERNAME + ' -T';

PRINT '以下のBCPコマンドを実行してください:';
PRINT @bcp_command;

-- 3. PowerShellスクリプト生成（より高度なエクスポート）
PRINT '
# PowerShell エクスポートスクリプト
$ServerInstance = "' + @@SERVERNAME + '"
$Database = "' + DB_NAME() + '"
$OutputFile = "C:\exports\users_export.csv"

$Query = @"
SELECT 
    user_id,
    user_name,
    email,
    full_name,
    FORMAT(birth_date, ''yyyy-MM-dd'') AS birth_date,
    CASE WHEN is_active = 1 THEN ''true'' ELSE ''false'' END AS is_active,
    FORMAT(created_at, ''yyyy-MM-dd HH:mm:ss'') AS created_at,
    department
FROM users 
WHERE is_active = 1
ORDER BY created_at DESC
"@

Invoke-Sqlcmd -ServerInstance $ServerInstance -Database $Database -Query $Query | 
Export-Csv -Path $OutputFile -Delimiter "`t" -NoTypeInformation -Encoding UTF8

Write-Host "エクスポート完了: $OutputFile"
';

-- 4. エクスポート統計
SELECT 
    COUNT(*) AS total_records,
    COUNT(CASE WHEN is_active = 1 THEN 1 END) AS active_records,
    MIN(created_at) AS oldest_record,
    MAX(created_at) AS newest_record
FROM users;

-- 5. ビュー削除
DROP VIEW v_users_export;
```

### 4. Supabaseエクスポート用スクリプト

```sql
-- csv_exports/supabase/export_users.sql

-- ================================
-- Supabase CSV エクスポート
-- テーブル: users
-- ファイル: users_export.csv
-- ================================

-- 1. エクスポート用ビュー作成
CREATE OR REPLACE VIEW v_users_export AS
SELECT 
    user_id,
    user_name,
    email,
    full_name,
    TO_CHAR(birth_date, 'YYYY-MM-DD') AS birth_date,
    CASE WHEN is_active THEN 'true' ELSE 'false' END AS is_active,
    TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
    department,
    -- 追加の計算フィールド
    EXTRACT(YEAR FROM AGE(birth_date)) AS age,
    CASE 
        WHEN created_at >= NOW() - INTERVAL '1 month' THEN 'new'
        WHEN created_at >= NOW() - INTERVAL '1 year' THEN 'recent'
        ELSE 'old'
    END AS user_category
FROM users
WHERE is_active = true  -- アクティブユーザーのみ
ORDER BY created_at DESC;

-- 2. CSV エクスポート（COPY TO）
\COPY (SELECT * FROM v_users_export) TO 'users_export.csv' WITH (FORMAT csv, DELIMITER E'\t', HEADER true, ENCODING 'UTF8');

-- 3. Node.js/JavaScriptエクスポートスクリプト生成
DO $$
DECLARE
    export_script TEXT;
BEGIN
    export_script := '
// Node.js CSV エクスポートスクリプト
const { createClient } = require("@supabase/supabase-js");
const fs = require("fs");

const supabaseUrl = "' || current_setting('app.supabase_url', true) || '";
const supabaseKey = "' || current_setting('app.supabase_key', true) || '";
const supabase = createClient(supabaseUrl, supabaseKey);

async function exportUsers() {
    try {
        const { data, error } = await supabase
            .from("v_users_export")
            .select("*")
            .order("created_at", { ascending: false });
        
        if (error) throw error;
        
        // CSV ヘッダー作成
        const headers = Object.keys(data[0]).join("\t");
        
        // CSV データ作成
        const csvData = data.map(row => 
            Object.values(row).join("\t")
        ).join("\n");
        
        const csvContent = headers + "\n" + csvData;
        
        // ファイル出力
        fs.writeFileSync("users_export.csv", csvContent, "utf8");
        
        console.log(`エクスポート完了: ${data.length} レコード`);
        
    } catch (error) {
        console.error("エクスポートエラー:", error);
    }
}

exportUsers();
';
    
    -- スクリプトをファイルに出力（実際の実装では適切なパスに）
    RAISE NOTICE 'Node.js エクスポートスクリプト: %', export_script;
END $$;

-- 4. エクスポート統計
SELECT 
    COUNT(*) AS total_records,
    COUNT(*) FILTER (WHERE is_active = true) AS active_records,
    MIN(created_at) AS oldest_record,
    MAX(created_at) AS newest_record
FROM users;

-- 5. ビュー削除
DROP VIEW v_users_export;

-- 完了メッセージ
DO $$
BEGIN
    RAISE NOTICE 'CSV エクスポート設定完了: users テーブル';
END $$;
```

## 設定ファイル

### csv-config.json

```json
{
  "import_settings": {
    "default_delimiter": "tab",
    "default_encoding": "utf8",
    "batch_size": 1000,
    "max_errors": 10,
    "create_error_log": true,
    "validate_data": true,
    "truncate_before_import": false
  },
  "export_settings": {
    "include_headers": true,
    "date_format": "YYYY-MM-DD",
    "datetime_format": "YYYY-MM-DD HH:mm:ss",
    "boolean_format": "true/false",
    "null_representation": ""
  },
  "field_mappings": {
    "users": {
      "user_id": {
        "type": "integer",
        "required": true,
        "validation": "^[0-9]+$"
      },
      "email": {
        "type": "string",
        "required": true,
        "validation": "^[^@]+@[^@]+\\.[^@]+$",
        "transform": "lowercase"
      },
      "is_active": {
        "type": "boolean",
        "default": true,
        "true_values": ["true", "1", "yes", "y", "t"],
        "false_values": ["false", "0", "no", "n", "f"]
      }
    }
  },
  "table_specific_settings": {
    "users": {
      "export_filter": "is_active = true",
      "sort_order": "created_at DESC",
      "additional_fields": ["age", "user_category"]
    },
    "products": {
      "export_filter": "status = 'active'",
      "sort_order": "product_name ASC"
    }
  }
}
```

## 実行例

### 単一テーブルインポート

```bash
# SQL Server にタブ区切りCSVをインポート
/csv-migration import sqlserver users users_data.csv --delimiter=tab --with-headers

# 出力ファイル:
# csv_imports/sqlserver/import_users.sql
# scripts/import_users.bat (Windowsバッチファイル)
# scripts/import_users.ps1 (PowerShellスクリプト)
```

### 一括エクスポート

```bash
# Supabase から全テーブルをエクスポート
/csv-migration bulk-export supabase --all-tables --config=csv-config.json

# 出力ファイル:
# csv_exports/supabase/export_all_tables.sql
# csv_exports/supabase/export_users.sql
# csv_exports/supabase/export_products.sql
# scripts/export_all.js (Node.jsスクリプト)
```

このコマンドにより、効率的なCSVデータ移行が可能になります。