# Fix Command - バグ修正・障害対応

## 概要

エンタープライズWindows Formsアプリケーションで発生したバグや障害を体系的に分析し、修正します。問題の根本原因を特定し、再発防止策を含めた包括的な修正を実施します。

## 使用方法

```
/fix <エラータイプ> [オプション]
```

### エラータイプ
- `runtime` - 実行時エラー（例外、クラッシュ）
- `ui` - UI関連の不具合（フリーズ、表示異常）
- `data` - データ不整合、破損
- `performance` - パフォーマンス劣化
- `integration` - 外部システム連携エラー
- `memory` - メモリリーク、リソース枯渇
- `security` - セキュリティ脆弱性

### オプション
- `--analyze` - 原因分析のみ実行
- `--hotfix` - 緊急修正（最小限の変更）
- `--comprehensive` - 包括的修正（関連箇所含む）
- `--test-coverage` - 修正後のテストカバレッジ確認

## 実行例

### 1. 実行時例外の修正

```bash
/fix runtime --comprehensive

# エラー内容
System.NullReferenceException: Object reference not set to an instance of an object.
   at CustomerForm.LoadCustomerData(Int32 customerId)
   at CustomerForm.customerDataGridView_CellClick(Object sender, DataGridViewCellEventArgs e)

# 実行結果
エラー分析と修正
================

## 問題分析
- エラータイプ: NullReferenceException
- 発生箇所: CustomerForm.LoadCustomerData
- 原因: 顧客データが存在しない場合のnullチェック漏れ

## 修正内容
1. Nullチェックの追加
2. 例外ハンドリングの強化
3. ユーザーへの適切なフィードバック
4. 防御的プログラミングの適用
```

#### 修正実装例

```csharp
// 修正前（問題のあるコード）
private void LoadCustomerData(int customerId)
{
    var customer = _customerRepository.GetById(customerId);
    // ❌ customer が null の場合にクラッシュ
    nameTextBox.Text = customer.Name;
    emailTextBox.Text = customer.Email;
    phoneTextBox.Text = customer.PhoneNumber;
}

// 修正後（包括的修正）
private async void LoadCustomerData(int customerId)
{
    try
    {
        // プログレス表示
        ShowLoadingIndicator(true);
        
        // 非同期でデータ取得
        var customer = await Task.Run(() => _customerRepository.GetById(customerId));
        
        if (customer == null)
        {
            // ユーザーフレンドリーなメッセージ
            MessageBox.Show(
                $"顧客ID {customerId} のデータが見つかりません。\n" +
                "データが削除されているか、IDが正しくない可能性があります。",
                "データ取得エラー",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning);
            
            // フォームをクリア
            ClearCustomerForm();
            
            // ログ記録
            _logger.LogWarning($"Customer not found: ID={customerId}");
            return;
        }
        
        // null安全なプロパティアクセス
        nameTextBox.Text = customer.Name ?? string.Empty;
        emailTextBox.Text = customer.Email ?? string.Empty;
        phoneTextBox.Text = customer.PhoneNumber ?? string.Empty;
        
        // 関連データの遅延読み込み
        await LoadRelatedDataAsync(customer);
        
        // 成功ログ
        _logger.LogInformation($"Customer loaded successfully: ID={customerId}");
    }
    catch (DataException ex)
    {
        // データアクセス例外の処理
        _logger.LogError(ex, $"Database error loading customer: ID={customerId}");
        
        MessageBox.Show(
            "データベースへの接続中にエラーが発生しました。\n" +
            "システム管理者に連絡してください。",
            "データベースエラー",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error);
    }
    catch (Exception ex)
    {
        // 予期しない例外の処理
        _logger.LogError(ex, $"Unexpected error loading customer: ID={customerId}");
        
        MessageBox.Show(
            "予期しないエラーが発生しました。\n" +
            $"エラー詳細: {ex.Message}",
            "システムエラー",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error);
    }
    finally
    {
        ShowLoadingIndicator(false);
    }
}

// 防御的プログラミングの追加メソッド
private void ClearCustomerForm()
{
    nameTextBox.Clear();
    emailTextBox.Clear();
    phoneTextBox.Clear();
    // 他のフィールドもクリア
}

private void ShowLoadingIndicator(bool show)
{
    loadingPictureBox.Visible = show;
    customerPanel.Enabled = !show;
    Application.DoEvents(); // UI更新を強制
}
```

### 2. UIフリーズの修正

