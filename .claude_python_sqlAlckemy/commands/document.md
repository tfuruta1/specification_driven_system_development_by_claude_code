# Document Command - 製造業システムドキュメント生成・整備

## 概要
FastAPI + SQLAlchemy製造業システムの既存コードから包括的なドキュメントを自動生成し、製造業エンジニア・品質管理者・運用者向けの実用的なドキュメンテーションを整備します。製造業特有のコンプライアンス要件と技術仕様に基づいたドキュメントを作成します。

## 使用方法
```
/document [製造業ドキュメント種別またはスコープ]
```

### 製造業ドキュメント種別
- `api` - 製造業API仕様書
- `models` - 製造業データモデル仕様
- `architecture` - 製造業システムアーキテクチャ
- `deployment` - 製造業デプロイメントガイド
- `operations` - 製造業運用マニュアル
- `compliance` - 製造業コンプライアンス文書
- `all` - 全ての製造業ドキュメント

## 実行プロセス

### 1. 製造業コードベース分析

#### 1.1 製造業システム構造の解析
```python
# 製造業プロジェクト構造の自動解析
async def analyze_manufacturing_project_structure():
    return {
        'framework': await detect_fastapi_version(),
        'orm': await detect_sqlalchemy_version(),
        'database': await analyze_postgresql_setup(),
        'cache': await analyze_redis_setup(),
        'task_queue': await analyze_celery_setup(),
        'iot_integration': await analyze_iot_systems(),
        'manufacturing_domains': await analyze_manufacturing_domains(),
        'compliance_systems': await analyze_compliance_features()
    }

# 製造業ドメインモデルの分析
async def analyze_manufacturing_models():
    models = await find_sqlalchemy_models()
    manufacturing_hierarchy = {}
    
    for model in models:
        analysis = await analyze_manufacturing_model(model)
        manufacturing_hierarchy[model.name] = {
            'name': model.name,
            'type': classify_manufacturing_model_type(analysis),
            'domain': determine_manufacturing_domain(analysis),
            'fields': analysis.columns,
            'relationships': analysis.relationships,
            'constraints': analysis.constraints,
            'indexes': analysis.indexes,
            'compliance_requirements': extract_compliance_requirements(analysis)
        }
    
    return build_manufacturing_model_hierarchy(manufacturing_hierarchy)

# 製造業ドメインの分類
def classify_manufacturing_model_type(analysis):
    manufacturing_patterns = {
        'production': ['work_order', 'batch', 'production_line', 'schedule'],
        'quality': ['quality_check', 'inspection', 'defect', 'spc'],
        'inventory': ['material', 'part', 'stock', 'warehouse'],
        'equipment': ['machine', 'tool', 'maintenance', 'sensor'],
        'compliance': ['audit', 'regulation', 'certification', 'trace']
    }
    
    model_name = analysis.table_name.lower()
    for domain, keywords in manufacturing_patterns.items():
        if any(keyword in model_name for keyword in keywords):
            return domain
    
    return 'general'
```

#### 1.2 製造業API エンドポイントの抽出
```python
# FastAPI製造業ルーターの自動抽出
async def extract_manufacturing_api_operations():
    operations = {
        'production': {},
        'quality': {},
        'inventory': {},
        'equipment': {},
        'maintenance': {},
        'reports': {}
    }
    
    # FastAPIルーターの解析
    routers = await find_fastapi_routers()
    
    for router in routers:
        router_analysis = await analyze_manufacturing_router(router)
        
        domain = classify_manufacturing_router_domain(router.path)
        operations[domain][router.path] = {
            'endpoints': router_analysis.endpoints,
            'models': router_analysis.models,
            'authentication': router_analysis.auth_requirements,
            'permissions': router_analysis.permission_requirements,
            'compliance': router_analysis.compliance_features
        }
    
    return operations

# 製造業エンドポイント分析
async def analyze_manufacturing_endpoint(endpoint):
    return {
        'method': endpoint.method,
        'path': endpoint.path,
        'summary': endpoint.summary,
        'description': endpoint.description,
        'parameters': extract_manufacturing_parameters(endpoint),
        'request_body': extract_manufacturing_request_schema(endpoint),
        'responses': extract_manufacturing_response_schemas(endpoint),
        'business_logic': extract_manufacturing_business_logic(endpoint),
        'data_validation': extract_manufacturing_validation_rules(endpoint),
        'compliance_notes': extract_compliance_requirements(endpoint)
    }

# 製造業特有のバリデーション抽出
def extract_manufacturing_validation_rules(endpoint):
    validation_rules = {
        'data_integrity': [],
        'business_rules': [],
        'compliance_checks': [],
        'safety_validations': []
    }
    
    # Pydanticモデルの解析
    if endpoint.request_model:
        validation_rules['data_integrity'] = extract_pydantic_validators(endpoint.request_model)
    
    # 製造業ビジネスルールの抽出
    business_logic = endpoint.function_body
    manufacturing_validations = extract_manufacturing_business_validations(business_logic)
    validation_rules['business_rules'] = manufacturing_validations
    
    return validation_rules
```

