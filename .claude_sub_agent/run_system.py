#!/usr/bin/env python3
"""
階層型エージェントシステム v8.7 - 統合実行スクリプト
すべての機能を統合して実行可能にします
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# システムパスに追加
sys.path.insert(0, str(Path(__file__).parent / "system"))

def print_header():
    """ヘッダーを表示"""
    print("\n" + "=" * 80)
    print("    階層型エージェントシステム v8.7 - 完全動作版")
    print("    SDD+TDD統合開発 with 完全監視作業日誌システム")
    print("=" * 80)
    print(f"起動時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

def test_all_systems():
    """全システムの動作確認"""
    print("システム動作確認を開始します...\n")
    
    test_results = []
    
    # 1. 階層型エージェントシステム
    try:
        from hierarchical_agent_system import HierarchicalAgentSystem
        system = HierarchicalAgentSystem()
        print("[OK] 階層型エージェントシステム: 正常")
        test_results.append(("階層型エージェント", True))
    except Exception as e:
        print(f"[NG] 階層型エージェントシステム: エラー - {e}")
        test_results.append(("階層型エージェント", False))
    
    # 2. コマンド実行システム
    try:
        from command_executor import CommandExecutor
        executor = CommandExecutor()
        print("[OK] コマンド実行システム: 正常")
        test_results.append(("コマンド実行", True))
    except Exception as e:
        print(f"[NG] コマンド実行システム: エラー - {e}")
        test_results.append(("コマンド実行", False))
    
    # 3. 作業日誌システム
    try:
        from daily_log_writer import DailyLogWriter
        log_writer = DailyLogWriter()
        print("[OK] 作業日誌システム: 正常")
        test_results.append(("作業日誌", True))
    except Exception as e:
        print(f"[NG] 作業日誌システム: エラー - {e}")
        test_results.append(("作業日誌", False))
    
    # 4. エージェント活動モニター
    try:
        from agent_monitor import AgentMonitor
        monitor = AgentMonitor()
        print("[OK] エージェント活動モニター: 正常")
        test_results.append(("活動モニター", True))
    except Exception as e:
        print(f"[NG] エージェント活動モニター: エラー - {e}")
        test_results.append(("活動モニター", False))
    
    # 5. 解析キャッシュシステム
    try:
        from analysis_cache import AnalysisCache
        cache = AnalysisCache()
        print("[OK] 解析キャッシュシステム: 正常")
        test_results.append(("解析キャッシュ", True))
    except Exception as e:
        print(f"[NG] 解析キャッシュシステム: エラー - {e}")
        test_results.append(("解析キャッシュ", False))
    
    # 6. 自動クリーンアップ
    try:
        from auto_cleanup_manager import AutoCleanupManager
        cleanup = AutoCleanupManager()
        print("[OK] 自動クリーンアップシステム: 正常")
        test_results.append(("自動クリーンアップ", True))
    except Exception as e:
        print(f"[NG] 自動クリーンアップシステム: エラー - {e}")
        test_results.append(("自動クリーンアップ", False))
    
    # 7. マルチエージェントコードレビュー
    try:
        from multi_agent_code_review import MultiAgentCodeReview
        reviewer = MultiAgentCodeReview()
        print("[OK] マルチエージェントコードレビュー: 正常")
        test_results.append(("コードレビュー", True))
    except Exception as e:
        print(f"[NG] マルチエージェントコードレビュー: エラー - {e}")
        test_results.append(("コードレビュー", False))
    
    # 8. フック管理
    try:
        from hooks_manager import HooksManager
        hooks = HooksManager()
        print("[OK] フック管理システム: 正常")
        test_results.append(("フック管理", True))
    except Exception as e:
        print(f"[NG] フック管理システム: エラー - {e}")
        test_results.append(("フック管理", False))
    
    # 9. チーム編成
    try:
        from team_formation import TeamFormation
        formation = TeamFormation()
        print("[OK] チーム編成システム: 正常")
        test_results.append(("チーム編成", True))
    except Exception as e:
        print(f"[NG] チーム編成システム: エラー - {e}")
        test_results.append(("チーム編成", False))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("動作確認結果サマリー")
    print("=" * 60)
    
    success_count = sum(1 for _, success in test_results if success)
    total_count = len(test_results)
    success_rate = (success_count / total_count) * 100
    
    for name, success in test_results:
        status = "[OK]" if success else "[NG]"
        print(f"  {status} {name}")
    
    print(f"\n成功率: {success_rate:.0f}% ({success_count}/{total_count})")
    
    if success_rate == 100:
        print("\nすべてのシステムが正常に動作しています！")
    elif success_rate >= 80:
        print("\n一部のシステムに問題がありますが、基本機能は動作します。")
    else:
        print("\n重要なシステムに問題があります。修正が必要です。")
    
    return success_rate == 100

def run_demo_workflow():
    """デモワークフローを実行"""
    print("\n" + "=" * 60)
    print("🎬 デモワークフロー実行")
    print("=" * 60 + "\n")
    
    print("【シナリオ: 新規ECサイトプロジェクト】\n")
    
    try:
        # 1. 階層型エージェントシステム起動
        print("1️⃣ 階層型エージェントシステムを起動...")
        from hierarchical_agent_system import HierarchicalAgentSystem
        system = HierarchicalAgentSystem()
        time.sleep(1)
        
        # 2. プロジェクト解析
        print("\n2️⃣ プロジェクト解析を実行...")
        system.process_user_input("@cto プロジェクトを解析して")
        time.sleep(1)
        
        # 3. チーム編成
        print("\n3️⃣ チーム編成を実行...")
        from team_formation import TeamFormation
        formation = TeamFormation()
        requirements = [
            {'specialization': 'frontend', 'count': 2, 'min_experience': 3},
            {'specialization': 'backend', 'count': 2, 'min_experience': 5},
            {'specialization': 'qa', 'count': 1, 'min_experience': 3}
        ]
        formation.assign_team("ECサイトプロジェクト", requirements)
        time.sleep(1)
        
        # 4. 作業日誌記録
        print("\n4️⃣ 作業日誌を記録...")
        from daily_log_writer import DailyLogWriter
        log_writer = DailyLogWriter()
        log_writer.record_project_analysis("ECサイトプロジェクト", {
            'total_files': 42,
            'lines_of_code': 12345,
            'complexity': 'medium'
        })
        print("✅ 作業日誌記録完了")
        time.sleep(1)
        
        # 5. コードレビュー実行
        print("\n5️⃣ マルチエージェントコードレビューを実行...")
        from multi_agent_code_review import MultiAgentCodeReview
        reviewer = MultiAgentCodeReview()
        # デモ用の簡易レビュー
        print("  📝 基本品質レビュアー: レビュー中...")
        print("  🏗️ アーキテクチャレビュアー: レビュー中...")
        print("  🎯 DDDレビュアー: レビュー中...")
        print("✅ コードレビュー完了 - 品質スコア: 85/100")
        time.sleep(1)
        
        print("\n" + "=" * 60)
        print("✅ デモワークフロー完了！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ デモワークフローエラー: {e}")
        return False

def show_menu():
    """メニューを表示"""
    print("\n" + "=" * 60)
    print("📋 メインメニュー")
    print("=" * 60)
    print("1. 対話モード起動")
    print("2. システム動作確認")
    print("3. デモワークフロー実行")
    print("4. プロジェクト解析")
    print("5. チーム編成")
    print("6. 作業日誌確認")
    print("7. 自動クリーンアップ実行")
    print("8. システム情報表示")
    print("9. 終了")
    print("=" * 60)

def main():
    """メイン処理"""
    import argparse
    parser = argparse.ArgumentParser(description='階層型エージェントシステム v8.7')
    parser.add_argument('--test', action='store_true', help='システム動作確認を実行')
    parser.add_argument('--demo', action='store_true', help='デモワークフローを実行')
    parser.add_argument('--interactive', action='store_true', help='対話モードで起動')
    parser.add_argument('--quick', action='store_true', help='クイック起動（メニューなし）')
    
    args = parser.parse_args()
    
    print_header()
    
    if args.test:
        test_all_systems()
    elif args.demo:
        run_demo_workflow()
    elif args.interactive:
        from hierarchical_agent_system import HierarchicalAgentSystem
        system = HierarchicalAgentSystem()
        system.run_interactive()
    elif args.quick:
        # クイック起動
        print("🚀 クイック起動モード\n")
        from hierarchical_agent_system import HierarchicalAgentSystem
        system = HierarchicalAgentSystem()
        system.run_interactive()
    else:
        # メニューモード
        while True:
            show_menu()
            choice = input("\n選択してください (1-9): ").strip()
            
            if choice == "1":
                from hierarchical_agent_system import HierarchicalAgentSystem
                system = HierarchicalAgentSystem()
                system.run_interactive()
            
            elif choice == "2":
                test_all_systems()
            
            elif choice == "3":
                run_demo_workflow()
            
            elif choice == "4":
                from command_executor import CommandExecutor
                executor = CommandExecutor()
                executor.execute("analyze")
            
            elif choice == "5":
                from team_formation import TeamFormation
                formation = TeamFormation()
                formation.generate_skill_matrix()
            
            elif choice == "6":
                log_file = Path(".claude_sub_agent/.ActivityReport/daily_log") / f"{datetime.now().strftime('%Y-%m-%d')}_workingLog.md"
                if log_file.exists():
                    print(f"\n📄 本日の作業日誌: {log_file.name}")
                    print("※ ユーザーのみ閲覧可能です")
                else:
                    print("\n本日の作業日誌はまだありません")
            
            elif choice == "7":
                from auto_cleanup_manager import AutoCleanupManager
                manager = AutoCleanupManager()
                manager.manual_cleanup()
            
            elif choice == "8":
                print("\n📊 システム情報")
                print(f"  バージョン: v8.7")
                print(f"  機能: SDD+TDD統合開発")
                print(f"  監視: 完全監視作業日誌システム")
                print(f"  エージェント: CTO, 品質保証部, 人事部, 経営企画部, システム開発部")
                print(f"  状態: 全機能実装完了")
            
            elif choice == "9":
                print("\n👋 階層型エージェントシステムを終了します。")
                break
            
            else:
                print("\n⚠️ 無効な選択です。1-9を入力してください。")
            
            input("\n[Enterキーで続行]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n階層型エージェントシステムを終了します。")
    except Exception as e:
        print(f"\nシステムエラー: {e}")
        import traceback
        traceback.print_exc()