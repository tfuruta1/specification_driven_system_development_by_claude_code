# .NET Framework ファイル構造ガイド - 拡張子と設定ファイル詳解

## 1. ソリューションファイル (.sln)

### 概要
Visual Studioソリューションファイルは、複数のプロジェクトを統合管理するためのコンテナファイルです。

### 基本構造
```text
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "EnterpriseApp.Core", "Core\EnterpriseApp.Core.csproj", "{12345678-1234-1234-1234-123456789012}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "EnterpriseApp.Infrastructure", "Infrastructure\EnterpriseApp.Infrastructure.csproj", "{87654321-4321-4321-4321-210987654321}"
EndProject
Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "Solution Items", "Solution Items", "{ABCDEF01-2345-6789-ABCD-EF0123456789}"
    ProjectSection(SolutionItems) = preProject
        .editorconfig = .editorconfig
        README.md = README.md
    EndProjectSection
EndProject
Global
    GlobalSection(SolutionConfigurationPlatforms) = preSolution
        Debug|Any CPU = Debug|Any CPU
        Release|Any CPU = Release|Any CPU
    EndGlobalSection
    GlobalSection(ProjectConfigurationPlatforms) = postSolution
        {12345678-1234-1234-1234-123456789012}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {12345678-1234-1234-1234-123456789012}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {12345678-1234-1234-1234-123456789012}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {12345678-1234-1234-1234-123456789012}.Release|Any CPU.Build.0 = Release|Any CPU
    EndGlobalSection
EndGlobal
```

### 便利な使い方
```powershell
# コマンドラインからソリューションをビルド
msbuild YourSolution.sln /p:Configuration=Release

# 特定のプロジェクトのみビルド
msbuild YourSolution.sln /t:EnterpriseApp.Core

# ソリューション内のNuGetパッケージを復元
nuget restore YourSolution.sln

# dotnet CLIを使用（.NET Core/5+互換プロジェクトの場合）
dotnet build YourSolution.sln
dotnet test YourSolution.sln
```

### プログラムによる操作
```csharp
using Microsoft.Build.Construction;

public class SolutionManager
{
    public void CreateSolution(string solutionPath)
    {
        var solution = SolutionFile.Create();
        
        // プロジェクトを追加
        var projectGuid = Guid.NewGuid();
        solution.ProjectsInOrder.Add(new ProjectInSolution
        {
            ProjectName = "EnterpriseApp.Core",
            RelativePath = @"Core\EnterpriseApp.Core.csproj",
            ProjectGuid = projectGuid.ToString("B"),
            ProjectType = SolutionProjectType.KnownToBeMSBuildFormat
        });
        
        // ソリューション構成を追加
        solution.SolutionConfigurations.Add(new SolutionConfiguration
        {
            ConfigurationName = "Debug",
            PlatformName = "Any CPU"
        });
        
        solution.Save(solutionPath);
    }
}
```

## 2. プロジェクトファイル (.csproj)

### 従来形式（.NET Framework）
```xml
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="15.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Import Project="$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props" Condition="Exists('$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props')" />
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <Platform Condition=" '$(Platform)' == '' ">AnyCPU</Platform>
    <ProjectGuid>{12345678-1234-1234-1234-123456789012}</ProjectGuid>
    <OutputType>WinExe</OutputType>
    <RootNamespace>EnterpriseApp</RootNamespace>
    <AssemblyName>EnterpriseApp</AssemblyName>
    <TargetFrameworkVersion>v4.8</TargetFrameworkVersion>
    <FileAlignment>512</FileAlignment>
    <AutoGenerateBindingRedirects>true</AutoGenerateBindingRedirects>
    <Deterministic>true</Deterministic>
  </PropertyGroup>
  
  <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Debug|AnyCPU' ">
    <DebugSymbols>true</DebugSymbols>
    <DebugType>full</DebugType>
    <Optimize>false</Optimize>
    <OutputPath>bin\Debug\</OutputPath>
    <DefineConstants>DEBUG;TRACE</DefineConstants>
    <ErrorReport>prompt</ErrorReport>
    <WarningLevel>4</WarningLevel>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <CodeAnalysisRuleSet>MinimumRecommendedRules.ruleset</CodeAnalysisRuleSet>
  </PropertyGroup>
  
  <ItemGroup>
    <Reference Include="System" />
    <Reference Include="System.Core" />
    <Reference Include="System.Configuration" />
    <Reference Include="System.Data" />
    <Reference Include="System.Drawing" />
    <Reference Include="System.Windows.Forms" />
    <Reference Include="System.Xml" />
  </ItemGroup>
  
  <ItemGroup>
    <Compile Include="Program.cs" />
    <Compile Include="Properties\AssemblyInfo.cs" />
    <EmbeddedResource Include="Properties\Resources.resx">
      <Generator>ResXFileCodeGenerator</Generator>
      <LastGenOutput>Resources.Designer.cs</LastGenOutput>
      <SubType>Designer</SubType>
    </EmbeddedResource>
  </ItemGroup>
  
  <ItemGroup>
    <None Include="App.config" />
    <None Include="packages.config" />
  </ItemGroup>
  
  <Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" />
  
  <!-- ビルドイベント -->
  <PropertyGroup>
    <PostBuildEvent>
      xcopy "$(ProjectDir)Resources\*.*" "$(TargetDir)Resources\" /Y /E
    </PostBuildEvent>
  </PropertyGroup>
</Project>
```

