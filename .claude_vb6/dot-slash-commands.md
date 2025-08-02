# VB6 カスタムコマンド使用ガイド

## 📋 コマンド一覧（25個）

### 🔍 分析系コマンド（5個）

#### `/vb6-analyze-code <project_path>`
VB6コードの静的解析を実行。複雑度、品質メトリクス、技術的負債を測定します。

```bash
# 使用例
/vb6-analyze-code "C:\Projects\MyVB6App" --metrics --complexity

# 出力例
=== VB6 Code Analysis Report ===
Total Files: 156
Total Lines: 45,230
Cyclomatic Complexity: 
  - High (>10): 23 methods
  - Medium (5-10): 67 methods
  - Low (<5): 234 methods
Technical Debt: 156 hours
```

#### `/vb6-check-dependencies`
プロジェクトの依存関係を完全チェック。COM、DLL、OCXの状態を確認します。

```bash
# 使用例
/vb6-check-dependencies

# 出力例
=== Dependency Check ===
✓ MSCOMCTL.OCX (v6.0) - Registered
✓ COMDLG32.OCX (v6.0) - Registered
✗ CustomLib.dll - Not found
✗ MSCAL.OCX - Not registered
```

#### `/vb6-com-inventory <project_path>`
COM/ActiveXコンポーネントの完全な調査を実行します。

```bash
# 使用例
/vb6-com-inventory "C:\Projects\MyVB6App"

# バージョン情報と登録状態を含む詳細レポート
```

#### `/vb6-api-usage-scan <project_path>`
Win32 API使用箇所を一覧化し、.NET代替案を提示します。

```bash
# 使用例
/vb6-api-usage-scan "C:\Projects\MyVB6App"
```

#### `/vb6-analyze-performance <file>`
パフォーマンスボトルネックを特定し、最適化提案を行います。

```bash
# 使用例
/vb6-analyze-performance "MainForm.frm"
```

### 🛠️ 開発支援コマンド（10個）

#### `/vb6-add-module <type> <name>`
新しいモジュールを追加（SJIS文字コードで保存）

```bash
# 使用例
/vb6-add-module bas CommonUtils
/vb6-add-module cls CustomerService
/vb6-add-module frm SettingsDialog

# 自動的にプロジェクトファイル(.vbp)も更新
```

#### `/vb6-add-error-handling <file> <procedure>`
包括的なエラーハンドリングを追加

```bash
# 使用例
/vb6-add-error-handling "Customer.cls" "SaveCustomer"
/vb6-add-error-handling "MainForm.frm" "*"  # 全プロシージャ

# 追加されるコード例：
' On Error GoTo ErrorHandler
' ... 処理 ...
' Exit Sub/Function
' ErrorHandler:
'     LogError "ProcedureName", Err.Number, Err.Description
```

#### `/vb6-create-dao <entity>`
データアクセスオブジェクト(DAO)クラスを自動生成

```bash
# 使用例
/vb6-create-dao Customer
/vb6-create-dao Order

# 生成される機能：
# - CRUD操作（Create, Read, Update, Delete）
# - トランザクション管理
# - エラーハンドリング
```

#### `/vb6-create-project <name> <type>`
標準構造で新規プロジェクトを作成

```bash
# 使用例
/vb6-create-project "InventorySystem" exe
/vb6-create-project "BusinessLogic" dll
/vb6-create-project "CustomControls" ocx
```

#### `/vb6-create-form <name> <type>`
フォームテンプレートを作成

```bash
# 使用例
/vb6-create-form "CustomerEdit" dialog
/vb6-create-form "MainWindow" mdi
/vb6-create-form "ReportView" standard
```

#### `/vb6-generate-interface <name> <methods>`
インターフェースクラスを生成

```bash
# 使用例
/vb6-generate-interface "IRepository" "GetById,GetAll,Save,Delete"
```

#### `/vb6-create-unittest <class>`
VB6Unitフレームワーク用のユニットテストを生成

```bash
# 使用例
/vb6-create-unittest CustomerService
```

#### `/vb6-optimize-db <file>`
データベースアクセスコードを最適化

```bash
# 使用例
/vb6-optimize-db "DataAccess.bas"

# 最適化内容：
# - N+1問題の解決
# - 接続プーリング実装
# - パラメータ化クエリ変換
```

#### `/vb6-refactor-to-patterns <file> <pattern>`
デザインパターンへのリファクタリング

```bash
# 使用例
/vb6-refactor-to-patterns "AppConfig.cls" singleton
/vb6-refactor-to-patterns "DocumentCreator.cls" factory
/vb6-refactor-to-patterns "EventManager.cls" observer
```

#### `/vb6-add-com-reference <project> <component>`
COMコンポーネント参照を追加

```bash
# 使用例
/vb6-add-com-reference "MyProject.vbp" "Microsoft Excel 16.0 Object Library"
/vb6-add-com-reference "MyProject.vbp" "{00020813-0000-0000-C000-000000000046}"
```

