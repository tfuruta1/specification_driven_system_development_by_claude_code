# /dotnet40-optimize - .NET Framework 4.0 TASK

## TASK
.NET Framework 4.0TASKWindows XP/7TASKCOMTASKAPITASK

## TASK
```bash
/dotnet40-optimize [feature] [action] [options]

# TASK
/dotnet40-optimize legacy com-interop --register
/dotnet40-optimize memory gc-optimize --workstation
/dotnet40-optimize threading background-worker --optimize
/dotnet40-optimize deploy windows-xp --compatible
/dotnet40-optimize performance ngen --install
```

## .NET Framework 4.0 SYSTEM

### 1. SYSTEMCOMSYSTEM
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
    // COM+ SUCCESS
    [AutoComplete]
    [Transaction(TransactionOption.Required)]
    public void ProcessTransaction(string data)
    {
        try
        {
            // SUCCESS
            ContextUtil.SetComplete();
        }
        catch (Exception ex)
        {
            ContextUtil.SetAbort();
            throw new COMException("Transaction failed", ex);
        }
    }
    
    // ERRORActiveX ERROR
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
            // ITypeLib 
        }
        
        public static void RegisterActiveX(string dllPath)
        {
            try
            {
                // regsvr32 
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
    
    // VB6 ERROR
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
            // VB6 
            if (input == null) return string.Empty;
            
            // VB6  vbCrLf 
            return input.Replace("\r\n", Environment.NewLine);
        }
        
        public object GetVariantData()
        {
            // VARIANT 
            return new object[] { 1, "text", DateTime.Now };
        }
        
        public void SetVariantData(object data)
        {
            // VARIANT 
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
                    // 
                    break;
            }
        }
    }
}

// Windows XP/7 API ERROR
public class LegacyWindowsApi
{
    // XPERRORAPI
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalAlloc(uint uFlags, UIntPtr dwBytes);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalFree(IntPtr hMem);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalLock(IntPtr hMem);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GlobalUnlock(IntPtr hMem);
    
