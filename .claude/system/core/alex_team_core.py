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
import copy


class TaskStatus(Enum):
    """Task execution status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class VoteResult(Enum):
    """Team voting result enumeration"""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


class EngineerRole(Enum):
    """Engineer role definitions for Alex Team"""
    ALEX_LEAD = "alex-sdd-tdd-lead"  # Team Lead / CTO role
    OPTIMIZER = "code-optimizer-engineer"
    QA_DOC = "qa-doc-engineer"
    TDD_TEST = "tdd-test-engineer"


@dataclass
class TaskAssignment:
    """Task assignment data structure"""
    engineer: EngineerRole
    task_type: str
    description: str
    priority: int
    dependencies: List[str] = field(default_factory=list)


@dataclass
class EngineerTask:
    """Individual engineer task with execution details"""
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
    """Collaborative team task with voting and iteration tracking"""
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
    """Configuration constants and team structure for Alex Team"""
    
    ENGINEERS = {
        "alex-sdd-tdd-lead": {
            "name": "Alex - Team Lead/CTO",
            "specialties": [
                "System Architecture Design",
                "TDD/SDD Leadership",
                "Code Review & Quality Assurance",
                "Team Coordination",
                "Performance Optimization",
                "Risk Management",
                "Strategic Planning"
            ],
            "responsibilities": [
                "Overall project leadership",
                "Architecture decision making",
                "Code quality enforcement",
                "Team coordination",
                "Final approval authority"
            ]
        },
        "code-optimizer-engineer": {
            "name": "Code Optimization Engineer",
            "specialties": [
                "Performance Analysis",
                "Memory Optimization", 
                "Algorithm Efficiency",
                "Refactoring Techniques",
                "KISS/DRY Principles"
            ],
            "responsibilities": [
                "Code performance optimization",
                "Memory usage analysis",
                "Algorithm improvement"
            ]
        },
        "qa-doc-engineer": {
            "name": "QA/Documentation Engineer", 
            "specialties": [
                "Quality Assurance",
                "Test Planning",
                "API Documentation",
                "User Documentation",
                "Compliance Testing"
            ],
            "responsibilities": [
                "Quality assurance processes",
                "Documentation maintenance",
                "Test strategy development"
            ]
        },
        "tdd-test-engineer": {
            "name": "TDD Test Engineer",
            "specialties": [
                "Unit Testing",
                "Integration Testing", 
                "TDD Red-Green-Refactor",
                "Test Automation",
                "Coverage Analysis"
            ],
            "responsibilities": [
                "Test case development",
                "TDD cycle implementation",
                "Test coverage monitoring"
            ]
        }
    }
    
    VOTING_RULES = {
        "quorum": 3,  # Minimum voters required
        "approval_threshold": 0.75,  # 75% approval needed
        "alex_lead_veto": True,  # Lead can veto decisions
        "required_voters": ["alex-sdd-tdd-lead", "qa-doc-engineer", "tdd-test-engineer"]  # Core voting members
    }
    
    QUALITY_THRESHOLDS = {
        "performance": {
            "max_execution_time": 30.0,  # Maximum execution time in seconds
            "memory_efficiency": 0.8,    # Memory efficiency threshold (80%)
            "code_coverage": 0.95        # Required code coverage (95%)
        },
        "code_quality": {
            "complexity_score": 10,      # Maximum cyclomatic complexity
            "duplication_ratio": 0.05,   # Maximum code duplication (5%)
            "maintainability": 0.9       # Minimum maintainability score
        }
    }
    
    TASK_PRIORITIES = {
        "CRITICAL": 1,
        "HIGH": 2,
        "MEDIUM": 3,
        "LOW": 4
    }


# Factory functions for creating task instances
def create_engineer_task(engineer_type: str, description: str, priority: int = 3) -> EngineerTask:
    """Create a new EngineerTask instance with specified parameters"""
    return EngineerTask(
        engineer_type=engineer_type,
        task_description=description,
        priority=priority
    )


def create_team_task(task_id: str, objective: str) -> TeamTask:
    """Create a new TeamTask instance with specified parameters"""
    return TeamTask(
        task_id=task_id,
        main_objective=objective
    )


def get_engineer_info(engineer_role: str) -> Dict[str, Any]:
    """Get engineer configuration information by role"""
    return AlexTeamConfig.ENGINEERS.get(engineer_role, {})


def get_voting_rules() -> Dict[str, Any]:
    """Get a copy of team voting rules"""
    return copy.deepcopy(AlexTeamConfig.VOTING_RULES)


def get_quality_thresholds() -> Dict[str, Any]:
    """Get a copy of quality threshold configurations"""
    return copy.deepcopy(AlexTeamConfig.QUALITY_THRESHOLDS)