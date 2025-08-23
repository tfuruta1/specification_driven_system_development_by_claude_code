#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Command System (Modular Structure)
アレックス・ペアプログラミングモード自動化システム

シンプルで強力な/auto-modeコマンドシステムを提供：
- /auto-mode start - ペアプログラミングモード開始
- /auto-mode stop - ペアプログラミングモード終了  
- /auto-mode status - 現在の状態確認
"""

from typing import Dict, List, Optional, Any

# 分割されたモジュールをインポート
from .auto_mode_config import AutoModeConfig, auto_config
from .auto_mode_state import AutoModeState, auto_state
from .auto_mode_core import AutoMode, auto_mode, create_auto_mode

# 後方互換性のためのエクスポート
__all__ = [
    'AutoModeConfig',
    'AutoModeState', 
    'AutoMode',
    'auto_config',
    'auto_state',
    'auto_mode',
    'create_auto_mode'
]

# デモ実行
if __name__ == "__main__":
    print("=== Auto-Mode System v12.0 (Modular Structure) ===")
    
    # システム状態表示
    print(f"設定有効: {auto_config.is_enabled}")
    print(f"現在のモード: {auto_config.mode}")
    print(f"アクティブ: {auto_state.is_active}")
    
    # 利用可能フロー表示
    print("\n利用可能フロー:")
    for i, flow in enumerate(auto_config.flows, 1):
        marker = "✓" if flow == auto_config.current_flow else " "
        print(f"  {marker} {i}. {flow}")
    
    # 統合テスト設定表示
    integration_settings = auto_config.get_config_summary()["integration_tests"]
    print("\n統合テスト設定:")
    for key, value in integration_settings.items():
        status = "有効" if value else "無効" if isinstance(value, bool) else str(value)
        print(f"  {key}: {status}")
    
    # コマンドデモ
    print("\nコマンドデモ...")
    commands = ["status", "start", "status", "stop", "status"]
    
    for cmd in commands:
        print(f"\n> /auto-mode {cmd}")
        result = auto_mode.execute_command(cmd)
        print(f"結果: {result}")
    
    print("\n=== Demo Complete ===")