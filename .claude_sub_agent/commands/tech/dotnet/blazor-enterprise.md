# /blazor-enterprise - Blazor エンタープライズ専用コマンド

## 概要
Blazor United（.NET 8）、Blazor Server、Blazor WebAssembly、Blazor Hybridのすべてのホスティングモデルに対応した包括的な開発コマンドです。各バージョンの特性を活かしたエンタープライズグレードの実装を提供します。

## バージョンとホスティングモデル検出
```csharp
// プロジェクトファイルから自動検出
#if NET8_0_OR_GREATER
    // Blazor United - SSR + Interactive
    builder.Services.AddRazorComponents()
        .AddInteractiveServerComponents()
        .AddInteractiveWebAssemblyComponents();
#elif NET7_0
    // Blazor Server or WASM
    builder.Services.AddServerSideBlazor();
#elif NET6_0
    // Blazor Server or WASM
    builder.Services.AddRazorPages();
    builder.Services.AddServerSideBlazor();
#endif
```

## Blazor United（.NET 8）- 統合レンダリングモード

### 1. Blazor United アプリケーション構成
```csharp
// Program.cs - Blazor United with .NET 8
using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Web;

var builder = WebApplication.CreateBuilder(args);

// Add Blazor services with United rendering
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents()
    .AddInteractiveWebAssemblyComponents();

// Authentication and Authorization
builder.Services.AddAuthentication(options =>
    {
        options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
        options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;
    })
    .AddCookie()
    .AddOpenIdConnect(options =>
    {
        options.Authority = builder.Configuration["Auth:Authority"];
        options.ClientId = builder.Configuration["Auth:ClientId"];
        options.ClientSecret = builder.Configuration["Auth:ClientSecret"];
        options.ResponseType = "code";
        options.SaveTokens = true;
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
    options.AddPolicy("Premium", policy => policy.RequireClaim("subscription", "premium"));
});

// State management
builder.Services.AddScoped<IStateContainer, StateContainer>();
builder.Services.AddSingleton<IAppState, AppState>();

// Business services
builder.Services.AddScoped<ICustomerService, CustomerService>();
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddScoped<IReportingService, ReportingService>();

// Real-time features
builder.Services.AddSignalR(options =>
{
    options.EnableDetailedErrors = builder.Environment.IsDevelopment();
    options.MaximumReceiveMessageSize = 1024 * 1024; // 1MB
});

// Caching
builder.Services.AddMemoryCache();
builder.Services.AddDistributedMemoryCache();

// HTTP client configuration
builder.Services.AddHttpClient("API", client =>
{
    client.BaseAddress = new Uri(builder.Configuration["API:BaseUrl"]);
    client.DefaultRequestHeaders.Add("Accept", "application/json");
})
.AddPolicyHandler(GetRetryPolicy())
.AddPolicyHandler(GetCircuitBreakerPolicy());

var app = builder.Build();

// Configure pipeline
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseAntiforgery();

app.UseAuthentication();
app.UseAuthorization();

// Map Blazor components with render modes
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode()
    .AddInteractiveWebAssemblyRenderMode()
    .AddAdditionalAssemblies(typeof(ClientAssembly).Assembly);

// Map SignalR hubs
app.MapHub<NotificationHub>("/notifications");
app.MapHub<DataSyncHub>("/datasync");

app.Run();

// Components/App.razor - Root component with render mode selection
@page "/"
@rendermode InteractiveAuto

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Enterprise Blazor App</title>
    <base href="/" />
    <link rel="stylesheet" href="css/bootstrap/bootstrap.min.css" />
    <link rel="stylesheet" href="css/app.css" />
    <HeadOutlet @rendermode="@InteractiveAuto" />
</head>
<body>
    <Routes @rendermode="@InteractiveAuto" />
    <script src="_framework/blazor.web.js"></script>
</body>
</html>

// Components/Pages/Dashboard.razor - Interactive component with streaming
@page "/dashboard"
@attribute [StreamRendering]
@attribute [Authorize(Policy = "Premium")]
@rendermode InteractiveServer

<PageTitle>Dashboard</PageTitle>

<div class="dashboard-container">
    @if (IsLoading)
    {
        <LoadingSpinner />
    }
    else
    {
        <div class="row">
            <div class="col-md-3">
                <MetricCard Title="Total Sales" 
                           Value="@TotalSales.ToString("C")" 
                           Change="@SalesChange"
                           Icon="trending_up" />
            </div>
            <div class="col-md-3">
                <MetricCard Title="Active Users" 
                           Value="@ActiveUsers.ToString("N0")"
                           Change="@UserChange"
                           Icon="people" />
            </div>
            <div class="col-md-3">
                <MetricCard Title="Orders Today"
                           Value="@OrdersToday.ToString("N0")"
                           Change="@OrderChange"
                           Icon="shopping_cart" />
            </div>
            <div class="col-md-3">
                <MetricCard Title="Performance"
                           Value="@Performance.ToString("P")"
                           Change="@PerfChange"
                           Icon="speed" />
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-8">
                <ChartComponent @ref="chartComponent" 
                               Data="@ChartData"
                               Type="ChartType.Line"
                               Options="@ChartOptions" />
            </div>
            <div class="col-md-4">
                <RecentActivityList Activities="@RecentActivities" />
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <DataGrid TItem="Order"
                         Items="@Orders"
                         Virtualize="true"
                         PageSize="20"
                         AllowSorting="true"
                         AllowFiltering="true"
                         @bind-SelectedItem="@SelectedOrder">
                    <Columns>
                        <DataGridColumn Field="@nameof(Order.Id)" Title="Order ID" />
                        <DataGridColumn Field="@nameof(Order.CustomerName)" Title="Customer" />
                        <DataGridColumn Field="@nameof(Order.OrderDate)" Title="Date" Format="yyyy-MM-dd" />
                        <DataGridColumn Field="@nameof(Order.Total)" Title="Total" Format="C" />
                        <DataGridColumn Field="@nameof(Order.Status)" Title="Status">
                            <Template Context="order">
                                <StatusBadge Status="@order.Status" />
                            </Template>
                        </DataGridColumn>
                        <DataGridColumn Title="Actions">
                            <Template Context="order">
                                <button class="btn btn-sm btn-primary" 
                                        @onclick="() => ViewOrderDetails(order)">
                                    View
                                </button>
                            </Template>
                        </DataGridColumn>
                    </Columns>
                </DataGrid>
            </div>
        </div>
    }
</div>

@code {
    [Inject] private IOrderService OrderService { get; set; } = default!;
    [Inject] private IMetricsService MetricsService { get; set; } = default!;
    [Inject] private NavigationManager Navigation { get; set; } = default!;
    [Inject] private IJSRuntime JS { get; set; } = default!;
    [CascadingParameter] private Task<AuthenticationState> AuthState { get; set; } = default!;
    
    private bool IsLoading = true;
    private decimal TotalSales;
    private int ActiveUsers;
    private int OrdersToday;
    private double Performance;
    private List<Order> Orders = new();
    private Order? SelectedOrder;
    private ChartComponent chartComponent = default!;
    
    protected override async Task OnInitializedAsync()
    {
        // Stream data as it becomes available
        await foreach (var metrics in MetricsService.GetMetricsStreamAsync())
        {
            TotalSales = metrics.TotalSales;
            ActiveUsers = metrics.ActiveUsers;
            OrdersToday = metrics.OrdersToday;
            Performance = metrics.Performance;
            
            StateHasChanged(); // Update UI with streamed data
            
            if (!IsLoading) break;
            IsLoading = false;
        }
        
        // Load orders
        Orders = await OrderService.GetRecentOrdersAsync();
    }
    
    private async Task ViewOrderDetails(Order order)
    {
        // Navigate with state
        Navigation.NavigateTo($"/orders/{order.Id}", 
            new NavigationOptions { ReplaceHistoryEntry = false });
    }
}
```

