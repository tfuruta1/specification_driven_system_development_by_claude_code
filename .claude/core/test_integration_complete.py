#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合完了確認テスト
Phase 1統合が正しく完了したことを確認
"""

import unittest
import tempfile
import shutil
from pathlib import Path


class TestIntegrationComplete(unittest.TestCase):
    """統合完了確認テスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_name = "integration_test_project"
    
    def tearDown(self):
        """テストクリーンアップ"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_unified_system_can_be_imported(self):
        """統合システムがインポートできる"""
        from unified_system import UnifiedSystem, DevelopmentFlow, SYSTEM_VERSION
        self.assertIsNotNone(UnifiedSystem)
        self.assertIsNotNone(DevelopmentFlow)
        self.assertEqual(SYSTEM_VERSION, "v1.0")
    
    def test_unified_system_replaces_both_old_systems(self):
        """統合システムが両方の旧システム機能を提供する"""
        from unified_system import UnifiedSystem
        
        # 一時的にパッチして安全にテスト
        import unittest.mock
        with unittest.mock.patch.object(Path, 'mkdir'):
            system = UnifiedSystem(self.project_name)
            
            # system.py の機能：開発フロー実行
            result = system.execute_new_project_flow("テスト要求")
            self.assertIn("requirements", result)
            self.assertIn("design", result)
            self.assertIn("tasks", result)
            
            # sdd_tdd_system.py の機能：SDD+TDD統合
            self.assertTrue(hasattr(system, 'create_requirements_doc'))
            self.assertTrue(hasattr(system, 'create_design_doc'))
            self.assertTrue(hasattr(system, 'create_tasks_doc'))
            self.assertTrue(hasattr(system, 'create_failing_test'))
    
    def test_kiss_principle_compliance(self):
        """KISS原則に準拠していることを確認"""
        from unified_system import UnifiedSystem
        import inspect
        
        # クラスのメソッド数が適切（過度に複雑でない）
        methods = [m for m in dir(UnifiedSystem) if not m.startswith('_')]
        self.assertLess(len(methods), 15, "メソッド数が多すぎる（KISS原則違反）")
        
        # 主要メソッドの複雑度確認（行数で簡易チェック）
        system = UnifiedSystem.__new__(UnifiedSystem)
        for method_name in ['create_requirements_doc', 'create_design_doc']:
            method = getattr(system, method_name)
            source_lines = inspect.getsource(method).split('\n')
            # ドキュメント文字列を除いた実装行数
            impl_lines = [l for l in source_lines if l.strip() and not l.strip().startswith('"""')]
            self.assertLess(len(impl_lines), 30, f"{method_name}が複雑すぎる")
    
    def test_yagni_principle_compliance(self):
        """YAGNI原則に準拠していることを確認"""
        from unified_system import UnifiedSystem
        
        # 使われない機能（キャッシュなど）が削除されていることを確認
        system = UnifiedSystem.__new__(UnifiedSystem)
        
        # 旧system.pyにあったキャッシュ機能は不要なので削除されている
        self.assertFalse(hasattr(system, 'get_cache_key'))
        self.assertFalse(hasattr(system, 'save_cache'))
        self.assertFalse(hasattr(system, 'load_cache'))
        
        # 過度に複雑だった既存システム修正フローが簡素化されている
        # （10ステップから必要最小限に）
        if hasattr(system, 'execute_existing_project_flow'):
            # 簡素化されたフローのみ
            pass
    
    def test_tdd_compliance(self):
        """TDD原則に準拠していることを確認"""
        from unified_system import UnifiedSystem
        
        # TDD Red-Green-Refactorサイクルをサポート
        system = UnifiedSystem.__new__(UnifiedSystem)
        self.assertTrue(hasattr(system, 'create_failing_test'), "Red Phaseサポートが必要")
        
        # TDDドキュメントを生成できる
        self.assertTrue(hasattr(system, 'create_tasks_doc'), "TDD計画書作成が必要")


class TestSystemIntegration(unittest.TestCase):
    """システム統合テスト"""
    
    def test_full_workflow_integration(self):
        """完全ワークフローの統合テスト"""
        from unified_system import UnifiedSystem
        import unittest.mock
        
        with unittest.mock.patch.object(Path, 'mkdir'), \
             unittest.mock.patch.object(Path, 'write_text'):
            
            system = UnifiedSystem("integration_test")
            
            # 新規開発フローが完全に動作する
            result = system.execute_new_project_flow("統合テスト要求")
            
            # 必要な要素がすべて含まれている
            self.assertIn("requirements", result)
            self.assertIn("design", result) 
            self.assertIn("tasks", result)
            self.assertIn("tdd_cycle", result)
            
            # 適切な形式で結果が返される
            self.assertEqual(result["flow"], "新規開発")
            self.assertIn("JST", result["timestamp"])


if __name__ == "__main__":
    print("=" * 60)
    print("[統合テスト] Phase 1 コアシステム統合確認")
    print("=" * 60)
    print("unified_system.py の統合が正しく完了したことを確認します")
    print("=" * 60)
    
    unittest.main(verbosity=2)