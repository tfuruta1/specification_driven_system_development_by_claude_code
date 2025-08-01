# UIコンポーネントカタログ - Windows Forms エンタープライズアプリケーション

## 1. 基本コンポーネント

### ボタンコンポーネント
```csharp
public class EnterpriseButton : Button
{
    public enum ButtonType
    {
        Primary,
        Secondary,
        Success,
        Warning,
        Danger,
        Info,
        Link
    }
    
    private ButtonType _type = ButtonType.Primary;
    private bool _isLoading = false;
    
    public ButtonType Type
    {
        get => _type;
        set
        {
            _type = value;
            ApplyStyle();
        }
    }
    
    public bool IsLoading
    {
        get => _isLoading;
        set
        {
            _isLoading = value;
            UpdateLoadingState();
        }
    }
    
    public EnterpriseButton()
    {
        SetStyle(ControlStyles.UserPaint | 
                ControlStyles.AllPaintingInWmPaint | 
                ControlStyles.DoubleBuffer, true);
        
        FlatStyle = FlatStyle.Flat;
        FlatAppearance.BorderSize = 1;
        Font = Typography.Special.Button;
        Cursor = Cursors.Hand;
        Size = new Size(100, 32);
        
        ApplyStyle();
    }
    
    private void ApplyStyle()
    {
        switch (_type)
        {
            case ButtonType.Primary:
                BackColor = ColorScheme.Primary.Main;
                ForeColor = Color.White;
                FlatAppearance.BorderColor = ColorScheme.Primary.Main;
                break;
                
            case ButtonType.Secondary:
                BackColor = Color.White;
                ForeColor = ColorScheme.Primary.Main;
                FlatAppearance.BorderColor = ColorScheme.Primary.Main;
                break;
                
            case ButtonType.Success:
                BackColor = ColorScheme.Semantic.Success;
                ForeColor = Color.White;
                FlatAppearance.BorderColor = ColorScheme.Semantic.Success;
                break;
                
            case ButtonType.Warning:
                BackColor = ColorScheme.Semantic.Warning;
                ForeColor = Color.White;
                FlatAppearance.BorderColor = ColorScheme.Semantic.Warning;
                break;
                
            case ButtonType.Danger:
                BackColor = ColorScheme.Semantic.Error;
                ForeColor = Color.White;
                FlatAppearance.BorderColor = ColorScheme.Semantic.Error;
                break;
                
            case ButtonType.Link:
                BackColor = Color.Transparent;
                ForeColor = ColorScheme.Primary.Main;
                FlatAppearance.BorderSize = 0;
                Font = new Font(Font, FontStyle.Underline);
                break;
        }
    }
    
    protected override void OnPaint(PaintEventArgs e)
    {
        base.OnPaint(e);
        
        if (_isLoading)
        {
            // ローディングアニメーション描画
            DrawLoadingAnimation(e.Graphics);
        }
    }
    
    private void DrawLoadingAnimation(Graphics g)
    {
        var rect = new Rectangle(Width - 24, (Height - 16) / 2, 16, 16);
        using (var pen = new Pen(ForeColor, 2))
        {
            g.DrawArc(pen, rect, _animationAngle, 270);
        }
    }
}
```

