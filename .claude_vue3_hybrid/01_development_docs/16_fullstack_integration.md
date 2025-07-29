# フルスタック統合設計 - Vue3 + FastAPI

## 概要

Vue3 + Axiosフロントエンドと、FastAPI + SQLAlchemyバックエンドの完全統合を実現する設計ドキュメントです。ハイブリッド接続アーキテクチャの一部として、プライマリバックエンドとしてのFastAPIとの統合を詳述します。

## システムアーキテクチャ

### 1. 全体構成図

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Vue3 UI Components]
        Store[Pinia Stores]
        Router[Vue Router]
        Services[Service Layer]
    end
    
    subgraph "Connection Layer"
        HybridManager[Hybrid Connection Manager]
        FastAPIClient[FastAPI Client]
        SupabaseClient[Supabase Client]
        JSONStorage[JSON File Storage]
    end
    
    subgraph "Backend Layer"
        FastAPI[FastAPI Application]
        SQLAlchemy[SQLAlchemy ORM]
        Database[(Database)]
    end
    
    subgraph "Fallback Systems"
        Supabase[Supabase Backend]
        LocalFiles[Local JSON Files]
    end
    
    UI --> Store
    Store --> Services
    Services --> HybridManager
    
    HybridManager --> FastAPIClient
    HybridManager --> SupabaseClient
    HybridManager --> JSONStorage
    
    FastAPIClient --> FastAPI
    FastAPI --> SQLAlchemy
    SQLAlchemy --> Database
    
    SupabaseClient --> Supabase
    JSONStorage --> LocalFiles
```

### 2. データフロー設計

```mermaid
sequenceDiagram
    participant UI as Vue3 Component
    participant Store as Pinia Store
    participant Hybrid as Hybrid Manager
    participant FastAPI as FastAPI Backend
    participant Supabase as Supabase
    participant JSON as JSON Files
    
    UI->>Store: Action Call
    Store->>Hybrid: Request Data
    
    alt FastAPI Available
        Hybrid->>FastAPI: HTTP Request
        FastAPI-->>Hybrid: Response
        Hybrid->>JSON: Cache Result
    else FastAPI Unavailable
        Hybrid->>Supabase: Fallback Request
        Supabase-->>Hybrid: Response
        Hybrid->>JSON: Cache Result
    else All Online Unavailable
        Hybrid->>JSON: Load Cached Data
        JSON-->>Hybrid: Cached Response
    end
    
    Hybrid-->>Store: Final Result
    Store-->>UI: Update State
```

## FastAPI統合仕様

### 1. API エンドポイント設計

#### 認証エンドポイント
```python
# FastAPI Backend - main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import jwt
from datetime import datetime, timedelta

app = FastAPI()

