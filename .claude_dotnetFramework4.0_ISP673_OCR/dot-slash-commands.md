# .NET Framework 4.0 Windows Forms カスタムコマンド一覧

このドキュメントは、.NET Framework 4.0 Windows Formsプロジェクトで利用可能なカスタムコマンドの完全なリストです。

## 🧠 Claude Code - 技術実装・品質保証系 (12コマンド)

### /spec - 統合開発フロー
仕様書駆動開発の全体フローを管理します。
```bash
/spec
/spec multiAI
```

### /requirements - 要件定義
プロジェクトの要件定義書を生成します。
```bash
/requirements "Windows XP対応業務管理システム"
```

### /design - 技術設計
詳細な技術設計書を作成します。
```bash
/design
/design detailed
```

### /tasks - タスク管理
開発タスクの分割と管理を行います。
```bash
/tasks
/tasks create "MVP実装"
```

### /analyze - プロジェクト分析
コードベースの分析とボトルネック検出を行います。
```bash
/analyze
/analyze performance
```

### /enhance - 機能追加・改善
新機能の追加や既存機能の改善を行います。
```bash
/enhance "レポート出力機能"
```

### /fix - バグ修正
バグの修正と問題解決を支援します。
```bash
/fix "DataGridViewの表示エラー"
```

### /refactor - リファクタリング
コードのリファクタリングを実行します。
```bash
/refactor
/refactor mvp_pattern
```

### /document - ドキュメント生成
自動ドキュメント生成を行います。
```bash
/document
/document api_reference
```

### /standardize - コード標準化
コードの標準化とベストプラクティスを適用します。
```bash
/standardize
/standardize naming_conventions
```

### /winforms-patterns - Windows Forms設計パターン
.NET Framework 4.0対応のWindows Forms設計パターンを適用します。
```bash
/winforms-patterns mvp
/winforms-patterns factory_di
/winforms-patterns repository
/winforms-patterns observer_dotnet40
```

### /legacy-integration - レガシーシステム統合
既存システムとの統合パターンを実装します。
```bash
/legacy-integration com_wrapper
/legacy-integration active_directory
/legacy-integration legacy_db
```

## 📊 Gemini CLI - データ分析・戦略系 (3コマンド)

### /research - 市場分析・調査
デスクトップアプリケーション市場の分析とユーザー調査を行います。
```bash
/research desktop_analysis
/research user_behavior
/research competitor_analysis
```

### /content-strategy - コンテンツ戦略
ブランディングとUX戦略を策定します。
```bash
/content-strategy branding
/content-strategy user_journey
/content-strategy desktop_ux
```

### /product-plan - プロダクト企画
ロードマップと機能仕様を策定します。
```bash
/product-plan roadmap
/product-plan feature_specs
/product-plan priority_matrix
```

## 🏗️ OpenAI o3 MCP - インフラ・運用系 (3コマンド)

### /architecture - システムアーキテクチャ
デスクトップアプリケーションのアーキテクチャ設計を行います。
```bash
/architecture desktop_design
/architecture legacy_integration
/architecture scalability
```

### /devops - DevOps・自動化
CI/CDパイプラインとデプロイメント自動化を設定します。
```bash
/devops ci_pipeline
/devops clickonce_automation
/devops msi_creation
```

### /security - セキュリティ設計
セキュリティ設計と監査を実施します。
```bash
/security threat_analysis
/security code_signing
/security audit_logging
```

## 🔧 使用例

### 新規プロジェクト開始
```bash
# マルチAI協調開発フロー
/spec multiAI

# 個別フェーズ実行
/research desktop_analysis
/requirements "Windows XP対応販売管理システム"
/architecture desktop_design
/winforms-patterns mvp
```

### 既存プロジェクト改善
```bash
# 分析と改善
/analyze
/fix "メモリリーク問題"
/refactor mvp_pattern
/standardize
```

### レガシーシステム統合
```bash
# 統合パターン適用
/legacy-integration com_wrapper
/legacy-integration active_directory
/security audit_logging
```

## 📝 関連ドキュメント

- [CLAUDE.md](CLAUDE.md) - マルチAI統合ガイド
- [Windows XP/2003デプロイメントガイド](03_library_docs/08_windows_xp_2003_deployment_guide.md)
- [.NET 4.0制限事項と回避策](03_library_docs/09_dotnet40_limitations_guide.md)

---

**💡 ヒント**: `/spec multiAI` でマルチAI協調開発を開始すると、各専門AIが連携して最適な開発フローを提供します。