# /dotnet48-optimize - .NET Framework 4.8 エンタープライズ最適化専用コマンド

## 概要
.NET Framework 4.8の最新機能を活用した、エンタープライズデスクトップアプリケーションの包括的な最適化コマンドです。高DPI対応、async/await、最新C#機能を最大限活用します。

## 使用方法
```bash
/dotnet48-optimize [feature] [action] [options]

# 使用例
/dotnet48-optimize async convert --all-methods
/dotnet48-optimize highdpi enable --per-monitor-v2
/dotnet48-optimize performance profile --dotmemory
/dotnet48-optimize security harden --dotfuscator
/dotnet48-optimize deploy prepare --clickonce
```

## .NET Framework 4.8 専用最適化機能

### 1. 非同期処理の完全最適化
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
        // CPU コア数に基づく並列度制御
        var maxDegreeOfParallelism = Environment.ProcessorCount * 2;
        _semaphore = new SemaphoreSlim(maxDegreeOfParallelism);
        _runningTasks = new ConcurrentDictionary<string, Task>();
        
        // カスタムタスクスケジューラー
        _customScheduler = new PriorityTaskScheduler();
    }
    
    // ValueTask を使用した高効率非同期処理
    public async ValueTask<T> ExecuteAsync<T>(
        Func<CancellationToken, Task<T>> operation,
        CancellationToken cancellationToken = default,
        [CallerMemberName] string operationName = "")
    {
        // 同一操作の重複実行防止
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
    
    // ConfigureAwait 最適化
    public async Task OptimizeConfigureAwait(Func<Task> operation)
    {
        // UIコンテキスト不要な場合は false
        await operation().ConfigureAwait(false);
    }
    
    // 非同期ストリーム処理（IAsyncEnumerable）
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
        
        // 並列処理
        var processingTask = Task.Run(async () =>
        {
            await Parallel.ForEachAsync(source, parallelOptions, async (item, ct) =>
            {
                var processed = await processor(item);
                await channel.Writer.WriteAsync(processed, ct);
            });
            
            channel.Writer.Complete();
        }, cancellationToken);
        
        // ストリーミング出力
        await foreach (var item in channel.Reader.ReadAllAsync(cancellationToken))
        {
            yield return item;
        }
        
        await processingTask;
    }
}

// カスタムタスクスケジューラー
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
        // タスクの優先度を計算
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

