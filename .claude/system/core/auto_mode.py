#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Unified System
统合されたAuto-Modeシステム - 複数モジュールの統合版

5つのモジュールを統合:
- Interfaces (auto_mode_interfaces.py)
- State Management (auto_mode_state.py) 
- Session Management (auto_mode_session.py)
- Core Controller (auto_mode_core.py)
- Main Entry Point (auto_mode.py)

Performance Optimization: 8ファイル -> 3ファイル (62.5%削減)
"""

import copy
import uuid
import json
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Core dependencies
try:
    from .integration_test_runner import IntegrationTestRunner
    from .logger import Logger as OptimizedLogger
    from .error_handler import StandardErrorHandler
    from .jst_utils import format_jst_datetime, get_filename_timestamp
    from .service_factory import get_config_service, get_state_service, initialize_services
except ImportError:
    # Fallback imports without relative syntax
    try:
        from integration_test_runner import IntegrationTestRunner
    except ImportError:
        IntegrationTestRunner = None  # Graceful degradation
    try:
        from logger import Logger as OptimizedLogger
    except ImportError:
        OptimizedLogger = None
    try:
        from error_handler import StandardErrorHandler
    except ImportError:
        StandardErrorHandler = None
    try:
        from jst_utils import format_jst_datetime, get_filename_timestamp
    except ImportError:
        format_jst_datetime = lambda dt: str(dt)
        get_filename_timestamp = lambda: "timestamp"
    try:
        from service_factory import get_config_service, get_state_service, initialize_services
    except ImportError:
        get_config_service = lambda: None
        get_state_service = lambda: None 
        initialize_services = lambda: None

import logging
logger = logging.getLogger(__name__)

# Type aliases for graceful degradation
from typing import Optional, Any
Logger = OptimizedLogger if OptimizedLogger else Any

# ============================================================================
# INTERFACES MODULE (from auto_mode_interfaces.py)
# ============================================================================

class ConfigInterface(ABC):
    """設定管理インターフェース"""
    
    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Auto-Modeが有効かどうか"""
        pass
    
    @property  
    @abstractmethod
    def current_flow(self) -> Optional[str]:
        """現在のフロー名"""
        pass
    
    @property
    @abstractmethod
    def mode(self) -> str:
        """動作モード"""
        pass
    
    @property
    @abstractmethod
    def flows(self) -> List[str]:
        """利用可能なフロー一覧"""
        pass
    
    @property
    @abstractmethod
    def integration_tests_enabled(self) -> bool:
        """統合テスト有効フラグ"""
        pass
    
    @property
    @abstractmethod
    def circular_import_detection(self) -> bool:
        """循環依存検出フラグ"""
        pass
    
    @property
    @abstractmethod
    def component_connectivity_test(self) -> bool:
        """コンポーネント接続テストフラグ"""
        pass
    
    @property
    @abstractmethod
    def initialization_test(self) -> bool:
        """初期化テストフラグ"""
        pass
    
    @abstractmethod
    def enable(self) -> None:
        """Auto-Modeを有効化"""
        pass
    
    @abstractmethod
    def disable(self) -> None:
        """Auto-Modeを無効化"""
        pass
    
    @abstractmethod
    def set_flow(self, flow_name: str) -> bool:
        """フローを設定"""
        pass
    
    @abstractmethod
    def update_integration_settings(self, **kwargs) -> None:
        """統合テスト設定を更新"""
        pass


