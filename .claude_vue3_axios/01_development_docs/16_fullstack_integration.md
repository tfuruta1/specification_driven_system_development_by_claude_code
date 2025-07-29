# Vue3 + FastAPI フルスタック統合設計書

## 概要

このドキュメントでは、Vue.js 3 (Composition API) + Axios フロントエンドと FastAPI + SQLAlchemy バックエンドによる完全なフルスタックWebアプリケーションの統合設計について詳細に説明します。

## 統合アーキテクチャ

### システム全体構成図
```mermaid
graph TB
    subgraph "Client Tier"
        Browser[Web Browser]
        Mobile[Mobile App]
        Desktop[Desktop App]
    end
    
    subgraph "Presentation Tier (Vue.js 3)"
        VueApp[Vue.js Application]
        Components[Vue Components]
        Composables[Vue Composables]
        Pinia[Pinia State Management]
        Router[Vue Router]
        AxiosClient[Axios HTTP Client]
    end
    
    subgraph "API Gateway Tier"
        LoadBalancer[Load Balancer]
        RateLimit[Rate Limiting]
        SSL[SSL Termination]
    end
    
    subgraph "Application Tier (FastAPI)"
        FastAPIApp[FastAPI Application]
        APIRouters[API Routers]
        Middleware[Middleware Stack]
        AuthService[Authentication Service]
        BusinessLogic[Business Logic Layer]
        ValidationLayer[Validation Layer]
    end
    
    subgraph "Data Access Tier"
        SQLAlchemy[SQLAlchemy ORM]
        Repository[Repository Pattern]
        CRUDOperations[CRUD Operations]
        DatabaseMigrations[Database Migrations]
    end
    
    subgraph "Data Tier"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis Cache)]
        FileStorage[File Storage]
        SearchEngine[Search Engine]
    end
    
    subgraph "External Services"
        EmailService[Email Service]
        PaymentGateway[Payment Gateway]  
        CloudStorage[Cloud Storage]
        MonitoringService[Monitoring]
    end
    
    Browser --> VueApp
    Mobile --> VueApp
    Desktop --> VueApp
    
    VueApp --> Components
    Components --> Composables
    Components --> Pinia
    VueApp --> Router
    Pinia --> AxiosClient
    
    AxiosClient --> LoadBalancer
    LoadBalancer --> RateLimit
    RateLimit --> SSL
    SSL --> FastAPIApp
    
    FastAPIApp --> APIRouters
    APIRouters --> Middleware
    Middleware --> AuthService
    AuthService --> BusinessLogic
    BusinessLogic --> ValidationLayer
    ValidationLayer --> SQLAlchemy
    
    SQLAlchemy --> Repository
    Repository --> CRUDOperations
    CRUDOperations --> DatabaseMigrations
    DatabaseMigrations --> PostgreSQL
    
    BusinessLogic --> Redis
    BusinessLogic --> FileStorage
    BusinessLogic --> SearchEngine
    
    BusinessLogic --> EmailService
    BusinessLogic --> PaymentGateway
    BusinessLogic --> CloudStorage
    FastAPIApp --> MonitoringService
```

### 技術スタック対応表
| Layer | Frontend | Backend | Integration |
|-------|----------|---------|-------------|
| **UI Layer** | Vue.js 3 Components + DaisyUI | FastAPI Templates (Optional) | Server-Side Rendering |
| **State Management** | Pinia Stores | FastAPI Dependencies | Real-time Synchronization |
| **Routing** | Vue Router | FastAPI Routers | Dynamic Route Generation |
| **HTTP Client** | Axios | HTTPx (Internal) | RESTful API |
| **Authentication** | JWT Token Management | OAuth2 + JWT | Bearer Token Flow |
| **Validation** | Vuelidate + Custom | Pydantic Models | Schema Validation |
| **ORM/Models** | TypeScript/JSDoc Types | SQLAlchemy Models | Type-safe Data Transfer |
| **Caching** | Browser Cache + Memory | Redis + FastAPI Cache | Multi-layer Caching |
| **File Handling** | File Upload Components | FastAPI File Handling | Multipart/Form-data |
| **Real-time** | WebSocket Client | FastAPI WebSocket | Bi-directional Communication |
| **Testing** | Vitest + Vue Test Utils | pytest + FastAPI TestClient | End-to-End Testing |
| **Build/Deploy** | Vite + Static Hosting | Uvicorn + Docker | Container Orchestration |

