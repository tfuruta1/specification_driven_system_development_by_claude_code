# .NET Framework 4.0 制限事項と回避策ガイド

## 1. 言語機能の制限と代替実装

### async/await が使用できない（4.5で導入）

#### ❌ 使用できないコード（.NET 4.5以降）
```csharp
// .NET Framework 4.5以降のasync/awaitパターン
public async Task<List<Customer>> GetCustomersAsync()
{
    using (var client = new HttpClient())
    {
        var response = await client.GetAsync("api/customers");
        var json = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<List<Customer>>(json);
    }
}
```

#### ✅ .NET Framework 4.0 での代替実装

**パターン1: BackgroundWorker を使用**
```csharp
public class CustomerService
{
    private BackgroundWorker _worker;
    
    public event EventHandler<List<Customer>> CustomersLoaded;
    public event EventHandler<Exception> LoadError;
    
    public void LoadCustomersAsync()
    {
        _worker = new BackgroundWorker();
        _worker.DoWork += (sender, e) =>
        {
            // バックグラウンドスレッドで実行
            using (var client = new WebClient())
            {
                var json = client.DownloadString("api/customers");
                e.Result = JsonConvert.DeserializeObject<List<Customer>>(json);
            }
        };
        
        _worker.RunWorkerCompleted += (sender, e) =>
        {
            if (e.Error != null)
            {
                LoadError?.Invoke(this, e.Error);
            }
            else
            {
                CustomersLoaded?.Invoke(this, (List<Customer>)e.Result);
            }
        };
        
        _worker.RunWorkerAsync();
    }
}
```

**パターン2: Task と ContinueWith を使用**
```csharp
public Task<List<Customer>> GetCustomersAsync()
{
    return Task.Factory.StartNew(() =>
    {
        using (var client = new WebClient())
        {
            var json = client.DownloadString("api/customers");
            return JsonConvert.DeserializeObject<List<Customer>>(json);
        }
    });
}

// 使用例
public void LoadCustomers()
{
    GetCustomersAsync().ContinueWith(task =>
    {
        if (task.IsFaulted)
        {
            // エラー処理
            MessageBox.Show("エラー: " + task.Exception.InnerException.Message);
        }
        else
        {
            // UI更新（UIスレッドで実行）
            this.Invoke((Action)(() =>
            {
                dataGridView1.DataSource = task.Result;
            }));
        }
    });
}
```

### HttpClient が使用できない（4.5で導入）

#### ✅ WebClient を使用した実装
```csharp
public class ApiClient
{
    private readonly string _baseUrl;
    
    public ApiClient(string baseUrl)
    {
        _baseUrl = baseUrl;
    }
    
    // GET リクエスト
    public T Get<T>(string endpoint)
    {
        using (var client = new WebClient())
        {
            client.Headers.Add("Content-Type", "application/json");
            var json = client.DownloadString(_baseUrl + endpoint);
            return JsonConvert.DeserializeObject<T>(json);
        }
    }
    
    // POST リクエスト
    public TResponse Post<TRequest, TResponse>(string endpoint, TRequest data)
    {
        using (var client = new WebClient())
        {
            client.Headers.Add("Content-Type", "application/json");
            var json = JsonConvert.SerializeObject(data);
            var response = client.UploadString(_baseUrl + endpoint, "POST", json);
            return JsonConvert.DeserializeObject<TResponse>(response);
        }
    }
    
    // 非同期版
    public void GetAsync<T>(string endpoint, Action<T> onSuccess, Action<Exception> onError)
    {
        var client = new WebClient();
        client.Headers.Add("Content-Type", "application/json");
        
        client.DownloadStringCompleted += (sender, e) =>
        {
            if (e.Error != null)
            {
                onError(e.Error);
            }
            else
            {
                try
                {
                    var result = JsonConvert.DeserializeObject<T>(e.Result);
                    onSuccess(result);
                }
                catch (Exception ex)
                {
                    onError(ex);
                }
            }
            client.Dispose();
        };
        
        client.DownloadStringAsync(new Uri(_baseUrl + endpoint));
    }
}
```

