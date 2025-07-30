# コマンド一覧・統合ガイド

このドキュメントは、FastAPI + SQLAlchemy エンタープライズシステム開発における仕様書駆動開発システムで利用可能な全コマンドの概要と、マルチAI連携による効率的な開発フローを説明します。

## 🎯 マルチAIチーム構成

### Claude Code（実装・品質保証）
- **専門分野**: FastAPI + SQLAlchemy開発、エンタープライズシステム設計、既存システム統合、テスト
- **役割**: システムエンジニア、エンタープライズドメインエキスパート、開発者、テスター

### Gemini CLI（分析・戦略）
- **専門分野**: ビジネスデータ分析、プロセス最適化、エンタープライズ戦略
- **役割**: ビジネスデータアナリスト、戦略プランナー、ビジネスインテリジェンススペシャリスト

### o3 MCP（インフラ・運用） 
- **専門分野**: エンタープライズシステムアーキテクチャ、既存システム統合、APIインターフェース
- **役割**: システムアーキテクト、統合エンジニア、インフラスペシャリスト

## 📋 コマンド一覧

### 🔄 統合管理コマンド

#### `/spec` - 統合仕様駆動開発
- **目的**: エンタープライズシステム全フェーズの統合管理・オーケストレーション
- **対象AI**: Claude Code（メイン）+ 全AI連携
- **入力**: フェーズ名（init, requirements, design, tasks, implement, status）
- **出力**: フェーズ別成果物、進捗レポート、エンタープライズ要件準拠チェック
- **連携**: 全コマンドのエントリーポイント

#### `/modeltest` - マルチAI連携テスト
- **目的**: Gemini CLI・o3 MCP・Claude Codeの連携状況確認・検証
- **対象AI**: Claude Code（統合管理）+ 全AI連携テスト
- **入力**: テスト範囲（basic, comprehensive, performance, integration）
- **出力**: 連携テストレポート、パフォーマンス分析、改善推奨事項
- **連携**: マルチAI開発環境の健康診断・準備状況確認

---

### 📊 Gemini CLI専用コマンド（製造データ分析・戦略）

#### `/research` - 製造データ分析・市場調査
- **目的**: 生産データ分析、製造業市場調査、サプライチェーン分析
- **対象AI**: Gemini CLI（製造データアナリスト/リサーチャー）
- **入力**: 調査タイプ（production_analysis, quality_metrics, supply_chain, market_trends, equipment_performance）
- **出力**: 製造データ分析レポート、生産効率可視化、改善推奨アクション
- **連携**: → `/content-strategy`, `/product-plan`

#### `/content-strategy` - 製造業ブランディング・マーケティング
- **目的**: 製造業向けコンテンツ企画・ブランド戦略・顧客エンゲージメント
- **対象AI**: Gemini CLI（製造業マーケティングストラテジスト）
- **入力**: 戦略タイプ（brand_positioning, customer_engagement, product_showcase, industry_authority, lead_generation）
- **出力**: 製造業ブランド戦略、顧客ペルソナ、技術コンテンツプラン
- **連携**: ← `/research` → `/product-plan`, `/design`

#### `/product-plan` - 製造システム・プロダクト管理
- **目的**: 製造業システム要件管理・ロードマップ策定・生産計画統合
- **対象AI**: Gemini CLI（製造システムプロダクトマネージャー）
- **入力**: 計画タイプ（system_roadmap, production_requirements, quality_standards, compliance_planning, capacity_optimization）
- **出力**: 製造システム計画書、生産要件仕様書、品質基準、コンプライアンス要件
- **連携**: ← `/research`, `/content-strategy` → `/requirements`, `/design`

---

### 🛠️ Claude Code専用コマンド（実装・品質保証）

#### `/requirements` - 製造業要件定義
- **目的**: 製造業ユーザー要求からFastAPI + SQLAlchemy技術要件への変換
- **対象AI**: Claude Code
- **入力**: 製造業タスク説明（$ARGUMENTS経由）
- **出力**: 製造業要件ドキュメント（`.tmp/manufacturing_requirements.md`）
- **連携**: ← `/product-plan` → `/design`

#### `/design` - 製造業システム技術設計
- **目的**: 製造業要件に基づく技術設計・データベース設計・API設計
- **対象AI**: Claude Code
- **入力**: 製造業要件ドキュメント
- **出力**: 技術設計書、SQLAlchemy ERD、FastAPI仕様書、製造業データモデル
- **連携**: ← `/requirements`, `/content-strategy` → `/architecture`, `/tasks`

