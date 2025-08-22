#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Command System
アレックス・ペアプログラミングモード自動化システム

シンプルで強力な/auto-modeコマンドシステムを提供：
- /auto-mode start - ペアプログラミングモード開始
- /auto-mode stop - ペアプログラミングモード終了  
- /auto-mode status - 現在の状態確認
"""

import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from activity_logger import logger
from jst_utils import format_jst_datetime, get_filename_timestamp
from test_strategy import TestStrategy, TestLevel, TestResult
from integration_test_runner import IntegrationTestRunner, IntegrationTestResult


class AutoModeConfig:
    """Auto-Mode設定管理クラス"""
    
    def __init__(self, config_file: Path = None):
        """
        設定初期化
        
        Args:
            config_file: 設定ファイルパス（Noneの場合はデフォルト）
        """
        self.config_file = config_file or Path(".claude/core/.claude/auto_config.json")
        self.is_enabled = False
        self.mode = "pair_programming"
        self.report_path = ".claude/ActivityReport"
        self.current_flow = None
        self.flows = [
            "新規開発",
            "既存解析", 
            "バグ修正",
            "リファクタリング"
        ]
        # 統合テスト設定
        self.integration_tests_enabled = True
        self.circular_import_detection = True
        self.component_connectivity_test = True
        self.initialization_test = True
        self.integration_test_timeout = 30
        
        # 設定ファイルが存在する場合は読み込み
        if self.config_file.exists():
            self._load()
            
    def _load(self):
        """設定ファイル読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.is_enabled = data.get('is_enabled', False)
            self.mode = data.get('mode', 'pair_programming')
            self.report_path = data.get('report_path', '.claude/ActivityReport')
            self.current_flow = data.get('current_flow')
            self.flows = data.get('flows', self.flows)
            # 統合テスト設定読み込み
            self.integration_tests_enabled = data.get('integration_tests_enabled', True)
            self.circular_import_detection = data.get('circular_import_detection', True)
            self.component_connectivity_test = data.get('component_connectivity_test', True)
            self.initialization_test = data.get('initialization_test', True)
            self.integration_test_timeout = data.get('integration_test_timeout', 30)
            
            # タイムアウト値の検証
            if self.integration_test_timeout <= 0:
                raise ValueError("Integration test timeout must be positive")
            
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}", "AUTO_MODE")
            
    def save(self):
        """設定ファイル保存"""
        try:
            # ディレクトリ作成
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'is_enabled': self.is_enabled,
                'mode': self.mode,
                'report_path': self.report_path,
                'current_flow': self.current_flow,
                'flows': self.flows,
                'integration_tests_enabled': self.integration_tests_enabled,
                'circular_import_detection': self.circular_import_detection,
                'component_connectivity_test': self.component_connectivity_test,
                'initialization_test': self.initialization_test,
                'integration_test_timeout': self.integration_test_timeout,
                'last_updated': format_jst_datetime()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"設定保存エラー: {e}", "AUTO_MODE")


class AutoModeState:
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
        
        return session_id
        
    def stop(self):
        """セッション停止"""
        self.is_active = False
        self.current_session = None
        
    def get_status(self) -> Dict[str, Any]:
        """
        現在の状態取得
        
        Returns:
            状態辞書
        """
        return {
            'active': self.is_active,
            'start_time': self.start_time,
            'session_id': self.current_session,
            'session_count': self.session_count
        }


