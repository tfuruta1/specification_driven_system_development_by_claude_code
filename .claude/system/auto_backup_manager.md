# 📦 自動バックアップ・履歴管理システム

## 概要
エージェントが自律的にファイルのバックアップと履歴を管理し、ユーザーの確認なしに安全な作業環境を維持します。

## 🔄 バックアップ戦略

### 3層バックアップ構造
```
.claude/
└── .tmp/
    └── backups/
        ├── instant/          # 即時バックアップ（作業前の自動保存）
        ├── checkpoint/       # チェックポイント（フェーズ完了時）
        └── archive/          # アーカイブ（日次・完了時）
            └── 2025-08-16/
                ├── 14-30-00_analysis_start/
                ├── 15-00-00_design_complete/
                └── 16-00-00_implementation_done/
```

## 📋 自動バックアップルール

### トリガー条件
```python
backup_triggers = {
    "BEFORE_MODIFICATION": "ファイル修正前",
    "PHASE_COMPLETE": "フェーズ完了時",
    "MILESTONE_REACHED": "マイルストーン到達時",
    "ERROR_RECOVERY": "エラー発生時",
    "USER_REQUEST": "ユーザー要求時",
    "SCHEDULED": "定期バックアップ（30分毎）"
}
```

### バックアップ対象
```python
backup_targets = {
    "source_code": {
        "patterns": ["*.py", "*.js", "*.vue", "*.cs", "*.java"],
        "priority": "HIGH",
        "versioning": True
    },
    "configuration": {
        "patterns": ["*.json", "*.yaml", "*.xml", "*.config"],
        "priority": "HIGH",
        "versioning": True
    },
    "documentation": {
        "patterns": ["*.md", "requirements.txt", "design.txt"],
        "priority": "MEDIUM",
        "versioning": True
    },
    "generated": {
        "patterns": ["specs/*", "docs/*", "reports/*"],
        "priority": "LOW",
        "versioning": False
    }
}
```

## 🎯 履歴管理システム

### 変更追跡
```python
class ChangeTracker:
    def __init__(self):
        self.history_file = ".tmp/backups/change_history.json"
        self.current_session = {
            "session_id": generate_session_id(),
            "start_time": datetime.now(),
            "changes": []
        }
    
    def track_change(self, file_path, action, agent, reason=""):
        change_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "action": action,  # CREATE, MODIFY, DELETE, RENAME
            "agent": f"{agent.emoji} {agent.name}",
            "reason": reason,
            "backup_location": self._create_backup(file_path),
            "checksum": self._calculate_checksum(file_path)
        }
        self.current_session["changes"].append(change_entry)
        self._save_history()
```

### 自動復元機能
```python
class AutoRestore:
    def restore_to_checkpoint(self, checkpoint_id):
        """チェックポイントへの自動復元"""
        checkpoint = self._load_checkpoint(checkpoint_id)
        
        # エージェントログ
        print(f"[{timestamp}] 🔄 自動復元 > チェックポイント {checkpoint_id} へ復元中...")
        
        for file_info in checkpoint["files"]:
            self._restore_file(file_info["backup_path"], file_info["original_path"])
        
        print(f"[{timestamp}] ✅ 復元完了 > {len(checkpoint['files'])} ファイルを復元")
```

## 📊 バージョン管理

### セマンティックバージョニング
```python
version_schema = {
    "major": "破壊的変更（APIの変更、データ構造の変更）",
    "minor": "機能追加（新規機能、拡張）",
    "patch": "バグ修正（修正、最適化）",
    "build": "ビルド番号（自動インクリメント）"
}

# 例: requirements_v1.2.3.build456.md
```

### 差分管理
```python
class DiffManager:
    def create_diff(self, old_file, new_file):
        """変更差分を生成して保存"""
        diff_content = self._generate_diff(old_file, new_file)
        diff_file = f".tmp/backups/diffs/{timestamp}_{file_name}.diff"
        
        # 差分が小さければ差分のみ保存（容量削減）
        if len(diff_content) < len(new_file) * 0.3:
            self._save_diff(diff_file, diff_content)
            return {"type": "diff", "path": diff_file}
        else:
            return {"type": "full", "path": self._create_full_backup(new_file)}
```

## 🤖 エージェント自律動作

