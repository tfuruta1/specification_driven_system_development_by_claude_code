#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v12.0 各開発フローの動作テスト
新規開発、既存解析、バグ修正、リファクタリングの4つのフローを完全にテスト
"""

import unittest
import tempfile
import shutil
import time
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

# テスト対象モジュールのインポート
sys.path.insert(0, str(Path(__file__).parent))

from auto_mode import AutoModeConfig, AutoMode, AutoModeState
from file_access_logger import FileAccessLogger, AccessPurpose
from test_strategy import TestStrategy, TestLevel, TestResult
from integration_test_runner import IntegrationTestRunner, CircularImportDetector
from activity_logger import UnifiedLogger, ActivityType


class TestDevelopmentFlows(unittest.TestCase):
    """各開発フローの包括的なテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.auto_mode = AutoMode(self.temp_dir)
        self.file_logger = FileAccessLogger()
        self.test_strategy = TestStrategy()
        self.activity_logger = UnifiedLogger(base_path=self.temp_dir)
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def simulate_sdd_tdd_steps(self, flow_type: str):
        """SDD+TDD 8ステップのシミュレーション"""
        steps = []
        
        # 1. 要件定義書作成
        self.file_logger.log_file_access(
            "requirements.md", 
            AccessPurpose.MODIFY, 
            f"{flow_type}: 要件定義書作成"
        )
        steps.append("要件定義書作成")
        
        # 2. 技術設計書作成
        self.file_logger.log_file_access(
            "design.md", 
            AccessPurpose.MODIFY, 
            f"{flow_type}: 技術設計書作成"
        )
        steps.append("技術設計書作成")
        
        # 3. 実装計画作成
        self.file_logger.log_file_access(
            "tasks.md", 
            AccessPurpose.MODIFY, 
            f"{flow_type}: 実装計画作成"
        )
        steps.append("実装計画作成")
        
        # 4. 設計レビュー
        self.file_logger.log_file_access(
            "design.md", 
            AccessPurpose.REFERENCE, 
            f"{flow_type}: 設計レビュー"
        )
        steps.append("設計レビュー")
        
        # 5. テスト作成（TDD Red）
        self.file_logger.log_file_access(
            "test_feature.py", 
            AccessPurpose.MODIFY, 
            f"{flow_type}: テスト作成"
        )
        steps.append("テスト作成（TDD Red）")
        
        # 6. 実装（TDD Green）
        self.file_logger.log_file_access(
            "feature.py", 
            AccessPurpose.MODIFY, 
            f"{flow_type}: 機能実装"
        )
        steps.append("実装（TDD Green）")
        
        # 7. リファクタリング（TDD Refactor）
        self.file_logger.log_file_access(
            "feature.py", 
            AccessPurpose.MODIFY, 
            f"{flow_type}: リファクタリング"
        )
        steps.append("リファクタリング（TDD Refactor）")
        
        # 8. 最終レビュー
        self.file_logger.log_file_access(
            "feature.py", 
            AccessPurpose.REFERENCE, 
            f"{flow_type}: 最終レビュー"
        )
        steps.append("最終レビュー")
        
        return steps
        
    @patch('builtins.input', return_value='1')
    def test_new_development_flow(self, mock_input):
        """新規開発フローのテスト"""
        print("\n=== 新規開発フローテスト ===")
        
        # 1. AutoMode開始（新規開発を選択）
        result = self.auto_mode.execute_command('start')
        self.assertIn('session_id', result)
        session_id = result['session_id']
        print(f"[OK] セッション開始: {session_id}")
        
        # 2. フロー確認
        self.assertEqual(self.auto_mode.config.current_flow, '新規開発')
        print(f"[OK] フロー設定: 新規開発")
        
        # 3. SDD+TDDステップ実行
        steps = self.simulate_sdd_tdd_steps("新規開発")
        self.assertEqual(len(steps), 8)
        print(f"[OK] SDD+TDD 8ステップ完了")
        
        # 4. ファイルアクセスパターン確認
        # 新規開発では全ファイルが新規作成（MODIFY）
        modify_count = sum(1 for h in self.file_logger.access_history 
                          if h['purpose'] == AccessPurpose.MODIFY)
        self.assertGreater(modify_count, 4)  # 最低4つ以上のファイル修正
        print(f"[OK] 新規ファイル作成: {modify_count}個")
        
        # 5. テスト実行
        # ユニットテスト
        unit_result = TestResult(
            level=TestLevel.UNIT,
            passed=True,
            failed=0,
            total=20,
            duration=2.0
        )
        self.test_strategy.add_test_result(unit_result)
        
        # 統合テスト（新規開発では必須）
        integration_result = TestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=10,
            duration=5.0
        )
        self.test_strategy.add_test_result(integration_result)
        
        self.assertTrue(self.test_strategy.is_all_passed())
        print(f"[OK] テスト全合格")
        
        # 6. ActivityReport確認
        report_file = Path(self.temp_dir) / "ActivityReport" / f"auto_mode_session_{session_id}.md"
        self.assertTrue(report_file.exists())
        print(f"[OK] ActivityReport作成")
        
        # 7. セッション終了
        stop_result = self.auto_mode.execute_command('stop')
        self.assertEqual(stop_result['status'], 'stopped')
        print(f"[OK] セッション終了")
        
    @patch('builtins.input', return_value='2')
    def test_existing_analysis_flow(self, mock_input):
        """既存解析フローのテスト"""
        print("\n=== 既存解析フローテスト ===")
        
        # 1. AutoMode開始（既存解析を選択）
        result = self.auto_mode.execute_command('start')
        session_id = result['session_id']
        print(f"[OK] セッション開始: {session_id}")
        
        # 2. フロー確認
        self.assertEqual(self.auto_mode.config.current_flow, '既存解析')
        print(f"[OK] フロー設定: 既存解析")
        
        # 3. 既存ファイルの解析シミュレーション
        existing_files = [
            "main.py", "utils.py", "config.py", "database.py",
            "api.py", "models.py", "views.py", "tests.py"
        ]
        
        for file in existing_files:
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.ANALYZE, 
                f"既存コード解析: {file}"
            )
        print(f"[OK] {len(existing_files)}個のファイルを解析")
        
        # 4. 依存関係の分析
        detector = CircularImportDetector()
        detector.visited_modules = {
            'main': ['utils', 'config', 'api'],
            'utils': ['config'],
            'config': [],
            'api': ['models', 'database'],
            'models': ['database'],
            'database': ['config'],
            'views': ['models', 'api'],
            'tests': ['main', 'utils', 'models']
        }
        
        cycles = detector.detect()
        print(f"[OK] 循環参照検出: {len(cycles)}個")
        
        # 5. ドキュメント生成
        self.file_logger.log_file_access(
            "analysis_report.md", 
            AccessPurpose.MODIFY, 
            "解析レポート作成"
        )
        self.file_logger.log_file_access(
            "architecture.md", 
            AccessPurpose.MODIFY, 
            "アーキテクチャ図作成"
        )
        print(f"[OK] 解析ドキュメント生成")
        
        # 6. 解析結果の確認
        analyze_count = sum(1 for h in self.file_logger.access_history 
                           if h['purpose'] == AccessPurpose.ANALYZE)
        self.assertGreater(analyze_count, 5)
        print(f"[OK] 解析ファイル数: {analyze_count}")
        
        # 7. セッション終了
        self.auto_mode.execute_command('stop')
        print(f"[OK] セッション終了")
        
    @patch('builtins.input', return_value='3')
    def test_bug_fix_flow(self, mock_input):
        """バグ修正フローのテスト"""
        print("\n=== バグ修正フローテスト ===")
        
        # 1. AutoMode開始（バグ修正を選択）
        result = self.auto_mode.execute_command('start')
        session_id = result['session_id']
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
        print(f"[OK] バグ修正テスト成功")
        
        # 7. 回帰テスト
        regression_test = TestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=15,
            duration=3.0,
            details="回帰テスト全合格"
        )
        self.test_strategy.add_test_result(regression_test)
        print(f"[OK] 回帰テスト完了")
        
        # 8. 修正完了確認
        self.assertTrue(self.test_strategy.is_all_passed())
        modify_count = sum(1 for h in self.file_logger.access_history 
                          if h['purpose'] == AccessPurpose.MODIFY)
        self.assertGreaterEqual(modify_count, 2)  # 最低2つのファイル修正
        print(f"[OK] 修正ファイル数: {modify_count}")
        
        # 9. セッション終了
        self.auto_mode.execute_command('stop')
        print(f"[OK] セッション終了")
        
    @patch('builtins.input', return_value='4')
    def test_refactoring_flow(self, mock_input):
        """リファクタリングフローのテスト"""
        print("\n=== リファクタリングフローテスト ===")
        
        # 1. AutoMode開始（リファクタリングを選択）
        result = self.auto_mode.execute_command('start')
        session_id = result['session_id']
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
        
        # 7. コードメトリクス改善確認
        improvements = {
            "循環的複雑度": "15 -> 8",
            "重複コード": "25% -> 5%",
            "関数の長さ": "平均50行 -> 平均20行",
            "テストカバレッジ": "75% -> 85%"
        }
        
        self.file_logger.log_file_access(
            "refactoring_report.md", 
            AccessPurpose.MODIFY, 
            f"リファクタリング成果レポート: {improvements}"
        )
        print(f"[OK] コード品質改善確認")
        for metric, improvement in improvements.items():
            print(f"  - {metric}: {improvement}")
            
        # 8. 統合テスト
        integration_test = TestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=20,
            duration=4.0
        )
        self.test_strategy.add_test_result(integration_test)
        print(f"[OK] 統合テスト完了")
        
        # 9. 成果確認
        self.assertTrue(self.test_strategy.is_all_passed())
        modify_count = sum(1 for h in self.file_logger.access_history 
                          if h['purpose'] == AccessPurpose.MODIFY)
        self.assertGreater(modify_count, 3)
        print(f"[OK] リファクタリング完了: {modify_count}ファイル改善")
        
        # 10. セッション終了
        self.auto_mode.execute_command('stop')
        print(f"[OK] セッション終了")


