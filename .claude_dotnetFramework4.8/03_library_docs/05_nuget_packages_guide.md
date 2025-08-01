# .NET Framework 4.8 NuGetパッケージ完全ガイド

## 1. NuGetパッケージ管理の基礎

### パッケージマネージャーコンソールコマンド
```powershell
# パッケージのインストール
Install-Package Newtonsoft.Json -Version 13.0.1

# 特定のプロジェクトにインストール
Install-Package EntityFramework -ProjectName EnterpriseApp.Data

# プレリリース版のインストール
Install-Package NLog -IncludePrerelease

# パッケージの更新
Update-Package Newtonsoft.Json

# すべてのパッケージを更新
Update-Package

# パッケージのアンインストール
Uninstall-Package Newtonsoft.Json

# インストール済みパッケージの一覧
Get-Package

# 利用可能なパッケージの検索
Find-Package AutoMapper
```

### .NET CLI コマンド（.NET Framework 4.8でも使用可能）
```bash
# パッケージの追加
dotnet add package Newtonsoft.Json --version 13.0.1

# パッケージの削除
dotnet remove package Newtonsoft.Json

# パッケージの復元
dotnet restore

# 古いパッケージの確認
dotnet list package --outdated
```

## 2. エンタープライズ開発必須パッケージ

### データアクセス・ORM

#### Entity Framework 6
```xml
<PackageReference Include="EntityFramework" Version="6.4.4" />
```
```csharp
// DbContext の実装例
public class EnterpriseDbContext : DbContext
{
    public EnterpriseDbContext() : base("name=DefaultConnection")
    {
        Configuration.LazyLoadingEnabled = false;
        Configuration.ProxyCreationEnabled = false;
    }
    
    public DbSet<Customer> Customers { get; set; }
    public DbSet<Order> Orders { get; set; }
    
    protected override void OnModelCreating(DbModelBuilder modelBuilder)
    {
        // Fluent API 設定
        modelBuilder.Entity<Customer>()
            .HasMany(c => c.Orders)
            .WithRequired(o => o.Customer)
            .WillCascadeOnDelete(false);
    }
}
```

#### Dapper（軽量ORM）
```xml
<PackageReference Include="Dapper" Version="2.0.123" />
<PackageReference Include="Dapper.Contrib" Version="2.0.78" />
```
```csharp
public class DapperRepository
{
    private readonly string _connectionString;
    
    public async Task<IEnumerable<Customer>> GetCustomersAsync()
    {
        using (var connection = new SqlConnection(_connectionString))
        {
            // 基本的なクエリ
            return await connection.QueryAsync<Customer>(
                "SELECT * FROM Customers WHERE IsActive = @IsActive",
                new { IsActive = true });
        }
    }
    
    public async Task<Customer> GetCustomerWithOrdersAsync(int customerId)
    {
        using (var connection = new SqlConnection(_connectionString))
        {
            // マルチマッピング
            var sql = @"
                SELECT c.*, o.*
                FROM Customers c
                LEFT JOIN Orders o ON c.Id = o.CustomerId
                WHERE c.Id = @customerId";
            
            var customerDict = new Dictionary<int, Customer>();
            
            return (await connection.QueryAsync<Customer, Order, Customer>(
                sql,
                (customer, order) =>
                {
                    if (!customerDict.TryGetValue(customer.Id, out var currentCustomer))
                    {
                        currentCustomer = customer;
                        currentCustomer.Orders = new List<Order>();
                        customerDict.Add(currentCustomer.Id, currentCustomer);
                    }
                    
                    if (order != null)
                        currentCustomer.Orders.Add(order);
                    
                    return currentCustomer;
                },
                new { customerId },
                splitOn: "Id")).FirstOrDefault();
        }
    }
}
```

### 依存性注入（DI）コンテナ