### 入力フィールドコンポーネント
```csharp
public class EnterpriseTextBox : UserControl
{
    private TextBox _textBox;
    private Label _label;
    private Label _errorLabel;
    private Panel _underline;
    private bool _hasError;
    
    public string Label
    {
        get => _label.Text;
        set => _label.Text = value;
    }
    
    public string Text
    {
        get => _textBox.Text;
        set => _textBox.Text = value;
    }
    
    public string Placeholder { get; set; }
    
    public string ErrorMessage
    {
        get => _errorLabel.Text;
        set
        {
            _errorLabel.Text = value;
            _hasError = !string.IsNullOrEmpty(value);
            UpdateErrorState();
        }
    }
    
    public EnterpriseTextBox()
    {
        InitializeComponents();
    }
    
    private void InitializeComponents()
    {
        Height = 64;
        
        _label = new Label
        {
            Location = new Point(0, 0),
            Size = new Size(Width, 16),
            Font = Typography.Body.Small,
            ForeColor = ColorScheme.Gray.G600
        };
        
        _textBox = new TextBox
        {
            Location = new Point(0, 20),
            Size = new Size(Width, 24),
            BorderStyle = BorderStyle.None,
            Font = Typography.Body.Normal
        };
        
        _underline = new Panel
        {
            Location = new Point(0, 44),
            Size = new Size(Width, 1),
            BackColor = ColorScheme.Gray.G400
        };
        
        _errorLabel = new Label
        {
            Location = new Point(0, 48),
            Size = new Size(Width, 16),
            Font = Typography.Body.Small,
            ForeColor = ColorScheme.Semantic.Error,
            Visible = false
        };
        
        Controls.AddRange(new Control[] { _label, _textBox, _underline, _errorLabel });
        
        // イベント設定
        _textBox.Enter += OnTextBoxEnter;
        _textBox.Leave += OnTextBoxLeave;
        _textBox.TextChanged += OnTextBoxTextChanged;
    }
    
    private void OnTextBoxEnter(object sender, EventArgs e)
    {
        if (!_hasError)
        {
            _underline.BackColor = ColorScheme.Primary.Main;
            _underline.Height = 2;
        }
    }
    
    private void OnTextBoxLeave(object sender, EventArgs e)
    {
        if (!_hasError)
        {
            _underline.BackColor = ColorScheme.Gray.G400;
            _underline.Height = 1;
        }
    }
    
    private void UpdateErrorState()
    {
        _errorLabel.Visible = _hasError;
        _underline.BackColor = _hasError ? ColorScheme.Semantic.Error : ColorScheme.Gray.G400;
        _underline.Height = _hasError ? 2 : 1;
    }
}
```

### セレクトボックスコンポーネント
```csharp
public class EnterpriseComboBox : ComboBox
{
    private string _placeholder = "選択してください";
    private Color _placeholderColor = ColorScheme.Gray.G500;
    
    public string Placeholder
    {
        get => _placeholder;
        set
        {
            _placeholder = value;
            Invalidate();
        }
    }
    
    public EnterpriseComboBox()
    {
        DrawMode = DrawMode.OwnerDrawFixed;
        DropDownStyle = ComboBoxStyle.DropDownList;
        FlatStyle = FlatStyle.Flat;
        Font = Typography.Body.Normal;
        ItemHeight = 24;
        
        // スタイル設定
        BackColor = Color.White;
        ForeColor = ColorScheme.Gray.G900;
    }
    
    protected override void OnDrawItem(DrawItemEventArgs e)
    {
        base.OnDrawItem(e);
        
        if (e.Index < 0) return;
        
        e.DrawBackground();
        
        var text = Items[e.Index]?.ToString() ?? string.Empty;
        var textColor = (e.State & DrawItemState.Selected) == DrawItemState.Selected
            ? Color.White
            : ForeColor;
        
        if ((e.State & DrawItemState.Selected) == DrawItemState.Selected)
        {
            using (var brush = new SolidBrush(ColorScheme.Primary.Main))
            {
                e.Graphics.FillRectangle(brush, e.Bounds);
            }
        }
        
        using (var brush = new SolidBrush(textColor))
        {
            e.Graphics.DrawString(text, Font, brush, 
                new Rectangle(e.Bounds.X + 8, e.Bounds.Y, e.Bounds.Width - 8, e.Bounds.Height),
                new StringFormat { LineAlignment = StringAlignment.Center });
        }
        
        e.DrawFocusRectangle();
    }
    
    protected override void OnPaint(PaintEventArgs e)
    {
        base.OnPaint(e);
        
        if (SelectedIndex == -1 && !string.IsNullOrEmpty(_placeholder))
        {
            using (var brush = new SolidBrush(_placeholderColor))
            {
                e.Graphics.DrawString(_placeholder, Font, brush,
                    new Rectangle(3, 3, Width - 20, Height - 6),
                    new StringFormat { LineAlignment = StringAlignment.Center });
            }
        }
    }
}
```

