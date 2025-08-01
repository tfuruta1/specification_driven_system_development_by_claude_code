# Refactor Command - コードリファクタリング

## 概要

既存の.NET Framework 4.8 Windows Formsコードを、機能を変更することなく内部構造を改善します。Clean Architecture原則に基づき、保守性、可読性、パフォーマンスを向上させます。

## 使用方法

```
/refactor <リファクタリングタイプ> [オプション]
```

### リファクタリングタイプ
- `architecture` - アーキテクチャレベルのリファクタリング
- `pattern` - デザインパターンの適用
- `performance` - パフォーマンス最適化
- `testability` - テスタビリティの向上
- `readability` - 可読性の改善
- `legacy` - レガシーコードのモダナイゼーション
- `solid` - SOLID原則の適用

### オプション
- `--scope <module|class|method>` - リファクタリング範囲
- `--preview` - 変更内容のプレビューのみ
- `--metrics` - リファクタリング前後のメトリクス比較
- `--safe` - 最小リスクの変更のみ実行

## 実行例

### 1. アーキテクチャリファクタリング

```bash
/refactor architecture --scope module

# 実行結果
アーキテクチャリファクタリング分析
==================================

## 現在の問題点
- Presentationレイヤーにビジネスロジックが混在
- 直接的なデータベースアクセス
- 密結合なコンポーネント

## リファクタリング計画
1. レイヤー分離の実施
2. 依存性注入の導入
3. インターフェースの抽出
```

#### Before: 密結合なコード

```csharp
// ❌ すべてが1つのフォームに詰め込まれている
public partial class CustomerManagementForm : Form
{
    private SqlConnection connection;
    
    public CustomerManagementForm()
    {
        InitializeComponent();
        connection = new SqlConnection(ConfigurationManager.ConnectionStrings["DefaultConnection"].ConnectionString);
    }
    
    private void btnSave_Click(object sender, EventArgs e)
    {
        try
        {
            connection.Open();
            
            // UIから直接データ検証
            if (string.IsNullOrEmpty(txtName.Text))
            {
                MessageBox.Show("名前は必須です");
                return;
            }
            
            // SQLを直接実行
            var command = new SqlCommand(
                "INSERT INTO Customers (Name, Email, Phone) VALUES (@name, @email, @phone)", 
                connection);
            command.Parameters.AddWithValue("@name", txtName.Text);
            command.Parameters.AddWithValue("@email", txtEmail.Text);
            command.Parameters.AddWithValue("@phone", txtPhone.Text);
            
            command.ExecuteNonQuery();
            
            // メール送信も同じメソッド内で
            var smtpClient = new SmtpClient("smtp.example.com");
            var message = new MailMessage(
                "noreply@example.com",
                txtEmail.Text,
                "登録完了",
                "お客様の登録が完了しました。");
            smtpClient.Send(message);
            
            MessageBox.Show("保存しました");
        }
        catch (Exception ex)
        {
            MessageBox.Show("エラー: " + ex.Message);
        }
        finally
        {
            connection.Close();
        }
    }
}
```

#### After: Clean Architectureに基づくリファクタリング

