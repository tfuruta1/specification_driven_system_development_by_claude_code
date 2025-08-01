# Entity Framework 6 ガイド - エンタープライズアプリケーション開発

## 1. Entity Framework 6 の基本設定

### DbContext の設定
```csharp
public class EnterpriseDbContext : DbContext
{
    public EnterpriseDbContext() : base("name=DefaultConnection")
    {
        // 遅延読み込みの設定
        Configuration.LazyLoadingEnabled = false;
        Configuration.ProxyCreationEnabled = false;
        
        // パフォーマンス最適化
        Configuration.AutoDetectChangesEnabled = false;
        Configuration.ValidateOnSaveEnabled = false;
        
        // ログ出力（開発時のみ）
#if DEBUG
        Database.Log = sql => Debug.WriteLine(sql);
#endif
    }
    
    // DbSet プロパティ
    public DbSet<Customer> Customers { get; set; }
    public DbSet<Order> Orders { get; set; }
    public DbSet<Product> Products { get; set; }
    public DbSet<OrderDetail> OrderDetails { get; set; }
    
    protected override void OnModelCreating(DbModelBuilder modelBuilder)
    {
        // 規約の設定
        modelBuilder.Conventions.Remove<PluralizingTableNameConvention>();
        modelBuilder.Conventions.Remove<OneToManyCascadeDeleteConvention>();
        
        // Fluent API による設定
        ConfigureCustomerEntity(modelBuilder);
        ConfigureOrderEntity(modelBuilder);
        ConfigureProductEntity(modelBuilder);
        
        // グローバルフィルター
        modelBuilder.Filter("IsDeleted", (ISoftDeletable d) => d.IsDeleted, false);
        modelBuilder.Filter("TenantId", (IMultiTenant t, int tenantId) => t.TenantId == tenantId, 0);
        
        base.OnModelCreating(modelBuilder);
    }
    
    private void ConfigureCustomerEntity(DbModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Customer>()
            .ToTable("Customers")
            .HasKey(c => c.Id);
        
        modelBuilder.Entity<Customer>()
            .Property(c => c.Name)
            .IsRequired()
            .HasMaxLength(200)
            .HasColumnType("nvarchar");
        
        modelBuilder.Entity<Customer>()
            .Property(c => c.Email)
            .IsRequired()
            .HasMaxLength(100)
            .HasColumnAnnotation(
                IndexAnnotation.AnnotationName,
                new IndexAnnotation(new IndexAttribute("IX_Customer_Email") { IsUnique = true }));
        
        modelBuilder.Entity<Customer>()
            .Property(c => c.CreditLimit)
            .HasPrecision(18, 2);
        
        // リレーションシップ
        modelBuilder.Entity<Customer>()
            .HasMany(c => c.Orders)
            .WithRequired(o => o.Customer)
            .HasForeignKey(o => o.CustomerId)
            .WillCascadeOnDelete(false);
        
        // 複合インデックス
        modelBuilder.Entity<Customer>()
            .HasIndex(c => new { c.IsActive, c.CreatedDate })
            .HasName("IX_Customer_Active_Created");
    }
    
    // 保存時の自動処理
    public override int SaveChanges()
    {
        ApplyAuditInfo();
        return base.SaveChanges();
    }
    
    public override async Task<int> SaveChangesAsync()
    {
        ApplyAuditInfo();
        return await base.SaveChangesAsync();
    }
    
    private void ApplyAuditInfo()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.Entity is IAuditable && 
                      (e.State == EntityState.Added || e.State == EntityState.Modified));
        
        var currentUser = Thread.CurrentPrincipal?.Identity?.Name ?? "System";
        var currentTime = DateTime.UtcNow;
        
        foreach (var entry in entries)
        {
            var entity = (IAuditable)entry.Entity;
            
            if (entry.State == EntityState.Added)
            {
                entity.CreatedDate = currentTime;
                entity.CreatedBy = currentUser;
            }
            
            entity.ModifiedDate = currentTime;
            entity.ModifiedBy = currentUser;
        }
    }
}
```

