# Fix Command - 製造業システムバグ修正・問題解決

## 概要
FastAPI + SQLAlchemy製造業システムの特定の問題やバグを迅速に特定・修正し、根本原因を解決します。製造業特有のトラブルシューティングから修正、テスト、再発防止まで包括的にサポートします。

## 使用方法
```
/fix [製造業問題の説明またはエラーメッセージ]
```

## 実行プロセス

### 1. 製造業問題の特定と分析

#### 1.1 製造業エラー情報の収集
```python
# 製造業エラー情報の構造化
def analyze_manufacturing_error_info(user_input):
    return {
        'type': classify_manufacturing_error_type(user_input), # 'production', 'quality', 'equipment', 'database', 'api'
        'severity': assess_manufacturing_severity(user_input), # 'critical', 'high', 'medium', 'low'
        'context': extract_manufacturing_context(user_input),
        'symptoms': extract_manufacturing_symptoms(user_input),
        'reproduction': extract_manufacturing_reproduction_steps(user_input)
    }

# 製造業エラータイプの分類
def classify_manufacturing_error_type(input_text):
    manufacturing_patterns = {
        'production': /production.*error|work.*order.*failed|batch.*processing.*error/i,
        'quality': /quality.*check.*failed|defect.*detection|spc.*violation/i,
        'equipment': /equipment.*down|maintenance.*error|sensor.*failure/i,
        'inventory': /stock.*level.*error|parts.*shortage|warehouse.*issue/i,
        'database': /database.*error|query.*failed|constraint.*violation/i,
        'api': /api.*error|endpoint.*failed|timeout|connection.*refused/i,
        'iot': /mqtt.*error|modbus.*timeout|plc.*communication.*failed/i,
        'performance': /slow.*response|high.*cpu|memory.*leak/i
    }
    
    for error_type, pattern in manufacturing_patterns.items():
        if pattern.test(input_text):
            return error_type
    
    return 'unknown'
```

#### 1.2 製造業システム状態の診断
```python
# 現在の製造業システム状態を確認
async def perform_manufacturing_system_diagnostics():
    diagnostics = {
        'environment': await check_manufacturing_environment(),
        'dependencies': await check_manufacturing_dependencies(),
        'services': await check_manufacturing_services(),
        'database': await check_manufacturing_database(),
        'iot_connectivity': await check_iot_connectivity(),
        'equipment_status': await check_equipment_status()
    }
    
    return diagnostics

# 製造業環境チェック
async def check_manufacturing_environment():
    return {
        'python': sys.version,
        'fastapi': await get_package_version('fastapi'),
        'sqlalchemy': await get_package_version('sqlalchemy'),
        'alembic': await get_package_version('alembic'),
        'celery': await get_package_version('celery'),
        'redis': await check_redis_connection(),
        'postgresql': await check_postgresql_connection(),
        'env_vars': check_manufacturing_env_vars()
    }

# 製造業データベース接続チェック
async def check_manufacturing_database_connection():
    try:
        async with AsyncSession() as session:
            result = await session.execute(text("SELECT 1"))
            latency_start = time.time()
            await session.execute(text("SELECT COUNT(*) FROM work_orders LIMIT 1"))
            latency = time.time() - latency_start
            
            return {
                'status': 'connected',
                'latency': latency * 1000,  # ms
                'error': None
            }
    except Exception as err:
        return {
            'status': 'error',
            'error': str(err),
            'possible_causes': [
                '不正なデータベース接続文字列',
                'PostgreSQLサービスの停止',
                'ネットワーク接続問題',
                '製造業テーブルの権限問題'
            ]
        }
```

### 2. 製造業問題の分類と優先度評価

#### 2.1 製造業問題の分類マトリックス
```python
# 製造業問題の重要度と緊急度を評価
def prioritize_manufacturing_issue(error_info, system_state):
    matrix = {
        'critical': {
            'criteria': [
                '生産ライン全停止',
                '製造データ損失の可能性',
                '品質管理システムの障害',
                '安全システムの機能停止'
            ],
            'response': 'immediate', # 5分以内
            'team': ['production-manager', 'system-admin', 'safety-officer']
        },
        'high': {
            'criteria': [
                '単一生産ラインの停止',
                '品質データ記録不能',
                '在庫管理システム障害',
                'MES連携エラー'
            ],
            'response': '30分以内',
            'team': ['production-engineer', 'it-support']
        },
        'medium': {
            'criteria': [
                '設備データ収集エラー',
                'レポート生成失敗',
                '一部機能の不具合',
                'パフォーマンス低下'
            ],
            'response': '2-4時間',
            'team': ['developer']
        },
        'low': {
            'criteria': [
                'ログ警告',
                 'UI表示の軽微な問題',
                '開発環境での問題'
            ],
            'response': '1-2日',
            'team': ['developer']
        }
    }
    
    return assess_manufacturing_priority(error_info, matrix)
```

