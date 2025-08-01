# WinForms Patterns Command - Windows Forms ベストプラクティス

## 概要

Windows Forms開発におけるベストプラクティスとデザインパターンを適用するためのコマンドです。AIは Designer.cs や .resx ファイルを直接編集せず、ユーザーへの実装指示を提供します。

## 使用方法

```
/winforms-patterns [パターン名]
```

### 利用可能なパターン
- `mvp` - Model-View-Presenter パターン
- `data-binding` - 高度なデータバインディング
- `async-ui` - 非同期UIパターン
- `validation` - 入力検証パターン
- `custom-controls` - カスタムコントロール作成
- `accessibility` - アクセシビリティ対応

## 🚨 重要：Designer.cs および .resx ファイルの取り扱い

**絶対的なルール：**
- `.Designer.cs` ファイルは**絶対に直接編集しない**
- `.resx` ファイルは**絶対に直接編集しない**
- すべてのUI実装は**Visual Studioのデザイナー**を通じて行う
- プログラム的な設定は**コードビハインド**（.cs）で行う

## MVP (Model-View-Presenter) パターン

### 実装手順

```markdown
## MVP パターンの実装手順

1. **インターフェースの定義**
   - 新しいインターフェースファイルを作成
   - ICustomerView.cs として保存

2. **フォームの作成**
   - 新しいWindows フォームを追加
   - CustomerForm.cs として保存

3. **フォームデザイン**
   Visual Studioのデザイナーで以下を配置：
   - DataGridView (Name: dgvCustomers)
   - Button (Name: btnRefresh, Text: "更新")
   - Button (Name: btnAdd, Text: "追加")
   - TextBox (Name: txtSearch)
   - StatusStrip with StatusLabel (Name: lblStatus)

4. **プロパティ設定**
   デザイナーのプロパティウィンドウで設定：
   - dgvCustomers:
     - Dock: Fill
     - AllowUserToAddRows: False
     - SelectionMode: FullRowSelect
```

### コード実装例

```csharp
// ICustomerView.cs - ビューインターフェース
public interface ICustomerView
{
    // イベント
    event EventHandler RefreshClicked;
    event EventHandler AddClicked;
    event EventHandler<CustomerEventArgs> CustomerSelected;
    
    // プロパティ
    string SearchText { get; set; }
    string StatusText { get; set; }
    
    // メソッド
    void ShowCustomers(IEnumerable<Customer> customers);
    void ShowError(string message);
    void ShowLoading(bool isLoading);
}

// CustomerForm.cs - フォーム実装（Designer.csではない）
public partial class CustomerForm : Form, ICustomerView
{
    // イベントの実装
    public event EventHandler RefreshClicked;
    public event EventHandler AddClicked;
    public event EventHandler<CustomerEventArgs> CustomerSelected;
    
    public CustomerForm()
    {
        InitializeComponent();
        WireUpEvents();
    }
    
    private void WireUpEvents()
    {
        // Designer で生成されたコントロールのイベントを接続
        btnRefresh.Click += (s, e) => RefreshClicked?.Invoke(this, e);
        btnAdd.Click += (s, e) => AddClicked?.Invoke(this, e);
        dgvCustomers.SelectionChanged += OnCustomerSelectionChanged;
    }
    
    // ICustomerView の実装
    public string SearchText
    {
        get => txtSearch.Text;
        set => txtSearch.Text = value;
    }
    
    public string StatusText
    {
        get => lblStatus.Text;
        set => lblStatus.Text = value;
    }
    
    public void ShowCustomers(IEnumerable<Customer> customers)
    {
        dgvCustomers.DataSource = new BindingList<Customer>(customers.ToList());
    }
}

// CustomerPresenter.cs - プレゼンター
public class CustomerPresenter
{
    private readonly ICustomerView _view;
    private readonly ICustomerRepository _repository;
    
    public CustomerPresenter(ICustomerView view, ICustomerRepository repository)
    {
        _view = view;
        _repository = repository;
        
        // ビューイベントの購読
        _view.RefreshClicked += OnRefreshClicked;
        _view.AddClicked += OnAddClicked;
    }
    
    private async void OnRefreshClicked(object sender, EventArgs e)
    {
        _view.ShowLoading(true);
        _view.StatusText = "データを読み込んでいます...";
        
        try
        {
            var customers = await _repository.GetAllAsync();
            _view.ShowCustomers(customers);
            _view.StatusText = $"{customers.Count}件のデータを読み込みました";
        }
        catch (Exception ex)
        {
            _view.ShowError($"エラーが発生しました: {ex.Message}");
        }
        finally
        {
            _view.ShowLoading(false);
        }
    }
}
```

