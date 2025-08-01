# Windows Forms ベストプラクティス - エンタープライズアプリケーション開発

## 1. フォーム設計のベストプラクティス

### 基本的なフォーム構造
```csharp
public partial class BaseBusinessForm : Form
{
    protected readonly ILogger Logger;
    protected readonly IServiceProvider ServiceProvider;
    private bool _isInitialized;
    private readonly List<IDisposable> _disposables = new List<IDisposable>();
    
    public BaseBusinessForm()
    {
        // サービスの初期化
        ServiceProvider = ServiceLocator.Instance;
        Logger = ServiceProvider.GetService<ILogger<BaseBusinessForm>>();
        
        InitializeComponent();
        SetupFormDefaults();
    }
    
    private void SetupFormDefaults()
    {
        // DPI対応
        AutoScaleMode = AutoScaleMode.Dpi;
        AutoScaleDimensions = new SizeF(96F, 96F);
        
        // フォント設定
        Font = SystemFonts.MessageBoxFont;
        
        // ダブルバッファリング
        SetStyle(ControlStyles.AllPaintingInWmPaint | 
                ControlStyles.UserPaint | 
                ControlStyles.DoubleBuffer | 
                ControlStyles.ResizeRedraw, true);
        
        // デフォルトボタン設定
        AcceptButton = GetDefaultAcceptButton();
        CancelButton = GetDefaultCancelButton();
    }
    
    protected override async void OnLoad(EventArgs e)
    {
        base.OnLoad(e);
        
        if (!_isInitialized)
        {
            try
            {
                ShowLoadingIndicator(true);
                await InitializeAsync();
                _isInitialized = true;
            }
            catch (Exception ex)
            {
                Logger.LogError(ex, "Form initialization failed");
                HandleInitializationError(ex);
            }
            finally
            {
                ShowLoadingIndicator(false);
            }
        }
    }
    
    protected virtual async Task InitializeAsync()
    {
        // オーバーライドして初期化処理を実装
        await Task.CompletedTask;
    }
    
    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            // 登録されたディスポーザブルをすべて解放
            foreach (var disposable in _disposables)
            {
                disposable?.Dispose();
            }
            _disposables.Clear();
        }
        
        base.Dispose(disposing);
    }
    
    protected void RegisterDisposable(IDisposable disposable)
    {
        _disposables.Add(disposable);
    }
}
```

### レスポンシブフォームデザイン
```csharp
public class ResponsiveFormBase : BaseBusinessForm
{
    private readonly TableLayoutPanel _mainLayout;
    private Size _lastSize;
    
    public ResponsiveFormBase()
    {
        _mainLayout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            AutoSize = true
        };
        
        Controls.Add(_mainLayout);
        
        // リサイズイベント
        Resize += OnFormResize;
        _lastSize = Size;
    }
    
    private void OnFormResize(object sender, EventArgs e)
    {
        // サイズ変更の閾値チェック
        if (Math.Abs(Width - _lastSize.Width) > 100 || 
            Math.Abs(Height - _lastSize.Height) > 100)
        {
            AdjustLayout();
            _lastSize = Size;
        }
    }
    
    protected virtual void AdjustLayout()
    {
        SuspendLayout();
        
        try
        {
            if (Width < 800) // コンパクトレイアウト
            {
                ApplyCompactLayout();
            }
            else if (Width < 1200) // 標準レイアウト
            {
                ApplyStandardLayout();
            }
            else // ワイドレイアウト
            {
                ApplyWideLayout();
            }
        }
        finally
        {
            ResumeLayout(true);
        }
    }
    
    private void ApplyCompactLayout()
    {
        _mainLayout.ColumnCount = 1;
        _mainLayout.RowCount = GetComponentCount();
        
        // すべてのコントロールを縦に配置
        foreach (Control control in GetLayoutControls())
        {
            _mainLayout.SetColumnSpan(control, 1);
        }
    }
}
```

## 2. データバインディングのベストプラクティス