#### `/tasks` - 製造業システムタスク分割
- **目的**: 製造業システム設計を実装可能な単位に分解・TodoWrite統合
- **対象AI**: Claude Code
- **入力**: 承認済み製造業システム設計ドキュメント
- **出力**: 詳細タスクリスト、実装順序、工数見積もり、品質チェックポイント
- **連携**: ← `/design` → 実装フェーズ

#### `/analyze` - 製造業システム分析
- **目的**: 既存製造業システムの技術的分析・問題検出・生産性評価
- **対象AI**: Claude Code
- **入力**: 分析対象・スコープ
- **出力**: システム分析レポート、製造業特有問題の特定、改善提案
- **連携**: → `/fix`, `/refactor`, `/enhance`

#### `/enhance` - 製造機能追加・改善
- **目的**: 新製造機能追加・既存生産システム改善
- **対象AI**: Claude Code
- **入力**: 製造機能要求・生産改善要求
- **出力**: 実装計画、コード変更、製造業テスト計画
- **連携**: ← `/analyze`, `/product-plan` → `/test`

#### `/fix` - 製造システムバグ修正・問題解決
- **目的**: 製造システムの迅速なバグ修正・生産トラブル解決
- **対象AI**: Claude Code
- **入力**: バグ・問題の詳細、生産への影響度
- **出力**: 修正コード、テスト、回帰防止策、生産停止リスク軽減
- **連携**: ← `/analyze`, `/security` → `/test`

#### `/refactor` - 製造システムリファクタリング
- **目的**: 製造システムコード品質向上・技術的負債解消・保守性改善
- **対象AI**: Claude Code
- **入力**: リファクタリング対象・目標
- **出力**: リファクタリング計画、改善コード、品質レポート
- **連携**: ← `/analyze` → `/test`, `/standardize`

#### `/document` - 製造業ドキュメント生成
- **目的**: 製造業システムの包括的ドキュメント自動生成
- **対象AI**: Claude Code
- **入力**: ドキュメント種類・範囲
- **出力**: API仕様、データベーススキーマ、製造業運用ガイド、品質管理手順書
- **連携**: ← 全コマンド → 最終成果物

#### `/standardize` - 製造業標準化・ベストプラクティス
- **目的**: 製造業コード標準・ベストプラクティスの適用
- **対象AI**: Claude Code
- **入力**: 標準化スコープ・基準
- **出力**: 標準化計画、コード改善、製造業ガイドライン
- **連携**: ← `/refactor` → `/document`

---

### 🏗️ o3 MCP専用コマンド（製造インフラ・運用）

#### `/architecture` - 製造システムアーキテクチャ設計
- **目的**: MCPプロトコル活用による製造業大規模システム設計
- **対象AI**: o3 MCP（製造システムアーキテクト）
- **入力**: アーキテクチャタイプ（manufacturing_system, iot_integration, plc_interface, mes_integration, scada_connection）
- **出力**: 製造アーキテクチャ設計書、IoTシステム構成図、PLC統合仕様
- **連携**: ← `/design`, `/product-plan` → `/devops`, `/security`

#### `/devops` - 製造業DevOps・インフラ自動化
- **目的**: 製造環境CI/CD・インフラ自動化・生産システム運用
- **対象AI**: o3 MCP（製造DevOpsエンジニア）
- **入力**: DevOpsタイプ（manufacturing_cicd, production_infrastructure, iot_monitoring, plc_deployment, edge_computing）
- **出力**: 製造インフラ設定、生産CI/CD設定、IoT監視設定、エッジコンピューティング
- **連携**: ← `/architecture` → `/security`, `/monitoring`

#### `/security` - 製造業セキュリティ設計・監査
- **目的**: 製造業セキュリティツール連携による脅威分析・対策
- **対象AI**: o3 MCP（製造セキュリティスペシャリスト）
- **入力**: セキュリティタイプ（ot_security, industrial_cybersecurity, plc_protection, scada_security, supply_chain_security）
- **出力**: 製造セキュリティ評価書、OT脅威分析、産業制御システム保護対策
- **連携**: ← `/architecture`, `/devops` → `/fix`, `/compliance`

---

## 🔄 製造業統合ワークフロー例

### 新規製造システム開発フロー

```mermaid
graph TD
    A[製造システム開発開始] --> B[/spec init]
    B --> C[/research production_analysis]
    C --> D[/content-strategy brand_positioning]
    D --> E[/product-plan system_roadmap]
    E --> F[/requirements]
    F --> G[/design]
    G --> H[/architecture manufacturing_system]
    H --> I[/tasks]
    I --> J[実装開始]
    J --> K[/devops manufacturing_cicd]
    K --> L[/security ot_security]
    L --> M[/document]
    M --> N[生産リリース]
```

### 既存製造システム改善フロー

