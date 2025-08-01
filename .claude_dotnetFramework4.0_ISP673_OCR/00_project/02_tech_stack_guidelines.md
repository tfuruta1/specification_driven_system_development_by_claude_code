# 🔧 .NET Framework 4.0 技術スタックガイドライン

**Windows XP/2003対応・レガシー統合特化技術選定**

## 🎯 技術スタック概要

### コア技術スタック
```
.NET Framework: 4.0 (2010年4月リリース)
C# バージョン: 4.0
UI フレームワーク: Windows Forms
アーキテクチャ: MVP (Model-View-Presenter)
DI コンテナ: Unity Container 2.1
ORM: Entity Framework 4.0 / ADO.NET
テスト: NUnit 2.6 / MSTest
ログ: log4net 1.2.15
```

### 対応環境
```
プライマリターゲット:
- Windows XP SP3 (x86/x64)
- Windows Server 2003 R2 (x86/x64)

推奨環境:
- Windows 7 SP1 (x86/x64)
- Windows Server 2008 R2 (x64)
- Windows 8/8.1
- Windows Server 2012/2012 R2

不サポート:
- Windows 2000
- Windows Vista RTM (なし)
```

## 🚫 .NET Framework 4.0 制約事項

### 使用不可機能 (.NET 4.5以降で導入)

#### 1. 非同期プログラミング
```csharp
// ❌ 使用不可: async/await (:NET 4.5で導入)
public async Task<string> GetDataAsync()
{
    return await httpClient.GetStringAsync(url);
}

// ✅ .NET 4.0 代替手段: BackgroundWorker
public void GetDataAsync(Action<string> onComplete, Action<Exception> onError)
{
    var worker = new BackgroundWorker();
    worker.DoWork += (s, e) =>
    {
        try
        {
            var client = new WebClient();
            e.Result = client.DownloadString(url);
        }
        catch (Exception ex)
        {
            e.Result = ex;
        }
    };
    worker.RunWorkerCompleted += (s, e) =>
    {
        if (e.Result is Exception)
            onError((Exception)e.Result);
        else
            onComplete((string)e.Result);
    };
    worker.RunWorkerAsync();
}
```

#### 2. HTTP通信
```csharp
// ❌ 使用不可: HttpClient (.NET 4.5で導入)
var httpClient = new HttpClient();
var response = await httpClient.GetAsync(url);

// ✅ .NET 4.0 代替手段: WebClient
var webClient = new WebClient();
webClient.Headers.Add("Content-Type", "application/json");
var response = webClient.DownloadString(url);

// ✅ .NET 4.0 代替手段: HttpWebRequest (より細かい制御が必要な場合)
var request = (HttpWebRequest)WebRequest.Create(url);
request.Method = "GET";
var response = (HttpWebResponse)request.GetResponse();
```

#### 3. コンパイラー情報取得
```csharp
// ❌ 使用不可: CallerMemberName 属性 (.NET 4.5で導入)
public void LogError(string message, [CallerMemberName] string memberName = "")
{
    Console.WriteLine($"Error in {memberName}: {message}");
}

// ✅ .NET 4.0 代替手段: 手動指定
public void LogError(string message, string memberName)
{
    Console.WriteLine(string.Format("Error in {0}: {1}", memberName, message));
}

// ✅ .NET 4.0 代替手段: StackTrace 使用
public void LogError(string message)
{
    var frame = new StackFrame(1);
    var method = frame.GetMethod();
    Console.WriteLine(string.Format("Error in {0}: {1}", method.Name, message));
}
```

#### 4. タスク並列ライブラリ (TPL) 制限
```csharp
// ❌ 使用不可: Task.Run (.NET 4.5で導入)
var task = Task.Run(() => DoWork());

// ✅ .NET 4.0 代替手段: ThreadPool
ThreadPool.QueueUserWorkItem(_ => DoWork());

// ✅ .NET 4.0 代替手段: Task.Factory (.NET 4.0で利用可能)
var task = Task.Factory.StartNew(() => DoWork());
```

