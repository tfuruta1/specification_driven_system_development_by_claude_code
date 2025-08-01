# Windows XP/2003 デプロイメントガイド

## 概要
Windows XP SP3およびWindows Server 2003 R2環境へのISP-673 OCRアプリケーションのデプロイメント手順です。

## 前提条件確認

### 1. OSバージョン
- Windows XP: Service Pack 3必須
- Windows Server 2003: R2 + Service Pack 2必須

### 2. 必要なランタイム
```cmd
# .NET Framework 4.0のインストール確認
reg query "HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" /v Release

# Visual C++ 2010再頒布可能パッケージ
# ダウンロード: https://www.microsoft.com/ja-jp/download/details.aspx?id=26999
```

## XCopyデプロイメント手順

### 1. フォルダ構成
```
C:\Program Files\ISP673_OCR\
├── ISP673_OCRApp.exe
├── ISP673_OCRApp.exe.config
├── ISP673_OCRApp.Core.dll
├── ISP673_OCRApp.Data.dll
├── GloryOcrMain4.dll          # COM DLL
├── Unity.dll
├── log4net.dll
├── EntityFramework.dll
└── その他の依存DLL
```

### 2. COM DLL登録
```cmd
cd "C:\Program Files\ISP673_OCR"
regsvr32 /s GloryOcrMain4.dll
```

### 3. ショートカット作成（VBScript）
```vbs
' CreateShortcut.vbs
Set WshShell = CreateObject("WScript.Shell")
Set oShortcut = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\ISP-673 OCR.lnk")
oShortcut.TargetPath = "C:\Program Files\ISP673_OCR\ISP673_OCRApp.exe"
oShortcut.WorkingDirectory = "C:\Program Files\ISP673_OCR"
oShortcut.IconLocation = "C:\Program Files\ISP673_OCR\ISP673_OCRApp.exe,0"
oShortcut.Description = "ISP-673 帳票OCRソフトウェア"
oShortcut.Save
```

## Windows XP特有の設定

### 1. DEP（データ実行防止）除外設定
```
1. システムのプロパティ → 詳細設定
2. パフォーマンス → 設定
3. データ実行防止タブ
4. ISP673_OCRApp.exeを除外リストに追加
```

### 2. ファイアウォール例外（必要な場合）
```cmd
netsh firewall add allowedprogram "C:\Program Files\ISP673_OCR\ISP673_OCRApp.exe" "ISP-673 OCR" ENABLE
```

## トラブルシューティング

### エラー: "アプリケーションを正しく初期化できませんでした (0xc0000135)"
→ .NET Framework 4.0がインストールされていません

### エラー: "GloryOcrMain4.dllが見つかりません"
→ Visual C++ 2010再頒布可能パッケージまたはCOM登録が必要

### パフォーマンスが遅い
→ Windows XPでは最小メモリ512MB、推奨1GB以上が必要