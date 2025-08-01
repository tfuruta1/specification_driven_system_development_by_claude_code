# デザインシステム概要 - Windows Forms エンタープライズアプリケーション

## 1. デザイン原則

### 基本理念
- **一貫性**: すべての画面で統一されたユーザー体験
- **効率性**: 業務効率を最大化するインターフェース
- **親しみやすさ**: 既存Windowsアプリケーションとの親和性
- **アクセシビリティ**: すべてのユーザーが使いやすい設計
- **拡張性**: 将来の機能追加に対応できる柔軟性

### ターゲットユーザー
```yaml
主要ユーザー:
  業務担当者:
    特徴: 
      - 日常的に8時間以上使用
      - キーボード操作を重視
      - 効率性を最優先
    要件:
      - ショートカットキー対応
      - タブ移動の最適化
      - 一括処理機能
      
  管理者:
    特徴:
      - 複数画面の同時監視
      - データ分析・レポート作成
      - 例外処理への対応
    要件:
      - ダッシュボード機能
      - 高度なフィルタリング
      - エクスポート機能
```

## 2. ビジュアルデザインシステム

### カラーパレット
```csharp
public static class ColorScheme
{
    // プライマリカラー
    public static class Primary
    {
        public static Color Main = Color.FromArgb(25, 118, 210);      // #1976D2
        public static Color Light = Color.FromArgb(66, 165, 245);     // #42A5F5
        public static Color Dark = Color.FromArgb(13, 71, 161);       // #0D47A1
        public static Color Text = Color.White;                        // テキスト色
    }
    
    // セカンダリカラー
    public static class Secondary
    {
        public static Color Main = Color.FromArgb(220, 231, 117);     // #DCE775
        public static Color Light = Color.FromArgb(240, 244, 195);    // #F0F4C3
        public static Color Dark = Color.FromArgb(174, 213, 129);     // #AED581
        public static Color Text = Color.FromArgb(33, 33, 33);        // テキスト色
    }
    
    // セマンティックカラー
    public static class Semantic
    {
        public static Color Success = Color.FromArgb(76, 175, 80);    // #4CAF50
        public static Color Warning = Color.FromArgb(255, 152, 0);    // #FF9800
        public static Color Error = Color.FromArgb(244, 67, 54);      // #F44336
        public static Color Info = Color.FromArgb(3, 169, 244);       // #03A9F4
    }
    
    // グレースケール
    public static class Gray
    {
        public static Color G50 = Color.FromArgb(250, 250, 250);      // #FAFAFA
        public static Color G100 = Color.FromArgb(245, 245, 245);     // #F5F5F5
        public static Color G200 = Color.FromArgb(238, 238, 238);     // #EEEEEE
        public static Color G300 = Color.FromArgb(224, 224, 224);     // #E0E0E0
        public static Color G400 = Color.FromArgb(189, 189, 189);     // #BDBDBD
        public static Color G500 = Color.FromArgb(158, 158, 158);     // #9E9E9E
        public static Color G600 = Color.FromArgb(117, 117, 117);     // #757575
        public static Color G700 = Color.FromArgb(97, 97, 97);        // #616161
        public static Color G800 = Color.FromArgb(66, 66, 66);        // #424242
        public static Color G900 = Color.FromArgb(33, 33, 33);        // #212121
    }
}
```

### タイポグラフィ
```csharp
public static class Typography
{
    private static readonly string DefaultFontFamily = "メイリオ";
    private static readonly string MonospaceFontFamily = "Consolas";
    
    // 見出し
    public static class Heading
    {
        public static Font H1 = new Font(DefaultFontFamily, 24f, FontStyle.Bold);
        public static Font H2 = new Font(DefaultFontFamily, 20f, FontStyle.Bold);
        public static Font H3 = new Font(DefaultFontFamily, 16f, FontStyle.Bold);
        public static Font H4 = new Font(DefaultFontFamily, 14f, FontStyle.Bold);
        public static Font H5 = new Font(DefaultFontFamily, 12f, FontStyle.Bold);
    }
    
    // 本文
    public static class Body
    {
        public static Font Large = new Font(DefaultFontFamily, 11f);
        public static Font Normal = new Font(DefaultFontFamily, 9f);
        public static Font Small = new Font(DefaultFontFamily, 8f);
    }
    
    // 特殊用途
    public static class Special
    {
        public static Font Code = new Font(MonospaceFontFamily, 9f);
        public static Font Caption = new Font(DefaultFontFamily, 8f);
        public static Font Button = new Font(DefaultFontFamily, 9f);
    }
}
```

