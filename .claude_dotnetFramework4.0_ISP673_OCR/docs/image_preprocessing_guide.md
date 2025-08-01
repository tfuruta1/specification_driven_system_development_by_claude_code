# OCR前処理画像調整ガイド - .NET Framework 4.0

## 1. 概要

OCR認識精度を向上させるため、画像の前処理機能を実装します。.NET Framework 4.0の`System.Drawing`名前空間を使用して、以下の調整機能を提供します：

- 背景色の白色化
- 罫線の強調・接続
- 文字の濃度調整
- ノイズ除去
- コントラスト調整

## 2. 実装クラス構造

```csharp
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

namespace ISP673_OCRApp.Core.ImageProcessing
{
    /// <summary>
    /// OCR前処理用画像調整クラス
    /// </summary>
    public class ImagePreprocessor : IDisposable
    {
        private bool _disposed = false;
        
        /// <summary>
        /// 画像の前処理を実行
        /// </summary>
        public Bitmap PreprocessImage(Bitmap sourceImage, PreprocessingOptions options)
        {
            if (sourceImage == null)
                throw new ArgumentNullException("sourceImage");
                
            Bitmap processedImage = new Bitmap(sourceImage);
            
            try
            {
                // 1. 背景色の白色化
                if (options.ConvertBackgroundToWhite)
                {
                    processedImage = ConvertBackgroundToWhite(processedImage, options.BackgroundThreshold);
                }
                
                // 2. コントラスト調整
                if (options.AdjustContrast)
                {
                    processedImage = AdjustContrast(processedImage, options.ContrastLevel);
                }
                
                // 3. 罫線強調
                if (options.EnhanceLines)
                {
                    processedImage = EnhanceLines(processedImage, options.LineThickness);
                }
                
                // 4. 文字濃度調整
                if (options.EnhanceText)
                {
                    processedImage = EnhanceText(processedImage, options.TextEnhancementLevel);
                }
                
                // 5. ノイズ除去
                if (options.RemoveNoise)
                {
                    processedImage = RemoveNoise(processedImage, options.NoiseThreshold);
                }
                
                return processedImage;
            }
            catch
            {
                processedImage?.Dispose();
                throw;
            }
        }
        
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }
        
        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                _disposed = true;
            }
        }
    }
    
    /// <summary>
    /// 前処理オプション
    /// </summary>
    public class PreprocessingOptions
    {
        public bool ConvertBackgroundToWhite { get; set; } = true;
        public int BackgroundThreshold { get; set; } = 200; // 0-255
        
        public bool AdjustContrast { get; set; } = true;
        public float ContrastLevel { get; set; } = 1.5f; // 0.5-3.0
        
        public bool EnhanceLines { get; set; } = true;
        public int LineThickness { get; set; } = 2; // ピクセル
        
        public bool EnhanceText { get; set; } = true;
        public int TextEnhancementLevel { get; set; } = 50; // 0-100
        
        public bool RemoveNoise { get; set; } = true;
        public int NoiseThreshold { get; set; } = 3; // ピクセル
        
        // プリセット設定
        public static PreprocessingOptions Default => new PreprocessingOptions();
        
        public static PreprocessingOptions ForFadedDocument => new PreprocessingOptions
        {
            ConvertBackgroundToWhite = true,
            BackgroundThreshold = 180,
            AdjustContrast = true,
            ContrastLevel = 2.0f,
            EnhanceText = true,
            TextEnhancementLevel = 70
        };
        
        public static PreprocessingOptions ForPoorQualityForm => new PreprocessingOptions
        {
            EnhanceLines = true,
            LineThickness = 3,
            EnhanceText = true,
            TextEnhancementLevel = 60,
            RemoveNoise = true,
            NoiseThreshold = 5
        };
    }
}
```

## 3. 画像処理アルゴリズム実装

### 3.1 背景色の白色化

