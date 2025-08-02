# VB6アプリケーションデプロイメントガイド

## 目次
1. [デプロイメント準備](#デプロイメント準備)
2. [依存関係管理](#依存関係管理)
3. [インストーラー作成](#インストーラー作成)
4. [配布方法](#配布方法)
5. [トラブルシューティング](#トラブルシューティング)

## デプロイメント準備

### 1. プロジェクト構成確認

#### チェックリスト
```
☐ プロジェクトファイル(.vbp)のバージョン番号更新
☐ コンパイルオプションの確認（最適化、P-Code/Native）
☐ アイコンファイルの準備
☐ マニフェストファイルの作成
☐ デジタル署名の準備
```

#### コンパイル設定 (Project.vbp)
```ini
Type=Exe
Reference=*\G{00020430-0000-0000-C000-000000000046}#2.0#0#..\..\WINDOWS\system32\stdole2.tlb#OLE Automation
CompilationType=0
OptimizationType=2
FavorPentiumPro(tm)=-1
CodeViewDebugInfo=0
NoAliasing=-1
BoundsCheck=0
OverflowCheck=0
FlPointCheck=0
FDIVCheck=0
UnroundedFP=0
StartMode=0
Unattended=0
Retained=0
ThreadPerObject=0
MaxNumberOfThreads=1
DebugStartupOption=0
VersionCompanyName="My Company"
VersionFileDescription="My Application"
VersionLegalCopyright="Copyright 2025"
VersionProductName="My Product"
VersionComments="Production Release"
```

### 2. マニフェストファイル

#### MyApp.exe.manifest
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="x86"
    name="MyCompany.MyApp"
    type="win32"
  />
  <description>My VB6 Application</description>
  
  <!-- Windows 共通コントロール -->
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="x86"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
  
  <!-- UAC 設定 -->
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v2">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  
  <!-- 高DPI対応 -->
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>
```

## 依存関係管理

### 1. 依存コンポーネント一覧

#### dependency_list.txt
```
# VB6ランタイム
MSVBVM60.DLL - Visual Basic 6.0 Runtime

# 標準OCX
COMDLG32.OCX - Common Dialog Control
MSCOMCTL.OCX - Microsoft Common Controls
MSCOMCT2.OCX - Microsoft Common Controls 2
MSFLXGRD.OCX - Microsoft FlexGrid Control
MSWINSCK.OCX - Microsoft Winsock Control

# データアクセス
MSADO15.DLL - Microsoft ActiveX Data Objects
MSDAOSP.DLL - Microsoft Data Access Objects

# Crystal Reports (オプション)
CRPE32.DLL - Crystal Reports Print Engine
CRVIEWER.DLL - Crystal Reports Viewer

# カスタムDLL
MyCustom.dll - 自社COMコンポーネント
```

### 2. 依存関係チェックスクリプト

#### check_dependencies.ps1
```powershell
# VB6 Dependency Checker
param(
    [string]$ExePath = ".",
    [string]$OutputFile = "dependencies.txt"
)

# Dependency Walker を使用した依存関係抽出
function Get-Dependencies {
    param([string]$FilePath)
    
    $deps = @()
    
    # dumpbinを使用（Visual Studioツール）
    $dumpbin = "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64\dumpbin.exe"
    
    if (Test-Path $dumpbin) {
        $output = & $dumpbin /dependents $FilePath
        $deps = $output | Select-String -Pattern "\s+\w+\.dll" | ForEach-Object { $_.Line.Trim() }
    }
    
    return $deps
}

# メイン処理
$exeFiles = Get-ChildItem -Path $ExePath -Filter "*.exe"
$allDeps = @()

foreach ($exe in $exeFiles) {
    Write-Host "Checking dependencies for: $($exe.Name)"
    $deps = Get-Dependencies $exe.FullName
    $allDeps += $deps
}

# 重複除去とソート
$uniqueDeps = $allDeps | Sort-Object -Unique

# 結果出力
$uniqueDeps | Out-File $OutputFile
Write-Host "Dependencies saved to: $OutputFile"

# 存在チェック
$missing = @()
foreach ($dep in $uniqueDeps) {
    $found = $false
    
    # システムディレクトリで検索
    $systemPaths = @(
        "C:\Windows\System32",
        "C:\Windows\SysWOW64",
        $ExePath
    )
    
    foreach ($path in $systemPaths) {
        if (Test-Path "$path\$dep") {
            $found = $true
            break
        }
    }
    
    if (-not $found) {
        $missing += $dep
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`nMissing dependencies:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}
```

### 3. Registration-Free COM

#### サイドバイサイドマニフェスト (MyApp.exe.manifest)
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="x86"
    name="MyCompany.MyApp"
    type="win32"
  />
  
  <!-- Registration-Free COM -->
  <file name="MyCustom.dll">
    <comClass
      clsid="{12345678-1234-1234-1234-123456789012}"
      threadingModel="Apartment"
      progid="MyCustom.MyClass"
    />
  </file>
  
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="MyCustom"
        version="1.0.0.0"
      />
    </dependentAssembly>
  </dependency>
</assembly>
```

## インストーラー作成

### 1. Inno Setupスクリプト (詳細版)

#### setup_advanced.iss
```iss
#define MyAppName "My Application"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "My Company"
#define MyAppURL "http://www.example.com"
#define MyAppExeName "MyApp.exe"

[Setup]
AppId={{12345678-1234-1234-1234-123456789012}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=License.txt
InfoBeforeFile=Readme.txt
OutputDir=Output
OutputBaseFilename=Setup_{#MyAppName}_{#MyAppVersion}
SetupIconFile=MyApp.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x86 x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; メインアプリケーション
Source: "bin\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "bin\{#MyAppExeName}.manifest"; DestDir: "{app}"; Flags: ignoreversion

; VB6ランタイム
Source: "redist\MSVBVM60.DLL"; DestDir: "{sys}"; Flags: restartreplace uninsneveruninstall sharedfile regserver

; 標準OCX
Source: "redist\COMDLG32.OCX"; DestDir: "{sys}"; Flags: restartreplace sharedfile regserver
Source: "redist\MSCOMCTL.OCX"; DestDir: "{sys}"; Flags: restartreplace sharedfile regserver
Source: "redist\MSCOMCT2.OCX"; DestDir: "{sys}"; Flags: restartreplace sharedfile regserver

; カスタムDLL
Source: "bin\MyCustom.dll"; DestDir: "{app}"; Flags: ignoreversion regserver

; データファイル
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

; ドキュメント
Source: "docs\UserManual.pdf"; DestDir: "{app}\docs"; Flags: ignoreversion isreadme

[Registry]
; アプリケーション設定
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; Flags: uninsdeletekeyifempty
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

; ファイル関連付け
Root: HKCR; Subkey: ".myext"; ValueType: string; ValueName: ""; ValueData: "MyAppDocument"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "MyAppDocument"; ValueType: string; ValueName: ""; ValueData: "My App Document"; Flags: uninsdeletekey
Root: HKCR; Subkey: "MyAppDocument\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCR; Subkey: "MyAppDocument\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; VC++ランタイムインストール
Filename: "{tmp}\vcredist_x86.exe"; Parameters: "/quiet"; Check: VCRedistNeedsInstall; StatusMsg: "Installing VC++ Runtime..."

; アプリケーション起動
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; アンインストール時のクリーンアップ
Filename: "{cmd}"; Parameters: "/c "taskkill /im {#MyAppExeName} /f""; Flags: runhidden

[Code]
// カスタムコード
var
  DownloadPage: TDownloadWizardPage;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded file to {tmp}: %s', [FileName]));
  Result := True;
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), @OnDownloadProgress);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    
    // VC++ランタイムダウンロード
    if VCRedistNeedsInstall then
      DownloadPage.Add('https://download.microsoft.com/download/vcredist_x86.exe', 'vcredist_x86.exe', '');
    
    DownloadPage.Show;
    try
      try
        DownloadPage.Download;
        Result := True;
      except
        if DownloadPage.AbortedByUser then
          Log('Aborted by user.')
        else
          SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end else
    Result := True;
end;

function VCRedistNeedsInstall: Boolean;
var
  Version: String;
begin
  if RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x86', 'Version', Version) then
    Result := (CompareStr(Version, 'v14.0.24215.01') < 0)
  else
    Result := True;
end;

function InitializeUninstall(): Boolean;
begin
  Result := MsgBox('アプリケーションをアンインストールしますか？', mbConfirmation, MB_YESNO) = IDYES;
end;
```

### 2. MSIパッケージ (WiX Toolset)

#### Product_Advanced.wxs
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi" 
     xmlns:util="http://schemas.microsoft.com/wix/UtilExtension">
  
  <?define ProductName = "My VB6 Application" ?>
  <?define ProductVersion = "1.0.0.0" ?>
  <?define ProductManufacturer = "My Company" ?>
  <?define ProductCode = "{12345678-1234-1234-1234-123456789012}" ?>
  <?define UpgradeCode = "{87654321-4321-4321-4321-210987654321}" ?>
  
  <Product Id="$(var.ProductCode)" 
           Name="$(var.ProductName)" 
           Language="1033" 
           Version="$(var.ProductVersion)" 
           Manufacturer="$(var.ProductManufacturer)" 
           UpgradeCode="$(var.UpgradeCode)">
    
    <Package InstallerVersion="300" 
             Compressed="yes" 
             InstallScope="perMachine" 
             Platform="x86" />
    
    <!-- アップグレードロジック -->
    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    
    <MediaTemplate EmbedCab="yes" />
    
    <!-- カスタムアクション -->
    <CustomAction Id="KillApp" 
                  Directory="INSTALLDIR" 
                  ExeCommand="cmd.exe /c taskkill /im MyApp.exe /f" 
                  Execute="immediate" 
                  Return="ignore" />
    
    <!-- インストールシーケンス -->
    <InstallExecuteSequence>
      <Custom Action="KillApp" Before="InstallValidate" />
    </InstallExecuteSequence>
    
    <!-- 機能定義 -->
    <Feature Id="ProductFeature" Title="$(var.ProductName)" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
      <ComponentGroupRef Id="RuntimeComponents" />
      <ComponentGroupRef Id="RegistryComponents" />
    </Feature>
    
    <!-- ディレクトリ構造 -->
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLDIR" Name="$(var.ProductName)">
          <Directory Id="DataFolder" Name="data" />
          <Directory Id="DocsFolder" Name="docs" />
        </Directory>
      </Directory>
      
      <Directory Id="SystemFolder" />
      
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="$(var.ProductName)" />
      </Directory>
      
      <Directory Id="DesktopFolder" />
    </Directory>
    
    <!-- プロダクトコンポーネント -->
    <ComponentGroup Id="ProductComponents" Directory="INSTALLDIR">
      <Component Id="MainExecutable" Guid="{11111111-1111-1111-1111-111111111111}">
        <File Id="MyApp.exe" Source="$(var.SourceDir)\MyApp.exe" KeyPath="yes">
          <Shortcut Id="StartMenuShortcut" 
                    Directory="ApplicationProgramsFolder" 
                    Name="$(var.ProductName)" 
                    WorkingDirectory="INSTALLDIR" 
                    Icon="MyApp.ico" 
                    IconIndex="0" 
                    Advertise="yes" />
          <Shortcut Id="DesktopShortcut" 
                    Directory="DesktopFolder" 
                    Name="$(var.ProductName)" 
                    WorkingDirectory="INSTALLDIR" 
                    Icon="MyApp.ico" 
                    IconIndex="0" 
                    Advertise="yes" />
        </File>
        <File Id="MyApp.exe.manifest" Source="$(var.SourceDir)\MyApp.exe.manifest" />
      </Component>
      
      <Component Id="CustomDLL" Guid="{22222222-2222-2222-2222-222222222222}">
        <File Id="MyCustom.dll" Source="$(var.SourceDir)\MyCustom.dll" KeyPath="yes">
          <TypeLib Id="{12345678-1234-1234-1234-123456789012}" 
                   Description="My Custom Library" 
                   Language="0" 
                   MajorVersion="1" 
                   MinorVersion="0" />
        </File>
      </Component>
    </ComponentGroup>
    
    <!-- ランタイムコンポーネント -->
    <ComponentGroup Id="RuntimeComponents" Directory="SystemFolder">
      <Component Id="VB6Runtime" Guid="{33333333-3333-3333-3333-333333333333}">
        <File Id="MSVBVM60.DLL" 
              Source="$(var.RedistDir)\MSVBVM60.DLL" 
              KeyPath="yes" 
              Checksum="yes" />
      </Component>
      
      <Component Id="CommonControls" Guid="{44444444-4444-4444-4444-444444444444}">
        <File Id="MSCOMCTL.OCX" 
              Source="$(var.RedistDir)\MSCOMCTL.OCX" 
              KeyPath="yes" 
              SelfRegCost="1" />
      </Component>
    </ComponentGroup>
    
    <!-- レジストリコンポーネント -->
    <ComponentGroup Id="RegistryComponents" Directory="TARGETDIR">
      <Component Id="RegistryEntries" Guid="{55555555-5555-5555-5555-555555555555}">
        <RegistryKey Root="HKLM" 
                     Key="Software\$(var.ProductManufacturer)\$(var.ProductName)">
          <RegistryValue Name="InstallPath" Type="string" Value="[INSTALLDIR]" />
          <RegistryValue Name="Version" Type="string" Value="$(var.ProductVersion)" />
        </RegistryKey>
      </Component>
    </ComponentGroup>
    
    <!-- アイコン定義 -->
    <Icon Id="MyApp.ico" SourceFile="$(var.SourceDir)\MyApp.ico" />
    <Property Id="ARPPRODUCTICON" Value="MyApp.ico" />
    
    <!-- UI定義 -->
    <UIRef Id="WixUI_InstallDir" />
    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLDIR" />
    
    <!-- ライセンスファイル -->
    <WixVariable Id="WixUILicenseRtf" Value="License.rtf" />
    <WixVariable Id="WixUIBannerBmp" Value="Banner.bmp" />
    <WixVariable Id="WixUIDialogBmp" Value="Dialog.bmp" />
  </Product>
</Wix>
```

## 配布方法

### 1. Webダウンロード

#### download.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>Download My Application</title>
    <script>
    function detectOS() {
        var userAgent = window.navigator.userAgent;
        var platform = window.navigator.platform;
        var macosPlatforms = ['Macintosh', 'MacIntel', 'MacPPC', 'Mac68K'];
        var windowsPlatforms = ['Win32', 'Win64', 'Windows', 'WinCE'];
        var iosPlatforms = ['iPhone', 'iPad', 'iPod'];
        
        if (windowsPlatforms.indexOf(platform) !== -1) {
            return 'Windows';
        }
        
        return 'Unsupported';
    }
    
    function downloadApp() {
        var os = detectOS();
        
        if (os === 'Windows') {
            // バージョンチェック
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/api/latest-version', true);
            xhr.onload = function() {
                if (xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    window.location.href = data.downloadUrl;
                }
            };
            xhr.send();
        } else {
            alert('This application requires Windows.');
        }
    }
    </script>
</head>
<body>
    <h1>Download My Application</h1>
    <button onclick="downloadApp()">Download for Windows</button>
    
    <h2>System Requirements</h2>
    <ul>
        <li>Windows 7 or later</li>
        <li>32-bit or 64-bit processor</li>
        <li>2 GB RAM minimum</li>
        <li>100 MB free disk space</li>
    </ul>
</body>
</html>
```

### 2. 自動更新システム

#### UpdateChecker.cls
```vb
VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "clsUpdateChecker"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
Option Explicit

Private Const UPDATE_SERVER As String = "https://updates.example.com"
Private Const UPDATE_CHECK_URL As String = "/api/check-update"

Public Event UpdateAvailable(Version As String, DownloadUrl As String)
Public Event UpdateCheckFailed(ErrorMessage As String)

Public Sub CheckForUpdates()
    Dim http As Object
    Dim url As String
    Dim currentVersion As String
    
    On Error GoTo ErrorHandler
    
    ' 現在のバージョン
    currentVersion = App.Major & "." & App.Minor & "." & App.Revision
    
    ' URL構築
    url = UPDATE_SERVER & UPDATE_CHECK_URL & "?version=" & currentVersion & _
          "&product=" & URLEncode(App.ProductName)
    
    ' HTTPリクエスト
    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    http.Open "GET", url, True
    http.SetRequestHeader "User-Agent", App.ProductName & "/" & currentVersion
    http.Send
    
    ' タイムアウト設定（10秒）
    http.WaitForResponse 10
    
    If http.Status = 200 Then
        ProcessUpdateResponse http.ResponseText
    Else
        RaiseEvent UpdateCheckFailed("Server returned status: " & http.Status)
    End If
    
    Exit Sub
    
ErrorHandler:
    RaiseEvent UpdateCheckFailed("Update check error: " & Err.Description)
End Sub

Private Sub ProcessUpdateResponse(ResponseText As String)
    ' JSONレスポンス解析
    ' {"hasUpdate": true, "version": "1.1.0", "downloadUrl": "...", "releaseNotes": "..."}
    
    Dim json As Object
    Set json = CreateObject("ScriptControl")
    json.Language = "JScript"
    json.AddCode "function parseJSON(s) { return eval('(' + s + ')'); }"
    
    Dim updateInfo As Object
    Set updateInfo = json.Run("parseJSON", ResponseText)
    
    If updateInfo.hasUpdate Then
        RaiseEvent UpdateAvailable(updateInfo.version, updateInfo.downloadUrl)
    End If
End Sub

Private Function URLEncode(Text As String) As String
    Dim i As Integer
    Dim char As String
    Dim result As String
    
    For i = 1 To Len(Text)
        char = Mid(Text, i, 1)
        Select Case Asc(char)
            Case 48 To 57, 65 To 90, 97 To 122
                result = result & char
            Case Else
                result = result & "%" & Right("0" & Hex(Asc(char)), 2)
        End Select
    Next i
    
    URLEncode = result
End Function
```

## トラブルシューティング

### 1. 一般的な問題と解決策

| 問題 | 原因 | 解決策 |
|------|------|----------|
| 「MSVBVM60.DLLが見つかりません」 | VB6ランタイム未インストール | VB6ランタイムをインストール |
| 「Component 'XXX.ocx' not registered」 | OCX未登録 | regsvr32で登録 |
| 「Run-time error '429'」 | COMコンポーネントエラー | 依存DLL確認・再登録 |
| 「Permission denied」 | UAC/権限不足 | 管理者権限で実行 |
| 文字化け | 文字コード不一致 | SJISエンコーディング確認 |

### 2. デバッグ用ツール

#### dependency_checker.vbs
```vbscript
' VB6 Dependency Checker Script
Option Explicit

Dim fso, shell, args
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
Set args = WScript.Arguments

If args.Count = 0 Then
    WScript.Echo "Usage: cscript dependency_checker.vbs <exe_path>"
    WScript.Quit 1
End If

Dim exePath
exePath = args(0)

WScript.Echo "Checking dependencies for: " & exePath
WScript.Echo String(50, "-")

' 基本的な依存関係チェック
CheckFile "MSVBVM60.DLL", "VB6 Runtime"
CheckFile "OLEAUT32.DLL", "OLE Automation"
CheckFile "OLEPRO32.DLL", "OLE Property Support"
CheckFile "COMCTL32.DLL", "Common Controls"

' OCXチェック
CheckOCX "COMDLG32.OCX", "{F9043C88-F6F2-101A-A3C9-08002B2F49FB}"
CheckOCX "MSCOMCTL.OCX", "{831FDD16-0C5C-11D2-A9FC-0000F8754DA1}"

' レポート出力
WScript.Echo vbCrLf & "Check completed."

Sub CheckFile(fileName, description)
    Dim paths, path, found
    paths = Array( _
        shell.ExpandEnvironmentStrings("%SystemRoot%\System32\"), _
        shell.ExpandEnvironmentStrings("%SystemRoot%\SysWOW64\"), _
        fso.GetParentFolderName(exePath) & "\" _
    )
    
    found = False
    For Each path In paths
        If fso.FileExists(path & fileName) Then
            WScript.Echo "[√] " & fileName & " - " & description & " (Found: " & path & ")"
            found = True
            Exit For
        End If
    Next
    
    If Not found Then
        WScript.Echo "[X] " & fileName & " - " & description & " (NOT FOUND)"
    End If
End Sub

Sub CheckOCX(fileName, clsid)
    On Error Resume Next
    Dim obj
    Set obj = CreateObject("WScript.Shell")
    
    ' レジストリチェック
    Dim regPath
    regPath = "HKCR\CLSID\" & clsid & "\"
    
    obj.RegRead regPath
    If Err.Number = 0 Then
        WScript.Echo "[√] " & fileName & " - Registered (CLSID: " & clsid & ")"
    Else
        WScript.Echo "[X] " & fileName & " - NOT Registered"
    End If
    
    On Error GoTo 0
End Sub
```

### 3. インストール後確認スクリプト

#### post_install_check.ps1
```powershell
# Post Installation Verification Script
param(
    [string]$InstallPath = "C:\Program Files (x86)\MyApp"
)

Write-Host "Post Installation Check" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green

# 1. ファイル存在確認
$requiredFiles = @(
    "MyApp.exe",
    "MyApp.exe.manifest",
    "MyCustom.dll"
)

Write-Host "`n1. Checking Files:" -ForegroundColor Yellow
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $InstallPath $file
    if (Test-Path $filePath) {
        Write-Host "  [√] $file" -ForegroundColor Green
    } else {
        Write-Host "  [X] $file - Missing!" -ForegroundColor Red
    }
}

# 2. レジストリ確認
$Write-Host "`n2. Checking Registry:" -ForegroundColor Yellow
$regPath = "HKLM:\Software\MyCompany\MyApp"
if (Test-Path $regPath) {
    $installPathReg = Get-ItemProperty -Path $regPath -Name "InstallPath" -ErrorAction SilentlyContinue
    if ($installPathReg) {
        Write-Host "  [√] Registry key exists" -ForegroundColor Green
        Write-Host "      InstallPath: $($installPathReg.InstallPath)" -ForegroundColor Gray
    }
} else {
    Write-Host "  [X] Registry key missing" -ForegroundColor Red
}

# 3. COMコンポーネント確認
Write-Host "`n3. Checking COM Components:" -ForegroundColor Yellow
try {
    $obj = New-Object -ComObject "MyCustom.MyClass" -ErrorAction Stop
    Write-Host "  [√] COM object created successfully" -ForegroundColor Green
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($obj) | Out-Null
} catch {
    Write-Host "  [X] COM object creation failed" -ForegroundColor Red
    Write-Host "      Error: $_" -ForegroundColor Red
}

# 4. ショートカット確認
Write-Host "`n4. Checking Shortcuts:" -ForegroundColor Yellow
$shortcuts = @(
    [Environment]::GetFolderPath("Desktop"),
    [Environment]::GetFolderPath("StartMenu")
)

foreach ($path in $shortcuts) {
    $shortcutPath = Join-Path $path "MyApp.lnk"
    if (Test-Path $shortcutPath) {
        Write-Host "  [√] Shortcut found: $shortcutPath" -ForegroundColor Green
    }
}

# 結果サマリ
Write-Host "`nInstallation check completed." -ForegroundColor Green
```