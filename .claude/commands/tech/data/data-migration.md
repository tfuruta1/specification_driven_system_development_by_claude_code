# /data-migration - データ移行・変換統合コマンド

## 概要
CSV、Excel、JSON、XML、データベース間のデータ移行と変換を包括的に実行するコマンドです。

## 使用方法
```bash
/data-migration [source_type] [target_type] [options]

# 使用例
/data-migration csv database --mapping=auto
/data-migration excel json --transform=custom
/data-migration database database --sync=realtime
/data-migration csv offline --optimize
```

## パラメータ

### 必須パラメータ
- `source_type`: 移行元データ形式
  - `csv` - CSVファイル
  - `excel` - Excelファイル
  - `json` - JSONファイル
  - `xml` - XMLファイル
  - `database` - データベース
  - `api` - REST API

- `target_type`: 移行先データ形式
  - `database` - データベース
  - `json` - JSONファイル
  - `offline` - オフラインデータ
  - `api` - REST API
  - `table` - テーブル形式

### オプション
- `--mapping`: マッピング方式（auto, manual, template）
- `--transform`: 変換ルール適用
- `--validate`: データ検証実施
- `--sync`: 同期方式（onetime, realtime, scheduled）
- `--optimize`: 最適化実施

## データ移行パターン

### 1. CSV → データベース
```python
import pandas as pd
from sqlalchemy import create_engine

class CsvToDatabase:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
    
    def migrate(self, csv_path, table_name, mapping=None):
        # CSVデータ読み込み
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # データ型推論と最適化
        df = self.optimize_dtypes(df)
        
        # カラムマッピング
        if mapping:
            df = df.rename(columns=mapping)
        
        # データクレンジング
        df = self.clean_data(df)
        
        # データベースへ書き込み
        df.to_sql(
            table_name, 
            self.engine,
            if_exists='append',
            index=False,
            chunksize=1000
        )
        
        return {
            'rows_migrated': len(df),
            'columns': list(df.columns),
            'status': 'success'
        }
    
    def optimize_dtypes(self, df):
        """データ型の最適化"""
        for col in df.columns:
            col_type = df[col].dtype
            
            if col_type != 'object':
                continue
                
            # 日付型の検出と変換
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
            
            # 数値型の検出と変換
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass
        
        return df
```

### 2. Excel → JSON変換
```python
class ExcelToJson:
    def migrate(self, excel_path, json_path, sheet_name=None):
        # Excel読み込み（複数シート対応）
        if sheet_name:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            data = df.to_dict('records')
        else:
            xl_file = pd.ExcelFile(excel_path)
            data = {}
            for sheet in xl_file.sheet_names:
                df = pd.read_excel(excel_path, sheet_name=sheet)
                data[sheet] = df.to_dict('records')
        
        # JSON出力（日本語対応）
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return {'sheets_processed': len(data) if isinstance(data, dict) else 1}
```

### 3. データベース間同期
```python
class DatabaseSync:
    def __init__(self, source_db, target_db):
        self.source_engine = create_engine(source_db)
        self.target_engine = create_engine(target_db)
    
    def sync_table(self, table_name, mode='full'):
        if mode == 'full':
            # フル同期
            df = pd.read_sql_table(table_name, self.source_engine)
            df.to_sql(table_name, self.target_engine, 
                     if_exists='replace', index=False)
        
        elif mode == 'incremental':
            # 差分同期
            last_sync = self.get_last_sync_timestamp(table_name)
            query = f"""
                SELECT * FROM {table_name} 
                WHERE updated_at > '{last_sync}'
            """
            df = pd.read_sql_query(query, self.source_engine)
            
            if not df.empty:
                df.to_sql(table_name, self.target_engine,
                         if_exists='append', index=False)
        
        return {'rows_synced': len(df)}
```

## データ変換ルール

### フィールド変換
```python
class FieldTransformer:
    def transform(self, data, rules):
        """
        変換ルール例:
        rules = {
            'name_conversion': {
                'source_field': 'customer_name',
                'target_field': 'client_name',
                'transform': 'uppercase'
            },
            'date_format': {
                'source_field': 'order_date',
                'format_from': '%Y/%m/%d',
                'format_to': '%Y-%m-%d'
            },
            'value_mapping': {
                'source_field': 'status',
                'mapping': {
                    '0': 'inactive',
                    '1': 'active'
                }
            }
        }
        """
        transformed = data.copy()
        
        for rule_name, rule in rules.items():
            if rule['type'] == 'rename':
                transformed = transformed.rename(columns={
                    rule['source']: rule['target']
                })
            
            elif rule['type'] == 'format':
                transformed[rule['field']] = transformed[rule['field']].apply(
                    lambda x: self.format_value(x, rule['format'])
                )
            
            elif rule['type'] == 'mapping':
                transformed[rule['field']] = transformed[rule['field']].map(
                    rule['mapping']
                )
        
        return transformed
```