```csharp
private Bitmap ConvertBackgroundToWhite(Bitmap source, int threshold)
{
    Bitmap result = new Bitmap(source.Width, source.Height);
    
    // 高速処理のためのBitmapDataアクセス
    BitmapData sourceData = source.LockBits(
        new Rectangle(0, 0, source.Width, source.Height),
        ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
        
    BitmapData resultData = result.LockBits(
        new Rectangle(0, 0, result.Width, result.Height),
        ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
    
    unsafe
    {
        byte* sourcePtr = (byte*)sourceData.Scan0.ToPointer();
        byte* resultPtr = (byte*)resultData.Scan0.ToPointer();
        
        int stride = sourceData.Stride;
        int offset = stride - source.Width * 3;
        
        for (int y = 0; y < source.Height; y++)
        {
            for (int x = 0; x < source.Width; x++)
            {
                byte b = sourcePtr[0];
                byte g = sourcePtr[1];
                byte r = sourcePtr[2];
                
                // グレースケール値を計算
                int gray = (int)(r * 0.299 + g * 0.587 + b * 0.114);
                
                // 閾値より明るい場合は白に変換
                if (gray >= threshold)
                {
                    resultPtr[0] = 255; // B
                    resultPtr[1] = 255; // G
                    resultPtr[2] = 255; // R
                }
                else
                {
                    resultPtr[0] = b;
                    resultPtr[1] = g;
                    resultPtr[2] = r;
                }
                
                sourcePtr += 3;
                resultPtr += 3;
            }
            
            sourcePtr += offset;
            resultPtr += offset;
        }
    }
    
    source.UnlockBits(sourceData);
    result.UnlockBits(resultData);
    
    return result;
}
```

### 3.2 罫線の強調・接続

```csharp
private Bitmap EnhanceLines(Bitmap source, int thickness)
{
    Bitmap result = new Bitmap(source);
    
    using (Graphics g = Graphics.FromImage(result))
    {
        // モルフォロジー処理（膨張・収縮）のシミュレーション
        using (Bitmap temp = ApplyMorphology(source, MorphologyOperation.Dilate, thickness))
        {
            result = ApplyMorphology(temp, MorphologyOperation.Erode, thickness / 2);
        }
    }
    
    // 水平・垂直線の検出と強調
    result = DetectAndEnhanceLines(result, thickness);
    
    return result;
}

private Bitmap DetectAndEnhanceLines(Bitmap source, int thickness)
{
    Bitmap result = new Bitmap(source);
    
    // Sobelフィルタによるエッジ検出
    float[,] sobelX = {
        { -1, 0, 1 },
        { -2, 0, 2 },
        { -1, 0, 1 }
    };
    
    float[,] sobelY = {
        { -1, -2, -1 },
        {  0,  0,  0 },
        {  1,  2,  1 }
    };
    
    // エッジ検出後、線として認識される部分を強調
    using (Bitmap edges = ApplyConvolution(source, sobelX, sobelY))
    {
        // 検出されたエッジを元画像に重ね合わせ
        using (Graphics g = Graphics.FromImage(result))
        {
            // エッジ部分を黒く描画
            for (int y = 0; y < edges.Height; y++)
            {
                for (int x = 0; x < edges.Width; x++)
                {
                    Color pixel = edges.GetPixel(x, y);
                    if (pixel.R < 128) // エッジとして検出された部分
                    {
                        using (Pen pen = new Pen(Color.Black, thickness))
                        {
                            g.DrawRectangle(pen, x, y, 1, 1);
                        }
                    }
                }
            }
        }
    }
    
    return result;
}
```

### 3.3 文字濃度の調整

