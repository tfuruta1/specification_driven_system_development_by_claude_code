# エンタープライズパターン集

## 概要

.NET Framework 4.8 Windows Forms を使用したエンタープライズアプリケーション開発で頻繁に使用されるデザインパターンと実装例をまとめたドキュメントです。

## 1. Repository Pattern + Unit of Work

### 概要
データアクセス層を抽象化し、ビジネスロジックからデータベース操作を分離するパターンです。

### 実装例

```csharp
// IRepository インターフェース
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<IEnumerable<T>> FindAsync(Expression<Func<T, bool>> predicate);
    Task AddAsync(T entity);
    Task AddRangeAsync(IEnumerable<T> entities);
    void Update(T entity);
    void Remove(T entity);
    void RemoveRange(IEnumerable<T> entities);
}

// IUnitOfWork インターフェース
public interface IUnitOfWork : IDisposable
{
    ICustomerRepository Customers { get; }
    IOrderRepository Orders { get; }
    IProductRepository Products { get; }
    Task<int> SaveChangesAsync();
    Task BeginTransactionAsync();
    Task CommitAsync();
    Task RollbackAsync();
}

// 実装例
public class UnitOfWork : IUnitOfWork
{
    private readonly ApplicationDbContext _context;
    private readonly IDbContextTransaction _transaction;
    
    private ICustomerRepository _customers;
    private IOrderRepository _orders;
    private IProductRepository _products;
    
    public UnitOfWork(ApplicationDbContext context)
    {
        _context = context;
    }
    
    public ICustomerRepository Customers => 
        _customers ??= new CustomerRepository(_context);
        
    public IOrderRepository Orders => 
        _orders ??= new OrderRepository(_context);
        
    public IProductRepository Products => 
        _products ??= new ProductRepository(_context);
    
    public async Task<int> SaveChangesAsync()
    {
        return await _context.SaveChangesAsync();
    }
    
    public async Task BeginTransactionAsync()
    {
        _transaction = await _context.Database.BeginTransactionAsync();
    }
    
    public async Task CommitAsync()
    {
        await _transaction?.CommitAsync();
    }
    
    public async Task RollbackAsync()
    {
        await _transaction?.RollbackAsync();
    }
    
    public void Dispose()
    {
        _transaction?.Dispose();
        _context?.Dispose();
    }
}
```

### Windows Formsでの使用例

```csharp
public partial class CustomerForm : Form
{
    private readonly IUnitOfWork _unitOfWork;
    
    public CustomerForm(IUnitOfWork unitOfWork)
    {
        InitializeComponent();
        _unitOfWork = unitOfWork;
    }
    
    private async void btnSave_Click(object sender, EventArgs e)
    {
        try
        {
            await _unitOfWork.BeginTransactionAsync();
            
            var customer = new Customer
            {
                Name = txtName.Text,
                Email = txtEmail.Text
            };
            
            await _unitOfWork.Customers.AddAsync(customer);
            await _unitOfWork.SaveChangesAsync();
            await _unitOfWork.CommitAsync();
            
            MessageBox.Show("保存しました。");
        }
        catch (Exception ex)
        {
            await _unitOfWork.RollbackAsync();
            MessageBox.Show($"エラー: {ex.Message}");
        }
    }
}
```

## 2. Service Layer Pattern

### 概要
ビジネスロジックをサービス層に集約し、プレゼンテーション層から分離するパターンです。

### 実装例

```csharp
// サービスインターフェース
public interface ICustomerService
{
    Task<CustomerDto> GetCustomerAsync(int id);
    Task<IEnumerable<CustomerDto>> GetAllCustomersAsync();
    Task<CustomerDto> CreateCustomerAsync(CreateCustomerDto dto);
    Task UpdateCustomerAsync(UpdateCustomerDto dto);
    Task DeleteCustomerAsync(int id);
    Task<bool> IsEmailUniqueAsync(string email, int? excludeId = null);
}

// サービス実装
public class CustomerService : ICustomerService
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly IMapper _mapper;
    private readonly ILogger<CustomerService> _logger;
    
    public CustomerService(
        IUnitOfWork unitOfWork, 
        IMapper mapper,
        ILogger<CustomerService> logger)
    {
        _unitOfWork = unitOfWork;
        _mapper = mapper;
        _logger = logger;
    }
    
    public async Task<CustomerDto> CreateCustomerAsync(CreateCustomerDto dto)
    {
        // ビジネスルールの検証
        if (!await IsEmailUniqueAsync(dto.Email))
        {
            throw new BusinessException("このメールアドレスは既に使用されています。");
        }
        
        // エンティティの作成
        var customer = _mapper.Map<Customer>(dto);
        customer.CreatedAt = DateTime.Now;
        customer.Status = CustomerStatus.Active;
        
        // 保存
        await _unitOfWork.Customers.AddAsync(customer);
        await _unitOfWork.SaveChangesAsync();
        
        _logger.LogInformation($"顧客を作成しました: {customer.Id}");
        
        return _mapper.Map<CustomerDto>(customer);
    }
    
    public async Task<bool> IsEmailUniqueAsync(string email, int? excludeId = null)
    {
        var existing = await _unitOfWork.Customers
            .FindAsync(c => c.Email == email && c.Id != excludeId);
        return !existing.Any();
    }
}
```

