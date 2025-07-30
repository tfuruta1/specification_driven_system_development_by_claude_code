# CLAUDE.md - Vue.js + ハイブリッド接続 仕様書駆動開発

このファイルは、Claude Code がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

Vue.js (Composition API) + ハイブリッド接続方式（REST API → Supabase → Offline）を使用した高可用性Webアプリケーション開発プロジェクトです。
複数のバックエンド接続オプションを持つ適応的なアーキテクチャにより、ネットワーク状況や接続可能性に応じて最適な接続方式を自動選択します。

## 技術スタック

### フロントエンド
- **フレームワーク**: Vue.js 3.x (Composition API)
- **状態管理**: Pinia
- **ルーティング**: Vue Router
- **スタイリング**: Tailwind CSS + DaisyUI
- **ビルドツール**: Vite
- **言語**: JavaScript (ES2015+)

### バックエンド・インフラ（ハイブリッド接続 + 既存システム統合）
- **プライマリ接続**: REST API（Axios）→ FastAPI + SQLAlchemy + venv連携
- **フォールバック接続**: Supabase（PostgreSQL + Auth + Realtime）
- **オフライン対応**: JSONファイルベースローカルストレージ（./data/offline/）
- **認証**: JWT（REST API）/ Supabase Auth（フォールバック）/ LDAP・既存認証連携
- **データベース**: SQL Server/PostgreSQL/Oracle/DB2（FastAPI）、PostgreSQL（Supabase）
- **既存システム統合**: SOAP・ETL・ESB・メインフレーム・レガシーDB統合
- **ホスティング**: Vercel / Netlify / オンプレミス
- **接続管理**: 自動フェイルオーバー・復旧・既存システム同期

## アーキテクチャ原則

### プロジェクト構造
```
src/
├── components/           # Vueコンポーネント
│   ├── ui/              # 基本UIコンポーネント (DaisyUI ベース)
│   ├── features/        # 機能別コンポーネント
│   └── layouts/         # レイアウトコンポーネント
├── composables/         # Vue Composition API カスタムコンポーザブル
├── stores/              # Pinia ストア
├── router/              # Vue Router 設定
├── services/            # ハイブリッド接続サービス（REST API・Supabase・Offline）
├── utils/               # ユーティリティ関数
├── types/               # TypeScript型定義 (JSDocで型安全性を確保)
└── assets/              # 静的ファイル
```

### 設計パターン
1. **コンポーザブルパターン**: ロジックの再利用性を重視
2. **ストアパターン**: Piniaによる状態管理の統一
3. **ハイブリッドサービス層**: 複数バックエンドの抽象化と自動切り替え
4. **アダプターパターン**: 接続方式に依存しない統一インターフェース
5. **フォールバック戦略**: 段階的な接続試行とエラーハンドリング
6. **オフライン同期**: ローカルデータとリモートデータの同期管理

## 開発ワークフロー - 仕様書駆動開発

### 4段階ワークフロー
1. **要件定義** (`/requirements`) - 機能要件の明確化
2. **設計** (`/design`) - 技術設計とアーキテクチャ
3. **タスク分割** (`/tasks`) - 実装可能な単位への分解
4. **実装** - 設計に基づく実装

### ワークフローコマンド
- `/spec` - 完全な仕様書駆動開発ワークフローを開始
- `/requirements` - 要件定義のみ実行
- `/design` - 設計フェーズのみ実行
- `/tasks` - タスク分割のみ実行

## 開発ルール

### Vue.js 開発ルール
- **Composition API必須**: `<script setup>` 構文を標準使用
- **Single File Component**: .vue ファイルによるコンポーネント開発
- **Props定義**: `defineProps()` による型安全なProps
- **Emit定義**: `defineEmits()` によるイベント定義
- **Reactive変数**: `ref()` / `reactive()` の適切な使い分け

