# /backend-sync - フロントエンド・バックエンド連携コマンド

## 目的
Vue3 + Axios フロントエンドから FastAPI + SQLAlchemy バックエンドへの仕様連携・API同期を自動化し、フルスタック開発における一貫性と効率性を確保します。

## 対象システム
- **フロントエンド**: Vue.js 3 + Composition API + Axios + Pinia
- **バックエンド**: FastAPI + SQLAlchemy + SQL Server
- **連携プロトコル**: REST API + JSON Schema + OpenAPI 3.0

## 入力パラメータ
- **必須**: `$SYNC_TYPE` - 同期タイプ（spec_to_backend, api_consume, full_sync, validation_sync）
- **任意**: `$TARGET_FEATURE` - 対象機能（authentication, products, orders, reports, all）
- **任意**: `$SYNC_DIRECTION` - 同期方向（frontend_to_backend, backend_to_frontend, bidirectional）
- **任意**: `$VALIDATION_LEVEL` - 検証レベル（basic, full, strict）

## 出力ファイル
- **API仕様書**: `.tmp/api_sync/openapi_spec_[timestamp].json`
- **型定義ファイル**: `.tmp/api_sync/frontend_types.js`
- **Axiosクライアント**: `.tmp/api_sync/api_client.js`
- **Piniaストア**: `.tmp/api_sync/stores/[feature]Store.js`
- **バックエンド要求仕様**: `.tmp/api_sync/backend_requirements.md`
- **同期レポート**: `.tmp/api_sync/sync_report_[timestamp].md`

## ワークフロー

### Phase 1: フロントエンド仕様解析・バックエンド要求生成

#### 1. Vue3コンポーネント・機能分析
```markdown
## フロントエンド仕様解析

### コンポーネント構造分析
- Vue3 Composition API使用パターンの特定
- Piniaストア・状態管理要件の抽出
- ルーティング・ページ構造の分析
- フォーム・バリデーションルールの抽出

### データフロー・API要求分析
- コンポーネント間のデータフロー分析
- API呼び出しパターンの特定
- 必要なエンドポイント・HTTPメソッドの定義
- リクエスト・レスポンス形式の設計

### UI/UX要件のAPI要求変換
- フォーム項目 → APIリクエストスキーマ
- 表示項目 → APIレスポンススキーマ
- ページネーション → クエリパラメータ仕様
- フィルタリング・ソート → API検索仕様

### セキュリティ・認証要件
- 認証フロー（JWT, OAuth）の要求仕様
- 権限管理・ロールベースアクセス制御
- CORS設定・セキュリティヘッダー要求
- セッション管理・トークンリフレッシュ
```

#### 2. OpenAPI 3.0仕様生成
```yaml
# 生成されるOpenAPI仕様例
openapi: 3.0.3
info:
  title: 製造業品質管理システムAPI
  version: 1.0.0
  description: Vue3フロントエンド向けFastAPI バックエンド

paths:
  /api/v1/auth/login:
    post:
      summary: ユーザーログイン
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

  /api/v1/products:
    get:
      summary: 製品一覧取得
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
```

#### 3. バックエンド実装要求書生成
```markdown
# バックエンド実装要求書

## 必要なFastAPIエンドポイント

### 認証システム
- `POST /api/v1/auth/login` - JWT認証
- `POST /api/v1/auth/refresh` - トークンリフレッシュ
- `POST /api/v1/auth/logout` - ログアウト
- `GET /api/v1/auth/me` - 現在ユーザー情報

### 製品管理
- `GET /api/v1/products` - 製品一覧（ページング・検索対応）
- `GET /api/v1/products/{id}` - 製品詳細
- `POST /api/v1/products` - 製品作成
- `PUT /api/v1/products/{id}` - 製品更新
- `DELETE /api/v1/products/{id}` - 製品削除

## SQLAlchemyモデル要件

### Userモデル
```python
class User(BaseModel):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Productモデル
```python
class Product(BaseModel):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    product_code = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(200), nullable=False)
    category = Column(String(100))
    price = Column(Numeric(10, 2))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## Pydanticスキーマ要件

### リクエストスキーマ
```python
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class ProductCreate(BaseModel):
    product_code: str = Field(..., min_length=1, max_length=50)
    product_name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None