## 2. データ表示コンポーネント

### データグリッドコンポーネント
```csharp
public class EnterpriseDataGrid : DataGridView
{
    private ContextMenuStrip _contextMenu;
    private ToolStripMenuItem _copyMenuItem;
    private ToolStripMenuItem _exportMenuItem;
    private ToolStripMenuItem _printMenuItem;
    
    public bool EnableContextMenu { get; set; } = true;
    public bool EnableSorting { get; set; } = true;
    public bool EnableFiltering { get; set; } = true;
    public bool EnableGrouping { get; set; } = false;
    
    public EnterpriseDataGrid()
    {
        InitializeStyle();
        InitializeContextMenu();
    }
    
    private void InitializeStyle()
    {
        // 基本設定
        AllowUserToAddRows = false;
        AllowUserToDeleteRows = false;
        AllowUserToResizeRows = false;
        AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
        BackgroundColor = Color.White;
        BorderStyle = BorderStyle.None;
        CellBorderStyle = DataGridViewCellBorderStyle.SingleHorizontal;
        ColumnHeadersBorderStyle = DataGridViewHeaderBorderStyle.None;
        
        // ヘッダースタイル
        ColumnHeadersDefaultCellStyle = new DataGridViewCellStyle
        {
            BackColor = ColorScheme.Gray.G100,
            ForeColor = ColorScheme.Gray.G900,
            Font = new Font(Typography.Body.Normal.FontFamily, Typography.Body.Normal.Size, FontStyle.Bold),
            SelectionBackColor = ColorScheme.Gray.G100,
            SelectionForeColor = ColorScheme.Gray.G900,
            Alignment = DataGridViewContentAlignment.MiddleLeft,
            Padding = new Padding(8, 4, 8, 4)
        };
        ColumnHeadersHeight = 40;
        ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.DisableResizing;
        
        // セルスタイル
        DefaultCellStyle = new DataGridViewCellStyle
        {
            BackColor = Color.White,
            ForeColor = ColorScheme.Gray.G900,
            Font = Typography.Body.Normal,
            SelectionBackColor = ColorScheme.Primary.Light,
            SelectionForeColor = Color.White,
            Padding = new Padding(8, 4, 8, 4)
        };
        
        // 交互行の色
        AlternatingRowsDefaultCellStyle = new DataGridViewCellStyle
        {
            BackColor = ColorScheme.Gray.G50
        };
        
        // グリッド線
        GridColor = ColorScheme.Gray.G200;
        
        // 行設定
        RowHeadersVisible = false;
        RowTemplate.Height = 40;
        
        // 選択モード
        SelectionMode = DataGridViewSelectionMode.FullRowSelect;
        MultiSelect = true;
        
        // パフォーマンス最適化
        DoubleBuffered = true;
        EnableHeadersVisualStyles = false;
    }
    
    protected override void OnCellPainting(DataGridViewCellPaintingEventArgs e)
    {
        base.OnCellPainting(e);
        
        // ヘッダーの下線
        if (e.RowIndex == -1 && e.ColumnIndex > -1)
        {
            e.Paint(e.CellBounds, DataGridViewPaintParts.All & ~DataGridViewPaintParts.Border);
            
            using (var pen = new Pen(ColorScheme.Gray.G300, 2))
            {
                e.Graphics.DrawLine(pen, 
                    e.CellBounds.Left, e.CellBounds.Bottom - 1,
                    e.CellBounds.Right, e.CellBounds.Bottom - 1);
            }
            
            e.Handled = true;
        }
    }
    
    public void AddActionColumn(string name, string headerText, Action<int> clickAction)
    {
        var column = new DataGridViewButtonColumn
        {
            Name = name,
            HeaderText = headerText,
            Text = "実行",
            UseColumnTextForButtonValue = true,
            Width = 80,
            DefaultCellStyle = new DataGridViewCellStyle
            {
                BackColor = ColorScheme.Primary.Main,
                ForeColor = Color.White,
                SelectionBackColor = ColorScheme.Primary.Dark,
                SelectionForeColor = Color.White
            }
        };
        
        Columns.Add(column);
        
        CellClick += (s, e) =>
        {
            if (e.ColumnIndex == column.Index && e.RowIndex >= 0)
            {
                clickAction(e.RowIndex);
            }
        };
    }
}
```

