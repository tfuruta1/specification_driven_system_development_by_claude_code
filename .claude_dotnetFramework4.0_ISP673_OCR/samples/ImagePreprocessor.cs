using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Linq;

namespace ISP673_OCRApp.Core.ImageProcessing
{
    /// <summary>
    /// OCR前処理用画像調整クラス
    /// .NET Framework 4.0対応版
    /// </summary>
    public class ImagePreprocessor : IDisposable
    {
        private bool _disposed = false;
        
        #region Public Methods
        
        /// <summary>
        /// 画像の前処理を実行
        /// </summary>
        /// <param name="sourceImage">元画像</param>
        /// <param name="options">前処理オプション</param>
        /// <returns>処理済み画像</returns>
        public Bitmap PreprocessImage(Bitmap sourceImage, PreprocessingOptions options)
        {
            if (sourceImage == null)
                throw new ArgumentNullException("sourceImage");
                
            Bitmap processedImage = null;
            Bitmap tempImage = null;
            
            try
            {
                // 元画像をコピー
                processedImage = new Bitmap(sourceImage);
                
                // 1. 背景色の白色化
                if (options.ConvertBackgroundToWhite)
                {
                    tempImage = ConvertBackgroundToWhite(processedImage, options.BackgroundThreshold);
                    processedImage.Dispose();
                    processedImage = tempImage;
                    tempImage = null;
                }
                
                // 2. コントラスト調整
                if (options.AdjustContrast)
                {
                    tempImage = AdjustContrast(processedImage, options.ContrastLevel);
                    processedImage.Dispose();
                    processedImage = tempImage;
                    tempImage = null;
                }
                
                // 3. 罫線強調
                if (options.EnhanceLines)
                {
                    tempImage = EnhanceLines(processedImage, options.LineThickness);
                    processedImage.Dispose();
                    processedImage = tempImage;
                    tempImage = null;
                }
                
                // 4. 文字濃度調整
                if (options.EnhanceText)
                {
                    tempImage = EnhanceText(processedImage, options.TextEnhancementLevel);
                    processedImage.Dispose();
                    processedImage = tempImage;
                    tempImage = null;
                }
                
                // 5. ノイズ除去
                if (options.RemoveNoise)
                {
                    tempImage = RemoveNoise(processedImage, options.NoiseThreshold);
                    processedImage.Dispose();
                    processedImage = tempImage;
                    tempImage = null;
                }
                
                return processedImage;
            }
            catch
            {
                processedImage?.Dispose();
                tempImage?.Dispose();
                throw;
            }
        }
        
        #endregion
        
        #region Image Processing Methods
        
