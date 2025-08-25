#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リファクタリング後のモジュールの統合テスト
TDD原則に基づき、100%カバレッジを目指す
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Setup import paths
current_file = Path(__file__).resolve()
claude_root = None
current = current_file.parent
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    if (current / '.claude').exists():
        claude_root = current / '.claude'
        break
    current = current.parent

if claude_root:
    sys.path.insert(0, str(claude_root / "system"))
    sys.path.insert(0, str(claude_root))

# Import refactored modules
try:
    from core.alex_team_unified import AlexTeamUnified, TaskStatus, EngineerRole, Task
    from core.dev_rules_unified import DevRulesUnified, RuleType, RuleViolation
    from core.system_manager import SystemManager
    from core.import_fixer import setup_import_paths, get_import_setup_code, fix_module_imports
except ImportError:
    # Alternative import for test environment
    sys.path.insert(0, str(claude_root / "system"))
    from core.alex_team_unified import AlexTeamUnified, TaskStatus, EngineerRole, Task
    from core.dev_rules_unified import DevRulesUnified, RuleType, RuleViolation
    from core.system_manager import SystemManager
    from core.import_fixer import setup_import_paths, get_import_setup_code, fix_module_imports


class TestAlexTeamUnified(unittest.TestCase):
    """AlexTeamUnifiedのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.team = AlexTeamUnified()
    
    def test_initialization(self):
        """初期化テスト"""
        result = self.team.initialize()
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Alex Team Unified System initialized")
    
    def test_create_task(self):
        """タスク作成テスト"""
        task = self.team.create_task("refactor", "Apply DRY principle")
        self.assertEqual(task.type, "refactor")
        self.assertEqual(task.description, "Apply DRY principle")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIsNone(task.assignee)
    
    def test_assign_task(self):
        """タスク割り当てテスト"""
        task = self.team.create_task("test", "Write unit tests")
        result = self.team.assign_task(task, EngineerRole.TEST)
        self.assertTrue(result.success)
        self.assertEqual(task.assignee, EngineerRole.TEST)
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
    
    def test_complete_task(self):
        """タスク完了テスト"""
        task = self.team.create_task("optimize", "Optimize performance")
        self.team.assign_task(task, EngineerRole.OPTIMIZER)
        result = self.team.complete_task(task, "Optimization completed")
        self.assertTrue(result.success)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.result, "Optimization completed")
    
    def test_task_failure(self):
        """タスク失敗テスト"""
        task = self.team.create_task("bugfix", "Fix critical bug")
        with patch.object(task, '__setattr__', side_effect=Exception("Test error")):
            result = self.team.complete_task(task, "Fixed")
            self.assertFalse(result.success)
    
    def test_get_task_summary(self):
        """タスクサマリー取得テスト"""
        # タスク作成
        task1 = self.team.create_task("task1", "Description 1")
        task2 = self.team.create_task("task2", "Description 2")
        self.team.assign_task(task1, EngineerRole.LEAD)
        self.team.complete_task(task2, "Done")
        
        summary = self.team.get_task_summary()
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["in_progress"], 1)
        self.assertEqual(summary["completed"], 1)
    
    def test_cleanup(self):
        """クリーンアップテスト"""
        self.team.create_task("task", "Test task")
        result = self.team.cleanup()
        self.assertTrue(result.success)
        self.assertEqual(len(self.team.tasks), 0)
    
    @patch('core.alex_team_unified.OptimizedSelfDiagnosisSystem')
    def test_run_self_diagnosis(self, mock_diagnosis):
        """自己診断テスト"""
        mock_instance = Mock()
        mock_instance.run_diagnosis.return_value = {"success": True, "issues": 0}
        mock_diagnosis.return_value = mock_instance
        
        result = self.team.run_self_diagnosis()
        self.assertTrue(result.success)
    
    @patch('core.alex_team_unified.AutomatedTestGenerator')
    def test_run_tests(self, mock_generator):
        """テスト実行テスト"""
        mock_instance = Mock()
        mock_instance.generate_tests.return_value = {
            "success": True,
            "message": "Tests completed",
            "coverage": 100.0
        }
        mock_generator.return_value = mock_instance
        
        result = self.team.run_tests(100.0)
        self.assertTrue(result.success)


class TestDevRulesUnified(unittest.TestCase):
    """DevRulesUnifiedのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.rules = DevRulesUnified()
    
    def test_initialization(self):
        """初期化テスト"""
        result = self.rules.initialize()
        self.assertTrue(result.success)
        self.assertEqual(len(self.rules.violations), 0)
    
    def test_check_tdd_compliance(self):
        """TDDコンプライアンステスト"""
        test_file = Path("test_module.py")
        violations = self.rules.check_tdd_compliance(test_file)
        # test_で始まるファイルはテストファイルなので違反なし
        self.assertEqual(len(violations), 0)
        
        # 通常のPythonファイルでテストファイルが存在しない場合
        regular_file = Path("module.py")
        violations = self.rules.check_tdd_compliance(regular_file)
        self.assertGreater(len(violations), 0)
    
    def test_check_dry_compliance(self):
        """DRYコンプライアンステスト"""
        # 重複コードを含むコンテンツ
        content = """
def func1():
    x = 1
    y = 2
    z = 3
    
def func2():
    x = 1
    y = 2
    z = 3
"""
        violations = self.rules.check_dry_compliance(content, "test.py")
        self.assertGreater(len(violations), 0)
    
    def test_check_kiss_compliance(self):
        """KISSコンプライアンステスト"""
        # 深いネストと長い行を含むコンテンツ
        content = "    " * 7 + "deep_nested_code\n"
        content += "x = " + "a" * 150 + "\n"
        
        violations = self.rules.check_kiss_compliance(content, "test.py")
        self.assertGreater(len(violations), 0)
    
    def test_check_yagni_compliance(self):
        """YAGNIコンプライアンステスト"""
        content = """
# TODO: Implement this later
# FIXME: This is broken
# HACK: Temporary solution
"""
        violations = self.rules.check_yagni_compliance(content, "test.py")
        self.assertEqual(len(violations), 3)
    
    def test_check_file(self):
        """ファイルチェックテスト"""
        # 一時ファイル作成
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Test file\nprint('hello')\n")
            temp_path = Path(f.name)
        
        try:
            result = self.rules.check_file(temp_path)
            # 結果を確認（違反の有無は内容次第）
            self.assertIsNotNone(result)
        finally:
            temp_path.unlink()
    
    def test_get_summary(self):
        """サマリー取得テスト"""
        # 違反を追加
        self.rules.violations.append(RuleViolation(
            rule_type=RuleType.TDD,
            file_path="test.py",
            line_number=1,
            message="Test violation",
            severity="warning"
        ))
        
        summary = self.rules.get_summary()
        self.assertEqual(summary["total_violations"], 1)
        self.assertEqual(summary["by_severity"]["warning"], 1)
    
    def test_cleanup(self):
        """クリーンアップテスト"""
        self.rules.violations.append(RuleViolation(
            rule_type=RuleType.DRY,
            file_path="test.py",
            line_number=1,
            message="Test",
            severity="info"
        ))
        result = self.rules.cleanup()
        self.assertTrue(result.success)
        self.assertEqual(len(self.rules.violations), 0)


