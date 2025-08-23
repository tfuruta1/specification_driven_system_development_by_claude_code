#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
循環依存解決成功テスト
ServiceLocatorパターンによる循環依存の完全解決を確認
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_circular_dependency_resolution():
    """循環依存が解決されたことを確認"""
    print("=" * 60)
    print("循環依存解決テスト - ServiceLocatorパターン")
    print("=" * 60)
    
    success_count = 0
    total_tests = 5
    
    # テスト1: ServiceFactoryのインポート
    print("\n[Test 1] ServiceFactoryのインポート")
    try:
        from service_factory import ServiceFactory
        print("  [OK] ServiceFactoryのインポート成功")
        success_count += 1
    except ImportError as e:
        print(f"  [FAIL] インポート失敗: {e}")
    
    # テスト2: サービス初期化
    print("\n[Test 2] サービスの初期化")
    try:
        ServiceFactory.initialize_services()
        print("  [OK] サービス初期化成功")
        success_count += 1
    except Exception as e:
        print(f"  [FAIL] 初期化失敗: {e}")
    
    # テスト3: ConfigServiceの取得
    print("\n[Test 3] ConfigServiceの取得")
    try:
        config = ServiceFactory.get_config_service()
        print(f"  [OK] ConfigService取得成功")
        print(f"    - is_enabled: {config.is_enabled}")
        print(f"    - mode: {config.mode}")
        print(f"    - flows: {config.flows}")
        success_count += 1
    except Exception as e:
        print(f"  [FAIL] 取得失敗: {e}")
    
    # テスト4: StateServiceの取得
    print("\n[Test 4] StateServiceの取得")
    try:
        state = ServiceFactory.get_state_service()
        print(f"  [OK] StateService取得成功")
        print(f"    - is_active: {state.is_active}")
        print(f"    - session_count: {state.session_count}")
        success_count += 1
    except Exception as e:
        print(f"  [FAIL] 取得失敗: {e}")
    
    # テスト5: ServiceLocatorの動作確認
    print("\n[Test 5] ServiceLocatorの動作確認")
    try:
        from auto_mode_interfaces import ServiceLocator
        
        # ServiceLocatorから直接サービスを取得
        config_from_locator = ServiceLocator.get('config')
        state_from_locator = ServiceLocator.get('state')
        
        # 同一インスタンスかを確認
        if config_from_locator is config and state_from_locator is state:
            print("  [OK] ServiceLocatorが正しく動作")
            print("    - 同一インスタンスを返却")
            success_count += 1
        else:
            print("  [FAIL] インスタンスが異なる")
    except Exception as e:
        print(f"  [FAIL] ServiceLocator失敗: {e}")
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"成功: {success_count}/{total_tests}")
    print(f"成功率: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("\n[SUCCESS] 循環依存が完全に解決されました！")
        print("ServiceLocatorパターンによる依存関係管理が正常に機能しています。")
        return True
    else:
        print("\n[WARNING] 一部のテストが失敗しました。")
        return False

def main():
    """メイン実行"""
    print("循環依存解決確認プログラム")
    print("ServiceFactoryとServiceLocatorの動作検証\n")
    
    success = test_circular_dependency_resolution()
    
    print("\n" + "=" * 60)
    if success:
        print("[PASS] すべてのテストに合格しました！")
        print("循環依存問題は完全に解決されています。")
    else:
        print("[FAIL] テストに失敗しました。")
        print("追加の修正が必要です。")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())