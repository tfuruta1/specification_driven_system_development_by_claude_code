# .NET Framework パターン集 - エンタープライズアプリケーション開発

## 1. 依存性注入パターン

### Unity Container 実装
```csharp
public class DependencyInjectionConfig
{
    private static IUnityContainer _container;
    
    public static IUnityContainer Container
    {
        get
        {
            if (_container == null)
            {
                _container = new UnityContainer();
                RegisterTypes(_container);
            }
            return _container;
        }
    }
    
    private static void RegisterTypes(IUnityContainer container)
    {
        // ライフサイクルマネージャー
        var singletonLifetime = new ContainerControlledLifetimeManager();
        var perRequestLifetime = new PerResolveLifetimeManager();
        
        // インフラストラクチャ層
        container.RegisterType<IDbConnection, SqlConnection>(
            new InjectionConstructor(ConfigurationManager.ConnectionStrings["DefaultConnection"].ConnectionString));
        
        container.RegisterType<AppDbContext>(perRequestLifetime);
        
        // リポジトリ層
        container.RegisterType<ICustomerRepository, CustomerRepository>(perRequestLifetime);
        container.RegisterType<IOrderRepository, OrderRepository>(perRequestLifetime);
        container.RegisterType<IProductRepository, ProductRepository>(perRequestLifetime);
        
        // サービス層
        container.RegisterType<ICustomerService, CustomerService>();
        container.RegisterType<IOrderService, OrderService>();
        container.RegisterType<IAuthenticationService, AuthenticationService>(singletonLifetime);
        
        // ファクトリー登録
        container.RegisterFactory<Func<IUnitOfWork>>(
            c => () => c.Resolve<IUnitOfWork>());
        
        // 汎用型の登録
        container.RegisterType(typeof(IRepository<>), typeof(Repository<>));
        
        // インターセプター登録（AOP）
        container.AddNewExtension<Interception>();
        container.RegisterType<IOrderService, OrderService>(
            new InterceptionBehavior<PolicyInjectionBehavior>(),
            new Interceptor<InterfaceInterceptor>());
    }
}

// Service Locator パターン（レガシーサポート用）
public static class ServiceLocator
{
    public static T GetService<T>()
    {
        return DependencyInjectionConfig.Container.Resolve<T>();
    }
    
    public static object GetService(Type serviceType)
    {
        return DependencyInjectionConfig.Container.Resolve(serviceType);
    }
    
    public static IEnumerable<T> GetServices<T>()
    {
        return DependencyInjectionConfig.Container.ResolveAll<T>();
    }
}
```

### コンストラクタインジェクション
```csharp
public class CustomerService : ICustomerService
{
    private readonly ICustomerRepository _customerRepository;
    private readonly IOrderRepository _orderRepository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly ILogger _logger;
    private readonly IEventBus _eventBus;
    
    public CustomerService(
        ICustomerRepository customerRepository,
        IOrderRepository orderRepository,
        IUnitOfWork unitOfWork,
        ILogger logger,
        IEventBus eventBus)
    {
        _customerRepository = customerRepository ?? throw new ArgumentNullException(nameof(customerRepository));
        _orderRepository = orderRepository ?? throw new ArgumentNullException(nameof(orderRepository));
        _unitOfWork = unitOfWork ?? throw new ArgumentNullException(nameof(unitOfWork));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _eventBus = eventBus ?? throw new ArgumentNullException(nameof(eventBus));
    }
    
    public async Task<CustomerDto> CreateCustomerAsync(CreateCustomerDto dto)
    {
        try
        {
            var customer = Customer.Create(dto.Name, dto.Email, dto.CreditLimit);
            
            await _customerRepository.AddAsync(customer);
            await _unitOfWork.CommitAsync();
            
            // イベント発行
            await _eventBus.PublishAsync(new CustomerCreatedEvent(customer));
            
            _logger.LogInformation($"Customer created: {customer.Id}");
            
            return MapToDto(customer);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating customer");
            throw;
        }
    }
}
```

## 2. リポジトリパターン

