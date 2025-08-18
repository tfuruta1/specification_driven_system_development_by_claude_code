# /ef-optimize - Entity Framework最適化専用コマンド

## 概要
Entity Framework Core（.NET Core 2.1+）とEntity Framework 6.x（.NET Framework）の両方に対応した包括的な最適化コマンドです。各バージョンの特性を活かした最適なパフォーマンスチューニングとベストプラクティスを提供します。

## バージョン検出と自動選択
```csharp
// プロジェクトファイルから自動検出
#if EFCORE8
    // EF Core 8 (最新機能)
    builder.Services.AddDbContext<AppDbContext>(options =>
        options.UseSqlServer(connectionString)
            .UseModel(CompiledModels.AppDbContextModel.Instance)); // Compiled Models
#elif EFCORE7
    // EF Core 7
    options.UseBulkOperations(); // Bulk operations
#elif EFCORE6
    // EF Core 6
    options.UseTemporalTables(); // Temporal tables
#elif EF6
    // Entity Framework 6.x
    Database.SetInitializer(new MigrateDatabaseToLatestVersion<AppContext, Configuration>());
#endif
```

## Entity Framework Core 8 最適化（.NET 8）

### 1. 高度なクエリ最適化とComplex Types
```csharp
// Models/ComplexTypes.cs - EF Core 8 Complex Types
using Microsoft.EntityFrameworkCore;

[ComplexType]
public class Address
{
    public required string Street { get; set; }
    public required string City { get; set; }
    public required string PostalCode { get; set; }
    public required string Country { get; set; }
}

[ComplexType]
public class Money
{
    public decimal Amount { get; set; }
    public required string Currency { get; set; }
    
    public static Money Zero => new() { Amount = 0, Currency = "JPY" };
}

// Models/Customer.cs
public class Customer
{
    public int Id { get; set; }
    public required string Name { get; set; }
    public required Address BillingAddress { get; set; } // Complex Type
    public Address? ShippingAddress { get; set; } // Nullable Complex Type
    public Money CreditLimit { get; set; } // Value Object
    
    // Collections with performance optimization
    private readonly List<Order> _orders = new();
    public IReadOnlyCollection<Order> Orders => _orders.AsReadOnly();
    
    // Computed columns
    [DatabaseGenerated(DatabaseGeneratedOption.Computed)]
    public string FullAddress { get; private set; } = null!;
}

// DbContext with EF Core 8 optimizations
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) 
        : base(options) 
    {
        // Query tracking behavior for read-heavy scenarios
        ChangeTracker.QueryTrackingBehavior = QueryTrackingBehavior.NoTrackingWithIdentityResolution;
        
        // Lazy loading proxies configuration
        ChangeTracker.LazyLoadingEnabled = false;
        
        // Auto-detect changes optimization
        ChangeTracker.AutoDetectChangesEnabled = false;
    }
    
    public DbSet<Customer> Customers => Set<Customer>();
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<Product> Products => Set<Product>();
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Complex type configuration
        modelBuilder.Entity<Customer>()
            .ComplexProperty(e => e.BillingAddress)
            .IsRequired();
        
        modelBuilder.Entity<Customer>()
            .ComplexProperty(e => e.ShippingAddress);
        
        // Computed column
        modelBuilder.Entity<Customer>()
            .Property(e => e.FullAddress)
            .HasComputedColumnSql(
                "[BillingAddress_Street] + ', ' + [BillingAddress_City] + ', ' + [BillingAddress_Country]");
        
        // Index optimization
        modelBuilder.Entity<Customer>()
            .HasIndex(e => new { e.Name, e.CreatedDate })
            .HasDatabaseName("IX_Customer_Name_Created")
            .IncludeProperties(e => new { e.Email, e.Phone });
        
        // Table splitting for large entities
        modelBuilder.Entity<Product>(entity =>
        {
            entity.ToTable("Products");
            entity.SplitToTable("ProductDetails", tableBuilder =>
            {
                tableBuilder.Property(p => p.Description);
                tableBuilder.Property(p => p.Specifications);
            });
        });
        
        // Discriminator-less TPH (Table Per Hierarchy)
        modelBuilder.Entity<PaymentMethod>()
            .UseTphMappingStrategy()
            .HasDiscriminator<string>("PaymentType")
            .HasValue<CreditCard>("CC")
            .HasValue<BankTransfer>("BT")
            .HasValue<DigitalWallet>("DW");
        
        // Global query filters
        modelBuilder.Entity<Customer>()
            .HasQueryFilter(c => !c.IsDeleted);
        
        // Owned entities for value objects
        modelBuilder.Entity<Order>().OwnsOne(o => o.ShippingInfo, sa =>
        {
            sa.Property(p => p.RecipientName).HasMaxLength(100);
            sa.Property(p => p.TrackingNumber).HasMaxLength(50);
            sa.HasIndex(p => p.TrackingNumber);
        });
        
        // JSON columns (EF Core 7+)
        modelBuilder.Entity<Product>()
            .OwnsOne(p => p.Metadata, ownedNavigationBuilder =>
            {
                ownedNavigationBuilder.ToJson();
                ownedNavigationBuilder.OwnsMany(m => m.Tags);
                ownedNavigationBuilder.OwnsOne(m => m.Dimensions);
            });
        
        // Temporal tables (SQL Server)
        modelBuilder.Entity<Customer>()
            .ToTable("Customers", tb => tb.IsTemporal(ttb =>
            {
                ttb.HasPeriodStart("ValidFrom");
                ttb.HasPeriodEnd("ValidTo");
                ttb.UseHistoryTable("CustomersHistory");
            }));
    }
    
    // Compiled models for startup performance
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder
            .UseModel(CompiledModels.AppDbContextModel.Instance)
            .EnableSensitiveDataLogging(false)
            .EnableServiceProviderCaching()
            .ConfigureWarnings(warnings => warnings
                .Ignore(CoreEventId.PossibleIncorrectRequiredNavigationWithQueryFilterInteractionWarning));
    }
}

// Services/OptimizedCustomerService.cs
public class OptimizedCustomerService
{
    private readonly AppDbContext _context;
    private readonly IMemoryCache _cache;
    private readonly ILogger<OptimizedCustomerService> _logger;
    
    public OptimizedCustomerService(
        AppDbContext context,
        IMemoryCache cache,
        ILogger<OptimizedCustomerService> logger)
    {
        _context = context;
        _cache = cache;
        _logger = logger;
    }
    
    // Optimized query with split queries
    public async Task<List<CustomerDto>> GetCustomersWithOrdersAsync(
        int page = 1,
        int pageSize = 20)
    {
        var query = _context.Customers
            .AsNoTracking()
            .AsSplitQuery() // Split query for multiple includes
            .Include(c => c.Orders)
                .ThenInclude(o => o.OrderItems)
                    .ThenInclude(oi => oi.Product)
            .Where(c => c.IsActive)
            .OrderBy(c => c.Name);
        
        // Pagination with keyset pagination for better performance
        var customers = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(c => new CustomerDto
            {
                Id = c.Id,
                Name = c.Name,
                OrderCount = c.Orders.Count(),
                TotalSpent = c.Orders.Sum(o => o.TotalAmount),
                LastOrderDate = c.Orders.Max(o => o.OrderDate)
            })
            .ToListAsync();
        
        return customers;
    }
    
    // Bulk operations with EF Core 8
    public async Task BulkUpdatePricesAsync(decimal increasePercentage)
    {
        // ExecuteUpdate for bulk updates without loading entities
        await _context.Products
            .Where(p => p.Category == "Electronics")
            .ExecuteUpdateAsync(setters => setters
                .SetProperty(p => p.Price, p => p.Price * (1 + increasePercentage / 100))
                .SetProperty(p => p.LastModified, DateTime.UtcNow));
    }
    
    // Bulk delete with ExecuteDelete
    public async Task BulkDeleteInactiveCustomersAsync()
    {
        var cutoffDate = DateTime.UtcNow.AddYears(-2);
        
        await _context.Customers
            .Where(c => c.LastActivityDate < cutoffDate && !c.Orders.Any())
            .ExecuteDeleteAsync();
    }
    
    // Raw SQL with interpolation (safe from SQL injection)
    public async Task<List<TopCustomer>> GetTopCustomersAsync(int year, int topN = 10)
    {
        var sql = $@"
            WITH CustomerStats AS (
                SELECT 
                    c.Id,
                    c.Name,
                    COUNT(DISTINCT o.Id) as OrderCount,
                    SUM(o.TotalAmount) as TotalSpent,
                    AVG(o.TotalAmount) as AverageOrderValue,
                    DATEDIFF(DAY, MIN(o.OrderDate), MAX(o.OrderDate)) as CustomerLifetimeDays
                FROM Customers c
                INNER JOIN Orders o ON c.Id = o.CustomerId
                WHERE YEAR(o.OrderDate) = {year}
                GROUP BY c.Id, c.Name
            )
            SELECT TOP({topN}) *
            FROM CustomerStats
            ORDER BY TotalSpent DESC";
        
        return await _context.Database
            .SqlQuery<TopCustomer>(sql)
            .ToListAsync();
    }
    
    // Compiled query for frequently used queries
    private static readonly Func<AppDbContext, int, Task<Customer?>> _getCustomerById =
        EF.CompileAsyncQuery((AppDbContext context, int id) =>
            context.Customers
                .Include(c => c.Orders)
                .FirstOrDefault(c => c.Id == id));
    
    public async Task<Customer?> GetCustomerByIdAsync(int id)
    {
        // Check cache first
        var cacheKey = $"customer_{id}";
        if (_cache.TryGetValue<Customer>(cacheKey, out var cached))
            return cached;
        
        // Use compiled query
        var customer = await _getCustomerById(_context, id);
        
        if (customer != null)
        {
            _cache.Set(cacheKey, customer, TimeSpan.FromMinutes(5));
        }
        
        return customer;
    }
    
    // Temporal queries (SQL Server)
    public async Task<List<CustomerHistory>> GetCustomerHistoryAsync(
        int customerId,
        DateTime from,
        DateTime to)
    {
        var history = await _context.Customers
            .TemporalBetween(from, to)
            .Where(c => c.Id == customerId)
            .OrderBy(c => EF.Property<DateTime>(c, "ValidFrom"))
            .Select(c => new CustomerHistory
            {
                Name = c.Name,
                Email = c.Email,
                ValidFrom = EF.Property<DateTime>(c, "ValidFrom"),
                ValidTo = EF.Property<DateTime>(c, "ValidTo")
            })
            .ToListAsync();
        
        return history;
    }
}
```

