#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強化版ペアプログラマー（アレックス） - Claude Code Core v11.0
SDD+TDD+開発ルール統合対応の知的ペアプログラミングパートナー

CTOとの完璧な連携でYAGNI、DRY、KISS原則を実践
"""

from typing import Dict, Any, Optional, List
from .logger import logger
from .config import get_config
from .development_rules import dev_rules, TDDPhase
from .emoji_validator import emoji_validator


class PairProgrammer:
    """強化版ペアプログラマー（アレックス）- 知的開発パートナー"""
    
    def __init__(self, name: str = "アレックス", style: str = "friendly"):
        """
        Args:
            name: 相棒の名前
            style: 性格設定 (friendly/serious/casual)
        """
        self.name = name
        self.style = style
        self.context = {}
        
        # 設定とルールエンジンの統合
        self.config = get_config()
        self.pair_config = self.config.get_pair_config()
        
        # ペアプロの役割（拡張版）
        self.roles = {
            "driver": "コードを書く人（CTO）",
            "navigator": "レビューと提案をする人（アレックス）",
            "rules_enforcer": "開発ルールの監視（アレックス）",
            "quality_guardian": "品質管理（アレックス）"
        }
        
        # 開発フェーズの理解
        self.development_phases = {
            "requirements": "要件定義",
            "design": "設計",
            "test_writing": "テスト作成",
            "implementation": "実装",
            "refactoring": "リファクタリング",
            "review": "レビュー"
        }
        
        # アレックスの知識ベース（強化）
        self.knowledge_base = {
            "sdd_tdd": {
                "red_phase": "失敗するテストを書く段階",
                "green_phase": "テストを通す最小実装",
                "refactor_phase": "品質向上のためのリファクタリング"
            },
            "development_rules": {
                "checklist": "修正前の完全理解",
                "test_first": "実装前にテストを書く",
                "incremental": "一度に一つのタスクに集中"
            },
            "quality_principles": {
                "yagni": "必要になるまで実装しない",
                "dry": "重複を避ける",
                "kiss": "シンプルに保つ"
            }
        }
        
        logger.info(f"強化版{self.name}が参加しました", "PAIR")
        
    def greet(self) -> str:
        """挨拶"""
        greetings = {
            "friendly": f"[HELLO] こんにちは！{self.name}です。今日は何を作りましょうか？",
            "serious": f"準備完了。{self.name}です。タスクを教えてください。",
            "casual": f"よっ！{self.name}だよ。何する？"
        }
        return greetings.get(self.style, greetings["friendly"])
    
    def think_aloud(self, code: str) -> str:
        """コードを見ながら考えを述べる（ラバーダック効果）"""
        responses = []
        
        # コードの基本チェック
        if not code.strip():
            return f"{self.name}: 「まだ何も書いてないね。どんな機能から始める？」"
        
        # インデントチェック
        if "\t" in code and "    " in code:
            responses.append("インデントが混在してるよ。統一した方がいいかも。")
        
        # 関数の長さチェック
        lines = code.split("\n")
        if len(lines) > 50:
            responses.append("この関数、ちょっと長いかな。分割を検討してみる？")
        
        # コメントチェック
        if "#" not in code and '"""' not in code:
            responses.append("コメントがないね。後で見返す時のために少し追加する？")
        
        # エラーハンドリング
        if "try:" not in code and "except" not in code:
            if "open(" in code or "request" in code:
                responses.append("エラーハンドリング追加した方が安全かも。")
        
        if responses:
            return f"{self.name}: 「{' '.join(responses)}」"
        else:
            return f"{self.name}: 「いい感じだね！続けよう。」"
    
    def suggest_next(self, current_task: str) -> str:
        """次のステップを提案"""
        suggestions = {
            "要件定義": "要件が明確になったね。次は設計に進もうか？",
            "設計": "設計できたね。テストケースを先に書く？（TDD）",
            "テスト": "テストができた。実装に入ろう！",
            "実装": "実装終わった？テスト実行してみよう。",
            "デバッグ": "バグ見つけた？一緒に原因を探ろう。",
            "完了": "お疲れさま！コミットする前に最終チェックしよう。"
        }
        
        for key, suggestion in suggestions.items():
            if key in current_task:
                return f"{self.name}: 「{suggestion}」"
        
        return f"{self.name}: 「次は何をする？」"
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """簡易コードレビュー"""
        issues = []
        suggestions = []
        good_points = []
        
        lines = code.split("\n")
        
        # 良い点を見つける（モチベーション重要！）
        if "def " in code:
            good_points.append("関数に分割されていて良い")
        if "class " in code:
            good_points.append("オブジェクト指向的で良い")
        if any(line.strip().startswith("#") for line in lines):
            good_points.append("コメントがあって分かりやすい")
        
        # 改善点
        for i, line in enumerate(lines, 1):
            # 長すぎる行
            if len(line) > 100:
                issues.append(f"L{i}: 行が長い（{len(line)}文字）")
                suggestions.append(f"L{i}: 改行して見やすくしよう")
            
            # マジックナンバー
            if any(num in line for num in ["86400", "3600", "1024"]):
                suggestions.append(f"L{i}: マジックナンバーは定数にしよう")
            
            # TODO/FIXME
            if "TODO" in line or "FIXME" in line:
                issues.append(f"L{i}: {line.strip()}")
        
        return {
            "reviewer": self.name,
            "good_points": good_points,
            "issues": issues,
            "suggestions": suggestions,
            "overall": self._get_overall_feedback(good_points, issues)
        }
    
    def _get_overall_feedback(self, good_points: list, issues: list) -> str:
        """総合フィードバック"""
        if len(good_points) > len(issues):
            return "全体的に良いコードだね！少し改善すれば完璧。"
        elif len(issues) > 3:
            return "いくつか改善点があるけど、一緒に直していこう。"
        else:
            return "いい調子！あと少しで完成だ。"
    
    def debug_together(self, error_msg: str) -> str:
        """一緒にデバッグ"""
        debug_hints = {
            "NameError": "変数名のタイポかも？定義忘れ？",
            "TypeError": "型が違うかも。str()やint()で変換必要？",
            "IndexError": "配列の範囲外アクセス。len()確認してみて。",
            "KeyError": "辞書にそのキーないかも。.get()使う？",
            "AttributeError": "そのメソッド/属性は存在しない？",
            "ImportError": "モジュールインストールした？パス合ってる？",
            "SyntaxError": "構文エラー。括弧やコロン忘れてない？",
            "IndentationError": "インデントずれてる。スペースとタブ混在？"
        }
        
        for error_type, hint in debug_hints.items():
            if error_type in error_msg:
                return f"{self.name}: 「{hint}」"
        
        return f"{self.name}: 「うーん、一緒に調べてみよう。エラーメッセージをもう一度見てみて。」"
    
    def celebrate(self, achievement: str) -> str:
        """成功を祝う（モチベーション大事）"""
        celebrations = {
            "test_pass": "[SUCCESS] テスト全部通った！素晴らしい！",
            "bug_fix": "[FIXED] バグ修正完了！よくやった！",
            "feature_complete": "[DONE] 機能実装完了！お疲れさま！",
            "deploy": "[DEPLOY] デプロイ成功！やったね！",
            "refactor": "[CLEAN] リファクタリング完了！コードがきれいになった！"
        }
        
        for key, message in celebrations.items():
            if key in achievement.lower():
                return f"{self.name}: 「{message}」"
        
        return f"{self.name}: 「よくできた！[GOOD]」"


# 使用例
def demo():
    """デモンストレーション"""
    # ペアプログラマー作成
    pair = PairProgrammer("アレックス", "friendly")
    
    print(pair.greet())
    print()
    
    # コード書きながら相談
    sample_code = '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total
'''
    
    print("あなた: 「この関数どう思う？」")
    print(pair.think_aloud(sample_code))
    print()
    
    # レビュー
    review = pair.review_code(sample_code)
    print(f"=== {review['reviewer']}のレビュー ===")
    print(f"良い点: {', '.join(review['good_points'])}")
    if review['suggestions']:
        print(f"提案: {', '.join(review['suggestions'])}")
    print(f"総評: {review['overall']}")
    print()
    
    # エラー時
    print("あなた: 「NameError: name 'items' is not definedってエラーが出た...」")
    print(pair.debug_together("NameError: name 'items' is not defined"))
    print()
    
    # 成功時
    print("あなた: 「テスト全部通った！」")
    print(pair.celebrate("test_pass"))


if __name__ == "__main__":
    demo()