# /maui-mobile - MAUI/Xamarin モバイル専用コマンド

## 概要
.NET MAUI（.NET 6+）とXamarin.Forms（レガシー）の両方に対応したクロスプラットフォームモバイル開発専用コマンドです。iOS、Android、Windows、macOSに対応したエンタープライズグレードのモバイルアプリケーション開発を支援します。

## バージョン検出と自動選択
```csharp
// プロジェクトファイルから自動検出
#if NET8_0_OR_GREATER
    // .NET MAUI with latest features
    <UseMaui>true</UseMaui>
    <SingleProject>true</SingleProject>
#elif NET7_0 || NET6_0
    // .NET MAUI initial versions
    <UseMaui>true</UseMaui>
#else
    // Xamarin.Forms (legacy)
    <PackageReference Include="Xamarin.Forms" Version="5.0.0.2612" />
#endif
```

## .NET MAUI エンタープライズ実装（.NET 8）

### 1. プロジェクト構成とプラットフォーム固有実装
```csharp
// MauiProgram.cs - Enterprise MAUI configuration
using Microsoft.Extensions.Logging;
using CommunityToolkit.Maui;
using SkiaSharp.Views.Maui.Controls.Hosting;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseMauiCommunityToolkit()
            .UseSkiaSharp()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
                fonts.AddFont("NotoSansJP-Regular.ttf", "NotoSansJP");
                fonts.AddFont("MaterialIcons-Regular.ttf", "MaterialIcons");
            })
            .ConfigureEssentials(essentials =>
            {
                essentials.UseVersionTracking();
                essentials.UseMapServiceToken("YOUR_MAP_TOKEN");
            })
            .ConfigureLifecycleEvents(events =>
            {
#if ANDROID
                events.AddAndroid(android => android
                    .OnActivityResult((activity, requestCode, resultCode, data) => 
                        LogEvent("ActivityResult"))
                    .OnBackPressed((activity) => LogEvent("BackPressed"))
                    .OnCreate((activity, bundle) => LogEvent("Created"))
                    .OnDestroy((activity) => LogEvent("Destroyed"))
                    .OnPause((activity) => LogEvent("Paused"))
                    .OnResume((activity) => LogEvent("Resumed")));
#elif IOS || MACCATALYST
                events.AddiOS(ios => ios
                    .OnActivated((app) => LogEvent("Activated"))
                    .OnResignActivation((app) => LogEvent("ResignActivation"))
                    .DidEnterBackground((app) => LogEvent("DidEnterBackground"))
                    .WillEnterForeground((app) => LogEvent("WillEnterForeground"))
                    .WillTerminate((app) => LogEvent("WillTerminate")));
#elif WINDOWS
                events.AddWindows(windows => windows
                    .OnActivated((window, args) => LogEvent("Activated"))
                    .OnClosed((window, args) => LogEvent("Closed"))
                    .OnLaunched((window, args) => LogEvent("Launched"))
                    .OnLaunching((window, args) => LogEvent("Launching"))
                    .OnVisibilityChanged((window, args) => LogEvent("VisibilityChanged")));
#endif
            });

        // Dependency Injection
        ConfigureServices(builder.Services);
        
        // Logging
#if DEBUG
        builder.Logging.AddDebug();
        builder.Services.AddBlazorWebViewDeveloperTools();
#endif
        
        return builder.Build();
    }
    
    private static void ConfigureServices(IServiceCollection services)
    {
        // Platform services
        services.AddSingleton<IConnectivity>(Connectivity.Current);
        services.AddSingleton<IGeolocation>(Geolocation.Default);
        services.AddSingleton<IMap>(Map.Default);
        services.AddSingleton<IDeviceInfo>(DeviceInfo.Current);
        services.AddSingleton<IDeviceDisplay>(DeviceDisplay.Current);
        
        // Custom services
        services.AddSingleton<INavigationService, NavigationService>();
        services.AddSingleton<IDataService, DataService>();
        services.AddSingleton<IAuthenticationService, AuthenticationService>();
        services.AddSingleton<IPushNotificationService, PushNotificationService>();
        services.AddSingleton<IOfflineDataSync, OfflineDataSync>();
        
        // Database
        var dbPath = Path.Combine(FileSystem.AppDataDirectory, "app.db3");
        services.AddSingleton<IDatabase>(s => 
            ActivatorUtilities.CreateInstance<SqliteDatabase>(s, dbPath));
        
        // ViewModels
        services.AddTransient<MainViewModel>();
        services.AddTransient<LoginViewModel>();
        services.AddTransient<CustomerListViewModel>();
        services.AddTransient<CustomerDetailViewModel>();
        
        // Pages
        services.AddTransient<MainPage>();
        services.AddTransient<LoginPage>();
        services.AddTransient<CustomerListPage>();
        services.AddTransient<CustomerDetailPage>();
        
        // HttpClient with Polly
        services.AddHttpClient<IApiService, ApiService>(client =>
        {
            client.BaseAddress = new Uri(AppSettings.ApiBaseUrl);
            client.DefaultRequestHeaders.Add("Accept", "application/json");
        })
        .AddPolicyHandler(GetRetryPolicy())
        .AddPolicyHandler(GetCircuitBreakerPolicy());
    }
    
    private static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy()
    {
        return HttpPolicyExtensions
            .HandleTransientHttpError()
            .OrResult(msg => !msg.IsSuccessStatusCode)
            .WaitAndRetryAsync(
                3,
                retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                onRetry: (outcome, timespan, retryCount, context) =>
                {
                    Debug.WriteLine($"Retry {retryCount} after {timespan} seconds");
                });
    }
    
    private static void LogEvent(string eventName)
    {
        Debug.WriteLine($"Lifecycle event: {eventName}");
    }
}

// App.xaml.cs - Application with dependency injection
public partial class App : Application
{
    private readonly IServiceProvider _serviceProvider;
    private readonly INavigationService _navigationService;
    
    public App(IServiceProvider serviceProvider)
    {
        InitializeComponent();
        
        _serviceProvider = serviceProvider;
        _navigationService = serviceProvider.GetRequiredService<INavigationService>();
        
        // Theme management
        UserAppTheme = AppTheme.Unspecified;
        
        // Set main page based on authentication state
        var authService = serviceProvider.GetRequiredService<IAuthenticationService>();
        
        if (authService.IsAuthenticated)
        {
            MainPage = new AppShell();
        }
        else
        {
            MainPage = new NavigationPage(serviceProvider.GetRequiredService<LoginPage>());
        }
    }
    
    protected override async void OnStart()
    {
        // Handle app start
        await CheckForUpdatesAsync();
        await RegisterForPushNotificationsAsync();
    }
    
    protected override void OnSleep()
    {
        // Handle app sleep
        _serviceProvider.GetRequiredService<IOfflineDataSync>().SavePendingChanges();
    }
    
    protected override void OnResume()
    {
        // Handle app resume
        _ = _serviceProvider.GetRequiredService<IOfflineDataSync>().SyncAsync();
    }
}
```

