# Database-Optimize Command - 製造業データベース特化最適化

## 概要

FastAPI + SQLAlchemy + PostgreSQL製造業システムの包括的なデータベース最適化を実行するコマンドです。製造業特有のデータ要求・パフォーマンス要求・規制要求に対応し、PostgreSQL、非同期処理、トランザクション管理、データ整合性、監査機能の全てを最適化し、マルチAI協調による高度な分析・改善を提供します。

## 使用方法

```bash
# 基本的な使用方法
/database-optimize [optimization_type] [options]

# 使用例
/database-optimize performance --ai-collaboration
/database-optimize manufacturing-transactions --with-audit-analysis
/database-optimize real-time --manufacturing-scale-testing
/database-optimize batch-processing --implementation-roadmap
/database-optimize full-system --multi-ai-manufacturing-report
```

## パラメータ

### 必須パラメータ
- `optimization_type`: 最適化タイプ (`performance` | `manufacturing-transactions` | `real-time` | `batch-processing` | `audit-compliance` | `full-system`)

### オプション
- `--ai-collaboration`: マルチAI協調分析実行
- `--with-audit-analysis`: 製造業監査専門分析
- `--manufacturing-scale-testing`: 製造業スケーラビリティテスト実行
- `--implementation-roadmap`: 製造業実装ロードマップ生成
- `--multi-ai-manufacturing-report`: 製造業統合レポート生成
- `--performance-target=N`: 製造業パフォーマンス目標値設定
- `--compliance-level`: 規制準拠レベル（iso9001, fda21cfr, gmp）

## 製造業マルチAI協調データベース最適化

### 1. Gemini CLI - 製造業データアナリスト連携

#### 製造業データベース利用パターン分析
```python
# Gemini CLI 製造業データベース分析要求
manufacturing_db_analysis_request = {
    "analysis_type": "manufacturing_database_optimization_patterns",
    "data_sources": [
        "manufacturing_analytics",
        "postgresql_performance_logs", 
        "production_data_metrics",
        "quality_control_data_patterns",
        "equipment_monitoring_data",
        "batch_record_access_patterns"
    ],
    
    "manufacturing_performance_analysis": {
        "production_queries": {
            "work_order_queries": "identify_and_optimize_production_queries",
            "batch_traceability": "analyze_traceability_query_patterns",
            "quality_data_access": "optimize_quality_control_queries",
            "equipment_monitoring": "real_time_equipment_data_optimization"
        },
        
        "real_time_manufacturing": {
            "sensor_data_ingestion": "iot_data_throughput_analysis",
            "production_line_monitoring": "real_time_performance_metrics",
            "alert_processing": "manufacturing_alert_latency_analysis",
            "dashboard_updates": "manufacturing_dashboard_optimization"
        },
        
        "audit_compliance_impact": {
            "audit_trail_performance": "compliance_logging_optimization",
            "regulatory_reporting": "manufacturing_report_generation_efficiency",
            "data_retention": "long_term_storage_optimization",
            "backup_recovery": "manufacturing_data_protection_analysis"
        }
    },
    
    "manufacturing_usage_insights": {
        "production_shift_patterns": "shift_based_usage_analysis",
        "seasonal_variations": "manufacturing_seasonal_load_patterns",
        "equipment_lifecycle": "equipment_data_growth_patterns",
        "quality_trend_analysis": "quality_data_correlation_analysis"
    },
    
    "manufacturing_optimization_recommendations": {
        "priority_ranking": "manufacturing_impact_vs_effort_matrix",
        "implementation_sequence": "production_disruption_minimization",
        "roi_estimation": "manufacturing_operational_benefits", 
        "compliance_risk_assessment": "regulatory_impact_analysis"
    }
}

# 製造業特化効率性分析フレームワーク
manufacturing_efficiency_analysis = {
    "production_database_performance": {
        "work_order_optimization": {
            "query_execution_plans": "optimize_production_queries",
            "index_strategies": "manufacturing_multi_column_indexes",
            "partitioning": "time_based_production_partitioning",
            "materialized_views": "production_kpi_acceleration"
        },
        
        "batch_traceability_optimization": {
            "genealogy_queries": "optimize_batch_genealogy_tracking",
            "lot_tracking": "efficient_lot_number_indexing",
            "material_consumption": "optimize_material_usage_queries",
            "yield_calculations": "production_yield_aggregations"
        }
    },
    
    "real_time_manufacturing_integration": {
        "iot_data_processing": {
            "sensor_data_ingestion": "high_throughput_sensor_processing",
            "time_series_optimization": "manufacturing_time_series_storage",
            "real_time_alerts": "manufacturing_alert_engine_optimization",
            "dashboard_performance": "real_time_manufacturing_dashboards"
        },
        
        "manufacturing_scaling_strategies": {
            "horizontal_scaling": "multi_plant_database_setup",
            "load_balancing": "manufacturing_workload_distribution",
            "caching_layers": "production_data_caching_strategy",
            "connection_pooling": "manufacturing_connection_optimization"
        }
    }
}
```