### SDK形式（.NET Core/5+互換）
```xml
<Project Sdk="Microsoft.NET.Sdk.WindowsDesktop">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net48</TargetFramework>
    <UseWindowsForms>true</UseWindowsForms>
    <LangVersion>7.3</LangVersion>
    <Nullable>enable</Nullable>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>

  <PropertyGroup Condition="'$(Configuration)'=='Release'">
    <DebugType>pdbonly</DebugType>
    <Optimize>true</Optimize>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="EntityFramework" Version="6.4.4" />
    <PackageReference Include="Unity.Container" Version="5.11.11" />
    <PackageReference Include="NLog" Version="4.7.15" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\Core\EnterpriseApp.Core.csproj" />
  </ItemGroup>

  <!-- カスタムビルドタスク -->
  <Target Name="CopyCustomFiles" AfterTargets="Build">
    <Copy SourceFiles="@(CustomFiles)" DestinationFolder="$(OutputPath)" />
  </Target>
</Project>
```

### 高度な使用例
```xml
<!-- 条件付きコンパイル -->
<PropertyGroup Condition="'$(Configuration)'=='Debug'">
  <DefineConstants>$(DefineConstants);DETAILED_LOGGING;MOCK_SERVICES</DefineConstants>
</PropertyGroup>

<!-- アセンブリ情報の自動生成 -->
<PropertyGroup>
  <AssemblyVersion>1.0.0.0</AssemblyVersion>
  <FileVersion>1.0.0.$([System.DateTime]::Now.ToString("yy"))$([System.DateTime]::Now.DayOfYear.ToString("000"))</FileVersion>
  <InformationalVersion>1.0.0-$(GitCommitHash)</InformationalVersion>
</PropertyGroup>

<!-- ビルド時のファイルコピー -->
<ItemGroup>
  <Content Include="Resources\**\*.*">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </Content>
</ItemGroup>

<!-- プラットフォーム固有の参照 -->
<ItemGroup Condition="'$(Platform)'=='x64'">
  <Reference Include="Oracle.DataAccess, Version=4.122.19.1, Culture=neutral, PublicKeyToken=89b483f429c47342, processorArchitecture=AMD64" />
</ItemGroup>
```

## 3. パッケージ管理ファイル

### packages.config（従来形式）
```xml
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="EntityFramework" version="6.4.4" targetFramework="net48" />
  <package id="EntityFramework.ja" version="6.4.4" targetFramework="net48" />
  <package id="Unity" version="5.11.10" targetFramework="net48" />
  <package id="Unity.Container" version="5.11.11" targetFramework="net48" />
  <package id="NLog" version="4.7.15" targetFramework="net48" />
  <package id="NLog.Config" version="4.7.15" targetFramework="net48" />
  <package id="Newtonsoft.Json" version="13.0.1" targetFramework="net48" />
</packages>
```

### PackageReference形式への移行
```powershell
# Visual Studioのパッケージマネージャーコンソールで実行
# packages.configからPackageReferenceへの移行
Migrate-PackagesConfig
```