### 2. プラットフォーム固有機能の実装
```csharp
// Platforms/Android/MainActivity.cs
[Activity(
    Theme = "@style/Maui.SplashTheme",
    MainLauncher = true,
    ConfigurationChanges = ConfigChanges.ScreenSize | ConfigChanges.Orientation | ConfigChanges.UiMode | ConfigChanges.ScreenLayout | ConfigChanges.SmallestScreenSize | ConfigChanges.Density)]
[IntentFilter(new[] { Intent.ActionView },
    Categories = new[] { Intent.CategoryDefault, Intent.CategoryBrowsable },
    DataScheme = "myapp")]
public class MainActivity : MauiAppCompatActivity
{
    protected override void OnCreate(Bundle savedInstanceState)
    {
        base.OnCreate(savedInstanceState);
        
        // Permissions
        Platform.Init(this, savedInstanceState);
        
        // Push notifications
        CreateNotificationChannel();
        
        // Deep linking
        HandleIntent(Intent);
    }
    
    public override void OnRequestPermissionsResult(int requestCode, string[] permissions, Permission[] grantResults)
    {
        Platform.OnRequestPermissionsResult(requestCode, permissions, grantResults);
        base.OnRequestPermissionsResult(requestCode, permissions, grantResults);
    }
    
    protected override void OnNewIntent(Intent intent)
    {
        base.OnNewIntent(intent);
        HandleIntent(intent);
    }
    
    private void HandleIntent(Intent intent)
    {
        if (intent?.Data != null)
        {
            var uri = intent.Data.ToString();
            var navigationService = IPlatformApplication.Current.Services
                .GetRequiredService<INavigationService>();
            navigationService.NavigateToDeepLink(uri);
        }
    }
    
    private void CreateNotificationChannel()
    {
        if (Build.VERSION.SdkInt >= BuildVersionCodes.O)
        {
            var channel = new NotificationChannel(
                "default",
                "Default notifications",
                NotificationImportance.Default)
            {
                Description = "Default notification channel"
            };
            
            var notificationManager = (NotificationManager)GetSystemService(NotificationService);
            notificationManager?.CreateNotificationChannel(channel);
        }
    }
}

// Platforms/iOS/AppDelegate.cs
[Register("AppDelegate")]
public class AppDelegate : MauiUIApplicationDelegate
{
    protected override MauiApp CreateMauiApp() => MauiProgram.CreateMauiApp();
    
    public override bool FinishedLaunching(UIApplication application, NSDictionary launchOptions)
    {
        // Push notifications
        UNUserNotificationCenter.Current.Delegate = new NotificationDelegate();
        
        var authOptions = UNAuthorizationOptions.Alert | UNAuthorizationOptions.Badge | UNAuthorizationOptions.Sound;
        UNUserNotificationCenter.Current.RequestAuthorization(authOptions, (granted, error) =>
        {
            if (granted)
            {
                InvokeOnMainThread(() => UIApplication.SharedApplication.RegisterForRemoteNotifications());
            }
        });
        
        return base.FinishedLaunching(application, launchOptions);
    }
    
    public override void RegisteredForRemoteNotifications(UIApplication application, NSData deviceToken)
    {
        var token = ExtractToken(deviceToken);
        var pushService = IPlatformApplication.Current.Services
            .GetRequiredService<IPushNotificationService>();
        pushService.RegisterDeviceToken(token);
    }
    
    public override bool OpenUrl(UIApplication application, NSUrl url, NSDictionary options)
    {
        if (url != null)
        {
            var navigationService = IPlatformApplication.Current.Services
                .GetRequiredService<INavigationService>();
            navigationService.NavigateToDeepLink(url.ToString());
            return true;
        }
        return base.OpenUrl(application, url, options);
    }
}

// Services/PlatformSpecific/BiometricService.cs
public interface IBiometricService
{
    Task<bool> IsAvailableAsync();
    Task<bool> AuthenticateAsync(string reason);
}

#if ANDROID
public class BiometricService : IBiometricService
{
    public async Task<bool> IsAvailableAsync()
    {
        var context = Platform.CurrentActivity ?? Android.App.Application.Context;
        var biometricManager = BiometricManager.From(context);
        
        return biometricManager.CanAuthenticate(BiometricManager.Authenticators.BiometricWeak) 
            == BiometricManager.BiometricSuccess;
    }
    
    public async Task<bool> AuthenticateAsync(string reason)
    {
        var tcs = new TaskCompletionSource<bool>();
        
        var context = Platform.CurrentActivity;
        var executor = ContextCompat.GetMainExecutor(context);
        var biometricPrompt = new BiometricPrompt(context as FragmentActivity, executor,
            new AuthenticationCallback(tcs));
        
        var promptInfo = new BiometricPrompt.PromptInfo.Builder()
            .SetTitle("認証が必要です")
            .SetSubtitle(reason)
            .SetNegativeButtonText("キャンセル")
            .Build();
        
        biometricPrompt.Authenticate(promptInfo);
        
        return await tcs.Task;
    }
    
    private class AuthenticationCallback : BiometricPrompt.AuthenticationCallback
    {
        private readonly TaskCompletionSource<bool> _tcs;
        
        public AuthenticationCallback(TaskCompletionSource<bool> tcs)
        {
            _tcs = tcs;
        }
        
        public override void OnAuthenticationSucceeded(BiometricPrompt.AuthenticationResult result)
        {
            base.OnAuthenticationSucceeded(result);
            _tcs.SetResult(true);
        }
        
        public override void OnAuthenticationError(int errorCode, Java.Lang.ICharSequence errString)
        {
            base.OnAuthenticationError(errorCode, errString);
            _tcs.SetResult(false);
        }
        
        public override void OnAuthenticationFailed()
        {
            base.OnAuthenticationFailed();
            _tcs.SetResult(false);
        }
    }
}
#elif IOS
public class BiometricService : IBiometricService
{
    public Task<bool> IsAvailableAsync()
    {
        var context = new LAContext();
        var error = new NSError();
        var available = context.CanEvaluatePolicy(
            LAPolicy.DeviceOwnerAuthenticationWithBiometrics, 
            out error);
        
        return Task.FromResult(available);
    }
    
    public async Task<bool> AuthenticateAsync(string reason)
    {
        var context = new LAContext();
        var result = await context.EvaluatePolicyAsync(
            LAPolicy.DeviceOwnerAuthenticationWithBiometrics,
            reason);
        
        return result.Item1;
    }
}
#endif
```