#### 製造業PostgreSQL + SQLAlchemy効率性分析
```python
# 統合製造業効率性分析フレームワーク
integrated_manufacturing_efficiency = {
    "sqlalchemy_performance": {
        "orm_optimization": {
            "eager_loading": "manufacturing_relationship_optimization",
            "query_batching": "bulk_manufacturing_operations",
            "connection_pooling": "async_manufacturing_connections",
            "session_management": "manufacturing_transaction_scope"
        },
        
        "manufacturing_model_optimization": {
            "inheritance_strategies": "manufacturing_entity_hierarchies",
            "polymorphic_queries": "product_variant_optimization",
            "lazy_loading": "manufacturing_data_access_patterns",
            "bulk_operations": "batch_manufacturing_updates"
        }  
    },
    
    "postgresql_manufacturing_features": {
        "time_series_data": {
            "timescaledb_integration": "manufacturing_sensor_data_optimization",
            "continuous_aggregates": "production_kpi_calculations",
            "data_retention": "manufacturing_data_lifecycle_management",
            "compression": "historical_manufacturing_data_storage"
        },
        
        "advanced_indexing": {
            "partial_indexes": "manufacturing_conditional_indexes",
            "expression_indexes": "calculated_manufacturing_metrics",
            "gin_gist_indexes": "manufacturing_full_text_search",
            "bloom_filters": "manufacturing_data_filtering"
        }
    }
}
```

### 2. o3 MCP - 製造業データベーススペシャリスト連携

