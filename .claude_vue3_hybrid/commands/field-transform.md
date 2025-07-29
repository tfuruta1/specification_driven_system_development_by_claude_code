# /field-transform - フィールド分割・統合変換

## 概要

データベースのフィールドを分割・統合・再構成するマイグレーション生成コマンドです。
既存データの分析、変換ルール定義、データ整合性保証を自動化します。

## 使用方法

```bash
# 基本的な使用方法
/field-transform [action] [table_name] [field_config] [options]

# 使用例
/field-transform split users department --into="division,section,team" --database=both
/field-transform merge users "first_name,last_name" --into=full_name --separator=" "
/field-transform restructure products --config=product_transform.json
```

## パラメータ

### 必須パラメータ
- `action`: 変換タイプ (`split` | `merge` | `restructure` | `normalize`)
- `table_name`: 対象テーブル名
- `field_config`: フィールド設定 (分割対象フィールドまたは設定ファイル)

### オプション
- `--into=fields`: 分割先フィールド名（カンマ区切り）
- `--separator=char`: 分割・結合の区切り文字
- `--database=type`: データベースタイプ (`sqlserver` | `supabase` | `both`)
- `--config=file`: 変換設定ファイル
- `--analyze-data`: データ分析実行
- `--preserve-original`: 元フィールド保持
- `--validate-results`: 結果検証実行

## 変換タイプ

### 1. フィールド分割 (split)

#### 例: 部署フィールドを3つに分割

```sql
-- Before: 部署 = "開発本部-システム開発部-第1チーム"
-- After: 
--   本部 = "開発本部"
--   部署 = "システム開発部" 
--   チーム = "第1チーム"
```

#### SQL Server用マイグレーション

```sql
-- field_transforms/sqlserver/split_department_001.sql

-- ================================
-- フィールド分割マイグレーション
-- テーブル: users
-- 分割フィールド: department
-- 分割先: division, section, team
-- ================================

-- 1. 現在のデータ分析
WITH department_analysis AS (
    SELECT 
        department,
        COUNT(*) as record_count,
        -- 区切り文字パターン分析
        CASE 
            WHEN CHARINDEX('-', department) > 0 THEN 'hyphen'
            WHEN CHARINDEX('_', department) > 0 THEN 'underscore'
            WHEN CHARINDEX(' ', department) > 0 THEN 'space'
            ELSE 'no_separator'
        END as separator_type,
        -- 分割可能性チェック
        LEN(department) - LEN(REPLACE(department, '-', '')) + 1 as potential_splits
    FROM users 
    WHERE department IS NOT NULL
    GROUP BY department
)
SELECT 
    separator_type,
    COUNT(*) as pattern_count,
    AVG(potential_splits) as avg_splits,
    STRING_AGG(department, '; ') as sample_values
FROM department_analysis
GROUP BY separator_type;

-- 2. 新しいカラム追加
ALTER TABLE users ADD division NVARCHAR(100);
ALTER TABLE users ADD section NVARCHAR(100);
ALTER TABLE users ADD team NVARCHAR(100);

-- 3. データ分割・変換
WITH split_data AS (
    SELECT 
        user_id,
        department,
        -- ハイフン区切りで分割
        CASE 
            WHEN CHARINDEX('-', department) > 0 THEN
                LTRIM(RTRIM(SUBSTRING(department, 1, CHARINDEX('-', department) - 1)))
            ELSE department
        END as division_value,
        
        CASE 
            WHEN CHARINDEX('-', department) > 0 AND 
                 CHARINDEX('-', department, CHARINDEX('-', department) + 1) > 0 THEN
                LTRIM(RTRIM(SUBSTRING(
                    department, 
                    CHARINDEX('-', department) + 1, 
                    CHARINDEX('-', department, CHARINDEX('-', department) + 1) - CHARINDEX('-', department) - 1
                )))
            WHEN CHARINDEX('-', department) > 0 THEN
                LTRIM(RTRIM(SUBSTRING(department, CHARINDEX('-', department) + 1, LEN(department))))
            ELSE NULL
        END as section_value,
        
        CASE 
            WHEN CHARINDEX('-', department, CHARINDEX('-', department) + 1) > 0 THEN
                LTRIM(RTRIM(SUBSTRING(
                    department, 
                    CHARINDEX('-', department, CHARINDEX('-', department) + 1) + 1, 
                    LEN(department)
                )))
            ELSE NULL
        END as team_value
    FROM users
    WHERE department IS NOT NULL
)
UPDATE u
SET 
    division = sd.division_value,
    section = sd.section_value,
    team = sd.team_value
FROM users u
INNER JOIN split_data sd ON u.user_id = sd.user_id;

-- 4. データ正規化・クリーンアップ
UPDATE users 
SET 
    division = CASE 
        WHEN division = '本部' THEN division
        WHEN division NOT LIKE '%本部' THEN division + '本部'
        ELSE division
    END,
    section = CASE 
        WHEN section = '部' THEN section  
        WHEN section NOT LIKE '%部' AND section IS NOT NULL THEN section + '部'
        ELSE section
    END,
    team = CASE 
        WHEN team LIKE '%チーム' THEN team
        WHEN team IS NOT NULL AND team NOT LIKE '%班' THEN team + 'チーム'
        ELSE team
    END
WHERE division IS NOT NULL OR section IS NOT NULL OR team IS NOT NULL;

-- 5. 制約条件追加
ALTER TABLE users ADD CONSTRAINT CK_users_division_format
    CHECK (division IS NULL OR LEN(division) >= 2);

ALTER TABLE users ADD CONSTRAINT CK_users_section_format  
    CHECK (section IS NULL OR LEN(section) >= 2);

-- 6. インデックス作成
CREATE NONCLUSTERED INDEX IX_users_division ON users(division);
CREATE NONCLUSTERED INDEX IX_users_section ON users(section);
CREATE NONCLUSTERED INDEX IX_users_team ON users(team);

-- 複合インデックス
CREATE NONCLUSTERED INDEX IX_users_org_structure 
    ON users(division, section, team)
    INCLUDE (user_name, email);

-- 7. 変換結果検証
SELECT 
    'Before Split' as phase,
    COUNT(*) as total_records,
    COUNT(department) as non_null_departments,
    COUNT(DISTINCT department) as unique_departments
FROM users
WHERE department IS NOT NULL

UNION ALL

SELECT 
    'After Split',
    COUNT(*),
    COUNT(division) + COUNT(section) + COUNT(team) as total_split_fields,
    COUNT(DISTINCT CONCAT(division, '-', section, '-', team)) as unique_combinations
FROM users;

-- 8. エラーレコード確認
SELECT 
    user_id,
    department as original_department,
    division,
    section, 
    team,
    CASE 
        WHEN department IS NOT NULL AND division IS NULL THEN 'Failed to extract division'
        WHEN CHARINDEX('-', department) > 0 AND section IS NULL THEN 'Failed to extract section'
        ELSE 'Success'
    END as conversion_status
FROM users
WHERE department IS NOT NULL
  AND (division IS NULL OR (CHARINDEX('-', department) > 0 AND section IS NULL));

-- 9. 統計情報更新
UPDATE STATISTICS users;

PRINT 'フィールド分割完了: department → division, section, team';
```

