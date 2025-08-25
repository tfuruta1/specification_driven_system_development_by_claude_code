#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合開発ルールシステム
DRY原則に基づき、5つの開発ルールモジュールを統合
KISS原則に基づき、シンプルなルールチェック機能を提供
YAGNI原則に基づき、実際に使用されるルールのみ実装
"""

# Auto-generated import setup
import sys
from pathlib import Path

# Setup import paths
current_file = Path(__file__).resolve()
claude_root = None
current = current_file.parent
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    if (current / '.claude').exists():
        claude_root = current / '.claude'
        break
    current = current.parent

if claude_root:
    sys.path.insert(0, str(claude_root / "system"))
    sys.path.insert(0, str(claude_root))

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum

# 既存の共通モジュールを使用（DRY原則）
try:
    from core.common_base import BaseManager, BaseResult, create_result
    from core.logger import get_logger
except ImportError:
    # Direct import for standalone execution
    from common_base import BaseManager, BaseResult, create_result
    from logger import get_logger

logger = get_logger(__name__)


class RuleType(Enum):
    """ルールタイプ（統一）"""
    TDD = "tdd"
    DRY = "dry"
    KISS = "kiss"
    YAGNI = "yagni"
    COVERAGE = "coverage"


@dataclass
class RuleViolation:
    """ルール違反"""
    rule_type: RuleType
    file_path: str
    line_number: Optional[int]
    message: str
    severity: str  # "error", "warning", "info"


class DevRulesUnified(BaseManager):
    """
    統合開発ルールシステム
    必要なルールチェック機能のみを含む（YAGNI原則）
    """
    
    def __init__(self):
        """初期化"""
        super().__init__("DevRulesUnified")
        self.violations: List[RuleViolation] = []
        
    def initialize(self) -> BaseResult:
        """初期化"""
        try:
            logger.info("Initializing Dev Rules Unified System")
            self.violations.clear()
            return create_result(True, "Dev Rules System initialized")
        except Exception as e:
            return create_result(False, f"Initialization failed: {e}")
    
    def cleanup(self) -> BaseResult:
        """クリーンアップ"""
        try:
            self.violations.clear()
            return create_result(True, "Cleanup completed")
        except Exception as e:
            return create_result(False, f"Cleanup failed: {e}")
    
    def check_tdd_compliance(self, file_path: Path) -> List[RuleViolation]:
        """
        TDDコンプライアンスチェック（シンプル化）
        
        Args:
            file_path: チェック対象ファイル
            
        Returns:
            違反リスト
        """
        violations = []
        
        # テストファイルの存在確認
        if file_path.suffix == '.py' and not file_path.name.startswith('test_'):
            test_file = file_path.parent / f"test_{file_path.name}"
            if not test_file.exists():
                violations.append(RuleViolation(
                    rule_type=RuleType.TDD,
                    file_path=str(file_path),
                    line_number=None,
                    message=f"Test file not found: {test_file.name}",
                    severity="warning"
                ))
        
        return violations
    
    def check_dry_compliance(self, content: str, file_path: str) -> List[RuleViolation]:
        """
        DRYコンプライアンスチェック（シンプル化）
        
        Args:
            content: ファイル内容
            file_path: ファイルパス
            
        Returns:
            違反リスト
        """
        violations = []
        lines = content.split('\n')
        
        # 重複コードの簡易検出（3行以上の重複）
        seen_blocks = {}
        for i in range(len(lines) - 2):
            block = '\n'.join(lines[i:i+3]).strip()
            if block and not block.startswith('#'):
                if block in seen_blocks:
                    violations.append(RuleViolation(
                        rule_type=RuleType.DRY,
                        file_path=file_path,
                        line_number=i + 1,
                        message=f"Duplicate code block detected (first seen at line {seen_blocks[block]})",
                        severity="warning"
                    ))
                else:
                    seen_blocks[block] = i + 1
        
        return violations
    
    def check_kiss_compliance(self, content: str, file_path: str) -> List[RuleViolation]:
        """
        KISSコンプライアンスチェック（シンプル化）
        
        Args:
            content: ファイル内容
            file_path: ファイルパス
            
        Returns:
            違反リスト
        """
        violations = []
        lines = content.split('\n')
        
        # 複雑度の簡易チェック
        for i, line in enumerate(lines):
            # ネストレベルチェック（インデント6レベル以上）
            indent_level = (len(line) - len(line.lstrip())) // 4
            if indent_level >= 6:
                violations.append(RuleViolation(
                    rule_type=RuleType.KISS,
                    file_path=file_path,
                    line_number=i + 1,
                    message=f"Deep nesting detected (level {indent_level})",
                    severity="warning"
                ))
            
            # 長い行チェック（120文字以上）
            if len(line.rstrip()) > 120:
                violations.append(RuleViolation(
                    rule_type=RuleType.KISS,
                    file_path=file_path,
                    line_number=i + 1,
                    message=f"Line too long ({len(line.rstrip())} characters)",
                    severity="info"
                ))
        
        return violations
    
    def check_yagni_compliance(self, content: str, file_path: str) -> List[RuleViolation]:
        """
        YAGNIコンプライアンスチェック（シンプル化）
        
        Args:
            content: ファイル内容
            file_path: ファイルパス
            
        Returns:
            違反リスト
        """
        violations = []
        
        # 未使用コードの簡易検出
        if 'TODO' in content or 'FIXME' in content or 'HACK' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if any(marker in line for marker in ['TODO', 'FIXME', 'HACK']):
                    violations.append(RuleViolation(
                        rule_type=RuleType.YAGNI,
                        file_path=file_path,
                        line_number=i + 1,
                        message="Unfinished code marker found",
                        severity="info"
                    ))
        
        # 未使用インポートの簡易検出
        if 'import' in content:
            # この実装は簡易版です
            pass
        
        return violations
    
    def check_file(self, file_path: Path) -> BaseResult:
        """
        ファイルの包括的チェック
        
        Args:
            file_path: チェック対象ファイル
            
        Returns:
            チェック結果
        """
        try:
            violations = []
            
            # ファイル読み込み
            if file_path.exists() and file_path.suffix == '.py':
                content = file_path.read_text(encoding='utf-8')
                
                # 各ルールチェック
                violations.extend(self.check_tdd_compliance(file_path))
                violations.extend(self.check_dry_compliance(content, str(file_path)))
                violations.extend(self.check_kiss_compliance(content, str(file_path)))
                violations.extend(self.check_yagni_compliance(content, str(file_path)))
            
            # 結果を保存
            self.violations.extend(violations)
            
            if violations:
                return create_result(
                    False,
                    f"Found {len(violations)} violations",
                    {"violations": violations}
                )
            else:
                return create_result(True, "No violations found")
                
        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")
            return create_result(False, f"Check failed: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        違反サマリー取得
        
        Returns:
            サマリー情報
        """
        summary = {
            "total_violations": len(self.violations),
            "by_type": {},
            "by_severity": {
                "error": 0,
                "warning": 0,
                "info": 0
            }
        }
        
        # タイプ別集計
        for rule_type in RuleType:
            count = sum(1 for v in self.violations if v.rule_type == rule_type)
            if count > 0:
                summary["by_type"][rule_type.value] = count
        
        # 重要度別集計
        for violation in self.violations:
            summary["by_severity"][violation.severity] += 1
        
        return summary


def main():
    """メインエントリーポイント"""
    rules = DevRulesUnified()
    
    # 初期化
    result = rules.initialize()
    print(f"Initialization: {result.message}")
    
    # サンプルチェック
    test_file = Path(__file__)
    result = rules.check_file(test_file)
    print(f"Check result: {result.message}")
    
    # サマリー表示
    summary = rules.get_summary()
    print(f"Violations summary: {summary}")
    
    # クリーンアップ
    result = rules.cleanup()
    print(f"Cleanup: {result.message}")


if __name__ == "__main__":
    main()