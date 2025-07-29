# Vue3 + Axios フロントエンド・バックエンド完全統合ガイド

## 概要

このドキュメントでは、Vue.js 3 (Composition API) + Axios を使用したフロントエンドと、FastAPI + SQLAlchemy バックエンドの完全統合パターンについて説明します。

## アーキテクチャ統合概要

### システム構成
```mermaid
graph TB
    subgraph "Frontend (Vue3 + Axios)"
        UI[Vue Components]
        Store[Pinia Stores]
        Service[API Services]
        Middleware[Axios Interceptors]
    end
    
    subgraph "Backend (FastAPI + SQLAlchemy)"
        API[FastAPI Endpoints]
        Auth[JWT Authentication]
        Service_Layer[Service Layer]
        Repository[Repository Pattern]
        DB[SQLAlchemy Models]
    end
    
    UI --> Store
    Store --> Service
    Service --> Middleware
    Middleware --> API
    API --> Auth
    API --> Service_Layer
    Service_Layer --> Repository
    Repository --> DB
```

### 技術スタック統合
| Layer | Frontend | Backend | Integration |
|-------|----------|---------|-----------|
| Presentation | Vue.js 3 Components | FastAPI Routes | REST API |
| State Management | Pinia Stores | FastAPI Dependencies | Reactive Data Sync |
| Data Access | Axios Services | SQLAlchemy Repository | HTTP/JSON |
| Authentication | JWT Token Management | JWT Authentication | Bearer Token |
| Validation | Vue/Vuelidate | Pydantic Models | Schema Validation |

## API 統合パターン

### 1. 基本設定

#### フロントエンド API クライアント設定
```javascript
// lib/api/client.js
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// リクエストインターセプター
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// レスポンスインターセプター
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()
    
    if (error.response?.status === 401) {
      try {
        await authStore.refreshToken()
        return apiClient(error.config)
      } catch (refreshError) {
        authStore.logout()
        throw refreshError
      }
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
```

#### バックエンド CORS 設定
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Vue3 + FastAPI Integration API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Vue dev server
        "http://localhost:5173",  # Vite dev server
        "https://yourdomain.com"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 認証統合

#### フロントエンド認証ストア
```javascript
// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const user = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value)

  const login = async (credentials) => {
    loading.value = true
    
    try {
      const response = await authService.login(credentials)
      
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token
      user.value = response.user
      
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const refreshTokenAction = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    const response = await authService.refreshToken(refreshToken.value)
    
    accessToken.value = response.access_token
    localStorage.setItem('access_token', response.access_token)
    
    if (response.refresh_token) {
      refreshToken.value = response.refresh_token
      localStorage.setItem('refresh_token', response.refresh_token)
    }
    
    return response
  }

  const logout = async () => {
    try {
      if (accessToken.value) {
        await authService.logout()
      }
    } finally {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
      
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  const fetchCurrentUser = async () => {
    if (!accessToken.value) return null
    
    try {
      const userData = await authService.getCurrentUser()
      user.value = userData
      return userData
    } catch (error) {
      if (error.status === 401) {
        await logout()
      }
      throw error
    }
  }

  return {
    accessToken: computed(() => accessToken.value),
    refreshToken: computed(() => refreshToken.value),
    user: computed(() => user.value),
    loading: computed(() => loading.value),
    isAuthenticated,
    login,
    refreshToken: refreshTokenAction,
    logout,
    fetchCurrentUser
  }
}, {
  persist: {
    paths: ['accessToken', 'refreshToken']
  }
})
```

#### バックエンド認証システム
```python
# auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta

from database import get_db
from models import User
from auth.security import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """現在認証されているユーザーを取得"""
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def require_roles(*required_roles: str):
    """指定されたロールを持つユーザーのみアクセス許可"""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker
```

### 3. データフェッチング統合

#### フロントエンド データサービス
```javascript
// services/dataService.js
import apiClient from '@/lib/api/client'

export const dataService = {
  /**
   * ページネーション付きデータ取得
   * @param {string} endpoint - API エンドポイント
   * @param {Object} params - クエリパラメータ
   * @returns {Promise<Object>} ページネーション結果
   */
  async getPaginatedData(endpoint, params = {}) {
    const response = await apiClient.get(endpoint, { params })
    return {
      data: response.data.data,
      total: response.data.total,
      page: response.data.page,
      limit: response.data.limit,
      pages: response.data.pages
    }
  },

  /**
   * リソース作成
   * @param {string} endpoint - API エンドポイント
   * @param {Object} data - 作成データ
   * @returns {Promise<Object>} 作成されたリソース
   */
  async createResource(endpoint, data) {
    const response = await apiClient.post(endpoint, data)
    return response.data
  },

  /**
   * リソース更新
   * @param {string} endpoint - API エンドポイント
   * @param {Object} data - 更新データ
   * @returns {Promise<Object>} 更新されたリソース
   */
  async updateResource(endpoint, data) {
    const response = await apiClient.put(endpoint, data)
    return response.data
  },

  /**
   * リソース削除
   * @param {string} endpoint - API エンドポイント
   * @returns {Promise<void>}
   */
  async deleteResource(endpoint) {
    await apiClient.delete(endpoint)
  }
}
```