### 双方向データバインディング
```csharp
public class DataBoundForm<TViewModel> : BaseBusinessForm where TViewModel : class, INotifyPropertyChanged
{
    private BindingSource _bindingSource;
    private TViewModel _viewModel;
    private readonly Dictionary<Control, ErrorProvider> _errorProviders = new();
    
    protected TViewModel ViewModel
    {
        get => _viewModel;
        set
        {
            if (_viewModel != null)
            {
                _viewModel.PropertyChanged -= OnViewModelPropertyChanged;
                if (_viewModel is INotifyDataErrorInfo errorInfo)
                {
                    errorInfo.ErrorsChanged -= OnErrorsChanged;
                }
            }
            
            _viewModel = value;
            
            if (_viewModel != null)
            {
                _viewModel.PropertyChanged += OnViewModelPropertyChanged;
                if (_viewModel is INotifyDataErrorInfo errorInfo)
                {
                    errorInfo.ErrorsChanged += OnErrorsChanged;
                }
            }
            
            _bindingSource.DataSource = _viewModel;
        }
    }
    
    protected override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        
        _bindingSource = new BindingSource();
        SetupDataBindings();
    }
    
    protected virtual void SetupDataBindings()
    {
        // オーバーライドして具体的なバインディングを設定
    }
    
    protected void BindProperty<TControl>(
        TControl control, 
        string controlProperty,
        string dataProperty,
        DataSourceUpdateMode updateMode = DataSourceUpdateMode.OnPropertyChanged)
        where TControl : Control
    {
        var binding = new Binding(controlProperty, _bindingSource, dataProperty, true, updateMode);
        
        // フォーマットとパースのイベント設定
        binding.Format += OnBindingFormat;
        binding.Parse += OnBindingParse;
        
        control.DataBindings.Add(binding);
        
        // エラープロバイダーの設定
        if (!_errorProviders.ContainsKey(control))
        {
            var errorProvider = new ErrorProvider();
            errorProvider.SetIconAlignment(control, ErrorIconAlignment.MiddleRight);
            _errorProviders[control] = errorProvider;
        }
    }
    
    private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
    {
        // UIスレッドで実行
        if (InvokeRequired)
        {
            BeginInvoke(new Action(() => OnViewModelPropertyChanged(sender, e)));
            return;
        }
        
        // カスタムプロパティ変更処理
        HandlePropertyChanged(e.PropertyName);
    }
    
    private void OnErrorsChanged(object sender, DataErrorsChangedEventArgs e)
    {
        if (InvokeRequired)
        {
            BeginInvoke(new Action(() => OnErrorsChanged(sender, e)));
            return;
        }
        
        UpdateErrorDisplay(e.PropertyName);
    }
    
    private void UpdateErrorDisplay(string propertyName)
    {
        var binding = _bindingSource.CurrencyManager.Bindings
            .Cast<Binding>()
            .FirstOrDefault(b => b.BindingMemberInfo.BindingMember == propertyName);
        
        if (binding != null && _errorProviders.TryGetValue(binding.Control, out var errorProvider))
        {
            var errors = (_viewModel as INotifyDataErrorInfo)?.GetErrors(propertyName);
            var errorMessage = errors?.Cast<object>().FirstOrDefault()?.ToString() ?? string.Empty;
            
            errorProvider.SetError(binding.Control, errorMessage);
        }
    }
}
```

### リストデータバインディング
```csharp
public class ListDataBindingHelper<T> where T : class
{
    private readonly DataGridView _gridView;
    private readonly BindingList<T> _bindingList;
    private readonly BindingSource _bindingSource;
    
    public ListDataBindingHelper(DataGridView gridView)
    {
        _gridView = gridView;
        _bindingList = new BindingList<T>();
        _bindingSource = new BindingSource(_bindingList, null);
        
        SetupGrid();
    }
    
    private void SetupGrid()
    {
        _gridView.AutoGenerateColumns = false;
        _gridView.DataSource = _bindingSource;
        
        // パフォーマンス最適化
        _gridView.SuspendLayout();
        
        typeof(DataGridView).InvokeMember("DoubleBuffered",
            BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.SetProperty,
            null, _gridView, new object[] { true });
        
        _gridView.ResumeLayout();
    }
    
    public void SetData(IEnumerable<T> data)
    {
        _bindingList.RaiseListChangedEvents = false;
        
        try
        {
            _bindingList.Clear();
            foreach (var item in data)
            {
                _bindingList.Add(item);
            }
        }
        finally
        {
            _bindingList.RaiseListChangedEvents = true;
            _bindingList.ResetBindings();
        }
    }
    
    public void AddColumn<TProperty>(
        string propertyName,
        string headerText,
        Expression<Func<T, TProperty>> propertyExpression)
    {
        var column = new DataGridViewTextBoxColumn
        {
            DataPropertyName = propertyName,
            HeaderText = headerText,
            Name = $"col{propertyName}"
        };
        
        // 型に応じた書式設定
        if (typeof(TProperty) == typeof(decimal) || typeof(TProperty) == typeof(double))
        {
            column.DefaultCellStyle.Format = "N2";
            column.DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
        }
        else if (typeof(TProperty) == typeof(DateTime))
        {
            column.DefaultCellStyle.Format = "yyyy/MM/dd HH:mm";
        }
        
        _gridView.Columns.Add(column);
    }
}
```

