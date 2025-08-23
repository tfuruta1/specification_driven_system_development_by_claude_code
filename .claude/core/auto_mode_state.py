#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode State Management
Auto-Mode状態管理モジュール
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from .activity_logger import logger
    from .jst_utils import format_jst_datetime
    from .auto_mode_interfaces import StateInterface
except ImportError:
    # スタンドアロン実行用
    import logging
    logger = logging.getLogger(__name__)
    from jst_utils import format_jst_datetime
    from auto_mode_interfaces import StateInterface


class AutoModeState(StateInterface):
    """Auto-Mode状態管理クラス"""
    
    # StateInterfaceの抽象プロパティ実装
    @property
    def is_active(self) -> bool:
        """アクティブ状態"""
        return self._is_active
    
    @property
    def start_time(self) -> Optional[str]:
        """開始時刻"""
        return self._start_time
    
    @property
    def current_session(self) -> Optional[str]:
        """現在のセッション"""
        return self._current_session
    
    @property
    def session_count(self) -> int:
        """セッション数"""
        return self._session_count
    
    @property
    def session_data(self) -> Dict[str, Any]:
        """セッションデータ"""
        return self._session_data
    
    def __init__(self):
        """状態初期化"""
        self._is_active = False
        self._start_time = None
        self._current_session = None
        self._session_count = 0
        self._session_data = {}  # セッション別データ保存
        
    def start(self) -> str:
        """
        セッション開始
        
        Returns:
            セッションID
        """
        self._is_active = True
        self.start_time = format_jst_datetime()
        session_id = str(uuid.uuid4())[:8]
        self._current_session = session_id
        self._session_count += 1
        
        # セッションデータ初期化
        self._session_data[session_id] = {
            'start_time': self._start_time,
            'commands_executed': 0,
            'test_results': [],
            'errors': [],
            'warnings': []
        }
        
        logger.info(f"Auto-Mode: セッション開始 - {session_id}", "AUTO_MODE")
        return session_id
        
    def stop(self):
        """セッション停止"""
        if self._is_active and self._current_session:
            # セッション終了時間を記録
            if self._current_session in self._session_data:
                self._session_data[self._current_session]['end_time'] = format_jst_datetime()
            
            logger.info(f"Auto-Mode: セッション停止 - {self._current_session}", "AUTO_MODE")
        
        self._is_active = False
        self._current_session = None
        
    def get_status(self) -> Dict[str, Any]:
        """
        現在の状態取得
        
        Returns:
            状態辞書
        """
        status = {
            'active': self._is_active,
            'start_time': self._start_time,
            'session_id': self._current_session,
            'session_count': self._session_count
        }
        
        if self._current_session and self._current_session in self._session_data:
            current_data = self._session_data[self._current_session]
            status.update({
                'commands_executed': current_data['commands_executed'],
                'test_results_count': len(current_data['test_results']),
                'errors_count': len(current_data['errors']),
                'warnings_count': len(current_data['warnings'])
            })
        
        return status

    def increment_command_count(self):
        """コマンド実行回数をインクリメント"""
        if self._current_session and self._current_session in self._session_data:
            self._session_data[self._current_session]['commands_executed'] += 1

    def add_test_result(self, test_result: Dict[str, Any]):
        """テスト結果を追加"""
        if self._current_session and self._current_session in self._session_data:
            self._session_data[self._current_session]['test_results'].append({
                'timestamp': format_jst_datetime(),
                'result': test_result
            })

    def add_error(self, error: str):
        """エラーを記録"""
        if self._current_session and self._current_session in self._session_data:
            self._session_data[self._current_session]['errors'].append({
                'timestamp': format_jst_datetime(),
                'error': error
            })

    def add_warning(self, warning: str):
        """警告を記録"""
        if self._current_session and self._current_session in self._session_data:
            self._session_data[self._current_session]['warnings'].append({
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
        target_session = session_id or self._current_session
        
        if not target_session or target_session not in self._session_data:
            return None
        
        data = self._session_data[target_session]
        
        return {
            'session_id': target_session,
            'start_time': data['start_time'],
            'end_time': data.get('end_time', '進行中'),
            'commands_executed': data['commands_executed'],
            'test_results': len(data['test_results']),
            'errors': len(data['errors']),
            'warnings': len(data['warnings']),
            'is_active': target_session == self._current_session and self._is_active
        }

    def get_all_sessions_summary(self) -> List[Dict[str, Any]]:
        """全セッションの要約を取得"""
        return [
            self.get_session_summary(session_id) 
            for session_id in self._session_data.keys()
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
                if session_id in self._session_data:
                    del self._session_data[session_id]
                    logger.info(f"Auto-Mode: セッションデータクリア - {session_id}", "AUTO_MODE")
                    return True
                return False
            else:
                # 全セッションクリア
                self._session_data.clear()
                self._session_count = 0
                logger.info("Auto-Mode: 全セッションデータクリア", "AUTO_MODE")
                return True
        except Exception as e:
            logger.error(f"Auto-Mode: セッションデータクリアエラー - {e}", "AUTO_MODE")
            return False

    def is_session_active(self) -> bool:
        """セッションがアクティブかどうか"""
        return self._is_active and self._current_session is not None

    def get_uptime(self) -> Optional[str]:
        """
        現在のセッションのアップタイムを取得
        
        Returns:
            アップタイム文字列（セッションが非アクティブの場合はNone）
        """
        if not self._is_active or not self.start_time:
            return None
        
        try:
            # JST文字列を datetime オブジェクトにパース（簡易版）
            # 実際の実装では適切なパースロジックが必要
            return f"開始: {self.start_time}"
        except Exception as e:
            logger.error(f"Auto-Mode: アップタイム計算エラー - {e}", "AUTO_MODE")
            return None

# ServiceLocatorパターンで管理 - シングルトン不要