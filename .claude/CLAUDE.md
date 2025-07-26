# CLAUDE.md - Vue.js + Supabase 仕様書駆動開発

このファイルは、Claude Code がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

Vue.js (Composition API) + Supabase を使用した現代的なWebアプリケーション開発プロジェクトです。
仕様書駆動開発により、品質と保守性を重視した開発を行います。

## 技術スタック

### フロントエンド
- **フレームワーク**: Vue.js 3.x (Composition API)
- **状態管理**: Pinia
- **ルーティング**: Vue Router
- **スタイリング**: Tailwind CSS + DaisyUI
- **ビルドツール**: Vite
- **言語**: JavaScript (ES2015+)

### バックエンド・インフラ
- **データベース**: Supabase (PostgreSQL)
- **認証**: Supabase Auth
- **ストレージ**: Supabase Storage
- **ホスティング**: Vercel / Netlify

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
├── services/            # API・外部サービス連携
├── utils/               # ユーティリティ関数
├── types/               # TypeScript型定義 (JSDocで型安全性を確保)
└── assets/              # 静的ファイル
```

### 設計パターン
1. **コンポーザブルパターン**: ロジックの再利用性を重視
2. **ストアパターン**: Piniaによる状態管理の統一
3. **サービス層**: Supabase操作の抽象化
4. **コンテナ・プレゼンテーション分離**: ロジックとUIの分離

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

### Supabase 連携ルール
- **サービス層の使用**: 直接的なSupabase呼び出しを避け、サービス層経由で実行
- **エラーハンドリング**: Supabaseエラーの適切な処理とユーザーフレンドリーなメッセージ
- **型安全性**: Supabaseクライアントの型定義を活用
- **認証状態管理**: Pinia ストアでの一元管理

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
4. **Supabase最適化**: RLSポリシーとリアルタイム機能の積極活用
5. **パフォーマンス重視**: Vue 3 の新機能（Suspense、Teleport等）の活用

## よくある落とし穴

1. **リアクティビティの破壊**: オブジェクトの分割代入に注意
2. **Pinia ストアの初期化**: SSRモードでの注意点
3. **Supabase セッション管理**: ブラウザリフレッシュ時の状態復元
4. **DaisyUI テーマ**: 動的テーマ切り替え時のちらつき対策
5. **Vue Router**: 動的ルートでのコンポーネント再利用問題

## ドキュメント参照ガイド

### プロジェクト概要・要件
- **`.claude/00_project/01_project_concept.md`** - プロジェクトのビジョンと目標
- **`.claude/00_project/02_tech_stack_guidelines.md`** - 技術選定の根拠と指針

### 技術設計ドキュメント
- **`.claude/01_development_docs/01_architecture_design.md`** - 全体アーキテクチャ
- **`.claude/01_development_docs/02_database_design.md`** - Supabase データベース設計
- **`.claude/01_development_docs/03_api_design.md`** - Supabase API 設計
- **`.claude/01_development_docs/04_component_design.md`** - Vue コンポーネント設計
- **`.claude/01_development_docs/05_state_management_design.md`** - Pinia ストア設計
- **`.claude/01_development_docs/06_routing_design.md`** - Vue Router 設計
- **`.claude/01_development_docs/07_error_handling_design.md`** - エラーハンドリング戦略
- **`.claude/01_development_docs/08_type_definitions.md`** - 型定義と JSDoc 規約

### デザインシステム
- **`.claude/02_design_system/00_design_overview.md`** - デザインシステム概要
- **`.claude/02_design_system/01_tailwind_config.md`** - Tailwind CSS 設定
- **`.claude/02_design_system/02_daisyui_components.md`** - DaisyUI コンポーネント使用指針
- **`.claude/02_design_system/03_vue_component_patterns.md`** - Vue コンポーネントパターン

### ライブラリ固有情報
- **`.claude/03_library_docs/01_vue_composition_patterns.md`** - Vue Composition API パターン集
- **`.claude/03_library_docs/02_pinia_store_patterns.md`** - Pinia ストアパターン集
- **`.claude/03_library_docs/03_supabase_integration.md`** - Supabase 統合ガイド
- **`.claude/03_library_docs/04_vite_configuration.md`** - Vite 設定とプラグイン

### タスク別クイックリファレンス

| タスク | 主要参照ドキュメント |
|-------|-------------------|
| 新機能追加 | アーキテクチャ → データベース → API → コンポーネント設計 |
| 新しいページ作成 | ルーティング → コンポーネント → 状態管理 |
| データベース変更 | データベース設計 → API設計 → 型定義 |
| UI実装 | コンポーネント設計 → DaisyUI → Tailwind設定 |
| 状態管理 | Pinia パターン → 状態管理設計 |
| 認証機能 | Supabase統合 → エラーハンドリング |
| API連携 | Supabase統合 → API設計 |
| テスト作成 | テスト戦略 → Vue Composition パターン |

このCLAUDE.mdを基盤として、各段階でのドキュメント作成と実装を進めてください。