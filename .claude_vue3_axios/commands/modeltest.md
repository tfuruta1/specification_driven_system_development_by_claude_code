# /modeltest - マルチAI連携テストコマンド

## 目的
現在のプロジェクト環境において、Gemini CLI・o3 MCP・Claude Codeの各AIモデルとの連携が正常に機能していることを確認し、マルチAI開発体制の準備状況を検証します。

## 対象AI
- **Claude Code**: 統合テスト管理・結果集約
- **Gemini CLI**: 大規模コンテキスト処理・マルチモーダル対応テスト
- **o3 MCP**: MCPプロトコル連携・外部ツール統合テスト

## 入力パラメータ
- **任意**: `$TEST_SCOPE` - テスト範囲（basic, comprehensive, performance, integration）
- **任意**: `$MODEL_TARGET` - 対象モデル（all, gemini, o3_high, o3_standard, o3_low, claude）
- **任意**: `$OUTPUT_FORMAT` - 出力形式（summary, detailed, json, markdown）

## 出力
- **連携テストレポート**: `.tmp/modeltest_report_[timestamp].md`
- **各AIテスト結果**: `.tmp/ai_test_results/`
- **パフォーマンス分析**: `.tmp/performance_metrics.json`
- **推奨改善事項**: `.tmp/optimization_recommendations.md`

## テスト項目

### Phase 1: 基本接続テスト
```markdown
## 基本接続確認

### 1. Claude Code接続テスト
- [ ] Claude Code API接続確認
- [ ] 基本的なコマンド実行テスト
- [ ] ファイル読み書き権限確認
- [ ] プロジェクトファイル構造認識

### 2. Gemini CLI接続テスト
- [ ] Gemini CLI API接続確認
- [ ] 大規模コンテキスト処理能力確認
- [ ] マルチモーダル入力対応確認
- [ ] 日本語・英語処理能力確認

### 3. o3 MCP接続テスト
- [ ] o3 MCP API接続確認
- [ ] MCPプロトコル通信確認
- [ ] 外部ツール統合機能確認
- [ ] 各階層（high/standard/low）アクセス確認
```

### Phase 2: 機能連携テスト
```markdown
## 機能連携確認

### 1. データフロー連携テスト
- [ ] Claude Code → Gemini CLI データ引き渡し
- [ ] Gemini CLI → o3 MCP データ引き渡し
- [ ] o3 MCP → Claude Code フィードバック
- [ ] 循環的データフロー確認

### 2. コマンド連携テスト
- [ ] /research → /content-strategy 連携
- [ ] /product-plan → /requirements 連携
- [ ] /design → /architecture 連携
- [ ] /architecture → /devops → /security 連携

### 3. ファイル共有・アクセステスト
- [ ] 共通ファイル(.tmp/)への読み書き
- [ ] プロジェクトファイル(.claude/)アクセス
- [ ] 成果物引き継ぎ・参照機能
- [ ] バージョン管理・競合解決
```

### Phase 3: パフォーマンステスト
```markdown
## パフォーマンス評価

### 1. 応答速度テスト
- [ ] Claude Code: 基本コマンド応答時間
- [ ] Gemini CLI: 大規模データ処理時間
- [ ] o3 MCP: ツール統合・実行時間
- [ ] 連携コマンド全体実行時間

### 2. 処理能力テスト
- [ ] Claude Code: コード生成・解析精度
- [ ] Gemini CLI: 長文コンテキスト保持
- [ ] o3 MCP: 複雑システム操作精度
- [ ] 並行処理・同期処理能力

### 3. 負荷耐性テスト
- [ ] 大量データ処理での安定性
- [ ] 長時間実行での接続維持
- [ ] エラー・タイムアウト回復力
- [ ] リソース使用量・効率性
```