#### Supabase用マイグレーション

```sql
-- field_transforms/supabase/split_department_001.sql

-- ================================
-- Supabase フィールド分割
-- テーブル: users
-- 分割フィールド: department  
-- 分割先: division, section, team
-- ================================

-- 1. 現在のデータ分析
WITH department_analysis AS (
    SELECT 
        department,
        COUNT(*) as record_count,
        CASE 
            WHEN position('-' in department) > 0 THEN 'hyphen'
            WHEN position('_' in department) > 0 THEN 'underscore'
            WHEN position(' ' in department) > 0 THEN 'space'
            ELSE 'no_separator'
        END as separator_type,
        array_length(string_to_array(department, '-'), 1) as split_count
    FROM users 
    WHERE department IS NOT NULL
    GROUP BY department
)
SELECT 
    separator_type,
    COUNT(*) as pattern_count,
    AVG(split_count) as avg_splits,
    string_agg(department, '; ' ORDER BY record_count DESC) as sample_values
FROM department_analysis
GROUP BY separator_type;

-- 2. 新しいカラム追加
ALTER TABLE users 
ADD COLUMN division VARCHAR(100),
ADD COLUMN section VARCHAR(100), 
ADD COLUMN team VARCHAR(100);

-- 3. 分割変換関数作成
CREATE OR REPLACE FUNCTION split_department_field()
RETURNS TRIGGER AS $$
BEGIN
    -- 自動分割処理
    IF NEW.department IS NOT NULL THEN
        DECLARE
            parts TEXT[];
        BEGIN
            parts := string_to_array(NEW.department, '-');
            
            -- 分割結果を各フィールドに設定
            NEW.division := CASE 
                WHEN array_length(parts, 1) >= 1 THEN trim(parts[1])
                ELSE NULL
            END;
            
            NEW.section := CASE 
                WHEN array_length(parts, 1) >= 2 THEN trim(parts[2])
                ELSE NULL  
            END;
            
            NEW.team := CASE
                WHEN array_length(parts, 1) >= 3 THEN trim(parts[3])
                ELSE NULL
            END;
            
            -- 正規化処理
            IF NEW.division IS NOT NULL AND NEW.division !~ '本部$' THEN
                NEW.division := NEW.division || '本部';
            END IF;
            
            IF NEW.section IS NOT NULL AND NEW.section !~ '部$' THEN
                NEW.section := NEW.section || '部';
            END IF;
            
            IF NEW.team IS NOT NULL AND NOT (NEW.team ~ 'チーム$' OR NEW.team ~ '班$') THEN
                NEW.team := NEW.team || 'チーム';
            END IF;
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. 既存データの一括変換
UPDATE users 
SET 
    division = CASE 
        WHEN position('-' in department) > 0 THEN
            trim(split_part(department, '-', 1))
        ELSE department
    END,
    section = CASE 
        WHEN position('-' in department) > 0 THEN
            trim(split_part(department, '-', 2))
        ELSE NULL
    END,
    team = CASE 
        WHEN position('-' in department) > 0 AND split_part(department, '-', 3) != '' THEN
            trim(split_part(department, '-', 3))
        ELSE NULL
    END
WHERE department IS NOT NULL;

-- 正規化処理
UPDATE users 
SET 
    division = CASE 
        WHEN division IS NOT NULL AND division !~ '本部$' THEN division || '本部'
        ELSE division
    END,
    section = CASE 
        WHEN section IS NOT NULL AND section !~ '部$' THEN section || '部'
        ELSE section  
    END,
    team = CASE
        WHEN team IS NOT NULL AND NOT (team ~ 'チーム$' OR team ~ '班$') THEN team || 'チーム'
        ELSE team
    END
WHERE division IS NOT NULL OR section IS NOT NULL OR team IS NOT NULL;

-- 5. トリガー設定（新規レコード用）
CREATE TRIGGER trigger_split_department
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION split_department_field();

-- 6. 制約条件
ALTER TABLE users ADD CONSTRAINT check_division_format
    CHECK (division IS NULL OR length(trim(division)) >= 2);

ALTER TABLE users ADD CONSTRAINT check_section_format
    CHECK (section IS NULL OR length(trim(section)) >= 2);

-- 7. インデックス作成
CREATE INDEX idx_users_division ON users(division);
CREATE INDEX idx_users_section ON users(section); 
CREATE INDEX idx_users_team ON users(team);

-- 複合インデックス  
CREATE INDEX idx_users_org_structure ON users(division, section, team);

-- 8. 変換結果検証
WITH conversion_stats AS (
    SELECT 
        COUNT(*) as total_records,
        COUNT(department) as original_departments,
        COUNT(division) as divisions_created,
        COUNT(section) as sections_created,
        COUNT(team) as teams_created,
        COUNT(DISTINCT department) as unique_departments,
        COUNT(DISTINCT (division, section, team)) as unique_combinations
    FROM users
)
SELECT 
    total_records,
    original_departments,
    divisions_created,
    sections_created, 
    teams_created,
    unique_departments,
    unique_combinations,
    ROUND(
        (divisions_created + sections_created + teams_created)::NUMERIC / 
        (original_departments * 3) * 100, 2
    ) as fill_rate_percent
FROM conversion_stats;

-- 9. エラーレコード確認
SELECT 
    user_id,
    department as original_department,
    division,
    section,
    team,
    CASE 
        WHEN department IS NOT NULL AND division IS NULL THEN 'Division extraction failed'
        WHEN position('-' in department) > 0 AND section IS NULL THEN 'Section extraction failed'
        ELSE 'Success'
    END as conversion_status
FROM users
WHERE department IS NOT NULL
  AND (division IS NULL OR (position('-' in department) > 0 AND section IS NULL))
LIMIT 50;

-- 完了メッセージ
DO $$
BEGIN
    RAISE NOTICE 'フィールド分割完了: department → division, section, team';
    RAISE NOTICE 'トリガー設定済み: 新規レコードは自動分割されます';
END $$;
```

