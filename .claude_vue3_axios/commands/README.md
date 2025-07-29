# コマンド一覧・統合ガイド

このドキュメントは、Vue.js + REST API 仕様書駆動開発システムで利用可能な全コマンドの概要と、マルチAI連携による効率的な開発フローを説明します。

## 🎯 マルチAIチーム構成

### Claude Code（実装・品質保証）
- **専門分野**: Vue.js + REST API開発、テスト、ドキュメント生成
- **役割**: システムエンジニア、デザイナー、開発者、テスター

### Gemini CLI（分析・戦略）
- **専門分野**: データ分析、コンテンツ戦略、プロダクト管理
- **役割**: データアナリスト、コンテンツストラテジスト、プロダクトマネージャー

### o3 MCP（インフラ・運用） 
- **専門分野**: システムアーキテクチャ、DevOps、セキュリティ
- **役割**: システムアーキテクト、DevOpsエンジニア、セキュリティスペシャリスト

## 📋 コマンド一覧

### 🔄 統合管理コマンド

#### `/spec` - 統合仕様駆動開発
- **目的**: 全フェーズの統合管理・オーケストレーション
- **対象AI**: Claude Code（メイン）+ 全AI連携
- **入力**: フェーズ名（init, requirements, design, tasks, implement, status）
- **出力**: フェーズ別成果物、進捗レポート
- **連携**: 全コマンドのエントリーポイント

#### `/modeltest` - マルチAI連携テスト
- **目的**: Gemini CLI・o3 MCP・Claude Codeの連携状況確認・検証
- **対象AI**: Claude Code（統合管理）+ 全AI連携テスト
- **入力**: テスト範囲（basic, comprehensive, performance, integration）
- **出力**: 連携テストレポート、パフォーマンス分析、改善推奨事項
- **連携**: マルチAI開発環境の健康診断・準備状況確認

---

### 📊 Gemini CLI専用コマンド（分析・戦略）

#### `/research` - データ分析・市場調査
- **目的**: 大規模データ分析、市場・競合・ユーザー調査
- **対象AI**: Gemini CLI（データアナリスト/リサーチャー）
- **入力**: 調査タイプ（user_behavior, market_analysis, competitor_analysis, performance_metrics, ab_test）
- **出力**: 分析レポート、データ可視化、推奨アクション
- **連携**: → `/content-strategy`, `/product-plan`

#### `/content-strategy` - コンテンツ戦略・ブランディング
- **目的**: マルチモーダル統合によるコンテンツ企画・ブランド戦略
- **対象AI**: Gemini CLI（コンテンツストラテジスト）
- **入力**: 戦略タイプ（content_planning, branding, persona, user_journey, marketing_campaign）
- **出力**: 戦略ドキュメント、ペルソナ、コンテンツプラン、ビジュアルアセット
- **連携**: ← `/research` → `/product-plan`, `/design`

#### `/product-plan` - プロダクト管理・要件管理
- **目的**: 長文コンテキスト活用による複雑な要件管理・ロードマップ策定
- **対象AI**: Gemini CLI（プロダクトマネージャー）
- **入力**: 計画タイプ（roadmap, feature_spec, requirements, prioritization, stakeholder_alignment）
- **出力**: プロダクト計画書、要件仕様書、ロードマップ、優先順位マトリクス
- **連携**: ← `/research`, `/content-strategy` → `/requirements`, `/design`

---

### 🛠️ Claude Code専用コマンド（実装・品質保証）

#### `/requirements` - 要件定義
- **目的**: ユーザー要求から技術要件への変換
- **対象AI**: Claude Code
- **入力**: タスク説明（$ARGUMENTS経由）
- **出力**: 要件ドキュメント（`.tmp/requirements.md`）
- **連携**: ← `/product-plan` → `/design`

#### `/design` - 技術設計
- **目的**: 要件に基づく技術設計・アーキテクチャ設計
- **対象AI**: Claude Code
- **入力**: 要件ドキュメント
- **出力**: 技術設計書、アーキテクチャ図、データベース設計
- **連携**: ← `/requirements`, `/content-strategy` → `/architecture`, `/tasks`