## 統合設計パターン

### 1. データフロー統合パターン

#### リクエスト-レスポンスフロー
```mermaid
sequenceDiagram
    participant User
    participant VueComponent
    participant PiniaStore
    participant AxiosService
    participant FastAPIRouter
    participant BusinessService
    participant SQLAlchemyRepo
    participant Database
    
    User->>VueComponent: User Action
    VueComponent->>PiniaStore: Dispatch Action
    PiniaStore->>AxiosService: HTTP Request
    AxiosService->>FastAPIRouter: REST API Call
    FastAPIRouter->>BusinessService: Business Logic
    BusinessService->>SQLAlchemyRepo: Data Operation
    SQLAlchemyRepo->>Database: SQL Query
    Database-->>SQLAlchemyRepo: Query Result
    SQLAlchemyRepo-->>BusinessService: Domain Object
    BusinessService-->>FastAPIRouter: Response Data
    FastAPIRouter-->>AxiosService: JSON Response
    AxiosService-->>PiniaStore: Parsed Data
    PiniaStore-->>VueComponent: Reactive State
    VueComponent-->>User: UI Update
```

#### 統合データモデル設計
```typescript
// Frontend Type Definitions (TypeScript/JSDoc)
/**
 * @typedef {Object} User
 * @property {number} id - User ID
 * @property {string} username - Username
 * @property {string} email - Email address
 * @property {string} full_name - Full name
 * @property {boolean} is_active - Active status
 * @property {string} created_at - Creation timestamp (ISO string)
 * @property {string} updated_at - Update timestamp (ISO string)
 */

/**
 * @typedef {Object} ApiResponse
 * @template T
 * @property {boolean} success - Success status
 * @property {T} data - Response data
 * @property {string} [message] - Optional message
 * @property {string} timestamp - Response timestamp
 */

/**
 * @typedef {Object} PaginatedResponse
 * @template T
 * @property {T[]} data - Array of items
 * @property {PaginationMeta} meta - Pagination metadata
 */

/**
 * @typedef {Object} PaginationMeta
 * @property {number} total - Total items
 * @property {number} page - Current page
 * @property {number} limit - Items per page
 * @property {number} pages - Total pages
 * @property {boolean} has_next - Has next page
 * @property {boolean} has_prev - Has previous page
 */
```

```python
# Backend Model Definitions (SQLAlchemy + Pydantic)
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Generic, TypeVar

Base = declarative_base()

# SQLAlchemy Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta
```

### 2. 認証・認可統合パターン

#### JWT認証フロー
```mermaid
sequenceDiagram
    participant Frontend
    participant AuthStore
    participant AxiosInterceptor
    participant AuthAPI
    participant JWTService
    participant Database
    
    Frontend->>AuthStore: login(credentials)
    AuthStore->>AuthAPI: POST /auth/login
    AuthAPI->>Database: Validate User
    Database-->>AuthAPI: User Data
    AuthAPI->>JWTService: Generate Tokens
    JWTService-->>AuthAPI: Access + Refresh Tokens
    AuthAPI-->>AuthStore: Token Response
    AuthStore->>AuthStore: Store Tokens
    AuthStore-->>Frontend: Success Response
    
    Note over AxiosInterceptor: Automatic Token Attachment
    Frontend->>AxiosInterceptor: API Request
    AxiosInterceptor->>AxiosInterceptor: Add Bearer Token
    AxiosInterceptor->>AuthAPI: Authenticated Request
    
    Note over AuthAPI: Token Validation
    AuthAPI->>JWTService: Verify Token
    JWTService-->>AuthAPI: User Info
    AuthAPI-->>AxiosInterceptor: API Response
    
    Note over AxiosInterceptor: Auto Token Refresh
    AxiosInterceptor->>AxiosInterceptor: Check 401 Error
    AxiosInterceptor->>AuthAPI: POST /auth/refresh
    AuthAPI-->>AxiosInterceptor: New Access Token
    AxiosInterceptor->>AuthStore: Update Token
    AxiosInterceptor->>AxiosInterceptor: Retry Original Request
```

