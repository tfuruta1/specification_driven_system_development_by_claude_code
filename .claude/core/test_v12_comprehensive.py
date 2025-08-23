#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v12.0システムの包括的テストスイート (モジュラー構造)
分割されたテストモジュールを統合して実行するメインテストランナー
"""

import unittest
import sys
from pathlib import Path

# テストモジュールのインポート
sys.path.insert(0, str(Path(__file__).parent))

from test_auto_mode_core import TestAutoModeConfig, TestAutoModeState, TestAutoMode
from test_file_logging import TestFileAccessLogger, TestColorTerminal, TestActivityLogger
from test_strategy_integration import (
    TestTestStrategy, 
    TestCircularImportDetector, 
    TestInitializationTester,
    TestComponentConnectivityTester,
    TestIntegrationTestRunner
)
from test_utilities_system import TestJSTUtils, TestSystemIntegration


class V12ComprehensiveTestSuite:
    """v12.0包括的テストスイート管理クラス"""
    
    def __init__(self):
        """テストスイートの初期化"""
        self.test_modules = [
            # Core Auto Mode Tests
            TestAutoModeConfig,
            TestAutoModeState, 
            TestAutoMode,
            
            # File & Logging Tests
            TestFileAccessLogger,
            TestColorTerminal,
            TestActivityLogger,
            
            # Test Strategy & Integration Tests
            TestTestStrategy,
            TestCircularImportDetector,
            TestInitializationTester,
            TestComponentConnectivityTester,
            TestIntegrationTestRunner,
            
            # Utility & System Tests
            TestJSTUtils,
            TestSystemIntegration
        ]
    
    def create_test_suite(self):
        """統合テストスイートの作成"""
        suite = unittest.TestSuite()
        
        for test_class in self.test_modules:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
            
        return suite
    
    def run_all_tests(self, verbosity=2):
        """全テストの実行"""
        print("=" * 80)
        print("v12.0システム包括的テスト実行開始")
        print("=" * 80)
        
        suite = self.create_test_suite()
        runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
        result = runner.run(suite)
        
        print("\n" + "=" * 80)
        print("テスト実行結果サマリー")
        print("=" * 80)
        print(f"実行テスト数: {result.testsRun}")
        print(f"失敗: {len(result.failures)}")
        print(f"エラー: {len(result.errors)}")
        print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        if result.failures:
            print("\n失敗したテスト:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('\\n')[-2]}")
                
        if result.errors:
            print("\nエラーが発生したテスト:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('\\n')[-2]}")
        
        return result.wasSuccessful()
    
    def run_module_tests(self, module_name):
        """特定モジュールのテスト実行"""
        module_map = {
            'auto_mode': [TestAutoModeConfig, TestAutoModeState, TestAutoMode],
            'logging': [TestFileAccessLogger, TestColorTerminal, TestActivityLogger],
            'strategy': [TestTestStrategy, TestCircularImportDetector, TestInitializationTester, 
                        TestComponentConnectivityTester, TestIntegrationTestRunner],
            'utilities': [TestJSTUtils, TestSystemIntegration]
        }
        
        if module_name not in module_map:
            print(f"不明なモジュール: {module_name}")
            print(f"利用可能: {list(module_map.keys())}")
            return False
            
        print(f"モジュール '{module_name}' のテスト実行")
        print("-" * 50)
        
        suite = unittest.TestSuite()
        for test_class in module_map[module_name]:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
            
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='v12.0システム包括的テスト')
    parser.add_argument('--module', '-m', choices=['auto_mode', 'logging', 'strategy', 'utilities'],
                       help='特定モジュールのテストのみ実行')
    parser.add_argument('--verbosity', '-v', type=int, default=2, choices=[0, 1, 2],
                       help='テスト出力の詳細レベル')
    
    args = parser.parse_args()
    
    test_suite = V12ComprehensiveTestSuite()
    
    if args.module:
        success = test_suite.run_module_tests(args.module)
    else:
        success = test_suite.run_all_tests(args.verbosity)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()