### 2. 製造業APIドキュメント生成

#### 2.1 製造業API仕様書の作成
```markdown
# 製造業システムAPI仕様書

## 概要
このAPIはFastAPI + SQLAlchemyを基盤とした製造業管理システムを提供します。
生産管理、品質管理、在庫管理、設備管理を統合的にサポートします。

## 認証・認可

### JWT認証
```python
# エンドポイント: POST /auth/login
async def login(credentials: UserCredentials, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "department": user.department}
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}
```

**パラメータ:**
- `username` (string, required): ユーザー名またはメールアドレス
- `password` (string, required): パスワード

**レスポンス:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "string",
    "role": "production_manager",
    "department": "production",
    "permissions": ["read_work_orders", "write_work_orders"]
  }
}
```

### ロールベース認可
- `production_manager`: 生産管理機能のフルアクセス
- `quality_controller`: 品質管理機能のフルアクセス
- `maintenance_engineer`: 設備保全機能のフルアクセス
- `operator`: オペレーター向け限定アクセス
- `admin`: システム管理者権限

## 生産管理API

### ワークオーダー管理

#### ワークオーダー一覧取得
```python
# GET /production/work-orders
async def get_work_orders(
    status: Optional[WorkOrderStatus] = None,
    production_line: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[WorkOrderResponse]:
    
    query = select(WorkOrder).options(
        selectinload(WorkOrder.product),
        selectinload(WorkOrder.production_line),
        selectinload(WorkOrder.quality_checks)
    )
    
    # フィルター適用
    if status:
        query = query.where(WorkOrder.status == status)
    if production_line:
        query = query.where(WorkOrder.production_line_id == production_line)
    if date_from:
        query = query.where(WorkOrder.scheduled_start >= date_from)
    if date_to:
        query = query.where(WorkOrder.scheduled_end <= date_to)
    
    # 権限チェック
    if current_user.role == "operator":
        query = query.where(WorkOrder.assigned_operator_id == current_user.id)
    
    result = await db.execute(query)
    work_orders = result.scalars().all()
    
    return [WorkOrderResponse.from_orm(wo) for wo in work_orders]
```

**クエリパラメータ:**
- `status` (WorkOrderStatus, optional): ワークオーダーステータス
  - `PLANNED`: 計画済み
  - `IN_PROGRESS`: 実行中
  - `COMPLETED`: 完了
  - `CANCELLED`: キャンセル
- `production_line` (string, optional): 生産ライン ID
- `date_from` (date, optional): 開始日フィルター
- `date_to` (date, optional): 終了日フィルター

**レスポンス:**
```json
[
  {
    "id": "uuid",
    "work_order_number": "WO-2024-0001",
    "product": {
      "id": "uuid",
      "product_code": "P001",
      "name": "製品A",
      "specification": "仕様詳細"
    },
    "quantity": 1000,
    "status": "IN_PROGRESS",
    "priority": 5,
    "scheduled_start": "2024-01-15T08:00:00Z",
    "scheduled_end": "2024-01-15T16:00:00Z",
    "actual_start": "2024-01-15T08:05:00Z",
    "actual_end": null,
    "production_line": {
      "id": "uuid",
      "name": "ライン1",
      "capacity": 100
    },
    "quality_checks": [
      {
        "id": "uuid",
        "check_type": "visual_inspection",
        "result": "PASS",
        "inspector": "検査員A"
      }
    ],
    "created_at": "2024-01-14T10:00:00Z",
    "updated_at": "2024-01-15T08:05:00Z"
  }
]
```

