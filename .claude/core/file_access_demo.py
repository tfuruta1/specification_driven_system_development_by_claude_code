#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileAccessLogger Standalone Demo
単体でのデモンストレーション（依存関係なし）
"""

import sys
from pathlib import Path
import os

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


def main_demo():
    """メインデモンストレーション"""
    
    print("Claude Code - File Access Logger Demo")
    print("CTO, ファイルアクセス目的表示システムのデモを開始します！\n")
    
    # ============================================
    # TDD ワークフローデモ  
    # ============================================
    print("="*60)
    print("TDD RED Phase - テスト作成")
    print("="*60)
    
    log_modify(
        "test/views/desktop/CheckSheetReview.test.js",
        "TDDレッドフェーズ - 失敗するテスト作成中"
    )
    
    log_reference(
        "test/views/desktop/DailyPlanSetting.test.js", 
        "テストパターン確認"
    )
    
    print("\n" + "="*60)
    print("TDD GREEN Phase - 実装")
    print("="*60)
    
    log_modify(
        "src/views/desktop/CheckSheetReview.vue",
        "TDDグリーンフェーズ - テストを通す実装中"
    )
    
    log_analyze(
        "src/components/desktop/ActionButtons.vue",
        "関連コンポーネントの仕様確認"
    )
    
    print("\n" + "="*60)
    print("TDD REFACTOR Phase - リファクタリング")
    print("="*60)
    
    log_modify(
        "src/views/desktop/CheckSheetReview.vue",
        "TDDリファクターフェーズ - コード品質向上"
    )
    
    # ============================================
    # バグ修正ワークフローデモ
    # ============================================
    print("\n" + "="*60)
    print("🐛 Bug Fix Workflow - バグ修正")
    print("="*60)
    
    print("\n🔍 調査フェーズ:")
    log_analyze(
        "src/views/desktop/DailyPlanSetting.vue",
        "スクロール問題の原因調査"
    )
    
    log_reference(
        "test/views/desktop/DailyPlanSetting.scroll.test.js",
        "既存テストの動作確認"
    )
    
    log_reference(
        "src/views/tablet/CheckSheet.vue", 
        "タブレット版のスクロール実装パターン確認"
    )
    
    print("\n🔧 修正フェーズ:")
    log_modify(
        "test/views/desktop/DailyPlanSetting.scroll.test.js",
        "スクロール問題のテストケース追加"
    )
    
    log_modify(
        "src/views/desktop/DailyPlanSetting.vue",
        "スクロール問題の修正実装"
    )
    
    # ============================================
    # 新機能開発デモ
    # ============================================
    print("\n" + "="*60)
    print("⭐ Feature Development - 新機能開発")
    print("="*60)
    
    print("\n📋 要件分析フェーズ:")
    log_reference(
        "src/views/desktop/CheckSheetReview.vue",
        "レビュー機能のUI/UXパターン確認"
    )
    
    log_reference(
        "src/stores/checksheet.js",
        "既存の状態管理パターン確認"
    )
    
    print("\n🎨 設計・実装フェーズ:")
    log_modify(
        "test/features/daily-plan-review.test.js",
        "日次レビュー機能のテスト設計"
    )
    
    log_modify(
        "src/components/desktop/DailyPlanReview.vue", 
        "日次レビューコンポーネント実装"
    )
    
    log_modify(
        "src/stores/dailyPlan.js",
        "日次計画ストアの実装（現在未実装機能）"
    )
    
    log_modify(
        "src/router/index.js",
        "日次レビュー画面のルート追加"
    )
    
    # ============================================
    # 使用方法の例
    # ============================================
    print("\n" + "="*60)
    print("📚 Usage Examples - 使用方法の例")
    print("="*60)
    
    print("\n# 便利関数を使った簡単な記録:")
    print("log_modify('MyComponent.vue', '新機能実装中')")
    print("log_reference('api.md', 'API仕様確認')")  
    print("log_analyze('helpers.js', 'ヘルパー関数調査')")
    
    print("\n実際の出力:")
    log_modify('src/components/MyComponent.vue', '新機能実装中')
    log_reference('docs/api.md', 'API仕様確認')
    log_analyze('src/utils/helpers.js', 'ヘルパー関数調査')
    
    # ============================================
    # 色分け確認
    # ============================================
    print("\n" + "="*60)
    print("🌈 Color Coding - 色分けの確認")
    print("="*60)
    
    print("\n各目的の色分けを確認:")
    logger = FileAccessLogger()
    
    print("🔴 修正対象 (赤色):")
    logger.log_file_access("example1.vue", AccessPurpose.MODIFY, "実装中")
    
    print("🔵 参照のみ (青色):")
    logger.log_file_access("example2.vue", AccessPurpose.REFERENCE, "パターン確認")
    
    print("🟡 解析中 (黄色):")
    logger.log_file_access("example3.vue", AccessPurpose.ANALYZE, "仕様調査")
    
    # ============================================
    # セッション概要
    # ============================================
    print("\n" + "="*60)
    print("📊 Session Summary - セッション概要")
    print("="*60)
    
    logger.print_session_summary()
    
    # ============================================
    # ログファイル確認
    # ============================================
    print("\n" + "="*60)
    print("📁 Log Files - 作成されたログファイル")
    print("="*60)
    
    log_dir = Path(".claude/logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*file_access*"))
        if log_files:
            print(f"\nログディレクトリ: {log_dir}")
            for log_file in log_files:
                size = log_file.stat().st_size
                mtime = log_file.stat().st_mtime
                print(f"  📄 {log_file.name} ({size} bytes)")
                
                # ログファイルの中身を少し表示
                if size < 2000:  # 小さいファイルのみ
                    print("     内容の一部:")
                    try:
                        content = log_file.read_text(encoding='utf-8')
                        lines = content.split('\n')[:3]  # 最初の3行のみ
                        for line in lines:
                            if line.strip():
                                print(f"     {line}")
                    except:
                        print("     (読み込みエラー)")
                print()
        else:
            print("ファイルアクセスログがまだ作成されていません")
    else:
        print("ログディレクトリが存在しません")
    
    # ============================================
    # 完了メッセージ
    # ============================================
    print("\n" + "="*60)
    print("🎉 Demo Complete!")
    print("="*60)
    print("CTO, ファイルアクセス目的表示システムが正常に動作しています！")
    print("以下の機能が利用可能になりました:")
    print("• ターミナルでの色分け表示")
    print("• ファイルアクセス目的の明確化")
    print("• セッションログの自動記録")
    print("• 既存システムとの統合")
    print("• TDDワークフローサポート")
    print("="*60)


if __name__ == "__main__":
    main_demo()