### 2. Blazor Server 最適化（.NET 6/7）
```csharp
// Blazor Server with optimized circuits
// Program.cs
builder.Services.AddServerSideBlazor(options =>
{
    options.DetailedErrors = builder.Environment.IsDevelopment();
    options.DisconnectedCircuitRetentionPeriod = TimeSpan.FromMinutes(3);
    options.DisconnectedCircuitMaxRetained = 100;
    options.JSInteropDefaultCallTimeout = TimeSpan.FromSeconds(60);
    options.MaxBufferedUnacknowledgedRenderBatches = 10;
});

// Circuit handler for monitoring
public class CircuitHandlerService : CircuitHandler
{
    private readonly ILogger<CircuitHandlerService> _logger;
    private readonly IMetricsCollector _metrics;
    
    public CircuitHandlerService(
        ILogger<CircuitHandlerService> logger,
        IMetricsCollector metrics)
    {
        _logger = logger;
        _metrics = metrics;
    }
    
    public override Task OnConnectionUpAsync(
        Circuit circuit,
        CancellationToken cancellationToken)
    {
        _metrics.IncrementActiveCircuits();
        _logger.LogInformation($"Circuit {circuit.Id} connected");
        return Task.CompletedTask;
    }
    
    public override Task OnConnectionDownAsync(
        Circuit circuit,
        CancellationToken cancellationToken)
    {
        _metrics.DecrementActiveCircuits();
        _logger.LogInformation($"Circuit {circuit.Id} disconnected");
        return Task.CompletedTask;
    }
}

// Components/VirtualizedDataTable.razor - Performance optimized component
@typeparam TItem
@implements IAsyncDisposable

<div class="data-table-container" @ref="containerElement">
    <Virtualize Items="@FilteredItems" 
                ItemSize="40"
                OverscanCount="5"
                @ref="virtualizeComponent">
        <ItemContent>
            <div class="data-row" @key="@GetItemKey(context)">
                @foreach (var column in Columns)
                {
                    <div class="data-cell">
                        @GetCellValue(context, column)
                    </div>
                }
            </div>
        </ItemContent>
        <Placeholder>
            <div class="data-row placeholder">
                <div class="shimmer"></div>
            </div>
        </Placeholder>
    </Virtualize>
</div>

@code {
    [Parameter] public IList<TItem> Items { get; set; } = new List<TItem>();
    [Parameter] public RenderFragment<TItem>? RowTemplate { get; set; }
    [Parameter] public List<ColumnDefinition> Columns { get; set; } = new();
    [Parameter] public Func<TItem, object> GetItemKey { get; set; } = item => item!;
    
    private ElementReference containerElement;
    private Virtualize<TItem>? virtualizeComponent;
    private IList<TItem> FilteredItems = new List<TItem>();
    private DotNetObjectReference<VirtualizedDataTable<TItem>>? dotNetHelper;
    
    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            dotNetHelper = DotNetObjectReference.Create(this);
            await JS.InvokeVoidAsync("initializeDataTable", containerElement, dotNetHelper);
        }
    }
    
    public async ValueTask DisposeAsync()
    {
        if (dotNetHelper != null)
        {
            await JS.InvokeVoidAsync("disposeDataTable", containerElement);
            dotNetHelper.Dispose();
        }
    }
    
    [JSInvokable]
    public async Task RefreshDataAsync()
    {
        if (virtualizeComponent != null)
        {
            await virtualizeComponent.RefreshDataAsync();
            StateHasChanged();
        }
    }
}
```

