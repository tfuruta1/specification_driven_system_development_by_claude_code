# 🔧 マルチAI協調ビルド/コンパイルサポートコマンド

**全プロジェクト対応・エラー自動診断・AI連携修復**

## 📋 概要

このコマンドセットは、.NET Framework 4.8/4.0、ISP-673 OCR、VB6プロジェクトのビルド/コンパイルエラーを、Claude Code、Gemini CLI、o3 MCPの3つのAIが協調して解決するための統合コマンドシステムです。

## 🎯 コマンド一覧

### 統合診断コマンド

#### `/build-diagnose`
**説明**: プロジェクトタイプを自動判定し、適切なビルド診断を実行

```bash
# 使用例
/build-diagnose --project="YourSolution.sln"
/build-diagnose --project="MyProject.vbp"
/build-diagnose --auto-detect
```

**オプション**:
- `--project`: プロジェクトファイルパス
- `--auto-detect`: カレントディレクトリから自動検出
- `--ai`: 使用するAI（all/claude/gemini/o3）
- `--verbose`: 詳細ログ出力

### プロジェクト別診断コマンド

#### `/net48-build-diagnose`
**.NET Framework 4.8専用ビルド診断**

```bash
/net48-build-diagnose --solution="Enterprise.sln" --deep-scan
```

**診断項目**:
- NuGetパッケージ整合性
- 参照アセンブリ検証
- プラットフォーム設定
- ターゲットフレームワーク確認

#### `/net40-build-diagnose`
**.NET Framework 4.0専用ビルド診断（レガシー対応）**

```bash
/net40-build-diagnose --check-xp-compatibility --verify-language-version
```

**診断項目**:
- C# 4.0言語機能制限チェック
- Windows XP互換性確認
- 使用不可API検出
- レガシーパッケージ互換性

#### `/ocr-build-diagnose`
**ISP-673 OCR専用ビルド診断**

```bash
/ocr-build-diagnose --verify-x86 --check-com-registration
```

**診断項目**:
- x86プラットフォーム強制確認
- COM DLL登録状態
- OCRランタイム依存関係
- メモリ管理実装確認

#### `/vb6-compile-diagnose`
**VB6専用コンパイル診断**

```bash
/vb6-compile-diagnose --check-sjis --verify-references
```

**診断項目**:
- SJIS文字コード確認
- 参照設定検証
- COM/ActiveX登録状態
- Option Explicit使用確認

## 🤖 AI協調機能

### Claude Code（実装・修正）

#### `/fix-build-errors`
**ビルドエラー自動修正**

```bash
# 構文エラー修正
/fix-build-errors --type=syntax --auto-fix

# 参照エラー修正
/fix-build-errors --type=reference --add-missing

# 型エラー修正
/fix-build-errors --type=type-mismatch --suggest
```

#### `/convert-to-compatible`
**互換性のあるコードへの変換**

```bash
# .NET 4.0互換への変換
/convert-to-compatible --target=net40 --remove-async

# VB6 SJIS変換
/convert-to-compatible --target=vb6 --encoding=sjis
```

### Gemini CLI（分析・最適化）

#### `/analyze-build-log`
**ビルドログ詳細分析**

```bash
/analyze-build-log --file="build.log" --pattern-analysis
```

**分析内容**:
- エラーパターン識別
- 根本原因分析
- 依存関係マッピング
- 最適化提案

#### `/optimize-build-performance`
**ビルドパフォーマンス最適化**

```bash
/optimize-build-performance --parallel --cache-optimization
```

### o3 MCP（環境・インフラ）

#### `/check-build-environment`
**ビルド環境総合診断**

```bash
/check-build-environment --deep-scan --fix-permissions
```

**チェック項目**:
- SDK/ツールインストール状態
- 環境変数設定
- ファイルシステム権限
- レジストリ設定

#### `/setup-build-infrastructure`
**ビルドインフラ自動構築**

```bash
/setup-build-infrastructure --ci-cd --automated-testing
```

## 🔄 統合ワークフロー

### 自動エラー解決フロー

```bash
# ステップ1: 総合診断
/build-diagnose --auto-detect --ai=all

# ステップ2: エラー分類
/categorize-errors --group-by-type

# ステップ3: AI別対応割り当て
/assign-to-ai --optimize-resolution

# ステップ4: 並列修復実行
/execute-fixes --parallel --verify

# ステップ5: 再ビルド確認
/verify-build --clean-build
```

### プロジェクト別ワークフロー

#### .NET Framework 4.8
```bash
/net48-build-diagnose
/fix-nuget-packages --restore
/update-references --verify
/build --configuration=Release
```

#### .NET Framework 4.0
```bash
/net40-build-diagnose
/convert-modern-syntax --to-net40
/fix-package-compatibility
/build --platform=x86
```

#### ISP-673 OCR
```bash
/ocr-build-diagnose
/register-com-components --admin
/enforce-x86-platform
/build --verify-output
```

#### VB6
```bash
/vb6-compile-diagnose
/fix-encoding --to-sjis
/register-activex-controls
/compile --make-exe
```

## 📊 レポート機能

### `/generate-build-report`
**ビルド診断レポート生成**

```bash
/generate-build-report --format=html --include-recommendations
```

**レポート内容**:
- エラー統計
- 解決済み/未解決項目
- AI別対応実績
- 推奨アクション

## 🆘 緊急サポート

### `/build-emergency-support`
**緊急ビルドサポート起動**

```bash
/build-emergency-support --priority=critical --escalate
```

**機能**:
- 全AI同時起動
- リアルタイム診断
- 優先度付き修復
- エスカレーション通知

## 💡 使用例

### ケース1: 参照エラーの解決
```bash
# 診断実行
/build-diagnose --project="MyApp.sln"
# 出力: 5個の参照エラーを検出

# AI協調修復
/fix-build-errors --type=reference --ai=all
# Claude: NuGetパッケージ復元
# Gemini: 依存関係分析
# o3: 環境設定確認

# 再ビルド
/build --verify
```

### ケース2: プラットフォームエラー
```bash
# OCRプロジェクト診断
/ocr-build-diagnose
# 出力: x86プラットフォーム不一致

# 自動修正
/enforce-x86-platform --all-projects
/verify-com-registration
/build --platform=x86
```

### ケース3: レガシー移行
```bash
# VB6プロジェクト診断
/vb6-compile-diagnose --project="Legacy.vbp"

# 文字コード修正
/fix-encoding --to-sjis --all-files

# 参照修復
/fix-vb6-references --auto-resolve

# コンパイル実行
/compile-vb6 --output="Legacy.exe"
```

## 🔧 カスタマイズ

### 設定ファイル
```json
{
  "buildSupport": {
    "defaultAI": "all",
    "autoFix": true,
    "verboseLogging": false,
    "parallelExecution": true,
    "emergencyThreshold": 10
  }
}
```

### 拡張コマンド作成
```bash
# カスタムビルドフロー定義
/define-build-flow --name="MyCustomFlow" --steps="diagnose,fix,verify"

# 実行
/run-build-flow --name="MyCustomFlow"
```

---

**🚀 クイックスタート**: ビルドエラーが発生したら、まず `/build-diagnose --auto-detect` を実行してください。AIが自動的に問題を分析し、最適な解決策を提示します。