```csharp
private Bitmap EnhanceText(Bitmap source, int enhancementLevel)
{
    Bitmap result = new Bitmap(source.Width, source.Height);
    
    // アダプティブ閾値処理
    int windowSize = 15; // 局所的な窓のサイズ
    float k = 0.5f + (enhancementLevel / 100.0f) * 0.5f; // 0.5 - 1.0
    
    BitmapData sourceData = source.LockBits(
        new Rectangle(0, 0, source.Width, source.Height),
        ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
        
    BitmapData resultData = result.LockBits(
        new Rectangle(0, 0, result.Width, result.Height),
        ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
    
    unsafe
    {
        byte* sourcePtr = (byte*)sourceData.Scan0.ToPointer();
        byte* resultPtr = (byte*)resultData.Scan0.ToPointer();
        
        int stride = sourceData.Stride;
        
        // 各ピクセルに対してアダプティブ閾値処理
        Parallel.For(0, source.Height, y =>
        {
            for (int x = 0; x < source.Width; x++)
            {
                // 局所的な平均を計算
                float localMean = CalculateLocalMean(
                    sourcePtr, x, y, windowSize, 
                    source.Width, source.Height, stride);
                
                int pixelIndex = y * stride + x * 3;
                byte gray = (byte)((sourcePtr[pixelIndex] + 
                                   sourcePtr[pixelIndex + 1] + 
                                   sourcePtr[pixelIndex + 2]) / 3);
                
                // アダプティブ閾値処理
                byte newValue = (byte)(gray < localMean * k ? 0 : 255);
                
                // ガンマ補正を適用して中間調を調整
                if (newValue > 0 && newValue < 255)
                {
                    float gamma = 1.0f + (enhancementLevel / 100.0f);
                    newValue = (byte)(255 * Math.Pow(newValue / 255.0, 1.0 / gamma));
                }
                
                resultPtr[pixelIndex] = newValue;
                resultPtr[pixelIndex + 1] = newValue;
                resultPtr[pixelIndex + 2] = newValue;
            }
        });
    }
    
    source.UnlockBits(sourceData);
    result.UnlockBits(resultData);
    
    return result;
}
```

### 3.4 ノイズ除去

```csharp
private Bitmap RemoveNoise(Bitmap source, int threshold)
{
    Bitmap result = new Bitmap(source);
    
    // メディアンフィルタ（スパイクノイズ除去）
    result = ApplyMedianFilter(result, threshold);
    
    // 小さな孤立点の除去
    result = RemoveSmallComponents(result, threshold * threshold);
    
    return result;
}

private Bitmap ApplyMedianFilter(Bitmap source, int windowSize)
{
    Bitmap result = new Bitmap(source.Width, source.Height);
    int offset = windowSize / 2;
    
    for (int y = offset; y < source.Height - offset; y++)
    {
        for (int x = offset; x < source.Width - offset; x++)
        {
            List<byte> rValues = new List<byte>();
            List<byte> gValues = new List<byte>();
            List<byte> bValues = new List<byte>();
            
            // 窓内のピクセル値を収集
            for (int wy = -offset; wy <= offset; wy++)
            {
                for (int wx = -offset; wx <= offset; wx++)
                {
                    Color pixel = source.GetPixel(x + wx, y + wy);
                    rValues.Add(pixel.R);
                    gValues.Add(pixel.G);
                    bValues.Add(pixel.B);
                }
            }
            
            // 中央値を取得
            rValues.Sort();
            gValues.Sort();
            bValues.Sort();
            
            int medianIndex = rValues.Count / 2;
            Color medianColor = Color.FromArgb(
                rValues[medianIndex],
                gValues[medianIndex],
                bValues[medianIndex]);
            
            result.SetPixel(x, y, medianColor);
        }
    }
    
    return result;
}
```

## 4. Windows Forms統合