### 3. MVVM パターンとデータバインディング
```csharp
// ViewModels/BaseViewModel.cs
public abstract class BaseViewModel : INotifyPropertyChanged
{
    private bool _isBusy;
    private string _title = string.Empty;
    
    public bool IsBusy
    {
        get => _isBusy;
        set => SetProperty(ref _isBusy, value);
    }
    
    public string Title
    {
        get => _title;
        set => SetProperty(ref _title, value);
    }
    
    protected bool SetProperty<T>(ref T backingStore, T value,
        [CallerMemberName] string propertyName = "",
        Action? onChanged = null)
    {
        if (EqualityComparer<T>.Default.Equals(backingStore, value))
            return false;
        
        backingStore = value;
        onChanged?.Invoke();
        OnPropertyChanged(propertyName);
        return true;
    }
    
    public event PropertyChangedEventHandler? PropertyChanged;
    
    protected void OnPropertyChanged([CallerMemberName] string propertyName = "")
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}

// ViewModels/CustomerListViewModel.cs
public class CustomerListViewModel : BaseViewModel
{
    private readonly IDataService _dataService;
    private readonly INavigationService _navigationService;
    private readonly IConnectivity _connectivity;
    
    public ObservableCollection<Customer> Customers { get; }
    public Command LoadCustomersCommand { get; }
    public Command<Customer> CustomerTappedCommand { get; }
    public Command AddCustomerCommand { get; }
    public Command<Customer> DeleteCustomerCommand { get; }
    public Command RefreshCommand { get; }
    
    private string _searchText = string.Empty;
    public string SearchText
    {
        get => _searchText;
        set
        {
            SetProperty(ref _searchText, value);
            FilterCustomers();
        }
    }
    
    public CustomerListViewModel(
        IDataService dataService,
        INavigationService navigationService,
        IConnectivity connectivity)
    {
        Title = "顧客一覧";
        _dataService = dataService;
        _navigationService = navigationService;
        _connectivity = connectivity;
        
        Customers = new ObservableCollection<Customer>();
        
        LoadCustomersCommand = new Command(async () => await LoadCustomersAsync());
        CustomerTappedCommand = new Command<Customer>(async (c) => await OnCustomerSelected(c));
        AddCustomerCommand = new Command(async () => await OnAddCustomer());
        DeleteCustomerCommand = new Command<Customer>(async (c) => await OnDeleteCustomer(c));
        RefreshCommand = new Command(async () => await RefreshAsync());
    }
    
    public async Task InitializeAsync()
    {
        await LoadCustomersAsync();
    }
    
    private async Task LoadCustomersAsync()
    {
        if (IsBusy) return;
        
        try
        {
            IsBusy = true;
            
            IEnumerable<Customer> customers;
            
            if (_connectivity.NetworkAccess == NetworkAccess.Internet)
            {
                // Online: Fetch from API
                customers = await _dataService.GetCustomersAsync();
                
                // Cache locally
                await _dataService.CacheCustomersAsync(customers);
            }
            else
            {
                // Offline: Load from local cache
                customers = await _dataService.GetCachedCustomersAsync();
            }
            
            Customers.Clear();
            foreach (var customer in customers)
            {
                Customers.Add(customer);
            }
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("エラー", 
                $"顧客データの読み込みに失敗しました: {ex.Message}", "OK");
        }
        finally
        {
            IsBusy = false;
        }
    }
    
    private async Task OnCustomerSelected(Customer customer)
    {
        if (customer == null) return;
        
        await _navigationService.NavigateToAsync<CustomerDetailViewModel>(
            new Dictionary<string, object>
            {
                { "Customer", customer }
            });
    }
    
    private async Task OnDeleteCustomer(Customer customer)
    {
        var confirm = await Shell.Current.DisplayAlert(
            "確認",
            $"{customer.Name}を削除しますか？",
            "削除",
            "キャンセル");
        
        if (confirm)
        {
            await _dataService.DeleteCustomerAsync(customer.Id);
            Customers.Remove(customer);
        }
    }
    
    private void FilterCustomers()
    {
        // Implement search/filter logic
    }
}

// Views/CustomerListPage.xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:toolkit="http://schemas.microsoft.com/dotnet/2022/maui/toolkit"
             x:Class="MyApp.Views.CustomerListPage"
             Title="{Binding Title}">
    
    <ContentPage.Behaviors>
        <toolkit:EventToCommandBehavior
            EventName="Appearing"
            Command="{Binding LoadCustomersCommand}" />
    </ContentPage.Behaviors>
    
    <ContentPage.ToolbarItems>
        <ToolbarItem Text="追加" Command="{Binding AddCustomerCommand}" />
    </ContentPage.ToolbarItems>
    
    <Grid RowDefinitions="Auto,*">
        <!-- Search Bar -->
        <SearchBar Grid.Row="0"
                   Placeholder="顧客を検索..."
                   Text="{Binding SearchText}"
                   SearchCommand="{Binding LoadCustomersCommand}" />
        
        <!-- Customer List -->
        <RefreshView Grid.Row="1"
                     IsRefreshing="{Binding IsBusy}"
                     Command="{Binding RefreshCommand}">
            <CollectionView ItemsSource="{Binding Customers}"
                           SelectionMode="None"
                           RemainingItemsThreshold="5"
                           RemainingItemsThresholdReachedCommand="{Binding LoadMoreCommand}">
                
                <CollectionView.EmptyView>
                    <ContentView>
                        <StackLayout HorizontalOptions="Center" 
                                    VerticalOptions="Center">
                            <Image Source="empty_state.png" 
                                   HeightRequest="200" />
                            <Label Text="顧客データがありません"
                                   FontSize="Large"
                                   HorizontalOptions="Center" />
                        </StackLayout>
                    </ContentView>
                </CollectionView.EmptyView>
                
                <CollectionView.ItemTemplate>
                    <DataTemplate>
                        <SwipeView>
                            <SwipeView.RightItems>
                                <SwipeItems>
                                    <SwipeItem Text="削除"
                                              BackgroundColor="Red"
                                              Command="{Binding Source={RelativeSource AncestorType={x:Type ContentPage}}, 
                                                        Path=BindingContext.DeleteCustomerCommand}"
                                              CommandParameter="{Binding .}" />
                                </SwipeItems>
                            </SwipeView.RightItems>
                            
                            <Frame Margin="10,5"
                                   Padding="10"
                                   BackgroundColor="{AppThemeBinding Light={StaticResource White}, 
                                                                     Dark={StaticResource Gray900}}">
                                <Frame.GestureRecognizers>
                                    <TapGestureRecognizer 
                                        Command="{Binding Source={RelativeSource AncestorType={x:Type ContentPage}}, 
                                                  Path=BindingContext.CustomerTappedCommand}"
                                        CommandParameter="{Binding .}" />
                                </Frame.GestureRecognizers>
                                
                                <Grid ColumnDefinitions="Auto,*,Auto"
                                      RowDefinitions="Auto,Auto,Auto">
                                    
                                    <!-- Avatar -->
                                    <Frame Grid.RowSpan="3"
                                           CornerRadius="25"
                                           HeightRequest="50"
                                           WidthRequest="50"
                                           Padding="0"
                                           IsClippedToBounds="True">
                                        <Image Source="{Binding AvatarUrl}"
                                               Aspect="AspectFill" />
                                    </Frame>
                                    
                                    <!-- Name -->
                                    <Label Grid.Column="1"
                                           Text="{Binding Name}"
                                           FontSize="Medium"
                                           FontAttributes="Bold"
                                           Margin="10,0,0,0" />
                                    
                                    <!-- Company -->
                                    <Label Grid.Column="1"
                                           Grid.Row="1"
                                           Text="{Binding Company}"
                                           FontSize="Small"
                                           TextColor="{AppThemeBinding Light={StaticResource Gray600}, 
                                                                       Dark={StaticResource Gray400}}"
                                           Margin="10,0,0,0" />
                                    
                                    <!-- Email -->
                                    <Label Grid.Column="1"
                                           Grid.Row="2"
                                           Text="{Binding Email}"
                                           FontSize="Small"
                                           TextColor="{AppThemeBinding Light={StaticResource Gray500}, 
                                                                       Dark={StaticResource Gray300}}"
                                           Margin="10,0,0,0" />
                                    
                                    <!-- Status -->
                                    <Frame Grid.Column="2"
                                           Grid.RowSpan="3"
                                           BackgroundColor="{Binding StatusColor}"
                                           CornerRadius="5"
                                           Padding="5,2">
                                        <Label Text="{Binding Status}"
                                               FontSize="Micro"
                                               TextColor="White" />
                                    </Frame>
                                </Grid>
                            </Frame>
                        </SwipeView>
                    </DataTemplate>
                </CollectionView.ItemTemplate>
            </CollectionView>
        </RefreshView>
    </Grid>
</ContentPage>
```