```bash
/fix ui --analyze

# 問題内容
アプリケーションが「応答なし」になる
大量データ読み込み時にUIがフリーズする

# 分析結果
UI フリーズ問題分析
==================

## 原因
- UIスレッドでの重い処理実行
- 同期的なデータベースアクセス
- 非効率なデータバインディング

## 推奨修正
1. 非同期パターンの実装
2. 仮想化モードの使用
3. プログレス表示の追加
```

#### UI応答性改善の実装

```csharp
// 修正前（UIフリーズの原因）
private void LoadLargeDataButton_Click(object sender, EventArgs e)
{
    // ❌ UIスレッドで重い処理
    var data = _repository.GetAllRecords(); // 10万件のデータ
    dataGridView.DataSource = data;
}

// 修正後（非同期処理）
private async void LoadLargeDataButton_Click(object sender, EventArgs e)
{
    // UIコントロールの状態管理
    loadButton.Enabled = false;
    cancelButton.Visible = true;
    progressBar.Visible = true;
    statusLabel.Text = "データを読み込んでいます...";
    
    var cts = new CancellationTokenSource();
    cancelButton.Tag = cts;
    
    try
    {
        // 非同期でデータ取得
        var progress = new Progress<int>(percent =>
        {
            progressBar.Value = percent;
            statusLabel.Text = $"読み込み中... {percent}%";
        });
        
        var data = await LoadDataAsync(progress, cts.Token);
        
        // 仮想モードでの表示
        SetupVirtualMode(data);
        
        statusLabel.Text = $"完了: {data.Count:N0}件のデータを読み込みました";
    }
    catch (OperationCanceledException)
    {
        statusLabel.Text = "読み込みがキャンセルされました";
    }
    catch (Exception ex)
    {
        MessageBox.Show($"エラー: {ex.Message}", "読み込みエラー", 
            MessageBoxButtons.OK, MessageBoxIcon.Error);
        statusLabel.Text = "エラーが発生しました";
    }
    finally
    {
        loadButton.Enabled = true;
        cancelButton.Visible = false;
        progressBar.Visible = false;
    }
}

private async Task<List<DataRecord>> LoadDataAsync(
    IProgress<int> progress, 
    CancellationToken cancellationToken)
{
    return await Task.Run(() =>
    {
        var records = new List<DataRecord>();
        var totalCount = _repository.GetTotalCount();
        var batchSize = 1000;
        var loaded = 0;
        
        for (int offset = 0; offset < totalCount; offset += batchSize)
        {
            cancellationToken.ThrowIfCancellationRequested();
            
            var batch = _repository.GetBatch(offset, batchSize);
            records.AddRange(batch);
            
            loaded += batch.Count;
            var percent = (int)((loaded / (double)totalCount) * 100);
            progress?.Report(percent);
        }
        
        return records;
    }, cancellationToken);
}

private void SetupVirtualMode(List<DataRecord> data)
{
    // DataGridViewの仮想モード設定
    dataGridView.VirtualMode = true;
    dataGridView.RowCount = data.Count;
    
    // キャッシュの設定
    _dataCache = new DataCache<DataRecord>(data);
    
    dataGridView.CellValueNeeded += (s, e) =>
    {
        var record = _dataCache.GetItem(e.RowIndex);
        if (record != null)
        {
            switch (e.ColumnIndex)
            {
                case 0: e.Value = record.Id; break;
                case 1: e.Value = record.Name; break;
                case 2: e.Value = record.Date.ToString("yyyy/MM/dd"); break;
                // 他のカラムも同様
            }
        }
    };
}
```

### 3. メモリリークの修正

```bash
/fix memory --comprehensive

# 問題内容
アプリケーションのメモリ使用量が徐々に増加
長時間使用でOutOfMemoryException発生

# 分析結果
メモリリーク分析
================

## 検出された問題
1. イベントハンドラの未解除（3箇所）
2. Disposeされていないリソース（5箇所）
3. 静的コレクションへの無制限追加（2箇所）

## 修正計画
```

#### メモリリーク修正の実装

