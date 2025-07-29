# /frontend-sync - バックエンド・フロントエンド連携コマンド

## 目的
FastAPI + SQLAlchemy バックエンドから Vue3 + Axios フロントエンドへの API仕様自動連携・同期を実現し、フルスタック開発における一貫性と効率性を確保します。

## 対象システム
- **バックエンド**: FastAPI + SQLAlchemy + SQL Server + OpenAPI 3.0
- **フロントエンド**: Vue.js 3 + Composition API + Axios + Pinia
- **連携プロトコル**: OpenAPI 3.0 → TypeScript + JavaScript 自動生成

## 入力パラメータ
- **必須**: `$SYNC_TYPE` - 同期タイプ（api_to_frontend, full_stack_sync, contract_first, validation_sync）
- **任意**: `$TARGET_MODULE` - 対象モジュール（auth, products, production, inventory, quality, all）
- **任意**: `$OUTPUT_FORMAT` - 出力形式（typescript, javascript, vue_components）
- **任意**: `$SYNC_DEPTH` - 同期深度（shallow, deep, comprehensive）

## 出力ファイル
- **OpenAPI仕様書**: `.tmp/frontend_sync/openapi_spec_[timestamp].json`
- **TypeScript型定義**: `.tmp/frontend_sync/types/api.d.ts`
- **Axiosクライアント**: `.tmp/frontend_sync/services/apiClient.js`
- **Piniaストア**: `.tmp/frontend_sync/stores/*.js`
- **Vue3コンポーネント**: `.tmp/frontend_sync/components/*.vue`
- **フロントエンド実装ガイド**: `.tmp/frontend_sync/implementation_guide.md`

## ワークフロー

### Phase 1: FastAPI仕様解析・OpenAPI生成

#### 1. SQLAlchemyモデル解析
```python
# SQLAlchemyモデル自動解析
class ModelAnalyzer:
    """SQLAlchemyモデル解析クラス"""
    
    def analyze_models(self, models: List[type]) -> Dict[str, Any]:
        """モデル構造を解析してOpenAPI Schema生成"""
        schemas = {}
        
        for model in models:
            schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for column in model.__table__.columns:
                prop_schema = self._column_to_schema(column)
                schema["properties"][column.name] = prop_schema
                
                if not column.nullable and not column.default:
                    schema["required"].append(column.name)
            
            schemas[model.__name__] = schema
        
        return schemas
    
    def _column_to_schema(self, column) -> Dict[str, Any]:
        """SQLAlchemyカラムをOpenAPIスキーマに変換"""
        type_mapping = {
            Integer: {"type": "integer"},
            String: {"type": "string"},
            Text: {"type": "string"},
            Boolean: {"type": "boolean"},
            DateTime: {"type": "string", "format": "date-time"},
            Date: {"type": "string", "format": "date"},
            Numeric: {"type": "number", "format": "decimal"},
            Float: {"type": "number", "format": "float"}
        }
        
        base_schema = type_mapping.get(type(column.type), {"type": "string"})
        
        # 文字列長制約
        if hasattr(column.type, 'length') and column.type.length:
            base_schema["maxLength"] = column.type.length
        
        # Enum処理
        if hasattr(column.type, 'enums'):
            base_schema["enum"] = list(column.type.enums)
        
        # デフォルト値
        if column.default:
            base_schema["default"] = column.default.arg
        
        return base_schema

# 使用例：製造業モデルの解析
manufacturing_models = [
    User, Product, ProductionResult, ShipmentChecksheet, 
    InventoryItem, QualityInspection, DefectRecord
]

analyzer = ModelAnalyzer()
schemas = analyzer.analyze_models(manufacturing_models)
```

