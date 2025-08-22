#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for TriggerKeywordDetector
TDD - Red Phase: 失敗するテストを先に書く
"""

import unittest
from unittest.mock import Mock, patch, call
from datetime import datetime

# テスト対象モジュール（まだ存在しない - これがTDDのRed Phase）
try:
    from trigger_keyword_detector import (
        TriggerKeywordDetector,
        AutoPairProgrammingActivator,
        TriggerEvent,
        TRIGGER_KEYWORDS
    )
except ImportError:
    # TDDのRed Phase - モジュールが存在しないことを想定
    pass


class TestTriggerKeywordDetector(unittest.TestCase):
    """TriggerKeywordDetectorのテストケース"""
    
    def setUp(self):
        """テストセットアップ"""
        self.detector = TriggerKeywordDetector()
        
    def test_trigger_keywords_constant_exists(self):
        """トリガーキーワード定数が定義されている"""
        expected_keywords = ["解析", "修正", "実装", "開発", "テスト", "リファクタ", "デバッグ"]
        self.assertEqual(TRIGGER_KEYWORDS, expected_keywords)
        
    def test_detector_initialization(self):
        """検出器が正しく初期化される"""
        self.assertIsInstance(self.detector, TriggerKeywordDetector)
        self.assertEqual(self.detector.keywords, TRIGGER_KEYWORDS)
        self.assertTrue(self.detector.enabled)
        
    def test_scan_message_single_keyword(self):
        """単一キーワードを含むメッセージの検出"""
        message = "アレックス、ユーザー認証機能を実装してください"
        result = self.detector.scan_message(message)
        
        self.assertTrue(result.triggered)
        self.assertIn("実装", result.detected_keywords)
        self.assertEqual(len(result.detected_keywords), 1)
        self.assertEqual(result.message, message)
        
    def test_scan_message_multiple_keywords(self):
        """複数キーワードを含むメッセージの検出"""
        message = "バグを解析して修正後、テストも実装してほしい"
        result = self.detector.scan_message(message)
        
        self.assertTrue(result.triggered)
        expected_keywords = ["解析", "修正", "テスト", "実装"]
        for keyword in expected_keywords:
            self.assertIn(keyword, result.detected_keywords)
        self.assertEqual(len(result.detected_keywords), 4)
        
    def test_scan_message_no_keywords(self):
        """キーワードを含まないメッセージ"""
        message = "こんにちは、今日の天気はどうですか？"
        result = self.detector.scan_message(message)
        
        self.assertFalse(result.triggered)
        self.assertEqual(len(result.detected_keywords), 0)
        
    def test_scan_message_case_sensitive(self):
        """キーワードの大小文字区別"""
        message = "実装をお願いします"  # 大文字
        result = self.detector.scan_message(message)
        
        # 日本語なので大小文字は関係ないが、将来英語対応時の準備
        self.assertTrue(result.triggered)
        self.assertIn("実装", result.detected_keywords)
        
    def test_scan_message_partial_match(self):
        """部分一致での検出"""
        message = "実装作業を開始します"
        result = self.detector.scan_message(message)
        
        self.assertTrue(result.triggered)
        self.assertIn("実装", result.detected_keywords)
        
    def test_scan_message_disabled_detector(self):
        """無効化された検出器"""
        self.detector.enabled = False
        message = "実装してください"
        result = self.detector.scan_message(message)
        
        self.assertFalse(result.triggered)
        self.assertEqual(len(result.detected_keywords), 0)
        
    def test_trigger_event_creation(self):
        """TriggerEventオブジェクトの生成"""
        keywords = ["実装", "テスト"]
        message = "実装とテストをお願いします"
        
        event = TriggerEvent(
            triggered=True,
            detected_keywords=keywords,
            message=message,
            timestamp=datetime.now()
        )
        
        self.assertTrue(event.triggered)
        self.assertEqual(event.detected_keywords, keywords)
        self.assertEqual(event.message, message)
        self.assertIsInstance(event.timestamp, datetime)


class TestAutoPairProgrammingActivator(unittest.TestCase):
    """AutoPairProgrammingActivatorのテストケース"""
    
    def setUp(self):
        """テストセットアップ"""
        self.activator = AutoPairProgrammingActivator()
        
    @patch('trigger_keyword_detector.logger')
    def test_activate_pair_programming_success(self, mock_logger):
        """ペアプログラミングモード正常起動"""
        keywords = ["実装", "テスト"]
        message = "ユーザー認証の実装とテストをお願いします"
        
        result = self.activator.activate_pair_programming(keywords, message)
        
        self.assertTrue(result.success)
        self.assertIn("アレックス", result.response_message)
        self.assertIsNotNone(result.todo_list)
        
        # ログが記録されることを確認
        mock_logger.log_activity.assert_called()
        
    @patch('trigger_keyword_detector.logger')
    def test_activate_pair_programming_with_logging(self, mock_logger):
        """ログ記録付きペアプログラミング起動"""
        keywords = ["解析"]
        message = "コードの解析をしてください"
        
        self.activator.activate_pair_programming(keywords, message)
        
        # ActivityLoggerの呼び出しを確認
        mock_logger.log_cto.assert_called_once()
        mock_logger.log_alex.assert_called_once()
        
    def test_create_todo_from_keywords(self):
        """キーワードからTodoリスト生成"""
        keywords = ["実装", "テスト", "デバッグ"]
        message = "ユーザー管理機能の実装、テスト、デバッグを行う"
        
        todos = self.activator._create_todo_from_keywords(keywords, message)
        
        self.assertTrue(len(todos) >= 3)  # 最低限キーワード数分のタスク
        
        # 各キーワードに対応するタスクが存在することを確認
        todo_contents = [todo['content'] for todo in todos]
        self.assertTrue(any("実装" in content for content in todo_contents))
        self.assertTrue(any("テスト" in content for content in todo_contents))
        self.assertTrue(any("デバッグ" in content for content in todo_contents))
        
        # 最初のタスクがin_progressであることを確認
        self.assertEqual(todos[0]['status'], 'in_progress')
        
    def test_extract_feature_from_message(self):
        """メッセージから機能名抽出"""
        test_cases = [
            ("ユーザー認証機能を実装してください", "ユーザー認証機能"),
            ("データベース接続の修正をお願いします", "データベース接続"),
            ("解析システムの開発", "解析システム"),
            ("テストしてください", "指定機能")  # 機能名が不明な場合
        ]
        
        for message, expected_feature in test_cases:
            with self.subTest(message=message):
                feature = self.activator._extract_feature_from_message(message)
                self.assertIn(expected_feature, feature)


class TestTriggerSystemIntegration(unittest.TestCase):
    """トリガーシステム統合テスト"""
    
    def setUp(self):
        """統合テストセットアップ"""
        self.detector = TriggerKeywordDetector()
        self.activator = AutoPairProgrammingActivator()
        
    @patch('trigger_keyword_detector.logger')
    def test_full_trigger_workflow(self, mock_logger):
        """完全なトリガーワークフローテスト"""
        # 1. メッセージ受信
        user_message = "アレックス、ログイン機能の実装をお願いします"
        
        # 2. キーワード検出
        scan_result = self.detector.scan_message(user_message)
        self.assertTrue(scan_result.triggered)
        
        # 3. ペアプログラミング起動
        activation_result = self.activator.activate_pair_programming(
            scan_result.detected_keywords, 
            user_message
        )
        self.assertTrue(activation_result.success)
        
        # 4. フックシステム連携確認は統合テストでは省略
        # mock_hooks.execute_hooks.assert_called()
        
        # 5. ログ記録確認
        mock_logger.log_cto.assert_called()
        
    def test_no_trigger_workflow(self):
        """トリガーされない場合のワークフロー"""
        user_message = "今日の天気はいいですね"
        
        scan_result = self.detector.scan_message(user_message)
        self.assertFalse(scan_result.triggered)
        
        # トリガーされない場合は後続処理は実行されない
        
    @patch('trigger_keyword_detector.logger')
    def test_error_handling(self, mock_logger):
        """エラーハンドリングテスト"""
        # 無効なメッセージでのテスト
        with self.assertRaises(Exception):
            self.detector.scan_message(None)
            
        # ログにエラーが記録されることを確認
        mock_logger.error.assert_called()


class TestHooksIntegration(unittest.TestCase):
    """Hooksシステム統合テスト"""
    
    def test_hook_registration(self):
        """フック登録テスト（hooks.py側での統合を確認）"""
        # hooks.pyで統合されているかをテスト
        from hooks import hooks_manager, HookType
        
        # トリガー検出フックが登録されていることを確認
        pre_command_hooks = hooks_manager.hooks.get(HookType.PRE_COMMAND, [])
        hook_names = [hook.name for hook in pre_command_hooks]
        self.assertIn("trigger_keyword_detector", hook_names)


if __name__ == '__main__':
    unittest.main()