### 2. Entity Framework 6.x 最適化（.NET Framework）
```csharp
// EF6/AppContext.cs
using System.Data.Entity;
using System.Data.Entity.Infrastructure;
using System.Data.Entity.Core.Objects;
using System.Data.Entity.SqlServer;

public class AppContext : DbContext
{
    public AppContext() : base("name=AppConnection")
    {
        // Disable lazy loading by default
        Configuration.LazyLoadingEnabled = false;
        Configuration.ProxyCreationEnabled = false;
        
        // Disable auto detect changes for performance
        Configuration.AutoDetectChangesEnabled = false;
        
        // Set command timeout
        Database.CommandTimeout = 30;
        
        // Use legacy behavior for SQL Server
        Database.SetInitializer(new MigrateDatabaseToLatestVersion<AppContext, Configuration>());
    }
    
    public DbSet<Customer> Customers { get; set; }
    public DbSet<Order> Orders { get; set; }
    public DbSet<Product> Products { get; set; }
    
    protected override void OnModelCreating(DbModelBuilder modelBuilder)
    {
        // Table configuration
        modelBuilder.Entity<Customer>()
            .ToTable("Customers")
            .HasKey(c => c.Id);
        
        // Index configuration (EF 6.1+)
        modelBuilder.Entity<Customer>()
            .HasIndex(c => c.Email)
            .IsUnique()
            .HasName("IX_Customer_Email");
        
        // Complex type
        modelBuilder.ComplexType<Address>()
            .Property(a => a.Street).HasMaxLength(200);
        
        // Relationship configuration
        modelBuilder.Entity<Order>()
            .HasRequired(o => o.Customer)
            .WithMany(c => c.Orders)
            .HasForeignKey(o => o.CustomerId)
            .WillCascadeOnDelete(false);
        
        // Table splitting
        modelBuilder.Entity<Product>()
            .Map(m =>
            {
                m.Properties(p => new { p.Id, p.Name, p.Price });
                m.ToTable("Products");
            })
            .Map(m =>
            {
                m.Properties(p => new { p.Id, p.Description, p.Specifications });
                m.ToTable("ProductDetails");
            });
        
        // TPH (Table Per Hierarchy) with discriminator
        modelBuilder.Entity<PaymentMethod>()
            .Map<CreditCard>(m => m.Requires("PaymentType").HasValue("CC"))
            .Map<BankTransfer>(m => m.Requires("PaymentType").HasValue("BT"));
        
        // Stored procedure mapping
        modelBuilder.Entity<Customer>()
            .MapToStoredProcedures(s =>
            {
                s.Insert(i => i.HasName("Customer_Insert"));
                s.Update(u => u.HasName("Customer_Update"));
                s.Delete(d => d.HasName("Customer_Delete"));
            });
    }
}

// Services/EF6OptimizedService.cs
public class EF6OptimizedService
{
    private readonly AppContext _context;
    
    public EF6OptimizedService(AppContext context)
    {
        _context = context;
    }
    
    // Optimized query with eager loading
    public async Task<List<Customer>> GetCustomersWithOrdersAsync()
    {
        return await _context.Customers
            .AsNoTracking()
            .Include(c => c.Orders.Select(o => o.OrderItems))
            .Where(c => c.IsActive)
            .OrderBy(c => c.Name)
            .ToListAsync();
    }
    
    // Compiled query for performance
    private static readonly Func<AppContext, int, Customer> GetCustomerById =
        CompiledQuery.Compile((AppContext ctx, int id) =>
            ctx.Customers.FirstOrDefault(c => c.Id == id));
    
    public Customer GetCustomer(int id)
    {
        return GetCustomerById(_context, id);
    }
    
    // Bulk insert with SqlBulkCopy
    public async Task BulkInsertCustomersAsync(List<Customer> customers)
    {
        var dataTable = ConvertToDataTable(customers);
        
        using (var bulkCopy = new SqlBulkCopy(_context.Database.Connection.ConnectionString))
        {
            bulkCopy.DestinationTableName = "Customers";
            bulkCopy.BatchSize = 1000;
            bulkCopy.BulkCopyTimeout = 60;
            
            // Map columns
            bulkCopy.ColumnMappings.Add("Name", "Name");
            bulkCopy.ColumnMappings.Add("Email", "Email");
            bulkCopy.ColumnMappings.Add("Phone", "Phone");
            
            await bulkCopy.WriteToServerAsync(dataTable);
        }
    }
    
    // Raw SQL with parameters (safe from SQL injection)
    public async Task<List<Customer>> SearchCustomersAsync(string searchTerm)
    {
        var sql = @"
            SELECT * FROM Customers 
            WHERE Name LIKE @p0 + '%' 
               OR Email LIKE @p0 + '%'
            ORDER BY Name";
        
        return await _context.Database
            .SqlQuery<Customer>(sql, searchTerm)
            .ToListAsync();
    }
    
    // Find method optimization
    public async Task<Customer> FindCustomerOptimizedAsync(int id)
    {
        // First check local cache
        var local = _context.Customers.Local
            .FirstOrDefault(c => c.Id == id);
        
        if (local != null)
            return local;
        
        // Then check database
        return await _context.Customers.FindAsync(id);
    }
    
    // Batch updates with change tracking
    public async Task UpdateCustomerStatusBatchAsync(List<int> customerIds, string newStatus)
    {
        // Disable auto-detect changes for batch operations
        _context.Configuration.AutoDetectChangesEnabled = false;
        
        try
        {
            foreach (var id in customerIds)
            {
                var customer = new Customer { Id = id, Status = newStatus };
                _context.Customers.Attach(customer);
                _context.Entry(customer).Property(c => c.Status).IsModified = true;
            }
            
            // Detect changes once before saving
            _context.ChangeTracker.DetectChanges();
            await _context.SaveChangesAsync();
        }
        finally
        {
            _context.Configuration.AutoDetectChangesEnabled = true;
        }
    }
}
```

