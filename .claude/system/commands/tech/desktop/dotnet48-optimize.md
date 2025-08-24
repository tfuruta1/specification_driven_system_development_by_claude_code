# /dotnet48-optimize - .NET Framework 4.8 TASK

## TASK
.NET Framework 4.8TASKDPITASKasync/awaitTASKC#TASK

## TASK
```bash
/dotnet48-optimize [feature] [action] [options]

# 
/dotnet48-optimize async convert --all-methods
/dotnet48-optimize highdpi enable --per-monitor-v2
/dotnet48-optimize performance profile --dotmemory
/dotnet48-optimize security harden --dotfuscator
/dotnet48-optimize deploy prepare --clickonce
```

## .NET Framework 4.8 SYSTEM

### 1. SYSTEM
```csharp
// Services/AsyncOptimizer.cs
using System;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using System.Runtime.CompilerServices;

public class AsyncOptimizer
{
    private readonly SemaphoreSlim _semaphore;
    private readonly ConcurrentDictionary<string, Task> _runningTasks;
    private readonly TaskScheduler _customScheduler;
    
    public AsyncOptimizer()
    {
        // CPU TASK
        var maxDegreeOfParallelism = Environment.ProcessorCount * 2;
        _semaphore = new SemaphoreSlim(maxDegreeOfParallelism);
        _runningTasks = new ConcurrentDictionary<string, Task>();
        
        // IN PROGRESS
        _customScheduler = new PriorityTaskScheduler();
    }
    
    // ValueTask TASK
    public async ValueTask<T> ExecuteAsync<T>(
        Func<CancellationToken, Task<T>> operation,
        CancellationToken cancellationToken = default,
        [CallerMemberName] string operationName = "")
    {
        // IN PROGRESS
        if (_runningTasks.TryGetValue(operationName, out var existingTask))
        {
            return await (Task<T>)existingTask;
        }
        
        await _semaphore.WaitAsync(cancellationToken);
        try
        {
            var task = Task.Factory.StartNew(
                async () => await operation(cancellationToken),
                cancellationToken,
                TaskCreationOptions.None,
                _customScheduler
            ).Unwrap();
            
            _runningTasks.TryAdd(operationName, task);
            
            return await task;
        }
        finally
        {
            _semaphore.Release();
            _runningTasks.TryRemove(operationName, out _);
        }
    }
    
    // ConfigureAwait CONFIG
    public async Task OptimizeConfigureAwait(Func<Task> operation)
    {
        // UICONFIG false
        await operation().ConfigureAwait(false);
    }
    
    // CONFIGIAsyncEnumerableCONFIG
    public async IAsyncEnumerable<T> ProcessStreamAsync<T>(
        IEnumerable<T> source,
        Func<T, Task<T>> processor,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var parallelOptions = new ParallelOptions
        {
            CancellationToken = cancellationToken,
            MaxDegreeOfParallelism = Environment.ProcessorCount
        };
        
        var channel = Channel.CreateUnbounded<T>();
        
        // IN PROGRESS
        var processingTask = Task.Run(async () =>
        {
            await Parallel.ForEachAsync(source, parallelOptions, async (item, ct) =>
            {
                var processed = await processor(item);
                await channel.Writer.WriteAsync(processed, ct);
            });
            
            channel.Writer.Complete();
        }, cancellationToken);
        
        // SUCCESS
        await foreach (var item in channel.Reader.ReadAllAsync(cancellationToken))
        {
            yield return item;
        }
        
        await processingTask;
    }
}

// IN PROGRESS
public class PriorityTaskScheduler : TaskScheduler
{
    private readonly ConcurrentPriorityQueue<Task, int> _tasks = new();
    private readonly Thread[] _threads;
    
    public PriorityTaskScheduler()
    {
        _threads = new Thread[Environment.ProcessorCount];
        for (int i = 0; i < _threads.Length; i++)
        {
            _threads[i] = new Thread(ProcessTasks)
            {
                IsBackground = true,
                Name = $"PriorityWorker-{i}"
            };
            _threads[i].Start();
        }
    }
    
    private void ProcessTasks()
    {
        while (true)
        {
            if (_tasks.TryDequeue(out var task, out _))
            {
                TryExecuteTask(task);
            }
            else
            {
                Thread.Sleep(10);
            }
        }
    }
    
    protected override IEnumerable<Task> GetScheduledTasks() => _tasks.ToArray();
    
    protected override void QueueTask(Task task)
    {
        // TASK
        var priority = CalculatePriority(task);
        _tasks.Enqueue(task, priority);
    }
    
    protected override bool TryExecuteTaskInline(Task task, bool taskWasPreviouslyQueued)
    {
        return Thread.CurrentThread.Name?.StartsWith("PriorityWorker") == true && 
               TryExecuteTask(task);
    }
}
```

