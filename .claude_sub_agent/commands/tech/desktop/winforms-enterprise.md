# /winforms-enterprise - WinForms エンタープライズ開発専用コマンド

## 概要
Windows Forms を使用した業務アプリケーション開発に特化した包括的な最適化コマンドです。MDI、高度なデータバインディング、印刷機能、サードパーティコントロール統合を完全サポートします。

## 使用方法
```bash
/winforms-enterprise [feature] [action] [options]

# 使用例
/winforms-enterprise mdi create --ribbon-interface
/winforms-enterprise databinding setup --complex-scenarios
/winforms-enterprise printing design --report-builder
/winforms-enterprise controls optimize --devexpress
/winforms-enterprise validation implement --enterprise-rules
```

## WinForms エンタープライズ専用機能

### 1. MDIアプリケーションとリボンインターフェース
```csharp
// UI/MdiRibbonApplication.cs
using System;
using System.Windows.Forms;
using System.Drawing;
using DevExpress.XtraBars.Ribbon;

public class EnterpriseMdiApplication : RibbonForm
{
    private RibbonControl ribbonControl;
    private RibbonStatusBar ribbonStatusBar;
    private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager mdiManager;
    
    public EnterpriseMdiApplication()
    {
        InitializeMdiEnvironment();
        InitializeRibbonInterface();
        ConfigureWindowManagement();
    }
    
    private void InitializeMdiEnvironment()
    {
        this.IsMdiContainer = true;
        this.WindowState = FormWindowState.Maximized;
        
        // MDI マネージャー設定
        mdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager();
        mdiManager.MdiParent = this;
        mdiManager.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
        mdiManager.ClosePageButtonShowMode = 
            DevExpress.XtraTab.ClosePageButtonShowMode.InActiveTabPageHeader;
        
        // MDI 子ウィンドウイベント
        mdiManager.PageAdded += (s, e) => UpdateWindowMenu();
        mdiManager.PageRemoved += (s, e) => UpdateWindowMenu();
    }
    
    private void InitializeRibbonInterface()
    {
        ribbonControl = new RibbonControl();
        
        // ホームページ
        var homePage = new RibbonPage("ホーム");
        var fileGroup = new RibbonPageGroup("ファイル");
        
        // ファイル操作ボタン
        var newButton = new BarButtonItem();
        newButton.Caption = "新規作成";
        newButton.LargeGlyph = Resources.NewDocument32;
        newButton.ItemClick += (s, e) => CreateNewDocument();
        
        fileGroup.ItemLinks.Add(newButton);
        homePage.Groups.Add(fileGroup);
        ribbonControl.Pages.Add(homePage);
        
        // クイックアクセスツールバー
        ribbonControl.Toolbar.ItemLinks.Add(newButton);
        
        this.Ribbon = ribbonControl;
    }
    
    // 子ウィンドウ管理
    public class MdiChildManager
    {
        private readonly Dictionary<string, Form> _openForms = new Dictionary<string, Form>();
        private readonly Stack<Form> _formHistory = new Stack<Form>();
        
        public T OpenOrActivate<T>(string key, Func<T> factory) where T : Form
        {
            if (_openForms.ContainsKey(key))
            {
                var existingForm = _openForms[key];
                existingForm.Activate();
                return (T)existingForm;
            }
            
            var newForm = factory();
            newForm.MdiParent = Application.OpenForms[0];
            newForm.FormClosed += (s, e) => _openForms.Remove(key);
            
            _openForms[key] = newForm;
            _formHistory.Push(newForm);
            
            newForm.Show();
            return newForm;
        }
        
        public void CascadeWindows()
        {
            Application.OpenForms[0].LayoutMdi(MdiLayout.Cascade);
        }
        
        public void TileHorizontal()
        {
            Application.OpenForms[0].LayoutMdi(MdiLayout.TileHorizontal);
        }
        
        public void CloseAll()
        {
            foreach (var form in _openForms.Values.ToList())
            {
                form.Close();
            }
        }
    }
}

// 高度なドッキングインターフェース
public class DockingInterfaceManager
{
    private readonly DevExpress.XtraBars.Docking.DockManager dockManager;
    private readonly Dictionary<string, DockPanel> panels;
    
    public DockingInterfaceManager(Control parentControl)
    {
        dockManager = new DockManager();
        dockManager.Form = parentControl;
        panels = new Dictionary<string, DockPanel>();
        
        CreateDefaultLayout();
    }
    
    private void CreateDefaultLayout()
    {
        // ナビゲーションパネル
        var navPanel = dockManager.AddPanel(DockingStyle.Left);
        navPanel.Text = "ナビゲーション";
        navPanel.Width = 250;
        panels["Navigation"] = navPanel;
        
        // プロパティパネル
        var propPanel = dockManager.AddPanel(DockingStyle.Right);
        propPanel.Text = "プロパティ";
        propPanel.Width = 300;
        panels["Properties"] = propPanel;
        
        // 出力パネル
        var outputPanel = dockManager.AddPanel(DockingStyle.Bottom);
        outputPanel.Text = "出力";
        outputPanel.Height = 200;
        outputPanel.Options.ShowCloseButton = false;
        panels["Output"] = outputPanel;
        
        // レイアウト保存/復元
        dockManager.SaveLayoutToXml("default_layout.xml");
    }
    
    public void SaveLayout(string fileName)
    {
        dockManager.SaveLayoutToXml(fileName);
    }
    
    public void RestoreLayout(string fileName)
    {
        if (File.Exists(fileName))
        {
            dockManager.RestoreLayoutFromXml(fileName);
        }
    }
}
```

