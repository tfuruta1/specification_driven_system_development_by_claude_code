#!/usr/bin/env python3
"""
階層型エージェントシステム - コマンド実行システム
/spec, /analyze などのカスタムコマンドを実行します
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from daily_log_writer import DailyLogWriter

class CommandExecutor:
    """カスタムコマンド実行エンジン"""
    
    def __init__(self):
        self.base_dir = Path(".claude")
        self.log_writer = DailyLogWriter()
        self.commands = {
            "spec": self.execute_spec,
            "analyze": self.execute_analyze,
            "requirements": self.execute_requirements,
            "design": self.execute_design,
            "tasks": self.execute_tasks,
            "modeltest": self.execute_modeltest,
            "log": self.execute_log
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
            print(f"🚀 コマンド実行: /{command} {' '.join(args)}")
            self.log_writer.write_activity("システム", "コマンド実行", f"/{command} {' '.join(args)}")
            return self.commands[command](args)
        else:
            print(f"❌ 不明なコマンド: /{command}")
            return False
    
    def execute_spec(self, args: List[str]):
        """統合開発フローコマンド"""
        if not args:
            args = ["status"]
        
        phase = args[0]
        print(f"📋 /spec {phase} を実行中...")
        
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
            print(f"❌ 不明なフェーズ: {phase}")
            return False
        
        return True
    
    def spec_init(self):
        """プロジェクト初期化"""
        print("🔧 プロジェクトを初期化しています...")
        
        # ディレクトリ構造を作成
        dirs = [
            ".claude/.ActivityReport/tasks",
            ".claude/.ActivityReport/daily_report",
            ".claude/.ActivityReport/daily_log",
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
        
        # README.md作成
        readme = """# プロジェクト

階層型エージェントシステムにより管理されています。

## 構造
- `.claude/` - エージェントシステム
- `src/` - ソースコード
- `docs/` - ドキュメント
"""
        Path("README.md").write_text(readme, encoding='utf-8')
        
        # shared_tasks.md作成
        tasks_file = Path(".claude/.ActivityReport/tasks/shared_tasks.md")
        tasks_file.write_text("# 共有タスクリスト\n\n## 進行中\n\n## 完了\n", encoding='utf-8')
        
        print("✅ プロジェクト初期化完了")
        self.log_writer.write_activity("CTO", "実行", "プロジェクト初期化完了")
    
    def spec_requirements(self):
        """要件定義フェーズ"""
        print("📝 要件定義を開始します...")
        
        requirements = f"""# 要件定義書
**作成日**: {datetime.now().strftime('%Y-%m-%d')}
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
- 技術スタック: Python, Vue.js, PostgreSQL
"""
        
        req_file = Path(f".claude/docs/requirements/requirements_{datetime.now().strftime('%Y%m%d')}.md")
        req_file.parent.mkdir(parents=True, exist_ok=True)
        req_file.write_text(requirements, encoding='utf-8')
        
        print(f"✅ 要件定義書作成完了: {req_file.name}")
        self.log_writer.write_activity("経営企画部", "文書作成", f"要件定義書: {req_file.name}")
    
    def spec_design(self):
        """技術設計フェーズ"""
        print("🏗️ 技術設計を開始します...")
        
        design = f"""# 技術設計書
**作成日**: {datetime.now().strftime('%Y-%m-%d')}
**作成者**: システム開発部

## 1. アーキテクチャ概要
```
[Frontend] --- [API Gateway] --- [Backend Services] --- [Database]
    |                                    |                    |
  Vue.js 3                          Python/FastAPI      PostgreSQL
```

## 2. API設計
### 2.1 認証API
- POST /api/auth/login
- POST /api/auth/logout
- POST /api/auth/refresh

### 2.2 ユーザーAPI
- GET /api/users
- GET /api/users/{id}
- POST /api/users
- PUT /api/users/{id}
- DELETE /api/users/{id}

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
- JWT認証
- Rate Limiting
- Input Validation
- SQL Injection対策

## 5. デプロイメント設計
- Docker Container
- CI/CD Pipeline
- 監視・ログ収集
"""
        
        design_file = Path(f".claude/docs/design/design_{datetime.now().strftime('%Y%m%d')}.md")
        design_file.parent.mkdir(parents=True, exist_ok=True)
        design_file.write_text(design, encoding='utf-8')
        
        print(f"✅ 技術設計書作成完了: {design_file.name}")
        self.log_writer.write_activity("システム開発部", "文書作成", f"技術設計書: {design_file.name}")
    
    def spec_tasks(self):
        """タスク分割フェーズ"""
        print("📋 タスクを分割します...")
        
        tasks = f"""# タスク分割書
**作成日**: {datetime.now().strftime('%Y-%m-%d')}
**作成者**: 人事部

## スプリント1（2週間）
### バックエンド
- [ ] データベース設計・構築 (3日)
- [ ] 認証API実装 (2日)
- [ ] ユーザーCRUD API実装 (3日)
- [ ] テスト作成 (2日)

### フロントエンド
- [ ] プロジェクトセットアップ (1日)
- [ ] 認証画面実装 (2日)
- [ ] ユーザー管理画面実装 (3日)
- [ ] API連携 (2日)
- [ ] UIテスト (2日)

### インフラ
- [ ] Docker環境構築 (2日)
- [ ] CI/CD設定 (2日)
- [ ] 本番環境準備 (1日)

