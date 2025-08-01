# Windows Forms デスクトップアプリケーション機能実装ガイド

## 1. MDI（Multiple Document Interface）実装

### MDI親フォームの設定
```csharp
public partial class MainMdiForm : Form
{
    private int _childFormNumber = 0;
    
    public MainMdiForm()
    {
        InitializeComponent();
        
        // MDI親フォームとして設定
        this.IsMdiContainer = true;
        this.WindowState = FormWindowState.Maximized;
        
        // MDIレイアウトのカスタマイズ
        this.BackColor = SystemColors.AppWorkspace;
        
        // ウィンドウメニューの設定
        this.menuStrip1.MdiWindowListItem = this.windowsToolStripMenuItem;
    }
    
    private void NewDocumentToolStripMenuItem_Click(object sender, EventArgs e)
    {
        var childForm = new DocumentForm();
        childForm.Text = $"ドキュメント {++_childFormNumber}";
        childForm.MdiParent = this;
        childForm.Show();
    }
    
    private void CascadeToolStripMenuItem_Click(object sender, EventArgs e)
    {
        LayoutMdi(MdiLayout.Cascade);
    }
    
    private void TileVerticalToolStripMenuItem_Click(object sender, EventArgs e)
    {
        LayoutMdi(MdiLayout.TileVertical);
    }
    
    private void TileHorizontalToolStripMenuItem_Click(object sender, EventArgs e)
    {
        LayoutMdi(MdiLayout.TileHorizontal);
    }
    
    // アクティブな子フォームの取得
    private DocumentForm ActiveMdiChild => this.ActiveMdiChild as DocumentForm;
}
```

### MDI子フォームの管理
```csharp
public class MdiManager
{
    private readonly MainMdiForm _mdiParent;
    private readonly Dictionary<string, Form> _openForms = new Dictionary<string, Form>();
    
    public MdiManager(MainMdiForm mdiParent)
    {
        _mdiParent = mdiParent;
    }
    
    public T ShowOrActivate<T>(string key = null) where T : Form, new()
    {
        key = key ?? typeof(T).Name;
        
        if (_openForms.TryGetValue(key, out var existingForm) && !existingForm.IsDisposed)
        {
            existingForm.Activate();
            return (T)existingForm;
        }
        
        var newForm = new T
        {
            MdiParent = _mdiParent,
            Name = key
        };
        
        newForm.FormClosed += (s, e) => _openForms.Remove(key);
        _openForms[key] = newForm;
        newForm.Show();
        
        return newForm;
    }
    
    public void CloseAll()
    {
        foreach (var form in _mdiParent.MdiChildren)
        {
            form.Close();
        }
    }
}
```

## 2. ドッキングウィンドウ実装

### カスタムドッキングパネル
```csharp
public class DockablePanel : Panel
{
    private bool _isDocked = true;
    private Form _floatingForm;
    private DockStyle _originalDock;
    
    public event EventHandler DockStateChanged;
    
    public bool IsDocked
    {
        get => _isDocked;
        set
        {
            if (_isDocked != value)
            {
                _isDocked = value;
                UpdateDockState();
                DockStateChanged?.Invoke(this, EventArgs.Empty);
            }
        }
    }
    
    public DockablePanel()
    {
        InitializeHeader();
    }
    
    private void InitializeHeader()
    {
        var header = new Panel
        {
            Height = 25,
            Dock = DockStyle.Top,
            BackColor = SystemColors.ActiveCaption
        };
        
        var titleLabel = new Label
        {
            Text = "ドッキングパネル",
            Dock = DockStyle.Fill,
            TextAlign = ContentAlignment.MiddleLeft,
            ForeColor = SystemColors.ActiveCaptionText
        };
        
        var floatButton = new Button
        {
            Text = "◇",
            Width = 25,
            Dock = DockStyle.Right,
            FlatStyle = FlatStyle.Flat
        };
        
        floatButton.Click += (s, e) => IsDocked = !IsDocked;
        
        header.Controls.Add(titleLabel);
        header.Controls.Add(floatButton);
        Controls.Add(header);
        
        // ドラッグによる移動
        header.MouseDown += OnHeaderMouseDown;
        header.MouseMove += OnHeaderMouseMove;
        header.MouseUp += OnHeaderMouseUp;
    }
    
    private void UpdateDockState()
    {
        if (_isDocked)
        {
            // フローティングからドッキングへ
            if (_floatingForm != null)
            {
                var parent = _floatingForm.Tag as Control;
                parent?.Controls.Add(this);
                this.Dock = _originalDock;
                _floatingForm.Close();
                _floatingForm = null;
            }
        }
        else
        {
            // ドッキングからフローティングへ
            _originalDock = this.Dock;
            var parent = this.Parent;
            
            _floatingForm = new Form
            {
                Text = "フローティングパネル",
                Size = this.Size,
                StartPosition = FormStartPosition.Manual,
                Location = this.PointToScreen(Point.Empty),
                FormBorderStyle = FormBorderStyle.SizableToolWindow,
                Tag = parent
            };
            
            this.Dock = DockStyle.Fill;
            _floatingForm.Controls.Add(this);
            _floatingForm.Show();
        }
    }
}
```