### ジェネリックリポジトリ
```csharp
public interface IRepository<TEntity> where TEntity : class, IEntity
{
    Task<TEntity> GetByIdAsync(int id);
    Task<IEnumerable<TEntity>> GetAllAsync();
    Task<IEnumerable<TEntity>> FindAsync(Expression<Func<TEntity, bool>> predicate);
    Task AddAsync(TEntity entity);
    Task AddRangeAsync(IEnumerable<TEntity> entities);
    void Update(TEntity entity);
    void Remove(TEntity entity);
    void RemoveRange(IEnumerable<TEntity> entities);
}

public class Repository<TEntity> : IRepository<TEntity> where TEntity : class, IEntity
{
    protected readonly DbContext Context;
    protected readonly DbSet<TEntity> DbSet;
    
    public Repository(DbContext context)
    {
        Context = context;
        DbSet = context.Set<TEntity>();
    }
    
    public virtual async Task<TEntity> GetByIdAsync(int id)
    {
        return await DbSet.FindAsync(id);
    }
    
    public virtual async Task<IEnumerable<TEntity>> GetAllAsync()
    {
        return await DbSet.ToListAsync();
    }
    
    public virtual async Task<IEnumerable<TEntity>> FindAsync(Expression<Func<TEntity, bool>> predicate)
    {
        return await DbSet.Where(predicate).ToListAsync();
    }
    
    public virtual async Task AddAsync(TEntity entity)
    {
        await DbSet.AddAsync(entity);
    }
    
    public virtual async Task AddRangeAsync(IEnumerable<TEntity> entities)
    {
        await DbSet.AddRangeAsync(entities);
    }
    
    public virtual void Update(TEntity entity)
    {
        DbSet.Attach(entity);
        Context.Entry(entity).State = EntityState.Modified;
    }
    
    public virtual void Remove(TEntity entity)
    {
        if (Context.Entry(entity).State == EntityState.Detached)
        {
            DbSet.Attach(entity);
        }
        DbSet.Remove(entity);
    }
    
    public virtual void RemoveRange(IEnumerable<TEntity> entities)
    {
        DbSet.RemoveRange(entities);
    }
}
```

### 仕様パターン（Specification Pattern）
```csharp
public abstract class Specification<T>
{
    public abstract Expression<Func<T, bool>> ToExpression();
    
    public bool IsSatisfiedBy(T entity)
    {
        var predicate = ToExpression().Compile();
        return predicate(entity);
    }
    
    public Specification<T> And(Specification<T> specification)
    {
        return new AndSpecification<T>(this, specification);
    }
    
    public Specification<T> Or(Specification<T> specification)
    {
        return new OrSpecification<T>(this, specification);
    }
    
    public Specification<T> Not()
    {
        return new NotSpecification<T>(this);
    }
}

public class AndSpecification<T> : Specification<T>
{
    private readonly Specification<T> _left;
    private readonly Specification<T> _right;
    
    public AndSpecification(Specification<T> left, Specification<T> right)
    {
        _left = left;
        _right = right;
    }
    
    public override Expression<Func<T, bool>> ToExpression()
    {
        var leftExpression = _left.ToExpression();
        var rightExpression = _right.ToExpression();
        
        var parameter = Expression.Parameter(typeof(T));
        var leftVisitor = new ReplaceExpressionVisitor(leftExpression.Parameters[0], parameter);
        var left = leftVisitor.Visit(leftExpression.Body);
        
        var rightVisitor = new ReplaceExpressionVisitor(rightExpression.Parameters[0], parameter);
        var right = rightVisitor.Visit(rightExpression.Body);
        
        return Expression.Lambda<Func<T, bool>>(
            Expression.AndAlso(left, right), parameter);
    }
}

// 具体的な仕様
public class ActiveCustomerSpecification : Specification<Customer>
{
    public override Expression<Func<Customer, bool>> ToExpression()
    {
        return customer => customer.IsActive && !customer.IsDeleted;
    }
}

public class HighValueCustomerSpecification : Specification<Customer>
{
    private readonly decimal _minimumOrderValue;
    
    public HighValueCustomerSpecification(decimal minimumOrderValue)
    {
        _minimumOrderValue = minimumOrderValue;
    }
    
    public override Expression<Func<Customer, bool>> ToExpression()
    {
        return customer => customer.Orders.Sum(o => o.TotalAmount) >= _minimumOrderValue;
    }
}

// 使用例
public class CustomerRepository : Repository<Customer>, ICustomerRepository
{
    public async Task<IEnumerable<Customer>> GetActiveHighValueCustomersAsync(decimal minimumOrderValue)
    {
        var spec = new ActiveCustomerSpecification()
            .And(new HighValueCustomerSpecification(minimumOrderValue));
        
        return await FindAsync(spec.ToExpression());
    }
}
```

