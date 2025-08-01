# Windows XP/2003 デプロイメントガイド - .NET Framework 4.0

## 1. 対応環境と要件

### システム要件
```yaml
Windows XP:
  最小バージョン: Windows XP SP3 (x86/x64)
  .NET Framework: 4.0 Client Profile または Full
  Windows Installer: 3.1以降
  RAM: 512MB以上（推奨1GB）
  
Windows Server 2003:
  最小バージョン: Windows Server 2003 R2 SP2
  .NET Framework: 4.0 Full
  Windows Installer: 3.1以降
  RAM: 1GB以上（推奨2GB）
```

### .NET Framework 4.0 インストール要件
```xml
<!-- 前提条件 -->
<prerequisites>
  <os>
    <windowsXP servicePackLevel="3" />
    <windowsServer2003 servicePackLevel="2" />
  </os>
  <runtime>
    <windowsInstaller version="3.1" />
    <microsoftVisualCPlusPlus version="2010" />
  </runtime>
</prerequisites>
```

## 2. .NET Framework 4.0 事前インストール

### オフラインインストーラーの準備
```batch
:: .NET Framework 4.0 フルインストーラーのダウンロード
:: ファイルサイズ: 約48MB（Web）/ 約870MB（フル）

:: Windows XP用（Client Profile）
dotNetFx40_Client_x86_x64.exe

:: Windows Server 2003用（Full）
dotNetFx40_Full_x86_x64.exe
```

### サイレントインストールスクリプト
```batch
@echo off
:: install_dotnet40.bat - .NET Framework 4.0 サイレントインストール

echo .NET Framework 4.0 をインストールしています...

:: OS判定
ver | findstr /i "5\.1\." > nul
if %ERRORLEVEL% EQU 0 (
    echo Windows XP を検出しました
    set INSTALLER=dotNetFx40_Client_x86_x64.exe
) else (
    echo Windows Server 2003 を検出しました
    set INSTALLER=dotNetFx40_Full_x86_x64.exe
)

:: インストール実行
%INSTALLER% /q /norestart
if %ERRORLEVEL% EQU 0 (
    echo インストールが完了しました
) else if %ERRORLEVEL% EQU 3010 (
    echo インストールが完了しました（再起動が必要です）
) else (
    echo エラーが発生しました: %ERRORLEVEL%
)
```

## 3. アプリケーション設定（app.config）

### Windows XP/2003 対応設定
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <!-- .NET Framework 4.0 明示的指定 -->
  <startup>
    <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.0"/>
    <!-- Windows XP互換性設定 -->
    <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
      <application>
        <!-- Windows XP -->
        <supportedOS Id="{e2011457-1546-43c5-a5fe-008deee3d3f0}"/>
        <!-- Windows Server 2003 -->
        <supportedOS Id="{e2011457-1546-43c5-a5fe-008deee3d3f1}"/>
      </application>
    </compatibility>
  </startup>
  
  <!-- Windows XP用のセキュリティプロトコル設定 -->
  <system.net>
    <settings>
      <!-- TLS 1.0をサポート（Windows XPはTLS 1.2非対応） -->
      <httpWebRequest useUnsafeHeaderParsing="true"/>
    </settings>
    <connectionManagement>
      <add address="*" maxconnection="10"/>
    </connectionManagement>
  </system.net>
  
  <!-- アプリケーション設定 -->
  <appSettings>
    <!-- Windows XP対応フラグ -->
    <add key="EnableWindowsXPCompatibility" value="true"/>
    <!-- レガシーレンダリングモード -->
    <add key="UseGDIPlusTextRendering" value="true"/>
    <!-- 高DPI無効化（Windows XPはDPI認識なし） -->
    <add key="EnableHighDpiSupport" value="false"/>
  </appSettings>
</configuration>
```

## 4. ClickOnce デプロイメント

### Windows XP/2003 対応 ClickOnce マニフェスト
```xml
<?xml version="1.0" encoding="utf-8"?>
<asmv1:assembly manifestVersion="1.0" xmlns="urn:schemas-microsoft-com:asm.v1" 
                xmlns:asmv1="urn:schemas-microsoft-com:asm.v1" 
                xmlns:asmv2="urn:schemas-microsoft-com:asm.v2" 
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  
  <assemblyIdentity version="1.0.0.0" name="BusinessManagementApp.app"/>
  
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v2">
    <security>
      <requestedPrivileges xmlns="urn:schemas-microsoft-com:asm.v3">
        <!-- Windows XP用の最小権限 -->
        <requestedExecutionLevel level="asInvoker" uiAccess="false" />
      </requestedPrivileges>
    </security>
  </trustInfo>
  
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*" />
    </dependentAssembly>
  </dependency>
  
  <!-- .NET Framework 4.0 依存関係 -->
  <dependency>
    <dependentAssembly>
      <assemblyIdentity name="Microsoft.CSharp" version="4.0.0.0" 
                       publicKeyToken="b03f5f7f11d50a3a" />
    </dependentAssembly>
  </dependency>