### 2. フィールド統合 (merge)

#### 例: 姓・名フィールドを統合

```sql
-- Before: first_name = "太郎", last_name = "山田"  
-- After: full_name = "山田 太郎"
```

#### SQL Server用統合マイグレーション

```sql
-- field_transforms/sqlserver/merge_names_001.sql

-- ================================
-- フィールド統合マイグレーション
-- テーブル: users
-- 統合フィールド: first_name, last_name
-- 統合先: full_name
-- ================================

-- 1. 現在のデータ分析
SELECT 
    COUNT(*) as total_records,
    COUNT(first_name) as has_first_name,
    COUNT(last_name) as has_last_name,
    COUNT(CASE WHEN first_name IS NOT NULL AND last_name IS NOT NULL THEN 1 END) as has_both,
    COUNT(CASE WHEN first_name IS NULL AND last_name IS NULL THEN 1 END) as has_neither
FROM users;

-- 2. 新しいカラム追加
ALTER TABLE users ADD full_name NVARCHAR(200);

-- 3. データ統合
UPDATE users 
SET full_name = 
    CASE 
        WHEN last_name IS NOT NULL AND first_name IS NOT NULL THEN
            LTRIM(RTRIM(last_name)) + ' ' + LTRIM(RTRIM(first_name))
        WHEN last_name IS NOT NULL THEN
            LTRIM(RTRIM(last_name))
        WHEN first_name IS NOT NULL THEN  
            LTRIM(RTRIM(first_name))
        ELSE NULL
    END
WHERE first_name IS NOT NULL OR last_name IS NOT NULL;

-- 4. 日本語名前の正規化
UPDATE users
SET full_name = 
    -- 全角スペースを半角スペースに統一
    REPLACE(
        -- 連続スペースを単一スペースに
        LTRIM(RTRIM(
            REPLACE(
                REPLACE(full_name, '　', ' '),  -- 全角→半角
                '  ', ' '  -- 連続スペース→単一
            )
        )),
        '  ', ' '  -- 再度チェック
    )
WHERE full_name IS NOT NULL;

-- 5. 制約条件
ALTER TABLE users ADD CONSTRAINT CK_users_full_name_length
    CHECK (full_name IS NULL OR LEN(full_name) >= 2);

-- 6. インデックス作成
CREATE NONCLUSTERED INDEX IX_users_full_name ON users(full_name);

-- 全文検索用（SQL Server Full-Text Search対応）
-- CREATE FULLTEXT INDEX ON users(full_name) KEY INDEX PK_users;

-- 7. 統合結果検証
SELECT 
    'Integration Results' as status,
    COUNT(*) as total_records,
    COUNT(full_name) as integrated_names,
    COUNT(CASE WHEN LEN(full_name) < 2 THEN 1 END) as suspicious_short_names,
    COUNT(CASE WHEN full_name LIKE '%  %' THEN 1 END) as names_with_multiple_spaces
FROM users;

PRINT 'フィールド統合完了: first_name + last_name → full_name';
```