```csharp
// Domain/Entities/Customer.cs
public class Customer
{
    public int Id { get; private set; }
    public string Name { get; private set; }
    public string Email { get; private set; }
    public string Phone { get; private set; }
    
    public Customer(string name, string email, string phone)
    {
        SetName(name);
        SetEmail(email);
        SetPhone(phone);
    }
    
    public void SetName(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new DomainException("顧客名は必須です");
        
        Name = name;
    }
    
    public void SetEmail(string email)
    {
        if (!IsValidEmail(email))
            throw new DomainException("有効なメールアドレスを入力してください");
        
        Email = email;
    }
    
    private bool IsValidEmail(string email)
    {
        return !string.IsNullOrEmpty(email) && 
               email.Contains("@") && 
               email.Contains(".");
    }
}

// Application/Services/CustomerService.cs
public class CustomerService : ICustomerService
{
    private readonly ICustomerRepository _repository;
    private readonly IEmailService _emailService;
    private readonly IUnitOfWork _unitOfWork;
    private readonly ILogger<CustomerService> _logger;
    
    public CustomerService(
        ICustomerRepository repository,
        IEmailService emailService,
        IUnitOfWork unitOfWork,
        ILogger<CustomerService> logger)
    {
        _repository = repository;
        _emailService = emailService;
        _unitOfWork = unitOfWork;
        _logger = logger;
    }
    
    public async Task<Result<Customer>> CreateCustomerAsync(CreateCustomerDto dto)
    {
        try
        {
            // ドメインエンティティの作成
            var customer = new Customer(dto.Name, dto.Email, dto.Phone);
            
            // リポジトリ経由で保存
            await _repository.AddAsync(customer);
            await _unitOfWork.SaveChangesAsync();
            
            // メール送信（非同期・エラーハンドリング付き）
            _ = Task.Run(async () =>
            {
                try
                {
                    await _emailService.SendWelcomeEmailAsync(customer);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Welcome email sending failed for customer {CustomerId}", customer.Id);
                }
            });
            
            _logger.LogInformation("Customer created successfully: {CustomerId}", customer.Id);
            
            return Result<Customer>.Success(customer);
        }
        catch (DomainException ex)
        {
            _logger.LogWarning("Domain validation failed: {Message}", ex.Message);
            return Result<Customer>.Failure(ex.Message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error creating customer");
            return Result<Customer>.Failure("顧客の作成中にエラーが発生しました");
        }
    }
}

// Presentation/Forms/CustomerManagementForm.cs
public partial class CustomerManagementForm : Form
{
    private readonly ICustomerService _customerService;
    private readonly IMapper _mapper;
    
    public CustomerManagementForm(
        ICustomerService customerService,
        IMapper mapper)
    {
        InitializeComponent();
        _customerService = customerService;
        _mapper = mapper;
    }
    
    private async void btnSave_Click(object sender, EventArgs e)
    {
        // UI状態の管理
        SetFormEnabled(false);
        ShowProgress(true);
        
        try
        {
            // DTOへのマッピング
            var dto = new CreateCustomerDto
            {
                Name = txtName.Text,
                Email = txtEmail.Text,
                Phone = txtPhone.Text
            };
            
            // ビジネスロジックの呼び出し
            var result = await _customerService.CreateCustomerAsync(dto);
            
            if (result.IsSuccess)
            {
                ShowSuccessMessage("顧客情報を保存しました");
                ClearForm();
                await RefreshCustomerListAsync();
            }
            else
            {
                ShowErrorMessage(result.Error);
            }
        }
        finally
        {
            SetFormEnabled(true);
            ShowProgress(false);
        }
    }
}

// Infrastructure/Repositories/CustomerRepository.cs
public class CustomerRepository : ICustomerRepository
{
    private readonly AppDbContext _context;
    
    public CustomerRepository(AppDbContext context)
    {
        _context = context;
    }
    
    public async Task AddAsync(Customer customer)
    {
        await _context.Customers.AddAsync(customer);
    }
    
    public async Task<Customer> GetByIdAsync(int id)
    {
        return await _context.Customers
            .FirstOrDefaultAsync(c => c.Id == id);
    }
}
```

### 2. デザインパターンの適用

```bash
/refactor pattern --scope class

# 対象: レポート生成クラス
# 適用パターン: Strategy + Builder パターン
```

#### Before: 条件分岐だらけのコード

```csharp
public class ReportGenerator
{
    public void GenerateReport(string reportType, DataSet data, string outputPath)
    {
        if (reportType == "PDF")
        {
            // PDF生成ロジック
            var document = new PdfDocument();
            // ... 100行のPDF生成コード
        }
        else if (reportType == "Excel")
        {
            // Excel生成ロジック
            var workbook = new ExcelWorkbook();
            // ... 150行のExcel生成コード
        }
        else if (reportType == "CSV")
        {
            // CSV生成ロジック
            using (var writer = new StreamWriter(outputPath))
            {
                // ... 50行のCSV生成コード
            }
        }
        else
        {
            throw new NotSupportedException($"Report type {reportType} is not supported");
        }
    }
}
```

#### After: Strategyパターンの適用