## 3. Specification Pattern

### 概要
ビジネスルールをオブジェクトとしてカプセル化し、複雑な条件を組み合わせ可能にするパターンです。

### 実装例

```csharp
// 仕様インターフェース
public interface ISpecification<T>
{
    Expression<Func<T, bool>> ToExpression();
    bool IsSatisfiedBy(T entity);
}

// 基底実装
public abstract class Specification<T> : ISpecification<T>
{
    public abstract Expression<Func<T, bool>> ToExpression();
    
    public bool IsSatisfiedBy(T entity)
    {
        var predicate = ToExpression().Compile();
        return predicate(entity);
    }
    
    public Specification<T> And(ISpecification<T> specification)
    {
        return new AndSpecification<T>(this, specification);
    }
    
    public Specification<T> Or(ISpecification<T> specification)
    {
        return new OrSpecification<T>(this, specification);
    }
    
    public Specification<T> Not()
    {
        return new NotSpecification<T>(this);
    }
}

// 具体的な仕様
public class ActiveCustomerSpecification : Specification<Customer>
{
    public override Expression<Func<Customer, bool>> ToExpression()
    {
        return customer => customer.Status == CustomerStatus.Active;
    }
}

public class PremiumCustomerSpecification : Specification<Customer>
{
    public override Expression<Func<Customer, bool>> ToExpression()
    {
        return customer => customer.TotalPurchaseAmount >= 1000000;
    }
}

// 組み合わせ仕様
public class AndSpecification<T> : Specification<T>
{
    private readonly ISpecification<T> _left;
    private readonly ISpecification<T> _right;
    
    public AndSpecification(ISpecification<T> left, ISpecification<T> right)
    {
        _left = left;
        _right = right;
    }
    
    public override Expression<Func<T, bool>> ToExpression()
    {
        var leftExpr = _left.ToExpression();
        var rightExpr = _right.ToExpression();
        
        var parameter = Expression.Parameter(typeof(T));
        var body = Expression.AndAlso(
            Expression.Invoke(leftExpr, parameter),
            Expression.Invoke(rightExpr, parameter)
        );
        
        return Expression.Lambda<Func<T, bool>>(body, parameter);
    }
}
```

### 使用例

```csharp
// リポジトリでの使用
public async Task<IEnumerable<Customer>> GetCustomersBySpecAsync(
    ISpecification<Customer> specification)
{
    return await _context.Customers
        .Where(specification.ToExpression())
        .ToListAsync();
}

// サービスでの使用
public async Task<IEnumerable<CustomerDto>> GetActivePremiumCustomersAsync()
{
    var activeSpec = new ActiveCustomerSpecification();
    var premiumSpec = new PremiumCustomerSpecification();
    var combinedSpec = activeSpec.And(premiumSpec);
    
    var customers = await _unitOfWork.Customers
        .GetCustomersBySpecAsync(combinedSpec);
        
    return _mapper.Map<IEnumerable<CustomerDto>>(customers);
}
```

## 4. Strategy Pattern（レガシーシステム統合）

### 概要
異なるレガシーシステムとの統合方法をストラテジーとして実装し、実行時に切り替え可能にするパターンです。

### 実装例