### 3. 製造業修正戦略の立案

#### 3.1 FastAPI + SQLAlchemy製造業特有の問題パターン
```python
# 製造業FastAPI関連の一般的な問題と解決策
manufacturing_fastapi_fix_patterns = {
    'async_database': {
        'symptoms': ['database connection timeout', 'async session error'],
        'common_causes': [
            'AsyncSession の不適切な使用',
            '非同期コンテキストマネージャーの不備',
            'connection pool設定問題'
        ],
        'solutions': [
            {
                'issue': 'AsyncSessionの不適切な使用',
                'fix': '''
# 問題のあるコード
async def get_work_orders():
    session = AsyncSession()  # ❌
    result = await session.execute(select(WorkOrder))
    return result.scalars().all()

# 修正版
async def get_work_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkOrder))
    return result.scalars().all()

# または
async def get_work_orders():
    async with AsyncSession() as session:  # ✅
        result = await session.execute(select(WorkOrder))
        return result.scalars().all()
''',
                'explanation': 'AsyncSessionは適切にライフサイクル管理する必要があります'
            }
        ]
    },
    
    'manufacturing_validation': {
        'symptoms': ['validation error', 'pydantic parsing failed'],
        'solutions': [
            {
                'issue': '製造業データ型の不整合',
                'fix': '''
# 製造業特有のバリデーション修正
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime

class WorkOrderCreate(BaseModel):
    product_code: str = Field(..., min_length=1, max_length=50)
    quantity: int = Field(..., gt=0, le=100000)
    priority: int = Field(default=5, ge=1, le=10)
    
    @validator('product_code')
    def validate_product_code(cls, v):
        if not v.startswith(('P', 'WO')):
            raise ValueError('製品コードはPまたはWOで始まる必要があります')
        return v
    
    @validator('quantity')
    def validate_manufacturing_quantity(cls, v):
        if v <= 0:
            raise ValueError('製造数量は0より大きい必要があります')
        return v
'''
            }
        ]
    },
    
    'iot_integration': {
        'symptoms': ['MQTT connection failed', 'sensor data timeout'],
        'solutions': [
            {
                'issue': 'IoTデバイス接続エラー',
                'fix': '''
# IoT接続の修正
import asyncio
from asyncio_mqtt import Client

class ManufacturingIoTClient:
    def __init__(self):
        self.client = None
        self.reconnect_interval = 5
    
    async def connect_with_retry(self):
        for attempt in range(3):
            try:
                self.client = Client(
                    hostname="mqtt.factory.local",
                    port=1883,
                    keepalive=60
                )
                await self.client.__aenter__()
                return True
            except Exception as e:
                logger.warning(f"MQTT接続試行 {attempt + 1} 失敗: {e}")
                if attempt < 2:
                    await asyncio.sleep(self.reconnect_interval)
        return False
    
    async def subscribe_to_sensors(self, topic_filter: str):
        if not self.client:
            if not await self.connect_with_retry():
                raise ConnectionError("MQTT接続に失敗しました")
        
        await self.client.subscribe(topic_filter)
        async with self.client.unfiltered_messages() as messages:
            async for message in messages:
                await self.process_sensor_data(message)
'''
            }
        ]
    }
}

# 製造業SQLAlchemy特有の問題パターン
manufacturing_sqlalchemy_fix_patterns = {
    'relationship_issues': {
        'symptoms': ['relationship loading failed', 'N+1 query problem'],
        'solutions': [
            {
                'issue': '製造業モデル間のN+1クエリ問題',
                'fix': '''
# 問題のあるコード - N+1クエリ
async def get_work_orders_with_products():
    result = await session.execute(select(WorkOrder))
    work_orders = result.scalars().all()
    
    for wo in work_orders:
        product = await session.get(Product, wo.product_id)  # ❌ N+1クエリ
        wo.product = product
    
    return work_orders

# 修正版 - Eager Loading使用
async def get_work_orders_with_products():
    result = await session.execute(
        select(WorkOrder)
        .options(selectinload(WorkOrder.product))  # ✅ Eager Loading
        .options(selectinload(WorkOrder.quality_checks))
    )
    return result.scalars().all()

# または JOIN使用
async def get_work_orders_with_products():
    result = await session.execute(
        select(WorkOrder, Product)
        .join(Product, WorkOrder.product_id == Product.id)
    )
    return result.all()
'''
            }
        ]
    },
    
    'constraint_violations': {
        'symptoms': ['IntegrityError', 'constraint violation'],
        'solutions': [
            {
                'issue': '製造業データ制約違反',
                'fix': '''
# 製造業特有の制約違反処理
from sqlalchemy.exc import IntegrityError

async def create_work_order_safe(work_order_data: WorkOrderCreate, db: AsyncSession):
    try:
        # 重複チェック
        existing = await db.execute(
            select(WorkOrder).where(
                WorkOrder.work_order_number == work_order_data.work_order_number
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail="ワークオーダー番号が既に存在します"
            )
        
        # 製品存在チェック
        product = await db.get(Product, work_order_data.product_id)
        if not product or not product.is_active:
            raise HTTPException(
                status_code=404,
                detail="有効な製品が見つかりません"
            )
        
        # 生産能力チェック
        if work_order_data.quantity > product.max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"製造数量が最大バッチサイズ({product.max_batch_size})を超えています"
            )
        
        work_order = WorkOrder(**work_order_data.dict())
        db.add(work_order)
        await db.commit()
        await db.refresh(work_order)
        return work_order
        
    except IntegrityError as e:
        await db.rollback()
        if "foreign key constraint" in str(e):
            raise HTTPException(
                status_code=400,
                detail="関連するデータが存在しません"
            )
        elif "unique constraint" in str(e):
            raise HTTPException(
                status_code=409,
                detail="重複するデータが存在します"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="データベース制約違反が発生しました"
            )
'''
            }
        ]
    }
}
```