### 2. SYSTEMDPISYSTEM
```csharp
// UI/HighDpiManager.cs
using System;
using System.Drawing;
using System.Windows.Forms;
using System.Runtime.InteropServices;

public static class HighDpiManager
{
    // Per-Monitor DPI Awareness V2
    [DllImport("user32.dll")]
    private static extern bool SetProcessDpiAwarenessContext(IntPtr value);
    
    [DllImport("user32.dll")]
    private static extern uint GetDpiForWindow(IntPtr hWnd);
    
    private const int DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4;
    
    public static void EnableHighDpiSupport()
    {
        // 
        SetProcessDpiAwarenessContext(new IntPtr(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2));
        
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        
        // DPI
        Application.SetDefaultFont(new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point));
    }
    
    // DPI
    public class DpiAwareControl : UserControl
    {
        private float _currentDpi = 96f;
        private float _designTimeDpi = 96f;
        
        protected override void OnDpiChangedAfterParent(EventArgs e)
        {
            base.OnDpiChangedAfterParent(e);
            
            var newDpi = GetDpiForWindow(Handle);
            var scaleFactor = newDpi / _currentDpi;
            
            ScaleControl(scaleFactor);
            _currentDpi = newDpi;
        }
        
        private void ScaleControl(float scaleFactor)
        {
            // 
            Font = new Font(Font.FontFamily, Font.Size * scaleFactor, Font.Style);
            
            // 
            ScaleImages(scaleFactor);
            
            // 
            InvalidateCustomDrawing();
        }
        
        private void ScaleImages(float scaleFactor)
        {
            // 
            var dpiSuffix = GetDpiSuffix(_currentDpi);
            
            foreach (Control control in Controls)
            {
                if (control is PictureBox pictureBox)
                {
                    var imagePath = pictureBox.Tag as string;
                    if (!string.IsNullOrEmpty(imagePath))
                    {
                        // DPI
                        var scaledImagePath = imagePath.Replace(".png", $"{dpiSuffix}.png");
                        if (File.Exists(scaledImagePath))
                        {
                            pictureBox.Image = Image.FromFile(scaledImagePath);
                        }
                    }
                }
            }
        }
        
        private string GetDpiSuffix(float dpi)
        {
            if (dpi <= 96) return "";
            if (dpi <= 120) return "@1.25x";
            if (dpi <= 144) return "@1.5x";
            if (dpi <= 192) return "@2x";
            return "@3x";
        }
    }
}

// WPFCONFIGDPICONFIG
public class WpfHighDpiHelper
{
    public static void ConfigureWpfDpiAwareness()
    {
        // app.manifest CONFIG
        // <application xmlns="urn:schemas-microsoft-com:asm.v3">
        //   <windowsSettings>
        //     <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
        //     <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/PM</dpiAware>
        //   </windowsSettings>
        // </application>
        
        // CONFIG
        var dpiScale = VisualTreeHelper.GetDpi(Application.Current.MainWindow);
        
        // SYSTEM
        Application.Current.Resources["GlobalFontSize"] = 14 * dpiScale.DpiScaleX;
        Application.Current.Resources["IconSize"] = 24 * dpiScale.DpiScaleX;
    }
}
```

