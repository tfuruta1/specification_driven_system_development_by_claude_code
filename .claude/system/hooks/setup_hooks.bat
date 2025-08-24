@echo off
REM Windows用フックセットアップスクリプト
REM Claude Code SDD+TDD開発システム

echo ====================================
echo Claude Code Hook Setup (Windows)
echo ====================================
echo.

REM Python環境確認
py --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    exit /b 1
)

echo [OK] Python is installed
py --version

REM フックディレクトリ確認
if not exist "%~dp0" (
    echo Error: Hook directory not found
    exit /b 1
)

echo [OK] Hook directory found: %~dp0

REM 設定ファイル確認
if not exist "%~dp0settings.json" (
    echo Warning: settings.json not found, creating default...
    echo { > "%~dp0settings.json"
    echo   "hooks_enabled": true, >> "%~dp0settings.json"
    echo   "log_level": "INFO", >> "%~dp0settings.json"
    echo   "windows_path_fix": true >> "%~dp0settings.json"
    echo } >> "%~dp0settings.json"
)

echo [OK] Settings file: %~dp0settings.json

REM フック実行権限設定（Windowsでは不要だが、ファイル存在確認）
if exist "%~dp0on_prompt.bat" (
    echo [OK] on_prompt.bat found
) else (
    echo Creating on_prompt.bat...
    copy "%~dp0on_prompt.sh" "%~dp0on_prompt.bat" >nul 2>&1
)

if exist "%~dp0on_response.bat" (
    echo [OK] on_response.bat found
) else (
    echo Creating on_response.bat...
    copy "%~dp0on_response.sh" "%~dp0on_response.bat" >nul 2>&1
)

if exist "%~dp0on_tool.bat" (
    echo [OK] on_tool.bat found
) else (
    echo Creating on_tool.bat...
    copy "%~dp0on_tool.sh" "%~dp0on_tool.bat" >nul 2>&1
)

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Hooks are now configured for Windows.
echo To test hooks, run: py -m claude.core.hooks
echo.

exit /b 0