```

### レスポンススキーマ
```python
class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

class ProductResponse(BaseModel):
    id: int
    product_code: str
    product_name: str
    category: Optional[str]
    price: Optional[Decimal]
    created_at: datetime
```
```

### Phase 2: Axiosクライアント・Piniaストア自動生成

#### 1. JavaScript型定義（JSDoc）生成
```javascript
// 自動生成される型定義ファイル: types/api.js

/**
 * @typedef {Object} User
 * @property {number} id - ユーザーID
 * @property {string} username - ユーザー名
 * @property {string} full_name - フルネーム
 * @property {string} email - メールアドレス
 * @property {'admin'|'manager'|'operator'|'viewer'} role - ユーザーロール
 * @property {boolean} is_active - 有効フラグ
 * @property {string} created_at - 作成日時
 */

/**
 * @typedef {Object} Product
 * @property {number} id - 製品ID
 * @property {string} product_code - 製品コード
 * @property {string} product_name - 製品名
 * @property {string} [category] - カテゴリ
 * @property {number} [price] - 価格
 * @property {string} created_at - 作成日時
 */

/**
 * @typedef {Object} LoginRequest
 * @property {string} username - ユーザー名
 * @property {string} password - パスワード
 */

/**
 * @typedef {Object} LoginResponse
 * @property {string} access_token - アクセストークン
 * @property {string} token_type - トークンタイプ
 * @property {number} expires_in - 有効期限（秒）
 * @property {User} user - ユーザー情報
 */

/**
 * @template T
 * @typedef {Object} PaginatedResponse
 * @property {T[]} items - アイテム配列
 * @property {number} total - 総件数
 * @property {number} page - ページ番号
 * @property {number} limit - 1ページあたりの件数
 */

/**
 * @typedef {Object} ApiError
 * @property {Object} error - エラー情報
 * @property {string} error.code - エラーコード
 * @property {string} error.message - エラーメッセージ
 * @property {Object} [error.details] - エラー詳細
 * @property {string} timestamp - タイムスタンプ
 */

export {}; // このファイルをモジュールとして扱う
```

#### 2. Axiosクライアント生成
```javascript
// 自動生成されるAPIクライアント: services/apiClient.js
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

// ベース設定
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:9995';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// リクエストインターセプター（認証トークン付与）
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// レスポンスインターセプター（エラーハンドリング）
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore();
      await authStore.logout();
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

// API関数群
export const authAPI = {
  async login(credentials) {
    const response = await apiClient.post('/api/v1/auth/login', credentials);
    return response.data;
  },
  
  async refreshToken() {
    const response = await apiClient.post('/api/v1/auth/refresh');
    return response.data;
  },
  
  async logout() {
    await apiClient.post('/api/v1/auth/logout');
  },
  
  async getCurrentUser() {
    const response = await apiClient.get('/api/v1/auth/me');
    return response.data;
  }
};

export const productAPI = {
  async getProducts(params = {}) {
    const response = await apiClient.get('/api/v1/products', { params });
    return response.data;
  },
  
  async getProduct(id) {
    const response = await apiClient.get(`/api/v1/products/${id}`);
    return response.data;
  },
  
  async createProduct(productData) {
    const response = await apiClient.post('/api/v1/products', productData);
    return response.data;
  },
  
  async updateProduct(id, productData) {
    const response = await apiClient.put(`/api/v1/products/${id}`, productData);
    return response.data;
  },
  
  async deleteProduct(id) {
    await apiClient.delete(`/api/v1/products/${id}`);
  }
};

export default apiClient;
```