### 4. オフライン対応とデータ同期
```csharp
// Services/OfflineDataSync.cs
public class OfflineDataSync : IOfflineDataSync
{
    private readonly IDatabase _database;
    private readonly IApiService _apiService;
    private readonly IConnectivity _connectivity;
    private readonly ILogger<OfflineDataSync> _logger;
    private readonly SemaphoreSlim _syncSemaphore = new(1, 1);
    
    public OfflineDataSync(
        IDatabase database,
        IApiService apiService,
        IConnectivity connectivity,
        ILogger<OfflineDataSync> logger)
    {
        _database = database;
        _apiService = apiService;
        _connectivity = connectivity;
        _logger = logger;
        
        // Monitor connectivity changes
        _connectivity.ConnectivityChanged += OnConnectivityChanged;
    }
    
    private async void OnConnectivityChanged(object? sender, ConnectivityChangedEventArgs e)
    {
        if (e.NetworkAccess == NetworkAccess.Internet)
        {
            // Automatically sync when coming online
            await SyncAsync();
        }
    }
    
    public async Task<SyncResult> SyncAsync()
    {
        if (_connectivity.NetworkAccess != NetworkAccess.Internet)
        {
            return new SyncResult { Success = false, Message = "No internet connection" };
        }
        
        await _syncSemaphore.WaitAsync();
        try
        {
            var result = new SyncResult();
            
            // 1. Upload pending changes
            var pendingChanges = await _database.GetPendingChangesAsync();
            foreach (var change in pendingChanges)
            {
                try
                {
                    switch (change.Operation)
                    {
                        case SyncOperation.Create:
                            await _apiService.CreateAsync(change.Entity);
                            break;
                        case SyncOperation.Update:
                            await _apiService.UpdateAsync(change.Entity);
                            break;
                        case SyncOperation.Delete:
                            await _apiService.DeleteAsync(change.EntityId);
                            break;
                    }
                    
                    await _database.MarkAsSyncedAsync(change.Id);
                    result.UploadedCount++;
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, $"Failed to sync change {change.Id}");
                    result.Errors.Add($"Failed to sync {change.EntityType} {change.EntityId}");
                }
            }
            
            // 2. Download server changes
            var lastSync = await _database.GetLastSyncTimeAsync();
            var serverChanges = await _apiService.GetChangesAsync(lastSync);
            
            foreach (var change in serverChanges)
            {
                await _database.ApplyServerChangeAsync(change);
                result.DownloadedCount++;
            }
            
            // 3. Update last sync time
            await _database.SetLastSyncTimeAsync(DateTime.UtcNow);
            
            result.Success = result.Errors.Count == 0;
            result.Message = result.Success 
                ? $"Synced {result.UploadedCount} uploads, {result.DownloadedCount} downloads"
                : $"Sync completed with {result.Errors.Count} errors";
            
            return result;
        }
        finally
        {
            _syncSemaphore.Release();
        }
    }
    
    public async Task SavePendingChanges()
    {
        // Save any unsaved changes to local database
        await _database.SaveChangesAsync();
    }
}

// Database/SqliteDatabase.cs
public class SqliteDatabase : IDatabase
{
    private readonly SQLiteAsyncConnection _connection;
    
    public SqliteDatabase(string dbPath)
    {
        _connection = new SQLiteAsyncConnection(dbPath, 
            SQLiteOpenFlags.ReadWrite | SQLiteOpenFlags.Create | SQLiteOpenFlags.SharedCache);
        
        InitializeAsync().SafeFireAndForget();
    }
    
    private async Task InitializeAsync()
    {
        await _connection.CreateTableAsync<Customer>();
        await _connection.CreateTableAsync<Order>();
        await _connection.CreateTableAsync<SyncChange>();
        await _connection.CreateTableAsync<CachedResponse>();
    }
    
    public async Task<List<T>> GetAllAsync<T>() where T : new()
    {
        return await _connection.Table<T>().ToListAsync();
    }
    
    public async Task<T> GetAsync<T>(int id) where T : new()
    {
        return await _connection.FindAsync<T>(id);
    }
    
    public async Task<int> SaveAsync<T>(T entity) where T : new()
    {
        if (entity is IEntity entityWithId)
        {
            if (entityWithId.Id == 0)
            {
                // Track as pending create
                await TrackChangeAsync(entity, SyncOperation.Create);
                return await _connection.InsertAsync(entity);
            }
            else
            {
                // Track as pending update
                await TrackChangeAsync(entity, SyncOperation.Update);
                return await _connection.UpdateAsync(entity);
            }
        }
        
        return await _connection.InsertOrReplaceAsync(entity);
    }
    
    private async Task TrackChangeAsync<T>(T entity, SyncOperation operation)
    {
        var change = new SyncChange
        {
            EntityType = typeof(T).Name,
            EntityId = (entity as IEntity)?.Id.ToString() ?? "",
            Operation = operation,
            ChangeData = JsonSerializer.Serialize(entity),
            CreatedAt = DateTime.UtcNow,
            IsSynced = false
        };
        
        await _connection.InsertAsync(change);
    }
}
```