### 解析時の自動管理
```python
def analyze_project_with_backup(project_path):
    """プロジェクト解析時の自動バックアップ"""
    
    # 開始時のスナップショット
    print(f"[{timestamp}] 📸 スナップショット作成中...")
    snapshot_id = backup_manager.create_snapshot(project_path)
    
    # 解析実行
    print(f"[{timestamp}] 🔍 プロジェクト解析開始...")
    analysis_results = analyze_project(project_path)
    
    # ドキュメント生成（ユーザー確認不要）
    print(f"[{timestamp}] 📝 ドキュメント自動生成中...")
    docs_path = ".tmp/generated_docs/"
    generate_requirements_doc(analysis_results, docs_path)
    generate_design_doc(analysis_results, docs_path)
    
    # 完了時のチェックポイント
    checkpoint_id = backup_manager.create_checkpoint(
        "analysis_complete",
        files=[docs_path],
        metadata={"snapshot": snapshot_id}
    )
    
    print(f"[{timestamp}] ✅ 解析完了 - チェックポイント: {checkpoint_id}")
    return analysis_results
```

### 修正作業時の自動管理
```python
def modify_with_protection(file_path, modifications):
    """修正作業時の自動保護"""
    
    # 修正前バックアップ（サイレント）
    backup_path = backup_manager.instant_backup(file_path)
    
    try:
        # 修正実行
        print(f"[{timestamp}] 🔧 {file_path} を修正中...")
        apply_modifications(file_path, modifications)
        
        # 成功時は差分を記録
        diff_manager.create_diff(backup_path, file_path)
        print(f"[{timestamp}] ✅ 修正完了")
        
    except Exception as e:
        # エラー時は自動復元
        print(f"[{timestamp}] ⚠️ エラー検出 - 自動復元中...")
        backup_manager.restore_instant(backup_path, file_path)
        print(f"[{timestamp}] ✅ 復元完了")
        raise e
```

## 🧹 自動クリーンアップ

### 保持ポリシー
```python
retention_policy = {
    "instant": {
        "max_age_hours": 24,
        "max_count": 100,
        "cleanup_interval": "hourly"
    },
    "checkpoint": {
        "max_age_days": 7,
        "max_count": 50,
        "cleanup_interval": "daily"
    },
    "archive": {
        "max_age_days": 30,
        "max_size_gb": 10,
        "cleanup_interval": "weekly"
    }
}
```

### インテリジェントクリーンアップ
```python
def intelligent_cleanup():
    """重要度に基づく自動クリーンアップ"""
    
    # 重複排除
    remove_duplicate_backups()
    
    # 古い差分をフルバックアップに統合
    consolidate_old_diffs()
    
    # 重要度の低いバックアップを圧縮
    compress_low_priority_backups()
    
    # 期限切れファイルを削除
    remove_expired_files()
```

## 📈 容量管理

### 容量モニタリング
```python
class StorageMonitor:
    def check_usage(self):
        usage = {
            "instant": self._get_folder_size(".tmp/backups/instant"),
            "checkpoint": self._get_folder_size(".tmp/backups/checkpoint"),
            "archive": self._get_folder_size(".tmp/backups/archive"),
            "total": self._get_folder_size(".tmp/backups")
        }
        
        if usage["total"] > self.max_size * 0.8:
            print(f"[{timestamp}] ⚠️ ストレージ警告: {usage['total']/1GB:.2f}GB使用中")
            self.trigger_cleanup()
```

## 🔐 セキュリティ

### チェックサム検証
- すべてのバックアップにSHA-256チェックサム付与
- 復元時の整合性検証
- 改ざん検出

### アクセスログ
```python
access_log = {
    "timestamp": "2025-08-16 14:30:00",
    "agent": "CTO",
    "action": "backup_created",
    "file": "requirements.md",
    "backup_id": "bkp_20250816_143000_req",
    "checksum": "sha256:abcd1234..."
}
```

## 🎮 ユーザーコマンド（オプション）

ユーザーが必要に応じて使用可能：
```bash
# バックアップ状況確認
/backup-status

# 特定時点への復元
/backup-restore <checkpoint_id>

# 手動チェックポイント作成
/backup-checkpoint "重要な変更完了"

# クリーンアップ実行
/backup-cleanup
```

---

*この自動バックアップシステムにより、エージェントは完全に自律的にファイル管理を行い、ユーザーの作業を中断することなく安全性を確保します。*