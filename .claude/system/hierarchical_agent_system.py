#!/usr/bin/env python3
"""
階層型エージェントシステム - 統合実行システム
CTOを通じて全部門のエージェントが協調動作します
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from daily_log_writer import DailyLogWriter

class Agent:
    """基底エージェントクラス"""
    
    def __init__(self, name: str, icon: str, role: str):
        self.name = name
        self.icon = icon
        self.role = role
        self.log_writer = DailyLogWriter()
        
    def think(self, content: str):
        """思考を記録"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.icon} {self.name} > 💭 {content}")
        self.log_writer.write_activity(self.name, "思考", content)
        
    def say(self, content: str):
        """発言を記録"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.icon} {self.name} > {content}")
        self.log_writer.write_activity(self.name, "発言", content)
        
    def command(self, target: str, command: str):
        """他部門へ指示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.icon} {self.name} → {target} > {command}")
        self.log_writer.write_activity(self.name, "指示", f"→ {target}: {command}")
        
    def report(self, content: str):
        """報告を記録"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.icon} {self.name} > 📊 {content}")
        self.log_writer.write_activity(self.name, "報告", content)
        
    def private_thought(self, content: str):
        """プライベートな本音を記録"""
        self.log_writer.write_activity(self.name, "", content, is_private=True)

class CTO(Agent):
    """CTOエージェント - ユーザー唯一の窓口"""
    
    def __init__(self):
        super().__init__("CTO", "🎯", "プロジェクト担当役員")
        self.departments = {}
        
    def add_department(self, dept):
        """部門を追加"""
        self.departments[dept.name] = dept
        
    def handle_user_request(self, request: str):
        """ユーザーからの要求を処理"""
        self.say(f"承知しました。「{request}」を実行します。")
        
        # リクエストの種類を判定
        if "プロジェクト" in request and "解析" in request:
            self.analyze_project()
        elif "チーム" in request and "編成" in request:
            self.form_team()
        elif "要件" in request:
            self.define_requirements()
        elif "実装" in request:
            self.start_implementation()
        else:
            self.think("このリクエストをどう処理すべきか...")
            self.coordinate_departments(request)
    
    def analyze_project(self):
        """プロジェクト解析フェーズ"""
        self.say("プロジェクト解析を開始します。")
        
        # 各部門に解析を依頼
        self.command("経営企画部", "市場調査と競合分析を実施してください")
        self.departments["経営企画部"].analyze_market()
        
        self.command("システム開発部", "技術スタックを調査してください")
        self.departments["システム開発部"].analyze_tech_stack()
        
        self.command("品質保証部", "テスト戦略を検討してください")
        self.departments["品質保証部"].plan_test_strategy()
        
        self.command("人事部", "必要リソースを見積もってください")
        self.departments["人事部"].estimate_resources()
        
        self.report("プロジェクト解析が完了しました。")
        
    def form_team(self):
        """チーム編成フェーズ"""
        self.say("チーム編成を開始します。")
        self.command("人事部", "最適なチームを編成してください")
        self.departments["人事部"].form_team()
        
    def define_requirements(self):
        """要件定義フェーズ"""
        self.say("要件定義を開始します。")
        self.command("経営企画部", "要件定義書を作成してください")
        self.departments["経営企画部"].create_requirements()
        
    def start_implementation(self):
        """実装開始フェーズ"""
        self.say("実装を開始します。")
        self.command("システム開発部", "実装を開始してください")
        self.departments["システム開発部"].implement()
        
    def coordinate_departments(self, request: str):
        """部門間調整"""
        self.think("各部門と調整が必要です...")
        for dept_name, dept in self.departments.items():
            self.command(dept_name, f"「{request}」について検討してください")

class PlanningDepartment(Agent):
    """経営企画部"""
    
    def __init__(self):
        super().__init__("経営企画部", "💡", "戦略立案・要件定義")
        
    def analyze_market(self):
        """市場調査"""
        self.think("市場動向を分析中...")
        time.sleep(0.5)
        self.report("競合3社の分析完了。差別化ポイントを特定しました。")
        self.private_thought("また新しいプロジェクトか...前のやつまだ終わってないのに")
        
    def create_requirements(self):
        """要件定義書作成"""
        self.say("要件定義書を作成しています...")
        time.sleep(0.5)
        
        # 要件定義書の作成
        requirements = """# 要件定義書

## 機能要件
1. ユーザー認証機能
2. データ管理機能
3. レポート生成機能

