#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYSTEM - Claude Code Core v11.0
YAGNI, DRY, KISSSYSTEM

CTOSYSTEM
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

# 相対パスユーティリティをインポート
try:
    from path_utils import paths
except ImportError:
    # path_utilsが見つからない場合は直接パスを設定
    sys.path.insert(0, str(Path(__file__).parent))
    from path_utils import paths

class Environment(Enum):
    """TEST"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"

class Config:
    """Configuration class for Claude Core system"""
    pass

class ClaudeCoreConfig:
    """TEST"""
    
    def __init__(self):
        """TEST"""
        # path_utilsを使って相対パスを取得
        self.base_path = paths.root
        self.config_file = paths.config / "core_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # CONFIG
        self.default_config = {
            "version": "11.0",
            "environment": "development",
            "debug": True,
            
            # 
            "pair_programming": {
                "cto_name": "CTO",
                "alex_name": "",
                "alex_style": "friendly",
                "auto_logging": True
            },
            
            # SDD+TDD
            "sdd_tdd": {
                "enforce_tdd": True,
                "require_specs": True,
                "require_tests_first": True,
                "auto_generate_docs": True
            },
            
            # ANALYSIS
            "development_rules": {
                "enforce_checklist": True,
                "enforce_test_first": True,
                "enforce_incremental_fix": True,
                "validate_emojis": True
            },
            
            # 
            "logging": {
                "level": "INFO",
                "console_output": True,
                "file_output": True,
                "activity_logging": True,
                "log_rotation": True
            },
            
            # TEST
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
            
            # TEST
            "project": {
                "root_path": ".",
                "docs_path": ".claude/docs",
                "workspace_path": ".claude/workspace",
                "cache_path": ".claude/temp/cache",
                "activity_report_path": ".claude/ActivityReport"
            },
            
            # REPORT
            "quality": {
                "emoji_validation": True,
                "code_review_required": True,
                "documentation_required": True,
                "performance_monitoring": True
            }
        }
        
        # CONFIG
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """CONFIG"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # CONFIG
                    return self._merge_config(self.default_config, loaded_config)
            except Exception as e:
                print(f"ERROR: {e}")
                return self.default_config.copy()
        else:
            # CONFIG
            self._save_config(self.default_config)
            return self.default_config.copy()
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """CONFIG"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """CONFIG"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"ERROR: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """CONFIG"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """CONFIG"""
        keys = key_path.split('.')
        target = self.config
        
        # CONFIG
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # CONFIG
        target[keys[-1]] = value
        
        # CONFIG
        self._save_config(self.config)
    
    def get_environment(self) -> Environment:
        """CONFIG"""
        env_str = self.get('environment', 'development')
        try:
            return Environment(env_str)
        except ValueError:
            return Environment.DEVELOPMENT
    
    def is_debug(self) -> bool:
        """ERROR"""
        return self.get('debug', True)
    
    def is_production(self) -> bool:
        """"""
        return self.get_environment() == Environment.PRODUCTION
    
    def get_project_paths(self) -> Dict[str, Path]:
        """"""
        root = Path(self.get('project.root_path', '.'))
        return {
            'root': root,
            'core': root / '.claude/core',
            'docs': root / self.get('project.docs_path', '.claude/docs'),
            'workspace': root / self.get('project.workspace_path', '.claude/workspace'),
            'cache': root / self.get('project.cache_path', '.claude/temp/cache'),
            'activity_report': root / self.get('project.activity_report_path', '.claude/ActivityReport')
        }
    
    def detect_environment(self) -> str:
        """CONFIG"""
        return self.get_environment().value
    
    def get_logging_config(self) -> Dict[str, Any]:
        """CONFIG"""
        return self.get('logging', {})
    
    def get_tdd_config(self) -> Dict[str, Any]:
        """TDDCONFIG"""
        return self.get('sdd_tdd', {})
    
    def get_rules_config(self) -> Dict[str, Any]:
        """TEST"""
        return self.get('development_rules', {})
    
    def get_testing_config(self) -> Dict[str, Any]:
        """TEST"""
        return self.get('testing', {})
    
    def get_quality_config(self) -> Dict[str, Any]:
        """TEST"""
        return self.get('quality', {})
    
    def get_pair_config(self) -> Dict[str, Any]:
        """CONFIG"""
        return self.get('pair_programming', {})
    
    def update_environment(self, env: Environment) -> None:
        """"""
        self.set('environment', env.value)
        
        # 
        if env == Environment.PRODUCTION:
            self.set('debug', False)
            self.set('logging.level', 'WARNING')
        else:
            self.set('debug', True)
            self.set('logging.level', 'INFO')
    
    def enable_rule(self, rule_name: str) -> None:
        """"""
        self.set(f'development_rules.{rule_name}', True)
    
    def disable_rule(self, rule_name: str) -> None:
        """"""
        self.set(f'development_rules.{rule_name}', False)
    
    def get_rule_status(self, rule_name: str) -> bool:
        """CONFIG"""
        return self.get(f'development_rules.{rule_name}', False)
    
    def validate_config(self) -> List[str]:
        """CONFIG"""
        issues = []
        
        # CONFIG
        paths = self.get_project_paths()
        for name, path in paths.items():
            if not path.parent.exists():
                issues.append(f"TEST: {path.parent}")
        
        # TEST
        test_command = self.get('testing.test_command')
        if not test_command:
            issues.append("TEST")
        
        # TEST
        threshold = self.get('testing.coverage_threshold')
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 100:
            issues.append("REPORT (0-100)")
        
        return issues
    
    def get_summary(self) -> Dict[str, Any]:
        """REPORT"""
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

# CONFIG
config = ClaudeCoreConfig()

# Environment constants for backward compatibility
DEVELOPMENT = Environment.DEVELOPMENT.value
PRODUCTION = Environment.PRODUCTION.value
TEST = Environment.TEST.value

# CONFIGTDD Green PhaseCONFIG
IntegratedConfig = ClaudeCoreConfig

# CONFIG - Module-level convenience functions
def get_config() -> ClaudeCoreConfig:
    """CONFIG"""
    return config

def is_debug() -> bool:
    """CONFIG"""
    return config.is_debug()

def is_production() -> bool:
    """CONFIG"""
    return config.is_production()

def get_project_root() -> Path:
    """CONFIG"""
    return config.get_project_paths()['root']

# Module-level wrappers for config instance methods
def get(key_path: str, default: Any = None) -> Any:
    """Get configuration value by key path"""
    return config.get(key_path, default)

def set(key_path: str, value: Any) -> None:
    """Set configuration value by key path"""
    config.set(key_path, value)

def get_environment() -> Environment:
    """Get current environment"""
    return config.get_environment()

def detect_environment() -> str:
    """Detect current environment as string"""
    return config.detect_environment()

def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration"""
    return config.get_logging_config()

