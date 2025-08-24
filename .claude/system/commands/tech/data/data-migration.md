# /data-migration - 

## 
CSVExcelJSONXML

## 
```bash
/data-migration [source_type] [target_type] [options]

# 
/data-migration csv database --mapping=auto
/data-migration excel json --transform=custom
/data-migration database database --sync=realtime
/data-migration csv offline --optimize
```

## 

### 
- `source_type`: 
  - `csv` - CSV
  - `excel` - Excel
  - `json` - JSON
  - `xml` - XML
  - `database` - 
  - `api` - REST API

- `target_type`: 
  - `database` - 
  - `json` - JSON
  - `offline` - 
  - `api` - REST API
  - `table` - 

### 
- `--mapping`: auto, manual, template
- `--transform`: 
- `--validate`: 
- `--sync`: onetime, realtime, scheduled
- `--optimize`: 

## 

### 1. CSV -> 
```python
import pandas as pd
from sqlalchemy import create_engine

class CsvToDatabase:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
    
    def migrate(self, csv_path, table_name, mapping=None):
        # CSV
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # 
        df = self.optimize_dtypes(df)
        
        # 
        if mapping:
            df = df.rename(columns=mapping)
        
        # 
        df = self.clean_data(df)
        
        # 
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
        """SUCCESS"""
        for col in df.columns:
            col_type = df[col].dtype
            
            if col_type != 'object':
                continue
                
            # 
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
            
            # SUCCESS
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass
        
        return df
```

### 2. Excel -> JSONSUCCESS
```python
class ExcelToJson:
    def migrate(self, excel_path, json_path, sheet_name=None):
        # Excel
        if sheet_name:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            data = df.to_dict('records')
        else:
            xl_file = pd.ExcelFile(excel_path)
            data = {}
            for sheet in xl_file.sheet_names:
                df = pd.read_excel(excel_path, sheet_name=sheet)
                data[sheet] = df.to_dict('records')
        
        # JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return {'sheets_processed': len(data) if isinstance(data, dict) else 1}
```

### 3. 
```python
class DatabaseSync:
    def __init__(self, source_db, target_db):
        self.source_engine = create_engine(source_db)
        self.target_engine = create_engine(target_db)
    
    def sync_table(self, table_name, mode='full'):
        if mode == 'full':
            # 
            df = pd.read_sql_table(table_name, self.source_engine)
            df.to_sql(table_name, self.target_engine, 
                     if_exists='replace', index=False)
        
        elif mode == 'incremental':
            # 
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

## 

### 
```python
class FieldTransformer:
    def transform(self, data, rules):
        """
        :
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

### 
```python
class NameLocalizer:
    def localize(self, data, lang='ja'):
        """"""
        localization_map = {
            'en_to_ja': {
                'customer_id': 'ID',
                'order_date': '',
                'amount': '',
                'status': '',
                'description': ''
            },
            'ja_to_en': {
                'ID': 'customer_id',
                '': 'order_date',
                '': 'amount',
                '': 'status',
                '': 'description'
            }
        }
        
        if lang == 'ja':
            return data.rename(columns=localization_map['en_to_ja'])
        else:
            return data.rename(columns=localization_map['ja_to_en'])
```

## 

### JSON
```javascript
// 
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

## 

### 
```python
class DataValidator:
    def validate(self, data, schema):
        """
        :
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
                
                # ERROR
                if rules.get('required') and pd.isna(value):
                    errors.append({
                        'row': index,
                        'field': field,
                        'error': 'Required field is missing'
                    })
                
                # ERROR
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

## ERROR

### ERROR
```markdown
# ERROR

## ERROR
- ERROR: customers.csv (UTF-8)
- : PostgreSQL (customers_table)
- WARNING: 2025-08-17 10:30:00

## ERROR
[OK] ERROR: 10,000
[OK] ERROR: 9,950
[WARNING] ERROR: 45
[ERROR] ERROR: 5

## ERROR
- ERROR: 120ERROR
- NULLERROR: 230ERROR
- ERROR: 1,500ERROR
- : 

## 
- : 45
- : 222 records/sec
- : 125MB

## 
- : 99.5%
- : [OK] OK
- : [OK] OK

## 
1. Row 1234: Invalid date format
2. Row 2345: Duplicate primary key
3. Row 3456: Foreign key violation
```

## 
|  |  |  |
|--------|------|--------|
|  |  | UTF-8-SIG |
|  |  |  |
|  |  |  |
|  | DB |  |

## 
- ****: 
- ****: 

## 
- `/csv-migration` - CSV
- `/database-optimize` - DB
- `/field-transform` - 
- `/name-localize` - 

---
**