#### 2. FastAPIエンドポイント解析
```python
# FastAPIルーター自動解析
class EndpointAnalyzer:
    """FastAPIエンドポイント解析クラス"""
    
    def analyze_routes(self, app: FastAPI) -> Dict[str, Any]:
        """FastAPIルートを解析してOpenAPI paths生成"""
        paths = {}
        
        for route in app.routes:
            if hasattr(route, 'methods'):
                for method in route.methods:
                    if method != 'HEAD':  # HEADメソッドは除外
                        path_item = self._analyze_route(route, method)
                        
                        if route.path not in paths:
                            paths[route.path] = {}
                        
                        paths[route.path][method.lower()] = path_item
        
        return paths
    
    def _analyze_route(self, route, method: str) -> Dict[str, Any]:
        """個別ルートの解析"""
        endpoint_func = route.endpoint
        
        # 関数シグネチャ解析
        signature = inspect.signature(endpoint_func)
        parameters = []
        request_body = None
        
        for param_name, param in signature.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                param_schema = self._type_to_schema(param.annotation)
                
                # パスパラメータ
                if param_name in route.path_regex.pattern:
                    parameters.append({
                        "name": param_name,
                        "in": "path",
                        "required": True,
                        "schema": param_schema
                    })
                # クエリパラメータ
                elif param.default == inspect.Parameter.empty:
                    parameters.append({
                        "name": param_name,
                        "in": "query", 
                        "required": True,
                        "schema": param_schema
                    })
                # リクエストボディ（Pydanticモデル）
                elif hasattr(param.annotation, '__fields__'):
                    request_body = {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{param.annotation.__name__}"}
                            }
                        }
                    }
        
        # レスポンススキーマ（戻り値の型ヒントから推測）
        return_annotation = signature.return_annotation
        response_schema = self._type_to_schema(return_annotation)
        
        operation = {
            "summary": endpoint_func.__doc__ or f"{method.upper()} {route.path}",
            "parameters": parameters,
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": response_schema
                        }
                    }
                }
            }
        }
        
        if request_body:
            operation["requestBody"] = request_body
        
        return operation

# 製造業API解析例
manufacturing_app = FastAPI()
# ... ルーター登録 ...

analyzer = EndpointAnalyzer()
paths = analyzer.analyze_routes(manufacturing_app)
```

#### 3. 完全OpenAPI仕様生成
```python
# 完全なOpenAPI仕様書生成
class OpenAPIGenerator:
    """OpenAPI 3.0仕様書生成クラス"""
    
    def generate_full_spec(
        self, 
        app: FastAPI,
        models: List[type],
        title: str = "製造業品質管理システムAPI",
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """完全なOpenAPI仕様書を生成"""
        
        model_analyzer = ModelAnalyzer()
        endpoint_analyzer = EndpointAnalyzer()
        
        # スキーマ生成
        schemas = model_analyzer.analyze_models(models)
        
        # パス生成
        paths = endpoint_analyzer.analyze_routes(app)
        
        # セキュリティスキーム
        security_schemes = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT認証トークン"
            }
        }
        
        # 完全仕様
        openapi_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": title,
                "version": version,
                "description": "FastAPI + SQLAlchemy による製造業向け統合品質管理システム",
                "contact": {
                    "name": "情報システム係",
                    "email": "support@company.com"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:9995",
                    "description": "開発環境"
                },
                {
                    "url": "https://api.production.com",
                    "description": "本番環境"
                }
            ],
            "paths": paths,
            "components": {
                "schemas": schemas,
                "securitySchemes": security_schemes
            },
            "security": [
                {"BearerAuth": []}
            ],
            "tags": [
                {"name": "authentication", "description": "認証・認可"},
                {"name": "production", "description": "生産管理"},
                {"name": "quality", "description": "品質管理"},
                {"name": "inventory", "description": "在庫管理"},
                {"name": "shipment", "description": "出荷管理"}
            ]
        }
        
        return openapi_spec

# 製造業システム用OpenAPI生成
generator = OpenAPIGenerator()
openapi_spec = generator.generate_full_spec(
    app=manufacturing_app,
    models=manufacturing_models,
    title="製造業品質管理システムAPI",
    version="1.0.0"
)

# JSON出力
with open('.tmp/frontend_sync/openapi_spec.json', 'w', encoding='utf-8') as f:
    json.dump(openapi_spec, f, ensure_ascii=False, indent=2)
```