### 3. Blazor WebAssembly エンタープライズ機能
```csharp
// Client/Program.cs - Blazor WASM with authentication
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using Microsoft.AspNetCore.Components.WebAssembly.Authentication;
using Blazored.LocalStorage;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Authentication with OIDC
builder.Services.AddOidcAuthentication(options =>
{
    builder.Configuration.Bind("Auth", options.ProviderOptions);
    options.ProviderOptions.DefaultScopes.Add("api");
    options.ProviderOptions.ResponseType = "code";
})
.AddAccountClaimsPrincipalFactory<CustomAccountFactory>();

// HTTP clients with authentication
builder.Services.AddHttpClient("API", client =>
{
    client.BaseAddress = new Uri(builder.Configuration["API:BaseUrl"]);
})
.AddHttpMessageHandler<BaseAddressAuthorizationMessageHandler>();

// State management
builder.Services.AddBlazoredLocalStorage();
builder.Services.AddScoped<IStateManager, StateManager>();

// Offline support with service worker
builder.Services.AddScoped<IOfflineService, OfflineService>();

await builder.Build().RunAsync();

// Services/StateManager.cs - Client-side state management
public class StateManager : IStateManager
{
    private readonly ILocalStorageService _localStorage;
    private readonly Dictionary<string, object> _memoryCache = new();
    private readonly Dictionary<string, List<Action>> _subscribers = new();
    
    public StateManager(ILocalStorageService localStorage)
    {
        _localStorage = localStorage;
    }
    
    public async Task<T?> GetStateAsync<T>(string key)
    {
        // Check memory cache first
        if (_memoryCache.TryGetValue(key, out var cached))
        {
            return (T)cached;
        }
        
        // Check local storage
        if (await _localStorage.ContainKeyAsync(key))
        {
            var value = await _localStorage.GetItemAsync<T>(key);
            _memoryCache[key] = value!;
            return value;
        }
        
        return default;
    }
    
    public async Task SetStateAsync<T>(string key, T value)
    {
        _memoryCache[key] = value!;
        await _localStorage.SetItemAsync(key, value);
        
        // Notify subscribers
        if (_subscribers.TryGetValue(key, out var callbacks))
        {
            foreach (var callback in callbacks)
            {
                callback.Invoke();
            }
        }
    }
    
    public void Subscribe(string key, Action callback)
    {
        if (!_subscribers.ContainsKey(key))
        {
            _subscribers[key] = new List<Action>();
        }
        _subscribers[key].Add(callback);
    }
    
    public async Task<bool> SyncWithServerAsync()
    {
        try
        {
            var pendingChanges = await _localStorage.GetItemAsync<List<PendingChange>>("pending_changes");
            if (pendingChanges?.Any() == true)
            {
                // Send to server
                foreach (var change in pendingChanges)
                {
                    await ApplyChangeToServerAsync(change);
                }
                
                // Clear pending changes
                await _localStorage.RemoveItemAsync("pending_changes");
            }
            return true;
        }
        catch
        {
            return false;
        }
    }
}

// Components/OfflineIndicator.razor - PWA offline support
@implements IDisposable
@inject IOfflineService OfflineService
@inject IJSRuntime JS

<div class="offline-indicator @(IsOffline ? "show" : "hide")">
    <i class="bi bi-wifi-off"></i>
    <span>オフラインモード - データは自動的に同期されます</span>
</div>

@code {
    private bool IsOffline;
    private DotNetObjectReference<OfflineIndicator>? dotNetHelper;
    
    protected override async Task OnInitializedAsync()
    {
        dotNetHelper = DotNetObjectReference.Create(this);
        await JS.InvokeVoidAsync("registerOfflineHandler", dotNetHelper);
        
        IsOffline = !await OfflineService.IsOnlineAsync();
    }
    
    [JSInvokable]
    public void UpdateOnlineStatus(bool isOnline)
    {
        IsOffline = !isOnline;
        InvokeAsync(StateHasChanged);
        
        if (isOnline)
        {
            // Sync pending changes when coming back online
            _ = OfflineService.SyncPendingChangesAsync();
        }
    }
    
    public void Dispose()
    {
        dotNetHelper?.Dispose();
    }
}
```

