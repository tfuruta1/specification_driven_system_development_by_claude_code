#!/usr/bin/env python3
"""
階層型エージェントシステム - マルチエージェントコードレビューシステム
3人の専門レビュアーによる並列コードレビュー
"""

import os
import sys
import time
import json
import threading
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from jst_config import format_jst_datetime, format_jst_timestamp

class Severity(Enum):
    """問題の重要度"""
    CRITICAL = "🔴 Critical"  # 必ず修正が必要
    WARNING = "🟡 Warning"    # 修正を推奨
    SUGGESTION = "🔵 Suggestion"  # 改善提案

@dataclass
class ReviewComment:
    """レビューコメント"""
    file: str
    line: int
    severity: Severity
    category: str
    message: str
    reviewer: str
    suggestion: Optional[str] = None

class BaseReviewer:
    """基本レビュアークラス"""
    
    def __init__(self, name: str, emoji: str):
        self.name = name
        self.emoji = emoji
        self.comments = []
        
    def review_file(self, file_path: Path) -> List[ReviewComment]:
        """ファイルをレビュー"""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            return []
        
        self.comments = []
        self._analyze_code(file_path, lines)
        return self.comments
    
    def _analyze_code(self, file_path: Path, lines: List[str]):
        """コードを解析（サブクラスで実装）"""
        pass
    
    def add_comment(self, file: str, line: int, severity: Severity, 
                   category: str, message: str, suggestion: str = None):
        """コメントを追加"""
        self.comments.append(ReviewComment(
            file=file,
            line=line,
            severity=severity,
            category=category,
            message=message,
            reviewer=self.name,
            suggestion=suggestion
        ))

class QualityReviewer(BaseReviewer):
    """📝 基本品質レビュアー：誤字脱字、命名規則、コーディングスタイル"""
    
    def __init__(self):
        super().__init__("基本品質レビュアー", "📝")
        self.naming_patterns = {
            'python': {
                'class': r'^[A-Z][a-zA-Z0-9]*$',  # PascalCase
                'function': r'^[a-z_][a-z0-9_]*$',  # snake_case
                'constant': r'^[A-Z][A-Z0-9_]*$',  # UPPER_SNAKE_CASE
            },
            'javascript': {
                'class': r'^[A-Z][a-zA-Z0-9]*$',  # PascalCase
                'function': r'^[a-z][a-zA-Z0-9]*$',  # camelCase
                'constant': r'^[A-Z][A-Z0-9_]*$',  # UPPER_SNAKE_CASE
            }
        }
    
    def _analyze_code(self, file_path: Path, lines: List[str]):
        """基本品質をチェック"""
        file_ext = file_path.suffix.lower()
        
        for i, line in enumerate(lines, 1):
            # 長すぎる行のチェック
            if len(line.rstrip()) > 120:
                self.add_comment(
                    str(file_path), i, Severity.WARNING,
                    "コーディングスタイル",
                    f"行が長すぎます（{len(line.rstrip())}文字）。120文字以内に収めてください。"
                )
            
            # TODO/FIXMEコメントのチェック
            if "TODO" in line or "FIXME" in line:
                self.add_comment(
                    str(file_path), i, Severity.SUGGESTION,
                    "未完了タスク",
                    "TODO/FIXMEコメントが残っています。"
                )
            
            # 日本語コメントの推奨（階層型エージェントシステム用）
            if file_ext in ['.py', '.js'] and '#' in line:
                comment_part = line.split('#')[1] if '#' in line else ""
                if comment_part and not any(ord(c) > 127 for c in comment_part):
                    self.add_comment(
                        str(file_path), i, Severity.SUGGESTION,
                        "ドキュメント",
                        "階層型エージェントシステムでは日本語コメントを推奨します。"
                    )
            
            # デバッグコードのチェック
            debug_patterns = ['console.log', 'print(', 'debugger', 'var_dump']
            for pattern in debug_patterns:
                if pattern in line and not line.strip().startswith('#'):
                    self.add_comment(
                        str(file_path), i, Severity.WARNING,
                        "デバッグコード",
                        f"デバッグコード（{pattern}）が残っています。"
                    )
            
            # インデントの一貫性チェック
            if line.startswith(' ') and not line.startswith('    '):
                self.add_comment(
                    str(file_path), i, Severity.WARNING,
                    "インデント",
                    "インデントは4スペースを使用してください。"
                )

