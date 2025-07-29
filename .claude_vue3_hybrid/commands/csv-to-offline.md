# /csv-to-offline - CSVをオフライン用JSONデータに変換・セット

## 概要

CSVファイルをハイブリッド接続システムのオフライン用JSONデータに変換し、offline/data/ディレクトリに配置するコマンドです。
データ検証、型変換、同期準備を自動化します。

## 使用方法

```bash
# 基本的な使用方法
/csv-to-offline [csv_file] [entity_type] [options]

# 使用例
/csv-to-offline users_data.csv users --validate --sync-ready
/csv-to-offline products.csv products --transform-fields --japanese-keys
/csv-to-offline sales_data.csv sales --batch-size=1000 --backup-existing
```

## パラメータ

### 必須パラメータ
- `csv_file`: 変換対象のCSVファイルパス
- `entity_type`: エンティティタイプ (users, products, orders等)

### オプション
- `--validate`: データバリデーション実行
- `--sync-ready`: 同期用メタデータ付与
- `--transform-fields`: フィールド変換実行
- `--japanese-keys`: 日本語キー名対応
- `--batch-size=N`: バッチ処理サイズ
- `--backup-existing`: 既存データをバックアップ
- `--delimiter=tab`: 区切り文字指定
- `--encoding=utf8`: エンコーディング指定
- `--mapping-file`: フィールドマッピングファイル

## データ変換プロセス

### 1. CSV読み込み・パース

```javascript
// CSV パース処理
const parseCSVToJSON = async (csvFile, options) => {
  const csvContent = await fs.readFile(csvFile, options.encoding || 'utf8');
  const delimiter = options.delimiter === 'tab' ? '\t' : ',';
  
  const lines = csvContent.split('\n').filter(line => line.trim());
  const headers = lines[0].split(delimiter).map(h => h.trim().replace(/"/g, ''));
  
  const records = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i], delimiter);
    
    if (values.length !== headers.length) {
      console.warn(`行 ${i + 1}: カラム数不一致 (期待: ${headers.length}, 実際: ${values.length})`);
      continue;
    }
    
    const record = {};
    headers.forEach((header, index) => {
      record[header] = values[index];
    });
    
    records.push(record);
  }
  
  return { headers, records };
};

const parseCSVLine = (line, delimiter) => {
  const values = [];
  let current = '';
  let inQuotes = false;
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++; // Skip next quote
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === delimiter && !inQuotes) {
      values.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  
  values.push(current.trim());
  return values;
};
```

### 2. データ型変換・正規化

```javascript
// データ変換ルール
const transformRecord = (record, entityType, mappings) => {
  const transformed = {
    id: generateOfflineId(),
    _sync_status: 'offline',
    _last_modified: new Date().toISOString(),
    _operation: 'import'
  };
  
  for (const [key, value] of Object.entries(record)) {
    const mapping = mappings[key] || { type: 'string', target: key };
    const transformedValue = convertValue(value, mapping);
    
    if (transformedValue !== null) {
      transformed[mapping.target || key] = transformedValue;
    }
  }
  
  return transformed;
};

const convertValue = (value, mapping) => {
  if (!value || value.trim() === '') {
    return mapping.default || null;
  }
  
  const trimmedValue = value.trim();
  
  switch (mapping.type) {
    case 'integer':
      const intValue = parseInt(trimmedValue, 10);
      return isNaN(intValue) ? null : intValue;
      
    case 'float':
      const floatValue = parseFloat(trimmedValue);
      return isNaN(floatValue) ? null : floatValue;
      
    case 'boolean':
      return ['true', '1', 'yes', 'y', 't', 'はい', '有効'].includes(trimmedValue.toLowerCase());
      
    case 'date':
      try {
        const date = new Date(trimmedValue);
        return isNaN(date.getTime()) ? null : date.toISOString().split('T')[0];
      } catch {
        return null;
      }
      
    case 'datetime':
      try {
        const date = new Date(trimmedValue);
        return isNaN(date.getTime()) ? null : date.toISOString();
      } catch {
        return null;
      }
      
    case 'json':
      try {
        return JSON.parse(trimmedValue);
      } catch {
        return trimmedValue; // Invalid JSON as string
      }
      
    case 'email':
      const emailRegex = /^[^@]+@[^@]+\.[^@]+$/;
      return emailRegex.test(trimmedValue) ? trimmedValue.toLowerCase() : null;
      
    case 'phone':
      // 電話番号正規化（日本）
      return normalizePhoneNumber(trimmedValue);
      
    case 'string':
    default:
      return mapping.transform ? mapping.transform(trimmedValue) : trimmedValue;
  }
};

const generateOfflineId = () => {
  return `offline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};
```

## 生成される成果物

### 1. オフライン用JSONデータファイル

```json
// offline/data/users.json