class TestSystemManager(unittest.TestCase):
    """SystemManagerのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.manager = SystemManager()
    
    @patch('core.system_manager.AlexTeamUnified')
    @patch('core.system_manager.DevRulesUnified')
    @patch('core.system_manager.UnifiedCache')
    def test_initialization(self, mock_cache, mock_rules, mock_team):
        """初期化テスト"""
        # モックの初期化メソッドを設定
        mock_team.return_value.initialize.return_value = Mock(success=True)
        mock_rules.return_value.initialize.return_value = Mock(success=True)
        mock_cache.return_value.initialize.return_value = Mock(success=True)
        
        result = self.manager.initialize()
        self.assertTrue(result.success)
        self.assertIsNotNone(self.manager.alex_team)
        self.assertIsNotNone(self.manager.dev_rules)
        self.assertIsNotNone(self.manager.cache)
    
    def test_get_system_status(self):
        """システムステータス取得テスト"""
        status = self.manager.get_system_status()
        self.assertIn("initialized", status)
        self.assertIn("components", status)
        self.assertIn("root_path", status)
    
    def test_execute_command(self):
        """コマンド実行テスト"""
        # initコマンド
        with patch.object(self.manager, 'initialize') as mock_init:
            mock_init.return_value = Mock(success=True)
            result = self.manager.execute_command("init")
            mock_init.assert_called_once()
        
        # 不明なコマンド
        result = self.manager.execute_command("unknown")
        self.assertFalse(result.success)
        self.assertIn("Unknown command", result.message)
    
    @patch('core.system_manager.AlexTeamUnified')
    def test_run_self_diagnosis(self, mock_team):
        """自己診断実行テスト"""
        mock_instance = Mock()
        mock_instance.run_self_diagnosis.return_value = Mock(success=True)
        mock_team.return_value = mock_instance
        
        self.manager.alex_team = mock_instance
        result = self.manager.run_self_diagnosis()
        self.assertTrue(result.success)
    
    @patch('core.system_manager.DevRulesUnified')
    def test_check_code_quality(self, mock_rules):
        """コード品質チェックテスト"""
        mock_instance = Mock()
        mock_instance.check_file.return_value = Mock(success=True)
        mock_instance.get_summary.return_value = {"total_violations": 0}
        mock_rules.return_value = mock_instance
        
        self.manager.dev_rules = mock_instance
        
        with patch.object(Path, 'glob', return_value=[Path("test.py")]):
            result = self.manager.check_code_quality()
            self.assertIsNotNone(result)
    
    def test_cleanup(self):
        """クリーンアップテスト"""
        # 各コンポーネントをモック化
        self.manager.alex_team = Mock()
        self.manager.alex_team.cleanup.return_value = Mock(success=True)
        self.manager.dev_rules = Mock()
        self.manager.dev_rules.cleanup.return_value = Mock(success=True)
        self.manager.cache = Mock()
        self.manager.cache.cleanup.return_value = Mock(success=True)
        
        result = self.manager.cleanup()
        self.assertTrue(result.success)


class TestImportFixer(unittest.TestCase):
    """ImportFixerのテスト"""
    
    def test_setup_import_paths(self):
        """インポートパス設定テスト"""
        claude_root, system_path = setup_import_paths()
        self.assertIsNotNone(claude_root)
        self.assertIsNotNone(system_path)
        self.assertTrue(system_path.exists())
    
    def test_get_import_setup_code(self):
        """インポート設定コード取得テスト"""
        code = get_import_setup_code()
        self.assertIn("Setup import paths", code)
        self.assertIn("sys.path.insert", code)
        self.assertIn("claude_root", code)
    
    def test_fix_module_imports(self):
        """モジュールインポート修正テスト"""
        import tempfile
        
        # テスト用の一時ファイル作成
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("#!/usr/bin/env python3\n")
            f.write('"""Test module"""\n')
            f.write("print('hello')\n")
            temp_path = Path(f.name)
        
        try:
            # インポート修正
            result = fix_module_imports(temp_path)
            self.assertTrue(result)
            
            # 修正後の内容確認
            content = temp_path.read_text()
            self.assertIn("Setup import paths", content)
            
            # 既に修正済みの場合
            result = fix_module_imports(temp_path)
            self.assertTrue(result)
            
        finally:
            temp_path.unlink()


def run_tests():
    """全テスト実行"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_tests()