class ArchitectureReviewer(BaseReviewer):
    """🏗️ アーキテクチャレビュアー：SOLID原則、設計パターン、レイヤー構造"""
    
    def __init__(self):
        super().__init__("アーキテクチャレビュアー", "🏗️")
        self.class_metrics = {}
    
    def _analyze_code(self, file_path: Path, lines: List[str]):
        """アーキテクチャをチェック"""
        content = ''.join(lines)
        
        # クラスの責任範囲チェック（Single Responsibility Principle）
        if file_path.suffix == '.py':
            classes = re.findall(r'class\s+(\w+)', content)
            for class_name in classes:
                methods = re.findall(rf'class\s+{class_name}.*?\n(.*?)(?=class\s+\w+|$)', 
                                    content, re.DOTALL)
                if methods:
                    method_count = len(re.findall(r'def\s+\w+', methods[0]))
                    if method_count > 10:
                        self.add_comment(
                            str(file_path), 0, Severity.WARNING,
                            "SOLID原則（SRP）",
                            f"クラス{class_name}のメソッド数が{method_count}個あります。" +
                            "単一責任の原則に違反している可能性があります。",
                            "機能ごとにクラスを分割することを検討してください。"
                        )
        
        # 依存性注入の確認（Dependency Inversion Principle）
        if 'import' in content:
            concrete_imports = re.findall(r'from\s+[\w.]+\s+import\s+\w+', content)
            if len(concrete_imports) > 5:
                self.add_comment(
                    str(file_path), 0, Severity.SUGGESTION,
                    "SOLID原則（DIP）",
                    "具象クラスへの直接的な依存が多いです。",
                    "インターフェースや抽象クラスを使用した依存性注入を検討してください。"
                )
        
        # レイヤー構造の確認
        file_path_str = str(file_path)
        if 'models' in file_path_str and ('api' in content or 'controller' in content):
            self.add_comment(
                str(file_path), 0, Severity.WARNING,
                "レイヤー違反",
                "モデル層からコントローラー層への参照があります。",
                "レイヤー間の依存関係を見直してください。"
            )
        
        # ファイルサイズのチェック
        if len(lines) > 500:
            self.add_comment(
                str(file_path), 0, Severity.WARNING,
                "ファイルサイズ",
                f"ファイルが{len(lines)}行と大きすぎます。",
                "機能ごとにファイルを分割することを検討してください。"
            )
        
        # 循環参照の可能性チェック
        imports = re.findall(r'(?:from|import)\s+([\w.]+)', content)
        current_module = file_path.stem
        for imp in imports:
            if current_module in imp:
                self.add_comment(
                    str(file_path), 0, Severity.CRITICAL,
                    "循環参照",
                    f"潜在的な循環参照が検出されました: {imp}",
                    "モジュール間の依存関係を見直してください。"
                )