#### Unity Container
```xml
<PackageReference Include="Unity.Container" Version="5.11.11" />
<PackageReference Include="Unity.Interception" Version="5.11.1" />
```
```csharp
public class UnityConfig
{
    public static IUnityContainer RegisterComponents()
    {
        var container = new UnityContainer();
        
        // 基本的な登録
        container.RegisterType<ICustomerService, CustomerService>();
        
        // シングルトン登録
        container.RegisterType<ILogger, Logger>(
            new ContainerControlledLifetimeManager());
        
        // ファクトリー登録
        container.RegisterFactory<Func<IUnitOfWork>>(
            c => () => c.Resolve<IUnitOfWork>());
        
        // インターセプター登録（AOP）
        container.AddNewExtension<Interception>();
        container.RegisterType<IOrderService, OrderService>(
            new Interceptor<InterfaceInterceptor>(),
            new InterceptionBehavior<LoggingBehavior>());
        
        return container;
    }
}

// AOP実装例
public class LoggingBehavior : IInterceptionBehavior
{
    private readonly ILogger _logger;
    
    public IMethodReturn Invoke(IMethodInvocation input, GetNextInterceptionBehaviorDelegate getNext)
    {
        _logger.Info($"Calling {input.MethodBase.Name}");
        var result = getNext()(input, getNext);
        
        if (result.Exception != null)
            _logger.Error(result.Exception);
        else
            _logger.Info($"Completed {input.MethodBase.Name}");
        
        return result;
    }
}
```

#### Autofac
```xml
<PackageReference Include="Autofac" Version="6.4.0" />
<PackageReference Include="Autofac.Extensions.DependencyInjection" Version="8.0.0" />
```
```csharp
public class AutofacConfig
{
    public static IContainer BuildContainer()
    {
        var builder = new ContainerBuilder();
        
        // アセンブリスキャン登録
        builder.RegisterAssemblyTypes(typeof(CustomerService).Assembly)
            .Where(t => t.Name.EndsWith("Service"))
            .AsImplementedInterfaces()
            .InstancePerLifetimeScope();
        
        // モジュール登録
        builder.RegisterModule<DataAccessModule>();
        
        // デコレーター登録
        builder.RegisterType<CustomerRepository>()
            .As<ICustomerRepository>();
        builder.RegisterDecorator<CachedRepository, ICustomerRepository>();
        
        return builder.Build();
    }
}
```

### ロギング

#### NLog
```xml
<PackageReference Include="NLog" Version="5.0.5" />
<PackageReference Include="NLog.Config" Version="5.0.5" />
```
```xml
<!-- NLog.config -->
<?xml version="1.0" encoding="utf-8" ?>
<nlog xmlns="http://www.nlog-project.org/schemas/NLog.xsd"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  
  <targets>
    <target name="file" xsi:type="File"
            fileName="${basedir}/logs/${shortdate}.log"
            layout="${longdate} ${uppercase:${level}} ${logger} ${message} ${exception:format=tostring}" />
    
    <target name="database" xsi:type="Database"
            connectionString="Data Source=server;Initial Catalog=LogDB;Integrated Security=True">
      <commandText>
        INSERT INTO Logs (Date, Level, Logger, Message, Exception)
        VALUES (@Date, @Level, @Logger, @Message, @Exception)
      </commandText>
      <parameter name="@Date" layout="${date}" />
      <parameter name="@Level" layout="${level}" />
      <parameter name="@Logger" layout="${logger}" />
      <parameter name="@Message" layout="${message}" />
      <parameter name="@Exception" layout="${exception:tostring}" />
    </target>
  </targets>
  
  <rules>
    <logger name="*" minlevel="Debug" writeTo="file" />
    <logger name="*" minlevel="Error" writeTo="database" />
  </rules>
</nlog>
```

#### Serilog
```xml
<PackageReference Include="Serilog" Version="2.12.0" />
<PackageReference Include="Serilog.Sinks.File" Version="5.0.0" />
<PackageReference Include="Serilog.Sinks.MSSqlServer" Version="6.0.0" />
```
```csharp
public class SerilogConfig
{
    public static void ConfigureLogging()
    {
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .MinimumLevel.Override("Microsoft", LogEventLevel.Information)
            .Enrich.FromLogContext()
            .Enrich.WithMachineName()
            .Enrich.WithThreadId()
            .WriteTo.File(
                path: @"logs\app-.txt",
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 30,
                outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}")
            .WriteTo.MSSqlServer(
                connectionString: ConfigurationManager.ConnectionStrings["LogDb"].ConnectionString,
                tableName: "Logs",
                autoCreateSqlTable: true)
            .CreateLogger();
    }
}
```