#### バックエンド ページネーション
```python
# utils/pagination.py
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Query
from math import ceil

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """ページネーションレスポンス"""
    data: List[T]
    total: int
    page: int
    limit: int
    pages: int

def paginate(
    query: Query,
    page: int = 1,
    limit: int = 50,
    max_limit: int = 100
) -> tuple[List, int]:
    """クエリをページネーション"""
    limit = min(limit, max_limit)
    offset = (page - 1) * limit
    
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return items, total

# routers/example.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from utils.pagination import paginate, PaginatedResponse

router = APIRouter()

@router.get("/items", response_model=PaginatedResponse[ItemResponse])
async def get_items(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """アイテム一覧取得（ページネーション付き）"""
    query = db.query(Item)
    items, total = paginate(query, page, limit)
    
    return PaginatedResponse(
        data=[ItemResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        limit=limit,
        pages=ceil(total / limit)
    )
```

### 4. リアルタイム通信統合

#### フロントエンド WebSocket
```javascript
// composables/useWebSocket.js
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useWebSocket(url) {
  const socket = ref(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5

  const authStore = useAuthStore()

  const connect = () => {
    const wsUrl = `${url}?token=${authStore.accessToken}`
    socket.value = new WebSocket(wsUrl)

    socket.value.onopen = () => {
      isConnected.value = true
      reconnectAttempts.value = 0
      console.log('WebSocket connected')
    }

    socket.value.onclose = () => {
      isConnected.value = false
      console.log('WebSocket disconnected')
      
      // 自動再接続
      if (reconnectAttempts.value < maxReconnectAttempts) {
        setTimeout(() => {
          reconnectAttempts.value++
          connect()
        }, 1000 * Math.pow(2, reconnectAttempts.value))
      }
    }

    socket.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  const send = (data) => {
    if (socket.value && isConnected.value) {
      socket.value.send(JSON.stringify(data))
    }
  }

  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
    }
  }

  onMounted(connect)
  onUnmounted(disconnect)

  return {
    socket,
    isConnected,
    send,
    disconnect
  }
}
```

#### バックエンド WebSocket
```python
# websocket/manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio

class ConnectionManager:
    """WebSocket接続管理"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        """WebSocket接続を受け入れ"""
        await websocket.accept()
        
        if room not in self.active_connections:
            self.active_connections[room] = []
        
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        """WebSocket接続を切断"""
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)
            
            if not self.active_connections[room]:
                del self.active_connections[room]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """個人メッセージ送信"""
        await websocket.send_text(message)

    async def broadcast_to_room(self, message: str, room: str):
        """ルーム内全体にブロードキャスト"""
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                try:
                    await connection.send_text(message)
                except:
                    # 接続が切れている場合は削除
                    self.active_connections[room].remove(connection)

manager = ConnectionManager()

# websocket/routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from auth.dependencies import get_current_user_ws

router = APIRouter()

@router.websocket("/ws/{room}")
async def websocket_endpoint(
    websocket: WebSocket,
    room: str,
    user: User = Depends(get_current_user_ws)
):
    await manager.connect(websocket, room)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # メッセージをルーム内にブロードキャスト
            await manager.broadcast_to_room(
                json.dumps({
                    "user": user.username,
                    "message": message_data.get("message", ""),
                    "timestamp": datetime.now().isoformat()
                }),
                room
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
```

### 5. エラーハンドリング統合

#### フロントエンド エラー管理
```javascript
// stores/error.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useErrorStore = defineStore('error', () => {
  const errors = ref([])
  const globalError = ref(null)

  const addError = (error) => {
    const errorObj = {
      id: Date.now(),
      message: error.message || 'An error occurred',
      type: error.type || 'error',
      timestamp: new Date(),
      details: error.details || null
    }
    
    errors.value.push(errorObj)
    
    // 自動削除（5秒後）
    setTimeout(() => {
      removeError(errorObj.id)
    }, 5000)
  }

  const removeError = (id) => {
    const index = errors.value.findIndex(e => e.id === id)
    if (index > -1) {
      errors.value.splice(index, 1)
    }
  }

  const setGlobalError = (error) => {
    globalError.value = error
  }

  const clearGlobalError = () => {
    globalError.value = null
  }

  return {
    errors,
    globalError,
    addError,
    removeError,
    setGlobalError,
    clearGlobalError
  }
})
```

#### バックエンド エラーハンドラー
```python
# exceptions/handlers.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP例外ハンドラー"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """バリデーション例外ハンドラー"""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """データベース整合性エラーハンドラー"""
    logger.error(f"Database integrity error: {exc}")
    
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "INTEGRITY_ERROR",
                "message": "Data integrity constraint violation",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

# main.py での登録
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
```

### 6. パフォーマンス最適化