#### 統合認証実装
```javascript
// Frontend Authentication Store (Pinia)
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const user = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => {
    if (!accessToken.value) return false
    
    try {
      const payload = JSON.parse(atob(accessToken.value.split('.')[1]))
      return payload.exp > Date.now() / 1000
    } catch {
      return false
    }
  })

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
    } finally {
      loading.value = false
    }
  }

  const refreshAccessToken = async () => {
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

  return {
    accessToken: computed(() => accessToken.value),
    refreshToken: computed(() => refreshToken.value),
    user: computed(() => user.value),
    loading: computed(() => loading.value),
    isAuthenticated,
    login,
    refreshAccessToken,
    logout
  }
}, {
  persist: {
    paths: ['accessToken', 'refreshToken', 'user']
  }
})
```

```python
# Backend Authentication Service (FastAPI)
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

async def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    username = payload.get("sub")
    token_type = payload.get("type")
    
    if username is None or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

# Authentication Router
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = AuthService.create_access_token({"sub": user.username})
    refresh_token = AuthService.create_refresh_token({"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    payload = AuthService.verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    new_access_token = AuthService.create_access_token({"sub": user.username})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
```

### 3. エラーハンドリング統合パターン

#### 統合エラーハンドリングフロー
```mermaid
graph TB
    subgraph "Frontend Error Handling"
        VueError[Vue Component Error]
        GlobalErrorHandler[Global Error Handler]
        AxiosInterceptor[Axios Response Interceptor]
        ErrorStore[Error Store]
        NotificationSystem[Notification System]
    end
    
    subgraph "Backend Error Handling"
        FastAPIError[FastAPI Route Error]
        ExceptionHandler[Exception Handler]
        CustomExceptions[Custom Exceptions]
        ErrorMiddleware[Error Middleware]
        LoggingSystem[Logging System]
    end
    
    VueError --> GlobalErrorHandler
    AxiosInterceptor --> ErrorStore
    ErrorStore --> NotificationSystem
    
    FastAPIError --> ExceptionHandler
    ExceptionHandler --> CustomExceptions
    CustomExceptions --> ErrorMiddleware
    ErrorMiddleware --> LoggingSystem
    
    AxiosInterceptor <--> ExceptionHandler
```

#### エラーハンドリング実装
```javascript
// Frontend Error Management
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
      code: error.code || 'UNKNOWN_ERROR',
      timestamp: new Date(),
      details: error.details || null,
      context: error.context || null
    }
    
    errors.value.push(errorObj)
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      removeError(errorObj.id)
    }, 5000)
    
    return errorObj
  }

  const removeError = (id) => {
    const index = errors.value.findIndex(e => e.id === id)
    if (index > -1) {
      errors.value.splice(index, 1)
    }
  }

  const handleApiError = (error) => {
    if (error.response) {
      // Server responded with error status
      const apiError = {
        message: error.response.data?.error?.message || 'Server Error',
        type: 'api_error',
        code: error.response.data?.error?.code || `HTTP_${error.response.status}`,
        status: error.response.status,
        details: error.response.data?.error?.details,
        context: {
          url: error.config?.url,
          method: error.config?.method
        }
      }
      
      return addError(apiError)
    } else if (error.request) {
      // Network error
      return addError({
        message: 'Network Error - Please check your connection',
        type: 'network_error',
        code: 'NETWORK_ERROR'
      })
    } else {
      // Something else happened
      return addError({
        message: error.message || 'An unexpected error occurred',
        type: 'client_error',
        code: 'CLIENT_ERROR'
      })
    }
  }

  return {
    errors,
    globalError,
    addError,
    removeError,
    handleApiError
  }
})

// Axios Error Interceptor
import axios from 'axios'
import { useErrorStore } from '@/stores/error'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorStore = useErrorStore()
    
    // Handle specific error types
    if (error.response?.status === 401) {
      // Authentication error - handle separately
      const authStore = useAuthStore()
      authStore.logout()
    } else if (error.response?.status >= 500) {
      // Server error - show user-friendly message
      errorStore.addError({
        message: 'Server is temporarily unavailable. Please try again later.',
        type: 'server_error',
        code: 'SERVER_ERROR'
      })
    } else {
      // Other API errors - show specific message
      errorStore.handleApiError(error)
    }
    
    return Promise.reject(error)
  }
)
```

