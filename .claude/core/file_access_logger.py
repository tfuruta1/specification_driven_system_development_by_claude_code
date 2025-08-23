#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileAccessLogger - ファイルアクセス目的表示システム
TDD Green Phase: テストを通すための実装
"""

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional

# 既存システムとの統合
from logger import logger as unified_logger
from jst_utils import get_jst_now, format_jst_time
from error_handler import StandardErrorHandler


class AccessPurpose(Enum):
    """ファイルアクセスの目的"""
    MODIFY = ("[修正対象]", "red")
    REFERENCE = ("[参照のみ]", "blue") 
    ANALYZE = ("[解析中]", "yellow")
    
    def __init__(self, display_value: str, color: str):
        self.display_value = display_value
        self.color = color


class ColorTerminal:
    """ターミナル色表示ユーティリティ（Windows互換）"""
    
    # ANSI カラーコード
    COLORS = {
        'red': '\033[31m',
        'blue': '\033[34m',
        'yellow': '\033[33m',
        'green': '\033[32m',
        'reset': '\033[0m'
    }
    
    def __init__(self):
        self.colors_enabled = True
        # Windows環境でのANSI色表示を有効化
        if os.name == 'nt':
            self.enable_windows_colors()
    
    def enable_windows_colors(self):
        """Windows環境でANSI色表示を有効化 - 統合エラーハンドリング使用"""
        try:
            # Windows 10以降でANSI色表示を有効化
            os.system('color')
            # より確実な方法
            import subprocess
            subprocess.run([''], shell=True)
        except Exception as e:
            # エラーを無視するがログに記録
            if hasattr(self, 'error_handler'):
                self.error_handler.handle_validation_error(
                    "windows_colors", "color_setup", "Windows色表示設定失敗", e
                )
    
    def colorize(self, text: str, color: str) -> str:
        """テキストに色を付ける"""
        if not self.colors_enabled or color not in self.COLORS:
            return text
        
        return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"
    
    def print_colored(self, text: str, color: str):
        """色付きテキストを出力"""
        colored_text = self.colorize(text, color)
        sys.stdout.write(colored_text + '\n')
        sys.stdout.flush()


class FileAccessLogger:
    """ファイルアクセス目的表示システム"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """初期化 - 統合エラーハンドリング使用"""
        # エラーハンドラー初期化
        self.error_handler = StandardErrorHandler()
        
        # ベースディレクトリ設定（エラーハンドリング付き）
        self.base_dir = Path(base_dir) if base_dir else Path('.claude/logs')
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.error_handler.handle_file_operation_error(
                "mkdir", self.base_dir, e
            )
        
        # セッション情報
        self.session_id = str(uuid.uuid4())[:8]
        self.session_start = get_jst_now()
        
        # カラーターミナル
        self.terminal = ColorTerminal()
        
        # ログファイル設定
        date_str = self.session_start.strftime('%Y-%m-%d')
        time_str = self.session_start.strftime('%H%M%S')
        self.session_log_file = self.base_dir / f"{date_str}_{time_str}_file_access.log"
        self.json_log_file = self.base_dir / "file_access.json"
        
        # セッション開始ログ
        self._init_session_log()
        
        # アクセス履歴
        self.access_history: List[Dict] = []
    
    def _init_session_log(self):
        """セッションログの初期化"""
        header = f"""
=== File Access Logger Session Start ===
Session ID: {self.session_id}
Start Time: {format_jst_time()}
===========================================

