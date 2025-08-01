# Enhance Command - 機能拡張・改善

## 概要

既存のWindows Formsアプリケーションに新機能を追加したり、既存機能を拡張・改善します。Clean Architectureの原則を保ちながら、エンタープライズ要件に対応した高品質な機能拡張を実現します。

## 使用方法

```
/enhance <機能タイプ> [オプション]
```

### 機能タイプ
- `ui` - UI/UX改善（モダンUI、レスポンシブ対応）
- `integration` - 既存システム統合機能の追加
- `performance` - パフォーマンス最適化
- `reporting` - レポート機能の拡張
- `security` - セキュリティ機能の強化
- `data` - データ処理機能の拡張
- `workflow` - ワークフロー機能の追加

### オプション
- `--priority <high|medium|low>` - 実装優先度
- `--estimate` - 工数見積もりのみ実行
- `--test-first` - テストファースト開発
- `--backward-compatible` - 後方互換性を保証

## 実行例

### 1. モダンUIへの改善

```bash
/enhance ui --priority high

# 実行結果
UI/UX改善計画
=================

## 現状分析
- 現在のUIフレームワーク: Windows Forms標準
- ユーザビリティスコア: 65/100
- アクセシビリティ準拠度: 部分的

## 改善提案
1. **Material Design風UIの導入**
   - MetroFramework または MaterialSkin の導入
   - 統一されたカラーパレットとアイコン
   
2. **レスポンシブレイアウト**
   - TableLayoutPanel によるレスポンシブ対応
   - DPI認識アプリケーション設定

3. **アニメーション効果**
   - 画面遷移のスムーズ化
   - プログレス表示の改善

## 実装計画
```

#### Material Design実装例

```csharp
// 1. MaterialSkinライブラリの導入
// Install-Package MaterialSkin.2

using MaterialSkin;
using MaterialSkin.Controls;

namespace EnterpriseApp.Presentation.Forms
{
    public partial class MainForm : MaterialForm
    {
        private readonly MaterialSkinManager materialSkinManager;
        
        public MainForm()
        {
            InitializeComponent();
            
            // Material Designの初期化
            materialSkinManager = MaterialSkinManager.Instance;
            materialSkinManager.AddFormToManage(this);
            materialSkinManager.Theme = MaterialSkinManager.Themes.LIGHT;
            materialSkinManager.ColorScheme = new ColorScheme(
                Primary.Blue600, 
                Primary.Blue700,
                Primary.Blue200, 
                Accent.LightBlue200,
                TextShade.WHITE
            );
        }
        
        private void InitializeModernUI()
        {
            // カードレイアウトの実装
            var cardPanel = new MaterialCard
            {
                Depth = 3,
                MouseState = MouseState.HOVER,
                Padding = new Padding(14),
                Size = new Size(350, 200),
                Location = new Point(12, 72)
            };
            
            // リップル効果付きボタン
            var actionButton = new MaterialRaisedButton
            {
                Text = "処理実行",
                Size = new Size(120, 36),
                UseVisualStyleBackColor = true
            };
            
            actionButton.Click += async (s, e) => 
            {
                // プログレス表示
                var progress = new MaterialProgressBar
                {
                    Style = ProgressBarStyle.Marquee
                };
                await ExecuteWithProgressAsync(progress);
            };
        }
    }
}
```

#### レスポンシブレイアウト実装

