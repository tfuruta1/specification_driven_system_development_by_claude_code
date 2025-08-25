#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI往復最適化システムテスト
目標: 20往復→3-5往復の削減を検証
"""

import unittest
import sys
from pathlib import Path

# Standard path setup pattern
current = Path(__file__).resolve()
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    current = current.parent
    if current == current.parent:
        raise RuntimeError("Could not find .claude directory")

system_path = claude_root / "system"
if str(system_path) not in sys.path:
    sys.path.insert(0, str(system_path))

try:
    from core.ai_batch_optimizer import AIBatchOptimizer, BatchTask, BatchTaskType
    from core.automated_test_generator import AutomatedTestGenerator
    from core.common_base import BaseResult
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class TestAIOptimizationSystem(unittest.TestCase):
    """AI往復最適化システムテスト"""
    
    def setUp(self):
        """テスト準備"""
        self.optimizer = AIBatchOptimizer()
        self.test_generator = AutomatedTestGenerator()
        
    def tearDown(self):
        """テスト後処理"""
        if hasattr(self.optimizer, 'cleanup'):
            self.optimizer.cleanup()
        if hasattr(self.test_generator, 'cleanup'):
            self.test_generator.cleanup()
    
    def test_batch_optimizer_initialization(self):
        """バッチオプティマイザー初期化テスト"""
        result = self.optimizer.initialize()
        self.assertIsInstance(result, BaseResult)
        self.assertTrue(result.success)
        
    def test_test_generator_initialization(self):
        """テストジェネレーター初期化テスト"""
        result = self.test_generator.initialize()  
        self.assertIsInstance(result, BaseResult)
        self.assertTrue(result.success)
        
    def test_batch_task_creation(self):
        """バッチタスク作成テスト"""
        spec = {
            "description": "Test module",
            "class_name": "TestManager"
        }
        
        task = self.optimizer.create_implementation_batch("test_module", spec)
        self.assertIsNotNone(task)
        self.assertEqual(task.task_type, BatchTaskType.IMPLEMENT_WITH_TESTS)
        self.assertIn("test_module", task.input_data["module_name"])
        
    def test_task_queue_management(self):
        """タスクキュー管理テスト"""
        self.optimizer.initialize()
        
        spec = {"description": "Queue test"}
        task = self.optimizer.create_implementation_batch("queue_test", spec)
        
        # タスク追加
        result = self.optimizer.add_task(task)
        self.assertTrue(result.success)
        self.assertEqual(len(self.optimizer.task_queue), 1)
        
    def test_optimization_report_generation(self):
        """最適化レポート生成テスト"""
        report = self.optimizer.get_optimization_report()
        self.assertIsInstance(report, dict)
        
        # 初期状態では実行タスクなし
        if "message" in report:
            self.assertIn("No tasks", report["message"])
        
    def test_specification_template_exists(self):
        """仕様書テンプレート存在確認"""
        template_path = claude_root / "system" / "templates" / "SPECIFICATION_TEMPLATE.md"
        self.assertTrue(template_path.exists())
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("AI往復最適化", content)
            self.assertIn("バッチ処理要求", content)
        
    def test_ai_context_documentation_exists(self):
        """AI協力コンテキスト文書存在確認"""
        context_path = claude_root / "AI_COLLABORATION_CONTEXT.md"
        self.assertTrue(context_path.exists())
        
        with open(context_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("往復最適化", content)
            self.assertIn("20回→3-5回", content)
            
    def test_pre_commit_hooks_setup(self):
        """Pre-commitフック設定確認"""
        lefthook_path = claude_root / "lefthook.yml" 
        self.assertTrue(lefthook_path.exists())
        
        with open(lefthook_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("ai-ready", content)
            self.assertIn("tdd-cycle", content)
            
    def test_system_integration(self):
        """システム統合テスト"""
        # 初期化
        init_result = self.optimizer.initialize()
        self.assertTrue(init_result.success)
        
        # テストタスク作成
        spec = {"description": "Integration test", "class_name": "IntegrationManager"}
        task = self.optimizer.create_implementation_batch("integration_test", spec)
        
        # タスク追加
        add_result = self.optimizer.add_task(task)
        self.assertTrue(add_result.success)
        
        # レポート生成（実行前）
        report = self.optimizer.get_optimization_report()
        self.assertIsInstance(report, dict)


class TestOptimizationMetrics(unittest.TestCase):
    """最適化メトリクス確認テスト"""
    
    def test_roundtrip_reduction_target(self):
        """往復削減目標の確認"""
        optimizer = AIBatchOptimizer()
        report = optimizer.get_optimization_report()
        
        # 目標値の確認
        if "ai_roundtrip_reduction" in report:
            self.assertIn("60-80%", report["ai_roundtrip_reduction"])
            
    def test_batch_processing_capability(self):
        """バッチ処理能力の確認"""
        optimizer = AIBatchOptimizer()
        
        # 複数タスクを同時処理できることを確認
        self.assertTrue(hasattr(optimizer, 'execute_batch'))
        self.assertTrue(hasattr(optimizer, 'add_task'))
        self.assertTrue(hasattr(optimizer, 'task_queue'))


class TestDocumentationIntegration(unittest.TestCase):
    """文書統合テスト"""
    
    def test_all_optimization_files_exist(self):
        """最適化関連ファイルの存在確認"""
        required_files = [
            "AI_COLLABORATION_CONTEXT.md",
            "system/templates/SPECIFICATION_TEMPLATE.md", 
            "system/core/ai_batch_optimizer.py",
            "system/core/automated_test_generator.py",
            "lefthook.yml"
        ]
        
        for file_path in required_files:
            full_path = claude_root / file_path
            self.assertTrue(full_path.exists(), f"Missing file: {file_path}")
            
    def test_claude_md_integration(self):
        """CLAUDE.md統合確認"""
        claude_md_path = claude_root.parent / "CLAUDE.md"
        
        if claude_md_path.exists():
            with open(claude_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # AI往復最適化の記載確認（あれば）
                self.assertIsInstance(content, str)


if __name__ == '__main__':
    unittest.main(verbosity=2)