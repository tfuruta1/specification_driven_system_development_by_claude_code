# フルスタック連携統合ガイド

## 🎯 概要

Vue3 + Axios フロントエンドと FastAPI + SQLAlchemy バックエンド間の完全連携を実現するための統合ガイドです。開発者が効率的にフルスタック開発を行うための実践的な手順を提供します。

## 🚀 クイックスタート

### 1. 連携コマンドの基本使用法

#### フロントエンド仕様からバックエンド生成
```bash
# Vue3コンポーネントからAPI要求を生成
cd .claude_vue3_axios
/backend-sync spec_to_backend --target_feature="products" --validation_level="full"

# 生成された要求を確認
cat .tmp/api_sync/backend_requirements.md

# バックエンド側で実装
cd ../claude_python_sqlAlckemy
/frontend-sync api_to_frontend --target_module="products" --output_format="javascript"
```

#### 既存バックエンドからフロントエンド生成
```bash
# FastAPI仕様からVue3クライアント生成
cd .claude_python_sqlAlckemy
/frontend-sync api_to_frontend --target_module="all" --output_format="javascript"

# 生成されたクライアントを確認
ls .tmp/frontend_sync/
- types/api.js            # JavaScript型定義（JSDoc）
- services/apiClient.js   # Axiosクライアント
- stores/productStore.js  # Piniaストア
- components/             # Vue3コンポーマント

# フロントエンド側で統合
cd ../claude_vue3_axios
cp -r ../claude_python_sqlAlckemy/.tmp/frontend_sync/* src/
```

### 2. 完全双方向同期
```bash
# フロントエンド・バックエンド完全同期
cd .claude_vue3_axios
/backend-sync full_sync --validation_level="strict"

cd ../claude_python_sqlAlckemy
/frontend-sync full_stack_sync --sync_depth="comprehensive"
```

## 📋 開発ワークフロー

### Phase 1: 要件定義・設計フェーズ

#### 1. フロントエンド要件定義
```bash
cd .claude_vue3_axios

# ユーザーストーリー・UI要件定義
/requirements --target="product_management" --user_role="operator"

# Vue3コンポーネント設計
/design --component_type="crud" --entity="Product"
```

#### 2. バックエンドAPI仕様生成
```bash
# Vue3要件からAPI仕様を生成
/backend-sync spec_to_backend --target_feature="product_management" --sync_direction="frontend_to_backend"

# 生成された仕様を確認
cat .tmp/api_sync/openapi_spec_*.json
cat .tmp/api_sync/backend_requirements.md
```

#### 3. バックエンド実装
```bash
cd ../claude_python_sqlAlckemy

# API要求を読み込んで実装
/design --api_spec="../claude_vue3_axios/.tmp/api_sync/openapi_spec.json"

# SQLAlchemyモデル実装
/implement --target="models" --entity="Product"

# FastAPIエンドポイント実装
/implement --target="api" --entity="Product"
```

### Phase 2: 実装・統合フェーズ

#### 1. バックエンドからフロントエンドクライアント生成
```bash
cd .claude_python_sqlAlckemy

# 実装完了後、フロントエンドクライアント生成
/frontend-sync api_to_frontend --target_module="products" --output_format="javascript"

# 型定義・クライアントコード出力確認
ls .tmp/frontend_sync/
```

#### 2. フロントエンド統合
```bash
cd ../claude_vue3_axios

# 生成されたクライアントコードを統合
cp -r ../claude_python_sqlAlckemy/.tmp/frontend_sync/types/* src/types/
cp -r ../claude_python_sqlAlckemy/.tmp/frontend_sync/services/* src/services/
cp -r ../claude_python_sqlAlckemy/.tmp/frontend_sync/stores/* src/stores/

# Vue3コンポーネントの自動統合
/integrate --generated_code="../claude_python_sqlAlckemy/.tmp/frontend_sync/components"
```

#### 3. バリデーション同期
```bash
# バリデーションルール統一
cd .claude_vue3_axios
/backend-sync validation_sync --target_feature="all"

cd ../claude_python_sqlAlckemy
/frontend-sync validation_sync --target_module="all" --validation_level="strict"
```

### Phase 3: テスト・検証フェーズ

#### 1. 統合テスト実行
```bash
# API契約テスト
cd .claude_python_sqlAlckemy
python .tmp/integration_test_examples.py

# フロントエンド・バックエンド統合テスト
cd ../claude_vue3_axios
npm run test:integration
```