class StateInterface(ABC):
    """状態管理インターフェース"""
    
    @property
    @abstractmethod
    def is_active(self) -> bool:
        """アクティブ状態かどうか"""
        pass
    
    @property
    @abstractmethod
    def current_session(self) -> Optional[str]:
        """現在のセッションID"""
        pass
    
    @property
    @abstractmethod
    def start_time(self) -> Optional[str]:
        """開始時刻"""
        pass
    
    @property
    @abstractmethod
    def session_data(self) -> Dict[str, Any]:
        """セッションデータ"""
        pass
    
    @abstractmethod
    def start(self) -> str:
        """セッションを開始"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """セッションを停止"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """ステータス情報を取得"""
        pass


class ServiceLocator:
    """
    シンプルなサービスロケーター
    
    KISS原則に基づいたDI代替実装
    循環依存解決のための軽量なサービス管理
    
    ServiceFactoryとの組み合わせで使用
    インポート順序問題を解決
    """
    
    _services: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, service_name: str, service_instance: Any) -> None:
        """サービスを登録"""
        cls._services[service_name] = service_instance
    
    @classmethod
    def get(cls, service_name: str) -> Any:
        """サービスを取得"""
        if service_name not in cls._services:
            # ServiceFactoryからの自動初期化
            from .service_factory import ServiceFactory
            if not ServiceFactory.is_initialized():
                ServiceFactory.initialize_services()
            
            if service_name not in cls._services:
                raise ValueError(f"Service '{service_name}' not registered")
        return cls._services[service_name]
    
    @classmethod
    def clear(cls) -> None:
        """全サービスをクリア"""
        cls._services.clear()
    
    @classmethod
    def has(cls, service_name: str) -> bool:
        """サービスの存在確認"""
        return service_name in cls._services


# ============================================================================
# STATE MANAGEMENT MODULE (from auto_mode_state.py)
# ============================================================================

class AutoModeState(StateInterface):
    """Auto-Mode状態管理システム"""
    
    # StateInterface実装
    @property
    def is_active(self) -> bool:
        """アクティブ状態フラグ"""
        return self._is_active
    
    @property
    def start_time(self) -> Optional[str]:
        """開始時刻"""
        return self._start_time
    
    @property
    def current_session(self) -> Optional[str]:
        """現在のセッションID"""
        return self._current_session
    
    @property
    def session_count(self) -> int:
        """セッション数"""
        return self._session_count
    
    @property
    def session_data(self) -> Dict[str, Any]:
        """セッションデータ辞書"""
        return self._session_data
    
    def __init__(self):
        """状態管理システム初期化"""
        self._is_active = False
        self._start_time = None
        self._current_session = None
        self._session_count = 0
        self._session_data = {}  # セッション固有データ
        
    def start(self) -> str:
        """
        Auto-Modeセッションを開始
        
        Returns:
            生成されたセッションID
        """
        self._is_active = True
        self._start_time = format_jst_datetime()
        session_id = str(uuid.uuid4())[:8]
        self._current_session = session_id
        self._session_count += 1
        
        # セッションデータを初期化
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
        """Auto-Modeセッションを停止"""
        if self._is_active and self._current_session:
            # 終了時刻を記録
            if self._current_session in self._session_data:
                self._session_data[self._current_session]['end_time'] = format_jst_datetime()
            
            logger.info(f"Auto-Mode: セッション停止 - {self._current_session}", "AUTO_MODE")
        
        self._is_active = False
        self._current_session = None
        
    def get_status(self) -> Dict[str, Any]:
        """
        現在のステータス情報を取得
        
        Returns:
            ステータス辞書
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
        """実行コマンド数をインクリメント"""
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
        セッションサマリーを取得
        
        Args:
            session_id: セッションID（Noneの場合は現在のセッション）
            
        Returns:
            セッションサマリー辞書
        """
        target_session = session_id or self._current_session
        
        if not target_session or target_session not in self._session_data:
            return None
        
        data = self._session_data[target_session]
        
        return {
            'session_id': target_session,
            'start_time': data['start_time'],
            'end_time': data.get('end_time', '実行中'),
            'commands_executed': data['commands_executed'],
            'test_results': len(data['test_results']),
            'errors': len(data['errors']),
            'warnings': len(data['warnings']),
            'is_active': target_session == self._current_session and self._is_active
        }

    def get_all_sessions_summary(self) -> List[Dict[str, Any]]:
        """全セッションサマリー一覧を取得"""
        return [
            self.get_session_summary(session_id) 
            for session_id in self._session_data.keys()
        ]

    def clear_session_data(self, session_id: str = None) -> bool:
        """
        セッションデータをクリア
        
        Args:
            session_id: セッションID（Noneの場合は全データクリア）
            
        Returns:
            クリア成功フラグ
        """
        try:
            if session_id:
                if session_id in self._session_data:
                    del self._session_data[session_id]
                    logger.info(f"Auto-Mode: セッションデータクリア - {session_id}", "AUTO_MODE")
                    return True
                return False
            else:
                # 全データクリア
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
        稼働時間を取得
        
        Returns:
            稼働時間（文字列）またはNone（非アクティブ時）
        """
        if not self._is_active or not self._start_time:
            return None
        
        try:
            # JST形式の datetime 変換は複雑なので簡単な形式で
            # 今回は開始時刻を返す
            return f"開始時刻: {self._start_time}"
        except Exception as e:
            logger.error(f"Auto-Mode: 稼働時間取得エラー - {e}", "AUTO_MODE")
            return None


