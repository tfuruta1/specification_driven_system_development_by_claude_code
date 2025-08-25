#!/bin/bash
# Pre-commit hooks setup script for Unix/Linux
# Based on: https://zenn.dev/sakupanda/articles/ecb4ae7e9a240e

set -e

echo "=== Alex Team Pre-commit Setup ==="

# 1. Install required tools
echo "Installing required tools..."
pip install flake8 mypy pytest pytest-cov

# 2. Install Lefthook (if available)
echo "Checking for Lefthook..."
if ! command -v lefthook &> /dev/null; then
    echo "Lefthook not found. Please install:"
    echo "npm install -g @arkweid/lefthook"
    echo "or"
    echo "go install github.com/evilmartians/lefthook@latest"
    exit 1
fi

# 3. Initialize Lefthook
echo "Initializing Lefthook..."
lefthook install

# 4. Test the setup
echo "Testing pre-commit hooks..."
git add .
lefthook run ai-ready

if [ $? -eq 0 ]; then
    echo "✅ Pre-commit hooks setup completed successfully!"
    echo
    echo "Available commands:"
    echo "  lefthook run ai-ready      - AI collaboration readiness check"
    echo "  lefthook run tdd-cycle     - TDD cycle verification"  
    echo "  lefthook run generate-tests - Auto-generate missing tests"
else
    echo "❌ Setup verification failed. Please check the configuration."
    exit 1
fi