### 4. Blazor Hybrid（MAUI/WPF/Windows Forms）
```csharp
// Platforms/Windows/MauiProgram.cs - Blazor Hybrid with MAUI
public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
            });

        // Add Blazor WebView
        builder.Services.AddMauiBlazorWebView();
        
#if DEBUG
        builder.Services.AddBlazorWebViewDeveloperTools();
#endif
        
        // Platform-specific services
        builder.Services.AddSingleton<IDeviceService, DeviceService>();
        builder.Services.AddSingleton<IFileService, FileService>();
        builder.Services.AddSingleton<IBiometricService, BiometricService>();
        
        // Database (SQLite)
        var dbPath = Path.Combine(FileSystem.AppDataDirectory, "app.db");
        builder.Services.AddDbContext<AppDbContext>(options =>
            options.UseSqlite($"Data Source={dbPath}"));
        
        return builder.Build();
    }
}

// Services/DeviceService.cs - Platform-specific functionality
public class DeviceService : IDeviceService
{
    public async Task<string> GetDeviceIdAsync()
    {
        return DeviceInfo.Current.Idiom == DeviceIdiom.Phone
            ? await SecureStorage.GetAsync("device_id") ?? Guid.NewGuid().ToString()
            : Environment.MachineName;
    }
    
    public async Task<bool> AuthenticateWithBiometricsAsync()
    {
        var request = new BiometricAuthenticationRequest
        {
            Title = "認証が必要です",
            Subtitle = "指紋またはFace IDで認証してください",
            Description = "セキュアなデータにアクセスするため",
            FallbackTitle = "パスコードを使用"
        };
        
        var result = await BiometricAuthentication.AuthenticateAsync(request);
        return result.Status == BiometricAuthenticationStatus.Succeeded;
    }
    
    public async Task<byte[]> TakePhotoAsync()
    {
        if (MediaPicker.Default.IsCaptureSupported)
        {
            var photo = await MediaPicker.Default.CapturePhotoAsync();
            if (photo != null)
            {
                using var stream = await photo.OpenReadAsync();
                using var memoryStream = new MemoryStream();
                await stream.CopyToAsync(memoryStream);
                return memoryStream.ToArray();
            }
        }
        return Array.Empty<byte>();
    }
}

// Pages/HybridFeatures.razor - Using platform features in Blazor
@page "/hybrid"
@inject IDeviceService DeviceService
@inject IFileService FileService

<h3>Platform-Specific Features</h3>

<div class="feature-grid">
    <div class="feature-card">
        <h4>Biometric Authentication</h4>
        <button class="btn btn-primary" @onclick="AuthenticateAsync">
            <i class="bi bi-fingerprint"></i> Authenticate
        </button>
        @if (IsAuthenticated)
        {
            <p class="text-success">✓ Authenticated</p>
        }
    </div>
    
    <div class="feature-card">
        <h4>Camera Integration</h4>
        <button class="btn btn-primary" @onclick="TakePhotoAsync">
            <i class="bi bi-camera"></i> Take Photo
        </button>
        @if (PhotoData != null)
        {
            <img src="@GetPhotoUrl()" class="captured-photo" />
        }
    </div>
    
    <div class="feature-card">
        <h4>File System Access</h4>
        <button class="btn btn-primary" @onclick="BrowseFilesAsync">
            <i class="bi bi-folder"></i> Browse Files
        </button>
        @if (SelectedFiles.Any())
        {
            <ul>
                @foreach (var file in SelectedFiles)
                {
                    <li>@file.Name (@file.Size bytes)</li>
                }
            </ul>
        }
    </div>
    
    <div class="feature-card">
        <h4>GPS Location</h4>
        <button class="btn btn-primary" @onclick="GetLocationAsync">
            <i class="bi bi-geo-alt"></i> Get Location
        </button>
        @if (Location != null)
        {
            <p>Lat: @Location.Latitude, Lon: @Location.Longitude</p>
        }
    </div>
</div>

@code {
    private bool IsAuthenticated;
    private byte[]? PhotoData;
    private List<FileInfo> SelectedFiles = new();
    private Location? Location;
    
    private async Task AuthenticateAsync()
    {
        IsAuthenticated = await DeviceService.AuthenticateWithBiometricsAsync();
    }
    
    private async Task TakePhotoAsync()
    {
        PhotoData = await DeviceService.TakePhotoAsync();
    }
    
    private string GetPhotoUrl()
    {
        if (PhotoData != null)
        {
            var base64 = Convert.ToBase64String(PhotoData);
            return $"data:image/jpeg;base64,{base64}";
        }
        return string.Empty;
    }
    
    private async Task GetLocationAsync()
    {
        var request = new GeolocationRequest(GeolocationAccuracy.Medium);
        Location = await Geolocation.GetLocationAsync(request);
    }
}
```