```csharp
// 修正前（メモリリークあり）
public partial class ReportForm : Form
{
    private Timer refreshTimer;
    private static List<ReportData> reportCache = new List<ReportData>();
    
    public ReportForm()
    {
        InitializeComponent();
        
        // ❌ イベントハンドラが解除されない
        GlobalEventManager.DataUpdated += OnDataUpdated;
        
        // ❌ タイマーがDisposeされない
        refreshTimer = new Timer();
        refreshTimer.Interval = 1000;
        refreshTimer.Tick += RefreshTimer_Tick;
        refreshTimer.Start();
    }
    
    private void LoadReport()
    {
        // ❌ 静的コレクションが無限に増加
        var data = GenerateReportData();
        reportCache.Add(data);
    }
}

// 修正後（メモリリーク対策済み）
public partial class ReportForm : Form, IDisposable
{
    private Timer refreshTimer;
    private readonly CompositeDisposable disposables = new CompositeDisposable();
    
    // 静的キャッシュをLRUキャッシュに変更
    private static readonly LRUCache<string, ReportData> reportCache = 
        new LRUCache<string, ReportData>(maxSize: 100);
    
    public ReportForm()
    {
        InitializeComponent();
        InitializeEventHandlers();
        InitializeTimer();
    }
    
    private void InitializeEventHandlers()
    {
        // WeakEventパターンの使用
        WeakEventManager<GlobalEventManager, DataEventArgs>
            .AddHandler(null, nameof(GlobalEventManager.DataUpdated), OnDataUpdated);
    }
    
    private void InitializeTimer()
    {
        refreshTimer = new Timer
        {
            Interval = 1000
        };
        refreshTimer.Tick += RefreshTimer_Tick;
        
        // Disposableコレクションに追加
        disposables.Add(Disposable.Create(() =>
        {
            refreshTimer.Stop();
            refreshTimer.Tick -= RefreshTimer_Tick;
            refreshTimer.Dispose();
        }));
        
        refreshTimer.Start();
    }
    
    private void LoadReport()
    {
        var data = GenerateReportData();
        var key = GenerateReportKey(data);
        
        // LRUキャッシュに追加（古いエントリは自動削除）
        reportCache.Set(key, data);
    }
    
    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            // すべてのリソースを解放
            disposables?.Dispose();
            
            // イベントハンドラの解除
            WeakEventManager<GlobalEventManager, DataEventArgs>
                .RemoveHandler(null, nameof(GlobalEventManager.DataUpdated), OnDataUpdated);
            
            // 管理リソースの解放
            foreach (Control control in Controls)
            {
                if (control is IDisposable disposable)
                {
                    disposable.Dispose();
                }
            }
        }
        
        base.Dispose(disposing);
    }
}

// LRUキャッシュの実装
public class LRUCache<TKey, TValue>
{
    private readonly int maxSize;
    private readonly Dictionary<TKey, LinkedListNode<CacheItem>> cacheMap;
    private readonly LinkedList<CacheItem> lruList;
    
    public LRUCache(int maxSize)
    {
        this.maxSize = maxSize;
        this.cacheMap = new Dictionary<TKey, LinkedListNode<CacheItem>>(maxSize);
        this.lruList = new LinkedList<CacheItem>();
    }
    
    public void Set(TKey key, TValue value)
    {
        lock (cacheMap)
        {
            if (cacheMap.TryGetValue(key, out var node))
            {
                // 既存のエントリを最新に移動
                lruList.Remove(node);
                node.Value = new CacheItem { Key = key, Value = value };
                lruList.AddFirst(node);
            }
            else
            {
                // 新規エントリ追加
                if (cacheMap.Count >= maxSize)
                {
                    // 最も古いエントリを削除
                    var lastNode = lruList.Last;
                    lruList.RemoveLast();
                    cacheMap.Remove(lastNode.Value.Key);
                }
                
                var newNode = lruList.AddFirst(new CacheItem { Key = key, Value = value });
                cacheMap[key] = newNode;
            }
        }
    }
    
    private class CacheItem
    {
        public TKey Key { get; set; }
        public TValue Value { get; set; }
    }
}
```

### 4. データ不整合の修正

```bash
/fix data --comprehensive

# 問題内容
トランザクション処理中のエラーでデータ不整合発生
在庫数と売上データが一致しない

# 修正結果
データ整合性修正
================

## 実装内容
1. トランザクション処理の修正
2. 整合性チェック機能の追加
3. データ修復ツールの提供
```

#### トランザクション処理の修正

