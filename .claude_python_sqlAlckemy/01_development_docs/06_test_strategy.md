# テスト戦略ドキュメント

## 🎯 テスト方針

### テストピラミッド
```
          E2Eテスト
         /    5%    \
        /            \
       統合テスト      
      /    25%       \
     /               \
    ユニットテスト     
   /      70%        \
  /                  \
```

### カバレッジ目標
- 全体: 80%以上
- コアビジネスロジック: 90%以上
- API エンドポイント: 95%以上

## 🧪 テストレベル別戦略

### 1. ユニットテスト

#### 対象
- ビジネスロジック関数
- バリデーション関数
- ユーティリティ関数
- モデルメソッド

#### 実装例
```python
# tests/unit/test_production_service.py
import pytest
from datetime import datetime, timedelta
from services.production import ProductionService
from models.production import ProductionResult

class TestProductionService:
    """生産サービスのユニットテスト"""
    
    @pytest.fixture
    def service(self):
        return ProductionService()
    
    def test_calculate_efficiency(self, service):
        """生産効率計算のテスト"""
        result = ProductionResult(
            planned_quantity=100,
            actual_quantity=95,
            defect_quantity=5
        )
        
        efficiency = service.calculate_efficiency(result)
        assert efficiency == 95.0
    
    def test_calculate_efficiency_zero_planned(self, service):
        """計画数ゼロの場合の効率計算"""
        result = ProductionResult(
            planned_quantity=0,
            actual_quantity=0,
            defect_quantity=0
        )
        
        efficiency = service.calculate_efficiency(result)
        assert efficiency == 0
    
    @pytest.mark.parametrize("planned,actual,expected", [
        (100, 100, 100.0),
        (100, 50, 50.0),
        (100, 150, 150.0),
        (0, 100, 0),
    ])
    def test_calculate_efficiency_various_cases(
        self, service, planned, actual, expected
    ):
        """様々なケースでの効率計算"""
        result = ProductionResult(
            planned_quantity=planned,
            actual_quantity=actual,
            defect_quantity=0
        )
        
        efficiency = service.calculate_efficiency(result)
        assert efficiency == expected
```

### 2. 統合テスト

#### 対象
- API エンドポイント
- データベース操作
- 外部サービス連携

#### 実装例
```python
# tests/integration/test_shipment_api.py
import pytest
from fastapi.testclient import TestClient
from datetime import date

class TestShipmentAPI:
    """出荷APIの統合テスト"""
    
    def test_create_checksheet(self, client: TestClient, db_session):
        """チェックシート作成のテスト"""
        # テストデータ準備
        payload = {
            "shipment_no": "TEST-2024-001",
            "customer_id": 1,
            "product_id": 1,
            "shipment_date": str(date.today()),
            "items": [
                {
                    "check_point": "外観検査",
                    "result": "OK"
                },
                {
                    "check_point": "数量確認",
                    "result": "OK"
                }
            ]
        }
        
        # APIコール
        response = client.post(
            "/syukkachecksheetapi/checksheets",
            json=payload
        )
        
        # アサーション
        assert response.status_code == 201
        data = response.json()
        assert data["shipment_no"] == payload["shipment_no"]
        assert "checksheet_id" in data
        
        # データベース確認
        from models.shipment import ShipmentChecksheet
        checksheet = db_session.query(ShipmentChecksheet).filter_by(
            shipment_no=payload["shipment_no"]
        ).first()
        assert checksheet is not None
        assert len(checksheet.items) == 2
    
    def test_get_checksheet_not_found(self, client: TestClient):
        """存在しないチェックシートの取得"""
        response = client.get("/syukkachecksheetapi/checksheets/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["error"]["message"].lower()
```

### 3. E2Eテスト

#### 対象
- 主要業務フロー
- クロスサービス連携
- 性能要件

#### 実装例
```python
# tests/e2e/test_production_flow.py
import pytest
from datetime import datetime
import asyncio

class TestProductionFlow:
    """生産フロー全体のE2Eテスト"""
    
    @pytest.mark.asyncio
    async def test_complete_production_flow(self, client, db_session):
        """生産開始から完了までの完全フロー"""
        
        # 1. 生産計画作成
        plan_response = await client.post(
            "/prdctrl/production-plans",
            json={
                "work_order_no": "WO-E2E-001",
                "product_id": 1,
                "planned_quantity": 1000,
                "scheduled_date": str(datetime.now().date())
            }
        )
        assert plan_response.status_code == 201
        
        # 2. 生産開始
        start_response = await client.post(
            "/prdctrl/production-results/start",
            json={
                "work_order_no": "WO-E2E-001",
                "line_id": 1,
                "worker_id": 100
            }
        )
        assert start_response.status_code == 200
        result_id = start_response.json()["result_id"]
        
        # 3. 実績報告（複数回）
        for i in range(10):
            report_response = await client.post(
                f"/prdctrl/production-results/{result_id}/report",
                json={
                    "quantity": 95,
                    "defects": [
                        {"defect_type_id": 1, "quantity": 5}
                    ]
                }
            )
            assert report_response.status_code == 200
            await asyncio.sleep(0.1)  # 実際の時間経過をシミュレート
        
        # 4. 生産完了
        complete_response = await client.post(
            f"/prdctrl/production-results/{result_id}/complete"
        )
        assert complete_response.status_code == 200
        
        # 5. 結果検証
        final_result = complete_response.json()
        assert final_result["actual_quantity"] == 950
        assert final_result["defect_quantity"] == 50
        assert final_result["efficiency"] == 95.0
        
        # 6. 在庫への反映確認
        inventory_response = await client.get(
            f"/zaikokanriapi/items/search?product_id=1"
        )
        assert inventory_response.status_code == 200
        inventory = inventory_response.json()["items"][0]
        # 在庫が増加していることを確認
```