### 2. 高度なデータバインディングとグリッド
```csharp
// DataBinding/EnterpriseDataBinding.cs
using System;
using System.ComponentModel;
using System.Windows.Forms;
using DevExpress.XtraGrid;
using DevExpress.XtraGrid.Views.Grid;

public class EnterpriseDataBindingManager
{
    // 複雑なマスター詳細バインディング
    public class MasterDetailBinding
    {
        private readonly GridControl masterGrid;
        private readonly GridControl detailGrid;
        private readonly BindingSource masterBindingSource;
        private readonly BindingSource detailBindingSource;
        
        public MasterDetailBinding()
        {
            masterBindingSource = new BindingSource();
            detailBindingSource = new BindingSource();
            
            // マスターグリッド設定
            masterGrid = new GridControl();
            masterGrid.DataSource = masterBindingSource;
            
            var masterView = masterGrid.MainView as GridView;
            masterView.OptionsView.ShowAutoFilterRow = true;
            masterView.OptionsView.ShowGroupPanel = true;
            masterView.OptionsBehavior.AutoExpandAllGroups = true;
            
            // 詳細グリッド設定
            detailGrid = new GridControl();
            detailGrid.DataSource = detailBindingSource;
            
            // リレーション設定
            masterBindingSource.CurrentChanged += (s, e) =>
            {
                UpdateDetailData();
            };
        }
        
        private void UpdateDetailData()
        {
            var currentMaster = masterBindingSource.Current;
            if (currentMaster != null)
            {
                // 動的フィルタリング
                var masterId = currentMaster.GetType()
                    .GetProperty("Id")?.GetValue(currentMaster);
                
                detailBindingSource.Filter = $"MasterId = {masterId}";
            }
        }
        
        // 仮想モード対応
        public void EnableVirtualMode(int pageSize = 100)
        {
            var view = masterGrid.MainView as GridView;
            view.OptionsView.EnableAppearanceEvenRow = true;
            view.OptionsView.EnableAppearanceOddRow = true;
            
            // サーバーモードデータソース
            var serverModeSource = new DevExpress.Data.Linq.LinqServerModeSource();
            serverModeSource.QueryableSource = GetQueryableDataSource();
            masterGrid.DataSource = serverModeSource;
        }
    }
    
    // カスタムバインディングコンバーター
    public class CustomBindingConverter : TypeConverter
    {
        public override bool CanConvertFrom(ITypeDescriptorContext context, Type sourceType)
        {
            return sourceType == typeof(string) || 
                   base.CanConvertFrom(context, sourceType);
        }
        
        public override object ConvertFrom(ITypeDescriptorContext context, 
            CultureInfo culture, object value)
        {
            if (value is string stringValue)
            {
                // カスタム変換ロジック
                return ParseCustomFormat(stringValue);
            }
            
            return base.ConvertFrom(context, culture, value);
        }
        
        private object ParseCustomFormat(string value)
        {
            // 業務固有のフォーマット解析
            if (value.StartsWith("¥"))
            {
                return decimal.Parse(value.Replace("¥", "").Replace(",", ""));
            }
            
            return value;
        }
    }
    
    // 双方向データバインディング
    public class TwoWayDataBinding<T> where T : INotifyPropertyChanged
    {
        private readonly Control control;
        private readonly T dataSource;
        private readonly Dictionary<string, Binding> bindings;
        
        public TwoWayDataBinding(Control control, T dataSource)
        {
            this.control = control;
            this.dataSource = dataSource;
            this.bindings = new Dictionary<string, Binding>();
            
            // 自動バインディング設定
            AutoBindProperties();
        }
        
        private void AutoBindProperties()
        {
            var dataProperties = typeof(T).GetProperties();
            
            foreach (Control child in control.Controls)
            {
                var controlProperty = GetBindableProperty(child);
                if (controlProperty != null)
                {
                    var matchingDataProperty = dataProperties
                        .FirstOrDefault(p => p.Name == child.Name.Replace("txt", "")
                                                             .Replace("cbo", "")
                                                             .Replace("chk", ""));
                    
                    if (matchingDataProperty != null)
                    {
                        var binding = new Binding(
                            controlProperty,
                            dataSource,
                            matchingDataProperty.Name,
                            true,
                            DataSourceUpdateMode.OnPropertyChanged);
                        
                        // 検証イベント追加
                        binding.Parse += ValidateBinding;
                        binding.Format += FormatBinding;
                        
                        child.DataBindings.Add(binding);
                        bindings[child.Name] = binding;
                    }
                }
            }
        }
        
        private string GetBindableProperty(Control control)
        {
            if (control is TextBox) return "Text";
            if (control is ComboBox) return "SelectedValue";
            if (control is CheckBox) return "Checked";
            if (control is DateTimePicker) return "Value";
            return null;
        }
        
        private void ValidateBinding(object sender, ConvertEventArgs e)
        {
            // バインディング検証
            var binding = sender as Binding;
            if (binding != null)
            {
                // ビジネスルール検証
                ValidateBusinessRules(binding.PropertyName, e.Value);
            }
        }
        
        private void FormatBinding(object sender, ConvertEventArgs e)
        {
            // 表示フォーマット
            if (e.Value is decimal)
            {
                e.Value = ((decimal)e.Value).ToString("C");
            }
            else if (e.Value is DateTime)
            {
                e.Value = ((DateTime)e.Value).ToString("yyyy/MM/dd");
            }
        }
    }
}
```

