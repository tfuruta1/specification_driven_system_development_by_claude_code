# 🔍 エージェント活動モニタリングシステム

## 概要
階層型エージェントシステムの活動をリアルタイムで可視化し、各エージェントの動作状況をターミナルに表示します。

## 📊 表示フォーマット

### 標準出力形式
```
[2025-08-16 14:30:15] 🎯 CTO > 修正要求を受け付けました。詳細分析を開始します...
[2025-08-16 14:30:16] 🎯 CTO → 💻 システム開発部 > コード解析を依頼
[2025-08-16 14:30:17] 💻 システム開発部 > backend-lead > 既存コードの解析中... [auth_module.py]
[2025-08-16 14:30:18] 💻 システム開発部 > frontend-lead > Vue3コンポーネント解析中... [LoginForm.vue]
[2025-08-16 14:30:20] 🛡️ 品質保証部 > テストカバレッジ確認中... [現在: 78%]
[2025-08-16 14:30:22] 🏢 人事部 > チーム編成検討中... [必要スキル: Python, Vue3, Testing]
[2025-08-16 14:30:25] 💡 経営企画部 > ビジネス影響分析中... [リスク評価: 中]
```

### 進捗インジケーター
```
[=====>    ] 50% | 🎯 CTO > 修正設計書作成中...
[=========>] 90% | 💻 システム開発部 > TDD実装 (Green Phase)
[==========] 100% | ✅ 品質保証部 > テスト完了
```

## 🎬 アクティビティタイプ

### 部門レベル活動
```python
activity_types = {
    "PLANNING": "📋 計画中",
    "ANALYZING": "🔍 解析中",
    "DESIGNING": "📐 設計中",
    "IMPLEMENTING": "💻 実装中",
    "TESTING": "🧪 テスト中",
    "REVIEWING": "👀 レビュー中",
    "DEPLOYING": "🚀 デプロイ中",
    "DOCUMENTING": "📝 文書作成中",
    "COORDINATING": "🤝 調整中",
    "WAITING": "⏳ 待機中"
}
```

### 通信パターン
```python
communication_patterns = {
    "REQUEST": "→",      # 依頼
    "RESPONSE": "←",     # 応答
    "BROADCAST": "📢",   # 全体通知
    "ALERT": "⚠️",      # 警告
    "SUCCESS": "✅",     # 成功
    "ERROR": "❌"        # エラー
}
```

## 💾 ログ管理

### ログファイル構造
```
.claude/
└── .tmp/
    └── agent_logs/
        ├── activity_stream.log     # リアルタイムストリーム
        ├── cto_decisions.log        # CTO意思決定ログ
        ├── department_actions.log   # 部門アクションログ
        ├── team_operations.log      # チーム作業ログ
        └── daily/
            └── 2025-08-16.log      # 日次アーカイブ
```

## 🔄 実装方法

### エージェントアクティビティクラス
```python
class AgentActivity:
    def __init__(self):
        self.current_activities = {}
        self.log_file = ".tmp/agent_logs/activity_stream.log"
    
    def log_activity(self, agent, action, details="", progress=None):
        from jst_config import format_jst_datetime
        timestamp = format_jst_datetime()
        
        # ターミナル出力
        if progress:
            print(f"[{self._progress_bar(progress)}] {progress}% | {agent.emoji} {agent.name} > {action}")
        else:
            print(f"[{timestamp}] {agent.emoji} {agent.name} > {action} {details}")
        
        # ログファイル記録
        self._write_to_log(timestamp, agent, action, details)
    
    def _progress_bar(self, percent):
        filled = int(percent / 10)
        bar = "=" * filled + ">" + " " * (10 - filled - 1)
        return bar
```

### 部門間通信の可視化
```python
def log_communication(from_agent, to_agent, message_type, content):
    from jst_config import format_jst_time
    timestamp = format_jst_time()
    arrow = communication_patterns[message_type]
    
    print(f"[{timestamp}] {from_agent.emoji} {from_agent.name} {arrow} "
          f"{to_agent.emoji} {to_agent.name} > {content}")
```

## 📋 使用例

### CTO主導の修正フロー
```python
# 修正要求受付
monitor.log_activity(cto, "ANALYZING", "修正要求を分析中...")

# 部門への依頼
monitor.log_communication(cto, system_dev, "REQUEST", "影響範囲の調査を依頼")
monitor.log_communication(cto, qa_dept, "REQUEST", "現在の品質状況を確認")

# 各部門の活動
monitor.log_activity(system_dev, "ANALYZING", "backend-lead: API endpoints確認中", 30)
monitor.log_activity(system_dev, "ANALYZING", "frontend-lead: UI components確認中", 45)
monitor.log_activity(qa_dept, "TESTING", "既存テストの実行中", 60)

# 人事部のチーム編成
monitor.log_activity(hr_dept, "COORDINATING", "必要スキルセットを分析中")
monitor.log_activity(hr_dept, "PLANNING", "田中さくら(Frontend)を配属準備")

# 経営企画部の戦略分析
monitor.log_activity(strategy_dept, "ANALYZING", "ビジネス影響度: 中")
```

## 🎮 制御コマンド

### モニタリング制御
```bash
# モニタリング詳細度設定
/monitor-level <verbose|normal|quiet>

# 特定部門のみ表示
/monitor-filter <cto|hr|strategy|qa|dev>

# ログクリア
/monitor-clear

# リアルタイム表示ON/OFF
/monitor-realtime <on|off>
```

## 🧹 自動クリーンアップ

### ログローテーション
- 24時間経過したログは自動アーカイブ
- 7日以上経過したアーカイブは自動削除
- activity_stream.logが100MBを超えたら自動ローテート

### 一時ファイル管理
```python
def cleanup_old_logs():
    log_dir = Path(".tmp/agent_logs")
    from jst_config import get_jst_now
    cutoff_date = get_jst_now() - timedelta(days=7)
    
    for log_file in log_dir.glob("daily/*.log"):
        if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
            log_file.unlink()
```

## 📊 パフォーマンス考慮

### 非同期ログ出力
- ログ出力は非同期で実行
- メインの処理をブロックしない
- バッファリングで効率化

### 表示の最適化
- 高頻度の更新は間引き表示
- プログレスバーは1%刻みで更新
- 重要度によるフィルタリング

---

*このモニタリングシステムにより、階層型エージェントシステムの動作が完全に可視化され、デバッグと監視が容易になります。*