```csharp
// Strategy インターフェース
public interface IReportStrategy
{
    Task GenerateAsync(ReportData data, string outputPath);
    string SupportedFormat { get; }
}

// Concrete Strategies
public class PdfReportStrategy : IReportStrategy
{
    public string SupportedFormat => "PDF";
    
    public async Task GenerateAsync(ReportData data, string outputPath)
    {
        using var document = new PdfDocument();
        var builder = new PdfReportBuilder(document);
        
        await builder
            .AddHeader(data.Title)
            .AddMetadata(data.Metadata)
            .AddContent(data.Content)
            .AddFooter(data.Footer)
            .BuildAsync(outputPath);
    }
}

public class ExcelReportStrategy : IReportStrategy
{
    public string SupportedFormat => "Excel";
    
    public async Task GenerateAsync(ReportData data, string outputPath)
    {
        using var package = new ExcelPackage();
        var builder = new ExcelReportBuilder(package);
        
        await builder
            .CreateWorksheet(data.Title)
            .AddHeaders(data.Headers)
            .AddData(data.Rows)
            .AddFormulas(data.Formulas)
            .ApplyFormatting(data.Formatting)
            .SaveAsync(outputPath);
    }
}

// Context
public class ReportGenerator
{
    private readonly Dictionary<string, IReportStrategy> _strategies;
    private readonly ILogger<ReportGenerator> _logger;
    
    public ReportGenerator(
        IEnumerable<IReportStrategy> strategies,
        ILogger<ReportGenerator> logger)
    {
        _strategies = strategies.ToDictionary(
            s => s.SupportedFormat.ToUpper(), 
            s => s);
        _logger = logger;
    }
    
    public async Task GenerateReportAsync(
        string format, 
        ReportData data, 
        string outputPath)
    {
        if (!_strategies.TryGetValue(format.ToUpper(), out var strategy))
        {
            throw new NotSupportedException(
                $"Report format '{format}' is not supported. " +
                $"Supported formats: {string.Join(", ", _strategies.Keys)}");
        }
        
        _logger.LogInformation(
            "Generating {Format} report: {Title}", 
            format, 
            data.Title);
        
        await strategy.GenerateAsync(data, outputPath);
        
        _logger.LogInformation(
            "Report generated successfully: {OutputPath}", 
            outputPath);
    }
}

// Builder Pattern for Report Construction
public abstract class ReportBuilder<T>
{
    protected readonly T Document;
    protected readonly List<Action<T>> BuildSteps = new();
    
    protected ReportBuilder(T document)
    {
        Document = document;
    }
    
    public ReportBuilder<T> AddStep(Action<T> step)
    {
        BuildSteps.Add(step);
        return this;
    }
    
    public virtual async Task BuildAsync(string outputPath)
    {
        foreach (var step in BuildSteps)
        {
            step(Document);
        }
        
        await SaveAsync(outputPath);
    }
    
    protected abstract Task SaveAsync(string outputPath);
}
```

### 3. パフォーマンス最適化リファクタリング

```bash
/refactor performance --metrics

# 分析結果
パフォーマンスリファクタリング
==============================

## 検出された問題
1. 同期的I/O操作（5箇所）
2. 非効率なコレクション操作（3箇所）
3. 不要なボクシング/アンボクシング（2箇所）
```

#### Before: 非効率なコード

```csharp
public class DataProcessor
{
    public List<ProcessedData> ProcessLargeDataSet(string filePath)
    {
        // ❌ 全データをメモリに読み込み
        var allLines = File.ReadAllLines(filePath);
        var results = new List<ProcessedData>();
        
        foreach (var line in allLines)
        {
            // ❌ 文字列の繰り返し処理
            if (line.Contains("ERROR") || line.Contains("WARNING") || line.Contains("INFO"))
            {
                var parts = line.Split(',');
                
                // ❌ 非効率なLINQ
                var timestamp = parts.Where(p => p.StartsWith("Time:")).FirstOrDefault();
                var level = parts.Where(p => p.StartsWith("Level:")).FirstOrDefault();
                var message = parts.Where(p => p.StartsWith("Message:")).FirstOrDefault();
                
                // ❌ ボクシング
                var data = new ProcessedData
                {
                    Timestamp = DateTime.Parse(timestamp?.Replace("Time:", "")),
                    Level = (LogLevel)Enum.Parse(typeof(LogLevel), level?.Replace("Level:", "")),
                    Message = message?.Replace("Message:", "")
                };
                
                results.Add(data);
            }
        }
        
        // ❌ 非効率なソート
        return results.OrderBy(r => r.Timestamp).ToList();
    }
}
```

