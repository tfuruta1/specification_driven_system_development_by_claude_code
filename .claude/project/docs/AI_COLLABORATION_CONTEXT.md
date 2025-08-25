# AI協力コンテキスト情報 - 往復最適化版

## 🤖 AI往復最適化戦略

### 基本方針
参考記事: [AIとの往復を最適化するTDD開発手法](https://zenn.dev/sakupanda/articles/ecb4ae7e9a240e)

**目標**: AI往復回数を20回→3-5回に削減する効率的な開発スタイルの確立

### 1. 仕様書ファースト開発
```
[実装依頼の構造]
1. 明確な仕様定義 (SPECIFICATION_TEMPLATE.md使用)
2. 技術要件とアーキテクチャ指示  
3. TDD要求 (RED/GREEN両フェーズ)
4. 一括実装依頼 (実装+テスト+検証)
5. 自動修正期待値の明示
```

### 2. バッチ処理リクエスト
AIに一度の往復で以下をまとめて依頼する:
- ✅ **実装**: 完全に動作するコード
- ✅ **テスト**: RED/GREEN両フェーズ対応
- ✅ **統合**: 既存システムとの統合
- ✅ **検証**: テスト実行とカバレッジ確認
- ✅ **修正**: エラー発生時の自動修正試行

## 🏗️ プロジェクト技術スタック

### コア技術
- **言語**: Python 3.13.5
- **テスト**: pytest + pytest-cov  
- **品質管理**: flake8, mypy
- **CI/CD**: Lefthook (pre-commit hooks)

### アーキテクチャパターン
```python
# 統一基盤パターン
from core.common_base import BaseManager, BaseResult, create_result

class NewFeature(BaseManager):
    def initialize(self) -> BaseResult:
        pass
    
    def main_process(self, input_data) -> BaseResult:
        pass
    
    def cleanup(self) -> BaseResult:
        pass
```

### ディレクトリ構造
```
.claude/
├── system/core/           # コアモジュール (41ファイル)
│   ├── optimized_self_diagnosis_system.py  # AI最適化診断システム v15.0
│   ├── ai_batch_optimizer.py      # AI往復最適化コア
│   └── automated_test_generator.py # 自動テスト生成
├── system/templates/      # AI最適化テンプレート
│   ├── SPECIFICATION_TEMPLATE.md  # 仕様書ファースト開発
│   └── DIAGNOSIS_IMPROVEMENT_TEMPLATES.md  # 診断問題解決テンプレート
├── project/tests/         # テストスイート (95%+ coverage)
├── lefthook.yml          # Pre-commitフック設定
└── AI_COLLABORATION_CONTEXT.md  # このファイル
```

## 📋 開発命令テンプレート

### 新機能実装依頼テンプレート
```
【仕様書ファースト実装依頼】

## 機能概要
[機能名]: [具体的な機能説明]
[目的]: [解決したい課題]
[モジュール]: system/core/[module_name].py

## 技術仕様
- 基盤: BaseManagerを継承
- インターフェース: BaseResult返却
- エラーハンドリング: try-except + logging
- 設定: core.config経由でアクセス

## TDD要求
以下を一括で実装してください:

1. **実装** (GREEN Phase):
   - 仕様に基づく完全なコード実装
   - 既存system/core/common_base.pyとの統合
   - 適切なエラーハンドリング

2. **テスト** (RED/GREEN両Phase):
   - project/tests/test_[module_name].py作成
   - 異常系テスト (RED Phase)
   - 正常系テスト (GREEN Phase)  
   - カバレッジ95%以上目標

3. **自動検証**:
   - テスト実行と結果確認
   - エラー発生時の自動修正試行
   - 最終的な動作確認

## 期待する成果物
- ✅ 動作するモジュール実装
- ✅ 完全なテストスイート
- ✅ 統合確認済み
- ✅ カバレッジレポート
```

### デバッグ・修正依頼テンプレート  
```
【統合デバッグ・修正依頼】

## 現状
[現在のエラー状況]
[実行コマンド]: 
[エラーメッセージ]:

## 修正依頼
以下を一括で実行してください:

1. **エラー分析**: 原因の特定と分析
2. **修正実装**: エラー解消のための修正
3. **テスト確認**: 修正後のテスト実行
4. **統合確認**: 他モジュールとの統合動作確認
5. **最終検証**: 全体的な動作確認

## 制約条件
- 既存のCLAUDE.md仕様に準拠
- YAGNI/DRY/KISS/TDD原則維持
- 既存テストは破壊しない
```

## 🔧 開発コマンド集

### 基本開発コマンド
```bash
# プロジェクトルートへ移動
cd .claude

# 基本テスト実行
python -m pytest project/tests/test_*_minimal.py -v

# カバレッジ付きテスト
python -m pytest project/tests/ --cov=system/core --cov-report=term-missing -v

# 新モジュール用テスト自動生成
python system/core/automated_test_generator.py [module_name]

# AI協力準備状況チェック
lefthook run ai-ready

# AI最適化診断実行（自動改善提案生成）
python system/core/optimized_self_diagnosis_system.py
```

### CI/CD コマンド
```bash  
# Pre-commit チェック実行
lefthook run pre-commit

# TDD サイクル検証
lefthook run tdd-cycle

# 自動テスト生成（欠落分）
lefthook run generate-tests
```

## 📊 品質基準

### コードメトリクス
- **テストカバレッジ**: 95%以上
- **メソッド行数**: 50行以下
- **クラス責任**: 単一責任原則
- **循環依存**: 0件 (dependency_checker.py使用)

### パフォーマンス基準
- **インポート時間**: 0.1秒以下
- **メモリ使用量**: 50MB以下  
- **テスト実行時間**: 30秒以下

### 保守性基準
- **YAGNI**: 現在不要な機能は実装しない
- **DRY**: 重複コードは共通化 (common_base.py活用)
- **KISS**: 複雑な解決策より単純な解決策を優先

## 🎯 AI協力最適化のポイント

### 効率的な依頼方法
1. **明確な仕様**: あいまいな指示は避ける
2. **一括処理**: 複数タスクをまとめて依頼
3. **文脈共有**: このファイルとCLAUDE.mdを事前参照
4. **自動修正**: エラー時の修正試行を含める
5. **検証含む**: 実装だけでなく動作確認まで

### 避けるべきパターン
- ❌ 段階的な小分け依頼 (往復増加)
- ❌ 曖昧な仕様での実装依頼
- ❌ テスト後回し (後でエラー発生)
- ❌ 既存システム無視 (統合エラー)
- ❌ 検証抜け (動作未確認)

### 推奨パターン  
- ✅ 完全仕様書 + 一括実装依頼
- ✅ TDD込み (実装+テスト+検証)
- ✅ エラー自動修正期待値明示
- ✅ 既存システム統合配慮
- ✅ 最終動作確認まで完了

## 🚀 開発フロー最適化

### Before (非効率パターン)
```
1. ユーザー: 「○○機能を作って」
2. AI: 「仕様を教えてください」  
3. ユーザー: 「△△のような機能で...」
4. AI: コード実装
5. ユーザー: 「テストが足りない」
6. AI: テスト追加
7. ユーザー: 「エラーが出る」
8. AI: エラー修正
... (20往復)
```

### After (最適化パターン)
```
1. ユーザー: 「SPECIFICATION_TEMPLATE.mdに基づき、仕様+実装+テスト+検証を一括で実行」
2. AI: 完全な実装+テスト+統合+動作確認完了
3. ユーザー: 「完成確認」
... (3往復)
```

### After (診断システム統合パターン) - NEW!
```
1. ユーザー: 「python system/core/optimized_self_diagnosis_system.py」
2. AI診断システム: 4フェーズ実行→AI実装依頼自動生成
3. ユーザー: 生成されたAI実装依頼をコピー&ペーストで実行
4. AI: バッチ処理で問題完全解決
... (2往復で問題解決完了)
```

---

## 💡 重要メモ

**このコンテキストファイルを常に参照し、効率的なAI協力開発を実現してください。**

記事参考: https://zenn.dev/sakupanda/articles/ecb4ae7e9a240e