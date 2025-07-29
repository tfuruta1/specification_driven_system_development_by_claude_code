# /csv-to-table - CSVからCREATE TABLEマイグレーション生成

## 概要

CSVファイルの構造を分析し、SQL ServerとSupabase両方に対応したCREATE TABLEマイグレーションを自動生成するコマンドです。
データ型の自動推論、制約条件の提案、最適化されたインデックス設計を提供します。

## 使用方法

```bash
# 基本的な使用方法
/csv-to-table [csv_file] [table_name] [database_type] [options]

# 使用例
/csv-to-table users_data.csv users sqlserver --analyze-data --suggest-indexes
/csv-to-table products.csv products supabase --with-constraints --japanese-fields
/csv-to-table sales_data.csv sales both --sample-size=10000 --optimize-types
```

## パラメータ

### 必須パラメータ
- `csv_file`: 分析対象のCSVファイルパス
- `table_name`: 生成するテーブル名
- `database_type`: データベースタイプ (`sqlserver` | `supabase` | `both`)

### オプション
- `--analyze-data`: データ内容を分析して型を推論
- `--suggest-indexes`: インデックス推奨を生成
- `--with-constraints`: 制約条件を自動生成
- `--japanese-fields`: 日本語フィールド名対応
- `--sample-size=N`: 分析するレコード数
- `--delimiter=tab`: 区切り文字指定
- `--encoding=utf8`: エンコーディング指定
- `--optimize-types`: 型の最適化提案

## データ型推論ロジック

### 1. 基本型推論

```javascript
// データ型推論アルゴリズム
const inferDataType = (values, databaseType) => {
  const nonNullValues = values.filter(v => v !== null && v !== '');
  
  if (nonNullValues.length === 0) {
    return databaseType === 'sqlserver' ? 'NVARCHAR(255)' : 'TEXT';
  }
  
  // 整数判定
  if (nonNullValues.every(v => /^-?\d+$/.test(v))) {
    const maxValue = Math.max(...nonNullValues.map(Number));
    const minValue = Math.min(...nonNullValues.map(Number));
    
    if (minValue >= -2147483648 && maxValue <= 2147483647) {
      return databaseType === 'sqlserver' ? 'INT' : 'INTEGER';
    } else {
      return databaseType === 'sqlserver' ? 'BIGINT' : 'BIGINT';
    }
  }
  
  // 小数判定
  if (nonNullValues.every(v => /^-?\d*\.?\d+$/.test(v))) {
    const decimalPlaces = Math.max(...nonNullValues.map(v => {
      const decimal = v.split('.')[1];
      return decimal ? decimal.length : 0;
    }));
    
    if (decimalPlaces <= 2) {
      return databaseType === 'sqlserver' ? 'DECIMAL(18,2)' : 'NUMERIC(18,2)';
    } else {
      return databaseType === 'sqlserver' ? 'FLOAT' : 'DOUBLE PRECISION';
    }
  }
  
  // 日付判定
  if (nonNullValues.every(v => isValidDate(v))) {
    if (nonNullValues.every(v => hasTimeComponent(v))) {
      return databaseType === 'sqlserver' ? 'DATETIME2' : 'TIMESTAMPTZ';
    } else {
      return databaseType === 'sqlserver' ? 'DATE' : 'DATE';
    }
  }
  
  // 真偽値判定
  if (nonNullValues.every(v => /^(true|false|0|1|yes|no|y|n)$/i.test(v))) {
    return databaseType === 'sqlserver' ? 'BIT' : 'BOOLEAN';
  }
  
  // UUID判定
  if (nonNullValues.every(v => isValidUUID(v))) {
    return databaseType === 'sqlserver' ? 'UNIQUEIDENTIFIER' : 'UUID';
  }
  
  // 文字列型（長さ最適化）
  const maxLength = Math.max(...nonNullValues.map(v => v.length));
  
  if (maxLength <= 50) {
    return databaseType === 'sqlserver' ? `NVARCHAR(${Math.max(50, maxLength)})` : `VARCHAR(${Math.max(50, maxLength)})`;
  } else if (maxLength <= 255) {
    return databaseType === 'sqlserver' ? `NVARCHAR(${maxLength + 20})` : `VARCHAR(${maxLength + 20})`;
  } else {
    return databaseType === 'sqlserver' ? 'NVARCHAR(MAX)' : 'TEXT';
  }
};
```