def get_tdd_config() -> Dict[str, Any]:
    """Get TDD configuration"""
    return config.get_tdd_config()

def get_rules_config() -> Dict[str, Any]:
    """Get development rules configuration"""
    return config.get_rules_config()

def get_testing_config() -> Dict[str, Any]:
    """Get testing configuration"""
    return config.get_testing_config()

def get_quality_config() -> Dict[str, Any]:
    """Get quality configuration"""
    return config.get_quality_config()

def get_pair_config() -> Dict[str, Any]:
    """Get pair programming configuration"""
    return config.get_pair_config()

def get_project_paths() -> Dict[str, Path]:
    """Get all project paths"""
    return config.get_project_paths()

def update_environment(env: Environment) -> None:
    """Update environment setting"""
    config.update_environment(env)

def enable_rule(rule_name: str) -> None:
    """Enable a development rule"""
    config.enable_rule(rule_name)

def disable_rule(rule_name: str) -> None:
    """Disable a development rule"""
    config.disable_rule(rule_name)

def get_rule_status(rule_name: str) -> bool:
    """Get status of a development rule"""
    return config.get_rule_status(rule_name)

def validate_config() -> List[str]:
    """Validate configuration and return list of issues"""
    return config.validate_config()

def get_summary() -> Dict[str, Any]:
    """Get configuration summary"""
    return config.get_summary()

# CONFIG
if __name__ == "__main__":
    print("=== Claude Core Config v11.0 ===")
    
    # CONFIG
    summary = config.get_summary()
    print(f"CONFIG: {summary['version']}")
    print(f"CONFIG: {summary['environment']}")
    print(f"REPORT: {summary['debug_mode']}")
    
    # REPORT
    print("\nREPORT:")
    for rule, enabled in summary['rules_enabled'].items():
        status = "[CHECK]" if enabled else "[CROSS]"
        print(f"  {status} {rule}")
    
    # WARNING
    issues = config.validate_config()
    if issues:
        print(f"\n[WARNING] WARNING: {len(issues)}WARNING")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[OK] CONFIG: CONFIG")
    
    # CONFIG
    paths = config.get_project_paths()
    print(f"\nCONFIG:")
    for name, path in paths.items():
        exists = "[CHECK]" if path.exists() else "[CROSS]"
        print(f"  {exists} {name}: {path}")


# エイリアス（互換性のため）
ConfigManager = ClaudeCoreConfig