### Phase 2: TypeScript型定義・Axiosクライアント自動生成

#### 1. TypeScript型定義生成
```python
# TypeScript型定義自動生成
class TypeScriptGenerator:
    """TypeScript型定義生成クラス"""
    
    def generate_types(self, openapi_spec: Dict[str, Any]) -> str:
        """OpenAPI仕様からTypeScript型定義を生成"""
        
        types = []
        
        # 基本型マッピング
        type_mapping = {
            "integer": "number",
            "number": "number", 
            "string": "string",
            "boolean": "boolean",
            "array": "Array",
            "object": "Record<string, any>"
        }
        
        # スキーマから型定義生成
        for schema_name, schema in openapi_spec.get("components", {}).get("schemas", {}).items():
            ts_interface = self._generate_interface(schema_name, schema, type_mapping)
            types.append(ts_interface)
        
        # API関数の型定義
        api_types = self._generate_api_types(openapi_spec, type_mapping)
        types.extend(api_types)
        
        return "\n\n".join(types)
    
    def _generate_interface(self, name: str, schema: Dict, type_mapping: Dict) -> str:
        """インターフェース定義生成"""
        
        interface_lines = [f"export interface {name} {{"]
        
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        for prop_name, prop_schema in properties.items():
            optional = "?" if prop_name not in required else ""
            ts_type = self._schema_to_ts_type(prop_schema, type_mapping)
            
            # JSDocコメント生成
            if "description" in prop_schema:
                interface_lines.append(f"  /** {prop_schema['description']} */")
            
            interface_lines.append(f"  {prop_name}{optional}: {ts_type};")
        
        interface_lines.append("}")
        
        return "\n".join(interface_lines)
    
    def _generate_api_types(self, openapi_spec: Dict, type_mapping: Dict) -> List[str]:
        """API関数の型定義生成"""
        
        api_types = []
        
        # 共通レスポンス型
        common_types = [
            """
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages?: number;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  timestamp: string;
}
            """.strip()
        ]
        
        api_types.extend(common_types)
        
        # パス別のリクエスト・レスポンス型
        for path, methods in openapi_spec.get("paths", {}).items():
            for method, operation in methods.items():
                func_name = self._path_to_function_name(path, method)
                
                # リクエスト型
                if "requestBody" in operation:
                    request_schema = operation["requestBody"]["content"]["application/json"]["schema"]
                    if "$ref" in request_schema:
                        ref_name = request_schema["$ref"].split("/")[-1]
                        api_types.append(f"export type {func_name}Request = {ref_name};")
                
                # レスポンス型
                response_schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
                if "$ref" in response_schema:
                    ref_name = response_schema["$ref"].split("/")[-1]
                    api_types.append(f"export type {func_name}Response = {ref_name};")
        
        return api_types

# TypeScript型定義生成実行
ts_generator = TypeScriptGenerator()
typescript_definitions = ts_generator.generate_types(openapi_spec)

# TypeScriptファイル出力
with open('.tmp/frontend_sync/types/api.d.ts', 'w', encoding='utf-8') as f:
    f.write(typescript_definitions)
```

