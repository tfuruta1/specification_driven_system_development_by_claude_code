# ClickOnce配布設定ガイド

## 概要
ClickOnceを使用したISP-673 OCRアプリケーションの配布設定手順です。

## 設定手順

### 1. プロジェクトプロパティ設定
```xml
<PropertyGroup>
  <PublishUrl>\\server\share\ISP673OCR\</PublishUrl>
  <Install>true</Install>
  <InstallFrom>Unc</InstallFrom>
  <UpdateEnabled>true</UpdateEnabled>
  <UpdateMode>Foreground</UpdateMode>
  <UpdateInterval>7</UpdateInterval>
  <UpdateIntervalUnits>Days</UpdateIntervalUnits>
  <UpdatePeriodically>true</UpdatePeriodically>
  <UpdateRequired>false</UpdateRequired>
  <MinimumRequiredVersion>1.0.0.0</MinimumRequiredVersion>
  <ApplicationRevision>1</ApplicationRevision>
  <ApplicationVersion>1.0.0.%2a</ApplicationVersion>
  <UseApplicationTrust>false</UseApplicationTrust>
  <PublishWizardCompleted>true</PublishWizardCompleted>
  <BootstrapperEnabled>true</BootstrapperEnabled>
</PropertyGroup>
```

### 2. 前提条件の設定
- .NET Framework 4.0 Client Profile
- Windows Installer 3.1

### 3. 配布前の準備
1. GloryOcrMain4.dllを各クライアントPCに事前インストール
2. COM登録の実行: `regsvr32 GloryOcrMain4.dll`

### 4. 署名設定
テスト証明書または正式な証明書でアプリケーションに署名

## 注意事項
- ClickOnceではCOM DLLの自動配布ができないため、事前インストールが必要
- x86プラットフォーム設定を維持すること