### カードコンポーネント
```csharp
public class EnterpriseCard : Panel
{
    private Label _titleLabel;
    private Panel _headerPanel;
    private Panel _contentPanel;
    private Panel _footerPanel;
    
    public string Title
    {
        get => _titleLabel.Text;
        set => _titleLabel.Text = value;
    }
    
    public Panel ContentPanel => _contentPanel;
    public Panel FooterPanel => _footerPanel;
    
    public EnterpriseCard()
    {
        InitializeComponents();
        ApplyStyle();
    }
    
    private void InitializeComponents()
    {
        // ヘッダーパネル
        _headerPanel = new Panel
        {
            Dock = DockStyle.Top,
            Height = 48,
            Padding = new Padding(16, 12, 16, 12)
        };
        
        _titleLabel = new Label
        {
            Dock = DockStyle.Fill,
            Font = Typography.Heading.H4,
            ForeColor = ColorScheme.Gray.G900,
            TextAlign = ContentAlignment.MiddleLeft
        };
        
        _headerPanel.Controls.Add(_titleLabel);
        
        // コンテンツパネル
        _contentPanel = new Panel
        {
            Dock = DockStyle.Fill,
            Padding = new Padding(16)
        };
        
        // フッターパネル
        _footerPanel = new Panel
        {
            Dock = DockStyle.Bottom,
            Height = 48,
            Padding = new Padding(16, 12, 16, 12),
            Visible = false
        };
        
        Controls.Add(_contentPanel);
        Controls.Add(_footerPanel);
        Controls.Add(_headerPanel);
    }
    
    private void ApplyStyle()
    {
        BackColor = Color.White;
        BorderStyle = BorderStyle.None;
        Padding = new Padding(1);
        
        // 影効果の実装
        SetStyle(ControlStyles.ResizeRedraw, true);
    }
    
    protected override void OnPaint(PaintEventArgs e)
    {
        base.OnPaint(e);
        
        // カードの影を描画
        var rect = new Rectangle(0, 0, Width - 1, Height - 1);
        
        using (var path = CreateRoundedRectanglePath(rect, 4))
        {
            // 影
            for (int i = 0; i < 3; i++)
            {
                var shadowRect = new Rectangle(i, i, Width - i * 2, Height - i * 2);
                using (var shadowPath = CreateRoundedRectanglePath(shadowRect, 4))
                using (var pen = new Pen(Color.FromArgb(20 - i * 5, 0, 0, 0), 1))
                {
                    e.Graphics.DrawPath(pen, shadowPath);
                }
            }
            
            // 背景
            using (var brush = new SolidBrush(BackColor))
            {
                e.Graphics.FillPath(brush, path);
            }
            
            // 枠線
            using (var pen = new Pen(ColorScheme.Gray.G200, 1))
            {
                e.Graphics.DrawPath(pen, path);
            }
        }
    }
    
    private GraphicsPath CreateRoundedRectanglePath(Rectangle rect, int radius)
    {
        var path = new GraphicsPath();
        path.AddArc(rect.X, rect.Y, radius * 2, radius * 2, 180, 90);
        path.AddArc(rect.Right - radius * 2, rect.Y, radius * 2, radius * 2, 270, 90);
        path.AddArc(rect.Right - radius * 2, rect.Bottom - radius * 2, radius * 2, radius * 2, 0, 90);
        path.AddArc(rect.X, rect.Bottom - radius * 2, radius * 2, radius * 2, 90, 90);
        path.CloseFigure();
        return path;
    }
}
```

## 3. フィードバックコンポーネント