```mermaid
graph TD
    A[製造改善要求] --> B[/analyze]
    B --> C[/research equipment_performance]
    C --> D{問題種別}
    D -->|生産効率| E[/refactor]
    D -->|セキュリティ| F[/security industrial_cybersecurity]
    D -->|機能追加| G[/enhance]
    E --> H[/test]
    F --> I[/fix]
    G --> J[/tasks]
    H --> K[/devops iot_monitoring]
    I --> K
    J --> K
    K --> L[/document]
```

## 📊 コマンド連携マトリクス

| From/To | Claude Code | Gemini CLI | o3 MCP |
|---------|-------------|------------|--------|
| **Claude Code** | analyze→fix, design→tasks | requirements←product-plan | design→architecture |
| **Gemini CLI** | research→content-strategy | content-strategy→product-plan | product-plan→architecture |
| **o3 MCP** | architecture→design | - | devops→security |

## 🎯 製造業場面別推奨フロー

### 💡 新製造機能開発
1. `/modeltest basic` - **AI連携環境確認**
2. `/research production_analysis` - 生産データニーズ調査
3. `/content-strategy customer_engagement` - 製造業ユーザーエクスペリエンス設計
4. `/product-plan system_roadmap` - 製造機能仕様策定
5. `/requirements` - 技術要件定義
6. `/design` - 詳細設計
7. `/architecture manufacturing_system` - システム設計
8. `/tasks` - 実装計画
9. 実装 → `/devops` → `/security` → `/document`

### 🔧 製造技術的負債解消
1. `/modeltest comprehensive` - **AI連携パフォーマンス確認**
2. `/analyze` - 現状分析・問題特定
3. `/research equipment_performance` - 設備パフォーマンス分析
4. `/refactor` - リファクタリング計画・実行
5. `/security ot_security` - 製造セキュリティ評価
6. `/devops iot_monitoring` - IoT監視・運用改善
7. `/standardize` - 標準化・ベストプラクティス適用
8. `/document` - ドキュメント更新

### 🚀 製造スケールアップ対応
1. `/modeltest performance` - **AI連携パフォーマンス・負荷評価**
2. `/research market_trends` - 製造業市場・競合分析
3. `/architecture mes_integration` - スケーラブル製造アーキテクチャ設計
4. `/devops production_infrastructure` - 製造インフラ自動化・拡張
5. `/security supply_chain_security` - サプライチェーンセキュリティ強化
6. `/product-plan capacity_optimization` - 生産能力最適化ロードマップ策定

### 🛡️ 製造セキュリティ強化
1. `/modeltest integration` - **AI連携セキュリティ・統合評価**
2. `/security ot_security` - OT脅威分析・リスク評価
3. `/security industrial_cybersecurity` - 産業サイバーセキュリティ監査
4. `/architecture plc_interface` - セキュアPLCインターフェース設計
5. `/devops edge_computing` - セキュアエッジコンピューティング・運用
6. `/fix` - セキュリティ脆弱性修正
7. `/security scada_security` - SCADA系セキュリティ対応体制構築

## 💡 製造業効率的な使い方のコツ

### 1. **製造業段階的アプローチ**
- 大きな製造変更は小さなフェーズに分割
- 各フェーズで適切なAIチームメンバーを活用
- 前のフェーズの成果物を次のフェーズの入力として活用

### 2. **製造業専門性の活用**
- 生産データ分析 → Gemini CLI (`/research`)
- 製造業戦略 → Gemini CLI (`/content-strategy`)
- 技術実装 → Claude Code (`/design`, `/enhance`, `/fix`)
- 製造インフラ・運用 → o3 MCP (`/architecture`, `/devops`, `/security`)

### 3. **製造業品質保証の徹底**
- 各フェーズで製造業品質チェックリストを活用
- `/analyze` による定期的な製造システム健康診断
- `/security` による継続的な製造セキュリティ評価
- `/document` による知識の体系化・共有

### 4. **製造業継続的改善**
- `/research equipment_performance` による定期的な設備パフォーマンス分析
- 製造ユーザーフィードバックを `/content-strategy` に反映
- 技術的負債を `/refactor` で計画的に解消
- 製造セキュリティ動向を `/security` で継続監視

## 🧪 環境準備・健康診断

### `/modeltest` の定期実行推奨
- **プロジェクト開始時**: `/modeltest basic` で基本連携確認
- **月次健康診断**: `/modeltest comprehensive` で総合評価
- **パフォーマンス監視**: `/modeltest performance` で負荷・応答性確認
- **環境変更後**: `/modeltest integration` で統合機能確認

この製造業向けコマンドシステムにより、個人開発者でも企業レベルの製造業システム開発力・品質を実現できます。