### Phase 4: 統合シナリオテスト
```markdown
## 実用シナリオ検証

### 1. 新機能開発シナリオ
- [ ] 市場調査（Gemini CLI /research）
- [ ] UX戦略（Gemini CLI /content-strategy）
- [ ] 要件定義（Claude Code /requirements）
- [ ] システム設計（o3 MCP /architecture）
- [ ] 実装・テスト（Claude Code）
- [ ] インフラ構築（o3 MCP /devops）

### 2. 既存システム改善シナリオ
- [ ] 現状分析（Claude Code /analyze）
- [ ] パフォーマンス調査（Gemini CLI /research）
- [ ] リファクタリング（Claude Code /refactor）
- [ ] セキュリティ強化（o3 MCP /security）
- [ ] 運用改善（o3 MCP /devops）

### 3. 緊急対応シナリオ
- [ ] インシデント検知（o3 MCP monitoring）
- [ ] 問題分析（Claude Code /analyze）
- [ ] 緊急修正（Claude Code /fix）
- [ ] 影響調査（Gemini CLI /research）
- [ ] 再発防止（o3 MCP /security）
```

## テストシナリオ詳細

### 基本接続テスト実行例
```yaml
test_basic_connection:
  claude_code:
    command: "プロジェクト概要を教えてください"
    expected: "Vue.js + REST API仕様書駆動開発システムの説明"
    timeout: 30s
    
  gemini_cli:
    command: "この長文ドキュメントを要約してください: [大容量テキスト]"
    expected: "構造化された要約・キーポイント抽出"
    timeout: 60s
    
  o3_mcp:
    command: "システム状態を確認してください"
    expected: "システムメトリクス・ツール連携状況"
    timeout: 45s
```

### 連携フローテスト実行例
```yaml
test_integration_flow:
  scenario: "簡単な機能追加フロー"
  steps:
    1:
      ai: "gemini_cli"
      command: "/research user_behavior --data_source='analytics'"
      expected_output: ".tmp/research_report_*.md"
      
    2:
      ai: "gemini_cli"
      command: "/content-strategy persona --input='research_report'"
      expected_output: ".tmp/personas/"
      
    3:
      ai: "claude_code"
      command: "/requirements --input='persona_data'"
      expected_output: ".tmp/requirements.md"
      
    4:
      ai: "o3_mcp"
      command: "/architecture system_design --input='requirements'"
      expected_output: ".tmp/architecture_design.md"
      
  validation:
    - file_continuity: "各ステップの出力が次の入力として利用可能"
    - data_consistency: "データ形式・構造の一貫性"
    - performance: "全体実行時間 < 10分"
```

## 成果物テンプレート

