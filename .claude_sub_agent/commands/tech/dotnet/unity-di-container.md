# /unity-di-container - Unity DI/IoCコンテナ専用コマンド

## 概要
Unity Container（.NET Framework）と.NET標準DI/IoCコンテナの両方に対応した依存性注入実装の専用コマンドです。レガシーシステムからモダンDIコンテナへの移行、企業レベルのDIパターン、AOP、ライフサイクル管理を包括的にサポートします。

## バージョン検出と自動選択
```csharp
// DI Container version detection
#if NET6_0_OR_GREATER
    // .NET 6+ built-in DI container with third-party enhancements
    builder.Services.AddAutofac(); // or AddScrutinor()
    builder.Services.AddInterception();
#elif NETCOREAPP3_1
    // .NET Core built-in DI
    services.AddScoped<IService, Service>();
#else
    // Unity Container for .NET Framework
    var container = new UnityContainer();
    container.RegisterType<IService, Service>();
    DependencyResolver.SetResolver(new UnityDependencyResolver(container));
#endif
```

## Unity Container実装（.NET Framework）

### 1. Unity Container エンタープライズ設定
```csharp
// Configuration/UnityConfig.cs
using Unity;
using Unity.Interception;
using Unity.Interception.PolicyInjection;
using Unity.Interception.ContainerIntegration;

public static class UnityConfig
{
    private static IUnityContainer _container;
    
    public static IUnityContainer Container => _container ?? (_container = BuildContainer());
    
    private static IUnityContainer BuildContainer()
    {
        var container = new UnityContainer();
        
        // Enable interception for AOP
        container.AddNewExtension<Interception>();
        
        // Register core services
        RegisterCoreServices(container);
        
        // Register business services
        RegisterBusinessServices(container);
        
        // Register data access
        RegisterDataAccess(container);
        
        // Register interceptors
        RegisterInterceptors(container);
        
        return container;
    }
    
    private static void RegisterCoreServices(IUnityContainer container)
    {
        // Singleton services
        container.RegisterSingleton<ILogger, EnterpriseLogger>();
        container.RegisterSingleton<IConfiguration, ConfigurationService>();
        container.RegisterSingleton<ICacheService, MemoryCacheService>();
        
        // Scoped services (per request in web apps)
        container.RegisterType<ISecurityContext, SecurityContext>(
            new ContainerControlledLifetimeManager());
        
        // Transient services
        container.RegisterType<IEmailService, SmtpEmailService>();
        container.RegisterType<IFileService, FileService>();
        
        // Named registrations
        container.RegisterType<IDataAccess, SqlServerDataAccess>("SqlServer");
        container.RegisterType<IDataAccess, OracleDataAccess>("Oracle");
        container.RegisterType<IDataAccess, MySqlDataAccess>("MySQL");
        
        // Factory pattern
        container.RegisterType<IDataAccessFactory, DataAccessFactory>();
    }
    
    private static void RegisterBusinessServices(IUnityContainer container)
    {
        // Business services with interception
        container.RegisterType<ICustomerService, CustomerService>(
            new Interceptor<InterfaceInterceptor>(),
            new InterceptionBehavior<LoggingInterceptionBehavior>(),
            new InterceptionBehavior<SecurityInterceptionBehavior>(),
            new InterceptionBehavior<CachingInterceptionBehavior>(),
            new InterceptionBehavior<TransactionInterceptionBehavior>());
        
        container.RegisterType<IOrderService, OrderService>(
            new Interceptor<InterfaceInterceptor>(),
            new InterceptionBehavior<LoggingInterceptionBehavior>(),
            new InterceptionBehavior<ValidationInterceptionBehavior>(),
            new InterceptionBehavior<PerformanceInterceptionBehavior>());
        
        container.RegisterType<IInventoryService, InventoryService>(
            new Interceptor<InterfaceInterceptor>(),
            new InterceptionBehavior<LoggingInterceptionBehavior>(),
            new InterceptionBehavior<RetryInterceptionBehavior>());
        
        // Conditional registration based on configuration
        var useAdvancedFeatures = ConfigurationManager.AppSettings["UseAdvancedFeatures"] == "true";
        if (useAdvancedFeatures)
        {
            container.RegisterType<IReportingService, AdvancedReportingService>();
        }
        else
        {
            container.RegisterType<IReportingService, BasicReportingService>();
        }
    }
    
    private static void RegisterDataAccess(IUnityContainer container)
    {
        // Entity Framework context
        container.RegisterType<DbContext, ApplicationDbContext>(
            new PerRequestLifetimeManager(),
            new InjectionConstructor(
                ConfigurationManager.ConnectionStrings["DefaultConnection"].ConnectionString));
        
        // Repository pattern
        container.RegisterType(typeof(IRepository<>), typeof(EntityFrameworkRepository<>));
        container.RegisterType<IUnitOfWork, EntityFrameworkUnitOfWork>();
        
        // Specific repositories
        container.RegisterType<ICustomerRepository, CustomerRepository>();
        container.RegisterType<IOrderRepository, OrderRepository>();
        container.RegisterType<IProductRepository, ProductRepository>();
    }
    
    private static void RegisterInterceptors(IUnityContainer container)
    {
        // Register interception behaviors
        container.RegisterType<LoggingInterceptionBehavior>();
        container.RegisterType<SecurityInterceptionBehavior>();
        container.RegisterType<CachingInterceptionBehavior>();
        container.RegisterType<TransactionInterceptionBehavior>();
        container.RegisterType<ValidationInterceptionBehavior>();
        container.RegisterType<PerformanceInterceptionBehavior>();
        container.RegisterType<RetryInterceptionBehavior>();
    }
    
    // Child container for scoped operations
    public static IUnityContainer CreateChildContainer()
    {
        return Container.CreateChildContainer();
    }
    
    // Dispose container properly
    public static void DisposeContainer()
    {
        _container?.Dispose();
        _container = null;
    }
}

// ASP.NET MVC Integration
public class UnityDependencyResolver : IDependencyResolver
{
    private readonly IUnityContainer _container;
    
    public UnityDependencyResolver(IUnityContainer container)
    {
        _container = container;
    }
    
    public object GetService(Type serviceType)
    {
        try
        {
            return _container.Resolve(serviceType);
        }
        catch (ResolutionFailedException)
        {
            return null;
        }
    }
    
    public IEnumerable<object> GetServices(Type serviceType)
    {
        try
        {
            return _container.ResolveAll(serviceType);
        }
        catch (ResolutionFailedException)
        {
            return new List<object>();
        }
    }
}

// Global.asax.cs
protected void Application_Start()
{
    // Set Unity as the dependency resolver
    DependencyResolver.SetResolver(new UnityDependencyResolver(UnityConfig.Container));
    
    // Register for proper disposal
    RegisterForDisposal();
}

protected void Application_End()
{
    UnityConfig.DisposeContainer();
}
```