```csharp
public class ResponsiveFormBase : Form
{
    private readonly TableLayoutPanel mainLayout;
    private float currentDpiScale = 1.0f;
    
    public ResponsiveFormBase()
    {
        // DPI認識設定
        this.AutoScaleMode = AutoScaleMode.Dpi;
        
        // レスポンシブレイアウトの基本構造
        mainLayout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 12, // 12カラムグリッド
            RowCount = 1,
            AutoSize = true
        };
        
        // カラム幅を比率で設定
        for (int i = 0; i < 12; i++)
        {
            mainLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100f / 12));
        }
        
        this.Controls.Add(mainLayout);
    }
    
    protected override void OnDpiChanged(DpiChangedEventArgs e)
    {
        base.OnDpiChanged(e);
        currentDpiScale = e.DeviceDpiNew / 96f;
        AdjustFormLayout();
    }
    
    private void AdjustFormLayout()
    {
        // DPIに応じてフォントサイズを調整
        foreach (Control control in GetAllControls(this))
        {
            if (control.Font != null)
            {
                control.Font = new Font(
                    control.Font.FontFamily,
                    control.Font.Size * currentDpiScale,
                    control.Font.Style
                );
            }
        }
    }
    
    protected void AddResponsiveControl(Control control, int column, int columnSpan, int row = 0)
    {
        mainLayout.Controls.Add(control, column, row);
        mainLayout.SetColumnSpan(control, columnSpan);
        control.Dock = DockStyle.Fill;
    }
}
```

### 2. 既存システム統合機能の追加

```bash
/enhance integration --test-first

# 実行結果
既存システム統合機能拡張
========================

## 統合対象システム
- 基幹システム（SAP）
- レガシーDB（Oracle 11g）
- 外部API（REST/SOAP）

## 実装内容
1. アダプターパターンによる統合層
2. データ同期メカニズム
3. エラーハンドリングとリトライ機構
```

#### 統合アダプター実装

```csharp
// Domain/Interfaces/ILegacySystemAdapter.cs
public interface ILegacySystemAdapter<TSource, TTarget>
{
    Task<TTarget> AdaptAsync(TSource source);
    Task<IEnumerable<TTarget>> AdaptManyAsync(IEnumerable<TSource> sources);
    Task<Result<TTarget>> SafeAdaptAsync(TSource source);
}

// Infrastructure/Adapters/SAPCustomerAdapter.cs
public class SAPCustomerAdapter : ILegacySystemAdapter<SAPCustomer, Customer>
{
    private readonly ISAPConnector _sapConnector;
    private readonly ILogger<SAPCustomerAdapter> _logger;
    private readonly IDataMappingService _mappingService;
    
    public SAPCustomerAdapter(
        ISAPConnector sapConnector,
        ILogger<SAPCustomerAdapter> logger,
        IDataMappingService mappingService)
    {
        _sapConnector = sapConnector;
        _logger = logger;
        _mappingService = mappingService;
    }
    
    public async Task<Customer> AdaptAsync(SAPCustomer sapCustomer)
    {
        try
        {
            // データ変換ルールの適用
            var customer = new Customer
            {
                Id = GenerateCustomerId(sapCustomer.KUNNR),
                Name = NormalizeCustomerName(sapCustomer.NAME1, sapCustomer.NAME2),
                TaxId = FormatTaxId(sapCustomer.STCD1),
                Address = await BuildAddressAsync(sapCustomer),
                CreditLimit = ConvertCurrency(sapCustomer.KLIMK, sapCustomer.WAERS),
                Status = MapCustomerStatus(sapCustomer.AUFSD),
                Metadata = new CustomerMetadata
                {
                    SourceSystem = "SAP",
                    SourceId = sapCustomer.KUNNR,
                    LastSyncDate = DateTime.UtcNow,
                    SyncVersion = sapCustomer.AEDAT
                }
            };
            
            // カスタムフィールドのマッピング
            await ApplyCustomMappingsAsync(sapCustomer, customer);
            
            return customer;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "SAP顧客データの変換エラー: {CustomerId}", sapCustomer.KUNNR);
            throw new AdapterException($"顧客データ変換失敗: {sapCustomer.KUNNR}", ex);
        }
    }
    
    public async Task<Result<Customer>> SafeAdaptAsync(SAPCustomer source)
    {
        try
        {
            var result = await AdaptAsync(source);
            return Result<Customer>.Success(result);
        }
        catch (AdapterException ex)
        {
            return Result<Customer>.Failure(ex.Message);
        }
    }
    
    private async Task<Address> BuildAddressAsync(SAPCustomer sapCustomer)
    {
        // 住所マスタからの追加情報取得
        var addressData = await _sapConnector.GetAddressAsync(sapCustomer.ADRNR);
        
        return new Address
        {
            Street = $"{addressData.STREET} {addressData.HOUSE_NUM1}",
            City = addressData.CITY1,
            PostalCode = addressData.POST_CODE1,
            Country = ConvertCountryCode(addressData.COUNTRY),
            Region = addressData.REGION
        };
    }
}
```