## 3. 高度なWindows統合機能

### ドラッグ&ドロップ実装
```csharp
public class DragDropManager
{
    public static void EnableFileDrop(Control control, Action<string[]> onFilesDropped)
    {
        control.AllowDrop = true;
        
        control.DragEnter += (s, e) =>
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effect = DragDropEffects.Copy;
            }
            else
            {
                e.Effect = DragDropEffects.None;
            }
        };
        
        control.DragDrop += (s, e) =>
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                var files = (string[])e.Data.GetData(DataFormats.FileDrop);
                onFilesDropped?.Invoke(files);
            }
        };
    }
    
    public static void EnableDataGridViewDragDrop(DataGridView source, DataGridView target)
    {
        source.MouseDown += (s, e) =>
        {
            if (e.Button == MouseButtons.Left)
            {
                var hitTestInfo = source.HitTest(e.X, e.Y);
                if (hitTestInfo.RowIndex >= 0)
                {
                    var draggedRow = source.Rows[hitTestInfo.RowIndex];
                    source.DoDragDrop(draggedRow, DragDropEffects.Move);
                }
            }
        };
        
        target.AllowDrop = true;
        target.DragOver += (s, e) =>
        {
            e.Effect = DragDropEffects.Move;
            var point = target.PointToClient(new Point(e.X, e.Y));
            var hitTestInfo = target.HitTest(point.X, point.Y);
            
            if (hitTestInfo.RowIndex >= 0)
            {
                target.ClearSelection();
                target.Rows[hitTestInfo.RowIndex].Selected = true;
            }
        };
        
        target.DragDrop += (s, e) =>
        {
            var point = target.PointToClient(new Point(e.X, e.Y));
            var hitTestInfo = target.HitTest(point.X, point.Y);
            
            if (e.Data.GetDataPresent(typeof(DataGridViewRow)))
            {
                var draggedRow = (DataGridViewRow)e.Data.GetData(typeof(DataGridViewRow));
                // 行データのコピー処理
            }
        };
    }
}
```

### システムトレイ統合
```csharp
public class SystemTrayManager
{
    private readonly NotifyIcon _notifyIcon;
    private readonly Form _mainForm;
    
    public SystemTrayManager(Form mainForm)
    {
        _mainForm = mainForm;
        _notifyIcon = new NotifyIcon
        {
            Icon = Properties.Resources.AppIcon,
            Text = "エンタープライズアプリケーション",
            Visible = true
        };
        
        CreateContextMenu();
        RegisterEvents();
    }
    
    private void CreateContextMenu()
    {
        var contextMenu = new ContextMenuStrip();
        
        contextMenu.Items.Add("開く", null, (s, e) => ShowMainForm());
        contextMenu.Items.Add("-");
        contextMenu.Items.Add("新規作成", null, (s, e) => CreateNew());
        contextMenu.Items.Add("最近使用したファイル", null, CreateRecentFilesMenu());
        contextMenu.Items.Add("-");
        contextMenu.Items.Add("設定", null, (s, e) => ShowSettings());
        contextMenu.Items.Add("-");
        contextMenu.Items.Add("終了", null, (s, e) => ExitApplication());
        
        _notifyIcon.ContextMenuStrip = contextMenu;
    }
    
    private void RegisterEvents()
    {
        _notifyIcon.DoubleClick += (s, e) => ShowMainForm();
        
        _mainForm.FormClosing += (s, e) =>
        {
            if (e.CloseReason == CloseReason.UserClosing)
            {
                e.Cancel = true;
                _mainForm.WindowState = FormWindowState.Minimized;
                _mainForm.Hide();
                
                _notifyIcon.ShowBalloonTip(
                    3000,
                    "バックグラウンドで実行中",
                    "アプリケーションはシステムトレイで実行されています。",
                    ToolTipIcon.Info);
            }
        };
    }
    
    private void ShowMainForm()
    {
        _mainForm.Show();
        _mainForm.WindowState = FormWindowState.Normal;
        _mainForm.Activate();
    }
    
    public void ShowNotification(string title, string message, ToolTipIcon icon = ToolTipIcon.Info)
    {
        _notifyIcon.ShowBalloonTip(5000, title, message, icon);
    }
    
    public void Dispose()
    {
        _notifyIcon.Visible = false;
        _notifyIcon.Dispose();
    }
}
```