#### ✅ HttpWebRequest を使用した高度な実装
```csharp
public class AdvancedApiClient
{
    private readonly string _baseUrl;
    private readonly int _timeout;
    
    public AdvancedApiClient(string baseUrl, int timeoutMs = 30000)
    {
        _baseUrl = baseUrl;
        _timeout = timeoutMs;
    }
    
    public T ExecuteRequest<T>(string endpoint, string method, object data = null)
    {
        var request = (HttpWebRequest)WebRequest.Create(_baseUrl + endpoint);
        request.Method = method;
        request.ContentType = "application/json";
        request.Timeout = _timeout;
        
        // 認証ヘッダー
        request.Headers.Add("Authorization", "Bearer " + GetAuthToken());
        
        // リクエストボディ
        if (data != null && (method == "POST" || method == "PUT"))
        {
            var json = JsonConvert.SerializeObject(data);
            var bytes = Encoding.UTF8.GetBytes(json);
            request.ContentLength = bytes.Length;
            
            using (var stream = request.GetRequestStream())
            {
                stream.Write(bytes, 0, bytes.Length);
            }
        }
        
        // レスポンス処理
        try
        {
            using (var response = (HttpWebResponse)request.GetResponse())
            using (var reader = new StreamReader(response.GetResponseStream()))
            {
                var responseJson = reader.ReadToEnd();
                return JsonConvert.DeserializeObject<T>(responseJson);
            }
        }
        catch (WebException ex)
        {
            if (ex.Response != null)
            {
                using (var reader = new StreamReader(ex.Response.GetResponseStream()))
                {
                    var errorResponse = reader.ReadToEnd();
                    throw new ApplicationException("API Error: " + errorResponse, ex);
                }
            }
            throw;
        }
    }
}
```

### CallerMemberName 属性が使用できない（4.5で導入）

#### ❌ 使用できないコード
```csharp
// .NET Framework 4.5以降
public void LogMessage(string message, [CallerMemberName] string memberName = "")
{
    Console.WriteLine($"{memberName}: {message}");
}
```

#### ✅ .NET Framework 4.0 での代替実装
```csharp
public class Logger
{
    // 手動でメソッド名を指定
    public void LogMessage(string message, string memberName)
    {
        Console.WriteLine("{0}: {1}", memberName, message);
    }
    
    // スタックトレースから取得（パフォーマンスに注意）
    public void LogMessageAuto(string message)
    {
        var stackTrace = new StackTrace();
        var method = stackTrace.GetFrame(1).GetMethod();
        var memberName = method.Name;
        Console.WriteLine("{0}: {1}", memberName, message);
    }
}

// 使用例
public void ProcessData()
{
    _logger.LogMessage("処理を開始します", "ProcessData");
    // または
    _logger.LogMessageAuto("処理を開始します");
}
```

## 2. Task Parallel Library (TPL) の制限

### Task.Run が使用できない（4.5で導入）

#### ✅ Task.Factory.StartNew を使用
```csharp
// .NET Framework 4.5以降
// Task.Run(() => DoWork());

// .NET Framework 4.0
Task.Factory.StartNew(() => DoWork());

// 長時間実行タスクの場合
Task.Factory.StartNew(() => DoLongRunningWork(), 
    TaskCreationOptions.LongRunning);
```

### Parallel.ForEach の基本的な使用
```csharp
public void ProcessItemsInParallel(List<DataItem> items)
{
    // .NET Framework 4.0 でも使用可能
    Parallel.ForEach(items, item =>
    {
        ProcessItem(item);
    });
    
    // オプション付き
    var options = new ParallelOptions
    {
        MaxDegreeOfParallelism = Environment.ProcessorCount
    };
    
    Parallel.ForEach(items, options, item =>
    {
        ProcessItem(item);
    });
}
```

## 3. NuGet パッケージ管理の制限

### packages.config による手動管理

#### プロジェクトファイル設定
```xml
<!-- .NET Framework 4.0 プロジェクトでの NuGet 設定 -->
<Project>
  <PropertyGroup>
    <RestorePackages>true</RestorePackages>
    <DownloadNuGetExe>true</DownloadNuGetExe>
  </PropertyGroup>
  
  <!-- NuGet パッケージ復元タスク -->
  <Import Project="$(SolutionDir)\.nuget\NuGet.targets" />
</Project>
```

#### packages.config の例
```xml
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <!-- .NET Framework 4.0 対応バージョンを明示的に指定 -->
  <package id="Newtonsoft.Json" version="6.0.8" targetFramework="net40" />
  <package id="log4net" version="2.0.3" targetFramework="net40" />
  <package id="Unity" version="2.1.505.2" targetFramework="net40" />
  <package id="EntityFramework" version="5.0.0" targetFramework="net40" />
</packages>
```

## 4. C# 4.0 言語機能の活用