#### 2. Axiosクライアント生成
```python
# Axiosクライアント自動生成
class AxiosClientGenerator:
    """Axiosクライアント自動生成クラス"""
    
    def generate_client(self, openapi_spec: Dict[str, Any]) -> str:
        """OpenAPI仕様からAxiosクライアントを生成"""
        
        client_parts = []
        
        # ベースクライアント設定
        base_client = """
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type * as API from '../types/api';

// 基本設定
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:9995';

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // リクエストインターセプター
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // レスポンスインターセプター  
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          this.token = null;
          localStorage.removeItem('auth_token');
          // ログイン画面にリダイレクト
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }
        """.strip()
        
        client_parts.append(base_client)
        
        # API関数群生成
        api_groups = self._group_endpoints_by_tag(openapi_spec)
        
        for tag, endpoints in api_groups.items():
            group_methods = []
            
            for endpoint in endpoints:
                method_code = self._generate_api_method(endpoint)
                group_methods.append(method_code)
            
            # APIグループクラス
            group_class = f"""
  // {tag.upper()} API
  {tag} = {{
{chr(10).join(group_methods)}
  }};
            """.strip()
            
            client_parts.append(group_class)
        
        # クラス終了とエクスポート
        client_parts.append("""
}

export const apiClient = new APIClient();
export default apiClient;
        """.strip())
        
        return "\n\n".join(client_parts)
    
    def _generate_api_method(self, endpoint: Dict) -> str:
        """個別APIメソッド生成"""
        
        method = endpoint["method"].upper()
        path = endpoint["path"]
        operation = endpoint["operation"]
        
        func_name = self._path_to_function_name(path, endpoint["method"])
        
        # パラメータ処理
        params = []
        path_params = []
        
        for param in operation.get("parameters", []):
            if param["in"] == "path":
                path_params.append(param["name"])
                params.append(f"{param['name']}: {self._schema_to_ts_type(param['schema'])}")
            elif param["in"] == "query":
                optional = "?" if not param.get("required", False) else ""
                params.append(f"{param['name']}{optional}: {self._schema_to_ts_type(param['schema'])}")
        
        # リクエストボディ
        if "requestBody" in operation:
            params.append("data: any")
        
        param_str = ", ".join(params)
        
        # URL構築
        url_template = path
        for path_param in path_params:
            url_template = url_template.replace(f"{{{path_param}}}", f"${{{path_param}}}")
        
        # メソッド実装
        if method == "GET":
            return f"""
    async {func_name}({param_str}) {{
      const response = await this.client.get(`{url_template}`);
      return response.data;
    }},"""
        elif method == "POST":
            return f"""
    async {func_name}({param_str}) {{
      const response = await this.client.post(`{url_template}`, data);
      return response.data;
    }},"""
        elif method == "PUT":
            return f"""
    async {func_name}({param_str}) {{
      const response = await this.client.put(`{url_template}`, data);
      return response.data;
    }},"""
        elif method == "DELETE":
            return f"""
    async {func_name}({param_str}) {{
      const response = await this.client.delete(`{url_template}`);
      return response.data;
    }},"""

# Axiosクライアント生成実行
axios_generator = AxiosClientGenerator()
axios_client_code = axios_generator.generate_client(openapi_spec)

# JavaScriptファイル出力
with open('.tmp/frontend_sync/services/apiClient.js', 'w', encoding='utf-8') as f:
    f.write(axios_client_code)
```

