#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Core Controller
Auto-Modeコア制御モジュール - リファクタリング済み（200行以下）
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

from .test_strategy import TestStrategy
from .integration_test_runner import IntegrationTestRunner

# 統合システムインポート
from .shared_logger import OptimizedLogger
from .error_handler import StandardErrorHandler

# 分離されたモジュールインポート
from .auto_mode_session import SessionManager
from .auto_mode_workflow import WorkflowExecutor
from .auto_mode_integration import IntegrationController


# 循環依存回避のため遅延インポート
def _get_auto_config():
    """
    auto_configの遅延インポート
    
    循環依存を回避するために遅延インポートパターンを使用。
    AutoModeConfigインスタンスへの安全なアクセスを提供。
    
    Returns:
        AutoModeConfig: 設定管理インスタンス
    """
    from .auto_mode_config import auto_config
    return auto_config

def _get_auto_state():
    """
    auto_stateの遅延インポート
    
    循環依存を回避するために遅延インポートパターンを使用。
    AutoModeStateインスタンスへの安全なアクセスを提供。
    
    Returns:
        AutoModeState: 状態管理インスタンス
    """
    from .auto_mode_state import auto_state
    return auto_state


class AutoMode:
    """Auto-Modeコアクラス - リファクタリング済み"""
    
    def __init__(self, base_dir: str = ".claude"):
        """
        Auto-Mode初期化 - 分離されたコンポーネント使用
        
        Args:
            base_dir: ベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.config = _get_auto_config()
        self.state = _get_auto_state()
        
        # 統合ロガーとエラーハンドラー初期化
        self.logger = OptimizedLogger(user="auto_mode", base_path=self.base_dir)
        self.error_handler = StandardErrorHandler(logger=self.logger)
        
        # テスト戦略と統合テスト実行器初期化
        self.test_strategy = TestStrategy()
        self.integration_runner = IntegrationTestRunner()
        
        # 分離されたコンポーネント初期化
        self.session_manager = SessionManager(
            self.base_dir, self.logger, self.error_handler
        )
        self.workflow_executor = WorkflowExecutor(
            self.test_strategy, self.logger, self.error_handler
        )
        self.integration_controller = IntegrationController(
            self.integration_runner, self.logger, self.error_handler
        )
        
        # 統合テスト設定適用
        self._setup_integration_tests()
        
    def execute_command(self, command: str, args: List[str] = None) -> Any:
        """
        コマンド実行
        
        Args:
            command: コマンド名 (start/stop/status)
            args: コマンド引数
            
        Returns:
            実行結果
        """
        if args is None:
            args = []
            
        self.logger.log_with_context("info", f"/auto-mode {command} を実行中...", 
                                   {"command": command, "args": args})
        
        if command == "start":
            return self._start_auto_mode()
        elif command == "stop":
            return self._stop_auto_mode()
        elif command == "status":
            return self._get_status()
        else:
            self.error_handler.handle_validation_error(
                "command", command, "有効なコマンド名", 
                suggestions=["start", "stop", "status"]
            )
            return False
            
    def _start_auto_mode(self) -> bool:
        """Auto-Mode開始 - 分離されたコンポーネント使用"""
        with self.error_handler.error_context("auto_mode_start"):
            if self.state.is_active:
                self.logger.log_with_context("warning", "Auto-Mode は既に開始されています")
                return True
            
            # セッション開始
            session_id = self.state.start()
            
            # 設定更新
            self.config.enable()
            flow = self._select_flow()
            self.config.set_flow(flow)
            
            # セッション情報作成とログ記録
            session = self.session_manager.create_session(
                session_id, self.state.start_time, flow, self.config.mode
            )
            self.session_manager.log_session_start(session)
            
            self.logger.log_with_context("info", "Auto-Mode開始完了", 
                                       {"session_id": session_id, "flow": flow})
            return True
            
    def _stop_auto_mode(self) -> bool:
        """Auto-Mode停止"""
        try:
            if not self.state.is_active:
                self.logger.log_with_context("warning", "Auto-Mode は開始されていません")
                return True
            
            # セッション情報取得
            session_id = self.state.current_session
            
            # セッション停止
            self.state.stop()
            self.config.disable()
            
            # セッション終了ログ記録
            self.session_manager.log_session_end(session_id)
            
            self.logger.log_with_context("info", "Auto-Mode停止完了", 
                                       {"session_id": session_id})
            return True
            
        except Exception as e:
            self.error_handler.handle_auto_mode_error("stop", e)
            return False
            
    def _get_status(self) -> Dict[str, Any]:
        """現在の状態取得"""
        status = self.state.get_status()
        status.update({
            'config_enabled': self.config.is_enabled,
            'current_flow': self.config.current_flow,
            'mode': self.config.mode,
            'report_path': str(self.session_manager.report_dir)
        })
        
        # ステータスログ
        if status['active']:
            self.logger.log_with_context("info", "Auto-Mode: アクティブ", status)
        else:
            self.logger.log_with_context("info", "Auto-Mode: 非アクティブ", status)
            
        return status
        
    def _select_flow(self) -> str:
        """
        フロー自動選択
        
        Returns:
            選択されたフロー名
        """
        try:
            # 簡単な選択機構（実際のCLIでは入力受付）
            choice = input("フロー番号を入力 (1-4): ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(self.config.flows):
                return self.config.flows[index]
            else:
                self.logger.log_with_context("warning", "無効な選択です。デフォルトフローを使用します")
                return self.config.flows[0]
                
        except (ValueError, EOFError):
            # 自動テスト時やCLI以外の環境での処理
            return self.config.flows[0]
    
    def _setup_integration_tests(self):
        """統合テスト設定"""
        self.integration_controller.setup_integration_tests(
            circular_import_detection=self.config.circular_import_detection,
            component_connectivity_test=self.config.component_connectivity_test,
            initialization_test=self.config.initialization_test
        )
    
    def is_active(self) -> bool:
        """アクティブ状態確認"""
        return self.state.is_active
        
    def get_tdd_workflow_phases(self) -> List[str]:
        """TDDワークフロー段階取得"""
        return self.workflow_executor.get_tdd_workflow_phases()
        
    def execute_tdd_workflow(self) -> Dict[str, Any]:
        """TDDワークフロー実行"""
        # 統合テストハンドラーを注入してワークフローを実行
        return self.workflow_executor.execute_tdd_workflow(
            integration_test_handler=lambda: self.integration_controller.execute_integration_test_phase(
                self.config.integration_tests_enabled
            )
        )
    
    def execute_integration_test_with_retry(self, max_retries: int = 1) -> Dict[str, Any]:
        """リトライ付き統合テスト実行"""
        return self.integration_controller.execute_integration_test_with_retry(
            max_retries, self.config.integration_tests_enabled
        )
    
    def configure_integration_tests(self, circular_import_detection: Optional[bool] = None,
                                   component_connectivity_test: Optional[bool] = None,
                                   initialization_test: Optional[bool] = None):
        """統合テスト設定変更"""
        # 設定更新
        kwargs = {}
        if circular_import_detection is not None:
            kwargs['circular_import_detection'] = circular_import_detection
        if component_connectivity_test is not None:
            kwargs['component_connectivity_test'] = component_connectivity_test
        if initialization_test is not None:
            kwargs['initialization_test'] = initialization_test
            
        if kwargs:
            self.config.update_integration_settings(**kwargs)
            self._setup_integration_tests()
        
    def is_integration_tests_enabled(self) -> bool:
        """統合テスト有効性確認"""
        return self.config.integration_tests_enabled
        
    def generate_integration_test_report(self, result) -> str:
        """統合テストレポート生成"""
        return self.integration_controller.generate_integration_test_report(result)
        
    def track_integration_test_in_session(self, session_id: str, result):
        """セッション中の統合テスト結果追跡"""
        self.integration_controller.track_integration_test_in_session(session_id, result)
        
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """セッション情報取得"""
        return self.state.session_data.get(session_id, {})


# ユーティリティ関数
def create_auto_mode(base_dir: str = ".claude") -> AutoMode:
    """
    AutoModeインスタンス作成
    
    Args:
        base_dir: ベースディレクトリ
        
    Returns:
        AutoModeインスタンス
    """
    return AutoMode(base_dir)


# シングルトンインスタンス
auto_mode = AutoMode()


if __name__ == "__main__":
    # デモ実行
    print("=== Auto-Mode Demo ===")
    print("Status:", auto_mode.execute_command("status"))
    print("Start:", auto_mode.execute_command("start"))
    print("Status:", auto_mode.execute_command("status"))
    print("Stop:", auto_mode.execute_command("stop"))
    print("Final Status:", auto_mode.execute_command("status"))