### NuGet.Config（ソリューションレベル）
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="CompanyNuGet" value="https://nuget.company.com/v3/index.json" />
  </packageSources>
  
  <packageSourceCredentials>
    <CompanyNuGet>
      <add key="Username" value="%NUGET_USER%" />
      <add key="ClearTextPassword" value="%NUGET_PASSWORD%" />
    </CompanyNuGet>
  </packageSourceCredentials>
  
  <config>
    <add key="defaultPushSource" value="https://nuget.company.com/v3/index.json" />
  </config>
  
  <packageRestore>
    <add key="enabled" value="True" />
    <add key="automatic" value="True" />
  </packageRestore>
</configuration>
```

## 4. 設定ファイル

### App.config（アプリケーション構成）
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <configSections>
    <section name="entityFramework" type="System.Data.Entity.Internal.ConfigFile.EntityFrameworkSection, EntityFramework, Version=6.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089" requirePermission="false" />
    <section name="unity" type="Microsoft.Practices.Unity.Configuration.UnityConfigurationSection, Unity.Configuration" />
    <section name="nlog" type="NLog.Config.ConfigSectionHandler, NLog" />
  </configSections>
  
  <startup>
    <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.8" />
  </startup>
  
  <connectionStrings>
    <add name="DefaultConnection" 
         connectionString="Data Source=.\SQLEXPRESS;Initial Catalog=EnterpriseDB;Integrated Security=True;MultipleActiveResultSets=True;Application Name=EnterpriseApp"
         providerName="System.Data.SqlClient" />
    <add name="LegacySystem" 
         connectionString="Server=legacy-server;Database=LegacyDB;User Id=app_user;Password={encrypted_password};"
         providerName="System.Data.SqlClient" />
  </connectionStrings>
  
  <appSettings>
    <!-- 基本設定 -->
    <add key="ApplicationName" value="エンタープライズ統合管理システム" />
    <add key="Version" value="1.0.0" />
    <add key="Environment" value="Development" />
    
    <!-- 機能フラグ -->
    <add key="Feature:EnableAdvancedSearch" value="true" />
    <add key="Feature:EnableBatchProcessing" value="true" />
    <add key="Feature:EnableLegacyIntegration" value="false" />
    
    <!-- パフォーマンス設定 -->
    <add key="MaxConcurrentRequests" value="100" />
    <add key="CommandTimeout" value="300" />
    <add key="CacheExpirationMinutes" value="20" />
    
    <!-- ファイルパス -->
    <add key="LogPath" value="C:\Logs\EnterpriseApp\" />
    <add key="TempPath" value="C:\Temp\EnterpriseApp\" />
    <add key="ReportTemplatePath" value=".\Templates\Reports\" />
  </appSettings>
  
  <system.data>
    <DbProviderFactories>
      <remove invariant="Oracle.ManagedDataAccess.Client" />
      <add name="ODP.NET, Managed Driver" invariant="Oracle.ManagedDataAccess.Client" 
           description="Oracle Data Provider for .NET, Managed Driver" 
           type="Oracle.ManagedDataAccess.Client.OracleClientFactory, Oracle.ManagedDataAccess, Version=4.122.19.1, Culture=neutral, PublicKeyToken=89b483f429c47342" />
    </DbProviderFactories>
  </system.data>
  
  <runtime>
    <assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1">
      <dependentAssembly>
        <assemblyIdentity name="Newtonsoft.Json" publicKeyToken="30ad4fe6b2a6aeed" culture="neutral" />
        <bindingRedirect oldVersion="0.0.0.0-13.0.0.0" newVersion="13.0.0.0" />
      </dependentAssembly>
      <dependentAssembly>
        <assemblyIdentity name="System.Runtime.CompilerServices.Unsafe" publicKeyToken="b03f5f7f11d50a3a" culture="neutral" />
        <bindingRedirect oldVersion="0.0.0.0-6.0.0.0" newVersion="6.0.0.0" />
      </dependentAssembly>
    </assemblyBinding>
    
    <!-- ガベージコレクション最適化 -->
    <gcServer enabled="true" />
    <gcConcurrent enabled="true" />
  </runtime>
  
  <system.net>
    <defaultProxy enabled="true" useDefaultCredentials="true">
      <proxy proxyaddress="http://proxy.company.com:8080" bypassonlocal="true" />
      <bypasslist>
        <add address="*.company.local" />
        <add address="192.168.*" />
      </bypasslist>
    </defaultProxy>
    
    <connectionManagement>
      <add address="*" maxconnection="100" />
    </connectionManagement>
  </system.net>
</configuration>
```

