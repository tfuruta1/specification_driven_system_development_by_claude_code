#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude システム - リファクタリング済み統合システム
YAGNI, DRY, KISS, TDD原則適用
"""

from .core.core_system import CoreSystem, Status, Result

__version__ = "2.0.0"
__all__ = ["CoreSystem", "Status", "Result"]

# シンプルなファクトリ関数（KISS原則）
def create_system():
    """システムインスタンスを作成"""
    return CoreSystem()

# 便利なショートカット（DRY原則）
def organize():
    """ファイル整理を実行"""
    return create_system().organize_files()

def cleanup():
    """クリーンアップを実行"""
    return create_system().cleanup_temp()

def test():
    """テストを実行"""
    return create_system().run_tests()

def check():
    """コード品質チェックを実行"""
    return create_system().check_code_quality()

def status():
    """ステータス取得"""
    return create_system().get_status()