### 利用可能な.NET 4.0機能

#### 1. C# 4.0 言語機能
```csharp
// ✅ 動的型 (dynamic)
dynamic obj = GetDynamicObject();
obj.PropertyName = "value";

// ✅ オプションパラメータ
public void Method(string required, string optional = "default")
{
    // 実装
}

// ✅ 名前付き引数
Method(required: "value1", optional: "value2");

// ✅ 共変性・反変性 (in/out)
public interface IRepository<out T> // 共変性
{
    T Get();
}
```

#### 2. LINQ (完全サポート)
```csharp
// ✅ LINQ to Objects
var result = customers
    .Where(c => c.Age > 18)
    .Select(c => new { c.Name, c.Email })
    .OrderBy(c => c.Name)
    .ToList();

// ✅ LINQ to SQL / LINQ to Entities
var customers = from c in context.Customers
                where c.City == "Tokyo"
                select c;
```

## 📚 NuGet パッケージ構成

### packages.config (.NET 4.0対応バージョン)
```xml
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <!-- DI コンテナ -->
  <package id="Unity" version="2.1.505.0" targetFramework="net40" />
  
  <!-- ORM -->
  <package id="EntityFramework" version="4.3.1" targetFramework="net40" />
  
  <!-- テスト -->
  <package id="NUnit" version="2.6.4" targetFramework="net40" />
  <package id="NUnit.Runners" version="2.6.4" targetFramework="net40" />
  
  <!-- ログ -->
  <package id="log4net" version="1.2.15" targetFramework="net40" />
  
  <!-- JSON 処理 -->
  <package id="Newtonsoft.Json" version="4.5.11" targetFramework="net40" />
  
  <!-- 設定管理 -->
  <package id="System.Configuration.ConfigurationManager" version="4.0.0" targetFramework="net40" />
  
  <!-- COM 統合支援 -->
  <package id="System.Runtime.InteropServices" version="4.0.0" targetFramework="net40" />
</packages>
```

### パッケージ選定理由

#### Unity Container 2.1
```
✅ .NET Framework 4.0 完全サポート
✅ 軽量・高速なDIコンテナ
✅ Microsoft公式ライブラリ
✅ 長期サポート実績
❌ Castle Windsor, Autofacは.NET 4.0サポート終了
```

#### Entity Framework 4.0
```
✅ .NET Framework 4.0ネイティブサポート
✅ Code First, Database First 両方対応
✅ LINQ to Entities サポート
❌ Entity Framework 6.xは.NET 4.5以降が必要
❌ Dapperは.NET 3.5サポート終了
```

#### NUnit 2.6
```
✅ .NET Framework 2.0-4.0 サポート
✅ Visual Studio統合
✅ 豊富な断言メソッド
❌ NUnit 3.xは.NET 4.5以降推奨
❌ xUnitは.NET 4.0サポート終了
```

## 💡 ベストプラクティス

### 1. 非同期処理パターン

#### BackgroundWorker パターン
```csharp
// .NET 4.0 推奨パターン
public class AsyncOperationHelper
{
    public static void ExecuteAsync<T>(
        Func<T> operation,
        Action<T> onSuccess,
        Action<Exception> onError = null,
        Action<int> onProgress = null)
    {
        var worker = new BackgroundWorker();
        worker.WorkerReportsProgress = onProgress != null;
        
        worker.DoWork += (s, e) =>
        {
            try
            {
                var result = operation();
                e.Result = result;
            }
            catch (Exception ex)
            {
                e.Result = ex;
            }
        };
        
        worker.ProgressChanged += (s, e) =>
        {
            onProgress?.Invoke(e.ProgressPercentage);
        };
        
        worker.RunWorkerCompleted += (s, e) =>
        {
            if (e.Result is Exception)
            {
                onError?.Invoke(e.Result as Exception);
            }
            else
            {
                onSuccess((T)e.Result);
            }
        };
        
        worker.RunWorkerAsync();
    }
}
```

