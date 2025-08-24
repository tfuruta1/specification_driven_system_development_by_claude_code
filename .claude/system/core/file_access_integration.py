#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileAccessLogger Integration Examples
既存システムとの統合例と使用方法
"""

import sys
from pathlib import Path
from file_access_logger import (
    FileAccessLogger, 
    AccessPurpose,
    log_modify,
    log_reference, 
    log_analyze
)
from activity_logger import logger as activity_logger
from pair_programmer import PairProgrammer


class IntegratedWorkflowDemo:
    """統合ワークフローのデモンストレーション"""
    
    def __init__(self):
        self.file_logger = FileAccessLogger()
        self.alex = PairProgrammer("アレックス")
        print("CTO! ファイルアクセス目的表示システムの統合が完了しました！")
    
    def demonstrate_tdd_workflow(self):
        """TDDワークフローでのファイルアクセスログデモ"""
        print("\n" + "="*60)
        print("TDD ワークフロー with File Access Logger")
        print("="*60)
        
        # Phase 1: RED - テスト作成
        print("\n🔴 RED Phase: テスト作成中...")
        
        # テストファイルにアクセス（修正対象）
        log_modify(
            "test/views/desktop/CheckSheetReview.test.js",
            "TDDレッドフェーズ - 失敗するテスト作成中"
        )
        
        # 既存テストファイルを参照
        log_reference(
            "test/views/desktop/DailyPlanSetting.test.js", 
            "テストパターン確認"
        )
        
        activity_logger.log_alex(
            "CheckSheetReviewコンポーネントのテストを作成しています",
            "TDDのRED phaseに入りました。先にテストを書いてから実装に進みます"
        )
        
        # Phase 2: GREEN - 実装
        print("\n🟢 GREEN Phase: 実装中...")
        
        # 実装対象ファイル（修正対象）
        log_modify(
            "src/views/desktop/CheckSheetReview.vue",
            "TDDグリーンフェーズ - テストを通す実装中"
        )
        
        # 関連コンポーネントの解析
        log_analyze(
            "src/components/desktop/ActionButtons.vue",
            "関連コンポーネントの仕様確認"
        )
        
        # Phase 3: REFACTOR - リファクタリング
        print("\n🔵 REFACTOR Phase: リファクタリング中...")
        
        log_modify(
            "src/views/desktop/CheckSheetReview.vue",
            "TDDリファクターフェーズ - コード品質向上"
        )
        
        print(self.alex.celebrate("test_pass"))
    
    def demonstrate_bug_fix_workflow(self):
        """バグ修正ワークフローでのファイルアクセスログデモ"""
        print("\n" + "="*60) 
        print("Bug Fix ワークフロー with File Access Logger")
        print("="*60)
        
        # バグ調査フェーズ
        print("\n🔍 調査フェーズ...")
        
        # 問題のあるファイルを解析
        log_analyze(
            "src/views/desktop/DailyPlanSetting.vue",
            "スクロール問題の原因調査"
        )
        
        # 関連するテストファイルを確認
        log_reference(
            "test/views/desktop/DailyPlanSetting.scroll.test.js",
            "既存テストの動作確認"
        )
        
        # 類似コンポーネントを参照
        log_reference(
            "src/views/tablet/CheckSheet.vue", 
            "タブレット版のスクロール実装パターン確認"
        )
        
        # 修正フェーズ
        print("\n🔧 修正フェーズ...")
        
        # テストを先に修正/追加
        log_modify(
            "test/views/desktop/DailyPlanSetting.scroll.test.js",
            "スクロール問題のテストケース追加"
        )
        
        # 実装を修正
        log_modify(
            "src/views/desktop/DailyPlanSetting.vue",
            "スクロール問題の修正実装"
        )
        
        activity_logger.log_alex(
            "DailyPlanSettingのスクロール問題を修正しました",
            "TDDアプローチでテストを先に書いてから修正。完璧です！"
        )
        
        print(self.alex.celebrate("bug_fix"))
    
    def demonstrate_feature_development(self):
        """新機能開発でのファイルアクセスログデモ"""
        print("\n" + "="*60)
        print("Feature Development ワークフロー with File Access Logger") 
        print("="*60)
        
        # 要件分析フェーズ
        print("\n📋 要件分析フェーズ...")
        
        # 既存の類似機能を参照
        log_reference(
            "src/views/desktop/CheckSheetReview.vue",
            "レビュー機能のUI/UXパターン確認"
        )
        
        log_reference(
            "src/stores/checksheet.js",
            "既存の状態管理パターン確認"
        )
        
        # 設計フェーズ
        print("\n🎨 設計フェーズ...")
        
        # 新機能のテストを設計
        log_modify(
            "test/features/daily-plan-review.test.js",
            "日次レビュー機能のテスト設計"
        )
        
        # 実装フェーズ
        print("\n⚙️ 実装フェーズ...")
        
        # 新しいコンポーネントを作成
        log_modify(
            "src/components/desktop/DailyPlanReview.vue", 
            "日次レビューコンポーネント実装"
        )
        
        # ストアを拡張
        log_modify(
            "src/stores/dailyPlan.js",
            "日次計画ストアの実装（現在未実装機能）"
        )
        
        # ルーティングを追加
        log_modify(
            "src/router/index.js",
            "日次レビュー画面のルート追加"
        )
        
        activity_logger.log_alex(
            "日次レビュー機能の実装を完了しました",
            "TDDでテストファーストアプローチを貫徹。素晴らしい開発体験でした！"
        )
        
        print(self.alex.celebrate("feature_complete"))
    
    def show_session_summary(self):
        """セッション概要の表示"""
        print("\n" + "="*60)
        print("セッション概要")
        print("="*60)
        
        self.file_logger.print_session_summary()


def quick_usage_examples():
    """クイック使用例"""
    print("\n" + "="*60)
    print("クイック使用例 - よく使うパターン")
    print("="*60)
    
    # 便利関数の使用例
    print("\n# 便利関数での使用:")
    print("log_modify('src/components/MyComponent.vue', '新機能実装中')")
    log_modify('src/components/MyComponent.vue', '新機能実装中')
    
    print("\nlog_reference('docs/api.md', 'API仕様確認')")
    log_reference('docs/api.md', 'API仕様確認')
    
    print("\nlog_analyze('src/utils/helpers.js', 'ヘルパー関数調査')")
    log_analyze('src/utils/helpers.js', 'ヘルパー関数調査')
    
    # 直接使用例
    print("\n# 直接使用:")
    logger = FileAccessLogger()
    logger.log_file_access(
        "src/services/dataAccess/DataAccessService.js",
        AccessPurpose.ANALYZE,
        "データアクセス層のアーキテクチャ理解"
    )


def integration_with_existing_systems():
    """既存システムとの統合デモ"""
    print("\n" + "="*60)
    print("既存システム統合デモ")
    print("="*60)
    
    # ActivityLoggerとの連携
    print("\n📝 ActivityLogger連携:")
    activity_logger.log_cto(
        "ファイルアクセス目的表示システムの導入を決定",
        "開発作業の意図がより明確になり、ペアプログラミングの効率が向上する"
    )
    
    # PairProgrammerとの連携
    print("\n👥 PairProgrammer連携:")
    alex = PairProgrammer("アレックス", "friendly")
    print(alex.greet())
    print(alex.suggest_next("ファイルアクセスログの確認"))
    
    # 統合ワークフロー
    file_logger = FileAccessLogger()
    
    # ファイルにアクセスしながらペアプログラミング
    log_modify("src/main.js", "アプリケーション初期化の改善")
    print(alex.think_aloud("// アプリケーション初期化の改善中..."))
    
    log_reference("src/App.vue", "既存の初期化パターン確認") 
    print(alex.review_code("// 既存パターンを参考にした実装"))


def show_log_files():
    """作成されたログファイルの確認"""
    print("\n" + "="*60)
    print("作成されたログファイル")
    print("="*60)
    
    log_dir = Path(".claude/temp/logs")
    
    if log_dir.exists():
        log_files = list(log_dir.glob("*file_access*"))
        if log_files:
            print(f"\n📁 ログディレクトリ: {log_dir}")
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"  📄 {log_file.name} ({size} bytes)")
        else:
            print("ログファイルがまだ作成されていません")
    else:
        print("ログディレクトリが存在しません")


if __name__ == "__main__":
    """メイン実行 - 全機能のデモンストレーション"""
    
    print("🚀 Claude Code - File Access Logger Integration Demo")
    print("CTO, ファイルアクセス目的表示システムの統合デモを開始します！\n")
    
    # 統合ワークフローデモ
    demo = IntegratedWorkflowDemo()
    
    # 各ワークフローのデモ
    demo.demonstrate_tdd_workflow()
    demo.demonstrate_bug_fix_workflow() 
    demo.demonstrate_feature_development()
    
    # 使用例
    quick_usage_examples()
    
    # 既存システム統合
    integration_with_existing_systems()
    
    # セッション概要
    demo.show_session_summary()
    
    # ログファイル確認
    show_log_files()
    
    print("\n" + "="*60)
    print("🎉 デモ完了！")
    print("CTO, ファイルアクセス目的表示システムの準備が整いました！")
    print("="*60)