### 2. AOP（Aspect-Oriented Programming）実装
```csharp
// Interception/LoggingInterceptionBehavior.cs
using Unity.Interception.PolicyInjection.Pipeline;

public class LoggingInterceptionBehavior : IInterceptionBehavior
{
    private readonly ILogger _logger;
    
    public LoggingInterceptionBehavior(ILogger logger)
    {
        _logger = logger;
    }
    
    public IMethodReturn Invoke(IMethodInvocation input, GetNextInterceptionBehaviorDelegate getNext)
    {
        var stopwatch = Stopwatch.StartNew();
        var methodName = $"{input.Target.GetType().Name}.{input.MethodBase.Name}";
        var parameters = string.Join(", ", input.Arguments.Cast<object>().Select(a => a?.ToString() ?? "null"));
        
        _logger.LogInformation($"Entering {methodName} with parameters: [{parameters}]");
        
        try
        {
            var result = getNext()(input, getNext);
            
            stopwatch.Stop();
            
            if (result.Exception != null)
            {
                _logger.LogError(result.Exception, 
                    $"Exception in {methodName} after {stopwatch.ElapsedMilliseconds}ms");
            }
            else
            {
                _logger.LogInformation(
                    $"Exiting {methodName} successfully after {stopwatch.ElapsedMilliseconds}ms");
            }
            
            return result;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, $"Unhandled exception in {methodName} after {stopwatch.ElapsedMilliseconds}ms");
            throw;
        }
    }
    
    public IEnumerable<Type> GetRequiredInterfaces()
    {
        return Type.EmptyTypes;
    }
    
    public bool WillExecute => true;
}

// Interception/CachingInterceptionBehavior.cs
public class CachingInterceptionBehavior : IInterceptionBehavior
{
    private readonly ICacheService _cacheService;
    
    public CachingInterceptionBehavior(ICacheService cacheService)
    {
        _cacheService = cacheService;
    }
    
    public IMethodReturn Invoke(IMethodInvocation input, GetNextInterceptionBehaviorDelegate getNext)
    {
        var method = input.MethodBase;
        var cacheAttribute = method.GetCustomAttribute<CacheableAttribute>();
        
        if (cacheAttribute == null)
        {
            return getNext()(input, getNext);
        }
        
        var cacheKey = GenerateCacheKey(input);
        var cachedResult = _cacheService.Get<object>(cacheKey);
        
        if (cachedResult != null)
        {
            return input.CreateMethodReturn(cachedResult);
        }
        
        var result = getNext()(input, getNext);
        
        if (result.Exception == null && result.ReturnValue != null)
        {
            _cacheService.Set(cacheKey, result.ReturnValue, cacheAttribute.Duration);
        }
        
        return result;
    }
    
    private string GenerateCacheKey(IMethodInvocation input)
    {
        var typeName = input.Target.GetType().FullName;
        var methodName = input.MethodBase.Name;
        var parameterHash = ComputeParameterHash(input.Arguments);
        
        return $"{typeName}.{methodName}:{parameterHash}";
    }
    
    private string ComputeParameterHash(IParameterCollection parameters)
    {
        var serializer = new JsonSerializer();
        using var stringWriter = new StringWriter();
        serializer.Serialize(stringWriter, parameters.Cast<object>().ToArray());
        var json = stringWriter.ToString();
        
        using var sha256 = SHA256.Create();
        var hash = sha256.ComputeHash(Encoding.UTF8.GetBytes(json));
        return Convert.ToBase64String(hash);
    }
    
    public IEnumerable<Type> GetRequiredInterfaces() => Type.EmptyTypes;
    public bool WillExecute => true;
}

// Interception/TransactionInterceptionBehavior.cs
public class TransactionInterceptionBehavior : IInterceptionBehavior
{
    private readonly IUnitOfWork _unitOfWork;
    
    public TransactionInterceptionBehavior(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }
    
    public IMethodReturn Invoke(IMethodInvocation input, GetNextInterceptionBehaviorDelegate getNext)
    {
        var method = input.MethodBase;
        var transactionAttribute = method.GetCustomAttribute<TransactionalAttribute>();
        
        if (transactionAttribute == null)
        {
            return getNext()(input, getNext);
        }
        
        using var transaction = _unitOfWork.BeginTransaction(transactionAttribute.IsolationLevel);
        
        try
        {
            var result = getNext()(input, getNext);
            
            if (result.Exception == null)
            {
                transaction.Commit();
            }
            else
            {
                transaction.Rollback();
            }
            
            return result;
        }
        catch
        {
            transaction.Rollback();
            throw;
        }
    }
    
    public IEnumerable<Type> GetRequiredInterfaces() => Type.EmptyTypes;
    public bool WillExecute => true;
}

// Attributes/CacheableAttribute.cs
[AttributeUsage(AttributeTargets.Method)]
public class CacheableAttribute : Attribute
{
    public TimeSpan Duration { get; set; } = TimeSpan.FromMinutes(5);
    
    public CacheableAttribute() { }
    
    public CacheableAttribute(int durationMinutes)
    {
        Duration = TimeSpan.FromMinutes(durationMinutes);
    }
}

// Attributes/TransactionalAttribute.cs
[AttributeUsage(AttributeTargets.Method)]
public class TransactionalAttribute : Attribute
{
    public IsolationLevel IsolationLevel { get; set; } = IsolationLevel.ReadCommitted;
}
```