#### 3. Piniaストア生成
```python
# Piniaストア自動生成
class PiniaStoreGenerator:
    """Piniaストア自動生成クラス"""
    
    def generate_stores(self, openapi_spec: Dict[str, Any]) -> Dict[str, str]:
        """OpenAPI仕様からPiniaストアを生成"""
        
        stores = {}
        
        # タグごとにストア生成
        api_groups = self._group_endpoints_by_tag(openapi_spec)
        
        for tag, endpoints in api_groups.items():
            store_code = self._generate_store_for_tag(tag, endpoints, openapi_spec)
            stores[f"{tag}Store.js"] = store_code
        
        return stores
    
    def _generate_store_for_tag(self, tag: str, endpoints: List, openapi_spec: Dict) -> str:
        """タグ別ストア生成"""
        
        # 主要エンティティ特定
        main_entity = self._identify_main_entity(tag, endpoints, openapi_spec)
        
        store_template = f"""
import {{ defineStore }} from 'pinia';
import {{ ref, computed }} from 'vue';
import {{ apiClient }} from '@/services/apiClient';
import type * as API from '@/types/api';

export const use{tag.capitalize()}Store = defineStore('{tag}', () => {{
  // State
  const items = ref<API.{main_entity}[]>([]);
  const currentItem = ref<API.{main_entity} | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref({{
    total: 0,
    page: 1,
    limit: 20
  }});

  // Getters
  const totalPages = computed(() => 
    Math.ceil(pagination.value.total / pagination.value.limit)
  );

  const hasItems = computed(() => items.value.length > 0);

  // Actions
  const fetchItems = async (params: any = {{}}) => {{
    try {{
      isLoading.value = true;
      error.value = null;
      
      const response = await apiClient.{tag}.getList({{
        page: pagination.value.page,
        limit: pagination.value.limit,
        ...params
      }});
      
      items.value = response.items;
      pagination.value = {{
        total: response.total,
        page: response.page,
        limit: response.limit
      }};
      
      return response;
    }} catch (err: any) {{
      error.value = err.response?.data?.error?.message || '{main_entity}取得に失敗しました';
      throw err;
    }} finally {{
      isLoading.value = false;
    }}
  }};

  const fetchItem = async (id: number) => {{
    try {{
      isLoading.value = true;
      error.value = null;
      
      const item = await apiClient.{tag}.getById(id);
      currentItem.value = item;
      
      return item;
    }} catch (err: any) {{
      error.value = err.response?.data?.error?.message || '{main_entity}詳細取得に失敗しました';
      throw err;
    }} finally {{
      isLoading.value = false;
    }}
  }};

  const createItem = async (data: API.{main_entity}CreateRequest) => {{
    try {{
      isLoading.value = true;
      error.value = null;
      
      const newItem = await apiClient.{tag}.create(data);
      items.value.unshift(newItem);
      
      return newItem;
    }} catch (err: any) {{
      error.value = err.response?.data?.error?.message || '{main_entity}作成に失敗しました';
      throw err;
    }} finally {{
      isLoading.value = false;
    }}
  }};

  const updateItem = async (id: number, data: API.{main_entity}UpdateRequest) => {{
    try {{
      isLoading.value = true;
      error.value = null;
      
      const updatedItem = await apiClient.{tag}.update(id, data);
      
      const index = items.value.findIndex(item => item.id === id);
      if (index !== -1) {{
        items.value[index] = updatedItem;
      }}
      
      if (currentItem.value?.id === id) {{
        currentItem.value = updatedItem;
      }}
      
      return updatedItem;
    }} catch (err: any) {{
      error.value = err.response?.data?.error?.message || '{main_entity}更新に失敗しました';
      throw err;
    }} finally {{
      isLoading.value = false;
    }}
  }};

  const deleteItem = async (id: number) => {{
    try {{
      isLoading.value = true;
      error.value = null;
      
      await apiClient.{tag}.delete(id);
      
      items.value = items.value.filter(item => item.id !== id);
      
      if (currentItem.value?.id === id) {{
        currentItem.value = null;
      }}
    }} catch (err: any) {{
      error.value = err.response?.data?.error?.message || '{main_entity}削除に失敗しました';
      throw err;
    }} finally {{
      isLoading.value = false;
    }}
  }};

  const setPage = (page: number) => {{
    pagination.value.page = page;
  }};

  const setLimit = (limit: number) => {{
    pagination.value.limit = limit;
  }};

  const clearError = () => {{
    error.value = null;
  }};

  const reset = () => {{
    items.value = [];
    currentItem.value = null;
    error.value = null;
    pagination.value = {{ total: 0, page: 1, limit: 20 }};
  }};

  return {{
    // State
    items,
    currentItem,
    isLoading,
    error,
    pagination,
    
    // Getters
    totalPages,
    hasItems,
    
    // Actions
    fetchItems,
    fetchItem,
    createItem,
    updateItem,
    deleteItem,
    setPage,
    setLimit,
    clearError,
    reset
  }};
}});
        """.strip()
        
        return store_template

# Piniaストア生成実行
pinia_generator = PiniaStoreGenerator()
pinia_stores = pinia_generator.generate_stores(openapi_spec)

# ストアファイル出力
for store_name, store_code in pinia_stores.items():
    with open(f'.tmp/frontend_sync/stores/{store_name}', 'w', encoding='utf-8') as f:
        f.write(store_code)
```

### Phase 3: Vue3コンポーネント・統合ガイド生成