```csharp
public partial class ImagePreprocessingForm : Form
{
    private ImagePreprocessor _preprocessor;
    private Bitmap _originalImage;
    private Bitmap _processedImage;
    
    public ImagePreprocessingForm()
    {
        InitializeComponent();
        _preprocessor = new ImagePreprocessor();
    }
    
    private void btnLoadImage_Click(object sender, EventArgs e)
    {
        using (OpenFileDialog ofd = new OpenFileDialog())
        {
            ofd.Filter = "画像ファイル|*.jpg;*.jpeg;*.png;*.bmp;*.tiff";
            
            if (ofd.ShowDialog() == DialogResult.OK)
            {
                _originalImage?.Dispose();
                _originalImage = new Bitmap(ofd.FileName);
                pictureBoxOriginal.Image = _originalImage;
                
                // 自動前処理
                ProcessImage();
            }
        }
    }
    
    private void ProcessImage()
    {
        if (_originalImage == null) return;
        
        try
        {
            // UIから設定を取得
            var options = new PreprocessingOptions
            {
                ConvertBackgroundToWhite = chkBackgroundWhite.Checked,
                BackgroundThreshold = trackBarBackground.Value,
                AdjustContrast = chkContrast.Checked,
                ContrastLevel = trackBarContrast.Value / 10.0f,
                EnhanceLines = chkEnhanceLines.Checked,
                LineThickness = (int)numLineThickness.Value,
                EnhanceText = chkEnhanceText.Checked,
                TextEnhancementLevel = trackBarTextEnhance.Value,
                RemoveNoise = chkRemoveNoise.Checked,
                NoiseThreshold = (int)numNoiseThreshold.Value
            };
            
            // BackgroundWorkerで非同期処理
            backgroundWorker1.RunWorkerAsync(options);
        }
        catch (Exception ex)
        {
            MessageBox.Show($"画像処理エラー: {ex.Message}", 
                "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
    
    private void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
    {
        var options = (PreprocessingOptions)e.Argument;
        e.Result = _preprocessor.PreprocessImage(_originalImage, options);
    }
    
    private void backgroundWorker1_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
    {
        if (e.Error != null)
        {
            MessageBox.Show($"処理エラー: {e.Error.Message}");
            return;
        }
        
        _processedImage?.Dispose();
        _processedImage = (Bitmap)e.Result;
        pictureBoxProcessed.Image = _processedImage;
        
        // OCR準備完了
        btnExecuteOCR.Enabled = true;
    }
    
    private void btnExecuteOCR_Click(object sender, EventArgs e)
    {
        if (_processedImage == null) return;
        
        // ISP-673 OCRを実行
        ExecuteOCR(_processedImage);
    }
}
```

## 5. パフォーマンス最適化

### 5.1 並列処理（.NET 4.0 TPL）

```csharp
private Bitmap ProcessLargeImage(Bitmap source, PreprocessingOptions options)
{
    int processorCount = Environment.ProcessorCount;
    int stripHeight = source.Height / processorCount;
    
    Bitmap result = new Bitmap(source.Width, source.Height);
    
    // 画像を水平ストリップに分割して並列処理
    Parallel.For(0, processorCount, i =>
    {
        int startY = i * stripHeight;
        int endY = (i == processorCount - 1) ? source.Height : (i + 1) * stripHeight;
        
        Rectangle stripRect = new Rectangle(0, startY, source.Width, endY - startY);
        
        using (Bitmap strip = source.Clone(stripRect, source.PixelFormat))
        {
            using (Bitmap processedStrip = _preprocessor.PreprocessImage(strip, options))
            {
                lock (result)
                {
                    using (Graphics g = Graphics.FromImage(result))
                    {
                        g.DrawImage(processedStrip, 0, startY);
                    }
                }
            }
        }
    });
    
    return result;
}
```

### 5.2 メモリ管理

