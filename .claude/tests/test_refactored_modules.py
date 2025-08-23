"""
リファクタリング済みモジュールの統合テスト
Phase 1-3で作成された新規モジュールのテストカバレッジ
"""

import unittest
import sys
from pathlib import Path

# .claudeディレクトリをパスに追加
claude_dir = Path(__file__).parent.parent
sys.path.insert(0, str(claude_dir))


class TestUnifiedSystem(unittest.TestCase):
    """統合システムのテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        from core.unified_system import UnifiedSystem
        self.system = UnifiedSystem()
    
    def test_sdd_workflow(self):
        """SDD（仕様書駆動開発）ワークフローのテスト"""
        # 要件定義書作成
        req_doc = self.system.create_requirements_doc("Test Project")
        self.assertIn("要件定義書", req_doc)
        self.assertIn("Test Project", req_doc)
        
        # 技術設計書作成
        design_doc = self.system.create_design_doc("Test Project")
        self.assertIn("技術設計書", design_doc)
        
        # 実装計画作成
        tasks_doc = self.system.create_tasks_doc("Test Project")
        self.assertIn("実装計画", tasks_doc)
    
    def test_tdd_workflow(self):
        """TDD（テスト駆動開発）ワークフローのテスト"""
        # RED Phase - 失敗テスト作成
        test_code = self.system.create_failing_test("test_feature")
        self.assertIn("def test_", test_code)
        self.assertIn("assert", test_code)
        
        # ワークフロー実行
        project_name = "TestProject"
        result = self.system.execute_new_project_flow(project_name)
        self.assertIn("新規プロジェクトフロー完了", result)
    
    def test_existing_project_flow(self):
        """既存プロジェクト修正フローのテスト"""
        result = self.system.execute_existing_project_flow("TestProject")
        self.assertIn("既存プロジェクト修正フロー完了", result)


class TestAutoModeModules(unittest.TestCase):
    """Auto Mode分割モジュールのテスト"""
    
    def test_auto_mode_config(self):
        """Auto Mode設定管理のテスト"""
        from core.auto_mode_config import AutoModeConfig
        config = AutoModeConfig()
        
        # デフォルト設定確認
        self.assertIsNotNone(config.config)
        self.assertTrue(hasattr(config, 'get'))
        self.assertTrue(hasattr(config, 'set'))
        
        # 設定の取得と更新
        config.set('test_key', 'test_value')
        self.assertEqual(config.get('test_key'), 'test_value')
    
    def test_auto_mode_state(self):
        """Auto Mode状態管理のテスト"""
        from core.auto_mode_state import AutoModeStateManager
        state_manager = AutoModeStateManager()
        
        # 状態遷移テスト
        self.assertEqual(state_manager.get_state(), 'inactive')
        state_manager.activate()
        self.assertEqual(state_manager.get_state(), 'active')
        state_manager.deactivate()
        self.assertEqual(state_manager.get_state(), 'inactive')
    
    def test_auto_mode_core(self):
        """Auto Modeコアロジックのテスト"""
        from core.auto_mode_core import AutoModeManager
        manager = AutoModeManager()
        
        # 基本機能確認
        self.assertFalse(manager.is_active())
        manager.start()
        self.assertTrue(manager.is_active())
        manager.stop()
        self.assertFalse(manager.is_active())


class TestDevelopmentRulesModules(unittest.TestCase):
    """Development Rules分割モジュールのテスト"""
    
    def test_dev_rules_core(self):
        """開発ルールエンジンのテスト"""
        from core.dev_rules_core import DevelopmentRulesEngine
        engine = DevelopmentRulesEngine()
        
        # 基本機能確認
        self.assertIsNotNone(engine.config)
        self.assertTrue(hasattr(engine, 'validate'))
        
        # ルール検証
        result = engine.validate("test_code")
        self.assertIsInstance(result, dict)
    
    def test_checklist_manager(self):
        """チェックリスト管理のテスト"""
        from core.dev_rules_checklist import ChecklistManager
        manager = ChecklistManager()
        
        # チェックリスト操作
        checklist = manager.create_checklist("test")
        self.assertIsInstance(checklist, list)
        
        # 項目追加
        manager.add_item("test", "Test Item")
        updated = manager.get_checklist("test")
        self.assertIn("Test Item", str(updated))
    
    def test_tdd_workflow_manager(self):
        """TDDワークフロー管理のテスト"""
        from core.dev_rules_tdd import TDDWorkflowManager
        manager = TDDWorkflowManager()
        
        # RED-GREEN-REFACTORサイクル
        red_result = manager.start_red_phase("test_feature")
        self.assertIn("RED", red_result)
        
        green_result = manager.start_green_phase("test_feature")
        self.assertIn("GREEN", green_result)
        
        refactor_result = manager.start_refactor_phase("test_feature")
        self.assertIn("REFACTOR", refactor_result)
    
    def test_task_manager(self):
        """タスク管理のテスト"""
        from core.dev_rules_tasks import TaskManager
        manager = TaskManager()
        
        # タスク作成と管理
        task_id = manager.create_task("Test Task", "pending")
        self.assertIsNotNone(task_id)
        
        # タスク状態更新
        manager.update_task_status(task_id, "in_progress")
        status = manager.get_task_status(task_id)
        self.assertEqual(status, "in_progress")
        
        # タスク完了
        manager.complete_task(task_id)
        status = manager.get_task_status(task_id)
        self.assertEqual(status, "completed")


class TestPathUtils(unittest.TestCase):
    """パスユーティリティのテスト"""
    
    def test_normalize_path(self):
        """パス正規化のテスト"""
        from core.path_utils import PathUtils
        
        # Windows形式のパス
        win_path = "C:\\Users\\test\\file.txt"
        normalized = PathUtils.normalize_path(win_path)
        self.assertIsInstance(normalized, Path)
        
        # Unix形式のパス
        unix_path = "/home/test/file.txt"
        normalized = PathUtils.normalize_path(unix_path)
        self.assertIsInstance(normalized, Path)
    
    def test_join_paths(self):
        """パス結合のテスト"""
        from core.path_utils import PathUtils
        
        result = PathUtils.join_paths("base", "sub", "file.txt")
        self.assertIsInstance(result, Path)
        self.assertTrue(str(result).endswith("file.txt"))
    
    def test_get_claude_dir(self):
        """Claudeディレクトリ取得のテスト"""
        from core.path_utils import PathUtils
        
        claude_dir = PathUtils.get_claude_dir()
        self.assertIsInstance(claude_dir, Path)
        self.assertTrue(claude_dir.name == '.claude' or 
                       str(claude_dir).endswith('.claude'))


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def test_module_imports(self):
        """すべてのモジュールがインポート可能か確認"""
        modules = [
            'core.unified_system',
            'core.auto_mode',
            'core.auto_mode_config',
            'core.auto_mode_state',
            'core.auto_mode_core',
            'core.development_rules',
            'core.dev_rules_core',
            'core.dev_rules_checklist',
            'core.dev_rules_tdd',
            'core.dev_rules_tasks',
            'core.dev_rules_integration',
            'core.path_utils',
        ]
        
        for module_name in modules:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")
    
    def test_end_to_end_workflow(self):
        """エンドツーエンドワークフローテスト"""
        from core.unified_system import UnifiedSystem
        from core.auto_mode import AutoMode
        from core.development_rules import DevelopmentRules
        
        # 統合システム初期化
        system = UnifiedSystem()
        auto_mode = AutoMode()
        dev_rules = DevelopmentRules()
        
        # 新規プロジェクトワークフロー
        project_name = "E2ETestProject"
        
        # Auto Mode有効化
        auto_mode.start()
        self.assertTrue(auto_mode.is_active())
        
        # 開発ルール適用
        rules_result = dev_rules.apply_rules(project_name)
        self.assertIsNotNone(rules_result)
        
        # SDDフロー実行
        sdd_result = system.execute_new_project_flow(project_name)
        self.assertIn("完了", sdd_result)
        
        # Auto Mode無効化
        auto_mode.stop()
        self.assertFalse(auto_mode.is_active())


def run_tests():
    """テスト実行"""
    # テストスイート作成
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # テストクラスを追加
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestAutoModeModules))
    suite.addTests(loader.loadTestsFromTestCase(TestDevelopmentRulesModules))
    suite.addTests(loader.loadTestsFromTestCase(TestPathUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # カバレッジレポート
    print("\n" + "="*60)
    print("テストカバレッジレポート")
    print("="*60)
    print(f"実行テスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] すべてのテストが成功しました！")
    else:
        print("\n[FAILED] テストに失敗がありました")
        for test, traceback in result.failures:
            print(f"\n失敗: {test}")
            print(traceback)
        for test, traceback in result.errors:
            print(f"\nエラー: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)