@echo off
REM Pre-commit hooks setup script for Windows
REM Based on: https://zenn.dev/sakupanda/articles/ecb4ae7e9a240e

echo === Alex Team Pre-commit Setup ===

REM 1. Install required tools
echo Installing required tools...
pip install flake8 mypy pytest pytest-cov

REM 2. Install Lefthook (if available)
echo Checking for Lefthook...
where lefthook >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Lefthook not found. Please install:
    echo npm install -g @arkweid/lefthook
    echo or
    echo go install github.com/evilmartians/lefthook@latest
    pause
    exit /b 1
)

REM 3. Initialize Lefthook
echo Initializing Lefthook...
lefthook install

REM 4. Test the setup
echo Testing pre-commit hooks...
git add .
lefthook run ai-ready

if %ERRORLEVEL% eq 0 (
    echo ✅ Pre-commit hooks setup completed successfully!
    echo.
    echo Available commands:
    echo   lefthook run ai-ready      - AI collaboration readiness check
    echo   lefthook run tdd-cycle     - TDD cycle verification
    echo   lefthook run generate-tests - Auto-generate missing tests
) else (
    echo ❌ Setup verification failed. Please check the configuration.
    exit /b 1
)

pause