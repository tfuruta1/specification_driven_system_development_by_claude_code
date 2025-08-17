# /dotnet40-optimize - .NET Framework 4.0 レガシー最適化専用コマンド

## 概要
.NET Framework 4.0をターゲットとしたレガシーシステムの最適化コマンドです。Windows XP/7互換性、COM相互運用、レガシーAPI対応を重視した安定性重視の最適化を提供します。

## 使用方法
```bash
/dotnet40-optimize [feature] [action] [options]

# 使用例
/dotnet40-optimize legacy com-interop --register
/dotnet40-optimize memory gc-optimize --workstation
/dotnet40-optimize threading background-worker --optimize
/dotnet40-optimize deploy windows-xp --compatible
/dotnet40-optimize performance ngen --install
```

## .NET Framework 4.0 専用最適化機能

### 1. レガシー互換性とCOM相互運用
```csharp
// Legacy/ComInteropManager.cs
using System;
using System.Runtime.InteropServices;
using System.EnterpriseServices;
using Microsoft.Win32;

[ComVisible(true)]
[Guid("12345678-1234-1234-1234-123456789012")]
[ClassInterface(ClassInterfaceType.AutoDual)]
[ProgId("EnterpriseApp.ComServer")]
public class ComInteropManager : ServicedComponent
{
    // COM+ トランザクション対応
    [AutoComplete]
    [Transaction(TransactionOption.Required)]
    public void ProcessTransaction(string data)
    {
        try
        {
            // トランザクション処理
            ContextUtil.SetComplete();
        }
        catch (Exception ex)
        {
            ContextUtil.SetAbort();
            throw new COMException("Transaction failed", ex);
        }
    }
    
    // レガシーActiveX コントロール操作
    public class ActiveXWrapper
    {
        [DllImport("oleaut32.dll")]
        private static extern int LoadTypeLib(
            [MarshalAs(UnmanagedType.LPWStr)] string szFile,
            out ITypeLib ppTypeLib);
        
        [ComImport]
        [Guid("00020402-0000-0000-C000-000000000046")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface ITypeLib
        {
            // ITypeLib メソッド定義
        }
        
        public static void RegisterActiveX(string dllPath)
        {
            try
            {
                // regsvr32 相当の処理
                var processInfo = new ProcessStartInfo
                {
                    FileName = "regsvr32.exe",
                    Arguments = $"/s \"{dllPath}\"",
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                
                using (var process = Process.Start(processInfo))
                {
                    process.WaitForExit();
                    if (process.ExitCode != 0)
                    {
                        throw new Exception($"Failed to register ActiveX: {dllPath}");
                    }
                }
            }
            catch (Exception ex)
            {
                EventLog.WriteEntry("Application", 
                    $"ActiveX registration failed: {ex.Message}", 
                    EventLogEntryType.Error);
            }
        }
    }
    
    // VB6 との相互運用
    [ComVisible(true)]
    [InterfaceType(ComInterfaceType.InterfaceIsDual)]
    public interface IVB6Compatible
    {
        [DispId(1)]
        string ProcessData(string input);
        
        [DispId(2)]
        object GetVariantData();
        
        [DispId(3)]
        void SetVariantData(object data);
    }
    
    public class VB6Bridge : IVB6Compatible
    {
        public string ProcessData(string input)
        {
            // VB6 文字列処理の互換性確保
            if (input == null) return string.Empty;
            
            // VB6 の vbCrLf 対応
            return input.Replace("\r\n", Environment.NewLine);
        }
        
        public object GetVariantData()
        {
            // VARIANT 型として返す
            return new object[] { 1, "text", DateTime.Now };
        }
        
        public void SetVariantData(object data)
        {
            // VARIANT 型の処理
            if (data is Array array)
            {
                foreach (var item in array)
                {
                    ProcessVariantItem(item);
                }
            }
        }
        
        private void ProcessVariantItem(object item)
        {
            switch (Type.GetTypeCode(item?.GetType()))
            {
                case TypeCode.Int32:
                case TypeCode.Double:
                case TypeCode.String:
                case TypeCode.DateTime:
                    // 型別処理
                    break;
            }
        }
    }
}

// Windows XP/7 API 互換性
public class LegacyWindowsApi
{
    // XP時代のAPI
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalAlloc(uint uFlags, UIntPtr dwBytes);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalFree(IntPtr hMem);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalLock(IntPtr hMem);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GlobalUnlock(IntPtr hMem);
    
    // Windows XP 互換のファイル操作
    public static void XpCompatibleFileOperation(string path)
    {
        // 8.3 形式パス名対応
        var shortPath = GetShortPathName(path);
        
        // MAX_PATH (260文字) 制限対応
        if (path.Length >= 260)
        {
            path = @"\\?\" + path; // 長いパス名のサポート
        }
    }
    
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern uint GetShortPathName(
        string lpszLongPath,
        StringBuilder lpszShortPath,
        uint cchBuffer);
    
    private static string GetShortPathName(string longPath)
    {
        var shortPath = new StringBuilder(260);
        GetShortPathName(longPath, shortPath, (uint)shortPath.Capacity);
        return shortPath.ToString();
    }
}
```

