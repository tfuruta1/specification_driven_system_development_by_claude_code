# .claude フォルダ構成ガイド

## 概要
.claudeフォルダは、永続的なシステムファイルと一時的なファイルを明確に分離した構成になっています。

## フォルダ構成

```
.claude/
├── system/                 # 【永続的】システムコア（削除禁止）
│   ├── core/              # Pythonモジュール（システムの心臓部）
│   ├── agents/            # エージェント定義
│   ├── commands/          # コマンド定義
│   ├── config/            # 設定ファイル
│   ├── hooks/             # フックスクリプト
│   └── scripts/           # ユーティリティスクリプト
│
├── project/               # 【永続的】プロジェクト固有（重要）
│   ├── specs/             # 仕様書
│   ├── tasks/             # タスク管理
│   ├── modifications/     # 変更仕様
│   ├── docs/              # ドキュメント
│   └── tests/             # テストスイート
│
└── temp/                  # 【一時的】削除可能
    ├── cache/             # キャッシュファイル
    ├── logs/              # ログファイル
    ├── reports/           # 実行レポート（旧alex_team）
    ├── workspace/         # 作業用一時ファイル
    └── benchmarks/        # ベンチマーク結果
```

## 各フォルダの説明

### system/ - システムコア（永続的）
**削除禁止** - システムの動作に必要不可欠なファイル
- `core/`: Pythonモジュール、システムロジック
- `agents/`: AIエージェントの定義
- `commands/`: カスタムコマンド
- `config/`: システム設定
- `hooks/`: 自動実行スクリプト
- `scripts/`: ユーティリティ

### project/ - プロジェクト固有（永続的）
**重要** - プロジェクトの仕様と履歴
- `specs/`: プロジェクト仕様書
- `tasks/`: タスク管理と進捗
- `modifications/`: 変更履歴
- `docs/`: プロジェクトドキュメント
- `tests/`: テストケース

### temp/ - 一時ファイル（削除可能）
**削除可能** - 再生成可能な一時データ
- `cache/`: キャッシュデータ（パフォーマンス向上用）
- `logs/`: 実行ログ
- `reports/`: 診断・分析レポート
- `workspace/`: 作業用一時ファイル
- `benchmarks/`: パフォーマンス測定結果

## メンテナンス

### 一時ファイルのクリーンアップ
```bash
# temp/フォルダ全体を安全に削除
rm -rf .claude/temp/*

# キャッシュのみクリア
rm -rf .claude/temp/cache/*

# ログのみクリア
rm -rf .claude/temp/logs/*
```

### バックアップ
```bash
# 重要なファイルのみバックアップ
tar -czf claude_backup.tar.gz .claude/system .claude/project

# リストア
tar -xzf claude_backup.tar.gz
```

## 注意事項

1. **system/とproject/は削除しないでください** - システムが動作しなくなります
2. **temp/は定期的にクリーンアップ可能** - パフォーマンスが低下した場合
3. **設定変更時** - system/config/内のファイルを編集
4. **新しい機能追加時** - 適切なフォルダに配置（永続的か一時的か判断）

## .gitignoreの推奨設定
```gitignore
.claude/temp/
*.pyc
__pycache__/
```

これにより、一時ファイルはGitリポジトリに含まれません。