#### 1. Vue3コンポーネントテンプレート生成
```python
# Vue3コンポーネント自動生成
class VueComponentGenerator:
    """Vue3コンポーネント自動生成クラス"""
    
    def generate_crud_components(self, entity: str, schema: Dict) -> Dict[str, str]:
        """CRUD操作用Vue3コンポーネント生成"""
        
        components = {}
        
        # 一覧コンポーネント
        list_component = self._generate_list_component(entity, schema)
        components[f"{entity}List.vue"] = list_component
        
        # 詳細コンポーネント
        detail_component = self._generate_detail_component(entity, schema)
        components[f"{entity}Detail.vue"] = detail_component
        
        # 作成・編集フォームコンポーネント
        form_component = self._generate_form_component(entity, schema)
        components[f"{entity}Form.vue"] = form_component
        
        return components
    
    def _generate_list_component(self, entity: str, schema: Dict) -> str:
        """一覧コンポーネント生成"""
        
        entity_lower = entity.lower()
        entity_pascal = entity.capitalize()
        
        return f"""
<template>
  <div class="{entity_lower}-list">
    <!-- ヘッダー -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">{entity_pascal}一覧</h1>
      <button 
        @click="showCreateForm = true"
        class="btn btn-primary"
        :disabled="!authStore.canCreate"
      >
        <PlusIcon class="w-5 h-5 mr-2" />
        新規作成
      </button>
    </div>

    <!-- 検索・フィルター -->
    <div class="card bg-base-100 shadow-sm mb-4">
      <div class="card-body">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="検索..."
            class="input input-bordered"
            @input="debouncedSearch"
          />
          <select v-model="filterStatus" class="select select-bordered">
            <option value="">全て</option>
            <option value="active">有効</option>
            <option value="inactive">無効</option>
          </select>
          <button @click="resetFilters" class="btn btn-outline">
            リセット
          </button>
        </div>
      </div>
    </div>

    <!-- テーブル -->
    <div class="card bg-base-100 shadow-sm">
      <div class="card-body">
        <div class="overflow-x-auto">
          <table class="table table-zebra w-full">
            <thead>
              <tr>
                {"".join([f"<th>{field}</th>" for field in schema.get("properties", {}).keys()])}
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in {entity_lower}Store.items" :key="item.id">
                {"".join([f"<td>{{{{ item.{field} }}}}</td>" for field in schema.get("properties", {}).keys()])}
                <td>
                  <div class="flex gap-2">
                    <button 
                      @click="viewDetail(item.id)"
                      class="btn btn-sm btn-outline"
                    >
                      詳細
                    </button>
                    <button 
                      @click="editItem(item)"
                      class="btn btn-sm btn-primary"
                      :disabled="!authStore.canEdit"
                    >
                      編集
                    </button>
                    <button 
                      @click="deleteItem(item.id)"
                      class="btn btn-sm btn-error"
                      :disabled="!authStore.canDelete"
                    >
                      削除
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ページネーション -->
        <div class="flex justify-between items-center mt-4">
          <span class="text-sm text-gray-600">
            {{{{ {entity_lower}Store.pagination.total }}}} 件中 
            {{{{ ({entity_lower}Store.pagination.page - 1) * {entity_lower}Store.pagination.limit + 1 }}}} - 
            {{{{ Math.min({entity_lower}Store.pagination.page * {entity_lower}Store.pagination.limit, {entity_lower}Store.pagination.total) }}}} 件
          </span>
          
          <div class="btn-group">
            <button 
              @click="previousPage"
              class="btn btn-sm"
              :disabled="{entity_lower}Store.pagination.page <= 1"
            >
              前へ
            </button>
            <span class="btn btn-sm btn-disabled">
              {{{{ {entity_lower}Store.pagination.page }}}} / {{{{ {entity_lower}Store.totalPages }}}}
            </span>
            <button 
              @click="nextPage"
              class="btn btn-sm"
              :disabled="{entity_lower}Store.pagination.page >= {entity_lower}Store.totalPages"
            >
              次へ
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 作成・編集モーダル -->
    <{entity_pascal}Form
      v-if="showCreateForm || editingItem"
      :item="editingItem"
      @close="closeForm"
      @saved="onItemSaved"
    />
  </div>
</template>

<script setup>
import {{ ref, onMounted, computed }} from 'vue';
import {{ use{entity_pascal}Store }} from '@/stores/{entity_lower}Store';
import {{ useAuthStore }} from '@/stores/authStore';
import {{ debounce }} from 'lodash';
import {entity_pascal}Form from './{entity_pascal}Form.vue';
import {{ PlusIcon }} from '@heroicons/vue/24/outline';

// Stores
const {entity_lower}Store = use{entity_pascal}Store();
const authStore = useAuthStore();

// State
const searchQuery = ref('');
const filterStatus = ref('');
const showCreateForm = ref(false);
const editingItem = ref(null);

// Methods
const debouncedSearch = debounce(() => {{
  fetchItems();
}}, 300);

const fetchItems = async () => {{
  await {entity_lower}Store.fetchItems({{
    search: searchQuery.value,
    status: filterStatus.value
  }});
}};

const viewDetail = (id) => {{
  // ルーターで詳細ページに遷移
  $router.push(`/{entity_lower}/{{id}}`);
}};

const editItem = (item) => {{
  editingItem.value = item;
}};

const deleteItem = async (id) => {{
  if (confirm('削除しますか？')) {{
    await {entity_lower}Store.deleteItem(id);
  }}
}};

const closeForm = () => {{
  showCreateForm.value = false;
  editingItem.value = null;
}};

const onItemSaved = () => {{
  closeForm();
  fetchItems();
}};

const resetFilters = () => {{
  searchQuery.value = '';
  filterStatus.value = '';
  fetchItems();
}};

const previousPage = () => {{
  if ({entity_lower}Store.pagination.page > 1) {{
    {entity_lower}Store.setPage({entity_lower}Store.pagination.page - 1);
    fetchItems();
  }}
}};

const nextPage = () => {{
  if ({entity_lower}Store.pagination.page < {entity_lower}Store.totalPages) {{
    {entity_lower}Store.setPage({entity_lower}Store.pagination.page + 1);
    fetchItems();
  }}
}};

// Lifecycle
onMounted(() => {{
  fetchItems();
}});
</script>
        """.strip()

# Vue3コンポーネント生成実行
vue_generator = VueComponentGenerator()

# 主要エンティティのコンポーネント生成
main_entities = ["Product", "ProductionResult", "InventoryItem", "QualityInspection"]

for entity in main_entities:
    schema = openapi_spec["components"]["schemas"].get(entity, {})
    components = vue_generator.generate_crud_components(entity, schema)
    
    for component_name, component_code in components.items():
        component_dir = f'.tmp/frontend_sync/components/{entity.lower()}'
        os.makedirs(component_dir, exist_ok=True)
        
        with open(f'{component_dir}/{component_name}', 'w', encoding='utf-8') as f:
            f.write(component_code)
```