## バージョン別機能対応表

| 機能 | EF Core 8 | EF Core 7 | EF Core 6 | EF Core 5 | EF 6.x |
|------|-----------|-----------|-----------|-----------|--------|
| Complex Types | ✅ | ❌ | ❌ | ❌ | ✅ |
| ExecuteUpdate/Delete | ✅ | ✅ | ❌ | ❌ | ❌ |
| Compiled Models | ✅ | ✅ | ✅ | ❌ | ❌ |
| Temporal Tables | ✅ | ✅ | ✅ | ❌ | ❌ |
| JSON Columns | ✅ | ✅ | ❌ | ❌ | ❌ |
| Split Queries | ✅ | ✅ | ✅ | ✅ | ❌ |
| Compiled Queries | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bulk Operations | ✅ Native | ✅ Native | 📦 Package | 📦 Package | 📦 SqlBulkCopy |
| Global Query Filters | ✅ | ✅ | ✅ | ✅ | ❌ |
| Lazy Loading Proxies | ✅ | ✅ | ✅ | ✅ | ✅ |
| Value Converters | ✅ | ✅ | ✅ | ✅ | ❌ |
| Shadow Properties | ✅ | ✅ | ✅ | ✅ | ❌ |
| Keyless Entities | ✅ | ✅ | ✅ | ✅ | ❌ |
| Table Splitting | ✅ | ✅ | ✅ | ✅ | ✅ |
| Owned Entities | ✅ | ✅ | ✅ | ✅ | ❌ |
| Database Functions | ✅ | ✅ | ✅ | ✅ | ⚠️ Limited |