#### ワークオーダー作成
```python
# POST /production/work-orders
async def create_work_order(
    work_order_data: WorkOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_work_order"))
) -> WorkOrderResponse:
    
    # 製品存在チェック
    product = await db.get(Product, work_order_data.product_id)
    if not product or not product.is_active:
        raise HTTPException(
            status_code=404,
            detail="Product not found or inactive"
        )
    
    # 生産能力チェック
    if work_order_data.quantity > product.max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"Quantity exceeds maximum batch size ({product.max_batch_size})"
        )
    
    # 生産ライン利用可能性チェック
    line_availability = await check_production_line_availability(
        db, work_order_data.production_line_id, 
        work_order_data.scheduled_start, work_order_data.scheduled_end
    )
    if not line_availability.available:
        raise HTTPException(
            status_code=409,
            detail=f"Production line not available: {line_availability.reason}"
        )
    
    # ワークオーダー作成
    work_order = WorkOrder(
        **work_order_data.dict(),
        created_by=current_user.id,
        status=WorkOrderStatus.PLANNED
    )
    
    db.add(work_order)
    await db.commit()
    await db.refresh(work_order)
    
    # 関連データの読み込み
    await db.refresh(work_order, ['product', 'production_line'])
    
    # 通知送信
    await notify_production_team(work_order)
    
    return WorkOrderResponse.from_orm(work_order)
```

**リクエストボディ:**
```json
{
  "product_id": "uuid",
  "production_line_id": "uuid",
  "quantity": 1000,
  "priority": 5,
  "scheduled_start": "2024-01-15T08:00:00Z",
  "scheduled_end": "2024-01-15T16:00:00Z",
  "special_instructions": "特別指示事項",
  "customer_order_reference": "CO-2024-001"
}
```

**バリデーション:**
- `quantity`: 1以上、製品の最大バッチサイズ以下
- `priority`: 1-10の範囲
- `scheduled_start`: 現在時刻以降
- `scheduled_end`: scheduled_start以降

## 品質管理API

### 品質検査記録

#### 品質検査実行
```python
# POST /quality/inspections
async def create_quality_inspection(
    inspection_data: QualityInspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_inspection"))
) -> QualityInspectionResponse:
    
    # ワークオーダー存在・状態チェック
    work_order = await db.get(WorkOrder, inspection_data.work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    if work_order.status not in [WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.COMPLETED]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot inspect work order in current status"
        )
    
    # 検査基準の取得
    inspection_standard = await get_inspection_standard(
        db, work_order.product_id, inspection_data.inspection_type
    )
    
    # 検査結果の自動判定
    inspection_result = evaluate_inspection_results(
        inspection_data.measurements, inspection_standard
    )
    
    # 検査記録作成
    inspection = QualityInspection(
        **inspection_data.dict(),
        inspector_id=current_user.id,
        result=inspection_result.overall_result,
        deviation_points=inspection_result.deviations,
        created_at=datetime.utcnow()
    )
    
    db.add(inspection)
    
    # 不良品検出時の処理
    if inspection_result.overall_result == InspectionResult.FAIL:
        await handle_quality_failure(db, work_order, inspection)
    
    await db.commit()
    await db.refresh(inspection)
    
    return QualityInspectionResponse.from_orm(inspection)
```

## 在庫管理API

### 材料在庫管理

#### 在庫レベル取得
```python
# GET /inventory/materials
async def get_material_inventory(
    material_code: Optional[str] = None,
    location: Optional[str] = None,
    low_stock_only: bool = False,
    db: AsyncSession = Depends(get_db)
) -> List[MaterialInventoryResponse]:
    
    query = select(MaterialInventory).options(
        selectinload(MaterialInventory.material),
        selectinload(MaterialInventory.location)
    )
    
    if material_code:
        query = query.join(Material).where(Material.code == material_code)
    
    if location:
        query = query.where(MaterialInventory.location_id == location)
    
    if low_stock_only:
        query = query.where(
            MaterialInventory.current_quantity <= MaterialInventory.safety_stock_level
        )
    
    result = await db.execute(query)
    inventory_items = result.scalars().all()
    
    return [MaterialInventoryResponse.from_orm(item) for item in inventory_items]
```

## 設備管理API

### 設備監視

#### 設備状態取得
```python
# GET /equipment/{equipment_id}/status
async def get_equipment_status(
    equipment_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> EquipmentStatusResponse:
    
    equipment = await db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # 最新のセンサーデータ取得
    latest_sensor_data = await get_latest_sensor_data(db, equipment_id)
    
    # 設備健全性評価
    health_score = await calculate_equipment_health(db, equipment, latest_sensor_data)
    
    # メンテナンス予定確認
    next_maintenance = await get_next_maintenance_schedule(db, equipment_id)
    
    return EquipmentStatusResponse(
        equipment=equipment,
        current_status=equipment.status,
        health_score=health_score,
        sensor_data=latest_sensor_data,
        next_maintenance=next_maintenance,
        alerts=await get_equipment_alerts(db, equipment_id)
    )
```