### JSONシリアライゼーション

#### Newtonsoft.Json
```xml
<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
```
```csharp
public class JsonSerializationExample
{
    public void ConfigureJson()
    {
        var settings = new JsonSerializerSettings
        {
            ContractResolver = new CamelCasePropertyNamesContractResolver(),
            DateFormatHandling = DateFormatHandling.IsoDateFormat,
            NullValueHandling = NullValueHandling.Ignore,
            ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
            Converters = new List<JsonConverter>
            {
                new StringEnumConverter(),
                new IsoDateTimeConverter { DateTimeFormat = "yyyy-MM-dd HH:mm:ss" }
            }
        };
        
        // カスタムコンバーター
        public class DecimalFormatConverter : JsonConverter<decimal>
        {
            public override void WriteJson(JsonWriter writer, decimal value, JsonSerializer serializer)
            {
                writer.WriteValue(value.ToString("F2"));
            }
        }
    }
}
```

### マッピング

#### AutoMapper
```xml
<PackageReference Include="AutoMapper" Version="12.0.1" />
```
```csharp
public class AutoMapperConfig
{
    public static MapperConfiguration CreateConfiguration()
    {
        return new MapperConfiguration(cfg =>
        {
            // 基本的なマッピング
            cfg.CreateMap<Customer, CustomerDto>();
            
            // カスタムマッピング
            cfg.CreateMap<Order, OrderDto>()
                .ForMember(dest => dest.CustomerName, 
                    opt => opt.MapFrom(src => src.Customer.Name))
                .ForMember(dest => dest.TotalAmount,
                    opt => opt.MapFrom(src => src.OrderItems.Sum(i => i.Quantity * i.UnitPrice)));
            
            // 条件付きマッピング
            cfg.CreateMap<Product, ProductDto>()
                .ForMember(dest => dest.Status,
                    opt => opt.MapFrom(src => src.IsActive ? "Active" : "Inactive"))
                .ForMember(dest => dest.StockLevel,
                    opt => opt.MapFrom(src => 
                        src.Quantity > 100 ? "High" :
                        src.Quantity > 20 ? "Medium" : "Low"));
            
            // プロファイル使用
            cfg.AddProfile<CustomerMappingProfile>();
        });
    }
}

public class CustomerMappingProfile : Profile
{
    public CustomerMappingProfile()
    {
        CreateMap<Customer, CustomerViewModel>()
            .ReverseMap()
            .ForMember(dest => dest.ModifiedDate, opt => opt.Ignore());
    }
}
```

### バリデーション

#### FluentValidation
```xml
<PackageReference Include="FluentValidation" Version="11.5.2" />
```
```csharp
public class CustomerValidator : AbstractValidator<Customer>
{
    public CustomerValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("名前は必須です")
            .MaximumLength(100).WithMessage("名前は100文字以内で入力してください");
        
        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("メールアドレスは必須です")
            .EmailAddress().WithMessage("有効なメールアドレスを入力してください")
            .MustAsync(BeUniqueEmail).WithMessage("このメールアドレスは既に登録されています");
        
        RuleFor(x => x.CreditLimit)
            .GreaterThanOrEqualTo(0).WithMessage("与信限度額は0以上で入力してください")
            .LessThanOrEqualTo(10000000).WithMessage("与信限度額は1000万円以下で入力してください");
        
        // 複雑な検証
        RuleFor(x => x)
            .Custom((customer, context) =>
            {
                if (customer.Type == CustomerType.Corporate && string.IsNullOrEmpty(customer.CompanyName))
                {
                    context.AddFailure("CompanyName", "法人顧客の場合、会社名は必須です");
                }
            });
    }
    
    private async Task<bool> BeUniqueEmail(string email, CancellationToken cancellationToken)
    {
        // データベースチェック
        return !await _repository.EmailExistsAsync(email);
    }
}
```