### 3. 印刷とレポート機能
```csharp
// Printing/EnterprisePrinting.cs
using System;
using System.Drawing;
using System.Drawing.Printing;
using System.Windows.Forms;

public class EnterprisePrintingManager
{
    private readonly PrintDocument printDocument;
    private readonly PrintPreviewDialog previewDialog;
    private readonly PageSetupDialog pageSetupDialog;
    private int currentPage;
    private readonly List<ReportPage> pages;
    
    public EnterprisePrintingManager()
    {
        printDocument = new PrintDocument();
        printDocument.PrintPage += PrintDocument_PrintPage;
        printDocument.BeginPrint += PrintDocument_BeginPrint;
        
        previewDialog = new PrintPreviewDialog
        {
            Document = printDocument,
            WindowState = FormWindowState.Maximized
        };
        
        pageSetupDialog = new PageSetupDialog
        {
            Document = printDocument
        };
        
        pages = new List<ReportPage>();
    }
    
    // 帳票デザイナー
    public class ReportDesigner
    {
        private readonly Panel designSurface;
        private readonly List<ReportElement> elements;
        private ReportElement selectedElement;
        
        public ReportDesigner()
        {
            designSurface = new Panel
            {
                BackColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };
            
            elements = new List<ReportElement>();
            
            // ドラッグ&ドロップ対応
            designSurface.AllowDrop = true;
            designSurface.DragEnter += DesignSurface_DragEnter;
            designSurface.DragDrop += DesignSurface_DragDrop;
            designSurface.MouseDown += DesignSurface_MouseDown;
            designSurface.MouseMove += DesignSurface_MouseMove;
            designSurface.MouseUp += DesignSurface_MouseUp;
        }
        
        public void AddElement(ReportElementType type, Point location)
        {
            ReportElement element = null;
            
            switch (type)
            {
                case ReportElementType.Label:
                    element = new LabelElement
                    {
                        Text = "ラベル",
                        Font = new Font("MS Gothic", 10),
                        Location = location
                    };
                    break;
                    
                case ReportElementType.Table:
                    element = new TableElement
                    {
                        Columns = 5,
                        Rows = 10,
                        Location = location
                    };
                    break;
                    
                case ReportElementType.Barcode:
                    element = new BarcodeElement
                    {
                        BarcodeType = BarcodeType.Code128,
                        Value = "123456789",
                        Location = location
                    };
                    break;
            }
            
            if (element != null)
            {
                elements.Add(element);
                designSurface.Invalidate();
            }
        }
        
        public void ExportToExcel(string fileName)
        {
            // Excel エクスポート
            using (var package = new ExcelPackage())
            {
                var worksheet = package.Workbook.Worksheets.Add("Report");
                
                foreach (var element in elements)
                {
                    if (element is TableElement table)
                    {
                        ExportTableToExcel(worksheet, table);
                    }
                }
                
                package.SaveAs(new FileInfo(fileName));
            }
        }
    }
    
    // 高度な印刷プレビュー
    public class AdvancedPrintPreview : Form
    {
        private readonly PrintPreviewControl previewControl;
        private readonly ToolStrip toolStrip;
        private int currentZoom = 100;
        
        public AdvancedPrintPreview(PrintDocument document)
        {
            previewControl = new PrintPreviewControl
            {
                Document = document,
                Dock = DockStyle.Fill,
                Zoom = 1.0
            };
            
            toolStrip = new ToolStrip();
            
            // ズームコントロール
            var zoomInButton = new ToolStripButton("拡大");
            zoomInButton.Click += (s, e) =>
            {
                currentZoom = Math.Min(currentZoom + 25, 500);
                previewControl.Zoom = currentZoom / 100.0;
            };
            
            var zoomOutButton = new ToolStripButton("縮小");
            zoomOutButton.Click += (s, e) =>
            {
                currentZoom = Math.Max(currentZoom - 25, 10);
                previewControl.Zoom = currentZoom / 100.0;
            };
            
            var fitToPageButton = new ToolStripButton("ページに合わせる");
            fitToPageButton.Click += (s, e) =>
            {
                previewControl.AutoZoom = true;
            };
            
            toolStrip.Items.AddRange(new ToolStripItem[]
            {
                zoomInButton,
                zoomOutButton,
                new ToolStripSeparator(),
                fitToPageButton
            });
            
            Controls.Add(previewControl);
            Controls.Add(toolStrip);
        }
    }
    
    // バーコード生成
    public class BarcodeGenerator
    {
        public Bitmap GenerateBarcode(string data, BarcodeType type, int width, int height)
        {
            var barcode = new Bitmap(width, height);
            
            using (var graphics = Graphics.FromImage(barcode))
            {
                graphics.Clear(Color.White);
                
                switch (type)
                {
                    case BarcodeType.Code128:
                        DrawCode128(graphics, data, width, height);
                        break;
                        
                    case BarcodeType.QRCode:
                        DrawQRCode(graphics, data, width, height);
                        break;
                        
                    case BarcodeType.Code39:
                        DrawCode39(graphics, data, width, height);
                        break;
                }
            }
            
            return barcode;
        }
        
        private void DrawCode128(Graphics g, string data, int width, int height)
        {
            // Code128 バーコード描画ロジック
            var barWidth = width / (data.Length * 11);
            var x = 0;
            
            foreach (char c in data)
            {
                var pattern = GetCode128Pattern(c);
                
                for (int i = 0; i < pattern.Length; i++)
                {
                    if (pattern[i] == '1')
                    {
                        g.FillRectangle(Brushes.Black, x, 0, barWidth, height - 20);
                    }
                    x += barWidth;
                }
            }
            
            // テキスト描画
            var font = new Font("Arial", 10);
            var textSize = g.MeasureString(data, font);
            g.DrawString(data, font, Brushes.Black, 
                (width - textSize.Width) / 2, height - 20);
        }
    }
}
```