#### After: 最適化されたコード

```csharp
public class OptimizedDataProcessor
{
    private static readonly Regex LogPattern = new Regex(
        @"Time:(?<time>[^,]+),Level:(?<level>[^,]+),Message:(?<message>.*)",
        RegexOptions.Compiled);
    
    private static readonly HashSet<string> LogLevels = new HashSet<string>(
        StringComparer.OrdinalIgnoreCase) { "ERROR", "WARNING", "INFO" };
    
    public async IAsyncEnumerable<ProcessedData> ProcessLargeDataSetAsync(
        string filePath,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        // ストリーミング処理
        await using var stream = new FileStream(
            filePath, 
            FileMode.Open, 
            FileAccess.Read, 
            FileShare.Read,
            bufferSize: 4096,
            useAsync: true);
        
        using var reader = new StreamReader(stream);
        
        // 並列処理用のチャネル
        var channel = Channel.CreateUnbounded<string>();
        
        // Producer
        var readerTask = Task.Run(async () =>
        {
            try
            {
                string line;
                while ((line = await reader.ReadLineAsync()) != null)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;
                        
                    await channel.Writer.WriteAsync(line, cancellationToken);
                }
            }
            finally
            {
                channel.Writer.Complete();
            }
        }, cancellationToken);
        
        // Consumer (並列処理)
        var parallelOptions = new ParallelOptions
        {
            CancellationToken = cancellationToken,
            MaxDegreeOfParallelism = Environment.ProcessorCount
        };
        
        await foreach (var line in channel.Reader.ReadAllAsync(cancellationToken))
        {
            // 効率的なパターンマッチング
            var match = LogPattern.Match(line);
            if (!match.Success)
                continue;
            
            var levelStr = match.Groups["level"].Value;
            if (!LogLevels.Contains(levelStr))
                continue;
            
            // オブジェクト生成の最適化
            yield return new ProcessedData
            {
                Timestamp = DateTime.Parse(match.Groups["time"].Value),
                Level = Enum.Parse<LogLevel>(levelStr),
                Message = match.Groups["message"].Value
            };
        }
        
        await readerTask;
    }
    
    // ソート済みマージ処理
    public async Task<IEnumerable<ProcessedData>> GetSortedDataAsync(
        IEnumerable<string> filePaths)
    {
        var sortedStreams = new List<IAsyncEnumerable<ProcessedData>>();
        
        foreach (var path in filePaths)
        {
            sortedStreams.Add(ProcessLargeDataSetAsync(path));
        }
        
        // K-way merge
        return await MergeSortedStreamsAsync(sortedStreams);
    }
}
```

### 4. テスタビリティ向上リファクタリング

```bash
/refactor testability --scope class

# 対象: データアクセスクラス
# 目標: モック可能な設計への変更
```

#### Before: テストが困難なコード

```csharp
public class OrderProcessor
{
    public void ProcessOrder(int orderId)
    {
        // ❌ 静的メソッドの直接呼び出し
        var order = DatabaseHelper.GetOrder(orderId);
        
        // ❌ new演算子での直接生成
        var validator = new OrderValidator();
        if (!validator.Validate(order))
        {
            throw new ValidationException("Invalid order");
        }
        
        // ❌ 外部依存の直接参照
        var inventory = InventorySystem.Instance.CheckStock(order.ProductId);
        
        // ❌ 現在時刻の直接取得
        order.ProcessedAt = DateTime.Now;
        
        // ❌ ファイルシステムの直接操作
        File.WriteAllText($"orders/{orderId}.txt", order.ToString());
    }
}
```

#### After: テスト可能な設計

