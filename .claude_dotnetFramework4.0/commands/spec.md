# /spec - 統合開発フロー管理コマンド

**マルチAI協調による.NET Framework 4.0デスクトップアプリ開発フロー統括**

## 📋 コマンド概要

.NET Framework 4.0デスクトップアプリケーション開発における全フェーズ（戦略立案→システム設計→技術実装→品質保証→運用）をマルチAI協調で統括管理するメインコマンドです。

## 🚀 使用方法

### 基本構文
```bash
/spec [mode] [options]
```

### 主要モード

#### 1. マルチAI統合開発フロー
```bash
/spec multiAI
```
**実行内容**: 3階層AI協調による完全開発フロー
- Phase 1: Gemini CLI による戦略・市場分析
- Phase 2: o3 MCP によるシステム・セキュリティ設計
- Phase 3: Claude Code による技術実装・品質保証

#### 2. デスクトップアプリ特化フロー
```bash
/spec desktop_app [app_type]
```
**パラメータ**:
- `business` - 業務管理システム
- `tool` - システム管理ツール
- `integration` - レガシー統合アプリ

#### 3. Windows XP/2003 対応フロー
```bash
/spec legacy_compatible
```
**実行内容**: レガシーOS対応の完全フロー
- Windows XP SP3 / Windows Server 2003 R2 対応確認
- .NET Framework 4.0 制限事項チェック
- COM統合・ActiveDirectory連携設計

## 🎯 .NET Framework 4.0 特化機能

### 制限事項対応フロー
```bash
/spec dotnet40_constraints
```
**チェック項目**:
- ❌ async/await → ✅ BackgroundWorker/ThreadPool設計
- ❌ HttpClient → ✅ WebClient/HttpWebRequest設計
- ❌ CallerMemberName → ✅ 手動パラメータ指定設計
- ❌ Task.Run → ✅ ThreadPool.QueueUserWorkItem設計

### Windows Forms MVP設計フロー
```bash
/spec mvp_pattern
```
**設計要素**:
- Model: ビジネスロジック・データモデル
- View: Windows Forms UI (IView インターフェース)
- Presenter: MVP制御ロジック・イベント処理

## 🤖 マルチAI協調フロー詳細

### Phase 1: 戦略・企画 (Gemini CLI)
```mermaid
graph LR
    A[/research desktop_analysis] --> B[/content-strategy ux_design]
    B --> C[/product-plan feature_specs]
```

### Phase 2: システム設計 (o3 MCP) 
```mermaid
graph LR
    D[/architecture desktop_design] --> E[/security desktop_security]
    E --> F[/devops deployment_strategy]
```

### Phase 3: 技術実装 (Claude Code)
```mermaid
graph LR
    G[/requirements] --> H[/design]
    H --> I[/winforms-patterns mvp]
    I --> J[/legacy-integration]
```

## 💻 実行例

### 業務管理システム開発
```bash
# 統合開発フロー開始
/spec multiAI

# 続行コマンド例
/research "顧客管理システム市場分析"
/architecture "3層アーキテクチャ設計"
/requirements "顧客・売上・在庫管理システム"
/winforms-patterns mvp
```

### レガシーシステム統合
```bash
# レガシー対応フロー開始
/spec legacy_compatible

# COM統合設計
/legacy-integration com_interop

# ActiveDirectory認証設計
/security ad_integration
```

## 🔧 詳細オプション

### AI協調レベル設定
```bash
/spec multiAI --coordination=[level]
```
**レベル**:
- `full` - 全AIが全フェーズで協調 (デフォルト)
- `sequential` - 順次実行・結果引き継ぎ
- `parallel` - 並列実行・結果統合

### プロジェクト規模設定
```bash
/spec [mode] --scale=[size]
```
**規模**:
- `small` - 単独開発・プロトタイプ
- `medium` - チーム開発・企業システム (デフォルト)
- `large` - 大規模・エンタープライズシステム

### 対象OS設定
```bash
/spec [mode] --target_os=[os]
```
**対象OS**:
- `xp_2003` - Windows XP SP3 / Server 2003 R2
- `vista_2008` - Windows Vista / Server 2008以降
- `win7_plus` - Windows 7以降 (デフォルト)

## 📊 進捗管理・品質評価

### 自動進捗トラッキング
```json
{
  "project_id": "desktop_app_001",
  "phase": "implementation",
  "completion": "65%",
  "quality_score": 8.5,
  "ai_coordination": "active",
  "constraints_check": "dotnet40_compliant"
}
```

### 品質ゲート
- **設計品質**: o3 MCP アーキテクチャレビュー合格
- **実装品質**: Claude Code 標準適合・テストカバレッジ80%以上
- **戦略品質**: Gemini CLI 市場適合性・ユーザビリティ評価合格

## 🔗 関連コマンド

- `/requirements` - 要件定義詳細化
- `/design` - 技術設計詳細化
- `/winforms-patterns` - Windows Forms設計パターン
- `/legacy-integration` - レガシーシステム統合
- `/analyze` - プロジェクト分析・進捗確認

## 📝 出力ファイル

- `.tmp/ai_shared_data/spec_results.json` - 仕様策定結果
- `.tmp/integration_reports/multiAI_coordination.md` - AI協調レポート
- `.tmp/collaboration_logs/spec_execution.log` - 実行ログ

---

**💡 推奨使用パターン**: 新規プロジェクトは `/spec multiAI` から開始し、既存プロジェクトの改善は `/spec desktop_app [type]` で目的別最適化を実行してください。