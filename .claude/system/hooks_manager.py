#!/usr/bin/env python3
"""
階層型エージェントシステム - フック管理システム
コマンド実行前後に自動的に処理を実行
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from enum import Enum
import threading
from jst_config import format_jst_datetime, format_jst_time

class HookType(Enum):
    """フックの種類"""
    PRE_COMMAND = "pre_command"      # コマンド実行前
    POST_COMMAND = "post_command"     # コマンド実行後
    PRE_ANALYSIS = "pre_analysis"     # 解析前
    POST_ANALYSIS = "post_analysis"   # 解析後
    PRE_BUILD = "pre_build"          # ビルド前
    POST_BUILD = "post_build"        # ビルド後
    PRE_TEST = "pre_test"            # テスト前
    POST_TEST = "post_test"          # テスト後
    ERROR = "error"                  # エラー発生時
    DAILY = "daily"                  # 日次処理

class Hook:
    """フック定義"""
    
    def __init__(self, name: str, hook_type: HookType, handler: Callable):
        self.name = name
        self.hook_type = hook_type
        self.handler = handler
        self.enabled = True
        self.execution_count = 0
        self.last_executed = None
        
    def execute(self, context: Dict) -> bool:
        """フックを実行"""
        if not self.enabled:
            return True
        
        try:
            self.handler(context)
            self.execution_count += 1
            self.last_executed = datetime.now()
            return True
        except Exception as e:
            print(f"フック実行エラー [{self.name}]: {e}")
            return False

class HooksManager:
    """フック管理システム"""
    
    def __init__(self):
        self.hooks_dir = Path(".claude/hooks")
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.hooks_dir / "hooks_config.json"
        self.log_file = self.hooks_dir / "hooks_log.json"
        self.hooks: Dict[HookType, List[Hook]] = {hook_type: [] for hook_type in HookType}
        
        # 組み込みフックを登録
        self._register_builtin_hooks()
        
        # カスタムフックを読み込み
        self._load_custom_hooks()
        
    def _register_builtin_hooks(self):
        """組み込みフックを登録"""
        
        # コマンド実行前後のログ記録
        self.register_hook(
            "log_command_start",
            HookType.PRE_COMMAND,
            self._log_command_start
        )
        
        self.register_hook(
            "log_command_end",
            HookType.POST_COMMAND,
            self._log_command_end
        )
        
        # 解析前のキャッシュチェック
        self.register_hook(
            "check_cache",
            HookType.PRE_ANALYSIS,
            self._check_analysis_cache
        )
        
        # 解析後のキャッシュ保存
        self.register_hook(
            "save_cache",
            HookType.POST_ANALYSIS,
            self._save_analysis_cache
        )
        
        # ビルド前のバックアップ
        self.register_hook(
            "backup_before_build",
            HookType.PRE_BUILD,
            self._create_backup
        )
        
        # テスト後のカバレッジチェック
        self.register_hook(
            "check_coverage",
            HookType.POST_TEST,
            self._check_test_coverage
        )
        
        # エラー時の自動バックアップ
        self.register_hook(
            "error_backup",
            HookType.ERROR,
            self._error_recovery
        )
        
        # 日次クリーンアップ
        self.register_hook(
            "daily_cleanup",
            HookType.DAILY,
            self._daily_cleanup
        )
    
    def _log_command_start(self, context: Dict):
        """コマンド開始をログに記録"""
        command = context.get('command', 'unknown')
        timestamp = format_jst_datetime()
        
        # 作業日誌に記録
        from daily_log_writer import DailyLogWriter
        log_writer = DailyLogWriter()
        log_writer.write_activity("システム", "コマンド開始", f"/{command}")
        
        print(f"フック: コマンド開始ログ記録 [{command}]")
    
    def _log_command_end(self, context: Dict):
        """コマンド終了をログに記録"""
        command = context.get('command', 'unknown')
        success = context.get('success', False)
        execution_time = context.get('execution_time', 0)
        
        # 作業日誌に記録
        from daily_log_writer import DailyLogWriter
        log_writer = DailyLogWriter()
        status = "成功" if success else "失敗"
        log_writer.write_activity("システム", "コマンド終了", 
                                 f"/{command} - {status} ({execution_time:.1f}秒)")
        
        print(f"フック: コマンド終了ログ記録 [{command}] - {status}")
    
    def _check_analysis_cache(self, context: Dict):
        """解析キャッシュをチェック"""
        project_path = context.get('project_path', '.')
        
        from analysis_cache import AnalysisCache
        cache = AnalysisCache()
        cached_result = cache.load_cache("project_analysis")
        
        if cached_result:
            context['cached_result'] = cached_result
            print(f"フック: キャッシュヒット - 解析をスキップ")
        else:
            print(f"フック: キャッシュミス - 解析を実行")
    
    def _save_analysis_cache(self, context: Dict):
        """解析結果をキャッシュに保存"""
        result = context.get('analysis_result')
        execution_time = context.get('execution_time', 0)
        
        if result:
            from analysis_cache import AnalysisCache
            cache = AnalysisCache()
            cache.save_cache("project_analysis", result, execution_time)
            print(f"フック: 解析結果をキャッシュに保存")
    
    def _create_backup(self, context: Dict):
        """ビルド前にバックアップを作成"""
        from auto_cleanup_manager import AutoCleanupManager
        manager = AutoCleanupManager()
        manager.create_checkpoint()
        print(f"フック: ビルド前バックアップ作成")
    
    def _check_test_coverage(self, context: Dict):
        """テストカバレッジをチェック"""
        coverage = context.get('coverage', 0)
        threshold = context.get('threshold', 80)
        
        if coverage < threshold:
            print(f"フック: テストカバレッジが基準値未満 ({coverage}% < {threshold}%)")
            
            # 品質保証部に通知
            from daily_log_writer import DailyLogWriter
            log_writer = DailyLogWriter()
            log_writer.write_activity("品質保証部", "警告", 
                                     f"テストカバレッジ不足: {coverage}%")
        else:
            print(f"フック: テストカバレッジ基準達成 ({coverage}%)")
    
    def _error_recovery(self, context: Dict):
        """エラー時の自動復旧"""
        error = context.get('error', 'Unknown error')
        
        from auto_cleanup_manager import AutoCleanupManager
        manager = AutoCleanupManager()
        backup_path = manager.create_error_backup(str(error))
        
        if backup_path:
            context['backup_path'] = backup_path
            print(f"フック: エラーバックアップ作成 - {backup_path.name}")
    
    def _daily_cleanup(self, context: Dict):
        """日次クリーンアップ"""
        from auto_cleanup_manager import AutoCleanupManager
        manager = AutoCleanupManager()
        manager.daily_cleanup()
        print(f"フック: 日次クリーンアップ完了")
    
    def _load_custom_hooks(self):
        """カスタムフックを読み込み"""
        custom_hooks_file = self.hooks_dir / "custom_hooks.py"
        
        if custom_hooks_file.exists():
            try:
                # カスタムフックをインポート
                import importlib.util
                spec = importlib.util.spec_from_file_location("custom_hooks", custom_hooks_file)
                custom_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(custom_module)
                
                # register_hooksがあれば実行
                if hasattr(custom_module, 'register_hooks'):
                    custom_module.register_hooks(self)
                    print(f"カスタムフック読み込み完了")
            except Exception as e:
                print(f"カスタムフック読み込みエラー: {e}")
    
    def register_hook(self, name: str, hook_type: HookType, handler: Callable):
        """フックを登録"""
        hook = Hook(name, hook_type, handler)
        self.hooks[hook_type].append(hook)
        print(f"フック登録: {name} ({hook_type.value})")
    
    def execute_hooks(self, hook_type: HookType, context: Dict) -> bool:
        """指定タイプのフックを実行"""
        hooks = self.hooks.get(hook_type, [])
        
        if not hooks:
            return True
        
        print(f"\nフック実行: {hook_type.value}")
        
        all_success = True
        for hook in hooks:
            if hook.enabled:
                success = hook.execute(context)
                if not success:
                    all_success = False
        
        return all_success
    
    def create_command_context(self, command: str, args: List[str] = None) -> Dict:
        """コマンド実行コンテキストを作成"""
        return {
            'command': command,
            'args': args or [],
            'timestamp': format_jst_datetime(),
            'user': os.environ.get('USER', 'unknown'),
            'cwd': os.getcwd()
        }
    
    def execute_with_hooks(self, command: str, args: List[str] = None) -> bool:
        """フック付きでコマンドを実行"""
        context = self.create_command_context(command, args)
        
        # 実行前フック
        self.execute_hooks(HookType.PRE_COMMAND, context)
        
        # コマンド実行
        start_time = time.time()
        success = True
        
        try:
            # ここで実際のコマンドを実行
            # この例では、command_executor.pyを呼び出す
            from command_executor import CommandExecutor
            executor = CommandExecutor()
            success = executor.execute(command, args)
            
        except Exception as e:
            success = False
            context['error'] = str(e)
            self.execute_hooks(HookType.ERROR, context)
        
        # 実行時間を記録
        execution_time = time.time() - start_time
        context['execution_time'] = execution_time
        context['success'] = success
        
        # 実行後フック
        self.execute_hooks(HookType.POST_COMMAND, context)
        
        return success
    
    def get_hook_stats(self) -> Dict:
        """フック実行統計を取得"""
        stats = {}
        
        for hook_type, hooks in self.hooks.items():
            type_stats = []
            for hook in hooks:
                type_stats.append({
                    'name': hook.name,
                    'enabled': hook.enabled,
                    'execution_count': hook.execution_count,
                    'last_executed': hook.last_executed.isoformat() if hook.last_executed else None
                })
            stats[hook_type.value] = type_stats
        
        return stats
    
    def save_config(self):
        """設定を保存"""
        config = {
            'hooks': {}
        }
        
        for hook_type, hooks in self.hooks.items():
            config['hooks'][hook_type.value] = [
                {
                    'name': hook.name,
                    'enabled': hook.enabled
                }
                for hook in hooks
            ]
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        """設定を読み込み"""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # フックの有効/無効を設定
            for hook_type_str, hook_configs in config.get('hooks', {}).items():
                hook_type = HookType(hook_type_str)
                hooks = self.hooks.get(hook_type, [])
                
                for hook_config in hook_configs:
                    for hook in hooks:
                        if hook.name == hook_config['name']:
                            hook.enabled = hook_config['enabled']
        except Exception as e:
            print(f"⚠️ 設定読み込みエラー: {e}")

def create_sample_custom_hooks():
    """サンプルカスタムフックを作成"""
    custom_hooks_code = '''"""