### 2. レガシー非同期処理パターン
```csharp
// Threading/LegacyAsyncManager.cs
using System;
using System.Threading;
using System.ComponentModel;

public class LegacyAsyncManager
{
    // BackgroundWorker パターン
    public class OptimizedBackgroundWorker
    {
        private readonly BackgroundWorker _worker;
        private readonly Queue<Action> _workQueue;
        private readonly object _queueLock = new object();
        
        public OptimizedBackgroundWorker()
        {
            _worker = new BackgroundWorker
            {
                WorkerReportsProgress = true,
                WorkerSupportsCancellation = true
            };
            
            _worker.DoWork += Worker_DoWork;
            _worker.ProgressChanged += Worker_ProgressChanged;
            _worker.RunWorkerCompleted += Worker_RunWorkerCompleted;
            
            _workQueue = new Queue<Action>();
        }
        
        public void QueueWork(Action work)
        {
            lock (_queueLock)
            {
                _workQueue.Enqueue(work);
                
                if (!_worker.IsBusy)
                {
                    _worker.RunWorkerAsync();
                }
            }
        }
        
        private void Worker_DoWork(object sender, DoWorkEventArgs e)
        {
            while (true)
            {
                Action work = null;
                
                lock (_queueLock)
                {
                    if (_workQueue.Count > 0)
                    {
                        work = _workQueue.Dequeue();
                    }
                }
                
                if (work == null)
                    break;
                
                if (_worker.CancellationPending)
                {
                    e.Cancel = true;
                    break;
                }
                
                try
                {
                    work();
                    _worker.ReportProgress(0);
                }
                catch (Exception ex)
                {
                    e.Result = ex;
                }
            }
        }
        
        private void Worker_ProgressChanged(object sender, ProgressChangedEventArgs e)
        {
            // 進捗更新処理
        }
        
        private void Worker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            if (e.Error != null)
            {
                // エラー処理
            }
            else if (e.Cancelled)
            {
                // キャンセル処理
            }
        }
    }
    
    // ThreadPool 最適化
    public class ThreadPoolOptimizer
    {
        private static readonly int OptimalThreadCount;
        
        static ThreadPoolOptimizer()
        {
            // CPU コア数に基づく最適化
            OptimalThreadCount = Environment.ProcessorCount * 2;
            
            int workerThreads, completionPortThreads;
            ThreadPool.GetMaxThreads(out workerThreads, out completionPortThreads);
            
            // .NET 4.0 での ThreadPool 設定
            ThreadPool.SetMinThreads(OptimalThreadCount, OptimalThreadCount);
            ThreadPool.SetMaxThreads(workerThreads, completionPortThreads);
        }
        
        public static void QueueOptimizedWork(WaitCallback callback, object state = null)
        {
            // 優先度付きキューイング
            if (ThreadPool.QueueUserWorkItem(callback, state))
            {
                Interlocked.Increment(ref _pendingWorkItems);
            }
        }
        
        private static int _pendingWorkItems;
        
        public static int PendingWorkItems => _pendingWorkItems;
    }
    
    // APM (Asynchronous Programming Model) パターン
    public class ApmOptimizer
    {
        public IAsyncResult BeginOperation(AsyncCallback callback, object state)
        {
            var result = new CustomAsyncResult(callback, state);
            
            ThreadPool.QueueUserWorkItem(_ =>
            {
                try
                {
                    // 非同期操作
                    Thread.Sleep(1000); // 実際の処理
                    
                    result.SetComplete(null);
                }
                catch (Exception ex)
                {
                    result.SetComplete(ex);
                }
            });
            
            return result;
        }
        
        public void EndOperation(IAsyncResult asyncResult)
        {
            var result = (CustomAsyncResult)asyncResult;
            result.EndInvoke();
        }
        
        private class CustomAsyncResult : IAsyncResult
        {
            private readonly AsyncCallback _callback;
            private readonly object _state;
            private readonly ManualResetEvent _waitHandle;
            private Exception _exception;
            private bool _completed;
            
            public CustomAsyncResult(AsyncCallback callback, object state)
            {
                _callback = callback;
                _state = state;
                _waitHandle = new ManualResetEvent(false);
            }
            
            public void SetComplete(Exception exception)
            {
                _exception = exception;
                _completed = true;
                _waitHandle.Set();
                
                _callback?.Invoke(this);
            }
            
            public void EndInvoke()
            {
                if (!_completed)
                {
                    _waitHandle.WaitOne();
                }
                
                if (_exception != null)
                {
                    throw _exception;
                }
            }
            
            public object AsyncState => _state;
            public WaitHandle AsyncWaitHandle => _waitHandle;
            public bool CompletedSynchronously => false;
            public bool IsCompleted => _completed;
        }
    }
}
```

