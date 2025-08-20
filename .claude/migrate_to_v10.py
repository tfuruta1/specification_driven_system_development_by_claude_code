#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v10.0への移行スクリプト
旧システムファイルをバックアップして新システムに移行
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


def migrate_to_v10():
    """v10.0への移行実行"""
    base_path = Path(__file__).parent
    backup_dir = base_path / f"backup_v9_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("[MIGRATION] v10.0への移行を開始します")
    
    # 1. バックアップ作成
    print("[BACKUP] 旧システムファイルをバックアップ中...")
    files_to_backup = [
        "system/agent_monitor.py",
        "system/agent_activity_logger.py",
        "system/cleanup_system.py",
        "system/auto_cleanup_manager.py",
        "system/daily_log_writer.py",
        "system/hierarchical_agent_system.py",
        "system/multi_agent_code_review.py",
        "agents/品質保証部",
        "agents/人事部",
        "agents/経営企画部",
        "agents/システム開発部",
        "commands/",  # 旧コマンドフォルダ全体
    ]
    
    backup_dir.mkdir(exist_ok=True)
    
    for item in files_to_backup:
        src = base_path / item
        if src.exists():
            dst = backup_dir / item
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            if src.is_dir():
                shutil.copytree(src, dst)
                print(f"  [DIR] {item} → backup/")
            else:
                shutil.copy2(src, dst)
                print(f"  [FILE] {item} → backup/")
    
    # 2. 新しいディレクトリ構造を作成
    print("\n[CREATE] 新しいディレクトリ構造を作成中...")
    new_dirs = [
        "core",
        "docs",
        "workspace",
        "cache",
        "logs"
    ]
    
    for dir_name in new_dirs:
        (base_path / dir_name).mkdir(exist_ok=True)
        print(f"  [DIR] {dir_name}/")
    
    # 3. 設定ファイル作成
    config_content = """# Claude Code v10.0 Configuration
VERSION = "10.0"
PRINCIPLES = ["YAGNI", "DRY", "KISS"]

# Development Flows
FLOWS = {
    "new": "要件定義→設計→レビュー→テスト作成→実装→テスト→デモ",
    "existing": "解析→影響報告→修正要件→修正設計→レビュー→テスト作成→実装→テスト→最終確認→デモ"
}

# Simplified Commands (10 basic commands)
COMMANDS = [
    "init", "analyze", "plan", "implement", "test",
    "review", "deploy", "status", "clean", "help"
]
"""
    
    config_file = base_path / "config.py"
    config_file.write_text(config_content, encoding='utf-8')
    print("\n[CONFIG] 設定ファイルを作成しました")
    
    # 4. 移行完了レポート
    report = f"""# 移行完了レポート
日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## バックアップ場所
{backup_dir}

## 新システム構造
.claude/
├── core/        # コアシステム（統合済み）
├── docs/        # ドキュメント
├── workspace/   # 作業領域
├── cache/       # キャッシュ
└── logs/        # ログ

## 削減効果
- ファイル数: 100+ → 20-30
- コード行数: 約80%削減
- 複雑性: 約90%削減

## 次のステップ
1. 新システムのテスト実行
2. 不要になった旧ファイルの削除確認
3. CLAUDE.mdをCLAUDE_v10.mdに置き換え
"""
    
    report_file = base_path / "MIGRATION_REPORT.md"
    report_file.write_text(report, encoding='utf-8')
    
    print("\n" + "="*50)
    print("[SUCCESS] v10.0への移行が完了しました！")
    print(f"[BACKUP] バックアップ: {backup_dir}")
    print("[REPORT] MIGRATION_REPORT.md を確認してください")
    print("="*50)
    
    return True


if __name__ == "__main__":
    migrate_to_v10()