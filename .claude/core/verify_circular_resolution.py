#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification Script: Circular Dependency Resolution
循環依存解決の検証スクリプト

実際のインポートとサービス生成が正常に動作するかを確認
"""

import sys
import traceback
from pathlib import Path

def verify_service_factory():
    """ServiceFactory検証"""
    print("=== ServiceFactory検証 ===")
    try:
        from service_factory import initialize_services, get_config_service, get_state_service
        
        print("✓ ServiceFactory インポート成功")
        
        # サービス初期化
        initialize_services()
        print("✓ サービス初期化成功")
        
        # サービス取得
        config = get_config_service()
        state = get_state_service()
        print("✓ サービス取得成功")
        
        # インターフェース確認
        from auto_mode_interfaces import ConfigInterface, StateInterface
        assert isinstance(config, ConfigInterface), "config is not ConfigInterface"
        assert isinstance(state, StateInterface), "state is not StateInterface"
        print("✓ インターフェース実装確認")
        
        return True
        
    except Exception as e:
        print(f"✗ ServiceFactory検証失敗: {e}")
        traceback.print_exc()
        return False

def verify_no_circular_imports():
    """循環インポート検証"""
    print("\n=== 循環インポート検証 ===")
    try:
        # 各モジュールを個別にインポート
        import auto_mode_interfaces
        print("[OK] auto_mode_interfaces import successful")
        
        import auto_mode_config
        print("[OK] auto_mode_config import successful")
        
        import auto_mode_state
        print("[OK] auto_mode_state import successful")
        
        import auto_mode_core
        print("[OK] auto_mode_core import successful")
        
        import service_factory
        print("[OK] service_factory import successful")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Circular import verification failed: {e}")
        traceback.print_exc()
        return False

def verify_singleton_removal():
    """シングルトン除去検証"""
    print("\n=== シングルトン除去検証 ===")
    try:
        # auto_configシングルトンが存在しないことを確認
        try:
            from auto_mode_config import auto_config
            print("✗ auto_config シングルトンが残存")
            return False
        except (ImportError, AttributeError):
            print("✓ auto_config シングルトン正常に除去")
        
        # auto_stateシングルトンが存在しないことを確認
        try:
            from auto_mode_state import auto_state
            print("✗ auto_state シングルトンが残存")
            return False
        except (ImportError, AttributeError):
            print("✓ auto_state シングルトン正常に除去")
        
        return True
        
    except Exception as e:
        print(f"✗ シングルトン除去検証失敗: {e}")
        traceback.print_exc()
        return False

def verify_delayed_import_removal():
    """遅延インポート除去検証"""
    print("\n=== 遅延インポート関数除去検証 ===")
    try:
        import auto_mode_core
        
        # _get_auto_config関数が存在しないことを確認
        assert not hasattr(auto_mode_core, '_get_auto_config'), "_get_auto_config が残存"
        print("✓ _get_auto_config 正常に除去")
        
        # _get_auto_state関数が存在しないことを確認
        assert not hasattr(auto_mode_core, '_get_auto_state'), "_get_auto_state が残存"
        print("✓ _get_auto_state 正常に除去")
        
        return True
        
    except Exception as e:
        print(f"✗ 遅延インポート除去検証失敗: {e}")
        traceback.print_exc()
        return False

def verify_auto_mode_creation():
    """AutoMode作成検証"""
    print("\n=== AutoMode作成検証 ===")
    try:
        from service_factory import initialize_services
        from auto_mode_core import create_auto_mode
        
        # サービス初期化
        initialize_services()
        print("✓ サービス初期化完了")
        
        # AutoMode作成
        auto_mode = create_auto_mode()
        print("✓ AutoMode作成成功")
        
        # 基本機能確認
        assert hasattr(auto_mode, 'config'), "configアトリビュートが存在しない"
        assert hasattr(auto_mode, 'state'), "stateアトリビュートが存在しない"
        print("✓ AutoMode基本機能確認")
        
        # コマンド実行テスト
        status = auto_mode.execute_command("status")
        assert isinstance(status, dict), "statusコマンドの戻り値が辞書でない"
        assert 'active' in status, "statusにactiveキーが存在しない"
        print("✓ コマンド実行テスト成功")
        
        return True
        
    except Exception as e:
        print(f"✗ AutoMode作成検証失敗: {e}")
        traceback.print_exc()
        return False

def main():
    """メイン検証実行"""
    print("循環依存解決検証開始...\n")
    
    results = []
    results.append(verify_no_circular_imports())
    results.append(verify_service_factory())
    results.append(verify_singleton_removal())
    results.append(verify_delayed_import_removal())
    results.append(verify_auto_mode_creation())
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n=== 検証結果 ===")
    print(f"成功: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 循環依存解決完了！")
        print("KISS・YAGNI原則に従いシンプルで効果的な解決策が実装されました。")
        return True
    else:
        print("❌ 循環依存解決に問題があります")
        return False

if __name__ == "__main__":
    main()