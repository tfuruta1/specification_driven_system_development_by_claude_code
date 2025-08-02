@echo off
REM ===============================================
REM .claude フォルダ認識確認スクリプト
REM Claude Codeがカスタムコマンドを正しく認識しているか確認
REM ===============================================

echo ========================================
echo  Claude Code 認識状態確認スクリプト
echo ========================================
echo.

REM 現在のディレクトリ表示
echo [現在のディレクトリ]
echo %CD%
echo.

REM .claudeフォルダの存在確認
echo [.claudeフォルダの確認]
if exist .claude (
    echo ✓ .claudeフォルダが見つかりました
    echo.
    
    REM カスタムコマンドファイルの確認
    echo [カスタムコマンドファイル]
    if exist .claude\commands\custom_commands.json (
        echo ✓ .claude\commands\custom_commands.json が見つかりました
        echo.
        
        REM コマンド数をカウント
        echo [登録コマンド数]
        findstr /c:"\"name\":" .claude\commands\custom_commands.json | find /c /v "" > temp_count.txt
        set /p COUNT=<temp_count.txt
        del temp_count.txt
        echo   登録されているコマンド数: %COUNT%個
    ) else (
        echo ✗ .claude\commands\custom_commands.json が見つかりません
    )
) else (
    echo ✗ .claudeフォルダが見つかりません
    echo.
    echo [利用可能なプロジェクトフォルダ]
    dir /b /ad | findstr "^\.claude"
)

echo.
echo [プロジェクト別フォルダ一覧]
for /d %%d in (.claude_*) do (
    if exist "%%d\commands\custom_commands.json" (
        echo ✓ %%d （カスタムコマンドあり）
    ) else if exist "%%d\commands\*.json" (
        echo ○ %%d （他のコマンドファイルあり）
    ) else (
        echo - %%d （コマンドファイルなし）
    )
)

echo.
echo ========================================
echo  使用方法
echo ========================================
echo 1. 使用したいプロジェクトフォルダを .claude にリネーム
echo    例: rename .claude_vb6 .claude
echo.
echo 2. Claude Codeを起動
echo    claude .
echo.
echo 3. ヘルプコマンドで確認
echo    /vb6-help （VB6の場合）
echo    /ocr-help （OCRの場合）
echo.
echo 4. 作業終了後、元に戻す
echo    例: rename .claude .claude_vb6
echo.

pause