class DDDReviewer(BaseReviewer):
    """🎯 DDDレビュアー：ドメインモデル、境界コンテキスト、ユビキタス言語"""
    
    def __init__(self):
        super().__init__("DDDレビュアー", "🎯")
        self.domain_terms = {
            'agent': 'エージェント',
            'department': '部門',
            'cto': 'CTO',
            'review': 'レビュー',
            'specification': '仕様書',
            'implementation': '実装'
        }
    
    def _analyze_code(self, file_path: Path, lines: List[str]):
        """DDD観点でチェック"""
        content = ''.join(lines)
        
        # エンティティとバリューオブジェクトの区別
        if 'class' in content:
            classes = re.findall(r'class\s+(\w+)', content)
            for class_name in classes:
                # IDを持つクラスはエンティティ
                if re.search(rf'class\s+{class_name}.*?\n.*?self\.id', content, re.DOTALL):
                    if not re.search(rf'def\s+__eq__.*?self\.id', content, re.DOTALL):
                        self.add_comment(
                            str(file_path), 0, Severity.WARNING,
                            "DDD - エンティティ",
                            f"{class_name}はエンティティですが、同一性の比較が実装されていません。",
                            "__eq__メソッドでIDによる比較を実装してください。"
                        )
        
        # ユビキタス言語の使用確認
        for eng_term, jp_term in self.domain_terms.items():
            if eng_term in content.lower():
                # 日本語コメントがあるか確認
                if jp_term not in content:
                    self.add_comment(
                        str(file_path), 0, Severity.SUGGESTION,
                        "DDD - ユビキタス言語",
                        f"'{eng_term}'に対応する日本語用語'{jp_term}'がコメントにありません。",
                        "ドメイン用語の日本語説明を追加してください。"
                    )
        
        # リポジトリパターンの確認
        if 'repository' in file_path.stem.lower():
            if not re.search(r'def\s+(find|get|save|delete)', content):
                self.add_comment(
                    str(file_path), 0, Severity.WARNING,
                    "DDD - リポジトリ",
                    "リポジトリクラスに基本的なCRUD操作が不足しています。",
                    "find, get, save, deleteメソッドの実装を検討してください。"
                )
        
        # 境界コンテキストの確認
        if 'service' in file_path.stem.lower():
            external_imports = re.findall(r'from\s+(\w+)\.', content)
            if len(set(external_imports)) > 3:
                self.add_comment(
                    str(file_path), 0, Severity.WARNING,
                    "DDD - 境界コンテキスト",
                    f"複数のコンテキスト（{len(set(external_imports))}個）に依存しています。",
                    "境界コンテキストを明確にし、依存関係を整理してください。"
                )
        
        # ドメインイベントの使用推奨
        if 'def ' in content and 'event' not in content.lower():
            method_count = len(re.findall(r'def\s+\w+', content))
            if method_count > 5:
                self.add_comment(
                    str(file_path), 0, Severity.SUGGESTION,
                    "DDD - ドメインイベント",
                    "複雑なビジネスロジックがありますが、ドメインイベントが使用されていません。",
                    "重要な状態変更時にドメインイベントの発行を検討してください。"
                )

class MultiAgentCodeReview:
    """マルチエージェントコードレビューシステム"""
    
    def __init__(self):
        self.reviewers = [
            QualityReviewer(),
            ArchitectureReviewer(),
            DDDReviewer()
        ]
        self.results_dir = Path(".claude_sub_agent/.tmp/review_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def review_files(self, file_paths: List[Path]) -> Dict:
        """複数ファイルを並列レビュー"""
        print(f"\n{'='*60}")
        print(f"🔍 マルチエージェントコードレビュー開始")
        print(f"{'='*60}\n")
        
        all_comments = []
        total_score = 100
        
        # 並列レビュー実行
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            for file_path in file_paths:
                print(f"📂 レビュー対象: {file_path}")
                for reviewer in self.reviewers:
                    future = executor.submit(self._review_single_file, reviewer, file_path)
                    futures.append((reviewer.name, file_path, future))
            
            # 結果収集
            for reviewer_name, file_path, future in futures:
                comments = future.result()
                all_comments.extend(comments)
        
        # スコア計算
        critical_count = sum(1 for c in all_comments if c.severity == Severity.CRITICAL)
        warning_count = sum(1 for c in all_comments if c.severity == Severity.WARNING)
        suggestion_count = sum(1 for c in all_comments if c.severity == Severity.SUGGESTION)
        
        total_score -= critical_count * 10
        total_score -= warning_count * 5
        total_score -= suggestion_count * 2
        total_score = max(0, total_score)
        
        # 結果をまとめる
        review_result = {
            'timestamp': format_jst_datetime(),
            'files_reviewed': [str(p) for p in file_paths],
            'total_comments': len(all_comments),
            'critical': critical_count,
            'warning': warning_count,
            'suggestion': suggestion_count,
            'score': total_score,
            'comments': self._format_comments(all_comments)
        }
        
        # 結果を保存
        self._save_results(review_result)
        
        # 結果を表示
        self._display_results(review_result)
        
        return review_result
    
    def _review_single_file(self, reviewer: BaseReviewer, file_path: Path) -> List[ReviewComment]:
        """単一ファイルをレビュー"""
        print(f"  {reviewer.emoji} {reviewer.name} がレビュー中...")
        time.sleep(0.5)  # レビューのシミュレーション
        return reviewer.review_file(file_path)
    
    def _format_comments(self, comments: List[ReviewComment]) -> List[Dict]:
        """コメントをフォーマット"""
        formatted = []
        for comment in comments:
            formatted.append({
                'file': comment.file,
                'line': comment.line,
                'severity': comment.severity.value,
                'category': comment.category,
                'message': comment.message,
                'reviewer': comment.reviewer,
                'suggestion': comment.suggestion
            })
        return formatted
    
    def _save_results(self, results: Dict):
        """結果を保存"""
        timestamp = format_jst_timestamp()
        result_file = self.results_dir / f"review_{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 レビュー結果保存: {result_file.name}")
    
    def _display_results(self, results: Dict):
        """結果を表示"""
        print(f"\n{'='*60}")
        print(f"📊 レビュー結果サマリー")
        print(f"{'='*60}")
        
        print(f"\n📈 品質スコア: {results['score']}/100")
        
        # プログレスバー表示
        bar_length = 20
        filled = int(bar_length * results['score'] / 100)
        bar = "=" * filled + " " * (bar_length - filled)
        color = "🟢" if results['score'] >= 80 else "🟡" if results['score'] >= 60 else "🔴"
        print(f"{color} [{bar}] {results['score']}%")
        
        print(f"\n📝 検出された問題:")
        print(f"  {Severity.CRITICAL.value}: {results['critical']}件")
        print(f"  {Severity.WARNING.value}: {results['warning']}件")
        print(f"  {Severity.SUGGESTION.value}: {results['suggestion']}件")
        
        # 重要な問題を表示
        if results['critical'] > 0:
            print(f"\n⚠️ Critical Issues:")
            for comment in results['comments']:
                if Severity.CRITICAL.value in comment['severity']:
                    print(f"  - [{comment['file']}:{comment['line']}] {comment['message']}")
        
        print(f"\n{'='*60}\n")