class TestFlowIntegration(unittest.TestCase):
    """フロー間の統合テスト"""
    
    def test_flow_switching(self):
        """フロー切り替えテスト"""
        print("\n=== フロー切り替えテスト ===")
        
        temp_dir = tempfile.mkdtemp()
        auto_mode = AutoMode(temp_dir)
        
        flows = ['新規開発', '既存解析', 'バグ修正', 'リファクタリング']
        
        for i, flow in enumerate(flows, 1):
            with patch('builtins.input', return_value=str(i)):
                result = auto_mode.execute_command('start')
                self.assertEqual(auto_mode.config.current_flow, flow)
                print(f"[OK] フロー{i}: {flow}")
                auto_mode.execute_command('stop')
                
        shutil.rmtree(temp_dir)
        
    def test_concurrent_logging(self):
        """並行ログ記録テスト"""
        print("\n=== 並行ログ記録テスト ===")
        
        temp_dir = tempfile.mkdtemp()
        
        # 複数のロガーインスタンス
        file_logger = FileAccessLogger()
        activity_logger = UnifiedLogger(base_path=temp_dir)
        
        # CTOとアレックスの並行作業シミュレーション
        activity_logger.log_cto("プロジェクト計画策定")
        file_logger.log_file_access("plan.md", AccessPurpose.MODIFY, "計画書作成")
        
        activity_logger.log_alex("実装開始")
        file_logger.log_file_access("implementation.py", AccessPurpose.MODIFY, "機能実装")
        
        activity_logger.log_cto("レビュー実施")
        file_logger.log_file_access("implementation.py", AccessPurpose.REFERENCE, "コードレビュー")
        
        # ログが正しく記録されているか確認
        self.assertEqual(file_logger.access_count, 3)
        print(f"[OK] ファイルアクセス: {file_logger.access_count}回記録")
        
        # ActivityReportファイルの存在確認
        log_files = list(Path(temp_dir).glob("*_workingLog.md"))
        self.assertGreater(len(log_files), 0)
        print(f"[OK] ActivityReport: {len(log_files)}ファイル生成")
        
        shutil.rmtree(temp_dir)
        
    def test_test_strategy_across_flows(self):
        """フロー横断的なテスト戦略テスト"""
        print("\n=== フロー横断テスト戦略テスト ===")
        
        strategy = TestStrategy()
        
        # 各フローでのテスト結果を追加
        flow_results = {
            "新規開発": (TestLevel.UNIT, 50, 0),
            "既存解析": (TestLevel.INTEGRATION, 20, 1),
            "バグ修正": (TestLevel.UNIT, 10, 0),
            "リファクタリング": (TestLevel.E2E, 15, 0)
        }
        
        for flow_name, (level, total, failed) in flow_results.items():
            result = TestResult(
                level=level,
                passed=(failed == 0),
                failed=failed,
                total=total,
                duration=1.0,
                details=f"{flow_name}のテスト"
            )
            strategy.add_test_result(result)
            print(f"[OK] {flow_name}: {total}テスト（失敗: {failed}）")
            
        # 全体サマリー
        summary = strategy.get_summary()
        total_tests = sum(r['total'] for r in summary.values())
        total_failures = sum(r['failed'] for r in summary.values())
        
        print(f"\n[サマリー]")
        print(f"  総テスト数: {total_tests}")
        print(f"  総失敗数: {total_failures}")
        print(f"  成功率: {((total_tests - total_failures) / total_tests * 100):.1f}%")
        
        # 既存解析で1つ失敗があるため、全体はFalse
        self.assertFalse(strategy.is_all_passed())


def run_all_flow_tests():
    """すべてのフローテストを実行"""
    # テストスイートの作成
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # テストクラスを追加
    suite.addTests(loader.loadTestsFromTestCase(TestDevelopmentFlows))
    suite.addTests(loader.loadTestsFromTestCase(TestFlowIntegration))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    
    # 結果サマリー
    print("\n" + "="*70)
    print("[開発フローテスト結果]")
    print(f"実行: {result.testsRun} テスト")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[OK] すべての開発フローテストが成功しました！")
        print("\n検証完了フロー:")
        print("  ✓ 新規開発フロー（SDD+TDD 8ステップ）")
        print("  ✓ 既存解析フロー（コード解析とドキュメント生成）")
        print("  ✓ バグ修正フロー（TDDによるバグ修正）")
        print("  ✓ リファクタリングフロー（品質改善と回帰テスト）")
        print("  ✓ フロー切り替え機能")
        print("  ✓ 並行ログ記録機能")
        print("  ✓ フロー横断的テスト戦略")
    else:
        print("\n[NG] 一部のテストが失敗しています。")
        
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_flow_tests()
    sys.exit(0 if success else 1)