## .NET Core/6+ DI Container統合

### 1. モダンDIコンテナ設定
```csharp
// Program.cs - .NET 6+ with enhanced DI
using Autofac;
using Autofac.Extensions.DependencyInjection;
using Scrutor;

var builder = WebApplication.CreateBuilder(args);

// Use Autofac as DI container for advanced features
builder.Host.UseServiceProviderFactory(new AutofacServiceProviderFactory());

// Built-in DI with Scrutor for decoration and scanning
builder.Services.Scan(scan => scan
    .FromApplicationDependencies()
    .AddClasses(classes => classes.Where(type => type.Name.EndsWith("Service")))
    .AsImplementedInterfaces()
    .WithScopedLifetime());

// Service decoration with Scrutor
builder.Services.AddScoped<ICustomerService, CustomerService>();
builder.Services.Decorate<ICustomerService, CachedCustomerService>();
builder.Services.Decorate<ICustomerService, LoggedCustomerService>();

// Register factories
builder.Services.AddSingleton<IServiceFactory>(provider => 
    new ServiceFactory(provider));

// Register with conditions
builder.Services.AddScoped<IPaymentProcessor>(provider =>
{
    var config = provider.GetRequiredService<IConfiguration>();
    var processorType = config["Payment:Processor"];
    
    return processorType?.ToLower() switch
    {
        "stripe" => provider.GetRequiredService<StripePaymentProcessor>(),
        "paypal" => provider.GetRequiredService<PayPalPaymentProcessor>(),
        _ => provider.GetRequiredService<DefaultPaymentProcessor>()
    };
});

// Autofac configuration
builder.Host.ConfigureContainer<ContainerBuilder>(containerBuilder =>
{
    // Module registration
    containerBuilder.RegisterModule<CoreModule>();
    containerBuilder.RegisterModule<BusinessModule>();
    containerBuilder.RegisterModule<DataModule>();
    
    // Advanced registration patterns
    containerBuilder.RegisterGeneric(typeof(Repository<>))
        .As(typeof(IRepository<>))
        .InstancePerLifetimeScope();
    
    // Conditional registration
    containerBuilder.Register(context =>
    {
        var config = context.Resolve<IConfiguration>();
        return config["Environment"] == "Development" 
            ? new MockEmailService() as IEmailService
            : new SmtpEmailService();
    }).SingleInstance();
    
    // Interceptors with Castle DynamicProxy
    containerBuilder.RegisterType<LoggingInterceptor>();
    containerBuilder.RegisterType<PerformanceInterceptor>();
    
    containerBuilder.RegisterType<CustomerService>()
        .As<ICustomerService>()
        .EnableInterfaceInterceptors()
        .InterceptedBy(typeof(LoggingInterceptor), typeof(PerformanceInterceptor));
});

var app = builder.Build();

// Modules/CoreModule.cs
public class CoreModule : Module
{
    protected override void Load(ContainerBuilder builder)
    {
        // Core services
        builder.RegisterType<Logger>()
            .As<ILogger>()
            .SingleInstance();
        
        builder.RegisterType<ConfigurationService>()
            .As<IConfiguration>()
            .SingleInstance();
        
        // HTTP clients with named configurations
        builder.Register(context =>
        {
            var httpClientFactory = context.Resolve<IHttpClientFactory>();
            return httpClientFactory.CreateClient("ApiClient");
        }).As<HttpClient>().InstancePerDependency();
        
        // Event sourcing
        builder.RegisterType<EventStore>()
            .As<IEventStore>()
            .SingleInstance();
        
        builder.RegisterType<EventBus>()
            .As<IEventBus>()
            .SingleInstance();
    }
}

// Services/ServiceFactory.cs
public class ServiceFactory : IServiceFactory
{
    private readonly IServiceProvider _serviceProvider;
    
    public ServiceFactory(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }
    
    public T Create<T>() where T : class
    {
        return _serviceProvider.GetRequiredService<T>();
    }
    
    public T Create<T>(string name) where T : class
    {
        return _serviceProvider.GetRequiredService<IEnumerable<T>>()
            .FirstOrDefault(s => s.GetType().Name.Equals(name, StringComparison.OrdinalIgnoreCase))
            ?? throw new InvalidOperationException($"Service {name} of type {typeof(T).Name} not found");
    }
    
    public object Create(Type serviceType)
    {
        return _serviceProvider.GetRequiredService(serviceType);
    }
}
```