#### 3. Piniaストア生成
```javascript
// 自動生成される認証ストア: stores/authStore.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authAPI } from '@/services/apiClient';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null);
  const token = ref(localStorage.getItem('auth_token'));
  const isLoading = ref(false);
  const error = ref(null);

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value);
  const userRole = computed(() => user.value?.role || null);
  const isAdmin = computed(() => userRole.value === 'admin');
  const isManager = computed(() => ['admin', 'manager'].includes(userRole.value));

  // Actions
  const login = async (credentials) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await authAPI.login(credentials);
      
      token.value = response.access_token;
      user.value = response.user;
      
      localStorage.setItem('auth_token', response.access_token);
      
      return response;
    } catch (err) {
      error.value = err.response?.data?.error?.message || 'ログインに失敗しました';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const logout = async () => {
    try {
      if (token.value) {
        await authAPI.logout();
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      token.value = null;
      user.value = null;
      localStorage.removeItem('auth_token');
    }
  };

  const refreshToken = async () => {
    try {
      const response = await authAPI.refreshToken();
      token.value = response.access_token;
      localStorage.setItem('auth_token', response.access_token);
      return response;
    } catch (err) {
      await logout();
      throw err;
    }
  };

  const fetchCurrentUser = async () => {
    try {
      const userData = await authAPI.getCurrentUser();
      user.value = userData;
      return userData;
    } catch (err) {
      await logout();
      throw err;
    }
  };

  // 初期化時にユーザー情報を取得
  const initialize = async () => {
    if (token.value) {
      try {
        await fetchCurrentUser();
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
    
    // Getters
    isAuthenticated,
    userRole,
    isAdmin,
    isManager,
    
    // Actions
    login,
    logout,
    refreshToken,
    fetchCurrentUser,
    initialize
  };
});

// 自動生成される製品ストア: stores/productStore.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { productAPI } from '@/services/apiClient';

export const useProductStore = defineStore('product', () => {
  // State
  const products = ref([]);
  const currentProduct = ref(null);
  const isLoading = ref(false);
  const error = ref(null);
  const pagination = ref({
    total: 0,
    page: 1,
    limit: 20
  });

  // Getters
  const totalPages = computed(() => 
    Math.ceil(pagination.value.total / pagination.value.limit)
  );

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
      
      products.value = response.items;
      pagination.value = {
        total: response.total,
        page: response.page,
        limit: response.limit
      };
      
      return response;
    } catch (err) {
      error.value = err.response?.data?.error?.message || '製品取得に失敗しました';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchProduct = async (id) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const product = await productAPI.getProduct(id);
      currentProduct.value = product;
      
      return product;
    } catch (err) {
      error.value = err.response?.data?.error?.message || '製品詳細取得に失敗しました';
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
      products.value.unshift(newProduct);
      
      return newProduct;
    } catch (err) {
      error.value = err.response?.data?.error?.message || '製品作成に失敗しました';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updateProduct = async (id, productData) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const updatedProduct = await productAPI.updateProduct(id, productData);
      
      const index = products.value.findIndex(p => p.id === id);
      if (index !== -1) {
        products.value[index] = updatedProduct;
      }
      
      if (currentProduct.value?.id === id) {
        currentProduct.value = updatedProduct;
      }
      
      return updatedProduct;
    } catch (err) {
      error.value = err.response?.data?.error?.message || '製品更新に失敗しました';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteProduct = async (id) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      await productAPI.deleteProduct(id);
      
      products.value = products.value.filter(p => p.id !== id);
      
      if (currentProduct.value?.id === id) {
        currentProduct.value = null;
      }
    } catch (err) {
      error.value = err.response?.data?.error?.message || '製品削除に失敗しました';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const setPage = (page) => {
    pagination.value.page = page;
  };

  const setLimit = (limit) => {
    pagination.value.limit = limit;
  };

  return {
    // State
    products,
    currentProduct,
    isLoading,
    error,
    pagination,
    
    // Getters
    totalPages,
    
    // Actions
    fetchProducts,
    fetchProduct,
    createProduct,
    updateProduct,
    deleteProduct,
    setPage,
    setLimit
  };
});
```

### Phase 3: バリデーション・テスト連携

#### 1. スキーマ同期検証
```javascript
// スキーマ同期検証ツール
export const schemaValidator = {
  validateRequest(data, schema) {
    // フロントエンドのバリデーションとバックエンドスキーマの整合性チェック
    const errors = [];
    
    for (const [field, rules] of Object.entries(schema.properties)) {
      const value = data[field];
      
      // 必須フィールドチェック
      if (schema.required?.includes(field) && !value) {
        errors.push(`${field} is required`);
      }
      
      // 型チェック
      if (value && typeof value !== rules.type) {
        errors.push(`${field} must be ${rules.type}`);
      }
      
      // 長さチェック
      if (rules.minLength && value?.length < rules.minLength) {
        errors.push(`${field} must be at least ${rules.minLength} characters`);
      }
    }
    
    return errors;
  },
  
  async validateAgainstBackend(endpoint, data) {
    // バックエンドとの実際の通信でバリデーション
    try {
      await apiClient.post(`${endpoint}/validate`, data);
      return { valid: true };
    } catch (error) {
      return { 
        valid: false, 
        errors: error.response?.data?.error?.details || []
      };
    }
  }
};
```