</asmv1:assembly>
```

### ClickOnce 発行設定
```xml
<!-- プロジェクトファイル(.csproj)の設定 -->
<PropertyGroup>
  <PublishUrl>\\server\apps\BusinessManagementApp\</PublishUrl>
  <InstallUrl>http://server/apps/BusinessManagementApp/</InstallUrl>
  <UpdateEnabled>true</UpdateEnabled>
  <UpdateMode>Foreground</UpdateMode>
  <UpdateInterval>1</UpdateInterval>
  <UpdateIntervalUnits>Days</UpdateIntervalUnits>
  <UpdatePeriodically>true</UpdatePeriodically>
  <UpdateRequired>false</UpdateRequired>
  <MapFileExtensions>true</MapFileExtensions>
  <ApplicationRevision>0</ApplicationRevision>
  <ApplicationVersion>1.0.0.%2a</ApplicationVersion>
  <UseApplicationTrust>false</UseApplicationTrust>
  <BootstrapperEnabled>true</BootstrapperEnabled>
  
  <!-- Windows XP対応設定 -->
  <TargetFrameworkVersion>v4.0</TargetFrameworkVersion>
  <TargetFrameworkProfile>Client</TargetFrameworkProfile>
</PropertyGroup>

<!-- 前提条件 -->
<ItemGroup>
  <BootstrapperPackage Include=".NETFramework,Version=v4.0,Profile=Client">
    <Visible>False</Visible>
    <ProductName>Microsoft .NET Framework 4 Client Profile</ProductName>
    <Install>true</Install>
  </BootstrapperPackage>
  <BootstrapperPackage Include="Microsoft.Windows.Installer.3.1">
    <Visible>False</Visible>
    <ProductName>Windows Installer 3.1</ProductName>
    <Install>true</Install>
  </BootstrapperPackage>
</ItemGroup>
```

## 5. MSI インストーラー作成

### WiX による Windows XP/2003 対応インストーラー
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="業務管理アプリケーション" 
           Language="1041" 
           Version="1.0.0.0" 
           Manufacturer="Your Company" 
           UpgradeCode="12345678-1234-1234-1234-123456789012">
    
    <Package InstallerVersion="301" 
             Compressed="yes" 
             InstallScope="perMachine"
             Platform="x86" />
    
    <!-- Windows XP/2003 サポート -->
    <Condition Message="このアプリケーションには Windows XP SP3 以降が必要です。">
      <![CDATA[VersionNT >= 501]]>
    </Condition>
    
    <!-- .NET Framework 4.0 チェック -->
    <PropertyRef Id="NETFRAMEWORK40CLIENT" />
    <Condition Message="このアプリケーションには .NET Framework 4.0 が必要です。">
      <![CDATA[Installed OR NETFRAMEWORK40CLIENT]]>
    </Condition>
    
    <!-- インストールディレクトリ -->
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="CompanyFolder" Name="YourCompany">
          <Directory Id="INSTALLFOLDER" Name="BusinessManagementApp" />
        </Directory>
      </Directory>
      
      <!-- スタートメニュー -->
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="業務管理アプリケーション" />
      </Directory>
    </Directory>
    
    <!-- ファイルコンポーネント -->
    <DirectoryRef Id="INSTALLFOLDER">
      <Component Id="MainExecutable" Guid="*">
        <File Id="BusinessManagementApp.exe" 
              Source="$(var.BusinessManagementApp.TargetPath)" 
              KeyPath="yes" />
        
        <!-- Windows XP用の設定ファイル -->
        <File Id="BusinessManagementApp.exe.config" 
              Source="$(var.BusinessManagementApp.TargetPath).config" />
      </Component>
    </DirectoryRef>
    
    <!-- 機能定義 -->
    <Feature Id="ProductFeature" Title="メインアプリケーション" Level="1">
      <ComponentRef Id="MainExecutable" />
    </Feature>
  </Product>
</Wix>
```

## 6. 手動デプロイメント（XCopy デプロイ）