### 2. Decorator Pattern とProxy実装
```csharp
// Decorators/CachedCustomerService.cs
public class CachedCustomerService : ICustomerService
{
    private readonly ICustomerService _innerService;
    private readonly IMemoryCache _cache;
    
    public CachedCustomerService(ICustomerService innerService, IMemoryCache cache)
    {
        _innerService = innerService;
        _cache = cache;
    }
    
    public async Task<Customer> GetCustomerAsync(int id)
    {
        var cacheKey = $"customer:{id}";
        
        if (_cache.TryGetValue<Customer>(cacheKey, out var cached))
        {
            return cached;
        }
        
        var customer = await _innerService.GetCustomerAsync(id);
        
        if (customer != null)
        {
            _cache.Set(cacheKey, customer, TimeSpan.FromMinutes(5));
        }
        
        return customer;
    }
    
    public async Task<Customer> CreateCustomerAsync(Customer customer)
    {
        var result = await _innerService.CreateCustomerAsync(customer);
        
        // Invalidate cache
        _cache.Remove($"customer:{result.Id}");
        
        return result;
    }
}

// Decorators/LoggedCustomerService.cs
public class LoggedCustomerService : ICustomerService
{
    private readonly ICustomerService _innerService;
    private readonly ILogger<LoggedCustomerService> _logger;
    
    public LoggedCustomerService(ICustomerService innerService, ILogger<LoggedCustomerService> logger)
    {
        _innerService = innerService;
        _logger = logger;
    }
    
    public async Task<Customer> GetCustomerAsync(int id)
    {
        _logger.LogInformation($"Getting customer {id}");
        
        try
        {
            var result = await _innerService.GetCustomerAsync(id);
            _logger.LogInformation($"Successfully retrieved customer {id}");
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error getting customer {id}");
            throw;
        }
    }
}

// Interceptors/LoggingInterceptor.cs (Castle DynamicProxy)
public class LoggingInterceptor : IInterceptor
{
    private readonly ILogger<LoggingInterceptor> _logger;
    
    public LoggingInterceptor(ILogger<LoggingInterceptor> logger)
    {
        _logger = logger;
    }
    
    public void Intercept(IInvocation invocation)
    {
        var stopwatch = Stopwatch.StartNew();
        var methodName = $"{invocation.TargetType.Name}.{invocation.Method.Name}";
        var parameters = string.Join(", ", invocation.Arguments.Select(a => a?.ToString() ?? "null"));
        
        _logger.LogInformation($"Calling {methodName} with parameters: [{parameters}]");
        
        try
        {
            invocation.Proceed();
            
            stopwatch.Stop();
            _logger.LogInformation($"Completed {methodName} in {stopwatch.ElapsedMilliseconds}ms");
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, $"Exception in {methodName} after {stopwatch.ElapsedMilliseconds}ms");
            throw;
        }
    }
}
```

