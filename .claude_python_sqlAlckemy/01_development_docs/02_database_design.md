# データベース設計書

## 🗄️ データベース概要

### 基本情報
- **DBMS**: Microsoft SQL Server
- **文字コード**: UTF-8
- **照合順序**: Japanese_CI_AS
- **接続方式**: pyodbc + SQLAlchemy ORM

## 📊 データモデリング方針

### 1. 正規化レベル
- 基本的に第3正規形（3NF）を適用
- パフォーマンスを考慮した適切な非正規化
- 読み取り専用テーブルでの冗長性許容

### 2. 命名規則
```sql
-- テーブル名: 複数形、スネークケース
CREATE TABLE production_results (...)

-- カラム名: スネークケース
product_id INT NOT NULL,
created_at DATETIME2 DEFAULT GETDATE()

-- 主キー: テーブル名_id
production_result_id INT IDENTITY(1,1) PRIMARY KEY

-- 外部キー: 参照テーブル名_id
product_id INT FOREIGN KEY REFERENCES products(product_id)
```

## 🔑 主要エンティティ設計

### 1. 出荷管理ドメイン

#### shipment_checksheets（出荷チェックシート）
```sql
CREATE TABLE shipment_checksheets (
    checksheet_id INT IDENTITY(1,1) PRIMARY KEY,
    shipment_no VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    shipment_date DATE NOT NULL,
    inspector_id INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (inspector_id) REFERENCES employees(employee_id)
);

-- インデックス
CREATE INDEX idx_shipment_date ON shipment_checksheets(shipment_date);
CREATE INDEX idx_customer_product ON shipment_checksheets(customer_id, product_id);
```

#### checksheet_items（チェックシート項目）
```sql
CREATE TABLE checksheet_items (
    item_id INT IDENTITY(1,1) PRIMARY KEY,
    checksheet_id INT NOT NULL,
    check_point VARCHAR(200) NOT NULL,
    result VARCHAR(10) NOT NULL CHECK (result IN ('OK', 'NG', 'NA')),
    note TEXT,
    checked_at DATETIME2,
    FOREIGN KEY (checksheet_id) REFERENCES shipment_checksheets(checksheet_id)
);
```

### 2. 生産管理ドメイン

#### production_results（生産実績）
```sql
CREATE TABLE production_results (
    result_id INT IDENTITY(1,1) PRIMARY KEY,
    work_order_no VARCHAR(50) NOT NULL,
    product_id INT NOT NULL,
    line_id INT NOT NULL,
    worker_id INT NOT NULL,
    start_time DATETIME2 NOT NULL,
    end_time DATETIME2,
    planned_quantity INT NOT NULL,
    actual_quantity INT NOT NULL DEFAULT 0,
    defect_quantity INT NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (line_id) REFERENCES production_lines(line_id),
    FOREIGN KEY (worker_id) REFERENCES employees(employee_id)
);

-- 複合インデックス
CREATE INDEX idx_work_order ON production_results(work_order_no);
CREATE INDEX idx_production_date ON production_results(start_time, end_time);
```

#### defect_records（不良記録）
```sql
CREATE TABLE defect_records (
    defect_id INT IDENTITY(1,1) PRIMARY KEY,
    result_id INT NOT NULL,
    defect_type_id INT NOT NULL,
    quantity INT NOT NULL,
    cause TEXT,
    action_taken TEXT,
    recorded_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (result_id) REFERENCES production_results(result_id),
    FOREIGN KEY (defect_type_id) REFERENCES defect_types(defect_type_id)
);
```

### 3. 在庫管理ドメイン

#### inventory_items（在庫品目）
```sql
CREATE TABLE inventory_items (
    item_id INT IDENTITY(1,1) PRIMARY KEY,
    item_code VARCHAR(50) NOT NULL UNIQUE,
    item_name NVARCHAR(200) NOT NULL,
    category_id INT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    min_stock_level DECIMAL(10,2),
    max_stock_level DECIMAL(10,2),
    current_stock DECIMAL(10,2) NOT NULL DEFAULT 0,
    location_id INT,
    qr_code VARCHAR(100) UNIQUE,
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (category_id) REFERENCES item_categories(category_id),
    FOREIGN KEY (location_id) REFERENCES storage_locations(location_id)
);
```

