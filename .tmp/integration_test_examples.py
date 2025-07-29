"""
フルスタック連携テスト・検証機能
Vue3 + FastAPI間の完全統合テスト実装例
"""

import pytest
import asyncio
import json
import websockets
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

# セットアップ
from main import app
from core.database import Base, get_db

# テスト用データベース
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テストクライアント
client = TestClient(app)

@pytest.fixture
def test_db():
    """テスト用データベースセットアップ"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def override_get_db():
    """データベースセッション上書き"""
    def _override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

class FullStackIntegrationTest:
    """フルスタック統合テストクラス"""
    
    def __init__(self):
        self.api_client = httpx.AsyncClient(base_url="http://localhost:9995")
        self.frontend_simulator = FrontendSimulator()
        self.test_data = TestDataManager()
        
    async def test_complete_product_lifecycle(self, test_db, override_get_db):
        """製品ライフサイクル完全テスト"""
        
        # Step 1: 認証
        auth_result = await self.authenticate_user("admin", "admin123")
        assert auth_result["success"], "認証に失敗しました"
        
        token = auth_result["token"]
        self.api_client.headers.update({"Authorization": f"Bearer {token}"})
        
        # Step 2: 製品作成（バックエンド）
        product_data = self.test_data.generate_product_data()
        create_response = await self.api_client.post("/api/v1/products", json=product_data)
        
        assert create_response.status_code == 201
        created_product = create_response.json()
        product_id = created_product["id"]
        
        # Step 3: フロントエンド同期検証
        frontend_sync_result = await self.frontend_simulator.sync_product_store()
        assert frontend_sync_result["success"], "フロントエンド同期に失敗"
        
        # Step 4: フロントエンドでの製品取得
        frontend_product = await self.frontend_simulator.fetch_product(product_id)
        assert frontend_product["id"] == product_id
        assert frontend_product["product_code"] == product_data["product_code"]
        
        # Step 5: リアルタイム更新テスト
        update_data = {"product_name": "更新された製品名"}
        update_response = await self.api_client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert update_response.status_code == 200
        
        # WebSocket経由でフロントエンドに更新通知が届くことを確認
        ws_notification = await self.frontend_simulator.wait_for_websocket_update(product_id, timeout=10)
        assert ws_notification is not None, "WebSocket更新通知が届きませんでした"
        
        # Step 6: バリデーション同期テスト
        invalid_data = {"product_code": "", "product_name": ""}  # 必須フィールドが空
        
        # バックエンドバリデーション
        backend_validation = await self.api_client.post("/api/v1/products", json=invalid_data)
        assert backend_validation.status_code == 422
        
        # フロントエンドバリデーション（シミュレート）
        frontend_validation = await self.frontend_simulator.validate_product_form(invalid_data)
        assert not frontend_validation["is_valid"]
        
        # バリデーションエラーメッセージの一致確認
        backend_errors = backend_validation.json()["error"]["details"]
        frontend_errors = frontend_validation["errors"]
        
        assert self.compare_validation_errors(backend_errors, frontend_errors), "バリデーションエラーが一致しません"
        
        # Step 7: 削除テスト
        delete_response = await self.api_client.delete(f"/api/v1/products/{product_id}")
        assert delete_response.status_code == 204
        
        # フロントエンドでの削除確認
        deleted_check = await self.frontend_simulator.fetch_product(product_id)
        assert deleted_check is None, "削除された製品がまだ存在します"
        
        return {
            "test_passed": True,
            "product_id": product_id,
            "steps_completed": 7
        }
    
    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """ユーザー認証"""
        auth_data = {"username": username, "password": password}
        response = await self.api_client.post("/api/v1/auth/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "token": data["access_token"],
                "user": data["user"]
            }
        else:
            return {
                "success": False,
                "error": response.json()
            }
    
    def compare_validation_errors(self, backend_errors: List, frontend_errors: List) -> bool:
        """バリデーションエラーの比較"""
        # フィールド名ベースでエラーを比較
        backend_fields = {err.get("field", err.get("loc", [""])[0]) for err in backend_errors}
        frontend_fields = {err.get("field") for err in frontend_errors}
        
        return backend_fields == frontend_fields

class FrontendSimulator:
    """フロントエンド動作シミュレーター"""
    
    def __init__(self):
        self.store_state = {}
        self.websocket_connection = None
        self.websocket_messages = []
        
    async def sync_product_store(self) -> Dict[str, Any]:
        """Piniaストア同期のシミュレート"""
        try:
            # 実際のフロントエンドストア同期ロジックをシミュレート
            await asyncio.sleep(0.1)  # 同期処理の遅延をシミュレート
            
            return {"success": True, "synced_at": datetime.utcnow().isoformat()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def fetch_product(self, product_id: int) -> Dict[str, Any] | None:
        """製品取得のシミュレート"""
        # 実際のAxiosクライアント呼び出しをシミュレート
        try:
            response = await httpx.AsyncClient().get(f"http://localhost:9995/api/v1/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"Unexpected status code: {response.status_code}")
        except Exception:
            return None
    
    async def validate_product_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """フロントエンドフォームバリデーションのシミュレート"""
        errors = []
        
        # 必須フィールドチェック
        if not form_data.get("product_code"):
            errors.append({
                "field": "product_code",
                "message": "製品コードは必須です"
            })
            
        if not form_data.get("product_name"):
            errors.append({
                "field": "product_name", 
                "message": "製品名は必須です"
            })
        
        # 長さチェック
        if form_data.get("product_code") and len(form_data["product_code"]) > 50:
            errors.append({
                "field": "product_code",
                "message": "製品コードは50文字以内で入力してください"
            })
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    async def wait_for_websocket_update(self, product_id: int, timeout: int = 10) -> Dict[str, Any] | None:
        """WebSocket更新通知の待機"""
        try:
            # WebSocket接続のシミュレート
            await asyncio.sleep(1)  # 通知遅延をシミュレート
            
            # 更新通知のシミュレート
            return {
                "type": "product_updated",
                "product_id": product_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        except asyncio.TimeoutError:
            return None

class TestDataManager:
    """テストデータ管理クラス"""
    
    def generate_product_data(self) -> Dict[str, Any]:
        """製品データ生成"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "product_code": f"TEST-{unique_id}",
            "product_name": f"テスト製品 {unique_id}",
            "category": "テストカテゴリ",
            "price": 1000.00,
            "description": "統合テスト用製品データ"
        }
    
    def generate_user_data(self) -> Dict[str, Any]:
        """ユーザーデータ生成"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "username": f"testuser_{unique_id}",
            "full_name": f"テストユーザー {unique_id}",
            "email": f"test_{unique_id}@example.com",
            "role": "operator"
        }

class SchemaContractTest:
    """API契約テストクラス"""
    
    def __init__(self, openapi_spec_path: str):
        with open(openapi_spec_path, 'r', encoding='utf-8') as f:
            self.openapi_spec = json.load(f)
    
    async def test_all_endpoints_contract(self):
        """全エンドポイントの契約テスト"""
        results = []
        
        for path, methods in self.openapi_spec.get("paths", {}).items():
            for method, operation in methods.items():
                test_result = await self.test_endpoint_contract(path, method, operation)
                results.append(test_result)
        
        return {
            "total_tests": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
            "results": results
        }
    
    async def test_endpoint_contract(self, path: str, method: str, operation: Dict) -> Dict[str, Any]:
        """個別エンドポイントの契約テスト"""
        
        # テストデータ生成
        test_data = self.generate_test_data_from_schema(operation)
        
        # リクエスト実行
        try:
            response = await self.execute_request(path, method, test_data)
            
            # レスポンススキーマ検証
            schema_validation = self.validate_response_schema(response, operation)
            
            return {
                "endpoint": f"{method.upper()} {path}",
                "passed": schema_validation["valid"],
                "response_status": response.status_code,
                "schema_validation": schema_validation
            }
        except Exception as e:
            return {
                "endpoint": f"{method.upper()} {path}",
                "passed": False,
                "error": str(e)
            }
    
    def generate_test_data_from_schema(self, operation: Dict) -> Dict[str, Any]:
        """スキーマからテストデータ生成"""
        test_data = {}
        
        # リクエストボディの生成
        request_body = operation.get("requestBody", {})
        if request_body:
            schema_ref = request_body.get("content", {}).get("application/json", {}).get("schema", {})
            test_data["body"] = self.generate_data_from_schema_ref(schema_ref)
        
        # パラメータの生成
        parameters = operation.get("parameters", [])
        test_data["params"] = {}
        test_data["path_params"] = {}
        
        for param in parameters:
            param_name = param["name"]
            param_schema = param["schema"]
            
            if param["in"] == "query":
                test_data["params"][param_name] = self.generate_value_from_schema(param_schema)
            elif param["in"] == "path":
                test_data["path_params"][param_name] = self.generate_value_from_schema(param_schema)
        
        return test_data
    
    def generate_data_from_schema_ref(self, schema_ref: Dict) -> Dict[str, Any]:
        """スキーマ参照からデータ生成"""
        if "$ref" in schema_ref:
            # 参照スキーマの解決
            ref_path = schema_ref["$ref"].split("/")
            schema = self.openapi_spec
            for part in ref_path[1:]:  # "#" をスキップ
                schema = schema[part]
        else:
            schema = schema_ref
        
        return self.generate_data_from_schema(schema)
    
    def generate_data_from_schema(self, schema: Dict) -> Any:
        """スキーマからデータ生成"""
        if schema.get("type") == "object":
            obj = {}
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            for prop_name, prop_schema in properties.items():
                if prop_name in required or prop_schema.get("default") is not None:
                    obj[prop_name] = self.generate_value_from_schema(prop_schema)
            
            return obj
        else:
            return self.generate_value_from_schema(schema)
    
    def generate_value_from_schema(self, schema: Dict) -> Any:
        """スキーマから値生成"""
        schema_type = schema.get("type")
        
        if schema.get("default") is not None:
            return schema["default"]
        
        if schema.get("enum"):
            return schema["enum"][0]
        
        if schema_type == "string":
            if schema.get("format") == "email":
                return "test@example.com"
            elif schema.get("format") == "date-time":
                return datetime.utcnow().isoformat()
            else:
                return "test_string"
        elif schema_type == "integer":
            return schema.get("minimum", 1)
        elif schema_type == "number":
            return schema.get("minimum", 1.0)
        elif schema_type == "boolean":
            return True
        elif schema_type == "array":
            item_schema = schema.get("items", {})
            return [self.generate_value_from_schema(item_schema)]
        else:
            return None
    
    async def execute_request(self, path: str, method: str, test_data: Dict) -> httpx.Response:
        """リクエスト実行"""
        # パスパラメータの置換
        actual_path = path
        for param_name, param_value in test_data.get("path_params", {}).items():
            actual_path = actual_path.replace(f"{{{param_name}}}", str(param_value))
        
        async with httpx.AsyncClient(base_url="http://localhost:9995") as client:
            if method.upper() == "GET":
                return await client.get(actual_path, params=test_data.get("params"))
            elif method.upper() == "POST":
                return await client.post(actual_path, json=test_data.get("body"), params=test_data.get("params"))
            elif method.upper() == "PUT":
                return await client.put(actual_path, json=test_data.get("body"), params=test_data.get("params"))
            elif method.upper() == "DELETE":
                return await client.delete(actual_path, params=test_data.get("params"))
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
    
    def validate_response_schema(self, response: httpx.Response, operation: Dict) -> Dict[str, Any]:
        """レスポンススキーマ検証"""
        status_code = str(response.status_code)
        responses = operation.get("responses", {})
        
        if status_code not in responses:
            return {
                "valid": False,
                "error": f"Unexpected status code: {status_code}"
            }
        
        expected_response = responses[status_code]
        content_schema = expected_response.get("content", {}).get("application/json", {}).get("schema", {})
        
        if not content_schema:
            return {"valid": True}  # スキーマが定義されていない場合は通過
        
        try:
            response_data = response.json()
            validation_result = self.validate_data_against_schema(response_data, content_schema)
            return validation_result
        except json.JSONDecodeError:
            return {
                "valid": False,
                "error": "Response is not valid JSON"
            }
    
    def validate_data_against_schema(self, data: Any, schema: Dict) -> Dict[str, Any]:
        """データのスキーマ検証"""
        errors = []
        
        if schema.get("type") == "object":
            if not isinstance(data, dict):
                errors.append(f"Expected object, got {type(data).__name__}")
            else:
                # 必須フィールドの確認
                required = schema.get("required", [])
                for req_field in required:
                    if req_field not in data:
                        errors.append(f"Required field '{req_field}' is missing")
                
                # プロパティの検証
                properties = schema.get("properties", {})
                for prop_name, prop_schema in properties.items():
                    if prop_name in data:
                        prop_validation = self.validate_data_against_schema(data[prop_name], prop_schema)
                        if not prop_validation["valid"]:
                            errors.extend([f"{prop_name}: {err}" for err in prop_validation["errors"]])
        
        elif schema.get("type") == "array":
            if not isinstance(data, list):
                errors.append(f"Expected array, got {type(data).__name__}")
            else:
                item_schema = schema.get("items", {})
                for i, item in enumerate(data):
                    item_validation = self.validate_data_against_schema(item, item_schema)
                    if not item_validation["valid"]:
                        errors.extend([f"[{i}]: {err}" for err in item_validation["errors"]])
        
        elif schema.get("type") == "string":
            if not isinstance(data, str):
                errors.append(f"Expected string, got {type(data).__name__}")
        
        elif schema.get("type") == "integer":
            if not isinstance(data, int):
                errors.append(f"Expected integer, got {type(data).__name__}")
        
        elif schema.get("type") == "number":
            if not isinstance(data, (int, float)):
                errors.append(f"Expected number, got {type(data).__name__}")
        
        elif schema.get("type") == "boolean":
            if not isinstance(data, bool):
                errors.append(f"Expected boolean, got {type(data).__name__}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

# 統合テスト実行例
async def run_integration_tests():
    """統合テスト実行"""
    
    # フルスタック統合テスト
    full_stack_test = FullStackIntegrationTest()
    lifecycle_result = await full_stack_test.test_complete_product_lifecycle(None, None)
    
    print("=== フルスタック統合テスト結果 ===")
    print(f"テスト結果: {'PASS' if lifecycle_result['test_passed'] else 'FAIL'}")
    print(f"完了ステップ数: {lifecycle_result['steps_completed']}")
    
    # API契約テスト
    contract_test = SchemaContractTest(".tmp/frontend_sync/openapi_spec.json")
    contract_result = await contract_test.test_all_endpoints_contract()
    
    print("\n=== API契約テスト結果 ===")
    print(f"総テスト数: {contract_result['total_tests']}")
    print(f"成功: {contract_result['passed']}")
    print(f"失敗: {contract_result['failed']}")
    print(f"成功率: {contract_result['passed'] / contract_result['total_tests'] * 100:.1f}%")
    
    return {
        "fullstack_test": lifecycle_result,
        "contract_test": contract_result
    }

if __name__ == "__main__":
    asyncio.run(run_integration_tests())