## バージョン別機能対応表

| 機能 | Blazor United (.NET 8) | Blazor Server | Blazor WASM | Blazor Hybrid |
|------|------------------------|---------------|-------------|---------------|
| レンダリングモード | SSR + Interactive | Server-side | Client-side | Native WebView |
| ストリーミングレンダリング | ✅ | ❌ | ❌ | ❌ |
| オフライン動作 | ⚠️ Partial | ❌ | ✅ PWA | ✅ Full |
| 初期読み込み速度 | ⚡ 最速 | ⚡ 高速 | 🐢 遅い | ⚡ 高速 |
| SEO対応 | ✅ Full | ⚠️ Limited | ❌ | N/A |
| リアルタイム更新 | ✅ SignalR | ✅ Built-in | ✅ SignalR | ✅ |
| デバイスアクセス | ❌ | ❌ | ⚠️ Limited | ✅ Full |
| デプロイ複雑度 | 中 | 低 | 低 | 高 |
| スケーラビリティ | ✅ 最高 | ⚠️ 制限あり | ✅ 高 | N/A |

## パフォーマンス最適化

### コンポーネント最適化
```csharp
// ❌ Bad: Unnecessary re-renders
<div @onclick="@(() => counter++)">
    @foreach (var item in GetFilteredItems())
    {
        <ItemComponent Item="@item" />
    }
</div>

// ✅ Good: Optimized with caching and keys
@code {
    private List<Item>? _filteredItems;
    
    private List<Item> FilteredItems => 
        _filteredItems ??= GetFilteredItems();
    
    protected override void OnParametersSet()
    {
        _filteredItems = null; // Reset cache when parameters change
    }
}

<div @onclick="IncrementCounter">
    @foreach (var item in FilteredItems)
    {
        <ItemComponent @key="item.Id" Item="@item" />
    }
</div>
```