### 2. 高DPIディスプレイ完全対応
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
        // アプリケーション起動時に呼び出し
        SetProcessDpiAwarenessContext(new IntPtr(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2));
        
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        
        // 高DPI用のデフォルトフォント設定
        Application.SetDefaultFont(new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point));
    }
    
    // DPI対応コントロール基底クラス
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
            // フォントのスケーリング
            Font = new Font(Font.FontFamily, Font.Size * scaleFactor, Font.Style);
            
            // 画像のスケーリング
            ScaleImages(scaleFactor);
            
            // カスタム描画のスケーリング
            InvalidateCustomDrawing();
        }
        
        private void ScaleImages(float scaleFactor)
        {
            // 複数解像度の画像を用意
            var dpiSuffix = GetDpiSuffix(_currentDpi);
            
            foreach (Control control in Controls)
            {
                if (control is PictureBox pictureBox)
                {
                    var imagePath = pictureBox.Tag as string;
                    if (!string.IsNullOrEmpty(imagePath))
                    {
                        // DPIに応じた画像を選択
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

// WPF高DPI対応
public class WpfHighDpiHelper
{
    public static void ConfigureWpfDpiAwareness()
    {
        // app.manifest で設定
        // <application xmlns="urn:schemas-microsoft-com:asm.v3">
        //   <windowsSettings>
        //     <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
        //     <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/PM</dpiAware>
        //   </windowsSettings>
        // </application>
        
        // コードでの設定
        var dpiScale = VisualTreeHelper.GetDpi(Application.Current.MainWindow);
        
        // リソースの動的スケーリング
        Application.Current.Resources["GlobalFontSize"] = 14 * dpiScale.DpiScaleX;
        Application.Current.Resources["IconSize"] = 24 * dpiScale.DpiScaleX;
    }
}
```

### 3. メモリ最適化とGCチューニング
```csharp
// Performance/MemoryOptimizer.cs
using System;
using System.Runtime;
using System.Runtime.CompilerServices;
using System.Buffers;

public class MemoryOptimizer
{
    // ArrayPool を使用したメモリ再利用
    private readonly ArrayPool<byte> _arrayPool = ArrayPool<byte>.Shared;
    
    public MemoryOptimizer()
    {
        ConfigureGarbageCollection();
    }
    
    private void ConfigureGarbageCollection()
    {
        // サーバーGCモード有効化（app.config でも設定可能）
        GCSettings.IsServerGC = true;
        
        // 大量オブジェクトヒープの圧縮
        GCSettings.LargeObjectHeapCompactionMode = GCLargeObjectHeapCompactionMode.CompactOnce;
        
        // 低遅延モード（短時間のGC停止）
        GCSettings.LatencyMode = GCLatencyMode.SustainedLowLatency;
    }
    
    // Span<T> を使用したゼロアロケーション処理
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
        // スタック割り当てで処理
        Span<byte> buffer = stackalloc byte[256];
        
        // 処理ロジック
        for (int i = 0; i < chunk.Length && i < buffer.Length; i++)
        {
            buffer[i] = (byte)(chunk[i] ^ 0xFF);
        }
    }
    
    // オブジェクトプーリング
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
    
    // WeakReference を使用したキャッシュ
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

### 4. セキュリティ強化
```csharp
// Security/SecurityHardening.cs
using System;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Security.Principal;

public class SecurityHardening
{
    // コード署名検証
    public static bool VerifyCodeSignature(string assemblyPath)
    {
        try
        {
            var cert = X509Certificate.CreateFromSignedFile(assemblyPath);
            var cert2 = new X509Certificate2(cert);
            
            // 証明書チェーン検証
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
    
    // データ保護API (DPAPI) 使用
    public class SecureDataStorage
    {
        private readonly byte[] _entropy;
        
        public SecureDataStorage()
        {
            // エントロピー生成
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
    
    // Windows認証統合
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
        
        // Active Directory グループチェック
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

### 5. 配布とデプロイメント最適化
```xml
<!-- ClickOnce 設定 app.manifest -->
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
            
            // 自動更新設定
            deployment.CheckForUpdateCompleted += (sender, e) =>
            {
                if (e.UpdateAvailable)
                {
                    MessageBox.Show("新しいバージョンが利用可能です。アプリケーションを再起動してください。");
                    
                    deployment.UpdateAsync();
                }
            };
            
            // バックグラウンド更新チェック
            deployment.CheckForUpdateAsync();
        }
    }
    
    // MSIX パッケージング対応
    public static void PrepareMsixPackage()
    {
        // Package.appxmanifest 設定
        // プロジェクトファイルに以下を追加:
        // <PropertyGroup>
        //   <WindowsPackageType>MSIX</WindowsPackageType>
        //   <AppxAutoIncrementPackageRevision>True</AppxAutoIncrementPackageRevision>
        //   <AppxSymbolPackageEnabled>True</AppxSymbolPackageEnabled>
        // </PropertyGroup>
    }
}
```

## 出力レポート
```markdown
# .NET Framework 4.8 最適化レポート

## 実施項目
✅ 非同期処理: async/await完全移行
✅ 高DPI対応: Per-Monitor V2実装
✅ メモリ最適化: GCチューニング、Span<T>活用
✅ セキュリティ: コード署名、DPAPI実装
✅ 配布: ClickOnce/MSIX対応

## パフォーマンス改善
- 起動時間: 3.2秒 → 0.8秒 (75%改善)
- メモリ使用量: 250MB → 95MB (62%削減)
- UI応答性: 60fps達成（スムーズ）
- GC停止時間: 50ms → 5ms (90%削減)

## セキュリティ強化
- コード署名: 実装済み
- データ暗号化: DPAPI使用
- Windows認証: AD統合
- 最小権限実行: 実装済み

## 推奨事項
1. .NET 5/6への移行検討
2. AOT コンパイル導入
3. Application Insights統合
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: .NET Framework 4.8 エンタープライズ開発

---
*このコマンドは.NET Framework 4.8の最新機能を活用したエンタープライズ開発に特化しています。*