#### 製造業PostgreSQL高度設計検証
```sql
-- o3 MCP 製造業データベース最適化検証クエリ

-- 1. 製造業PostgreSQLパフォーマンス詳細分析
WITH manufacturing_query_performance AS (
    SELECT 
        query,
        calls,
        total_time,
        mean_time,
        max_time,
        stddev_time,
        rows,
        100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent,
        CASE 
            WHEN query ILIKE '%work_orders%' THEN 'Production Management'
            WHEN query ILIKE '%quality_checks%' THEN 'Quality Control'
            WHEN query ILIKE '%batch_records%' THEN 'Batch Processing'
            WHEN query ILIKE '%equipment_data%' THEN 'Equipment Monitoring'
            ELSE 'Other'
        END AS manufacturing_category
    FROM pg_stat_statements 
    WHERE calls > 50 AND query NOT ILIKE '%pg_%'
    ORDER BY total_time DESC
    LIMIT 30
),
manufacturing_index_efficiency AS (
    SELECT 
        schemaname,
        tablename,
        indexname,
        idx_tup_read,
        idx_tup_fetch,
        CASE 
            WHEN idx_tup_read > 0 
            THEN round((idx_tup_fetch::numeric / idx_tup_read) * 100, 2)
            ELSE 0
        END as efficiency_percent,
        pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
        CASE 
            WHEN tablename IN ('work_orders', 'batch_records', 'quality_checks') 
            THEN 'Critical Manufacturing Table'
            ELSE 'Standard Table'
        END as manufacturing_priority
    FROM pg_stat_user_indexes
    WHERE idx_tup_read > 100
    ORDER BY efficiency_percent DESC
)
SELECT 
    'Manufacturing Query Performance Analysis' as analysis_type,
    json_agg(manufacturing_query_performance.*) as query_data
FROM manufacturing_query_performance
UNION ALL
SELECT 
    'Manufacturing Index Efficiency Analysis' as analysis_type,
    json_agg(manufacturing_index_efficiency.*) as index_data  
FROM manufacturing_index_efficiency;

-- 2. 製造業リアルタイムデータ処理分析
WITH manufacturing_real_time_stats AS (
    SELECT 
        table_name,
        operation_type,
        COUNT(*) as operation_count,
        AVG(processing_time_ms) as avg_processing_time,
        MAX(processing_time_ms) as max_processing_time,
        AVG(affected_rows) as avg_affected_rows,
        CASE 
            WHEN table_name = 'sensor_data' THEN 'IoT Data Stream'
            WHEN table_name = 'production_events' THEN 'Production Events'
            WHEN table_name = 'quality_measurements' THEN 'Quality Data'
            WHEN table_name = 'equipment_status' THEN 'Equipment Monitoring'
            ELSE 'Other Manufacturing Data'
        END as data_category
    FROM manufacturing_operations_log
    WHERE created_at >= NOW() - INTERVAL '24 hours'
    GROUP BY table_name, operation_type
),
manufacturing_connection_analysis AS (
    SELECT 
        DATE_TRUNC('hour', connected_at) as hour_bucket,
        COUNT(*) as concurrent_connections,
        AVG(session_duration_ms) as avg_session_duration,
        COUNT(*) FILTER (WHERE application_name LIKE '%production%') as production_connections,
        COUNT(*) FILTER (WHERE application_name LIKE '%quality%') as quality_connections,
        COUNT(*) FILTER (WHERE application_name LIKE '%maintenance%') as maintenance_connections
    FROM pg_stat_activity_history
    WHERE connected_at >= NOW() - INTERVAL '7 days'
    GROUP BY hour_bucket
    ORDER BY hour_bucket
)
SELECT 
    'manufacturing_real_time_performance' as metric_type,
    json_build_object(
        'operation_statistics', (SELECT json_agg(manufacturing_real_time_stats.*) FROM manufacturing_real_time_stats),
        'connection_patterns', (SELECT json_agg(manufacturing_connection_analysis.*) FROM manufacturing_connection_analysis)
    ) as metrics;

-- 3. 製造業監査・コンプライアンス効率性検証
WITH manufacturing_audit_performance AS (
    SELECT 
        table_name,
        audit_operation,
        COUNT(*) as audit_count,
        AVG(audit_processing_time_ms) as avg_audit_time,
        MAX(audit_processing_time_ms) as max_audit_time,
        AVG(audit_payload_size_bytes) as avg_payload_size,
        COUNT(*) FILTER (WHERE compliance_flags ? 'iso9001') as iso9001_entries,
        COUNT(*) FILTER (WHERE compliance_flags ? 'fda21cfr') as fda_entries
    FROM manufacturing_audit_log
    WHERE created_at >= NOW() - INTERVAL '24 hours'
    GROUP BY table_name, audit_operation
    HAVING COUNT(*) > 10
    ORDER BY avg_audit_time DESC
),
manufacturing_data_integrity AS (
    SELECT 
        table_name,
        COUNT(*) as total_records,
        COUNT(*) FILTER (WHERE data_integrity_hash IS NOT NULL) as hash_protected_records,
        COUNT(*) FILTER (WHERE electronic_signature IS NOT NULL) as signed_records,
        COUNT(*) FILTER (WHERE created_at != updated_at) as modified_records,
        round(
            (COUNT(*) FILTER (WHERE data_integrity_hash IS NOT NULL)::numeric / COUNT(*)) * 100, 
            2
        ) as integrity_coverage_percent
    FROM manufacturing_critical_tables_view
    WHERE table_name IN ('work_orders', 'batch_records', 'quality_checks', 'change_controls')
    GROUP BY table_name
)
SELECT 
    'manufacturing_audit_compliance' as analysis_type,
    json_build_object(
        'audit_performance', (SELECT json_agg(manufacturing_audit_performance.*) FROM manufacturing_audit_performance),
        'data_integrity_metrics', (SELECT json_agg(manufacturing_data_integrity.*) FROM manufacturing_data_integrity)
    ) as compliance_metrics;
```

