# エラーハンドリング設計書 - エンタープライズ統合管理システム

## 1. エラーハンドリング方針

### 基本原則
- **ユーザーフレンドリー**: 技術的な詳細を隠し、分かりやすいメッセージを表示
- **詳細なロギング**: 開発者向けに完全な情報を記録
- **一貫性**: アプリケーション全体で統一されたエラー処理
- **回復可能性**: 可能な限りエラーから回復する手段を提供
- **セキュリティ**: 機密情報がエラーメッセージに含まれないよう配慮

### エラー分類
```csharp
public enum ErrorCategory
{
    // ビジネスエラー（ユーザー起因）
    Validation,          // 入力検証エラー
    BusinessRule,        // ビジネスルール違反
    Authorization,       // 権限エラー
    
    // システムエラー（システム起因）
    Database,           // データベース関連
    Network,            // ネットワーク関連
    FileSystem,         // ファイルシステム関連
    ExternalSystem,     // 外部システム連携
    
    // アプリケーションエラー
    Configuration,      // 設定エラー
    UnexpectedError    // 予期しないエラー
}
```

## 2. 例外階層設計

### カスタム例外クラス
```csharp
// 基底例外クラス
public abstract class EnterpriseSystemException : Exception
{
    public ErrorCategory Category { get; }
    public string ErrorCode { get; }
    public string UserMessage { get; }
    public Dictionary<string, object> Context { get; }
    
    protected EnterpriseSystemException(
        ErrorCategory category,
        string errorCode,
        string userMessage,
        string technicalMessage,
        Exception innerException = null)
        : base(technicalMessage, innerException)
    {
        Category = category;
        ErrorCode = errorCode;
        UserMessage = userMessage;
        Context = new Dictionary<string, object>();
    }
    
    public void AddContext(string key, object value)
    {
        Context[key] = value;
    }
}

// ビジネス例外
public class BusinessRuleException : EnterpriseSystemException
{
    public BusinessRuleException(string errorCode, string userMessage, string rule)
        : base(ErrorCategory.BusinessRule, errorCode, userMessage, 
              $"Business rule violation: {rule}")
    {
        AddContext("Rule", rule);
    }
}

// 検証例外
public class ValidationException : EnterpriseSystemException
{
    public List<ValidationError> Errors { get; }
    
    public ValidationException(List<ValidationError> errors)
        : base(ErrorCategory.Validation, "VAL001", 
              "入力内容に誤りがあります。", 
              $"Validation failed with {errors.Count} errors")
    {
        Errors = errors;
    }
}

// データアクセス例外
public class DataAccessException : EnterpriseSystemException
{
    public string Query { get; }
    
    public DataAccessException(string operation, Exception innerException)
        : base(ErrorCategory.Database, "DAL001",
              "データベース操作中にエラーが発生しました。",
              $"Database operation failed: {operation}",
              innerException)
    {
        AddContext("Operation", operation);
    }
}

// 外部システム連携例外
public class ExternalSystemException : EnterpriseSystemException
{
    public string SystemName { get; }
    public int? HttpStatusCode { get; }
    
    public ExternalSystemException(
        string systemName, 
        string operation, 
        int? httpStatusCode = null,
        Exception innerException = null)
        : base(ErrorCategory.ExternalSystem, "EXT001",
              $"{systemName}との通信中にエラーが発生しました。",
              $"External system error: {systemName} - {operation}",
              innerException)
    {
        SystemName = systemName;
        HttpStatusCode = httpStatusCode;
        AddContext("SystemName", systemName);
        AddContext("Operation", operation);
    }
}
```

## 3. グローバルエラーハンドリング