[
  {
    "id": "offline_1738144200000_k9j3l2m4n",
    "user_id": 1,
    "user_name": "yamada_taro",
    "email": "yamada@example.com",
    "full_name": "山田太郎",
    "birth_date": "1985-05-15",
    "is_active": true,
    "created_at": "2023-01-15T09:30:00.000Z",
    "updated_at": "2025-01-29T10:30:00.000Z",
    "department": "開発部",
    "metadata": {
      "source": "csv_import",
      "original_row": 2,
      "import_date": "2025-01-29T10:30:00.000Z"
    },
    "_sync_status": "offline",
    "_last_modified": "2025-01-29T10:30:00.000Z",
    "_operation": "import"
  },
  {
    "id": "offline_1738144200001_p5q7r8s2t",
    "user_id": 2,
    "user_name": "tanaka_hanako",
    "email": "tanaka@example.com",
    "full_name": "田中花子",
    "birth_date": "1990-12-03",
    "is_active": true,
    "created_at": "2023-02-20T14:15:00.000Z",
    "updated_at": "2025-01-29T10:30:00.000Z",
    "department": "営業部",
    "metadata": {
      "source": "csv_import",
      "original_row": 3,
      "import_date": "2025-01-29T10:30:00.000Z"
    },
    "_sync_status": "offline",
    "_last_modified": "2025-01-29T10:30:00.000Z",
    "_operation": "import"
  }
]
```

### 2. 同期キューエントリ

```json
// offline/sync/sync_queue.json

[
  {
    "id": "sync_1738144200000_a1b2c3d4e",
    "entity_type": "users",
    "entity_id": "offline_1738144200000_k9j3l2m4n",
    "operation": "create",
    "data": {
      "user_id": 1,
      "user_name": "yamada_taro",
      "email": "yamada@example.com",
      // ... other fields
    },
    "created_at": "2025-01-29T10:30:00.000Z",
    "status": "pending",
    "retry_count": 0,
    "priority": "normal",
    "metadata": {
      "source": "csv_import",
      "batch_id": "batch_1738144200000"
    }
  }
]
```

### 3. 変換ログ・レポート

```json
// logs/csv_import_users_20250129_103000.json

{
  "import_session": {
    "id": "import_1738144200000",
    "source_file": "users_data.csv",
    "entity_type": "users",
    "started_at": "2025-01-29T10:30:00.000Z",
    "completed_at": "2025-01-29T10:32:15.000Z",
    "duration_ms": 135000
  },
  
  "statistics": {
    "total_records": 10000,
    "successful_imports": 9850,
    "failed_imports": 150,
    "validation_errors": 120,
    "transformation_errors": 30,
    "success_rate": 0.985
  },
  
  "data_quality": {
    "missing_data_analysis": {
      "email": { "missing_count": 5, "missing_rate": 0.0005 },
      "birth_date": { "missing_count": 45, "missing_rate": 0.0045 },
      "department": { "missing_count": 12, "missing_rate": 0.0012 }
    },
    "format_validation": {
      "email_format_errors": 15,
      "date_format_errors": 8,
      "phone_format_errors": 22
    },
    "duplicate_analysis": {
      "email_duplicates": 3,
      "user_name_duplicates": 0
    }
  },
  
  "transformation_summary": {
    "field_mappings": {
      "ユーザーID": "user_id",
      "ユーザー名": "user_name", 
      "メールアドレス": "email",
      "氏名": "full_name",
      "生年月日": "birth_date",
      "アクティブ": "is_active",
      "作成日時": "created_at",
      "部署": "department"
    },
    "type_conversions": {
      "integer_conversions": 1,
      "boolean_conversions": 1,
      "date_conversions": 2,
      "email_normalizations": 1
    }
  },
  
  "errors": [
    {
      "row": 157,
      "field": "email",
      "value": "invalid-email",
      "error": "Invalid email format",
      "action": "skipped"
    },
    {
      "row": 289,
      "field": "birth_date", 
      "value": "1999/13/45",
      "error": "Invalid date",
      "action": "set_to_null"
    }
  ],
  
  "warnings": [
    {
      "message": "High number of missing birth_date values (4.5%)",
      "recommendation": "Consider setting default value or validation rule"
    },
    {
      "message": "Some user_name values contain special characters",
      "recommendation": "Consider normalization rules"
    }
  ],
  
  "file_outputs": {
    "main_data": "offline/data/users.json",
    "sync_queue": "offline/sync/sync_queue.json", 
    "backup": "offline/backup/2025-01-29T10-30-00/users_backup.json",
    "error_records": "logs/csv_import_errors_users_20250129.csv"
  }
}
```

### 4. フィールドマッピング設定

```json
// mappings/users_field_mapping.json

