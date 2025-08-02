# ===============================================
# .claude フォルダ認識確認スクリプト (PowerShell版)
# Claude Codeがカスタムコマンドを正しく認識しているか確認
# ===============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Claude Code 認識状態確認スクリプト" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 現在のディレクトリ表示
Write-Host "[現在のディレクトリ]" -ForegroundColor Yellow
Write-Host $PWD.Path
Write-Host ""

# .claudeフォルダの存在確認
Write-Host "[.claudeフォルダの確認]" -ForegroundColor Yellow
if (Test-Path ".claude") {
    Write-Host "✓ .claudeフォルダが見つかりました" -ForegroundColor Green
    Write-Host ""
    
    # カスタムコマンドファイルの確認
    Write-Host "[カスタムコマンドファイル]" -ForegroundColor Yellow
    $customCommandsPath = ".claude\commands\custom_commands.json"
    
    if (Test-Path $customCommandsPath) {
        Write-Host "✓ $customCommandsPath が見つかりました" -ForegroundColor Green
        Write-Host ""
        
        # JSONファイルの解析
        try {
            $json = Get-Content $customCommandsPath -Raw | ConvertFrom-Json
            $commands = @()
            
            # commands配列の場合
            if ($json.commands) {
                $commands = $json.commands
            }
            # その他の構造の場合
            else {
                $json.PSObject.Properties | ForEach-Object {
                    if ($_.Value -is [PSCustomObject]) {
                        $_.Value.PSObject.Properties | ForEach-Object {
                            $commands += $_.Value
                        }
                    }
                }
            }
            
            Write-Host "[登録コマンド一覧]" -ForegroundColor Yellow
            Write-Host "  登録されているコマンド数: $($commands.Count)個" -ForegroundColor Cyan
            Write-Host ""
            
            # コマンド名を表示（最初の10個まで）
            $displayCount = [Math]::Min($commands.Count, 10)
            for ($i = 0; $i -lt $displayCount; $i++) {
                if ($commands[$i].name) {
                    Write-Host "  - $($commands[$i].name)" -ForegroundColor Gray
                }
            }
            if ($commands.Count -gt 10) {
                Write-Host "  ... 他 $($commands.Count - 10)個のコマンド" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "✗ JSONファイルの解析に失敗しました: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "✗ $customCommandsPath が見つかりません" -ForegroundColor Red
    }
}
else {
    Write-Host "✗ .claudeフォルダが見つかりません" -ForegroundColor Red
    Write-Host ""
    Write-Host "[利用可能なプロジェクトフォルダ]" -ForegroundColor Yellow
    Get-ChildItem -Directory -Filter ".claude_*" | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[プロジェクト別フォルダ詳細]" -ForegroundColor Yellow

Get-ChildItem -Directory -Filter ".claude*" | ForEach-Object {
    $folderName = $_.Name
    $commandFiles = @()
    
    if (Test-Path "$folderName\commands") {
        $commandFiles = Get-ChildItem "$folderName\commands\*.json" -ErrorAction SilentlyContinue
    }
    
    if ($commandFiles.Count -gt 0) {
        Write-Host "✓ $folderName" -ForegroundColor Green
        foreach ($file in $commandFiles) {
            try {
                $json = Get-Content $file.FullName -Raw | ConvertFrom-Json
                $commandCount = 0
                
                # コマンド数をカウント
                if ($json.commands) {
                    $commandCount = $json.commands.Count
                }
                else {
                    $json.PSObject.Properties | ForEach-Object {
                        if ($_.Value -is [PSCustomObject]) {
                            $commandCount += ($_.Value.PSObject.Properties | Measure-Object).Count
                        }
                    }
                }
                
                Write-Host "    - $($file.Name): $commandCount コマンド" -ForegroundColor Gray
            }
            catch {
                Write-Host "    - $($file.Name): 解析エラー" -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "- $folderName （コマンドファイルなし）" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 使用方法" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. 使用したいプロジェクトフォルダを .claude にリネーム" -ForegroundColor White
Write-Host "   例: Rename-Item .claude_vb6 .claude" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Claude Codeを起動" -ForegroundColor White
Write-Host "   claude ." -ForegroundColor Gray
Write-Host ""
Write-Host "3. ヘルプコマンドで確認" -ForegroundColor White
Write-Host "   /vb6-help （VB6の場合）" -ForegroundColor Gray
Write-Host "   /ocr-help （OCRの場合）" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 作業終了後、元に戻す" -ForegroundColor White
Write-Host "   例: Rename-Item .claude .claude_vb6" -ForegroundColor Gray
Write-Host ""

# Claude Codeのバージョン確認
Write-Host "[Claude Code情報]" -ForegroundColor Yellow
try {
    $claudeVersion = & claude --version 2>$null
    if ($claudeVersion) {
        Write-Host "  バージョン: $claudeVersion" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  Claude Codeが見つかりません" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")