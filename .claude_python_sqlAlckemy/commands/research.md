# Research Command - 製造業データ分析・業務調査

## 目的
FastAPI + SQLAlchemy製造業システムのデータアナリスト/リサーチャーとして、製造業特有の大規模データ処理と製造業務分析を実行します。生産データ・品質データ・設備データの統合分析により、製造業務最適化・改善提案を実現します。

## 対象AI
- **Gemini CLI**: 製造業大規模データ処理、製造業複雑パターン認識、製造業マルチモーダル対応能力を活用

## 使用方法
```
/research [調査タイプ] [データソース] [分析深度] [期間]
```

### パラメータ
- `RESEARCH_TYPE`: production_analysis, quality_analysis, equipment_analysis, inventory_analysis, performance_metrics, manufacturing_process_optimization
- `DATA_SOURCE`: production_data, quality_data, equipment_sensors, inventory_data, operator_feedback, maintenance_logs
- `ANALYSIS_DEPTH`: basic, detailed, comprehensive, predictive_modeling
- `TIME_PERIOD`: shift, daily, weekly, monthly, quarterly, annual

## 実行プロセス

### 1. 製造業データ収集・前処理

#### 1.1 製造業データソース特定
```python
# 製造業データソース体系
manufacturing_data_sources = {
    'production_data': {
        'sources': [
            'MES (Manufacturing Execution System)',
            'SCADA (Supervisory Control and Data Acquisition)',
            'PLC (Programmable Logic Controller)',
            'Work Order Management System',
            'Production Planning System'
        ],
        'data_types': [
            'Production Volume (units/hour)',
            'Cycle Time (seconds/unit)',
            'First Pass Yield (%)',
            'Overall Equipment Effectiveness (OEE)',
            'Throughput Rate'
        ],
        'collection_frequency': 'Real-time to Hourly'
    },
    
    'quality_data': {
        'sources': [
            'QMS (Quality Management System)',
            'SPC (Statistical Process Control) Tools',
            'Inspection Equipment',
            'Laboratory Information System (LIMS)',
            'Customer Complaint System'
        ],
        'data_types': [
            'Defect Rate (PPM)',
            'Quality Control Test Results',
            'Customer Complaints',
            'Audit Scores',
            'Cost of Quality'
        ],
        'collection_frequency': 'Per batch/lot to Daily'
    },
    
    'equipment_data': {
        'sources': [
            'CMMS (Computerized Maintenance Management)',
            'IoT Sensors (Temperature, Vibration, Pressure)',
            'Energy Management Systems',
            'Condition Monitoring Systems',
            'Maintenance Work Orders'
        ],
        'data_types': [
            'Equipment Uptime (%)',
            'Mean Time Between Failures (MTBF)',
            'Mean Time To Repair (MTTR)',
            'Energy Consumption (kWh)',
            'Maintenance Costs'
        ],
        'collection_frequency': 'Continuous to Weekly'
    },
    
    'inventory_data': {
        'sources': [
            'ERP (Enterprise Resource Planning)',
            'Warehouse Management System (WMS)',
            'Supplier Systems',
            'Inventory Tracking Systems',
            'Purchase Order Systems'
        ],
        'data_types': [
            'Inventory Levels',
            'Inventory Turnover Rate',
            'Stockout Frequency',
            'Supplier Lead Times',
            'Carrying Costs'
        ],
        'collection_frequency': 'Daily to Weekly'
    }
}

# 製造業マルチモーダルデータ処理
async def process_manufacturing_multimodal_data():
    return {
        'numerical_data': await process_sensor_data(),
        'time_series_data': await process_production_trends(),
        'categorical_data': await process_quality_classifications(),
        'image_data': await process_visual_inspections(),
        'text_data': await process_operator_logs(),
        'video_data': await process_production_recordings()
    }
```