#### 2. E2Eテスト生成
```javascript
// E2Eテストケース自動生成
export const generateE2ETests = {
  authFlow: `
    describe('認証フロー', () => {
      it('ログイン → ダッシュボード → ログアウト', async () => {
        await page.goto('/login');
        
        await page.fill('[data-testid="username"]', 'testuser');
        await page.fill('[data-testid="password"]', 'testpass123');
        await page.click('[data-testid="login-button"]');
        
        await expect(page).toHaveURL('/dashboard');
        await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
        
        await page.click('[data-testid="logout-button"]');
        await expect(page).toHaveURL('/login');
      });
    });
  `,
  
  productCRUD: `
    describe('製品CRUD操作', () => {
      beforeEach(async () => {
        await authenticateUser(page, 'admin');
      });
      
      it('製品作成 → 一覧表示 → 編集 → 削除', async () => {
        // 製品作成
        await page.goto('/products/create');
        await page.fill('[data-testid="product-code"]', 'TEST001');
        await page.fill('[data-testid="product-name"]', 'テスト製品');
        await page.click('[data-testid="create-button"]');
        
        // 一覧で確認
        await page.goto('/products');
        await expect(page.locator('text=TEST001')).toBeVisible();
        
        // 編集
        await page.click('[data-testid="edit-TEST001"]');
        await page.fill('[data-testid="product-name"]', 'テスト製品（更新）');
        await page.click('[data-testid="save-button"]');
        
        // 削除
        await page.click('[data-testid="delete-TEST001"]');
        await page.click('[data-testid="confirm-delete"]');
        
        await expect(page.locator('text=TEST001')).not.toBeVisible();
      });
    });
  `
};
```

## 同期タイプ別仕様

### 1. 仕様→バックエンド（spec_to_backend）
```yaml
目的: フロントエンド仕様からバックエンドAPI要求を生成
フロー:
  1. Vue3コンポーネント・ストア分析
  2. 必要なAPI仕様の抽出
  3. OpenAPI仕様書生成
  4. FastAPI実装要求書出力
  5. SQLAlchemyモデル要求定義
期待効果:
  - フロントエンド要件の漏れなき反映
  - 一貫したAPI設計
  - 効率的なバックエンド開発
```

### 2. API利用（api_consume）
```yaml
目的: 既存バックエンドAPIの自動フロントエンド統合
フロー:
  1. バックエンドOpenAPI仕様取得
  2. JavaScript型定義生成（JSDoc）
  3. Axiosクライアント自動生成
  4. Piniaストア自動生成
  5. Vue3コンポーネント使用例生成
期待効果:
  - 型安全なAPI利用（JSDocによる）
  - 自動化されたクライアント生成
  - 一貫したエラーハンドリング
```

### 3. 完全同期（full_sync）
```yaml
目的: フロントエンド・バックエンド双方向完全同期
フロー:
  1. フロントエンド仕様解析
  2. バックエンドAPI仕様解析
  3. 差分検出・整合性チェック
  4. 双方向同期計画生成
  5. 自動コード生成・更新
期待効果:
  - 完全な一貫性保証
  - 自動同期によるメンテナンス効率化
  - リアルタイム整合性チェック
```

### 4. バリデーション同期（validation_sync）
```yaml
目的: フロントエンド・バックエンド間のバリデーション統一
フロー:
  1. バックエンドPydanticスキーマ解析
  2. フロントエンドバリデーションルール生成
  3. Vue3フォームバリデーション適用
  4. エラーメッセージ統一
  5. テストケース自動生成
期待効果:
  - 統一されたバリデーション体験
  - ユーザビリティ向上
  - バグ削減・品質向上
```

## 連携データフォーマット