### 3. SYSTEMGCSYSTEM
```csharp
// Performance/MemoryOptimizer.cs
using System;
using System.Runtime;
using System.Runtime.CompilerServices;
using System.Buffers;

public class MemoryOptimizer
{
    // ArrayPool SYSTEM
    private readonly ArrayPool<byte> _arrayPool = ArrayPool<byte>.Shared;
    
    public MemoryOptimizer()
    {
        ConfigureGarbageCollection();
    }
    
    private void ConfigureGarbageCollection()
    {
        // CONFIGGCCONFIGapp.config CONFIG
        GCSettings.IsServerGC = true;
        
        // CONFIG
        GCSettings.LargeObjectHeapCompactionMode = GCLargeObjectHeapCompactionMode.CompactOnce;
        
        // CONFIGGCCONFIG
        GCSettings.LatencyMode = GCLatencyMode.SustainedLowLatency;
    }
    
    // Span<T> CONFIG
    public void ProcessLargeData(ReadOnlySpan<byte> data)
    {
        const int ChunkSize = 4096;
        
        for (int i = 0; i < data.Length; i += ChunkSize)
        {
            var chunk = data.Slice(i, Math.Min(ChunkSize, data.Length - i));
            ProcessChunk(chunk);
        }
    }
    
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    private void ProcessChunk(ReadOnlySpan<byte> chunk)
    {
        // 
        Span<byte> buffer = stackalloc byte[256];
        
        // 
        for (int i = 0; i < chunk.Length && i < buffer.Length; i++)
        {
            buffer[i] = (byte)(chunk[i] ^ 0xFF);
        }
    }
    
    // 
    public class ObjectPool<T> where T : class, new()
    {
        private readonly ConcurrentBag<T> _objects = new();
        private readonly Func<T> _objectGenerator;
        private readonly Action<T> _resetAction;
        
        public ObjectPool(Func<T> objectGenerator = null, Action<T> resetAction = null)
        {
            _objectGenerator = objectGenerator ?? (() => new T());
            _resetAction = resetAction ?? (obj => { });
        }
        
        public T Rent()
        {
            if (_objects.TryTake(out T item))
            {
                return item;
            }
            
            return _objectGenerator();
        }
        
        public void Return(T item)
        {
            _resetAction(item);
            _objects.Add(item);
        }
    }
    
    // WeakReference 
    public class WeakCache<TKey, TValue> where TValue : class
    {
        private readonly Dictionary<TKey, WeakReference> _cache = new();
        
        public bool TryGetValue(TKey key, out TValue value)
        {
            if (_cache.TryGetValue(key, out var weakRef) && weakRef.IsAlive)
            {
                value = (TValue)weakRef.Target;
                return value != null;
            }
            
            value = null;
            return false;
        }
        
        public void Add(TKey key, TValue value)
        {
            _cache[key] = new WeakReference(value);
        }
        
        public void Cleanup()
        {
            var deadKeys = _cache
                .Where(kvp => !kvp.Value.IsAlive)
                .Select(kvp => kvp.Key)
                .ToList();
            
            foreach (var key in deadKeys)
            {
                _cache.Remove(key);
            }
        }
    }
}
```