## 🛠️ テストツールとライブラリ

### 必須ツール
```python
# テスト関連の依存関係
pytest==7.1.2
pytest-asyncio==0.19.0
pytest-cov==3.0.0
pytest-mock==3.8.2
pytest-xdist==2.5.0  # 並列実行
pytest-timeout==2.1.0
pytest-env==0.6.2

# モック・フィクスチャ
factory-boy==3.2.1
faker==13.15.0
freezegun==1.2.1  # 時間の固定

# アサーション
pytest-benchmark==3.4.1
pytest-clarity==1.0.1
```

### テストデータ生成
```python
# tests/factories.py
import factory
from factory.alchemy import SQLAlchemyModelFactory
from models import Product, Customer, Employee
from faker import Faker

fake = Faker('ja_JP')

class ProductFactory(SQLAlchemyModelFactory):
    """製品のテストデータファクトリー"""
    class Meta:
        model = Product
        sqlalchemy_session_persistence = 'commit'
    
    product_code = factory.Sequence(lambda n: f"TEST-PROD-{n:04d}")
    product_name = factory.LazyAttribute(lambda _: fake.word())
    product_type = factory.Faker('random_element', elements=['TypeA', 'TypeB', 'TypeC'])
    unit = '個'
    is_active = True

class CustomerFactory(SQLAlchemyModelFactory):
    """顧客のテストデータファクトリー"""
    class Meta:
        model = Customer
        sqlalchemy_session_persistence = 'commit'
    
    customer_code = factory.Sequence(lambda n: f"TEST-CUST-{n:04d}")
    customer_name = factory.LazyAttribute(lambda _: fake.company())
    address = factory.LazyAttribute(lambda _: fake.address())
    contact_person = factory.LazyAttribute(lambda _: fake.name())
    phone = factory.LazyAttribute(lambda _: fake.phone_number())
    email = factory.LazyAttribute(lambda _: fake.company_email())
```

## 📊 テストカバレッジ

### カバレッジ設定（.coveragerc）
```ini
[run]
source = .
omit = 
    */tests/*
    */venv/*
    */alembic/*
    */__init__.py
    */conftest.py
    setup.py

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

### カバレッジレポート生成
```bash
# カバレッジ付きテスト実行
pytest --cov=. --cov-report=html --cov-report=term-missing

# 特定モジュールのカバレッジ
pytest --cov=api.syukkachecksheetapi tests/unit/test_shipment.py

# カバレッジレポートの表示
python -m http.server --directory htmlcov 8000
```

## 🔄 CI/CDパイプライン

### GitHub Actions設定
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mssql:
        image: mcr.microsoft.com/mssql/server:2019-latest
        env:
          ACCEPT_EULA: Y
          SA_PASSWORD: Test@123
        ports:
          - 1433:1433
        options: >-
          --health-cmd "/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P Test@123 -Q 'SELECT 1'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run linting
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        mypy .
    
    - name: Run tests
      env:
        DATABASE_SERVER: localhost
        DATABASE_USER: sa
        DATABASE_PASSWORD: Test@123
      run: |
        pytest -v --cov=. --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

## 🐛 テストデバッグ

### デバッグ用設定
```python
# pytest.ini に追加
[tool:pytest]
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    -p no:cacheprovider

# デバッグ時のみ
# addopts = -s --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
```

### テストのデバッグ例
```python
import pytest
import pdb

def test_complex_logic():
    """複雑なロジックのデバッグ"""
    data = prepare_test_data()
    
    # ブレークポイント設定
    pdb.set_trace()
    
    result = complex_business_logic(data)
    assert result.status == "success"
```

## 📈 パフォーマンステスト

### 負荷テスト
```python
# tests/performance/test_load.py
import pytest
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_production_results(self):
        self.client.get("/prdctrl/production-results")
    
    @task(1)
    def create_inventory_transaction(self):
        self.client.post("/zaikokanriapi/transactions", json={
            "item_id": 1,
            "transaction_type": "OUT",
            "quantity": 10
        })

# 実行: locust -f tests/performance/test_load.py --host=http://localhost:9995
```

## ✅ テストチェックリスト

### PRマージ前チェック
- [ ] 全テストがパスしている
- [ ] カバレッジが基準を満たしている
- [ ] 新機能に対するテストが追加されている
- [ ] 統合テストが実装されている
- [ ] ドキュメントが更新されている
- [ ] パフォーマンステストを実施（必要に応じて）