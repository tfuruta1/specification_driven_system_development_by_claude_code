# /winforms-patterns - Windows Forms設計パターン適用コマンド

**.NET Framework 4.0 専用 Windows Forms MVPパターン・ベストプラクティス**

## 📋 コマンド概要

.NET Framework 4.0のWindows Formsアプリケーション開発における主要設計パターンの適用とベストプラクティスの実装を支援します。async/awaitやHttpClientが使用できない制約下での最適なアーキテクチャを提供します。

## 🚀 使用方法

### 基本構文
```bash
/winforms-patterns [pattern] [options]
```

### 主要パターン

#### 1. MVP (Model-View-Presenter) パターン
```bash
/winforms-patterns mvp
```
**適用範囲**: 全アプリケーションのMVPアーキテクチャ実装

#### 2. ファクトリーパターン + DI
```bash
/winforms-patterns factory_di
```
**適用範囲**: Unity Containerを使用したファクトリー + 依存性注入

#### 3. リポジトリパターン
```bash
/winforms-patterns repository
```
**適用範囲**: データアクセス層のリポジトリパターン実装

#### 4. Observerパターン (.NET 4.0対応)
```bash
/winforms-patterns observer_dotnet40
```
**適用範囲**: イベントドリブンアーキテクチャ (.NET 4.0制約対応)

## 🎯 .NET Framework 4.0 特化実装

### MVPパターン 実装例

#### IView インターフェース
```csharp
// .NET Framework 4.0 対応 IView インターフェース
public interface ICustomerView
{
    // イベント定義 (.NET 4.0 対応)
    event EventHandler<CustomerSearchEventArgs> SearchRequested;
    event EventHandler<int> CustomerSelected;
    event EventHandler<Customer> CustomerSaveRequested;
    
    // View操作メソッド
    void DisplayCustomers(List<Customer> customers);
    void ShowMessage(string message, MessageType type);
    void SetLoadingState(bool isLoading);
    void ClearForm();
    
    // プロパティアクセス
    Customer CurrentCustomer { get; set; }
    bool IsFormValid { get; }
}

// .NET 4.0 対応イベント引数
public class CustomerSearchEventArgs : EventArgs
{
    public string SearchTerm { get; set; }
    public SearchType SearchType { get; set; }
    
    public CustomerSearchEventArgs(string searchTerm, SearchType searchType)
    {
        SearchTerm = searchTerm;
        SearchType = searchType;
    }
}
```

#### Presenter 実装 (BackgroundWorker使用)
```csharp
// .NET Framework 4.0 対応 Presenter (async/await不可)
public class CustomerPresenter
{
    private readonly ICustomerView _view;
    private readonly ICustomerService _customerService;
    private readonly BackgroundWorker _searchWorker;
    private readonly BackgroundWorker _saveWorker;
    
    public CustomerPresenter(ICustomerView view, ICustomerService customerService)
    {
        _view = view;
        _customerService = customerService;
        
        // BackgroundWorker 初期化 (.NET 4.0 非同期パターン)
        InitializeBackgroundWorkers();
        
        // イベントハンドラ登録
        _view.SearchRequested += OnSearchRequested;
        _view.CustomerSaveRequested += OnCustomerSaveRequested;
    }
    
    private void InitializeBackgroundWorkers()
    {
        // 顧客検索用 BackgroundWorker
        _searchWorker = new BackgroundWorker();
        _searchWorker.DoWork += SearchWorker_DoWork;
        _searchWorker.RunWorkerCompleted += SearchWorker_Completed;
        
        // 顧客保存用 BackgroundWorker
        _saveWorker = new BackgroundWorker();
        _saveWorker.DoWork += SaveWorker_DoWork;
        _saveWorker.RunWorkerCompleted += SaveWorker_Completed;
    }
    
    private void OnSearchRequested(object sender, CustomerSearchEventArgs e)
    {
        if (!_searchWorker.IsBusy)
        {
            _view.SetLoadingState(true);
            _searchWorker.RunWorkerAsync(e);
        }
    }
    
    private void SearchWorker_DoWork(object sender, DoWorkEventArgs e)
    {
        var args = (CustomerSearchEventArgs)e.Argument;
        try
        {
            // サービス呼び出し (同期処理)
            var customers = _customerService.SearchCustomers(args.SearchTerm, args.SearchType);
            e.Result = customers;
        }
        catch (Exception ex)
        {
            e.Result = ex;
        }
    }
    
    private void SearchWorker_Completed(object sender, RunWorkerCompletedEventArgs e)
    {
        _view.SetLoadingState(false);
        
        if (e.Result is Exception)
        {
            var error = (Exception)e.Result;
            _view.ShowMessage($"検索エラー: {error.Message}", MessageType.Error);
        }
        else
        {
            var customers = (List<Customer>)e.Result;
            _view.DisplayCustomers(customers);
        }
    }
}
```