## 3. 非同期処理のベストプラクティス

### 非同期操作の実装
```csharp
public static class AsyncFormExtensions
{
    public static async Task RunAsync(
        this Form form,
        Func<IProgress<int>, CancellationToken, Task> operation,
        string progressMessage = "処理中...")
    {
        using (var progressForm = new ProgressDialogForm())
        {
            var cts = new CancellationTokenSource();
            progressForm.CancelRequested += (s, e) => cts.Cancel();
            
            var progress = new Progress<int>(value =>
            {
                form.BeginInvoke(new Action(() =>
                {
                    progressForm.UpdateProgress(value, progressMessage);
                }));
            });
            
            progressForm.Show(form);
            
            try
            {
                await operation(progress, cts.Token);
            }
            catch (OperationCanceledException)
            {
                MessageBox.Show("処理がキャンセルされました。", "キャンセル", 
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            finally
            {
                progressForm.Close();
            }
        }
    }
    
    public static async Task<T> RunAsync<T>(
        this Form form,
        Func<Task<T>> operation,
        Action<T> onSuccess,
        Action<Exception> onError = null)
    {
        form.Enabled = false;
        form.Cursor = Cursors.WaitCursor;
        
        try
        {
            var result = await operation();
            onSuccess?.Invoke(result);
            return result;
        }
        catch (Exception ex)
        {
            if (onError != null)
            {
                onError(ex);
            }
            else
            {
                MessageBox.Show(
                    $"エラーが発生しました: {ex.Message}",
                    "エラー",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
            throw;
        }
        finally
        {
            form.Enabled = true;
            form.Cursor = Cursors.Default;
        }
    }
}

// 使用例
public partial class CustomerForm : BaseBusinessForm
{
    private async void btnLoadData_Click(object sender, EventArgs e)
    {
        await this.RunAsync(
            async (progress, cancellationToken) =>
            {
                var customers = await _customerService.GetAllCustomersAsync(cancellationToken);
                
                for (int i = 0; i < customers.Count; i++)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    
                    // 処理...
                    progress.Report((i + 1) * 100 / customers.Count);
                }
            },
            "顧客データを読み込んでいます..."
        );
    }
}
```

### BackgroundWorker パターン（レガシーサポート）
```csharp
public class LongRunningOperation<TInput, TResult>
{
    private readonly BackgroundWorker _worker;
    private readonly Action<TResult> _onCompleted;
    private readonly Action<Exception> _onError;
    private readonly Action<int> _onProgress;
    
    public LongRunningOperation(
        Func<TInput, BackgroundWorker, TResult> operation,
        Action<TResult> onCompleted,
        Action<Exception> onError = null,
        Action<int> onProgress = null)
    {
        _onCompleted = onCompleted;
        _onError = onError;
        _onProgress = onProgress;
        
        _worker = new BackgroundWorker
        {
            WorkerReportsProgress = true,
            WorkerSupportsCancellation = true
        };
        
        _worker.DoWork += (s, e) =>
        {
            e.Result = operation((TInput)e.Argument, _worker);
        };
        
        _worker.ProgressChanged += (s, e) =>
        {
            _onProgress?.Invoke(e.ProgressPercentage);
        };
        
        _worker.RunWorkerCompleted += (s, e) =>
        {
            if (e.Error != null)
            {
                _onError?.Invoke(e.Error);
            }
            else if (!e.Cancelled)
            {
                _onCompleted?.Invoke((TResult)e.Result);
            }
        };
    }
    
    public void Execute(TInput input)
    {
        _worker.RunWorkerAsync(input);
    }
    
    public void Cancel()
    {
        _worker.CancelAsync();
    }
}
```

