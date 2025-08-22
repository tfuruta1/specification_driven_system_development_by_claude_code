# Claude Code 開発支援システム v12.0

## 概要
Claude Code（CTO）とアレックス（技術リード）によるペアプログラミング開発支援システム。TDD/SDD統合開発フローと自動化ツールにより、高品質なソフトウェア開発を実現します。

## 最新更新（2025年8月22日）

### v12.0 新機能
- **統合テストフレームワーク**: ユニット→統合→E2Eの3層テスト戦略
- **ファイルアクセス目的表示**: 作業透明性の向上（修正/参照/解析を色分け表示）
- **循環参照自動検出**: 初期化エラーを事前防止
- **/auto-modeコマンド**: ペアプログラミングモードの明示的制御

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
├── core/                    # コアシステム
│   ├── auto_mode.py        # auto-modeコマンド実装
│   ├── test_strategy.py    # テスト戦略管理
│   ├── integration_test_runner.py  # 統合テスト実行
│   └── file_access_logger.py      # ファイルアクセスロガー
├── ActivityReport/         # 作業ログ
├── CLAUDE.md              # システム仕様書
└── README.md              # このファイル
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

## チーム体制

### CTO（Claude Code）
- プロジェクト管理
- ユーザー対話
- 意思決定

### アレックス（技術リード）
- 技術実装
- コード作成
- テスト実行

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

- [CLAUDE.md](./CLAUDE.md) - 詳細システム仕様
- [TEST_STRATEGY.md](./core/TEST_STRATEGY.md) - テスト戦略
- [README_FileAccessLogger.md](./core/README_FileAccessLogger.md) - ファイルアクセスロガー詳細

---
*Version 12.0 - Integrated Testing & Transparency Enhancement*
*© 2025 Claude Code Development System*
*Last Updated: 2025-08-22*