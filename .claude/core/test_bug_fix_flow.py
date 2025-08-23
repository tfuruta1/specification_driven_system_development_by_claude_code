#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
バグ修正フローテスト - Claude Code Core v12.0
バグ修正フローの包括的なテスト
"""

import unittest
from unittest.mock import patch
from pathlib import Path
from test_base import BaseTestFlow
from file_access_logger import AccessPurpose
from test_strategy import TestLevel, TestResult

class TestBugFixFlow(BaseTestFlow):
    """バグ修正フローのテスト"""
    
    @patch('builtins.input', return_value='3')
    def test_bug_fix_flow(self, mock_input):
        """バグ修正フローのテスト"""
        print("\n=== バグ修正フローテスト ===")
        
        # 1. AutoMode開始（バグ修正を選択）
        session_id = self.start_session_with_flow('3')
        print(f"[OK] セッション開始: {session_id}")
        
        # 2. フロー確認
        self.assertEqual(self.auto_mode.config.current_flow, 'バグ修正')
        print(f"[OK] フロー設定: バグ修正")
        
        # 3. バグ特定フェーズ
        # 問題のあるファイルを解析
        self.file_logger.log_file_access(
            "buggy_module.py", 
            AccessPurpose.ANALYZE, 
            "バグ箇所特定"
        )
        self.file_logger.log_file_access(
            "error_log.txt", 
            AccessPurpose.REFERENCE, 
            "エラーログ確認"
        )
        print(f"[OK] バグ箇所特定完了")
        
        # 4. テスト作成（バグ再現）
        self.file_logger.log_file_access(
            "test_bugfix.py", 
            AccessPurpose.MODIFY, 
            "バグ再現テスト作成"
        )
        
        # 失敗するテスト（TDD Red）
        failing_test = TestResult(
            level=TestLevel.UNIT,
            passed=False,
            failed=1,
            total=1,
            duration=0.5,
            details="バグ再現テスト失敗（期待通り）"
        )
        self.test_strategy.add_test_result(failing_test)
        print(f"[OK] バグ再現テスト作成（失敗）")
        
        # 5. バグ修正
        self.file_logger.log_file_access(
            "buggy_module.py", 
            AccessPurpose.MODIFY, 
            "バグ修正実装"
        )
        
        # 関連ファイルの確認
        self.file_logger.log_file_access(
            "related_module.py", 
            AccessPurpose.REFERENCE, 
            "影響範囲確認"
        )
        print(f"[OK] バグ修正実装")
        
        # 6. テスト再実行（成功）
        self.test_strategy.clear_results()  # 前のテスト結果をクリア
        
        passing_test = TestResult(
            level=TestLevel.UNIT,
            passed=True,
            failed=0,
            total=1,
            duration=0.5,
            details="バグ修正テスト成功"
        )
        self.test_strategy.add_test_result(passing_test)
        
        # 回帰テスト
        regression_test = TestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=15,
            duration=3.0,
            details="回帰テスト成功"
        )
        self.test_strategy.add_test_result(regression_test)
        
        self.assertTrue(self.test_strategy.is_all_passed())
        print(f"[OK] バグ修正・テスト成功")
        
        # 7. ActivityReport確認
        self.verify_activity_report(session_id)
        print(f"[OK] ActivityReport作成")
        
        # 8. セッション終了
        self.stop_session()
        print(f"[OK] セッション終了")
    
    @patch('builtins.input', return_value='3')
    def test_critical_bug_fix(self, mock_input):
        """クリティカルバグ修正テスト"""
        print("\n=== クリティカルバグ修正テスト ===")
        
        session_id = self.start_session_with_flow('3')
        
        # クリティカルバグの特定
        critical_files = [
            "security_module.py",
            "authentication.py",
            "payment_processor.py",
            "data_validator.py"
        ]
        
        for file in critical_files:
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.ANALYZE, 
                f"クリティカルバグ解析: {file}"
            )
            print(f"[OK] {file} 解析完了")
        
        # 緊急修正テスト作成
        self.file_logger.log_file_access(
            "test_critical_security.py", 
            AccessPurpose.MODIFY, 
            "セキュリティバグ再現テスト"
        )
        
        # セキュリティバグ修正
        self.file_logger.log_file_access(
            "security_module.py", 
            AccessPurpose.MODIFY, 
            "セキュリティバグ修正"
        )
        
        # 影響範囲の確認
        related_files = [
            "user_controller.py",
            "admin_panel.py",
            "api_endpoints.py"
        ]
        
        for file in related_files:
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.REFERENCE, 
                f"影響範囲確認: {file}"
            )
        
        # 包括的テスト実行
        security_test = TestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=25,
            duration=10.0,
            details="セキュリティテスト完全合格"
        )
        self.test_strategy.add_test_result(security_test)
        
        print("[OK] クリティカルバグ修正完了")
        
        self.stop_session()
    
    @patch('builtins.input', return_value='3')
    def test_performance_bug_fix(self, mock_input):
        """パフォーマンスバグ修正テスト"""
        print("\n=== パフォーマンスバグ修正テスト ===")
        
        session_id = self.start_session_with_flow('3')
        
        # パフォーマンス問題のあるファイル解析
        performance_files = [
            "slow_query_module.py",
            "memory_leak_handler.py",
            "inefficient_algorithm.py"
        ]
        
        for file in performance_files:
            # パフォーマンス解析
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.ANALYZE, 
                f"パフォーマンス解析: {file}"
            )
            
            # プロファイリング実行
            self.file_logger.log_file_access(
                f"profile_{file}.txt", 
                AccessPurpose.REFERENCE, 
                f"プロファイリング結果確認"
            )
        
        print(f"[OK] パフォーマンス問題解析完了")
        
        # 最適化実装
        optimizations = [
            ("slow_query_module.py", "クエリ最適化"),
            ("memory_leak_handler.py", "メモリリーク修正"),
            ("inefficient_algorithm.py", "アルゴリズム改善")
        ]
        
        for file, description in optimizations:
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.MODIFY, 
                description
            )
            print(f"[OK] {description}完了")
        
        # パフォーマンステスト実行
        perf_test = TestResult(
            level=TestLevel.PERFORMANCE,
            passed=True,
            failed=0,
            total=10,
            duration=15.0,
            details="パフォーマンス改善確認"
        )
        self.test_strategy.add_test_result(perf_test)
        
        print("[OK] パフォーマンス修正完了")
        
        self.stop_session()

if __name__ == '__main__':
    unittest.main()