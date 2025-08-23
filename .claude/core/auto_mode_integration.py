#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Integration Controller
統合テスト制御専用モジュール - 単一責任原則に基づく分離
"""

import time
from typing import Dict, Any, Optional

from .integration_test_runner import IntegrationTestRunner, IntegrationTestResult
from .shared_logger import OptimizedLogger
from .error_handler import StandardErrorHandler


class IntegrationController:
    """
    統合テスト制御クラス
    
    統合テストの実行、リトライ、結果管理を担当。
    KISS原則に基づいた効率的なテスト制御。
    """
    
    def __init__(self, integration_runner: IntegrationTestRunner, 
                 logger: OptimizedLogger, error_handler: StandardErrorHandler):
        """
        IntegrationController初期化
        
        Args:
            integration_runner: 統合テスト実行器
            logger: 統合ロガー
            error_handler: エラーハンドラー
        """
        self.integration_runner = integration_runner
        self.logger = logger
        self.error_handler = error_handler
        
        # 統合テストセッション結果ストレージ
        self.session_results: Dict[str, list] = {}
    
    def setup_integration_tests(self, circular_import_detection: bool = True,
                               component_connectivity_test: bool = True,
                               initialization_test: bool = True):
        """
        統合テスト設定
        
        Args:
            circular_import_detection: 循環インポート検出有効化
            component_connectivity_test: コンポーネント接続テスト有効化
            initialization_test: 初期化テスト有効化
        """
        try:
            self.integration_runner.configure(
                circular_import_detection=circular_import_detection,
                component_connectivity_test=component_connectivity_test,
                initialization_test=initialization_test
            )
            
            self.logger.log_with_context(
                "info", "統合テスト設定完了",
                {
                    "circular_import_detection": circular_import_detection,
                    "component_connectivity_test": component_connectivity_test,
                    "initialization_test": initialization_test
                }
            )
            
        except Exception as e:
            self.error_handler.handle_configuration_error("integration_test_setup", e)
    
    def execute_integration_test_phase(self, integration_tests_enabled: bool = True) -> Dict[str, Any]:
        """
        統合テストフェーズ実行
        
        Args:
            integration_tests_enabled: 統合テスト有効フラグ
            
        Returns:
            統合テスト実行結果
        """
        try:
            if not integration_tests_enabled:
                return {
                    'success': True, 
                    'skipped': True,
                    'reason': 'Integration tests disabled'
                }
            
            # 統合テスト実行
            self.logger.log_with_context("info", "統合テスト実行開始")
            start_time = time.time()
            
            result = self.integration_runner.run()
            
            execution_time = time.time() - start_time
            
            # 結果構築
            test_result = {
                'success': result.passed,
                'result': result,
                'execution_time': execution_time,
                'circular_imports': result.circular_imports,
                'connectivity_issues': result.connectivity_issues,
                'initialization_errors': result.initialization_errors,
                'test_details': {
                    'passed': result.passed,
                    'failed': result.failed,
                    'total': result.total,
                    'duration': result.duration
                }
            }
            
            # ログ記録
            if result.passed:
                self.logger.log_with_context(
                    "info", "統合テスト実行成功",
                    {"execution_time": execution_time, "total_tests": result.total}
                )
            else:
                self.logger.log_with_context(
                    "error", "統合テスト実行失敗",
                    {
                        "execution_time": execution_time,
                        "failed_tests": result.failed,
                        "circular_imports": len(result.circular_imports),
                        "connectivity_issues": len(result.connectivity_issues)
                    }
                )
            
            return test_result
            
        except Exception as e:
            self.error_handler.handle_test_execution_error("integration_test", e)
            return {
                'success': False, 
                'error': str(e),
                'execution_time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    def execute_integration_test_with_retry(self, max_retries: int = 1, 
                                          integration_tests_enabled: bool = True) -> Dict[str, Any]:
        """
        リトライ付き統合テスト実行
        
        Args:
            max_retries: 最大リトライ回数
            integration_tests_enabled: 統合テスト有効フラグ
            
        Returns:
            統合テスト実行結果
        """
        retry_count = 0
        all_attempts = []
        
        while retry_count <= max_retries:
            self.logger.log_with_context(
                "info", f"統合テスト実行試行 {retry_count + 1}/{max_retries + 1}"
            )
            
            result = self.execute_integration_test_phase(integration_tests_enabled)
            all_attempts.append(result)
            
            if result['success']:
                result['retry_count'] = retry_count
                result['total_attempts'] = retry_count + 1
                result['all_attempts'] = all_attempts
                
                self.logger.log_with_context(
                    "info", f"統合テスト成功 (試行回数: {retry_count + 1})",
                    {"retry_count": retry_count}
                )
                return result
            
            retry_count += 1
            
            if retry_count <= max_retries:
                self.logger.log_with_context(
                    "info", f"統合テストリトライ {retry_count}/{max_retries}",
                    {"retry_count": retry_count, "max_retries": max_retries}
                )
                time.sleep(1)  # リトライ前の待機
        
        # 全試行失敗
        result['retry_count'] = retry_count - 1
        result['total_attempts'] = retry_count
        result['all_attempts'] = all_attempts
        result['final_failure'] = True
        
        self.logger.log_with_context(
            "error", f"統合テスト最終失敗 (全{retry_count}回試行)",
            {"total_attempts": retry_count}
        )
        
        return result
    
    def configure_integration_tests(self, circular_import_detection: Optional[bool] = None,
                                   component_connectivity_test: Optional[bool] = None,
                                   initialization_test: Optional[bool] = None):
        """
        統合テスト設定変更
        
        Args:
            circular_import_detection: 循環インポート検出設定
            component_connectivity_test: コンポーネント接続テスト設定
            initialization_test: 初期化テスト設定
        """
        kwargs = {}
        
        if circular_import_detection is not None:
            kwargs['circular_import_detection'] = circular_import_detection
        if component_connectivity_test is not None:
            kwargs['component_connectivity_test'] = component_connectivity_test
        if initialization_test is not None:
            kwargs['initialization_test'] = initialization_test
        
        if kwargs:
            try:
                self.integration_runner.configure(**kwargs)
                self.logger.log_with_context(
                    "info", "統合テスト設定更新", kwargs
                )
            except Exception as e:
                self.error_handler.handle_configuration_error("integration_test_config_update", e)
    
    def generate_integration_test_report(self, result: IntegrationTestResult) -> str:
        """
        統合テストレポート生成
        
        Args:
            result: 統合テスト結果
            
        Returns:
            レポート文字列
        """
        try:
            return result.get_summary()
        except Exception as e:
            self.error_handler.handle_report_generation_error("integration_test_report", e)
            return f"レポート生成エラー: {str(e)}"
    
    def track_integration_test_in_session(self, session_id: str, 
                                         result: IntegrationTestResult):
        """
        セッション中の統合テスト結果追跡
        
        Args:
            session_id: セッションID
            result: 統合テスト結果
        """
        try:
            if session_id not in self.session_results:
                self.session_results[session_id] = []
            
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
            
            self.session_results[session_id].append(result_data)
            
            self.logger.log_with_context(
                "info", "セッション統合テスト結果記録",
                {"session_id": session_id, "result_count": len(self.session_results[session_id])}
            )
            
        except Exception as e:
            self.error_handler.handle_data_tracking_error("integration_test_session_tracking", e)
    
    def get_session_integration_results(self, session_id: str) -> list:
        """
        セッション統合テスト結果取得
        
        Args:
            session_id: セッションID
            
        Returns:
            統合テスト結果リスト
        """
        return self.session_results.get(session_id, [])
    
    def clear_session_results(self, session_id: str):
        """
        セッション結果クリア
        
        Args:
            session_id: セッションID
        """
        if session_id in self.session_results:
            del self.session_results[session_id]
            self.logger.log_with_context(
                "info", "セッション統合テスト結果クリア",
                {"session_id": session_id}
            )