### モデルテストレポート構成
```markdown
# マルチAI連携テストレポート

## テスト実行概要
- **実行日時**: [timestamp]
- **テスト範囲**: [basic/comprehensive/performance/integration]
- **対象モデル**: [all/specific models]
- **実行環境**: [OS, versions, configurations]

## 各AIモデル接続状況

### Claude Code
- **接続状態**: ✅ 正常 / ⚠️ 警告 / ❌ エラー
- **応答時間**: [平均/最大/最小] ms
- **機能確認**: 
  - ファイル操作: ✅
  - コード生成: ✅
  - プロジェクト理解: ✅
- **特記事項**: [問題・制限事項があれば記載]

### Gemini CLI
- **接続状態**: ✅ 正常 / ⚠️ 警告 / ❌ エラー
- **応答時間**: [平均/最大/最小] ms
- **機能確認**:
  - 大規模コンテキスト: ✅
  - マルチモーダル処理: ✅
  - 日本語処理: ✅
  - 分析・推論: ✅
- **特記事項**: [コンテキスト制限・処理能力等]

### o3 MCP
- **接続状態**: ✅ 正常 / ⚠️ 警告 / ❌ エラー
- **各階層状況**:
  - o3-high: ✅ 正常 (応答: [time]ms)
  - o3-standard: ✅ 正常 (応答: [time]ms)  
  - o3-low: ✅ 正常 (応答: [time]ms)
- **機能確認**:
  - MCPプロトコル: ✅
  - 外部ツール統合: ✅
  - リアルタイム操作: ✅
- **特記事項**: [MCP制限・ツール可用性等]

## 連携テスト結果

### データフロー連携
| 連携パス | 状態 | 実行時間 | データ整合性 | 備考 |
|---------|------|----------|-------------|------|
| Claude → Gemini | ✅ | 1.2s | ✅ | 正常 |
| Gemini → o3 | ✅ | 2.1s | ✅ | 正常 |
| o3 → Claude | ✅ | 0.8s | ✅ | 正常 |
| 循環フロー | ✅ | 4.5s | ✅ | 正常 |

### コマンド連携
| コマンドチェーン | 状態 | 総実行時間 | 成果物品質 | 備考 |
|----------------|------|-----------|-----------|------|
| /research → /content-strategy | ✅ | 3.2s | ✅ 高品質 | 正常連携 |
| /product-plan → /requirements | ✅ | 2.8s | ✅ 高品質 | 正常連携 |
| /design → /architecture | ✅ | 4.1s | ✅ 高品質 | 正常連携 |
| /architecture → /devops | ✅ | 5.2s | ✅ 高品質 | 正常連携 |

## パフォーマンス分析

### 応答時間分析
```json
{
  "claude_code": {
    "average_response_time": "1.2s",
    "max_response_time": "3.1s",
    "min_response_time": "0.3s",
    "percentile_95": "2.8s"
  },
  "gemini_cli": {
    "average_response_time": "2.8s",
    "max_response_time": "8.2s",
    "min_response_time": "0.8s",
    "percentile_95": "6.1s"
  },
  "o3_mcp": {
    "o3_high": {
      "average_response_time": "3.2s",
      "max_response_time": "12.1s",
      "min_response_time": "1.1s"
    },
    "o3_standard": {
      "average_response_time": "1.8s",
      "max_response_time": "5.2s",
      "min_response_time": "0.6s"
    },
    "o3_low": {
      "average_response_time": "0.9s",
      "max_response_time": "2.1s",
      "min_response_time": "0.3s"
    }
  }
}
```

### 処理能力評価
- **Claude Code**: コード生成精度 95%, 解析精度 92%
- **Gemini CLI**: 長文理解度 98%, 多言語対応 96%
- **o3 MCP**: システム操作精度 94%, ツール統合率 89%

## 問題・制限事項

### 検出された問題
1. **[問題分類] - [重要度: High/Medium/Low]**
   - 現象: [具体的な問題の説明]
   - 影響: [開発・運用への影響]
   - 回避策: [一時的な対処方法]
   - 恒久対策: [根本的な解決方法]

2. **[問題分類] - [重要度]**
   - [同様の構成]

### 制限事項・注意点
- **Gemini CLI**: 同時リクエスト数制限（最大3並行）
- **o3 MCP**: 高負荷時の応答遅延（>10s で要注意）
- **全体**: 長時間実行時のセッション維持（>30分で再接続推奨）

## 推奨改善事項

### 優先度 High（即座に対応）
1. **[改善項目]**
   - 現状: [現在の状況]
   - 目標: [改善後の目標]
   - 方法: [具体的な改善手順]
   - 期限: [実施期限]

### 優先度 Medium（1週間以内）
1. **[改善項目]**
   - [同様の構成]

### 優先度 Low（1ヶ月以内）
1. **[改善項目]**
   - [同様の構成]

## 総合評価・推奨事項

### マルチAI連携準備状況
- **総合評価**: ✅ 準備完了 / ⚠️ 部分的準備 / ❌ 準備不足
- **推奨開始レベル**: [基本開発/本格開発/エンタープライズ]
- **注意事項**: [運用上の重要な注意点]

### 次のステップ
1. [具体的な次の行動]
2. [継続的な監視・改善項目]
3. [定期的な再テスト推奨]

## 付録

### テスト実行ログ
[詳細な実行ログ・エラーメッセージ]

### 設定・環境情報
[システム設定・バージョン情報等]
```

## 実行例

### 基本テスト実行
```bash
/modeltest basic
```

### 包括的テスト実行
```bash
/modeltest comprehensive --output_format="detailed"
```

### 特定モデルテスト
```bash
/modeltest --model_target="gemini,o3_high" --test_scope="performance"
```

### パフォーマンス重点テスト
```bash
/modeltest performance --output_format="json"
```

## 連携コマンド
- **前提**: プロジェクト環境の基本設定完了
- **後続**: 各AIの専用コマンド（/research, /architecture, /security等）
- **定期実行**: 月次・環境変更時の健康診断として活用

## 品質チェックリスト
- [ ] 全AIモデルとの基本接続確認
- [ ] データフロー・ファイル共有の正常性確認
- [ ] パフォーマンス・応答時間の妥当性確認
- [ ] エラーハンドリング・回復力の確認
- [ ] セキュリティ・権限設定の適切性確認
- [ ] 実用シナリオでの統合動作確認

このコマンドにより、マルチAI開発環境の準備状況を客観的に評価し、最適な開発体制を構築できます。