### appsettings.json（モダンな設定管理）
```json
{
  "ApplicationSettings": {
    "Name": "エンタープライズ統合管理システム",
    "Version": "1.0.0",
    "Environment": "Development"
  },
  
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=.\\SQLEXPRESS;Initial Catalog=EnterpriseDB;Integrated Security=True",
    "LegacySystem": "Server=legacy-server;Database=LegacyDB;User Id=app_user;Password={vault:legacy_db_password};"
  },
  
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "EnterpriseApp": "Debug"
    },
    "NLog": {
      "IncludeScopes": true,
      "RemoveLoggerFactoryFilter": true
    }
  },
  
  "Features": {
    "EnableAdvancedSearch": true,
    "EnableBatchProcessing": true,
    "EnableLegacyIntegration": false,
    "ExperimentalFeatures": {
      "EnableAIAssistant": false,
      "EnablePredictiveAnalytics": false
    }
  },
  
  "Security": {
    "Authentication": {
      "Type": "Windows",
      "EnableMultiFactor": true,
      "SessionTimeout": 30
    },
    "Encryption": {
      "Algorithm": "AES256",
      "KeyRotationDays": 90
    }
  },
  
  "Performance": {
    "MaxConcurrentRequests": 100,
    "CommandTimeout": 300,
    "CacheSettings": {
      "DefaultExpirationMinutes": 20,
      "MaxMemoryMB": 512
    }
  },
  
  "ExternalServices": {
    "LegacyAPI": {
      "BaseUrl": "https://legacy.company.com/api",
      "Timeout": 60,
      "RetryCount": 3
    },
    "DocumentService": {
      "BaseUrl": "https://docs.company.com",
      "ApiKey": "{vault:document_service_key}"
    }
  }
}
```

### 設定ファイルの読み込みヘルパー
```csharp
// App.config の読み込み
public static class ConfigurationHelper
{
    public static string GetAppSetting(string key, string defaultValue = null)
    {
        return ConfigurationManager.AppSettings[key] ?? defaultValue;
    }
    
    public static T GetAppSetting<T>(string key, T defaultValue = default)
    {
        var value = ConfigurationManager.AppSettings[key];
        if (string.IsNullOrEmpty(value))
            return defaultValue;
        
        return (T)Convert.ChangeType(value, typeof(T));
    }
    
    public static bool IsFeatureEnabled(string featureName)
    {
        return GetAppSetting($"Feature:{featureName}", false);
    }
}

// appsettings.json の読み込み（.NET Framework でも使用可能）
public class JsonConfigurationService
{
    private readonly JObject _configuration;
    
    public JsonConfigurationService(string configPath = "appsettings.json")
    {
        var json = File.ReadAllText(configPath);
        _configuration = JObject.Parse(json);
        
        // 環境別設定のマージ
        var environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Production";
        var envConfigPath = $"appsettings.{environment}.json";
        if (File.Exists(envConfigPath))
        {
            var envJson = File.ReadAllText(envConfigPath);
            var envConfig = JObject.Parse(envJson);
            _configuration.Merge(envConfig);
        }
    }
    
    public T GetValue<T>(string path)
    {
        return _configuration.SelectToken(path).ToObject<T>();
    }
    
    public string GetConnectionString(string name)
    {
        return GetValue<string>($"ConnectionStrings:{name}");
    }
}
```

## 5. Program.cs（エントリーポイント）