### アプリケーションレベルのエラーハンドラ
```csharp
public class GlobalErrorHandler
{
    private readonly ILogger _logger;
    private readonly IErrorNotificationService _notificationService;
    
    public GlobalErrorHandler()
    {
        _logger = LogManager.GetLogger("GlobalError");
        _notificationService = ServiceLocator.GetService<IErrorNotificationService>();
        
        // アプリケーションドメインの未処理例外
        AppDomain.CurrentDomain.UnhandledException += OnUnhandledException;
        
        // Windows Formsの未処理例外
        Application.ThreadException += OnThreadException;
        Application.SetUnhandledExceptionMode(UnhandledExceptionMode.CatchException);
        
        // タスクの未処理例外
        TaskScheduler.UnobservedTaskException += OnUnobservedTaskException;
    }
    
    private void OnUnhandledException(object sender, UnhandledExceptionEventArgs e)
    {
        var exception = e.ExceptionObject as Exception;
        HandleCriticalError(exception, "AppDomain.UnhandledException");
        
        if (e.IsTerminating)
        {
            // アプリケーション終了前の処理
            EmergencyShutdown(exception);
        }
    }
    
    private void OnThreadException(object sender, ThreadExceptionEventArgs e)
    {
        HandleError(e.Exception, "Application.ThreadException");
    }
    
    private void OnUnobservedTaskException(object sender, UnobservedTaskExceptionEventArgs e)
    {
        HandleError(e.Exception, "TaskScheduler.UnobservedTaskException");
        e.SetObserved(); // アプリケーションのクラッシュを防ぐ
    }
    
    private void HandleError(Exception exception, string source)
    {
        try
        {
            // エラーログ記録
            LogError(exception, source);
            
            // ユーザー通知
            ShowUserNotification(exception);
            
            // 管理者通知（重大なエラーの場合）
            if (IsCriticalError(exception))
            {
                _notificationService.NotifyAdministratorsAsync(exception);
            }
        }
        catch (Exception ex)
        {
            // エラーハンドリング中のエラー
            try
            {
                _logger.Fatal(ex, "Error in error handler");
                MessageBox.Show(
                    "システムエラーが発生しました。アプリケーションを再起動してください。",
                    "致命的エラー",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
            catch
            {
                // 最後の手段
                Environment.FailFast("Fatal error in error handling", ex);
            }
        }
    }
    
    private void LogError(Exception exception, string source)
    {
        var errorInfo = new
        {
            Timestamp = DateTime.UtcNow,
            Source = source,
            MachineName = Environment.MachineName,
            User = Thread.CurrentPrincipal?.Identity?.Name,
            ProcessId = Process.GetCurrentProcess().Id,
            ThreadId = Thread.CurrentThread.ManagedThreadId,
            Exception = exception
        };
        
        _logger.Error(exception, "Unhandled exception: {@ErrorInfo}", errorInfo);
    }
}
```

### エラー表示サービス
```csharp
public interface IErrorDisplayService
{
    void ShowError(Exception exception, IWin32Window owner = null);
    void ShowValidationErrors(IEnumerable<ValidationError> errors, IWin32Window owner = null);
    DialogResult ShowErrorWithOptions(Exception exception, ErrorDisplayOptions options);
}

public class ErrorDisplayService : IErrorDisplayService
{
    private readonly ILogger _logger;
    
    public void ShowError(Exception exception, IWin32Window owner = null)
    {
        var errorForm = CreateErrorForm(exception);
        errorForm.ShowDialog(owner);
    }
    
    private ErrorDisplayForm CreateErrorForm(Exception exception)
    {
        var form = new ErrorDisplayForm();
        
        if (exception is EnterpriseSystemException enterpriseEx)
        {
            form.Title = GetErrorTitle(enterpriseEx.Category);
            form.Message = enterpriseEx.UserMessage;
            form.ErrorCode = enterpriseEx.ErrorCode;
            form.Details = FormatTechnicalDetails(enterpriseEx);
            form.Icon = GetErrorIcon(enterpriseEx.Category);
        }
        else
        {
            form.Title = "システムエラー";
            form.Message = "予期しないエラーが発生しました。";
            form.ErrorCode = "SYS001";
            form.Details = exception.ToString();
            form.Icon = MessageBoxIcon.Error;
        }
        
        // 回復オプションの設定
        form.RecoveryOptions = GetRecoveryOptions(exception);
        
        return form;
    }
    
    private List<RecoveryOption> GetRecoveryOptions(Exception exception)
    {
        var options = new List<RecoveryOption>();
        
        if (exception is DataAccessException)
        {
            options.Add(new RecoveryOption
            {
                Text = "再試行",
                Action = RecoveryAction.Retry
            });
        }
        
        if (exception is ExternalSystemException)
        {
            options.Add(new RecoveryOption
            {
                Text = "オフラインモードで続行",
                Action = RecoveryAction.ContinueOffline
            });
        }
        
        options.Add(new RecoveryOption
        {
            Text = "アプリケーションを再起動",
            Action = RecoveryAction.RestartApplication
        });
        
        return options;
    }
}

// エラー表示フォーム
public partial class ErrorDisplayForm : Form
{
    public string Title { get; set; }
    public string Message { get; set; }
    public string ErrorCode { get; set; }
    public string Details { get; set; }
    public MessageBoxIcon Icon { get; set; }
    public List<RecoveryOption> RecoveryOptions { get; set; }
    
    protected override void OnLoad(EventArgs e)
    {
        base.OnLoad(e);
        
        this.Text = Title;
        lblMessage.Text = Message;
        lblErrorCode.Text = $"エラーコード: {ErrorCode}";
        picIcon.Image = GetIconImage(Icon);
        
        // 詳細情報は折りたたみ可能に
        txtDetails.Text = Details;
        pnlDetails.Visible = false;
        
        // 回復オプションボタンを動的生成
        CreateRecoveryButtons();
    }
}
```

