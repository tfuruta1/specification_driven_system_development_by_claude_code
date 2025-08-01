# Windows デスクトップアプリケーション配布ガイド - .NET Framework 4.8

## 1. 配布要件と前提条件

### システム要件
```yaml
最小要件:
  OS: Windows 10 バージョン 1607 以上
  .NET Framework: 4.8
  メモリ: 4GB RAM
  ディスク: 500MB の空き容量
  
推奨要件:
  OS: Windows 10 バージョン 21H2 以上 / Windows 11
  メモリ: 8GB RAM 以上
  ディスク: 1GB の空き容量
  ディスプレイ: 1920x1080 以上（高DPI対応）
```

### 必要なランタイム
```xml
<!-- 依存関係一覧 -->
<dependencies>
  <runtime>
    <package id=".NET Framework 4.8" version="4.8" />
    <package id="Visual C++ 2019 Redistributable" version="14.28" />
    <package id="SQL Server Compact 4.0 SP1" version="4.0.8876.1" optional="true" />
  </runtime>
</dependencies>
```

## 2. ClickOnce配布

### ClickOnce設定（プロジェクトファイル）
```xml
<PropertyGroup>
  <PublishUrl>\\fileserver\apps\EnterpriseApp\</PublishUrl>
  <InstallUrl>https://apps.company.com/EnterpriseApp/</InstallUrl>
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
  <PublishWizardCompleted>true</PublishWizardCompleted>
  <BootstrapperEnabled>true</BootstrapperEnabled>
</PropertyGroup>

<!-- 前提条件の設定 -->
<ItemGroup>
  <BootstrapperPackage Include=".NETFramework,Version=v4.8">
    <Visible>False</Visible>
    <ProductName>Microsoft .NET Framework 4.8</ProductName>
    <Install>true</Install>
  </BootstrapperPackage>
  <BootstrapperPackage Include="Microsoft.Windows.Installer.4.5">
    <Visible>False</Visible>
    <ProductName>Windows Installer 4.5</ProductName>
    <Install>true</Install>
  </BootstrapperPackage>
</ItemGroup>
```

### 自動更新の実装
```csharp
public class AutoUpdateManager
{
    private static readonly ILogger Logger = LogManager.GetCurrentClassLogger();
    
    public static async Task CheckForUpdatesAsync()
    {
        if (!ApplicationDeployment.IsNetworkDeployed)
        {
            Logger.Info("アプリケーションはClickOnceで配布されていません");
            return;
        }
        
        try
        {
            var deployment = ApplicationDeployment.CurrentDeployment;
            
            // 更新チェック
            var info = await Task.Run(() => deployment.CheckForDetailedUpdate());
            
            if (info.UpdateAvailable)
            {
                var message = $"新しいバージョン {info.AvailableVersion} が利用可能です。\n" +
                             $"現在のバージョン: {deployment.CurrentVersion}\n" +
                             $"更新サイズ: {info.UpdateSizeBytes / 1024 / 1024:F2} MB\n\n" +
                             "今すぐ更新しますか？";
                
                if (info.IsUpdateRequired)
                {
                    message += "\n\nこの更新は必須です。";
                }
                
                var result = MessageBox.Show(
                    message, 
                    "更新の確認", 
                    MessageBoxButtons.YesNo, 
                    MessageBoxIcon.Information);
                
                if (result == DialogResult.Yes)
                {
                    await UpdateApplicationAsync();
                }
            }
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "更新チェック中にエラーが発生しました");
        }
    }
    
    private static async Task UpdateApplicationAsync()
    {
        var deployment = ApplicationDeployment.CurrentDeployment;
        
        using (var progressForm = new UpdateProgressForm())
        {
            deployment.UpdateProgressChanged += (s, e) =>
            {
                progressForm.UpdateProgress(e.ProgressPercentage, e.BytesCompleted, e.BytesTotal);
            };
            
            deployment.UpdateCompleted += (s, e) =>
            {
                if (e.Error != null)
                {
                    Logger.Error(e.Error, "更新に失敗しました");
                    MessageBox.Show("更新に失敗しました。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
                else
                {
                    MessageBox.Show("更新が完了しました。アプリケーションを再起動してください。", 
                        "更新完了", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    Application.Restart();
                }
            };
            
            progressForm.Show();
            await Task.Run(() => deployment.UpdateAsync());
        }
    }
}
```