## 生成される成果物

### 1. SQL Server用 CREATE TABLE

```sql
-- table_migrations/sqlserver/create_users.sql

-- ================================
-- SQL Server テーブル作成
-- 元ファイル: users_data.csv
-- 分析レコード数: 10,000件
-- 生成日時: 2025-01-29 10:30:00
-- ================================

-- 分析結果サマリー
/*
総レコード数: 10,000
カラム数: 8
推論されたプライマリキー: user_id
推論された外部キー: department_id -> departments(id)
推奨インデックス数: 3
データ品質: 98.5% (欠損値: 1.5%)
*/

-- 1. メインテーブル作成
CREATE TABLE users (
    -- プライマリキー（自動推論: ユニーク値、連番パターン検出）
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    
    -- ユーザー情報
    user_name NVARCHAR(50) NOT NULL,  -- 最大長: 45文字、NULL率: 0%
    email NVARCHAR(100) UNIQUE NOT NULL,  -- Email形式検証済み、重複なし
    full_name NVARCHAR(100),  -- 最大長: 87文字、NULL率: 2.3%
    
    -- 日付・時刻フィールド
    birth_date DATE,  -- 日付形式: YYYY-MM-DD、範囲: 1950-2005
    created_at DATETIME2 DEFAULT GETDATE(),  -- ISO形式検出
    updated_at DATETIME2 DEFAULT GETDATE(),
    
    -- 真偽値フィールド
    is_active BIT DEFAULT 1,  -- true/false形式で95%がtrue
    
    -- 外部キー（リレーション推論）
    department_id INT,  -- 1-50の範囲、departments.id への参照推定
    
    -- JSON/構造化データ
    metadata NVARCHAR(MAX) CHECK (ISJSON(metadata) = 1),  -- JSON形式検出
    
    -- 計算フィールド（推奨）
    age AS (DATEDIFF(YEAR, birth_date, GETDATE())),
    full_email AS (user_name + '@company.com') PERSISTED
);

-- 2. 制約条件
ALTER TABLE users ADD CONSTRAINT CK_users_email 
    CHECK (email LIKE '%_@_%._%');

ALTER TABLE users ADD CONSTRAINT CK_users_birth_date 
    CHECK (birth_date >= '1900-01-01' AND birth_date <= GETDATE());

ALTER TABLE users ADD CONSTRAINT CK_users_user_name_length 
    CHECK (LEN(user_name) >= 2);

-- 3. インデックス（使用パターン分析に基づく推奨）
-- 検索頻度分析: email (95%), user_name (80%), created_at (60%)
CREATE NONCLUSTERED INDEX IX_users_email 
    ON users(email) 
    INCLUDE (user_name, full_name);  -- カバリングインデックス

CREATE NONCLUSTERED INDEX IX_users_user_name 
    ON users(user_name) 
    WHERE is_active = 1;  -- フィルター付きインデックス

CREATE NONCLUSTERED INDEX IX_users_created_at 
    ON users(created_at DESC)  -- 最新レコード取得最適化
    INCLUDE (user_id, user_name);

CREATE NONCLUSTERED INDEX IX_users_department_active 
    ON users(department_id, is_active)  -- 複合インデックス
    INCLUDE (user_name, email);

-- 4. 外部キー制約（推論ベース - 確認が必要）
-- 注意: 以下は推論結果です。実際の参照テーブルを確認してください。
/*
ALTER TABLE users ADD CONSTRAINT FK_users_department_id 
    FOREIGN KEY (department_id) 
    REFERENCES departments(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE;
*/

-- 5. トリガー（自動更新）
CREATE TRIGGER tr_users_updated_at
    ON users
    AFTER UPDATE
AS
BEGIN
    UPDATE users 
    SET updated_at = GETDATE()
    WHERE user_id IN (SELECT user_id FROM inserted);
END;

-- 6. 統計情報の更新
UPDATE STATISTICS users;

-- 7. パフォーマンス改善提案
/*
パフォーマンス最適化提案:

1. パーティション検討:
   - created_at による月次パーティション（レコード数が100万件を超える場合）

2. 圧縮検討:
   - ROW圧縮またはPAGE圧縮でストレージ効率向上

3. インデックス最適化:
   - 使用頻度の低いインデックスの定期見直し
   - カバリングインデックスによるKey Lookup削減

4. 統計情報:
   - 頻繁な更新がある場合、AUTO_UPDATE_STATISTICS_ASYNC = ON
*/

PRINT 'テーブル作成完了: users';
PRINT '推奨事項: データインポート後にインデックスの効果を検証してください';
```