### 基本的なProgram.cs
```csharp
using System;
using System.Windows.Forms;
using System.Threading;
using System.Runtime.InteropServices;
using Unity;
using NLog;

namespace EnterpriseApp
{
    static class Program
    {
        private static readonly Logger Logger = LogManager.GetCurrentClassLogger();
        private static Mutex _mutex;
        
        /// <summary>
        /// アプリケーションのメイン エントリ ポイントです。
        /// </summary>
        [STAThread]
        static void Main()
        {
            try
            {
                // 多重起動チェック
                if (!CheckSingleInstance())
                {
                    MessageBox.Show("アプリケーションは既に起動しています。", 
                        "起動エラー", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }
                
                // グローバル例外ハンドラーの設定
                SetupGlobalExceptionHandlers();
                
                // アプリケーション設定
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);
                
                // 高DPI対応
                if (Environment.OSVersion.Version.Major >= 6)
                    SetProcessDPIAware();
                
                // ログ初期化
                Logger.Info("=== アプリケーション起動 ===");
                Logger.Info($"Version: {Application.ProductVersion}");
                Logger.Info($"Environment: {Environment.MachineName}");
                Logger.Info($"User: {Environment.UserName}");
                
                // DIコンテナ初期化
                var container = ConfigureServices();
                
                // メインフォーム起動
                using (var mainForm = container.Resolve<MainForm>())
                {
                    Application.Run(mainForm);
                }
                
                Logger.Info("=== アプリケーション終了 ===");
            }
            catch (Exception ex)
            {
                Logger.Fatal(ex, "起動時に致命的なエラーが発生しました");
                MessageBox.Show(
                    $"アプリケーションの起動に失敗しました。\n\n{ex.Message}", 
                    "起動エラー", 
                    MessageBoxButtons.OK, 
                    MessageBoxIcon.Error);
            }
            finally
            {
                _mutex?.ReleaseMutex();
                _mutex?.Dispose();
            }
        }
        
        private static bool CheckSingleInstance()
        {
            const string mutexName = "EnterpriseApp_SingleInstance_Mutex";
            bool createdNew;
            _mutex = new Mutex(true, mutexName, out createdNew);
            return createdNew;
        }
        
        private static void SetupGlobalExceptionHandlers()
        {
            // UIスレッドの未処理例外
            Application.ThreadException += (sender, e) =>
            {
                Logger.Error(e.Exception, "UIスレッドで未処理の例外が発生しました");
                ShowErrorDialog(e.Exception);
            };
            
            // 非UIスレッドの未処理例外
            AppDomain.CurrentDomain.UnhandledException += (sender, e) =>
            {
                var ex = e.ExceptionObject as Exception;
                Logger.Fatal(ex, "未処理の例外が発生しました");
                
                if (e.IsTerminating)
                {
                    MessageBox.Show(
                        "致命的なエラーが発生しました。アプリケーションを終了します。", 
                        "エラー", 
                        MessageBoxButtons.OK, 
                        MessageBoxIcon.Error);
                }
            };
        }
        
        private static IUnityContainer ConfigureServices()
        {
            var container = new UnityContainer();
            
            // 設定の登録
            container.RegisterInstance<IConfiguration>(
                new JsonConfigurationService());
            
            // ログの登録
            container.RegisterInstance<ILogger>(Logger);
            
            // リポジトリの登録
            container.RegisterType<ICustomerRepository, CustomerRepository>();
            container.RegisterType<IOrderRepository, OrderRepository>();
            
            // サービスの登録
            container.RegisterType<ICustomerService, CustomerService>();
            container.RegisterType<IAuthenticationService, WindowsAuthenticationService>();
            
            // フォームの登録
            container.RegisterType<MainForm>();
            
            return container;
        }
        
        private static void ShowErrorDialog(Exception ex)
        {
            var message = $"エラーが発生しました。\n\n" +
                         $"エラー内容: {ex.Message}\n\n" +
                         $"詳細情報はログファイルを確認してください。";
            
            MessageBox.Show(message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
        
        [DllImport("user32.dll")]
        private static extern bool SetProcessDPIAware();
    }
}
```

