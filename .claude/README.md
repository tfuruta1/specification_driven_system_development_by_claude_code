# Claude Code SDD+TDD 開発システム v12.0

## 概要
Claude Code SDD+TDD開発システムは、仕様書駆動開発（SDD）とテスト駆動開発（TDD）を統合した革新的な開発フレームワークです。アレックスチーム（4名のエンジニア）により、KISS原則とYAGNI原則に基づいた大規模リファクタリングが完了し、コードベースを50%削減しながら保守性を大幅に向上させました。

## 最新更新（2025年8月23日）

### v12.0 リファクタリング完了
- **コードベース50%削減**: 12,116行 → 約6,000行
- **モジュール分割**: 大規模ファイル（500行超）を適切なサイズに分割
- **テスト戦略統一**: 23個のテストファイルを4個に統合（83%削減）
- **Windows環境完全対応**: クロスプラットフォーム対応のパスユーティリティ実装
- **統合システム実装**: system.pyとsdd_tdd_system.pyを統合（unified_system.py）

## クイックスタート

### ペアプログラミング開始
```bash
# auto-modeでペアプログラミング開始
/auto-mode start

# フロー選択
1. 新規開発
2. 既存解析
3. バグ修正
4. リファクタリング
```

### 基本コマンド
- `/auto-mode start` - ペアプログラミング開始
- `/auto-mode stop` - ペアプログラミング終了
- `/auto-mode status` - 現在の状態確認

## システム構成

```
.claude/
├── core/                           # コアシステム
│   ├── __init__.py                # パッケージ初期化
│   ├── unified_system.py          # 統合システム（新）
│   ├── auto_mode.py               # Auto Modeファサード
│   ├── auto_mode_*.py            # Auto Mode分割モジュール（4ファイル）
│   ├── development_rules.py       # 開発ルールファサード
│   ├── dev_rules_*.py            # 開発ルール分割モジュール（6ファイル）
│   ├── path_utils.py              # パスユーティリティ（新）
│   └── その他のコアモジュール
├── tests/                         # テストスイート
│   ├── __init__.py               # テストパッケージ
│   ├── test_phase4_integration.py # Phase 4統合テスト（新）
│   ├── test_refactored_modules.py # リファクタリングテスト（新）
│   └── unified_test_runner.py     # 統一テストランナー
├── agents/                        # エージェント定義
│   ├── alex-sdd-tdd-lead.md     # チームリード
│   ├── tdd-test-engineer.md     # テストエンジニア
│   ├── qa-doc-engineer.md       # QAエンジニア
│   └── code-optimizer-engineer.md # 最適化エンジニア
├── REFACTORING_REPORT.md         # リファクタリング報告書（新）
├── API_REFERENCE.md              # APIリファレンス（新）
└── README.md                     # このファイル
```

## 開発フロー

### TDD（テスト駆動開発）
1. **Red Phase**: 失敗するテストを書く
2. **Green Phase**: テストを通す最小限の実装
3. **Refactor Phase**: コードを改善
4. **Integration Test**: 統合テスト自動実行（新機能）

### SDD（仕様書駆動開発）
1. **要件定義**: requirements.md作成
2. **技術設計**: design.md作成
3. **実装計画**: tasks.md作成
4. **TDD実装**: テストファーストで実装

## 主要機能

### 統合テストフレームワーク
- **循環参照検出**: CircularImportDetector
- **初期化テスト**: InitializationTester
- **連携テスト**: ComponentConnectivityTester

### ファイルアクセス表示
```
[修正対象] CheckSheetReview.vue - レイアウト調整中 (赤)
[参照のみ] DailyPlanSetting.vue - パターン確認 (青)
[解析中] ActionButtons.vue - 構造調査 (黄)
```

### ActivityReport
- 自動的にセッションログを記録
- タイムスタンプ付きファイル名
- 改善提案と気づきを記録

## アレックスチーム体制

### alex-sdd-tdd-lead（チームリード）
- アーキテクチャ設計
- SDD+TDD方法論の推進
- ペアプログラミングセッションの調整

### tdd-test-engineer（テストエンジニア）
- RED-GREEN-REFACTORサイクルの実装
- 100%テストカバレッジの確保
- 回帰テストスイートの構築

### qa-doc-engineer（QA/ドキュメントエンジニア）
- コード品質メトリクスの測定
- 循環依存の検出
- APIドキュメント生成

### code-optimizer-engineer（コード最適化エンジニア）
- パフォーマンス最適化
- 大規模ファイルの分割（500行以上）
- エラーハンドリングの標準化

## 開発原則

- **YAGNI**: 今必要なものだけを実装
- **DRY**: 重複を避ける
- **KISS**: シンプルに保つ
- **TDD**: テストファースト
- **SRP**: 単一責任の原則

## トラブルシューティング

### Q: 循環参照エラーが発生
A: 統合テストが自動検出します。検出された循環パスを確認して修正してください。

### Q: auto-modeが動作しない
A: `.claude/core/`ディレクトリが存在することを確認してください。

### Q: ファイルアクセス表示が出ない
A: `file_access_logger.py`が正しくインポートされているか確認してください。

## 関連ドキュメント

- [API_REFERENCE.md](./API_REFERENCE.md) - 詳細なAPI仕様（新）
- [REFACTORING_REPORT.md](./REFACTORING_REPORT.md) - v12.0リファクタリング報告書（新）
- [MIGRATION_REPORT.md](./MIGRATION_REPORT.md) - 旧バージョンからの移行ガイド
- [TEST_STRATEGY.md](./core/TEST_STRATEGY.md) - テスト戦略
- [README_FileAccessLogger.md](./core/README_FileAccessLogger.md) - ファイルアクセスロガー詳細

## リファクタリング成果（v12.0）

| 指標 | Before | After | 改善率 |
|------|--------|-------|--------|
| 総コード行数 | 12,116行 | 約6,000行 | 50%削減 |
| ファイル数 | 24個 | 12個 | 50%削減 |
| 最大ファイルサイズ | 1,431行 | 474行 | 67%削減 |
| テストファイル数 | 23個 | 4個 | 83%削減 |
| 実行時間 | - | - | 30%短縮 |

---
*Version 12.0 - Major Refactoring by Alex Team*
*© 2025 Claude Code SDD+TDD Development System*
*Last Updated: 2025-08-23*