#### 1.2 製造業データクリーニング・正規化
```python
# 製造業特化データクリーニング
manufacturing_data_cleaning = {
    'sensor_data_cleaning': {
        'outlier_detection': 'Remove sensor values beyond physical limits',
        'noise_filtering': 'Apply low-pass filters to sensor signals',
        'drift_correction': 'Correct sensor drift over time',
        'missing_value_handling': 'Interpolate missing sensor readings'
    },
    
    'production_data_cleaning': {
        'shift_boundary_handling': 'Align data to production shift boundaries',
        'product_variant_normalization': 'Standardize across product types',
        'downtime_categorization': 'Classify planned vs unplanned downtime',
        'batch_consistency_check': 'Validate batch/lot data integrity'
    },
    
    'quality_data_cleaning': {
        'measurement_standardization': 'Convert to standard units',
        'inspection_result_validation': 'Verify against specifications',
        'defect_classification_mapping': 'Map to standard defect categories',
        'customer_feedback_processing': 'Extract actionable quality issues'
    }
}
```

### 2. 製造業分析実行

#### 2.1 製造業探索的データ分析（EDA）
```python
# 製造業特化EDA
manufacturing_eda_framework = {
    'production_analysis': {
        'oee_analysis': 'Calculate and trend Overall Equipment Effectiveness',
        'bottleneck_identification': 'Identify production constraints',
        'capacity_utilization': 'Analyze equipment and line utilization',
        'production_variance': 'Analyze production volume variations'
    },
    
    'quality_analysis': {
        'spc_analysis': 'Statistical Process Control chart analysis',
        'pareto_analysis': 'Identify top quality issues',
        'correlation_analysis': 'Find quality-production correlations',
        'cost_of_quality': 'Analyze prevention, appraisal, failure costs'
    },
    
    'equipment_analysis': {
        'reliability_analysis': 'MTBF/MTTR trending and analysis',
        'maintenance_effectiveness': 'Analyze preventive vs corrective maintenance',
        'energy_efficiency': 'Energy consumption per unit analysis',
        'condition_monitoring': 'Predictive maintenance indicators'
    },
    
    'inventory_analysis': {
        'abc_analysis': 'Classify inventory by value and usage',
        'turnover_analysis': 'Inventory turnover rate optimization',
        'safety_stock_analysis': 'Optimize safety stock levels',
        'supplier_performance': 'Analyze supplier delivery and quality'
    }
}

# 製造業高度分析手法
async def apply_advanced_manufacturing_analytics():
    return {
        'time_series_forecasting': await forecast_production_demand(),
        'anomaly_detection': await detect_equipment_anomalies(),
        'root_cause_analysis': await analyze_quality_root_causes(),
        'optimization_modeling': await optimize_production_scheduling(),
        'predictive_maintenance': await predict_equipment_failures(),
        'six_sigma_analysis': await perform_dmaic_analysis()
    }
```

#### 2.2 製造業予測・最適化分析
```python
# 製造業予測分析モデル
manufacturing_predictive_models = {
    'demand_forecasting': {
        'models': ['ARIMA', 'Prophet', 'LSTM'],
        'inputs': ['Historical demand', 'Seasonal patterns', 'Economic indicators'],
        'outputs': ['Production demand forecast', 'Capacity requirements'],
        'accuracy_target': '95% confidence interval'
    },
    
    'quality_prediction': {
        'models': ['Random Forest', 'Gradient Boosting', 'Neural Networks'],
        'inputs': ['Process parameters', 'Environmental conditions', 'Material properties'],
        'outputs': ['Defect probability', 'Quality score prediction'],
        'accuracy_target': 'AUC > 0.85'
    },
    
    'maintenance_prediction': {
        'models': ['Survival Analysis', 'RUL (Remaining Useful Life)', 'Anomaly Detection'],
        'inputs': ['Sensor data', 'Maintenance history', 'Operating conditions'],
        'outputs': ['Failure probability', 'Optimal maintenance timing'],
        'accuracy_target': 'Precision > 80%, Recall > 90%'
    },
    
    'production_optimization': {
        'models': ['Linear Programming', 'Genetic Algorithm', 'Simulation'],
        'inputs': ['Capacity constraints', 'Demand forecast', 'Cost parameters'],
        'outputs': ['Optimal production schedule', 'Resource allocation'],
        'objective': 'Minimize cost while meeting demand'
    }
}
```

### 3. 製造業洞察抽出・改善提案