#### 製造業高度データベース機能実装戦略
```python
# o3 MCP 製造業データベース最適化戦略
manufacturing_db_optimization_strategy = {
    "advanced_postgresql_features": {
        "time_series_optimization": {
            "use_case": "IoT sensor data and production metrics storage",
            "implementation": "TimescaleDB extension for manufacturing time-series",
            "benefit": "90% compression ratio, 10x query performance",
            "expected_improvement": "Real-time manufacturing analytics capability"
        },
        
        "manufacturing_partitioning": {
            "use_case": "Large manufacturing tables (work_orders, batch_records)",
            "implementation": "Time-based and facility-based partitioning",
            "benefit": "Query performance improvement, maintenance optimization",
            "expected_improvement": "70% query time reduction for historical data"
        },
        
        "manufacturing_materialized_views": {
            "use_case": "Complex manufacturing KPI calculations",
            "implementation": "Production dashboard aggregations, OEE calculations",
            "benefit": "Sub-second dashboard response times",
            "expected_improvement": "95% reduction in dashboard load times"
        }
    },
    
    "manufacturing_data_integrity": {
        "cryptographic_hashing": {
            "implementation": "SHA-256 hashing for critical manufacturing records",
            "compliance_benefit": "FDA 21 CFR Part 11 electronic records integrity",
            "expected_improvement": "Tamper-evident manufacturing records"
        },
        
        "electronic_signatures": {
            "implementation": "Digital signatures for critical manufacturing operations",
            "compliance_benefit": "ISO 9001:2015 document control compliance",
            "expected_improvement": "Non-repudiation for manufacturing decisions"
        },
        
        "audit_trail_optimization": {
            "implementation": "Efficient trigger-based audit logging",
            "performance_benefit": "Minimal overhead audit trail generation",
            "expected_improvement": "Complete audit trail with <5% performance impact"
        }
    },
    
    "manufacturing_performance_optimization": {
        "connection_pooling": {
            "implementation": "PgBouncer with manufacturing-optimized settings",
            "benefit": "Efficient connection management for production systems",
            "expected_improvement": "Support 1000+ concurrent manufacturing users"
        },
        
        "manufacturing_caching": {
            "implementation": "Redis for manufacturing data caching strategies",
            "benefit": "Fast access to frequently used manufacturing data",
            "expected_improvement": "80% reduction in repeated query execution"
        },
        
        "bulk_operations": {
            "implementation": "Optimized bulk insert/update for manufacturing data",
            "benefit": "Efficient batch processing for production data ingestion",
            "expected_improvement": "100x improvement in batch data processing"
        }
    }
}
```

## 生成される成果物

### 1. 製造業データベース最適化分析レポート

```json
{
  "manufacturing_database_optimization_analysis": {
    "report_id": "mfg_db_opt_20250129_103000",
    "analysis_period": "2025-01-22T00:00:00Z to 2025-01-29T10:30:00Z",
    "manufacturing_facility": "Plant_A_Production_Line_1_2_3",
    "ai_collaboration_metrics": {
      "gemini_cli": {
        "manufacturing_data_patterns_analyzed": 2500000,
        "production_optimization_opportunities": 35,
        "quality_control_insights": 28,
        "equipment_performance_predictions": 15
      },
      "o3_mcp": {
        "database_optimizations": 42,
        "manufacturing_architecture_validations": 18,
        "compliance_enhancements": 23,
        "performance_improvements": 31
      },
      "claude_code": {
        "sqlalchemy_integration_improvements": 26,
        "manufacturing_code_optimizations": 34,
        "api_performance_plans": 19
      }
    },
    
    "manufacturing_performance_analysis": {
      "production_database_performance": {
        "work_order_queries": {
          "average_response_time_ms": 25,
          "p95_response_time_ms": 85,
          "p99_response_time_ms": 180,
          "slow_queries_count": 3,
          "optimization_potential": "45% improvement available"
        },
        "batch_traceability_performance": {
          "genealogy_query_time_ms": 150,
          "lot_tracking_efficiency": 0.78,
          "material_consumption_queries_ms": 95,
          "traceability_index_utilization": 0.85
        },
        "quality_control_data": {
          "spc_calculation_time_ms": 45,
          "quality_test_result_queries_ms": 35,
          "deviation_analysis_time_ms": 220,
          "quality_report_generation_s": 12
        }
      },
      
      "real_time_manufacturing_performance": {
        "iot_data_ingestion": {
          "sensor_data_throughput": "50,000 points/second",
          "ingestion_latency_ms": 15,
          "data_loss_rate": 0.001,
          "storage_efficiency": "compression_ratio_8_to_1"
        },
        "production_monitoring": {
          "real_time_oee_calculation_ms": 200,
          "equipment_status_updates_ms": 50,
          "production_alert_latency_ms": 100,
          "dashboard_refresh_rate_ms": 500
        }
      },
      
      "audit_compliance_performance": {
        "audit_trail_generation": {
          "audit_log_write_time_ms": 8,
          "audit_completeness": 0.999,
          "electronic_signature_verification_ms": 25,
          "compliance_report_generation_s": 45
        },
        "regulatory_reporting": {
          "iso9001_report_generation_s": 180,
          "fda_batch_record_compilation_s": 300,
          "change_control_documentation_s": 120,
          "audit_readiness_score": 0.96
        }
      }
    },
    
    "manufacturing_optimization_recommendations": {
      "immediate_implementation": [
        {
          "optimization": "work_order_index_optimization",
          "priority": 1,
          "expected_benefit": "45% query performance improvement",
          "manufacturing_impact": "Faster production planning and execution",
          "implementation_effort": "1 day",
          "downtime_required": "5 minutes maintenance window"
        },
        {
          "optimization": "batch_traceability_materialized_views",
          "priority": 2,
          "expected_benefit": "70% traceability query improvement", 
          "manufacturing_impact": "Instant batch genealogy reports",
          "implementation_effort": "2 days",
          "downtime_required": "None - online implementation"
        },
        {
          "optimization": "iot_data_partitioning",
          "priority": 3,
          "expected_benefit": "80% historical data query improvement",
          "manufacturing_impact": "Fast equipment performance analysis",
          "implementation_effort": "1 week",
          "downtime_required": "Weekend maintenance window"
        }
      ],
      
      "medium_term_implementation": [
        {
          "optimization": "manufacturing_connection_pooling",
          "priority": 4,
          "expected_benefit": "Support 500+ concurrent manufacturing users",
          "manufacturing_impact": "Scale to multiple shifts and departments",
          "implementation_effort": "1-2 weeks",
          "compliance_benefit": "No audit trail impact"
        },
        {
          "optimization": "advanced_audit_optimization",
          "priority": 5,
          "expected_benefit": "50% audit log performance improvement",
          "manufacturing_impact": "Faster regulatory reporting",
          "implementation_effort": "2-3 weeks",
          "compliance_benefit": "Enhanced 21 CFR Part 11 compliance"
        }
      ]
    }
  }
}
```