## 高度なデータバインディング

### マスター詳細バインディングの実装手順

```markdown
## マスター詳細バインディング設定手順

1. **フォームレイアウト作成**
   Visual Studioデザイナーで：
   - SplitContainer を配置 (Name: splitContainer1)
   - Panel1 に DataGridView を配置 (Name: dgvOrders)
   - Panel2 に以下を配置：
     - Label と TextBox (lblOrderId, txtOrderId)
     - Label と DateTimePicker (lblOrderDate, dtpOrderDate)
     - DataGridView (Name: dgvOrderDetails)

2. **BindingSource の追加**
   ツールボックスのコンポーネントから：
   - BindingSource を2つ追加
   - Name: ordersBindingSource
   - Name: orderDetailsBindingSource

3. **データソースの設定**
   - プロジェクト → データソースの追加
   - オブジェクトを選択
   - Order と OrderDetail クラスを選択
```

### バインディング実装例

```csharp
// OrderManagementForm.cs での実装
public partial class OrderManagementForm : Form
{
    public OrderManagementForm()
    {
        InitializeComponent();
        SetupDataBindings();
    }
    
    private void SetupDataBindings()
    {
        // マスターのバインディング設定
        ordersBindingSource.DataSource = typeof(Order);
        dgvOrders.DataSource = ordersBindingSource;
        
        // 詳細のバインディング設定（リレーション）
        orderDetailsBindingSource.DataSource = ordersBindingSource;
        orderDetailsBindingSource.DataMember = "OrderDetails";
        dgvOrderDetails.DataSource = orderDetailsBindingSource;
        
        // 個別フィールドのバインディング
        txtOrderId.DataBindings.Add("Text", ordersBindingSource, "OrderId");
        dtpOrderDate.DataBindings.Add("Value", ordersBindingSource, "OrderDate");
        
        // フォーマット付きバインディング
        var totalBinding = new Binding("Text", ordersBindingSource, "TotalAmount", true);
        totalBinding.FormatString = "C"; // 通貨フォーマット
        txtTotalAmount.DataBindings.Add(totalBinding);
    }
    
    private void OrderManagementForm_Load(object sender, EventArgs e)
    {
        // データの読み込み
        LoadOrders();
    }
    
    private async void LoadOrders()
    {
        var orders = await _orderService.GetOrdersWithDetailsAsync();
        ordersBindingSource.DataSource = orders;
    }
}
```

## 非同期UIパターン

### プログレス表示付き非同期処理の実装手順

```markdown
## 非同期処理UIの実装手順

1. **プログレスフォームの作成**
   - 新しいフォーム: ProgressForm.cs
   - 以下のコントロールを配置：
     - ProgressBar (Name: progressBar1)
     - Label (Name: lblMessage)
     - Button (Name: btnCancel, Text: "キャンセル")

2. **プロパティ設定**
   - FormBorderStyle: FixedDialog
   - StartPosition: CenterParent
   - ControlBox: False
   - progressBar1.Style: Continuous
```

### 非同期処理実装例

```csharp
// ProgressService.cs - 進捗表示サービス
public class ProgressService
{
    public async Task<T> ExecuteWithProgressAsync<T>(
        Form owner,
        string title,
        Func<IProgress<int>, CancellationToken, Task<T>> operation)
    {
        using (var progressForm = new ProgressForm())
        {
            progressForm.Text = title;
            var cts = new CancellationTokenSource();
            
            // プログレス更新の設定
            var progress = new Progress<int>(percent =>
            {
                if (progressForm.InvokeRequired)
                {
                    progressForm.Invoke(new Action(() =>
                    {
                        progressForm.UpdateProgress(percent);
                    }));
                }
                else
                {
                    progressForm.UpdateProgress(percent);
                }
            });
            
            // 非同期でフォーム表示とタスク実行
            var formTask = Task.Run(() => progressForm.ShowDialog(owner));
            var operationTask = operation(progress, cts.Token);
            
            var result = await operationTask;
            
            progressForm.Invoke(new Action(() => progressForm.Close()));
            
            return result;
        }
    }
}

// 使用例
private async void btnImport_Click(object sender, EventArgs e)
{
    var progressService = new ProgressService();
    
    try
    {
        var result = await progressService.ExecuteWithProgressAsync(
            this,
            "データインポート中...",
            async (progress, cancellationToken) =>
            {
                return await ImportDataAsync(progress, cancellationToken);
            });
        
        MessageBox.Show($"インポート完了: {result.RecordCount}件");
    }
    catch (OperationCanceledException)
    {
        MessageBox.Show("処理がキャンセルされました。");
    }
}
```