## 4. エラーロギング

### 構造化ロギング
```csharp
public class ErrorLogger : IErrorLogger
{
    private readonly ILogger _logger;
    
    public ErrorLogger()
    {
        _logger = LogManager.GetCurrentClassLogger();
    }
    
    public void LogError(Exception exception, ErrorContext context)
    {
        var errorEntry = new ErrorLogEntry
        {
            Id = Guid.NewGuid(),
            Timestamp = DateTime.UtcNow,
            Category = DetermineCategory(exception),
            Severity = DetermineSeverity(exception),
            
            // エラー情報
            ExceptionType = exception.GetType().FullName,
            Message = exception.Message,
            StackTrace = exception.StackTrace,
            InnerException = exception.InnerException?.ToString(),
            
            // コンテキスト情報
            User = context.User,
            SessionId = context.SessionId,
            CorrelationId = context.CorrelationId,
            
            // 環境情報
            MachineName = Environment.MachineName,
            ApplicationVersion = Assembly.GetExecutingAssembly().GetName().Version.ToString(),
            OperatingSystem = Environment.OSVersion.ToString(),
            
            // カスタムプロパティ
            CustomProperties = ExtractCustomProperties(exception)
        };
        
        // 重要度に応じたログレベル
        switch (errorEntry.Severity)
        {
            case ErrorSeverity.Critical:
                _logger.Fatal(exception, "Critical error: {@ErrorEntry}", errorEntry);
                break;
            case ErrorSeverity.High:
                _logger.Error(exception, "High severity error: {@ErrorEntry}", errorEntry);
                break;
            case ErrorSeverity.Medium:
                _logger.Warn(exception, "Medium severity error: {@ErrorEntry}", errorEntry);
                break;
            case ErrorSeverity.Low:
                _logger.Info(exception, "Low severity error: {@ErrorEntry}", errorEntry);
                break;
        }
        
        // データベースにも記録
        SaveToDatabase(errorEntry);
    }
    
    private async void SaveToDatabase(ErrorLogEntry entry)
    {
        try
        {
            using (var context = new LoggingDbContext())
            {
                context.ErrorLogs.Add(entry);
                await context.SaveChangesAsync();
            }
        }
        catch (Exception ex)
        {
            // データベース保存失敗時はファイルに保存
            _logger.Error(ex, "Failed to save error log to database");
            SaveToFailoverFile(entry);
        }
    }
}
```