### 2. Supabase用 CREATE TABLE

```sql
-- table_migrations/supabase/create_users.sql

-- ================================
-- Supabase テーブル作成
-- 元ファイル: users_data.csv
-- 分析レコード数: 10,000件
-- 生成日時: 2025-01-29 10:30:00
-- ================================

-- 分析結果サマリー
/*
総レコード数: 10,000
カラム数: 8
推論されたプライマリキー: user_id
RLS推奨レベル: HIGH（個人情報含む）
リアルタイム推奨: YES（ユーザーデータ）
*/

-- 1. メインテーブル作成
CREATE TABLE users (
    -- プライマリキー（UUID推奨 for Supabase）
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 元のuser_idを保持（マイグレーション用）
    legacy_user_id INTEGER UNIQUE,  -- 元のuser_id値
    
    -- ユーザー情報
    user_name VARCHAR(50) NOT NULL,  -- 最大長: 45文字、NULL率: 0%
    email VARCHAR(100) UNIQUE NOT NULL,  -- Email形式検証済み
    full_name VARCHAR(100),  -- 最大長: 87文字、NULL率: 2.3%
    
    -- 日付・時刻フィールド（タイムゾーン対応）
    birth_date DATE,  -- 範囲: 1950-2005
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 真偽値フィールド
    is_active BOOLEAN DEFAULT true,  -- 95%がtrue
    
    -- 外部キー
    department_id INTEGER,  -- departments.id への参照推定
    
    -- JSON データ（PostgreSQL JSONB）
    metadata JSONB,  -- JSON形式検出、インデックス対応
    
    -- 全文検索用（日本語対応）
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('japanese', coalesce(user_name, '')), 'A') ||
        setweight(to_tsvector('japanese', coalesce(full_name, '')), 'B') ||
        setweight(to_tsvector('japanese', coalesce(email, '')), 'C')
    ) STORED
);

-- 2. 制約条件
ALTER TABLE users ADD CONSTRAINT users_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users ADD CONSTRAINT users_birth_date_range 
    CHECK (birth_date >= '1900-01-01' AND birth_date <= CURRENT_DATE);

ALTER TABLE users ADD CONSTRAINT users_user_name_length 
    CHECK (length(trim(user_name)) >= 2);

-- 3. インデックス（PostgreSQL最適化）
-- B-tree インデックス
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_name ON users(user_name);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_department_active ON users(department_id, is_active) 
    WHERE is_active = true;

-- JSONB インデックス（GIN）
CREATE INDEX idx_users_metadata ON users USING GIN (metadata);

-- 全文検索インデックス
CREATE INDEX idx_users_search ON users USING GIN (search_vector);

-- 部分インデックス（アクティブユーザーのみ）
CREATE INDEX idx_users_active_created ON users(created_at DESC) 
    WHERE is_active = true;

-- 4. Row Level Security (RLS) 設定
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS ポリシー
CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- 管理者用ポリシー
CREATE POLICY "Admins can view all users"
    ON users FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

-- 公開プロフィール表示用ポリシー
CREATE POLICY "Public profile access"
    ON users FOR SELECT
    USING (
        is_active = true AND
        metadata->>'is_public' = 'true'
    );

-- 5. リアルタイム機能有効化
ALTER PUBLICATION supabase_realtime ADD TABLE users;

-- 6. トリガー関数
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

-- メタデータ検証トリガー
CREATE OR REPLACE FUNCTION validate_user_metadata()
RETURNS TRIGGER AS $$
BEGIN
    -- JSONB バリデーション
    IF NEW.metadata IS NOT NULL THEN
        -- 必須フィールドチェック
        IF NOT (NEW.metadata ? 'profile_version') THEN
            RAISE EXCEPTION 'metadata must contain profile_version field';
        END IF;
        
        -- 型チェック
        IF NOT (jsonb_typeof(NEW.metadata->'profile_version') = 'string') THEN
            RAISE EXCEPTION 'profile_version must be a string';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER validate_users_metadata
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION validate_user_metadata();

-- 7. 外部キー制約（推論ベース）
-- 注意: 実際の参照テーブルを確認してから有効化してください
/*
ALTER TABLE users ADD CONSTRAINT fk_users_department 
    FOREIGN KEY (department_id) 
    REFERENCES departments(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE;
*/

-- 8. 便利なビュー
CREATE VIEW active_users AS
SELECT 
    id,
    user_name,
    email,
    full_name,
    department_id,
    created_at,
    -- 計算フィールド
    EXTRACT(YEAR FROM AGE(birth_date)) AS age,
    CASE 
        WHEN created_at >= NOW() - INTERVAL '30 days' THEN 'new'
        WHEN created_at >= NOW() - INTERVAL '1 year' THEN 'recent'
        ELSE 'veteran'
    END AS user_category
FROM users
WHERE is_active = true;

-- 9. 統計情報とパフォーマンス
ANALYZE users;

-- 10. Edge Functions用のコメント
COMMENT ON TABLE users IS 'ユーザー情報テーブル - RLS有効、リアルタイム対応';
COMMENT ON COLUMN users.metadata IS 'JSONB形式のメタデータ。profile_version必須';
COMMENT ON COLUMN users.search_vector IS '全文検索用。user_name, full_name, emailを対象';

-- 完了メッセージ
DO $$
BEGIN
    RAISE NOTICE 'Supabase テーブル作成完了: users';
    RAISE NOTICE 'RLS有効、リアルタイム対応済み';
    RAISE NOTICE '推奨: データインポート後にパフォーマンスを検証してください';
END $$;
```