### HTTPクライアント

#### RestSharp
```xml
<PackageReference Include="RestSharp" Version="108.0.3" />
```
```csharp
public class RestApiClient
{
    private readonly RestClient _client;
    
    public RestApiClient(string baseUrl)
    {
        var options = new RestClientOptions(baseUrl)
        {
            MaxTimeout = 30000,
            ThrowOnAnyError = true,
            Authenticator = new JwtAuthenticator(_tokenService.GetToken())
        };
        
        _client = new RestClient(options);
    }
    
    public async Task<T> GetAsync<T>(string resource)
    {
        var request = new RestRequest(resource);
        request.AddHeader("Accept", "application/json");
        
        var response = await _client.ExecuteAsync<T>(request);
        return response.Data;
    }
    
    public async Task<T> PostAsync<T>(string resource, object body)
    {
        var request = new RestRequest(resource, Method.Post);
        request.AddJsonBody(body);
        
        var response = await _client.ExecuteAsync<T>(request);
        return response.Data;
    }
}
```

#### Refit
```xml
<PackageReference Include="Refit" Version="6.3.2" />
```
```csharp
// API インターフェース定義
public interface ICustomerApi
{
    [Get("/api/customers")]
    Task<List<Customer>> GetCustomersAsync();
    
    [Get("/api/customers/{id}")]
    Task<Customer> GetCustomerAsync(int id);
    
    [Post("/api/customers")]
    Task<Customer> CreateCustomerAsync([Body] Customer customer);
    
    [Put("/api/customers/{id}")]
    Task<Customer> UpdateCustomerAsync(int id, [Body] Customer customer);
    
    [Delete("/api/customers/{id}")]
    Task DeleteCustomerAsync(int id);
    
    [Get("/api/customers/search")]
    Task<List<Customer>> SearchCustomersAsync([Query] string term, [Query] int? limit = 10);
}

// 使用例
var api = RestService.For<ICustomerApi>("https://api.example.com");
var customers = await api.GetCustomersAsync();
```

### テスティング

#### Moq
```xml
<PackageReference Include="Moq" Version="4.18.4" />
```
```csharp
[TestClass]
public class CustomerServiceTests
{
    private Mock<ICustomerRepository> _mockRepository;
    private Mock<ILogger> _mockLogger;
    private CustomerService _service;
    
    [TestInitialize]
    public void Setup()
    {
        _mockRepository = new Mock<ICustomerRepository>();
        _mockLogger = new Mock<ILogger>();
        _service = new CustomerService(_mockRepository.Object, _mockLogger.Object);
    }
    
    [TestMethod]
    public async Task GetCustomer_ReturnsCustomer_WhenExists()
    {
        // Arrange
        var customerId = 1;
        var expectedCustomer = new Customer { Id = customerId, Name = "Test Customer" };
        
        _mockRepository
            .Setup(x => x.GetByIdAsync(customerId))
            .ReturnsAsync(expectedCustomer);
        
        // Act
        var result = await _service.GetCustomerAsync(customerId);
        
        // Assert
        Assert.IsNotNull(result);
        Assert.AreEqual(expectedCustomer.Name, result.Name);
        _mockRepository.Verify(x => x.GetByIdAsync(customerId), Times.Once);
    }
    
    [TestMethod]
    public async Task CreateCustomer_LogsError_WhenRepositoryThrows()
    {
        // Arrange
        var customer = new Customer { Name = "Test" };
        var exception = new DataException("Database error");
        
        _mockRepository
            .Setup(x => x.AddAsync(It.IsAny<Customer>()))
            .ThrowsAsync(exception);
        
        // Act & Assert
        await Assert.ThrowsExceptionAsync<DataException>(
            () => _service.CreateCustomerAsync(customer));
        
        _mockLogger.Verify(
            x => x.Error(It.Is<string>(msg => msg.Contains("Failed to create customer")), exception),
            Times.Once);
    }
}
```

