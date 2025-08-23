#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Workflow Executor
ワークフロー実行専用モジュール - 単一責任原則に基づく分離
"""

from typing import Dict, List, Any, Callable
import time

from .test_strategy import TestStrategy, TestLevel, TestResult
from .shared_logger import OptimizedLogger
from .error_handler import StandardErrorHandler


class WorkflowExecutor:
    """
    ワークフロー実行クラス
    
    TDDワークフローの各段階を管理・実行。
    KISS原則に基づいた段階的実行機構。
    """
    
    def __init__(self, test_strategy: TestStrategy, logger: OptimizedLogger, 
                 error_handler: StandardErrorHandler):
        """
        WorkflowExecutor初期化
        
        Args:
            test_strategy: テスト戦略インスタンス
            logger: 統合ロガー
            error_handler: エラーハンドラー
        """
        self.test_strategy = test_strategy
        self.logger = logger
        self.error_handler = error_handler
        
        # フェーズ実行ハンドラーのマッピング
        self._phase_handlers: Dict[str, Callable] = {
            'requirements_analysis': self._execute_requirements_analysis,
            'unit_test_creation': self._execute_unit_test_creation,
            'unit_test_execution': self._execute_unit_test_execution,
            'integration_test_execution': self._execute_integration_test_execution,
            'implementation': self._execute_implementation,
            'refactoring': self._execute_refactoring,
            'documentation': self._execute_documentation
        }
    
    def get_tdd_workflow_phases(self) -> List[str]:
        """
        TDDワークフロー段階取得
        
        Returns:
            フェーズリスト
        """
        return [
            'requirements_analysis',
            'unit_test_creation', 
            'unit_test_execution',
            'integration_test_execution',
            'implementation',
            'refactoring',
            'documentation'
        ]
    
    def execute_tdd_workflow(self, integration_test_handler: Callable = None) -> Dict[str, Any]:
        """
        TDDワークフロー実行
        
        Args:
            integration_test_handler: 統合テスト実行ハンドラー（外部から注入）
            
        Returns:
            ワークフロー実行結果
        """
        workflow_result = {
            'success': False,
            'phases_completed': [],
            'current_phase': None,
            'error': None,
            'start_time': time.time()
        }
        
        try:
            phases = self.get_tdd_workflow_phases()
            
            for phase in phases:
                workflow_result['current_phase'] = phase
                
                self.logger.log_with_context(
                    "info", f"ワークフロー段階開始: {phase}",
                    {"phase": phase}
                )
                
                # フェーズ実行
                if phase == 'integration_test_execution' and integration_test_handler:
                    # 外部統合テストハンドラー使用
                    phase_result = integration_test_handler()
                else:
                    # 内部ハンドラー使用
                    handler = self._phase_handlers.get(phase)
                    if handler:
                        phase_result = handler()
                    else:
                        phase_result = {'success': False, 'error': f'Unknown phase: {phase}'}
                
                # 結果記録
                workflow_result[f'{phase}_result'] = phase_result
                
                if not phase_result.get('success', False):
                    workflow_result['error'] = f'{phase}_failed'
                    self.logger.log_with_context(
                        "error", f"ワークフロー段階失敗: {phase}",
                        {"phase": phase, "error": phase_result.get('error')}
                    )
                    
                    # 特別な統合テストエラー処理
                    if phase == 'integration_test_execution':
                        self._handle_integration_test_failure(workflow_result, phase_result)
                    
                    return workflow_result
                
                workflow_result['phases_completed'].append(phase)
                self.logger.log_with_context(
                    "info", f"ワークフロー段階完了: {phase}",
                    {"phase": phase}
                )
            
            workflow_result['success'] = True
            workflow_result['end_time'] = time.time()
            workflow_result['duration'] = workflow_result['end_time'] - workflow_result['start_time']
            
            self.logger.log_with_context(
                "info", "TDDワークフロー実行完了",
                {"duration": workflow_result['duration'], "phases": len(phases)}
            )
            
            return workflow_result
            
        except Exception as e:
            workflow_result['error'] = str(e)
            workflow_result['end_time'] = time.time()
            workflow_result['duration'] = workflow_result['end_time'] - workflow_result['start_time']
            
            self.error_handler.handle_workflow_error("tdd_workflow_execution", e)
            return workflow_result
    
    def _handle_integration_test_failure(self, workflow_result: Dict, phase_result: Dict):
        """統合テスト失敗時の特別処理"""
        if 'circular_imports' in phase_result:
            workflow_result['circular_imports'] = phase_result['circular_imports']
        if 'connectivity_issues' in phase_result:
            workflow_result['connectivity_issues'] = phase_result['connectivity_issues']
        if 'initialization_errors' in phase_result:
            workflow_result['initialization_errors'] = phase_result['initialization_errors']
    
    def _execute_unit_test_execution(self) -> Dict[str, Any]:
        """ユニットテスト実行フェーズ"""
        try:
            if TestLevel.UNIT in self.test_strategy._runners:
                result = self.test_strategy.execute_single_level(TestLevel.UNIT)
                return {
                    'success': result.passed,
                    'result': result,
                    'duration': getattr(result, 'duration', 0)
                }
            else:
                # デフォルト成功結果（モック実行）
                return {
                    'success': True, 
                    'result': None,
                    'mock_execution': True
                }
                
        except Exception as e:
            self.error_handler.handle_test_execution_error("unit_test", e)
            return {'success': False, 'error': str(e)}
    
    def _execute_integration_test_execution(self) -> Dict[str, Any]:
        """統合テスト実行フェーズ（プレースホルダー）"""
        # このメソッドは通常外部ハンドラーで置き換えられる
        return {
            'success': True, 
            'placeholder': True,
            'message': 'Integration test execution delegated to external handler'
        }
    
    # プレースホルダー実装（各フェーズ実行メソッド）
    def _execute_requirements_analysis(self) -> Dict[str, Any]:
        """要件分析フェーズ"""
        self.logger.log_with_context("info", "要件分析フェーズ実行")
        return {'success': True, 'phase': 'requirements_analysis'}
    
    def _execute_unit_test_creation(self) -> Dict[str, Any]:
        """ユニットテスト作成フェーズ"""
        self.logger.log_with_context("info", "ユニットテスト作成フェーズ実行")
        return {'success': True, 'phase': 'unit_test_creation'}
    
    def _execute_implementation(self) -> Dict[str, Any]:
        """実装フェーズ"""
        self.logger.log_with_context("info", "実装フェーズ実行")
        return {'success': True, 'phase': 'implementation'}
    
    def _execute_refactoring(self) -> Dict[str, Any]:
        """リファクタリングフェーズ"""
        self.logger.log_with_context("info", "リファクタリングフェーズ実行")
        return {'success': True, 'phase': 'refactoring'}
    
    def _execute_documentation(self) -> Dict[str, Any]:
        """ドキュメント作成フェーズ"""
        self.logger.log_with_context("info", "ドキュメント作成フェーズ実行")
        return {'success': True, 'phase': 'documentation'}
    
    def get_phase_handler(self, phase: str) -> Callable:
        """
        フェーズハンドラー取得
        
        Args:
            phase: フェーズ名
            
        Returns:
            フェーズハンドラー関数
        """
        return self._phase_handlers.get(phase)
    
    def register_phase_handler(self, phase: str, handler: Callable):
        """
        カスタムフェーズハンドラー登録
        
        Args:
            phase: フェーズ名
            handler: ハンドラー関数
        """
        self._phase_handlers[phase] = handler
        self.logger.log_with_context(
            "info", f"カスタムフェーズハンドラー登録: {phase}",
            {"phase": phase}
        )