## 3. Unit of Work パターン

```csharp
public interface IUnitOfWork : IDisposable
{
    ICustomerRepository Customers { get; }
    IOrderRepository Orders { get; }
    IProductRepository Products { get; }
    
    Task<int> CommitAsync();
    Task<IDbContextTransaction> BeginTransactionAsync();
}

public class UnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _context;
    private readonly Dictionary<Type, object> _repositories;
    
    private ICustomerRepository _customerRepository;
    private IOrderRepository _orderRepository;
    private IProductRepository _productRepository;
    
    public UnitOfWork(AppDbContext context)
    {
        _context = context;
        _repositories = new Dictionary<Type, object>();
    }
    
    public ICustomerRepository Customers => 
        _customerRepository ??= new CustomerRepository(_context);
    
    public IOrderRepository Orders => 
        _orderRepository ??= new OrderRepository(_context);
    
    public IProductRepository Products => 
        _productRepository ??= new ProductRepository(_context);
    
    public async Task<int> CommitAsync()
    {
        try
        {
            // 変更追跡の最適化
            var entries = _context.ChangeTracker.Entries()
                .Where(e => e.State == EntityState.Added || e.State == EntityState.Modified);
            
            foreach (var entry in entries)
            {
                // 監査フィールドの自動更新
                if (entry.Entity is IAuditable auditable)
                {
                    if (entry.State == EntityState.Added)
                    {
                        auditable.CreatedDate = DateTime.UtcNow;
                        auditable.CreatedBy = Thread.CurrentPrincipal?.Identity?.Name ?? "System";
                    }
                    
                    auditable.ModifiedDate = DateTime.UtcNow;
                    auditable.ModifiedBy = Thread.CurrentPrincipal?.Identity?.Name ?? "System";
                }
            }
            
            return await _context.SaveChangesAsync();
        }
        catch (DbUpdateConcurrencyException ex)
        {
            throw new ConcurrencyException("データが他のユーザーによって更新されています。", ex);
        }
    }
    
    public async Task<IDbContextTransaction> BeginTransactionAsync()
    {
        return await _context.Database.BeginTransactionAsync();
    }
    
    public void Dispose()
    {
        _context?.Dispose();
    }
}
```

## 4. ファクトリーパターン

### 抽象ファクトリー
```csharp
public interface IReportFactory
{
    IReport CreateReport(ReportType type);
    IReportExporter CreateExporter(ExportFormat format);
}

public class StandardReportFactory : IReportFactory
{
    private readonly IServiceProvider _serviceProvider;
    
    public StandardReportFactory(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }
    
    public IReport CreateReport(ReportType type)
    {
        return type switch
        {
            ReportType.Sales => new SalesReport(_serviceProvider.GetService<ISalesDataService>()),
            ReportType.Inventory => new InventoryReport(_serviceProvider.GetService<IInventoryService>()),
            ReportType.Customer => new CustomerReport(_serviceProvider.GetService<ICustomerService>()),
            ReportType.Financial => new FinancialReport(_serviceProvider.GetService<IFinancialService>()),
            _ => throw new NotSupportedException($"Report type {type} is not supported")
        };
    }
    
    public IReportExporter CreateExporter(ExportFormat format)
    {
        return format switch
        {
            ExportFormat.Pdf => new PdfExporter(),
            ExportFormat.Excel => new ExcelExporter(),
            ExportFormat.Csv => new CsvExporter(),
            ExportFormat.Html => new HtmlExporter(),
            _ => throw new NotSupportedException($"Export format {format} is not supported")
        };
    }
}

// ファクトリーメソッド
public abstract class DocumentProcessor
{
    protected abstract IDocument CreateDocument(string content);
    protected abstract IValidator CreateValidator();
    
    public async Task<ProcessResult> ProcessDocumentAsync(string content)
    {
        var document = CreateDocument(content);
        var validator = CreateValidator();
        
        var validationResult = await validator.ValidateAsync(document);
        if (!validationResult.IsValid)
        {
            return ProcessResult.ValidationFailed(validationResult.Errors);
        }
        
        return await ProcessDocumentInternalAsync(document);
    }
    
    protected abstract Task<ProcessResult> ProcessDocumentInternalAsync(IDocument document);
}

public class InvoiceProcessor : DocumentProcessor
{
    protected override IDocument CreateDocument(string content)
    {
        return new InvoiceDocument(content);
    }
    
    protected override IValidator CreateValidator()
    {
        return new InvoiceValidator();
    }
    
    protected override async Task<ProcessResult> ProcessDocumentInternalAsync(IDocument document)
    {
        var invoice = (InvoiceDocument)document;
        // 請求書固有の処理
        return ProcessResult.Success();
    }
}
```