### Unity Container DI設定 (.NET 4.0対応)
```csharp
// .NET Framework 4.0 対応 Unity Container 設定
public class UnityConfig
{
    private static readonly Lazy<IUnityContainer> _container = 
        new Lazy<IUnityContainer>(() =>
        {
            var container = new UnityContainer();
            RegisterTypes(container);
            return container;
        });
    
    public static IUnityContainer Container => _container.Value;
    
    private static void RegisterTypes(IUnityContainer container)
    {
        // サービス登録
        container.RegisterType<ICustomerService, CustomerService>();
        container.RegisterType<IOrderService, OrderService>();
        
        // リポジトリ登録
        container.RegisterType<ICustomerRepository, CustomerRepository>();
        container.RegisterType<IOrderRepository, OrderRepository>();
        
        // データアクセス登録
        container.RegisterType<IDbContext, BusinessDbContext>();
        
        // 設定値の注入
        var connectionString = ConfigurationManager
            .ConnectionStrings["DefaultConnection"].ConnectionString;
        container.RegisterInstance<string>("connectionString", connectionString);
        
        // Presenter登録 (Singletonパターン)
        container.RegisterType<CustomerPresenter>(new ContainerControlledLifetimeManager());
    }
}
```

### Repositoryパターン (.NET 4.0対応)
```csharp
// .NET Framework 4.0 対応 Repositoryパターン
public interface IRepository<T> where T : class
{
    List<T> GetAll();
    T GetById(int id);
    List<T> Find(Expression<Func<T, bool>> predicate);
    void Add(T entity);
    void Update(T entity);
    void Delete(T entity);
    void SaveChanges();
}

public class Repository<T> : IRepository<T> where T : class
{
    private readonly DbContext _context;
    private readonly DbSet<T> _dbSet;
    
    public Repository(DbContext context)
    {
        _context = context;
        _dbSet = context.Set<T>();
    }
    
    public List<T> GetAll()
    {
        return _dbSet.ToList();
    }
    
    public T GetById(int id)
    {
        return _dbSet.Find(id);
    }
    
    public List<T> Find(Expression<Func<T, bool>> predicate)
    {
        return _dbSet.Where(predicate).ToList();
    }
    
    public void Add(T entity)
    {
        _dbSet.Add(entity);
    }
    
    public void Update(T entity)
    {
        _context.Entry(entity).State = EntityState.Modified;
    }
    
    public void Delete(T entity)
    {
        _dbSet.Remove(entity);
    }
    
    public void SaveChanges()
    {
        _context.SaveChanges();
    }
}
```

## 🔧 詳細オプション

### UIコンポーネントパターン
```bash
/winforms-patterns ui_components [component_type]
```
**コンポーネントタイプ**:
- `data_grid` - DataGridViewのBindingSource連携パターン
- `input_form` - 入力フォームのバリデーションパターン
- `tree_view` - TreeViewの階層データ表示パターン
- `menu_toolbar` - メニュー・ツールバーのコマンドパターン

### エラーハンドリングパターン
```bash
/winforms-patterns error_handling [strategy]
```
**戦略**:
- `global` - グローバルエラーハンドラー設定
- `presenter` - Presenter層でのエラー処理
- `service` - サービス層での例外管理
- `logging` - 構造化ログ・エラートラッキング

### スレッドセーフパターン (.NET 4.0対応)
```bash
/winforms-patterns thread_safe [pattern]
```
**パターン**:
- `invoke_pattern` - Control.Invokeパターン
- `background_worker` - BackgroundWorkerパターン
- `thread_pool` - ThreadPool.QueueUserWorkItemパターン
- `lock_pattern` - lock文・ミューテックスパターン

## 📊 パフォーマンス最適化

### メモリ管理パターン
```csharp
// .NET Framework 4.0 メモリ管理パターン
public class MemoryEfficientPresenter : IDisposable
{
    private readonly List<IDisposable> _disposables = new List<IDisposable>();
    private bool _disposed = false;
    
    public void RegisterDisposable(IDisposable disposable)
    {
        _disposables.Add(disposable);
    }
    
    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                foreach (var disposable in _disposables)
                {
                    disposable?.Dispose();
                }
                _disposables.Clear();
            }
            _disposed = true;
        }
    }
    
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
}
```

## 📝 生成ファイル

- `src/Forms/` - Windows Formsクラスファイル
- `src/Presenters/` - MVP Presenter実装
- `src/Services/` - ビジネスサービス層
- `src/Infrastructure/DI/` - Unity Container設定
- `tests/Unit/` - 単体テストコード
- `docs/patterns/` - パターン詳細ドキュメント

## 🔗 関連コマンド

- `/design` - 技術設計詳細化
- `/legacy-integration` - レガシーシステム統合パターン
- `/refactor` - パターンリファクタリング
- `/standardize` - コード標準化適用
- `/analyze` - パターン適用状況分析

---

**💡 推奨**: MVPパターンは.NET Framework 4.0のWindows Forms開発で最も効果的です。BackgroundWorkerとUnity Containerを組み合わせることで、モダンなアーキテクチャ (.NET 4.5以降相当) を.NET 4.0環境で実現できます。