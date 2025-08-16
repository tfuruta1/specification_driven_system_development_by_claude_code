# 📚 統合SDD仕様 - 新規開発と既存プロジェクト解析の統一フレームワーク

## 🎯 概要
KIRO方式のSDD（仕様書駆動開発）を拡張し、新規開発と既存プロジェクト解析の両方に対応した統合フレームワークを提供します。

## 🔄 2つの開発パス

### Path A: 新規開発（KIRO方式）
```mermaid
graph TD
    A[プロジェクト開始] --> B[/steering]
    B --> C[/spec-init]
    C --> D[要件定義書作成]
    D --> E[承認ゲート]
    E --> F[技術設計書作成]
    F --> G[承認ゲート]
    G --> H[タスク分解]
    H --> I[承認ゲート]
    I --> J[実装開始]
    J --> K[ソースコード生成]
```

### Path B: 既存プロジェクト解析・修正
```mermaid
graph TD
    A[既存プロジェクト] --> B[/analyze]
    B --> C[ソースコード解析]
    C --> D[要件定義書自動生成]
    C --> E[技術設計書自動生成]
    D --> F[修正要求受付]
    E --> F
    F --> G[詳細影響分析]
    G --> H[修正要件定義書作成]
    H --> I[修正技術設計書作成]
    I --> J[承認ゲート]
    J --> K[TDD: テストコード作成]
    K --> L[TDD: 実装]
    L --> M[TDD: リファクタリング]
    M --> N[設計書自動更新]
```

## 📋 統合コマンド体系

### 共通コマンド

#### /project-type - プロジェクトタイプの設定
```bash
# 新規開発モード
/project-type new

# 既存プロジェクト解析モード
/project-type existing [project-path]

# ハイブリッドモード（既存を拡張）
/project-type hybrid [project-path]
```

### 新規開発用コマンド（Path A）

#### /steering - プロジェクトステアリング
```bash
# プロジェクトの方向性を定義
/steering
  - ゴール設定
  - 制約条件定義
  - 優先順位設定
  - ステークホルダー定義
```

#### /spec-init - 仕様初期化
```bash
# プロジェクト仕様の初期化
/spec-init [project-name]
  - プロジェクト概要作成
  - スコープ定義
  - 基本アーキテクチャ決定
```

#### /spec-requirements - 要件定義書作成
```bash
# 要件定義書を段階的に作成
/spec-requirements [feature-name]
  - 機能要件の定義
  - 非機能要件の定義
  - 制約事項の明確化
  → [人間によるレビューと承認]
```

#### /spec-design - 技術設計書作成
```bash
# 技術設計書を作成
/spec-design [feature-name]
  - アーキテクチャ設計
  - モジュール設計
  - インターフェース定義
  - データモデル設計
  → [人間によるレビューと承認]
```

#### /spec-tasks - タスク分解
```bash
# 実装タスクへの分解
/spec-tasks [feature-name]
  - 実装タスクリスト生成
  - 優先順位付け
  - 工数見積もり
  → [人間によるレビューと承認]
```

#### /spec-implement - 実装開始
```bash
# 承認された仕様に基づいて実装
/spec-implement [task-id]
  - コード生成
  - テスト作成
  - ドキュメント更新
```

### 既存プロジェクト解析・修正用コマンド（Path B）

#### /analyze - プロジェクト解析
```bash
# 初回解析（設計書生成）
/analyze [project-path] --generate-docs
  - ソースコード全体解析
  - 要件定義書自動生成
  - 技術設計書自動生成

# 高速解析（キャッシュ活用）
/analyze [project-path] --use-cache
  - 設計書から情報取得
  - 差分のみ再解析
  - 設計書自動更新

# 特定機能の解析
/analyze [project-path] --feature [feature-name]
```

#### /modify-request - 修正要求分析
```bash
# 修正要求の詳細分析
/modify-request [description]
  - 修正内容の理解と明確化
  - 影響範囲の特定
  - 潜在的な課題の洗い出し
  - リスク評価
  → [分析結果のレビュー]
```

#### /modify-requirements - 修正要件定義
```bash
# 修正のための要件定義書作成
/modify-requirements [modification-id]
  - 現状（AS-IS）の明確化
  - 目標（TO-BE）の定義
  - 受入条件の設定
  - 制約事項の確認
  → [要件の承認]
```

#### /modify-design - 修正設計
```bash
# 包括的な修正設計書作成
/modify-design [modification-id]
  - アーキテクチャへの影響分析
  - インターフェース変更設計
  - データモデル変更設計
  - 後方互換性の確保
  - テスト戦略の策定
  → [設計の承認]
```

#### /tdd-start - TDD駆動開発開始
```bash
# テスト駆動開発への移行
/tdd-start [modification-id]
  - テストケース作成（Red）
  - 最小限の実装（Green）
  - リファクタリング（Refactor）
  - 継続的なテスト実行
```

#### /reverse-spec - リバースエンジニアリング
```bash
# ソースコードから仕様を逆生成
/reverse-spec [module-path]
  - コードから要件を抽出
  - 実装から設計を推測
  - ドキュメント生成
```

#### /sync-docs - 設計書同期
```bash
# 設計書とソースコードの同期
/sync-docs [project-path]
  - 差分検出
  - 自動更新
  - 競合解決
```

### 共通管理コマンド

#### /spec-status - 進捗状況
```bash
# プロジェクト全体の状況確認
/spec-status
  - 各フェーズの完了率
  - 承認待ち項目
  - ブロッカー表示
  - 次のアクション提示
```