```python
# Backend Error Handling
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import logging
import traceback
import uuid

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API Error"""
    def __init__(
        self,
        message: str,
        code: str = "API_ERROR",
        details: dict = None,
        status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(APIError):
    """Validation Error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details, 422)

class NotFoundError(APIError):
    """Not Found Error"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND", {}, 404)

class UnauthorizedError(APIError):
    """Unauthorized Error"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, "UNAUTHORIZED", {}, 401)

async def api_error_handler(request: Request, exc: APIError):
    """Custom API Error Handler"""
    error_id = str(uuid.uuid4())
    
    logger.error(
        f"API Error {error_id}: {exc.message}",
        extra={
            "error_id": error_id,
            "code": exc.code,
            "details": exc.details,
            "url": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "id": error_id,
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP Exception Handler"""
    error_id = str(uuid.uuid4())
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "id": error_id,
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation Exception Handler"""
    error_id = str(uuid.uuid4())
    
    # Format validation errors for frontend
    validation_errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        validation_errors[field] = error["msg"]
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "id": error_id,
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": {
                    "fields": validation_errors,
                    "raw_errors": exc.errors()
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """General Exception Handler"""
    error_id = str(uuid.uuid4())
    
    logger.error(
        f"Unhandled Exception {error_id}: {str(exc)}",
        extra={
            "error_id": error_id,
            "url": str(request.url),
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "id": error_id,
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

# Register error handlers
app = FastAPI()
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
```

### 4. リアルタイム通信統合パターン

#### WebSocket統合アーキテクチャ
```mermaid
graph TB
    subgraph "Frontend WebSocket"
        VueComponent[Vue Component]
        WebSocketClient[WebSocket Client]
        ConnectionManager[Connection Manager]
        EventBus[Event Bus]
        ReconnectLogic[Reconnect Logic]
    end
    
    subgraph "Backend WebSocket"
        FastAPIWebSocket[FastAPI WebSocket]
        ConnectionManager_BE[Connection Manager]
        MessageRouter[Message Router]
        Authentication[Authentication]
        BusinessLogic[Business Logic]
    end
    
    subgraph "Message Broker"
        Redis[Redis Pub/Sub]
        MessageQueue[Message Queue]
    end
    
    VueComponent --> WebSocketClient
    WebSocketClient --> ConnectionManager
    ConnectionManager --> EventBus
    EventBus --> ReconnectLogic
    
    WebSocketClient <--> FastAPIWebSocket
    FastAPIWebSocket --> ConnectionManager_BE
    ConnectionManager_BE --> MessageRouter
    MessageRouter --> Authentication
    Authentication --> BusinessLogic
    
    BusinessLogic --> Redis
    Redis --> MessageQueue
    MessageQueue --> ConnectionManager_BE
```

### 5. デプロイメント統合パターン

#### Docker統合デプロイ
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_BASE_URL=http://backend:8000
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - NODE_ENV=production
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./backend/uploads:/app/uploads
    networks:
      - app-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

