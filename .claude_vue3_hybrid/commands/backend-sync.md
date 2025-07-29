# /backend-sync - ハイブリッド・バックエンド連携コマンド

## 目的
ハイブリッド接続対応Vue3アプリケーションから複数バックエンド（REST API・Supabase・オフライン）への仕様連携・API同期を自動化し、フルスタック開発における一貫性と効率性を確保します。

## 対象システム
- **フロントエンド**: Vue.js 3 + Composition API + Axios + Pinia（ハイブリッド接続対応）
- **プライマリバックエンド**: FastAPI + SQLAlchemy + SQL Server / PostgreSQL
- **セカンダリバックエンド**: Supabase（PostgreSQL + Auth + Realtime）
- **オフラインストレージ**: JSONファイルベース（./data/offline/）
- **連携プロトコル**: REST API + JSON Schema + OpenAPI 3.0 + Supabase SDK

## 入力パラメータ
- **必須**: `$SYNC_TYPE` - 同期タイプ（spec_to_backends, hybrid_consume, full_hybrid_sync, validation_sync）
- **任意**: `$TARGET_FEATURE` - 対象機能（authentication, products, orders, reports, all）
- **任意**: `$SYNC_DIRECTION` - 同期方向（frontend_to_backends, backends_to_frontend, bidirectional）
- **任意**: `$BACKEND_PRIORITY` - バックエンド優先順位（api_first, supabase_first, offline_first）
- **任意**: `$VALIDATION_LEVEL` - 検証レベル（basic, full, strict）

## 出力ファイル
- **API仕様書**: `.tmp/hybrid_sync/openapi_spec_[timestamp].json`
- **Supabase設定**: `.tmp/hybrid_sync/supabase_schema.sql`
- **型定義ファイル**: `.tmp/hybrid_sync/frontend_types.js`
- **ハイブリッドクライアント**: `.tmp/hybrid_sync/hybrid_client.js`
- **Piniaストア**: `.tmp/hybrid_sync/stores/[feature]Store.js`
- **JSONファイル設定**: `.tmp/hybrid_sync/json_storage_config.js`
- **同期レポート**: `.tmp/hybrid_sync/sync_report_[timestamp].md`

## ワークフロー

### Phase 1: フロントエンド仕様解析・マルチバックエンド要求生成

#### 1. Vue3ハイブリッドコンポーネント分析
```markdown
## ハイブリッドフロントエンド仕様解析

### コンポーネント構造・接続パターン分析
- Vue3 Composition API + ハイブリッド接続パターンの特定
- Piniaストア・マルチバックエンド状態管理要件の抽出
- 接続切り替え・フォールバック要件の分析
- フォーム・バリデーションルール（複数バックエンド対応）の抽出

### データフロー・マルチAPI要求分析
- コンポーネント間のハイブリッドデータフロー分析
- API呼び出しパターン・優先順位の特定
- Supabaseリアルタイム機能要件の定義
- JSONファイル同期・ローカルストレージ戦略の設計

### UI/UX要件のマルチバックエンドAPI要求変換
- フォーム項目 → REST API + Supabase + JSONファイルスキーマ
- 表示項目 → 統合レスポンススキーマ
- リアルタイム要件 → Supabase Realtime設定
- オフライン対応 → ローカルストレージ設計

### ハイブリッド認証・セキュリティ要件
- JWT認証（REST API）+ Supabase Auth統合
- 権限管理・ロールベース制御（複数バックエンド対応）
- オフライン認証キャッシュ戦略
- セッション管理・トークン同期
```