### 2. メモリ管理パターン

#### IDisposable パターン徹底
```csharp
// .NET 4.0 メモリ管理ベストプラクティス
public class ResourceManager : IDisposable
{
    private readonly List<IDisposable> _disposables;
    private bool _disposed = false;
    
    public ResourceManager()
    {
        _disposables = new List<IDisposable>();
    }
    
    public T RegisterDisposable<T>(T resource) where T : IDisposable
    {
        if (resource != null)
        {
            _disposables.Add(resource);
        }
        return resource;
    }
    
    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                foreach (var disposable in _disposables)
                {
                    try
                    {
                        disposable?.Dispose();
                    }
                    catch (Exception ex)
                    {
                        // ログ出力のみ、例外は再スローしない
                        LogManager.GetLogger(GetType()).Error(
                            "Error disposing resource", ex);
                    }
                }
                _disposables.Clear();
            }
            _disposed = true;
        }
    }
    
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
}
```

### 3. スレッドセーフティパターン

#### UIスレッド安全な操作
```csharp
public static class ControlExtensions
{
    public static void InvokeIfRequired(this Control control, Action action)
    {
        if (control.InvokeRequired)
        {
            control.Invoke(action);
        }
        else
        {
            action();
        }
    }
    
    public static T InvokeIfRequired<T>(this Control control, Func<T> func)
    {
        if (control.InvokeRequired)
        {
            return (T)control.Invoke(func);
        }
        else
        {
            return func();
        }
    }
}

// 使用例
label1.InvokeIfRequired(() => label1.Text = "Updated from background thread");
```

## 📎 コーディング標準

### 1. 命名規約
```csharp
// クラス名: PascalCase
public class CustomerService { }

// メソッド名: PascalCase
public void GetCustomerById(int id) { }

// フィールド: _camelCase (プライベート)
private readonly ICustomerRepository _customerRepository;

// プロパティ: PascalCase
public string CustomerName { get; set; }

// ローカル変数: camelCase
var customerList = new List<Customer>();

// 定数: PascalCase
public const int MaxRetryCount = 3;
```

### 2. エラーハンドリングパターン
```csharp
// .NET 4.0 推奨エラーハンドリング
public class OperationResult<T>
{
    public bool IsSuccess { get; private set; }
    public T Data { get; private set; }
    public string ErrorMessage { get; private set; }
    public Exception Exception { get; private set; }
    
    public static OperationResult<T> Success(T data)
    {
        return new OperationResult<T>
        {
            IsSuccess = true,
            Data = data
        };
    }
    
    public static OperationResult<T> Failure(string errorMessage, Exception exception = null)
    {
        return new OperationResult<T>
        {
            IsSuccess = false,
            ErrorMessage = errorMessage,
            Exception = exception
        };
    }
}

// 使用例
public OperationResult<Customer> GetCustomer(int id)
{
    try
    {
        var customer = _repository.GetById(id);
        return OperationResult<Customer>.Success(customer);
    }
    catch (Exception ex)
    {
        _logger.Error("Failed to get customer", ex);
        return OperationResult<Customer>.Failure(
            "Customer not found", ex);
    }
}
```

## 🛠️ 開発ツール推奨

### 1. Visual Studio バージョン
```
✅ Visual Studio 2010 Professional/Premium/Ultimate
✅ Visual Studio 2012 Professional/Premium/Ultimate  
✅ Visual Studio 2013 Professional/Premium/Ultimate
✅ Visual Studio 2015 Community/Professional/Enterprise
✅ Visual Studio 2017 Community/Professional/Enterprise
✅ Visual Studio 2019 Community/Professional/Enterprise
✅ Visual Studio 2022 Community/Professional/Enterprise

❌ Visual Studio Express (NUnit統合制限)
❌ Visual Studio Code (フル.NET Frameworkサポート制限)
```

