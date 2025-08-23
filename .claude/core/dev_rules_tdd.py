#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDDワークフロー管理システム - TDD Workflow Manager
教訓2「テストファースト」の実装
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .dev_rules_core import dev_rules_core, TDDPhase, logger

class TDDWorkflowManager:
    """TDDワークフロー管理システム"""
    
    def __init__(self):
        """TDDワークフロー管理システムの初期化"""
        self.core = dev_rules_core
        self.tdd_state_file = self.core.tdd_state_file
        logger.info("TDDワークフロー管理システム初期化完了", "TDD")
    
    def enforce_tdd_workflow(self, operation: str, file_path: str) -> Dict[str, Any]:
        """
        TDDワークフローの強制（教訓2）
        
        Args:
            operation: 実行操作 ('test', 'implement', 'refactor')
            file_path: 対象ファイルパス
            
        Returns:
            TDD強制結果
        """
        if not self.core.rules_config.get('enforce_test_first', True):
            return {
                "allowed": True,
                "message": "TDD強制は無効化されています",
                "phase": "bypassed"
            }
        
        current_phase = self._get_current_tdd_phase()
        
        enforcement_result = {
            "operation": operation,
            "file_path": file_path,
            "current_phase": current_phase.value,
            "allowed": False,
            "message": "",
            "required_actions": [],
            "recommendations": []
        }
        
        # フェーズ別の操作制御
        if operation == "test":
            # テスト作成は常に許可
            enforcement_result["allowed"] = True
            enforcement_result["message"] = "テスト作成は常に許可されます"
            self._update_tdd_phase(TDDPhase.RED, file_path)
            
        elif operation == "implement":
            if current_phase == TDDPhase.RED:
                # REDフェーズでの実装は許可
                enforcement_result["allowed"] = True
                enforcement_result["message"] = "RED phase: 実装許可"
                enforcement_result["recommendations"].append("最小限の実装でテストを通してください")
                self._update_tdd_phase(TDDPhase.GREEN, file_path)
            else:
                # 他のフェーズでは失敗するテストが必要
                enforcement_result["allowed"] = False
                enforcement_result["message"] = "実装には失敗するテストが必要です（RED phase）"
                enforcement_result["required_actions"].append("先に失敗するテストを作成してください")
                
        elif operation == "refactor":
            if current_phase in [TDDPhase.GREEN, TDDPhase.REFACTOR]:
                # GREEN/REFACTORフェーズでのリファクタリングは許可
                enforcement_result["allowed"] = True
                enforcement_result["message"] = "GREEN phase: リファクタリング許可"
                enforcement_result["recommendations"].append("テストが通り続けることを確認してください")
                self._update_tdd_phase(TDDPhase.REFACTOR, file_path)
            else:
                enforcement_result["allowed"] = False
                enforcement_result["message"] = "リファクタリングには全テストの成功が必要です"
                enforcement_result["required_actions"].append("全テストを成功させてください")
        
        # TDD状態の記録
        self._record_tdd_operation(operation, file_path, enforcement_result)
        
        logger.info(f"TDD強制: {operation} on {Path(file_path).name} - {'許可' if enforcement_result['allowed'] else '拒否'}", "TDD")
        
        return enforcement_result
    
    def _get_current_tdd_phase(self) -> TDDPhase:
        """現在のTDDフェーズを取得"""
        try:
            if not self.tdd_state_file.exists():
                return TDDPhase.UNKNOWN
            
            with open(self.tdd_state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            last_test_result = state.get('last_test_result')
            
            if not last_test_result:
                return TDDPhase.UNKNOWN
            
            # テストが失敗している場合 = REDフェーズ
            if last_test_result.get('failed', 0) > 0:
                return TDDPhase.RED
            
            # テストが全て通っている場合
            elif last_test_result.get('passed', 0) > 0:
                # 最近実装が行われた場合 = GREENフェーズ
                last_implementation = state.get('last_implementation_time')
                if last_implementation:
                    impl_time = datetime.fromisoformat(last_implementation)
                    if datetime.now() - impl_time < timedelta(hours=1):
                        return TDDPhase.GREEN
                    else:
                        return TDDPhase.REFACTOR
                else:
                    return TDDPhase.GREEN
            
            return TDDPhase.UNKNOWN
            
        except Exception as e:
            logger.error(f"TDDフェーズ取得エラー: {e}", "TDD")
            return TDDPhase.UNKNOWN
    
    def _update_tdd_phase(self, phase: TDDPhase, file_path: str) -> None:
        """TDDフェーズの更新"""
        try:
            state = {}
            if self.tdd_state_file.exists():
                with open(self.tdd_state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            
            state.update({
                "current_phase": phase.value,
                "last_file": file_path,
                "last_update": datetime.now().isoformat()
            })
            
            if phase == TDDPhase.GREEN:
                state["last_implementation_time"] = datetime.now().isoformat()
            
            with open(self.tdd_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"TDDフェーズ更新エラー: {e}", "TDD")
    
    def _record_tdd_operation(self, operation: str, file_path: str, result: Dict[str, Any]) -> None:
        """TDD操作の記録"""
        try:
            state = {}
            if self.tdd_state_file.exists():
                with open(self.tdd_state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            
            if "operations_history" not in state:
                state["operations_history"] = []
            
            operation_record = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "file_path": file_path,
                "phase": result["current_phase"],
                "allowed": result["allowed"],
                "message": result["message"]
            }
            
            state["operations_history"].append(operation_record)
            
            # 履歴は最新100件まで保持
            if len(state["operations_history"]) > 100:
                state["operations_history"] = state["operations_history"][-100:]
            
            with open(self.tdd_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"TDD操作記録エラー: {e}", "TDD")
    
    def get_current_phase(self) -> str:
        """現在のTDDフェーズを取得（外部API用）"""
        return self._get_current_tdd_phase().value

# シングルトンインスタンス
tdd_manager = TDDWorkflowManager()