#### 2. 統合OpenAPI 3.0仕様生成
```yaml
# ハイブリッド対応OpenAPI仕様例
openapi: 3.0.3
info:
  title: ハイブリッド接続製造業品質管理システムAPI
  version: 1.0.0
  description: Vue3ハイブリッドフロントエンド向けマルチバックエンド統合API

servers:
  - url: http://localhost:9995
    description: Primary REST API Server
  - url: https://your-project.supabase.co
    description: Supabase Fallback Server
  - url: offline://localhost
    description: Offline Mode (IndexedDB)

paths:
  /api/v1/auth/login:
    post:
      summary: ハイブリッド認証ログイン
      description: REST API優先、Supabaseフォールバック対応
      x-hybrid-config:
        primary: "rest_api"
        fallback: "supabase"
        offline_support: true
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  minLength: 3
                  maxLength: 50
                password:
                  type: string
                  minLength: 8
                connection_preference:
                  type: string
                  enum: [api, supabase, auto]
                  default: auto
              required: [username, password]
      responses:
        200:
          description: ログイン成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  token_type:
                    type: string
                  expires_in:
                    type: integer
                  user:
                    $ref: '#/components/schemas/User'
                  connection_used:
                    type: string
                    enum: [api, supabase, offline]
                  sync_status:
                    $ref: '#/components/schemas/SyncStatus'

  /api/v1/products:
    get:
      summary: 製品一覧取得（ハイブリッド対応）
      x-hybrid-config:
        primary: "rest_api"
        fallback: "supabase"
        offline_support: true
        cache_ttl: 300
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: search
          in: query
          schema:
            type: string
        - name: connection_hint
          in: query
          schema:
            type: string
            enum: [api, supabase, offline]
          description: 優先接続方式のヒント
      responses:
        200:
          description: 製品一覧
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items:
                      $ref: '#/components/schemas/Product'
                  total:
                    type: integer
                  page:
                    type: integer
                  limit:
                    type: integer
                  data_source:
                    type: string
                    enum: [api, supabase, offline]
                  last_sync:
                    type: string
                    format: date-time

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        username:
          type: string
        full_name:
          type: string
        email:
          type: string
          format: email
        role:
          type: string
          enum: [admin, manager, operator, viewer]
        auth_source:
          type: string
          enum: [api, supabase]
        last_sync:
          type: string
          format: date-time
    
    Product:
      type: object
      properties:
        id:
          type: integer
        product_code:
          type: string
        product_name:
          type: string
        category:
          type: string
        price:
          type: number
          format: decimal
        created_at:
          type: string
          format: date-time
        data_source:
          type: string
          enum: [api, supabase, offline]
        sync_status:
          $ref: '#/components/schemas/SyncStatus'
    
    SyncStatus:
      type: object
      properties:
        is_synced:
          type: boolean
        last_sync:
          type: string
          format: date-time
        pending_changes:
          type: integer
        conflicts:
          type: integer
```

#### 3. マルチバックエンド実装要求書生成
```markdown
# マルチバックエンド実装要求書

## 必要なREST APIエンドポイント（プライマリ）

### 認証システム
- `POST /api/v1/auth/login` - JWT認証（Supabase連携対応）
- `POST /api/v1/auth/refresh` - トークンリフレッシュ
- `POST /api/v1/auth/sync` - Supabase認証状態同期
- `GET /api/v1/auth/me` - 現在ユーザー情報

### 製品管理
- `GET /api/v1/products` - 製品一覧（Supabase同期メタデータ含む）
- `GET /api/v1/products/{id}` - 製品詳細
- `POST /api/v1/products` - 製品作成（Supabase自動同期）
- `PUT /api/v1/products/{id}` - 製品更新
- `DELETE /api/v1/products/{id}` - 製品削除
- `POST /api/v1/products/sync` - Supabaseとの手動同期

## 必要なSupabaseスキーマ・設定

### テーブル定義
```sql
-- Users table (authentication + profile)
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  uuid UUID DEFAULT gen_random_uuid(),
  username VARCHAR(50) UNIQUE NOT NULL,
  full_name VARCHAR(100),
  email VARCHAR(100) UNIQUE NOT NULL,
  role VARCHAR(20) CHECK (role IN ('admin', 'manager', 'operator', 'viewer')),
  is_active BOOLEAN DEFAULT true,
  auth_source VARCHAR(20) DEFAULT 'supabase',
  api_user_id INTEGER, -- REST APIのユーザーIDとの関連付け
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_sync TIMESTAMP DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  uuid UUID DEFAULT gen_random_uuid(),
  product_code VARCHAR(50) UNIQUE NOT NULL,
  product_name VARCHAR(200) NOT NULL,
  category VARCHAR(100),
  price DECIMAL(10,2),
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  api_product_id INTEGER, -- REST APIの製品IDとの関連付け
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_sync TIMESTAMP DEFAULT NOW(),
  sync_status VARCHAR(20) DEFAULT 'synced' -- synced, pending, conflict
);

