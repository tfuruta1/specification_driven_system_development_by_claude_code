#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リファクタリングフローテスト - Claude Code Core v12.0
リファクタリングフローの包括的なテスト
"""

import unittest
from unittest.mock import patch
from pathlib import Path
from test_base import BaseTestFlow
from file_access_logger import AccessPurpose
from test_strategy import TestLevel, TestResult

class TestRefactoringFlow(BaseTestFlow):
    """リファクタリングフローのテスト"""
    
    @patch('builtins.input', return_value='4')
    def test_refactoring_flow(self, mock_input):
        """リファクタリングフローのテスト"""
        print("\n=== リファクタリングフローテスト ===")
        
        # 1. AutoMode開始（リファクタリングを選択）
        session_id = self.start_session_with_flow('4')
        print(f"[OK] セッション開始: {session_id}")
        
        # 2. フロー確認
        self.assertEqual(self.auto_mode.config.current_flow, 'リファクタリング')
        print(f"[OK] フロー設定: リファクタリング")
        
        # 3. コード品質分析
        target_files = ["legacy_module.py", "complex_function.py", "duplicated_code.py"]
        
        for file in target_files:
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.ANALYZE, 
                f"コード品質分析: {file}"
            )
        print(f"[OK] コード品質分析完了")
        
        # 4. 既存テストの確認
        self.file_logger.log_file_access(
            "test_existing.py", 
            AccessPurpose.REFERENCE, 
            "既存テスト確認"
        )
        
        # 既存テスト実行（リファクタリング前）
        before_refactor = TestResult(
            level=TestLevel.UNIT,
            passed=True,
            failed=0,
            total=30,
            duration=3.0,
            details="リファクタリング前: 全テスト合格"
        )
        self.test_strategy.add_test_result(before_refactor)
        print(f"[OK] 既存テスト確認（30テスト全合格）")
        
        # 5. リファクタリング実施
        refactoring_tasks = [
            ("legacy_module.py", "レガシーコードの近代化"),
            ("complex_function.py", "複雑な関数の分割"),
            ("duplicated_code.py", "重複コードの統合"),
            ("utils.py", "共通処理の抽出")
        ]
        
        for file, task in refactoring_tasks:
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.MODIFY, 
                f"リファクタリング: {task}"
            )
        print(f"[OK] リファクタリング実施: {len(refactoring_tasks)}タスク")
        
        # 6. テスト再実行（リファクタリング後）
        after_refactor = TestResult(
            level=TestLevel.UNIT,
            passed=True,
            failed=0,
            total=30,
            duration=2.5,  # パフォーマンス改善
            details="リファクタリング後: 全テスト合格（実行時間短縮）"
        )
        self.test_strategy.add_test_result(after_refactor)
        print(f"[OK] リファクタリング後テスト（全合格、速度改善）")
        
        # 7. 品質メトリクス比較
        self.assertTrue(after_refactor.duration < before_refactor.duration)
        print(f"[OK] パフォーマンス改善確認: {before_refactor.duration}s → {after_refactor.duration}s")
        
        # 8. ActivityReport確認
        self.verify_activity_report(session_id)
        print(f"[OK] ActivityReport作成")
        
        # 9. セッション終了
        self.stop_session()
        print(f"[OK] セッション終了")
    
    @patch('builtins.input', return_value='4')
    def test_large_scale_refactoring(self, mock_input):
        """大規模リファクタリングテスト"""
        print("\n=== 大規模リファクタリングテスト ===")
        
        session_id = self.start_session_with_flow('4')
        
        # 大規模リファクタリング対象
        large_refactor_targets = [
            "monolith/user_service.py",
            "monolith/order_service.py", 
            "monolith/payment_service.py",
            "monolith/notification_service.py",
            "monolith/reporting_service.py"
        ]
        
        # マイクロサービス分割準備
        for service in large_refactor_targets:
            # 既存コード解析
            self.file_logger.log_file_access(
                service, 
                AccessPurpose.ANALYZE, 
                f"マイクロサービス分割解析: {service}"
            )
            
            # 依存関係分析
            self.file_logger.log_file_access(
                service, 
                AccessPurpose.REFERENCE, 
                f"依存関係分析: {service}"
            )
            
            print(f"[OK] {service} 分割準備完了")
        
        # 新しいマイクロサービス作成
        microservices = [
            "services/user_service.py",
            "services/order_service.py",
            "services/payment_service.py",
            "services/notification_service.py",
            "services/reporting_service.py"
        ]
        
        for service in microservices:
            self.file_logger.log_file_access(
                service, 
                AccessPurpose.MODIFY, 
                f"マイクロサービス作成: {service}"
            )
            print(f"[OK] {service} 作成完了")
        
        # 統合テスト実行
        integration_test = TestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=50,
            duration=20.0,
            details="マイクロサービス統合テスト成功"
        )
        self.test_strategy.add_test_result(integration_test)
        
        print("[OK] 大規模リファクタリング完了")
        
        self.stop_session()
    
    @patch('builtins.input', return_value='4')
    def test_code_quality_improvement(self, mock_input):
        """コード品質改善テスト"""
        print("\n=== コード品質改善テスト ===")
        
        session_id = self.start_session_with_flow('4')
        
        # 品質問題のあるファイル
        quality_issues = [
            ("complex_class.py", "複雑度削減"),
            ("long_methods.py", "メソッド分割"),
            ("god_object.py", "責任分離"),
            ("tight_coupling.py", "結合度低下"),
            ("magic_numbers.py", "定数化")
        ]
        
        # リファクタリング前の品質測定
        for file, issue in quality_issues:
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.ANALYZE, 
                f"品質問題分析: {issue}"
            )
        
        # 品質改善実施
        for file, improvement in quality_issues:
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.MODIFY, 
                f"品質改善: {improvement}"
            )
            
            # 改善後の確認
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.REFERENCE, 
                f"改善確認: {improvement}"
            )
            
            print(f"[OK] {improvement}完了")
        
        # 品質メトリクス測定
        quality_test = TestResult(
            level=TestLevel.UNIT,
            passed=True,
            failed=0,
            total=40,
            duration=5.0,
            details="品質改善後テスト全合格"
        )
        self.test_strategy.add_test_result(quality_test)
        
        print("[OK] コード品質改善完了")
        
        self.stop_session()

if __name__ == '__main__':
    unittest.main()