# ISP-673 OCR デプロイメント

このフォルダには、ISP-673 OCRアプリケーションのデプロイメント設定が含まれています。

## フォルダ構成

- **clickonce/** - ClickOnce配布設定
- **msi/** - MSIインストーラー設定（WiX Toolset）
- **legacy/** - Windows XP/2003デプロイメントガイド

## デプロイメント方法

### 1. MSI インストーラー（推奨）
GloryOcrMain4.dllを同梱した完全なインストーラーを作成します。

### 2. ClickOnce
自動更新機能付きの配布方法。ただし、GloryOcrMain4.dllは事前インストールが必要です。

### 3. XCopy デプロイ
手動でファイルをコピーする最も簡単な方法。レガシー環境向け。

## 必要なランタイム

- .NET Framework 4.0
- Visual C++ 2010 再頒布可能パッケージ (x86)
- ISP-673 認識エンジン（GloryOcrMain4.dll）

## プラットフォーム要件

- **必須**: x86プラットフォーム
- 64bitOSではWOW64で動作