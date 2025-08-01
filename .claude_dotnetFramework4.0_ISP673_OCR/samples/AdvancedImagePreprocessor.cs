using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Linq;
using System.Collections.Concurrent;

namespace ISP673_OCRApp.Core.ImageProcessing.Advanced
{
    /// <summary>
    /// 高度なOCR前処理クラス - マルチAI分析結果実装
    /// </summary>
    public class AdvancedImagePreprocessor : IDisposable
    {
        private bool _disposed = false;
        private readonly ImageQualityAnalyzer _qualityAnalyzer;
        private readonly Dictionary<DocumentCondition, PreprocessingOptions> _optimalProfiles;
        
        public AdvancedImagePreprocessor()
        {
            _qualityAnalyzer = new ImageQualityAnalyzer();
            _optimalProfiles = InitializeOptimalProfiles();
        }
        
        #region 自動最適化処理
        
        /// <summary>
        /// 文書品質を自動判定して最適な前処理を実行
        /// </summary>
        public Bitmap AutoOptimizeForOCR(Bitmap source)
        {
            // 1. 文書品質分析
            var analysis = _qualityAnalyzer.AnalyzeDocument(source);
            
            // 2. 最適なプロファイル選択
            var options = SelectOptimalProfile(analysis);
            
            // 3. 段階的処理
            var result = ApplyAdaptiveProcessing(source, options, analysis);
            
            // 4. 品質検証
            var finalQuality = _qualityAnalyzer.PredictOCRQuality(result);
            if (finalQuality.EstimatedAccuracy < 0.85f)
            {
                // 追加処理
                var enhanced = ApplyEnhancementProcessing(result, finalQuality);
                result.Dispose();
                result = enhanced;
            }
            
            return result;
        }
        
        #endregion
        
        #region 特殊ケース処理
        
        /// <summary>
        /// モアレ除去処理
        /// </summary>
        public Bitmap RemoveMoirePattern(Bitmap source)
        {
            // FFTを使用した周波数領域フィルタリング
            var fftData = ApplyFFT(source);
            
            // モアレ周波数の検出と除去
            RemoveMoireFrequencies(fftData);
            
            // 逆FFTで画像復元
            var result = ApplyInverseFFT(fftData);
            
            // ガウシアンぼかし後のシャープニング
            using (var blurred = ApplyGaussianBlur(result, 1.5f))
            {
                var sharpened = ApplyUnsharpMask(blurred, 2.0f, 150.0f, 10);
                result.Dispose();
                return sharpened;
            }
        }
        