#### データ同期サービス

```csharp
public class DataSynchronizationService : IDataSynchronizationService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ISyncStateRepository _syncStateRepository;
    private readonly ILogger<DataSynchronizationService> _logger;
    
    public async Task<SyncResult> SynchronizeAsync(SyncConfiguration config)
    {
        var result = new SyncResult();
        var syncState = await _syncStateRepository.GetLatestAsync(config.EntityType);
        
        try
        {
            // 差分データの取得
            var changes = await GetIncrementalChangesAsync(config, syncState);
            _logger.LogInformation("同期対象: {Count}件", changes.Count());
            
            // バッチ処理による効率的な同期
            var batches = changes.Batch(config.BatchSize);
            
            await Parallel.ForEachAsync(batches, new ParallelOptions
            {
                MaxDegreeOfParallelism = config.MaxParallelism
            }, async (batch, ct) =>
            {
                await ProcessBatchAsync(batch, config, result, ct);
            });
            
            // 同期状態の更新
            await UpdateSyncStateAsync(config, result);
            
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "データ同期エラー: {EntityType}", config.EntityType);
            result.Errors.Add(new SyncError
            {
                Message = ex.Message,
                Timestamp = DateTime.UtcNow,
                Severity = ErrorSeverity.Critical
            });
            return result;
        }
    }
    
    private async Task ProcessBatchAsync(
        IEnumerable<dynamic> batch, 
        SyncConfiguration config, 
        SyncResult result,
        CancellationToken cancellationToken)
    {
        using var scope = _serviceProvider.CreateScope();
        var adapter = scope.ServiceProvider.GetRequiredService(config.AdapterType) as ILegacySystemAdapter<dynamic, dynamic>;
        
        foreach (var item in batch)
        {
            if (cancellationToken.IsCancellationRequested) break;
            
            try
            {
                var adapted = await adapter.SafeAdaptAsync(item);
                if (adapted.IsSuccess)
                {
                    await SaveEntityAsync(adapted.Value, config);
                    result.SuccessCount++;
                }
                else
                {
                    result.Errors.Add(new SyncError
                    {
                        EntityId = GetEntityId(item),
                        Message = adapted.Error,
                        Timestamp = DateTime.UtcNow
                    });
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "エンティティ同期エラー");
                result.Errors.Add(new SyncError
                {
                    EntityId = GetEntityId(item),
                    Message = ex.Message,
                    Timestamp = DateTime.UtcNow,
                    StackTrace = ex.StackTrace
                });
            }
        }
    }
}
```

### 3. パフォーマンス最適化

```bash
/enhance performance --priority high

# 実行結果
パフォーマンス最適化計画
========================

## ボトルネック分析結果
1. データグリッドの大量データ表示（10万件以上）
2. 同期的なデータベースアクセス
3. UIスレッドのブロッキング

## 最適化実装
```

#### 仮想モードDataGridView実装

