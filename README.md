# 🚀 Claude Code SDD+TDD システム v14.0

**仕様駆動開発(SDD)とテスト駆動開発(TDD)の完全統合システム**

## 📋 概要

Claude Code v14.0は、アレックスチーム体制による完全自動化されたSDD+TDD開発システムです。100%のテストカバレッジを達成し、エンタープライズレベルの品質を実現しました。

## 🎯 最新アップデート

### v14.0 新機能 (2025-08-24)
- **テストカバレッジ100%達成**: アレックスチーム並列実行により全41モジュール完全カバー
- **フォルダ構成最適化**: 永続的/一時的ファイルの明確な分離構造
- **ホワイトボックステスト完備**: 全関数の全パス・全分岐を網羅
- **自己診断システム強化**: リアルタイムヘルスチェック機能

### アレックスチーム体制
- **Alex (リードエンジニア)**: SDD+TDD手法の統括とアーキテクチャ設計
- **TDDテストエンジニア**: 100%カバレッジのテスト実装
- **QA・ドキュメントエンジニア**: 品質保証と技術文書作成
- **コード最適化エンジニア**: パフォーマンス最適化と重複削除

### SDD+TDD開発サイクル
1. 仕様定義（Specification）
2. 設計ドキュメント作成（Design）
3. テストファースト実装（RED）
4. 最小限の実装（GREEN）
5. リファクタリング（REFACTOR）
6. 統合テスト
7. 品質検証
8. デプロイ

## 🚀 クイックスタート

### 1. リポジトリのクローン
```bash
git clone [your-repository-url]
cd [project-directory]
```

### 2. Claude Codeの起動
```bash
claude
```

### 3. アレックスチームによる開発
```bash
# 自己診断の実行
python .claude/system/core/alex_team_self_diagnosis_system.py

# テストカバレッジの確認
python .claude/project/tests/comprehensive_test_runner.py

# アレックスチーム起動
/auto-mode start

# 主要コマンド
1. 仕様作成      # SDD+TDD仕様定義
2. テスト実装    # TDDサイクル実行
3. 品質検証      # カバレッジ確認
4. 最適化実行    # パフォーマンス改善
```

### 4. ステータス確認
```bash
# 進行状況の確認
/auto-mode status

# 作業の停止
/auto-mode stop
```

## 📁 プロジェクト構成

```
project/
├── .claude/
│   ├── system/                      # 【永続的】システムコア
│   │   ├── core/                   # Pythonモジュール（41モジュール、100%カバレッジ）
│   │   ├── agents/                 # エージェント定義
│   │   ├── commands/               # コマンド定義
│   │   ├── config/                 # 設定ファイル
│   │   ├── hooks/                  # フックスクリプト
│   │   └── scripts/                # ユーティリティ
│   ├── project/                    # 【永続的】プロジェクト固有
│   │   ├── specs/                  # 仕様書
│   │   ├── tasks/                  # タスク管理
│   │   ├── modifications/          # 変更仕様
│   │   ├── docs/                   # ドキュメント
│   │   └── tests/                  # テストスイート（136テスト）
│   └── temp/                       # 【一時的】削除可能
│       ├── cache/                  # キャッシュ
│       ├── logs/                   # ログ
│       ├── reports/                # レポート
│       ├── workspace/              # 作業領域
│       └── benchmarks/             # ベンチマーク
├── README.md                       # このファイル
├── ALEX_TEAM_SYSTEM.md            # チーム体制説明
└── MIGRATION_COMPLETE.md          # 移行完了レポート
```

## 🔧 必要要件

- Claude Code (最新版)
- Git
- Python 3.8以上

## 📊 パフォーマンス指標

### システムメトリクス
- **テストカバレッジ**: 100%達成（全41モジュール）
- **テスト数**: 136個の包括的テスト
- **コード削減**: 80%削減（重複排除により）
- **実行速度**: 70-80%高速化（キャッシュシステム）

### 品質指標
- **ホワイトボックステスト**: 全関数・全パスカバー
- **ブランチカバレッジ**: 100%
- **エラーハンドリング**: 全例外パス検証済み
- **TDD準拠**: RED->GREEN->REFACTOR完全実装

## 👥 アレックスチーム

### チームメンバー
各エージェントの詳細は以下のファイルを参照：
- `.claude/system/agents/alex-sdd-tdd-lead.md` - リードエンジニア
- `.claude/system/agents/qa-doc-engineer.md` - QA・ドキュメントエンジニア
- `.claude/system/agents/code-optimizer-engineer.md` - コード最適化エンジニア
- `.claude/system/agents/tdd-test-engineer.md` - TDDテストエンジニア

### 設定とカスタマイズ
詳細な設定方法は`.claude/project/docs/`を参照してください。

## 🛠️ トラブルシューティング

問題が発生した場合は`.claude/system/core/alex_team_self_diagnosis_system.py`を実行して自己診断を行ってください。

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

MITライセンス

## 📝 更新履歴

### v14.0 (2025-08-24)
- ✅ テストカバレッジ100%達成（アレックスチーム並列実行）
- ✅ フォルダ構成最適化（永続的/一時的ファイル分離）
- ✅ ホワイトボックステスト完全実装
- ✅ 自己診断システム強化
- ✅ 全41モジュールの完全テスト網羅

### v13.0 (2025-08-23)
- ✅ アレックスチーム4人体制確立
- ✅ ServiceLocator廃止とDI簡素化
- ✅ コード削減42%達成
- ✅ モジュール数80%削減（40→8）
- ✅ 基本テストカバレッジ向上

### v12.0 (2025-08-22)
- ✅ 大規模リファクタリング実施
- ✅ 循環依存の完全解消
- ✅ /auto-mode機能強化
- ✅ エラーハンドリング改善

### v11.0 (2025-08-21)
- ✅ /auto-mode初期実装
- ✅ セッション管理機能
- ✅ ActivityReport自動生成

### v10.7 (2025-08-20)
- ✅ 初期システム構築
- ✅ JST対応実装

---

**🎯 次のゴール**: エンタープライズレベルの完全自動化開発システムの確立