### JavaScript Interop最適化
```javascript
// wwwroot/js/blazor-interop.js
window.blazorInterop = {
    // Batch operations to reduce interop calls
    batchUpdate: function (updates) {
        requestAnimationFrame(() => {
            updates.forEach(update => {
                const element = document.getElementById(update.id);
                if (element) {
                    Object.assign(element.style, update.styles);
                }
            });
        });
    },
    
    // Use event delegation instead of individual handlers
    initializeEventDelegation: function (containerid, dotNetHelper) {
        const container = document.getElementById(containerId);
        container.addEventListener('click', async (e) => {
            const target = e.target.closest('[data-action]');
            if (target) {
                await dotNetHelper.invokeMethodAsync('HandleAction', 
                    target.dataset.action, 
                    target.dataset.id);
            }
        });
    }
};
```

## 出力レポート
```markdown
# Blazor エンタープライズ開発レポート

## 実施項目
✅ レンダリングモード: 最適化完了
✅ 認証・認可: 実装済み
✅ 状態管理: 設定完了
✅ リアルタイム機能: SignalR統合
✅ オフライン対応: PWA設定

## パフォーマンス指標
- 初期表示時間: 150ms (Blazor United)
- インタラクティブ時間: 300ms
- メモリ使用量: 25MB (WASM)
- 再レンダリング: 50%削減

## 推奨事項
1. .NET 8 Blazor United採用
2. ストリーミングレンダリング活用
3. コンポーネント仮想化
4. PWAオフライン対応
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: Blazor全ホスティングモデル対応

---
*このコマンドはBlazorの全ホスティングモデルに対応したエンタープライズ開発に特化しています。*