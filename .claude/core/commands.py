#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Core - 統合コマンド実行システム
system/command_executor.py を統合し、依存関係をcoreに修正
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from system import ClaudeCodeSystem
from activity_logger import logger
from jst_utils import format_jst_date, format_jst_time
from auto_mode import AutoMode


class CommandExecutor:
    """統合カスタムコマンド実行エンジン"""
    
    def __init__(self):
        self.base_dir = Path(".claude")
        self.system = ClaudeCodeSystem()
        self.auto_mode = AutoMode(str(self.base_dir))
        self.commands = {
            "spec": self.execute_spec,
            "analyze": self.execute_analyze,
            "requirements": self.execute_requirements,
            "design": self.execute_design,
            "tasks": self.execute_tasks,
            "modeltest": self.execute_modeltest,
            "log": self.execute_log,
            "auto-mode": self.execute_auto_mode
        }
        
    def execute(self, command: str, args: List[str] = None):
        """コマンドを実行"""
        if args is None:
            args = []
            
        # コマンドを解析
        if command.startswith("/"):
            command = command[1:]
        
        # コマンドを実行
        if command in self.commands:
            logger.info(f"コマンド実行: /{command} {' '.join(args)}", "COMMAND")
            return self.commands[command](args)
        else:
            logger.error(f"不明なコマンド: /{command}", "COMMAND")
            return False
    
    def execute_spec(self, args: List[str]):
        """統合開発フローコマンド"""
        if not args:
            args = ["status"]
        
        phase = args[0]
        logger.info(f"/spec {phase} を実行中...", "SPEC")
        
        if phase == "init":
            self.spec_init()
        elif phase == "requirements":
            self.spec_requirements()
        elif phase == "design":
            self.spec_design()
        elif phase == "tasks":
            self.spec_tasks()
        elif phase == "implement":
            self.spec_implement()
        elif phase == "status":
            self.spec_status()
        else:
            logger.error(f"不明なフェーズ: {phase}", "SPEC")
            return False
        
        return True
    
    def spec_init(self):
        """プロジェクト初期化"""
        logger.info("プロジェクトを初期化しています...", "INIT")
        
        # ディレクトリ構造を作成
        dirs = [
            ".claude/ActivityReport/tasks",
            ".claude/ActivityReport/daily_report",
            ".claude/ActivityReport/daily_log",
            ".claude/docs/requirements",
            ".claude/docs/design",
            ".claude/docs/tasks",
            "src/api",
            "src/models",
            "src/services",
            "src/tests"
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # shared_tasks.md作成
        tasks_file = Path(".claude/ActivityReport/tasks/shared_tasks.md")
        tasks_file.write_text("# 共有タスクリスト\n\n## 進行中\n\n## 完了\n", encoding='utf-8')
        
        logger.info("プロジェクト初期化完了", "INIT")
    
    def spec_requirements(self):
        """要件定義フェーズ"""
        logger.info("要件定義を開始します...", "REQUIREMENTS")
        
        requirements = f"""# 要件定義書
**作成日**: {format_jst_date()}
**作成者**: 経営企画部

## 1. プロジェクト概要
[プロジェクトの目的と背景]

## 2. 機能要件
### 2.1 ユーザー管理
- ユーザー登録・認証
- 権限管理

### 2.2 データ管理
- CRUD操作
- データ検証

### 2.3 レポート機能
- データ集計
- PDF/Excel出力

## 3. 非機能要件
### 3.1 パフォーマンス
- レスポンス時間: 3秒以内
- 同時接続数: 100ユーザー

### 3.2 セキュリティ
- SSL/TLS暗号化
- 定期的なセキュリティ監査

### 3.3 可用性
- 稼働率: 99.9%
- 自動バックアップ

## 4. 制約事項
- 予算: [金額]
- 納期: [日付]
- 技術スタック: Vue.js, Supabase, PostgreSQL
"""
        
        req_file = Path(f".claude/docs/requirements/requirements_{format_jst_date().replace('-', '')}.md")
        req_file.parent.mkdir(parents=True, exist_ok=True)
        req_file.write_text(requirements, encoding='utf-8')
        
        logger.info(f"要件定義書作成完了: {req_file.name}", "REQUIREMENTS")
    
    def spec_design(self):
        """技術設計フェーズ"""
        logger.info("技術設計を開始します...", "DESIGN")
        
        design = f"""# 技術設計書
**作成日**: {format_jst_date()}
**作成者**: システム開発部

## 1. アーキテクチャ概要
```
[Frontend] --- [API Gateway] --- [Backend Services] --- [Database]
    |                                    |                    |
  Vue.js 3                          Supabase             PostgreSQL
```

## 2. API設計
### 2.1 認証API
- POST /auth/v1/token
- POST /auth/v1/logout
- POST /auth/v1/refresh

### 2.2 ユーザーAPI
- GET /rest/v1/users
- GET /rest/v1/users?id=eq.{id}
- POST /rest/v1/users
- PATCH /rest/v1/users?id=eq.{id}
- DELETE /rest/v1/users?id=eq.{id}

## 3. データベース設計
### 3.1 テーブル構造
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. セキュリティ設計
- JWT認証 (Supabase Auth)
- Row Level Security (RLS)
- Input Validation
- SQL Injection対策

## 5. デプロイメント設計
- Supabase Hosting
- GitHub Actions CI/CD
- 監視・ログ収集
"""
        
        design_file = Path(f".claude/docs/design/design_{format_jst_date().replace('-', '')}.md")
        design_file.parent.mkdir(parents=True, exist_ok=True)
        design_file.write_text(design, encoding='utf-8')
        
        logger.info(f"技術設計書作成完了: {design_file.name}", "DESIGN")
    
    def spec_tasks(self):
        """タスク分割フェーズ"""
        logger.info("タスクを分割します...", "TASKS")
        
        tasks = f"""# タスク分割書
**作成日**: {format_jst_date()}
**作成者**: 人事部

## スプリント1（2週間）
### フロントエンド
- [ ] Vue.js 3プロジェクトセットアップ (1日)
- [ ] 認証画面実装 (2日)
- [ ] ユーザー管理画面実装 (3日)
- [ ] Supabase連携 (2日)
- [ ] UIテスト (2日)

### バックエンド
- [ ] Supabaseプロジェクト設定 (1日)
- [ ] データベース設計・構築 (2日)
- [ ] Row Level Security設定 (2日)
- [ ] APIテスト (2日)

### QA
- [ ] テスト計画書作成 (1日)
- [ ] 機能テスト (3日)
- [ ] セキュリティテスト (2日)

## スプリント2（2週間）
### 追加機能
- [ ] レポート機能実装
- [ ] パフォーマンス最適化
- [ ] セキュリティ監査

## チーム割り当て
- フロントエンド: 田中、鈴木
- バックエンド: 山田、佐藤
- QA: 高橋、小林
"""
        
        tasks_file = Path(f".claude/docs/tasks/tasks_{format_jst_date().replace('-', '')}.md")
        tasks_file.parent.mkdir(parents=True, exist_ok=True)
        tasks_file.write_text(tasks, encoding='utf-8')
        
        logger.info(f"タスク分割完了: {tasks_file.name}", "TASKS")
    
    def spec_implement(self):
        """実装開始フェーズ"""
        logger.info("実装を開始します...", "IMPLEMENT")
        
        # Vue.jsサンプルコードを生成
        vue_code = '''<template>
  <div class="auth-container">
    <h1>認証システム</h1>
    <form @submit.prevent="handleLogin">
      <input 
        v-model="email" 
        type="email" 
        placeholder="Email"
        required
      />
      <input 
        v-model="password" 
        type="password" 
        placeholder="Password"
        required
      />
      <button type="submit">ログイン</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { supabase } from '@/lib/supabase'

const email = ref('')
const password = ref('')

const handleLogin = async () => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value
  })
  
  if (error) {
    console.error('Login error:', error)
  } else {
    console.log('Login success:', data)
  }
}
</script>
'''
        
        vue_file = Path("src/components/Auth.vue")
        vue_file.parent.mkdir(parents=True, exist_ok=True)
        vue_file.write_text(vue_code, encoding='utf-8')
        
        logger.info("実装開始: 基本構造を作成しました", "IMPLEMENT")
    
    def spec_status(self):
        """プロジェクト状態確認"""
        logger.info("プロジェクト状態を確認しています...", "STATUS")
        
        # 各フェーズのファイル存在確認
        phases = {
            "初期化": Path("src").exists(),
            "要件定義": any(Path(".claude/docs/requirements").glob("*.md")) if Path(".claude/docs/requirements").exists() else False,
            "技術設計": any(Path(".claude/docs/design").glob("*.md")) if Path(".claude/docs/design").exists() else False,
            "タスク分割": any(Path(".claude/docs/tasks").glob("*.md")) if Path(".claude/docs/tasks").exists() else False,
            "実装": Path("src/components/Auth.vue").exists()
        }
        
        logger.info("プロジェクト進捗:", "STATUS")
        for phase, completed in phases.items():
            status = "完了" if completed else "未実施"
            logger.info(f"  {phase}: {status}", "STATUS")
        
        # 完了率計算
        completion = sum(1 for v in phases.values() if v) / len(phases) * 100
        logger.info(f"進捗率: {completion:.0f}%", "STATUS")
    
    def execute_analyze(self, args: List[str]):
        """プロジェクト解析コマンド"""
        logger.info("プロジェクトを解析しています...", "ANALYZE")
        
        # ファイル構造を解析
        project_files = []
        for ext in ['*.py', '*.js', '*.vue', '*.md']:
            project_files.extend(Path(".").rglob(ext))
        
        stats = {
            "Python": len(list(Path('.').rglob('*.py'))),
            "JavaScript": len(list(Path('.').rglob('*.js'))),
            "Vue": len(list(Path('.').rglob('*.vue'))),
            "Markdown": len(list(Path('.').rglob('*.md')))
        }
        
        logger.info("ファイル構造:", "ANALYZE")
        for file_type, count in stats.items():
            logger.info(f"  {file_type}: {count} files", "ANALYZE")
        
        # 解析結果を保存
        analysis = f"""# プロジェクト解析結果
**解析日時**: {format_jst_datetime()}

## ファイル統計
- Python: {stats['Python']} files
- JavaScript: {stats['JavaScript']} files
- Vue: {stats['Vue']} files
- Markdown: {stats['Markdown']} files

## 技術スタック
- Frontend: Vue.js 3
- Backend: Supabase
- Database: PostgreSQL
- Testing: Vitest
"""
        
        cache_dir = Path(".claude/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"analysis_{format_jst_timestamp()}.md"
        cache_file.write_text(analysis, encoding='utf-8')
        
        logger.info(f"解析完了: {cache_file.name}", "ANALYZE")
        return True
    
    def execute_requirements(self, args: List[str]):
        """要件定義コマンド"""
        return self.spec_requirements()
    
    def execute_design(self, args: List[str]):
        """技術設計コマンド"""
        return self.spec_design()
    
    def execute_tasks(self, args: List[str]):
        """タスク管理コマンド"""
        return self.spec_tasks()
    
    def execute_modeltest(self, args: List[str]):
        """AI連携テストコマンド"""
        logger.info("AI連携テストを実行します...", "MODELTEST")
        
        # MCP連携チェック
        logger.info("MCP連携状況:", "MODELTEST")
        logger.info("  Gemini-CLI: 未接続", "MODELTEST")
        logger.info("  o3 MCP: 未接続", "MODELTEST")
        logger.info("※ MCP接続には別途設定が必要です", "MODELTEST")
        
        return True
    
    def execute_log(self, args: List[str]):
        """ログ記録コマンド"""
        logger.info("ログを記録します...", "LOG")
        
        # 引数を解析
        if args and args[0] in ['analysis', 'team', 'work', 'all']:
            # 実際のログ処理はactivity_loggerで処理
            logger.info(f"ログフェーズ: {args[0]}", "LOG")
        else:
            logger.info("全ログフェーズを実行", "LOG")
        
        return True
    
    def execute_auto_mode(self, args: List[str]):
        """Auto-Modeコマンド - アレックス・ペアプログラミングモード"""
        if not args:
            # 引数なしの場合は使用方法を表示
            logger.info("Auto-Mode コマンド使用方法:", "AUTO_MODE")
            logger.info("  /auto-mode start   - ペアプログラミングモード開始", "AUTO_MODE")
            logger.info("  /auto-mode stop    - ペアプログラミングモード終了", "AUTO_MODE")
            logger.info("  /auto-mode status  - 現在の状態確認", "AUTO_MODE")
            return True
        
        command = args[0]
        remaining_args = args[1:] if len(args) > 1 else []
        
        # AutoModeに処理を委譲
        result = self.auto_mode.execute_command(command, remaining_args)
        
        return result


def main():
    """メイン処理"""
    executor = CommandExecutor()
    
    import argparse
    parser = argparse.ArgumentParser(description='コマンド実行システム')
    parser.add_argument('command', help='実行するコマンド')
    parser.add_argument('args', nargs='*', help='コマンド引数')
    
    args = parser.parse_args()
    
    # コマンド実行
    success = executor.execute(args.command, args.args)
    
    if not success:
        print("\n使用可能なコマンド:")
        for cmd in executor.commands.keys():
            print(f"  /{cmd}")


if __name__ == "__main__":
    main()