### 2. サードパーティツール
```
✅ ReSharper (JetBrains) - コード品質・リファクタリング
✅ NCrunch - 継続的テスト実行
✅ dotTrace - パフォーマンスプロファイラ
✅ NDepend - コード品質メトリクス
✅ Telerik JustDecompile - リバースエンジニアリング
```

### 3. バージョン管理
```
✅ Git (GitHub, GitLab, Azure DevOps)
✅ Subversion (SVN)
✅ Team Foundation Server (TFS)
❌ Mercurial (サポート終了済み)
```

## 📦 デプロイメント戦略

### 1. デプロイ方式選択

#### ClickOnce デプロイメント (推奨)
```
✅ 自動更新機能
✅ ユーザー権限でインストール可能
✅ .NET Framework 4.0 ネイティブサポート
✅ オフライン実行対応
❌ レジストリアクセス制限
❌ COMコンポーネント登録不可
```

#### MSI インストーラー
```
✅ フルシステムアクセス可能
✅ COMコンポーネント登録可能
✅ グループポリシー連携
✅ サイレントインストール対応
❌ 管理者権限必要
❌ 更新手動対応
```

#### XCopy デプロイメント
```
✅ 最もシンプル
✅ ネットワーク共有フォルダから実行可能
✅ ポータブルアプリケーション対応
❌ 依存関係手動管理
❌ アンインストール手動対応
```

### 2. 配置管理

#### app.config 設定例
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <configSections>
    <section name="log4net" type="log4net.Config.Log4NetConfigurationSectionHandler, log4net" />
    <section name="unity" type="Microsoft.Practices.Unity.Configuration.UnityConfigurationSection, Microsoft.Practices.Unity.Configuration" />
  </configSections>
  
  <!-- .NET Framework 4.0 ランタイム設定 -->
  <startup>
    <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.0" />
  </startup>
  
  <!-- 接続文字列 -->
  <connectionStrings>
    <add name="DefaultConnection" 
         connectionString="Data Source=.\SQLEXPRESS;Initial Catalog=BusinessDB;Integrated Security=True" 
         providerName="System.Data.SqlClient" />
    <add name="LegacyConnection" 
         connectionString="Data Source=LEGACY-SERVER;Initial Catalog=LegacyDB;User ID=sa;Password=password" 
         providerName="System.Data.SqlClient" />
  </connectionStrings>
  
  <!-- アプリケーション設定 -->
  <appSettings>
    <add key="WindowsXPCompatibilityMode" value="true" />
    <add key="MaxRetryCount" value="3" />
    <add key="DefaultTimeout" value="30000" />
    <add key="EnableLegacySupport" value="true" />
    <add key="ComComponentPath" value="C:\Program Files\LegacyComponents" />
  </appSettings>
  
  <!-- Unity DI 設定 -->
  <unity xmlns="http://schemas.microsoft.com/practices/2010/unity">
    <container>
      <register type="ICustomerService" mapTo="CustomerService" />
      <register type="ICustomerRepository" mapTo="CustomerRepository" />
    </container>
  </unity>
  
  <!-- log4net 設定 -->
  <log4net>
    <appender name="FileAppender" type="log4net.Appender.FileAppender">
      <file value="logs\application.log" />
      <appendToFile value="true" />
      <layout type="log4net.Layout.PatternLayout">
        <conversionPattern value="%date [%thread] %-5level %logger - %message%newline" />
      </layout>
    </appender>
    <root>
      <level value="INFO" />
      <appender-ref ref="FileAppender" />
    </root>
  </log4net>
  
</configuration>
```

---

**💡 技術選定のポイント**: .NET Framework 4.0の制約下でも、正しいアーキテクチャパターンとベストプラクティスを適用することで、保守性が高くモダンなコードを書くことが可能です。重要なのは、新技術の代替手段を理解し、一貫したパターンで実装することです。