        /// <summary>
        /// 背景色を白に変換
        /// </summary>
        private unsafe Bitmap ConvertBackgroundToWhite(Bitmap source, int threshold)
        {
            Bitmap result = new Bitmap(source.Width, source.Height, PixelFormat.Format24bppRgb);
            
            BitmapData sourceData = null;
            BitmapData resultData = null;
            
            try
            {
                sourceData = source.LockBits(
                    new Rectangle(0, 0, source.Width, source.Height),
                    ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                    
                resultData = result.LockBits(
                    new Rectangle(0, 0, result.Width, result.Height),
                    ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
                
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
            finally
            {
                if (sourceData != null)
                    source.UnlockBits(sourceData);
                if (resultData != null)
                    result.UnlockBits(resultData);
            }
            
            return result;
        }
        
        /// <summary>
        /// コントラスト調整
        /// </summary>
        private unsafe Bitmap AdjustContrast(Bitmap source, float contrastLevel)
        {
            Bitmap result = new Bitmap(source.Width, source.Height, PixelFormat.Format24bppRgb);
            
            BitmapData sourceData = null;
            BitmapData resultData = null;
            
            try
            {
                sourceData = source.LockBits(
                    new Rectangle(0, 0, source.Width, source.Height),
                    ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                    
                resultData = result.LockBits(
                    new Rectangle(0, 0, result.Width, result.Height),
                    ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
                
                byte* sourcePtr = (byte*)sourceData.Scan0.ToPointer();
                byte* resultPtr = (byte*)resultData.Scan0.ToPointer();
                
                int totalPixels = source.Width * source.Height * 3;
                
                // コントラスト調整の計算
                float factor = (259.0f * (contrastLevel + 255.0f)) / (255.0f * (259.0f - contrastLevel));
                
                for (int i = 0; i < totalPixels; i++)
                {
                    float pixel = sourcePtr[i];
                    pixel = factor * (pixel - 128) + 128;
                    
                    // クリッピング
                    if (pixel < 0) pixel = 0;
                    if (pixel > 255) pixel = 255;
                    
                    resultPtr[i] = (byte)pixel;
                }
            }
            finally
            {
                if (sourceData != null)
                    source.UnlockBits(sourceData);
                if (resultData != null)
                    result.UnlockBits(resultData);
            }
            
            return result;
        }
        
        /// <summary>
        /// 罫線の強調
        /// </summary>
        private Bitmap EnhanceLines(Bitmap source, int thickness)
        {
            // まず画像を2値化
            Bitmap binary = ConvertToBinary(source, 128);
            
            // 水平線と垂直線を検出して強調
            Bitmap result = new Bitmap(binary);
            
            using (Graphics g = Graphics.FromImage(result))
            {
                // 水平線の検出と強調
                for (int y = 1; y < source.Height - 1; y++)
                {
                    int consecutiveBlackPixels = 0;
                    int startX = 0;
                    
                    for (int x = 0; x < source.Width; x++)
                    {
                        Color pixel = binary.GetPixel(x, y);
                        
                        if (pixel.R < 128) // 黒ピクセル
                        {
                            if (consecutiveBlackPixels == 0)
                                startX = x;
                            consecutiveBlackPixels++;
                        }
                        else
                        {
                            // 一定以上の長さの黒ピクセルが続いたら線として認識
                            if (consecutiveBlackPixels > 20)
                            {
                                using (Pen pen = new Pen(Color.Black, thickness))
                                {
                                    g.DrawLine(pen, startX, y, x - 1, y);
                                }
                            }
                            consecutiveBlackPixels = 0;
                        }
                    }
                }
                
                // 垂直線の検出と強調
                for (int x = 1; x < source.Width - 1; x++)
                {
                    int consecutiveBlackPixels = 0;
                    int startY = 0;
                    
                    for (int y = 0; y < source.Height; y++)
                    {
                        Color pixel = binary.GetPixel(x, y);
                        
                        if (pixel.R < 128) // 黒ピクセル
                        {
                            if (consecutiveBlackPixels == 0)
                                startY = y;
                            consecutiveBlackPixels++;
                        }
                        else
                        {
                            // 一定以上の長さの黒ピクセルが続いたら線として認識
                            if (consecutiveBlackPixels > 20)
                            {
                                using (Pen pen = new Pen(Color.Black, thickness))
                                {
                                    g.DrawLine(pen, x, startY, x, y - 1);
                                }
                            }
                            consecutiveBlackPixels = 0;
                        }
                    }
                }
            }
            
            binary.Dispose();
            return result;
        }
        
        /// <summary>
        /// 文字の濃度調整
        /// </summary>
        private unsafe Bitmap EnhanceText(Bitmap source, int enhancementLevel)
        {
            Bitmap result = new Bitmap(source.Width, source.Height, PixelFormat.Format24bppRgb);
            
            // まずグレースケールに変換
            Bitmap grayscale = ConvertToGrayscale(source);
            
            BitmapData grayData = null;
            BitmapData resultData = null;
            
            try
            {
                grayData = grayscale.LockBits(
                    new Rectangle(0, 0, grayscale.Width, grayscale.Height),
                    ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                    
                resultData = result.LockBits(
                    new Rectangle(0, 0, result.Width, result.Height),
                    ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
                
                byte* grayPtr = (byte*)grayData.Scan0.ToPointer();
                byte* resultPtr = (byte*)resultData.Scan0.ToPointer();
                
                int stride = grayData.Stride;
                int offset = stride - source.Width * 3;
                
                // アダプティブ閾値処理のウィンドウサイズ
                int windowSize = 15;
                float k = 0.5f + (enhancementLevel / 100.0f) * 0.3f; // 0.5 - 0.8
                
                for (int y = 0; y < source.Height; y++)
                {
                    for (int x = 0; x < source.Width; x++)
                    {
                        // 局所的な平均を計算
                        float localMean = CalculateLocalMean(
                            grayPtr, x, y, windowSize, 
                            source.Width, source.Height, stride);
                        
                        byte grayValue = grayPtr[y * stride + x * 3];
                        
                        // アダプティブ閾値処理
                        byte newValue;
                        if (grayValue < localMean * k)
                        {
                            // 文字として認識 - 黒く強調
                            newValue = (byte)Math.Max(0, grayValue - enhancementLevel);
                        }
                        else
                        {
                            // 背景として認識 - 白く
                            newValue = (byte)Math.Min(255, grayValue + enhancementLevel / 2);
                        }
                        
                        int index = y * stride + x * 3;
                        resultPtr[index] = newValue;
                        resultPtr[index + 1] = newValue;
                        resultPtr[index + 2] = newValue;
                    }
                }
            }
            finally
            {
                if (grayData != null)
                    grayscale.UnlockBits(grayData);
                if (resultData != null)
                    result.UnlockBits(resultData);
                grayscale.Dispose();
            }
            
            return result;
        }
        
        /// <summary>
        /// ノイズ除去
        /// </summary>
        private Bitmap RemoveNoise(Bitmap source, int threshold)
        {
            // メディアンフィルタでノイズ除去
            return ApplyMedianFilter(source, threshold);
        }
        
        #endregion
        
        #region Helper Methods
        
        /// <summary>
        /// 2値化処理
        /// </summary>
        private unsafe Bitmap ConvertToBinary(Bitmap source, byte threshold)
        {
            Bitmap result = new Bitmap(source.Width, source.Height, PixelFormat.Format24bppRgb);
            
            BitmapData sourceData = null;
            BitmapData resultData = null;
            
            try
            {
                sourceData = source.LockBits(
                    new Rectangle(0, 0, source.Width, source.Height),
                    ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                    
                resultData = result.LockBits(
                    new Rectangle(0, 0, result.Width, result.Height),
                    ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
                
                byte* sourcePtr = (byte*)sourceData.Scan0.ToPointer();
                byte* resultPtr = (byte*)resultData.Scan0.ToPointer();
                
                int totalPixels = source.Width * source.Height;
                
                for (int i = 0; i < totalPixels; i++)
                {
                    int index = i * 3;
                    byte gray = (byte)((sourcePtr[index] + sourcePtr[index + 1] + sourcePtr[index + 2]) / 3);
                    byte value = (byte)(gray < threshold ? 0 : 255);
                    
                    resultPtr[index] = value;
                    resultPtr[index + 1] = value;
                    resultPtr[index + 2] = value;
                }
            }
            finally
            {
                if (sourceData != null)
                    source.UnlockBits(sourceData);
                if (resultData != null)
                    result.UnlockBits(resultData);
            }
            
            return result;
        }
        
        /// <summary>
        /// グレースケール変換
        /// </summary>
        private unsafe Bitmap ConvertToGrayscale(Bitmap source)
        {
            Bitmap result = new Bitmap(source.Width, source.Height, PixelFormat.Format24bppRgb);
            
            BitmapData sourceData = null;
            BitmapData resultData = null;
            
            try
            {
                sourceData = source.LockBits(
                    new Rectangle(0, 0, source.Width, source.Height),
                    ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                    
                resultData = result.LockBits(
                    new Rectangle(0, 0, result.Width, result.Height),
                    ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
                
                byte* sourcePtr = (byte*)sourceData.Scan0.ToPointer();
                byte* resultPtr = (byte*)resultData.Scan0.ToPointer();
                
                int totalPixels = source.Width * source.Height;
                
                for (int i = 0; i < totalPixels; i++)
                {
                    int index = i * 3;
                    byte gray = (byte)(sourcePtr[index + 2] * 0.299 + 
                                      sourcePtr[index + 1] * 0.587 + 
                                      sourcePtr[index] * 0.114);
                    
                    resultPtr[index] = gray;
                    resultPtr[index + 1] = gray;
                    resultPtr[index + 2] = gray;
                }
            }
            finally
            {
                if (sourceData != null)
                    source.UnlockBits(sourceData);
                if (resultData != null)
                    result.UnlockBits(resultData);
            }
            
            return result;
        }
        
        /// <summary>
        /// 局所的な平均値を計算
        /// </summary>
        private unsafe float CalculateLocalMean(byte* data, int x, int y, int windowSize, 
            int width, int height, int stride)
        {
            int halfWindow = windowSize / 2;
            int sum = 0;
            int count = 0;
            
            for (int dy = -halfWindow; dy <= halfWindow; dy++)
            {
                for (int dx = -halfWindow; dx <= halfWindow; dx++)
                {
                    int nx = x + dx;
                    int ny = y + dy;
                    
                    if (nx >= 0 && nx < width && ny >= 0 && ny < height)
                    {
                        sum += data[ny * stride + nx * 3];
                        count++;
                    }
                }
            }
            
            return count > 0 ? (float)sum / count : 128.0f;
        }
        
        /// <summary>
        /// メディアンフィルタ適用
        /// </summary>
        private Bitmap ApplyMedianFilter(Bitmap source, int windowSize)
        {
            if (windowSize % 2 == 0) windowSize++; // 奇数にする
            
            Bitmap result = new Bitmap(source.Width, source.Height);
            int offset = windowSize / 2;
            
            // .NET 4.0 でのParallel.For使用
            Parallel.For(offset, source.Height - offset, y =>
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
                            Color pixel;
                            lock (source)
                            {
                                pixel = source.GetPixel(x + wx, y + wy);
                            }
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
                    
                    lock (result)
                    {
                        result.SetPixel(x, y, medianColor);
                    }
                }
            });
            
            // 境界部分は元画像をコピー
            using (Graphics g = Graphics.FromImage(result))
            {
                // 上下の境界
                g.DrawImage(source, 0, 0, source.Width, offset, 
                    0, 0, source.Width, offset, GraphicsUnit.Pixel);
                g.DrawImage(source, 0, source.Height - offset, source.Width, offset, 
                    0, source.Height - offset, source.Width, offset, GraphicsUnit.Pixel);
                    
                // 左右の境界
                g.DrawImage(source, 0, 0, offset, source.Height, 
                    0, 0, offset, source.Height, GraphicsUnit.Pixel);
                g.DrawImage(source, source.Width - offset, 0, offset, source.Height, 
                    source.Width - offset, 0, offset, source.Height, GraphicsUnit.Pixel);
            }
            
            return result;
        }
        
        #endregion
        
        #region IDisposable Implementation
        
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }
        
        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    // マネージドリソースの解放
                }
                
                _disposed = true;
            }
        }
        
        #endregion
    }
    
    /// <summary>
    /// 前処理オプション
    /// </summary>
    public class PreprocessingOptions
    {
        public bool ConvertBackgroundToWhite { get; set; } = true;
        public int BackgroundThreshold { get; set; } = 200; // 0-255
        
        public bool AdjustContrast { get; set; } = true;
        public float ContrastLevel { get; set; } = 30.0f; // -100 to 100
        
        public bool EnhanceLines { get; set; } = true;
        public int LineThickness { get; set; } = 2; // ピクセル
        
        public bool EnhanceText { get; set; } = true;
        public int TextEnhancementLevel { get; set; } = 50; // 0-100
        
        public bool RemoveNoise { get; set; } = true;
        public int NoiseThreshold { get; set; } = 3; // ピクセル (メディアンフィルタのウィンドウサイズ)
        
        /// <summary>
        /// デフォルト設定
        /// </summary>
        public static PreprocessingOptions Default 
        {
            get { return new PreprocessingOptions(); }
        }
        
        /// <summary>
        /// 薄い文書用設定
        /// </summary>
        public static PreprocessingOptions ForFadedDocument 
        {
            get
            {
                return new PreprocessingOptions
                {
                    ConvertBackgroundToWhite = true,
                    BackgroundThreshold = 180,
                    AdjustContrast = true,
                    ContrastLevel = 50.0f,
                    EnhanceText = true,
                    TextEnhancementLevel = 70,
                    RemoveNoise = true,
                    NoiseThreshold = 3
                };
            }
        }
        
        /// <summary>
        /// 低品質フォーム用設定
        /// </summary>
        public static PreprocessingOptions ForPoorQualityForm 
        {
            get
            {
                return new PreprocessingOptions
                {
                    ConvertBackgroundToWhite = true,
                    BackgroundThreshold = 190,
                    AdjustContrast = true,
                    ContrastLevel = 40.0f,
                    EnhanceLines = true,
                    LineThickness = 3,
                    EnhanceText = true,
                    TextEnhancementLevel = 60,
                    RemoveNoise = true,
                    NoiseThreshold = 5
                };
            }
        }
    }
}