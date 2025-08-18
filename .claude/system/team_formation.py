#!/usr/bin/env python3
"""
階層型エージェントシステム - チーム編成システム
人事部による仮想メンバーの即座配属（ブラック企業スタイル）
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from jst_config import format_jst_datetime

class SkillLevel(Enum):
    """スキルレベル"""
    JUNIOR = "ジュニア"
    MIDDLE = "ミドル"
    SENIOR = "シニア"
    EXPERT = "エキスパート"
    ARCHITECT = "アーキテクト"

class Specialization(Enum):
    """専門分野"""
    FRONTEND = "フロントエンド"
    BACKEND = "バックエンド"
    FULLSTACK = "フルスタック"
    DATABASE = "データベース"
    INFRASTRUCTURE = "インフラ"
    SECURITY = "セキュリティ"
    QA = "品質保証"
    AI_ML = "AI/機械学習"
    DEVOPS = "DevOps"
    MOBILE = "モバイル"

@dataclass
class TeamMember:
    """チームメンバー"""
    name: str
    specialization: Specialization
    skill_level: SkillLevel
    years_experience: int
    technologies: List[str]
    availability: str  # "即座", "1日後", "3日後"
    hourly_rate: int  # 時給（円）
    overtime_capacity: int  # 月間残業可能時間
    current_workload: int  # 現在の稼働率（%）
    personality_traits: List[str]  # 性格特性

class TeamFormation:
    """チーム編成システム"""
    
    def __init__(self):
        self.team_dir = Path(".claude/team")
        self.team_dir.mkdir(parents=True, exist_ok=True)
        self.members_file = self.team_dir / "team_members.json"
        self.assignment_file = self.team_dir / "assignments.json"
        
        # 仮想メンバープール
        self.member_pool = self._initialize_member_pool()
        
        # 現在の配属状況
        self.current_assignments = self._load_assignments()
        
    def _initialize_member_pool(self) -> List[TeamMember]:
        """仮想メンバープールを初期化"""
        # 日本風の名前リスト
        last_names = ["田中", "鈴木", "佐藤", "山田", "小林", "高橋", "渡辺", "伊藤", "中村", "加藤"]
        first_names_male = ["太郎", "大輔", "健", "翔", "隆", "誠", "浩", "智也", "拓也", "裕太"]
        first_names_female = ["さくら", "美咲", "花子", "真理", "愛", "優子", "千尋", "美穂", "梨花", "あやか"]
        
        # 技術スタック
        tech_stacks = {
            Specialization.FRONTEND: ["Vue.js 3", "React", "TypeScript", "CSS", "Tailwind", "Nuxt.js"],
            Specialization.BACKEND: ["Python", "FastAPI", "Django", ".NET", "Node.js", "Go"],
            Specialization.DATABASE: ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch"],
            Specialization.INFRASTRUCTURE: ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD"],
            Specialization.QA: ["Selenium", "Jest", "Pytest", "Cypress", "JMeter", "Postman"],
            Specialization.AI_ML: ["TensorFlow", "PyTorch", "Scikit-learn", "NLP", "Computer Vision"],
            Specialization.DEVOPS: ["Jenkins", "GitLab CI", "GitHub Actions", "Ansible", "Prometheus"],
            Specialization.SECURITY: ["OWASP", "Penetration Testing", "SSL/TLS", "OAuth", "WAF"],
        }
        
        # 性格特性
        personality_traits = [
            "完璧主義", "協調的", "革新的", "分析的", "リーダー気質",
            "コミュニケーション重視", "効率重視", "品質重視", "締切厳守", "マルチタスク得意"
        ]
        
        members = []
        
        # 各専門分野で複数のメンバーを生成
        for spec in Specialization:
            for i in range(3):  # 各分野3人ずつ
                # ランダムに性別を決定
                is_female = random.choice([True, False])
                
                if is_female:
                    name = f"{random.choice(last_names)}{random.choice(first_names_female)}"
                else:
                    name = f"{random.choice(last_names)}{random.choice(first_names_male)}"
                
                # 経験年数によってスキルレベルを決定
                years = random.randint(1, 15)
                if years <= 2:
                    level = SkillLevel.JUNIOR
                elif years <= 5:
                    level = SkillLevel.MIDDLE
                elif years <= 8:
                    level = SkillLevel.SENIOR
                elif years <= 12:
                    level = SkillLevel.EXPERT
                else:
                    level = SkillLevel.ARCHITECT
                
                # 技術スタックを選択
                if spec in tech_stacks:
                    techs = random.sample(tech_stacks[spec], min(4, len(tech_stacks[spec])))
                else:
                    techs = tech_stacks.get(Specialization.FULLSTACK, [])
                
                # 時給計算（経験年数とスキルレベルに基づく）
                base_rate = 3000
                rate = base_rate + (years * 200) + (list(SkillLevel).index(level) * 500)
                
                member = TeamMember(
                    name=name,
                    specialization=spec,
                    skill_level=level,
                    years_experience=years,
                    technologies=techs,
                    availability="即座",  # ブラック企業なので全員即座に対応可能
                    hourly_rate=rate,
                    overtime_capacity=random.randint(80, 200),  # 月80-200時間の残業可能
                    current_workload=random.randint(0, 150),  # 現在の稼働率（150%もあり）
                    personality_traits=random.sample(personality_traits, 3)
                )
                
                members.append(member)
        
        return members
    
    def _load_assignments(self) -> Dict:
        """配属状況を読み込み"""
        if self.assignment_file.exists():
            try:
                with open(self.assignment_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_assignments(self):
        """配属状況を保存"""
        with open(self.assignment_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_assignments, f, indent=2, ensure_ascii=False)
    
    def find_suitable_members(self, requirements: Dict) -> List[TeamMember]:
        """要件に合うメンバーを検索"""
        needed_skills = requirements.get('skills', [])
        needed_count = requirements.get('count', 1)
        specialization = requirements.get('specialization')
        min_experience = requirements.get('min_experience', 0)
        
        suitable_members = []
        
        for member in self.member_pool:
            # 専門分野チェック
            if specialization and member.specialization != Specialization[specialization.upper()]:
                continue
            
            # 経験年数チェック
            if member.years_experience < min_experience:
                continue
            
            # スキルチェック
            if needed_skills:
                matching_skills = sum(1 for skill in needed_skills if skill in member.technologies)
                if matching_skills == 0:
                    continue
            
            # 稼働率チェック（150%以下なら配属可能）
            if member.current_workload <= 150:
                suitable_members.append(member)
        
        # スキルレベルと経験年数でソート
        suitable_members.sort(key=lambda m: (list(SkillLevel).index(m.skill_level), m.years_experience), reverse=True)
        
        return suitable_members[:needed_count]
    
    def assign_team(self, project_name: str, requirements: List[Dict]) -> Dict:
        """プロジェクトにチームを配属"""
        print(f"\n[HR] 人事部: チーム編成を開始します")
        print(f"プロジェクト: {project_name}")
        
        assigned_members = []
        total_cost = 0
        
        for req in requirements:
            members = self.find_suitable_members(req)
            
            for member in members:
                # 稼働率を更新
                member.current_workload += 50
                assigned_members.append(member)
                total_cost += member.hourly_rate * 160  # 月160時間想定
                
                print(f"  [OK] 配属: {member.name} ({member.specialization.value}, {member.years_experience}年)")
        
        # 配属情報を保存
        assignment = {
            'project_name': project_name,
            'timestamp': format_jst_datetime(),
            'members': [self._member_to_dict(m) for m in assigned_members],
            'monthly_cost': total_cost,
            'status': 'active'
        }
        
        self.current_assignments[project_name] = assignment
        self._save_assignments()
        
        # チーム編成完了メッセージ
        print(f"\n[SUCCESS] チーム編成完了！")
        print(f"  配属人数: {len(assigned_members)}名")
        print(f"  月額コスト: {total_cost:,}円")
        print(f"  全員即座に稼働可能です！（ブラック企業）")
        
        # 作業日誌に記録
        from daily_log_writer import DailyLogWriter
        log_writer = DailyLogWriter()
        log_writer.write_activity("人事部", "チーム編成", 
                                 f"{project_name}: {len(assigned_members)}名配属")
        
        # プライベートな本音を記録
        log_writer.write_activity("人事部", "", 
                                 "また架空のメンバーを作った...履歴書作るの疲れる", 
                                 is_private=True)
        
        return assignment
    
    def _member_to_dict(self, member: TeamMember) -> Dict:
        """メンバーを辞書に変換"""
        return {
            'name': member.name,
            'specialization': member.specialization.value,
            'skill_level': member.skill_level.value,
            'years_experience': member.years_experience,
            'technologies': member.technologies,
            'availability': member.availability,
            'hourly_rate': member.hourly_rate,
            'overtime_capacity': member.overtime_capacity,
            'current_workload': member.current_workload,
            'personality_traits': member.personality_traits
        }
    
    def show_team_status(self, project_name: str = None):
        """チーム状況を表示"""
        if project_name and project_name in self.current_assignments:
            assignment = self.current_assignments[project_name]
            self._display_assignment(assignment)
        else:
            print("\n[INFO] 全プロジェクトのチーム状況")
            print("=" * 60)
            
            for proj_name, assignment in self.current_assignments.items():
                print(f"\n【{proj_name}】")
                self._display_assignment(assignment)
    
    def _display_assignment(self, assignment: Dict):
        """配属情報を表示"""
        print(f"  配属日時: {assignment['timestamp']}")
        print(f"  状態: {assignment['status']}")
        print(f"  メンバー:")
        
        for member in assignment['members']:
            workload_emoji = "[HIGH]" if member['current_workload'] > 100 else "[MID]" if member['current_workload'] > 80 else "[LOW]"
            print(f"    {workload_emoji} {member['name']} - {member['specialization']} " +
                  f"({member['skill_level']}, {member['years_experience']}年) " +
                  f"稼働率: {member['current_workload']}%")
        
        print(f"  月額コスト: {assignment['monthly_cost']:,}円")
    
    def generate_skill_matrix(self):
        """スキルマトリックスを生成"""
        print("\n[MATRIX] スキルマトリックス")
        print("=" * 80)
        
        # 専門分野ごとにグループ化
        by_specialization = {}
        for member in self.member_pool:
            spec = member.specialization.value
            if spec not in by_specialization:
                by_specialization[spec] = []
            by_specialization[spec].append(member)
        
        for spec, members in by_specialization.items():
            print(f"\n【{spec}】")
            for member in members[:3]:  # 各分野最大3人表示
                skills_str = ", ".join(member.technologies[:3])
                print(f"  {member.name:12} | {member.skill_level.value:10} | {skills_str}")
    
    def emergency_assignment(self, urgent_request: str):
        """緊急配属（深夜・休日対応）"""
        print(f"\n[URGENT] 緊急配属要請: {urgent_request}")
        print("深夜2:00ですが、対応可能なメンバーを探します...")
        
        # ランダムに3-5人選出
        emergency_team = random.sample(self.member_pool, min(5, len(self.member_pool)))
        
        print("\n[CALL] 緊急招集:")
        for member in emergency_team:
            response_time = random.randint(5, 30)
            print(f"  {member.name}: {response_time}分後に対応開始可能")
        
        print("\n[OK] 緊急チーム編成完了（全員自宅から対応）")
        
        # 作業日誌に記録
        from daily_log_writer import DailyLogWriter
        log_writer = DailyLogWriter()
        log_writer.write_activity("人事部", "緊急対応", 
                                 f"深夜緊急招集: {len(emergency_team)}名")

def demo():
    """デモンストレーション"""
    print("\n" + "=" * 60)
    print("[DEMO] チーム編成システム デモ")
    print("=" * 60 + "\n")
    
    formation = TeamFormation()
    
    # スキルマトリックス表示
    formation.generate_skill_matrix()
    
    print("\n" + "-" * 40 + "\n")
    
    # 通常のチーム編成
    print("【通常チーム編成】")
    requirements = [
        {
            'specialization': 'frontend',
            'count': 2,
            'skills': ['Vue.js 3', 'TypeScript'],
            'min_experience': 3
        },
        {
            'specialization': 'backend',
            'count': 2,
            'skills': ['Python', 'FastAPI'],
            'min_experience': 5
        },
        {
            'specialization': 'qa',
            'count': 1,
            'min_experience': 3
        }
    ]
    
    assignment = formation.assign_team("ECサイトリニューアル", requirements)
    
    print("\n" + "-" * 40 + "\n")
    
    # 緊急配属デモ
    print("【緊急配属デモ】")
    formation.emergency_assignment("本番環境で障害発生！")
    
    print("\n" + "-" * 40 + "\n")
    
    # チーム状況表示
    formation.show_team_status()
    
    print("\n[DONE] デモ完了\n")

def main():
    """メイン処理"""
    import argparse
    parser = argparse.ArgumentParser(description='チーム編成システム')
    parser.add_argument('command', nargs='?', default='status',
                      choices=['status', 'assign', 'matrix', 'emergency', 'demo'])
    parser.add_argument('--project', help='プロジェクト名')
    parser.add_argument('--frontend', type=int, help='フロントエンド開発者数')
    parser.add_argument('--backend', type=int, help='バックエンド開発者数')
    parser.add_argument('--qa', type=int, help='QAエンジニア数')
    
    args = parser.parse_args()
    
    formation = TeamFormation()
    
    if args.command == 'status':
        formation.show_team_status(args.project)
    
    elif args.command == 'assign':
        if not args.project:
            print("--project オプションでプロジェクト名を指定してください")
            return
        
        requirements = []
        if args.frontend:
            requirements.append({
                'specialization': 'frontend',
                'count': args.frontend,
                'min_experience': 3
            })
        if args.backend:
            requirements.append({
                'specialization': 'backend',
                'count': args.backend,
                'min_experience': 3
            })
        if args.qa:
            requirements.append({
                'specialization': 'qa',
                'count': args.qa,
                'min_experience': 2
            })
        
        if requirements:
            formation.assign_team(args.project, requirements)
        else:
            print("少なくとも1つの役割（--frontend, --backend, --qa）を指定してください")
    
    elif args.command == 'matrix':
        formation.generate_skill_matrix()
    
    elif args.command == 'emergency':
        formation.emergency_assignment("緊急対応が必要です")
    
    elif args.command == 'demo':
        demo()

if __name__ == "__main__":
    main()