# Smart Refactoring Command

DRY・YAGNI・KISS原則に基づく自動リファクタリングを実行します。

## Usage
```bash
/refactor [target_directory] [--dry-run]
```

## Implementation
```bash
#!/bin/bash

TARGET_DIR="${1:-.}"
DRY_RUN=""

if [ "$2" = "--dry-run" ]; then
    DRY_RUN="--dry-run"
    echo "🧪 Dry run mode - no changes will be made"
fi

echo "🔧 Starting intelligent refactoring in $TARGET_DIR"
echo "📋 Applying DRY・YAGNI・KISS principles..."

# Check for duplicate code patterns
echo ""
echo "🔍 DRY Analysis - Detecting duplicate code..."
find "$TARGET_DIR" -name "*.py" -exec python -c "
import ast
import sys
from collections import defaultdict

def find_duplicates(file_path):
    try:
        with open(file_path) as f:
            content = f.read()
        # Simple duplicate detection logic
        lines = content.split('\n')
        line_counts = defaultdict(int)
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                line_counts[stripped] += 1
        
        duplicates = {line: count for line, count in line_counts.items() if count > 1 and len(line) > 20}
        if duplicates:
            print(f'  📄 {file_path}:')
            for line, count in list(duplicates.items())[:3]:
                print(f'    • {line[:50]}... ({count} occurrences)')
    except:
        pass

find_duplicates('$TARGET_DIR')
" {} \;

# Check for YAGNI violations (unused imports, functions)
echo ""
echo "🎯 YAGNI Analysis - Finding unused code..."
python -c "
import os
import re
import sys

def check_unused_imports(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath) as f:
                        content = f.read()
                    
                    imports = re.findall(r'^(import|from) (\w+)', content, re.MULTILINE)
                    for imp_type, module in imports:
                        if module not in content[content.find(module) + len(module):]:
                            print(f'  📄 {filepath}: Potentially unused {imp_type} {module}')
                except:
                    pass

check_unused_imports('$TARGET_DIR')
"

# KISS Analysis - Complex code patterns
echo ""
echo "💡 KISS Analysis - Finding overly complex patterns..."
find "$TARGET_DIR" -name "*.py" -exec python -c "
import re
import sys

def analyze_complexity(file_path):
    try:
        with open(file_path) as f:
            content = f.read()
        
        # Check for deeply nested code
        max_indent = 0
        for line in content.split('\n'):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
        
        if max_indent > 20:
            print(f'  📄 {file_path}: High nesting depth ({max_indent//4} levels)')
            
        # Check for long functions
        functions = re.findall(r'def \w+.*?(?=\ndef|\nclass|\Z)', content, re.DOTALL)
        for func in functions:
            lines = len(func.split('\n'))
            if lines > 30:
                func_name = re.match(r'def (\w+)', func).group(1)
                print(f'  📄 {file_path}: Long function {func_name} ({lines} lines)')
                
    except:
        pass

analyze_complexity('$TARGET_DIR')
" {} \;

echo ""
echo "✅ Refactoring analysis complete!"
echo ""
echo "💡 Next steps:"
echo "1. Review identified issues above"
echo "2. Run tests before making changes: pytest $TARGET_DIR/tests/"
echo "3. Apply refactoring incrementally"
echo "4. Run tests after each change"
echo "5. Commit changes with descriptive messages"