        /// <summary>
        /// 裏写り除去処理
        /// </summary>
        public Bitmap RemoveShowThrough(Bitmap source, Bitmap backSide = null)
        {
            Bitmap result = new Bitmap(source.Width, source.Height);
            
            BitmapData sourceData = null;
            BitmapData backData = null;
            BitmapData resultData = null;
            
            try
            {
                sourceData = source.LockBits(
                    new Rectangle(0, 0, source.Width, source.Height),
                    ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                    
                if (backSide != null)
                {
                    backData = backSide.LockBits(
                        new Rectangle(0, 0, backSide.Width, backSide.Height),
                        ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                }
                
                resultData = result.LockBits(
                    new Rectangle(0, 0, result.Width, result.Height),
                    ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
                
                unsafe
                {
                    byte* sourcePtr = (byte*)sourceData.Scan0.ToPointer();
                    byte* backPtr = backData != null ? (byte*)backData.Scan0.ToPointer() : null;
                    byte* resultPtr = (byte*)resultData.Scan0.ToPointer();
                    
                    int stride = sourceData.Stride;
                    
                    Parallel.For(0, source.Height, y =>
                    {
                        for (int x = 0; x < source.Width; x++)
                        {
                            int idx = y * stride + x * 3;
                            
                            if (backPtr != null)
                            {
                                // 両面スキャンデータを使用した高度な裏写り除去
                                float frontB = sourcePtr[idx];
                                float frontG = sourcePtr[idx + 1];
                                float frontR = sourcePtr[idx + 2];
                                
                                float backB = backPtr[idx];
                                float backG = backPtr[idx + 1];
                                float backR = backPtr[idx + 2];
                                
                                // 裏面の影響を減算
                                float correctedB = frontB - 0.3f * (255 - backB);
                                float correctedG = frontG - 0.3f * (255 - backG);
                                float correctedR = frontR - 0.3f * (255 - backR);
                                
                                resultPtr[idx] = ClampByte(correctedB);
                                resultPtr[idx + 1] = ClampByte(correctedG);
                                resultPtr[idx + 2] = ClampByte(correctedR);
                            }
                            else
                            {
                                // 単一画像での裏写り除去
                                byte gray = (byte)((sourcePtr[idx + 2] * 0.299 + 
                                                   sourcePtr[idx + 1] * 0.587 + 
                                                   sourcePtr[idx] * 0.114));
                                
                                // 高輝度ピクセルをより白く
                                if (gray > 200)
                                {
                                    resultPtr[idx] = 255;
                                    resultPtr[idx + 1] = 255;
                                    resultPtr[idx + 2] = 255;
                                }
                                else
                                {
                                    // コントラスト強調
                                    float factor = 1.5f;
                                    resultPtr[idx] = ClampByte((sourcePtr[idx] - 128) * factor + 128);
                                    resultPtr[idx + 1] = ClampByte((sourcePtr[idx + 1] - 128) * factor + 128);
                                    resultPtr[idx + 2] = ClampByte((sourcePtr[idx + 2] - 128) * factor + 128);
                                }
                            }
                        }
                    });
                }
            }
            finally
            {
                source.UnlockBits(sourceData);
                if (backData != null) backSide.UnlockBits(backData);
                result.UnlockBits(resultData);
            }
            
            return result;
        }
        
        /// <summary>
        /// ドットマトリクスプリンター文字の強調
        /// </summary>
        public Bitmap EnhanceDotMatrixText(Bitmap source)
        {
            // 1. ドット検出
            var dots = DetectDots(source);
            
            // 2. ドット接続
            var connected = ConnectDots(source, dots, 2, 0.7f);
            
            // 3. モルフォロジー処理
            var morphed = ApplyMorphologicalOperations(connected, new[]
            {
                new MorphOperation { Type = MorphType.Close, Size = 3 },
                new MorphOperation { Type = MorphType.Open, Size = 2 }
            });
            
            connected.Dispose();
            
            // 4. ストローク幅正規化
            return NormalizeStrokeWidth(morphed, 2);
        }
        
        #endregion
        
        #region 高度な画像処理アルゴリズム
        
        /// <summary>
        /// 適応的局所コントラスト強調 (CLAHE)
        /// </summary>
        private Bitmap ApplyCLAHE(Bitmap source, float clipLimit, int tileSize)
        {
            var result = new Bitmap(source.Width, source.Height);
            var gray = ConvertToGrayscale(source);
            
            // タイルごとにヒストグラム均等化
            int tileWidth = source.Width / tileSize;
            int tileHeight = source.Height / tileSize;
            
            var histograms = new int[tileSize, tileSize, 256];
            var cdfs = new float[tileSize, tileSize, 256];
            
            // 各タイルのヒストグラム計算
            Parallel.For(0, tileSize, ty =>
            {
                for (int tx = 0; tx < tileSize; tx++)
                {
                    CalculateTileHistogram(gray, tx, ty, tileWidth, tileHeight, 
                                         histograms, clipLimit);
                    CalculateCDF(histograms, tx, ty, cdfs);
                }
            });
            
            // 双線形補間で画素値を決定
            BitmapData grayData = gray.LockBits(
                new Rectangle(0, 0, gray.Width, gray.Height),
                ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                
            BitmapData resultData = result.LockBits(
                new Rectangle(0, 0, result.Width, result.Height),
                ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
            
            unsafe
            {
                byte* grayPtr = (byte*)grayData.Scan0.ToPointer();
                byte* resultPtr = (byte*)resultData.Scan0.ToPointer();
                
                Parallel.For(0, source.Height, y =>
                {
                    for (int x = 0; x < source.Width; x++)
                    {
                        float tileX = (float)x / tileWidth;
                        float tileY = (float)y / tileHeight;
                        
                        int tx0 = (int)tileX;
                        int ty0 = (int)tileY;
                        int tx1 = Math.Min(tx0 + 1, tileSize - 1);
                        int ty1 = Math.Min(ty0 + 1, tileSize - 1);
                        
                        float fx = tileX - tx0;
                        float fy = tileY - ty0;
                        
                        int idx = y * grayData.Stride + x * 3;
                        byte pixelValue = grayPtr[idx];
                        
                        // 双線形補間
                        float v00 = cdfs[ty0, tx0, pixelValue];
                        float v01 = cdfs[ty0, tx1, pixelValue];
                        float v10 = cdfs[ty1, tx0, pixelValue];
                        float v11 = cdfs[ty1, tx1, pixelValue];
                        
                        float v0 = v00 * (1 - fx) + v01 * fx;
                        float v1 = v10 * (1 - fx) + v11 * fx;
                        float v = v0 * (1 - fy) + v1 * fy;
                        
                        byte newValue = (byte)(v * 255);
                        resultPtr[idx] = newValue;
                        resultPtr[idx + 1] = newValue;
                        resultPtr[idx + 2] = newValue;
                    }
                });
            }
            
            gray.UnlockBits(grayData);
            result.UnlockBits(resultData);
            gray.Dispose();
            
            return result;
        }
        
        /// <summary>
        /// Sauvolaの適応的2値化
        /// </summary>
        private Bitmap ApplySauvolaBinarization(Bitmap source, int windowSize, float k)
        {
            var result = new Bitmap(source.Width, source.Height);
            var gray = ConvertToGrayscale(source);
            
            // 積分画像の計算
            var integral = CalculateIntegralImage(gray);
            var integralSquare = CalculateIntegralSquareImage(gray);
            
            BitmapData grayData = gray.LockBits(
                new Rectangle(0, 0, gray.Width, gray.Height),
                ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
                
            BitmapData resultData = result.LockBits(
                new Rectangle(0, 0, result.Width, result.Height),
                ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
            
            unsafe
            {
                byte* grayPtr = (byte*)grayData.Scan0.ToPointer();
                byte* resultPtr = (byte*)resultData.Scan0.ToPointer();
                
                int halfWindow = windowSize / 2;
                
                Parallel.For(0, source.Height, y =>
                {
                    for (int x = 0; x < source.Width; x++)
                    {
                        // ウィンドウ範囲
                        int x1 = Math.Max(0, x - halfWindow);
                        int y1 = Math.Max(0, y - halfWindow);
                        int x2 = Math.Min(source.Width - 1, x + halfWindow);
                        int y2 = Math.Min(source.Height - 1, y + halfWindow);
                        
                        // 局所平均と標準偏差
                        int area = (x2 - x1 + 1) * (y2 - y1 + 1);
                        double sum = GetIntegralSum(integral, x1, y1, x2, y2);
                        double sumSquare = GetIntegralSum(integralSquare, x1, y1, x2, y2);
                        
                        double mean = sum / area;
                        double variance = (sumSquare / area) - (mean * mean);
                        double stdDev = Math.Sqrt(Math.Max(0, variance));
                        
                        // Sauvolaの閾値
                        double threshold = mean * (1 + k * (stdDev / 128 - 1));
                        
                        int idx = y * grayData.Stride + x * 3;
                        byte pixelValue = grayPtr[idx];
                        byte binaryValue = (byte)(pixelValue > threshold ? 255 : 0);
                        
                        resultPtr[idx] = binaryValue;
                        resultPtr[idx + 1] = binaryValue;
                        resultPtr[idx + 2] = binaryValue;
                    }
                });
            }
            
            gray.UnlockBits(grayData);
            result.UnlockBits(resultData);
            gray.Dispose();
            
            return result;
        }
        
        /// <summary>
        /// 罫線検出と除去（文字保護付き）
        /// </summary>
        public Bitmap RemoveGridLines(Bitmap source)
        {
            var result = new Bitmap(source);
            
            // 1. 連結成分分析で文字領域を検出
            var textRegions = DetectTextRegions(source);
            
            // 2. ハフ変換で直線検出
            var lines = DetectLinesHoughTransform(source);
            
            // 3. 文字領域と交差しない線を除去
            using (Graphics g = Graphics.FromImage(result))
            {
                foreach (var line in lines)
                {
                    if (!IntersectsWithTextRegions(line, textRegions))
                    {
                        // 線を白で上書き
                        using (Pen pen = new Pen(Color.White, 3))
                        {
                            g.DrawLine(pen, line.Start, line.End);
                        }
                    }
                }
            }
            
            // 4. 交差点の修復
            RepairIntersections(result, textRegions);
            
            return result;
        }
        
        #endregion
        
        #region ヘルパーメソッド
        
        private byte ClampByte(float value)
        {
            if (value < 0) return 0;
            if (value > 255) return 255;
            return (byte)value;
        }
        
        private Bitmap ConvertToGrayscale(Bitmap source)
        {
            var result = new Bitmap(source.Width, source.Height, PixelFormat.Format24bppRgb);
            
            using (Graphics g = Graphics.FromImage(result))
            {
                var colorMatrix = new ColorMatrix(new float[][]
                {
                    new float[] {0.299f, 0.299f, 0.299f, 0, 0},
                    new float[] {0.587f, 0.587f, 0.587f, 0, 0},
                    new float[] {0.114f, 0.114f, 0.114f, 0, 0},
                    new float[] {0, 0, 0, 1, 0},
                    new float[] {0, 0, 0, 0, 1}
                });
                
                var attributes = new ImageAttributes();
                attributes.SetColorMatrix(colorMatrix);
                
                g.DrawImage(source, new Rectangle(0, 0, source.Width, source.Height),
                    0, 0, source.Width, source.Height, GraphicsUnit.Pixel, attributes);
            }
            
            return result;
        }
        
        private Dictionary<DocumentCondition, PreprocessingOptions> InitializeOptimalProfiles()
        {
            return new Dictionary<DocumentCondition, PreprocessingOptions>
            {
                { DocumentCondition.MoirePattern, new MoireRemovalOptions() },
                { DocumentCondition.ShowThrough, new ShowThroughRemovalOptions() },
                { DocumentCondition.DotMatrix, new DotMatrixEnhancementOptions() },
                { DocumentCondition.AgedDocument, new AgedDocumentOptions() },
                { DocumentCondition.InkBleed, new InkBleedCorrectionOptions() },
                { DocumentCondition.GridBackground, new GridRemovalOptions() },
                { DocumentCondition.SkewedDocument, new SkewCorrectionOptions() },
                { DocumentCondition.PoorIllumination, new IlluminationCorrectionOptions() }
            };
        }
        
        #endregion
        
        #region IDisposable
        
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
                    _qualityAnalyzer?.Dispose();
                }
                _disposed = true;
            }
        }
        
        #endregion
    }
    
    #region サポートクラス
    
    /// <summary>
    /// 文書品質分析器
    /// </summary>
    public class ImageQualityAnalyzer : IDisposable
    {
        public DocumentAnalysis AnalyzeDocument(Bitmap image)
        {
            return new DocumentAnalysis
            {
                Condition = DetectDocumentCondition(image),
                QualityMetrics = CalculateQualityMetrics(image),
                TextCharacteristics = AnalyzeTextCharacteristics(image),
                BackgroundCharacteristics = AnalyzeBackground(image)
            };
        }
        
        public OCRQualityPrediction PredictOCRQuality(Bitmap image)
        {
            var metrics = CalculateQualityMetrics(image);
            
            return new OCRQualityPrediction
            {
                EstimatedAccuracy = PredictAccuracy(metrics),
                ProblematicAreas = IdentifyProblematicAreas(image),
                RecommendedActions = SuggestImprovements(metrics)
            };
        }
        
        private DocumentCondition DetectDocumentCondition(Bitmap image)
        {
            // 複数の条件を検出して最も顕著なものを返す
            var conditions = new Dictionary<DocumentCondition, float>();
            
            conditions[DocumentCondition.MoirePattern] = DetectMoireLevel(image);
            conditions[DocumentCondition.ShowThrough] = DetectShowThroughLevel(image);
            conditions[DocumentCondition.DotMatrix] = DetectDotMatrixLevel(image);
            conditions[DocumentCondition.AgedDocument] = DetectAgingLevel(image);
            
            return conditions.OrderByDescending(c => c.Value).First().Key;
        }
        
        private float DetectMoireLevel(Bitmap image)
        {
            // FFTで周期的パターンを検出
            // 実装簡略化のため、仮の値を返す
            return 0.1f;
        }
        
        private float DetectShowThroughLevel(Bitmap image)
        {
            // 裏写りの程度を評価
            return 0.2f;
        }
        
        private float DetectDotMatrixLevel(Bitmap image)
        {
            // ドットパターンの検出
            return 0.15f;
        }
        
        private float DetectAgingLevel(Bitmap image)
        {
            // 経年劣化の程度を評価
            return 0.25f;
        }
        
        private QualityMetrics CalculateQualityMetrics(Bitmap image)
        {
            return new QualityMetrics
            {
                Brightness = CalculateAverageBrightness(image),
                Contrast = CalculateContrastRatio(image),
                Sharpness = CalculateSharpness(image),
                NoiseLevel = EstimateNoiseLevel(image),
                UniformityScore = CalculateUniformity(image)
            };
        }
        
        private float CalculateAverageBrightness(Bitmap image)
        {
            long sum = 0;
            int pixels = image.Width * image.Height;
            
            BitmapData data = image.LockBits(
                new Rectangle(0, 0, image.Width, image.Height),
                ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
            
            unsafe
            {
                byte* ptr = (byte*)data.Scan0.ToPointer();
                int remain = data.Stride - data.Width * 3;
                
                for (int y = 0; y < data.Height; y++)
                {
                    for (int x = 0; x < data.Width; x++)
                    {
                        sum += (ptr[0] + ptr[1] + ptr[2]) / 3;
                        ptr += 3;
                    }
                    ptr += remain;
                }
            }
            
            image.UnlockBits(data);
            
            return (float)sum / pixels;
        }
        
        public void Dispose()
        {
            // クリーンアップ
        }
    }
    
    #endregion
    
    #region データ構造
    
    public class DocumentAnalysis
    {
        public DocumentCondition Condition { get; set; }
        public QualityMetrics QualityMetrics { get; set; }
        public TextCharacteristics TextCharacteristics { get; set; }
        public BackgroundCharacteristics BackgroundCharacteristics { get; set; }
    }
    
    public enum DocumentCondition
    {
        Normal,
        MoirePattern,
        ShowThrough,
        DotMatrix,
        AgedDocument,
        InkBleed,
        GridBackground,
        SkewedDocument,
        PoorIllumination,
        Watermarked
    }
    
    public class QualityMetrics
    {
        public float Brightness { get; set; }
        public float Contrast { get; set; }
        public float Sharpness { get; set; }
        public float NoiseLevel { get; set; }
        public float UniformityScore { get; set; }
    }
    
    public class OCRQualityPrediction
    {
        public float EstimatedAccuracy { get; set; }
        public List<Rectangle> ProblematicAreas { get; set; }
        public List<string> RecommendedActions { get; set; }
    }
    
    public class TextCharacteristics
    {
        public float AverageStrokeWidth { get; set; }
        public float TextDensity { get; set; }
        public bool IsHandwritten { get; set; }
        public FontType EstimatedFontType { get; set; }
    }
    
    public class BackgroundCharacteristics
    {
        public Color DominantColor { get; set; }
        public float NoiseLevel { get; set; }
        public bool HasPattern { get; set; }
        public PatternType PatternType { get; set; }
    }
    
    public enum FontType
    {
        Unknown,
        Serif,
        SansSerif,
        Monospace,
        Handwritten,
        DotMatrix
    }
    
    public enum PatternType
    {
        None,
        Grid,
        Lines,
        Dots,
        Watermark
    }
    
    public class MorphOperation
    {
        public MorphType Type { get; set; }
        public int Size { get; set; }
    }
    
    public enum MorphType
    {
        Erode,
        Dilate,
        Open,
        Close
    }
    
    #endregion
    
    #region 特殊オプションクラス
    
    public class MoireRemovalOptions : PreprocessingOptions
    {
        public MoireRemovalOptions()
        {
            ConvertBackgroundToWhite = true;
            BackgroundThreshold = 185;
            AdjustContrast = true;
            ContrastLevel = 30.0f;
            RemoveNoise = true;
            NoiseThreshold = 3;
        }
    }
    
    public class ShowThroughRemovalOptions : PreprocessingOptions
    {
        public ShowThroughRemovalOptions()
        {
            ConvertBackgroundToWhite = true;
            BackgroundThreshold = 200;
            AdjustContrast = true;
            ContrastLevel = 50.0f;
            EnhanceText = true;
            TextEnhancementLevel = 70;
        }
    }
    
    public class DotMatrixEnhancementOptions : PreprocessingOptions
    {
        public DotMatrixEnhancementOptions()
        {
            EnhanceText = true;
            TextEnhancementLevel = 80;
            EnhanceLines = true;
            LineThickness = 2;
            RemoveNoise = false; // ドットを保護
        }
    }
    
    public class AgedDocumentOptions : PreprocessingOptions
    {
        public AgedDocumentOptions()
        {
            ConvertBackgroundToWhite = true;
            BackgroundThreshold = 180;
            AdjustContrast = true;
            ContrastLevel = 60.0f;
            EnhanceText = true;
            TextEnhancementLevel = 75;
            RemoveNoise = true;
            NoiseThreshold = 5;
        }
    }
    
    public class InkBleedCorrectionOptions : PreprocessingOptions
    {
        public InkBleedCorrectionOptions()
        {
            EnhanceText = true;
            TextEnhancementLevel = 60;
            AdjustContrast = true;
            ContrastLevel = 40.0f;
            RemoveNoise = true;
            NoiseThreshold = 3;
        }
    }
    
    public class GridRemovalOptions : PreprocessingOptions
    {
        public GridRemovalOptions()
        {
            EnhanceLines = false; // 罫線は除去対象
            EnhanceText = true;
            TextEnhancementLevel = 70;
            ConvertBackgroundToWhite = true;
            BackgroundThreshold = 190;
        }
    }
    
    public class SkewCorrectionOptions : PreprocessingOptions
    {
        public SkewCorrectionOptions()
        {
            EnhanceLines = true;
            LineThickness = 2;
            AdjustContrast = true;
            ContrastLevel = 30.0f;
        }
    }
    
    public class IlluminationCorrectionOptions : PreprocessingOptions
    {
        public IlluminationCorrectionOptions()
        {
            ConvertBackgroundToWhite = true;
            BackgroundThreshold = 195;
            AdjustContrast = true;
            ContrastLevel = 45.0f;
            EnhanceText = true;
            TextEnhancementLevel = 65;
        }
    }
    
    #endregion
}