## データモデル仕様

### 製造業コアモデル

#### WorkOrder (ワークオーダー)
```python
class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    production_line_id: Mapped[UUID] = mapped_column(ForeignKey("production_lines.id"))
    
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[WorkOrderStatus] = mapped_column(Enum(WorkOrderStatus), default=WorkOrderStatus.PLANNED)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 関係性
    product: Mapped["Product"] = relationship("Product", back_populates="work_orders")
    production_line: Mapped["ProductionLine"] = relationship("ProductionLine")
    quality_checks: Mapped[List["QualityInspection"]] = relationship("QualityInspection", back_populates="work_order")
    
    # 制約
    __table_args__ = (
        CheckConstraint('quantity > 0', name='positive_quantity'),
        CheckConstraint('priority >= 1 AND priority <= 10', name='valid_priority'),
        CheckConstraint('scheduled_end > scheduled_start', name='valid_schedule'),
        Index('idx_work_order_status', 'status'),
        Index('idx_work_order_dates', 'scheduled_start', 'scheduled_end'),
    )
```

## エラーハンドリング

### 製造業特有のエラーパターン
```python
class ManufacturingException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code, detail)
        self.error_code = error_code

# 製造業エラーハンドラー
@app.exception_handler(ManufacturingException)
async def manufacturing_exception_handler(request: Request, exc: ManufacturingException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "code": exc.error_code,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url)
            }
        }
    )

# 一般的な製造業エラーコード
MANUFACTURING_ERROR_CODES = {
    "PRODUCTION_LINE_OCCUPIED": "指定された生産ラインは使用中です",
    "MATERIAL_SHORTAGE": "必要な材料が不足しています",
    "QUALITY_STANDARD_NOT_MET": "品質基準を満たしていません",
    "EQUIPMENT_MAINTENANCE_REQUIRED": "設備のメンテナンスが必要です",
    "BATCH_SIZE_EXCEEDED": "最大バッチサイズを超えています",
    "INVALID_PRODUCTION_SCHEDULE": "無効な生産スケジュールです"
}
```

## セキュリティ

### 製造業データ保護
- **データ暗号化**: 機密性の高い製造データ（レシピ、仕様等）の暗号化
- **アクセス制御**: 部門・役職に基づいた細かいアクセス権限制御
- **監査ログ**: 全ての製造業務操作の完全なログ記録（ISO 9001対応）
- **セッション管理**: 製造現場での安全なセッション管理

### コンプライアンス
- **ISO 9001**: 品質管理システム要件への対応
- **FDA 21 CFR Part 11**: 電子記録・電子署名要件への対応
- **データ保持**: 製造記録の法定保存期間対応
- **トレーサビリティ**: 製品の完全な履歴追跡

## API制限

### レート制限
- **認証API**: 10リクエスト/分
- **データ取得API**: 1000リクエスト/分
- **データ更新API**: 100リクエスト/分
- **バッチ処理API**: 10リクエスト/分

### 同時接続制限
- **生産ライン監視**: 50接続/生産ライン
- **リアルタイムデータ**: 100接続/システム
- **レポート生成**: 5同時生成/ユーザー
```

## 出力形式

### 製造業ドキュメント構成（docs/）
```
docs/
├── README.md                           # 製造業システム概要
├── getting-started.md                  # 製造業システムセットアップガイド
├── architecture/
│   ├── overview.md                    # 製造業システム概要
│   ├── database-schema.md             # 製造業データベース設計
│   ├── api-design.md                  # 製造業API設計
│   ├── iot-integration.md             # IoT統合設計
│   └── security.md                    # 製造業セキュリティ設計
├── api/
│   ├── authentication.md             # 認証・認可API
│   ├── production.md                  # 生産管理API
│   ├── quality.md                     # 品質管理API
│   ├── inventory.md                   # 在庫管理API
│   ├── equipment.md                   # 設備管理API
│   └── maintenance.md                 # 保全管理API
├── models/
│   ├── production-models.md           # 生産管理モデル
│   ├── quality-models.md              # 品質管理モデル
│   ├── inventory-models.md            # 在庫管理モデル
│   └── equipment-models.md            # 設備管理モデル
├── operations/
│   ├── deployment.md                  # 製造業システムデプロイ
│   ├── monitoring.md                  # 製造業システム監視
│   ├── backup-recovery.md             # バックアップ・復旧
│   └── troubleshooting.md             # トラブルシューティング
├── compliance/
│   ├── iso-9001.md                    # ISO 9001対応
│   ├── fda-cfr-21.md                  # FDA 21 CFR Part 11対応
│   ├── data-retention.md              # データ保持ポリシー
│   └── audit-trails.md                # 監査証跡管理
└── user-guides/
    ├── production-manager.md          # 生産管理者ガイド
    ├── quality-controller.md          # 品質管理者ガイド
    ├── maintenance-engineer.md        # 保全エンジニアガイド
    └── operator.md                    # オペレーターガイド