### Pinia ストアルール
- **ストア分割**: 機能別にストアを分割
- **アクション中心**: 状態変更はアクションを通して実行
- **コンポーザブル活用**: `use{StoreName}Store()` パターン
- **永続化**: 必要に応じて `pinia-plugin-persistedstate` を使用

### ハイブリッド接続ルール（既存システム統合強化）
- **統一インターフェース**: どの接続方式でも同じAPIで操作・既存システムも統一インターフェース
- **自動フェイルオーバー**: REST API → Supabase → 既存システム → Offline の順で自動切り替え
- **接続状態管理**: リアルタイムでの接続状態監視と復旧処理
- **データ同期**: オフラインデータとオンラインデータの双方向同期・既存システム同期
- **認証連携**: JWT / Supabase Auth / LDAP・既存認証システムの統合管理
- **キャッシュ戦略**: 各接続方式に最適化されたキャッシュとデータ永続化
- **venv連携**: FastAPIバックエンドとのシームレス統合開発・デプロイ

### スタイリング・UI ルール
- **DaisyUI優先**: 基本コンポーネントはDaisyUIを活用
- **Tailwind CSS**: カスタムスタイルはTailwindユーティリティクラス
- **レスポンシブ**: モバイルファーストの設計
- **ダークモード**: DaisyUIのテーマ切り替え機能を活用

## 品質保証

### テスト戦略
- **コンポーネントテスト**: Vue Test Utils + Vitest
- **ユニットテスト**: ユーティリティ関数・コンポーザブル
- **E2Eテスト**: Playwright (重要フローのみ)

### コード品質
- **ESLint**: Vue.js推奨設定 + Prettier
- **型安全性**: JSDocによる型注釈（必要に応じてTypeScript移行）
- **コミット規約**: Conventional Commits

## 重要な設計上の決定

1. **JavaScript優先**: TypeScriptは将来の選択肢として残し、まずはJSDocで型安全性を確保
2. **コンポーザブル活用**: Vue 3 の Composition API の利点を最大化
3. **DaisyUI中心**: 統一されたデザインシステムの構築
4. **API最適化**: Axiosインターセプターとキャッシュ戦略の積極活用
5. **パフォーマンス重視**: Vue 3 の新機能（Suspense、Teleport等）の活用
6. **既存システム統合優先**: レガシーシステムとのシームレス連携を重視
7. **venv連携最適化**: Python仮想環境との効率的連携を実現

## よくある落とし穴

1. **リアクティビティの破壊**: オブジェクトの分割代入に注意
2. **Pinia ストアの初期化**: SSRモードでの注意点
3. **JWT トークン管理**: ブラウザリフレッシュ時の認証状態復元
4. **DaisyUI テーマ**: 動的テーマ切り替え時のちらつき対策
5. **Vue Router**: 動的ルートでのコンポーネント再利用問題

## ドキュメント参照ガイド

### プロジェクト概要・要件
- **`.claude/00_project/01_project_concept.md`** - プロジェクトのビジョンと目標
- **`.claude/00_project/02_tech_stack_guidelines.md`** - 技術選定の根拠と指針

### 技術設計ドキュメント
- **`.claude/01_development_docs/01_architecture_design.md`** - 全体アーキテクチャ
- **`.claude/01_development_docs/02_api_design.md`** - REST API 設計・仕様
- **`.claude/01_development_docs/03_authentication_design.md`** - 認証・認可設計
- **`.claude/01_development_docs/04_component_design.md`** - Vue コンポーネント設計
- **`.claude/01_development_docs/05_state_management_design.md`** - Pinia ストア設計
- **`.claude/01_development_docs/06_routing_design.md`** - Vue Router 設計
- **`.claude/01_development_docs/07_error_handling_design.md`** - エラーハンドリング戦略
- **`.claude/01_development_docs/08_type_definitions.md`** - 型定義と JSDoc 規約
- **`.claude/01_development_docs/16_fullstack_integration.md`** - Vue3 + FastAPI フルスタック統合設計

