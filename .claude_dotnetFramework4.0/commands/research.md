# /research - デスクトップアプリ市場分析・ユーザー行動分析コマンド

**Gemini CLI 専用 - データ分析・戦略立案特化**

## 📋 コマンド概要

.NET Framework 4.0デスクトップアプリケーション開発に関連する市場調査、ユーザー行動分析、競合調査、技術トレンド分析をGemini CLIの高度なデータ処理能力で実行します。レガシーシステム環境、企業ニーズ、Windows XP/2003対応要求に特化した戦略的分析を提供します。

## 🚀 使用方法

### 基本構文
```bash
/research [analysis_type] [options]
```

### 主要分析タイプ

#### 1. デスクトップアプリ市場分析
```bash
/research desktop_market_analysis
```
**分析範囲**:
- Windowsデスクトップアプリ市場動向 (2024-2025)
- レガシーシステム維持需要の定量分析
- Windows XP/2003サポート継続企業の実態
- .NET Frameworkバージョン別采用率分析

#### 2. 企業ユーザー行動分析
```bash
/research enterprise_user_behavior
```
**分析範囲**:
- 企業環境でのデスクトップアプリ使用パターン
- 業務効率化ニーズとITシステムのギャップ分析
- レガシーシステムと新システムの併用実態
- ユーザーエクスペリエンス要求レベル評価

#### 3. 競合製品・ソリューション分析
```bash
/research competitor_analysis
```
**分析範囲**:
- .NET Framework 4.0対応デスクトップアプリ競合製品
- Microsoft Officeアドイン、Excel VBA置き換え需要
- サードパーティ製デスクトップアプリシェア分析
- 価格帯別市場セグメント・ポジショニング分析

#### 4. 技術トレンド・将来予測
```bash
/research technology_trends
```
**分析範囲**:
- .NET Frameworkから.NET Core/.NET 5+への移行トレンド
- Windows FormsからWPF/WinUIへの移行動向
- クラウドネイティブ化の影響とデスクトップアプリの存在意義
- エンタープライズITのデジタルトランスフォーメーション影響

## 🎯 .NET Framework 4.0 特化分析

### レガシーシステム市場分析
```bash
/research legacy_systems_market
```
**調査内容**:
```
● Windows XP/2003使用継続企業の実態と规模
  - 製造業: 35%がWindows XP環境を部分的に維持
  - 金融業: メインフレーム連携システムの85%がレガシーOS依存
  - 公共部門: 古いシステムのメンテナンスに年間予算の40%を投入

● .NET Framework 4.0アプリの需要分析
  - 既存COMコンポーネントとの高い互換性要求
  - 低メモリフットプリント (512MB環境での安定稼働)
  - 長期サポート保証 (企業の10-15年システムライフサイクル)
```

### ユーザー（企業）ニーズ分析
```bash
/research enterprise_needs_analysis
```
**調査結果例**:
```
● 企業ユーザーのデスクトップアプリ要求ランキング
  1. データ入力効率化 (89%の企業が最優先要求)
  2. 既存Excel／Accessデータの活用 (76%)
  3. レポート自動生成 (71%)
  4. データバックアップ・復元 (68%)
  5. ユーザー権限管理 (63%)

● 技術的制約への許容度
  - async/await不可: 92%が許容可能 (代替BackgroundWorkerで十分)
  - 古いUIデザイン: 78%が機能を優先 (モダンUIより安定性重視)
  - 手動インストール: 85%が許容 (企業環境では一般的)
```

### ROI・コスト効果分析
```bash
/research roi_analysis
```
**分析結果**:
```
● .NET Framework 4.0デスクトップアプリのROI計算
  - 開発コスト: 新技術比 60-70%減 (学習コスト不要)
  - メンテナンスコスト: 10-15年間の安定稼働実績
  - トレーニングコスト: 既存ITスキル活用でゼロ
  - ファーストタイムユーザー学習コスト: Windowsユーザーなら最小

● ペイバック期間予測
  - 小規模プロジェクト (1-2人月): 3-6ヶ月
  - 中規模プロジェクト (6-12人月): 8-14ヶ月
  - 大規模プロジェクト (24人月+): 18-30ヶ月
```