### スペーシングシステム
```csharp
public static class Spacing
{
    // 基本単位（8pxグリッド）
    public const int Unit = 8;
    
    // スペーシングスケール
    public const int XXS = Unit / 2;      // 4px
    public const int XS = Unit;           // 8px
    public const int SM = Unit * 2;       // 16px
    public const int MD = Unit * 3;       // 24px
    public const int LG = Unit * 4;       // 32px
    public const int XL = Unit * 5;       // 40px
    public const int XXL = Unit * 6;      // 48px
    
    // パディング
    public static class Padding
    {
        public static readonly System.Windows.Forms.Padding None = new System.Windows.Forms.Padding(0);
        public static readonly System.Windows.Forms.Padding Small = new System.Windows.Forms.Padding(XS);
        public static readonly System.Windows.Forms.Padding Medium = new System.Windows.Forms.Padding(SM);
        public static readonly System.Windows.Forms.Padding Large = new System.Windows.Forms.Padding(MD);
    }
    
    // マージン
    public static class Margin
    {
        public static readonly System.Windows.Forms.Padding None = new System.Windows.Forms.Padding(0);
        public static readonly System.Windows.Forms.Padding Small = new System.Windows.Forms.Padding(XS);
        public static readonly System.Windows.Forms.Padding Medium = new System.Windows.Forms.Padding(SM);
        public static readonly System.Windows.Forms.Padding Large = new System.Windows.Forms.Padding(MD);
    }
}
```

## 3. コンポーネントライブラリ

### ボタンスタイル
```csharp
public static class ButtonStyles
{
    public static void ApplyPrimaryStyle(Button button)
    {
        button.BackColor = ColorScheme.Primary.Main;
        button.ForeColor = ColorScheme.Primary.Text;
        button.FlatStyle = FlatStyle.Flat;
        button.FlatAppearance.BorderSize = 0;
        button.Font = Typography.Special.Button;
        button.Padding = new Padding(Spacing.SM, Spacing.XS, Spacing.SM, Spacing.XS);
        button.Cursor = Cursors.Hand;
        
        // ホバー効果
        button.MouseEnter += (s, e) => button.BackColor = ColorScheme.Primary.Dark;
        button.MouseLeave += (s, e) => button.BackColor = ColorScheme.Primary.Main;
    }
    
    public static void ApplySecondaryStyle(Button button)
    {
        button.BackColor = Color.White;
        button.ForeColor = ColorScheme.Primary.Main;
        button.FlatStyle = FlatStyle.Flat;
        button.FlatAppearance.BorderSize = 1;
        button.FlatAppearance.BorderColor = ColorScheme.Primary.Main;
        button.Font = Typography.Special.Button;
        button.Padding = new Padding(Spacing.SM, Spacing.XS, Spacing.SM, Spacing.XS);
        button.Cursor = Cursors.Hand;
    }
    
    public static void ApplyDangerStyle(Button button)
    {
        button.BackColor = ColorScheme.Semantic.Error;
        button.ForeColor = Color.White;
        button.FlatStyle = FlatStyle.Flat;
        button.FlatAppearance.BorderSize = 0;
        button.Font = Typography.Special.Button;
        button.Padding = new Padding(Spacing.SM, Spacing.XS, Spacing.SM, Spacing.XS);
        button.Cursor = Cursors.Hand;
    }
}
```

### フォームレイアウト
```csharp
public static class FormLayouts
{
    public static TableLayoutPanel CreateFormLayout(int labelWidth = 120)
    {
        var layout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 2,
            RowCount = 0,
            Padding = new Padding(Spacing.MD),
            AutoSize = true,
            AutoSizeMode = AutoSizeMode.GrowAndShrink
        };
        
        // カラム設定
        layout.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, labelWidth));
        layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        
        return layout;
    }
    
    public static void AddFormField(
        TableLayoutPanel layout, 
        string labelText, 
        Control inputControl, 
        bool required = false)
    {
        var rowIndex = layout.RowCount;
        layout.RowCount++;
        
        // ラベル
        var label = new Label
        {
            Text = required ? $"{labelText} *" : labelText,
            Font = Typography.Body.Normal,
            TextAlign = ContentAlignment.MiddleRight,
            Dock = DockStyle.Fill
        };
        
        if (required)
        {
            label.ForeColor = ColorScheme.Semantic.Error;
        }
        
        // 入力コントロール
        inputControl.Dock = DockStyle.Fill;
        inputControl.Font = Typography.Body.Normal;
        
        layout.Controls.Add(label, 0, rowIndex);
        layout.Controls.Add(inputControl, 1, rowIndex);
        
        // 行スタイル
        layout.RowStyles.Add(new RowStyle(SizeType.AutoSize));
    }
}
```

## 4. アイコンシステム

### アイコンセット
```csharp
public static class Icons
{
    private static readonly string IconBasePath = @"Resources\Icons\";
    
    public static class Actions
    {
        public static Image Add => GetIcon("add.png");
        public static Image Edit => GetIcon("edit.png");
        public static Image Delete => GetIcon("delete.png");
        public static Image Save => GetIcon("save.png");
        public static Image Cancel => GetIcon("cancel.png");
        public static Image Refresh => GetIcon("refresh.png");
        public static Image Search => GetIcon("search.png");
        public static Image Print => GetIcon("print.png");
        public static Image Export => GetIcon("export.png");
    }
    
    public static class Navigation
    {
        public static Image Back => GetIcon("back.png");
        public static Image Forward => GetIcon("forward.png");
        public static Image Home => GetIcon("home.png");
        public static Image Menu => GetIcon("menu.png");
    }
    
    public static class Status
    {
        public static Image Success => GetIcon("success.png");
        public static Image Warning => GetIcon("warning.png");
        public static Image Error => GetIcon("error.png");
        public static Image Info => GetIcon("info.png");
        public static Image Loading => GetIcon("loading.gif");
    }
    
    private static Image GetIcon(string fileName)
    {
        var path = Path.Combine(IconBasePath, fileName);
        return File.Exists(path) ? Image.FromFile(path) : null;
    }
}
```