```csharp
public class ImageProcessingMemoryManager : IDisposable
{
    private readonly List<IntPtr> _allocatedMemory = new List<IntPtr>();
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalAlloc(uint uFlags, UIntPtr dwBytes);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalFree(IntPtr hMem);
    
    public IntPtr AllocateImageMemory(int width, int height, int bytesPerPixel)
    {
        uint size = (uint)(width * height * bytesPerPixel);
        IntPtr ptr = GlobalAlloc(0x0040, (UIntPtr)size); // GMEM_ZEROINIT
        
        if (ptr == IntPtr.Zero)
            throw new OutOfMemoryException("画像メモリの割り当てに失敗しました");
            
        _allocatedMemory.Add(ptr);
        return ptr;
    }
    
    public void FreeImageMemory(IntPtr ptr)
    {
        if (ptr != IntPtr.Zero)
        {
            GlobalFree(ptr);
            _allocatedMemory.Remove(ptr);
        }
    }
    
    public void Dispose()
    {
        foreach (var ptr in _allocatedMemory.ToList())
        {
            FreeImageMemory(ptr);
        }
    }
}
```

## 6. ISP-673 OCRとの統合

```csharp
public class OCRImagePreprocessingIntegration
{
    private readonly ImagePreprocessor _preprocessor;
    private readonly GlyOcr _gOcr;
    private readonly GlyOcrEx _gOcrEx;
    
    public OCRImagePreprocessingIntegration()
    {
        _preprocessor = new ImagePreprocessor();
        _gOcr = new GlyOcr();
        _gOcrEx = new GlyOcrEx();
    }
    
    public async Task<string> ProcessAndRecognizeAsync(string imagePath)
    {
        return await Task.Factory.StartNew(() =>
        {
            // 1. 画像の読み込み
            using (Bitmap originalImage = new Bitmap(imagePath))
            {
                // 2. 前処理の実行
                PreprocessingOptions options = DeterminePreprocessingOptions(originalImage);
                
                using (Bitmap processedImage = _preprocessor.PreprocessImage(originalImage, options))
                {
                    // 3. 一時ファイルに保存
                    string tempPath = Path.GetTempFileName() + ".tiff";
                    processedImage.Save(tempPath, ImageFormat.Tiff);
                    
                    try
                    {
                        // 4. ISP-673 OCRの実行
                        int docId = 0;
                        int retVal = _gOcr.RecogDocumentFn(ref docId, tempPath);
                        
                        if (retVal == 0)
                        {
                            // 5. 結果の取得
                            return ExtractOCRResults();
                        }
                        else
                        {
                            throw new Exception($"OCR処理エラー: {retVal}");
                        }
                    }
                    finally
                    {
                        // 6. 一時ファイルの削除
                        if (File.Exists(tempPath))
                            File.Delete(tempPath);
                    }
                }
            }
        });
    }
    
    private PreprocessingOptions DeterminePreprocessingOptions(Bitmap image)
    {
        // 画像の品質を分析して最適な前処理オプションを決定
        float brightness = CalculateAverageBrightness(image);
        float contrast = CalculateContrast(image);
        
        if (brightness > 200 && contrast < 50)
        {
            return PreprocessingOptions.ForFadedDocument;
        }
        else if (contrast < 30)
        {
            return PreprocessingOptions.ForPoorQualityForm;
        }
        else
        {
            return PreprocessingOptions.Default;
        }
    }
}
```

## 7. 使用例

```csharp
// 基本的な使用例
var preprocessor = new ImagePreprocessor();
var options = PreprocessingOptions.ForFadedDocument;

using (Bitmap original = new Bitmap(@"C:\scanned_form.jpg"))
using (Bitmap processed = preprocessor.PreprocessImage(original, options))
{
    processed.Save(@"C:\processed_form.tiff", ImageFormat.Tiff);
    
    // OCR実行
    int docId = 0;
    gOcr.RecogDocumentFn(ref docId, @"C:\processed_form.tiff");
}

// 高度な使用例：カスタム設定
var customOptions = new PreprocessingOptions
{
    ConvertBackgroundToWhite = true,
    BackgroundThreshold = 190,
    EnhanceLines = true,
    LineThickness = 3,
    EnhanceText = true,
    TextEnhancementLevel = 80,
    RemoveNoise = true,
    NoiseThreshold = 5
};
```

この実装により、OCR認識精度を大幅に向上させることができます。