#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合開発システム v1.0
SDD（仕様書駆動開発）+ TDD（テスト駆動開発）統合システム

KISS原則: 最もシンプルで理解しやすい実装
YAGNI原則: 現在必要な機能のみ実装
TDD適合: Red→Green→Refactorサイクルに従う
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from enum import Enum


# 定数定義（KISS原則: 設定は一箇所に）
DEFAULT_TEST_COVERAGE = 80
DEFAULT_RESPONSE_TIME = "3秒以内"
SYSTEM_VERSION = "v1.0"


class DevelopmentFlow(Enum):
    """開発フローの定義"""
    NEW = "new"
    EXISTING = "existing"


class UnifiedSystem:
    """
    統合開発システム
    system.py と sdd_tdd_system.py を統合したシンプルなシステム
    """
    
    def __init__(self, project_name: str):
        """
        初期化
        
        Args:
            project_name: プロジェクト名
        """
        self.project_name = project_name
        self.base_path = Path(__file__).parent.parent
        
        # ディレクトリ構成（KISS: 必要最小限）
        self.specs_dir = self.base_path / "specs" / project_name
        self.workspace_dir = self.base_path / "workspace" / project_name
        self.docs_dir = self.base_path / "docs" / project_name
        
        # 必要なディレクトリを作成
        self._init_directories()
        
        # 現在のフロー情報
        self.current_flow = None
    
    def _init_directories(self):
        """必要なディレクトリを初期化"""
        for dir_path in [self.specs_dir, self.workspace_dir, self.docs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_jst_time(self) -> str:
        """JST時刻を取得"""
        jst = timezone(timedelta(hours=9))
        return datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S JST")
    
    # ==================== SDD（仕様書駆動開発） ====================
    
    def create_requirements_doc(self, user_request: str) -> Dict[str, Any]:
        """
        要件定義書作成
        
        Args:
            user_request: ユーザーからの要求
            
        Returns:
            作成結果
            
        Raises:
            ValueError: user_requestが空の場合
            OSError: ファイル書き込みに失敗した場合
        """
        if not user_request or not user_request.strip():
            raise ValueError("ユーザー要求は空にできません")
        
        doc_path = self.specs_dir / "requirements.md"
        
        content = f"""# 要件定義書

## プロジェクト概要
- **プロジェクト名**: {self.project_name}
- **作成日**: {self.get_jst_time()}
- **バージョン**: 1.0.0

## ユーザー要求
{user_request}

## 機能要件

### 必須機能
- [ ] 機能1: [詳細を記載]
- [ ] 機能2: [詳細を記載]

## 非機能要件

### パフォーマンス
- レスポンスタイム: {DEFAULT_RESPONSE_TIME}

### セキュリティ
- 基本的な入力検証

## 成功基準
- すべての必須機能が実装されている
- テストカバレッジ{DEFAULT_TEST_COVERAGE}%以上

---
*統合開発システム {SYSTEM_VERSION}で生成*
"""
        
        doc_path.write_text(content, encoding='utf-8')
        
        return {
            "status": "completed",
            "path": str(doc_path),
            "type": "requirements"
        }
    
    def create_design_doc(self, requirements: Dict) -> Dict[str, Any]:
        """
        技術設計書作成
        
        Args:
            requirements: 要件定義書の結果
            
        Returns:
            作成結果
        """
        doc_path = self.specs_dir / "design.md"
        
        content = f"""# 技術設計書

## プロジェクト
- **プロジェクト名**: {self.project_name}
- **作成日**: {self.get_jst_time()}
- **要件定義書**: requirements.md

## アーキテクチャ

### システム構成
```
[フロントエンド] <-> [API] <-> [データベース]
```

### 技術スタック
- **バックエンド**: Python
- **テスト**: unittest/pytest

## モジュール設計

### コアモジュール
1. **メインロジック**
   - 主要な処理

## テスト戦略（TDD）
- ユニットテスト: 各関数
- 統合テスト: 全体フロー

---
*統合開発システム {SYSTEM_VERSION}で生成*
"""
        
        doc_path.write_text(content, encoding='utf-8')
        
        return {
            "status": "completed",
            "path": str(doc_path),
            "type": "design"
        }
    
    def create_tasks_doc(self, design: Dict) -> Dict[str, Any]:
        """
        実装計画作成
        
        Args:
            design: 技術設計書の結果
            
        Returns:
            作成結果
        """
        doc_path = self.specs_dir / "tasks.md"
        
        content = f"""# 実装計画

## プロジェクト
- **プロジェクト名**: {self.project_name}
- **作成日**: {self.get_jst_time()}
- **設計書**: design.md

## タスク一覧

### Phase 1: TDD準備
- [ ] テストフレームワーク設定
- [ ] テストケース設計

### Phase 2: TDD実装
- [ ] Red: テスト作成
- [ ] Green: 実装
- [ ] Refactor: リファクタリング

## 完了基準
- [ ] すべてのテストがパス
- [ ] カバレッジ80%以上

---
*統合開発システム {SYSTEM_VERSION}で生成*
"""
        
        doc_path.write_text(content, encoding='utf-8')
        
        return {
            "status": "completed",
            "path": str(doc_path),
            "type": "tasks"
        }
    
    # ==================== TDD（テスト駆動開発） ====================
    
    def create_failing_test(self, feature_name: str) -> str:
        """
        TDD Red Phase: 失敗するテストを作成
        
        Args:
            feature_name: 機能名
            
        Returns:
            テストファイルパス
        """
        test_file = self.workspace_dir / f"test_{feature_name}.py"
        
        test_content = f'''import unittest

class Test{feature_name.capitalize()}(unittest.TestCase):
    """
    TDD Red Phase - 失敗するテスト
    """
    
    def test_{feature_name}_basic(self):
        """基本機能のテスト"""
        # まだ実装されていないので失敗する
        from {feature_name} import main_function
        result = main_function()
        self.assertEqual(result, "expected")

if __name__ == '__main__':
    unittest.main()
'''
        
        test_file.write_text(test_content, encoding='utf-8')
        return str(test_file)
    
    # ==================== 統合フロー ====================
    
    def execute_new_project_flow(self, user_request: str) -> Dict[str, Any]:
        """
        新規プロジェクトの統合フロー実行
        
        Args:
            user_request: ユーザー要求
            
        Returns:
            実行結果
        """
        self.current_flow = DevelopmentFlow.NEW
        
        results = {
            "project": self.project_name,
            "flow": "新規開発",
            "timestamp": self.get_jst_time()
        }
        
        # SDD Phase
        print(f"[SDD] 新規開発フロー開始: {self.project_name}")
        
        results["requirements"] = self.create_requirements_doc(user_request)
        print(f"[OK] 要件定義書: {results['requirements']['path']}")
        
        results["design"] = self.create_design_doc(results["requirements"])
        print(f"[OK] 技術設計書: {results['design']['path']}")
        
        results["tasks"] = self.create_tasks_doc(results["design"])
        print(f"[OK] 実装計画: {results['tasks']['path']}")
        
        # TDD Phase
        print("[TDD] テスト駆動開発フェーズ")
        
        feature_name = "main_feature"
        test_file = self.create_failing_test(feature_name)
        results["tdd_cycle"] = {
            "red_phase": test_file,
            "green_phase": "実装が必要",
            "refactor_phase": "リファクタリング待ち"
        }
        print(f"[OK] TDD Red Phase: {test_file}")
        
        return results
    
    def execute_existing_project_flow(self, target_path: str, modification_request: str) -> Dict[str, Any]:
        """
        既存プロジェクト修正の統合フロー実行（簡素化版）
        
        Args:
            target_path: 対象パス
            modification_request: 修正要求
            
        Returns:
            実行結果
        """
        self.current_flow = DevelopmentFlow.EXISTING
        
        results = {
            "project": target_path,
            "flow": "既存修正",
            "timestamp": self.get_jst_time(),
            "modification_request": modification_request
        }
        
        # 簡素化された修正フロー（KISS原則）
        print(f"[MODIFY] 既存修正フロー開始: {target_path}")
        
        # 1. 簡単な解析
        results["analysis"] = {
            "target": target_path,
            "modification": modification_request,
            "impact": "minimal"
        }
        
        # 2. 修正要件
        results["mod_requirements"] = self.create_requirements_doc(modification_request)
        
        # 3. TDDサイクル
        results["tdd_cycle"] = {
            "red_phase": "修正用テスト作成が必要",
            "green_phase": "修正実装が必要",
            "refactor_phase": "リファクタリング待ち"
        }
        
        return results