### 🔨 ビルド・デプロイコマンド（5個）

#### `/vb6-build <project>`
プロジェクトをビルド

```bash
# 使用例
/vb6-build "MyProject.vbp"

# ログ出力付きビルド
```

#### `/vb6-compile-check`
コンパイルチェックとエラー診断

```bash
# 使用例
/vb6-compile-check

# エラーがある場合は修正提案も表示
```

#### `/vb6-create-installer <project>`
Inno Setupインストーラーを作成

```bash
# 使用例
/vb6-create-installer "MyProject.vbp"

# 生成内容：
# - 依存ファイルリスト
# - レジストリ設定
# - アンインストール処理
```

#### `/vb6-setup-ci <project> <platform>`
CI/CDパイプラインを設定

```bash
# 使用例
/vb6-setup-ci "MyProject.vbp" jenkins
/vb6-setup-ci "MyProject.vbp" azure-devops
```

#### `/vb6-generate-documentation <project>`
プロジェクトドキュメントを自動生成

```bash
# 使用例
/vb6-generate-documentation "C:\Projects\MyVB6App"

# 生成内容：
# - クラス・モジュール一覧
# - API仕様書
# - 依存関係図
```

### 🚀 移行支援コマンド（5個）

#### `/vb6-migration-assessment <project>`
.NET移行の実現可能性を評価

```bash
# 使用例
/vb6-migration-assessment "C:\Projects\MyVB6App"

# 評価レポート：
# - 移行難易度: 中
# - 推定工数: 320時間
# - 非互換機能: 15件
# - 推奨移行戦略: 段階的移行
```

#### `/vb6-convert-to-net <file>`
.NET Framework 4.0/4.8向けに変換準備

```bash
# 使用例
/vb6-convert-to-net "Customer.cls"

# 変換に必要な修正箇所をマーク
```

#### `/vb6-check-security <path>`
セキュリティ脆弱性をチェック

```bash
# 使用例
/vb6-check-security "C:\Projects\MyVB6App"

# チェック項目：
# - SQLインジェクション
# - ハードコードされた認証情報
# - 安全でないファイル操作
```

#### `/vb6-database-extract <project_path>`
データベーススキーマを抽出

```bash
# 使用例
/vb6-database-extract "C:\Projects\MyVB6App"

# 抽出内容：
# - 接続文字列
# - 使用テーブル・ビュー
# - ストアドプロシージャ
```

#### `/vb6-generate-report <name> <datasource>`
Crystal Reportsレポートテンプレートを生成

```bash
# 使用例
/vb6-generate-report "SalesReport" "vw_Sales"
```

## 🎯 使用例シナリオ

### 1. 新規プロジェクト開始
```bash
# プロジェクト作成
/vb6-create-project "OrderManagement" exe

# 基本モジュール追加
/vb6-add-module bas GlobalConstants
/vb6-add-module cls DatabaseConnection
/vb6-create-form "MainMenu" mdi

# エラーハンドリング追加
/vb6-add-error-handling "*" "*"
```

### 2. 既存プロジェクト分析
```bash
# 完全分析
/vb6-analyze-code "C:\Legacy\OrderSystem"
/vb6-check-dependencies
/vb6-com-inventory "C:\Legacy\OrderSystem"
/vb6-api-usage-scan "C:\Legacy\OrderSystem"
/vb6-check-security "C:\Legacy\OrderSystem"
```

### 3. パフォーマンス改善
```bash
# ボトルネック特定
/vb6-analyze-performance "DataProcess.bas"

# データベース最適化
/vb6-optimize-db "OrderDAO.cls"

# リファクタリング
/vb6-refactor-to-patterns "OrderFactory.cls" factory
```

### 4. 移行準備
```bash
# 移行評価
/vb6-migration-assessment "C:\Legacy\OrderSystem"

# 段階的移行準備
/vb6-convert-to-net "Customer.cls"
/vb6-convert-to-net "Order.cls"

# ドキュメント生成
/vb6-generate-documentation "C:\Legacy\OrderSystem"
```

## 💡 Tips

1. **文字コード注意**: VB6ファイルの編集コマンドは自動的にSJISで保存
2. **依存関係確認**: 新規モジュール追加前に`/vb6-check-dependencies`実行推奨
3. **バッチ処理**: 複数のコマンドをスクリプト化して一括実行可能
4. **エラー時**: `/vb6-compile-check`で詳細なエラー情報と修正提案を取得

## 🔗 関連ドキュメント

- [architecture.md](./architecture.md) - アーキテクチャパターン詳細
- [legacy-integration.md](./legacy-integration.md) - レガシーシステム統合
- [CLAUDE.md](./CLAUDE.md) - プロジェクト概要

---

**注意**: すべてのコマンドは`.claude`フォルダ内で実行してください。