### トースト通知
```csharp
public class ToastNotification : Form
{
    public enum ToastType
    {
        Success,
        Error,
        Warning,
        Info
    }
    
    private Timer _autoCloseTimer;
    private Timer _animationTimer;
    private int _targetY;
    
    public ToastNotification(string message, ToastType type = ToastType.Info, int duration = 3000)
    {
        InitializeForm();
        SetupContent(message, type);
        SetupTimers(duration);
    }
    
    private void InitializeForm()
    {
        FormBorderStyle = FormBorderStyle.None;
        ShowInTaskbar = false;
        TopMost = true;
        StartPosition = FormStartPosition.Manual;
        Size = new Size(400, 80);
        
        // 角丸の実装
        Region = Region.FromHrgn(CreateRoundRectRgn(0, 0, Width, Height, 8, 8));
    }
    
    private void SetupContent(string message, ToastType type)
    {
        var panel = new Panel
        {
            Dock = DockStyle.Fill,
            Padding = new Padding(16)
        };
        
        var icon = new PictureBox
        {
            Size = new Size(24, 24),
            Location = new Point(16, 28),
            SizeMode = PictureBoxSizeMode.CenterImage
        };
        
        var label = new Label
        {
            Text = message,
            Location = new Point(56, 16),
            Size = new Size(328, 48),
            Font = Typography.Body.Normal,
            TextAlign = ContentAlignment.MiddleLeft
        };
        
        switch (type)
        {
            case ToastType.Success:
                BackColor = ColorScheme.Semantic.Success;
                icon.Image = Icons.Status.Success;
                break;
            case ToastType.Error:
                BackColor = ColorScheme.Semantic.Error;
                icon.Image = Icons.Status.Error;
                break;
            case ToastType.Warning:
                BackColor = ColorScheme.Semantic.Warning;
                icon.Image = Icons.Status.Warning;
                break;
            case ToastType.Info:
                BackColor = ColorScheme.Semantic.Info;
                icon.Image = Icons.Status.Info;
                break;
        }
        
        label.ForeColor = Color.White;
        
        panel.Controls.AddRange(new Control[] { icon, label });
        Controls.Add(panel);
    }
    
    public void ShowToast(Control parent = null)
    {
        var screen = Screen.FromControl(parent ?? Form.ActiveForm);
        var x = screen.WorkingArea.Right - Width - 20;
        var startY = screen.WorkingArea.Bottom;
        _targetY = screen.WorkingArea.Bottom - Height - 20;
        
        Location = new Point(x, startY);
        
        Show();
        
        // スライドインアニメーション
        _animationTimer = new Timer { Interval = 10 };
        _animationTimer.Tick += (s, e) =>
        {
            if (Top > _targetY)
            {
                Top -= 5;
            }
            else
            {
                _animationTimer.Stop();
            }
        };
        _animationTimer.Start();
    }
    
    [DllImport("Gdi32.dll", EntryPoint = "CreateRoundRectRgn")]
    private static extern IntPtr CreateRoundRectRgn(int x1, int y1, int x2, int y2, int cx, int cy);
}
```

