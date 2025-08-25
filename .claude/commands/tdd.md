# TDD Development Command

実行テスト駆動開発の完全サイクルを実行します。

## Usage
```bash
/tdd <feature_name>
```

## Implementation
```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: /tdd <feature_name>"
    echo "Example: /tdd authentication"
    exit 1
fi

FEATURE_NAME="$1"
echo "🔴 RED Phase: Creating failing test for $FEATURE_NAME"

# Create test structure if not exists
mkdir -p project/tests
TEST_FILE="project/tests/test_${FEATURE_NAME}.py"

# Create failing test template
cat > "$TEST_FILE" << EOF
#!/usr/bin/env python3
import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class Test${FEATURE_NAME^}(unittest.TestCase):
    """Test cases for $FEATURE_NAME functionality"""
    
    def test_${FEATURE_NAME}_basic_functionality(self):
        """Test basic $FEATURE_NAME functionality"""
        # TODO: Implement test logic
        self.fail("Test not implemented yet - RED phase")

if __name__ == '__main__':
    unittest.main()
EOF

echo "📝 Created test file: $TEST_FILE"

# Run tests to ensure they fail (RED)
echo "🔴 Running tests (should fail)..."
python -m pytest "$TEST_FILE" -v

echo ""
echo "✅ RED Phase Complete!"
echo "Next: Implement minimum code to make tests pass (GREEN phase)"
echo "Then: Refactor for quality (REFACTOR phase)"