## Xamarin.Forms レガシー対応

### Xamarin.Forms 基本実装
```csharp
// App.xaml.cs (Xamarin.Forms)
public partial class App : Application
{
    public App()
    {
        InitializeComponent();
        
        // Register services
        DependencyService.Register<IDataService, DataService>();
        DependencyService.Register<INavigationService, NavigationService>();
        
        MainPage = new NavigationPage(new MainPage());
    }
}

// Custom renderers for platform-specific UI
[assembly: ExportRenderer(typeof(CustomEntry), typeof(CustomEntryRenderer))]
namespace MyApp.iOS.Renderers
{
    public class CustomEntryRenderer : EntryRenderer
    {
        protected override void OnElementChanged(ElementChangedEventArgs<Entry> e)
        {
            base.OnElementChanged(e);
            
            if (Control != null)
            {
                Control.BorderStyle = UITextBorderStyle.None;
                Control.Layer.CornerRadius = 10;
                Control.Layer.BorderWidth = 1;
                Control.Layer.BorderColor = UIColor.LightGray.CGColor;
            }
        }
    }
}
```

## バージョン別機能対応表

| 機能 | .NET MAUI (.NET 8) | .NET MAUI (.NET 7) | .NET MAUI (.NET 6) | Xamarin.Forms |
|------|-------------------|-------------------|-------------------|---------------|
| Single Project | ✅ | ✅ | ✅ | ❌ |
| Hot Reload | ✅ Enhanced | ✅ | ✅ | ⚠️ Limited |
| MVU Pattern | ✅ | ✅ | ✅ | ❌ |
| Blazor Hybrid | ✅ | ✅ | ✅ | ❌ |
| .NET 6+ APIs | ✅ | ✅ | ✅ | ❌ |
| Graphics API | ✅ Enhanced | ✅ | ✅ | ⚠️ SkiaSharp |
| Handlers | ✅ | ✅ | ✅ | ❌ Renderers |
| Performance | ⚡ 最速 | ⚡ 高速 | ⚡ 高速 | 🐢 普通 |
| Windows Support | ✅ WinUI 3 | ✅ WinUI 3 | ✅ WinUI 3 | ⚠️ UWP |
| macOS Support | ✅ Native | ✅ Native | ✅ Native | ⚠️ Limited |

## 出力レポート
```markdown
# MAUI/Xamarin モバイル開発レポート

## 実施項目
✅ プロジェクト構成: 完了
✅ DI設定: 実装済み
✅ MVVM実装: 完了
✅ オフライン対応: 実装済み
✅ プラットフォーム機能: 統合完了

## パフォーマンス指標
- 起動時間: 1.2秒 (iOS), 1.5秒 (Android)
- メモリ使用量: 45MB (平均)
- バッテリー影響: 最小
- オフライン同期: 95%成功率

## 推奨事項
1. .NET 8 MAUI採用
2. Blazor Hybrid検討
3. 自動UIテスト導入
4. CI/CD パイプライン構築
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: クロスプラットフォームモバイル開発

---
*このコマンドはMAUI/Xamarinの全バージョンに対応したモバイル開発に特化しています。*