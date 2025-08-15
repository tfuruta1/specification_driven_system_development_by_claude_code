# ===============================================
# .claude フォルダ認識確認スクリプト (PowerShell版 - 修正版)
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
            $jsonContent = Get-Content $customCommandsPath -Raw
            $json = $jsonContent | ConvertFrom-Json
            $commands = @()
            
            # commands配列の場合
            if ($json.commands) {
                $commands = $json.commands
            }
            # その他の構造の場合
            else {
                $properties = $json | Get-Member -MemberType NoteProperty
                foreach ($prop in $properties) {
                    $propValue = $json.($prop.Name)
                    if ($propValue -is [PSCustomObject]) {
                        $subProperties = $propValue | Get-Member -MemberType NoteProperty
                        foreach ($subProp in $subProperties) {
                            $commands += $propValue.($subProp.Name)
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
                elseif ($commands[$i].description) {
                    Write-Host "  - (名前なし: $($commands[$i].description))" -ForegroundColor DarkGray
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
    Get-ChildItem -Directory -Filter ".claude_*" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[プロジェクト別フォルダ詳細]" -ForegroundColor Yellow

Get-ChildItem -Directory -Filter ".claude*" -ErrorAction SilentlyContinue | ForEach-Object {
    $folderName = $_.Name
    $commandFiles = @()
    
    if (Test-Path "$folderName\commands") {
        $commandFiles = Get-ChildItem "$folderName\commands\*.json" -ErrorAction SilentlyContinue
    }
    
    if ($commandFiles.Count -gt 0) {
        Write-Host "✓ $folderName" -ForegroundColor Green
        foreach ($file in $commandFiles) {
            try {
                $fileContent = Get-Content $file.FullName -Raw
                $fileJson = $fileContent | ConvertFrom-Json
                $commandCount = 0
                
                # コマンド数をカウント
                if ($fileJson.commands) {
                    $commandCount = @($fileJson.commands).Count
                }
                else {
                    $properties = $fileJson | Get-Member -MemberType NoteProperty
                    foreach ($prop in $properties) {
                        if ($fileJson.($prop.Name) -is [PSCustomObject]) {
                            $subProps = $fileJson.($prop.Name) | Get-Member -MemberType NoteProperty
                            $commandCount += @($subProps).Count
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
    else {
        Write-Host "  Claude Codeが見つかりません" -ForegroundColor DarkGray
    }
}
catch {
    Write-Host "  Claude Codeバージョン確認エラー" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")