## 4. メモリ管理のベストプラクティス

### リソース管理
```csharp
public class ResourceManager : IDisposable
{
    private readonly List<IDisposable> _managedResources = new();
    private readonly List<IntPtr> _unmanagedResources = new();
    private bool _disposed;
    
    public T AddManagedResource<T>(T resource) where T : IDisposable
    {
        _managedResources.Add(resource);
        return resource;
    }
    
    public void AddUnmanagedResource(IntPtr handle)
    {
        _unmanagedResources.Add(handle);
    }
    
    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                // マネージドリソースの解放
                foreach (var resource in _managedResources)
                {
                    resource?.Dispose();
                }
                _managedResources.Clear();
            }
            
            // アンマネージドリソースの解放
            foreach (var handle in _unmanagedResources)
            {
                if (handle != IntPtr.Zero)
                {
                    // 適切なWin32 APIを呼び出してリソースを解放
                    NativeMethods.CloseHandle(handle);
                }
            }
            _unmanagedResources.Clear();
            
            _disposed = true;
        }
    }
    
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
    
    ~ResourceManager()
    {
        Dispose(false);
    }
}

// イベントハンドラーのメモリリーク防止
public class WeakEventManager<TEventArgs> where TEventArgs : EventArgs
{
    private readonly List<WeakReference> _handlers = new();
    
    public void AddHandler(EventHandler<TEventArgs> handler)
    {
        _handlers.Add(new WeakReference(handler));
        CleanupHandlers();
    }
    
    public void RemoveHandler(EventHandler<TEventArgs> handler)
    {
        _handlers.RemoveAll(wr => wr.Target == null || wr.Target.Equals(handler));
    }
    
    public void Raise(object sender, TEventArgs e)
    {
        CleanupHandlers();
        
        foreach (var weakRef in _handlers.ToArray())
        {
            if (weakRef.Target is EventHandler<TEventArgs> handler)
            {
                handler(sender, e);
            }
        }
    }
    
    private void CleanupHandlers()
    {
        _handlers.RemoveAll(wr => !wr.IsAlive);
    }
}
```

## 5. パフォーマンス最適化

### UIの仮想化
```csharp
public class VirtualListView : ListView
{
    private readonly IVirtualListDataSource _dataSource;
    private readonly Cache<int, ListViewItem> _itemCache;
    
    public VirtualListView(IVirtualListDataSource dataSource)
    {
        _dataSource = dataSource;
        _itemCache = new Cache<int, ListViewItem>(1000); // 1000アイテムをキャッシュ
        
        VirtualMode = true;
        RetrieveVirtualItem += OnRetrieveVirtualItem;
        CacheVirtualItems += OnCacheVirtualItems;
        
        VirtualListSize = _dataSource.Count;
    }
    
    private void OnRetrieveVirtualItem(object sender, RetrieveVirtualItemEventArgs e)
    {
        if (_itemCache.TryGetValue(e.ItemIndex, out var cachedItem))
        {
            e.Item = cachedItem;
            return;
        }
        
        var data = _dataSource.GetItem(e.ItemIndex);
        e.Item = CreateListViewItem(data);
        _itemCache.Add(e.ItemIndex, e.Item);
    }
    
    private void OnCacheVirtualItems(object sender, CacheVirtualItemsEventArgs e)
    {
        // 表示される範囲のアイテムを事前にキャッシュ
        for (int i = e.StartIndex; i <= e.EndIndex; i++)
        {
            if (!_itemCache.ContainsKey(i))
            {
                var data = _dataSource.GetItem(i);
                var item = CreateListViewItem(data);
                _itemCache.Add(i, item);
            }
        }
    }
    
    public void RefreshItems()
    {
        _itemCache.Clear();
        VirtualListSize = _dataSource.Count;
        Invalidate();
    }
}
```

