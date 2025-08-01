# Windows Forms UIパターン集

## 概要

このドキュメントでは、Windows Formsアプリケーションで頻繁に使用されるUIパターンと、その実装方法を**Visual Studioのデザイナー操作手順**として説明します。

## 🚨 重要：Designer.cs ファイルの取り扱い

**AIは以下のファイルを絶対に直接編集しません：**
- `*.Designer.cs` - Visual Studioが自動生成するファイル
- `*.resx` - リソースファイル

すべてのUI実装は、Visual Studioのデザイナーを通じて行う手順を提供します。

## 1. マスター詳細画面パターン

### 実装手順

```markdown
### Visual Studioでの実装手順

1. **新しいフォームの作成**
   - プロジェクト右クリック → 追加 → Windows フォーム
   - 名前: CustomerMasterDetailForm.cs

2. **SplitContainerの配置**
   - ツールボックスから SplitContainer をドラッグ
   - プロパティ設定:
     - Name: splitContainer1
     - Dock: Fill
     - Orientation: Vertical
     - SplitterDistance: 400
     - FixedPanel: None

3. **左パネル（マスター）の設定**
   - splitContainer1.Panel1 を選択
   - DataGridView をドラッグして配置
   - DataGridView のプロパティ:
     - Name: dgvCustomers
     - Dock: Fill
     - AllowUserToAddRows: False
     - AllowUserToDeleteRows: False
     - SelectionMode: FullRowSelect
     - MultiSelect: False
     - ReadOnly: True

4. **右パネル（詳細）の設定**
   - splitContainer1.Panel2 を選択
   - TableLayoutPanel をドラッグして配置
     - Name: tlpDetails
     - Dock: Fill
     - RowCount: 10
     - ColumnCount: 2
   
5. **詳細フィールドの配置**
   TableLayoutPanel 内に以下を配置:
   - Row 0, Col 0: Label (Text: "顧客ID:")
   - Row 0, Col 1: TextBox (Name: txtCustomerId, ReadOnly: True)
   - Row 1, Col 0: Label (Text: "顧客名:")
   - Row 1, Col 1: TextBox (Name: txtCustomerName)
   - Row 2, Col 0: Label (Text: "メール:")
   - Row 2, Col 1: TextBox (Name: txtEmail)
   
6. **ボタンパネルの追加**
   - 最下行に FlowLayoutPanel を配置
     - Name: flpButtons
     - FlowDirection: RightToLeft
   - ボタンを追加:
     - btnSave (Text: "保存")
     - btnCancel (Text: "キャンセル")
```

### コードビハインド実装

```csharp
// CustomerMasterDetailForm.cs
public partial class CustomerMasterDetailForm : Form
{
    private BindingSource _masterBindingSource;
    private BindingSource _detailBindingSource;
    
    public CustomerMasterDetailForm()
    {
        InitializeComponent();
        SetupDataBinding();
    }
    
    private void SetupDataBinding()
    {
        // データソースの設定
        _masterBindingSource = new BindingSource();
        _detailBindingSource = new BindingSource();
        
        // マスターグリッドのバインディング
        dgvCustomers.DataSource = _masterBindingSource;
        
        // 詳細フィールドのバインディング
        txtCustomerId.DataBindings.Add("Text", _detailBindingSource, "CustomerId");
        txtCustomerName.DataBindings.Add("Text", _detailBindingSource, "CustomerName");
        txtEmail.DataBindings.Add("Text", _detailBindingSource, "Email");
        
        // 選択変更イベント
        dgvCustomers.SelectionChanged += DgvCustomers_SelectionChanged;
    }
    
    private void DgvCustomers_SelectionChanged(object sender, EventArgs e)
    {
        if (dgvCustomers.CurrentRow != null)
        {
            var customer = dgvCustomers.CurrentRow.DataBoundItem as Customer;
            _detailBindingSource.DataSource = customer;
        }
    }
}
```

## 2. 検索機能付きリスト画面

### 実装手順