class AutoMode:
    """Auto-Modeメインクラス"""
    
    def __init__(self, base_dir: str = ".claude"):
        """
        Auto-Mode初期化
        
        Args:
            base_dir: ベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.config = AutoModeConfig(self.base_dir / "core" / ".claude" / "auto_config.json")
        self.state = AutoModeState()
        
        # ActivityReportディレクトリ準備
        self.report_dir = self.base_dir / "ActivityReport"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # テスト戦略と統合テスト実行器初期化
        self.test_strategy = TestStrategy()
        self.integration_runner = IntegrationTestRunner()
        
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
            
        logger.info(f"/auto-mode {command} を実行中...", "AUTO_MODE")
        
        if command == "start":
            return self._start_auto_mode()
        elif command == "stop":
            return self._stop_auto_mode()
        elif command == "status":
            return self._get_status()
        else:
            logger.error(f"不明なコマンド: {command}", "AUTO_MODE")
            logger.info("使用可能なコマンド: start, stop, status", "AUTO_MODE")
            return False
            
    def _start_auto_mode(self) -> bool:
        """Auto-Mode開始"""
        try:
            if self.state.is_active:
                logger.warn("Auto-Mode は既に開始されています", "AUTO_MODE")
                return True
                
            # セッション開始
            session_id = self.state.start()
            
            # 設定更新
            self.config.is_enabled = True
            self.config.current_flow = self._select_flow()
            self.config.save()
            
            # セッション情報作成
            session = self._create_session()
            
            # ActivityReport記録
            self._log_session_start(session)
            
            logger.info(f"Auto-Mode開始完了！ セッションID: {session_id}", "AUTO_MODE")
            logger.info(f"選択フロー: {self.config.current_flow}", "AUTO_MODE")
            logger.info("アレックスとのペアプログラミングモードを開始します", "AUTO_MODE")
            
            return True
            
        except Exception as e:
            logger.error(f"Auto-Mode開始エラー: {e}", "AUTO_MODE")
            return False
            
    def _stop_auto_mode(self) -> bool:
        """Auto-Mode停止"""
        try:
            if not self.state.is_active:
                logger.warn("Auto-Mode は開始されていません", "AUTO_MODE")
                return True
                
            # セッション情報取得
            session_id = self.state.current_session
            
            # セッション停止
            self.state.stop()
            
            # 設定更新
            self.config.is_enabled = False
            self.config.current_flow = None
            self.config.save()
            
            # ActivityReport記録
            self._log_session_end(session_id)
            
            logger.info(f"Auto-Mode停止完了！ セッションID: {session_id}", "AUTO_MODE")
            logger.info("ペアプログラミングセッションが終了しました", "AUTO_MODE")
            
            return True
            
        except Exception as e:
            logger.error(f"Auto-Mode停止エラー: {e}", "AUTO_MODE")
            return False
            
    def _get_status(self) -> Dict[str, Any]:
        """現在の状態取得"""
        status = self.state.get_status()
        status.update({
            'config_enabled': self.config.is_enabled,
            'current_flow': self.config.current_flow,
            'mode': self.config.mode,
            'report_path': str(self.report_dir)
        })
        
        # ステータス表示
        if status['active']:
            logger.info("Auto-Mode: アクティブ", "AUTO_MODE")
            logger.info(f"  セッションID: {status['session_id']}", "AUTO_MODE")
            logger.info(f"  開始時刻: {status['start_time']}", "AUTO_MODE")
            logger.info(f"  現在のフロー: {status['current_flow']}", "AUTO_MODE")
        else:
            logger.info("Auto-Mode: 非アクティブ", "AUTO_MODE")
            logger.info(f"  合計セッション数: {status['session_count']}", "AUTO_MODE")
            
        return status
        
    def _select_flow(self) -> str:
        """
        フロー自動選択
        
        Returns:
            選択されたフロー名
        """
        logger.info("開発フローを選択してください:", "AUTO_MODE")
        for i, flow in enumerate(self.config.flows, 1):
            logger.info(f"  {i}. {flow}", "AUTO_MODE")
            
        # 簡単な選択機構（実際のCLIでは入力受付）
        try:
            choice = input("フロー番号を入力 (1-4): ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(self.config.flows):
                return self.config.flows[index]
            else:
                logger.warn("無効な選択です。デフォルトフローを使用します", "AUTO_MODE")
                return self.config.flows[0]
                
        except (ValueError, EOFError):
            # 自動テスト時やCLI以外の環境での処理
            return self.config.flows[0]
            
    def _create_session(self) -> Dict[str, Any]:
        """
        セッション情報作成
        
        Returns:
            セッション辞書
        """
        return {
            'session_id': self.state.current_session,
            'start_time': self.state.start_time,
            'flow_type': self.config.current_flow,
            'mode': self.config.mode,
            'timestamp': get_filename_timestamp()
        }
        
    def _log_session_start(self, session: Dict[str, Any]):
        """セッション開始ログ記録"""
        log_file = self.report_dir / f"auto_mode_session_{session['session_id']}.md"
        
        content = f"""# Auto-Mode セッションログ
