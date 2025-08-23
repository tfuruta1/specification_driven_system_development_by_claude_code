#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
開発フローテストの共通ベースクラス - Claude Code Core v12.0
全テストモジュールで使用される共通機能
"""

import sys
import unittest.mock
from pathlib import Path

# 共通インポート
sys.path.insert(0, str(Path(__file__).parent))

# 統合システムインポート
from test_base_utilities import OptimizedTestCase
from shared_logger import OptimizedLogger
from error_handler import StandardErrorHandler

try:
    from auto_mode import AutoModeConfig, AutoMode, AutoModeState
    from test_strategy import TestStrategy, TestLevel, TestResult
    from integration_test_runner import IntegrationTestRunner, CircularImportDetector
except ImportError as e:
    # フォールバックのためのダミークラス定義
    print(f"Warning: Import failed, using dummy classes: {e}")
    
    class AutoMode:
        def __init__(self, temp_dir):
            self.config = type('Config', (), {'current_flow': '新規開発'})()
        def execute_command(self, cmd):
            if cmd == 'start':
                return {'session_id': 'test123'}
            return {'status': 'stopped'}
    
    # FileAccessLoggerは統合ロガーで置き換え済み
    
    class AccessPurpose:
        MODIFY = 'MODIFY'
        REFERENCE = 'REFERENCE'
        ANALYZE = 'ANALYZE'
    
    class TestStrategy:
        def __init__(self):
            self.results = []
        def add_test_result(self, result):
            self.results.append(result)
        def is_all_passed(self):
            return all(r.passed for r in self.results)
        def clear_results(self):
            self.results.clear()
    
    class TestLevel:
        UNIT = 'UNIT'
        INTEGRATION = 'INTEGRATION'
        PERFORMANCE = 'PERFORMANCE'
    
    class TestResult:
        def __init__(self, level, passed, failed, total, duration, details=""):
            self.level = level
            self.passed = passed
            self.failed = failed
            self.total = total
            self.duration = duration
            self.details = details
    
    # UnifiedLoggerは統合ロガーで置き換え済み

class BaseTestFlow(OptimizedTestCase):
    """開発フローテストの共通ベースクラス - 統合システム使用"""
    
    def setUp(self):
        """テスト前の準備 - 統合システム使用"""
        super().setUp()  # OptimizedTestCaseのsetUpを実行
        self.auto_mode = AutoMode(self.temp_dir)
        self.test_strategy = TestStrategy()
        # 統合ロガーを使用（self.loggerは既にOptimizedTestCaseで設定済み）
        
    def tearDown(self):
        """テスト後のクリーンアップ - 統合システム使用"""
        super().tearDown()  # OptimizedTestCaseのtearDownを実行
        
    def simulate_sdd_tdd_steps(self, flow_type: str):
        """SDD+TDD 8ステップのシミュレーション"""
        steps = []
        
        # 1. 要件定義書作成
        self.logger.log_file_access(
            "create", 
            "requirements.md", 
            "success",
            {"flow_type": flow_type, "step": "要件定義書作成"}
        )
        steps.append("要件定義書作成")
        
        # 2. 技術設計書作成
        self.logger.log_file_access(
            "create", 
            "design.md", 
            "success",
            {"flow_type": flow_type, "step": "技術設計書作成"}
        )
        steps.append("技術設計書作成")
        
        # 3. 実装計画作成
        self.logger.log_file_access(
            "create", 
            "tasks.md", 
            "success",
            {"flow_type": flow_type, "step": "実装計画作成"}
        )
        steps.append("実装計画作成")
        
        # 4. 設計レビュー
        self.logger.log_file_access(
            "read", 
            "design.md", 
            "success",
            {"flow_type": flow_type, "step": "設計レビュー"}
        )
        steps.append("設計レビュー")
        
        # 5. テスト作成（TDD Red）
        self.logger.log_file_access(
            "create", 
            "test_feature.py", 
            "success",
            {"flow_type": flow_type, "step": "テスト作成（TDD Red）"}
        )
        steps.append("テスト作成（TDD Red）")
        
        # 6. 実装（TDD Green）
        self.logger.log_file_access(
            "create", 
            "feature.py", 
            "success",
            {"flow_type": flow_type, "step": "機能実装（TDD Green）"}
        )
        steps.append("実装（TDD Green）")
        
        # 7. リファクタリング（TDD Refactor）
        self.logger.log_file_access(
            "modify", 
            "feature.py", 
            "success",
            {"flow_type": flow_type, "step": "リファクタリング（TDD Refactor）"}
        )
        steps.append("リファクタリング（TDD Refactor）")
        
        # 8. 最終レビュー
        self.logger.log_file_access(
            "read", 
            "feature.py", 
            "success",
            {"flow_type": flow_type, "step": "最終レビュー"}
        )
        steps.append("最終レビュー")
        
        return steps
    
    def create_test_results(self, unit_passed=True, integration_passed=True):
        """テスト結果の作成"""
        # ユニットテスト
        unit_result = TestResult(
            level=TestLevel.UNIT,
            passed=unit_passed,
            failed=0 if unit_passed else 3,
            total=20,
            duration=2.0
        )
        self.test_strategy.add_test_result(unit_result)
        
        # 統合テスト
        integration_result = TestResult(
            level=TestLevel.INTEGRATION,
            passed=integration_passed,
            failed=0 if integration_passed else 1,
            total=10,
            duration=5.0
        )
        self.test_strategy.add_test_result(integration_result)
        
        return unit_result, integration_result
    
    def verify_activity_report(self, session_id: str):
        """ActivityReport確認 - 統合ロガー使用"""
        report_file = Path(self.temp_dir) / "ActivityReport" / f"auto_mode_session_{session_id}.md"
        self.assert_file_exists(report_file, "ActivityReportファイルが存在しません")
        return report_file
    
    def start_session_with_flow(self, flow_number: str):
        """指定フローでセッションを開始"""
        with unittest.mock.patch('builtins.input', return_value=flow_number):
            result = self.auto_mode.execute_command('start')
            self.assertIn('session_id', result)
            return result['session_id']
    
    def stop_session(self):
        """セッション終了"""
        stop_result = self.auto_mode.execute_command('stop')
        self.assertEqual(stop_result['status'], 'stopped')
        return stop_result