#### `/tasks` - タスク分割
- **目的**: 設計を実装可能な単位に分解・TodoWrite統合
- **対象AI**: Claude Code
- **入力**: 承認済み設計ドキュメント
- **出力**: 詳細タスクリスト、実装順序、工数見積もり
- **連携**: ← `/design` → 実装フェーズ

#### `/analyze` - プロジェクト分析
- **目的**: 既存プロジェクトの技術的分析・問題検出
- **対象AI**: Claude Code
- **入力**: 分析対象・スコープ
- **出力**: 分析レポート、改善提案、技術的負債評価
- **連携**: → `/fix`, `/refactor`, `/enhance`

#### `/enhance` - 機能追加・改善
- **目的**: 新機能追加・既存機能改善
- **対象AI**: Claude Code
- **入力**: 機能要求・改善要求
- **出力**: 実装計画、コード変更、テスト計画
- **連携**: ← `/analyze`, `/product-plan` → `/test`

#### `/fix` - バグ修正・問題解決
- **目的**: 迅速なバグ修正・問題解決
- **対象AI**: Claude Code
- **入力**: バグ・問題の詳細
- **出力**: 修正コード、テスト、回帰防止策
- **連携**: ← `/analyze`, `/security` → `/test`

#### `/refactor` - コードリファクタリング
- **目的**: コード品質向上・技術的負債解消
- **対象AI**: Claude Code
- **入力**: リファクタリング対象・目標
- **出力**: リファクタリング計画、改善コード、品質レポート
- **連携**: ← `/analyze` → `/test`, `/standardize`

#### `/document` - ドキュメント生成
- **目的**: 包括的なプロジェクトドキュメント自動生成
- **対象AI**: Claude Code
- **入力**: ドキュメント種類・範囲
- **出力**: API仕様、コンポーネントカタログ、ユーザーガイド
- **連携**: ← 全コマンド → 最終成果物

#### `/standardize` - 標準化・ベストプラクティス
- **目的**: コード標準・ベストプラクティスの適用
- **対象AI**: Claude Code
- **入力**: 標準化スコープ・基準
- **出力**: 標準化計画、コード改善、ガイドライン
- **連携**: ← `/refactor` → `/document`

---

### 🏗️ o3 MCP専用コマンド（インフラ・運用）

#### `/architecture` - システムアーキテクチャ設計
- **目的**: MCPプロトコル活用による大規模システム設計
- **対象AI**: o3 MCP（システムアーキテクト）
- **入力**: アーキテクチャタイプ（system_design, microservices, integration, scalability, migration）
- **出力**: アーキテクチャ設計書、システム構成図、実装ガイド
- **連携**: ← `/design`, `/product-plan` → `/devops`, `/security`

#### `/devops` - DevOps・インフラ自動化
- **目的**: ツール直接統合によるCI/CD・インフラ自動化
- **対象AI**: o3 MCP（DevOpsエンジニア）
- **入力**: DevOpsタイプ（cicd, infrastructure, monitoring, deployment, automation）
- **出力**: インフラ設定、CI/CD設定、監視設定、自動化スクリプト
- **連携**: ← `/architecture` → `/security`, `/monitoring`

#### `/security` - セキュリティ設計・監査
- **目的**: セキュリティツール連携による脅威分析・対策
- **対象AI**: o3 MCP（セキュリティスペシャリスト）
- **入力**: セキュリティタイプ（threat_analysis, security_audit, compliance, incident_response, penetration_test）
- **出力**: セキュリティ評価書、脅威分析、対策実装ガイド、インシデント対応計画
- **連携**: ← `/architecture`, `/devops` → `/fix`, `/compliance`

---

## 🔄 統合ワークフロー例

### 新規プロジェクト開発フロー

```mermaid
graph TD
    A[プロジェクト開始] --> B[/spec init]
    B --> C[/research market_analysis]
    C --> D[/content-strategy branding]
    D --> E[/product-plan roadmap]
    E --> F[/requirements]
    F --> G[/design]
    G --> H[/architecture system_design]
    H --> I[/tasks]
    I --> J[実装開始]
    J --> K[/devops cicd]
    K --> L[/security threat_analysis]
    L --> M[/document]
    M --> N[リリース]
```

