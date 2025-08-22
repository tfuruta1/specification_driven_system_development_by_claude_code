#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一設定システム - Claude Code Core v11.0
YAGNI, DRY, KISS原則に準拠した統一設定管理

CTOとアレックスの開発環境を一元管理
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

class Environment(Enum):
    """環境タイプ"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"

class ClaudeCoreConfig:
    """統一設定クラス"""
    
    def __init__(self):
        """設定の初期化"""
        self.base_path = Path(__file__).parent.parent
        self.config_file = self.base_path / ".claude" / "core_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # デフォルト設定
        self.default_config = {
            "version": "11.0",
            "environment": "development",
            "debug": True,
            
            # ペアプログラミング設定
            "pair_programming": {
                "cto_name": "CTO",
                "alex_name": "アレックス",
                "alex_style": "friendly",
                "auto_logging": True
            },
            
            # SDD+TDD設定
            "sdd_tdd": {
                "enforce_tdd": True,
                "require_specs": True,
                "require_tests_first": True,
                "auto_generate_docs": True
            },
            
            # 開発ルール設定
            "development_rules": {
                "enforce_checklist": True,
                "enforce_test_first": True,
                "enforce_incremental_fix": True,
                "validate_emojis": True
            },
            
            # ログ設定
            "logging": {
                "level": "INFO",
                "console_output": True,
                "file_output": True,
                "activity_logging": True,
                "log_rotation": True
            },
            
            # テスト設定
            "testing": {
                "test_command": "npm test",
                "coverage_threshold": 80,
                "auto_run_tests": True,
                "test_patterns": {
                    "javascript": ["*.test.js", "*.spec.js"],
                    "vue": ["*.test.vue.js"],
                    "python": ["test_*.py", "*_test.py"]
                }
            },
            
            # プロジェクト設定
            "project": {
                "root_path": ".",
                "docs_path": ".claude/docs",
                "workspace_path": ".claude/workspace",
                "cache_path": ".claude/cache",
                "activity_report_path": ".claude/ActivityReport"
            },
            
            # 品質管理設定
            "quality": {
                "emoji_validation": True,
                "code_review_required": True,
                "documentation_required": True,
                "performance_monitoring": True
            }
        }
        
        # 設定を読み込み
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # デフォルト設定とマージ
                    return self._merge_config(self.default_config, loaded_config)
            except Exception as e:
                print(f"設定ファイル読み込み失敗: {e}")
                return self.default_config.copy()
        else:
            # 初回作成
            self._save_config(self.default_config)
            return self.default_config.copy()
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """設定の再帰的マージ"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """設定ファイルの保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイル保存失敗: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """ドット記法での設定値取得"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """ドット記法での設定値設定"""
        keys = key_path.split('.')
        target = self.config
        
        # 最後のキーまでナビゲート
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # 値を設定
        target[keys[-1]] = value
        
        # 設定ファイルを更新
        self._save_config(self.config)
    
    def get_environment(self) -> Environment:
        """現在の環境を取得"""
        env_str = self.get('environment', 'development')
        try:
            return Environment(env_str)
        except ValueError:
            return Environment.DEVELOPMENT
    
    def is_debug(self) -> bool:
        """デバッグモードかどうか"""
        return self.get('debug', True)
    
    def is_production(self) -> bool:
        """本番環境かどうか"""
        return self.get_environment() == Environment.PRODUCTION
    
    def get_project_paths(self) -> Dict[str, Path]:
        """プロジェクトパスの取得"""
        root = Path(self.get('project.root_path', '.'))
        return {
            'root': root,
            'core': root / '.claude/core',
            'docs': root / self.get('project.docs_path', '.claude/docs'),
            'workspace': root / self.get('project.workspace_path', '.claude/workspace'),
            'cache': root / self.get('project.cache_path', '.claude/cache'),
            'activity_report': root / self.get('project.activity_report_path', '.claude/ActivityReport')
        }
    
    def detect_environment(self) -> str:
        """環境の自動検出（テスト用エイリアス）"""
        return self.get_environment().value
    
    def get_logging_config(self) -> Dict[str, Any]:
        """ログ設定の取得"""
        return self.get('logging', {})
    
    def get_tdd_config(self) -> Dict[str, Any]:
        """TDD設定の取得"""
        return self.get('sdd_tdd', {})
    
    def get_rules_config(self) -> Dict[str, Any]:
        """開発ルール設定の取得"""
        return self.get('development_rules', {})
    
    def get_testing_config(self) -> Dict[str, Any]:
        """テスト設定の取得"""
        return self.get('testing', {})
    
    def get_quality_config(self) -> Dict[str, Any]:
        """品質管理設定の取得"""
        return self.get('quality', {})
    
    def get_pair_config(self) -> Dict[str, Any]:
        """ペアプログラミング設定の取得"""
        return self.get('pair_programming', {})
    
    def update_environment(self, env: Environment) -> None:
        """環境の更新"""
        self.set('environment', env.value)
        
        # 環境に応じてデバッグモードを調整
        if env == Environment.PRODUCTION:
            self.set('debug', False)
            self.set('logging.level', 'WARNING')
        else:
            self.set('debug', True)
            self.set('logging.level', 'INFO')
    
    def enable_rule(self, rule_name: str) -> None:
        """開発ルールの有効化"""
        self.set(f'development_rules.{rule_name}', True)
    
    def disable_rule(self, rule_name: str) -> None:
        """開発ルールの無効化"""
        self.set(f'development_rules.{rule_name}', False)
    
    def get_rule_status(self, rule_name: str) -> bool:
        """開発ルールの状態取得"""
        return self.get(f'development_rules.{rule_name}', False)
    
    def validate_config(self) -> List[str]:
        """設定の検証"""
        issues = []
        
        # 必須パスの確認
        paths = self.get_project_paths()
        for name, path in paths.items():
            if not path.parent.exists():
                issues.append(f"親ディレクトリが存在しません: {path.parent}")
        
        # テストコマンドの確認
        test_command = self.get('testing.test_command')
        if not test_command:
            issues.append("テストコマンドが設定されていません")
        
        # カバレッジ閾値の確認
        threshold = self.get('testing.coverage_threshold')
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 100:
            issues.append("カバレッジ閾値が無効です (0-100)")
        
        return issues
    
    def get_summary(self) -> Dict[str, Any]:
        """設定サマリーの取得"""
        return {
            'version': self.get('version'),
            'environment': self.get_environment().value,
            'debug_mode': self.is_debug(),
            'rules_enabled': {
                'tdd_enforcement': self.get_rule_status('enforce_test_first'),
                'checklist_enforcement': self.get_rule_status('enforce_checklist'),
                'incremental_fix': self.get_rule_status('enforce_incremental_fix'),
                'emoji_validation': self.get_rule_status('validate_emojis')
            },
            'pair_programming': {
                'alex_style': self.get('pair_programming.alex_style'),
                'auto_logging': self.get('pair_programming.auto_logging')
            },
            'paths_configured': len(self.get_project_paths()),
            'validation_issues': len(self.validate_config())
        }

# シングルトンインスタンス
config = ClaudeCoreConfig()

# テスト用エイリアス（TDD Green Phase対応）
IntegratedConfig = ClaudeCoreConfig

# 便利関数
def get_config() -> ClaudeCoreConfig:
    """設定インスタンスの取得"""
    return config

def is_debug() -> bool:
    """デバッグモードかどうか"""
    return config.is_debug()

def is_production() -> bool:
    """本番環境かどうか"""
    return config.is_production()

def get_project_root() -> Path:
    """プロジェクトルートの取得"""
    return config.get_project_paths()['root']

# デモ実行
if __name__ == "__main__":
    print("=== Claude Core Config v11.0 ===")
    
    # 設定サマリー表示
    summary = config.get_summary()
    print(f"バージョン: {summary['version']}")
    print(f"環境: {summary['environment']}")
    print(f"デバッグモード: {summary['debug_mode']}")
    
    # ルール状態
    print("\n開発ルール:")
    for rule, enabled in summary['rules_enabled'].items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {rule}")
    
    # 設定検証
    issues = config.validate_config()
    if issues:
        print(f"\n⚠️ 設定問題: {len(issues)}件")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ 設定検証: 問題なし")
    
    # パス確認
    paths = config.get_project_paths()
    print(f"\nプロジェクトパス:")
    for name, path in paths.items():
        exists = "✓" if path.exists() else "✗"
        print(f"  {exists} {name}: {path}")