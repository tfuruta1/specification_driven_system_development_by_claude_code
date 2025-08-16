# 🗂️ 集中一時ファイル管理システム

## 概要
すべての一時ファイル・フォルダを`.tmp`ディレクトリに集中管理し、自動クリーンアップで常にクリーンな環境を維持します。

## 📁 ディレクトリ構造

### 標準構成
```
.claude_sub_agent/
└── .tmp/                           # すべての一時ファイルのルート
    ├── agent_workspace/            # エージェント作業領域
    │   ├── cto/                   # CTO専用
    │   ├── hr_dept/                # 人事部専用
    │   ├── strategy_dept/          # 経営企画部専用
    │   ├── qa_dept/                # 品質保証部専用
    │   └── dev_dept/               # システム開発部専用
    │       ├── frontend/
    │       ├── backend/
    │       └── testing/
    ├── analysis_cache/             # 解析キャッシュ
    │   ├── checksums/              # ファイルチェックサム
    │   ├── parsed/                 # パース済みデータ
    │   └── results/                # 解析結果
    ├── generated_docs/             # 生成ドキュメント
    │   ├── requirements/           # 要件定義書
    │   ├── design/                 # 設計書
    │   └── reports/                # レポート
    ├── backups/                    # バックアップ
    │   ├── instant/                # 即時バックアップ
    │   ├── checkpoint/             # チェックポイント
    │   └── archive/                # アーカイブ
    ├── agent_logs/                 # エージェントログ
    │   ├── activity_stream.log     # アクティビティストリーム
    │   └── daily/                  # 日次ログ
    └── session/                    # セッション情報
        ├── current/                # 現在のセッション
        └── history/                # 過去のセッション
```

## 🔒 アクセス制御

### エージェント別権限
```python
access_permissions = {
    "cto": {
        "read": [".tmp/**/*"],
        "write": [".tmp/agent_workspace/cto/", ".tmp/session/"],
        "delete": [".tmp/agent_workspace/cto/"],
        "admin": True  # 全体管理権限
    },
    "hr_dept": {
        "read": [".tmp/agent_workspace/hr_dept/", ".tmp/generated_docs/"],
        "write": [".tmp/agent_workspace/hr_dept/"],
        "delete": [".tmp/agent_workspace/hr_dept/"]
    },
    "dev_dept": {
        "read": [".tmp/agent_workspace/dev_dept/", ".tmp/analysis_cache/"],
        "write": [".tmp/agent_workspace/dev_dept/", ".tmp/analysis_cache/"],
        "delete": [".tmp/agent_workspace/dev_dept/**/*"]
    }
}
```

## 🎯 ファイル命名規則

### 標準命名パターン
```python
naming_patterns = {
    "timestamp": "{yyyy}-{mm}-{dd}_{hh}-{mm}-{ss}",
    "session": "session_{session_id}_{type}",
    "backup": "bkp_{timestamp}_{original_name}",
    "cache": "cache_{checksum}_{type}",
    "report": "report_{dept}_{type}_{timestamp}",
    "temp": "tmp_{random_id}_{purpose}"
}

# 例
# 2025-08-16_14-30-00_requirements_analysis.md
# session_abc123_checkpoint.json
# bkp_20250816_143000_user_model.py
# cache_sha256abcd_parsed.json
# report_cto_progress_2025-08-16.md
# tmp_xyz789_code_generation.py
```

## 🤖 自動管理機能

### TempFileManager クラス
```python
class TempFileManager:
    def __init__(self):
        self.tmp_root = Path(".claude_sub_agent/.tmp")
        self.session_id = self._generate_session_id()
        self.active_files = {}
        self._ensure_structure()
    
    def create_temp_file(self, agent, purpose, extension=".tmp"):
        """一時ファイルを作成"""
        workspace = self.tmp_root / "agent_workspace" / agent.folder_name
        workspace.mkdir(parents=True, exist_ok=True)
        
        filename = f"tmp_{self.session_id}_{purpose}{extension}"
        file_path = workspace / filename
        
        # アクティブファイルとして登録
        self.active_files[str(file_path)] = {
            "created": datetime.now(),
            "agent": agent.name,
            "purpose": purpose,
            "auto_delete": True
        }
        
        print(f"[{timestamp}] 📁 一時ファイル作成 > {file_path.relative_to(self.tmp_root)}")
        return file_path
    
    def use_temp_folder(self, agent, purpose):
        """一時フォルダを使用"""
        workspace = self.tmp_root / "agent_workspace" / agent.folder_name / purpose
        workspace.mkdir(parents=True, exist_ok=True)
        
        print(f"[{timestamp}] 📂 作業フォルダ準備 > {workspace.relative_to(self.tmp_root)}")
        return workspace
    
    def cleanup_on_complete(self, file_or_folder):
        """作業完了時の自動削除"""
        path = Path(file_or_folder)
        
        if path.exists():
            if path.is_file():
                path.unlink()
                print(f"[{timestamp}] 🗑️ 削除完了 > {path.name}")
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"[{timestamp}] 🗑️ フォルダ削除 > {path.name}")
        
        # アクティブリストから削除
        self.active_files.pop(str(path), None)
```

## 🧹 自動クリーンアップ