#### CI/CD統合パイプライン
```yaml
# .github/workflows/deploy.yml
name: Full Stack Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
          
      - name: Install Frontend Dependencies
        run: |
          cd frontend
          npm ci
          
      - name: Run Frontend Tests
        run: |
          cd frontend
          npm run test
          
      - name: Run Frontend Linting
        run: |
          cd frontend
          npm run lint
          
      - name: Build Frontend
        run: |
          cd frontend
          npm run build

  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Backend Dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          
      - name: Run Backend Tests
        run: |
          cd backend
          pytest
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379
          
      - name: Run Backend Linting
        run: |
          cd backend
          flake8 .
          mypy .

  e2e-test:
    needs: [test-frontend, test-backend]
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Start Full Stack
        run: |
          docker-compose -f docker-compose.test.yml up -d
          
      - name: Wait for Services
        run: |
          sleep 30
          curl -f http://localhost:3000 || exit 1
          curl -f http://localhost:8000/health || exit 1
          
      - name: Run E2E Tests
        run: |
          cd frontend
          npm run test:e2e
          
      - name: Cleanup
        run: |
          docker-compose -f docker-compose.test.yml down

  deploy:
    needs: [test-frontend, test-backend, e2e-test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        run: |
          # Production deployment script
          ./deploy.sh
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

## 統合開発ワークフロー

### 1. 開発環境セットアップ
```bash
#!/bin/bash
# setup-dev-environment.sh

echo "Setting up Full Stack Development Environment..."

# Backend setup
echo "Setting up Backend (FastAPI + SQLAlchemy)..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --port 8000 &

# Frontend setup
echo "Setting up Frontend (Vue.js 3 + Axios)..."
cd ../frontend
npm install
npm run dev &

# Database setup
echo "Setting up Database..."
docker run -d \
  --name dev-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=myapp \
  -p 5432:5432 \
  postgres:15

# Redis setup
echo "Setting up Redis..."
docker run -d \
  --name dev-redis \
  -p 6379:6379 \
  redis:7-alpine

echo "Development environment is ready!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
```

### 2. 統合テスト戦略
```javascript
// tests/integration/fullstack.test.js
import { test, expect } from '@playwright/test'

test.describe('Full Stack Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Setup test data via API
    await page.request.post('/api/v1/test/setup')
  })

  test('Complete user workflow', async ({ page }) => {
    // 1. User registration
    await page.goto('/register')
    await page.fill('[data-testid="username"]', 'testuser')
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="register-button"]')
    
    // Verify backend created user
    const userResponse = await page.request.get('/api/v1/users/me')
    expect(userResponse.status()).toBe(200)
    
    // 2. User login
    await page.goto('/login')
    await page.fill('[data-testid="username"]', 'testuser')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-button"]')
    
    // Verify frontend state
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
    
    // 3. Create item
    await page.click('[data-testid="create-item"]')
    await page.fill('[data-testid="item-title"]', 'Test Item')
    await page.fill('[data-testid="item-description"]', 'Test Description')
    await page.click('[data-testid="save-item"]')
    
    // Verify item in database
    const itemsResponse = await page.request.get('/api/v1/items')
    const items = await itemsResponse.json()
    expect(items.data).toHaveLength(1)
    expect(items.data[0].title).toBe('Test Item')
    
    // 4. Real-time update test
    await page.goto('/dashboard')
    
    // Simulate WebSocket message from another client
    await page.evaluate(() => {
      window.webSocket.send(JSON.stringify({
        type: 'item_updated',
        item_id: 1,
        title: 'Updated Item'
      }))
    })
    
    // Verify UI updates in real-time
    await expect(page.locator('[data-testid="item-1"]')).toContainText('Updated Item')
  })

  test('Error handling integration', async ({ page }) => {
    // Test network error handling
    await page.route('/api/v1/**', route => route.abort())
    
    await page.goto('/dashboard')
    await page.click('[data-testid="load-data"]')
    
    // Verify error notification
    await expect(page.locator('[data-testid="error-notification"]')).toBeVisible()
    await expect(page.locator('[data-testid="error-notification"]')).toContainText('Network Error')
    
    // Test API error handling
    await page.unroute('/api/v1/**')
    await page.route('/api/v1/items', route => 
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: {
            code: 'INTERNAL_SERVER_ERROR',
            message: 'Database connection failed'
          }
        })
      })
    )
    
    await page.click('[data-testid="load-data"]')
    await expect(page.locator('[data-testid="error-notification"]')).toContainText('Server is temporarily unavailable')
  })

  test.afterEach(async ({ page }) => {
    // Cleanup test data
    await page.request.post('/api/v1/test/cleanup')
  })
})
```

このドキュメントにより、Vue3 + FastAPI フルスタック統合の完全な実装指針が提供されます。