## 同期タイプ別仕様

### 1. API→フロントエンド（api_to_frontend）
```yaml
目的: 既存FastAPI仕様からフロントエンドクライアント自動生成
フロー:
  1. FastAPIアプリケーション解析
  2. OpenAPI 3.0仕様書生成
  3. TypeScript型定義生成
  4. Axiosクライアント生成
  5. Piniaストア生成
  6. Vue3コンポーネントテンプレート生成
期待効果:
  - 型安全なAPI統合
  - 開発時間の大幅短縮
  - 人的エラーの削減
```

### 2. フルスタック同期（full_stack_sync）
```yaml
目的: バックエンド・フロントエンド完全一貫性保証
フロー:
  1. バックエンドAPI完全解析
  2. フロントエンド要件との整合性確認
  3. 差分検出・調整提案
  4. 双方向同期実行
  5. E2Eテストケース生成
期待効果:
  - 完全な一貫性保証
  - 継続的同期による品質維持
  - 自動テストによる回帰防止
```

### 3. 契約ファースト（contract_first）
```yaml
目的: OpenAPI仕様を契約とした開発サポート
フロー:
  1. OpenAPI仕様書設計
  2. バックエンド実装ガイド生成
  3. フロントエンドクライアント生成
  4. モックサーバー生成
  5. 契約テスト生成
期待効果:
  - 明確な契約による開発
  - 並行開発の効率化
  - 仕様変更の影響分析
```