## 入力検証パターン

### ErrorProvider を使用した検証の実装手順

```markdown
## 入力検証の実装手順

1. **ErrorProvider の追加**
   - ツールボックスから ErrorProvider をフォームに追加
   - Name: errorProvider1

2. **検証対象コントロールの設定**
   各TextBoxのプロパティ：
   - CausesValidation: True
   
3. **検証イベントの設定**
   - 各TextBoxを選択
   - プロパティウィンドウのイベントタブ
   - Validating イベントをダブルクリックしてハンドラ生成
```

### 検証実装例

```csharp
// CustomerEditForm.cs での検証実装
public partial class CustomerEditForm : Form
{
    private readonly IValidator<Customer> _validator;
    
    public CustomerEditForm()
    {
        InitializeComponent();
        _validator = new CustomerValidator();
    }
    
    // 名前フィールドの検証
    private void txtName_Validating(object sender, CancelEventArgs e)
    {
        var textBox = sender as TextBox;
        
        if (string.IsNullOrWhiteSpace(textBox.Text))
        {
            e.Cancel = true;
            errorProvider1.SetError(textBox, "名前は必須項目です。");
        }
        else if (textBox.Text.Length > 50)
        {
            e.Cancel = true;
            errorProvider1.SetError(textBox, "名前は50文字以内で入力してください。");
        }
        else
        {
            errorProvider1.SetError(textBox, string.Empty);
        }
    }
    
    // メールアドレスの検証
    private void txtEmail_Validating(object sender, CancelEventArgs e)
    {
        var textBox = sender as TextBox;
        var emailRegex = new Regex(@"^[^@\s]+@[^@\s]+\.[^@\s]+$");
        
        if (!string.IsNullOrEmpty(textBox.Text) && !emailRegex.IsMatch(textBox.Text))
        {
            e.Cancel = true;
            errorProvider1.SetError(textBox, "有効なメールアドレスを入力してください。");
        }
        else
        {
            errorProvider1.SetError(textBox, string.Empty);
        }
    }
    
    // フォーム全体の検証
    private bool ValidateForm()
    {
        foreach (Control control in this.Controls)
        {
            control.Focus();
            if (!Validate())
            {
                return false;
            }
        }
        return true;
    }
    
    private void btnSave_Click(object sender, EventArgs e)
    {
        if (ValidateForm())
        {
            // 保存処理
            SaveCustomer();
        }
    }
}
```

## カスタムコントロール作成

### 検索機能付きComboBoxの作成手順

```markdown
## カスタムコントロール作成手順

1. **ユーザーコントロールの作成**
   - 新しい項目 → ユーザーコントロール
   - Name: SearchableComboBox.cs

2. **コントロールの配置**
   Visual Studioデザイナーで：
   - ComboBox を配置 (Name: comboBox1)
   - TextBox を配置 (Name: txtSearch)
   - 配置を調整（TextBoxを上、ComboBoxを下）

3. **プロパティ設定**
   - comboBox1.DropDownStyle: DropDownList
   - txtSearch.Visible: False (初期状態)

4. **公開プロパティの作成**
   コードビューで実装
```

### カスタムコントロール実装例