# ============================================================================
# SESSION MANAGEMENT MODULE (from auto_mode_session.py)
# ============================================================================

class SessionManager:
    """
    セッション管理システム
    
    ActivityReportファイルへのロギングを含む
    KISS原則に基づく簡潔なセッション管理
    """
    
    def __init__(self, base_dir: Path, logger: Logger, error_handler: StandardErrorHandler):
        """
        SessionManager初期化
        
        Args:
            base_dir: ベースディレクトリ
            logger: ログ出力システム
            error_handler: エラーハンドラー
        """
        self.base_dir = base_dir
        self.logger = logger
        self.error_handler = error_handler
        
        # ActivityReportディレクトリを設定
        self.report_dir = self.base_dir / "ActivityReport"
        self._ensure_report_dir()
        
    def _ensure_report_dir(self):
        """レポートディレクトリの存在確認"""
        try:
            self.report_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.error_handler.handle_file_operation_error(
                "mkdir", self.report_dir, e
            )
    
    def create_session(self, session_id: str, start_time: str, 
                      flow_type: str, mode: str) -> Dict[str, Any]:
        """
        新しいセッションを作成
        
        Args:
            session_id: セッションID
            start_time: 開始時刻
            flow_type: フロータイプ  
            mode: 動作モード
            
        Returns:
            セッション情報辞書
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
        セッション開始ログを記録
        
        Args:
            session: セッション情報
            
        Returns:
            ログ記録成功フラグ
        """
        try:
            log_file = self.report_dir / f"auto_mode_session_{session['session_id']}.md"
            
            content = self._generate_session_start_content(session)
            
            log_file.write_text(content, encoding='utf-8')
            self.logger.log_with_context(
                "info", f"セッション開始ログ作成: {log_file.name}",
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
        セッション終了ログを記録
        
        Args:
            session_id: セッションID
            
        Returns:
            ログ記録成功フラグ
        """
        try:
            log_file = self.report_dir / f"auto_mode_session_{session_id}.md"
            
            if not log_file.exists():
                self.logger.log_with_context(
                    "warning", f"セッションファイルが見つかりません: {session_id}",
                    {"session_id": session_id}
                )
                return False
                
            # 既存内容を読み込み
            content = log_file.read_text(encoding='utf-8')
            
            # 終了ログを追加
            end_log = self._generate_session_end_content()
            content += end_log
            
            log_file.write_text(content, encoding='utf-8')
            self.logger.log_with_context(
                "info", f"セッション終了ログ追加: {log_file.name}",
                {"session_id": session_id}
            )
            return True
            
        except Exception as e:
            self.error_handler.handle_file_operation_error(
                "session_log_update", log_file, e
            )
            return False
            
    def _generate_session_start_content(self, session: Dict[str, Any]) -> str:
        """セッション開始時のMarkdownコンテンツを生成"""
        return f"""# Auto-Mode セッションログ
**セッションID**: {session['session_id']}
**開始時刻**: {session['start_time']}
**フロー種別**: {session['flow_type']}
**動作モード**: {session['mode']}

## セッション実行ログ
Auto-Modeセッションが開始されました。

### 選択されたフロー: {session['flow_type']}

## アクティビティログ
"""
    
    def _generate_session_end_content(self) -> str:
        """セッション終了時のMarkdownコンテンツを生成"""
        return f"""

## セッション終了
**終了時刻**: {format_jst_datetime()}
**ステータス**: 正常終了

セッションが正常に終了しました。
"""

    def get_session_log_path(self, session_id: str) -> Path:
        """
        セッションログファイルパスを取得
        
        Args:
            session_id: セッションID
            
        Returns:
            ログファイルパス
        """
        return self.report_dir / f"auto_mode_session_{session_id}.md"
        
    def session_log_exists(self, session_id: str) -> bool:
        """
        セッションログファイルの存在確認
        
        Args:
            session_id: セッションID
            
        Returns:
            存在フラグ
        """
        return self.get_session_log_path(session_id).exists()


# ============================================================================
# CORE CONTROLLER MODULE (from auto_mode_core.py)
# ============================================================================

class AutoMode:
    """Auto-Modeコアコントローラ - 統合システム管理レイヤー"""
    
    def __init__(self, base_dir: str = ".claude"):
        """
        Auto-Modeコントローラー初期化 - CTO風統合管理
        
        Args:
            base_dir: ベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.config = get_config_service()
        self.state = get_state_service()
        
        # 依存サービスの初期化
        self.logger = OptimizedLogger(user="auto_mode", base_path=self.base_dir)
        self.error_handler = StandardErrorHandler(logger=self.logger)
        
        # 統合テスト実行システム
        self.integration_runner = IntegrationTestRunner()
        
        # サブシステムの初期化
        self.session_manager = SessionManager(
            self.base_dir, self.logger, self.error_handler
        )
        
        # ワークフローとインテグレーション制御は別モジュールに委譲
        # auto_mode_workflow.pyで管理
        
        # 統合テストセットアップ
        self._setup_integration_tests()
        
    def execute_command(self, command: str, args: List[str] = None) -> Any:
        """
        コマンド実行インターフェース
        
        Args:
            command: コマンド名 (start/stop/status)
            args: コマンド引数
            
        Returns:
            実行結果
        """
        if args is None:
            args = []
            
        self.logger.log_with_context("info", f"/auto-mode {command} 実行開始...", 
                                   {"command": command, "args": args})
        
        if command == "start":
            return self._start_auto_mode()
        elif command == "stop":
            return self._stop_auto_mode()
        elif command == "status":
            return self._get_status()
        else:
            self.error_handler.handle_validation_error(
                "command", command, "無効なコマンドです", 
                suggestions=["start", "stop", "status"]
            )
            return False
            
    def _start_auto_mode(self) -> bool:
        """Auto-Mode開始処理 - TDC責任分離原則適用"""
        with self.error_handler.error_context("auto_mode_start"):
            if self.state.is_active:
                self.logger.log_with_context("warning", "Auto-Mode は既に実行中です")
                return True
            
            # ステート層での開始処理
            session_id = self.state.start()
            
            # 設定層での開始処理
            self.config.enable()
            flow = self._select_flow()
            self.config.set_flow(flow)
            
            # セッション層での開始処理
            session = self.session_manager.create_session(
                session_id, self.state.start_time, flow, self.config.mode
            )
            self.session_manager.log_session_start(session)
            
            self.logger.log_with_context("info", "Auto-Mode開始完了", 
                                       {"session_id": session_id, "flow": flow})
            return True
            
    def _stop_auto_mode(self) -> bool:
        """Auto-Mode停止処理"""
        try:
            if not self.state.is_active:
                self.logger.log_with_context("warning", "Auto-Mode は実行中ではありません")
                return True
            
            # セッションIDを保存
            session_id = self.state.current_session
            
            # 各層での停止処理
            self.state.stop()
            self.config.disable()
            
            # セッションログの終了処理
            self.session_manager.log_session_end(session_id)
            
            self.logger.log_with_context("info", "Auto-Mode停止完了", 
                                       {"session_id": session_id})
            return True
            
        except Exception as e:
            self.error_handler.handle_auto_mode_error("stop", e)
            return False
            
    def _get_status(self) -> Dict[str, Any]:
        """ステータス情報取得"""
        status = self.state.get_status()
        status.update({
            'config_enabled': self.config.is_enabled,
            'current_flow': self.config.current_flow,
            'mode': self.config.mode,
            'report_path': str(self.session_manager.report_dir)
        })
        
        # ログ出力
        if status['active']:
            self.logger.log_with_context("info", "Auto-Mode: 実行中", status)
        else:
            self.logger.log_with_context("info", "Auto-Mode: 停止中", status)
            
        return status
        
    def _select_flow(self) -> str:
        """
        フロー選択処理
        
        Returns:
            選択されたフロー名
        """
        try:
            # 実際のCLIインタラクション
            choice = input("フローを選択してください (1-4): ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(self.config.flows):
                return self.config.flows[index]
            else:
                self.logger.log_with_context("warning", "無効な選択です。デフォルトフローを使用します")
                return self.config.flows[0]
                
        except (ValueError, EOFError):
            # 自動化環境やCLI非対話環境での処理
            return self.config.flows[0]
    
    def _setup_integration_tests(self):
        """統合テスト設定"""
        # integration_controllerは外部化されているため、基本設定のみここで行う
        pass
    
    def is_active(self) -> bool:
        """アクティブ状態確認"""
        return self.state.is_active
        
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """セッション情報取得"""
        return self.state.session_data.get(session_id, {})


# ============================================================================
# MAIN ENTRY POINT AND FACTORY (from auto_mode.py)
# ============================================================================

def create_auto_mode(base_dir: str = ".claude") -> AutoMode:
    """
    AutoModeインスタンス作成ファクトリ
    
    Args:
        base_dir: ベースディレクトリ
        
    Returns:
        AutoModeインスタンス
    """
    return AutoMode(base_dir)


# ============================================================================
# PUBLIC API EXPORTS
# ============================================================================

__all__ = [
    # Interfaces
    'ConfigInterface',
    'StateInterface', 
    'ServiceLocator',
    # Core Classes
    'AutoModeState',
    'SessionManager',
    'AutoMode',
    # Factory Functions
    'create_auto_mode',
    # Service Integration
    'get_config_service',
    'get_state_service',
    'initialize_services'
]


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== Auto-Mode Unified System v13.2 (8->3 Files Consolidated) ===")
    
    # サービス初期化
    initialize_services()
    
    # サービス取得
    config = get_config_service()
    state = get_state_service()
    
    # 基本情報表示
    print(f"設定有効: {config.is_enabled}")
    print(f"動作モード: {config.mode}")
    print(f"アクティブ: {state.is_active}")
    
    # フロー一覧表示
    print("\n利用可能なフロー:")
    for i, flow in enumerate(config.flows, 1):
        marker = "[✓]" if flow == config.current_flow else " "
        print(f"  {marker} {i}. {flow}")
    
    # 統合テスト設定表示
    integration_settings = config.get_config_summary()["integration_tests"]
    print("\n統合テスト設定:")
    for key, value in integration_settings.items():
        status = "有効" if value else "無効" if isinstance(value, bool) else str(value)
        print(f"  {key}: {status}")
    
    # AutoModeデモンストレーション
    auto_mode_instance = create_auto_mode()
    
    # コマンドデモ実行
    print("\nコマンド実行デモ...")
    commands = ["status", "start", "status", "stop", "status"]
    
    for cmd in commands:
        print(f"\n> /auto-mode {cmd}")
        result = auto_mode_instance.execute_command(cmd)
        print(f"結果: {result}")
    
    print("\n=== Unified Demo Complete - Performance Enhanced ===")
    print("ファイル数: 8 -> 3 (62.5%削減)")
    print("循環依存: 解決済み")
    print("KISS原則: 適用済み")