## 5. ストラテジーパターン

```csharp
public interface IPricingStrategy
{
    decimal CalculatePrice(Order order);
    string Name { get; }
}

public class StandardPricingStrategy : IPricingStrategy
{
    public string Name => "Standard";
    
    public decimal CalculatePrice(Order order)
    {
        return order.OrderLines.Sum(line => line.Quantity * line.UnitPrice);
    }
}

public class VolumePricingStrategy : IPricingStrategy
{
    private readonly Dictionary<int, decimal> _volumeDiscounts = new()
    {
        { 10, 0.05m },   // 10個以上で5%割引
        { 50, 0.10m },   // 50個以上で10%割引
        { 100, 0.15m }   // 100個以上で15%割引
    };
    
    public string Name => "Volume";
    
    public decimal CalculatePrice(Order order)
    {
        var subtotal = order.OrderLines.Sum(line => line.Quantity * line.UnitPrice);
        var totalQuantity = order.OrderLines.Sum(line => line.Quantity);
        
        var discountRate = _volumeDiscounts
            .Where(kv => totalQuantity >= kv.Key)
            .OrderByDescending(kv => kv.Key)
            .Select(kv => kv.Value)
            .FirstOrDefault();
        
        return subtotal * (1 - discountRate);
    }
}

public class PricingContext
{
    private readonly Dictionary<string, IPricingStrategy> _strategies;
    private IPricingStrategy _currentStrategy;
    
    public PricingContext(IEnumerable<IPricingStrategy> strategies)
    {
        _strategies = strategies.ToDictionary(s => s.Name, s => s);
        _currentStrategy = _strategies.Values.First();
    }
    
    public void SetStrategy(string strategyName)
    {
        if (_strategies.TryGetValue(strategyName, out var strategy))
        {
            _currentStrategy = strategy;
        }
        else
        {
            throw new ArgumentException($"Strategy '{strategyName}' not found");
        }
    }
    
    public decimal CalculatePrice(Order order)
    {
        return _currentStrategy.CalculatePrice(order);
    }
}
```

## 6. オブザーバーパターン（イベント駆動）

```csharp
// イベントアグリゲーター
public interface IEventAggregator
{
    void Subscribe<TEvent>(Action<TEvent> handler) where TEvent : IEvent;
    void Unsubscribe<TEvent>(Action<TEvent> handler) where TEvent : IEvent;
    Task PublishAsync<TEvent>(TEvent eventToPublish) where TEvent : IEvent;
}

public class EventAggregator : IEventAggregator
{
    private readonly Dictionary<Type, List<Delegate>> _eventHandlers = new();
    private readonly SynchronizationContext _synchronizationContext;
    
    public EventAggregator()
    {
        _synchronizationContext = SynchronizationContext.Current;
    }
    
    public void Subscribe<TEvent>(Action<TEvent> handler) where TEvent : IEvent
    {
        var eventType = typeof(TEvent);
        
        if (!_eventHandlers.ContainsKey(eventType))
        {
            _eventHandlers[eventType] = new List<Delegate>();
        }
        
        _eventHandlers[eventType].Add(handler);
    }
    
    public void Unsubscribe<TEvent>(Action<TEvent> handler) where TEvent : IEvent
    {
        var eventType = typeof(TEvent);
        
        if (_eventHandlers.ContainsKey(eventType))
        {
            _eventHandlers[eventType].Remove(handler);
        }
    }
    
    public async Task PublishAsync<TEvent>(TEvent eventToPublish) where TEvent : IEvent
    {
        var eventType = typeof(TEvent);
        
        if (_eventHandlers.ContainsKey(eventType))
        {
            var handlers = _eventHandlers[eventType].Cast<Action<TEvent>>().ToList();
            
            foreach (var handler in handlers)
            {
                if (_synchronizationContext != null)
                {
                    _synchronizationContext.Post(_ => handler(eventToPublish), null);
                }
                else
                {
                    await Task.Run(() => handler(eventToPublish));
                }
            }
        }
    }
}

// イベント定義
public interface IEvent
{
    DateTime OccurredAt { get; }
}

public class CustomerCreatedEvent : IEvent
{
    public int CustomerId { get; }
    public string CustomerName { get; }
    public DateTime OccurredAt { get; }
    
    public CustomerCreatedEvent(Customer customer)
    {
        CustomerId = customer.Id;
        CustomerName = customer.Name;
        OccurredAt = DateTime.UtcNow;
    }
}

// イベントハンドラー
public class EmailNotificationHandler
{
    private readonly IEmailService _emailService;
    private readonly IEventAggregator _eventAggregator;
    
    public EmailNotificationHandler(IEmailService emailService, IEventAggregator eventAggregator)
    {
        _emailService = emailService;
        _eventAggregator = eventAggregator;
        
        // イベント購読
        _eventAggregator.Subscribe<CustomerCreatedEvent>(HandleCustomerCreated);
    }
    
    private async void HandleCustomerCreated(CustomerCreatedEvent e)
    {
        await _emailService.SendWelcomeEmailAsync(e.CustomerId);
    }
}
```