### クリーンアップポリシー
```python
cleanup_policies = {
    "immediate": {
        "trigger": "task_complete",
        "targets": ["tmp_*", "*.tmp"],
        "delay": 0
    },
    "session_end": {
        "trigger": "session_close",
        "targets": ["agent_workspace/**/*", "session/current/*"],
        "delay": 0
    },
    "scheduled": {
        "trigger": "time_based",
        "targets": {
            "1_hour": ["instant/*", "tmp_*"],
            "24_hours": ["agent_workspace/*", "session/history/*"],
            "7_days": ["analysis_cache/*", "generated_docs/*"],
            "30_days": ["backups/archive/*", "agent_logs/daily/*"]
        }
    },
    "size_based": {
        "trigger": "size_threshold",
        "max_size_mb": 1000,
        "action": "oldest_first_deletion"
    }
}
```

### インテリジェントクリーンアップ
```python
class SmartCleanup:
    def __init__(self, manager):
        self.manager = manager
        self.importance_scores = {}
    
    def evaluate_importance(self, file_path):
        """ファイルの重要度を評価"""
        score = 0
        
        # 最近アクセスされた
        if self._last_accessed(file_path) < timedelta(hours=1):
            score += 10
        
        # エラーリカバリ用
        if "backup" in str(file_path) or "checkpoint" in str(file_path):
            score += 20
        
        # アクティブセッション関連
        if self.manager.session_id in str(file_path):
            score += 15
        
        # 生成されたドキュメント
        if file_path.parent.name == "generated_docs":
            score += 5
        
        return score
    
    def smart_cleanup(self):
        """重要度に基づくクリーンアップ"""
        all_files = list(self.manager.tmp_root.rglob("*"))
        
        # 重要度を評価
        for file in all_files:
            if file.is_file():
                self.importance_scores[file] = self.evaluate_importance(file)
        
        # 重要度の低いものから削除
        sorted_files = sorted(
            self.importance_scores.items(), 
            key=lambda x: x[1]
        )
        
        for file, score in sorted_files:
            if score < 5 and self._is_old_enough(file):
                file.unlink()
                print(f"[{timestamp}] 🧹 自動削除 > {file.name} (重要度: {score})")
```

## 📊 使用統計

### 容量モニタリング
```python
class StorageMonitor:
    def get_usage_report(self):
        """使用状況レポート生成"""
        report = {
            "total_size": self._get_folder_size(self.tmp_root),
            "by_department": {},
            "by_type": {},
            "file_count": 0,
            "oldest_file": None,
            "largest_file": None
        }
        
        # 部門別集計
        for dept in ["cto", "hr_dept", "strategy_dept", "qa_dept", "dev_dept"]:
            dept_path = self.tmp_root / "agent_workspace" / dept
            if dept_path.exists():
                report["by_department"][dept] = self._get_folder_size(dept_path)
        
        # タイプ別集計
        for type_folder in ["analysis_cache", "generated_docs", "backups"]:
            type_path = self.tmp_root / type_folder
            if type_path.exists():
                report["by_type"][type_folder] = self._get_folder_size(type_path)
        
        return report
    
    def display_usage(self):
        """使用状況を表示"""
        report = self.get_usage_report()
        
        print(f"""
╔══════════════════════════════════════╗
║     一時ファイル使用状況レポート      ║
╠══════════════════════════════════════╣
║ 総使用量: {report['total_size']/1024/1024:.2f} MB
║ ファイル数: {report['file_count']}
╠──────────────────────────────────────╣
║ 部門別使用量:
║   CTO: {report['by_department'].get('cto', 0)/1024:.1f} KB
║   人事部: {report['by_department'].get('hr_dept', 0)/1024:.1f} KB
║   経営企画部: {report['by_department'].get('strategy_dept', 0)/1024:.1f} KB
║   品質保証部: {report['by_department'].get('qa_dept', 0)/1024:.1f} KB
║   開発部: {report['by_department'].get('dev_dept', 0)/1024:.1f} KB
╚══════════════════════════════════════╝
        """)
```

## 🚨 エラー防止

### 誤削除防止
```python
protected_patterns = [
    "*.checkpoint",     # チェックポイントファイル
    "*.backup",        # バックアップファイル
    "current_session*", # 現在のセッション
    ".gitkeep"         # Git管理用
]

def is_protected(file_path):
    """保護されたファイルかチェック"""
    for pattern in protected_patterns:
        if fnmatch.fnmatch(file_path.name, pattern):
            return True
    return False
```

### 自動リカバリ
```python
def safe_operation(func):
    """安全な操作のデコレータ"""
    def wrapper(*args, **kwargs):
        try:
            # 操作前のスナップショット
            snapshot = create_snapshot()
            
            # 操作実行
            result = func(*args, **kwargs)
            
            # 成功
            return result
            
        except Exception as e:
            # エラー時は復元
            print(f"[{timestamp}] ⚠️ エラー検出: {e}")
            restore_snapshot(snapshot)
            print(f"[{timestamp}] ✅ スナップショットから復元完了")
            raise e
    
    return wrapper
```

## 🎮 管理コマンド

```bash
# 使用状況確認
/tmp-status

# 手動クリーンアップ
/tmp-cleanup [--force]

# 特定エージェントの作業領域クリア
/tmp-clear-agent <agent_name>

# 保護ファイルリスト表示
/tmp-protected

# セッションリセット
/tmp-reset-session
```

---

*この集中一時ファイル管理システムにより、プロジェクト全体がクリーンに保たれ、一時ファイルが散乱することを防ぎます。*