```csharp
public class VirtualDataGridView : DataGridView
{
    private readonly IDataCache<CustomerViewModel> _cache;
    private readonly int _pageSize = 100;
    private int _totalRows;
    
    public VirtualDataGridView()
    {
        this.VirtualMode = true;
        this.CellValueNeeded += OnCellValueNeeded;
        this.CellValuePushed += OnCellValuePushed;
        
        _cache = new LRUDataCache<CustomerViewModel>(capacity: 1000);
    }
    
    public async Task LoadDataAsync(IQueryable<Customer> query)
    {
        // 総件数の取得（高速）
        _totalRows = await query.CountAsync();
        this.RowCount = _totalRows;
        
        // 初期ページのプリロード
        await PreloadVisibleRangeAsync();
    }
    
    private async void OnCellValueNeeded(object sender, DataGridViewCellValueEventArgs e)
    {
        // キャッシュからデータ取得
        var customer = await GetCustomerAsync(e.RowIndex);
        
        if (customer != null)
        {
            switch (this.Columns[e.ColumnIndex].DataPropertyName)
            {
                case nameof(CustomerViewModel.Id):
                    e.Value = customer.Id;
                    break;
                case nameof(CustomerViewModel.Name):
                    e.Value = customer.Name;
                    break;
                case nameof(CustomerViewModel.Revenue):
                    e.Value = customer.Revenue.ToString("C");
                    break;
                // 他のプロパティも同様に処理
            }
        }
    }
    
    private async Task<CustomerViewModel> GetCustomerAsync(int rowIndex)
    {
        // キャッシュチェック
        if (_cache.TryGet(rowIndex, out var cached))
        {
            return cached;
        }
        
        // ページ単位でデータ取得
        var pageIndex = rowIndex / _pageSize;
        var pageData = await LoadPageAsync(pageIndex);
        
        // ページ全体をキャッシュ
        foreach (var item in pageData)
        {
            _cache.Set(item.RowIndex, item.Customer);
        }
        
        return pageData.FirstOrDefault(p => p.RowIndex == rowIndex)?.Customer;
    }
    
    private async Task<IEnumerable<(int RowIndex, CustomerViewModel Customer)>> LoadPageAsync(int pageIndex)
    {
        return await Task.Run(() =>
        {
            using var scope = ServiceLocator.CreateScope();
            var repository = scope.GetService<ICustomerRepository>();
            
            var customers = repository.Query()
                .OrderBy(c => c.Id)
                .Skip(pageIndex * _pageSize)
                .Take(_pageSize)
                .ProjectTo<CustomerViewModel>()
                .ToList();
            
            return customers.Select((c, i) => 
                (pageIndex * _pageSize + i, c));
        });
    }
}
```

#### 非同期データ処理

```csharp
public class AsyncDataProcessor
{
    private readonly SemaphoreSlim _semaphore;
    private readonly IProgress<ProcessingProgress> _progress;
    
    public AsyncDataProcessor(int maxConcurrency = 4)
    {
        _semaphore = new SemaphoreSlim(maxConcurrency);
    }
    
    public async Task<ProcessingResult> ProcessLargeDataSetAsync<T>(
        IEnumerable<T> data,
        Func<T, Task<ProcessingItemResult>> processor,
        IProgress<ProcessingProgress> progress = null)
    {
        var result = new ProcessingResult();
        var items = data.ToList();
        var completed = 0;
        
        // データフロー処理パイプライン
        var processBlock = new TransformBlock<T, ProcessingItemResult>(
            async item =>
            {
                await _semaphore.WaitAsync();
                try
                {
                    var itemResult = await processor(item);
                    
                    Interlocked.Increment(ref completed);
                    progress?.Report(new ProcessingProgress
                    {
                        Total = items.Count,
                        Completed = completed,
                        CurrentItem = item.ToString()
                    });
                    
                    return itemResult;
                }
                finally
                {
                    _semaphore.Release();
                }
            },
            new ExecutionDataflowBlockOptions
            {
                MaxDegreeOfParallelism = Environment.ProcessorCount,
                BoundedCapacity = 100 // バックプレッシャー制御
            });
        
        var collectBlock = new ActionBlock<ProcessingItemResult>(
            itemResult =>
            {
                if (itemResult.Success)
                    result.SuccessCount++;
                else
                    result.Errors.Add(itemResult.Error);
            });
        
        processBlock.LinkTo(collectBlock);
        
        // データ投入
        foreach (var item in items)
        {
            await processBlock.SendAsync(item);
        }
        
        processBlock.Complete();
        await collectBlock.Completion;
        
        return result;
    }
}
```

### 4. レポート機能の拡張

```bash
/enhance reporting --backward-compatible

# 実行結果
レポート機能拡張
================

## 新機能
1. Excel/PDF/CSV エクスポート
2. 動的レポートビルダー
3. スケジュール配信
4. ダッシュボード統合
```

#### 動的レポートビルダー