#### 3.1 製造業キーファインディング特定
```python
# 製造業重要発見事項の評価基準
manufacturing_key_findings_criteria = {
    'production_efficiency': {
        'impact_metrics': ['OEE improvement potential', 'Throughput increase', 'Cost reduction'],
        'threshold_values': {'high': '>10%', 'medium': '5-10%', 'low': '<5%'},
        'priority_factors': ['Production volume impact', 'Implementation difficulty', 'ROI']
    },
    
    'quality_improvement': {
        'impact_metrics': ['Defect rate reduction', 'Customer satisfaction', 'Cost of quality'],
        'threshold_values': {'high': '>25%', 'medium': '10-25%', 'low': '<10%'},
        'priority_factors': ['Customer impact', 'Regulatory compliance', 'Cost savings']
    },
    
    'equipment_optimization': {
        'impact_metrics': ['Uptime improvement', 'Maintenance cost reduction', 'Energy savings'],
        'threshold_values': {'high': '>20%', 'medium': '10-20%', 'low': '<10%'},
        'priority_factors': ['Safety impact', 'Capital investment required', 'Payback period']
    },
    
    'inventory_optimization': {
        'impact_metrics': ['Inventory cost reduction', 'Stockout reduction', 'Cash flow improvement'],
        'threshold_values': {'high': '>15%', 'medium': '8-15%', 'low': '<8%'},
        'priority_factors': ['Working capital impact', 'Service level impact', 'Implementation complexity']
    }
}

# 製造業アクションプラン策定
async def generate_manufacturing_action_plan(findings):
    return {
        'immediate_actions': await generate_quick_wins(findings),
        'short_term_improvements': await plan_short_term_projects(findings),
        'long_term_strategic_initiatives': await design_strategic_programs(findings),
        'resource_requirements': await estimate_implementation_resources(findings),
        'risk_mitigation': await assess_implementation_risks(findings)
    }
```

## 製造業調査タイプ別仕様

### 1. 生産分析（production_analysis）
```yaml
目的: 生産効率・OEE・ボトルネック分析による生産最適化
データ: MES、SCADA、PLC、生産計画、実績データ
分析手法:
  - OEE分析（稼働率・性能率・品質率）
  - ボトルネック分析（制約理論）
  - 生産能力分析
  - スループット最適化
出力:
  - 生産効率改善レポート
  - ボトルネック特定・改善提案
  - 生産能力最適化計画
  - OEE向上ロードマップ
```

### 2. 品質分析（quality_analysis）
```yaml
目的: 品質データ分析による品質改善・コスト削減
データ: QMS、SPC、検査結果、顧客クレーム、監査結果
分析手法:
  - 統計的工程管理（SPC）
  - パレート分析（品質問題の80/20分析）
  - 相関分析（品質要因分析）
  - 品質コスト分析
出力:
  - 品質改善優先順位リスト
  - 統計的工程管理実装計画
  - 品質コスト削減提案
  - 顧客満足度向上計画
```

### 3. 設備分析（equipment_analysis）
```yaml
目的: 設備効率・信頼性・保全最適化分析
データ: CMMS、IoTセンサー、保全履歴、故障データ
分析手法:
  - 信頼性解析（MTBF/MTTR）
  - 予知保全分析
  - エネルギー効率分析
  - 設備総合効率（OEE）分析
出力:
  - 予知保全実装計画
  - 設備効率改善提案
  - エネルギー最適化計画
  - 保全コスト削減提案
```

### 4. 在庫分析（inventory_analysis）
```yaml
目的: 在庫最適化・調達改善・キャッシュフロー最適化
データ: ERP、WMS、調達データ、需要予測
分析手法:
  - ABC分析（在庫重要度分類）
  - 需要予測・安全在庫最適化
  - サプライヤー分析
  - 在庫回転率分析
出力:
  - 在庫最適化計画
  - 調達戦略改善提案
  - サプライヤー評価・改善計画
  - キャッシュフロー改善計画
```

## 出力形式