### 2. 製造業SQLAlchemy最適化テンプレート

```python
# manufacturing_optimized_models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy import Index
import uuid
from datetime import datetime
from typing import Optional, List

Base = declarative_base()

class OptimizedWorkOrder(Base):
    """o3 MCP最適化設計による作業指示書モデル"""
    __tablename__ = "work_orders"
    
    # 主キー - UUID for manufacturing traceability
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # 製造業関連外部キー - 最適化されたインデックス
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    production_line_id = Column(UUID(as_uuid=True), ForeignKey("production_lines.id"), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True)
    
    # 製造業データ - 最適化された型定義
    planned_quantity = Column(Numeric(12, 4), nullable=False)
    actual_quantity = Column(Numeric(12, 4), nullable=True)
    uom = Column(String(10), nullable=False)  # Unit of Measure
    
    # ステータス管理 - 製造業ワークフロー最適化
    status = Column(String(20), nullable=False, default='created', index=True)
    priority = Column(String(10), nullable=False, default='normal')
    
    # 時間管理 - 製造業スケジューリング最適化
    scheduled_start = Column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    
    # 監査・コンプライアンス - 製造業規制対応
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 電子署名・データ整合性 - FDA 21 CFR Part 11対応
    electronic_signature = Column(JSONB, nullable=True)
    data_integrity_hash = Column(String(64), nullable=True)  # SHA-256
    version = Column(Integer, nullable=False, default=1)
    
    # 製造業メタデータ
    manufacturing_parameters = Column(JSONB, nullable=True)
    quality_requirements = Column(JSONB, nullable=True)
    special_instructions = Column(Text, nullable=True)
    
    # リレーションシップ - 最適化されたeager loading
    product = relationship("Product", back_populates="work_orders", lazy="select")
    production_line = relationship("ProductionLine", back_populates="work_orders", lazy="select")
    batch = relationship("Batch", back_populates="work_orders", lazy="select")
    quality_checks = relationship("QualityCheck", back_populates="work_order", lazy="dynamic")
    material_consumptions = relationship("MaterialConsumption", back_populates="work_order", lazy="dynamic")
    
    # 製造業最適化インデックス - o3 MCP分析結果
    __table_args__ = (
        # 複合インデックス - 製造業クエリパターン最適化
        Index('ix_work_orders_status_priority', 'status', 'priority'),
        Index('ix_work_orders_scheduled_dates', 'scheduled_start', 'scheduled_end'),
        Index('ix_work_orders_production_line_status', 'production_line_id', 'status'),
        Index('ix_work_orders_batch_traceability', 'batch_id', 'product_id'),
        
        # 部分インデックス - パフォーマンス最適化
        Index('ix_work_orders_active', 'status', postgresql_where=(status.in_(['planned', 'released', 'in_progress']))),
        Index('ix_work_orders_current_date', 'scheduled_start', postgresql_where=(scheduled_start >= func.current_date())),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        """製造業ステータス検証"""
        valid_statuses = ['created', 'planned', 'released', 'in_progress', 'completed', 'cancelled', 'on_hold']
        if status not in valid_statuses:
            raise ValueError(f"Invalid work order status: {status}")
        return status
    
    @validates('planned_quantity', 'actual_quantity')
    def validate_quantities(self, key, quantity):
        """製造業数量検証"""
        if quantity is not None and quantity <= 0:
            raise ValueError(f"Manufacturing quantity must be positive: {quantity}")
        return quantity
    
    def calculate_oee_metrics(self) -> dict:
        """OEE計算 - 製造業KPI"""
        if not (self.actual_start and self.actual_end and self.scheduled_start and self.scheduled_end):
            return {}
        
        # 可用性 (Availability)
        planned_time = (self.scheduled_end - self.scheduled_start).total_seconds()
        actual_time = (self.actual_end - self.actual_start).total_seconds()
        availability = (actual_time / planned_time) * 100 if planned_time > 0 else 0
        
        # 性能率 (Performance)
        performance = (float(self.actual_quantity or 0) / float(self.planned_quantity)) * 100 if self.planned_quantity > 0 else 0
        
        # 品質率は関連する品質チェックから計算
        quality_rate = self.calculate_quality_rate()
        
        # OEE = 可用性 × 性能率 × 品質率
        oee = (availability * performance * quality_rate) / 10000  # Convert to percentage
        
        return {
            'availability': round(availability, 2),
            'performance': round(performance, 2),
            'quality': round(quality_rate, 2),
            'oee': round(oee, 2)
        }
    
    def calculate_quality_rate(self) -> float:
        """品質率計算"""
        # 関連する品質チェックから良品率を計算
        quality_checks = self.quality_checks.all()
        if not quality_checks:
            return 100.0  # 品質チェックがない場合は100%とする
        
        passed_checks = sum(1 for qc in quality_checks if qc.result == 'pass')
        total_checks = len(quality_checks)
        
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 100.0
    
    def generate_data_integrity_hash(self) -> str:
        """データ整合性ハッシュ生成 - FDA 21 CFR Part 11対応"""
        import hashlib
        
        # 重要なデータフィールドからハッシュを生成
        hash_data = f"{self.work_order_number}|{self.product_id}|{self.planned_quantity}|{self.status}|{self.created_at}"
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def __repr__(self):
        return f"<OptimizedWorkOrder(work_order_number='{self.work_order_number}', status='{self.status}')>"

# 製造業最適化されたリポジトリパターン
class OptimizedWorkOrderRepository:
    """製造業最適化作業指示書リポジトリ"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def find_active_work_orders_optimized(
        self, 
        production_line_id: Optional[UUID] = None,
        status_filter: Optional[List[str]] = None
    ) -> List[OptimizedWorkOrder]:
        """最適化されたアクティブ作業指示書検索"""
        
        # o3 MCP最適化クエリ - インデックス活用
        query = self.db.query(OptimizedWorkOrder)
        
        # 部分インデックス活用
        if not status_filter:
            status_filter = ['planned', 'released', 'in_progress']
        
        query = query.filter(OptimizedWorkOrder.status.in_(status_filter))
        
        if production_line_id:
            # 複合インデックス活用
            query = query.filter(OptimizedWorkOrder.production_line_id == production_line_id)
        
        # 現在日付の部分インデックス活用
        query = query.filter(OptimizedWorkOrder.scheduled_start >= func.current_date())
        
        # eager loading最適化
        query = query.options(
            selectinload(OptimizedWorkOrder.product),
            selectinload(OptimizedWorkOrder.production_line)
        )
        
        return await query.all()
    
    async def get_production_kpi_materialized(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> dict:
        """製造業KPI - マテリアライズドビュー活用"""
        
        # o3 MCP設計のマテリアライズドビューを使用
        result = await self.db.execute(
            text("""
                SELECT 
                    production_line_id,
                    total_work_orders,
                    completed_work_orders,
                    avg_oee,
                    total_quantity_produced,
                    quality_rate,
                    on_time_delivery_rate
                FROM mv_production_kpi_daily 
                WHERE report_date BETWEEN :start_date AND :end_date
                ORDER BY report_date DESC, production_line_id
            """),
            {"start_date": start_date, "end_date": end_date}
        )
        
        return [dict(row) for row in result.fetchall()]
```