    // Windows XP ERROR
    public static void XpCompatibleFileOperation(string path)
    {
        // 8.3 
        var shortPath = GetShortPathName(path);
        
        // MAX_PATH (260) 
        if (path.Length >= 260)
        {
            path = @"\\?\" + path; // ERROR
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

### 2. SYSTEM
```csharp
// Threading/LegacyAsyncManager.cs
using System;
using System.Threading;
using System.ComponentModel;

public class LegacyAsyncManager
{
    // BackgroundWorker SYSTEM
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
            // SUCCESS
        }
        
        private void Worker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            if (e.Error != null)
            {
                // SUCCESS
            }
            else if (e.Cancelled)
            {
                // 
            }
        }
    }
    
    // ThreadPool 
    public class ThreadPoolOptimizer
    {
        private static readonly int OptimalThreadCount;
        
        static ThreadPoolOptimizer()
        {
            // CPU TASK
            OptimalThreadCount = Environment.ProcessorCount * 2;
            
            int workerThreads, completionPortThreads;
            ThreadPool.GetMaxThreads(out workerThreads, out completionPortThreads);
            
            // .NET 4.0 TASK ThreadPool TASK
            ThreadPool.SetMinThreads(OptimalThreadCount, OptimalThreadCount);
            ThreadPool.SetMaxThreads(workerThreads, completionPortThreads);
        }
        
        public static void QueueOptimizedWork(WaitCallback callback, object state = null)
        {
            // TASK
            if (ThreadPool.QueueUserWorkItem(callback, state))
            {
                Interlocked.Increment(ref _pendingWorkItems);
            }
        }
        
        private static int _pendingWorkItems;
        
        public static int PendingWorkItems => _pendingWorkItems;
    }
    
    // APM (Asynchronous Programming Model) TASK
    public class ApmOptimizer
    {
        public IAsyncResult BeginOperation(AsyncCallback callback, object state)
        {
            var result = new CustomAsyncResult(callback, state);
            
            ThreadPool.QueueUserWorkItem(_ =>
            {
                try
                {
                    // TASK
                    Thread.Sleep(1000); // SUCCESS
                    
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

### 3. SUCCESS
```csharp
// Performance/Net40Optimizer.cs
using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;

public class Net40MemoryOptimizer
{
    // .NET 4.0 SYSTEM GC SYSTEM
    public static void OptimizeGarbageCollection()
    {
        // CONFIGGCCONFIG
        // app.config CONFIG:
        // <runtime>
        //   <gcServer enabled="false"/>
        //   <gcConcurrent enabled="true"/>
        // </runtime>
        
        // GC
        GC.Collect(0, GCCollectionMode.Optimized); // Gen0
        
        // .NET 4.5.14.0
        // GC
        if (GC.GetTotalMemory(false) > 100 * 1024 * 1024) // 100MB
        {
            GC.Collect(GC.MaxGeneration, GCCollectionMode.Forced);
            GC.WaitForPendingFinalizers();
            GC.Collect();
        }
    }
    
    // 
    public class StringOptimizer
    {
        private static readonly Dictionary<string, string> StringCache = 
            new Dictionary<string, string>();
        
        // 
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
        
        // StringBuilder 
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
            if (sb.Capacity > 4096) // 
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
    
    // 
    public class CollectionOptimizer
    {
        // 
        public static List<T> CreateOptimizedList<T>(int expectedSize)
        {
            // 2
            int capacity = 16;
            while (capacity < expectedSize)
            {
                capacity *= 2;
            }
            
            return new List<T>(capacity);
        }
        
        // Dictionary 
        public static Dictionary<TKey, TValue> CreateOptimizedDictionary<TKey, TValue>(
            int expectedSize)
        {
            // 
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

// NGEN (Native Image Generator) 
public class NgenOptimizer
{
    public static void InstallNativeImages()
    {
        // NGEN 
        var ngenPath = Path.Combine(
            RuntimeEnvironment.GetRuntimeDirectory(), 
            "ngen.exe");
        
        var assemblies = new[]
        {
            Assembly.GetExecutingAssembly().Location,
            // 
        };
        
        foreach (var assembly in assemblies)
        {
            var processInfo = new ProcessStartInfo
            {
                FileName = ngenPath,
                Arguments = $"install \"{assembly}\" /silent",
                UseShellExecute = false,
                CreateNoWindow = true,
                Verb = "runas" // 
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
                // NGENERROR
                Trace.WriteLine($"NGEN failed: {ex.Message}");
            }
        }
    }
}
```

### 4. Windows XP/7 ERROR
```xml
<!-- app.config - Windows XP/7 CONFIG -->
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <startup>
    <!-- Windows XP SP3 CONFIG -->
    <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.0,Profile=Client"/>
  </startup>
  
  <runtime>
    <!-- TASK -->
    <NetFx40_LegacySecurityPolicy enabled="true"/>
    
    <!-- CAS Code Access Security -->
    <legacyCasPolicy enabled="true"/>
    
    <!--  -->
    <assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1">
      <probing privatePath="bin;plugins"/>
      
      <!-- SUCCESS -->
      <bypassTrustedAppStrongNames enabled="true"/>
    </assemblyBinding>
    
    <!-- GCSUCCESS -->
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
    // Windows XP 
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
    
    // ANALYSIS
    public static bool CheckPrerequisites()
    {
        try
        {
            // .NET Framework 4.0 TASK
            using (var key = Registry.LocalMachine.OpenSubKey(
                @"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full"))
            {
                if (key == null)
                {
                    MessageBox.Show(
                        ".NET Framework 4.0 TASK",
                        "ERROR",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error);
                    return false;
                }
            }
            
            // Visual C++ ANALYSIS
            if (!CheckVCRedist())
            {
                MessageBox.Show(
                    "Visual C++ 2010 ",
                    "WARNING",
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
        // ANALYSIS VC++ ANALYSIS
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

## TASK
```markdown
# .NET Framework 4.0 TASK

## TASK
[OK] COMTASK: TASK
[OK] TASKAPI: Windows XP/7TASK
[OK] TASK: BackgroundWorkerTASK
[OK] TASK: GCTASK
[OK] TASK: XPTASK

## TASK
- TASK: 5TASK -> 2TASK (60%)
- : 180MB -> 120MB (33%)
- COM: 50ms -> 20ms (60%)
- ThreadPool: 40%

## 
- Windows XP SP3: [OK] 
- Windows 7: [OK] 
- COM/ActiveX: [OK] 
- VB6: [OK] 

## 
1. .NET 4.5TASK
2. NGENTASK
3. TASK
```

## TASK
- **TASK**: TASK
- **TASK**: .NET Framework 4.0 TASK

---
*TASK.NET Framework 4.0TASK*