### レジストリとファイル関連付け
```csharp
public static class FileAssociationManager
{
    public static void RegisterFileAssociation(string extension, string progId, string description, string iconPath, string openCommand)
    {
        // HKEY_CURRENT_USER で登録（管理者権限不要）
        using (var key = Registry.CurrentUser.CreateSubKey($@"Software\Classes\{extension}"))
        {
            key.SetValue("", progId);
        }
        
        using (var key = Registry.CurrentUser.CreateSubKey($@"Software\Classes\{progId}"))
        {
            key.SetValue("", description);
            
            using (var iconKey = key.CreateSubKey("DefaultIcon"))
            {
                iconKey.SetValue("", iconPath);
            }
            
            using (var commandKey = key.CreateSubKey(@"shell\open\command"))
            {
                commandKey.SetValue("", openCommand);
            }
        }
        
        // エクスプローラーに変更を通知
        SHChangeNotify(0x08000000, 0x0000, IntPtr.Zero, IntPtr.Zero);
    }
    
    [DllImport("shell32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern void SHChangeNotify(uint wEventId, uint uFlags, IntPtr dwItem1, IntPtr dwItem2);
}
```

## 4. パフォーマンス最適化

### 仮想モードDataGridView
```csharp
public class VirtualDataGridView : DataGridView
{
    private readonly IList<DataItem> _dataSource;
    private readonly Cache<int, DataGridViewRow> _rowCache;
    
    public VirtualDataGridView()
    {
        VirtualMode = true;
        _rowCache = new Cache<int, DataGridViewRow>(1000);
        
        CellValueNeeded += OnCellValueNeeded;
        CellValuePushed += OnCellValuePushed;
        NewRowNeeded += OnNewRowNeeded;
        RowsAdded += OnRowsAdded;
        RowsRemoved += OnRowsRemoved;
        UserDeletingRow += OnUserDeletingRow;
    }
    
    public void SetDataSource(IList<DataItem> dataSource)
    {
        _dataSource = dataSource;
        RowCount = dataSource.Count;
        _rowCache.Clear();
    }
    
    private void OnCellValueNeeded(object sender, DataGridViewCellValueEventArgs e)
    {
        if (e.RowIndex < _dataSource.Count)
        {
            var item = _dataSource[e.RowIndex];
            
            switch (Columns[e.ColumnIndex].Name)
            {
                case "Id":
                    e.Value = item.Id;
                    break;
                case "Name":
                    e.Value = item.Name;
                    break;
                case "Description":
                    e.Value = item.Description;
                    break;
            }
        }
    }
    
    // ページング実装
    public void LoadPage(int pageNumber, int pageSize)
    {
        var startIndex = (pageNumber - 1) * pageSize;
        var endIndex = Math.Min(startIndex + pageSize, _dataSource.Count);
        
        FirstDisplayedScrollingRowIndex = startIndex;
        
        // 事前キャッシュ
        Task.Run(() =>
        {
            for (int i = startIndex; i < endIndex; i++)
            {
                if (!_rowCache.Contains(i))
                {
                    var row = CreateCachedRow(i);
                    _rowCache.Add(i, row);
                }
            }
        });
    }
}
```

### 非同期UI更新パターン
```csharp
public class AsyncUIUpdater
{
    private readonly Control _control;
    private readonly SynchronizationContext _syncContext;
    
    public AsyncUIUpdater(Control control)
    {
        _control = control;
        _syncContext = SynchronizationContext.Current;
    }
    
    public async Task UpdateUIAsync<T>(
        Func<IProgress<int>, CancellationToken, Task<T>> operation,
        Action<T> onSuccess,
        Action<Exception> onError = null)
    {
        using (var cts = new CancellationTokenSource())
        using (var progressDialog = new ProgressDialog())
        {
            progressDialog.CancelRequested += (s, e) => cts.Cancel();
            
            var progress = new Progress<int>(percent =>
            {
                _syncContext.Post(_ => progressDialog.UpdateProgress(percent), null);
            });
            
            progressDialog.Show(_control);
            
            try
            {
                var result = await operation(progress, cts.Token);
                _syncContext.Post(_ => onSuccess(result), null);
            }
            catch (OperationCanceledException)
            {
                // キャンセルされた
            }
            catch (Exception ex)
            {
                _syncContext.Post(_ => onError?.Invoke(ex), null);
            }
            finally
            {
                progressDialog.Close();
            }
        }
    }
}
```

