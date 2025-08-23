#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フロー統合テスト - Claude Code Core v12.0
フロー間の統合テストと横断的機能のテスト
"""

from unittest.mock import patch
from pathlib import Path

from auto_mode import AutoMode
from test_strategy import TestStrategy, TestLevel, TestResult

# 統合システムインポート
from test_base_utilities import OptimizedTestCase
from shared_logger import OptimizedLogger
from error_handler import StandardErrorHandler

class TestFlowIntegration(OptimizedTestCase):
    """フロー間の統合テスト - 統合システム使用"""
    
    def test_flow_switching(self):
        """フロー切り替えテスト - 統合システム使用"""
        self.logger.log_with_context("info", "フロー切り替えテスト開始")
        
        auto_mode = AutoMode(self.temp_dir)
        
        flows = ['新規開発', '既存解析', 'バグ修正', 'リファクタリング']
        
        for i, flow in enumerate(flows, 1):
            with patch('builtins.input', return_value=str(i)):
                result = auto_mode.execute_command('start')
                self.assertEqual(auto_mode.config.current_flow, flow)
                self.logger.log_with_context("info", f"フロー{i}切り替え成功: {flow}")
                auto_mode.execute_command('stop')
        
    def test_concurrent_logging(self):
        """並行ログ記録テスト - 統合システム使用"""
        self.logger.log_with_context("info", "並行ログ記録テスト開始")
        
        # 統合ロガーで並行処理をシミュレート
        cto_logger = OptimizedLogger(user="CTO", base_path=self.temp_dir)
        alex_logger = OptimizedLogger(user="Alex", base_path=self.temp_dir)
        
        # CTOとアレックスの並行作業シミュレーション
        cto_logger.log_activity("プロジェクト計画策定", metadata={"role": "CTO", "phase": "planning"})
        cto_logger.log_file_access("create", "plan.md", "success", {"description": "計画書作成"})
        
        alex_logger.log_activity("実装開始", metadata={"role": "Alex", "phase": "implementation"})
        alex_logger.log_file_access("create", "implementation.py", "success", {"description": "機能実装"})
        
        cto_logger.log_activity("レビュー実施", metadata={"role": "CTO", "phase": "review"})
        cto_logger.log_file_access("read", "implementation.py", "success", {"description": "コードレビュー"})
        
        # ログが正しく記録されているか確認（統合ロガーはバッファリング）
        cto_logger.flush()
        alex_logger.flush()
        
        # ログファイルの存在確認
        log_files = list(self.temp_dir.glob("optimized_log_*.jsonl"))
        self.assertGreater(len(log_files), 0)
        self.logger.log_with_context("info", f"並行ログ記録成功: {len(log_files)}ファイル生成")
        
        # リソースクリーンアップ
        cto_logger.close()
        alex_logger.close()
        
    def test_test_strategy_across_flows(self):
        """フロー横断的なテスト戦略テスト - 統合システム使用"""
        self.logger.log_with_context("info", "フロー横断テスト戦略テスト開始")
        
        strategy = TestStrategy()
        
        # 各フローでのテスト結果を追加
        flow_results = {
            "新規開発": TestResult(TestLevel.UNIT, True, 0, 20, 3.0),
            "既存解析": TestResult(TestLevel.INTEGRATION, True, 0, 15, 5.0),
            "バグ修正": TestResult(TestLevel.UNIT, True, 0, 8, 1.5),
            "リファクタリング": TestResult(TestLevel.PERFORMANCE, True, 0, 25, 10.0)
        }
        
        for flow_name, result in flow_results.items():
            strategy.add_test_result(result)
            self.logger.log_with_context("info", f"{flow_name}テスト結果追加", 
                                       {"total_tests": result.total, "passed": result.passed})
        
        # 全体的なテスト戦略が成功しているか確認
        self.assertTrue(strategy.is_all_passed())
        total_tests = sum(result.total for result in flow_results.values())
        self.assertEqual(strategy.get_total_count(), total_tests)
        
        self.logger.log_with_context("info", "フロー横断テスト戦略完了",
                                   {"total_tests": total_tests, "all_passed": True})
    
    def test_end_to_end_development_cycle(self):
        """エンドツーエンド開発サイクルテスト - 統合システム使用"""
        self.logger.log_with_context("info", "エンドツーエンド開発サイクルテスト開始")
        auto_mode = AutoMode(temp_dir)
        file_logger = FileAccessLogger()
        
        # 1. 新規開発フロー
        with patch('builtins.input', return_value='1'):
            session1 = auto_mode.execute_command('start')
            
            # 新規開発での作業
            file_logger.log_file_access("new_feature.py", AccessPurpose.MODIFY, "新機能実装")
            file_logger.log_file_access("test_new_feature.py", AccessPurpose.MODIFY, "新機能テスト")
            
            auto_mode.execute_command('stop')
            print("[OK] 新規開発フロー完了")
        
        # 2. バグ修正フロー
        with patch('builtins.input', return_value='3'):
            session2 = auto_mode.execute_command('start')
            
            # バグ修正での作業
            file_logger.log_file_access("new_feature.py", AccessPurpose.ANALYZE, "バグ解析")
            file_logger.log_file_access("new_feature.py", AccessPurpose.MODIFY, "バグ修正")
            
            auto_mode.execute_command('stop')
            print("[OK] バグ修正フロー完了")
        
        # 3. リファクタリングフロー
        with patch('builtins.input', return_value='4'):
            session3 = auto_mode.execute_command('start')
            
            # リファクタリングでの作業
            file_logger.log_file_access("new_feature.py", AccessPurpose.ANALYZE, "品質分析")
            file_logger.log_file_access("new_feature.py", AccessPurpose.MODIFY, "コード改善")
            
            auto_mode.execute_command('stop')
            print("[OK] リファクタリングフロー完了")
        
        # 4. 既存解析フロー
        with patch('builtins.input', return_value='2'):
            session4 = auto_mode.execute_command('start')
            
            # 既存解析での作業
            file_logger.log_file_access("new_feature.py", AccessPurpose.ANALYZE, "最終解析")
            file_logger.log_file_access("analysis_final.md", AccessPurpose.MODIFY, "総合解析報告")
            
            auto_mode.execute_command('stop')
            print("[OK] 既存解析フロー完了")
        
        # 全フローでの作業が記録されていることを確認
        modify_count = sum(1 for h in file_logger.access_history 
                          if h['purpose'] == AccessPurpose.MODIFY)
        analyze_count = sum(1 for h in file_logger.access_history 
                           if h['purpose'] == AccessPurpose.ANALYZE)
        
        self.assertGreater(modify_count, 3)
        self.assertGreater(analyze_count, 2)
        
        print(f"[OK] エンドツーエンドサイクル: 修正{modify_count}回、解析{analyze_count}回")
        
        shutil.rmtree(temp_dir)
    
    def test_multi_user_collaboration(self):
        """マルチユーザー協調作業テスト"""
        print("\n=== マルチユーザー協調作業テスト ===")
        
        temp_dir = tempfile.mkdtemp()
        
        # 複数のActivityLogger（CTOとアレックス）
        cto_logger = UnifiedLogger(base_path=temp_dir, user="CTO")
        alex_logger = UnifiedLogger(base_path=temp_dir, user="Alex")
        
        # 協調作業シナリオ
        collaboration_tasks = [
            (cto_logger.log_cto, "要件定義レビュー"),
            (alex_logger.log_alex, "技術設計書作成"),
            (cto_logger.log_cto, "設計書レビュー"),
            (alex_logger.log_alex, "実装開始"),
            (cto_logger.log_cto, "中間レビュー"),
            (alex_logger.log_alex, "テスト作成"),
            (cto_logger.log_cto, "最終承認"),
            (alex_logger.log_alex, "デプロイ準備")
        ]
        
        for logger_method, task in collaboration_tasks:
            logger_method(task)
            print(f"[OK] {task}")
        
        # 両方のユーザーのログファイルが生成されていることを確認
        cto_logs = list(Path(temp_dir).glob("*CTO*.md"))
        alex_logs = list(Path(temp_dir).glob("*Alex*.md"))
        
        self.assertGreater(len(cto_logs), 0)
        self.assertGreater(len(alex_logs), 0)
        
        print(f"[OK] 協調作業ログ: CTO {len(cto_logs)}ファイル、Alex {len(alex_logs)}ファイル")
        
        shutil.rmtree(temp_dir)

def run_integration_tests():
    """統合テストの実行"""
    print("=== フロー統合テスト開始 ===")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFlowIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n[OK] 全フロー統合テスト合格")
        print("  ✓ フロー切り替え機能")
        print("  ✓ 並行ログ記録機能")
        print("  ✓ フロー横断的テスト戦略")
        print("  ✓ エンドツーエンド開発サイクル")
        print("  ✓ マルチユーザー協調作業")
    else:
        print("\n[NG] 一部の統合テストが失敗しています。")
        
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_integration_tests()
    exit(0 if success else 1)