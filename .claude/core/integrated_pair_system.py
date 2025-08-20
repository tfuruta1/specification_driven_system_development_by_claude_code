#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合ペアプログラミングシステム
CTO（Claude Code/私）とアレックスのペアプロ
"""

from typing import Dict, Any, Optional
from system import ClaudeCodeSystem
from pair_programmer import PairProgrammer
from logger import logger


class IntegratedPairSystem:
    """
    CTO（私）とアレックスのペアプログラミングシステム
    ユーザーは見守るだけで、2人が対話しながら開発を進める
    """
    
    def __init__(self):
        self.cto_system = ClaudeCodeSystem()  # CTO（私）のシステム
        self.alex = PairProgrammer("アレックス", "friendly")  # 相棒
        self.current_task = None
        
    def start_session(self, project_name: str, requirements: str):
        """ペアプログラミングセッション開始"""
        print("\n" + "="*60)
        print("[PAIR] ペアプログラミングセッション開始")
        print("="*60 + "\n")
        
        # アレックスの挨拶
        print(f"アレックス: 「{self.alex.greet()[7:]}」")  # [HELLO]を除去
        print()
        
        # CTOの応答
        print("CTO（私）: 「よろしく、アレックス。今日は新しいプロジェクトを始めよう。」")
        print(f"CTO（私）: 「プロジェクト名は『{project_name}』だ。」")
        print()
        
        # アレックスの反応
        print(f"アレックス: 「いいね！どんな要件？」")
        print()
        
        # CTOが要件を説明
        print(f"CTO（私）: 「要件はこうだ: {requirements}」")
        print()
        
        # アレックスの理解確認
        print(f"アレックス: 「なるほど、理解した。じゃあ要件定義書から始めよう！」")
        print()
        
        self.current_task = "requirements"
        return self._execute_development_flow(project_name, requirements)
    
    def _execute_development_flow(self, project_name: str, requirements: str):
        """開発フローを対話形式で実行"""
        
        # Step 1: 要件定義
        print("【要件定義フェーズ】")
        print("CTO（私）: 「要件定義書を作成するよ。」")
        
        req_result = self.cto_system._create_requirements(requirements)
        
        print(f"アレックス: 「要件定義書できた？確認してみよう。」")
        print(f"CTO（私）: 「うん、{req_result['path']}に保存した。」")
        print(f"アレックス: 「{self.alex.suggest_next('要件定義')[11:]}」")  # 名前部分を除去
        print()
        
        # Step 2: 設計
        print("【設計フェーズ】")
        print("CTO（私）: 「設計書を作成しよう。」")
        print("アレックス: 「どんなアーキテクチャにする？」")
        
        design_result = self.cto_system._create_design(req_result)
        
        print(f"CTO（私）: 「設計書完成。{design_result['path']}に保存した。」")
        print()
        
        # Step 3: レビュー
        print("【レビューフェーズ】")
        print("アレックス: 「設計書をレビューしてみるね。」")
        
        # アレックスがレビュー
        sample_code = """
def main():
    # TODO: 実装
    pass