### 接続文字列の設定
```xml
<configuration>
  <connectionStrings>
    <add name="DefaultConnection" 
         connectionString="Data Source=.\SQLEXPRESS;Initial Catalog=EnterpriseDB;Integrated Security=True;MultipleActiveResultSets=True;Application Name=EnterpriseApp"
         providerName="System.Data.SqlClient" />
  </connectionStrings>
  
  <entityFramework>
    <defaultConnectionFactory type="System.Data.Entity.Infrastructure.LocalDbConnectionFactory, EntityFramework">
      <parameters>
        <parameter value="mssqllocaldb" />
      </parameters>
    </defaultConnectionFactory>
    
    <providers>
      <provider invariantName="System.Data.SqlClient" 
                type="System.Data.Entity.SqlServer.SqlProviderServices, EntityFramework.SqlServer" />
    </providers>
    
    <interceptors>
      <interceptor type="EnterpriseApp.Data.Interceptors.CommandInterceptor, EnterpriseApp.Data" />
    </interceptors>
  </entityFramework>
</configuration>
```

## 2. Code First Migration

### Migration の設定
```csharp
internal sealed class Configuration : DbMigrationsConfiguration<EnterpriseDbContext>
{
    public Configuration()
    {
        AutomaticMigrationsEnabled = false;
        AutomaticMigrationDataLossAllowed = false;
        
        // Migration履歴テーブルのカスタマイズ
        SetHistoryContextFactory("System.Data.SqlClient", 
            (conn, schema) => new CustomHistoryContext(conn, schema));
    }
    
    protected override void Seed(EnterpriseDbContext context)
    {
        // マスターデータの投入
        SeedLookupData(context);
        SeedSystemData(context);
        
        // 開発環境用のテストデータ
#if DEBUG
        SeedTestData(context);
#endif
    }
    
    private void SeedLookupData(EnterpriseDbContext context)
    {
        // AddOrUpdate を使用して冪等性を保証
        context.CustomerTypes.AddOrUpdate(
            ct => ct.Code,
            new CustomerType { Code = "IND", Name = "個人", DisplayOrder = 1 },
            new CustomerType { Code = "COR", Name = "法人", DisplayOrder = 2 },
            new CustomerType { Code = "GOV", Name = "官公庁", DisplayOrder = 3 }
        );
        
        context.OrderStatuses.AddOrUpdate(
            os => os.Code,
            new OrderStatus { Code = "DFT", Name = "下書き", DisplayOrder = 1 },
            new OrderStatus { Code = "CNF", Name = "確定", DisplayOrder = 2 },
            new OrderStatus { Code = "SHP", Name = "出荷済", DisplayOrder = 3 },
            new OrderStatus { Code = "CMP", Name = "完了", DisplayOrder = 4 },
            new OrderStatus { Code = "CAN", Name = "キャンセル", DisplayOrder = 99 }
        );
    }
}

// カスタムMigration
public partial class AddCustomerCreditLimit : DbMigration
{
    public override void Up()
    {
        AddColumn("dbo.Customers", "CreditLimit", c => c.Decimal(nullable: false, precision: 18, scale: 2, defaultValue: 0));
        
        // 既存データの更新
        Sql(@"
            UPDATE c
            SET c.CreditLimit = COALESCE(o.TotalAmount, 0) * 1.5
            FROM dbo.Customers c
            LEFT JOIN (
                SELECT CustomerId, SUM(TotalAmount) as TotalAmount
                FROM dbo.Orders
                WHERE OrderStatusId NOT IN (99) -- キャンセル以外
                GROUP BY CustomerId
            ) o ON c.Id = o.CustomerId
        ");
        
        // インデックスの作成
        CreateIndex("dbo.Customers", "CreditLimit");
    }
    
    public override void Down()
    {
        DropIndex("dbo.Customers", new[] { "CreditLimit" });
        DropColumn("dbo.Customers", "CreditLimit");
    }
}
```

