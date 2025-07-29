# /name-localize - フィールド名・テーブル名の多言語変換

## 概要

データベースのテーブル名・フィールド名を日本語⇔英語間で相互変換するマイグレーション生成コマンドです。
命名規則の統一、国際化対応、可読性向上を支援します。

## 使用方法

```bash
# 基本的な使用方法
/name-localize [direction] [target] [database_type] [options]

# 使用例
/name-localize jp-to-en users sqlserver --convention=snake_case
/name-localize en-to-jp products supabase --preserve-original --add-comments
/name-localize auto-detect all both --config=naming_rules.json
```

## パラメータ

### 必須パラメータ
- `direction`: 変換方向 (`jp-to-en` | `en-to-jp` | `auto-detect`)
- `target`: 対象 (`table_name` | `all` | `schema.json`)
- `database_type`: データベースタイプ (`sqlserver` | `supabase` | `both`)

### オプション
- `--convention=style`: 命名規則 (`snake_case` | `camelCase` | `PascalCase`)
- `--preserve-original`: 元の名前をコメントで保持
- `--add-comments`: 日本語説明コメント追加
- `--config=file`: 変換ルール設定ファイル
- `--dictionary=file`: カスタム辞書ファイル
- `--validate-conflicts`: 命名衝突チェック

## 変換ルール・辞書

### 1. 基本変換辞書

```json
// dictionaries/basic_translation.json

{
  "field_translations": {
    "jp_to_en": {
      "ユーザーID": "user_id",
      "ユーザー名": "user_name", 
      "ユーザー名前": "user_name",
      "名前": "name",
      "氏名": "full_name",
      "姓": "last_name",
      "名": "first_name",
      "メールアドレス": "email",
      "電話番号": "phone_number",
      "住所": "address",
      "郵便番号": "postal_code",
      "生年月日": "birth_date",
      "年齢": "age",
      "性別": "gender",
      "職業": "occupation",
      "会社名": "company_name",
      "部署": "department",
      "役職": "position",
      "給与": "salary",
      "入社日": "hire_date",
      "退社日": "leave_date",
      "作成日時": "created_at",
      "更新日時": "updated_at",
      "削除日時": "deleted_at",
      "有効フラグ": "is_active",
      "削除フラグ": "is_deleted",
      "ステータス": "status",
      "種別": "type",
      "カテゴリ": "category",
      "タグ": "tags",
      "備考": "notes",
      "コメント": "comments",
      "説明": "description",
      "詳細": "details"
    },
    
    "en_to_jp": {
      "user_id": "ユーザーID",
      "user_name": "ユーザー名",
      "name": "名前",
      "full_name": "氏名",
      "last_name": "姓", 
      "first_name": "名",
      "email": "メールアドレス",
      "phone_number": "電話番号",
      "address": "住所",
      "postal_code": "郵便番号",
      "birth_date": "生年月日",
      "age": "年齢",
      "gender": "性別",
      "occupation": "職業",
      "company_name": "会社名",
      "department": "部署",
      "position": "役職",
      "salary": "給与",
      "hire_date": "入社日",
      "leave_date": "退社日",
      "created_at": "作成日時",
      "updated_at": "更新日時", 
      "deleted_at": "削除日時",
      "is_active": "有効フラグ",
      "is_deleted": "削除フラグ",
      "status": "ステータス",
      "type": "種別",
      "category": "カテゴリ",
      "tags": "タグ",
      "notes": "備考",
      "comments": "コメント",
      "description": "説明",
      "details": "詳細"
    }
  },
  
  "table_translations": {
    "jp_to_en": {
      "ユーザー": "users",
      "ユーザーマスタ": "users",
      "顧客": "customers",
      "顧客マスタ": "customers",
      "商品": "products",
      "商品マスタ": "products",
      "注文": "orders",
      "注文明細": "order_details",
      "会社": "companies",
      "部署": "departments",
      "従業員": "employees",
      "カテゴリ": "categories",
      "タグ": "tags",
      "設定": "settings",
      "ログ": "logs",
      "履歴": "histories"
    },
    
    "en_to_jp": {
      "users": "ユーザー",
      "customers": "顧客", 
      "products": "商品",
      "orders": "注文",
      "order_details": "注文明細",
      "companies": "会社",
      "departments": "部署",
      "employees": "従業員",
      "categories": "カテゴリ",
      "tags": "タグ",
      "settings": "設定",
      "logs": "ログ",
      "histories": "履歴"
    }
  },
  
  "naming_conventions": {
    "snake_case": {
      "pattern": "^[a-z][a-z0-9_]*[a-z0-9]$",
      "transform": "lowercase_with_underscores",
      "examples": ["user_name", "created_at", "is_active"]
    },
    "camelCase": {
      "pattern": "^[a-z][a-zA-Z0-9]*$", 
      "transform": "camelCase",
      "examples": ["userName", "createdAt", "isActive"]
    },
    "PascalCase": {
      "pattern": "^[A-Z][a-zA-Z0-9]*$",
      "transform": "PascalCase", 
      "examples": ["UserName", "CreatedAt", "IsActive"]
    }
  }
}
```