"""
        with open(self.session_log_file, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def log_file_access(self, file_path: str, purpose: AccessPurpose, description: str):
        """ファイルアクセスをログに記録"""
        timestamp = get_jst_now()
        
        # ファイル名抽出
        filename = self.extract_filename(file_path)
        relative_path = self.convert_to_relative_path(file_path)
        
        # ターミナル表示用メッセージ
        display_message = f"{purpose.display_value} {filename} - {description}"
        colored_message = self.terminal.colorize(display_message, purpose.color)
        
        # ターミナルに出力
        print(colored_message)
        
        # セッションログファイルに記録
        log_entry = f"[{format_jst_time()}] {purpose.display_value} {relative_path} - {description}\n"
        with open(self.session_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # 構造化JSONログに記録
        json_entry = {
            'timestamp': format_jst_time(),
            'session_id': self.session_id,
            'file_path': relative_path,
            'filename': filename,
            'purpose': purpose.name,
            'purpose_display': purpose.display_value,
            'description': description,
            'color': purpose.color
        }
        
        # JSONファイルに追記（単一エントリとして）
        with open(self.json_log_file, 'w', encoding='utf-8') as f:
            json.dump(json_entry, f, ensure_ascii=False, indent=2)
        
        # 履歴に追加
        self.access_history.append(json_entry)
        
        # UnifiedLoggerとの連携
        unified_logger.info(
            f"FILE_ACCESS: {purpose.display_value} {filename} - {description}",
            "FILE_ACCESS_LOGGER"
        )
    
    def convert_to_relative_path(self, file_path: str) -> str:
        """絶対パスを相対パスに変換"""
        try:
            # プロジェクトルートを検出
            current = Path.cwd()
            while current.parent != current:
                if (current / '.claude').exists() or (current / 'package.json').exists():
                    project_root = current
                    break
                current = current.parent
            else:
                project_root = Path.cwd()
            
            # 絶対パスの場合、相対パスに変換
            abs_path = Path(file_path)
            if abs_path.is_absolute():
                try:
                    relative = abs_path.relative_to(project_root)
                    return str(relative).replace('\\', '/')
                except ValueError:
                    # プロジェクトルート外の場合
                    return abs_path.name
            
            # 既に相対パスの場合はそのまま
            return str(Path(file_path)).replace('\\', '/')
            
        except Exception:
            # エラー時はファイル名のみ
            return Path(file_path).name
    
    def extract_filename(self, file_path: str) -> str:
        """ファイル名を抽出"""
        return Path(file_path).name
    
    def get_session_summary(self) -> Dict:
        """セッション概要を取得"""
        total_files = len(self.access_history)
        
        # 目的別集計
        by_purpose = {}
        file_list = []
        
        for entry in self.access_history:
            purpose = entry['purpose']
            by_purpose[purpose] = by_purpose.get(purpose, 0) + 1
            file_list.append({
                'filename': entry['filename'],
                'purpose': entry['purpose_display'],
                'description': entry['description']
            })
        
        return {
            'session_id': self.session_id,
            'session_start': format_jst_time(),
            'total_files': total_files,
            'by_purpose': by_purpose,
            'file_list': file_list
        }
    
    def print_session_summary(self):
        """セッション概要を表示"""
        summary = self.get_session_summary()
        
        print("\n" + "="*50)
        print(f"File Access Session Summary")
        print("="*50)
        print(f"Session ID: {summary['session_id']}")
        print(f"Total Files: {summary['total_files']}")
        print(f"\nBy Purpose:")
        
        for purpose, count in summary['by_purpose'].items():
            purpose_enum = getattr(AccessPurpose, purpose)
            colored_purpose = self.terminal.colorize(purpose_enum.display_value, purpose_enum.color)
            print(f"  {colored_purpose}: {count} files")
        
        print(f"\nFile List:")
        for file_info in summary['file_list']:
            print(f"  {file_info['purpose']} {file_info['filename']} - {file_info['description']}")
        
        print("="*50)


# 便利な関数
def log_modify(file_path: str, description: str):
    """修正対象ファイルをログ"""
    _get_logger().log_file_access(file_path, AccessPurpose.MODIFY, description)

def log_reference(file_path: str, description: str):
    """参照のみファイルをログ"""
    _get_logger().log_file_access(file_path, AccessPurpose.REFERENCE, description)

def log_analyze(file_path: str, description: str):
    """解析中ファイルをログ"""
    _get_logger().log_file_access(file_path, AccessPurpose.ANALYZE, description)


# シングルトンインスタンス管理
_logger_instance = None

def _get_logger() -> FileAccessLogger:
    """シングルトンロガーを取得"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = FileAccessLogger()
    return _logger_instance


# 使用例とテスト
if __name__ == "__main__":
    # デモンストレーション
    logger = FileAccessLogger()
    
    print("File Access Logger Demo:")
    print("-" * 30)
    
    # 各種アクセスパターンのデモ
    logger.log_file_access(
        "src/views/desktop/CheckSheetReview.vue",
        AccessPurpose.MODIFY,
        "レイアウト調整実装中"
    )
    
    logger.log_file_access(
        "src/views/desktop/DailyPlanSetting.vue", 
        AccessPurpose.REFERENCE,
        "グリッドパターン確認"
    )
    
    logger.log_file_access(
        "src/components/ActionButtons.vue",
        AccessPurpose.ANALYZE,
        "関連コンポーネント調査"
    )
    
    # セッション概要表示
    logger.print_session_summary()