#### フロントエンド キャッシュ戦略
```javascript
// composables/useApiCache.js
import { ref, computed } from 'vue'

class ApiCache {
  constructor(ttl = 5 * 60 * 1000) { // 5分のTTL
    this.cache = new Map()
    this.ttl = ttl
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  get(key) {
    const item = this.cache.get(key)
    if (!item) return null

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.data
  }

  invalidate(pattern) {
    const keys = Array.from(this.cache.keys())
    keys.forEach(key => {
      if (key.includes(pattern)) {
        this.cache.delete(key)
      }
    })
  }

  clear() {
    this.cache.clear()
  }
}

const apiCache = new ApiCache()

export function useApiCache() {
  const getCached = (key) => apiCache.get(key)
  const setCached = (key, data) => apiCache.set(key, data)
  const invalidateCache = (pattern) => apiCache.invalidate(pattern)
  const clearCache = () => apiCache.clear()

  return {
    getCached,
    setCached,
    invalidateCache,
    clearCache
  }
}
```

#### バックエンド キャッシュ実装
```python
# utils/cache.py
from functools import wraps
from typing import Any, Optional
import json
import redis
from datetime import timedelta

# Redis クライアント設定
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

def cache_result(expiration: timedelta = timedelta(minutes=5)):
    """結果をキャッシュするデコレータ"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # キャッシュキー生成
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # キャッシュから取得試行
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # キャッシュにない場合は実行
            result = await func(*args, **kwargs)
            
            # 結果をキャッシュに保存
            redis_client.setex(
                cache_key,
                expiration,
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

# 使用例
@cache_result(expiration=timedelta(minutes=10))
async def get_expensive_data():
    """重い処理のキャッシュ例"""
    # 重い計算処理
    pass
```

## 統合テスト戦略

### E2Eテスト
```javascript
// tests/e2e/integration.spec.js
import { test, expect } from '@playwright/test'

test.describe('Frontend-Backend Integration', () => {
  test('User authentication flow', async ({ page }) => {
    // ログインページに移動
    await page.goto('/login')
    
    // 認証情報入力
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    
    // ログインボタンクリック
    await page.click('[data-testid="login-button"]')
    
    // ダッシュボードへのリダイレクト確認
    await expect(page).toHaveURL('/dashboard')
    
    // 認証後のAPIリクエスト確認
    const response = await page.waitForResponse('/api/auth/me')
    expect(response.status()).toBe(200)
  })

  test('Data CRUD operations', async ({ page }) => {
    // 認証済みセットアップ
    await page.goto('/dashboard')
    
    // データ作成
    await page.click('[data-testid="create-button"]')
    await page.fill('[data-testid="name-input"]', 'Test Item')
    await page.click('[data-testid="save-button"]')
    
    // 作成確認
    await expect(page.locator('[data-testid="item-list"]')).toContainText('Test Item')
    
    // データ更新
    await page.click('[data-testid="edit-button"]')
    await page.fill('[data-testid="name-input"]', 'Updated Item')
    await page.click('[data-testid="save-button"]')
    
    // 更新確認
    await expect(page.locator('[data-testid="item-list"]')).toContainText('Updated Item')
  })
})
```

### API統合テスト
```python
# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_authentication_flow():
    """認証フロー統合テスト"""
    # ログイン
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    
    # 認証必須エンドポイントへアクセス
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = client.get("/api/auth/me", headers=headers)
    
    assert profile_response.status_code == 200
    user_data = profile_response.json()
    assert user_data["email"] == "test@example.com"

def test_data_operations_with_auth():
    """認証付きデータ操作テスト"""
    # 認証取得
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # データ作成
    create_response = client.post("/api/items", 
        json={"name": "Test Item", "description": "Test Description"},
        headers=headers
    )
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # データ取得
    get_response = client.get(f"/api/items/{item_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Item"
    
    # データ更新
    update_response = client.put(f"/api/items/{item_id}",
        json={"name": "Updated Item", "description": "Updated Description"},
        headers=headers
    )
    assert update_response.status_code == 200
    
    # データ削除
    delete_response = client.delete(f"/api/items/{item_id}", headers=headers)
    assert delete_response.status_code == 204
```

## デプロイメント統合

### Docker Compose 統合
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### CI/CD パイプライン
```yaml
# .github/workflows/deploy.yml
name: Deploy Full Stack Application

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Frontend Dependencies
        run: |
          cd frontend
          npm install
          
      - name: Install Backend Dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          
      - name: Run Frontend Tests
        run: |
          cd frontend
          npm run test
          
      - name: Run Backend Tests
        run: |
          cd backend
          pytest
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          
      - name: Run E2E Tests
        run: |
          docker-compose up -d
          cd frontend
          npm run test:e2e
          docker-compose down

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        run: |
          # デプロイスクリプト実行
          ./deploy.sh
```

このガイドに従って、Vue3 + Axios フロントエンドと FastAPI + SQLAlchemy バックエンドの完全統合を実現してください。