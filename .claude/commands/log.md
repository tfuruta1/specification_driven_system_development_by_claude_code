# `/log` - 作業日誌記録コマンド

## 概要
階層型エージェントシステムの全活動を作業日誌に記録します。

## 使用方法

### 基本構文
```bash
/log [フェーズ] [オプション]
```

### フェーズ指定
- `analysis` - プロジェクト解析フェーズ
- `team` - チーム編成フェーズ  
- `work` - 日常作業
- `all` - 全フェーズ（デフォルト）

### オプション
- `--agent <名前>` - エージェント名を指定
- `--type <タイプ>` - 活動タイプ（作業、思考、指示、報告など）
- `--content <内容>` - 記録する内容
- `--private` - プライベート記録として保存

## 使用例

### プロジェクト解析を記録
```bash
/log analysis
```

### チーム編成を記録
```bash
/log team
```

### 個別の活動を記録
```bash
/log --agent "CTO" --type "指示" --content "品質テストを開始してください"
```

### プライベート記録
```bash
/log --agent "人事部" --content "また無茶な要求..." --private
```

## エージェントごとの記録例

### CTO
```bash
/log --agent "CTO" --type "戦略" --content "Phase 2の開始を決定"
/log --agent "CTO" --type "指示" --content "→ システム開発部: バグ修正を優先"
/log --agent "CTO" --content "正直きついスケジュール..." --private
```

### 経営企画部
```bash
/log --agent "経営企画部" --type "分析" --content "競合3社の分析完了"
/log --agent "経営企画部" --type "要件" --content "決済フロー改善を最優先に設定"
/log --agent "経営企画部" --content "要件がコロコロ変わるの勘弁して" --private
```

### システム開発部
```bash
/log --agent "システム開発部" --type "実装" --content "API 15エンドポイント完成"
/log --agent "システム開発部" --type "課題" --content "Piniaで予期せぬ副作用発生"
/log --agent "システム開発部" --content "早く帰ってゲームしたい" --private
```

### 人事部
```bash
/log --agent "人事部" --type "チーム編成" --content "フロントエンド2名増員完了"
/log --agent "人事部" --type "スキル分析" --content "TypeScript研修が必要"
/log --agent "人事部" --content "なんで人事がログ削除なんだよ..." --private
```

### 品質保証部
```bash
/log --agent "品質保証部" --type "テスト" --content "カバレッジ85%達成"
/log --agent "品質保証部" --type "バグ" --content "Critical 1件、Major 3件検出"
/log --agent "品質保証部" --content "目がショボショボする..." --private
```

## 自動記録されるイベント

以下のイベントは自動的に記録されます：
- プロジェクト解析開始時
- チーム編成時
- コマンド実行時
- エラー発生時
- 長時間作業時（8時間超過）
- 休憩時

## ログファイルの場所

### 通常ログ
```
.claude/.ActivityReport/daily_log/YYYY-MM-DD_workingLog.md
```

### プライベートログ
```
.claude/.ActivityReport/daily_log/.private/YYYY-MM-DD_private.md
```

## アクセス権限

- **ユーザー**: 全ログ読み取り可能
- **エージェント**: 書き込みのみ（読み取り不可）
- **人事部**: 30日経過後の削除権限

## 注意事項

- プライベート記録は他のエージェントには見えません
- パフォーマンス記録は自動で行われますが、面談等の判断はユーザーが行います
- ログは30日後に人事部により自動削除されます