```markdown
### 検索機能付きリストの作成手順

1. **フォームレイアウト作成**
   - 新規フォーム: CustomerSearchForm.cs
   
2. **検索パネルの作成**
   - Panel をフォーム上部に配置
     - Name: pnlSearch
     - Dock: Top
     - Height: 80
   
3. **検索コントロールの配置**
   pnlSearch 内に TableLayoutPanel を配置:
   - Name: tlpSearch
   - ColumnCount: 4
   - RowCount: 2
   
   以下のコントロールを配置:
   - Label (Text: "顧客名:") + TextBox (Name: txtSearchName)
   - Label (Text: "メール:") + TextBox (Name: txtSearchEmail)
   - Label (Text: "ステータス:") + ComboBox (Name: cboSearchStatus)
   - Button (Name: btnSearch, Text: "検索")
   - Button (Name: btnClear, Text: "クリア")

4. **結果表示グリッドの配置**
   - DataGridView を配置
     - Name: dgvSearchResults
     - Dock: Fill
     - AllowUserToAddRows: False
     - ReadOnly: True

5. **ステータスバーの追加**
   - StatusStrip を配置
     - Name: statusStrip1
   - ToolStripStatusLabel を追加
     - Name: lblResultCount
     - Text: "0 件"

6. **コンテキストメニューの追加**
   - ContextMenuStrip を追加
     - Name: contextMenuStrip1
   - メニュー項目:
     - 詳細表示 (Name: tsmiShowDetail)
     - 編集 (Name: tsmiEdit)
     - 削除 (Name: tsmiDelete)
   - dgvSearchResults.ContextMenuStrip = contextMenuStrip1
```

### 非同期検索の実装

```csharp
// CustomerSearchForm.cs
public partial class CustomerSearchForm : Form
{
    private readonly ICustomerService _customerService;
    private CancellationTokenSource _searchCancellationToken;
    
    public CustomerSearchForm(ICustomerService customerService)
    {
        InitializeComponent();
        _customerService = customerService;
        InitializeSearchControls();
    }
    
    private void InitializeSearchControls()
    {
        // ステータスコンボボックスの初期化
        cboSearchStatus.Items.AddRange(new[] { "すべて", "アクティブ", "非アクティブ" });
        cboSearchStatus.SelectedIndex = 0;
        
        // Enterキーで検索
        txtSearchName.KeyDown += (s, e) => { if (e.KeyCode == Keys.Enter) PerformSearch(); };
        txtSearchEmail.KeyDown += (s, e) => { if (e.KeyCode == Keys.Enter) PerformSearch(); };
    }
    
    private async void btnSearch_Click(object sender, EventArgs e)
    {
        await PerformSearchAsync();
    }
    
    private async Task PerformSearchAsync()
    {
        // 既存の検索をキャンセル
        _searchCancellationToken?.Cancel();
        _searchCancellationToken = new CancellationTokenSource();
        
        // UI状態の更新
        SetSearchUIState(false);
        lblResultCount.Text = "検索中...";
        
        try
        {
            var criteria = new CustomerSearchCriteria
            {
                Name = txtSearchName.Text,
                Email = txtSearchEmail.Text,
                Status = GetSelectedStatus()
            };
            
            var results = await _customerService.SearchCustomersAsync(
                criteria, 
                _searchCancellationToken.Token);
            
            // 結果の表示
            dgvSearchResults.DataSource = new BindingList<CustomerDto>(results.ToList());
            lblResultCount.Text = $"{results.Count()} 件";
        }
        catch (OperationCanceledException)
        {
            lblResultCount.Text = "検索がキャンセルされました";
        }
        catch (Exception ex)
        {
            MessageBox.Show($"検索エラー: {ex.Message}", "エラー", 
                MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
        finally
        {
            SetSearchUIState(true);
        }
    }
    
    private void SetSearchUIState(bool enabled)
    {
        btnSearch.Enabled = enabled;
        btnClear.Enabled = enabled;
        pnlSearch.Enabled = enabled;
    }
}
```

## 3. ウィザード形式入力画面

### 実装手順