## 3. クエリ最適化

### Eager Loading（事前読み込み）
```csharp
public class CustomerRepository : ICustomerRepository
{
    private readonly EnterpriseDbContext _context;
    
    public async Task<Customer> GetCustomerWithOrdersAsync(int customerId)
    {
        return await _context.Customers
            .Include(c => c.Orders.Select(o => o.OrderDetails.Select(od => od.Product)))
            .Include(c => c.Addresses)
            .Include(c => c.Contacts)
            .AsNoTracking()
            .FirstOrDefaultAsync(c => c.Id == customerId);
    }
    
    public async Task<IEnumerable<Customer>> GetActiveCustomersAsync()
    {
        // 複数レベルのInclude
        return await _context.Customers
            .Include(c => c.CustomerType)
            .Include(c => c.Orders.Select(o => o.OrderStatus))
            .Where(c => c.IsActive && !c.IsDeleted)
            .OrderBy(c => c.Name)
            .AsNoTracking()
            .ToListAsync();
    }
}
```

### Projection（射影）
```csharp
public class CustomerQueryService
{
    public async Task<IEnumerable<CustomerSummaryDto>> GetCustomerSummariesAsync()
    {
        return await _context.Customers
            .Where(c => c.IsActive)
            .Select(c => new CustomerSummaryDto
            {
                Id = c.Id,
                Name = c.Name,
                Email = c.Email,
                TotalOrders = c.Orders.Count(o => o.OrderStatusId != 99),
                TotalAmount = c.Orders
                    .Where(o => o.OrderStatusId != 99)
                    .Sum(o => (decimal?)o.TotalAmount) ?? 0,
                LastOrderDate = c.Orders
                    .Where(o => o.OrderStatusId != 99)
                    .OrderByDescending(o => o.OrderDate)
                    .Select(o => o.OrderDate)
                    .FirstOrDefault()
            })
            .ToListAsync();
    }
    
    // 動的プロジェクション
    public IQueryable<TDto> ProjectTo<TEntity, TDto>(
        IQueryable<TEntity> query,
        Expression<Func<TEntity, TDto>> selector)
        where TEntity : class
    {
        return query.Select(selector);
    }
}
```

### バッチ処理
```csharp
public class BatchOperationService
{
    private readonly EnterpriseDbContext _context;
    
    public async Task UpdateProductPricesAsync(decimal increasePercent)
    {
        const int batchSize = 1000;
        var processedCount = 0;
        
        // AutoDetectChanges を無効化
        _context.Configuration.AutoDetectChangesEnabled = false;
        
        try
        {
            var totalProducts = await _context.Products.CountAsync(p => p.IsActive);
            
            while (processedCount < totalProducts)
            {
                var products = await _context.Products
                    .Where(p => p.IsActive)
                    .OrderBy(p => p.Id)
                    .Skip(processedCount)
                    .Take(batchSize)
                    .ToListAsync();
                
                foreach (var product in products)
                {
                    product.StandardPrice *= (1 + increasePercent / 100);
                    _context.Entry(product).State = EntityState.Modified;
                }
                
                await _context.SaveChangesAsync();
                
                processedCount += products.Count;
                
                // メモリ解放
                _context.DetachAllEntities();
            }
        }
        finally
        {
            _context.Configuration.AutoDetectChangesEnabled = true;
        }
    }
    
    // Entity Framework Extended を使用したバルク操作
    public async Task BulkDeleteInactiveCustomersAsync()
    {
        await _context.Customers
            .Where(c => !c.IsActive && c.ModifiedDate < DateTime.UtcNow.AddYears(-1))
            .Delete();
    }
    
    public async Task BulkUpdateAsync()
    {
        await _context.Products
            .Where(p => p.CategoryId == 5)
            .Update(p => new Product { IsDiscontinued = true, DiscontinuedDate = DateTime.UtcNow });
    }
}
```

## 4. トランザクション管理