カスタムフック定義
"""

def register_hooks(manager):
    """カスタムフックを登録"""
    
    # プロジェクト解析時に部門に通知
    def notify_departments(context):
        print("全部門へ: プロジェクト解析を開始します")
        
        from daily_log_writer import DailyLogWriter
        log_writer = DailyLogWriter()
        
        departments = ["CTO", "品質保証部", "人事部", "経営企画部", "システム開発部"]
        for dept in departments:
            log_writer.write_activity(dept, "通知受信", "プロジェクト解析開始の通知")
    
    manager.register_hook(
        "notify_departments",
        manager.HookType.PRE_ANALYSIS,
        notify_departments
    )
    
    # テスト成功時の自動コミット
    def auto_commit_on_test_success(context):
        if context.get('success') and context.get('coverage', 0) >= 80:
            print("テスト成功！自動コミット準備中...")
            # 実際のコミットはユーザー確認後に実行
    
    manager.register_hook(
        "auto_commit",
        manager.HookType.POST_TEST,
        auto_commit_on_test_success
    )
'''
    
    hooks_dir = Path(".claude/hooks")
    hooks_dir.mkdir(parents=True, exist_ok=True)
    custom_hooks_file = hooks_dir / "custom_hooks.py"
    custom_hooks_file.write_text(custom_hooks_code)
    print(f"サンプルカスタムフック作成: {custom_hooks_file}")

def demo():
    """デモンストレーション"""
    print("\n" + "=" * 60)
    print("フック管理システム デモ")
    print("=" * 60 + "\n")
    
    # フックマネージャー初期化
    manager = HooksManager()
    
    # フック統計表示
    print("登録されているフック:")
    stats = manager.get_hook_stats()
    for hook_type, hooks in stats.items():
        if hooks:
            print(f"\n  {hook_type}:")
            for hook in hooks:
                status = "✅" if hook['enabled'] else "❌"
                print(f"    {status} {hook['name']}")
    
    print("\n" + "-" * 40 + "\n")
    
    # コマンド実行デモ
    print("【コマンド実行デモ】")
    context = manager.create_command_context("spec", ["init"])
    
    # PRE_COMMANDフック実行
    manager.execute_hooks(HookType.PRE_COMMAND, context)
    
    # コマンド実行シミュレーション
    time.sleep(1)
    context['success'] = True
    context['execution_time'] = 1.0
    
    # POST_COMMANDフック実行
    manager.execute_hooks(HookType.POST_COMMAND, context)
    
    print("\n" + "-" * 40 + "\n")
    
    # エラー処理デモ
    print("【エラー処理デモ】")
    error_context = {
        'error': 'ビルドエラー: モジュールが見つかりません'
    }
    manager.execute_hooks(HookType.ERROR, error_context)
    
    print("\n✅ デモ完了\n")

def main():
    """メイン処理"""
    import argparse
    parser = argparse.ArgumentParser(description='フック管理システム')
    parser.add_argument('command', nargs='?', default='status',
                      choices=['status', 'demo', 'create-sample', 'exec'])
    parser.add_argument('--cmd', help='実行するコマンド（execモード用）')
    parser.add_argument('--args', nargs='*', help='コマンド引数')
    
    args = parser.parse_args()
    
    manager = HooksManager()
    
    if args.command == 'status':
        stats = manager.get_hook_stats()
        print("📊 フック統計:")
        for hook_type, hooks in stats.items():
            if hooks:
                print(f"\n{hook_type}:")
                for hook in hooks:
                    status = "有効" if hook['enabled'] else "無効"
                    count = hook['execution_count']
                    print(f"  {hook['name']}: {status} (実行回数: {count})")
    
    elif args.command == 'demo':
        demo()
    
    elif args.command == 'create-sample':
        create_sample_custom_hooks()
    
    elif args.command == 'exec':
        if args.cmd:
            success = manager.execute_with_hooks(args.cmd, args.args)
            exit(0 if success else 1)
        else:
            print("--cmd オプションでコマンドを指定してください")

if __name__ == "__main__":
    main()