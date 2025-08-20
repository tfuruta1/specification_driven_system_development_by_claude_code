# Claude Code セットアップガイド

## 他のPCでアレックスとペアプログラミングを開始する方法

### 前提条件
- Claude Codeがインストール済み
- Gitリポジトリをクローン済み

### 必要なファイル（リポジトリに含まれています）
1. `.claude/CLAUDE.md` - システム設定（v10.3）
2. `.claude/agents/alex-sdd-tdd-engineer.md` - アレックスのエージェント定義

### セットアップ手順

1. **リポジトリをクローン**
```bash
git clone [your-repository-url]
cd [project-directory]
```

2. **Claude Codeを起動**
```bash
claude
```

3. **自動セットアップ確認**
- CLAUDE.md v10.3により、起動時に自動的に以下が実行されます：
  - CTOとしての役割確立
  - アレックス（alex-sdd-tdd-engineer）との接続
  - ペアプログラミング体制の確立

4. **動作確認**
初回起動時、以下のメッセージが表示されれば成功：
```
CTOとアレックスがペアプロ準備完了
```

### トラブルシューティング

**アレックスが呼び出せない場合:**
1. `.claude/agents/alex-sdd-tdd-engineer.md`が存在するか確認
2. ファイルの内容が正しいか確認
3. Claude Codeを再起動

**CLAUDE.mdが読み込まれない場合:**
1. `.claude/CLAUDE.md`が存在するか確認
2. バージョンがv10.3以上であることを確認

### 注意事項
- Windows/Mac/Linux全てで動作します
- エージェント定義はリポジトリに含まれているため、追加設定は不要です
- 起動時の自動セットアップにより、手動でアレックスを呼び出す必要はありません

---
*Created: 2025-08-20*
*System: CLAUDE v10.3*