```markdown
### ウィザード画面の作成手順

1. **基本フォームの作成**
   - 新規フォーム: CustomerRegistrationWizard.cs
   - プロパティ:
     - FormBorderStyle: FixedDialog
     - MaximizeBox: False
     - MinimizeBox: False
     - StartPosition: CenterParent

2. **レイアウトの作成**
   - TableLayoutPanel を配置
     - Name: tlpMain
     - Dock: Fill
     - RowCount: 3
     - RowStyles:
       - Row 0: Absolute, 60px (ヘッダー)
       - Row 1: Percent, 100% (コンテンツ)
       - Row 2: Absolute, 50px (ボタン)

3. **ヘッダーパネルの作成**
   Row 0 に Panel を配置:
   - Name: pnlHeader
   - BackColor: White
   - BorderStyle: FixedSingle
   
   内部に配置:
   - Label (Name: lblStepTitle, Font: Bold, 14pt)
   - Label (Name: lblStepDescription)

4. **コンテンツエリアの作成**
   Row 1 に Panel を配置:
   - Name: pnlContent
   - AutoScroll: True

5. **ボタンエリアの作成**
   Row 2 に FlowLayoutPanel を配置:
   - Name: flpButtons
   - FlowDirection: RightToLeft
   
   ボタンを追加:
   - btnCancel (Text: "キャンセル")
   - btnNext (Text: "次へ >")
   - btnPrevious (Text: "< 戻る")

6. **各ステップ用UserControlの作成**
   以下のUserControlを作成:
   - Step1_BasicInfo.cs
   - Step2_ContactInfo.cs
   - Step3_Confirmation.cs
```

### ウィザードロジックの実装

```csharp
// CustomerRegistrationWizard.cs
public partial class CustomerRegistrationWizard : Form
{
    private int _currentStep = 0;
    private readonly List<IWizardStep> _steps;
    private readonly CustomerRegistrationData _registrationData;
    
    public CustomerRegistrationWizard()
    {
        InitializeComponent();
        
        _registrationData = new CustomerRegistrationData();
        _steps = new List<IWizardStep>
        {
            new Step1_BasicInfo(),
            new Step2_ContactInfo(),
            new Step3_Confirmation()
        };
        
        ShowCurrentStep();
    }
    
    private void ShowCurrentStep()
    {
        // 現在のステップを表示
        pnlContent.Controls.Clear();
        var currentStep = _steps[_currentStep];
        
        // UserControlの設定
        var control = currentStep as UserControl;
        control.Dock = DockStyle.Fill;
        pnlContent.Controls.Add(control);
        
        // ヘッダー更新
        lblStepTitle.Text = currentStep.Title;
        lblStepDescription.Text = currentStep.Description;
        
        // データのロード
        currentStep.LoadData(_registrationData);
        
        // ボタン状態の更新
        UpdateButtonStates();
    }
    
    private void UpdateButtonStates()
    {
        btnPrevious.Enabled = _currentStep > 0;
        btnNext.Text = _currentStep < _steps.Count - 1 ? "次へ >" : "完了";
    }
    
    private async void btnNext_Click(object sender, EventArgs e)
    {
        var currentStep = _steps[_currentStep];
        
        // 検証
        if (!currentStep.Validate())
        {
            MessageBox.Show(currentStep.ValidationMessage, "入力エラー", 
                MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }
        
        // データ保存
        currentStep.SaveData(_registrationData);
        
        if (_currentStep < _steps.Count - 1)
        {
            _currentStep++;
            ShowCurrentStep();
        }
        else
        {
            // 完了処理
            await CompleteRegistrationAsync();
        }
    }
    
    private void btnPrevious_Click(object sender, EventArgs e)
    {
        if (_currentStep > 0)
        {
            _currentStep--;
            ShowCurrentStep();
        }
    }
}

// IWizardStep インターフェース
public interface IWizardStep
{
    string Title { get; }
    string Description { get; }
    void LoadData(CustomerRegistrationData data);
    void SaveData(CustomerRegistrationData data);
    bool Validate();
    string ValidationMessage { get; }
}
```

## 4. ダッシュボード画面

### 実装手順