#### FluentAssertions
```xml
<PackageReference Include="FluentAssertions" Version="6.11.0" />
```
```csharp
[TestMethod]
public void CustomerValidation_ShouldHaveExpectedBehavior()
{
    // Arrange
    var customer = new Customer
    {
        Name = "John Doe",
        Email = "john@example.com",
        CreatedDate = DateTime.Now
    };
    
    // Act & Assert
    customer.Should().NotBeNull();
    customer.Name.Should().Be("John Doe");
    customer.Email.Should().MatchRegex(@"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$");
    customer.CreatedDate.Should().BeCloseTo(DateTime.Now, TimeSpan.FromSeconds(1));
    
    // コレクションのアサーション
    var customers = new List<Customer> { customer };
    customers.Should().HaveCount(1)
        .And.ContainSingle(c => c.Email == "john@example.com")
        .And.OnlyHaveUniqueItems();
    
    // 例外のアサーション
    Action action = () => _service.DeleteCustomer(null);
    action.Should().Throw<ArgumentNullException>()
        .WithMessage("*customer*");
}
```

### ユーティリティ

#### Polly（リトライ・サーキットブレーカー）
```xml
<PackageReference Include="Polly" Version="7.2.4" />
```
```csharp
public class ResilientHttpClient
{
    private readonly HttpClient _httpClient;
    private readonly IAsyncPolicy<HttpResponseMessage> _retryPolicy;
    
    public ResilientHttpClient()
    {
        _httpClient = new HttpClient();
        
        // リトライポリシー
        var retryPolicy = Policy
            .HandleResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
            .Or<HttpRequestException>()
            .WaitAndRetryAsync(
                3,
                retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                onRetry: (outcome, timespan, retryCount, context) =>
                {
                    var logger = context.Values.ContainsKey("logger") 
                        ? context.Values["logger"] as ILogger 
                        : null;
                    logger?.Warning($"Retry {retryCount} after {timespan} seconds");
                });
        
        // サーキットブレーカー
        var circuitBreakerPolicy = Policy
            .HandleResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
            .CircuitBreakerAsync(
                3,
                TimeSpan.FromMinutes(1),
                onBreak: (result, duration) => 
                {
                    Console.WriteLine($"Circuit breaker opened for {duration}");
                },
                onReset: () => 
                {
                    Console.WriteLine("Circuit breaker reset");
                });
        
        // ポリシーの組み合わせ
        _retryPolicy = Policy.WrapAsync(retryPolicy, circuitBreakerPolicy);
    }
    
    public async Task<T> GetAsync<T>(string url)
    {
        var response = await _retryPolicy.ExecuteAsync(async () => 
            await _httpClient.GetAsync(url));
        
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<T>(content);
    }
}
```

#### Humanizer
```xml
<PackageReference Include="Humanizer" Version="2.14.1" />
```
```csharp
public class HumanizerExample
{
    public void DemonstrateHumanizer()
    {
        // 日付の人間的表現
        DateTime.UtcNow.AddHours(-2).Humanize(); // "2 hours ago"
        DateTime.UtcNow.AddDays(3).Humanize(); // "in 3 days"
        
        // 数値の人間的表現
        123456789.ToWords(); // "one hundred and twenty-three million..."
        1024.Bytes().Humanize(); // "1 KB"
        (1024 * 1024 * 5).Bytes().Humanize(); // "5 MB"
        
        // 文字列の変換
        "CustomerName".Humanize(); // "Customer name"
        "customer_name".Pascalize(); // "CustomerName"
        "Customer".Pluralize(); // "Customers"
        
        // TimeSpanの人間的表現
        TimeSpan.FromMinutes(121).Humanize(); // "2 hours, 1 minute"
        TimeSpan.FromMilliseconds(1).Humanize(); // "1 millisecond"
    }
}
```

### セキュリティ

