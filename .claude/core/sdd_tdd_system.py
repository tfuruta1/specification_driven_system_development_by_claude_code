#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDD+TDD統合開発システム
仕様書駆動開発（SDD）とテスト駆動開発（TDD）の統合
参考: https://kiro.dev/docs/specs/
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from logger import logger


class SDDTDDSystem:
    """SDD+TDD統合開発システム"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.base_path = Path(__file__).parent.parent
        self.specs_dir = self.base_path / "specs" / project_name
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        
        # 3つの必須ドキュメント
        self.docs = {
            "requirements": self.specs_dir / "requirements.md",
            "design": self.specs_dir / "design.md",
            "tasks": self.specs_dir / "tasks.md"
        }
        
    # ==================== SDD（仕様書駆動開発） ====================
    
    def create_requirements_doc(self, user_request: str) -> Dict[str, Any]:
        """
        要件定義書（requirements.md）作成
        参考: https://kiro.dev/docs/specs/
        """
        logger.info(f"要件定義書作成開始: {self.project_name}", "SDD")
        
        content = f"""# 要件定義書

## プロジェクト概要
- **プロジェクト名**: {self.project_name}
- **作成日**: {datetime.now().strftime('%Y-%m-%d')}
- **バージョン**: 1.0.0

## ビジネス要求
{user_request}

## 機能要件

### 必須機能（Must Have）
- [ ] 機能1: [詳細を記載]
- [ ] 機能2: [詳細を記載]

### あると良い機能（Nice to Have）
- [ ] 機能3: [詳細を記載]

## 非機能要件

### パフォーマンス
- レスポンスタイム: 3秒以内
- 同時接続数: 100ユーザー

### セキュリティ
- 認証・認可の実装
- データ暗号化

### 可用性
- 稼働率: 99.9%
- バックアップ: 日次

## 制約事項
- 技術スタック: Python/JavaScript
- 開発期間: [期間を記載]
- 予算: [予算を記載]

## 成功基準
- すべての必須機能が実装されている
- テストカバレッジ80%以上
- パフォーマンス要件を満たす

---
*このドキュメントはSDD（仕様書駆動開発）プロセスの一部です*
*参考: https://kiro.dev/docs/specs/*
"""
        
        self.docs["requirements"].write_text(content, encoding='utf-8')
        logger.info(f"要件定義書作成完了: {self.docs['requirements']}", "SDD")
        
        return {
            "status": "completed",
            "path": str(self.docs["requirements"]),
            "type": "requirements"
        }
    
    def create_design_doc(self, requirements: Dict) -> Dict[str, Any]:
        """
        技術設計書（design.md）作成
        """
        logger.info(f"技術設計書作成開始: {self.project_name}", "SDD")
        
        content = f"""# 技術設計書

## プロジェクト
- **プロジェクト名**: {self.project_name}
- **作成日**: {datetime.now().strftime('%Y-%m-%d')}
- **要件定義書**: requirements.md

## アーキテクチャ

### システム構成図
```
[フロントエンド] <-> [API] <-> [データベース]
```

### 技術スタック
- **フロントエンド**: HTML/CSS/JavaScript
- **バックエンド**: Python (FastAPI/Flask)
- **データベース**: SQLite/PostgreSQL
- **テスト**: pytest/unittest

## モジュール設計

### コアモジュール
1. **認証モジュール**
   - ユーザー認証
   - セッション管理

2. **ビジネスロジック**
   - [主要な処理を記載]

3. **データアクセス層**
   - ORM/SQL

## API設計

### エンドポイント
| メソッド | パス | 説明 |
|---------|------|------|
| GET | /api/items | 一覧取得 |
| POST | /api/items | 新規作成 |
| PUT | /api/items/{id} | 更新 |
| DELETE | /api/items/{id} | 削除 |

## データベース設計