## 生成される成果物

### 1. 日本語→英語変換 (SQL Server)

```sql
-- name_localizations/sqlserver/jp_to_en_users_001.sql

-- ================================
-- テーブル・フィールド名の英語化
-- 対象テーブル: ユーザー → users
-- 命名規則: snake_case
-- 生成日時: 2025-01-29 10:30:00
-- ================================

-- 1. 現在のテーブル構造確認
SELECT 
    COLUMN_NAME as 現在のカラム名,
    DATA_TYPE as データ型,
    IS_NULLABLE as NULL許可,
    COLUMN_DEFAULT as デフォルト値
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'ユーザー'
ORDER BY ORDINAL_POSITION;

-- 2. 新しいテーブル作成（英語名）
CREATE TABLE users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,  -- 元: ユーザーID
    user_name NVARCHAR(50) NOT NULL,         -- 元: ユーザー名
    email NVARCHAR(100) UNIQUE NOT NULL,     -- 元: メールアドレス
    full_name NVARCHAR(100),                 -- 元: 氏名
    phone_number NVARCHAR(20),               -- 元: 電話番号
    birth_date DATE,                         -- 元: 生年月日
    department NVARCHAR(100),                -- 元: 部署
    hire_date DATE,                          -- 元: 入社日
    is_active BIT DEFAULT 1,                 -- 元: 有効フラグ
    created_at DATETIME2 DEFAULT GETDATE(),  -- 元: 作成日時
    updated_at DATETIME2 DEFAULT GETDATE()   -- 元: 更新日時
);

-- 3. 元テーブルからデータ移行
INSERT INTO users (
    user_id, user_name, email, full_name, phone_number,
    birth_date, department, hire_date, is_active, created_at, updated_at
)
SELECT 
    ユーザーID as user_id,
    ユーザー名 as user_name,
    メールアドレス as email,
    氏名 as full_name,
    電話番号 as phone_number,
    生年月日 as birth_date,
    部署 as department,
    入社日 as hire_date,
    有効フラグ as is_active,
    作成日時 as created_at,
    更新日時 as updated_at
FROM ユーザー;

-- 4. インデックス再作成
CREATE NONCLUSTERED INDEX IX_users_email ON users(email);
CREATE NONCLUSTERED INDEX IX_users_user_name ON users(user_name);
CREATE NONCLUSTERED INDEX IX_users_department ON users(department);
CREATE NONCLUSTERED INDEX IX_users_created_at ON users(created_at DESC);

-- 5. 制約条件追加
ALTER TABLE users ADD CONSTRAINT CK_users_email_format
    CHECK (email LIKE '%_@_%._%');

ALTER TABLE users ADD CONSTRAINT CK_users_user_name_length  
    CHECK (LEN(user_name) >= 2);

-- 6. トリガー作成（updated_at自動更新）
CREATE TRIGGER tr_users_updated_at
    ON users
    AFTER UPDATE
AS
BEGIN
    UPDATE users 
    SET updated_at = GETDATE()
    WHERE user_id IN (SELECT user_id FROM inserted);
END;

-- 7. ビュー作成（日本語カラム名でのアクセス）
CREATE VIEW v_ユーザー AS
SELECT 
    user_id as ユーザーID,
    user_name as ユーザー名,
    email as メールアドレス,
    full_name as 氏名,
    phone_number as 電話番号,
    birth_date as 生年月日,
    department as 部署,
    hire_date as 入社日,
    is_active as 有効フラグ,
    created_at as 作成日時,
    updated_at as 更新日時
FROM users;

-- 8. 説明コメント追加（拡張プロパティ）
EXEC sp_addextendedproperty 
    @name = N'MS_Description', @value = N'ユーザー情報テーブル',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'users';

EXEC sp_addextendedproperty
    @name = N'MS_Description', @value = N'ユーザーID（主キー）',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'users',
    @level2type = N'COLUMN', @level2name = N'user_id';

EXEC sp_addextendedproperty
    @name = N'MS_Description', @value = N'ユーザー名（ログイン名）',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'users',
    @level2type = N'COLUMN', @level2name = N'user_name';

-- 9. 外部キー制約の更新（他テーブルへの影響）
-- 注意: 関連テーブルのFK制約も更新が必要
/*
-- 例: 注文テーブルの外部キー更新
ALTER TABLE 注文 DROP CONSTRAINT FK_注文_ユーザーID;
ALTER TABLE 注文 ADD CONSTRAINT FK_orders_user_id 
    FOREIGN KEY (ユーザーID) REFERENCES users(user_id);
*/

-- 10. 移行検証
SELECT 
    (SELECT COUNT(*) FROM ユーザー) as 元テーブル件数,
    (SELECT COUNT(*) FROM users) as 新テーブル件数,
    CASE 
        WHEN (SELECT COUNT(*) FROM ユーザー) = (SELECT COUNT(*) FROM users) 
        THEN '移行成功' 
        ELSE '移行失敗'
    END as 移行結果;

-- 11. 元テーブルのリネーム（バックアップ）
-- 注意: 本番環境では慎重に実行
-- EXEC sp_rename 'ユーザー', 'ユーザー_backup_20250129';

-- 完了メッセージ
PRINT 'テーブル名英語化完了: ユーザー → users';
PRINT '日本語アクセス用ビュー作成: v_ユーザー';
```