### 3. メモリとパフォーマンス最適化
```csharp
// Performance/Net40Optimizer.cs
using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;

public class Net40MemoryOptimizer
{
    // .NET 4.0 での GC 最適化
    public static void OptimizeGarbageCollection()
    {
        // ワークステーションGC（デスクトップアプリ向け）
        // app.config で設定:
        // <runtime>
        //   <gcServer enabled="false"/>
        //   <gcConcurrent enabled="true"/>
        // </runtime>
        
        // 世代別GC強制実行
        GC.Collect(0, GCCollectionMode.Optimized); // Gen0のみ
        
        // 大きなオブジェクトヒープの圧縮（.NET 4.5.1以降の機能のため4.0では使用不可）
        // 代わりに定期的なフルGCを実行
        if (GC.GetTotalMemory(false) > 100 * 1024 * 1024) // 100MB以上
        {
            GC.Collect(GC.MaxGeneration, GCCollectionMode.Forced);
            GC.WaitForPendingFinalizers();
            GC.Collect();
        }
    }
    
    // 文字列処理の最適化
    public class StringOptimizer
    {
        private static readonly Dictionary<string, string> StringCache = 
            new Dictionary<string, string>();
        
        // 文字列インターン化のカスタム実装
        public static string Intern(string str)
        {
            if (string.IsNullOrEmpty(str))
                return str;
            
            lock (StringCache)
            {
                string cached;
                if (StringCache.TryGetValue(str, out cached))
                {
                    return cached;
                }
                
                StringCache[str] = str;
                return str;
            }
        }
        
        // StringBuilder プールリング
        private static readonly Stack<StringBuilder> StringBuilderPool = 
            new Stack<StringBuilder>();
        
        public static StringBuilder RentStringBuilder()
        {
            lock (StringBuilderPool)
            {
                if (StringBuilderPool.Count > 0)
                {
                    return StringBuilderPool.Pop().Clear();
                }
            }
            
            return new StringBuilder(256);
        }
        
        public static void ReturnStringBuilder(StringBuilder sb)
        {
            if (sb.Capacity > 4096) // 大きすぎるものはプールに戻さない
                return;
            
            lock (StringBuilderPool)
            {
                if (StringBuilderPool.Count < 10)
                {
                    StringBuilderPool.Push(sb);
                }
            }
        }
    }
    
    // コレクション最適化
    public class CollectionOptimizer
    {
        // 事前サイズ指定による最適化
        public static List<T> CreateOptimizedList<T>(int expectedSize)
        {
            // 2のべき乗に切り上げ（内部配列の再割り当てを減らす）
            int capacity = 16;
            while (capacity < expectedSize)
            {
                capacity *= 2;
            }
            
            return new List<T>(capacity);
        }
        
        // Dictionary の最適化
        public static Dictionary<TKey, TValue> CreateOptimizedDictionary<TKey, TValue>(
            int expectedSize)
        {
            // 素数を使用（ハッシュ衝突を減らす）
            int[] primes = { 17, 37, 79, 163, 331, 673, 1361, 2729, 5471, 10949 };
            
            int capacity = primes[0];
            foreach (int prime in primes)
            {
                if (prime >= expectedSize)
                {
                    capacity = prime;
                    break;
                }
            }
            
            return new Dictionary<TKey, TValue>(capacity);
        }
    }
}

// NGEN (Native Image Generator) 最適化
public class NgenOptimizer
{
    public static void InstallNativeImages()
    {
        // NGEN でネイティブイメージを生成
        var ngenPath = Path.Combine(
            RuntimeEnvironment.GetRuntimeDirectory(), 
            "ngen.exe");
        
        var assemblies = new[]
        {
            Assembly.GetExecutingAssembly().Location,
            // 他の重要なアセンブリ
        };
        
        foreach (var assembly in assemblies)
        {
            var processInfo = new ProcessStartInfo
            {
                FileName = ngenPath,
                Arguments = $"install \"{assembly}\" /silent",
                UseShellExecute = false,
                CreateNoWindow = true,
                Verb = "runas" // 管理者権限が必要
            };
            
            try
            {
                using (var process = Process.Start(processInfo))
                {
                    process.WaitForExit();
                }
            }
            catch (Exception ex)
            {
                // NGEN失敗はアプリ実行に影響しないため続行
                Trace.WriteLine($"NGEN failed: {ex.Message}");
            }
        }
    }
}
```