### 4. SYSTEM
```csharp
// Security/SecurityHardening.cs
using System;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Security.Principal;

public class SecurityHardening
{
    // SYSTEM
    public static bool VerifyCodeSignature(string assemblyPath)
    {
        try
        {
            var cert = X509Certificate.CreateFromSignedFile(assemblyPath);
            var cert2 = new X509Certificate2(cert);
            
            // 
            var chain = new X509Chain
            {
                ChainPolicy = new X509ChainPolicy
                {
                    RevocationMode = X509RevocationMode.Online,
                    RevocationFlag = X509RevocationFlag.EntireChain,
                    UrlRetrievalTimeout = new TimeSpan(0, 0, 30),
                    VerificationFlags = X509VerificationFlags.NoFlag
                }
            };
            
            return chain.Build(cert2);
        }
        catch
        {
            return false;
        }
    }
    
    // API (DPAPI) 
    public class SecureDataStorage
    {
        private readonly byte[] _entropy;
        
        public SecureDataStorage()
        {
            // 
            _entropy = new byte[32];
            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(_entropy);
            }
        }
        
        public byte[] Protect(byte[] userData)
        {
            return ProtectedData.Protect(
                userData,
                _entropy,
                DataProtectionScope.CurrentUser
            );
        }
        
        public byte[] Unprotect(byte[] protectedData)
        {
            return ProtectedData.Unprotect(
                protectedData,
                _entropy,
                DataProtectionScope.CurrentUser
            );
        }
    }
    
    // Windows
    public class WindowsAuthenticationHelper
    {
        public static bool IsUserInRole(string role)
        {
            var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            return principal.IsInRole(role);
        }
        
        public static string GetCurrentUserInfo()
        {
            var identity = WindowsIdentity.GetCurrent();
            return $"User: {identity.Name}, Auth: {identity.AuthenticationType}, " +
                   $"IsAuthenticated: {identity.IsAuthenticated}";
        }
        
        // Active Directory 
        public static bool IsInActiveDirectoryGroup(string groupName)
        {
            var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            
            var sid = new SecurityIdentifier(WellKnownSidType.BuiltinUsersSid, null);
            return principal.IsInRole(sid);
        }
    }
}
```

### 5. 
```xml
<!-- ClickOnce  app.manifest -->
<?xml version="1.0" encoding="utf-8"?>
<assembly manifestVersion="1.0" xmlns="urn:schemas-microsoft-com:asm.v1">
  <assemblyIdentity version="1.0.0.0" name="EnterpriseApp.app"/>
  
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v2">
    <security>
      <requestedPrivileges xmlns="urn:schemas-microsoft-com:asm.v3">
        <requestedExecutionLevel level="asInvoker" uiAccess="false" />
      </requestedPrivileges>
    </security>
  </trustInfo>
  
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10/11 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}" />
    </application>
  </compatibility>
  
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/PM</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
      <longPathAware xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">true</longPathAware>
    </windowsSettings>
  </application>
</assembly>
```

```csharp
// Deployment/ClickOnceHelper.cs
public class ClickOnceHelper
{
    public static void ConfigureAutoUpdate()
    {
        if (ApplicationDeployment.IsNetworkDeployed)
        {
            var deployment = ApplicationDeployment.CurrentDeployment;
            
            // SUCCESS
            deployment.CheckForUpdateCompleted += (sender, e) =>
            {
                if (e.UpdateAvailable)
                {
                    MessageBox.Show("");
                    
                    deployment.UpdateAsync();
                }
            };
            
            // ANALYSIS
            deployment.CheckForUpdateAsync();
        }
    }
    
    // MSIX ANALYSIS
    public static void PrepareMsixPackage()
    {
        // Package.appxmanifest 
        // :
        // <PropertyGroup>
        //   <WindowsPackageType>MSIX</WindowsPackageType>
        //   <AppxAutoIncrementPackageRevision>True</AppxAutoIncrementPackageRevision>
        //   <AppxSymbolPackageEnabled>True</AppxSymbolPackageEnabled>
        // </PropertyGroup>
    }
}
```

## TASK
```markdown
# .NET Framework 4.8 TASK

## TASK
[OK] TASK: async/awaitTASK
[OK] TASKDPITASK: Per-Monitor V2TASK
[OK] : GCSpan<T>
[OK] : DPAPI
[OK] : ClickOnce/MSIX

## 
- : 3.2 -> 0.8 (75%)
- : 250MB -> 95MB (62%)
- UI: 60fps
- GC: 50ms -> 5ms (90%)

## 
- : 
- : DPAPI
- Windows: AD
- : 

## 
1. .NET 5/6
2. AOT TASK
3. Application InsightsTASK
```

## TASK
- **TASK**: TASK
- **TASK**: .NET Framework 4.8 TASK

---
*TASK.NET Framework 4.8TASK*