#### 2. E2Eテスト
```bash
# Playwrightによる E2Eテスト
cd .claude_vue3_axios
npx playwright test --config=playwright.integration.config.js
```

## 🔧 詳細設定ガイド

### 1. 環境設定

#### バックエンド環境（.env）
```env
# FastAPI設定
APP_NAME=Manufacturing Quality Management API
APP_VERSION=1.0.0
DEBUG=true

# データベース
DATABASE_URL=mssql+pyodbc://user:password@localhost/manufacturing_db?driver=ODBC+Driver+17+for+SQL+Server

# CORS設定（フロントエンド連携用）
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# WebSocket（リアルタイム同期用）
WEBSOCKET_ENABLED=true
WEBSOCKET_PATH=/ws

# 認証
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

#### フロントエンド環境（.env.local）
```env
# API接続
VUE_APP_API_BASE_URL=http://localhost:9995
VUE_APP_WS_URL=ws://localhost:9995/ws

# 認証
VUE_APP_TOKEN_REFRESH_THRESHOLD=300000

# 開発設定
VUE_APP_DEBUG=true
VUE_APP_MOCK_API=false
```

### 2. パッケージ依存関係

#### バックエンド（requirements.txt）
```txt
# フルスタック連携追加分
fastapi-websocket==0.1.1
asyncio-mqtt==0.11.1
pydantic[email]==1.10.2
```

#### フロントエンド（package.json）
```json
{
  "dependencies": {
    "@vueuse/core": "^10.0.0",
    "zod": "^3.21.0",
    "lodash": "^4.17.21",
    "socket.io-client": "^4.7.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.35.0",
    "jsdoc": "^4.0.2",
    "eslint-plugin-jsdoc": "^46.4.0"
  }
}
```

### 3. 自動化スクリプト設定

#### package.json scripts
```json
{
  "scripts": {
    "dev:fullstack": "concurrently \"npm run dev\" \"cd ../claude_python_sqlAlckemy && python main.py\"",
    "sync:backend": "node scripts/sync-with-backend.js",
    "test:integration": "playwright test --config=integration.config.js",
    "build:with-sync": "npm run sync:backend && npm run build"
  }
}
```

#### 同期スクリプト（scripts/sync-with-backend.js）
```javascript
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

async function syncWithBackend() {
  console.log('🔄 バックエンドとの同期を開始...');
  
  try {
    // バックエンドから最新のOpenAPI仕様を取得
    execSync('curl http://localhost:9995/openapi.json > .tmp/backend_openapi.json');
    
    // 型定義の更新（JSDoc形式）
    execSync('node scripts/openapi-to-jsdoc.js .tmp/backend_openapi.json src/types/api.js');
    
    // Axiosクライアントの再生成
    execSync('node scripts/generate-api-client.js');
    
    console.log('✅ 同期完了');
  } catch (error) {
    console.error('❌ 同期エラー:', error.message);
    process.exit(1);
  }
}

syncWithBackend();
```

## 🧪 テスト戦略

### 1. ユニットテスト

#### バックエンド
```python
# tests/test_product_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_product():
    """製品作成APIテスト"""
    product_data = {
        "product_code": "TEST001",
        "product_name": "テスト製品",
        "price": 1000.00
    }
    
    response = client.post("/api/v1/products", json=product_data)
    assert response.status_code == 201
    
    created_product = response.json()
    assert created_product["product_code"] == "TEST001"
    assert created_product["product_name"] == "テスト製品"
```

#### フロントエンド
```javascript
// tests/unit/ProductStore.spec.js
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProductStore } from '@/stores/productStore'

describe('ProductStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('製品を正常に作成できる', async () => {
    const store = useProductStore()
    
    const productData = {
      product_code: 'TEST001',
      product_name: 'テスト製品'
    }
    
    await store.createProduct(productData)
    
    expect(store.products).toHaveLength(1)
    expect(store.products[0].product_code).toBe('TEST001')
  })
})
```

### 2. 統合テスト

#### API契約テスト
```python
# tests/integration/test_api_contract.py
async def test_product_api_contract():
    """製品API契約テスト"""
    # OpenAPI仕様に基づくテスト実行
    contract_test = SchemaContractTest('.tmp/openapi_spec.json')
    result = await contract_test.test_all_endpoints_contract()
    
    assert result['passed'] >= result['total_tests'] * 0.95  # 95%以上の成功率