## 3. MSIインストーラー作成（WiX Toolset）

### WiX プロジェクト設定（Product.wxs）
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="エンタープライズアプリケーション" 
           Language="1041" 
           Version="1.0.0.0" 
           Manufacturer="Your Company" 
           UpgradeCode="12345678-1234-1234-1234-123456789012">
    
    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine" 
             Platform="x64" />
    
    <MajorUpgrade DowngradeErrorMessage="新しいバージョンが既にインストールされています。" />
    <MediaTemplate EmbedCab="yes" />
    
    <!-- 前提条件チェック -->
    <PropertyRef Id="NETFRAMEWORK45" />
    <Condition Message="このアプリケーションには .NET Framework 4.8 が必要です。">
      <![CDATA[Installed OR NETFRAMEWORK45 >= "#528040"]]>
    </Condition>
    
    <!-- インストール先 -->
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFiles64Folder">
        <Directory Id="CompanyFolder" Name="YourCompany">
          <Directory Id="INSTALLFOLDER" Name="EnterpriseApp" />
        </Directory>
      </Directory>
      
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="エンタープライズアプリケーション" />
      </Directory>
      
      <Directory Id="DesktopFolder" />
    </Directory>
    
    <!-- コンポーネント -->
    <Feature Id="ProductFeature" Title="メインアプリケーション" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
      <ComponentRef Id="ApplicationShortcut" />
      <ComponentRef Id="DesktopShortcut" />
    </Feature>
    
    <!-- ショートカット -->
    <DirectoryRef Id="ApplicationProgramsFolder">
      <Component Id="ApplicationShortcut" Guid="*">
        <Shortcut Id="ApplicationStartMenuShortcut"
                  Name="エンタープライズアプリケーション"
                  Description="エンタープライズアプリケーションを起動"
                  Target="[#EnterpriseApp.exe]"
                  WorkingDirectory="INSTALLFOLDER"
                  Icon="AppIcon.ico" />
        <RemoveFolder Id="CleanUpShortCut" Directory="ApplicationProgramsFolder" On="uninstall" />
        <RegistryValue Root="HKCU" Key="Software\YourCompany\EnterpriseApp" 
                       Name="installed" Type="integer" Value="1" KeyPath="yes" />
      </Component>
    </DirectoryRef>
    
    <!-- レジストリ設定 -->
    <Component Id="RegistryEntries" Guid="*" Directory="INSTALLFOLDER">
      <RegistryKey Root="HKLM" Key="Software\YourCompany\EnterpriseApp">
        <RegistryValue Type="string" Name="InstallPath" Value="[INSTALLFOLDER]" />
        <RegistryValue Type="string" Name="Version" Value="[ProductVersion]" />
      </RegistryKey>
    </Component>
  </Product>