### デプロイメントスクリプト
```batch
@echo off
:: deploy_xp.bat - Windows XP/2003 手動デプロイメント

set APP_NAME=BusinessManagementApp
set SOURCE_DIR=%~dp0
set TARGET_DIR=C:\Program Files\YourCompany\%APP_NAME%

echo %APP_NAME% をインストールしています...

:: ディレクトリ作成
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

:: ファイルコピー
xcopy "%SOURCE_DIR%*.exe" "%TARGET_DIR%" /Y
xcopy "%SOURCE_DIR%*.dll" "%TARGET_DIR%" /Y
xcopy "%SOURCE_DIR%*.config" "%TARGET_DIR%" /Y

:: ショートカット作成（VBScript使用）
echo Set WshShell = CreateObject("WScript.Shell") > CreateShortcut.vbs
echo Set oShellLink = WshShell.CreateShortcut("%USERPROFILE%\デスクトップ\%APP_NAME%.lnk") >> CreateShortcut.vbs
echo oShellLink.TargetPath = "%TARGET_DIR%\%APP_NAME%.exe" >> CreateShortcut.vbs
echo oShellLink.WindowStyle = 1 >> CreateShortcut.vbs
echo oShellLink.IconLocation = "%TARGET_DIR%\%APP_NAME%.exe, 0" >> CreateShortcut.vbs
echo oShellLink.WorkingDirectory = "%TARGET_DIR%" >> CreateShortcut.vbs
echo oShellLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo インストールが完了しました。
pause
```

## 7. Windows XP/2003 特有の考慮事項

### メモリ管理
```csharp
// Windows XP のメモリ制限を考慮した実装
public class MemoryOptimizedDataManager
{
    private const int MAX_ITEMS_IN_MEMORY = 1000; // Windows XP用の制限
    
    public void ProcessLargeDataSet(IEnumerable<DataItem> items)
    {
        var batch = new List<DataItem>(MAX_ITEMS_IN_MEMORY);
        
        foreach (var item in items)
        {
            batch.Add(item);
            
            if (batch.Count >= MAX_ITEMS_IN_MEMORY)
            {
                ProcessBatch(batch);
                batch.Clear();
                
                // Windows XP用：明示的なガベージコレクション
                if (Environment.OSVersion.Version.Major == 5)
                {
                    GC.Collect();
                    GC.WaitForPendingFinalizers();
                }
            }
        }
        
        if (batch.Count > 0)
        {
            ProcessBatch(batch);
        }
    }
}
```

### セキュリティプロトコル対応
```csharp
// Windows XP は TLS 1.2 非対応のため、TLS 1.0 を使用
public class LegacyWebClient
{
    static LegacyWebClient()
    {
        // Windows XP/2003 の場合、TLS 1.0 を明示的に設定
        if (Environment.OSVersion.Version.Major == 5)
        {
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls;
        }
    }
    
    public string DownloadString(string url)
    {
        using (var client = new WebClient())
        {
            // Windows XP用の追加ヘッダー
            client.Headers.Add("User-Agent", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1)");
            return client.DownloadString(url);
        }
    }
}
```

## 8. トラブルシューティング

### よくある問題と解決方法

#### 1. .NET Framework 4.0 がインストールできない
```batch
:: Windows XP SP3 の確認
ver | findstr /i "5\.1\.2600"
if %ERRORLEVEL% NEQ 0 (
    echo Windows XP SP3 が必要です
    echo Windows Update で SP3 をインストールしてください
)

:: Windows Installer 3.1 の確認
msiexec /?
:: バージョンが 3.1 未満の場合は WindowsInstaller-KB893803-v2-x86.exe をインストール
```

#### 2. アプリケーションが起動しない
```xml
<!-- app.config に以下を追加 -->
<configuration>
  <runtime>
    <!-- Windows XP用の互換性設定 -->
    <legacyCorruptedStateExceptionsPolicy enabled="true"/>
    <NetFx40_LegacySecurityPolicy enabled="true"/>
  </runtime>
</configuration>
```

#### 3. フォントレンダリングの問題
```csharp
// Windows XP でのフォントレンダリング改善
public partial class MainForm : Form
{
    protected override void OnLoad(EventArgs e)
    {
        base.OnLoad(e);
        
        // Windows XP の場合、ClearType を無効化
        if (Environment.OSVersion.Version.Major == 5)
        {
            SetStyle(ControlStyles.AllPaintingInWmPaint | 
                    ControlStyles.UserPaint | 
                    ControlStyles.DoubleBuffer, true);
        }
    }
}
```

## 9. パフォーマンス最適化

### Windows XP/2003 向け最適化
```csharp
public static class WindowsXPOptimizations
{
    public static void ApplyOptimizations()
    {
        if (Environment.OSVersion.Version.Major != 5)
            return;
            
        // 1. ビジュアルスタイルの簡素化
        Application.VisualStyleState = VisualStyleState.NonClientAreaEnabled;
        
        // 2. ダブルバッファリングの調整
        typeof(Control).GetProperty("DoubleBuffered", 
            BindingFlags.NonPublic | BindingFlags.Instance);
            
        // 3. GDI+ の最適化
        Application.SetCompatibleTextRenderingDefault(false);
    }
}
```

このガイドに従うことで、Windows XP SP3 および Windows Server 2003 R2 環境で .NET Framework 4.0 アプリケーションを確実にデプロイできます。