### デザインシステム
- **`.claude/02_design_system/00_design_overview.md`** - デザインシステム概要
- **`.claude/02_design_system/01_tailwind_config.md`** - Tailwind CSS 設定
- **`.claude/02_design_system/02_daisyui_components.md`** - DaisyUI コンポーネント使用指針
- **`.claude/02_design_system/03_vue_component_patterns.md`** - Vue コンポーネントパターン

### ライブラリ固有情報
- **`.claude/03_library_docs/01_vue_composition_patterns.md`** - Vue Composition API パターン集
- **`.claude/03_library_docs/02_pinia_store_patterns.md`** - Pinia ストアパターン集
- **`.claude/03_library_docs/03_axios_integration.md`** - Axios 統合ガイド（ハイブリッド接続対応）
- **`.claude/03_library_docs/04_vite_configuration.md`** - Vite 設定とプラグイン
- **`.claude/03_library_docs/05_fastapi_integration.md`** - FastAPI + SQLAlchemy 完全統合ガイド

### タスク別クイックリファレンス

| タスク | 主要参照ドキュメント |
|-------|-------------------|
| 新機能追加 | アーキテクチャ → API設計 → コンポーネント設計 |
| 新しいページ作成 | ルーティング → コンポーネント → 状態管理 |
| API連携機能 | API設計 → 認証設計 → エラーハンドリング |
| UI実装 | コンポーネント設計 → DaisyUI → Tailwind設定 |
| 状態管理 | Pinia パターン → 状態管理設計 |
| 認証機能 | 認証設計 → Axios統合 → エラーハンドリング |
| API統合 | Axios統合 → API設計 → 型定義 |
| FastAPI統合 | FastAPI統合ガイド → フルスタック統合設計 → 認証設計 |
| テスト作成 | テスト戦略 → Vue Composition パターン |

## マルチAIチーム構成

このプロジェクトでは、複数のAIシステムを専門分野別に活用し、効率的なチーム開発を実現します。

### チームメンバー構成

#### 統括管理層
- **プロジェクトマネージャー（ユーザー）**: 全体戦略・意思決定・品質管理の最終責任者

#### Claude Code チーム（実装・品質保証）
- **技術実装エキスパート**: Vue.js + REST API開発の中核を担当
  - システムエンジニア（設計）
  - デザイナー（UI/UX）
  - フロントエンド・バックエンド開発者
  - テスター（品質保証）

#### Gemini CLI チーム（分析・戦略）
- **データアナリスト / リサーチャー**: 
  - 専門領域: データ分析・市場調査・ユーザー行動分析
  - 強み: 大規模コンテキスト処理、マルチモーダル対応、パターン認識
  - 主要活用: ユーザー行動データ分析、競合調査、A/Bテスト解析、パフォーマンス洞察

- **コンテンツストラテジスト**:
  - 専門領域: コンテンツ企画・ブランディング・UI/UXデザイン戦略
  - 強み: マルチモーダル統合、クリエイティブ発想、戦略的思考
  - 主要活用: ペルソナ設計、マーケティング戦略、ブランドアイデンティティ、ユーザージャーニーマップ

- **プロダクトマネージャー**:
  - 専門領域: 要件管理・ロードマップ策定・機能優先順位付け
  - 強み: 長文コンテキスト保持、総合判断、ステークホルダー調整
  - 主要活用: 複雑要件整理、依存関係管理、ユーザーストーリー詳細化、ロードマップ策定

#### o3 MCP チーム（インフラ・運用・データベース）
- **データベーススペシャリスト**:
  - 専門領域: ハイブリッド接続DB設計・SQL Server⇔Supabase統合・データ同期
  - 強み: MCPによる実DB連携、複雑クエリ最適化、3層データアーキテクチャ設計
  - 主要活用: ハイブリッド接続設計、マイグレーション戦略、パフォーマンス最適化、データ整合性保証