```csharp
// 修正前（トランザクション不完全）
public void ProcessOrder(Order order)
{
    // ❌ 個別にデータ更新（途中でエラーが発生すると不整合）
    _inventoryRepository.UpdateStock(order.ProductId, -order.Quantity);
    _orderRepository.Insert(order);
    _salesRepository.RecordSale(order);
}

// 修正後（完全なトランザクション処理）
public class OrderService : IOrderService
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly IInventoryService _inventoryService;
    private readonly IOrderValidator _validator;
    private readonly ILogger<OrderService> _logger;
    
    public async Task<OrderResult> ProcessOrderAsync(Order order)
    {
        // 入力検証
        var validationResult = await _validator.ValidateAsync(order);
        if (!validationResult.IsValid)
        {
            return OrderResult.ValidationFailed(validationResult.Errors);
        }
        
        // トランザクション開始
        using (var transaction = await _unitOfWork.BeginTransactionAsync())
        {
            try
            {
                // 1. 在庫チェックと更新（悲観的ロック）
                var inventory = await _unitOfWork.InventoryRepository
                    .GetByIdWithLockAsync(order.ProductId);
                
                if (inventory.AvailableQuantity < order.Quantity)
                {
                    return OrderResult.InsufficientStock(
                        inventory.AvailableQuantity, 
                        order.Quantity);
                }
                
                inventory.Reserve(order.Quantity);
                await _unitOfWork.InventoryRepository.UpdateAsync(inventory);
                
                // 2. 注文作成
                order.OrderNumber = await GenerateOrderNumberAsync();
                order.Status = OrderStatus.Confirmed;
                order.CreatedAt = DateTime.UtcNow;
                
                await _unitOfWork.OrderRepository.InsertAsync(order);
                
                // 3. 売上記録
                var sale = new SalesRecord
                {
                    OrderId = order.Id,
                    ProductId = order.ProductId,
                    Quantity = order.Quantity,
                    Amount = order.TotalAmount,
                    RecordedAt = DateTime.UtcNow
                };
                
                await _unitOfWork.SalesRepository.InsertAsync(sale);
                
                // 4. 監査ログ
                await _unitOfWork.AuditRepository.LogAsync(new AuditEntry
                {
                    EntityType = nameof(Order),
                    EntityId = order.Id.ToString(),
                    Action = AuditAction.Create,
                    UserId = order.UserId,
                    Timestamp = DateTime.UtcNow,
                    Details = JsonSerializer.Serialize(order)
                });
                
                // すべて成功したらコミット
                await _unitOfWork.SaveChangesAsync();
                await transaction.CommitAsync();
                
                _logger.LogInformation(
                    "Order processed successfully: {OrderNumber}", 
                    order.OrderNumber);
                
                return OrderResult.Success(order);
            }
            catch (Exception ex)
            {
                // エラー時はロールバック
                await transaction.RollbackAsync();
                
                _logger.LogError(ex, 
                    "Order processing failed for ProductId: {ProductId}", 
                    order.ProductId);
                
                // 補償トランザクション
                await ExecuteCompensationAsync(order);
                
                return OrderResult.SystemError(ex.Message);
            }
        }
    }
    
    private async Task ExecuteCompensationAsync(Order order)
    {
        try
        {
            // 部分的に処理されたデータのクリーンアップ
            await _inventoryService.ReleaseReservationAsync(
                order.ProductId, 
                order.Quantity);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, 
                "Compensation failed for order: {OrderId}", 
                order.Id);
        }
    }
}

// データ整合性チェックサービス
public class DataIntegrityService
{
    public async Task<IntegrityCheckResult> CheckOrderIntegrityAsync(
        DateTime startDate, 
        DateTime endDate)
    {
        var result = new IntegrityCheckResult();
        
        // 注文と在庫の整合性チェック
        var orderSummary = await _orderRepository
            .GetOrderSummaryAsync(startDate, endDate);
            
        var inventoryMovements = await _inventoryRepository
            .GetMovementsAsync(startDate, endDate);
        
        foreach (var productGroup in orderSummary.GroupBy(o => o.ProductId))
        {
            var orderQuantity = productGroup.Sum(o => o.Quantity);
            var movementQuantity = inventoryMovements
                .Where(m => m.ProductId == productGroup.Key)
                .Sum(m => m.Quantity);
            
            if (Math.Abs(orderQuantity + movementQuantity) > 0.01m)
            {
                result.AddInconsistency(new DataInconsistency
                {
                    Type = InconsistencyType.QuantityMismatch,
                    EntityType = "Product",
                    EntityId = productGroup.Key,
                    Expected = orderQuantity,
                    Actual = -movementQuantity,
                    Description = "注文数量と在庫移動量が一致しません"
                });
            }
        }
        
        return result;
    }
}
```

### 5. パフォーマンス問題の修正

```bash
/fix performance --analyze

# 問題内容
レポート生成に10分以上かかる
データベースクエリのタイムアウト頻発

# 分析結果
パフォーマンス問題分析
=====================

## ボトルネック
1. N+1クエリ問題（関連データの遅延読み込み）
2. インデックス不足
3. 非効率なLINQクエリ
4. 大量データの一括読み込み
```