### 名前のローカライズ
```python
class NameLocalizer:
    def localize(self, data, lang='ja'):
        """日本語ローカライズ"""
        localization_map = {
            'en_to_ja': {
                'customer_id': '顧客ID',
                'order_date': '注文日',
                'amount': '金額',
                'status': 'ステータス',
                'description': '説明'
            },
            'ja_to_en': {
                '顧客ID': 'customer_id',
                '注文日': 'order_date',
                '金額': 'amount',
                'ステータス': 'status',
                '説明': 'description'
            }
        }
        
        if lang == 'ja':
            return data.rename(columns=localization_map['en_to_ja'])
        else:
            return data.rename(columns=localization_map['ja_to_en'])
```

## オフラインデータ生成

### JSONファイル生成
```javascript
// オフライン用データ構造
const offlineDataGenerator = {
    generateOfflineData(sourceData) {
        return {
            metadata: {
                version: '1.0',
                generated: new Date().toISOString(),
                recordCount: sourceData.length,
                checksum: this.calculateChecksum(sourceData)
            },
            
            data: sourceData.map(record => ({
                ...record,
                _offline_id: this.generateOfflineId(),
                _sync_status: 'pending',
                _modified_at: null
            })),
            
            indexes: {
                byId: this.createIndexById(sourceData),
                byCategory: this.createIndexByCategory(sourceData)
            },
            
            cache: {
                aggregates: this.calculateAggregates(sourceData),
                lookups: this.createLookupTables(sourceData)
            }
        };
    }
};
```

## データ検証

### 検証ルール
```python
class DataValidator:
    def validate(self, data, schema):
        """
        スキーマ例:
        schema = {
            'customer_id': {'type': 'integer', 'required': True},
            'email': {'type': 'email', 'required': True},
            'age': {'type': 'integer', 'min': 0, 'max': 150},
            'status': {'type': 'enum', 'values': ['active', 'inactive']}
        }
        """
        errors = []
        
        for index, row in data.iterrows():
            for field, rules in schema.items():
                value = row.get(field)
                
                # 必須チェック
                if rules.get('required') and pd.isna(value):
                    errors.append({
                        'row': index,
                        'field': field,
                        'error': 'Required field is missing'
                    })
                
                # 型チェック
                if not pd.isna(value):
                    if rules['type'] == 'email':
                        if not self.is_valid_email(value):
                            errors.append({
                                'row': index,
                                'field': field,
                                'error': 'Invalid email format'
                            })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'error_count': len(errors)
        }
```

## 出力例

### 移行完了レポート
```markdown
# データ移行レポート

## 実行概要
- 移行元: customers.csv (UTF-8)
- 移行先: PostgreSQL (customers_table)
- 実行日時: 2025-08-17 10:30:00

## 処理結果
✅ 総レコード数: 10,000
✅ 成功: 9,950
⚠️ スキップ: 45
❌ エラー: 5

## データ品質
- 重複除去: 120件
- NULL値補完: 230件
- 型変換: 1,500件
- 文字コード変換: 全件

## パフォーマンス
- 処理時間: 45秒
- スループット: 222 records/sec
- メモリ使用量: 125MB

## 検証結果
- スキーマ適合率: 99.5%
- データ整合性: ✅ OK
- 外部キー制約: ✅ OK

## エラー詳細
1. Row 1234: Invalid date format
2. Row 2345: Duplicate primary key
3. Row 3456: Foreign key violation
```

## エラーハンドリング
| エラー | 原因 | 対処法 |
|--------|------|--------|
| 文字化け | エンコーディング | UTF-8-SIG使用 |
| 型エラー | データ型不一致 | 自動型推論 |
| メモリ不足 | 大量データ | チャンク処理 |
| 接続エラー | DB接続失敗 | リトライ機構 |

## 管理責任
- **管理部門**: システム開発部
- **カスタマイズ**: データ形式と要件に応じて調整

## 関連コマンド
- `/csv-migration` - CSV特化移行
- `/database-optimize` - DB最適化
- `/field-transform` - フィールド変換
- `/name-localize` - 名前ローカライズ

---
*このコマンドはシステム開発部が管理します。*