## 7. デコレーターパターン

```csharp
// キャッシング デコレーター
public class CachedRepository<T> : IRepository<T> where T : class, IEntity
{
    private readonly IRepository<T> _innerRepository;
    private readonly IMemoryCache _cache;
    private readonly TimeSpan _cacheDuration;
    
    public CachedRepository(IRepository<T> innerRepository, IMemoryCache cache, TimeSpan cacheDuration)
    {
        _innerRepository = innerRepository;
        _cache = cache;
        _cacheDuration = cacheDuration;
    }
    
    public async Task<T> GetByIdAsync(int id)
    {
        var cacheKey = $"{typeof(T).Name}_{id}";
        
        if (_cache.TryGetValue(cacheKey, out T cached))
        {
            return cached;
        }
        
        var entity = await _innerRepository.GetByIdAsync(id);
        
        if (entity != null)
        {
            _cache.Set(cacheKey, entity, _cacheDuration);
        }
        
        return entity;
    }
    
    public async Task<IEnumerable<T>> GetAllAsync()
    {
        var cacheKey = $"{typeof(T).Name}_All";
        
        if (_cache.TryGetValue(cacheKey, out IEnumerable<T> cached))
        {
            return cached;
        }
        
        var entities = await _innerRepository.GetAllAsync();
        _cache.Set(cacheKey, entities, _cacheDuration);
        
        return entities;
    }
    
    public async Task AddAsync(T entity)
    {
        await _innerRepository.AddAsync(entity);
        InvalidateCache();
    }
    
    public void Update(T entity)
    {
        _innerRepository.Update(entity);
        InvalidateCache();
    }
    
    private void InvalidateCache()
    {
        // キャッシュクリア
        var cacheKeys = _cache.GetKeys<string>()
            .Where(key => key.StartsWith(typeof(T).Name));
        
        foreach (var key in cacheKeys)
        {
            _cache.Remove(key);
        }
    }
}

// ロギング デコレーター
public class LoggingRepository<T> : IRepository<T> where T : class, IEntity
{
    private readonly IRepository<T> _innerRepository;
    private readonly ILogger _logger;
    
    public LoggingRepository(IRepository<T> innerRepository, ILogger logger)
    {
        _innerRepository = innerRepository;
        _logger = logger;
    }
    
    public async Task<T> GetByIdAsync(int id)
    {
        _logger.LogDebug($"Getting {typeof(T).Name} with ID: {id}");
        
        try
        {
            var result = await _innerRepository.GetByIdAsync(id);
            
            if (result == null)
            {
                _logger.LogWarning($"{typeof(T).Name} with ID {id} not found");
            }
            
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error getting {typeof(T).Name} with ID: {id}");
            throw;
        }
    }
    
    public async Task AddAsync(T entity)
    {
        _logger.LogInformation($"Adding new {typeof(T).Name}");
        
        try
        {
            await _innerRepository.AddAsync(entity);
            _logger.LogInformation($"Successfully added {typeof(T).Name} with ID: {entity.Id}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error adding {typeof(T).Name}");
            throw;
        }
    }
}
```

これらのパターンを適切に組み合わせることで、保守性が高く、拡張可能なエンタープライズアプリケーションを構築できます。