```csharp
public class DynamicReportBuilder
{
    private readonly IReportDataSource _dataSource;
    private readonly IReportTemplateRepository _templateRepository;
    
    public ReportDefinition CreateReport(ReportRequest request)
    {
        var builder = new FluentReportBuilder()
            .WithTitle(request.Title)
            .WithDateRange(request.StartDate, request.EndDate);
        
        // 動的カラム構成
        foreach (var field in request.Fields)
        {
            builder.AddColumn(field.Name, field.DataType, field.Format);
        }
        
        // フィルター条件
        foreach (var filter in request.Filters)
        {
            builder.AddFilter(filter.Field, filter.Operator, filter.Value);
        }
        
        // グルーピング
        if (request.GroupBy.Any())
        {
            builder.GroupBy(request.GroupBy.ToArray());
        }
        
        // 集計
        foreach (var aggregation in request.Aggregations)
        {
            builder.AddAggregation(
                aggregation.Field, 
                aggregation.Function, 
                aggregation.Alias);
        }
        
        return builder.Build();
    }
    
    public async Task<ReportResult> ExecuteReportAsync(ReportDefinition definition)
    {
        // SQLクエリの動的生成
        var query = GenerateDynamicQuery(definition);
        
        // データ取得
        var data = await _dataSource.ExecuteQueryAsync(query);
        
        // 後処理（フォーマット、計算フィールド等）
        var processed = await PostProcessDataAsync(data, definition);
        
        return new ReportResult
        {
            Definition = definition,
            Data = processed,
            ExecutionTime = DateTime.UtcNow,
            RowCount = processed.Count()
        };
    }
}

// Fluent API実装
public class FluentReportBuilder
{
    private readonly ReportDefinition _definition = new();
    
    public FluentReportBuilder WithTitle(string title)
    {
        _definition.Title = title;
        return this;
    }
    
    public FluentReportBuilder AddColumn(string name, Type dataType, string format = null)
    {
        _definition.Columns.Add(new ReportColumn
        {
            Name = name,
            DataType = dataType,
            DisplayFormat = format ?? GetDefaultFormat(dataType)
        });
        return this;
    }
    
    public FluentReportBuilder AddFilter(string field, FilterOperator op, object value)
    {
        _definition.Filters.Add(new ReportFilter
        {
            Field = field,
            Operator = op,
            Value = value
        });
        return this;
    }
    
    public FluentReportBuilder GroupBy(params string[] fields)
    {
        _definition.GroupByFields.AddRange(fields);
        return this;
    }
    
    public ReportDefinition Build() => _definition;
}
```

### 5. セキュリティ機能の強化

```bash
/enhance security --test-first

# 実行結果
セキュリティ機能強化
====================

## 実装内容
1. 多要素認証（MFA）
2. 監査ログの強化
3. データ暗号化
4. 権限管理の細分化
```

#### 多要素認証実装

```csharp
public class MultiFactorAuthenticationService : IAuthenticationService
{
    private readonly IUserRepository _userRepository;
    private readonly ITotpService _totpService;
    private readonly ISmsService _smsService;
    private readonly IAuditLogger _auditLogger;
    
    public async Task<AuthenticationResult> AuthenticateAsync(AuthenticationRequest request)
    {
        // 第1要素：パスワード認証
        var user = await _userRepository.GetByUsernameAsync(request.Username);
        if (user == null || !VerifyPassword(request.Password, user.PasswordHash))
        {
            await _auditLogger.LogFailedLoginAsync(request.Username, "Invalid credentials");
            return AuthenticationResult.Failed("認証情報が正しくありません");
        }
        
        // MFA要求チェック
        if (user.MfaEnabled)
        {
            // 第2要素の送信
            var mfaToken = await SendMfaTokenAsync(user, request.MfaMethod);
            
            return AuthenticationResult.RequiresMfa(mfaToken.ChallengeId, request.MfaMethod);
        }
        
        // セッション生成
        var session = await CreateSessionAsync(user);
        await _auditLogger.LogSuccessfulLoginAsync(user.Id, request.IpAddress);
        
        return AuthenticationResult.Success(session);
    }
    
    public async Task<AuthenticationResult> VerifyMfaAsync(MfaVerificationRequest request)
    {
        var challenge = await GetMfaChallengeAsync(request.ChallengeId);
        if (challenge == null || challenge.IsExpired)
        {
            return AuthenticationResult.Failed("認証チャレンジが無効です");
        }
        
        var isValid = challenge.Method switch
        {
            MfaMethod.Totp => await _totpService.VerifyAsync(challenge.UserId, request.Code),
            MfaMethod.Sms => VerifySmsCode(challenge, request.Code),
            MfaMethod.Email => VerifyEmailCode(challenge, request.Code),
            _ => false
        };
        
        if (!isValid)
        {
            await _auditLogger.LogFailedMfaAsync(challenge.UserId, challenge.Method);
            return AuthenticationResult.Failed("認証コードが正しくありません");
        }
        
        // セッション生成
        var user = await _userRepository.GetByIdAsync(challenge.UserId);
        var session = await CreateSessionAsync(user, mfaVerified: true);
        
        await _auditLogger.LogSuccessfulMfaAsync(user.Id, challenge.Method);
        
        return AuthenticationResult.Success(session);
    }
}
```

