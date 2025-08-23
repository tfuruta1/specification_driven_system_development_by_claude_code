#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Import Test
分割後のモジュールのインポートテスト
"""

import sys
from pathlib import Path

# テスト結果を保存
test_results = []

def test_import(module_name, description):
    """インポートテスト実行"""
    try:
        __import__(module_name)
        test_results.append(f"✓ {description}: OK")
        return True
    except ImportError as e:
        test_results.append(f"✗ {description}: {e}")
        return False
    except Exception as e:
        test_results.append(f"⚠ {description}: 予期しないエラー - {e}")
        return False

def run_import_tests():
    """全インポートテストの実行"""
    print("=== Module Import Test ===")
    
    # 基本ユーティリティモジュール
    test_import('activity_logger', 'Activity Logger')
    test_import('jst_utils', 'JST Utilities')
    test_import('config', 'Configuration')
    test_import('logger', 'Logger')
    
    # Development Rulesモジュール
    test_import('dev_rules_core', 'Dev Rules Core')
    test_import('dev_rules_checklist', 'Dev Rules Checklist')
    test_import('dev_rules_tdd', 'Dev Rules TDD')
    test_import('dev_rules_tasks', 'Dev Rules Tasks')
    test_import('dev_rules_integration', 'Dev Rules Integration')
    test_import('development_rules', 'Development Rules (Main)')
    
    # Auto Modeモジュール
    test_import('auto_mode_config', 'Auto Mode Config')
    test_import('auto_mode_state', 'Auto Mode State')
    test_import('auto_mode_core', 'Auto Mode Core')
    test_import('auto_mode', 'Auto Mode (Main)')
    
    # テストモジュール
    test_import('test_auto_mode_core', 'Test Auto Mode Core')
    test_import('test_file_logging', 'Test File Logging')
    test_import('test_strategy_integration', 'Test Strategy Integration')
    test_import('test_utilities_system', 'Test Utilities System')
    test_import('test_v12_comprehensive', 'Test v12 Comprehensive (Main)')
    
    # 結果表示
    print("\n=== Test Results ===")
    for result in test_results:
        print(result)
    
    # サマリー
    success_count = len([r for r in test_results if r.startswith('✓')])
    warning_count = len([r for r in test_results if r.startswith('⚠')])
    error_count = len([r for r in test_results if r.startswith('✗')])
    total_count = len(test_results)
    
    print(f"\n=== Summary ===")
    print(f"総テスト数: {total_count}")
    print(f"成功: {success_count}")
    print(f"警告: {warning_count}")
    print(f"エラー: {error_count}")
    print(f"成功率: {(success_count/total_count*100):.1f}%")
    
    return error_count == 0

if __name__ == '__main__':
    # カレントディレクトリをPythonパスに追加
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    success = run_import_tests()
    sys.exit(0 if success else 1)