### 3. データ型分析レポート

```json
{
  "analysis_report": {
    "source_file": "users_data.csv",
    "analyzed_at": "2025-01-29T10:30:00Z",
    "total_records": 10000,
    "sample_size": 10000,
    "encoding": "utf-8",
    "delimiter": "tab",
    
    "data_quality": {
      "overall_score": 98.5,
      "missing_data_rate": 0.015,
      "duplicate_rate": 0.002,
      "format_consistency": 0.992
    },
    
    "columns": [
      {
        "name": "user_id",
        "original_name": "user_id",
        "inferred_type_sqlserver": "INT IDENTITY(1,1)",
        "inferred_type_supabase": "SERIAL",
        "is_primary_key": true,
        "is_unique": true,
        "null_rate": 0.0,
        "sample_values": ["1", "2", "3", "4", "5"],
        "statistics": {
          "min": 1,
          "max": 10000,
          "avg": 5000.5,
          "pattern": "sequential_integer"
        },
        "constraints": ["NOT NULL", "PRIMARY KEY"],
        "recommendations": ["Use as primary key", "Consider UUID for distributed systems"]
      },
      {
        "name": "user_name",
        "original_name": "ユーザー名",
        "inferred_type_sqlserver": "NVARCHAR(50)",
        "inferred_type_supabase": "VARCHAR(50)",
        "is_unique": false,
        "null_rate": 0.0,
        "max_length": 45,
        "avg_length": 8.2,
        "sample_values": ["yamada", "tanaka", "sato", "suzuki", "watanabe"],
        "constraints": ["NOT NULL"],
        "patterns": ["alphanumeric_lowercase", "japanese_romanji"],
        "recommendations": ["Create index for search", "Consider unique constraint"]
      },
      {
        "name": "email",
        "original_name": "メールアドレス",
        "inferred_type_sqlserver": "NVARCHAR(100)",
        "inferred_type_supabase": "VARCHAR(100)",
        "is_unique": true,
        "null_rate": 0.0,
        "validation_pattern": "email",
        "sample_values": ["yamada@example.com", "tanaka@test.jp"],
        "constraints": ["NOT NULL", "UNIQUE", "CHECK (email format)"],
        "recommendations": ["Create unique index", "Add email format validation"]
      },
      {
        "name": "birth_date",
        "original_name": "生年月日",
        "inferred_type_sqlserver": "DATE",
        "inferred_type_supabase": "DATE",
        "null_rate": 0.05,
        "date_format": "YYYY-MM-DD",
        "date_range": {
          "min": "1950-01-01",
          "max": "2005-12-31"
        },
        "constraints": ["CHECK (birth_date >= '1900-01-01')"],
        "recommendations": ["Add age calculation", "Consider age-based partitioning"]
      },
      {
        "name": "is_active",
        "original_name": "アクティブ",
        "inferred_type_sqlserver": "BIT",
        "inferred_type_supabase": "BOOLEAN",
        "null_rate": 0.0,
        "true_rate": 0.95,
        "value_mapping": {
          "true": ["true", "1", "はい", "有効"],
          "false": ["false", "0", "いいえ", "無効"]
        },
        "constraints": ["DEFAULT true"],
        "recommendations": ["Use for filtered indexes", "Consider soft delete pattern"]
      }
    ],
    
    "relationships": [
      {
        "column": "department_id",
        "referenced_table": "departments",
        "referenced_column": "id",
        "confidence": 0.85,
        "foreign_key_rate": 0.95
      }
    ],
    
    "index_recommendations": [
      {
        "columns": ["email"],
        "type": "unique",
        "reason": "Unique constraint and frequent lookups"
      },
      {
        "columns": ["user_name"],
        "type": "btree",
        "reason": "Frequent search operations"
      },
      {
        "columns": ["created_at"],
        "type": "btree_desc",
        "reason": "Order by recent records"
      },
      {
        "columns": ["department_id", "is_active"],
        "type": "composite",
        "reason": "Combined filtering operations"
      }
    ],
    
    "partitioning_recommendations": [
      {
        "strategy": "range_monthly",
        "column": "created_at",
        "reason": "Large dataset with time-based queries"
      }
    ]
  }
}
```