-- Sync status tracking
CREATE TABLE sync_log (
  id SERIAL PRIMARY KEY,
  table_name VARCHAR(50) NOT NULL,
  record_id INTEGER NOT NULL,
  sync_type VARCHAR(20) NOT NULL, -- api_to_supabase, supabase_to_api, conflict
  status VARCHAR(20) NOT NULL, -- success, failed, pending
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Row Level Security (RLS)
```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- User policies
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = uuid);

CREATE POLICY "Admins can view all users" ON users
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users 
      WHERE uuid = auth.uid() AND role = 'admin'
    )
  );

-- Product policies
CREATE POLICY "Authenticated users can view products" ON products
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Managers can modify products" ON products
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users 
      WHERE uuid = auth.uid() AND role IN ('admin', 'manager')
    )
  );
```

### Realtime subscriptions
```sql
-- Enable realtime for specific tables
ALTER PUBLICATION supabase_realtime ADD TABLE products;
ALTER PUBLICATION supabase_realtime ADD TABLE users;
```

## オフラインストレージ設計

### IndexedDB Schema
```javascript
const offlineDBSchema = {
  name: 'HybridApp',
  version: 1,
  stores: [
    {
      name: 'users',
      keyPath: 'id',
      indexes: [
        { name: 'username', keyPath: 'username', unique: true },
        { name: 'email', keyPath: 'email', unique: true }
      ]
    },
    {
      name: 'products', 
      keyPath: 'id',
      indexes: [
        { name: 'product_code', keyPath: 'product_code', unique: true },
        { name: 'category', keyPath: 'category' },
        { name: 'created_at', keyPath: 'created_at' }
      ]
    },
    {
      name: 'sync_queue',
      keyPath: 'id',
      indexes: [
        { name: 'table_name', keyPath: 'table_name' },
        { name: 'status', keyPath: 'status' },
        { name: 'created_at', keyPath: 'created_at' }
      ]
    },
    {
      name: 'app_metadata',
      keyPath: 'key'
    }
  ]
};
```

### オフライン同期ルール
```javascript
const offlineSyncRules = {
  // 優先順位付き同期戦略
  syncPriority: {
    'users': 1,      // 認証情報は最優先
    'products': 2,   // マスターデータ
    'orders': 3,     // トランザクションデータ
    'logs': 4        // ログ系は最後
  },
  
  // 競合解決戦略
  conflictResolution: {
    'users': 'server_wins',     // ユーザー情報はサーバー優先
    'products': 'last_modified', // 製品は最終更新日時で判定
    'orders': 'manual_review'    // 注文は手動確認
  },
  
  // オフライン期間制限
  offlineLimits: {
    maxOfflineDays: 7,          // 7日以上オフラインなら強制同期
    maxPendingChanges: 100,     // 未同期変更100件で警告
    maxCacheSize: '50MB'        // キャッシュサイズ制限
  }
};
```
```

### Phase 2: ハイブリッドクライアント・Piniaストア自動生成

#### 1. JavaScript型定義（JSDoc）生成（ハイブリッド対応）
```javascript
// 自動生成される型定義ファイル: types/hybrid-api.js

/**
 * @typedef {Object} HybridConnectionConfig
 * @property {'api'|'supabase'|'offline'} primary - プライマリ接続
 * @property {'api'|'supabase'|'offline'} fallback - フォールバック接続
 * @property {boolean} offline_support - オフライン対応
 * @property {number} cache_ttl - キャッシュTTL（秒）
 */

/**
 * @typedef {Object} SyncStatus
 * @property {boolean} is_synced - 同期済みフラグ
 * @property {string} last_sync - 最終同期日時
 * @property {number} pending_changes - 未同期変更数
 * @property {number} conflicts - 競合数
 */

/**
 * @typedef {Object} User
 * @property {number} id - ユーザーID
 * @property {string} username - ユーザー名
 * @property {string} full_name - フルネーム
 * @property {string} email - メールアドレス
 * @property {'admin'|'manager'|'operator'|'viewer'} role - ユーザーロール
 * @property {boolean} is_active - 有効フラグ
 * @property {'api'|'supabase'} auth_source - 認証ソース
 * @property {string} created_at - 作成日時
 * @property {string} last_sync - 最終同期日時
 */

/**
 * @typedef {Object} Product
 * @property {number} id - 製品ID
 * @property {string} product_code - 製品コード
 * @property {string} product_name - 製品名
 * @property {string} [category] - カテゴリ
 * @property {number} [price] - 価格
 * @property {string} created_at - 作成日時
 * @property {'api'|'supabase'|'offline'} data_source - データソース
 * @property {SyncStatus} sync_status - 同期状態
 */

/**
 * @typedef {Object} LoginRequest
 * @property {string} username - ユーザー名
 * @property {string} password - パスワード
 * @property {'api'|'supabase'|'auto'} [connection_preference] - 接続優先設定
 */

/**
 * @typedef {Object} LoginResponse
 * @property {string} access_token - アクセストークン
 * @property {string} token_type - トークンタイプ
 * @property {number} expires_in - 有効期限（秒）
 * @property {User} user - ユーザー情報
 * @property {'api'|'supabase'|'offline'} connection_used - 使用された接続
 * @property {SyncStatus} sync_status - 同期状態
 */

/**
 * @template T
 * @typedef {Object} HybridPaginatedResponse
 * @property {T[]} items - アイテム配列
 * @property {number} total - 総件数
 * @property {number} page - ページ番号
 * @property {number} limit - 1ページあたりの件数
 * @property {'api'|'supabase'|'offline'} data_source - データソース
 * @property {string} last_sync - 最終同期日時
 */

/**
 * @typedef {Object} HybridApiError
 * @property {Object} error - エラー情報
 * @property {string} error.code - エラーコード
 * @property {string} error.message - エラーメッセージ
 * @property {Object} [error.details] - エラー詳細
 * @property {'api'|'supabase'|'offline'} error.source - エラー発生源
 * @property {string} timestamp - タイムスタンプ
 */

/**
 * @typedef {Object} ConnectionState
 * @property {boolean} available - 接続可能フラグ
 * @property {number} response_time - レスポンス時間（ms）
 * @property {number} error_rate - エラー率（0-1）
 * @property {string} last_check - 最終チェック日時
 */

export {}; // このファイルをモジュールとして扱う
```

#### 2. ハイブリッドクライアント生成
```javascript
// 自動生成されるハイブリッドAPIクライアント: services/hybridClient.js
import axios from 'axios';
import { createClient } from '@supabase/supabase-js';
import { JSONFileStorage } from './jsonFileStorage';
import { useAuthStore } from '@/stores/authStore';

// 設定
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:9995';
const SUPABASE_URL = process.env.VUE_APP_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.VUE_APP_SUPABASE_ANON_KEY;

class HybridClient {
  constructor() {
    // REST API クライアント
    this.apiClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    // Supabase クライアント
    this.supabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    
    // オフラインストレージ
    this.jsonFileStorage = new JSONFileStorage('./data/offline/');
    
    // 接続状態管理
    this.connectionStates = {
      api: { available: true, responseTime: 0, errorRate: 0 },
      supabase: { available: true, responseTime: 0, errorRate: 0 },
      offline: { available: true }
    };
    
    this.setupInterceptors();
    this.startConnectionMonitoring();
  }
  
  setupInterceptors() {
    // REST APIインターセプター
    this.apiClient.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore();
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    this.apiClient.interceptors.response.use(
      (response) => {
        this.updateConnectionState('api', 'success');
        return response;
      },
      async (error) => {
        this.updateConnectionState('api', 'error');
        
        // 自動フォールバック
        if (error.response?.status >= 500 || !error.response) {
          console.log('API error, attempting Supabase fallback');
          return this.handleFallback(error.config, 'supabase');
        }
        
        return Promise.reject(error);
      }
    );
  }
  
  async handleFallback(originalConfig, fallbackType) {
    try {
      switch (fallbackType) {
        case 'supabase':
          return await this.retryWithSupabase(originalConfig);
        case 'offline':
          return await this.retryWithOffline(originalConfig);
        default:
          throw new Error('Unknown fallback type');
      }
    } catch (fallbackError) {
      // 次のフォールバックを試行
      if (fallbackType === 'supabase') {
        return await this.handleFallback(originalConfig, 'offline');
      }
      throw fallbackError;
    }
  }
  
  async retryWithSupabase(config) {
    // REST APIリクエストをSupabaseクエリに変換
    const supabaseEquivalent = this.convertToSupabaseQuery(config);
    return await supabaseEquivalent;
  }
  
  async retryWithOffline(config) {
    // オフラインストレージからデータ取得
    const offlineKey = `${config.method}_${config.url.replace(/\//g, '_')}`;
    const offlineData = await this.jsonFileStorage.loadData(offlineKey);
    
    if (offlineData) {
      return {
        data: offlineData,
        status: 200,
        headers: { 'x-data-source': 'offline' }
      };
    }
    
    throw new Error('No offline data available');
  }
  
  convertToSupabaseQuery(config) {
    // REST APIパスをSupabaseテーブル操作に変換
    const urlParts = config.url.split('/');
    const tableName = urlParts[urlParts.length - 1];
    
    switch (config.method.toLowerCase()) {
      case 'get':
        if (config.params?.id) {
          return this.supabaseClient
            .from(tableName)
            .select('*')
            .eq('id', config.params.id)
            .single();
        } else {
          let query = this.supabaseClient.from(tableName).select('*');
          
          // クエリパラメータを適用
          if (config.params?.search) {
            query = query.ilike('name', `%${config.params.search}%`);
          }
          if (config.params?.limit) {
            query = query.limit(config.params.limit);
          }
          
          return query;
        }
      
      case 'post':
        return this.supabaseClient
          .from(tableName)
          .insert(config.data)
          .select();
      
      case 'put':
        const id = urlParts[urlParts.length - 1];
        return this.supabaseClient
          .from(tableName)
          .update(config.data)
          .eq('id', id)
          .select();
      
      case 'delete':
        const deleteId = urlParts[urlParts.length - 1];
        return this.supabaseClient
          .from(tableName)
          .delete()
          .eq('id', deleteId);
      
      default:
        throw new Error(`Unsupported method: ${config.method}`);
    }
  }
  
  updateConnectionState(connection, result) {
    const state = this.connectionStates[connection];
    
    if (result === 'success') {
      state.errorRate = Math.max(0, state.errorRate - 0.1);
      state.available = true;
    } else {
      state.errorRate = Math.min(1, state.errorRate + 0.1);
      state.available = state.errorRate < 0.5;
    }
    
    state.lastCheck = new Date().toISOString();
  }
  
  startConnectionMonitoring() {
    setInterval(async () => {
      await this.checkConnectionHealth();
    }, 30000); // 30秒ごと
  }
  
  async checkConnectionHealth() {
    // API接続チェック
    try {
      const start = Date.now();
      await this.apiClient.get('/health');
      this.connectionStates.api.responseTime = Date.now() - start;
      this.connectionStates.api.available = true;
    } catch (error) {
      this.connectionStates.api.available = false;
    }
    
    // Supabase接続チェック
    try {
      const start = Date.now();
      await this.supabaseClient.from('users').select('count', { count: 'exact' });
      this.connectionStates.supabase.responseTime = Date.now() - start;
      this.connectionStates.supabase.available = true;
    } catch (error) {
      this.connectionStates.supabase.available = false;
    }
  }
  
  getBestConnection(requestType = 'read') {
    // リクエストタイプと接続状態に基づいて最適な接続を選択
    const availableConnections = Object.entries(this.connectionStates)
      .filter(([_, state]) => state.available)
      .sort(([_, a], [__, b]) => a.responseTime - b.responseTime);
    
    if (availableConnections.length === 0) {
      return 'offline';
    }
    
    // リアルタイム要求はSupabase優先
    if (requestType === 'realtime' && this.connectionStates.supabase.available) {
      return 'supabase';
    }
    
    // 通常は最も高速な接続を使用
    return availableConnections[0][0];
  }
}

// API関数群（ハイブリッド対応）
const hybridClient = new HybridClient();

export const authAPI = {
  async login(credentials) {
    const connection = hybridClient.getBestConnection('auth');
    
    if (connection === 'api') {
      const response = await hybridClient.apiClient.post('/api/v1/auth/login', credentials);
      return response.data;
    } else if (connection === 'supabase') {
      const { data, error } = await hybridClient.supabaseClient.auth.signInWithPassword({
        email: credentials.username,
        password: credentials.password
      });
      
      if (error) throw error;
      
      return {
        access_token: data.session.access_token,
        token_type: 'bearer',
        expires_in: data.session.expires_in,
        user: data.user,
        connection_used: 'supabase'
      };
    }
  },
  
  async getCurrentUser() {
    const connection = hybridClient.getBestConnection('read');
    
    if (connection === 'api') {
      const response = await hybridClient.apiClient.get('/api/v1/auth/me');
      return response.data;
    } else if (connection === 'supabase') {
      const { data: { user } } = await hybridClient.supabaseClient.auth.getUser();
      return user;
    } else {
      // オフラインキャッシュから取得
      return await hybridClient.jsonFileStorage.loadData('current_user');
    }
  }
};

export const productAPI = {
  async getProducts(params = {}) {
    const connection = hybridClient.getBestConnection('read');
    
    if (connection === 'api') {
      const response = await hybridClient.apiClient.get('/api/v1/products', { params });
      return response.data;
    } else if (connection === 'supabase') {
      let query = hybridClient.supabaseClient.from('products').select('*');
      
      if (params.search) {
        query = query.ilike('product_name', `%${params.search}%`);
      }
      if (params.limit) {
        query = query.limit(params.limit);
      }
      
      const { data, error } = await query;
      if (error) throw error;
      
      return {
        items: data,
        data_source: 'supabase',
        last_sync: new Date().toISOString()
      };
    } else {
      // オフラインデータ取得
      const productsData = await hybridClient.jsonFileStorage.loadData('products_list');
      return productsData?.data || [];
    }
  },
  
  async createProduct(productData) {
    const connection = hybridClient.getBestConnection('write');
    
    try {
      let result;
      
      if (connection === 'api') {
        const response = await hybridClient.apiClient.post('/api/v1/products', productData);
        result = response.data;
      } else if (connection === 'supabase') {
        const { data, error } = await hybridClient.supabaseClient
          .from('products')
          .insert(productData)
          .select()
          .single();
        
        if (error) throw error;
        result = data;
      }
      
      // オフラインキャッシュに保存
      await hybridClient.jsonFileStorage.saveData(`product_${result.id}`, result);
      
      return result;
      
    } catch (error) {
      // オフライン作成（後で同期）
      const offlineResult = {
        ...productData,
        id: Date.now(), // 一時的なID
        offline: true,
        created_at: new Date().toISOString()
      };
      await hybridClient.jsonFileStorage.saveData(`product_offline_${offlineResult.id}`, offlineResult);
      return offlineResult;
    }
  }
};

export default hybridClient;
```

#### 3. ハイブリッドPiniaストア生成
```javascript
// 自動生成されるハイブリッド認証ストア: stores/hybridAuthStore.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authAPI } from '@/services/hybridClient';

export const useHybridAuthStore = defineStore('hybridAuth', () => {
  // State
  const user = ref(null);
  const token = ref(localStorage.getItem('auth_token'));
  const isLoading = ref(false);
  const error = ref(null);
  const connectionUsed = ref('api');  // 最後に使用した接続
  const syncStatus = ref({
    is_synced: true,
    last_sync: null,
    pending_changes: 0,
    conflicts: 0
  });

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value);
  const userRole = computed(() => user.value?.role || null);
  const isAdmin = computed(() => userRole.value === 'admin');
  const isManager = computed(() => ['admin', 'manager'].includes(userRole.value));
  const needsSync = computed(() => !syncStatus.value.is_synced || syncStatus.value.pending_changes > 0);

  // Actions
  const login = async (credentials) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await authAPI.login(credentials);
      
      token.value = response.access_token;
      user.value = response.user;
      connectionUsed.value = response.connection_used || 'api';
      syncStatus.value = response.sync_status || syncStatus.value;
      
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('auth_connection', connectionUsed.value);
      
      return response;
    } catch (err) {
      error.value = err.response?.data?.error?.message || 'ログインに失敗しました';
      
      // オフライン認証を試行
      try {
        const offlineUser = await authAPI.loginOffline(credentials);
        if (offlineUser) {
          user.value = offlineUser;
          connectionUsed.value = 'offline';
          syncStatus.value.is_synced = false;
          syncStatus.value.pending_changes++;
        }
      } catch (offlineError) {
        throw err; // 元のエラーを投げる
      }
    } finally {
      isLoading.value = false;
    }
  };

  const logout = async () => {
    try {
      if (token.value && connectionUsed.value !== 'offline') {
        await authAPI.logout();
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      token.value = null;
      user.value = null;
      connectionUsed.value = 'api';
      syncStatus.value = {
        is_synced: true,
        last_sync: null,
        pending_changes: 0,
        conflicts: 0
      };
      
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_connection');
    }
  };

  const syncAuthData = async () => {
    if (!needsSync.value || !navigator.onLine) {
      return;
    }
    
    try {
      const syncResult = await authAPI.syncUserData();
      
      if (syncResult.success) {
        user.value = syncResult.user;
        syncStatus.value = {
          is_synced: true,
          last_sync: new Date().toISOString(),
          pending_changes: 0,
          conflicts: syncResult.conflicts || 0
        };
      }
    } catch (error) {
      console.error('Auth sync failed:', error);
    }
  };

  const switchConnection = async (newConnection) => {
    if (newConnection === connectionUsed.value) {
      return;
    }
    
    try {
      // 新しい接続での認証確認
      await authAPI.validateConnection(newConnection);
      connectionUsed.value = newConnection;
      localStorage.setItem('auth_connection', newConnection);
      
      // 必要に応じてデータを再取得
      await fetchCurrentUser();
    } catch (error) {
      console.error(`Failed to switch to ${newConnection}:`, error);
      throw error;
    }
  };

  const fetchCurrentUser = async () => {
    try {
      const userData = await authAPI.getCurrentUser();
      user.value = userData;
      return userData;
    } catch (err) {
      if (connectionUsed.value !== 'offline') {
        await logout();
      }
      throw err;
    }
  };

  // 自動同期（オンライン復帰時）
  const setupAutoSync = () => {
    window.addEventListener('online', () => {
      if (needsSync.value) {
        syncAuthData();
      }
    });
  };

  // 初期化
  const initialize = async () => {
    if (token.value) {
      try {
        await fetchCurrentUser();
        
        // 保存された接続方式を復元
        const savedConnection = localStorage.getItem('auth_connection');
        if (savedConnection) {
          connectionUsed.value = savedConnection;
        }
        
        // 自動同期設定
        setupAutoSync();
        
        // オンライン時は同期チェック
        if (navigator.onLine && needsSync.value) {
          await syncAuthData();
        }
      } catch (err) {
        console.error('Auth initialization failed:', err);
      }
    }
  };

  return {
    // State
    user,
    token,
    isLoading,
    error,
    connectionUsed,
    syncStatus,
    
    // Getters
    isAuthenticated,
    userRole,
    isAdmin,
    isManager,
    needsSync,
    
    // Actions
    login,
    logout,
    syncAuthData,
    switchConnection,
    fetchCurrentUser,
    initialize
  };
});