### 高度なProgram.cs（プラグインシステム対応）
```csharp
static class Program
{
    [STAThread]
    static void Main(string[] args)
    {
        // コマンドライン引数の解析
        var options = ParseCommandLineArgs(args);
        
        if (options.ShowHelp)
        {
            ShowHelp();
            return;
        }
        
        // 起動モードの判定
        if (options.ConsoleMode)
        {
            RunConsoleMode(options);
        }
        else
        {
            RunWindowsFormsMode(options);
        }
    }
    
    private static void RunWindowsFormsMode(CommandLineOptions options)
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        
        // スプラッシュスクリーンの表示
        using (var splash = new SplashScreen())
        {
            splash.Show();
            
            // 初期化処理
            var container = InitializeApplication(splash.UpdateProgress);
            
            splash.Close();
            
            // メインフォーム起動
            var mainForm = container.Resolve<MainForm>();
            Application.Run(mainForm);
        }
    }
    
    private static void RunConsoleMode(CommandLineOptions options)
    {
        // コンソールモードでの実行
        AllocConsole();
        
        try
        {
            var container = InitializeApplication(progress => Console.WriteLine(progress));
            var batchService = container.Resolve<IBatchService>();
            
            if (options.BatchName != null)
            {
                batchService.ExecuteBatch(options.BatchName).Wait();
            }
        }
        finally
        {
            FreeConsole();
        }
    }
    
    private static IUnityContainer InitializeApplication(Action<string> progressCallback)
    {
        progressCallback("設定を読み込んでいます...");
        var configuration = LoadConfiguration();
        
        progressCallback("データベースに接続しています...");
        TestDatabaseConnection(configuration);
        
        progressCallback("プラグインを読み込んでいます...");
        var plugins = LoadPlugins();
        
        progressCallback("サービスを初期化しています...");
        var container = ConfigureServices(configuration, plugins);
        
        progressCallback("起動準備が完了しました");
        return container;
    }
    
    private static List<IPlugin> LoadPlugins()
    {
        var plugins = new List<IPlugin>();
        var pluginPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Plugins");
        
        if (Directory.Exists(pluginPath))
        {
            foreach (var dll in Directory.GetFiles(pluginPath, "*.dll"))
            {
                try
                {
                    var assembly = Assembly.LoadFrom(dll);
                    var pluginTypes = assembly.GetTypes()
                        .Where(t => typeof(IPlugin).IsAssignableFrom(t) && !t.IsAbstract);
                    
                    foreach (var type in pluginTypes)
                    {
                        var plugin = (IPlugin)Activator.CreateInstance(type);
                        plugins.Add(plugin);
                        Logger.Info($"プラグインを読み込みました: {plugin.Name}");
                    }
                }
                catch (Exception ex)
                {
                    Logger.Error(ex, $"プラグインの読み込みに失敗しました: {dll}");
                }
            }
        }
        
        return plugins;
    }
    
    [DllImport("kernel32.dll")]
    static extern bool AllocConsole();
    
    [DllImport("kernel32.dll")]
    static extern bool FreeConsole();
}
```

## 6. その他の重要なファイル

### AssemblyInfo.cs
```csharp
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

[assembly: AssemblyTitle("EnterpriseApp")]
[assembly: AssemblyDescription("エンタープライズ統合管理システム")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Your Company")]
[assembly: AssemblyProduct("Enterprise Integration System")]
[assembly: AssemblyCopyright("Copyright © Your Company 2024")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]

[assembly: ComVisible(false)]
[assembly: Guid("12345678-1234-1234-1234-123456789012")]

[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]
[assembly: AssemblyInformationalVersion("1.0.0-release")]

// 内部クラスをテストプロジェクトに公開
[assembly: InternalsVisibleTo("EnterpriseApp.Tests")]
[assembly: InternalsVisibleTo("DynamicProxyGenAssembly2")]
```

### GlobalSuppressions.cs
```csharp
using System.Diagnostics.CodeAnalysis;

[assembly: SuppressMessage("Design", "CA1062:Validate arguments of public methods", 
    Justification = "Null checks are performed by Guard clauses")]
[assembly: SuppressMessage("Globalization", "CA1303:Do not pass literals as localized parameters", 
    Justification = "日本語専用アプリケーション")]
[assembly: SuppressMessage("Performance", "CA1819:Properties should not return arrays", 
    Justification = "DTOクラスでの使用")]
```

## 7. ビルドとデプロイメント

### Directory.Build.props（ソリューション共通設定）
```xml
<Project>
  <PropertyGroup>
    <LangVersion>7.3</LangVersion>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <CodeAnalysisRuleSet>$(MSBuildThisFileDirectory)CodeAnalysis.ruleset</CodeAnalysisRuleSet>
    <Company>Your Company</Company>
    <Product>Enterprise Integration System</Product>
    <Copyright>Copyright © Your Company 2024</Copyright>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="6.0.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
    </PackageReference>
  </ItemGroup>
</Project>
```

### .editorconfig
```ini
root = true

[*]
charset = utf-8
end_of_line = crlf
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true

[*.{cs,vb}]
# C# コーディング規約
dotnet_sort_system_directives_first = true
dotnet_separate_import_directive_groups = false

# 命名規則
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.severity = warning
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.symbols = interface_symbols
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.style = prefix_interface_with_i

[*.{json,xml,config}]
indent_size = 2
```

これらのファイルを理解し、適切に活用することで、.NET Frameworkアプリケーションの開発効率と保守性が大幅に向上します。