## スプリント2（2週間）
### 追加機能
- [ ] レポート機能実装
- [ ] パフォーマンス最適化
- [ ] セキュリティ監査

## チーム割り当て
- バックエンド: 田中、鈴木
- フロントエンド: 山田、佐藤
- インフラ: 高橋
- QA: 小林
"""
        
        tasks_file = Path(f".claude/docs/tasks/tasks_{datetime.now().strftime('%Y%m%d')}.md")
        tasks_file.parent.mkdir(parents=True, exist_ok=True)
        tasks_file.write_text(tasks, encoding='utf-8')
        
        print(f"✅ タスク分割完了: {tasks_file.name}")
        self.log_writer.write_activity("人事部", "タスク管理", f"タスク分割書: {tasks_file.name}")
    
    def spec_implement(self):
        """実装開始フェーズ"""
        print("💻 実装を開始します...")
        
        # サンプルコードを生成
        api_code = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Project API")

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str

users_db = []

@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.post("/api/users", response_model=User)
def create_user(user: User):
    user.id = len(users_db) + 1
    users_db.append(user)
    return user

@app.get("/api/users", response_model=List[User])
def get_users():
    return users_db
'''
        
        api_file = Path("src/api/main.py")
        api_file.parent.mkdir(parents=True, exist_ok=True)
        api_file.write_text(api_code, encoding='utf-8')
        
        # テストコードを生成
        test_code = '''import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}

def test_create_user():
    response = client.post("/api/users", json={"username": "test", "email": "test@example.com"})
    assert response.status_code == 200
    assert response.json()["username"] == "test"
'''
        
        test_file = Path("src/tests/test_api.py")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_code, encoding='utf-8')
        
        print("✅ 実装開始: 基本構造を作成しました")
        self.log_writer.write_activity("システム開発部", "実装", "基本API構造を作成")
    
    def spec_status(self):
        """プロジェクト状態確認"""
        print("📊 プロジェクト状態を確認しています...")
        
        # 各フェーズのファイル存在確認
        phases = {
            "初期化": Path("README.md").exists(),
            "要件定義": any(Path(".claude/docs/requirements").glob("*.md")),
            "技術設計": any(Path(".claude/docs/design").glob("*.md")),
            "タスク分割": any(Path(".claude/docs/tasks").glob("*.md")),
            "実装": Path("src/api/main.py").exists()
        }
        
        print("\n【プロジェクト進捗】")
        for phase, completed in phases.items():
            status = "✅ 完了" if completed else "⏳ 未実施"
            print(f"  {phase}: {status}")
        
        # 完了率計算
        completion = sum(1 for v in phases.values() if v) / len(phases) * 100
        print(f"\n進捗率: {completion:.0f}%")
        
        # プログレスバー表示
        bar_length = 20
        filled = int(bar_length * completion / 100)
        bar = "=" * filled + ">" + " " * (bar_length - filled - 1)
        print(f"[{bar}] {completion:.0f}%")
    
    def execute_analyze(self, args: List[str]):
        """プロジェクト解析コマンド"""
        print("🔍 プロジェクトを解析しています...")
        
        # ファイル構造を解析
        project_files = []
        for ext in ['*.py', '*.js', '*.vue', '*.md']:
            project_files.extend(Path(".").rglob(ext))
        
        print(f"\n📁 ファイル構造:")
        print(f"  Python: {len(list(Path('.').rglob('*.py')))} files")
        print(f"  JavaScript: {len(list(Path('.').rglob('*.js')))} files")
        print(f"  Vue: {len(list(Path('.').rglob('*.vue')))} files")
        print(f"  Markdown: {len(list(Path('.').rglob('*.md')))} files")
        
        # 解析結果を保存
        analysis = f"""# プロジェクト解析結果
**解析日時**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## ファイル統計
- Python: {len(list(Path('.').rglob('*.py')))} files
- JavaScript: {len(list(Path('.').rglob('*.js')))} files
- Vue: {len(list(Path('.').rglob('*.vue')))} files
- Markdown: {len(list(Path('.').rglob('*.md')))} files

## 技術スタック
- Backend: Python/FastAPI
- Frontend: Vue.js 3
- Database: PostgreSQL
"""
        
        cache_dir = Path(".claude/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        cache_file.write_text(analysis, encoding='utf-8')
        
        print(f"\n✅ 解析完了: {cache_file.name}")
        self.log_writer.write_activity("システム開発部", "解析", "プロジェクト構造解析完了")
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
        print("🤖 AI連携テストを実行します...")
        
        # MCP連携チェック
        print("\n📡 MCP連携状況:")
        print("  Gemini-CLI: ❌ 未接続")
        print("  o3 MCP: ❌ 未接続")
        print("\n※ MCP接続には別途設定が必要です")
        
        self.log_writer.write_activity("経営企画部", "テスト", "MCP連携テスト実行")
        return True
    
    def execute_log(self, args: List[str]):
        """ログ記録コマンド"""
        print("📝 ログを記録します...")
        
        # 引数を解析
        if args and args[0] in ['analysis', 'team', 'work', 'all']:
            os.system(f"python system/daily_log_writer.py --phase {args[0]}")
        else:
            os.system("python system/daily_log_writer.py --phase all")
        
        return True

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