// 自動生成されるハイブリッド製品ストア: stores/hybridProductStore.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { productAPI } from '@/services/hybridClient';

export const useHybridProductStore = defineStore('hybridProduct', () => {
  // State
  const products = ref([]);
  const currentProduct = ref(null);
  const isLoading = ref(false);
  const error = ref(null);
  const dataSource = ref('api');  // データの取得元
  const lastSync = ref(null);
  const pagination = ref({
    total: 0,
    page: 1,
    limit: 20
  });
  const pendingSyncItems = ref([]); // 同期待ちアイテム

  // Getters
  const totalPages = computed(() => 
    Math.ceil(pagination.value.total / pagination.value.limit)
  );
  const needsSync = computed(() => pendingSyncItems.value.length > 0);
  const isOnlineData = computed(() => ['api', 'supabase'].includes(dataSource.value));

  // Actions
  const fetchProducts = async (params = {}) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await productAPI.getProducts({
        page: pagination.value.page,
        limit: pagination.value.limit,
        ...params
      });
      
      products.value = response.items || [];
      dataSource.value = response.data_source || 'api';
      lastSync.value = response.last_sync || new Date().toISOString();
      
      if (response.total !== undefined) {
        pagination.value.total = response.total;
        pagination.value.page = response.page || pagination.value.page;
        pagination.value.limit = response.limit || pagination.value.limit;
      }
      
      return response;
    } catch (err) {
      error.value = err.response?.data?.error?.message || '製品取得に失敗しました';
      
      // オフラインフォールバック時の処理
      if (err.message?.includes('offline')) {
        dataSource.value = 'offline';
      }
      
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const createProduct = async (productData) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const newProduct = await productAPI.createProduct(productData);
      
      // オフライン作成の場合は同期待ちリストに追加
      if (newProduct.data_source === 'offline') {
        pendingSyncItems.value.push({
          id: newProduct.id,
          action: 'create',
          data: newProduct,
          timestamp: Date.now()
        });
      }
      
      products.value.unshift(newProduct);
      return newProduct;
    } catch (err) {
      error.value = err.response?.data?.error?.message || '製品作成に失敗しました';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const syncPendingChanges = async () => {
    if (!needsSync.value || !navigator.onLine) {
      return { success: false, reason: 'No pending changes or offline' };
    }
    
    const syncResults = [];
    
    for (const pendingItem of pendingSyncItems.value) {
      try {
        let result;
        
        switch (pendingItem.action) {
          case 'create':
            result = await productAPI.createProduct(pendingItem.data);
            break;
          case 'update':
            result = await productAPI.updateProduct(pendingItem.id, pendingItem.data);
            break;
          case 'delete':
            await productAPI.deleteProduct(pendingItem.id);
            result = { id: pendingItem.id, deleted: true };
            break;
        }
        
        syncResults.push({ success: true, item: pendingItem, result });
      } catch (error) {
        syncResults.push({ success: false, item: pendingItem, error });
      }
    }
    
    // 成功した項目を同期待ちリストから削除
    const successfulSyncs = syncResults.filter(r => r.success);
    successfulSyncs.forEach(sync => {
      const index = pendingSyncItems.value.findIndex(item => 
        item.id === sync.item.id && item.action === sync.item.action
      );
      if (index > -1) {
        pendingSyncItems.value.splice(index, 1);
      }
    });
    
    // データを再取得してUI更新
    if (successfulSyncs.length > 0) {
      await fetchProducts();
    }
    
    return {
      success: syncResults.every(r => r.success),
      results: syncResults,
      synced: successfulSyncs.length,
      failed: syncResults.length - successfulSyncs.length
    };
  };

  const switchDataSource = async (newSource) => {
    if (!['api', 'supabase', 'offline'].includes(newSource)) {
      throw new Error(`Invalid data source: ${newSource}`);
    }
    
    try {
      // 新しいデータソースでデータを取得
      const params = { connection_hint: newSource };
      await fetchProducts(params);
      
      dataSource.value = newSource;
    } catch (error) {
      console.error(`Failed to switch to ${newSource}:`, error);
      throw error;
    }
  };

  // 自動同期設定（オンライン復帰時）
  const setupAutoSync = () => {
    window.addEventListener('online', () => {
      if (needsSync.value) {
        syncPendingChanges();
      }
    });
    
    // 定期同期（5分おき、オンライン時のみ）
    setInterval(() => {
      if (navigator.onLine && needsSync.value) {
        syncPendingChanges();
      }
    }, 5 * 60 * 1000);
  };

  return {
    // State
    products,
    currentProduct,
    isLoading,
    error,
    dataSource,
    lastSync,
    pagination,
    pendingSyncItems,
    
    // Getters
    totalPages,
    needsSync,
    isOnlineData,
    
    // Actions
    fetchProducts,
    createProduct,
    syncPendingChanges,
    switchDataSource,
    setupAutoSync
  };
});
```

### Phase 3: ハイブリッドバリデーション・テスト連携

#### 1. マルチバックエンドスキーマ同期検証
```javascript
// ハイブリッドスキーマ同期検証ツール
export const hybridSchemaValidator = {
  async validateAcrossBackends(data, schema) {
    const validationResults = {
      api: null,
      supabase: null,
      offline: null,
      conflicts: []
    };
    
    // REST API バリデーション
    try {
      validationResults.api = await this.validateAgainstAPI(data, schema);
    } catch (error) {
      validationResults.api = { valid: false, errors: [error.message] };
    }
    
    // Supabase バリデーション
    try {
      validationResults.supabase = await this.validateAgainstSupabase(data, schema);
    } catch (error) {
      validationResults.supabase = { valid: false, errors: [error.message] };
    }
    
    // オフライン バリデーション
    validationResults.offline = this.validateOfflineSchema(data, schema);
    
    // 競合検出
    validationResults.conflicts = this.detectValidationConflicts(validationResults);
    
    return validationResults;
  },
  
  async validateAgainstAPI(data, schema) {
    try {
      await apiClient.post(`/api/v1/${schema.table}/validate`, data);
      return { valid: true };
    } catch (error) {
      return { 
        valid: false, 
        errors: error.response?.data?.error?.details || [error.message]
      };
    }
  },
  
  async validateAgainstSupabase(data, schema) {
    // Supabase スキーマに対するクライアントサイドバリデーション
    const supabaseRules = schema.supabase_rules || {};
    const errors = [];
    
    for (const [field, rules] of Object.entries(supabaseRules)) {
      const value = data[field];
      
      if (rules.required && !value) {
        errors.push(`${field} is required`);
      }
      
      if (rules.max_length && value?.length > rules.max_length) {
        errors.push(`${field} exceeds maximum length of ${rules.max_length}`);
      }
      
      if (rules.type && typeof value !== rules.type) {
        errors.push(`${field} must be of type ${rules.type}`);
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  },
  
  detectValidationConflicts(results) {
    const conflicts = [];
    
    // API とSupabase間の競合チェック
    if (results.api?.valid !== results.supabase?.valid) {
      conflicts.push({
        type: 'api_supabase_conflict',
        message: 'API and Supabase validation results differ',
        api_result: results.api,
        supabase_result: results.supabase
      });
    }
    
    // エラーメッセージの不一致チェック
    if (results.api?.errors && results.supabase?.errors) {
      const apiErrors = new Set(results.api.errors);
      const supabaseErrors = new Set(results.supabase.errors);
      
      apiErrors.forEach(error => {
        if (!supabaseErrors.has(error)) {
          conflicts.push({
            type: 'error_message_mismatch',
            message: `API-specific error: ${error}`
          });
        }
      });
    }
    
    return conflicts;
  }
};
```

## 成功指標・KPI（ハイブリッド対応）

### 技術指標
- **型安全性**: JavaScript型エラー削減率 95%（JSDocによる型チェック）
- **API整合性**: マルチバックエンド仕様一致率 100%
- **自動化率**: 手動API統合作業削減 80%
- **ハイブリッド対応**: 接続切り替え成功率 99%
- **品質**: バリデーション不整合バグ削減 90%

### 開発効率指標  
- **開発時間**: ハイブリッドAPI統合時間 70% 短縮
- **バグ修正**: 接続関連バグ修正時間 60% 短縮
- **メンテナンス**: 仕様変更時の同期時間 85% 短縮

### ユーザー体験指標
- **接続切り替え**: フォールバック時間 500ms以内
- **データ整合性**: マルチバックエンド同期率 99.5%
- **オフライン機能**: 主要機能の80%オフライン利用可能

## 使用例

### フロントエンド仕様からマルチバックエンド生成
```bash
# Vue3ハイブリッドコンポーネントからAPI要求生成
/backend-sync spec_to_backends --target_feature="products" --backend_priority="api_first"
```

### 既存APIの自動ハイブリッド統合
```bash
# 複数バックエンドからVue3クライアント生成
/backend-sync hybrid_consume --target_feature="all" --sync_direction="backends_to_frontend"
```

### 完全ハイブリッド同期
```bash
# フロントエンド・マルチバックエンド完全同期
/backend-sync full_hybrid_sync --validation_level="strict" --backend_priority="api_first"
```

## 注意事項・制約

### 技術制約
- OpenAPI 3.0仕様への準拠が必要
- Vue3 Composition API + Pinia構成前提
- Supabase プロジェクト設定が必要
- ハイブリッド接続対応設計前提

### 同期制約
- マルチバックエンド同期は準リアルタイム（数分間隔）
- 複雑なビジネスロジックは手動調整が必要
- オフライン期間の制限あり（デフォルト7日間）
- 競合解決は設定に基づく自動処理

### 品質保証
- 自動生成コードの品質レビュー推奨
- ハイブリッドE2Eテストによる動作確認必須
- セキュリティ監査の定期実施
- マルチバックエンド整合性チェック