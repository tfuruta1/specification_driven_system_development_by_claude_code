# 🖥️ .NET Framework 4.0 デスクトップアプリ - カスタムコマンド統合ガイド

**18コマンド体系 - マルチAI協調システム対応**

## 📋 コマンド概要

このディレクトリには、.NET Framework 4.0デスクトップアプリケーション開発に特化した18個のマルチAIカスタムコマンドが含まれています。3つのAIシステムが専門領域を分担し、統合的な開発フローを提供します。

## 🤖 AI別コマンド分類

### 🧠 Claude Code - 技術実装・品質保証系 (12コマンド)
1. `spec.md` - 統合開発フロー管理
2. `requirements.md` - 要件定義書の生成
3. `design.md` - 技術設計書の作成
4. `tasks.md` - タスク分割とTodo管理
5. `analyze.md` - プロジェクト分析とボトルネック検出
6. `enhance.md` - 新機能の追加・既存機能の改善
7. `fix.md` - バグ修正と問題解決
8. `refactor.md` - コードリファクタリング
9. `document.md` - 自動ドキュメント生成
10. `standardize.md` - コード標準化とベストプラクティス適用
11. `winforms-patterns.md` - Windows Forms設計パターン適用
12. `legacy-integration.md` - レガシーシステム統合支援

### 📊 Gemini CLI - データ分析・戦略系 (3コマンド)
13. `research.md` - デスクトップアプリ市場分析・ユーザー行動分析
14. `content-strategy.md` - ブランディング・ペルソナ設計・UX戦略
15. `product-plan.md` - ロードマップ策定・機能仕様・優先度付け

### 🏗️ OpenAI o3 MCP - インフラ・運用系 (3コマンド)
16. `architecture.md` - デスクトップアプリアーキテクチャ・レガシー統合設計
17. `devops.md` - CI/CD・デプロイ自動化・ClickOnce配布
18. `security.md` - セキュリティ設計・脅威分析・監査

## 🚀 使用方法

### マルチAI統合開発フロー
```bash
# 統合開発フローの開始
/spec multiAI

# フェーズ別実行
/research desktop_analysis     # Phase 1: 戦略・企画
/architecture desktop_design  # Phase 2: システム設計  
/requirements "デスクトップアプリ" # Phase 3: 技術実装
```

### Windows Forms 特化開発
```bash
# Windows Forms MVPパターン適用
/winforms-patterns mvp

# レガシーシステム統合
/legacy-integration com_interop

# デスクトップアプリ最適化
/enhance desktop_performance
```

### 品質保証・運用
```bash
# プロジェクト分析
/analyze performance

# コード標準化
/standardize dotnet40_patterns

# セキュリティ監査
/security desktop_security
```

## 🎯 .NET Framework 4.0 特化機能

### 制限事項対応
- **async/await不可**: BackgroundWorker / ThreadPoolパターン提供
- **HttpClient不可**: WebClient / HttpWebRequestパターン提供
- **限定的TPL**: スレッド管理・並行処理パターン提供
- **NuGet制約**: packages.config手動管理サポート

### Windows XP/2003 対応
- **レガシーOS対応**: 互換性チェック・デプロイガイド
- **小さなフットプリント**: メモリ使用量最適化
- **COM統合**: 既存システム連携パターン
- **セキュリティ対応**: 企業環境・ドメイン認証

## 📁 コマンドファイル構成

各コマンドファイルには以下の構成が含まれています：

```
[コマンド名].md
├── コマンド概要・目的
├── 使用方法・パラメータ
├── .NET Framework 4.0 固有の制約・対応策
├── Windows XP/2003 対応事項
├── マルチAI連携ポイント
├── 実行例・サンプルコード
└── 関連コマンド・参考資料
```

## 🔗 関連ドキュメント

- `../CLAUDE.md` - プロジェクト全体ガイド
- `../00_project/` - プロジェクトコンセプト・技術スタック
- `../01_development_docs/` - 開発ドキュメント体系
- `../.tmp/` - マルチAI協調作業領域

---

**💡 Tip**: 初回は `/spec multiAI` で統合開発フローを開始することを推奨します。各AIの専門性を活かした効率的な開発が可能になります。