### プログレスインジケーター
```csharp
public class CircularProgressBar : Control
{
    private int _value = 0;
    private int _maximum = 100;
    private Timer _animationTimer;
    private float _animationAngle = 0;
    
    public int Value
    {
        get => _value;
        set
        {
            _value = Math.Max(0, Math.Min(value, _maximum));
            Invalidate();
        }
    }
    
    public int Maximum
    {
        get => _maximum;
        set
        {
            _maximum = Math.Max(1, value);
            Invalidate();
        }
    }
    
    public bool IsIndeterminate { get; set; }
    
    public CircularProgressBar()
    {
        SetStyle(ControlStyles.UserPaint | 
                ControlStyles.AllPaintingInWmPaint | 
                ControlStyles.DoubleBuffer | 
                ControlStyles.ResizeRedraw, true);
        
        Size = new Size(48, 48);
        
        _animationTimer = new Timer { Interval = 50 };
        _animationTimer.Tick += (s, e) =>
        {
            _animationAngle += 10;
            if (_animationAngle >= 360) _animationAngle = 0;
            Invalidate();
        };
    }
    
    protected override void OnPaint(PaintEventArgs e)
    {
        base.OnPaint(e);
        
        e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
        
        var rect = new Rectangle(4, 4, Width - 8, Height - 8);
        
        using (var bgPen = new Pen(ColorScheme.Gray.G300, 4))
        {
            e.Graphics.DrawEllipse(bgPen, rect);
        }
        
        if (IsIndeterminate)
        {
            using (var pen = new Pen(ColorScheme.Primary.Main, 4))
            {
                e.Graphics.DrawArc(pen, rect, _animationAngle, 90);
            }
            
            if (!_animationTimer.Enabled)
                _animationTimer.Start();
        }
        else
        {
            if (_animationTimer.Enabled)
                _animationTimer.Stop();
            
            var sweepAngle = (float)(_value * 360.0 / _maximum);
            
            using (var pen = new Pen(ColorScheme.Primary.Main, 4))
            {
                e.Graphics.DrawArc(pen, rect, -90, sweepAngle);
            }
            
            // パーセンテージ表示
            var text = $"{_value * 100 / _maximum}%";
            var textSize = e.Graphics.MeasureString(text, Font);
            var textLocation = new PointF(
                (Width - textSize.Width) / 2,
                (Height - textSize.Height) / 2
            );
            
            using (var brush = new SolidBrush(ColorScheme.Gray.G900))
            {
                e.Graphics.DrawString(text, Font, brush, textLocation);
            }
        }
    }
}
```

## 4. ナビゲーションコンポーネント

### タブコントロール
```csharp
public class EnterpriseTabControl : TabControl
{
    public EnterpriseTabControl()
    {
        SetStyle(ControlStyles.UserPaint | 
                ControlStyles.AllPaintingInWmPaint | 
                ControlStyles.DoubleBuffer, true);
        
        ItemSize = new Size(120, 40);
        SizeMode = TabSizeMode.Fixed;
        Font = Typography.Body.Normal;
    }
    
    protected override void OnPaint(PaintEventArgs e)
    {
        e.Graphics.Clear(BackColor);
        
        // タブヘッダー背景
        var headerRect = new Rectangle(0, 0, Width, ItemSize.Height);
        using (var brush = new SolidBrush(ColorScheme.Gray.G100))
        {
            e.Graphics.FillRectangle(brush, headerRect);
        }
        
        // 各タブを描画
        for (int i = 0; i < TabCount; i++)
        {
            DrawTab(e.Graphics, i);
        }
        
        // コンテンツ領域の枠線
        var contentRect = new Rectangle(0, ItemSize.Height, Width - 1, Height - ItemSize.Height - 1);
        using (var pen = new Pen(ColorScheme.Gray.G300))
        {
            e.Graphics.DrawRectangle(pen, contentRect);
        }
    }
    
    private void DrawTab(Graphics g, int index)
    {
        var bounds = GetTabRect(index);
        var selected = SelectedIndex == index;
        var tabPage = TabPages[index];
        
        // 背景
        if (selected)
        {
            using (var brush = new SolidBrush(BackColor))
            {
                g.FillRectangle(brush, bounds);
            }
        }
        
        // テキスト
        var textColor = selected ? ColorScheme.Primary.Main : ColorScheme.Gray.G700;
        var textFormat = new StringFormat
        {
            Alignment = StringAlignment.Center,
            LineAlignment = StringAlignment.Center
        };
        
        using (var brush = new SolidBrush(textColor))
        {
            g.DrawString(tabPage.Text, Font, brush, bounds, textFormat);
        }
        
        // 選択インジケーター
        if (selected)
        {
            using (var pen = new Pen(ColorScheme.Primary.Main, 3))
            {
                g.DrawLine(pen, bounds.Left, bounds.Bottom - 2, bounds.Right, bounds.Bottom - 2);
            }
        }
    }
}
```

このUIコンポーネントカタログにより、統一されたデザインで高品質なWindows Formsアプリケーションを効率的に構築できます。