#### /spec-history - 変更履歴
```bash
# 仕様変更の履歴表示
/spec-history [--since date]
  - 要件変更履歴
  - 設計変更履歴
  - 承認履歴
```

## 📁 統合ディレクトリ構造

```
.claude_sub_agent/
├── steering/                # プロジェクトステアリング
│   └── [project-name]/
│       ├── goals.md
│       ├── constraints.md
│       └── stakeholders.md
├── specs/
│   ├── new/                # 新規開発プロジェクト
│   │   └── [project-name]/
│   │       ├── requirements/
│   │       │   ├── draft/      # 作成中
│   │       │   ├── approved/   # 承認済み
│   │       │   └── history/    # 変更履歴
│   │       ├── design/
│   │       │   ├── draft/
│   │       │   ├── approved/
│   │       │   └── history/
│   │       └── tasks/
│   │           ├── backlog/
│   │           ├── in-progress/
│   │           └── completed/
│   └── existing/           # 既存プロジェクト解析
│       └── [project-name]/
│           ├── requirements/
│           │   ├── current.md
│           │   ├── checksums.json
│           │   └── history/
│           └── design/
│               ├── current.md
│               ├── checksums.json
│               └── history/
├── progress/               # 進捗管理
│   └── [project-name]/
│       ├── status.json
│       ├── metrics.json
│       └── reports/
└── templates/             # テンプレート
    ├── requirements.md
    ├── design.md
    └── tasks.md
```

## 🔄 統合ワークフロー

### 新規開発時のフロー
```
1. /project-type new
2. /steering
3. /spec-init "プロジェクト名"
4. /spec-requirements "機能名"
   → レビュー & 承認
5. /spec-design "機能名"
   → レビュー & 承認
6. /spec-tasks "機能名"
   → レビュー & 承認
7. /spec-implement
8. /spec-status （進捗確認）
```

### 既存プロジェクト解析・修正時のフロー
```
【初回解析】
1. /project-type existing "path/to/project"
2. /analyze --generate-docs
3. 要件定義書・技術設計書のレビュー

【修正実装時】※重要: すぐにコーディングせず、以下のフローに従う
1. /modify-request "修正内容の説明"
   → 詳細分析・影響範囲特定・潜在的課題の洗い出し
2. /modify-requirements
   → 修正要件定義書作成 & 承認
3. /modify-design
   → 包括的な修正設計書作成 & 承認
4. /tdd-start
   → テストコード作成（Red）
   → 最小限の実装（Green）
   → リファクタリング（Refactor）
5. /sync-docs
   → 設計書自動更新

【2回目以降の解析】
1. /analyze --use-cache （高速解析）
```

### ハイブリッド開発のフロー
```
1. /project-type hybrid "path/to/project"
2. /analyze --generate-docs （既存部分の解析）
3. /spec-requirements "新機能名" （新機能の要件定義）
4. /spec-design "新機能名" （新機能の設計）
5. /spec-implement （統合実装）
6. /sync-docs （全体の設計書更新）
```

## 📊 モード別の特徴

### 新規開発モード
- **特徴**: 仕様先行、段階的承認
- **利点**: 品質保証、手戻り削減
- **適用**: グリーンフィールドプロジェクト

### 既存解析モード
- **特徴**: コード先行、自動ドキュメント化
- **利点**: 高速解析、保守性向上
- **適用**: レガシーシステム、リファクタリング

### ハイブリッドモード
- **特徴**: 既存拡張、段階的モダナイゼーション
- **利点**: リスク最小化、継続的改善
- **適用**: 機能追加、システム統合

## 🤖 AI活用マトリクス

| フェーズ | 新規開発 | 既存解析 | 使用AI |
|---------|----------|----------|--------|
| 要件定義 | 作成支援 | 自動抽出 | Gemini-CLI |
| 技術設計 | 設計支援 | 自動生成 | o3 MCP |
| タスク分解 | 提案 | 影響分析 | Claude Code |
| 実装 | コード生成 | リファクタリング | Claude Code |
| テスト | テスト生成 | カバレッジ分析 | 全AI連携 |

## ⚠️ 重要な原則

### 新規開発時
1. **仕様が正**: 承認された仕様書に従って実装
2. **段階的承認**: 各フェーズで人間のレビュー必須
3. **トレーサビリティ**: 要件から実装まで追跡可能

### 既存解析時
1. **コードが正**: ソースコードを真実の源泉とする
2. **自動同期**: 設計書は常にコードに追従
3. **効率重視**: キャッシュ活用で解析時間短縮

### 共通原則
1. **透明性**: 進捗と状態を常に可視化
2. **品質**: 自動チェックと人間レビューの組み合わせ
3. **柔軟性**: プロジェクトに応じてモード切り替え可能

## 🚀 実装ロードマップ

### Phase 1: 基盤構築（1週間）
- [ ] 統合コマンドフレームワーク
- [ ] プロジェクトタイプ管理
- [ ] 基本ディレクトリ構造

### Phase 2: 新規開発パス（2週間）
- [ ] /steering, /spec-init実装
- [ ] 要件定義書作成機能
- [ ] 技術設計書作成機能
- [ ] 承認ワークフロー

### Phase 3: 既存解析パス（2週間）
- [ ] /analyze実装
- [ ] 自動ドキュメント生成
- [ ] キャッシュシステム
- [ ] 差分検出

### Phase 4: 統合機能（1ヶ月）
- [ ] ハイブリッドモード
- [ ] 進捗管理ダッシュボード
- [ ] MCP完全統合
- [ ] Git hooks連携

---

*この統合SDD仕様により、新規開発と既存プロジェクト解析の両方で、効率的かつ高品質な開発が可能になります。*