```markdown
### ダッシュボード画面の作成手順

1. **メインレイアウトの作成**
   - 新規フォーム: DashboardForm.cs
   - TableLayoutPanel を配置
     - Name: tlpDashboard
     - Dock: Fill
     - ColumnCount: 3
     - RowCount: 3
     - 列幅: 33.33% ずつ
     - 行高: 33.33% ずつ

2. **サマリーカードの作成**
   各セルに GroupBox を配置してカードを作成:
   
   Cell[0,0]: 売上サマリー
   - GroupBox (Text: "本日の売上")
   - 内部に TableLayoutPanel
   - Label (Name: lblTodaySales, Font: 24pt)
   - Label (Name: lblSalesChange, ForeColor: Green)
   
   Cell[1,0]: 顧客数
   - GroupBox (Text: "アクティブ顧客")
   - Label (Name: lblActiveCustomers, Font: 24pt)
   
   Cell[2,0]: 注文数
   - GroupBox (Text: "本日の注文")
   - Label (Name: lblTodayOrders, Font: 24pt)

3. **チャートエリアの作成**
   Cell[0,1] から [2,1] を結合:
   - Chart コントロールを配置 (要: System.Windows.Forms.DataVisualization)
   - Name: chartSales
   - ChartAreas[0].Name: "MainArea"
   - Series を追加:
     - Name: "売上推移"
     - ChartType: Line

4. **最近の活動リストの作成**
   Cell[0,2] から [1,2] を結合:
   - GroupBox (Text: "最近の活動")
   - ListBox を配置
     - Name: lstRecentActivities
     - Dock: Fill

5. **クイックアクションボタンの作成**
   Cell[2,2]:
   - FlowLayoutPanel を配置
   - 大きめのボタンを追加:
     - btnNewOrder (Text: "新規注文")
     - btnNewCustomer (Text: "新規顧客")
     - btnReports (Text: "レポート")

6. **自動更新タイマーの追加**
   - Timer コンポーネントを追加
     - Name: timerRefresh
     - Interval: 30000 (30秒)
     - Enabled: True
```

### ダッシュボードのデータ更新

```csharp
// DashboardForm.cs
public partial class DashboardForm : Form
{
    private readonly IDashboardService _dashboardService;
    private CancellationTokenSource _refreshCancellation;
    
    public DashboardForm(IDashboardService dashboardService)
    {
        InitializeComponent();
        _dashboardService = dashboardService;
        
        // 初回データロード
        _ = LoadDashboardDataAsync();
    }
    
    private async Task LoadDashboardDataAsync()
    {
        try
        {
            // 既存のリフレッシュをキャンセル
            _refreshCancellation?.Cancel();
            _refreshCancellation = new CancellationTokenSource();
            
            var data = await _dashboardService.GetDashboardDataAsync(
                _refreshCancellation.Token);
            
            // UIスレッドで更新
            if (!_refreshCancellation.Token.IsCancellationRequested)
            {
                UpdateDashboardUI(data);
            }
        }
        catch (Exception ex)
        {
            ShowErrorNotification($"データ更新エラー: {ex.Message}");
        }
    }
    
    private void UpdateDashboardUI(DashboardData data)
    {
        // サマリーカードの更新
        lblTodaySales.Text = data.TodaySales.ToString("C");
        lblSalesChange.Text = $"{data.SalesChangePercent:+0.0;-0.0;0}%";
        lblSalesChange.ForeColor = data.SalesChangePercent >= 0 ? 
            Color.Green : Color.Red;
        
        lblActiveCustomers.Text = data.ActiveCustomerCount.ToString("N0");
        lblTodayOrders.Text = data.TodayOrderCount.ToString("N0");
        
        // チャートの更新
        UpdateSalesChart(data.SalesHistory);
        
        // 最近の活動
        UpdateRecentActivities(data.RecentActivities);
    }
    
    private void UpdateSalesChart(IEnumerable<SalesDataPoint> salesData)
    {
        chartSales.Series["売上推移"].Points.Clear();
        
        foreach (var point in salesData)
        {
            chartSales.Series["売上推移"].Points.AddXY(
                point.Date.ToShortDateString(), 
                point.Amount);
        }
        
        // チャートの見た目を調整
        chartSales.ChartAreas[0].AxisX.LabelStyle.Angle = -45;
        chartSales.ChartAreas[0].AxisY.LabelStyle.Format = "C0";
    }
    
    private void timerRefresh_Tick(object sender, EventArgs e)
    {
        _ = LoadDashboardDataAsync();
    }
}
```

## 5. 印刷プレビュー画面

### 実装手順

```markdown
### 印刷プレビュー画面の作成手順

1. **PrintDocument の追加**
   - ツールボックスから PrintDocument をフォームに追加
     - Name: printDocument1
   
2. **PrintPreviewDialog の追加**
   - PrintPreviewDialog を追加
     - Name: printPreviewDialog1
     - Document: printDocument1

3. **印刷設定ダイアログの追加**
   - PrintDialog を追加
     - Name: printDialog1
     - Document: printDocument1

4. **ページ設定ダイアログの追加**
   - PageSetupDialog を追加
     - Name: pageSetupDialog1
     - Document: printDocument1

5. **印刷メニューの作成**
   メインフォームのメニューに追加:
   - ファイル(&F)
     - ページ設定(&U)
     - 印刷プレビュー(&V)
     - 印刷(&P)

6. **カスタムプレビューフォームの作成（オプション）**
   より高度な制御が必要な場合:
   - 新規フォーム: CustomPrintPreview.cs
   - PrintPreviewControl を配置
     - Name: printPreviewControl1
     - Dock: Fill
   - ツールバーを追加してズーム、ページ切り替えボタンを配置
```

