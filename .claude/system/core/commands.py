#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Core - SYSTEM
system/command_executor.py SYSTEMcoreSYSTEM
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from system import ClaudeCodeSystem
from logger import logger
from jst_utils import format_jst_date, format_jst_time
from auto_mode import AutoMode


class CommandExecutor:
    """SYSTEM"""
    
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
        """"""
        if args is None:
            args = []
            
        # 
        if command.startswith("/"):
            command = command[1:]
        
        # 
        if command in self.commands:
            logger.info(f": /{command} {' '.join(args)}", "COMMAND")
            return self.commands[command](args)
        else:
            logger.error(f"ERROR: /{command}", "COMMAND")
            return False
    
    def execute_spec(self, args: List[str]):
        """"""
        if not args:
            args = ["status"]
        
        phase = args[0]
        logger.info(f"/spec {phase} ...", "SPEC")
        
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
            logger.error(f"ERROR: {phase}", "SPEC")
            return False
        
        return True
    
    def spec_init(self):
        """"""
        logger.info("TASK...", "INIT")
        
        # TASK
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
        
        # shared_tasks.mdTASK
        tasks_file = Path(".claude/ActivityReport/tasks/shared_tasks.md")
        tasks_file.write_text("# TASK\n\n## TASK\n\n## TASK\n", encoding='utf-8')
        
        logger.info("", "INIT")
    
    def spec_requirements(self):
        """"""
        logger.info("...", "REQUIREMENTS")
        
        requirements = f"""# 
****: {format_jst_date()}
****: 

## 1. 
[]

## 2. 
### 2.1 
- 
- 

### 2.2 
- CRUD
- 

### 2.3 
- 
- PDF/Excel

## 3. 
### 3.1 
- : 3
- : 100

### 3.2 
- SSL/TLS
- 

### 3.3 
- : 99.9%
- 

## 4. 
- : []
- : []
- : Vue.js, Supabase, PostgreSQL
"""
        
        req_file = Path(f".claude/docs/requirements/requirements_{format_jst_date().replace('-', '')}.md")
        req_file.parent.mkdir(parents=True, exist_ok=True)
        req_file.write_text(requirements, encoding='utf-8')
        
        logger.info(f": {req_file.name}", "REQUIREMENTS")
    
    def spec_design(self):
        """"""
        logger.info("...", "DESIGN")
        
        design = f"""# 
****: {format_jst_date()}
****: 

## 1. 
```
[Frontend] --- [API Gateway] --- [Backend Services] --- [Database]
    |                                    |                    |
  Vue.js 3                          Supabase             PostgreSQL
```

## 2. API
### 2.1 API
- POST /auth/v1/token
- POST /auth/v1/logout
- POST /auth/v1/refresh

### 2.2 API
- GET /rest/v1/users
- GET /rest/v1/users?id=eq.{id}
- POST /rest/v1/users
- PATCH /rest/v1/users?id=eq.{id}
- DELETE /rest/v1/users?id=eq.{id}

## 3. 
### 3.1 
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 
- JWT (Supabase Auth)
- Row Level Security (RLS)
- Input Validation
- SQL Injection

## 5. 
- Supabase Hosting
- GitHub Actions CI/CD
- 
"""
        
        design_file = Path(f".claude/docs/design/design_{format_jst_date().replace('-', '')}.md")
        design_file.parent.mkdir(parents=True, exist_ok=True)
        design_file.write_text(design, encoding='utf-8')
        
        logger.info(f"TASK: {design_file.name}", "DESIGN")
    
    def spec_tasks(self):
        """TASK"""
        logger.info("TASK...", "TASKS")
        
        tasks = f"""# TASK
**TASK**: {format_jst_date()}
**TASK**: TASK

## TASK1TASK2TASK
### 
- [ ] Vue.js 3 (1)
- [ ]  (2)
- [ ]  (3)
- [ ] Supabase (2)
- [ ] UI (2)

### 
- [ ] Supabase (1)
- [ ]  (2)
- [ ] Row Level Security (2)
- [ ] API (2)

### QA
- [ ]  (1)
- [ ]  (3)
- [ ]  (2)

## 22
### 
- [ ] 
- [ ] 
- [ ] TASK

## TASK
- TASK: TASK
- TASK: TASK
- QA: TASK
"""
        
        tasks_file = Path(f".claude/docs/tasks/tasks_{format_jst_date().replace('-', '')}.md")
        tasks_file.parent.mkdir(parents=True, exist_ok=True)
        tasks_file.write_text(tasks, encoding='utf-8')
        
        logger.info(f"TASK: {tasks_file.name}", "TASKS")
    
    def spec_implement(self):
        """TASK"""
        logger.info("TASK...", "IMPLEMENT")
        
        # Vue.js
        vue_code = '''<template>
  <div class="auth-container">
    <h1></h1>
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
      <button type="submit">SUCCESS</button>
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
        
        logger.info(": ", "IMPLEMENT")
    
    def spec_status(self):
        """"""
        logger.info("...", "STATUS")
        
        # 
        phases = {
            "": Path("src").exists(),
            "": any(Path(".claude/docs/requirements").glob("*.md")) if Path(".claude/docs/requirements").exists() else False,
            "": any(Path(".claude/docs/design").glob("*.md")) if Path(".claude/docs/design").exists() else False,
            "TASK": any(Path(".claude/docs/tasks").glob("*.md")) if Path(".claude/docs/tasks").exists() else False,
            "TASK": Path("src/components/Auth.vue").exists()
        }
        
        logger.info("SUCCESS:", "STATUS")
        for phase, completed in phases.items():
            status = "SUCCESS" if completed else "SUCCESS"
            logger.info(f"  {phase}: {status}", "STATUS")
        
        # 
        completion = sum(1 for v in phases.values() if v) / len(phases) * 100
        logger.info(f"ANALYSIS: {completion:.0f}%", "STATUS")
    
    def execute_analyze(self, args: List[str]):
        """ANALYSIS"""
        logger.info("ANALYSIS...", "ANALYZE")
        
        # ANALYSIS
        project_files = []
        for ext in ['*.py', '*.js', '*.vue', '*.md']:
            project_files.extend(Path(".").rglob(ext))
        
        stats = {
            "Python": len(list(Path('.').rglob('*.py'))),
            "JavaScript": len(list(Path('.').rglob('*.js'))),
            "Vue": len(list(Path('.').rglob('*.vue'))),
            "Markdown": len(list(Path('.').rglob('*.md')))
        }
        
        logger.info("ANALYSIS:", "ANALYZE")
        for file_type, count in stats.items():
            logger.info(f"  {file_type}: {count} files", "ANALYZE")
        
        # ANALYSIS
        analysis = f"""# ANALYSIS
**ANALYSIS**: {format_jst_datetime()}

## ANALYSIS
- Python: {stats['Python']} files
- JavaScript: {stats['JavaScript']} files
- Vue: {stats['Vue']} files
- Markdown: {stats['Markdown']} files

## TEST
- Frontend: Vue.js 3
- Backend: Supabase
- Database: PostgreSQL
- Testing: Vitest
"""
        
        cache_dir = Path(".claude/temp/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"analysis_{format_jst_timestamp()}.md"
        cache_file.write_text(analysis, encoding='utf-8')
        
        logger.info(f"ANALYSIS: {cache_file.name}", "ANALYZE")
        return True
    
    def execute_requirements(self, args: List[str]):
        """ANALYSIS"""
        return self.spec_requirements()
    
    def execute_design(self, args: List[str]):
        """TASK"""
        return self.spec_design()
    
    def execute_tasks(self, args: List[str]):
        """TEST"""
        return self.spec_tasks()
    
    def execute_modeltest(self, args: List[str]):
        """AITEST"""
        logger.info("AITEST...", "MODELTEST")
        
        # MCPTEST
        logger.info("MCPTEST:", "MODELTEST")
        logger.info("  Gemini-CLI: TEST", "MODELTEST")
        logger.info("  o3 MCP: TEST", "MODELTEST")
        logger.info("[NOTE] MCPTEST", "MODELTEST")
        
        return True
    
    def execute_log(self, args: List[str]):
        """TEST"""
        logger.info("TASK...", "LOG")
        
        # TASK
        if args and args[0] in ['analysis', 'team', 'work', 'all']:
            # TASKactivity_loggerTASK
            logger.info(f"TASK: {args[0]}", "LOG")
        else:
            logger.info("", "LOG")
        
        return True
    
    def execute_auto_mode(self, args: List[str]):
        """Auto-Mode - """
        if not args:
            # 
            logger.info("Auto-Mode :", "AUTO_MODE")
            logger.info("  /auto-mode start   - ", "AUTO_MODE")
            logger.info("  /auto-mode stop    - ", "AUTO_MODE")
            logger.info("  /auto-mode status  - SYSTEM", "AUTO_MODE")
            return True
        
        command = args[0]
        remaining_args = args[1:] if len(args) > 1 else []
        
        # AutoModeSYSTEM
        result = self.auto_mode.execute_command(command, remaining_args)
        
        return result


def main():
    """SYSTEM"""
    executor = CommandExecutor()
    
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('command', help='')
    parser.add_argument('args', nargs='*', help='SUCCESS')
    
    args = parser.parse_args()
    
    # SUCCESS
    success = executor.execute(args.command, args.args)
    
    if not success:
        print("\nSUCCESS:")
        for cmd in executor.commands.keys():
            print(f"  /{cmd}")


if __name__ == "__main__":
    main()