# CORS設定（Vue3フロントエンド対応）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 認証エンドポイント
@app.post("/auth/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@app.post("/auth/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        new_token = create_access_token(data={"sub": username})
        return {"access_token": new_token, "token_type": "bearer"}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/auth/me")
async def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user
```

#### CRUD エンドポイント
```python
# データ操作エンドポイント
@app.get("/items/", response_model=PaginatedResponse[ItemResponse])
async def get_items(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * size
    
    query = db.query(Item)
    if search:
        query = query.filter(Item.name.contains(search))
    
    total = query.count()
    items = query.offset(skip).limit(size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items/", response_model=ItemResponse)
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = Item(**item.dict(), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}
```

### 2. SQLAlchemy モデル設計

```python
# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    items = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    owner = relationship("User", back_populates="items")
```

### 3. Pydantic スキーマ設計

```python
# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ベーススキーマ
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True

# 認証関連
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseSchema):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

# アイテム関連
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ItemResponse(BaseSchema):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

# ページネーション
from typing import TypeVar, Generic
from pydantic.generics import GenericModel

T = TypeVar('T')

class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
```

## フロントエンド統合実装

### 1. 環境設定統合

```javascript
// .env
# FastAPI Backend
VUE_APP_FASTAPI_URL=http://localhost:8000
VUE_APP_FASTAPI_TIMEOUT=10000

# Supabase Fallback
VUE_APP_SUPABASE_URL=your-supabase-url
VUE_APP_SUPABASE_ANON_KEY=your-anon-key

# Connection Strategy
VUE_APP_CONNECTION_PRIORITY=fastapi,supabase,offline
VUE_APP_ENABLE_OFFLINE_CACHE=true
VUE_APP_OFFLINE_CACHE_TTL=3600000
```

### 2. Vue Router統合

```javascript
// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useFastApiAuthStore } from '@/stores/fastApiAuthStore'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/items',
    name: 'Items',
    component: () => import('@/views/ItemListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/items/create',
    name: 'CreateItem',
    component: () => import('@/views/CreateItemView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/items/:id/edit',
    name: 'EditItem',
    component: () => import('@/views/EditItemView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// FastAPI認証ガード
router.beforeEach(async (to, from, next) => {
  const authStore = useFastApiAuthStore()
  
  // 認証が必要なルート
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }
    
    // トークンの有効性を確認
    try {
      await authStore.fetchCurrentUser()
      next()
    } catch (error) {
      next('/login')
    }
  }
  // ゲストのみアクセス可能なルート
  else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/dashboard')
  }
  else {
    next()
  }
})

export default router
```

### 3. メインアプリケーション統合

```javascript
// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// CSS
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// FastAPI認証の初期化
import { useFastApiAuthStore } from '@/stores/fastApiAuthStore'

const initializeApp = async () => {
  const authStore = useFastApiAuthStore()
  
  // 保存された認証状態を復元
  await authStore.initialize()
  
  app.mount('#app')
}

initializeApp()
```

## 開発・デプロイ統合

### 1. Docker Compose統合

```yaml
# docker-compose.yml
version: '3.8'

services:
  # FastAPI Backend
  fastapi:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/dbname
      - SECRET_KEY=your-secret-key
    depends_on:
      - postgres
    volumes:
      - ./backend:/app
    
  # PostgreSQL Database
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  # Vue3 Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VUE_APP_FASTAPI_URL=http://fastapi:8000
    depends_on:
      - fastapi
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

### 2. CI/CD統合

```yaml
# .github/workflows/fullstack.yml
name: Fullstack CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install backend dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        
    - name: Test FastAPI
      run: |
        cd backend
        pytest
        
  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci
        
    - name: Test Vue3
      run: |
        cd frontend
        npm run test:unit
        
    - name: Build frontend
      run: |
        cd frontend
        npm run build
        
  e2e-test:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run E2E tests
      run: |
        docker-compose up -d
        npm run test:e2e
        docker-compose down
```

## 統合テスト戦略

### 1. ユニットテスト

```javascript
// tests/unit/stores/fastApiDataStore.spec.js
import { describe, it, expect, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFastApiDataStore } from '@/stores/fastApiDataStore'
import { fastApiService } from '@/services/fastApiService'

vi.mock('@/services/fastApiService')

describe('FastApiDataStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  
  it('should fetch items successfully', async () => {
    const mockItems = [
      { id: 1, name: 'Test Item 1' },
      { id: 2, name: 'Test Item 2' }
    ]
    
    fastApiService.getItems.mockResolvedValue({
      items: mockItems,
      total: 2,
      page: 1,
      size: 50
    })
    
    const store = useFastApiDataStore()
    await store.fetchItems()
    
    expect(store.items).toEqual(mockItems)
    expect(store.pagination.total).toBe(2)
  })
})
```

### 2. 統合テスト

```javascript
// tests/integration/api.spec.js
import { describe, it, expect } from 'vitest'
import { fastApiClient } from '@/services/fastApiClient'

describe('FastAPI Integration', () => {
  it('should authenticate user', async () => {
    const response = await fastApiClient.post('/auth/login', {
      username: 'testuser',
      password: 'testpass'
    })
    
    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('access_token')
    expect(response.data).toHaveProperty('user')
  })
  
  it('should create and retrieve item', async () => {
    // ログイン
    const loginResponse = await fastApiClient.post('/auth/login', {
      username: 'testuser',
      password: 'testpass'
    })
    
    const token = loginResponse.data.access_token
    
    // アイテム作成
    const createResponse = await fastApiClient.post('/items/', {
      name: 'Test Item',
      description: 'Test Description'
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    expect(createResponse.status).toBe(200)
    const itemId = createResponse.data.id
    
    // アイテム取得
    const getResponse = await fastApiClient.get(`/items/${itemId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    expect(getResponse.status).toBe(200)
    expect(getResponse.data.name).toBe('Test Item')
  })
})
```

### 3. E2Eテスト

```javascript
// tests/e2e/fullstack.spec.js
import { test, expect } from '@playwright/test'