### テーブル構造
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    created_at TIMESTAMP
);
```

## セキュリティ設計
- JWT認証
- HTTPS通信
- 入力値検証

## テスト戦略（TDD）
- ユニットテスト: 各関数
- 統合テスト: API
- E2Eテスト: ユーザーシナリオ

---
*このドキュメントはSDD（仕様書駆動開発）プロセスの一部です*
"""
        
        self.docs["design"].write_text(content, encoding='utf-8')
        logger.info(f"技術設計書作成完了: {self.docs['design']}", "SDD")
        
        return {
            "status": "completed",
            "path": str(self.docs["design"]),
            "type": "design"
        }
    
    def create_tasks_doc(self, design: Dict) -> Dict[str, Any]:
        """
        実装計画（tasks.md）作成
        """
        logger.info(f"実装計画作成開始: {self.project_name}", "SDD")
        
        content = f"""# 実装計画

## プロジェクト
- **プロジェクト名**: {self.project_name}
- **作成日**: {datetime.now().strftime('%Y-%m-%d')}
- **設計書**: design.md

## タスク一覧

### Phase 1: 基盤構築
- [ ] プロジェクト初期設定
- [ ] 開発環境構築
- [ ] CI/CD設定

### Phase 2: TDD準備
- [ ] テストフレームワーク設定
- [ ] テストケース設計
- [ ] モックデータ準備

### Phase 3: コア機能実装（TDD）
各機能をRed-Green-Refactorサイクルで実装

#### 3.1 認証機能
- [ ] テスト作成（Red）
- [ ] 実装（Green）
- [ ] リファクタリング（Refactor）

#### 3.2 CRUD機能
- [ ] テスト作成（Red）
- [ ] 実装（Green）
- [ ] リファクタリング（Refactor）

### Phase 4: 統合
- [ ] API統合テスト
- [ ] フロントエンド統合
- [ ] E2Eテスト

### Phase 5: 最終確認
- [ ] パフォーマンステスト
- [ ] セキュリティ監査
- [ ] ドキュメント更新

## タイムライン
| フェーズ | 期間 | 状態 |
|---------|------|------|
| Phase 1 | 1日 | 未着手 |
| Phase 2 | 1日 | 未着手 |
| Phase 3 | 3日 | 未着手 |
| Phase 4 | 1日 | 未着手 |
| Phase 5 | 1日 | 未着手 |

## 完了基準
- [ ] すべてのテストがパス
- [ ] カバレッジ80%以上
- [ ] ドキュメント完備
- [ ] コードレビュー完了

---
*このドキュメントはSDD+TDD統合開発プロセスの一部です*
"""
        
        self.docs["tasks"].write_text(content, encoding='utf-8')
        logger.info(f"実装計画作成完了: {self.docs['tasks']}", "SDD")
        
        return {
            "status": "completed",
            "path": str(self.docs["tasks"]),
            "type": "tasks"
        }
    
    # ==================== TDD（テスト駆動開発） ====================
    
    def create_test_first(self, feature_name: str) -> str:
        """
        TDD: テストファースト（Red Phase）
        """
        logger.info(f"TDD Red Phase: {feature_name}", "TDD")
        
        test_file = self.specs_dir / f"test_{feature_name}.py"
        test_content = f'''import pytest
import unittest

class Test{feature_name.capitalize()}(unittest.TestCase):
    """
    TDD: Red Phase - テストを先に書く
    このテストは最初は失敗する（Red）
    """
    
    def setUp(self):
        """テストセットアップ"""
        pass
    
    def test_{feature_name}_exists(self):
        """機能が存在することを確認"""
        # TODO: 実装前なので失敗する
        from {feature_name} import main_function
        self.assertIsNotNone(main_function)
    
    def test_{feature_name}_basic_functionality(self):
        """基本機能のテスト"""
        # TODO: 期待される動作を記述
        expected = "expected_result"
        # actual = function_under_test()
        # self.assertEqual(expected, actual)
        pass
    
    def test_{feature_name}_edge_cases(self):
        """エッジケースのテスト"""
        # TODO: 境界値、異常系のテスト
        pass

if __name__ == '__main__':
    # TDD: まず失敗することを確認（Red）
    unittest.main()
'''
        
        test_file.write_text(test_content, encoding='utf-8')
        return str(test_file)
    
    def implement_to_pass_tests(self, feature_name: str, test_file: str) -> str:
        """
        TDD: 実装（Green Phase）
        テストが通る最小限の実装
        """
        logger.info(f"TDD Green Phase: {feature_name}", "TDD")
        
        impl_file = self.specs_dir / f"{feature_name}.py"
        impl_content = f'''"""
TDD: Green Phase - テストを通す最小限の実装
"""

def main_function():
    """テストを通すための最小実装"""
    return "expected_result"

# 追加の実装...
'''
        
        impl_file.write_text(impl_content, encoding='utf-8')
        return str(impl_file)
    
    def refactor_code(self, impl_file: str) -> str:
        """
        TDD: リファクタリング（Refactor Phase）
        テストが通る状態を保ちながら改善
        """
        logger.info(f"TDD Refactor Phase", "TDD")
        
        # リファクタリング指針
        refactor_checklist = """
        ## リファクタリングチェックリスト
        - [ ] 重複コードの除去（DRY）
        - [ ] 関数の単一責任化（SRP）
        - [ ] 変数名の改善
        - [ ] コメントの追加
        - [ ] パフォーマンス最適化
        - [ ] エラーハンドリング追加
        """
        
        return refactor_checklist
    
    # ==================== 統合実行 ====================
    
    def execute_sdd_tdd_flow(self, user_request: str) -> Dict[str, Any]:
        """
        SDD+TDD統合フロー実行
        """
        logger.info("SDD+TDD統合フロー開始", "SYSTEM")
        
        results = {}
        
        # SDD Phase
        print("\n" + "="*60)
        print("[SDD] 仕様書駆動開発フェーズ")
        print("="*60)
        
        # 1. 要件定義書
        results["requirements"] = self.create_requirements_doc(user_request)
        print(f"[OK] 要件定義書作成: {results['requirements']['path']}")
        
        # 2. 技術設計書
        results["design"] = self.create_design_doc(results["requirements"])
        print(f"[OK] 技術設計書作成: {results['design']['path']}")
        
        # 3. 実装計画
        results["tasks"] = self.create_tasks_doc(results["design"])
        print(f"[OK] 実装計画作成: {results['tasks']['path']}")
        
        # TDD Phase
        print("\n" + "="*60)
        print("[TDD] テスト駆動開発フェーズ")
        print("="*60)
        
        # 4. Red-Green-Refactor
        feature_name = "main_feature"
        
        print("\n[RED] Red Phase: テスト作成")
        test_file = self.create_test_first(feature_name)
        results["test"] = test_file
        print(f"[OK] テストファイル作成: {test_file}")
        
        print("\n[GREEN] Green Phase: 実装")
        impl_file = self.implement_to_pass_tests(feature_name, test_file)
        results["implementation"] = impl_file
        print(f"[OK] 実装ファイル作成: {impl_file}")
        
        print("\n[REFACTOR] Refactor Phase: リファクタリング")
        refactor = self.refactor_code(impl_file)
        print(refactor)
        
        print("\n" + "="*60)
        print("✨ SDD+TDD統合フロー完了")
        print("="*60)
        
        return results


# デモ実行
def demo():
    """SDD+TDDデモ"""
    system = SDDTDDSystem("sample_project")
    results = system.execute_sdd_tdd_flow("ユーザー管理システムを作りたい")
    
    print("\n📊 生成されたドキュメント:")
    for doc_type, info in results.items():
        if isinstance(info, dict) and 'path' in info:
            print(f"  - {doc_type}: {info['path']}")
        else:
            print(f"  - {doc_type}: {info}")


if __name__ == "__main__":
    demo()