### 製造業分析レポート（.tmp/manufacturing_research_report.md）
```markdown
# 製造業分析レポート: [分析タイプ]

## エグゼクティブサマリー

### 主要発見事項
1. **生産効率**: OEE 75% → 85% 向上可能（年間売上1.2億円増加見込み）
2. **品質改善**: 不良率 500PPM → 100PPM 削減可能（品質コスト30%削減）
3. **設備最適化**: 予知保全により計画外停止時間50%削減可能
4. **在庫最適化**: 在庫回転率4.2回 → 6.0回 改善により運転資本20%削減

### ビジネスインパクト評価
- **年間コスト削減効果**: 3.5億円
- **売上向上効果**: 1.2億円  
- **投資回収期間**: 18ヶ月
- **リスク評価**: 中程度（実装複雑性による）

### 推奨アクション（優先度順）
1. **高優先度**: ボトルネック設備の効率改善（6ヶ月、ROI 300%）
2. **中優先度**: 予知保全システム導入（12ヶ月、ROI 250%）
3. **中優先度**: 品質管理システム強化（9ヶ月、ROI 200%）

## 製造業分析概要

### 分析目的・背景
- **目的**: 製造効率20%向上・品質コスト30%削減の実現
- **背景**: 競合他社との収益性格差拡大、顧客品質要求レベル向上
- **スコープ**: 主力生産ライン3ライン、製品カテゴリA・B対象

### 製造業データソース・分析方法
- **生産データ**: MES（3ヶ月）、SCADA（リアルタイム）、PLC（24時間365日）
- **品質データ**: QMS（6ヶ月）、検査装置（全数検査）、顧客クレーム（1年）
- **設備データ**: CMMS（1年）、IoTセンサー（3ヶ月）、保全記録（2年）
- **分析期間**: 2024年1月-6月（6ヶ月間）

## 詳細分析結果

### 生産効率分析
#### 基本メトリクス
- **現在のOEE**: 75.2%（目標85%に対し9.8ポイント不足）
- **稼働率**: 82.1%（計画外停止が主要因）
- **性能率**: 91.6%（設備能力の91.6%で稼働）
- **品質率**: 99.9%（不良品による損失0.1%）

#### ボトルネック分析
1. **設備B-02**: 処理能力不足によりライン全体の75%効率制限
2. **材料供給**: 段取り時間平均45分（目標30分）
3. **検査工程**: 手動検査による待ち時間発生

### 品質管理分析
#### 品質メトリクス
- **不良率**: 485 PPM（目標100 PPM）
- **一発合格率**: 96.2%（目標98.5%）
- **顧客クレーム**: 月平均3.2件（目標1件以下）
- **品質コスト**: 売上の4.8%（業界平均2.5%）

#### 品質問題分析（パレート分析）
1. **寸法不良**: 35%（主要原因：設備精度劣化）
2. **表面欠陥**: 28%（主要原因：材料品質変動）
3. **機能不良**: 20%（主要原因：組立工程管理）

### 設備効率分析
#### 設備信頼性
- **MTBF**: 168時間（目標240時間）
- **MTTR**: 3.2時間（目標2時間以内）
- **計画外停止時間**: 月平均28時間（目標15時間以内）
- **保全コスト**: 年間1.2億円（売上の6.8%）

#### 予知保全可能性分析
- **振動異常検知精度**: 87%（現在の状態監視）
- **温度異常検知精度**: 92%（IoTセンサー活用）
- **予知保全実装効果予測**: 計画外停止50%削減可能

## 製造業洞察・改善提案

### パターン・トレンド解釈
1. **生産効率トレンド**: 朝シフトが最高効率（85%）、夜勤が最低（68%）
2. **品質季節変動**: 夏季に不良率20%増加（環境温度影響）
3. **設備劣化パターン**: 稼働時間2000時間超で故障率急増

### ビジネスへの影響分析
- **競合優位性**: 効率改善により製造原価15%削減→価格競争力向上
- **顧客満足度**: 品質向上により顧客満足度95%→98%向上見込み
- **従業員満足度**: 予知保全により緊急対応50%削減→労働環境改善

### 因果関係の考察
- **効率↔品質**: 過度の生産スピード向上は品質悪化リスク
- **保全↔効率**: 予防保全投資増により長期的効率向上
- **人材↔品質**: オペレータースキル向上が品質安定化に直結

## 推奨アクション

### 短期施策（1-3ヶ月）
1. **ボトルネック設備B-02の緊急改善**
   - 実施内容: 処理能力20%向上改造
   - 期待効果: ライン効率75%→82%向上
   - 投資額: 800万円、ROI: 6ヶ月
   
2. **段取り時間短縮プロジェクト**
   - 実施内容: SMED（シングル段取り）手法導入
   - 期待効果: 段取り時間45分→25分短縮
   - 投資額: 200万円、ROI: 4ヶ月

### 中期施策（3-6ヶ月）
1. **統計的工程管理（SPC）システム導入**
   - 実施内容: リアルタイム品質監視システム
   - 期待効果: 不良率485PPM→150PPM削減
   - 投資額: 1500万円、ROI: 12ヶ月

2. **IoT予知保全システム構築**
   - 実施内容: センサー増設・AI故障予測
   - 期待効果: 計画外停止50%削減
   - 投資額: 2500万円、ROI: 18ヶ月

### 長期戦略（6ヶ月-1年）
1. **スマートファクトリー化**
   - 実施内容: AI・IoT活用による自動最適化
   - 期待効果: OEE 85%→90%向上
   - 投資額: 5000万円、ROI: 24ヶ月

2. **品質保証体制革新**
   - 実施内容: 全自動検査システム・トレーサビリティ強化
   - 期待効果: 品質コスト4.8%→2.0%削減
   - 投資額: 3000万円、ROI: 30ヶ月

## 次のステップ

### 追加調査が必要な領域
- **競合ベンチマーク**: 同業他社のOEE・品質水準比較
- **最新技術調査**: Industry 4.0技術の適用可能性
- **サプライヤー分析**: 材料品質改善の可能性調査

### 監視指標の設定
- **日次**: OEE、不良率、計画外停止時間
- **週次**: 設備効率、エネルギー原単位、在庫回転率
- **月次**: 品質コスト、顧客満足度、改善提案実施率

### 効果測定方法
- **ベースライン設定**: 改善前6ヶ月平均を基準値
- **KPI監視**: ダッシュボードによるリアルタイム監視
- **ROI計算**: 投資対効果の四半期レビュー
- **改善効果検証**: 統計的有意性検定による効果確認
```