test.describe('Fullstack Flow', () => {
  test('should complete full user journey', async ({ page }) => {
    // ログインページに移動
    await page.goto('/login')
    
    // ログイン
    await page.fill('[data-testid="username"]', 'testuser')
    await page.fill('[data-testid="password"]', 'testpass')
    await page.click('[data-testid="login-button"]')
    
    // ダッシュボードに移動
    await expect(page).toHaveURL('/dashboard')
    
    // アイテムリストに移動
    await page.click('[data-testid="items-link"]')
    await expect(page).toHaveURL('/items')
    
    // アイテム作成
    await page.click('[data-testid="create-item-button"]')
    await page.fill('[data-testid="item-name"]', 'E2E Test Item')
    await page.fill('[data-testid="item-description"]', 'Created by E2E test')
    await page.click('[data-testid="submit-button"]')
    
    // アイテムがリストに表示されることを確認
    await expect(page.locator('text=E2E Test Item')).toBeVisible()
    
    // アイテム編集
    await page.click('[data-testid="edit-item-button"]')
    await page.fill('[data-testid="item-name"]', 'Updated E2E Test Item')
    await page.click('[data-testid="submit-button"]')
    
    // 更新されたアイテムが表示されることを確認
    await expect(page.locator('text=Updated E2E Test Item')).toBeVisible()
  })
})
```

## パフォーマンス最適化

### 1. フロントエンド最適化

```javascript
// src/composables/useOptimizedFetch.js
import { ref, computed } from 'vue'
import { debounce } from 'lodash-es'

export function useOptimizedFetch(fetchFn, options = {}) {
  const data = ref(null)
  const isLoading = ref(false) 
  const error = ref(null)
  const cache = new Map()
  
  const debouncedFetch = debounce(async (params) => {
    const cacheKey = JSON.stringify(params)
    
    // キャッシュチェック
    if (cache.has(cacheKey) && !options.skipCache) {
      data.value = cache.get(cacheKey)
      return
    }
    
    try {
      isLoading.value = true
      error.value = null
      
      const result = await fetchFn(params)
      data.value = result
      
      // キャッシュに保存（TTL付き）
      cache.set(cacheKey, result)
      setTimeout(() => cache.delete(cacheKey), options.cacheTTL || 5 * 60 * 1000)
      
    } catch (err) {
      error.value = err
    } finally {
      isLoading.value = false
    }
  }, options.debounceMs || 300)
  
  return {
    data: computed(() => data.value),
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    fetch: debouncedFetch,
    clearCache: () => cache.clear()
  }
}
```

### 2. バックエンド最適化

```python
# FastAPI最適化設定
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import selectinload

app = FastAPI()

# GZip圧縮
app.add_middleware(GZipMiddleware, minimum_size=1000)

# データベースクエリ最適化
@app.get("/items/", response_model=PaginatedResponse[ItemResponse])
async def get_items_optimized(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # N+1問題を防ぐためのJOIN
    query = db.query(Item).options(selectinload(Item.owner))
    
    if search:
        # 全文検索インデックスを使用
        query = query.filter(Item.search_vector.match(search))
    
    # カウントクエリの最適化
    total = query.count()
    
    # ページネーションとソート
    items = (query
            .order_by(Item.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all())
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )
```

このフルスタック統合設計により、Vue3 + AxiosフロントエンドとFastAPI + SQLAlchemyバックエンドが完全に統合され、ハイブリッド接続システムの一部として高い可用性とパフォーマンスを実現します。