## 実装ガイドライン

### Clean Architectureの維持

```csharp
// ✅ 正しい実装例
// Application/UseCases/EnhanceFeatureUseCase.cs
public class EnhanceFeatureUseCase : IEnhanceFeatureUseCase
{
    private readonly IFeatureRepository _repository;
    private readonly IFeatureEnhancer _enhancer;
    private readonly INotificationService _notificationService;
    
    public async Task<EnhancementResult> ExecuteAsync(EnhancementRequest request)
    {
        // ビジネスロジックはドメイン層で
        var feature = await _repository.GetByIdAsync(request.FeatureId);
        var enhanced = await _enhancer.EnhanceAsync(feature, request.Options);
        
        await _repository.UpdateAsync(enhanced);
        await _notificationService.NotifyEnhancementAsync(enhanced);
        
        return new EnhancementResult(enhanced);
    }
}

// ❌ 誤った実装例
// Presentation/Forms/FeatureForm.cs
public partial class FeatureForm : Form
{
    private void btnEnhance_Click(object sender, EventArgs e)
    {
        // UIレイヤーにビジネスロジックを書かない
        using (var connection = new SqlConnection(connectionString))
        {
            // 直接データベースアクセスしない
            var command = new SqlCommand("UPDATE Features SET...", connection);
            command.ExecuteNonQuery();
        }
    }
}
```

### テスト駆動開発

```csharp
[TestFixture]
public class FeatureEnhancementTests
{
    private IEnhanceFeatureUseCase _useCase;
    private Mock<IFeatureRepository> _mockRepository;
    
    [SetUp]
    public void Setup()
    {
        _mockRepository = new Mock<IFeatureRepository>();
        _useCase = new EnhanceFeatureUseCase(_mockRepository.Object, ...);
    }
    
    [Test]
    public async Task Should_Enhance_Feature_With_Valid_Request()
    {
        // Arrange
        var request = new EnhancementRequest { FeatureId = 1, Options = new() };
        var existingFeature = new Feature { Id = 1, Version = "1.0" };
        
        _mockRepository.Setup(r => r.GetByIdAsync(1))
            .ReturnsAsync(existingFeature);
        
        // Act
        var result = await _useCase.ExecuteAsync(request);
        
        // Assert
        Assert.That(result.IsSuccess, Is.True);
        Assert.That(result.Feature.Version, Is.EqualTo("1.1"));
        _mockRepository.Verify(r => r.UpdateAsync(It.IsAny<Feature>()), Times.Once);
    }
}
```

## まとめ

このコマンドにより、エンタープライズWindows Formsアプリケーションの段階的な機能拡張を実現し、以下を達成します：

1. **モダンUI/UX** - Material Design導入による使いやすさの向上
2. **既存システム連携** - アダプターパターンによる疎結合な統合
3. **高パフォーマンス** - 非同期処理と仮想化による大規模データ対応
4. **柔軟なレポート** - 動的レポート生成によるビジネス要求への迅速な対応
5. **エンタープライズセキュリティ** - 多要素認証と監査ログによる堅牢性