## 5. 多言語対応

### リソースマネージャー実装
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
        _currentCulture = CultureInfo.CurrentUICulture;
    }
    
    public static void SetLanguage(string cultureName)
    {
        _currentCulture = new CultureInfo(cultureName);
        Thread.CurrentThread.CurrentUICulture = _currentCulture;
        Thread.CurrentThread.CurrentCulture = _currentCulture;
        
        // 開いているすべてのフォームを更新
        foreach (Form form in Application.OpenForms)
        {
            UpdateFormLocalization(form);
        }
    }
    
    public static string GetString(string key)
    {
        return _resourceManager.GetString(key, _currentCulture) ?? key;
    }
    
    private static void UpdateFormLocalization(Control control)
    {
        var resources = new ComponentResourceManager(control.GetType());
        
        // コントロール自体のテキストを更新
        resources.ApplyResources(control, control.Name, _currentCulture);
        
        // 子コントロールを再帰的に更新
        foreach (Control child in control.Controls)
        {
            UpdateFormLocalization(child);
        }
        
        // メニューやツールバーの更新
        if (control is Form form)
        {
            UpdateMenuStrip(form.MainMenuStrip, resources);
            UpdateToolStrip(form.Controls.OfType<ToolStrip>().FirstOrDefault(), resources);
        }
    }
}
```

### 動的レイアウト調整
```csharp
public class CultureAwareLayoutManager
{
    public static void AdjustLayoutForCulture(Control container, CultureInfo culture)
    {
        var isRightToLeft = culture.TextInfo.IsRightToLeft;
        
        container.RightToLeft = isRightToLeft ? RightToLeft.Yes : RightToLeft.No;
        
        // コントロールの配置を調整
        foreach (Control control in container.Controls)
        {
            if (control is Label || control is Button || control is TextBox)
            {
                // テキストの長さに応じてサイズを調整
                using (var g = control.CreateGraphics())
                {
                    var textSize = g.MeasureString(control.Text, control.Font);
                    var padding = 10;
                    control.Width = (int)Math.Ceiling(textSize.Width) + padding;
                }
            }
            
            // 子コントロールも再帰的に調整
            if (control.HasChildren)
            {
                AdjustLayoutForCulture(control, culture);
            }
        }
    }
}
```

## 6. 高度な印刷機能

### カスタム印刷プレビュー
```csharp
public class AdvancedPrintPreview : PrintPreviewDialog
{
    private readonly PrintDocument _document;
    private int _currentPage = 1;
    private int _totalPages = 1;
    
    public AdvancedPrintPreview(PrintDocument document)
    {
        _document = document;
        Document = document;
        
        // カスタムツールバーの追加
        AddCustomToolbar();
    }
    
    private void AddCustomToolbar()
    {
        var toolbar = new ToolStrip();
        
        // ページ設定
        var pageSetupButton = new ToolStripButton("ページ設定", null, (s, e) =>
        {
            using (var pageSetupDialog = new PageSetupDialog())
            {
                pageSetupDialog.Document = _document;
                pageSetupDialog.ShowDialog();
            }
        });
        
        // エクスポート
        var exportButton = new ToolStripDropDownButton("エクスポート");
        exportButton.DropDownItems.Add("PDF", null, (s, e) => ExportToPdf());
        exportButton.DropDownItems.Add("XPS", null, (s, e) => ExportToXps());
        
        toolbar.Items.AddRange(new ToolStripItem[] { pageSetupButton, exportButton });
        Controls.Add(toolbar);
    }
    
    private void ExportToPdf()
    {
        // PDF出力実装
        using (var saveDialog = new SaveFileDialog())
        {
            saveDialog.Filter = "PDF Files|*.pdf";
            if (saveDialog.ShowDialog() == DialogResult.OK)
            {
                // iTextSharp等を使用してPDF生成
            }
        }
    }
}
```

このガイドに従うことで、Windows Formsデスクトップアプリケーションに必要な高度な機能を実装できます。