## 実行例

```bash
# CSVファイルから両方のDBタイプのテーブル作成
/csv-to-table users_data.csv users both --analyze-data --suggest-indexes

# 出力ファイル:
# table_migrations/sqlserver/create_users.sql
# table_migrations/supabase/create_users.sql
# analysis/users_data_analysis_report.json
# recommendations/users_optimization_guide.md
```

このコマンドにより、CSVデータから最適化されたテーブル構造を自動生成できます。

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "CSV\u304b\u3089create table\u30de\u30a4\u30b0\u30ec\u30fc\u30b7\u30e7\u30f3\u751f\u6210\u30b3\u30de\u30f3\u30c9", "status": "completed", "priority": "high", "id": "57"}, {"content": "CSV\u3092\u30aa\u30d5\u30e9\u30a4\u30f3\u7528JSON\u30c7\u30fc\u30bf\u306b\u5909\u63db\u30fb\u30bb\u30c3\u30c8\u30b3\u30de\u30f3\u30c9", "status": "in_progress", "priority": "high", "id": "58"}, {"content": "\u30d5\u30a3\u30fc\u30eb\u30c9\u5206\u5272\u30fb\u7d71\u5408\u5909\u63db\u30b3\u30de\u30f3\u30c9", "status": "pending", "priority": "high", "id": "59"}, {"content": "\u30d5\u30a3\u30fc\u30eb\u30c9\u540d\u30fb\u30c6\u30fc\u30d6\u30eb\u540d\u306e\u591a\u8a00\u8a9e\u5909\u63db\u30b3\u30de\u30f3\u30c9", "status": "pending", "priority": "high", "id": "60"}]