```csharp
// ストラテジーインターフェース
public interface ILegacyIntegrationStrategy
{
    string SystemType { get; }
    Task<IEnumerable<CustomerData>> ImportCustomersAsync();
    Task<bool> ExportCustomerAsync(CustomerData customer);
}

// AS/400統合ストラテジー
public class AS400IntegrationStrategy : ILegacyIntegrationStrategy
{
    private readonly IAS400Connection _connection;
    
    public string SystemType => "AS400";
    
    public async Task<IEnumerable<CustomerData>> ImportCustomersAsync()
    {
        var query = @"
            SELECT CUSTCD, CUSTNM, CUSTEML 
            FROM CUSTMST 
            WHERE DELFLG = '0'";
            
        var results = await _connection.QueryAsync(query);
        
        return results.Select(r => new CustomerData
        {
            Code = ConvertFromEBCDIC(r.CUSTCD),
            Name = ConvertFromEBCDIC(r.CUSTNM),
            Email = ConvertFromEBCDIC(r.CUSTEML)
        });
    }
    
    private string ConvertFromEBCDIC(string input)
    {
        // EBCDIC変換ロジック
        var encoding = Encoding.GetEncoding("IBM930");
        var bytes = encoding.GetBytes(input);
        return Encoding.UTF8.GetString(bytes);
    }
}

// ファイル統合ストラテジー
public class FileIntegrationStrategy : ILegacyIntegrationStrategy
{
    private readonly IFileTransferService _fileService;
    private readonly IFixedLengthParser _parser;
    
    public string SystemType => "FixedLengthFile";
    
    public async Task<IEnumerable<CustomerData>> ImportCustomersAsync()
    {
        // FTPからファイルダウンロード
        var localPath = await _fileService.DownloadLatestCustomerFile();
        
        // 固定長ファイル解析
        var layout = new FixedLengthLayout
        {
            Fields = new List<FieldDefinition>
            {
                new FieldDefinition { Name = "Code", Start = 0, Length = 8 },
                new FieldDefinition { Name = "Name", Start = 8, Length = 40 },
                new FieldDefinition { Name = "Email", Start = 48, Length = 50 }
            }
        };
        
        return await _parser.ParseFileAsync<CustomerData>(localPath, layout);
    }
}

// コンテキスト
public class LegacyIntegrationContext
{
    private readonly Dictionary<string, ILegacyIntegrationStrategy> _strategies;
    private ILegacyIntegrationStrategy _currentStrategy;
    
    public LegacyIntegrationContext(
        IEnumerable<ILegacyIntegrationStrategy> strategies)
    {
        _strategies = strategies.ToDictionary(s => s.SystemType);
    }
    
    public void SetStrategy(string systemType)
    {
        if (_strategies.ContainsKey(systemType))
        {
            _currentStrategy = _strategies[systemType];
        }
        else
        {
            throw new NotSupportedException(
                $"システムタイプ '{systemType}' はサポートされていません。");
        }
    }
    
    public async Task<IEnumerable<CustomerData>> ImportCustomersAsync()
    {
        if (_currentStrategy == null)
        {
            throw new InvalidOperationException("ストラテジーが設定されていません。");
        }
        
        return await _currentStrategy.ImportCustomersAsync();
    }
}
```

## 5. Command Pattern（バッチ処理）

### 概要
バッチ処理の各ステップをコマンドとして実装し、実行順序の制御やロールバックを可能にするパターンです。

### 実装例

```csharp
// コマンドインターフェース
public interface IBatchCommand
{
    string Name { get; }
    int Order { get; }
    Task<CommandResult> ExecuteAsync();
    Task<CommandResult> UndoAsync();
}

// コマンド結果
public class CommandResult
{
    public bool Success { get; set; }
    public string Message { get; set; }
    public Dictionary<string, object> OutputData { get; set; }
    public Exception Exception { get; set; }
}

// 具体的なコマンド
public class ImportCustomersCommand : IBatchCommand
{
    private readonly ILegacyIntegrationContext _integration;
    private readonly ICustomerService _customerService;
    private List<int> _importedCustomerIds;
    
    public string Name => "顧客データインポート";
    public int Order => 1;
    
    public async Task<CommandResult> ExecuteAsync()
    {
        try
        {
            _importedCustomerIds = new List<int>();
            
            var legacyCustomers = await _integration.ImportCustomersAsync();
            
            foreach (var legacyCustomer in legacyCustomers)
            {
                var dto = new CreateCustomerDto
                {
                    Code = legacyCustomer.Code,
                    Name = legacyCustomer.Name,
                    Email = legacyCustomer.Email
                };
                
                var created = await _customerService.CreateCustomerAsync(dto);
                _importedCustomerIds.Add(created.Id);
            }
            
            return new CommandResult
            {
                Success = true,
                Message = $"{_importedCustomerIds.Count}件の顧客をインポートしました。",
                OutputData = new Dictionary<string, object>
                {
                    ["ImportedIds"] = _importedCustomerIds
                }
            };
        }
        catch (Exception ex)
        {
            return new CommandResult
            {
                Success = false,
                Message = "インポート中にエラーが発生しました。",
                Exception = ex
            };
        }
    }
    
    public async Task<CommandResult> UndoAsync()
    {
        if (_importedCustomerIds == null || !_importedCustomerIds.Any())
        {
            return new CommandResult { Success = true };
        }
        
        foreach (var id in _importedCustomerIds)
        {
            await _customerService.DeleteCustomerAsync(id);
        }
        
        return new CommandResult
        {
            Success = true,
            Message = $"{_importedCustomerIds.Count}件の顧客を削除しました。"
        };
    }
}

// バッチ実行エンジン
public class BatchExecutor
{
    private readonly IEnumerable<IBatchCommand> _commands;
    private readonly Stack<IBatchCommand> _executedCommands;
    
    public BatchExecutor(IEnumerable<IBatchCommand> commands)
    {
        _commands = commands.OrderBy(c => c.Order);
        _executedCommands = new Stack<IBatchCommand>();
    }
    
    public async Task<BatchResult> ExecuteAsync(IProgress<BatchProgress> progress = null)
    {
        var result = new BatchResult();
        var totalCommands = _commands.Count();
        var currentCommand = 0;
        
        foreach (var command in _commands)
        {
            currentCommand++;
            
            progress?.Report(new BatchProgress
            {
                CurrentCommand = command.Name,
                PercentComplete = (currentCommand * 100) / totalCommands
            });
            
            var commandResult = await command.ExecuteAsync();
            result.CommandResults.Add(command.Name, commandResult);
            
            if (commandResult.Success)
            {
                _executedCommands.Push(command);
            }
            else
            {
                // 失敗時はロールバック
                await RollbackAsync();
                result.Success = false;
                result.FailedCommand = command.Name;
                break;
            }
        }
        
        if (result.FailedCommand == null)
        {
            result.Success = true;
        }
        
        return result;
    }
    
    private async Task RollbackAsync()
    {
        while (_executedCommands.Count > 0)
        {
            var command = _executedCommands.Pop();
            await command.UndoAsync();
        }
    }
}
```