### 3. 高度なライフサイクル管理
```csharp
// LifecycleManagement/ScopedServiceManager.cs
public class ScopedServiceManager : IDisposable
{
    private readonly IServiceScope _scope;
    private readonly Dictionary<Type, object> _scopedServices = new();
    
    public ScopedServiceManager(IServiceProvider serviceProvider)
    {
        _scope = serviceProvider.CreateScope();
    }
    
    public T GetService<T>() where T : class
    {
        var serviceType = typeof(T);
        
        if (_scopedServices.TryGetValue(serviceType, out var cached))
        {
            return (T)cached;
        }
        
        var service = _scope.ServiceProvider.GetRequiredService<T>();
        _scopedServices[serviceType] = service;
        
        return service;
    }
    
    public void Dispose()
    {
        // Dispose all scoped services in reverse order
        foreach (var service in _scopedServices.Values.Reverse())
        {
            if (service is IDisposable disposable)
            {
                disposable.Dispose();
            }
        }
        
        _scope?.Dispose();
    }
}

// LifecycleManagement/ServiceLifecycleManager.cs
public class ServiceLifecycleManager : IHostedService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<ServiceLifecycleManager> _logger;
    private readonly List<IInitializableService> _initializableServices = new();
    
    public ServiceLifecycleManager(
        IServiceProvider serviceProvider,
        ILogger<ServiceLifecycleManager> logger)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
    }
    
    public async Task StartAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Starting service lifecycle management");
        
        // Get all services that need initialization
        using var scope = _serviceProvider.CreateScope();
        var services = scope.ServiceProvider.GetServices<IInitializableService>();
        
        foreach (var service in services)
        {
            try
            {
                await service.InitializeAsync(cancellationToken);
                _initializableServices.Add(service);
                _logger.LogInformation($"Initialized service: {service.GetType().Name}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Failed to initialize service: {service.GetType().Name}");
                throw;
            }
        }
    }
    
    public async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Stopping service lifecycle management");
        
        // Dispose services in reverse order
        foreach (var service in _initializableServices.AsEnumerable().Reverse())
        {
            try
            {
                if (service is IAsyncDisposable asyncDisposable)
                {
                    await asyncDisposable.DisposeAsync();
                }
                else if (service is IDisposable disposable)
                {
                    disposable.Dispose();
                }
                
                _logger.LogInformation($"Disposed service: {service.GetType().Name}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error disposing service: {service.GetType().Name}");
            }
        }
    }
}
```