### 印刷処理の実装

```csharp
// 印刷可能なフォームの実装
public partial class CustomerReportForm : Form
{
    private List<Customer> _customersToPrint;
    private int _currentPrintPage = 0;
    private readonly int _recordsPerPage = 30;
    
    public CustomerReportForm()
    {
        InitializeComponent();
        SetupPrinting();
    }
    
    private void SetupPrinting()
    {
        printDocument1.PrintPage += PrintDocument1_PrintPage;
        printDocument1.BeginPrint += PrintDocument1_BeginPrint;
    }
    
    private void PrintDocument1_BeginPrint(object sender, PrintEventArgs e)
    {
        _currentPrintPage = 0;
    }
    
    private void PrintDocument1_PrintPage(object sender, PrintPageEventArgs e)
    {
        var g = e.Graphics;
        var font = new Font("MS UI Gothic", 10);
        var titleFont = new Font("MS UI Gothic", 16, FontStyle.Bold);
        var headerFont = new Font("MS UI Gothic", 10, FontStyle.Bold);
        
        float yPos = e.MarginBounds.Top;
        float xPos = e.MarginBounds.Left;
        
        // タイトル
        g.DrawString("顧客一覧レポート", titleFont, Brushes.Black, xPos, yPos);
        yPos += titleFont.GetHeight(g) + 10;
        
        // 印刷日時
        g.DrawString($"印刷日時: {DateTime.Now:yyyy/MM/dd HH:mm}", 
            font, Brushes.Black, xPos, yPos);
        yPos += font.GetHeight(g) + 20;
        
        // ヘッダー行
        DrawTableHeader(g, headerFont, xPos, ref yPos);
        
        // データ行
        int startIndex = _currentPrintPage * _recordsPerPage;
        int endIndex = Math.Min(startIndex + _recordsPerPage, _customersToPrint.Count);
        
        for (int i = startIndex; i < endIndex; i++)
        {
            DrawCustomerRow(g, font, _customersToPrint[i], xPos, ref yPos);
        }
        
        // ページ番号
        string pageNumber = $"ページ {_currentPrintPage + 1}";
        g.DrawString(pageNumber, font, Brushes.Black, 
            e.MarginBounds.Right - g.MeasureString(pageNumber, font).Width,
            e.MarginBounds.Bottom);
        
        // 次ページの判定
        _currentPrintPage++;
        e.HasMorePages = endIndex < _customersToPrint.Count;
    }
    
    private void DrawTableHeader(Graphics g, Font font, float xPos, ref float yPos)
    {
        var columns = new[] { "顧客ID", "顧客名", "電話番号", "メール" };
        var widths = new[] { 80f, 200f, 120f, 200f };
        
        float currentX = xPos;
        for (int i = 0; i < columns.Length; i++)
        {
            g.DrawString(columns[i], font, Brushes.Black, currentX, yPos);
            currentX += widths[i];
        }
        
        yPos += font.GetHeight(g);
        g.DrawLine(Pens.Black, xPos, yPos, xPos + 600, yPos);
        yPos += 5;
    }
    
    private void btnPrintPreview_Click(object sender, EventArgs e)
    {
        _customersToPrint = GetCustomersToPrint();
        printPreviewDialog1.ShowDialog();
    }
    
    private void btnPrint_Click(object sender, EventArgs e)
    {
        _customersToPrint = GetCustomersToPrint();
        if (printDialog1.ShowDialog() == DialogResult.OK)
        {
            printDocument1.Print();
        }
    }
}
```

## まとめ

これらのUIパターンは、Windows Formsアプリケーションで一般的に使用されるものです。重要なポイント：

1. **すべてのUI構築はVisual Studioのデザイナーを使用**
2. **Designer.csファイルは直接編集しない**
3. **データバインディングを活用して保守性を向上**
4. **非同期処理でUIの応答性を維持**
5. **適切なエラーハンドリングとユーザーフィードバック**

各パターンは組み合わせて使用することも可能で、アプリケーションの要件に応じて適切に選択・カスタマイズしてください。