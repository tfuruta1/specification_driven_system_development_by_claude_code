#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileAccessLogger Quick Demo - Windows Compatible
"""

import sys
from pathlib import Path

# 現在のディレクトリをパスに追加
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from file_access_logger import (
    FileAccessLogger, 
    AccessPurpose,
    log_modify,
    log_reference, 
    log_analyze
)

def quick_demo():
    print("Claude Code - File Access Logger Quick Demo")
    print("CTO, システムが正常に動作しています！")
    print("="*60)
    
    # 基本的な使用例
    print("\n[TDD Red Phase] テスト作成:")
    log_modify("test/CheckSheetReview.test.js", "新機能のテスト作成")
    
    print("\n[TDD Green Phase] 実装:")
    log_modify("src/CheckSheetReview.vue", "テストを通す実装")
    log_reference("src/ExampleComponent.vue", "実装パターン確認")
    
    print("\n[解析・調査]:")
    log_analyze("src/services/DataService.js", "データフロー調査")
    
    # セッション概要
    print("\n" + "="*60)
    logger = FileAccessLogger()
    summary = logger.get_session_summary()
    
    print("セッション概要:")
    print(f"  総ファイル数: {summary['total_files']}")
    print(f"  修正対象: {summary['by_purpose'].get('MODIFY', 0)} 件")
    print(f"  参照のみ: {summary['by_purpose'].get('REFERENCE', 0)} 件")
    print(f"  解析中: {summary['by_purpose'].get('ANALYZE', 0)} 件")
    
    print("\n機能確認完了！システム準備完了です。")
    print("="*60)

if __name__ == "__main__":
    quick_demo()