#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Team Core - Core data structures and definitions
Extracted from alex_team_system_v2.py for better modularity

Split from original alex_team_system_v2.py (685 lines) following single responsibility principle
Focus: Core data structures, enums, and basic team configuration
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    """タスクステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class VoteResult(Enum):
    """投票結果"""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


class EngineerRole(Enum):
    """エンジニアロール（CTOを削除）"""
    ALEX_LEAD = "alex-sdd-tdd-lead"  # 旧CTOの責務を統合
    OPTIMIZER = "code-optimizer-engineer"
    QA_DOC = "qa-doc-engineer"
    TDD_TEST = "tdd-test-engineer"


@dataclass
class TaskAssignment:
    """タスク割り当て"""
    engineer: EngineerRole
    task_type: str
    description: str
    priority: int
    dependencies: List[str] = field(default_factory=list)


@dataclass
class EngineerTask:
    """エンジニア個別タスク"""
    engineer_type: str
    task_description: str
    priority: int
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    quality_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass 
class TeamTask:
    """チーム全体タスク"""
    task_id: str
    main_objective: str
    engineer_tasks: Dict[str, EngineerTask] = field(default_factory=dict)
    iteration_count: int = 0
    max_iterations: int = 3
    final_votes: Dict[str, VoteResult] = field(default_factory=dict)
    completion_status: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class AlexTeamConfig:
    """アレックスチーム設定定数クラス"""
    
    ENGINEERS = {
        "alex-sdd-tdd-lead": {
            "name": "アレックス（統括リーダー/元CTO業務統合）",
            "specialties": [
                "全体アーキテクチャ設計",
                "TDD/SDD実装戦略",
                "ペアプログラミング指揮",
                "技術的意思決定",
                "コードレビュー統括",
                "リファクタリング戦略",
                "チーム調整"
            ],
            "responsibilities": [
                "プロジェクト全体の技術的方向性決定",
                "アーキテクチャ設計と実装",
                "チームメンバーへのタスク割り当て",
                "品質基準の設定と監督",
                "最終的な技術判断"
            ]
        },
        "code-optimizer-engineer": {
            "name": "最適化エンジニア",
            "specialties": [
                "パフォーマンス最適化",
                "重複コード削除", 
                "メモリ効率化",
                "ファイル分割",
                "KISS/DRY原則適用"
            ],
            "responsibilities": [
                "コード品質の向上",
                "パフォーマンスボトルネック解消",
                "リファクタリング実施"
            ]
        },
        "qa-doc-engineer": {
            "name": "QA/ドキュメントエンジニア", 
            "specialties": [
                "品質保証",
                "循環依存検出",
                "API文書化",
                "テストカバレッジ分析",
                "メトリクス測定"
            ],
            "responsibilities": [
                "品質チェックと検証",
                "ドキュメント作成と管理",
                "品質レポート作成"
            ]
        },
        "tdd-test-engineer": {
            "name": "TDDテストエンジニア",
            "specialties": [
                "単体テスト設計実装",
                "統合テスト設計実装", 
                "TDD Red-Green-Refactor",
                "テストスイート管理",
                "テストデータ生成"
            ],
            "responsibilities": [
                "テストコードの作成と管理",
                "テスト戦略の策定",
                "品質メトリクス測定"
            ]
        }
    }
    
    VOTING_RULES = {
        "quorum": 3,  # 最低投票数
        "approval_threshold": 0.75,  # 承認閾値 (75%)
        "alex_lead_veto": True,  # リーダーの拒否権
        "required_voters": ["alex-sdd-tdd-lead", "qa-doc-engineer", "tdd-test-engineer"]  # 必須投票者
    }
    
    QUALITY_THRESHOLDS = {
        "performance": {
            "max_execution_time": 30.0,  # 最大実行時間(秒)
            "memory_efficiency": 0.8,    # メモリ効率(%)
            "code_coverage": 0.95        # コードカバレッジ(%)
        },
        "code_quality": {
            "complexity_score": 10,      # 最大複雑度
            "duplication_ratio": 0.05,   # 重複コード率(%)
            "maintainability": 0.9       # 保守性指数
        }
    }
    
    TASK_PRIORITIES = {
        "CRITICAL": 1,
        "HIGH": 2,
        "MEDIUM": 3,
        "LOW": 4
    }


# 互換性のためのヘルパー関数
def create_engineer_task(engineer_type: str, description: str, priority: int = 3) -> EngineerTask:
    """エンジニアタスクを作成（互換性関数）"""
    return EngineerTask(
        engineer_type=engineer_type,
        task_description=description,
        priority=priority
    )


def create_team_task(task_id: str, objective: str) -> TeamTask:
    """チームタスクを作成（互換性関数）"""
    return TeamTask(
        task_id=task_id,
        main_objective=objective
    )


def get_engineer_info(engineer_role: str) -> Dict[str, Any]:
    """エンジニア情報を取得（互換性関数）"""
    return AlexTeamConfig.ENGINEERS.get(engineer_role, {})


def get_voting_rules() -> Dict[str, Any]:
    """投票ルールを取得（互換性関数）"""
    return AlexTeamConfig.VOTING_RULES.copy()


def get_quality_thresholds() -> Dict[str, Any]:
    """品質閾値を取得（互換性関数）"""
    return AlexTeamConfig.QUALITY_THRESHOLDS.copy()