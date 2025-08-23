#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Session Manager
セッション管理専用モジュール - 単一責任原則に基づく分離
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .jst_utils import format_jst_datetime, get_filename_timestamp
from .shared_logger import OptimizedLogger
from .error_handler import StandardErrorHandler


class SessionManager:
    """
    セッション管理クラス
    
    セッション作成、ログ記録、状態管理を担当。
    KISS原則に基づいたシンプルな実装。
    """
    
    def __init__(self, base_dir: Path, logger: OptimizedLogger, error_handler: StandardErrorHandler):
        """
        SessionManager初期化
        
        Args:
            base_dir: ベースディレクトリ
            logger: 統合ロガー
            error_handler: エラーハンドラー
        """
        self.base_dir = base_dir
        self.logger = logger
        self.error_handler = error_handler
        
        # ActivityReportディレクトリ準備
        self.report_dir = self.base_dir / "ActivityReport"
        self._ensure_report_dir()
        
    def _ensure_report_dir(self):
        """レポートディレクトリ確保（エラーハンドリング付き）"""
        try:
            self.report_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.error_handler.handle_file_operation_error(
                "mkdir", self.report_dir, e
            )
    
    def create_session(self, session_id: str, start_time: str, 
                      flow_type: str, mode: str) -> Dict[str, Any]:
        """
        セッション情報作成
        
        Args:
            session_id: セッションID
            start_time: 開始時刻
            flow_type: フロータイプ  
            mode: モード
            
        Returns:
            セッション辞書
        """
        return {
            'session_id': session_id,
            'start_time': start_time,
            'flow_type': flow_type,
            'mode': mode,
            'timestamp': get_filename_timestamp()
        }
        
    def log_session_start(self, session: Dict[str, Any]) -> bool:
        """
        セッション開始ログ記録
        
        Args:
            session: セッション情報
            
        Returns:
            成功かどうか
        """
        try:
            log_file = self.report_dir / f"auto_mode_session_{session['session_id']}.md"
            
            content = self._generate_session_start_content(session)
            
            log_file.write_text(content, encoding='utf-8')
            self.logger.log_with_context(
                "info", f"セッションログ作成: {log_file.name}",
                {"session_id": session['session_id']}
            )
            return True
            
        except Exception as e:
            self.error_handler.handle_file_operation_error(
                "session_log_creation", log_file, e
            )
            return False
            
    def log_session_end(self, session_id: str) -> bool:
        """
        セッション終了ログ記録
        
        Args:
            session_id: セッションID
            
        Returns:
            成功かどうか
        """
        try:
            log_file = self.report_dir / f"auto_mode_session_{session_id}.md"
            
            if not log_file.exists():
                self.logger.log_with_context(
                    "warning", f"セッションログファイルが存在しません: {session_id}",
                    {"session_id": session_id}
                )
                return False
                
            # 既存内容読み取り
            content = log_file.read_text(encoding='utf-8')
            
            # 終了ログ追加
            end_log = self._generate_session_end_content()
            content += end_log
            
            log_file.write_text(content, encoding='utf-8')
            self.logger.log_with_context(
                "info", f"セッションログ更新: {log_file.name}",
                {"session_id": session_id}
            )
            return True
            
        except Exception as e:
            self.error_handler.handle_file_operation_error(
                "session_log_update", log_file, e
            )
            return False
            
    def _generate_session_start_content(self, session: Dict[str, Any]) -> str:
        """セッション開始ログ内容生成"""
        return f"""# Auto-Mode セッションログ
**セッションID**: {session['session_id']}
**開始時刻**: {session['start_time']}
**開発フロー**: {session['flow_type']}
**モード**: {session['mode']}

## セッション概要
アレックスとのペアプログラミングセッションを開始しました。

### 選択フロー: {session['flow_type']}

## 作業ログ
"""
    
    def _generate_session_end_content(self) -> str:
        """セッション終了ログ内容生成"""
        return f"""

## セッション終了
**終了時刻**: {format_jst_datetime()}
**ステータス**: 正常終了

ペアプログラミングセッションが完了しました。
"""

    def get_session_log_path(self, session_id: str) -> Path:
        """
        セッションログパス取得
        
        Args:
            session_id: セッションID
            
        Returns:
            ログファイルパス
        """
        return self.report_dir / f"auto_mode_session_{session_id}.md"
        
    def session_log_exists(self, session_id: str) -> bool:
        """
        セッションログ存在確認
        
        Args:
            session_id: セッションID
            
        Returns:
            存在するかどうか
        """
        return self.get_session_log_path(session_id).exists()