### 4. Windows XP/7 互換デプロイメント
```xml
<!-- app.config - Windows XP/7 互換設定 -->
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <startup>
    <!-- Windows XP SP3 以降をサポート -->
    <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.0,Profile=Client"/>
  </startup>
  
  <runtime>
    <!-- レガシーセキュリティポリシー -->
    <NetFx40_LegacySecurityPolicy enabled="true"/>
    
    <!-- CAS ポリシー（Code Access Security） -->
    <legacyCasPolicy enabled="true"/>
    
    <!-- アセンブリバインディング -->
    <assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1">
      <probing privatePath="bin;plugins"/>
      
      <!-- 強い名前のバイパス（開発環境用） -->
      <bypassTrustedAppStrongNames enabled="true"/>
    </assemblyBinding>
    
    <!-- GC設定 -->
    <gcConcurrent enabled="true"/>
    <gcServer enabled="false"/>
  </runtime>
  
  <system.diagnostics>
    <trace autoflush="true">
      <listeners>
        <add name="textWriterTraceListener" 
             type="System.Diagnostics.TextWriterTraceListener" 
             initializeData="trace.log"/>
      </listeners>
    </trace>
  </system.diagnostics>
</configuration>
```

```csharp
// Deployment/XpCompatibleDeployment.cs
public class XpCompatibleDeployment
{
    // Windows XP での実行確認
    public static bool IsWindowsXpCompatible()
    {
        var os = Environment.OSVersion;
        
        // Windows XP: 5.1, Windows Server 2003: 5.2
        if (os.Platform == PlatformID.Win32NT)
        {
            if (os.Version.Major == 5 && os.Version.Minor >= 1)
            {
                return true;
            }
        }
        
        return false;
    }
    
    // 必須ランタイムチェック
    public static bool CheckPrerequisites()
    {
        try
        {
            // .NET Framework 4.0 確認
            using (var key = Registry.LocalMachine.OpenSubKey(
                @"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full"))
            {
                if (key == null)
                {
                    MessageBox.Show(
                        ".NET Framework 4.0 が必要です。",
                        "システム要件",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error);
                    return false;
                }
            }
            
            // Visual C++ 再頒布可能パッケージ確認
            if (!CheckVCRedist())
            {
                MessageBox.Show(
                    "Visual C++ 2010 再頒布可能パッケージが必要です。",
                    "システム要件",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning);
            }
            
            return true;
        }
        catch
        {
            return false;
        }
    }
    
    private static bool CheckVCRedist()
    {
        // レジストリから VC++ ランタイムを確認
        var registryPaths = new[]
        {
            @"SOFTWARE\Microsoft\VisualStudio\10.0\VC\VCRedist\x86",
            @"SOFTWARE\Wow6432Node\Microsoft\VisualStudio\10.0\VC\VCRedist\x86"
        };
        
        foreach (var path in registryPaths)
        {
            using (var key = Registry.LocalMachine.OpenSubKey(path))
            {
                if (key != null)
                {
                    var installed = key.GetValue("Installed");
                    if (installed != null && (int)installed == 1)
                    {
                        return true;
                    }
                }
            }
        }
        
        return false;
    }
}
```

## 出力レポート
```markdown
# .NET Framework 4.0 最適化レポート

## 実施項目
✅ COM相互運用: 完全実装
✅ レガシーAPI: Windows XP/7対応
✅ 非同期処理: BackgroundWorker最適化
✅ メモリ管理: GCチューニング実施
✅ 配布: XP互換性確保

## パフォーマンス改善
- 起動時間: 5秒 → 2秒 (60%改善)
- メモリ使用量: 180MB → 120MB (33%削減)
- COM呼び出し: 50ms → 20ms (60%改善)
- ThreadPool効率: 40%向上

## 互換性
- Windows XP SP3: ✅ 対応
- Windows 7: ✅ 対応
- COM/ActiveX: ✅ 完全互換
- VB6連携: ✅ 動作確認済み

## 推奨事項
1. 可能であれば.NET 4.5以降へ移行
2. NGENによる起動高速化
3. 定期的なメモリプロファイリング
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: .NET Framework 4.0 レガシーシステム保守

---
*このコマンドは.NET Framework 4.0レガシーシステムの安定運用に特化しています。*