### 4. 製造業修正の実装

#### 4.1 製造業段階的修正アプローチ
```python
# 製造業修正の実装計画
def create_manufacturing_fix_plan(problem_analysis):
    return {
        'phases': [
            {
                'name': '製造業緊急対応',
                'duration': '5-15分',
                'actions': [
                    '生産への影響評価と一時停止判断',
                    'エラーログの詳細確認',
                    '製造業システム影響範囲の限定'
                ],
                'rollback': '変更の即座の取り消し可能'
            },
            {
                'name': '製造業根本原因の修正',
                'duration': '30分-2時間',
                'actions': [
                    '製造業特有の原因特定と修正',
                    '開発環境での動作確認',
                    '製造業関連箇所への影響確認'
                ],
                'validation': '製造業テストデータでの動作確認'
            },
            {
                'name': '製造業品質保証',
                'duration': '30分-1時間',
                'actions': [
                    '製造業テストケースの作成・実行',
                    '製造業リグレッションテスト',
                    '生産パフォーマンス影響の確認'
                ]
            },
            {
                'name': '製造業再発防止',
                'duration': '30分-1時間',
                'actions': [
                    '製造業 lint ルールの追加',
                    '製造業ドキュメント更新',
                    '製造業チーム共有・ナレッジベース更新'
                ]
            }
        ]
    }
```

## 出力形式

### 製造業修正レポート（.tmp/manufacturing_fix_report.md）
```markdown
# 製造業システム修正レポート

## 問題概要
- **報告日時**: 2024-01-15 14:30:00
- **問題**: 生産ラインでの品質チェック記録時にデータベースエラー
- **影響範囲**: 品質管理機能、生産実績記録
- **優先度**: Critical
- **生産への影響**: ライン#3 一時停止

## 1. 製造業問題分析

### 症状
- 品質検査結果を登録するとIntegrityError発生
- 生産実績が記録されず、ラインが停止状態
- エラーメッセージ: "constraint violation: quality_checks_fk"

### 根本原因
```python
# 問題のあったコード
async def create_quality_check(quality_data: QualityCheckCreate, db: AsyncSession):
    quality_check = QualityCheck(**quality_data.dict())
    db.add(quality_check)  # ❌ work_order_id の存在チェックなし
    await db.commit()