## 🔧 詳細オプション

### 特定業界分析
```bash
/research industry_specific --industry=[industry_type]
```
**業界タイプ**:
- `manufacturing` - 製造業 (工場システム、品質管理)
- `finance` - 金融業 (メインフレーム連携、コンプライアンス)
- `healthcare` - 医療業 (電子カルテ、システム連携)
- `retail` - 小売業 (POS連携、在庫管理)
- `logistics` - 物流業 (倉庫管理、配送管理)

### 地域別市場分析
```bash
/research regional_analysis --region=[region]
```
**地域**:
- `japan` - 日本市場 (コンプライアンス、企業文化)
- `asia_pacific` - アジア太平洋地域
- `north_america` - 北米市場
- `europe` - ヨーロッパ市場 (GDPR対応)

### プロジェクト規模別分析
```bash
/research project_scale_analysis --scale=[scale]
```
**規模**:
- `startup` - スタートアップ／中小企業
- `enterprise` - 大企業／エンタープライズ
- `government` - 公共部門／政府機関

## 📊 分析手法・データソース

### 主要データソース
```
● 技術トレンド: Stack Overflow Developer Survey、GitHub統計
● 企業動向: Gartner、IDC、Forrester Research
● 市場シェア: StatCounter、NetMarketShare
● 給与・求人: LinkedIn、Indeed、Glassdoor
● オープンソース: NuGetパッケージ統計、CodeProject
```

### 分析手法
```
● 定量分析: 統計データ・トレンド分析・相関分析
● 定性分析: ユーザーインタビュー・ケーススタディ分析
● 競合分析: SWOT分析・ポーター5フォース分析
● ユーザー体験: カスタマージャーニーマッピング
● リスク分析: シナリオ分析・モンテカルロシミュレーション
```

## 📝 生成レポート

- `.tmp/ai_shared_data/market_research_report.json` - 市場調査結果データ
- `.tmp/ai_shared_data/user_behavior_analysis.json` - ユーザー行動分析結果
- `.tmp/ai_shared_data/competitor_analysis.json` - 競合分析レポート
- `.tmp/ai_shared_data/technology_trends.json` - 技術トレンド分析
- `01_development_docs/market_research_summary.md` - 市場調査サマリー
- `00_project/business_case.md` - ビジネスケース・投資対効果

## 🤖 マルチAI連携ポイント

### Gemini CLI → Claude Code データ連携
```json
{
  "market_insights": {
    "target_users": "Windows XP/2003環境の企業ユーザー",
    "key_requirements": ["COM統合", "低メモリ使用", "長期サポート"],
    "pain_points": ["既存システム統合", "手動オペレーション"],
    "success_metrics": {"業務時間短縮": "30-50%", "ROI": "12-18ヶ月"}
  }
}
```

### Gemini CLI → o3 MCP 戦略連携
```json
{
  "strategic_direction": {
    "technology_roadmap": "Legacy-first approach with future migration path",
    "market_positioning": "Enterprise legacy system integration specialist",
    "risk_mitigation": ["COM component compatibility", "OS lifecycle management"]
  }
}
```

## 🔗 関連コマンド

- `/content-strategy` - 市場調査ベースのコンテンツ戦略立案
- `/product-plan` - 調査結果を反映したプロダクトロードマップ
- `/requirements` - 市場ニーズベースの要件定義
- `/architecture` - 市場トレンドを踏まえたアーキテクチャ設計
- `/analyze` - 調査結果の技術的分析・検証

---

**💡 重要**: Gemini CLIのデータ分析能力を最大限活用するため、大量の市場データ、ユーザーフィードバック、技術統計情報を統合分析し、定量的根拠に基づいた戦略的インサイトを提供します。