</Wix>
```

### カスタムアクション（データベース初期化等）
```csharp
[CustomAction]
public static ActionResult InitializeDatabase(Session session)
{
    session.Log("Begin InitializeDatabase");
    
    try
    {
        var installFolder = session["INSTALLFOLDER"];
        var dbPath = Path.Combine(installFolder, "Data", "EnterpriseApp.sdf");
        
        // SQL Server Compact データベースの作成
        if (!File.Exists(dbPath))
        {
            Directory.CreateDirectory(Path.GetDirectoryName(dbPath));
            
            using (var engine = new SqlCeEngine($"Data Source={dbPath}"))
            {
                engine.CreateDatabase();
            }
            
            // 初期テーブル作成
            using (var connection = new SqlCeConnection($"Data Source={dbPath}"))
            {
                connection.Open();
                ExecuteInitialSchema(connection);
            }
        }
        
        return ActionResult.Success;
    }
    catch (Exception ex)
    {
        session.Log($"Error in InitializeDatabase: {ex.Message}");
        return ActionResult.Failure;
    }
}
```

## 4. アプリケーション設定とセキュリティ

### app.manifest（UAC、DPI対応）
```xml
<?xml version="1.0" encoding="utf-8"?>
<assembly manifestVersion="1.0" xmlns="urn:schemas-microsoft-com:asm.v1">
  <assemblyIdentity version="1.0.0.0" name="EnterpriseApp.app"/>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v2">
    <security>
      <requestedPrivileges xmlns="urn:schemas-microsoft-com:asm.v3">
        <!-- UAC 設定: asInvoker / highestAvailable / requireAdministrator -->
        <requestedExecutionLevel level="asInvoker" uiAccess="false" />
      </requestedPrivileges>
    </security>
  </trustInfo>
  
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10/11 サポート -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}" />
    </application>
  </compatibility>
  
  <!-- DPI 対応 -->
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/PM</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>
```

### コード署名
```powershell
# 自己署名証明書の作成（開発用）
$cert = New-SelfSignedCertificate -Type CodeSigningCert `
    -Subject "CN=YourCompany Code Signing" `
    -KeyUsage DigitalSignature `
    -FriendlyName "EnterpriseApp Code Signing" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -NotAfter (Get-Date).AddYears(5)

# 証明書のエクスポート
$pwd = ConvertTo-SecureString -String "password" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath ".\CodeSigning.pfx" -Password $pwd

# アプリケーションへの署名
signtool sign /f ".\CodeSigning.pfx" /p "password" /t http://timestamp.digicert.com ".\bin\Release\EnterpriseApp.exe"

# 商用証明書での署名（本番環境）
signtool sign /n "Your Company" /t http://timestamp.digicert.com /fd sha256 ".\bin\Release\EnterpriseApp.exe"
```

## 5. 設定とデータの管理

### ユーザー設定の保存場所
```csharp
public static class AppDataManager
{
    // アプリケーションデータのパス
    public static string AppDataPath => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
        "YourCompany",
        "EnterpriseApp");
    
    // ローカルデータのパス（ローミングしない）
    public static string LocalDataPath => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "YourCompany",
        "EnterpriseApp");
    
    // 共有データのパス（全ユーザー共通）
    public static string CommonDataPath => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),
        "YourCompany",
        "EnterpriseApp");
    
    public static void EnsureDirectoriesExist()
    {
        Directory.CreateDirectory(AppDataPath);
        Directory.CreateDirectory(LocalDataPath);
        Directory.CreateDirectory(Path.Combine(LocalDataPath, "Cache"));
        Directory.CreateDirectory(Path.Combine(LocalDataPath, "Logs"));
        
        // 共有データフォルダは管理者権限が必要な場合がある
        try
        {
            Directory.CreateDirectory(CommonDataPath);
        }
        catch (UnauthorizedAccessException)
        {
            // インストーラーで作成する
        }
    }
}
```

### 設定ファイルの暗号化
```csharp
public class SecureSettingsManager
{
    private readonly string _settingsPath;
    
    public SecureSettingsManager()
    {
        _settingsPath = Path.Combine(AppDataManager.AppDataPath, "settings.encrypted");
    }
    
    public void SaveSettings(UserSettings settings)
    {
        var json = JsonConvert.SerializeObject(settings);
        var encrypted = ProtectedData.Protect(
            Encoding.UTF8.GetBytes(json),
            null,
            DataProtectionScope.CurrentUser);
        
        File.WriteAllBytes(_settingsPath, encrypted);
    }
    
    public UserSettings LoadSettings()
    {
        if (!File.Exists(_settingsPath))
            return new UserSettings();
        
        try
        {
            var encrypted = File.ReadAllBytes(_settingsPath);
            var decrypted = ProtectedData.Unprotect(
                encrypted,
                null,
                DataProtectionScope.CurrentUser);
            
            var json = Encoding.UTF8.GetString(decrypted);
            return JsonConvert.DeserializeObject<UserSettings>(json);
        }
        catch
        {
            return new UserSettings();
        }
    }
}
```

## 6. トラブルシューティングとサポート