### 4. エンタープライズ検証とルールエンジン
```csharp
// Validation/EnterpriseValidation.cs
using System;
using System.ComponentModel.DataAnnotations;
using System.Windows.Forms;

public class EnterpriseValidationFramework
{
    // ルールベース検証エンジン
    public class ValidationRuleEngine
    {
        private readonly List<IValidationRule> rules;
        private readonly ErrorProvider errorProvider;
        
        public ValidationRuleEngine(Form form)
        {
            rules = new List<IValidationRule>();
            errorProvider = new ErrorProvider();
            errorProvider.ContainerControl = form;
            
            // デフォルトルール登録
            RegisterDefaultRules();
        }
        
        private void RegisterDefaultRules()
        {
            // 必須入力ルール
            AddRule(new RequiredFieldRule());
            
            // 形式検証ルール
            AddRule(new EmailFormatRule());
            AddRule(new PhoneNumberRule());
            AddRule(new PostalCodeRule());
            
            // ビジネスルール
            AddRule(new CreditLimitRule());
            AddRule(new InventoryCheckRule());
            AddRule(new DuplicateCheckRule());
        }
        
        public ValidationResult ValidateControl(Control control)
        {
            var results = new List<ValidationError>();
            
            foreach (var rule in rules)
            {
                if (rule.AppliesTo(control))
                {
                    var result = rule.Validate(control);
                    if (!result.IsValid)
                    {
                        results.Add(new ValidationError
                        {
                            Control = control,
                            Message = result.ErrorMessage,
                            Severity = result.Severity
                        });
                    }
                }
            }
            
            // エラー表示
            if (results.Any())
            {
                var error = results.OrderByDescending(r => r.Severity).First();
                errorProvider.SetError(control, error.Message);
                
                // エラーアイコンのカスタマイズ
                switch (error.Severity)
                {
                    case ValidationSeverity.Error:
                        errorProvider.Icon = SystemIcons.Error.ToBitmap();
                        break;
                    case ValidationSeverity.Warning:
                        errorProvider.Icon = SystemIcons.Warning.ToBitmap();
                        break;
                }
            }
            else
            {
                errorProvider.SetError(control, string.Empty);
            }
            
            return new ValidationResult
            {
                IsValid = !results.Any(),
                Errors = results
            };
        }
    }
    
    // 複合検証ルール
    public class CompositeValidationRule : IValidationRule
    {
        private readonly List<IValidationRule> rules;
        private readonly LogicalOperator operator;
        
        public CompositeValidationRule(LogicalOperator op)
        {
            rules = new List<IValidationRule>();
            this.operator = op;
        }
        
        public ValidationResult Validate(Control control)
        {
            var results = rules.Select(r => r.Validate(control)).ToList();
            
            bool isValid = operator == LogicalOperator.And
                ? results.All(r => r.IsValid)
                : results.Any(r => r.IsValid);
            
            return new ValidationResult
            {
                IsValid = isValid,
                ErrorMessage = isValid ? null : 
                    string.Join(", ", results.Where(r => !r.IsValid)
                                            .Select(r => r.ErrorMessage))
            };
        }
    }
    
    // 非同期検証
    public class AsyncValidation
    {
        public async Task<ValidationResult> ValidateAsync(Control control)
        {
            var validationTasks = new List<Task<ValidationResult>>();
            
            // データベース重複チェック
            validationTasks.Add(CheckDatabaseDuplicateAsync(control.Text));
            
            // Web API検証
            validationTasks.Add(ValidateWithWebApiAsync(control.Text));
            
            // 外部サービス検証
            validationTasks.Add(ValidateWithExternalServiceAsync(control.Text));
            
            var results = await Task.WhenAll(validationTasks);
            
            return new ValidationResult
            {
                IsValid = results.All(r => r.IsValid),
                ErrorMessage = string.Join(", ", 
                    results.Where(r => !r.IsValid).Select(r => r.ErrorMessage))
            };
        }
    }
}

// カスタムコントロール検証属性
[AttributeUsage(AttributeTargets.Property)]
public class CustomValidationAttribute : ValidationAttribute
{
    private readonly string validationMethod;
    
    public CustomValidationAttribute(string methodName)
    {
        validationMethod = methodName;
    }
    
    protected override ValidationResult IsValid(object value, ValidationContext context)
    {
        var method = context.ObjectType.GetMethod(validationMethod);
        
        if (method != null)
        {
            var result = method.Invoke(context.ObjectInstance, new[] { value });
            
            if (result is bool isValid && !isValid)
            {
                return new ValidationResult(ErrorMessage ?? "検証エラー");
            }
        }
        
        return ValidationResult.Success;
    }
}
```