```csharp
// 抽象化されたインターフェース
public interface IOrderRepository
{
    Task<Order> GetByIdAsync(int orderId);
    Task UpdateAsync(Order order);
}

public interface IOrderValidator
{
    ValidationResult Validate(Order order);
}

public interface IInventoryService
{
    Task<InventoryStatus> CheckStockAsync(int productId, int quantity);
}

public interface IDateTimeProvider
{
    DateTime UtcNow { get; }
}

public interface IFileService
{
    Task WriteAsync(string path, string content);
}

// テスト可能なクラス
public class OrderProcessor
{
    private readonly IOrderRepository _orderRepository;
    private readonly IOrderValidator _validator;
    private readonly IInventoryService _inventoryService;
    private readonly IDateTimeProvider _dateTimeProvider;
    private readonly IFileService _fileService;
    private readonly ILogger<OrderProcessor> _logger;
    
    public OrderProcessor(
        IOrderRepository orderRepository,
        IOrderValidator validator,
        IInventoryService inventoryService,
        IDateTimeProvider dateTimeProvider,
        IFileService fileService,
        ILogger<OrderProcessor> logger)
    {
        _orderRepository = orderRepository;
        _validator = validator;
        _inventoryService = inventoryService;
        _dateTimeProvider = dateTimeProvider;
        _fileService = fileService;
        _logger = logger;
    }
    
    public async Task<ProcessOrderResult> ProcessOrderAsync(int orderId)
    {
        try
        {
            // 依存性注入されたサービスを使用
            var order = await _orderRepository.GetByIdAsync(orderId);
            if (order == null)
            {
                return ProcessOrderResult.NotFound();
            }
            
            // バリデーション
            var validationResult = _validator.Validate(order);
            if (!validationResult.IsValid)
            {
                return ProcessOrderResult.ValidationFailed(validationResult.Errors);
            }
            
            // 在庫確認
            var inventoryStatus = await _inventoryService.CheckStockAsync(
                order.ProductId, 
                order.Quantity);
                
            if (inventoryStatus.AvailableQuantity < order.Quantity)
            {
                return ProcessOrderResult.InsufficientStock();
            }
            
            // 注文処理
            order.ProcessedAt = _dateTimeProvider.UtcNow;
            order.Status = OrderStatus.Processed;
            
            await _orderRepository.UpdateAsync(order);
            
            // 監査ログ
            var auditContent = JsonSerializer.Serialize(order);
            await _fileService.WriteAsync($"orders/{orderId}.json", auditContent);
            
            _logger.LogInformation("Order processed successfully: {OrderId}", orderId);
            
            return ProcessOrderResult.Success(order);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing order: {OrderId}", orderId);
            return ProcessOrderResult.SystemError(ex.Message);
        }
    }
}

// ユニットテストの例
[TestFixture]
public class OrderProcessorTests
{
    private Mock<IOrderRepository> _mockRepository;
    private Mock<IOrderValidator> _mockValidator;
    private Mock<IInventoryService> _mockInventory;
    private Mock<IDateTimeProvider> _mockDateTime;
    private Mock<IFileService> _mockFileService;
    private OrderProcessor _processor;
    
    [SetUp]
    public void Setup()
    {
        _mockRepository = new Mock<IOrderRepository>();
        _mockValidator = new Mock<IOrderValidator>();
        _mockInventory = new Mock<IInventoryService>();
        _mockDateTime = new Mock<IDateTimeProvider>();
        _mockFileService = new Mock<IFileService>();
        
        _processor = new OrderProcessor(
            _mockRepository.Object,
            _mockValidator.Object,
            _mockInventory.Object,
            _mockDateTime.Object,
            _mockFileService.Object,
            Mock.Of<ILogger<OrderProcessor>>());
    }
    
    [Test]
    public async Task ProcessOrder_Should_Return_Success_When_Valid()
    {
        // Arrange
        var order = new Order { Id = 1, ProductId = 100, Quantity = 5 };
        var fixedDateTime = new DateTime(2024, 1, 1, 12, 0, 0, DateTimeKind.Utc);
        
        _mockRepository.Setup(r => r.GetByIdAsync(1))
            .ReturnsAsync(order);
            
        _mockValidator.Setup(v => v.Validate(It.IsAny<Order>()))
            .Returns(ValidationResult.Success());
            
        _mockInventory.Setup(i => i.CheckStockAsync(100, 5))
            .ReturnsAsync(new InventoryStatus { AvailableQuantity = 10 });
            
        _mockDateTime.Setup(d => d.UtcNow)
            .Returns(fixedDateTime);
        
        // Act
        var result = await _processor.ProcessOrderAsync(1);
        
        // Assert
        Assert.That(result.IsSuccess, Is.True);
        Assert.That(result.Order.ProcessedAt, Is.EqualTo(fixedDateTime));
        Assert.That(result.Order.Status, Is.EqualTo(OrderStatus.Processed));
        
        _mockRepository.Verify(r => r.UpdateAsync(It.IsAny<Order>()), Times.Once);
        _mockFileService.Verify(f => f.WriteAsync(
            It.Is<string>(p => p.Contains("orders/1.json")),
            It.IsAny<string>()), Times.Once);
    }
}
```