### 描画の最適化
```csharp
public class OptimizedPanel : Panel
{
    private readonly BufferedGraphicsContext _graphicsContext;
    private BufferedGraphics _bufferedGraphics;
    
    public OptimizedPanel()
    {
        SetStyle(ControlStyles.AllPaintingInWmPaint | 
                ControlStyles.UserPaint | 
                ControlStyles.DoubleBuffer | 
                ControlStyles.ResizeRedraw, true);
        
        _graphicsContext = BufferedGraphicsManager.Current;
        UpdateBuffer();
    }
    
    protected override void OnPaint(PaintEventArgs e)
    {
        if (_bufferedGraphics == null)
        {
            UpdateBuffer();
        }
        
        // バッファに描画
        var g = _bufferedGraphics.Graphics;
        g.Clear(BackColor);
        
        DrawContent(g);
        
        // 画面に転送
        _bufferedGraphics.Render(e.Graphics);
    }
    
    protected override void OnResize(EventArgs e)
    {
        base.OnResize(e);
        UpdateBuffer();
        Invalidate();
    }
    
    private void UpdateBuffer()
    {
        if (Width > 0 && Height > 0)
        {
            _bufferedGraphics?.Dispose();
            _bufferedGraphics = _graphicsContext.Allocate(
                CreateGraphics(), 
                new Rectangle(0, 0, Width, Height));
        }
    }
    
    protected virtual void DrawContent(Graphics g)
    {
        // オーバーライドして描画処理を実装
    }
    
    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            _bufferedGraphics?.Dispose();
        }
        base.Dispose(disposing);
    }
}
```

## 6. 国際化（i18n）対応

### リソース管理
```csharp
public static class LocalizationManager
{
    private static ResourceManager _resourceManager;
    private static CultureInfo _currentCulture;
    
    static LocalizationManager()
    {
        _resourceManager = new ResourceManager(
            "EnterpriseApp.Resources.Strings", 
            Assembly.GetExecutingAssembly());
        
        _currentCulture = Thread.CurrentThread.CurrentUICulture;
    }
    
    public static string GetString(string key)
    {
        return _resourceManager.GetString(key, _currentCulture) ?? key;
    }
    
    public static void SetCulture(string cultureName)
    {
        _currentCulture = new CultureInfo(cultureName);
        Thread.CurrentThread.CurrentUICulture = _currentCulture;
        Thread.CurrentThread.CurrentCulture = _currentCulture;
        
        // すべての開いているフォームを更新
        foreach (Form form in Application.OpenForms)
        {
            UpdateFormLocalization(form);
        }
    }
    
    private static void UpdateFormLocalization(Control control)
    {
        if (control.Tag is string resourceKey)
        {
            control.Text = GetString(resourceKey);
        }
        
        foreach (Control child in control.Controls)
        {
            UpdateFormLocalization(child);
        }
    }
}

// ローカライズ可能なフォーム
public class LocalizableForm : BaseBusinessForm
{
    protected override void OnLoad(EventArgs e)
    {
        base.OnLoad(e);
        LocalizeControls();
    }
    
    protected virtual void LocalizeControls()
    {
        // フォームタイトル
        if (Tag is string formKey)
        {
            Text = LocalizationManager.GetString(formKey);
        }
        
        // 子コントロール
        LocalizeControlHierarchy(this);
    }
    
    private void LocalizeControlHierarchy(Control parent)
    {
        foreach (Control control in parent.Controls)
        {
            if (control.Tag is string resourceKey)
            {
                control.Text = LocalizationManager.GetString(resourceKey);
            }
            
            // ツールチップの設定
            var toolTipKey = $"{control.Tag}_ToolTip";
            var toolTipText = LocalizationManager.GetString(toolTipKey);
            if (toolTipText != toolTipKey)
            {
                toolTip1.SetToolTip(control, toolTipText);
            }
            
            LocalizeControlHierarchy(control);
        }
    }
}
```

これらのベストプラクティスを適用することで、高品質で保守性の高いWindows Formsアプリケーションを開発できます。