- **システムアーキテクト**:
  - 専門領域: システム設計・インフラ構成・技術選定
  - 強み: MCPによる実システム連携、リアルタイム構成変更、複雑統合設計
  - 主要活用: 大規模アーキテクチャ設計、マイクロサービス構成、外部システム連携

- **DevOpsエンジニア**:
  - 専門領域: CI/CD・インフラ自動化・運用監視
  - 強み: ツールとの直接統合、実環境操作、継続的改善プロセス
  - 主要活用: デプロイパイプライン、インフラコード管理、監視システム、自動復旧

- **セキュリティスペシャリスト**:
  - 専門領域: セキュリティ設計・脅威分析・コンプライアンス
  - 強み: セキュリティツール連携、リアルタイム脅威検知、システムレベル分析
  - 主要活用: セキュリティ監査、脅威モデリング、ポリシー策定、インシデント対応

### o3モデル階層別ロール分担

#### o3-high（チーフアーキテクト / テクニカルリード）
- **担当**: 重要な技術的意思決定、アーキテクチャ大幅変更、クリティカル問題解決
- **責任**: 長期技術戦略策定、技術的リスク評価、チーム技術方針決定

#### o3-standard（シニアエンジニア / 実装スペシャリスト）
- **担当**: 日常開発タスク、コードレビュー、API・ミドルウェア設計、技術メンタリング
- **責任**: 機能開発・バグ修正、技術ドキュメント作成、チーム内技術指導

#### o3-low（オペレーションエンジニア / 自動化スペシャリスト）
- **担当**: 定型タスク自動化、監視・アラート管理、ログ解析、簡易トラブルシューティング
- **責任**: 運用効率化、定期メンテナンス、簡易スクリプト作成

### チーム連携ワークフロー

```mermaid
graph TB
    PM[プロジェクトマネージャー<br/>統括・意思決定]
    
    subgraph "分析・戦略フェーズ"
        DA[データアナリスト<br/>Gemini CLI]
        CS[コンテンツストラテジスト<br/>Gemini CLI] 
        GPM[プロダクトマネージャー<br/>Gemini CLI]
    end
    
    subgraph "実装・品質フェーズ"
        CC[Claude Code<br/>実装エキスパート]
    end
    
    subgraph "インフラ・運用フェーズ"
        DBS[データベーススペシャリスト<br/>o3 MCP]
        SA[システムアーキテクト<br/>o3 MCP]
        DO[DevOpsエンジニア<br/>o3 MCP]
        SS[セキュリティスペシャリスト<br/>o3 MCP]
    end
    
    PM --> DA
    PM --> GPM
    DA --> CS
    GPM --> CC
    CS --> CC
    CC --> DBS
    DBS --> SA
    SA --> DO
    DO --> SS
    SS --> PM
```

### AIチーム活用指針

#### 新規プロジェクト開始時
1. **Gemini CLI**: 市場調査・要件分析・戦略策定
2. **Claude Code**: 設計・実装・テスト
3. **o3 MCP**: データベース設計・インフラ設計・運用準備

#### 既存プロジェクト改善時
1. **Gemini CLI**: 現状分析・改善戦略立案
2. **Claude Code**: リファクタリング・機能追加
3. **o3 MCP**: DB最適化・パフォーマンス改善・セキュリティ強化

#### 運用フェーズ
1. **Gemini CLI**: ユーザー分析・コンテンツ最適化
2. **Claude Code**: バグ修正・機能拡張
3. **o3 MCP**: データベース監視・自動化・セキュリティ運用

## マルチAI協調開発指針

### Claude Code 作業指針（実装・品質保証責任者）

#### 他AIとの連携指針
1. **Gemini CLI成果物の活用**
   - `/research` 結果を設計・実装の優先順位決定に活用
   - `/content-strategy` 成果をUIデザイン・UX設計に反映
   - `/product-plan` 要件を技術仕様に落とし込み