```

### 影響箇所
- `app/services/quality_service.py`
- `app/routers/quality.py`
- 生産ライン#3の品質管理プロセス

## 2. 修正内容

### 実装した修正
```python
# 修正後のコード
async def create_quality_check(quality_data: QualityCheckCreate, db: AsyncSession):
    # ワークオーダー存在確認
    work_order = await db.get(WorkOrder, quality_data.work_order_id)
    if not work_order:
        raise HTTPException(
            status_code=404,
            detail="指定されたワークオーダーが見つかりません"
        )
    
    # ワークオーダーステータス確認
    if work_order.status not in ['IN_PROGRESS', 'COMPLETED']:
        raise HTTPException(
            status_code=400,
            detail="このワークオーダーには品質チェックを追加できません"
        )
    
    quality_check = QualityCheck(**quality_data.dict())
    db.add(quality_check)
    
    try:
        await db.commit()
        await db.refresh(quality_check)
        
        # 生産実績の更新
        await update_production_metrics(work_order.id, db)
        
        return quality_check
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"品質チェック作成エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail="品質チェックの作成に失敗しました"
        )
```

### 修正理由
1. ワークオーダーの存在確認を事前に実施
2. ワークオーダーステータスの妥当性チェック
3. 適切なエラーハンドリングとロールバック処理
4. 生産実績の連動更新

## 3. 製造業テスト結果

### 実行したテスト
- ✅ 正常な品質チェック記録の動作確認
- ✅ 存在しないワークオーダーでのエラーハンドリング確認
- ✅ 無効ステータスワークオーダーでの拒否確認
- ✅ 生産ライン#3での実際の動作確認
- ✅ 他の生産ラインへの影響確認（影響なし）

### 追加されたテストケース
```python
@pytest.mark.asyncio
async def test_quality_check_with_invalid_work_order():
    """存在しないワークオーダーIDでの品質チェック作成テスト"""
    quality_data = QualityCheckCreate(
        work_order_id="non-existent-id",
        check_type="visual_inspection",
        result="pass",
        inspector_id="inspector1"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await create_quality_check(quality_data, db_session)
    
    assert exc_info.value.status_code == 404
    assert "ワークオーダーが見つかりません" in str(exc_info.value.detail)
```

## 4. 製造業再発防止策

### 実装済み対策
1. **製造業バリデーションルール追加**
   ```python
   # app/core/validators.py
   async def validate_work_order_exists(work_order_id: str, db: AsyncSession):
       work_order = await db.get(WorkOrder, work_order_id)
       if not work_order:
           raise ValueError(f"ワークオーダー {work_order_id} が存在しません")
       return work_order
   ```

2. **製造業データ整合性チェック強化**
   - 品質チェック前のワークオーダー状態確認
   - 生産ライン稼働状態との整合性確認

3. **製造業監視アラート追加**
   - 品質チェック失敗時の自動アラート
   - 生産ライン停止時の即座通知

## 5. 影響範囲と検証

### 影響したファイル
- `app/services/quality_service.py`（修正）
- `app/core/validators.py`（新規追加）
- `tests/services/test_quality_service.py`（テスト追加）

### 検証済み項目
- ✅ 全生産ラインでの正常動作確認
- ✅ 既存品質データへの影響なし
- ✅ パフォーマンス劣化なし（応答時間 < 100ms維持）
- ✅ 他の製造システムへの影響なし

## 6. 製造業デプロイメント

### デプロイ手順
1. 生産ライン#3 一時停止（14:45）
2. ステージング環境での最終テスト完了（15:00）
3. 製造業システムへのホットフィックスデプロイ実行（15:15）
4. 品質チェック機能の動作確認（15:20）
5. 生産ライン#3 再開（15:25）

### ロールバック計画
- 修正前の製造業コードをバックアップ済み
- 問題発生時は5分以内にロールバック可能
- 生産データの整合性確認済み

## 7. 製造業学習内容

### チームで共有すべき製造業知識
1. 製造業データベース制約の重要性理解
2. 生産データ整合性チェックの必要性
3. 製造業システムでのエラーハンドリングベストプラクティス
4. 生産ラインへの影響を最小化する修正手順

### 製造業ベストプラクティス
```python
# 製造業推奨パターン
async def safe_manufacturing_operation(operation_data, db: AsyncSession):
    # 1. 事前検証
    await validate_manufacturing_prerequisites(operation_data, db)
    
    # 2. トランザクション開始
    async with db.begin():
        try:
            # 3. 製造業操作実行
            result = await execute_manufacturing_operation(operation_data, db)
            
            # 4. 関連する製造データの更新
            await update_related_manufacturing_data(result.id, db)
            
            # 5. 製造業KPIの更新
            await update_manufacturing_kpis(db)
            
            return result
            
        except Exception as e:
            # 6. エラー時の適切な処理
            logger.error(f"製造業操作エラー: {e}")
            await notify_production_team(f"製造業操作失敗: {e}")
            raise
```

## 8. 次のアクション

### 短期（1週間以内）
- [ ] 類似の製造業データ整合性問題がないかコードベース全体をレビュー
- [ ] 製造業チーム勉強会でエラーハンドリングについて共有
- [ ] 他の生産ラインでの同様問題の予防的チェック

### 中期（1ヶ月以内）
- [ ] 製造業データ整合性の自動チェックツール導入検討
- [ ] 製造業開発ガイドラインの更新
- [ ] 生産ライン向け障害対応手順書の見直し

## 9. まとめ

この修正により、品質チェック機能が正常に動作し、生産ラインが復旧しました。
根本原因は製造業データ整合性チェックの不足によるものでしたが、
適切な修正と再発防止策により、同様の問題を防ぐことができます。

**製造業システム停止時間**: 40分
**修正時間**: 1時間15分
**テスト時間**: 30分
**総所要時間**: 2時間25分
**生産への影響**: 最小限（計画停止として記録）
```

## TodoWrite連携

製造業修正作業のタスクを自動生成：

```python
manufacturing_fix_tasks = [
    {
        'id': 'manufacturing-fix-001',
        'content': '製造業問題の分析と原因特定',
        'status': 'completed',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-fix-002',
        'content': '製造業緊急対応（生産ライン影響評価）',
        'status': 'completed',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-fix-003',
        'content': '製造業根本原因の修正実装',
        'status': 'in_progress',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-fix-004',
        'content': '製造業テスト環境での動作確認',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-fix-005',
        'content': '製造業ユニットテストの作成',
        'status': 'pending',
        'priority': 'medium'
    },
    {
        'id': 'manufacturing-fix-006',
        'content': '生産ライン統合テスト実行',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-fix-007',
        'content': '製造業再発防止策の実装',
        'status': 'pending',
        'priority': 'medium'
    },
    {
        'id': 'manufacturing-fix-008',
        'content': '製造業ドキュメント更新と知識共有',
        'status': 'pending',
        'priority': 'low'
    }
]
```

## 製造業緊急対応フロー

```python
# 製造業緊急度に応じた対応フロー
manufacturing_emergency_flow = {
    'critical': {
        'response': '5分以内',
        'actions': [
            '生産ライン停止判断',
            '安全システム状態確認',
            '製造データバックアップ確認',
            '生産管理者・安全責任者への緊急連絡'
        ],
        'team': ['production-manager', 'safety-officer', 'system-admin']
    },
    'high': {
        'response': '30分以内',
        'actions': [
            '製造業問題の詳細分析',
            '生産への影響範囲特定',
            '回避策の検討・実装',
            '関係者への状況共有'
        ],
        'team': ['production-engineer', 'it-support']
    }
}
```

## 製造業エラーパターン辞書

```python
# よくある製造業問題パターンと解決策
manufacturing_common_patterns = {
    'work-order-constraint-violation': {
        'symptoms': ['IntegrityError: work_orders_fk', 'foreign key constraint fails'],
        'solution': 'ワークオーダー存在チェックと状態確認の実装',
        'prevention': '製造業データ整合性バリデーションの強化'
    },
    'quality-check-timeout': {
        'symptoms': ['quality check timeout', 'inspection device not responding'],
        'solution': '検査装置接続の再試行とフォールバック処理',
        'prevention': '検査装置監視とヘルスチェックの自動化'
    },
    'production-line-sync-error': {
        'symptoms': ['production data sync failed', 'line status mismatch'],
        'solution': '生産ライン状態の同期処理と整合性チェック',
        'prevention': 'リアルタイム同期監視の実装'
    },
    'iot-sensor-data-loss': {
        'symptoms': ['sensor data missing', 'mqtt message lost'],
        'solution': 'センサーデータの冗長化とバッファリング',
        'prevention': 'IoTデータロス検知とアラートシステム'
    }
}
```

## まとめ

このコマンドはFastAPI + SQLAlchemy製造業システムでの問題解決を迅速かつ体系的にサポートします：

1. **製造業迅速対応**: 生産への影響を最小化する段階的対応フロー
2. **製造業根本解決**: 一時的な対処ではなく、製造業特有の根本原因への対応
3. **製造業再発防止**: 製造業特化のlintルール、テスト、ドキュメント化による予防策
4. **製造業知識蓄積**: 製造業チーム全体での学習と問題パターンの蓄積

修正完了後は関連する他の製造業コマンド（analyze, enhance, refactor）での継続的改善を推奨します。