### クラッシュダンプ収集
```csharp
public class CrashReporter
{
    public static void SetupCrashHandling()
    {
        AppDomain.CurrentDomain.UnhandledException += OnUnhandledException;
        Application.ThreadException += OnThreadException;
        Application.SetUnhandledExceptionMode(UnhandledExceptionMode.CatchException);
    }
    
    private static void OnUnhandledException(object sender, UnhandledExceptionEventArgs e)
    {
        var exception = e.ExceptionObject as Exception;
        CreateCrashReport(exception, e.IsTerminating);
    }
    
    private static void CreateCrashReport(Exception exception, bool isTerminating)
    {
        var crashDir = Path.Combine(AppDataManager.LocalDataPath, "CrashReports");
        Directory.CreateDirectory(crashDir);
        
        var fileName = $"Crash_{DateTime.Now:yyyyMMdd_HHmmss}.txt";
        var filePath = Path.Combine(crashDir, fileName);
        
        var report = new StringBuilder();
        report.AppendLine("=== クラッシュレポート ===");
        report.AppendLine($"発生日時: {DateTime.Now:yyyy/MM/dd HH:mm:ss}");
        report.AppendLine($"アプリケーションバージョン: {Application.ProductVersion}");
        report.AppendLine($"OS: {Environment.OSVersion}");
        report.AppendLine($".NET Framework: {Environment.Version}");
        report.AppendLine($"64ビットOS: {Environment.Is64BitOperatingSystem}");
        report.AppendLine($"64ビットプロセス: {Environment.Is64BitProcess}");
        report.AppendLine();
        report.AppendLine("=== 例外情報 ===");
        report.AppendLine(exception?.ToString() ?? "不明なエラー");
        
        File.WriteAllText(filePath, report.ToString());
        
        if (isTerminating)
        {
            MessageBox.Show(
                "予期しないエラーが発生しました。\n" +
                $"クラッシュレポートが保存されました:\n{filePath}",
                "エラー",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error);
        }
    }
}
```

### サポート情報収集ツール
```csharp
public class SupportInfoCollector
{
    public static string CollectSystemInfo()
    {
        var info = new StringBuilder();
        
        // システム情報
        info.AppendLine("=== システム情報 ===");
        info.AppendLine($"コンピューター名: {Environment.MachineName}");
        info.AppendLine($"ユーザー名: {Environment.UserName}");
        info.AppendLine($"OS: {GetWindowsVersion()}");
        info.AppendLine($"メモリ: {GetTotalMemory()} GB");
        info.AppendLine($"プロセッサ: {Environment.ProcessorCount} コア");
        
        // アプリケーション情報
        info.AppendLine("\n=== アプリケーション情報 ===");
        info.AppendLine($"バージョン: {Application.ProductVersion}");
        info.AppendLine($"インストールパス: {Application.StartupPath}");
        info.AppendLine($"設定フォルダ: {AppDataManager.AppDataPath}");
        
        // .NET Framework情報
        info.AppendLine("\n=== .NET Framework ===");
        info.AppendLine($"バージョン: {Environment.Version}");
        info.AppendLine($"インストール済み: {Get45PlusFromRegistry()}");
        
        return info.ToString();
    }
    
    private static string GetWindowsVersion()
    {
        var reg = Registry.LocalMachine.OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion");
        var productName = reg?.GetValue("ProductName")?.ToString() ?? "Unknown";
        var releaseId = reg?.GetValue("ReleaseId")?.ToString() ?? "";
        var build = reg?.GetValue("CurrentBuild")?.ToString() ?? "";
        
        return $"{productName} ({releaseId}) Build {build}";
    }
}
```

## 7. 配布チェックリスト

### リリース前チェック項目
- [ ] コード署名証明書の適用
- [ ] アセンブリバージョンの更新
- [ ] リリースビルドの作成
- [ ] 依存関係の確認
- [ ] ウイルススキャンの実施
- [ ] インストーラーのテスト
- [ ] アンインストールのテスト
- [ ] 更新機能のテスト
- [ ] 各Windows バージョンでの動作確認
- [ ] 高DPI環境でのテスト

このガイドに従うことで、Windows Formsデスクトップアプリケーションを安全かつ効率的に配布できます。