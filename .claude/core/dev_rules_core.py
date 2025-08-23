#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
開発ルール基盤エンジン - Core Engine & Configuration
統合開発ルール自動化システムの基盤部分
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

from .config import get_config
from .logger import logger
from .emoji_validator import emoji_validator

class RuleType(Enum):
    """開発ルールタイプ"""
    CHECKLIST = "checklist"           # 修正前チェックリスト
    TEST_FIRST = "test_first"         # テストファースト
    INCREMENTAL = "incremental"       # 段階的修正
    EMOJI_VALIDATION = "emoji"        # 絵文字検証

class TDDPhase(Enum):
    """TDDフェーズ"""
    RED = "red"        # 失敗するテストを書く
    GREEN = "green"    # テストを通す最小限の実装
    REFACTOR = "refactor"  # リファクタリング
    UNKNOWN = "unknown"    # 状態不明

class DevelopmentRulesCoreEngine:
    """開発ルール基盤エンジン - 設定・状態管理"""
    
    def __init__(self):
        """エンジンの初期化"""
        self.config = get_config()
        self.rules_config = self.config.get_rules_config()
        
        # プロジェクトパス設定
        self.project_paths = self.config.get_project_paths()
        self.state_file = self.project_paths['cache'] / 'development_rules_state.json'
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # TDD状態管理
        self.tdd_state_file = self.project_paths['cache'] / 'tdd_state.json'
        
        # チェックリスト状態管理
        self.checklist_file = self.project_paths['cache'] / 'checklist_status.json'
        
        # 現在の状態を読み込み
        self.current_state = self._load_state()
        
        logger.info("開発ルール基盤エンジン初期化完了", "RULES_CORE")
    
    def _load_state(self) -> Dict[str, Any]:
        """開発状態の読み込み"""
        default_state = {
            "version": "11.0",
            "last_updated": datetime.now().isoformat(),
            "active_rules": [],
            "current_task": None,
            "modification_allowed": False,
            "workflow_history": []
        }
        
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    return {**default_state, **state}
        except Exception as e:
            logger.error(f"状態読み込みエラー: {e}", "RULES_CORE")
        
        return default_state
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """開発状態の保存"""
        try:
            state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"状態保存エラー: {e}", "RULES_CORE")
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム状態の取得"""
        return {
            "version": "11.0",
            "rules_enabled": {
                "checklist": self.rules_config.get('enforce_checklist', True),
                "test_first": self.rules_config.get('enforce_test_first', True),
                "incremental": self.rules_config.get('enforce_incremental_fix', True),
                "emoji_validation": self.rules_config.get('validate_emojis', True)
            },
            "project_paths": {k: str(v) for k, v in self.project_paths.items()},
            "last_updated": self.current_state.get("last_updated")
        }

    def _validate_emojis_in_request(self, modification_request: Dict[str, Any]) -> Dict[str, Any]:
        """修正要求内の絵文字検証"""
        description = modification_request.get("description", "")
        emojis_found = emoji_validator.detect_emojis(description)
        
        return {
            "valid": len(emojis_found) == 0,
            "emojis_found": emojis_found,
            "cleaned_description": emoji_validator.replace_emojis_with_text(description)
        }
    
    def _record_workflow_execution(self, result: Dict[str, Any]) -> None:
        """ワークフロー実行履歴の記録"""
        try:
            history_file = self.project_paths['cache'] / 'workflow_history.json'
            
            # 既存履歴を読み込み
            history = []
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 新しい実行結果を追加
            history.append({
                "workflow_id": result["workflow_id"],
                "timestamp": datetime.now().isoformat(),
                "status": result["status"],
                "steps_completed": result["steps_completed"],
                "modification_allowed": result["modification_allowed"],
                "errors_count": len(result.get("errors", [])),
                "warnings_count": len(result.get("warnings", []))
            })
            
            # 履歴は最新50件まで保持
            if len(history) > 50:
                history = history[-50:]
            
            # ファイルに保存
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"ワークフロー履歴記録エラー: {e}", "RULES_CORE")

# シングルトンインスタンス
dev_rules_core = DevelopmentRulesCoreEngine()