```

#### フロントエンド・バックエンド統合テスト
```javascript
// tests/integration/product-flow.spec.js
import { test, expect } from '@playwright/test';

test('製品管理フルフロー', async ({ page }) => {
  // ログイン
  await page.goto('/login');
  await page.fill('[data-testid=username]', 'testuser');
  await page.fill('[data-testid=password]', 'testpass');
  await page.click('[data-testid=login-button]');
  
  // 製品作成
  await page.goto('/products');
  await page.click('[data-testid=create-product]');
  await page.fill('[data-testid=product-code]', 'TEST001');
  await page.fill('[data-testid=product-name]', 'テスト製品');
  await page.click('[data-testid=save-product]');
  
  // 作成確認
  await expect(page.locator('text=TEST001')).toBeVisible();
  
  // バックエンドでの確認
  const response = await page.request.get('/api/v1/products?search=TEST001');
  const products = await response.json();
  expect(products.items).toHaveLength(1);
});
```

## 🔍 トラブルシューティング

### よくある問題と解決方法

#### 1. 型定義の不整合
```bash
# 問題: JavaScript型エラーが発生
# 解決: スキーマ同期の実行
cd .claude_vue3_axios
/backend-sync validation_sync --target_feature="all"

# 生成された型定義を確認
cat .tmp/api_sync/frontend_types.js
```

#### 2. CORS エラー
```python
# バックエンド CORS設定確認
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3. WebSocket 接続エラー
```javascript
// フロントエンド WebSocket接続確認
const ws = new WebSocket('ws://localhost:9995/ws');
ws.onopen = () => console.log('WebSocket connected');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

#### 4. バリデーションの不一致
```bash
# バリデーション同期の実行
cd .claude_python_sqlAlckemy
/frontend-sync validation_sync --target_module="all" --validation_level="strict"

# 生成されたバリデーションルールを確認
cat .tmp/frontend_sync/validation_rules.json
```

## 📊 監視・メトリクス

### 1. 同期品質の監視
```javascript
// 同期品質チェック
import { SchemaSyncValidator } from '@/utils/sync-validation';

const validator = new SchemaSyncValidator();
const result = await validator.validateSchemaConsistency(openApiSpec, frontendTypes);

console.log(`Schema consistency: ${result.summary.consistency_rate}%`);
```

### 2. パフォーマンス監視
```python
# バックエンド パフォーマンス監視
from prometheus_client import Counter, Histogram

api_requests = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
response_time = Histogram('api_response_time_seconds', 'API response time')
```

## 🚀 デプロイメント

### 1. 開発環境
```bash
# Docker compose での統合環境
version: '3.8'
services:
  backend:
    build: ./claude_python_sqlAlckemy
    ports:
      - "9995:9995"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/manufacturing
  
  frontend:
    build: ./claude_vue3_axios
    ports:
      - "3000:3000"
    environment:
      - VUE_APP_API_BASE_URL=http://backend:9995
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=manufacturing
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

### 2. 本番環境
```bash
# CI/CD パイプライン例
name: Full Stack Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        run: |
          cd .claude_python_sqlAlckemy
          python -m pytest tests/integration/
          cd ../claude_vue3_axios
          npm run test:integration
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy backend
        run: |
          cd .claude_python_sqlAlckemy
          docker build -t backend:latest .
          kubectl apply -f k8s/
      
      - name: Deploy frontend
        run: |
          cd .claude_vue3_axios
          npm run build:with-sync
          aws s3 sync dist/ s3://frontend-bucket/
```

## 🎯 ベストプラクティス

### 1. 開発ワークフロー
- 常にフロントエンド要件を先に定義
- バックエンド実装前にAPI仕様を合意
- 定期的な同期（日次）を実施
- テスト駆動開発（TDD）の実践

### 2. コード品質
- 自動生成コードの直接編集を避ける
- カスタマイズは継承・拡張で対応
- ESLint・Prettier による自動整形
- JSDocによるJavaScript型チェック
- mypy によるPython型チェック

### 3. 運用・保守
- 同期履歴の定期的なクリーンアップ
- エラーログの監視・アラート設定
- パフォーマンスメトリクスの定期確認
- セキュリティ監査の実施

このガイドにより、Vue3 + FastAPI間の効率的なフルスタック開発が実現できます。