### 3. 製造業データベース最適化スクリプト

```sql
-- manufacturing_database_optimization.sql
-- o3 MCP データベーススペシャリスト設計による製造業最適化

-- 1. 製造業TimeScaleDB拡張 - IoTデータ最適化
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- IoTセンサーデータ用ハイパーテーブル
CREATE TABLE IF NOT EXISTS sensor_data (
    time TIMESTAMPTZ NOT NULL,
    equipment_id UUID NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    sensor_value NUMERIC(12,4) NOT NULL,
    unit_of_measure VARCHAR(10) NOT NULL,
    quality_flag VARCHAR(10) DEFAULT 'good',
    data_source VARCHAR(50) NOT NULL,
    CONSTRAINT pk_sensor_data PRIMARY KEY (time, equipment_id, sensor_type)
);

-- ハイパーテーブル化 - 時系列データ最適化
SELECT create_hypertable('sensor_data', 'time', if_not_exists => TRUE);

-- 連続集約 - 製造業KPI計算最適化
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_equipment_hourly_stats
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    equipment_id,
    sensor_type,
    AVG(sensor_value) as avg_value,
    MIN(sensor_value) as min_value,
    MAX(sensor_value) as max_value,
    COUNT(*) as data_points,
    COUNT(*) FILTER (WHERE quality_flag = 'good') as good_data_points
FROM sensor_data
GROUP BY bucket, equipment_id, sensor_type;

-- 自動リフレッシュポリシー
SELECT add_continuous_aggregate_policy('mv_equipment_hourly_stats',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '10 minutes',
    schedule_interval => INTERVAL '10 minutes',
    if_not_exists => TRUE);

-- 2. 製造業最適化インデックス戦略
-- 作業指示書複合インデックス - Gemini CLI分析結果
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_work_orders_production_scheduling
  ON work_orders (production_line_id, scheduled_start, status)
  WHERE status IN ('planned', 'released', 'in_progress');

-- バッチトレーサビリティ最適化インデックス
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_batch_genealogy_optimized
  ON material_consumptions (batch_id, work_order_id, material_id)
  INCLUDE (consumed_quantity, consumption_timestamp);

-- 品質管理高速検索インデックス
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_quality_checks_efficient
  ON quality_checks (work_order_id, test_type, result, performed_at DESC)
  WHERE result IS NOT NULL;

-- 3. 製造業マテリアライズドビュー - ダッシュボード最適化
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_production_kpi_daily AS
SELECT 
    DATE(wo.scheduled_start) as report_date,
    wo.production_line_id,
    pl.line_name,
    COUNT(*) as total_work_orders,
    COUNT(*) FILTER (WHERE wo.status = 'completed') as completed_work_orders,
    COUNT(*) FILTER (WHERE wo.actual_end <= wo.scheduled_end) as on_time_completions,
    SUM(wo.actual_quantity) as total_quantity_produced,
    AVG(
        CASE 
            WHEN wo.planned_quantity > 0 
            THEN (wo.actual_quantity / wo.planned_quantity) * 100 
            ELSE NULL 
        END
    ) as avg_yield_percentage,
    AVG(
        CASE 
            WHEN wo.actual_start IS NOT NULL AND wo.actual_end IS NOT NULL
            THEN EXTRACT(EPOCH FROM (wo.actual_end - wo.actual_start))/3600
            ELSE NULL
        END
    ) as avg_processing_hours,
    -- OEE計算（簡略版）
    AVG(
        CASE 
            WHEN wo.status = 'completed' AND wo.scheduled_end > wo.scheduled_start AND wo.planned_quantity > 0
            THEN (
                (EXTRACT(EPOCH FROM (wo.actual_end - wo.actual_start)) / 
                 EXTRACT(EPOCH FROM (wo.scheduled_end - wo.scheduled_start))) *
                (wo.actual_quantity / wo.planned_quantity) *
                -- 簡略品質率（実際は品質チェックテーブルから計算）
                0.98
            ) * 100
            ELSE NULL
        END
    ) as estimated_oee
FROM work_orders wo
JOIN production_lines pl ON wo.production_line_id = pl.id
WHERE wo.scheduled_start >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(wo.scheduled_start), wo.production_line_id, pl.line_name;

-- マテリアライズドビューの一意インデックス
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_production_kpi_daily_unique
  ON mv_production_kpi_daily (report_date, production_line_id);

-- 自動リフレッシュ関数
CREATE OR REPLACE FUNCTION refresh_production_kpi_daily()
RETURNS TRIGGER AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_production_kpi_daily;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- トリガー設定 - 作業指示書更新時に自動リフレッシュ
CREATE TRIGGER trigger_refresh_production_kpi
  AFTER INSERT OR UPDATE OR DELETE ON work_orders
  FOR EACH STATEMENT
  EXECUTE FUNCTION refresh_production_kpi_daily();

-- 4. 製造業監査・コンプライアンス最適化
-- 監査ログ専用テーブル - パフォーマンス最適化
CREATE TABLE IF NOT EXISTS manufacturing_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation_type VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    user_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    old_values JSONB,
    new_values JSONB,
    change_reason TEXT,
    electronic_signature JSONB,
    compliance_flags JSONB, -- ISO, FDA, etc.
    data_integrity_hash VARCHAR(64) NOT NULL
);

-- 監査ログ用インデックス - 高速検索
CREATE INDEX IF NOT EXISTS idx_audit_log_table_record
  ON manufacturing_audit_log (table_name, record_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_user_timestamp
  ON manufacturing_audit_log (user_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_compliance
  ON manufacturing_audit_log USING GIN (compliance_flags);

-- 監査ログパーティショニング - 長期間データ管理
CREATE TABLE IF NOT EXISTS manufacturing_audit_log_y2025m01 
  PARTITION OF manufacturing_audit_log
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- 5. 製造業パフォーマンス最適化設定
-- PgBouncer設定最適化（設定ファイル用コメント）
/*
# /etc/pgbouncer/pgbouncer.ini - 製造業最適化設定
[databases]
manufacturing_prod = host=localhost port=5432 dbname=manufacturing_db user=mfg_app

[pgbouncer]
# 製造業同時接続最適化
pool_mode = session
max_client_conn = 1000
default_pool_size = 25
max_db_connections = 100

# 製造業アプリケーション特性に合わせた調整
server_reset_query = DISCARD ALL
server_check_query = SELECT 1
server_idle_timeout = 600
query_timeout = 300

# 製造業監査ログ
log_connections = 1
log_disconnections = 1
*/

-- PostgreSQL設定最適化（postgresql.conf用）
-- 製造業ワークロード特性に合わせた設定推奨値
/*
# 製造業データベース最適化設定
shared_buffers = '2GB'                    # 製造業データ用メモリ
effective_cache_size = '6GB'              # システム全体キャッシュ
work_mem = '64MB'                         # 製造業集計クエリ用
maintenance_work_mem = '512MB'            # インデックス・バキューム用

# 製造業リアルタイムデータ処理
wal_buffers = '64MB'                      # WALバッファ最適化
checkpoint_completion_target = 0.9        # チェックポイント最適化
random_page_cost = 1.1                    # SSD環境最適化

# 製造業監査・ログ設定
log_statement = 'mod'                     # 変更系クエリをログ
log_min_duration_statement = 1000         # 1秒以上のクエリをログ
log_checkpoints = on                      # チェックポイントログ
log_connections = on                      # 接続ログ
log_disconnections = on                   # 切断ログ

# 製造業時系列データ最適化
timezone = 'UTC'                          # タイムゾーン統一
datestyle = 'ISO, YMD'                    # 日付形式統一
*/
```