#### inventory_transactions（在庫取引）
```sql
CREATE TABLE inventory_transactions (
    transaction_id INT IDENTITY(1,1) PRIMARY KEY,
    item_id INT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('IN', 'OUT', 'ADJUST')),
    quantity DECIMAL(10,2) NOT NULL,
    reference_no VARCHAR(50),
    reference_type VARCHAR(50),
    performed_by INT NOT NULL,
    note TEXT,
    transaction_date DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (item_id) REFERENCES inventory_items(item_id),
    FOREIGN KEY (performed_by) REFERENCES employees(employee_id)
);

-- パーティショニング候補
-- transaction_dateでの月次パーティション
```

### 4. マスタデータ

#### employees（従業員）
```sql
CREATE TABLE employees (
    employee_id INT IDENTITY(1,1) PRIMARY KEY,
    employee_code VARCHAR(20) NOT NULL UNIQUE,
    full_name NVARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    role_id INT NOT NULL,
    email VARCHAR(100),
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);
```

#### products（製品）
```sql
CREATE TABLE products (
    product_id INT IDENTITY(1,1) PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    product_name NVARCHAR(200) NOT NULL,
    product_type VARCHAR(50),
    specification TEXT,
    unit VARCHAR(20) NOT NULL,
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
```

## 🔐 セキュリティ設計

### 1. アクセス制御
```sql
-- ロールベースアクセス
CREATE ROLE db_api_reader;
CREATE ROLE db_api_writer;
CREATE ROLE db_api_admin;

-- 権限付与
GRANT SELECT ON SCHEMA::dbo TO db_api_reader;
GRANT SELECT, INSERT, UPDATE ON SCHEMA::dbo TO db_api_writer;
GRANT CONTROL ON SCHEMA::dbo TO db_api_admin;
```

### 2. 監査ログ
```sql
CREATE TABLE audit_logs (
    log_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    user_id INT,
    changed_data NVARCHAR(MAX),
    ip_address VARCHAR(45),
    created_at DATETIME2 DEFAULT GETDATE()
);

-- トリガーによる自動記録
CREATE TRIGGER tr_products_audit
ON products
AFTER INSERT, UPDATE, DELETE
AS BEGIN
    -- 監査ログ記録処理
END
```

## 🚀 パフォーマンス最適化

### 1. インデックス戦略
```sql
-- カバリングインデックス
CREATE INDEX idx_production_results_covering
ON production_results(start_time, product_id)
INCLUDE (actual_quantity, defect_quantity);

-- フィルタードインデックス
CREATE INDEX idx_active_items
ON inventory_items(item_code)
WHERE is_active = 1;
```

### 2. パーティショニング
```sql
-- 月次パーティション（大量データテーブル）
CREATE PARTITION FUNCTION pf_monthly(DATETIME2)
AS RANGE RIGHT FOR VALUES 
('2024-01-01', '2024-02-01', '2024-03-01', ...);

CREATE PARTITION SCHEME ps_monthly
AS PARTITION pf_monthly
TO ([PRIMARY], [PRIMARY], [PRIMARY], ...);
```

## 📈 スケーラビリティ考慮

### 1. シャーディング準備
- customer_idベースの水平分割準備
- 地域別データ分離の考慮

### 2. アーカイブ戦略
```sql
-- 古いデータのアーカイブテーブル
CREATE TABLE production_results_archive (
    -- 同じ構造
) ON [ARCHIVE_FG];

-- 定期的なアーカイブ処理
CREATE PROCEDURE sp_archive_old_data
AS BEGIN
    -- 1年以上前のデータを移動
END
```

## 🔄 データ整合性

### 1. 制約
- 外部キー制約による参照整合性
- CHECK制約によるドメイン制約
- UNIQUE制約による一意性保証

### 2. トランザクション設計
```sql
-- 在庫更新の例
BEGIN TRANSACTION;
    -- 在庫数量更新
    UPDATE inventory_items 
    SET current_stock = current_stock - @quantity
    WHERE item_id = @item_id;
    
    -- トランザクション記録
    INSERT INTO inventory_transactions ...;
    
    -- 履歴記録
    INSERT INTO inventory_history ...;
COMMIT TRANSACTION;
```