### 分散トランザクション
```csharp
public class TransactionService
{
    public async Task<OrderResult> ProcessOrderWithInventoryAsync(Order order)
    {
        using (var scope = new TransactionScope(
            TransactionScopeOption.Required,
            new TransactionOptions { IsolationLevel = IsolationLevel.ReadCommitted },
            TransactionScopeAsyncFlowOption.Enabled))
        {
            try
            {
                // 注文の作成
                using (var orderContext = new EnterpriseDbContext())
                {
                    orderContext.Orders.Add(order);
                    await orderContext.SaveChangesAsync();
                }
                
                // 在庫の更新（別のデータベース）
                using (var inventoryContext = new InventoryDbContext())
                {
                    foreach (var item in order.OrderDetails)
                    {
                        var inventory = await inventoryContext.Inventories
                            .FirstOrDefaultAsync(i => i.ProductId == item.ProductId);
                        
                        if (inventory == null || inventory.AvailableQuantity < item.Quantity)
                        {
                            throw new InsufficientInventoryException(
                                $"在庫が不足しています。商品ID: {item.ProductId}");
                        }
                        
                        inventory.AvailableQuantity -= item.Quantity;
                        inventory.ReservedQuantity += item.Quantity;
                    }
                    
                    await inventoryContext.SaveChangesAsync();
                }
                
                // 成功時のみコミット
                scope.Complete();
                
                return OrderResult.Success(order.Id);
            }
            catch (Exception ex)
            {
                // ロールバックは自動的に行われる
                return OrderResult.Failed(ex.Message);
            }
        }
    }
}
```

### Retry Policy
```csharp
public class ResilientDbContext : EnterpriseDbContext
{
    protected override void OnModelCreating(DbModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        
        // SQL Database execution strategy
        SetExecutionStrategy("System.Data.SqlClient", 
            () => new SqlAzureExecutionStrategy());
    }
}

// カスタム実行戦略
public class CustomExecutionStrategy : DbExecutionStrategy
{
    public CustomExecutionStrategy() : base(5, TimeSpan.FromSeconds(10))
    {
    }
    
    protected override bool ShouldRetryOn(Exception exception)
    {
        // タイムアウトと接続エラーのみリトライ
        return exception is SqlException sqlException &&
               (sqlException.Number == -2 ||  // Timeout
                sqlException.Number == 20 ||   // Instance not found
                sqlException.Number == 64 ||   // Instance not accessible
                sqlException.Number == 233 ||  // Connection initialization error
                sqlException.Number == 10053 || // Transport-level error
                sqlException.Number == 10054 || // Transport-level error
                sqlException.Number == 10060 || // Network timeout
                sqlException.Number == 40197 || // Service error
                sqlException.Number == 40501 || // Service busy
                sqlException.Number == 40613);  // Database unavailable
    }
}
```

## 5. パフォーマンスチューニング

### コンパイル済みクエリ
```csharp
public static class CompiledQueries
{
    public static readonly Func<EnterpriseDbContext, int, Task<Customer>> 
        GetCustomerById = EF.CompileAsyncQuery(
            (EnterpriseDbContext context, int id) =>
                context.Customers
                    .Include(c => c.CustomerType)
                    .FirstOrDefault(c => c.Id == id));
    
    public static readonly Func<EnterpriseDbContext, string, IQueryable<Customer>> 
        SearchCustomersByName = EF.CompileQuery(
            (EnterpriseDbContext context, string searchTerm) =>
                context.Customers
                    .Where(c => c.Name.Contains(searchTerm))
                    .OrderBy(c => c.Name));
    
    public static readonly Func<EnterpriseDbContext, DateTime, DateTime, IQueryable<Order>> 
        GetOrdersByDateRange = EF.CompileQuery(
            (EnterpriseDbContext context, DateTime startDate, DateTime endDate) =>
                context.Orders
                    .Include(o => o.Customer)
                    .Include(o => o.OrderDetails)
                    .Where(o => o.OrderDate >= startDate && o.OrderDate <= endDate));
}

// 使用例
public class OptimizedRepository
{
    private readonly EnterpriseDbContext _context;
    
    public async Task<Customer> GetCustomerAsync(int id)
    {
        return await CompiledQueries.GetCustomerById(_context, id);
    }
}
```