#### IdentityModel
```xml
<PackageReference Include="IdentityModel" Version="6.1.0" />
```
```csharp
public class TokenService
{
    private readonly HttpClient _httpClient;
    
    public async Task<string> GetAccessTokenAsync()
    {
        var disco = await _httpClient.GetDiscoveryDocumentAsync("https://identity.server");
        if (disco.IsError) throw new Exception(disco.Error);
        
        var tokenResponse = await _httpClient.RequestClientCredentialsTokenAsync(
            new ClientCredentialsTokenRequest
            {
                Address = disco.TokenEndpoint,
                ClientId = "client_id",
                ClientSecret = "client_secret",
                Scope = "api1 api2"
            });
        
        if (tokenResponse.IsError) throw new Exception(tokenResponse.Error);
        return tokenResponse.AccessToken;
    }
}
```

### Windows Forms 拡張

#### MetroModernUI
```xml
<PackageReference Include="MetroModernUI" Version="1.4.0.0" />
```
```csharp
public partial class ModernForm : MetroFramework.Forms.MetroForm
{
    public ModernForm()
    {
        InitializeComponent();
        
        // モダンUIスタイルの設定
        this.Style = MetroFramework.MetroColorStyle.Blue;
        this.Theme = MetroFramework.MetroThemeStyle.Light;
    }
}
```

#### MaterialSkin
```xml
<PackageReference Include="MaterialSkin.2" Version="2.3.1" />
```
```csharp
public partial class MaterialForm : MaterialForm
{
    private readonly MaterialSkinManager materialSkinManager;
    
    public MaterialForm()
    {
        InitializeComponent();
        
        materialSkinManager = MaterialSkinManager.Instance;
        materialSkinManager.AddFormToManage(this);
        materialSkinManager.Theme = MaterialSkinManager.Themes.LIGHT;
        materialSkinManager.ColorScheme = new ColorScheme(
            Primary.Blue600, Primary.Blue700,
            Primary.Blue200, Accent.LightBlue200,
            TextShade.WHITE);
    }
}
```

## 3. パッケージの選定基準

### エンタープライズ向けパッケージ選定チェックリスト
1. **安定性**: 本番環境での実績があるか
2. **サポート**: 長期サポートが保証されているか
3. **ライセンス**: 商用利用可能なライセンスか
4. **パフォーマンス**: 大規模データで問題ないか
5. **セキュリティ**: 既知の脆弱性がないか
6. **互換性**: .NET Framework 4.8で完全動作するか

### パッケージバージョン管理のベストプラクティス
```xml
<!-- Directory.Packages.props (中央パッケージ管理) -->
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  
  <ItemGroup>
    <!-- データアクセス -->
    <PackageVersion Include="EntityFramework" Version="6.4.4" />
    <PackageVersion Include="Dapper" Version="2.0.123" />
    
    <!-- DI コンテナ -->
    <PackageVersion Include="Unity.Container" Version="5.11.11" />
    
    <!-- ロギング -->
    <PackageVersion Include="NLog" Version="5.0.5" />
    
    <!-- その他共通 -->
    <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageVersion Include="AutoMapper" Version="12.0.1" />
  </ItemGroup>
</Project>
```

## 4. トラブルシューティング

### よくある問題と解決方法

#### パッケージの復元エラー
```powershell
# NuGet キャッシュのクリア
nuget locals all -clear

# パッケージの再インストール
Update-Package -reinstall

# 特定のフレームワークバージョンを指定
Install-Package PackageName -Framework net48
```

#### バージョン競合の解決
```xml
<!-- App.config でのバインディングリダイレクト -->
<configuration>
  <runtime>
    <assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1">
      <dependentAssembly>
        <assemblyIdentity name="Newtonsoft.Json" publicKeyToken="30ad4fe6b2a6aeed" />
        <bindingRedirect oldVersion="0.0.0.0-13.0.0.0" newVersion="13.0.0.0" />
      </dependentAssembly>
    </assemblyBinding>
  </runtime>
</configuration>
```

これらのNuGetパッケージを適切に活用することで、.NET Framework 4.8での開発効率と品質を大幅に向上させることができます。