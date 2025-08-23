#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v12.0 開発フロー統合テストスイート
分割されたテストモジュールを統合実行するメインインターフェース
"""

import unittest
import sys
from pathlib import Path

# テストモジュールのインポート
sys.path.insert(0, str(Path(__file__).parent))

from test_new_development import TestNewDevelopmentFlow
from test_existing_analysis import TestExistingAnalysisFlow
from test_bug_fix_flow import TestBugFixFlow
from test_refactoring_flow import TestRefactoringFlow
from test_flow_integration import TestFlowIntegration

def create_test_suite():
    """統合テストスイートの作成"""
    suite = unittest.TestSuite()
    
    # 新規開発フローテスト
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNewDevelopmentFlow))
    
    # 既存解析フローテスト
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestExistingAnalysisFlow))
    
    # バグ修正フローテスト
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBugFixFlow))
    
    # リファクタリングフローテスト
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestRefactoringFlow))
    
    # フロー統合テスト
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFlowIntegration))
    
    return suite

def run_all_flow_tests():
    """すべての開発フローテストを実行"""
    print("=== v12.0 開発フロー統合テスト開始 ===")
    
    # 統合テストスイートの作成
    suite = create_test_suite()
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # 結果サマリー
    print("\n" + "="*70)
    print("[開発フロー統合テスト結果]")
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
        print("  ✓ フロー統合機能（切り替え・並行処理・横断テスト）")
        
        print("\n分割されたテストモジュール:")
        print("  - test_new_development.py: 新規開発フローテスト")
        print("  - test_existing_analysis.py: 既存解析フローテスト")
        print("  - test_bug_fix_flow.py: バグ修正フローテスト")
        print("  - test_refactoring_flow.py: リファクタリングフローテスト")
        print("  - test_flow_integration.py: フロー統合テスト")
        print("  - test_base.py: 共通ベースクラス")
    else:
        print("\n[NG] 一部のテストが失敗しています。")
        
        if result.failures:
            print("\n[失敗したテスト]")
            for test, traceback in result.failures:
                print(f"  - {test}")
                
        if result.errors:
            print("\n[エラーが発生したテスト]")
            for test, traceback in result.errors:
                print(f"  - {test}")
        
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_flow_tests()
    sys.exit(0 if success else 1)