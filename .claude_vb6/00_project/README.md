# Visual Basic 6.0 レガシーシステム解析・移行プロジェクト

## プロジェクト概要

既存のVisual Basic 6.0レガシーシステムの解析、保守、修正、および.NET Framework 4.8への段階的移行を支援する専門プロジェクトです。新規開発ではなく、既存VB6資産の最大活用と安全な移行に特化しています。

## 主要機能

### 1. 🔍 レガシーコード解析
- **静的コード解析**: 複雑度、品質メトリクス、技術的負債の測定
- **依存関係分析**: プロジェクト間、COM/ActiveX、外部DLLの依存関係可視化
- **未使用コード検出**: デッドコード、到達不能コードの特定
- **移行リスク評価**: 自動移行可能率、手動作業量の見積もり

### 2. 🔧 安全な修正・保守
- **影響範囲分析**: 修正による影響を事前に評価
- **自動バックアップ**: 修正前の状態を自動保存
- **テスト生成**: 修正箇所の回帰テスト自動生成
- **段階的リファクタリング**: リスクを最小化した改善

### 3. 🚀 .NET Framework 4.8への移行
- **段階的移行**: データ層→ビジネス層→UI層の順次移行
- **COM相互運用**: 既存COMコンポーネントとの共存
- **並行実行テスト**: VB6/.NETの動作比較検証
- **ロールバック対応**: 問題発生時の迅速な復旧

## 必要環境

### 最小構成（基本解析）
- Windows 10/11
- .NET Framework 4.8
- Visual Studio 2019/2022

### 推奨構成（実用的な移行）
- 最小構成 + VB6ランタイム（msvbvm60.dll）
- 主要なVB6標準OCXコンポーネント

### 理想構成（完全な移行と検証）
- 推奨構成 + Visual Basic 6.0 SP6 IDE
- 対象プロジェクトの全依存コンポーネント

詳細は[移行環境要件ガイド](../03_migration_docs/migration_environment_requirements.md)を参照してください。

## カスタムコマンド（24個）

### 解析系コマンド（8個）
- `/analyze-vb6-code` - コード品質分析
- `/dependency-analysis` - 依存関係可視化
- `/find-obsolete-code` - 未使用コード検出
- `/api-usage-scan` - Win32 API使用調査
- `/com-inventory` - COM依存関係調査
- `/database-schema-extract` - DBスキーマ抽出
- `/ui-controls-map` - UIコントロールマッピング
- `/code-metrics` - 品質メトリクス測定

### 修正・保守系コマンド（8個）
- `/fix-vb6` - 安全な修正支援
- `/add-error-handling` - エラー処理追加
- `/refactor-vb6` - リファクタリング
- `/add-logging` - ログ機能追加
- `/optimize-performance` - パフォーマンス改善
- `/fix-memory-leaks` - メモリリーク修正
- `/update-db-connection` - DB接続更新
- `/modernize-ui` - UI部分改善

### 移行系コマンド（8個）
- `/migration-assessment` - 移行可能性評価
- `/migration-plan` - 移行計画策定
- `/migrate-to-net` - 移行実行
- `/validate-compatibility` - 互換性検証
- `/parallel-run-test` - 並行実行テスト
- `/data-migration` - データ移行
- `/com-wrapper-gen` - COMラッパー生成
- `/rollback-plan` - ロールバック計画

## ドキュメント構成

### 📁 01_analysis_docs/
- `code_analysis_guide.md` - VB6コード解析の手法と基準
- `dependency_mapping.md` - 依存関係の分析方法
- `risk_assessment_template.md` - リスク評価テンプレート

### 📁 02_maintenance_docs/
- `safe_modification_guide.md` - 安全な修正手順とベストプラクティス
- `testing_strategy.md` - テスト戦略
- `troubleshooting_guide.md` - トラブルシューティング

### 📁 03_migration_docs/
- `vb6_to_dotnet48_migration_patterns.md` - 具体的な移行パターン集
- `migration_environment_requirements.md` - 環境要件詳細
- `compatibility_matrix.md` - 互換性マトリクス

## 典型的なワークフロー

### 1. 初期解析（.NET環境のみで実行可能）
```bash
/analyze-vb6-code "C:\Legacy\MyVB6Project" --complexity
/dependency-analysis "C:\Legacy\MyVB6Project" --output-format html
/migration-assessment "C:\Legacy\MyVB6Project" --detailed-report
```

### 2. 保守作業
```bash
/fix-vb6 "CustomerID型変更" --analyze-impact
/add-error-handling module --pattern comprehensive
/add-logging info --output file
```

### 3. 段階的移行
```bash
# Phase 1: データアクセス層
/migrate-to-net --phase data_access --project "C:\Legacy\MyVB6Project"

# Phase 2: ビジネスロジック層
/migrate-to-net --phase business_logic --validate

# Phase 3: UI層
/migrate-to-net --phase ui --compatibility-mode
```

## 成功指標

### 解析フェーズ
- コードカバレッジ: 100%解析完了
- 依存関係: 完全マッピング
- リスク特定: 全リスク文書化

### 移行フェーズ
- 機能互換性: 100%維持
- 性能: 同等以上
- バグ密度: 既存以下

### 運用フェーズ
- 安定性: MTBF向上
- 保守性: 工数削減
- 拡張性: 新機能追加容易

## サポート

- **解析ツール**: analysis_tools/ ディレクトリ
- **移行ツール**: migration_tools/ ディレクトリ
- **カスタムコマンド**: commands/ ディレクトリ

---

VB6レガシーシステムの解析から移行まで、体系的かつ安全にサポートします。