### ログ設定（NLog）
```xml
<?xml version="1.0" encoding="utf-8" ?>
<nlog xmlns="http://www.nlog-project.org/schemas/NLog.xsd"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      
    <targets>
        <!-- ファイルターゲット -->
        <target name="errorFile" xsi:type="File"
                fileName="${basedir}/logs/errors/${shortdate}_error.log"
                layout="${longdate}|${level:uppercase=true}|${logger}|${message} ${exception:format=tostring}"
                archiveEvery="Day"
                archiveNumbering="Rolling"
                maxArchiveFiles="30" />
                
        <!-- データベースターゲット -->
        <target name="database" xsi:type="Database"
                connectionString="Data Source=.\SQLEXPRESS;Initial Catalog=EnterpriseLog;Integrated Security=True">
            <commandText>
                INSERT INTO ErrorLogs (
                    Timestamp, Level, Logger, Message, Exception,
                    MachineName, UserName, CorrelationId
                ) VALUES (
                    @timestamp, @level, @logger, @message, @exception,
                    @machineName, @userName, @correlationId
                )
            </commandText>
            <parameter name="@timestamp" layout="${date}" />
            <parameter name="@level" layout="${level}" />
            <parameter name="@logger" layout="${logger}" />
            <parameter name="@message" layout="${message}" />
            <parameter name="@exception" layout="${exception:tostring}" />
            <parameter name="@machineName" layout="${machinename}" />
            <parameter name="@userName" layout="${windows-identity}" />
            <parameter name="@correlationId" layout="${mdlc:CorrelationId}" />
        </target>
        
        <!-- メール通知ターゲット（重大エラー用） -->
        <target name="mail" xsi:type="Mail"
                smtpServer="smtp.company.local"
                from="system@company.local"
                to="it-support@company.local"
                subject="Critical Error in Enterprise System"
                body="${message}${newline}${exception:format=tostring}" />
    </targets>
    
    <rules>
        <!-- エラーレベル以上をファイルに記録 -->
        <logger name="*" minlevel="Error" writeTo="errorFile" />
        
        <!-- 警告レベル以上をデータベースに記録 -->
        <logger name="*" minlevel="Warn" writeTo="database" />
        
        <!-- 致命的エラーはメール通知 -->
        <logger name="*" minlevel="Fatal" writeTo="mail" />
    </rules>
</nlog>
```

## 5. エラー回復戦略

### リトライポリシー
```csharp
public class RetryPolicy
{
    private readonly int _maxRetries;
    private readonly TimeSpan _initialDelay;
    private readonly BackoffStrategy _backoffStrategy;
    
    public RetryPolicy(int maxRetries = 3, int initialDelayMs = 1000, 
        BackoffStrategy strategy = BackoffStrategy.Exponential)
    {
        _maxRetries = maxRetries;
        _initialDelay = TimeSpan.FromMilliseconds(initialDelayMs);
        _backoffStrategy = strategy;
    }
    
    public async Task<T> ExecuteAsync<T>(
        Func<Task<T>> operation,
        Func<Exception, bool> shouldRetry = null)
    {
        shouldRetry = shouldRetry ?? IsTransientError;
        
        for (int attempt = 0; attempt <= _maxRetries; attempt++)
        {
            try
            {
                return await operation();
            }
            catch (Exception ex) when (attempt < _maxRetries && shouldRetry(ex))
            {
                var delay = GetDelay(attempt);
                
                _logger.Warn(ex, 
                    "Operation failed on attempt {Attempt}. Retrying in {Delay}ms...",
                    attempt + 1, delay.TotalMilliseconds);
                
                await Task.Delay(delay);
            }
        }
        
        // 最後の試行
        return await operation();
    }
    
    private TimeSpan GetDelay(int attempt)
    {
        return _backoffStrategy switch
        {
            BackoffStrategy.Fixed => _initialDelay,
            BackoffStrategy.Linear => TimeSpan.FromMilliseconds(
                _initialDelay.TotalMilliseconds * (attempt + 1)),
            BackoffStrategy.Exponential => TimeSpan.FromMilliseconds(
                _initialDelay.TotalMilliseconds * Math.Pow(2, attempt)),
            _ => _initialDelay
        };
    }
    
    private bool IsTransientError(Exception ex)
    {
        return ex is TimeoutException ||
               ex is TaskCanceledException ||
               (ex is HttpRequestException httpEx && IsRetryableStatusCode(httpEx)) ||
               (ex is SqlException sqlEx && IsTransientSqlError(sqlEx));
    }
}

// 使用例
public class ResilientDataService
{
    private readonly RetryPolicy _retryPolicy;
    
    public async Task<Customer> GetCustomerAsync(int id)
    {
        return await _retryPolicy.ExecuteAsync(async () =>
        {
            using (var context = new DataContext())
            {
                return await context.Customers
                    .Include(c => c.Orders)
                    .FirstOrDefaultAsync(c => c.Id == id);
            }
        });
    }
}
```