### 5. SOLID原則の適用

```bash
/refactor solid --preview

# 違反検出
SOLID原則違反の分析
==================

## 検出された違反
1. SRP違反: CustomerService（5つの責任）
2. OCP違反: PaymentProcessor（新しい支払い方法追加時に修正必要）
3. LSP違反: SpecialCustomer（基底クラスの契約違反）
4. ISP違反: IDataAccess（巨大インターフェース）
5. DIP違反: ReportGenerator（具象クラスへの依存）
```

#### SOLID原則適用の例

```csharp
// Single Responsibility Principle (SRP)
// Before: 複数の責任を持つクラス
public class CustomerService
{
    public void CreateCustomer(Customer customer) { }
    public void UpdateCustomer(Customer customer) { }
    public void SendEmail(string email, string message) { }
    public void GenerateReport(DateTime from, DateTime to) { }
    public void ExportToExcel(List<Customer> customers) { }
}

// After: 単一責任に分割
public class CustomerRepository
{
    public async Task CreateAsync(Customer customer) { }
    public async Task UpdateAsync(Customer customer) { }
}

public class CustomerNotificationService
{
    public async Task SendWelcomeEmailAsync(Customer customer) { }
}

public class CustomerReportService
{
    public async Task<CustomerReport> GenerateReportAsync(ReportCriteria criteria) { }
}

// Open/Closed Principle (OCP)
// Before: 拡張に対して開いていない
public class PaymentProcessor
{
    public void ProcessPayment(string type, decimal amount)
    {
        if (type == "CreditCard")
        {
            // クレジットカード処理
        }
        else if (type == "BankTransfer")
        {
            // 銀行振込処理
        }
        // 新しい支払い方法を追加するには、このクラスを修正する必要がある
    }
}

// After: 拡張に対して開いている
public interface IPaymentMethod
{
    Task<PaymentResult> ProcessAsync(decimal amount);
    bool CanProcess(PaymentRequest request);
}

public class CreditCardPayment : IPaymentMethod
{
    public async Task<PaymentResult> ProcessAsync(decimal amount)
    {
        // クレジットカード固有の処理
    }
    
    public bool CanProcess(PaymentRequest request)
    {
        return request.Type == PaymentType.CreditCard;
    }
}

public class PaymentProcessor
{
    private readonly IEnumerable<IPaymentMethod> _paymentMethods;
    
    public PaymentProcessor(IEnumerable<IPaymentMethod> paymentMethods)
    {
        _paymentMethods = paymentMethods;
    }
    
    public async Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request)
    {
        var method = _paymentMethods.FirstOrDefault(m => m.CanProcess(request));
        
        if (method == null)
            throw new NotSupportedException($"Payment type {request.Type} is not supported");
            
        return await method.ProcessAsync(request.Amount);
    }
}

// Interface Segregation Principle (ISP)
// Before: 巨大なインターフェース
public interface IDataAccess
{
    void Create(object entity);
    object Read(int id);
    void Update(object entity);
    void Delete(int id);
    List<object> Query(string sql);
    void ExecuteStoredProcedure(string name, object parameters);
    void BulkInsert(IEnumerable<object> entities);
    void Truncate(string tableName);
}

// After: 分離されたインターフェース
public interface IReadRepository<T>
{
    Task<T> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
}

public interface IWriteRepository<T>
{
    Task AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(int id);
}

public interface IQueryRepository<T>
{
    Task<IEnumerable<T>> QueryAsync(ISpecification<T> specification);
}

// Dependency Inversion Principle (DIP)
// Before: 高レベルモジュールが低レベルモジュールに依存
public class OrderService
{
    private readonly SqlDatabase database = new SqlDatabase();
    private readonly SmtpEmailService emailService = new SmtpEmailService();
    
    public void ProcessOrder(Order order)
    {
        database.Save(order);
        emailService.SendEmail(order.CustomerEmail, "Order confirmed");
    }
}

// After: 抽象に依存
public class OrderService
{
    private readonly IOrderRepository _repository;
    private readonly INotificationService _notificationService;
    
    public OrderService(
        IOrderRepository repository,
        INotificationService notificationService)
    {
        _repository = repository;
        _notificationService = notificationService;
    }
    
    public async Task ProcessOrderAsync(Order order)
    {
        await _repository.SaveAsync(order);
        await _notificationService.NotifyOrderConfirmedAsync(order);
    }
}
```