```

## TodoWrite連携

製造業ドキュメント作成タスクを自動生成：

```python
manufacturing_documentation_tasks = [
    {
        'id': 'manufacturing-doc-001',
        'content': '製造業システム構造分析とドメインモデル抽出',
        'status': 'completed',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-doc-002',
        'content': '製造業API仕様書の生成',
        'status': 'in_progress',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-doc-003',
        'content': '製造業データモデル仕様書の作成',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-doc-004',
        'content': '製造業システムアーキテクチャ文書の生成',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-doc-005',
        'content': '製造業コンプライアンス文書の作成',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-doc-006',
        'content': '製造業運用マニュアルの生成',
        'status': 'pending',
        'priority': 'medium'
    },
    {
        'id': 'manufacturing-doc-007',
        'content': '製造業ユーザーガイドの作成',
        'status': 'pending',
        'priority': 'medium'
    },
    {
        'id': 'manufacturing-doc-008',
        'content': '製造業ドキュメントの校正と公開',
        'status': 'pending',
        'priority': 'low'
    }
]
```

## 製造業ドキュメント品質チェック

```python
# 製造業ドキュメント品質の自動チェック
manufacturing_doc_quality_check = {
    'completeness': {
        'api_coverage': '全製造業APIエンドポイントのドキュメント化率',
        'model_coverage': '全製造業データモデルのドキュメント化率',
        'compliance_coverage': '必要なコンプライアンス文書の完成度'
    },
    
    'accuracy': {
        'code_sync': 'コードと製造業ドキュメントの同期状態',
        'validation_examples': '製造業バリデーションルールの実行可能性',
        'api_examples': '製造業API使用例の動作確認'
    },
    
    'compliance': {
        'iso_9001': 'ISO 9001要件への適合性',
        'fda_cfr_21': 'FDA 21 CFR Part 11要件への適合性',
        'audit_trail': '監査証跡要件の文書化完成度',
        'data_integrity': 'データ完全性要件の文書化'
    },
    
    'usability': {
        'manufacturing_terminology': '製造業専門用語の適切な使用',
        'role_based_navigation': '職務別ドキュメントナビゲーション',
        'practical_examples': '実際の製造業務に即した例の提供'
    }
}
```

## 継続的ドキュメント更新

```python
# 製造業CI/CDでの自動ドキュメント更新
manufacturing_automated_doc_update = {
    'triggers': [
        '製造業APIエンドポイントの追加・変更',
        '製造業データモデルの変更',
        '製造業ビジネスルールの更新',
        'コンプライアンス要件の変更',
        '製造業セキュリティポリシーの更新'
    ],
    
    'actions': [
        '製造業API仕様書の自動更新',
        '製造業データモデル図の再生成',
        'コンプライアンス文書の更新確認',
        '製造業ユーザーガイドの更新',
        '製造業ドキュメントの品質チェック実行'
    ],
    
    'validation': [
        '製造業専門用語の一貫性チェック',
        'コンプライアンス要件の網羅性確認',
        '製造業ワークフローの正確性検証',
        'セキュリティ要件の文書化確認'
    ]
}
```

## まとめ

このコマンドはFastAPI + SQLAlchemy製造業システムの包括的なドキュメント生成を支援します：

1. **製造業特化**: 生産管理・品質管理・在庫管理・設備管理の専門ドキュメント
2. **コンプライアンス対応**: ISO 9001、FDA 21 CFR Part 11等の規制要件を満たすドキュメント
3. **実用性重視**: 製造業エンジニア・品質管理者・オペレーター向けの実践的ガイド
4. **自動更新**: コード変更に連動した製造業ドキュメントの自動更新

生成されたドキュメントは製造業システムの運用・保守・コンプライアンス監査の基礎資料として活用できます。