### サーキットブレーカー
```csharp
public class CircuitBreaker
{
    private readonly int _failureThreshold;
    private readonly TimeSpan _timeout;
    private int _failureCount;
    private DateTime _lastFailureTime;
    private CircuitState _state = CircuitState.Closed;
    
    public CircuitBreaker(int failureThreshold = 5, int timeoutSeconds = 60)
    {
        _failureThreshold = failureThreshold;
        _timeout = TimeSpan.FromSeconds(timeoutSeconds);
    }
    
    public async Task<T> ExecuteAsync<T>(Func<Task<T>> operation)
    {
        if (_state == CircuitState.Open)
        {
            if (DateTime.UtcNow - _lastFailureTime > _timeout)
            {
                _state = CircuitState.HalfOpen;
            }
            else
            {
                throw new CircuitBreakerOpenException(
                    "Circuit breaker is open. Service is temporarily unavailable.");
            }
        }
        
        try
        {
            var result = await operation();
            
            if (_state == CircuitState.HalfOpen)
            {
                _state = CircuitState.Closed;
                _failureCount = 0;
            }
            
            return result;
        }
        catch (Exception ex)
        {
            RecordFailure();
            throw;
        }
    }
    
    private void RecordFailure()
    {
        _failureCount++;
        _lastFailureTime = DateTime.UtcNow;
        
        if (_failureCount >= _failureThreshold)
        {
            _state = CircuitState.Open;
            _logger.Error($"Circuit breaker opened after {_failureCount} failures");
        }
    }
}
```

## 6. エラー監視とアラート

### リアルタイム監視
```csharp
public class ErrorMonitoringService
{
    private readonly IErrorRepository _errorRepository;
    private readonly IAlertService _alertService;
    private readonly Timer _monitoringTimer;
    
    public ErrorMonitoringService()
    {
        _monitoringTimer = new Timer(MonitorErrors, null, 
            TimeSpan.Zero, TimeSpan.FromMinutes(5));
    }
    
    private async void MonitorErrors(object state)
    {
        try
        {
            var recentErrors = await _errorRepository
                .GetErrorsSinceAsync(DateTime.UtcNow.AddMinutes(-5));
            
            // エラー率の計算
            var errorRate = CalculateErrorRate(recentErrors);
            if (errorRate > 0.05) // 5%以上
            {
                await _alertService.SendAlertAsync(new Alert
                {
                    Type = AlertType.HighErrorRate,
                    Message = $"エラー率が閾値を超えました: {errorRate:P}",
                    Severity = AlertSeverity.High
                });
            }
            
            // 特定のエラーパターン検出
            DetectErrorPatterns(recentErrors);
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "Error monitoring failed");
        }
    }
    
    private void DetectErrorPatterns(IEnumerable<ErrorLogEntry> errors)
    {
        // 同一エラーの繰り返し
        var repeatingErrors = errors
            .GroupBy(e => e.ExceptionType)
            .Where(g => g.Count() > 10);
        
        foreach (var errorGroup in repeatingErrors)
        {
            _alertService.SendAlertAsync(new Alert
            {
                Type = AlertType.RepeatingError,
                Message = $"エラー '{errorGroup.Key}' が {errorGroup.Count()}回発生しています",
                Severity = AlertSeverity.Medium
            });
        }
    }
}
```

このエラーハンドリング設計により、堅牢で保守性の高いエンタープライズアプリケーションの構築が可能になります。