## リファクタリング実施ガイドライン

### 安全なリファクタリングプロセス

```csharp
public class RefactoringOrchestrator
{
    public async Task<RefactoringResult> ExecuteRefactoringAsync(
        RefactoringPlan plan)
    {
        // 1. 現在の状態をスナップショット
        var snapshot = await CreateSnapshotAsync(plan.TargetCode);
        
        // 2. テストの実行（グリーンであることを確認）
        var testResult = await RunTestsAsync(plan.TestSuite);
        if (!testResult.AllPassed)
        {
            return RefactoringResult.Failed("既存のテストが失敗しています");
        }
        
        // 3. リファクタリングの実行
        var refactoredCode = await ApplyRefactoringAsync(plan);
        
        // 4. テストの再実行
        var postTestResult = await RunTestsAsync(plan.TestSuite);
        if (!postTestResult.AllPassed)
        {
            // ロールバック
            await RestoreSnapshotAsync(snapshot);
            return RefactoringResult.Failed("リファクタリング後にテストが失敗しました");
        }
        
        // 5. メトリクスの比較
        var metrics = await CompareMetricsAsync(snapshot.Code, refactoredCode);
        
        return RefactoringResult.Success(refactoredCode, metrics);
    }
}
```

### 段階的リファクタリング

```csharp
public class IncrementalRefactoring
{
    public async Task RefactorLegacySystemAsync()
    {
        var steps = new[]
        {
            // Phase 1: 準備
            new RefactoringStep("テストの追加", AddCharacterizationTests),
            new RefactoringStep("依存関係の明確化", IdentifyDependencies),
            
            // Phase 2: 構造の改善
            new RefactoringStep("メソッドの抽出", ExtractMethods),
            new RefactoringStep("クラスの分割", SplitClasses),
            
            // Phase 3: 設計の改善
            new RefactoringStep("インターフェースの抽出", ExtractInterfaces),
            new RefactoringStep("依存性注入の導入", IntroduceDI),
            
            // Phase 4: 最適化
            new RefactoringStep("パフォーマンス改善", OptimizePerformance),
            new RefactoringStep("コードクリーンアップ", CleanupCode)
        };
        
        foreach (var step in steps)
        {
            await ExecuteStepAsync(step);
        }
    }
}
```

## まとめ

このコマンドにより、既存の.NET Framework 4.8コードを体系的にリファクタリングし、以下を実現します：

1. **保守性の向上** - Clean Architectureに基づく明確な構造
2. **テスタビリティの向上** - 依存性注入とモック可能な設計
3. **パフォーマンスの改善** - 最適化されたアルゴリズムとデータ構造
4. **拡張性の確保** - SOLID原則に基づく柔軟な設計
5. **技術的負債の削減** - 段階的なコード品質の改善