#### パフォーマンス最適化の実装

```csharp
// 修正前（N+1問題）
public List<CustomerReportDto> GetCustomerReport()
{
    var customers = _context.Customers.ToList();
    var report = new List<CustomerReportDto>();
    
    foreach (var customer in customers)
    {
        // ❌ ループ内でクエリ実行（N+1問題）
        var orders = _context.Orders
            .Where(o => o.CustomerId == customer.Id)
            .ToList();
            
        var totalAmount = orders.Sum(o => o.Amount);
        
        report.Add(new CustomerReportDto
        {
            CustomerId = customer.Id,
            CustomerName = customer.Name,
            OrderCount = orders.Count,
            TotalAmount = totalAmount
        });
    }
    
    return report;
}

// 修正後（最適化済み）
public class OptimizedReportService
{
    private readonly IDbConnection _connection;
    private readonly IMemoryCache _cache;
    
    public async Task<IEnumerable<CustomerReportDto>> GetCustomerReportAsync(
        ReportParameters parameters)
    {
        // キャッシュチェック
        var cacheKey = $"CustomerReport_{parameters.GetHashCode()}";
        if (_cache.TryGetValue(cacheKey, out List<CustomerReportDto> cached))
        {
            return cached;
        }
        
        // 最適化されたSQLクエリ
        const string sql = @"
            WITH CustomerOrderSummary AS (
                SELECT 
                    c.Id AS CustomerId,
                    c.Name AS CustomerName,
                    COUNT(o.Id) AS OrderCount,
                    COALESCE(SUM(o.Amount), 0) AS TotalAmount,
                    MAX(o.OrderDate) AS LastOrderDate
                FROM Customers c
                LEFT JOIN Orders o ON c.Id = o.CustomerId
                WHERE (@StartDate IS NULL OR o.OrderDate >= @StartDate)
                  AND (@EndDate IS NULL OR o.OrderDate <= @EndDate)
                  AND c.IsActive = 1
                GROUP BY c.Id, c.Name
            )
            SELECT 
                CustomerId,
                CustomerName,
                OrderCount,
                TotalAmount,
                LastOrderDate,
                CASE 
                    WHEN TotalAmount >= 1000000 THEN 'Premium'
                    WHEN TotalAmount >= 100000 THEN 'Gold'
                    ELSE 'Standard'
                END AS CustomerTier
            FROM CustomerOrderSummary
            ORDER BY TotalAmount DESC
            OFFSET @Offset ROWS
            FETCH NEXT @PageSize ROWS ONLY";
        
        using (var multi = await _connection.QueryMultipleAsync(sql, new
        {
            parameters.StartDate,
            parameters.EndDate,
            parameters.Offset,
            parameters.PageSize
        }))
        {
            var results = (await multi.ReadAsync<CustomerReportDto>()).ToList();
            
            // 結果をキャッシュ（5分間）
            _cache.Set(cacheKey, results, TimeSpan.FromMinutes(5));
            
            return results;
        }
    }
    
    // バッチ処理による大量データ処理
    public async Task ProcessLargeDatasetAsync(
        Func<IEnumerable<CustomerReportDto>, Task> processor,
        CancellationToken cancellationToken = default)
    {
        const int batchSize = 1000;
        var offset = 0;
        
        // ストリーミング処理
        await using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync(cancellationToken);
        
        while (!cancellationToken.IsCancellationRequested)
        {
            var batch = await GetBatchAsync(connection, offset, batchSize);
            
            if (!batch.Any())
                break;
            
            // バッチ処理
            await processor(batch);
            
            offset += batchSize;
            
            // CPUを他のタスクに譲る
            await Task.Yield();
        }
    }
}

// インデックス作成スクリプト
public class DatabaseOptimizer
{
    public async Task CreateMissingIndexesAsync()
    {
        var indexScripts = new[]
        {
            @"CREATE NONCLUSTERED INDEX IX_Orders_CustomerId_OrderDate
              ON Orders (CustomerId, OrderDate) 
              INCLUDE (Amount)
              WHERE IsDeleted = 0",
              
            @"CREATE NONCLUSTERED INDEX IX_Customers_IsActive_Name
              ON Customers (IsActive, Name)
              WHERE IsActive = 1",
              
            @"CREATE COLUMNSTORE INDEX IX_OrderHistory_Columnstore
              ON OrderHistory (OrderDate, CustomerId, ProductId, Amount)"
        };
        
        foreach (var script in indexScripts)
        {
            try
            {
                await _connection.ExecuteAsync(script);
                _logger.LogInformation($"Index created successfully");
            }
            catch (SqlException ex) when (ex.Number == 1913) // Index already exists
            {
                _logger.LogInformation("Index already exists");
            }
        }
    }
}
```