## 5. レイアウトグリッドシステム

### グリッドレイアウト
```csharp
public class GridLayoutManager
{
    private readonly int _columns;
    private readonly int _gutter;
    private readonly Control _container;
    
    public GridLayoutManager(Control container, int columns = 12, int gutter = 16)
    {
        _container = container;
        _columns = columns;
        _gutter = gutter;
    }
    
    public void AddControl(Control control, int columnStart, int columnSpan)
    {
        var containerWidth = _container.ClientSize.Width - (_gutter * (_columns + 1));
        var columnWidth = containerWidth / _columns;
        
        var x = _gutter + (columnStart - 1) * (columnWidth + _gutter);
        var width = (columnWidth * columnSpan) + (_gutter * (columnSpan - 1));
        
        control.Location = new Point(x, GetNextY());
        control.Width = width;
        
        _container.Controls.Add(control);
    }
    
    private int GetNextY()
    {
        if (_container.Controls.Count == 0)
            return _gutter;
        
        var lastControl = _container.Controls[_container.Controls.Count - 1];
        return lastControl.Bottom + _gutter;
    }
}
```

## 6. アニメーションとトランジション

### トランジション効果
```csharp
public static class Animations
{
    public static async Task FadeIn(Control control, int duration = 300)
    {
        control.Visible = true;
        var steps = duration / 10;
        var increment = 1.0 / steps;
        
        for (double opacity = 0; opacity <= 1; opacity += increment)
        {
            if (control is Form form)
                form.Opacity = opacity;
            
            await Task.Delay(10);
        }
    }
    
    public static async Task SlideIn(Control control, Direction direction, int duration = 300)
    {
        var targetLocation = control.Location;
        var startLocation = GetStartLocation(control, direction);
        
        control.Location = startLocation;
        control.Visible = true;
        
        var steps = duration / 10;
        var incrementX = (targetLocation.X - startLocation.X) / (double)steps;
        var incrementY = (targetLocation.Y - startLocation.Y) / (double)steps;
        
        for (int i = 0; i < steps; i++)
        {
            control.Location = new Point(
                startLocation.X + (int)(incrementX * i),
                startLocation.Y + (int)(incrementY * i)
            );
            
            await Task.Delay(10);
        }
        
        control.Location = targetLocation;
    }
}
```

## 7. テーマシステム

### テーマ管理
```csharp
public interface ITheme
{
    ColorScheme Colors { get; }
    Typography Fonts { get; }
    Spacing Spacing { get; }
    string Name { get; }
}

public class ThemeManager
{
    private static ITheme _currentTheme;
    private static readonly Dictionary<string, ITheme> _themes = new Dictionary<string, ITheme>();
    
    static ThemeManager()
    {
        RegisterTheme(new LightTheme());
        RegisterTheme(new DarkTheme());
        RegisterTheme(new HighContrastTheme());
        
        _currentTheme = _themes["Light"];
    }
    
    public static void RegisterTheme(ITheme theme)
    {
        _themes[theme.Name] = theme;
    }
    
    public static void ApplyTheme(string themeName)
    {
        if (_themes.TryGetValue(themeName, out var theme))
        {
            _currentTheme = theme;
            OnThemeChanged?.Invoke(theme);
        }
    }
    
    public static event Action<ITheme> OnThemeChanged;
    
    public static ITheme Current => _currentTheme;
}
```

## 8. アクセシビリティガイドライン

### キーボードナビゲーション
```csharp
public static class AccessibilityHelper
{
    public static void SetupKeyboardNavigation(Form form)
    {
        // タブオーダーの自動設定
        var controls = GetAllControls(form)
            .Where(c => c.TabStop)
            .OrderBy(c => c.Top)
            .ThenBy(c => c.Left)
            .ToList();
        
        for (int i = 0; i < controls.Count; i++)
        {
            controls[i].TabIndex = i;
        }
        
        // アクセスキーの設定
        SetupAccessKeys(form);
    }
    
    private static void SetupAccessKeys(Form form)
    {
        foreach (var button in GetAllControls(form).OfType<Button>())
        {
            if (!button.Text.Contains("&"))
            {
                // 最初の文字をアクセスキーに
                button.Text = "&" + button.Text;
            }
        }
    }
    
    public static void AnnounceToScreenReader(string message)
    {
        // スクリーンリーダー対応
        if (SystemInformation.ScreenReaderPresent)
        {
            // Windows Narrator API を使用
            // 実装省略
        }
    }
}
```

このデザインシステムにより、一貫性があり、使いやすく、保守性の高いWindows Formsアプリケーションの構築が可能になります。