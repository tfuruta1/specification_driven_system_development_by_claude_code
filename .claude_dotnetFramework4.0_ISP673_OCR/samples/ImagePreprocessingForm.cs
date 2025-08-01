using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Windows.Forms;
using GloryOcr4Lib;
using ISP673_OCRApp.Core.ImageProcessing;

namespace ISP673_OCRApp.Forms
{
    /// <summary>
    /// OCR前処理画像調整フォーム
    /// </summary>
    public partial class ImagePreprocessingForm : Form
    {
        #region Fields
        
        private ImagePreprocessor _preprocessor;
        private Bitmap _originalImage;
        private Bitmap _processedImage;
        private BackgroundWorker _processingWorker;
        private GlyOcr _gOcr;
        private GlyOcrEx _gOcrEx;
        
        #endregion
        
        #region Constructor
        
        public ImagePreprocessingForm()
        {
            InitializeComponent();
            InitializeBackgroundWorker();
            _preprocessor = new ImagePreprocessor();
            _gOcr = new GlyOcr();
            _gOcrEx = new GlyOcrEx();
        }
        
        #endregion
        
        #region Form Designer Code
        
        private void InitializeComponent()
        {
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.splitContainer2 = new System.Windows.Forms.SplitContainer();
            this.groupBoxOriginal = new System.Windows.Forms.GroupBox();
            this.pictureBoxOriginal = new System.Windows.Forms.PictureBox();
            this.groupBoxProcessed = new System.Windows.Forms.GroupBox();
            this.pictureBoxProcessed = new System.Windows.Forms.PictureBox();
            this.groupBoxControls = new System.Windows.Forms.GroupBox();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabPageBackground = new System.Windows.Forms.TabPage();
            this.chkBackgroundWhite = new System.Windows.Forms.CheckBox();
            this.trackBarBackground = new System.Windows.Forms.TrackBar();
            this.lblBackgroundValue = new System.Windows.Forms.Label();
            this.tabPageContrast = new System.Windows.Forms.TabPage();
            this.chkContrast = new System.Windows.Forms.CheckBox();
            this.trackBarContrast = new System.Windows.Forms.TrackBar();
            this.lblContrastValue = new System.Windows.Forms.Label();
            this.tabPageLines = new System.Windows.Forms.TabPage();
            this.chkEnhanceLines = new System.Windows.Forms.CheckBox();
            this.numLineThickness = new System.Windows.Forms.NumericUpDown();
            this.lblLineThickness = new System.Windows.Forms.Label();
            this.tabPageText = new System.Windows.Forms.TabPage();
            this.chkEnhanceText = new System.Windows.Forms.CheckBox();
            this.trackBarTextEnhance = new System.Windows.Forms.TrackBar();
            this.lblTextEnhanceValue = new System.Windows.Forms.Label();
            this.tabPageNoise = new System.Windows.Forms.TabPage();
            this.chkRemoveNoise = new System.Windows.Forms.CheckBox();
            this.numNoiseThreshold = new System.Windows.Forms.NumericUpDown();
            this.lblNoiseThreshold = new System.Windows.Forms.Label();
            this.panelButtons = new System.Windows.Forms.Panel();
            this.btnLoadImage = new System.Windows.Forms.Button();
            this.btnApplyPreset = new System.Windows.Forms.Button();
            this.cmbPresets = new System.Windows.Forms.ComboBox();
            this.btnProcess = new System.Windows.Forms.Button();
            this.btnSaveProcessed = new System.Windows.Forms.Button();
            this.btnExecuteOCR = new System.Windows.Forms.Button();
            this.progressBar1 = new System.Windows.Forms.ProgressBar();
            this.statusStrip1 = new System.Windows.Forms.StatusStrip();
            this.toolStripStatusLabel1 = new System.Windows.Forms.ToolStripStatusLabel();
            
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).BeginInit();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer2)).BeginInit();
            this.splitContainer2.Panel1.SuspendLayout();
            this.splitContainer2.Panel2.SuspendLayout();
            this.splitContainer2.SuspendLayout();
            this.groupBoxOriginal.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBoxOriginal)).BeginInit();
            this.groupBoxProcessed.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBoxProcessed)).BeginInit();
            this.groupBoxControls.SuspendLayout();
            this.tabControl1.SuspendLayout();
            this.tabPageBackground.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBarBackground)).BeginInit();
            this.tabPageContrast.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBarContrast)).BeginInit();
            this.tabPageLines.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.numLineThickness)).BeginInit();
            this.tabPageText.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBarTextEnhance)).BeginInit();
            this.tabPageNoise.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.numNoiseThreshold)).BeginInit();
            this.panelButtons.SuspendLayout();
            this.statusStrip1.SuspendLayout();
            this.SuspendLayout();
            
            // Form設定
            this.Text = "ISP-673 OCR 画像前処理";
            this.ClientSize = new System.Drawing.Size(1200, 700);
            this.StartPosition = FormStartPosition.CenterScreen;
            
            // splitContainer1
            this.splitContainer1.Dock = DockStyle.Fill;
            this.splitContainer1.Location = new Point(0, 0);
            this.splitContainer1.Size = new Size(1200, 678);
            this.splitContainer1.SplitterDistance = 900;
            
            // splitContainer2
            this.splitContainer2.Dock = DockStyle.Fill;
            this.splitContainer2.Orientation = Orientation.Horizontal;
            
            // groupBoxOriginal
            this.groupBoxOriginal.Text = "元画像";
            this.groupBoxOriginal.Dock = DockStyle.Fill;
            
            // pictureBoxOriginal
            this.pictureBoxOriginal.Dock = DockStyle.Fill;
            this.pictureBoxOriginal.SizeMode = PictureBoxSizeMode.Zoom;
            this.pictureBoxOriginal.BackColor = Color.White;
            
            // groupBoxProcessed
            this.groupBoxProcessed.Text = "処理後画像";
            this.groupBoxProcessed.Dock = DockStyle.Fill;
            
            // pictureBoxProcessed
            this.pictureBoxProcessed.Dock = DockStyle.Fill;
            this.pictureBoxProcessed.SizeMode = PictureBoxSizeMode.Zoom;
            this.pictureBoxProcessed.BackColor = Color.White;
            
            // groupBoxControls
            this.groupBoxControls.Text = "画像調整設定";
            this.groupBoxControls.Dock = DockStyle.Fill;
            
            // Controls設定
            SetupControls();
            
            // Layout
            this.groupBoxOriginal.Controls.Add(this.pictureBoxOriginal);
            this.groupBoxProcessed.Controls.Add(this.pictureBoxProcessed);
            this.splitContainer2.Panel1.Controls.Add(this.groupBoxOriginal);
            this.splitContainer2.Panel2.Controls.Add(this.groupBoxProcessed);
            this.splitContainer1.Panel1.Controls.Add(this.splitContainer2);
            this.splitContainer1.Panel2.Controls.Add(this.groupBoxControls);
            this.Controls.Add(this.splitContainer1);
            this.Controls.Add(this.statusStrip1);
            
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).EndInit();
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer2)).EndInit();
            this.splitContainer2.Panel1.ResumeLayout(false);
            this.splitContainer2.Panel2.ResumeLayout(false);
            this.splitContainer2.ResumeLayout(false);
            this.groupBoxOriginal.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.pictureBoxOriginal)).EndInit();
            this.groupBoxProcessed.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.pictureBoxProcessed)).EndInit();
            this.groupBoxControls.ResumeLayout(false);
            this.tabControl1.ResumeLayout(false);
            this.tabPageBackground.ResumeLayout(false);
            this.tabPageBackground.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBarBackground)).EndInit();
            this.tabPageContrast.ResumeLayout(false);
            this.tabPageContrast.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBarContrast)).EndInit();
            this.tabPageLines.ResumeLayout(false);
            this.tabPageLines.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.numLineThickness)).EndInit();
            this.tabPageText.ResumeLayout(false);
            this.tabPageText.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBarTextEnhance)).EndInit();
            this.tabPageNoise.ResumeLayout(false);
            this.tabPageNoise.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.numNoiseThreshold)).EndInit();
            this.panelButtons.ResumeLayout(false);
            this.statusStrip1.ResumeLayout(false);
            this.statusStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();
        }
        
        private void SetupControls()
        {
            // TabControl
            this.tabControl1 = new TabControl();
            this.tabControl1.Dock = DockStyle.Fill;
            
            // 背景タブ
            this.tabPageBackground = new TabPage("背景処理");
            this.chkBackgroundWhite = new CheckBox();
            this.chkBackgroundWhite.Text = "背景を白に変換";
            this.chkBackgroundWhite.Checked = true;
            this.chkBackgroundWhite.Location = new Point(10, 10);
            this.chkBackgroundWhite.CheckedChanged += SettingChanged;
            
            this.trackBarBackground = new TrackBar();
            this.trackBarBackground.Minimum = 0;
            this.trackBarBackground.Maximum = 255;
            this.trackBarBackground.Value = 200;
            this.trackBarBackground.Location = new Point(10, 40);
            this.trackBarBackground.Size = new Size(250, 45);
            this.trackBarBackground.ValueChanged += trackBarBackground_ValueChanged;
            
            this.lblBackgroundValue = new Label();
            this.lblBackgroundValue.Text = "閾値: 200";
            this.lblBackgroundValue.Location = new Point(270, 50);
            
            this.tabPageBackground.Controls.Add(this.chkBackgroundWhite);
            this.tabPageBackground.Controls.Add(this.trackBarBackground);
            this.tabPageBackground.Controls.Add(this.lblBackgroundValue);
            
            // 他のタブも同様に設定...
            
            this.tabControl1.TabPages.Add(this.tabPageBackground);
            // 他のタブページも追加...
            
            // ボタンパネル
            this.panelButtons = new Panel();
            this.panelButtons.Dock = DockStyle.Top;
            this.panelButtons.Height = 80;
            
            this.btnLoadImage = new Button();
            this.btnLoadImage.Text = "画像読み込み";
            this.btnLoadImage.Location = new Point(10, 10);
            this.btnLoadImage.Size = new Size(100, 30);
            this.btnLoadImage.Click += btnLoadImage_Click;
            
            this.btnProcess = new Button();
            this.btnProcess.Text = "処理実行";
            this.btnProcess.Location = new Point(120, 10);
            this.btnProcess.Size = new Size(100, 30);
            this.btnProcess.Enabled = false;
            this.btnProcess.Click += btnProcess_Click;
            
            this.btnExecuteOCR = new Button();
            this.btnExecuteOCR.Text = "OCR実行";
            this.btnExecuteOCR.Location = new Point(10, 45);
            this.btnExecuteOCR.Size = new Size(100, 30);
            this.btnExecuteOCR.Enabled = false;
            this.btnExecuteOCR.Click += btnExecuteOCR_Click;
            
            this.panelButtons.Controls.Add(this.btnLoadImage);
            this.panelButtons.Controls.Add(this.btnProcess);
            this.panelButtons.Controls.Add(this.btnExecuteOCR);
            
            this.groupBoxControls.Controls.Add(this.tabControl1);
            this.groupBoxControls.Controls.Add(this.panelButtons);
            
            // StatusStrip
            this.statusStrip1 = new StatusStrip();
            this.toolStripStatusLabel1 = new ToolStripStatusLabel();
            this.toolStripStatusLabel1.Text = "準備完了";
            this.statusStrip1.Items.Add(this.toolStripStatusLabel1);
        }
        
        #endregion
        
        #region Event Handlers
        
        private void btnLoadImage_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog ofd = new OpenFileDialog())
            {
                ofd.Filter = "画像ファイル|*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.tif|すべてのファイル|*.*";
                ofd.Title = "OCR対象画像を選択";
                
                if (ofd.ShowDialog() == DialogResult.OK)
                {
                    try
                    {
                        _originalImage?.Dispose();
                        _originalImage = new Bitmap(ofd.FileName);
                        pictureBoxOriginal.Image = _originalImage;
                        
                        btnProcess.Enabled = true;
                        toolStripStatusLabel1.Text = $"画像読み込み完了: {Path.GetFileName(ofd.FileName)}";
                        
                        // 自動的に処理を実行
                        if (MessageBox.Show("画像を自動的に前処理しますか？", "確認", 
                            MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
                        {
                            ProcessImage();
                        }
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"画像の読み込みに失敗しました: {ex.Message}", 
                            "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
            }
        }
        
        private void btnProcess_Click(object sender, EventArgs e)
        {
            ProcessImage();
        }
        
        private void ProcessImage()
        {
            if (_originalImage == null) return;
            
            if (_processingWorker.IsBusy)
            {
                MessageBox.Show("処理中です。しばらくお待ちください。", 
                    "情報", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }
            
            // UIから設定を取得
            var options = GetPreprocessingOptions();
            
            // プログレスバー表示
            progressBar1.Style = ProgressBarStyle.Marquee;
            btnProcess.Enabled = false;
            toolStripStatusLabel1.Text = "画像処理中...";
            
            // BackgroundWorkerで非同期処理
            _processingWorker.RunWorkerAsync(options);
        }
        
        private void btnExecuteOCR_Click(object sender, EventArgs e)
        {
            if (_processedImage == null)
            {
                MessageBox.Show("処理済み画像がありません。", 
                    "エラー", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            
            ExecuteOCR();
        }
        
        private void SettingChanged(object sender, EventArgs e)
        {
            // 設定が変更されたら自動的に再処理
            if (_originalImage != null && chkAutoProcess.Checked)
            {
                ProcessImage();
            }
        }
        
        private void trackBarBackground_ValueChanged(object sender, EventArgs e)
        {
            lblBackgroundValue.Text = $"閾値: {trackBarBackground.Value}";
            SettingChanged(sender, e);
        }
        
        #endregion
        
        #region BackgroundWorker
        
        private void InitializeBackgroundWorker()
        {
            _processingWorker = new BackgroundWorker();
            _processingWorker.DoWork += ProcessingWorker_DoWork;
            _processingWorker.RunWorkerCompleted += ProcessingWorker_RunWorkerCompleted;
        }
        
        private void ProcessingWorker_DoWork(object sender, DoWorkEventArgs e)
        {
            var options = (PreprocessingOptions)e.Argument;
            
            try
            {
                e.Result = _preprocessor.PreprocessImage(_originalImage, options);
            }
            catch (Exception ex)
            {
                e.Result = ex;
            }
        }
        
        private void ProcessingWorker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            progressBar1.Style = ProgressBarStyle.Continuous;
            btnProcess.Enabled = true;
            
            if (e.Result is Exception)
            {
                var ex = (Exception)e.Result;
                MessageBox.Show($"処理エラー: {ex.Message}", 
                    "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                toolStripStatusLabel1.Text = "処理エラー";
                return;
            }
            
            _processedImage?.Dispose();
            _processedImage = (Bitmap)e.Result;
            pictureBoxProcessed.Image = _processedImage;
            
            btnExecuteOCR.Enabled = true;
            toolStripStatusLabel1.Text = "画像処理完了";
        }
        
        #endregion
        
        #region OCR Integration
        
        private void ExecuteOCR()
        {
            try
            {
                // 一時ファイルに保存
                string tempPath = Path.GetTempFileName();
                tempPath = Path.ChangeExtension(tempPath, ".tiff");
                _processedImage.Save(tempPath, ImageFormat.Tiff);
                
                toolStripStatusLabel1.Text = "OCR処理中...";
                
                // OCR実行
                int docId = 0;
                int retVal = _gOcr.RecogDocumentFn(ref docId, tempPath);
                
                if (retVal == 0)
                {
                    // 結果表示
                    ShowOCRResults();
                }
                else
                {
                    MessageBox.Show($"OCR処理エラー: エラーコード {retVal}", 
                        "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
                
                // 一時ファイル削除
                if (File.Exists(tempPath))
                    File.Delete(tempPath);
                    
                toolStripStatusLabel1.Text = "OCR処理完了";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"OCR実行エラー: {ex.Message}", 
                    "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                toolStripStatusLabel1.Text = "OCRエラー";
            }
        }
        
        private void ShowOCRResults()
        {
            // OCR結果を表示する新しいフォームを開く
            using (var resultsForm = new OCRResultsForm(_gOcr))
            {
                resultsForm.ShowDialog(this);
            }
        }
        
        #endregion
        
        #region Helper Methods
        
        private PreprocessingOptions GetPreprocessingOptions()
        {
            return new PreprocessingOptions
            {
                ConvertBackgroundToWhite = chkBackgroundWhite.Checked,
                BackgroundThreshold = trackBarBackground.Value,
                AdjustContrast = chkContrast.Checked,
                ContrastLevel = trackBarContrast.Value,
                EnhanceLines = chkEnhanceLines.Checked,
                LineThickness = (int)numLineThickness.Value,
                EnhanceText = chkEnhanceText.Checked,
                TextEnhancementLevel = trackBarTextEnhance.Value,
                RemoveNoise = chkRemoveNoise.Checked,
                NoiseThreshold = (int)numNoiseThreshold.Value
            };
        }
        
        #endregion
        
        #region Form Controls
        
        private SplitContainer splitContainer1;
        private SplitContainer splitContainer2;
        private GroupBox groupBoxOriginal;
        private GroupBox groupBoxProcessed;
        private GroupBox groupBoxControls;
        private PictureBox pictureBoxOriginal;
        private PictureBox pictureBoxProcessed;
        private TabControl tabControl1;
        private TabPage tabPageBackground;
        private TabPage tabPageContrast;
        private TabPage tabPageLines;
        private TabPage tabPageText;
        private TabPage tabPageNoise;
        private CheckBox chkBackgroundWhite;
        private TrackBar trackBarBackground;
        private Label lblBackgroundValue;
        private CheckBox chkContrast;
        private TrackBar trackBarContrast;
        private Label lblContrastValue;
        private CheckBox chkEnhanceLines;
        private NumericUpDown numLineThickness;
        private Label lblLineThickness;
        private CheckBox chkEnhanceText;
        private TrackBar trackBarTextEnhance;
        private Label lblTextEnhanceValue;
        private CheckBox chkRemoveNoise;
        private NumericUpDown numNoiseThreshold;
        private Label lblNoiseThreshold;
        private CheckBox chkAutoProcess;
        private Panel panelButtons;
        private Button btnLoadImage;
        private Button btnApplyPreset;
        private ComboBox cmbPresets;
        private Button btnProcess;
        private Button btnSaveProcessed;
        private Button btnExecuteOCR;
        private ProgressBar progressBar1;
        private StatusStrip statusStrip1;
        private ToolStripStatusLabel toolStripStatusLabel1;
        
        #endregion
        
        #region Cleanup
        
        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _preprocessor?.Dispose();
                _originalImage?.Dispose();
                _processedImage?.Dispose();
                _processingWorker?.Dispose();
            }
            base.Dispose(disposing);
        }
        
        #endregion
    }
}