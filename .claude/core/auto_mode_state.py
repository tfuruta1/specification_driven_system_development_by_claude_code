#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode State Management
Auto-Mode状態管理モジュール
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from .activity_logger import logger
from .jst_utils import format_jst_datetime
from .auto_mode_interfaces import StateInterface


class AutoModeState(StateInterface):
    """Auto-Mode状態管理クラス"""
    
    def __init__(self):
        """状態初期化"""
        self.is_active = False
        self.start_time = None
        self.current_session = None
        self.session_count = 0
        self.session_data = {}  # セッション別データ保存
        
    def start(self) -> str:
        """
        セッション開始
        
        Returns:
            セッションID
        """
        self.is_active = True
        self.start_time = format_jst_datetime()
        session_id = str(uuid.uuid4())[:8]
        self.current_session = session_id
        self.session_count += 1
        
        # セッションデータ初期化
        self.session_data[session_id] = {
            'start_time': self.start_time,
            'commands_executed': 0,
            'test_results': [],
            'errors': [],
            'warnings': []
        }
        
        logger.info(f"Auto-Mode: セッション開始 - {session_id}", "AUTO_MODE")
        return session_id
        
    def stop(self):
        """セッション停止"""
        if self.is_active and self.current_session:
            # セッション終了時間を記録
            if self.current_session in self.session_data:
                self.session_data[self.current_session]['end_time'] = format_jst_datetime()
            
            logger.info(f"Auto-Mode: セッション停止 - {self.current_session}", "AUTO_MODE")
        
        self.is_active = False
        self.current_session = None
        
    def get_status(self) -> Dict[str, Any]:
        """
        現在の状態取得
        
        Returns:
            状態辞書
        """
        status = {
            'active': self.is_active,
            'start_time': self.start_time,
            'session_id': self.current_session,
            'session_count': self.session_count
        }
        
        if self.current_session and self.current_session in self.session_data:
            current_data = self.session_data[self.current_session]
            status.update({
                'commands_executed': current_data['commands_executed'],
                'test_results_count': len(current_data['test_results']),
                'errors_count': len(current_data['errors']),
                'warnings_count': len(current_data['warnings'])
            })
        
        return status

    def increment_command_count(self):
        """コマンド実行回数をインクリメント"""
        if self.current_session and self.current_session in self.session_data:
            self.session_data[self.current_session]['commands_executed'] += 1

    def add_test_result(self, test_result: Dict[str, Any]):
        """テスト結果を追加"""
        if self.current_session and self.current_session in self.session_data:
            self.session_data[self.current_session]['test_results'].append({
                'timestamp': format_jst_datetime(),
                'result': test_result
            })

    def add_error(self, error: str):
        """エラーを記録"""
        if self.current_session and self.current_session in self.session_data:
            self.session_data[self.current_session]['errors'].append({
                'timestamp': format_jst_datetime(),
                'error': error
            })

    def add_warning(self, warning: str):
        """警告を記録"""
        if self.current_session and self.current_session in self.session_data:
            self.session_data[self.current_session]['warnings'].append({
                'timestamp': format_jst_datetime(),
                'warning': warning
            })

    def get_session_summary(self, session_id: str = None) -> Optional[Dict[str, Any]]:
        """
        セッション要約を取得
        
        Args:
            session_id: セッションID（Noneの場合は現在のセッション）
            
        Returns:
            セッション要約データ
        """
        target_session = session_id or self.current_session
        
        if not target_session or target_session not in self.session_data:
            return None
        
        data = self.session_data[target_session]
        
        return {
            'session_id': target_session,
            'start_time': data['start_time'],
            'end_time': data.get('end_time', '進行中'),
            'commands_executed': data['commands_executed'],
            'test_results': len(data['test_results']),
            'errors': len(data['errors']),
            'warnings': len(data['warnings']),
            'is_active': target_session == self.current_session and self.is_active
        }

    def get_all_sessions_summary(self) -> List[Dict[str, Any]]:
        """全セッションの要約を取得"""
        return [
            self.get_session_summary(session_id) 
            for session_id in self.session_data.keys()
        ]

    def clear_session_data(self, session_id: str = None) -> bool:
        """
        セッションデータをクリア
        
        Args:
            session_id: セッションID（Noneの場合は全セッション）
            
        Returns:
            成功フラグ
        """
        try:
            if session_id:
                if session_id in self.session_data:
                    del self.session_data[session_id]
                    logger.info(f"Auto-Mode: セッションデータクリア - {session_id}", "AUTO_MODE")
                    return True
                return False
            else:
                # 全セッションクリア
                self.session_data.clear()
                self.session_count = 0
                logger.info("Auto-Mode: 全セッションデータクリア", "AUTO_MODE")
                return True
        except Exception as e:
            logger.error(f"Auto-Mode: セッションデータクリアエラー - {e}", "AUTO_MODE")
            return False

    def is_session_active(self) -> bool:
        """セッションがアクティブかどうか"""
        return self.is_active and self.current_session is not None

    def get_uptime(self) -> Optional[str]:
        """
        現在のセッションのアップタイムを取得
        
        Returns:
            アップタイム文字列（セッションが非アクティブの場合はNone）
        """
        if not self.is_active or not self.start_time:
            return None
        
        try:
            # JST文字列を datetime オブジェクトにパース（簡易版）
            # 実際の実装では適切なパースロジックが必要
            return f"開始: {self.start_time}"
        except Exception as e:
            logger.error(f"Auto-Mode: アップタイム計算エラー - {e}", "AUTO_MODE")
            return None

# シングルトンインスタンス削除 - サービスロケーターパターンを使用