## 6. Mediator Pattern（画面間連携）

### 概要
複数のWindows Forms間の複雑な相互作用をメディエーターで管理するパターンです。

### 実装例

```csharp
// メディエーターインターフェース
public interface IFormMediator
{
    void RegisterForm(string key, Form form);
    void UnregisterForm(string key);
    void SendMessage(string fromKey, string toKey, MediatorMessage message);
    void BroadcastMessage(string fromKey, MediatorMessage message);
}

// メッセージクラス
public class MediatorMessage
{
    public string MessageType { get; set; }
    public object Data { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.Now;
}

// メディエーター実装
public class FormMediator : IFormMediator
{
    private readonly Dictionary<string, Form> _forms;
    private readonly Dictionary<string, List<Action<MediatorMessage>>> _handlers;
    
    public FormMediator()
    {
        _forms = new Dictionary<string, Form>();
        _handlers = new Dictionary<string, List<Action<MediatorMessage>>>();
    }
    
    public void RegisterForm(string key, Form form)
    {
        _forms[key] = form;
        
        if (form is IMediatorParticipant participant)
        {
            _handlers[key] = new List<Action<MediatorMessage>>
            {
                participant.HandleMessage
            };
        }
    }
    
    public void SendMessage(string fromKey, string toKey, MediatorMessage message)
    {
        if (_handlers.ContainsKey(toKey))
        {
            foreach (var handler in _handlers[toKey])
            {
                // UIスレッドで実行
                var form = _forms[toKey];
                form.BeginInvoke(new Action(() => handler(message)));
            }
        }
    }
    
    public void BroadcastMessage(string fromKey, MediatorMessage message)
    {
        foreach (var key in _handlers.Keys.Where(k => k != fromKey))
        {
            SendMessage(fromKey, key, message);
        }
    }
}

// 参加者インターフェース
public interface IMediatorParticipant
{
    void HandleMessage(MediatorMessage message);
}

// フォーム実装例
public partial class CustomerListForm : Form, IMediatorParticipant
{
    private readonly IFormMediator _mediator;
    
    public CustomerListForm(IFormMediator mediator)
    {
        InitializeComponent();
        _mediator = mediator;
        _mediator.RegisterForm("CustomerList", this);
    }
    
    public void HandleMessage(MediatorMessage message)
    {
        switch (message.MessageType)
        {
            case "CustomerUpdated":
                var customerId = (int)message.Data;
                RefreshCustomer(customerId);
                break;
                
            case "RefreshRequested":
                RefreshAllCustomers();
                break;
        }
    }
    
    private void dgvCustomers_CellDoubleClick(object sender, DataGridViewCellEventArgs e)
    {
        var customerId = (int)dgvCustomers.Rows[e.RowIndex].Cells["Id"].Value;
        
        // 詳細画面に通知
        _mediator.SendMessage("CustomerList", "CustomerDetail", 
            new MediatorMessage
            {
                MessageType = "ShowCustomer",
                Data = customerId
            });
    }
}
```

## まとめ

これらのパターンを適切に組み合わせることで、保守性が高く、拡張可能なエンタープライズアプリケーションを構築できます。各パターンは独立して使用することも、組み合わせて使用することも可能です。

### パターン選択の指針

1. **データアクセス**: Repository + Unit of Work
2. **ビジネスロジック**: Service Layer + Specification
3. **外部システム統合**: Strategy + Adapter
4. **バッチ処理**: Command + Chain of Responsibility
5. **UI連携**: Mediator + Observer

実装時は、要件の複雑さとチームのスキルレベルを考慮して、適切なパターンを選択してください。