### 3. 複雑な再構成 (restructure)

#### 設定ファイル例

```json
// field_transform_config.json

{
  "transformation": {
    "table": "users",
    "database_types": ["sqlserver", "supabase"],
    "description": "ユーザー情報の再構成",
    
    "operations": [
      {
        "type": "split",
        "source_field": "department",
        "target_fields": ["division", "section", "team"],
        "separator": "-",
        "normalization": {
          "division": "append_suffix:本部",
          "section": "append_suffix:部", 
          "team": "append_suffix:チーム"
        }
      },
      {
        "type": "merge",
        "source_fields": ["first_name", "last_name"],
        "target_field": "full_name",
        "separator": " ",
        "order": "last_first"
      },
      {
        "type": "calculate",
        "target_field": "age",
        "formula": "DATEDIFF(YEAR, birth_date, GETDATE())",
        "condition": "birth_date IS NOT NULL"
      },
      {
        "type": "normalize",
        "target_field": "email",
        "transformations": ["lowercase", "trim"]
      },
      {
        "type": "categorize",
        "source_field": "age", 
        "target_field": "age_group",
        "categories": [
          {"range": "< 25", "label": "新卒"},
          {"range": "25-35", "label": "若手"},
          {"range": "36-50", "label": "中堅"},
          {"range": "> 50", "label": "ベテラン"}
        ]
      }
    ],
    
    "validation": {
      "required_fields": ["full_name", "email"],
      "unique_fields": ["email"],
      "format_checks": {
        "email": "email_format",
        "full_name": "min_length:2"
      }
    },
    
    "indexes": [
      {"fields": ["division", "section"], "type": "composite"},
      {"fields": ["full_name"], "type": "btree"},
      {"fields": ["age_group"], "type": "btree"}
    ]
  }
}
```

## 実行例

```bash
# 部署フィールドを3つに分割
/field-transform split users department --into="division,section,team" --database=both

# 出力ファイル:
# field_transforms/sqlserver/split_department_001.sql
# field_transforms/supabase/split_department_001.sql
# analysis/department_split_analysis.json
# rollback/undo_split_department_001.sql
```

このコマンドにより、柔軟なフィールド変換が可能になります。