## バージョン別DI機能対応表

| 機能 | .NET 6+ Built-in | Autofac | Unity Container | .NET Framework DI |
|------|------------------|---------|-----------------|-------------------|
| Constructor Injection | ✅ | ✅ | ✅ | ⚠️ Manual |
| Property Injection | ❌ | ✅ | ✅ | ❌ |
| Method Injection | ❌ | ✅ | ✅ | ❌ |
| Generic Registration | ✅ | ✅ | ✅ | ❌ |
| Named Registration | ❌ | ✅ | ✅ | ❌ |
| Conditional Registration | ⚠️ Factory | ✅ | ✅ | ❌ |
| Interception/AOP | ❌ | ✅ Castle | ✅ Policy | ❌ |
| Module System | ❌ | ✅ | ✅ | ❌ |
| Child Containers | ❌ | ✅ | ✅ | ❌ |
| Decoration | 📦 Scrutor | ✅ | ✅ | ❌ |
| Assembly Scanning | 📦 Scrutor | ✅ | ✅ | ❌ |
| Lifetime Management | ✅ Basic | ✅ Advanced | ✅ Advanced | ❌ |

## 出力レポート
```markdown
# Unity DI/IoCコンテナ最適化レポート

## 実施項目
✅ Unity Container: 完全設定
✅ AOP実装: Interception対応
✅ モダンDI移行: Autofac統合
✅ Decorator Pattern: 実装完了
✅ ライフサイクル管理: 自動化

## パフォーマンス指標
- 依存解決時間: <1ms
- メモリ使用量: 基準比20%削減
- AOP オーバーヘッド: <5%
- 設定読み込み: 50ms

## 移行効果
- レガシーコード: Unity → .NET DI
- テスタビリティ: 300%向上
- 結合度: 70%削減
- 保守性: 200%向上

## 推奨事項
1. .NET 6+への段階的移行
2. Autofac採用検討
3. AOP活用拡大
4. 単体テスト強化
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: 依存性注入・IoC設計パターン

---
*このコマンドはUnity ContainerとモダンDI/IoCコンテナの実装に特化しています。*