## パフォーマンス最適化ベストプラクティス

### N+1問題の解決
```csharp
// ❌ Bad: N+1 queries
var customers = context.Customers.ToList();
foreach (var customer in customers)
{
    var orderCount = customer.Orders.Count(); // Additional query for each customer
}

// ✅ Good: Single query with Include
var customers = context.Customers
    .Include(c => c.Orders)
    .ToList();

// ✅ Better: Project to DTO
var customerStats = context.Customers
    .Select(c => new CustomerStatsDto
    {
        Name = c.Name,
        OrderCount = c.Orders.Count()
    })
    .ToList();
```

### クエリ分割戦略
```csharp
// Cartesian explosion prevention
var orders = context.Orders
    .AsSplitQuery() // EF Core 5+
    .Include(o => o.OrderItems)
    .Include(o => o.Payments)
    .Include(o => o.Shipments)
    .ToList();
```

### メモリ効率的なページング
```csharp
// Keyset pagination (faster than OFFSET)
public async Task<List<Product>> GetProductsKeysetAsync(
    int? lastId = null,
    int pageSize = 20)
{
    var query = _context.Products.AsQueryable();
    
    if (lastId.HasValue)
    {
        query = query.Where(p => p.Id > lastId.Value);
    }
    
    return await query
        .OrderBy(p => p.Id)
        .Take(pageSize)
        .ToListAsync();
}
```

## 出力レポート
```markdown
# Entity Framework 最適化レポート

## 実施項目
✅ クエリ最適化: 完了
✅ インデックス追加: 12個
✅ N+1問題解決: 8箇所
✅ バルク操作導入: 実装済み
✅ キャッシュ戦略: 設定完了

## パフォーマンス改善
- クエリ実行時間: 85%削減
- メモリ使用量: 60%削減
- データベース接続数: 70%削減
- 起動時間: 40%短縮（Compiled Models）

## 推奨事項
1. EF Core 8への移行（EF6案件）
2. Compiled Models導入
3. 読み取り専用クエリの最適化
4. バルク操作の活用
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: Entity Framework全バージョン最適化

---
*このコマンドはEntity Frameworkの全バージョンに対応した最適化に特化しています。*