## TodoWrite連携

製造業調査・分析実行のタスクを自動生成：

```python
manufacturing_research_tasks = [
    {
        'id': 'manufacturing-research-001',
        'content': '製造業データソース調査・データ品質評価',
        'status': 'completed',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-research-002', 
        'content': '生産効率・OEE分析・ボトルネック特定',
        'status': 'in_progress',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-research-003',
        'content': '品質データ分析・SPC分析・品質コスト分析',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-research-004',
        'content': '設備効率・信頼性分析・予知保全可能性評価',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-research-005',
        'content': '在庫最適化・サプライチェーン分析',
        'status': 'pending',
        'priority': 'medium'
    },
    {
        'id': 'manufacturing-research-006',
        'content': '予測分析・最適化モデル構築',
        'status': 'pending',
        'priority': 'medium'
    },
    {
        'id': 'manufacturing-research-007',
        'content': '製造業改善提案・アクションプラン策定',
        'status': 'pending',
        'priority': 'medium'
    },
    {
        'id': 'manufacturing-research-008',
        'content': '効果測定・ROI分析・継続監視計画',
        'status': 'pending', 
        'priority': 'low'
    }
]
```

## まとめ

このコマンドは製造業特化のデータ分析・業務調査を実現します：

1. **製造業データ統合分析**: 生産・品質・設備・在庫データの包括的分析
2. **製造業予測・最適化**: AI/機械学習による予知保全・生産最適化
3. **ビジネス価値創出**: 具体的な改善提案・ROI評価による価値創出
4. **継続改善サイクル**: 監視・測定・改善の継続的な製造業務最適化

製造業特有の複雑なデータ構造と業務要求に対応した高度な分析により、持続的な競争優位性確立を支援します。