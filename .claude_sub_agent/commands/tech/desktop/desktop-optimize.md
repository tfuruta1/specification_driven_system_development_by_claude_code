# /desktop-optimize - デスクトップアプリケーション最適化コマンド

## 概要
Windows Forms、WPF、.NET Frameworkデスクトップアプリケーションを最適化する統合コマンドです。レガシー環境から最新環境まで幅広く対応します。

## 使用方法
```bash
/desktop-optimize [framework] [target] [options]

# 使用例
/desktop-optimize winforms performance --net48
/desktop-optimize winforms ui-patterns --mvp
/desktop-optimize wpf memory --net6
/desktop-optimize legacy compatibility --net40
```

## パラメータ

### 必須パラメータ
- `framework`: フレームワーク（winforms, wpf, legacy）
- `target`: 最適化対象
  - `performance` - パフォーマンス最適化
  - `ui-patterns` - UIパターン適用
  - `memory` - メモリ最適化
  - `compatibility` - 互換性確保
  - `unity-container` - DI/IoC設定

### オプション
- `--net48`: .NET Framework 4.8対応
- `--net40`: .NET Framework 4.0対応
- `--mvp`: MVPパターン適用
- `--mvvm`: MVVMパターン適用
- `--async`: 非同期処理最適化
- `--legacy-support`: レガシーOS対応

## Windows Forms最適化

### 1. UIパターン実装
```csharp
// MVP (Model-View-Presenter) パターン
public interface IMainView
{
    event EventHandler LoadData;
    event EventHandler SaveData;
    
    string StatusText { get; set; }
    void ShowMessage(string message);
    void UpdateGrid(DataTable data);
}

public class MainPresenter
{
    private readonly IMainView _view;
    private readonly IDataService _service;
    
    public MainPresenter(IMainView view, IDataService service)
    {
        _view = view;
        _service = service;
        
        _view.LoadData += OnLoadData;
        _view.SaveData += OnSaveData;
    }
    
    private async void OnLoadData(object sender, EventArgs e)
    {
        _view.StatusText = "データ読み込み中...";
        var data = await _service.GetDataAsync();
        _view.UpdateGrid(data);
        _view.StatusText = "完了";
    }
}
```

### 2. パフォーマンス最適化
```csharp
// ダブルバッファリング有効化
public partial class OptimizedForm : Form
{
    public OptimizedForm()
    {
        InitializeComponent();
        
        // ちらつき防止
        SetStyle(ControlStyles.AllPaintingInWmPaint |
                ControlStyles.UserPaint |
                ControlStyles.DoubleBuffer, true);
        
        // 仮想モード有効化（大量データ対応）
        dataGridView1.VirtualMode = true;
        dataGridView1.CellValueNeeded += OnCellValueNeeded;
    }
    
    // BackgroundWorker による非同期処理
    private void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
    {
        // 重い処理をバックグラウンドで実行
        var result = ProcessLargeData();
        e.Result = result;
    }
}
```

### 3. Unity Container (DI/IoC) 設定
```csharp
// Unity Container 設定
public class ContainerConfig
{
    public static IUnityContainer Configure()
    {
        var container = new UnityContainer();
        
        // サービス登録
        container.RegisterType<IDataService, SqlDataService>(
            new ContainerControlledLifetimeManager());
        
        container.RegisterType<ILogger, FileLogger>(
            new PerResolveLifetimeManager());
        
        // ファクトリー登録
        container.RegisterFactory<IDbConnection>(
            c => new SqlConnection(ConfigurationManager
                .ConnectionStrings["Default"].ConnectionString));
        
        // インターセプター設定（AOP）
        container.AddNewExtension<Interception>();
        container.RegisterType<IBusinessService, BusinessService>(
            new InterceptionBehavior<PolicyInjectionBehavior>(),
            new Interceptor<InterfaceInterceptor>());
        
        return container;
    }
}
```

## .NET Framework バージョン別最適化