def demo():
    """デモンストレーション"""
    print("\n" + "=" * 60)
    print("👥 マルチエージェントコードレビュー デモ")
    print("=" * 60 + "\n")
    
    # デモ用ファイルを作成
    demo_file = Path("demo_review.py")
    demo_code = '''class UserManager:
    def __init__(self):
        self.users = []
        self.groups = []
        self.permissions = []
        self.logs = []
        self.cache = {}
        self.db = None
        self.api = None
        self.mailer = None
        self.validator = None
        self.formatter = None
        self.parser = None
    
    def add_user(self, user):
        print("Adding user:", user)  # デバッグコード
        self.users.append(user)
    
    def remove_user(self, user):
        self.users.remove(user)
    
    def update_user(self, user):
        pass
    
    def get_user(self, id):
        pass
    
    def list_users(self):
        pass
    
    def search_users(self, query):
        pass
    
    def validate_user(self, user):
        pass
    
    def format_user(self, user):
        pass
    
    def parse_user(self, data):
        pass
    
    def cache_user(self, user):
        pass
    
    # TODO: implement email notification
    def notify_user(self, user):
        pass
'''
    
    demo_file.write_text(demo_code)
    
    # レビュー実行
    reviewer = MultiAgentCodeReview()
    results = reviewer.review_files([demo_file])
    
    # デモファイル削除
    demo_file.unlink()
    
    print("✅ デモ完了\n")

def main():
    """メイン処理"""
    import argparse
    parser = argparse.ArgumentParser(description='マルチエージェントコードレビュー')
    parser.add_argument('files', nargs='*', help='レビュー対象ファイル')
    parser.add_argument('--demo', action='store_true', help='デモを実行')
    parser.add_argument('--all', action='store_true', help='全Pythonファイルをレビュー')
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
    elif args.all:
        reviewer = MultiAgentCodeReview()
        py_files = list(Path(".").rglob("*.py"))[:5]  # 最初の5ファイルのみ
        if py_files:
            reviewer.review_files(py_files)
        else:
            print("レビュー対象のPythonファイルが見つかりません")
    elif args.files:
        reviewer = MultiAgentCodeReview()
        file_paths = [Path(f) for f in args.files if Path(f).exists()]
        if file_paths:
            reviewer.review_files(file_paths)
        else:
            print("指定されたファイルが見つかりません")
    else:
        print("レビューするファイルを指定するか、--demoまたは--allオプションを使用してください")

if __name__ == "__main__":
    main()