### 2. 英語→日本語変換 (Supabase)

```sql
-- name_localizations/supabase/en_to_jp_users_001.sql

-- ================================
-- Supabase テーブル・フィールド名の日本語化
-- 対象テーブル: users → ユーザー
-- 生成日時: 2025-01-29 10:30:00
-- ================================

-- 1. 現在のテーブル構造確認
SELECT 
    column_name as "Current Column Name",
    data_type as "Data Type",
    is_nullable as "Nullable",
    column_default as "Default Value"
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- 2. 新しいテーブル作成（日本語名）
CREATE TABLE ユーザー (
    ユーザーID SERIAL PRIMARY KEY,                    -- 元: user_id
    ユーザー名 VARCHAR(50) NOT NULL,                   -- 元: user_name
    メールアドレス VARCHAR(100) UNIQUE NOT NULL,       -- 元: email
    氏名 VARCHAR(100),                               -- 元: full_name
    電話番号 VARCHAR(20),                            -- 元: phone_number
    生年月日 DATE,                                   -- 元: birth_date
    部署 VARCHAR(100),                               -- 元: department
    入社日 DATE,                                    -- 元: hire_date
    有効フラグ BOOLEAN DEFAULT true,                  -- 元: is_active
    作成日時 TIMESTAMPTZ DEFAULT NOW(),              -- 元: created_at
    更新日時 TIMESTAMPTZ DEFAULT NOW()               -- 元: updated_at
);

-- 3. 元テーブルからデータ移行
INSERT INTO ユーザー (
    ユーザーID, ユーザー名, メールアドレス, 氏名, 電話番号,
    生年月日, 部署, 入社日, 有効フラグ, 作成日時, 更新日時
)
SELECT 
    user_id as ユーザーID,
    user_name as ユーザー名,
    email as メールアドレス,
    full_name as 氏名,
    phone_number as 電話番号,
    birth_date as 生年月日,
    department as 部署,
    hire_date as 入社日,
    is_active as 有効フラグ,
    created_at as 作成日時,
    updated_at as 更新日時
FROM users;

-- 4. インデックス作成
CREATE INDEX idx_ユーザー_メールアドレス ON ユーザー(メールアドレス);
CREATE INDEX idx_ユーザー_ユーザー名 ON ユーザー(ユーザー名);
CREATE INDEX idx_ユーザー_部署 ON ユーザー(部署);
CREATE INDEX idx_ユーザー_作成日時 ON ユーザー(作成日時 DESC);

-- 5. 制約条件追加
ALTER TABLE ユーザー ADD CONSTRAINT chk_ユーザー_メール形式
    CHECK (メールアドレス ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE ユーザー ADD CONSTRAINT chk_ユーザー名_長さ
    CHECK (length(trim(ユーザー名)) >= 2);

-- 6. Row Level Security (RLS) 設定
ALTER TABLE ユーザー ENABLE ROW LEVEL SECURITY;

-- RLSポリシー
CREATE POLICY "ユーザーは自分の情報のみ閲覧可能"
    ON ユーザー FOR SELECT
    USING (auth.uid()::text = ユーザーID::text);

CREATE POLICY "ユーザーは自分の情報のみ更新可能" 
    ON ユーザー FOR UPDATE
    USING (auth.uid()::text = ユーザーID::text)
    WITH CHECK (auth.uid()::text = ユーザーID::text);

-- 管理者用ポリシー
CREATE POLICY "管理者は全ユーザー閲覧可能"
    ON ユーザー FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

-- 7. トリガー関数作成（更新日時自動更新）
CREATE OR REPLACE FUNCTION update_更新日時()
RETURNS TRIGGER AS $$
BEGIN
    NEW.更新日時 = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_ユーザー_更新日時
    BEFORE UPDATE ON ユーザー
    FOR EACH ROW
    EXECUTE FUNCTION update_更新日時();

-- 8. ビュー作成（英語カラム名でのアクセス）
CREATE VIEW v_users_english AS
SELECT 
    ユーザーID as user_id,
    ユーザー名 as user_name,
    メールアドレス as email,
    氏名 as full_name,
    電話番号 as phone_number,
    生年月日 as birth_date,
    部署 as department,
    入社日 as hire_date,
    有効フラグ as is_active,
    作成日時 as created_at,
    更新日時 as updated_at
FROM ユーザー;

-- 9. リアルタイム機能有効化
ALTER PUBLICATION supabase_realtime ADD TABLE ユーザー;

-- 10. テーブル・カラムコメント
COMMENT ON TABLE ユーザー IS 'ユーザー情報を管理するテーブル';
COMMENT ON COLUMN ユーザー.ユーザーID IS 'ユーザーの一意識別子（主キー）';
COMMENT ON COLUMN ユーザー.ユーザー名 IS 'ログイン用のユーザー名';
COMMENT ON COLUMN ユーザー.メールアドレス IS 'ユーザーのメールアドレス（ユニーク）';
COMMENT ON COLUMN ユーザー.氏名 IS 'ユーザーの本名';
COMMENT ON COLUMN ユーザー.有効フラグ IS 'ユーザーのアクティブ状態';
COMMENT ON COLUMN ユーザー.作成日時 IS 'レコード作成日時';
COMMENT ON COLUMN ユーザー.更新日時 IS 'レコード最終更新日時';

-- 11. 移行検証
WITH migration_stats AS (
    SELECT 
        (SELECT COUNT(*) FROM users) as original_count,
        (SELECT COUNT(*) FROM ユーザー) as japanese_count
)
SELECT 
    original_count as "元テーブル件数",
    japanese_count as "日本語テーブル件数",
    CASE 
        WHEN original_count = japanese_count THEN '移行成功'
        ELSE '移行失敗'
    END as "移行結果"
FROM migration_stats;

-- 12. 元テーブルのリネーム（バックアップ）
-- 注意: 本番環境では慎重に実行
-- ALTER TABLE users RENAME TO users_backup_20250129;

-- 完了メッセージ
DO $$
BEGIN
    RAISE NOTICE 'テーブル名日本語化完了: users → ユーザー';
    RAISE NOTICE 'RLS設定済み、リアルタイム対応済み';
    RAISE NOTICE '英語アクセス用ビュー作成: v_users_english';
END $$;
```