## 障害対応プロセス

### 1. 緊急対応フロー

```csharp
public class EmergencyResponseService
{
    public async Task<EmergencyResponse> HandleCriticalErrorAsync(
        Exception exception,
        ErrorContext context)
    {
        var response = new EmergencyResponse();
        
        // 1. エラーの分類
        var severity = ClassifyErrorSeverity(exception);
        
        // 2. 即座の対応
        if (severity == ErrorSeverity.Critical)
        {
            // システムを安全な状態に
            await EnterSafeModeAsync();
            
            // アラート送信
            await SendCriticalAlertAsync(exception, context);
        }
        
        // 3. 診断情報の収集
        var diagnostics = await CollectDiagnosticsAsync(exception, context);
        
        // 4. 自動回復の試行
        if (CanAutoRecover(exception))
        {
            var recovered = await AttemptAutoRecoveryAsync(exception);
            if (recovered)
            {
                response.Status = ResponseStatus.AutoRecovered;
                return response;
            }
        }
        
        // 5. フォールバック処理
        await ExecuteFallbackAsync(context);
        
        response.Status = ResponseStatus.RequiresManualIntervention;
        response.Diagnostics = diagnostics;
        
        return response;
    }
}
```

### 2. 根本原因分析

```csharp
public class RootCauseAnalyzer
{
    public async Task<RootCauseAnalysis> AnalyzeAsync(ErrorReport report)
    {
        var analysis = new RootCauseAnalysis();
        
        // スタックトレース分析
        var stackAnalysis = AnalyzeStackTrace(report.Exception);
        
        // タイミング分析
        var timingAnalysis = await AnalyzeTimingPatternsAsync(report);
        
        // 環境要因分析
        var environmentAnalysis = AnalyzeEnvironment(report);
        
        // 相関分析
        var correlations = await FindCorrelationsAsync(report);
        
        // 根本原因の特定
        analysis.ProbableCauses = DetermineProbableCauses(
            stackAnalysis,
            timingAnalysis,
            environmentAnalysis,
            correlations);
        
        // 修正提案の生成
        analysis.Recommendations = GenerateRecommendations(
            analysis.ProbableCauses);
        
        return analysis;
    }
}
```

## テスト戦略

### 修正の検証

```csharp
[TestFixture]
public class BugFixVerificationTests
{
    [Test]
    public async Task Fixed_NullReferenceException_Should_Handle_Null_Customer()
    {
        // Arrange
        var repository = new Mock<ICustomerRepository>();
        repository.Setup(r => r.GetById(It.IsAny<int>()))
            .Returns((Customer)null);
        
        var form = new CustomerForm(repository.Object);
        
        // Act & Assert
        Assert.DoesNotThrowAsync(async () =>
        {
            await form.LoadCustomerDataAsync(999);
        });
        
        // UIが適切にクリアされていることを確認
        Assert.That(form.NameTextBox.Text, Is.Empty);
        Assert.That(form.EmailTextBox.Text, Is.Empty);
    }
    
    [Test]
    public async Task Fixed_Performance_Should_Complete_Within_Timeout()
    {
        // Arrange
        var service = new OptimizedReportService();
        var parameters = new ReportParameters
        {
            PageSize = 1000
        };
        
        // Act
        var stopwatch = Stopwatch.StartNew();
        var results = await service.GetCustomerReportAsync(parameters);
        stopwatch.Stop();
        
        // Assert
        Assert.That(results.Count(), Is.LessThanOrEqualTo(1000));
        Assert.That(stopwatch.ElapsedMilliseconds, Is.LessThan(1000),
            "クエリは1秒以内に完了する必要があります");
    }
}
```

## まとめ

このコマンドにより、エンタープライズアプリケーションの障害を体系的に分析・修正し、以下を実現します：

1. **迅速な問題解決** - 原因分析から修正まで体系的アプローチ
2. **再発防止** - 根本原因の特定と予防策の実装
3. **品質向上** - 包括的な修正とテストカバレッジ
4. **安定性向上** - 防御的プログラミングとエラーハンドリング
5. **保守性向上** - クリーンなコードと適切なログ記録