## 実行例

```bash
# マルチAI協調による製造業データベース全機能最適化
/database-optimize full-system --multi-ai-manufacturing-report --performance-target=95 --compliance-level=fda21cfr

# 出力ファイル:
# analysis/manufacturing_database_optimization_analysis_20250129.json
# sql/manufacturing_database_optimization_scripts.sql
# reports/multi_ai_manufacturing_database_recommendations.md
# monitoring/manufacturing_database_performance_dashboard.html
# compliance/manufacturing_audit_optimization_report.md
```

## まとめ

このコマンドにより、マルチAI協調による次世代製造業データベースシステムの最適化が可能になります：

1. **製造業特化最適化**: 生産管理・品質管理・設備管理に特化したデータベース最適化
2. **規制コンプライアンス**: ISO 9001、FDA 21 CFR Part 11等の製造業規制に完全対応
3. **マルチAI協調**: Gemini CLI、o3 MCP、Claude Codeの専門性を活用した統合最適化
4. **リアルタイム処理**: IoTデータ・生産データのリアルタイム処理最適化
5. **監査・トレーサビリティ**: 完全な監査証跡と製造業トレーサビリティ要求への対応
6. **パフォーマンス向上**: 製造業特有のクエリパターンに最適化された高性能データベース

製造業特有の複雑なデータ要求と規制要求に対応した包括的データベース最適化により、安全で効率的な製造業システムを実現します。