### 3. 自動検出・一括変換

```json
// analysis/naming_analysis_report.json

{
  "analysis_result": {
    "database": "hybrid_app",
    "analyzed_at": "2025-01-29T10:30:00Z",
    "total_tables": 15,
    "total_columns": 127,
    
    "language_detection": {
      "japanese_tables": [
        {"name": "ユーザー", "confidence": 0.95, "suggested_en": "users"},
        {"name": "商品マスタ", "confidence": 0.90, "suggested_en": "products"},
        {"name": "注文履歴", "confidence": 0.88, "suggested_en": "order_histories"}
      ],
      "english_tables": [
        {"name": "customers", "confidence": 0.92, "suggested_jp": "顧客"},
        {"name": "order_details", "confidence": 0.85, "suggested_jp": "注文明細"}
      ],
      "mixed_tables": [
        {"name": "user_settings", "has_jp_columns": true, "requires_attention": true}
      ]
    },
    
    "naming_convention_analysis": {
      "snake_case": 65,
      "camelCase": 12, 
      "PascalCase": 8,
      "japanese": 35,
      "inconsistent": 7
    },
    
    "recommended_actions": [
      {
        "action": "standardize_to_english_snake_case",
        "affected_tables": 8,
        "priority": "high",
        "reason": "Improve international compatibility"
      },
      {
        "action": "add_japanese_comments",
        "affected_tables": 15,
        "priority": "medium", 
        "reason": "Maintain Japanese documentation"
      }
    ]
  }
}
```

## 実行例

```bash
# 日本語テーブル名を英語に変換
/name-localize jp-to-en users sqlserver --convention=snake_case --preserve-original

# 出力ファイル:
# name_localizations/sqlserver/jp_to_en_users_001.sql
# views/japanese_compatibility_views.sql
# rollback/revert_localization_001.sql
# analysis/naming_analysis_report.json
```

このコマンドにより、データベースの国際化と命名統一が可能になります。

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "\u30d5\u30a3\u30fc\u30eb\u30c9\u540d\u30fb\u30c6\u30fc\u30d6\u30eb\u540d\u306e\u591a\u8a00\u8a9e\u5909\u63db\u30b3\u30de\u30f3\u30c9", "status": "completed", "priority": "high", "id": "60"}, {"content": "\u30cf\u30a4\u30d6\u30ea\u30c3\u30c9\u63a5\u7d9a\u30d7\u30ed\u30b8\u30a7\u30af\u30c8\u5c02\u7528\u30ab\u30b9\u30bf\u30e0\u30b3\u30de\u30f3\u30c9\u4f5c\u6210", "status": "completed", "priority": "high", "id": "54"}]