```csharp
// SearchableComboBox.cs - カスタムコントロール
public partial class SearchableComboBox : UserControl
{
    private List<object> _allItems = new List<object>();
    
    public SearchableComboBox()
    {
        InitializeComponent();
        SetupControl();
    }
    
    // 公開プロパティ
    [Browsable(true)]
    [Category("データ")]
    [Description("コンボボックスのデータソース")]
    public object DataSource
    {
        get => comboBox1.DataSource;
        set
        {
            if (value is IEnumerable enumerable)
            {
                _allItems = enumerable.Cast<object>().ToList();
                comboBox1.DataSource = _allItems;
            }
        }
    }
    
    [Browsable(true)]
    public string DisplayMember
    {
        get => comboBox1.DisplayMember;
        set => comboBox1.DisplayMember = value;
    }
    
    [Browsable(true)]
    public string ValueMember
    {
        get => comboBox1.ValueMember;
        set => comboBox1.ValueMember = value;
    }
    
    public object SelectedValue
    {
        get => comboBox1.SelectedValue;
        set => comboBox1.SelectedValue = value;
    }
    
    // 検索機能の実装
    private void SetupControl()
    {
        // F3キーで検索ボックス表示
        this.KeyDown += (s, e) =>
        {
            if (e.KeyCode == Keys.F3)
            {
                txtSearch.Visible = !txtSearch.Visible;
                if (txtSearch.Visible)
                {
                    txtSearch.Focus();
                }
            }
        };
        
        // インクリメンタルサーチ
        txtSearch.TextChanged += (s, e) =>
        {
            FilterItems(txtSearch.Text);
        };
    }
    
    private void FilterItems(string searchText)
    {
        if (string.IsNullOrEmpty(searchText))
        {
            comboBox1.DataSource = _allItems;
            return;
        }
        
        var filtered = _allItems.Where(item =>
        {
            var displayText = GetDisplayText(item);
            return displayText.IndexOf(searchText, StringComparison.OrdinalIgnoreCase) >= 0;
        }).ToList();
        
        comboBox1.DataSource = filtered;
    }
}
```

## アクセシビリティ対応

### アクセシブルなフォーム作成手順

```markdown
## アクセシビリティ対応手順

1. **タブオーダーの設定**
   - 表示メニュー → タブオーダー
   - 論理的な順序でクリック

2. **アクセスキーの設定**
   各コントロールのTextプロパティ：
   - ボタン: "保存(&S)"
   - ラベル: "名前(&N):"

3. **ツールチップの設定**
   - ToolTip コンポーネントを追加
   - 各コントロールに説明を設定

4. **色とコントラストの確認**
   - 高コントラストモードでの表示確認
   - カスタム色は SystemColors を使用
```

### アクセシビリティ実装例

```csharp
// AccessibleForm.cs - アクセシブルなフォーム
public partial class AccessibleForm : Form
{
    private ToolTip toolTip1;
    
    public AccessibleForm()
    {
        InitializeComponent();
        SetupAccessibility();
    }
    
    private void SetupAccessibility()
    {
        // ツールチップの設定
        toolTip1 = new ToolTip();
        toolTip1.SetToolTip(btnSave, "変更を保存します (Ctrl+S)");
        toolTip1.SetToolTip(btnCancel, "変更を破棄して閉じます (Esc)");
        
        // アクセシビリティ情報の設定
        btnSave.AccessibleName = "保存ボタン";
        btnSave.AccessibleDescription = "フォームの内容を保存します";
        
        // ショートカットキーの設定
        this.KeyPreview = true;
        this.KeyDown += (s, e) =>
        {
            if (e.Control && e.KeyCode == Keys.S)
            {
                btnSave.PerformClick();
            }
        };
        
        // 高コントラストモード対応
        if (SystemInformation.HighContrast)
        {
            ApplyHighContrastTheme();
        }
    }
    
    private void ApplyHighContrastTheme()
    {
        // システムカラーを使用
        this.BackColor = SystemColors.Window;
        this.ForeColor = SystemColors.WindowText;
        
        foreach (Control control in this.Controls)
        {
            if (control is Button)
            {
                control.BackColor = SystemColors.ButtonFace;
                control.ForeColor = SystemColors.ControlText;
            }
        }
    }
}
```

## ベストプラクティスまとめ

### 1. Designer.cs の取り扱い
- **絶対に直接編集しない**
- Visual Studioのデザイナーを使用
- プログラム的な変更はコードビハインドで

### 2. パフォーマンス最適化
- 大量データは仮想モードを使用
- 非同期処理でUIの応答性を維持
- リソースの適切な解放（using文）

### 3. 保守性の向上
- MVPパターンでロジックを分離
- カスタムコントロールで再利用性向上
- 適切な名前付けとコメント

### 4. ユーザビリティ
- 一貫性のあるUI設計
- 適切なエラーメッセージ
- キーボード操作のサポート

## まとめ

このコマンドは、Windows Forms開発のベストプラクティスを提供します。AIは Designer.cs を直接編集せず、Visual Studioのデザイナーを通じた実装方法をユーザーに指示します。これにより、安全で保守性の高いWindows Formsアプリケーション開発を支援します。