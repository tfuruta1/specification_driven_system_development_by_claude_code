# Test Coverage Analysis Command

テストカバレッジ100%維持のための分析とレポート生成を行います。

## Usage
```bash
/coverage [--html] [--target-dir]
```

## Implementation
```bash
#!/bin/bash

HTML_REPORT=""
TARGET_DIR="${2:-.}"

if [ "$1" = "--html" ]; then
    HTML_REPORT="--html"
    echo "📊 Generating HTML coverage report"
fi

echo "🧪 Running comprehensive test coverage analysis..."
echo "📂 Target directory: $TARGET_DIR"

# Install coverage if not present
if ! command -v coverage &> /dev/null; then
    echo "📦 Installing coverage package..."
    pip install coverage
fi

# Run tests with coverage
echo ""
echo "🏃 Running tests with coverage tracking..."
cd "$TARGET_DIR"

# Clean previous coverage data
coverage erase

# Run coverage on all Python files
coverage run --source=. -m pytest tests/ -v

# Generate coverage report
echo ""
echo "📊 Coverage Report:"
echo "==================="
coverage report -m

# Check if we have 100% coverage
COVERAGE_PERCENT=$(coverage report | tail -n 1 | grep -o '[0-9]\+%' | head -n 1 | sed 's/%//')

echo ""
if [ "$COVERAGE_PERCENT" = "100" ]; then
    echo "🎉 Perfect! 100% test coverage achieved!"
else
    echo "⚠️  Current coverage: $COVERAGE_PERCENT%"
    echo ""
    echo "📋 Missing coverage in:"
    coverage report --show-missing | grep -E "^[^ ].*[0-9]+%" | grep -v "100%"
    
    echo ""
    echo "💡 To achieve 100% coverage:"
    echo "1. Add tests for uncovered lines shown above"
    echo "2. Remove unused code (YAGNI principle)"
    echo "3. Run /coverage again to verify"
fi

# Generate HTML report if requested
if [ -n "$HTML_REPORT" ]; then
    echo ""
    echo "🌐 Generating HTML coverage report..."
    coverage html
    echo "📂 HTML report generated in: htmlcov/index.html"
fi

# Generate badge data for README
echo ""
echo "📛 Coverage Badge Data:"
if [ "$COVERAGE_PERCENT" = "100" ]; then
    echo "[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)]()"
else
    if [ "$COVERAGE_PERCENT" -ge 90 ]; then
        COLOR="green"
    elif [ "$COVERAGE_PERCENT" -ge 80 ]; then
        COLOR="yellow"
    else
        COLOR="red"
    fi
    echo "[![Coverage](https://img.shields.io/badge/coverage-$COVERAGE_PERCENT%25-$COLOR.svg)]()"
fi

echo ""
echo "✅ Coverage analysis complete!"