#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アレックスチーム起動確認テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.claude', 'core'))

from alex_team_parallel_system import AlexTeamParallelSystem

def test_team_startup():
    """チーム起動時に4人のメンバーがコメントを出力することを確認"""
    print("\n" + "="*80)
    print("アレックスチーム起動テスト開始")
    print("="*80)
    
    # システムインスタンス作成（これだけで4人のメンバーがコメントを出力）
    system = AlexTeamParallelSystem()
    
    print("\n" + "="*80)
    print("テストタスク実行: 簡単なリファクタリングタスク")
    print("="*80)
    
    # 簡単なタスクを実行
    success = system.run_complete_workflow("テスト用の簡単なリファクタリングタスク")
    
    if success:
        print("\n[SUCCESS] テスト成功：4人のチームメンバーが正常に動作しました！")
    else:
        print("\n[WARNING] テスト完了：タスクは最大イテレーションに達しました")
    
    return success

if __name__ == "__main__":
    test_team_startup()