{
  "entity_type": "users",
  "csv_source": "users_data.csv",
  "created_at": "2025-01-29T10:30:00.000Z",
  
  "field_mappings": {
    "ユーザーID": {
      "target": "user_id",
      "type": "integer",
      "required": true,
      "validation": "^[0-9]+$"
    },
    "ユーザー名": {
      "target": "user_name",
      "type": "string",
      "required": true,
      "transform": "lowercase_alphanumeric",
      "max_length": 50
    },
    "メールアドレス": {
      "target": "email",
      "type": "email",
      "required": true,
      "transform": "lowercase_trim"
    },
    "氏名": {
      "target": "full_name",
      "type": "string",
      "required": false,
      "max_length": 100
    },
    "生年月日": {
      "target": "birth_date",
      "type": "date",
      "required": false,
      "format": "YYYY-MM-DD"
    },
    "アクティブ": {
      "target": "is_active",
      "type": "boolean",
      "default": true,
      "true_values": ["有効", "true", "1", "はい", "○"],
      "false_values": ["無効", "false", "0", "いいえ", "×"]
    },
    "作成日時": {
      "target": "created_at",
      "type": "datetime",
      "required": false,
      "default": "current_timestamp"
    },
    "部署": {
      "target": "department",
      "type": "string",
      "required": false,
      "normalize": true
    }
  },
  
  "transformation_rules": {
    "lowercase_alphanumeric": {
      "description": "英数字小文字化、特殊文字除去",
      "pattern": "/[^a-z0-9_]/g",
      "replacement": ""
    },
    "lowercase_trim": {
      "description": "小文字化、前後空白除去",
      "steps": ["trim", "toLowerCase"]
    },
    "normalize": {
      "description": "日本語正規化",
      "steps": ["trim", "normalize_japanese"]
    }
  },
  
  "validation_rules": {
    "global": {
      "max_errors_per_record": 3,
      "skip_invalid_records": false,
      "log_all_errors": true
    },
    "entity_specific": {
      "unique_fields": ["user_id", "email"],
      "required_combinations": [["user_name", "email"]]
    }
  },
  
  "sync_settings": {
    "auto_sync": false,
    "sync_priority": "normal",
    "batch_sync": true,
    "batch_size": 100
  }
}
```

## バッチ処理・エラーハンドリング

### 大容量CSV処理

```javascript
// ストリーミング処理
const processLargeCSV = async (csvFile, entityType, options) => {
  const batchSize = options.batchSize || 1000;
  const results = {
    processed: 0,
    successful: 0,
    errors: []
  };
  
  const outputPath = path.join('offline', 'data', `${entityType}.json`);
  
  // 既存データ読み込み
  let existingData = [];
  try {
    existingData = JSON.parse(await fs.readFile(outputPath, 'utf8'));
  } catch {
    // ファイルが存在しない場合は空配列
  }
  
  // バックアップ作成
  if (options.backupExisting && existingData.length > 0) {
    const backupPath = `offline/backup/${new Date().toISOString().replace(/[:.]/g, '-')}/${entityType}_backup.json`;
    await fs.mkdir(path.dirname(backupPath), { recursive: true });
    await fs.writeFile(backupPath, JSON.stringify(existingData, null, 2));
  }
  
  // ストリーミング処理
  const readStream = fs.createReadStream(csvFile);
  const parser = csv({
    delimiter: options.delimiter === 'tab' ? '\t' : ',',
    headers: true,
    skipEmptyLines: true
  });
  
  let batch = [];
  let processedData = [...existingData];
  
  return new Promise((resolve, reject) => {
    readStream
      .pipe(parser)
      .on('data', async (record) => {
        batch.push(record);
        results.processed++;
        
        if (batch.length >= batchSize) {
          try {
            const transformedBatch = await processBatch(batch, entityType, options);
            processedData.push(...transformedBatch.successful);
            results.successful += transformedBatch.successful.length;
            results.errors.push(...transformedBatch.errors);
            
            // 中間保存
            await fs.writeFile(outputPath, JSON.stringify(processedData, null, 2));
            
            batch = [];
            console.log(`処理済み: ${results.processed} / 成功: ${results.successful}`);
          } catch (error) {
            results.errors.push({ batch: results.processed, error: error.message });
          }
        }
      })
      .on('end', async () => {
        // 残りのバッチ処理
        if (batch.length > 0) {
          try {
            const transformedBatch = await processBatch(batch, entityType, options);
            processedData.push(...transformedBatch.successful);
            results.successful += transformedBatch.successful.length;
            results.errors.push(...transformedBatch.errors);
          } catch (error) {
            results.errors.push({ batch: 'final', error: error.message });
          }
        }
        
        // 最終保存
        await fs.writeFile(outputPath, JSON.stringify(processedData, null, 2));
        
        resolve(results);
      })
      .on('error', reject);
  });
};
```

## 実行例

```bash
# ユーザーデータをオフライン用JSONに変換
/csv-to-offline users_data.csv users --validate --sync-ready --japanese-keys

# 出力ファイル:
# offline/data/users.json (メインデータ)
# offline/sync/sync_queue.json (同期キュー)
# logs/csv_import_users_20250129_103000.json (インポートログ)
# mappings/users_field_mapping.json (フィールドマッピング)
```

このコマンドにより、CSVデータを効率的にオフライン対応JSONデータに変換できます。