### 4. バリデーション同期（validation_sync）
```yaml
目的: バックエンド・フロントエンド間バリデーション統一
フロー:
  1. Pydanticスキーマ解析
  2. フロントエンドバリデーションルール生成
  3. エラーメッセージ統一
  4. フォームバリデーション適用
  5. バリデーションテスト生成
期待効果:
  - 統一されたUX
  - バリデーションエラーの削減
  - 保守性の向上
```

## フロントエンド実装ガイド

### セットアップ手順
```bash
# 生成されたファイルのコピー
cp .tmp/frontend_sync/types/api.d.ts src/types/
cp .tmp/frontend_sync/services/apiClient.js src/services/
cp -r .tmp/frontend_sync/stores/* src/stores/
cp -r .tmp/frontend_sync/components/* src/components/

# 必要な依存関係インストール
npm install axios @heroicons/vue lodash
npm install -D @types/lodash

# 環境変数設定
echo "VUE_APP_API_BASE_URL=http://localhost:9995" >> .env.local
```

### ルーター設定
```javascript
// router/index.js に追加
import ProductList from '@/components/product/ProductList.vue'
import ProductDetail from '@/components/product/ProductDetail.vue'

const routes = [
  // ... 既存ルート
  {
    path: '/products',
    name: 'ProductList',
    component: ProductList,
    meta: { requiresAuth: true }
  },
  {
    path: '/products/:id',
    name: 'ProductDetail', 
    component: ProductDetail,
    meta: { requiresAuth: true }
  }
]
```

### メイン.jsでの初期化
```javascript
// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { apiClient } from './services/apiClient'
import { useAuthStore } from './stores/authStore'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 認証状態の初期化
const authStore = useAuthStore()
const token = localStorage.getItem('auth_token')
if (token) {
  apiClient.setToken(token)
  authStore.initialize()
}

app.mount('#app')
```

## 成功指標・KPI

### 技術指標
- **型安全性**: TypeScriptエラー削減率 95%
- **API整合性**: バックエンド・フロントエンド仕様一致率 100%
- **自動化率**: 手動クライアント実装作業削減 90%
- **コード品質**: ESLint警告削減率 80%

### 開発効率指標
- **開発時間**: フロントエンド開発時間 60% 短縮
- **バグ修正**: API統合バグ修正時間 70% 短縮
- **メンテナンス**: 仕様変更時の同期時間 85% 短縮

### 品質指標
- **ユーザビリティ**: 一貫したバリデーション体験
- **パフォーマンス**: API呼び出し最適化
- **保守性**: 自動生成コードの保守容易性

## 使用例

### 既存APIからフロントエンド生成
```bash
# FastAPI仕様からVue3クライアント完全生成
/frontend-sync api_to_frontend --target_module="all" --output_format="typescript"
```

### 特定モジュールの同期
```bash
# 製品管理モジュールのみ同期
/frontend-sync full_stack_sync --target_module="products" --sync_depth="deep"
```

### バリデーション統一
```bash
# バックエンド・フロントエンドバリデーション同期
/frontend-sync validation_sync --target_module="all" --validation_level="strict"
```

## 注意事項・制約

### 技術制約
- FastAPI + SQLAlchemy構成が前提
- OpenAPI 3.0仕様への準拠が必要
- Vue3 Composition API + Pinia構成前提

### 生成コード制約
- 複雑なビジネスロジックは手動実装が必要
- カスタムバリデーションは個別対応
- 高度なUI/UXは手動調整が必要

### 保守制約
- 自動生成コードの直接編集は避ける
- カスタマイズは継承・拡張で対応
- 定期的な再生成による同期が必要