## サードパーティコントロール統合
```csharp
// ThirdParty/DevExpressIntegration.cs
public class DevExpressOptimization
{
    public static void OptimizeDevExpressControls()
    {
        // スキンの最適化
        DevExpress.UserSkins.BonusSkins.Register();
        DevExpress.Skins.SkinManager.EnableFormSkins();
        DevExpress.LookAndFeel.UserLookAndFeel.Default.SetSkinStyle("Office 2019 Colorful");
        
        // パフォーマンス設定
        DevExpress.Utils.AppearanceObject.DefaultFont = 
            new Font("Segoe UI", 9F, FontStyle.Regular);
        
        // グリッドのグローバル設定
        DevExpress.XtraGrid.Views.Grid.GridView.ColumnAutoWidthEnabled = false;
        
        // エディターのグローバル設定
        DevExpress.XtraEditors.WindowsFormsSettings.AnimationMode = 
            DevExpress.XtraEditors.AnimationMode.DisableAll;
    }
}
```

## 出力レポート
```markdown
# WinForms エンタープライズ 最適化レポート

## 実施項目
✅ MDI環境: リボンインターフェース実装
✅ データバインディング: 双方向・仮想モード対応
✅ 印刷機能: 帳票デザイナー・バーコード対応
✅ 検証フレームワーク: ルールエンジン実装
✅ サードパーティ: DevExpress最適化

## パフォーマンス改善
- フォーム起動: 2秒 → 0.5秒 (75%改善)
- グリッド表示: 100万件を2秒で表示
- 印刷プレビュー: 即座に表示
- メモリ使用量: 30%削減

## 機能強化
- MDI子ウィンドウ: 無制限対応
- レポート形式: Excel/PDF/HTML出力
- バーコード: 10種類以上対応
- 検証ルール: 50種類以上実装

## 推奨事項
1. WPFへの段階的移行検討
2. クラウド連携機能追加
3. タッチ操作対応
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: WinForms エンタープライズ業務アプリケーション開発

---
*このコマンドはWinFormsエンタープライズ業務アプリケーション開発に特化しています。*