### .NET Framework 4.8
```csharp
// 最新の非同期パターン
public async Task<DataResult> GetDataAsync()
{
    using (var client = new HttpClient())
    {
        var response = await client.GetAsync(apiUrl);
        response.EnsureSuccessStatusCode();
        
        var json = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<DataResult>(json);
    }
}
```

### .NET Framework 4.0（レガシー環境）
```csharp
// .NET 4.0 互換の非同期処理
public void GetDataAsync(Action<DataResult> callback)
{
    var client = new WebClient();
    
    client.DownloadStringCompleted += (s, e) =>
    {
        if (e.Error == null)
        {
            var result = JsonConvert.DeserializeObject<DataResult>(e.Result);
            callback(result);
        }
    };
    
    client.DownloadStringAsync(new Uri(apiUrl));
}
```

## メモリ最適化

### メモリリーク防止
```csharp
public class OptimizedControl : UserControl
{
    private Timer _timer;
    private EventHandler _handler;
    
    protected override void OnLoad(EventArgs e)
    {
        base.OnLoad(e);
        
        // イベントハンドラーの適切な管理
        _handler = new EventHandler(OnTimerTick);
        _timer = new Timer();
        _timer.Tick += _handler;
    }
    
    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            // イベントハンドラーの解除
            if (_timer != null)
            {
                _timer.Tick -= _handler;
                _timer.Dispose();
            }
            
            // 大きなオブジェクトの明示的解放
            LargeDataCache?.Clear();
        }
        
        base.Dispose(disposing);
    }
}
```

## レガシーシステム統合

### COM相互運用
```csharp
// レガシーCOMコンポーネントの統合
[ComImport]
[Guid("12345678-1234-1234-1234-123456789012")]
[InterfaceType(ComInterfaceType.InterfaceIsIDispatch)]
public interface ILegacyComponent
{
    string ProcessData(string input);
}

public class LegacyIntegration
{
    public void UseLegacyComponent()
    {
        Type legacyType = Type.GetTypeFromProgID("Legacy.Component");
        dynamic legacy = Activator.CreateInstance(legacyType);
        
        try
        {
            string result = legacy.ProcessData("input");
        }
        finally
        {
            Marshal.ReleaseComObject(legacy);
        }
    }
}
```

## 出力例

### 最適化レポート
```markdown
# デスクトップアプリケーション最適化レポート

## 実施項目
✅ UIレスポンス: 500ms → 150ms (70%改善)
✅ メモリ使用量: 450MB → 280MB (38%削減)
✅ 起動時間: 8秒 → 3秒 (62%改善)
✅ CPU使用率: 35% → 15% (57%削減)

## パターン適用
- MVPパターン: 15画面に適用
- Unity Container: DI/IoC完全移行
- 非同期処理: 全データアクセス層

## 互換性確認
- Windows 11: ✅ 完全対応
- Windows 10: ✅ 完全対応
- Windows 7: ✅ 互換モードで動作
- Windows XP: ⚠️ .NET 4.0版で対応

## 推奨事項
1. .NET 6への移行検討
2. WPFへの段階的移行
3. ClickOnce配布の導入
```

## トラブルシューティング

| 問題 | 原因 | 解決策 |
|------|------|--------|
| 起動しない | .NET Framework未インストール | ランタイムインストール |
| 文字化け | エンコーディング問題 | UTF-8に統一 |
| DLLエラー | 依存関係の問題 | NuGetパッケージ復元 |
| 遅い描画 | ダブルバッファリング無効 | SetStyle設定追加 |

## 管理責任
- **管理部門**: システム開発部
- **カスタマイズ**: プロジェクトのデスクトップ技術に応じて最適化

## 関連コマンド
- `/winforms-design` - Windows Forms設計専門
- `/winforms-patterns` - デザインパターン適用
- `/unity-container` - DI/IoC専門設定
- `/legacy-integration` - レガシーシステム統合

---
*このコマンドはシステム開発部が管理します。*