### 利用可能な機能
```csharp
// 1. dynamic 型
dynamic expando = new ExpandoObject();
expando.Name = "Dynamic Property";
expando.GetValue = new Func<string>(() => "Dynamic Method");

// 2. 名前付き引数とオプション引数
public void ConfigureApp(
    string appName, 
    int timeout = 30000, 
    bool enableLogging = true)
{
    // 実装
}

// 呼び出し
ConfigureApp("MyApp", enableLogging: false);

// 3. 共変性と反変性
IEnumerable<string> strings = new List<string>();
IEnumerable<object> objects = strings; // 共変性

// 4. Tuple のサポート（System.Tuple）
public Tuple<bool, string> ValidateInput(string input)
{
    if (string.IsNullOrEmpty(input))
        return Tuple.Create(false, "入力が空です");
    
    return Tuple.Create(true, "OK");
}
```

## 5. Windows Forms での非同期パターン

### BackgroundWorker を使用した進捗表示付き非同期処理
```csharp
public partial class MainForm : Form
{
    private BackgroundWorker _worker;
    
    public MainForm()
    {
        InitializeComponent();
        InitializeBackgroundWorker();
    }
    
    private void InitializeBackgroundWorker()
    {
        _worker = new BackgroundWorker();
        _worker.WorkerReportsProgress = true;
        _worker.WorkerSupportsCancellation = true;
        
        _worker.DoWork += Worker_DoWork;
        _worker.ProgressChanged += Worker_ProgressChanged;
        _worker.RunWorkerCompleted += Worker_RunWorkerCompleted;
    }
    
    private void btnStart_Click(object sender, EventArgs e)
    {
        if (!_worker.IsBusy)
        {
            btnStart.Enabled = false;
            btnCancel.Enabled = true;
            _worker.RunWorkerAsync();
        }
    }
    
    private void Worker_DoWork(object sender, DoWorkEventArgs e)
    {
        var worker = sender as BackgroundWorker;
        
        for (int i = 1; i <= 100; i++)
        {
            if (worker.CancellationPending)
            {
                e.Cancel = true;
                break;
            }
            
            // 実際の処理
            System.Threading.Thread.Sleep(50);
            
            // 進捗報告
            worker.ReportProgress(i);
        }
        
        e.Result = "処理完了";
    }
    
    private void Worker_ProgressChanged(object sender, ProgressChangedEventArgs e)
    {
        progressBar1.Value = e.ProgressPercentage;
        lblStatus.Text = string.Format("処理中... {0}%", e.ProgressPercentage);
    }
    
    private void Worker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
    {
        if (e.Cancelled)
        {
            lblStatus.Text = "キャンセルされました";
        }
        else if (e.Error != null)
        {
            lblStatus.Text = "エラー: " + e.Error.Message;
        }
        else
        {
            lblStatus.Text = e.Result.ToString();
        }
        
        btnStart.Enabled = true;
        btnCancel.Enabled = false;
        progressBar1.Value = 0;
    }
}
```

## 6. ThreadPool を使用した軽量非同期処理
```csharp
public class AsyncProcessor
{
    public void ProcessMultipleItems(List<string> items)
    {
        var countdown = new CountdownEvent(items.Count);
        var results = new ConcurrentBag<string>();
        
        foreach (var item in items)
        {
            ThreadPool.QueueUserWorkItem(state =>
            {
                try
                {
                    var result = ProcessItem((string)state);
                    results.Add(result);
                }
                finally
                {
                    countdown.Signal();
                }
            }, item);
        }
        
        // すべての処理が完了するまで待機
        countdown.Wait();
        
        // 結果を処理
        foreach (var result in results)
        {
            Console.WriteLine(result);
        }
    }
    
    private string ProcessItem(string item)
    {
        // 処理実装
        return "Processed: " + item;
    }
}
```

## 7. .NET Framework 4.0 でのベストプラクティス

### メモリ管理
```csharp
public class ResourceManager : IDisposable
{
    private bool _disposed = false;
    private IntPtr _unmanagedResource;
    private FileStream _managedResource;
    
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
    
    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                // マネージドリソースの解放
                if (_managedResource != null)
                {
                    _managedResource.Dispose();
                    _managedResource = null;
                }
            }
            
            // アンマネージドリソースの解放
            if (_unmanagedResource != IntPtr.Zero)
            {
                Marshal.FreeHGlobal(_unmanagedResource);
                _unmanagedResource = IntPtr.Zero;
            }
            
            _disposed = true;
        }
    }
    
    ~ResourceManager()
    {
        Dispose(false);
    }
}
```

このガイドに従うことで、.NET Framework 4.0 の制限を理解し、適切な代替実装を行うことができます。