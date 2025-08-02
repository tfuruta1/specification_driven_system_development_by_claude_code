# VB6 CI/CD・デプロイメント戦略ガイド

## 目次
1. [概要](#概要)
2. [ビルド自動化](#ビルド自動化)
3. [継続的インテグレーション](#継続的インテグレーション)
4. [テスト自動化](#テスト自動化)
5. [デプロイメント戦略](#デプロイメント戦略)
6. [環境管理](#環境管理)
7. [ツールとインフラ](#ツールとインフラ)

## 概要

VB6アプリケーションのCI/CDパイプライン構築は、レガシーシステムの特性を考慮した独自のアプローチが必要です。

### 主な課題
- VB6 IDEの自動化制限
- COM依存関係の管理
- レジストリ設定の管理
- バイナリ互換性の維持

## ビルド自動化

### 1. コマンドラインビルド

#### 基本的なビルドスクリプト (build.bat)
```batch
@echo off
setlocal

REM 環境変数設定
set VB6_PATH="C:\Program Files (x86)\Microsoft Visual Studio\VB98"
set PROJECT_PATH=%~dp0
set OUTPUT_PATH=%PROJECT_PATH%bin\

REM 出力ディレクトリ作成
if not exist "%OUTPUT_PATH%" mkdir "%OUTPUT_PATH%"

REM ビルド実行
echo Building VB6 Project...
%VB6_PATH%\VB6.EXE /make "%PROJECT_PATH%MyProject.vbp" /outdir "%OUTPUT_PATH%" /out "%OUTPUT_PATH%build.log"

REM エラーチェック
if %errorlevel% neq 0 (
    echo Build failed! Check build.log for details.
    type "%OUTPUT_PATH%build.log"
    exit /b 1
)

echo Build completed successfully!
exit /b 0
```

#### 高度なビルドスクリプト (build_advanced.ps1)
```powershell
# VB6 Advanced Build Script
param(
    [string]$ProjectPath,
    [string]$Configuration = "Release",
    [string]$OutputPath = "bin",
    [switch]$IncrementVersion
)

# VB6パス設定
$vb6Path = "C:\Program Files (x86)\Microsoft Visual Studio\VB98\VB6.EXE"

# ビルド前処理
Write-Host "Preparing build environment..." -ForegroundColor Green

# バージョン番号自動インクリメント
if ($IncrementVersion) {
    $vbpContent = Get-Content $ProjectPath
    $versionLine = $vbpContent | Where-Object { $_ -match "^RevisionVer=" }
    if ($versionLine) {
        $currentVersion = [int]($versionLine -replace "RevisionVer=", "")
        $newVersion = $currentVersion + 1
        $vbpContent = $vbpContent -replace "RevisionVer=$currentVersion", "RevisionVer=$newVersion"
        Set-Content $ProjectPath $vbpContent
        Write-Host "Version incremented to: $newVersion" -ForegroundColor Yellow
    }
}

# COM参照チェック
Write-Host "Checking COM references..." -ForegroundColor Green
$references = Select-String -Path $ProjectPath -Pattern "^Reference=" | ForEach-Object { $_.Line }
foreach ($ref in $references) {
    # COM参照の存在確認ロジック
    Write-Host "  Checking: $ref"
}

# ビルド実行
Write-Host "Building project..." -ForegroundColor Green
$buildArgs = @(
    "/make", $ProjectPath,
    "/outdir", $OutputPath
)

if ($Configuration -eq "Debug") {
    $buildArgs += "/d", "DEBUG=1"
}

$process = Start-Process -FilePath $vb6Path -ArgumentList $buildArgs -Wait -PassThru -NoNewWindow

if ($process.ExitCode -ne 0) {
    Write-Host "Build failed with exit code: $($process.ExitCode)" -ForegroundColor Red
    exit 1
}

Write-Host "Build completed successfully!" -ForegroundColor Green
```

### 2. MSBuildラッパー

#### VB6用MSBuildプロジェクトファイル (VB6Build.proj)
```xml
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <VB6Path>C:\Program Files (x86)\Microsoft Visual Studio\VB98\VB6.EXE</VB6Path>
    <ProjectFile>MyProject.vbp</ProjectFile>
    <OutputPath>bin\</OutputPath>
    <Configuration>Release</Configuration>
  </PropertyGroup>

  <Target Name="Clean">
    <RemoveDir Directories="$(OutputPath)" />
  </Target>

  <Target Name="PreBuild">
    <MakeDir Directories="$(OutputPath)" />
    <!-- COM登録チェック -->
    <Exec Command="regsvr32 /s dependencies\*.dll" ContinueOnError="true" />
  </Target>

  <Target Name="Build" DependsOnTargets="PreBuild">
    <Exec Command="&quot;$(VB6Path)&quot; /make &quot;$(ProjectFile)&quot; /outdir &quot;$(OutputPath)&quot;" />
  </Target>

  <Target Name="PostBuild" DependsOnTargets="Build">
    <!-- マニフェスト埋め込み -->
    <Exec Command="mt.exe -manifest $(OutputPath)MyApp.exe.manifest -outputresource:$(OutputPath)MyApp.exe;#1" />
  </Target>
</Project>
```

## 継続的インテグレーション

### 1. Jenkins Pipeline

#### Jenkinsfile
```groovy
pipeline {
    agent any
    
    environment {
        VB6_PATH = 'C:\\Program Files (x86)\\Microsoft Visual Studio\\VB98'
        PROJECT_NAME = 'MyVB6App'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Restore Dependencies') {
            steps {
                bat '''
                    echo Registering COM components...
                    for %%f in (dependencies\\*.dll) do (
                        regsvr32 /s "%%f"
                    )
                '''
            }
        }
        
        stage('Build') {
            steps {
                bat '''
                    "%VB6_PATH%\\VB6.EXE" /make "%WORKSPACE%\\%PROJECT_NAME%.vbp" /out build.log
                '''
            }
        }
        
        stage('Test') {
            steps {
                // VB6Unit テスト実行
                bat '''
                    TestRunner.exe /project:"%WORKSPACE%\\Tests\\%PROJECT_NAME%Tests.vbp"
                '''
            }
        }
        
        stage('Package') {
            steps {
                bat '''
                    "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" setup.iss
                '''
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'Output/*.exe', fingerprint: true
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'TestResults',
                    reportFiles: 'TestReport.html',
                    reportName: 'Test Report'
                ])
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            mail to: 'team@example.com',
                 subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                 body: "Build failed. Please check Jenkins for details."
        }
    }
}
```

### 2. Azure DevOps Pipeline

#### azure-pipelines.yml
```yaml
trigger:
- main
- develop

pool:
  vmImage: 'windows-2019'

variables:
  solution: '**/*.vbp'
  buildConfiguration: 'Release'
  buildPlatform: 'x86'

stages:
- stage: Build
  jobs:
  - job: BuildVB6
    steps:
    - task: PowerShell@2
      displayName: 'Install VB6 Runtime'
      inputs:
        targetType: 'inline'
        script: |
          # VB6ランタイムインストールスクリプト
          choco install vb6runtime -y
    
    - task: PowerShell@2
      displayName: 'Register COM Components'
      inputs:
        targetType: 'inline'
        script: |
          Get-ChildItem -Path "$(Build.SourcesDirectory)\dependencies" -Filter *.dll | ForEach-Object {
              regsvr32 /s $_.FullName
          }
    
    - task: CmdLine@2
      displayName: 'Build VB6 Project'
      inputs:
        script: |
          "C:\Program Files (x86)\Microsoft Visual Studio\VB98\VB6.EXE" /make "$(Build.SourcesDirectory)\MyProject.vbp" /out "$(Build.ArtifactStagingDirectory)\build.log"
    
    - task: VSTest@2
      displayName: 'Run Tests'
      inputs:
        testSelector: 'testAssemblies'
        testAssemblyVer2: |
          **\*test*.dll
          !**\*TestAdapter.dll
          !**\obj\**
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish Artifacts'
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)'
        ArtifactName: 'drop'
        publishLocation: 'Container'

- stage: Deploy
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToProduction
    environment: 'Production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: IISWebAppDeploymentOnMachineGroup@0
            displayName: 'Deploy to IIS'
            inputs:
              WebSiteName: 'Default Web Site'
              Package: '$(Pipeline.Workspace)/drop/*.zip'
```

## テスト自動化

### 1. VB6Unit フレームワーク

#### テストクラス例 (TestCustomer.cls)
```vb
' TestCustomer.cls
Option Explicit
Implements ITestCase

Private m_TestContext As TestContext

Private Sub ITestCase_Setup(Context As TestContext)
    Set m_TestContext = Context
    ' テスト前準備
End Sub

Private Sub ITestCase_TearDown()
    ' テスト後処理
End Sub

Private Sub ITestCase_RunTests()
    TestCustomerValidation
    TestCustomerSave
    TestCustomerDelete
End Sub

Private Sub TestCustomerValidation()
    Dim customer As clsCustomer
    Set customer = New clsCustomer
    
    ' 空の顧客名でバリデーションエラー
    customer.CustomerCode = "TEST001"
    customer.CustomerName = ""
    
    m_TestContext.AssertFalse customer.Validate(), "Empty name should fail validation"
    
    ' 正しいデータでバリデーション成功
    customer.CustomerName = "Test Customer"
    m_TestContext.AssertTrue customer.Validate(), "Valid data should pass validation"
End Sub
```

### 2. 自動UIテスト

#### AutoIt スクリプト (UITest.au3)
```autoit
; VB6 Application UI Test
#include <MsgBoxConstants.au3>

; アプリケーション起動
Run("C:\MyApp\MyApp.exe")
WinWaitActive("My Application")

; ログインテスト
ControlSetText("Login", "", "[NAME:txtUsername]", "admin")
ControlSetText("Login", "", "[NAME:txtPassword]", "password")
ControlClick("Login", "", "[NAME:btnLogin]")

; メインフォーム待機
WinWaitActive("Main Form")

; 顧客追加テスト
ControlClick("Main Form", "", "[NAME:btnNewCustomer]")
WinWaitActive("Customer Form")

ControlSetText("Customer Form", "", "[NAME:txtCustomerCode]", "TEST001")
ControlSetText("Customer Form", "", "[NAME:txtCustomerName]", "Test Customer")
ControlClick("Customer Form", "", "[NAME:btnSave]")

; 結果確認
If WinExists("Success") Then
    ConsoleWrite("Test Passed: Customer created successfully" & @CRLF)
    Exit 0
Else
    ConsoleWrite("Test Failed: Customer creation failed" & @CRLF)
    Exit 1
EndIf
```

## デプロイメント戦略

### 1. インストーラー作成

#### Inno Setup スクリプト (setup.iss)
```iss
[Setup]
AppName=My VB6 Application
AppVersion=1.0.0
AppPublisher=My Company
AppPublisherURL=http://www.example.com
DefaultDirName={pf}\MyApp
DefaultGroupName=My Application
OutputDir=Output
OutputBaseFilename=MyAppSetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "bin\MyApp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "bin\*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dependencies\*.ocx"; DestDir: "{sys}"; Flags: restartreplace sharedfile regserver
Source: "dependencies\*.dll"; DestDir: "{sys}"; Flags: restartreplace sharedfile regserver

[Registry]
Root: HKLM; Subkey: "Software\MyCompany\MyApp"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\MyCompany\MyApp"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"

[Icons]
Name: "{group}\My Application"; Filename: "{app}\MyApp.exe"
Name: "{commondesktop}\My Application"; Filename: "{app}\MyApp.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MyApp.exe"; Description: "{cm:LaunchProgram,My Application}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  // 前提条件チェック
  if not RegKeyExists(HKLM, 'SOFTWARE\Microsoft\VisualStudio\6.0') then
  begin
    MsgBox('VB6 Runtime is required. Please install VB6 Runtime first.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // レジストリクリーンアップ
    RegDeleteKeyIncludingSubkeys(HKLM, 'Software\MyCompany\MyApp');
  end;
end;
```

### 2. ClickOnce風デプロイメント

#### 自動更新機能 (AutoUpdate.bas)
```vb
Attribute VB_Name = "modAutoUpdate"
' 自動更新モジュール
Option Explicit

Private Const UPDATE_URL As String = "http://updates.example.com/myapp/"
Private Const VERSION_FILE As String = "version.xml"

Public Function CheckForUpdates() As Boolean
    Dim xmlHttp As Object
    Dim xmlDoc As Object
    Dim currentVersion As String
    Dim latestVersion As String
    
    On Error GoTo ErrorHandler
    
    ' 現在のバージョン取得
    currentVersion = App.Major & "." & App.Minor & "." & App.Revision
    
    ' 最新バージョン情報取得
    Set xmlHttp = CreateObject("MSXML2.XMLHTTP")
    xmlHttp.Open "GET", UPDATE_URL & VERSION_FILE, False
    xmlHttp.Send
    
    If xmlHttp.Status = 200 Then
        Set xmlDoc = CreateObject("MSXML2.DOMDocument")
        xmlDoc.LoadXML xmlHttp.responseText
        
        latestVersion = xmlDoc.SelectSingleNode("//version").Text
        
        If CompareVersions(latestVersion, currentVersion) > 0 Then
            If MsgBox("新しいバージョン " & latestVersion & " が利用可能です。" & vbCrLf & _
                     "更新しますか？", vbQuestion + vbYesNo) = vbYes Then
                DownloadAndInstallUpdate latestVersion
                CheckForUpdates = True
            End If
        End If
    End If
    
    Exit Function
    
ErrorHandler:
    Debug.Print "Update check failed: " & Err.Description
    CheckForUpdates = False
End Function

Private Sub DownloadAndInstallUpdate(Version As String)
    Dim updateUrl As String
    Dim localPath As String
    
    updateUrl = UPDATE_URL & "MyApp_" & Version & "_Setup.exe"
    localPath = Environ("TEMP") & "\MyApp_Update.exe"
    
    ' ダウンロード
    URLDownloadToFile 0, updateUrl, localPath, 0, 0
    
    ' インストーラー実行
    Shell localPath & " /SILENT", vbNormalFocus
    
    ' アプリケーション終了
    End
End Sub
```

### 3. MSI パッケージ作成

#### WiX Toolset プロジェクト (Product.wxs)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="My VB6 Application" 
           Language="1033" 
           Version="1.0.0.0" 
           Manufacturer="My Company" 
           UpgradeCode="{12345678-1234-1234-1234-123456789012}">
    
    <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />
    
    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />
    
    <Feature Id="ProductFeature" Title="My VB6 Application" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
      <ComponentGroupRef Id="COMComponents" />
    </Feature>
    
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="MyApp" />
      </Directory>
      <Directory Id="SystemFolder" />
    </Directory>
    
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable">
        <File Id="MyApp.exe" Source="$(var.SourceDir)\MyApp.exe" KeyPath="yes">
          <Shortcut Id="StartMenuShortcut" 
                    Directory="ProgramMenuFolder" 
                    Name="My Application" 
                    WorkingDirectory="INSTALLFOLDER" 
                    Icon="MyApp.exe" 
                    IconIndex="0" 
                    Advertise="yes" />
        </File>
      </Component>
    </ComponentGroup>
    
    <ComponentGroup Id="COMComponents" Directory="SystemFolder">
      <Component Id="MyComDll">
        <File Id="MyCom.dll" 
              Source="$(var.SourceDir)\MyCom.dll" 
              KeyPath="yes" 
              SelfRegCost="1" />
      </Component>
    </ComponentGroup>
    
    <Icon Id="MyApp.exe" SourceFile="$(var.SourceDir)\MyApp.exe" />
  </Product>
</Wix>
```

## 環境管理

### 1. 環境別設定管理

#### 設定ファイル (config.ini)
```ini
; Development Environment
[Development]
DatabaseServer=localhost\SQLEXPRESS
DatabaseName=MyApp_Dev
LogLevel=DEBUG
APIEndpoint=http://localhost:8080/api

; Testing Environment
[Testing]
DatabaseServer=test-server\SQLEXPRESS
DatabaseName=MyApp_Test
LogLevel=INFO
APIEndpoint=http://test-api.example.com/api

; Production Environment
[Production]
DatabaseServer=prod-server\SQLEXPRESS
DatabaseName=MyApp_Prod
LogLevel=WARNING
APIEndpoint=https://api.example.com/api
```

#### 環境切り替えモジュール (Environment.bas)
```vb
Attribute VB_Name = "modEnvironment"
Option Explicit

Private m_Environment As String
Private m_Config As Dictionary

Public Sub InitializeEnvironment()
    ' 環境変数から環境を判定
    m_Environment = Environ("APP_ENVIRONMENT")
    If m_Environment = "" Then
        m_Environment = "Development"
    End If
    
    ' 設定読み込み
    LoadConfiguration
End Sub

Private Sub LoadConfiguration()
    Dim configFile As String
    configFile = App.Path & "\config.ini"
    
    Set m_Config = New Dictionary
    
    ' INIファイルから設定読み込み
    m_Config.Add "DatabaseServer", GetINIValue(m_Environment, "DatabaseServer", configFile)
    m_Config.Add "DatabaseName", GetINIValue(m_Environment, "DatabaseName", configFile)
    m_Config.Add "LogLevel", GetINIValue(m_Environment, "LogLevel", configFile)
    m_Config.Add "APIEndpoint", GetINIValue(m_Environment, "APIEndpoint", configFile)
End Sub

Public Function GetConfig(Key As String) As String
    If m_Config.Exists(Key) Then
        GetConfig = m_Config(Key)
    Else
        GetConfig = ""
    End If
End Function
```

### 2. Docker コンテナ化

#### Dockerfile
```dockerfile
# Windows Server Core with VB6 Runtime
FROM mcr.microsoft.com/windows/servercore:ltsc2019

# Install Chocolatey
RUN powershell -NoProfile -ExecutionPolicy Bypass -Command \
    "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; \
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"

# Install VB6 Runtime and dependencies
RUN choco install vb6runtime -y
RUN choco install vcredist2008 -y

# Create app directory
WORKDIR /app

# Copy application files
COPY bin/ .
COPY dependencies/ ./dependencies/

# Register COM components
RUN powershell -Command \
    "Get-ChildItem -Path .\dependencies -Filter *.dll | ForEach-Object { regsvr32 /s $_.FullName }"

# Expose port if needed
EXPOSE 8080

# Run application
CMD ["MyApp.exe"]
```

## ツールとインフラ

### 推奨ツールスタック

1. **ソース管理**: Git + GitHub/GitLab/Bitbucket
2. **CI/CD**: Jenkins, Azure DevOps, TeamCity
3. **ビルドツール**: MSBuild, NAnt, PowerShell
4. **テスト**: VB6Unit, AutoIt, TestComplete
5. **パッケージング**: Inno Setup, WiX Toolset, Advanced Installer
6. **配布**: IIS, Windows Server, Docker
7. **監視**: Application Insights, New Relic, Datadog

### ベストプラクティス

1. **バージョン管理**
   - セマンティックバージョニング採用
   - タグとブランチ戦略の明確化

2. **ビルドプロセス**
   - 完全自動化
   - 再現可能なビルド
   - ビルド成果物の保存

3. **テスト戦略**
   - ユニットテストカバレッジ目標設定
   - 統合テストの自動化
   - パフォーマンステスト

4. **デプロイメント**
   - Blue-Greenデプロイメント
   - ロールバック手順の準備
   - 段階的リリース

5. **監視とログ**
   - アプリケーションログの集約
   - パフォーマンスメトリクス収集
   - エラー追跡とアラート