### API仕様共有フォーマット
```json
{
  "sync_metadata": {
    "timestamp": "2024-01-15T12:00:00Z",
    "sync_type": "spec_to_backend",
    "source": "vue3_frontend",
    "target": "fastapi_backend",
    "version": "1.0.0"
  },
  "api_requirements": {
    "base_url": "http://localhost:9995",
    "authentication": {
      "type": "jwt",
      "endpoints": {
        "login": "/api/v1/auth/login",
        "refresh": "/api/v1/auth/refresh",
        "logout": "/api/v1/auth/logout"
      }
    },
    "endpoints": [
      {
        "path": "/api/v1/products",
        "method": "GET",
        "description": "製品一覧取得",
        "parameters": {
          "page": {"type": "integer", "default": 1},
          "limit": {"type": "integer", "default": 20},
          "search": {"type": "string", "required": false}
        },
        "response_schema": {
          "type": "object",
          "properties": {
            "items": {"type": "array", "items": {"$ref": "#/schemas/Product"}},
            "total": {"type": "integer"},
            "page": {"type": "integer"},
            "limit": {"type": "integer"}
          }
        }
      }
    ],
    "schemas": {
      "Product": {
        "type": "object",
        "properties": {
          "id": {"type": "integer"},
          "product_code": {"type": "string", "maxLength": 50},
          "product_name": {"type": "string", "maxLength": 200},
          "category": {"type": "string", "required": false},
          "price": {"type": "number", "format": "decimal"},
          "created_at": {"type": "string", "format": "date-time"}
        },
        "required": ["product_code", "product_name"]
      }
    }
  },
  "validation_rules": {
    "client_side": {
      "Product": {
        "product_code": [
          {"rule": "required", "message": "製品コードは必須です"},
          {"rule": "maxLength", "value": 50, "message": "製品コードは50文字以内で入力してください"}
        ],
        "product_name": [
          {"rule": "required", "message": "製品名は必須です"},
          {"rule": "maxLength", "value": 200, "message": "製品名は200文字以内で入力してください"}
        ]
      }
    }
  }
}
```

### 連携テストフォーマット
```json
{
  "test_scenarios": [
    {
      "name": "製品管理フルフロー",
      "description": "製品の作成から削除までの完全テスト",
      "steps": [
        {
          "action": "login",
          "credentials": {"username": "testuser", "password": "testpass"},
          "expected": {"status": 200, "token_exists": true}
        },
        {
          "action": "create_product",
          "data": {"product_code": "TEST001", "product_name": "テスト製品"},
          "expected": {"status": 201, "id_exists": true}
        },
        {
          "action": "get_products",
          "expected": {"status": 200, "contains": "TEST001"}
        },
        {
          "action": "delete_product",
          "product_code": "TEST001",
          "expected": {"status": 204}
        }
      ]
    }
  ]
}
```

## 成功指標・KPI

### 技術指標
- **型安全性**: JavaScript型エラー削減率 95%（JSDocによる型チェック）
- **API整合性**: フロントエンド・バックエンド仕様一致率 100%
- **自動化率**: 手動API統合作業削減 80%
- **品質**: バリデーション不整合バグ削減 90%

### 開発効率指標  
- **開発時間**: API統合時間 70% 短縮
- **バグ修正**: API関連バグ修正時間 60% 短縮
- **メンテナンス**: 仕様変更時の同期時間 85% 短縮

## 使用例

### フロントエンド仕様からバックエンド生成
```bash
# Vue3コンポーネントからAPI要求生成
/backend-sync spec_to_backend --target_feature="products" --validation_level="full"
```

### 既存APIの自動フロントエンド統合
```bash
# FastAPI仕様からVue3クライアント生成
/backend-sync api_consume --target_feature="all" --sync_direction="backend_to_frontend"
```

### 完全双方向同期
```bash
# フロントエンド・バックエンド完全同期
/backend-sync full_sync --validation_level="strict"
```

## 注意事項・制約

### 技術制約
- OpenAPI 3.0仕様への準拠が必要
- Vue3 Composition API + Pinia構成前提
- FastAPI + SQLAlchemy構成前提

### 同期制約
- リアルタイム同期は準リアルタイム（数分間隔）
- 複雑なビジネスロジックは手動調整が必要
- カスタムバリデーションは個別対応

### 品質保証
- 自動生成コードの品質レビュー推奨
- E2Eテストによる動作確認必須
- セキュリティ監査の定期実施