2. **o3 MCP成果物の活用**
   - データベーススペシャリスト設計をDB統合実装に反映
   - `/architecture` 設計をフロントエンド・バックエンド実装に反映
   - `/devops` 要件を開発環境・CI/CD設定に適用
   - `/security` 要件をコード実装・認証機能に統合

3. **成果物共有責任**
   - 設計書を `.tmp/ai_shared_data/claude_designs/` に出力
   - 実装進捗を JSON 形式で他AIと共有
   - テスト結果・品質評価を他AIの改善に活用

#### マルチAI品質保証プロセス
1. **設計段階**: Gemini CLI 分析結果 + o3 MCP アーキテクチャ要件の整合性確認
2. **実装段階**: o3 MCP セキュリティ要件 + Gemini CLI UX要件の実装品質確認
3. **テスト段階**: 全AI成果物との整合性テスト・統合品質評価

### データ共有プロトコル（Claude Code視点）

#### 受信データフォーマット
```javascript
// Gemini CLI からの分析結果（ハイブリッド接続特化）
{
  "source": "gemini_cli",
  "type": "hybrid_connection_analysis",
  "insights": {
    "connection_performance": {
      "rest_api_response_time": "number",
      "supabase_fallback_frequency": "number", 
      "offline_usage_patterns": "array"
    },
    "data_flow_efficiency": {
      "sync_success_rate": "number",
      "conflict_resolution_patterns": "array",
      "bottleneck_analysis": "object"
    },
    "user_behavior": "object",
    "content_strategy": "object"
  },
  "implementation_suggestions": "array",
  "priority_ranking": "array"
}

// o3 MCP からのデータベース設計要件（ハイブリッド特化）
{
  "source": "o3_mcp", 
  "type": "hybrid_db_architecture",
  "technical_constraints": {
    "rest_api_optimization": "object",
    "supabase_configuration": "object", 
    "offline_storage_strategy": "object"
  },
  "security_requirements": "array",
  "infrastructure_specs": {
    "connection_pooling": "object",
    "cache_strategy": "object",
    "sync_algorithms": "object"
  },
  "performance_targets": {
    "connection_switch_time": "number",
    "sync_throughput": "number",
    "data_consistency": "number"
  }
}
```

#### 送信データフォーマット
```javascript
// Claude Code からの実装結果
{
  "source": "claude_code",
  "type": "implementation_result", 
  "implementation_status": "object",
  "design_decisions": "array",
  "technical_debt": "array",
  "performance_metrics": "object",
  "feedback_to_gemini": "array", // UX改善提案
  "feedback_to_o3": "array" // インフラ・セキュリティ改善提案
}
```

### エスカレーション・調整プロセス

#### AI間の意見対立解決
1. **技術vs戦略の対立**: Gemini CLI戦略 vs Claude Code実装可能性
   - データ駆動による客観的評価
   - プロトタイプ・PoC実装による検証
   - 段階的実装による リスク軽減

2. **実装vsインフラの対立**: Claude Code設計 vs o3 MCPインフラ制約  
   - アーキテクチャ代替案の検討
   - パフォーマンス・コスト トレードオフ分析
   - 段階的移行計画による調整

3. **優先順位の調整**: 機能要件 vs 非機能要件 vs 運用要件
   - ビジネス価値・技術的リスク・運用コストの定量評価
   - ステークホルダー・ユーザーフィードバックの活用
   - MVP・段階的デリバリによる調整

### 継続的学習・改善プロセス

#### AI協調効果の測定
- **品質指標**: バグ数削減、レビュー指摘事項削減、テストカバレッジ向上
- **効率指標**: 実装時間短縮、手戻り工数削減、リリース頻度向上
- **顧客価値**: ユーザー満足度向上、パフォーマンス改善、機能充実度

#### 知見共有・蓄積
- AI協調成功事例・失敗事例の体系的蓄積
- ベストプラクティス・アンチパターンの整理
- チームメンバー・ステークホルダーへの知見共有

このCLAUDE.mdを基盤として、マルチAI協調による高品質な開発を進めてください。