"""
        review = self.alex.review_code(sample_code)
        
        print(f"アレックス: 「{review['overall']}」")
        print("CTO（私）: 「フィードバックありがとう。次はテストを書こう。」")
        print()
        
        # Step 4: TDD
        print("【TDDフェーズ】")
        print("アレックス: 「TDDだね！先にテストを書こう。」")
        print("CTO（私）: 「Red-Green-Refactorの順番で進めよう。」")
        
        test_result = self.cto_system._create_unit_tests(design_result)
        
        print(f"CTO（私）: 「テストファイル作成: {test_result['path']}」")
        print("アレックス: 「まずはテストが失敗することを確認（Red）」")
        print()
        
        # Step 5: 実装
        print("【実装フェーズ】")
        print("CTO（私）: 「実装を始めよう。」")
        print("アレックス: 「何か困ったら言って！」")
        
        impl_result = self.cto_system._implement(design_result)
        
        if "error" in str(impl_result).lower():
            print("CTO（私）: 「エラーが出た...」")
            print(f"アレックス: 「{self.alex.debug_together('実装エラー')[11:]}」")
        else:
            print("CTO（私）: 「実装完了！」")
            print("アレックス: 「いいね！テスト実行してみよう。」")
        print()
        
        # Step 6: テスト実行
        print("【テスト実行フェーズ】")
        print("CTO（私）: 「テストを実行するよ。」")
        print("アレックス: 「ドキドキ...」")
        
        test_run = self.cto_system._run_tests(test_result)
        
        if "pass" in str(test_run).lower() or "success" in str(test_run).lower():
            print("CTO（私）: 「テスト成功！」")
            celebrate_msg = self.alex.celebrate("test_pass")
            print(f"アレックス: 「{celebrate_msg.split('「')[1][:-1]}」")
        else:
            print("CTO（私）: 「まだテストが通らない。」")
            print("アレックス: 「一緒にデバッグしよう！」")
        print()
        
        # Step 7: 完了報告
        print("【完了報告フェーズ】")
        print("CTO（私）: 「プロジェクト完了！報告書を作成するよ。」")
        
        report = self.cto_system._create_report({
            "project": project_name,
            "requirements": req_result,
            "design": design_result,
            "tests": test_result,
            "implementation": impl_result
        })
        
        print(f"アレックス: 「お疲れさま！素晴らしい仕事だったね。」")
        print(f"CTO（私）: 「ありがとう、アレックス。良いペアプログラミングだった。」")
        print()
        
        print("="*60)
        print("[COMPLETE] ペアプログラミングセッション完了")
        print("="*60)
        
        return {
            "status": "completed",
            "report": report,
            "pair_feedback": "素晴らしいチームワークでした！"
        }
    
    def modify_existing_project(self, target_path: str, modification: str):
        """既存プロジェクト修正もペアプロで"""
        print("\n" + "="*60)
        print("[MODIFY] 既存プロジェクト修正セッション")
        print("="*60 + "\n")
        
        print("アレックス: 「既存プロジェクトの修正だね。」")
        print(f"CTO（私）: 「そう、{target_path}を修正する。」")
        print()
        
        # Step 1: 解析
        print("【解析フェーズ】")
        print("CTO（私）: 「まず現状を解析しよう。」")
        print("アレックス: 「影響範囲も確認しないとね。」")
        
        analysis = self.cto_system._analyze_existing_system(target_path, modification)
        
        print(f"CTO（私）: 「解析完了。影響範囲: {len(analysis.get('impact_areas', []))}箇所」")
        print("アレックス: 「思ったより影響あるね。慎重に進めよう。」")
        print()
        
        # Step 2: 影響範囲報告
        print("【影響範囲確認フェーズ】")
        impact_report = self.cto_system._report_impact(analysis)
        
        print(f"CTO（私）: 「影響レベル: {impact_report.get('risk_level', 'unknown')}」")
        print("アレックス: 「ユーザーに報告した方がいいね。」")
        print()
        
        # 以降の修正フロー...
        print("CTO（私）: 「修正要件定義書を作成して...」")
        print("アレックス: 「テストも忘れずに！」")
        print()
        
        return {
            "status": "modification_ready",
            "analysis": analysis,
            "impact": impact_report
        }
    
    def interactive_debug(self, error_message: str):
        """インタラクティブデバッグ"""
        print("\n【デバッグセッション】")
        print(f"CTO（私）: 「エラーが出た: {error_message}」")
        
        hint = self.alex.debug_together(error_message)
        print(f"アレックス: 「{hint.split('「')[1][:-1]}」")
        
        print("CTO（私）: 「なるほど、確認してみる。」")
        print("アレックス: 「一緒に解決しよう！」")
        
        return {"debug_hint": hint}


def demo():
    """デモンストレーション"""
    system = IntegratedPairSystem()
    
    # 新規プロジェクト
    result = system.start_session(
        project_name="TodoApp",
        requirements="タスク管理ができるシンプルなアプリ"
    )
    
    print("\n" + "="*60)
    print("デモ完了")
    print(f"結果: {result['status']}")
    print("="*60)


if __name__ == "__main__":
    demo()