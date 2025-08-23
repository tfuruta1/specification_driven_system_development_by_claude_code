#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存解析フローテスト - Claude Code Core v12.0
既存コードベース解析フローの包括的なテスト
"""

import unittest
from unittest.mock import patch
from pathlib import Path
from test_base import BaseTestFlow
from file_access_logger import AccessPurpose
from integration_test_runner import CircularImportDetector

class TestExistingAnalysisFlow(BaseTestFlow):
    """既存解析フローのテスト"""
    
    @patch('builtins.input', return_value='2')
    def test_existing_analysis_flow(self, mock_input):
        """既存解析フローのテスト"""
        print("\n=== 既存解析フローテスト ===")
        
        # 1. AutoMode開始（既存解析を選択）
        session_id = self.start_session_with_flow('2')
        print(f"[OK] セッション開始: {session_id}")
        
        # 2. フロー確認
        self.assertEqual(self.auto_mode.config.current_flow, '既存解析')
        print(f"[OK] フロー設定: 既存解析")
        
        # 3. 既存ファイルの解析シミュレーション
        existing_files = [
            "main.py", "utils.py", "config.py", "database.py",
            "api.py", "models.py", "views.py", "tests.py"
        ]
        
        for file in existing_files:
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.ANALYZE, 
                f"既存コード解析: {file}"
            )
        print(f"[OK] {len(existing_files)}個のファイルを解析")
        
        # 4. 依存関係の分析
        detector = CircularImportDetector()
        detector.visited_modules = {
            'main': ['utils', 'config', 'api'],
            'utils': ['config'],
            'config': [],
            'api': ['models', 'database'],
            'models': ['database'],
            'database': ['config'],
            'views': ['models', 'api'],
            'tests': ['main', 'utils', 'models']
        }
        
        cycles = detector.detect()
        print(f"[OK] 循環参照検出: {len(cycles)}個")
        
        # 5. ドキュメント生成
        self.file_logger.log_file_access(
            "analysis_report.md", 
            AccessPurpose.MODIFY, 
            "解析レポート作成"
        )
        self.file_logger.log_file_access(
            "architecture.md", 
            AccessPurpose.MODIFY, 
            "アーキテクチャ図作成"
        )
        print(f"[OK] 解析ドキュメント生成")
        
        # 6. 解析結果の確認
        analyze_count = sum(1 for h in self.file_logger.access_history 
                           if h['purpose'] == AccessPurpose.ANALYZE)
        self.assertGreater(analyze_count, 5)
        print(f"[OK] 解析ファイル数: {analyze_count}")
        
        # 7. セッション終了
        self.stop_session()
        print(f"[OK] セッション終了")
    
    @patch('builtins.input', return_value='2')
    def test_deep_code_analysis(self, mock_input):
        """詳細コード解析テスト"""
        print("\n=== 詳細コード解析テスト ===")
        
        session_id = self.start_session_with_flow('2')
        
        # 詳細解析対象ファイル
        analysis_targets = [
            ("core/main.py", "メインモジュール解析"),
            ("core/database.py", "データベースモジュール解析"),
            ("core/api.py", "APIモジュール解析"),
            ("utils/helpers.py", "ユーティリティモジュール解析"),
            ("models/user.py", "ユーザーモデル解析"),
            ("models/product.py", "プロダクトモデル解析"),
            ("tests/test_main.py", "メインテスト解析"),
            ("tests/test_database.py", "データベーステスト解析")
        ]
        
        for file_path, description in analysis_targets:
            # コード解析
            self.file_logger.log_file_access(
                file_path, 
                AccessPurpose.ANALYZE, 
                description
            )
            
            # メトリクス収集シミュレーション
            self.file_logger.log_file_access(
                file_path, 
                AccessPurpose.REFERENCE, 
                f"{description} - 複雑度測定"
            )
            
            print(f"[OK] {description}完了")
        
        # 解析レポート生成
        reports = [
            "complexity_report.md",
            "dependency_graph.md", 
            "code_quality_report.md",
            "security_analysis.md"
        ]
        
        for report in reports:
            self.file_logger.log_file_access(
                report, 
                AccessPurpose.MODIFY, 
                f"解析レポート生成: {report}"
            )
        
        print("[OK] 全解析レポート生成完了")
        
        self.stop_session()
    
    @patch('builtins.input', return_value='2')
    def test_legacy_code_analysis(self, mock_input):
        """レガシーコード解析テスト"""
        print("\n=== レガシーコード解析テスト ===")
        
        session_id = self.start_session_with_flow('2')
        
        # レガシーファイル解析
        legacy_files = [
            "legacy/old_system.py",
            "legacy/deprecated_api.py", 
            "legacy/legacy_database.py",
            "legacy/old_utils.py",
            "legacy/abandoned_features.py"
        ]
        
        for file in legacy_files:
            # レガシーコード解析
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.ANALYZE, 
                f"レガシーコード解析: {file}"
            )
            
            # 移行可能性評価
            self.file_logger.log_file_access(
                file, 
                AccessPurpose.REFERENCE, 
                f"移行可能性評価: {file}"
            )
        
        print(f"[OK] {len(legacy_files)}個のレガシーファイル解析完了")
        
        # 移行計画書作成
        migration_docs = [
            "migration_plan.md",
            "refactoring_strategy.md",
            "risk_assessment.md"
        ]
        
        for doc in migration_docs:
            self.file_logger.log_file_access(
                doc, 
                AccessPurpose.MODIFY, 
                f"移行ドキュメント作成: {doc}"
            )
        
        print("[OK] 移行計画書作成完了")
        
        self.stop_session()

if __name__ == '__main__':
    unittest.main()