### 非同期処理の最適化
```csharp
public class AsyncDataService
{
    public async Task<CustomerAnalytics> GetCustomerAnalyticsAsync(int customerId)
    {
        // 複数の非同期クエリを並列実行
        var customerTask = _context.Customers
            .Include(c => c.CustomerType)
            .FirstOrDefaultAsync(c => c.Id == customerId);
        
        var ordersTask = _context.Orders
            .Where(o => o.CustomerId == customerId)
            .ToListAsync();
        
        var totalAmountTask = _context.Orders
            .Where(o => o.CustomerId == customerId && o.OrderStatusId != 99)
            .SumAsync(o => (decimal?)o.TotalAmount) ?? 0;
        
        var productCountTask = _context.Orders
            .Where(o => o.CustomerId == customerId)
            .SelectMany(o => o.OrderDetails)
            .Select(od => od.ProductId)
            .Distinct()
            .CountAsync();
        
        // すべてのタスクを待機
        await Task.WhenAll(customerTask, ordersTask, totalAmountTask, productCountTask);
        
        return new CustomerAnalytics
        {
            Customer = await customerTask,
            Orders = await ordersTask,
            TotalPurchaseAmount = await totalAmountTask,
            UniqueProductsPurchased = await productCountTask
        };
    }
}
```

## 6. 監査とログ

### Interceptor の実装
```csharp
public class CommandInterceptor : IDbCommandInterceptor
{
    private readonly ILogger _logger;
    
    public CommandInterceptor()
    {
        _logger = LogManager.GetCurrentClassLogger();
    }
    
    public void NonQueryExecuting(DbCommand command, DbCommandInterceptionContext<int> interceptionContext)
    {
        LogCommand(command, interceptionContext);
    }
    
    public void ReaderExecuting(DbCommand command, DbCommandInterceptionContext<DbDataReader> interceptionContext)
    {
        LogCommand(command, interceptionContext);
    }
    
    private void LogCommand<T>(DbCommand command, DbCommandInterceptionContext<T> interceptionContext)
    {
        var commandText = command.CommandText;
        var parameters = command.Parameters.Cast<DbParameter>()
            .Select(p => $"{p.ParameterName}={p.Value}")
            .ToList();
        
        _logger.Debug($"Executing SQL: {commandText}");
        if (parameters.Any())
        {
            _logger.Debug($"Parameters: {string.Join(", ", parameters)}");
        }
        
        // 実行時間の計測
        interceptionContext.UserState = Stopwatch.StartNew();
    }
    
    public void NonQueryExecuted(DbCommand command, DbCommandInterceptionContext<int> interceptionContext)
    {
        LogExecutionTime(command, interceptionContext);
    }
    
    public void ReaderExecuted(DbCommand command, DbCommandInterceptionContext<DbDataReader> interceptionContext)
    {
        LogExecutionTime(command, interceptionContext);
    }
    
    private void LogExecutionTime<T>(DbCommand command, DbCommandInterceptionContext<T> interceptionContext)
    {
        var stopwatch = interceptionContext.UserState as Stopwatch;
        if (stopwatch != null)
        {
            stopwatch.Stop();
            var duration = stopwatch.ElapsedMilliseconds;
            
            if (duration > 1000) // 1秒以上かかったクエリ
            {
                _logger.Warn($"Slow query detected ({duration}ms): {command.CommandText}");
            }
        }
        
        if (interceptionContext.Exception != null)
        {
            _logger.Error(interceptionContext.Exception, 
                $"Error executing command: {command.CommandText}");
        }
    }
}
```

このガイドに従うことで、Entity Framework 6を使用した高性能で保守性の高いデータアクセス層を構築できます。