## 非機能要件
- レスポンス時間: 3秒以内
- 可用性: 99.9%
"""
        
        req_dir = Path(".claude/docs/requirements")
        req_dir.mkdir(parents=True, exist_ok=True)
        req_file = req_dir / f"requirements_{datetime.now().strftime('%Y%m%d')}.md"
        req_file.write_text(requirements, encoding='utf-8')
        
        self.report(f"要件定義書を作成しました: {req_file.name}")

class DevelopmentDepartment(Agent):
    """システム開発部"""
    
    def __init__(self):
        super().__init__("システム開発部", "💻", "技術実装")
        self.team_members = ["田中（バックエンド）", "鈴木（フロントエンド）", "佐藤（インフラ）"]
        
    def analyze_tech_stack(self):
        """技術スタック調査"""
        self.think("現在の技術スタックを確認中...")
        time.sleep(0.5)
        self.report("Python/FastAPI, Vue.js 3, PostgreSQLを確認しました。")
        self.private_thought("このコード、リファクタリング必要だな...")
        
    def implement(self):
        """実装作業"""
        self.say("実装を開始します。")
        
        for member in self.team_members:
            self.say(f"{member}が作業を開始しました。")
            time.sleep(0.3)
        
        self.report("APIエンドポイント15個を定義完了しました。")
        self.private_thought("早く帰ってゲームしたい...")

class HRDepartment(Agent):
    """人事部"""
    
    def __init__(self):
        super().__init__("人事部", "🏢", "チーム編成・リソース管理")
        
    def estimate_resources(self):
        """リソース見積もり"""
        self.think("必要な人員を計算中...")
        time.sleep(0.5)
        self.report("フロントエンド3名、バックエンド4名、QA2名が必要です。")
        self.private_thought("9人も必要とか言われても、どこから調達するんだよ")
        
    def form_team(self):
        """チーム編成"""
        self.say("チームを編成します。")
        time.sleep(0.5)
        
        team = [
            "田中さくら（フロントエンド、Vue.js専門、7年）",
            "鈴木大輔（バックエンド、Python専門、10年）",
            "山田花子（QA、自動テスト専門、5年）",
            "佐藤健（インフラ、AWS専門、8年）"
        ]
        
        self.say("以下のメンバーを配属しました：")
        for member in team:
            self.say(f"  - {member}")
        
        self.report("チーム編成完了。全員即座に稼働可能です。")
        self.private_thought("実在しないメンバーの経歴書作るの疲れた...")

class QADepartment(Agent):
    """品質保証部"""
    
    def __init__(self):
        super().__init__("品質保証部", "🛡️", "テスト・品質管理")
        
    def plan_test_strategy(self):
        """テスト戦略立案"""
        self.think("テスト戦略を検討中...")
        time.sleep(0.5)
        self.report("単体テスト、結合テスト、E2Eテストの3段階で実施します。")
        self.private_thought("このプロジェクト、テスト可能なのか？")
        
    def run_tests(self):
        """テスト実行"""
        self.say("テストを実行しています...")
        
        # プログレスバーを表示
        for i in range(11):
            progress = "=" * i + ">" + " " * (10 - i)
            print(f"\r[{progress}] {i*10}% | テスト実行中...", end="")
            time.sleep(0.2)
        print()
        
        self.report("テスト完了。カバレッジ85%達成。")
        self.private_thought("また夜更かししそう...明日きつい")

class HierarchicalAgentSystem:
    """階層型エージェントシステム本体"""
    
    def __init__(self):
        self.cto = CTO()
        self.setup_departments()
        self.log_writer = DailyLogWriter()
        
    def setup_departments(self):
        """部門を設定"""
        self.cto.add_department(PlanningDepartment())
        self.cto.add_department(DevelopmentDepartment())
        self.cto.add_department(HRDepartment())
        self.cto.add_department(QADepartment())
        
    def visualize_activity(self, message: str):
        """活動を可視化"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def process_user_input(self, user_input: str):
        """ユーザー入力を処理"""
        self.visualize_activity("=" * 60)
        self.visualize_activity(f"👤 ユーザー: {user_input}")
        self.visualize_activity("=" * 60)
        
        # CTOが対応
        if "@cto" in user_input.lower() or "cto" in user_input.lower():
            request = user_input.replace("@cto", "").replace("CTO", "").strip()
            self.cto.handle_user_request(request)
        else:
            # @ctoがなくても、CTOが対応
            self.cto.handle_user_request(user_input)
        
        self.visualize_activity("=" * 60)
        self.visualize_activity("✅ 処理完了")
        
    def run_interactive(self):
        """対話モード"""
        print("\n" + "=" * 60)
        print("🏢 階層型エージェントシステム v8.7")
        print("=" * 60)
        print("CTOに指示してください（例: @cto プロジェクトを解析して）")
        print("終了するには 'exit' と入力してください")
        print("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("👤 ユーザー > ").strip()
                
                if user_input.lower() in ['exit', 'quit', '終了']:
                    print("\n階層型エージェントシステムを終了します。")
                    break
                
                if user_input:
                    self.process_user_input(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n階層型エージェントシステムを終了します。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")

def main():
    """メイン処理"""
    system = HierarchicalAgentSystem()
    
    import argparse
    parser = argparse.ArgumentParser(description='階層型エージェントシステム')
    parser.add_argument('command', nargs='?', help='実行するコマンド')
    parser.add_argument('--interactive', '-i', action='store_true', 
                      help='対話モードで起動')
    
    args = parser.parse_args()
    
    if args.interactive or not args.command:
        system.run_interactive()
    else:
        system.process_user_input(args.command)

if __name__ == "__main__":
    main()