### 既存プロジェクト改善フロー

```mermaid
graph TD
    A[改善要求] --> B[/analyze]
    B --> C[/research performance_metrics]
    C --> D{問題種別}
    D -->|パフォーマンス| E[/refactor]
    D -->|セキュリティ| F[/security security_audit]
    D -->|機能追加| G[/enhance]
    E --> H[/test]
    F --> I[/fix]
    G --> J[/tasks]
    H --> K[/devops monitoring]
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

## 🎯 使用場面別推奨フロー

### 💡 新機能開発
1. `/modeltest basic` - **AI連携環境確認**
2. `/research user_behavior` - ユーザーニーズ調査
3. `/content-strategy persona` - ペルソナ・UX設計
4. `/product-plan feature_spec` - 機能仕様策定
5. `/requirements` - 技術要件定義
6. `/design` - 詳細設計
7. `/architecture` - システム設計
8. `/tasks` - 実装計画
9. 実装 → `/devops` → `/security` → `/document`

### 🔧 技術的負債解消
1. `/modeltest comprehensive` - **AI連携パフォーマンス確認**
2. `/analyze` - 現状分析・問題特定
3. `/research performance_metrics` - パフォーマンス分析
4. `/refactor` - リファクタリング計画・実行
5. `/security security_audit` - セキュリティ評価
6. `/devops monitoring` - 監視・運用改善
7. `/standardize` - 標準化・ベストプラクティス適用
8. `/document` - ドキュメント更新

### 🚀 スケールアップ対応
1. `/modeltest performance` - **AI連携パフォーマンス・負荷評価**
2. `/research market_analysis` - 市場・競合分析
3. `/architecture scalability` - スケーラブルアーキテクチャ設計
4. `/devops infrastructure` - インフラ自動化・拡張
5. `/security compliance` - セキュリティ・コンプライアンス強化
6. `/product-plan roadmap` - 成長ロードマップ策定

### 🛡️ セキュリティ強化
1. `/modeltest integration` - **AI連携セキュリティ・統合評価**
2. `/security threat_analysis` - 脅威分析・リスク評価
3. `/security security_audit` - セキュリティ監査
4. `/architecture security` - セキュリティアーキテクチャ設計
5. `/devops security` - セキュアなCI/CD・運用
6. `/fix` - セキュリティ脆弱性修正
7. `/security incident_response` - インシデント対応体制構築

## 💡 効率的な使い方のコツ

### 1. **段階的アプローチ**
- 大きな変更は小さなフェーズに分割
- 各フェーズで適切なAIチームメンバーを活用
- 前のフェーズの成果物を次のフェーズの入力として活用

### 2. **専門性の活用**
- データ分析 → Gemini CLI (`/research`)
- クリエイティブ戦略 → Gemini CLI (`/content-strategy`)
- 技術実装 → Claude Code (`/design`, `/enhance`, `/fix`)
- インフラ・運用 → o3 MCP (`/architecture`, `/devops`, `/security`)

### 3. **品質保証の徹底**
- 各フェーズで品質チェックリストを活用
- `/analyze` による定期的な健康診断
- `/security` による継続的なセキュリティ評価
- `/document` による知識の体系化・共有

### 4. **継続的改善**
- `/research performance_metrics` による定期的なパフォーマンス分析
- ユーザーフィードバックを `/content-strategy` に反映
- 技術的負債を `/refactor` で計画的に解消
- セキュリティ動向を `/security` で継続監視

## 🧪 環境準備・健康診断

### `/modeltest` の定期実行推奨
- **プロジェクト開始時**: `/modeltest basic` で基本連携確認
- **月次健康診断**: `/modeltest comprehensive` で総合評価
- **パフォーマンス監視**: `/modeltest performance` で負荷・応答性確認
- **環境変更後**: `/modeltest integration` で統合機能確認

このコマンドシステムにより、個人開発者でも企業レベルの開発力・品質を実現できます。