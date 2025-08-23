#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新規開発フローテスト - Claude Code Core v12.0
新規開発フローの包括的なテスト
"""

import unittest
from unittest.mock import patch
from pathlib import Path
from test_base import BaseTestFlow
from file_access_logger import AccessPurpose
from test_strategy import TestLevel, TestResult

class TestNewDevelopmentFlow(BaseTestFlow):
    """新規開発フローのテスト"""
    
    @patch('builtins.input', return_value='1')
    def test_new_development_flow(self, mock_input):
        """新規開発フローのテスト"""
        print("\n=== 新規開発フローテスト ===")
        
        # 1. AutoMode開始（新規開発を選択）
        session_id = self.start_session_with_flow('1')
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
        unit_result, integration_result = self.create_test_results(
            unit_passed=True, integration_passed=True
        )
        
        self.assertTrue(self.test_strategy.is_all_passed())
        print(f"[OK] テスト全合格")
        
        # 6. ActivityReport確認
        self.verify_activity_report(session_id)
        print(f"[OK] ActivityReport作成")
        
        # 7. セッション終了
        self.stop_session()
        print(f"[OK] セッション終了")
    
    @patch('builtins.input', return_value='1')
    def test_new_development_with_tdd_cycle(self, mock_input):
        """新規開発でのTDDサイクルテスト"""
        print("\n=== 新規開発 TDDサイクルテスト ===")
        
        session_id = self.start_session_with_flow('1')
        
        # TDDサイクル: Red -> Green -> Refactor を3回実行
        for cycle in range(1, 4):
            print(f"\nTDDサイクル {cycle}:")
            
            # Red: テスト作成
            self.file_logger.log_file_access(
                f"test_feature_{cycle}.py", 
                AccessPurpose.MODIFY, 
                f"TDD Red: テスト{cycle}作成"
            )
            print(f"  [OK] Red: テスト{cycle}作成")
            
            # Green: 実装
            self.file_logger.log_file_access(
                f"feature_{cycle}.py", 
                AccessPurpose.MODIFY, 
                f"TDD Green: 機能{cycle}実装"
            )
            print(f"  [OK] Green: 機能{cycle}実装")
            
            # Refactor: リファクタリング
            self.file_logger.log_file_access(
                f"feature_{cycle}.py", 
                AccessPurpose.MODIFY, 
                f"TDD Refactor: リファクタリング{cycle}"
            )
            print(f"  [OK] Refactor: リファクタリング{cycle}")
        
        # 最終的なテスト実行
        self.create_test_results(unit_passed=True, integration_passed=True)
        self.assertTrue(self.test_strategy.is_all_passed())
        print("[OK] 全TDDサイクル完了・テスト合格")
        
        self.stop_session()
    
    @patch('builtins.input', return_value='1')
    def test_new_development_documentation_flow(self, mock_input):
        """新規開発でのドキュメント作成フロー"""
        print("\n=== 新規開発 ドキュメントフローテスト ===")
        
        session_id = self.start_session_with_flow('1')
        
        # ドキュメント作成順序
        docs = [
            ("requirements.md", "要件定義書"),
            ("architecture.md", "システム設計書"),
            ("api_spec.md", "API仕様書"),
            ("database_design.md", "データベース設計書"),
            ("deployment.md", "デプロイメント設計書"),
            ("user_manual.md", "ユーザーマニュアル")
        ]
        
        for filename, description in docs:
            self.file_logger.log_file_access(
                filename, 
                AccessPurpose.MODIFY, 
                f"新規開発: {description}作成"
            )
            print(f"[OK] {description}作成")
        
        # ドキュメントレビュー
        for filename, description in docs:
            self.file_logger.log_file_access(
                filename, 
                AccessPurpose.REFERENCE, 
                f"新規開発: {description}レビュー"
            )
        
        print("[OK] 全ドキュメント作成・レビュー完了")
        
        # ドキュメントアクセス数確認
        doc_modify_count = sum(1 for h in self.file_logger.access_history 
                              if h['purpose'] == AccessPurpose.MODIFY and h['file_path'].endswith('.md'))
        self.assertEqual(doc_modify_count, len(docs))
        
        self.stop_session()

if __name__ == '__main__':
    unittest.main()