**セッションID**: {session['session_id']}
**開始時刻**: {session['start_time']}
**開発フロー**: {session['flow_type']}
**モード**: {session['mode']}

## セッション概要
アレックスとのペアプログラミングセッションを開始しました。

### 選択フロー: {session['flow_type']}

## 作業ログ
"""
        
        try:
            log_file.write_text(content, encoding='utf-8')
            logger.info(f"セッションログ作成: {log_file.name}", "AUTO_MODE")
        except Exception as e:
            logger.error(f"セッションログ作成エラー: {e}", "AUTO_MODE")
            
    def _log_session_end(self, session_id: str):
        """セッション終了ログ記録"""
        log_file = self.report_dir / f"auto_mode_session_{session_id}.md"
        
        if log_file.exists():
            try:
                content = log_file.read_text(encoding='utf-8')
                end_log = f"""

## セッション終了
**終了時刻**: {format_jst_datetime()}
**ステータス**: 正常終了

ペアプログラミングセッションが完了しました。
"""
                content += end_log
                log_file.write_text(content, encoding='utf-8')
                logger.info(f"セッションログ更新: {log_file.name}", "AUTO_MODE")
            except Exception as e:
                logger.error(f"セッションログ更新エラー: {e}", "AUTO_MODE")
                
    def is_active(self) -> bool:
        """
        アクティブ状態確認
        
        Returns:
            アクティブかどうか
        """
        return self.state.is_active
        
    def _setup_integration_tests(self):
        """統合テスト設定"""
        self.integration_runner.configure(
            circular_import_detection=self.config.circular_import_detection,
            component_connectivity_test=self.config.component_connectivity_test,
            initialization_test=self.config.initialization_test
        )
        
    def get_tdd_workflow_phases(self) -> List[str]:
        """TDDワークフロー段階取得"""
        return [
            'requirements_analysis',
            'unit_test_creation',
            'unit_test_execution',
            'integration_test_execution',  # 新規追加
            'implementation',
            'refactoring',
            'documentation'
        ]
        
    def execute_tdd_workflow(self) -> Dict[str, Any]:
        """TDDワークフロー実行"""
        workflow_result = {
            'success': False,
            'phases_completed': [],
            'current_phase': None,
            'error': None
        }
        
        try:
            phases = self.get_tdd_workflow_phases()
            
            for phase in phases:
                workflow_result['current_phase'] = phase
                
                if phase == 'unit_test_execution':
                    # ユニットテスト実行
                    unit_result = self.execute_unit_test_phase()
                    workflow_result['unit_test_result'] = unit_result
                    
                    if not unit_result.get('success', False):
                        workflow_result['error'] = 'unit_test_failed'
                        return workflow_result
                        
                elif phase == 'integration_test_execution':
                    # 統合テスト実行
                    integration_result = self.execute_integration_test_phase()
                    workflow_result['integration_test_result'] = integration_result
                    
                    if not integration_result.get('success', False):
                        workflow_result['error'] = 'integration_test_failed'
                        # 循環参照情報を結果に含める
                        if 'circular_imports' in integration_result:
                            workflow_result['circular_imports'] = integration_result['circular_imports']
                        return workflow_result
                        
                else:
                    # その他のフェーズ実行
                    phase_result = getattr(self, f'execute_{phase}', lambda: {'success': True})()
                    workflow_result[f'{phase}_result'] = phase_result
                    
                    if not phase_result.get('success', False):
                        workflow_result['error'] = f'{phase}_failed'
                        return workflow_result
                        
                workflow_result['phases_completed'].append(phase)
                
            workflow_result['success'] = True
            return workflow_result
            
        except Exception as e:
            workflow_result['error'] = str(e)
            logger.error(f"TDDワークフロー実行エラー: {e}", "AUTO_MODE")
            return workflow_result
            
    def execute_unit_test_phase(self) -> Dict[str, Any]:
        """ユニットテストフェーズ実行"""
        try:
            # モックランナーを使用（実際の実装では適切なランナーを設定）
            if TestLevel.UNIT in self.test_strategy._runners:
                result = self.test_strategy.execute_single_level(TestLevel.UNIT)
                return {
                    'success': result.passed,
                    'result': result
                }
            else:
                # デフォルト成功結果
                return {'success': True, 'result': None}
                
        except Exception as e:
            logger.error(f"ユニットテスト実行エラー: {e}", "AUTO_MODE")
            return {'success': False, 'error': str(e)}
            
    def execute_integration_test_phase(self) -> Dict[str, Any]:
        """統合テストフェーズ実行"""
        try:
            if not self.config.integration_tests_enabled:
                return {'success': True, 'skipped': True}
                
            result = self.integration_runner.run()
            
            return {
                'success': result.passed,
                'result': result,
                'circular_imports': result.circular_imports,
                'connectivity_issues': result.connectivity_issues,
                'initialization_errors': result.initialization_errors
            }
            
        except Exception as e:
            logger.error(f"統合テスト実行エラー: {e}", "AUTO_MODE")
            return {'success': False, 'error': str(e)}
            
    def execute_integration_test_with_retry(self, max_retries: int = 1) -> Dict[str, Any]:
        """リトライ付き統合テスト実行"""
        retry_count = 0
        
        while retry_count <= max_retries:
            result = self.execute_integration_test_phase()
            
            if result['success']:
                result['retry_count'] = retry_count
                return result
                
            retry_count += 1
            if retry_count <= max_retries:
                logger.info(f"統合テストリトライ {retry_count}/{max_retries}", "AUTO_MODE")
                time.sleep(1)  # リトライ前の待機
                
        result['retry_count'] = retry_count - 1
        return result
        
    def configure_integration_tests(self, circular_import_detection: bool = None,
                                   component_connectivity_test: bool = None,
                                   initialization_test: bool = None):
        """統合テスト設定変更"""
        if circular_import_detection is not None:
            self.config.circular_import_detection = circular_import_detection
            
        if component_connectivity_test is not None:
            self.config.component_connectivity_test = component_connectivity_test
            
        if initialization_test is not None:
            self.config.initialization_test = initialization_test
            
        # 設定を統合テスト実行器に反映
        self._setup_integration_tests()
        
        # 設定保存
        self.config.save()
        
    def is_integration_tests_enabled(self) -> bool:
        """統合テスト有効性確認"""
        return self.config.integration_tests_enabled
        
    def generate_integration_test_report(self, result: IntegrationTestResult) -> str:
        """統合テストレポート生成"""
        return result.get_summary()
        
    def track_integration_test_in_session(self, session_id: str, result: IntegrationTestResult):
        """セッション中の統合テスト結果追跡"""
        if session_id not in self.state.session_data:
            self.state.session_data[session_id] = {'integration_test_results': []}
            
        result_data = {
            'passed': result.passed,
            'failed': result.failed,
            'total': result.total,
            'duration': result.duration,
            'details': result.details,
            'circular_imports': result.circular_imports,
            'connectivity_issues': result.connectivity_issues,
            'initialization_errors': result.initialization_errors,
            'timestamp': result.timestamp.isoformat() if result.timestamp else None
        }
        
        self.state.session_data[session_id]['integration_test_results'].append(result_data)
        
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """セッション情報取得"""
        return self.state.session_data.get(session_id, {})
        
    # プレースホルダー実装（実際のフェーズ実行メソッド）
    def execute_requirements_analysis(self) -> Dict[str, Any]:
        """要件分析フェーズ"""
        return {'success': True}
        
    def execute_unit_test_creation(self) -> Dict[str, Any]:
        """ユニットテスト作成フェーズ"""
        return {'success': True}
        
    def execute_implementation(self) -> Dict[str, Any]:
        """実装フェーズ"""
        return {'success': True}
        
    def execute_refactoring(self) -> Dict[str, Any]:
        """リファクタリングフェーズ"""
        return {'success': True}
        
    def execute_documentation(self) -> Dict[str, Any]:
        """ドキュメント作成フェーズ"""
        return {'success': True}


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


if __name__ == "__main__":
    # デモ実行
    auto_mode = AutoMode()
    
    print("=== Auto-Mode Demo ===")
    print("Status:", auto_mode.execute_command("status"))
    print("Start:", auto_mode.execute_command("start"))
    print("Status:", auto_mode.execute_command("status"))
    print("Stop:", auto_mode.execute_command("stop"))
    print("Final Status:", auto_mode.execute_command("status"))