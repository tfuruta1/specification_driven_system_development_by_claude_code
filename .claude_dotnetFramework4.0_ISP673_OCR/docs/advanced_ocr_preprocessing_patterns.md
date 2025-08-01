# 高度なOCR前処理パターンガイド - マルチAI分析結果

## 1. 概要

Gemini CLI（データ分析）、o3 MCP（画像処理アルゴリズム）、Claude Code（実装）の3つのAIによる分析結果を統合し、様々な低品質文書に対する最適な前処理パターンを提供します。

## 2. 文書品質問題の分類と対策

### 2.1 スキャン品質に起因する問題

#### パターン1: モアレ（干渉縞）が発生した文書
```csharp
public class MoireRemovalOptions : PreprocessingOptions
{
    public MoireRemovalOptions()
    {
        // 周波数フィルタリング
        ApplyFrequencyFilter = true;
        FrequencyThreshold = 0.3f;
        
        // ガウシアンぼかし後のシャープニング
        ApplyGaussianBlur = true;
        BlurRadius = 1.5f;
        ApplySharpening = true;
        SharpnessLevel = 0.8f;
        
        // アダプティブ2値化
        ConvertBackgroundToWhite = true;
        BackgroundThreshold = 185;
        UseAdaptiveBinarization = true;
        AdaptiveWindowSize = 31;
    }
}
```

#### パターン2: スキュー（傾き）が大きい文書
```csharp
public class SkewCorrectionOptions : PreprocessingOptions
{
    public SkewCorrectionOptions()
    {
        // ハフ変換による傾き検出
        DetectSkewAngle = true;
        SkewDetectionMethod = SkewMethod.HoughTransform;
        MaxSkewAngle = 15.0f; // ±15度まで
        
        // 回転後の補間方法
        RotationInterpolation = InterpolationMode.HighQualityBicubic;
        
        // エッジ強調
        EnhanceEdges = true;
        EdgeDetectionMethod = EdgeMethod.Canny;
        EdgeThresholdLow = 50;
        EdgeThresholdHigh = 150;
    }
}
```

#### パターン3: 影や光ムラがある文書
```csharp
public class IlluminationCorrectionOptions : PreprocessingOptions
{
    public IlluminationCorrectionOptions()
    {
        // 照明補正
        ApplyIlluminationCorrection = true;
        IlluminationMethod = IlluminationMethod.MorphologicalTopHat;
        StructuringElementSize = 15;
        
        // 局所的コントラスト強調
        ApplyLocalContrastEnhancement = true;
        LocalWindowSize = 64;
        ContrastLimit = 3.0f;
        
        // グラデーション除去
        RemoveGradient = true;
        GradientKernelSize = 51;
    }
}
```

### 2.2 印刷品質に起因する問題

#### パターン4: ドットマトリクスプリンター印刷
```csharp
public class DotMatrixEnhancementOptions : PreprocessingOptions
{
    public DotMatrixEnhancementOptions()
    {
        // ドット接続処理
        ConnectDots = true;
        DotConnectionRadius = 2;
        DotConnectionThreshold = 0.7f;
        
        // モルフォロジー処理
        ApplyMorphology = true;
        MorphologyOperations = new[]
        {
            new MorphOperation(MorphType.Close, 3),
            new MorphOperation(MorphType.Open, 2)
        };
        
        // 文字太さ正規化
        NormalizeStrokeWidth = true;
        TargetStrokeWidth = 2;
    }
}
```

#### パターン5: インクジェットのにじみ
```csharp
public class InkBleedCorrectionOptions : PreprocessingOptions
{
    public InkBleedCorrectionOptions()
    {
        // エッジ鮮鋭化
        ApplyUnsharpMask = true;
        UnsharpRadius = 2.0f;
        UnsharpAmount = 150.0f;
        UnsharpThreshold = 10;
        
        // 適応的閾値処理
        UseAdaptiveBinarization = true;
        AdaptiveMethod = AdaptiveMethod.Sauvola;
        SauvolaK = 0.3f;
        SauvolaWindowSize = 25;
        
        // 細線化処理
        ApplyThinning = true;
        ThinningMethod = ThinningMethod.ZhangSuen;
    }
}
```

### 2.3 紙質・経年劣化に起因する問題

#### パターン6: 黄ばみ・変色した古文書
```csharp
public class AgedDocumentOptions : PreprocessingOptions
{
    public AgedDocumentOptions()
    {
        // カラーチャンネル別処理
        ProcessColorChannels = true;
        RedChannelWeight = 0.4f;
        GreenChannelWeight = 0.4f;
        BlueChannelWeight = 0.2f;
        
        // ヒストグラム均等化
        ApplyHistogramEqualization = true;
        EqualizationMethod = HistogramMethod.CLAHE;
        ClipLimit = 2.0f;
        TileSize = 8;
        
        // 色温度補正
        CorrectColorTemperature = true;
        TargetTemperature = 6500; // K
        
        // ノイズ除去（古い紙特有のスポット）
        RemoveSpeckleNoise = true;
        SpeckleSize = 4;
        SpeckleStrength = 0.8f;
    }
}
```

#### パターン7: 透け・裏写り
```csharp
public class ShowThroughRemovalOptions : PreprocessingOptions
{
    public ShowThroughRemovalOptions()
    {
        // 両面スキャンデータを使用した裏写り除去
        UseDoubleSidedProcessing = true;
        BackSideWeight = -0.3f;
        
        // 周波数領域フィルタリング
        ApplyFrequencyDomainFilter = true;
        HighPassCutoff = 0.1f;
        ButterworthOrder = 2;
        
        // 選択的色消去
        SelectiveColorRemoval = true;
        RemovalThreshold = 200;
        PreserveColorRange = new ColorRange(0, 100); // 黒文字保護
    }
}
```

### 2.4 複雑な背景パターン

#### パターン8: 罫線・方眼紙
```csharp
public class GridRemovalOptions : PreprocessingOptions
{
    public GridRemovalOptions()
    {
        // 直線検出と除去
        DetectAndRemoveLines = true;
        LineDetectionMethod = LineMethod.ProbabilisticHough;
        MinLineLength = 50;
        MaxLineGap = 10;
        LineRemovalThickness = 3;
        
        // 交差点修復
        RepairIntersections = true;
        IntersectionRadius = 5;
        
        // 文字部分の保護
        ProtectTextRegions = true;
        TextProtectionMethod = ProtectionMethod.ConnectedComponents;
        MinTextSize = 10;
    }
}
```

#### パターン9: ウォーターマーク・透かし
```csharp
public class WatermarkRemovalOptions : PreprocessingOptions
{
    public WatermarkRemovalOptions()
    {
        // 周期的パターン検出
        DetectPeriodicPatterns = true;
        PatternDetectionMethod = PatternMethod.FFT;
        
        // インペインティング
        ApplyInpainting = true;
        InpaintingMethod = InpaintMethod.NavierStokes;
        InpaintingRadius = 3;
        
        // テクスチャ合成
        SynthesizeBackground = true;
        TexturePatchSize = 7;
        TextureSearchRadius = 21;
    }
}
```

## 3. 高度な前処理アルゴリズム実装

### 3.1 マルチスケール処理
```csharp
public class MultiScaleProcessor
{
    public Bitmap ProcessMultiScale(Bitmap source, MultiScaleOptions options)
    {
        var pyramid = BuildGaussianPyramid(source, options.PyramidLevels);
        var processedLevels = new List<Bitmap>();
        
        // 各スケールで異なる処理を適用
        for (int i = 0; i < pyramid.Count; i++)
        {
            var level = pyramid[i];
            var scaleOptions = options.GetOptionsForScale(i);
            
            var processed = ApplyScaleSpecificProcessing(level, scaleOptions);
            processedLevels.Add(processed);
        }
        
        // ラプラシアンピラミッドで再構成
        return ReconstructFromPyramid(processedLevels);
    }
    
    private List<Bitmap> BuildGaussianPyramid(Bitmap source, int levels)
    {
        var pyramid = new List<Bitmap> { source };
        var current = source;
        
        for (int i = 1; i < levels; i++)
        {
            var downsampled = DownsampleWithGaussian(current);
            pyramid.Add(downsampled);
            current = downsampled;
        }
        
        return pyramid;
    }
}
```

### 3.2 機械学習ベースのパラメータ最適化
```csharp
public class MLParameterOptimizer
{
    private readonly Dictionary<DocumentType, PreprocessingOptions> _learnedParams;
    
    public PreprocessingOptions OptimizeParameters(Bitmap sample)
    {
        // 文書特徴を抽出
        var features = ExtractDocumentFeatures(sample);
        
        // 最適なパラメータを予測
        var documentType = ClassifyDocument(features);
        var baseOptions = _learnedParams[documentType];
        
        // 微調整
        return FineTuneParameters(baseOptions, features);
    }
    
    private DocumentFeatures ExtractDocumentFeatures(Bitmap image)
    {
        return new DocumentFeatures
        {
            AverageBrightness = CalculateAverageBrightness(image),
            ContrastRatio = CalculateContrastRatio(image),
            NoiseLevel = EstimateNoiseLevel(image),
            TextDensity = EstimateTextDensity(image),
            LinePresence = DetectLineStructures(image),
            ColorDistribution = AnalyzeColorDistribution(image)
        };
    }
}
```

### 3.3 適応的処理パイプライン
```csharp
public class AdaptivePreprocessingPipeline
{
    private readonly List<IPreprocessingStage> _stages;
    
    public Bitmap Process(Bitmap source)
    {
        var quality = AssessImageQuality(source);
        var pipeline = BuildAdaptivePipeline(quality);
        
        var current = source;
        foreach (var stage in pipeline)
        {
            if (stage.ShouldApply(current, quality))
            {
                var stageResult = stage.Process(current);
                
                // 各段階で品質を再評価
                var newQuality = AssessImageQuality(stageResult);
                if (newQuality.Score > quality.Score)
                {
                    current = stageResult;
                    quality = newQuality;
                }
                else
                {
                    stageResult.Dispose();
                }
            }
        }
        
        return current;
    }
}
```

## 4. 文書タイプ別最適化プロファイル

### 4.1 手書き文書
```csharp
public static class HandwrittenDocumentProfiles
{
    public static PreprocessingOptions PencilWriting = new PreprocessingOptions
    {
        // 鉛筆書き特有の薄さ対策
        EnhanceText = true,
        TextEnhancementLevel = 80,
        UseLocalAdaptiveThreshold = true,
        LocalWindowSize = 51,
        
        // ノイズ除去は控えめに（筆跡保護）
        RemoveNoise = true,
        NoiseThreshold = 2,
        PreserveFineDe‌tails = true
    };
    
    public static PreprocessingOptions BallpointPen = new PreprocessingOptions
    {
        // ボールペンのムラ対策
        NormalizeStrokeWidth = true,
        StrokeNormalizationMethod = StrokeMethod.Morphological,
        
        // インクの濃淡補正
        ApplyGammaCorrection = true,
        GammaValue = 0.7f
    };
}
```

### 4.2 印刷文書
```csharp
public static class PrintedDocumentProfiles
{
    public static PreprocessingOptions LaserPrinter = new PreprocessingOptions
    {
        // トナーの散りを除去
        RemoveScatteredPixels = true,
        ScatterThreshold = 2,
        
        // シャープネス強調
        ApplySharpening = true,
        SharpnessKernel = SharpenKernel.Laplacian
    };
    
    public static PreprocessingOptions Newspaper = new PreprocessingOptions
    {
        // 新聞紙特有の処理
        RemoveHalftone = true,
        HalftoneFrequency = 150, // lpi
        
        // 薄い紙による裏写り除去
        ReduceShowThrough = true,
        ShowThroughThreshold = 220
    };
}
```

## 5. 品質評価メトリクス

### 5.1 OCR品質予測
```csharp
public class OCRQualityPredictor
{
    public OCRQualityMetrics PredictQuality(Bitmap processedImage)
    {
        return new OCRQualityMetrics
        {
            TextClarity = MeasureTextClarity(processedImage),
            BackgroundUniformity = MeasureBackgroundUniformity(processedImage),
            CharacterSeparation = MeasureCharacterSeparation(processedImage),
            NoiseLevel = MeasureNoiseLevel(processedImage),
            ContrastRatio = MeasureContrastRatio(processedImage),
            EstimatedAccuracy = PredictOCRAccuracy(processedImage)
        };
    }
    
    private float MeasureTextClarity(Bitmap image)
    {
        // エッジの鮮明さを評価
        var edges = DetectEdges(image);
        var sharpness = CalculateEdgeSharpness(edges);
        var consistency = CalculateStrokeConsistency(edges);
        
        return (sharpness * 0.6f + consistency * 0.4f);
    }
}
```

## 6. パフォーマンス最適化

### 6.1 GPU アクセラレーション（OpenCL）
```csharp
public class GPUAcceleratedProcessor
{
    private readonly OpenCLContext _context;
    
    public unsafe Bitmap ProcessWithGPU(Bitmap source, PreprocessingOptions options)
    {
        // GPU用バッファ作成
        var sourceBuffer = _context.CreateBuffer(source);
        var resultBuffer = _context.CreateBuffer(source.Width * source.Height * 4);
        
        // カーネル実行
        var kernel = _context.LoadKernel("preprocessing.cl", "processImage");
        kernel.SetArgument(0, sourceBuffer);
        kernel.SetArgument(1, resultBuffer);
        kernel.SetArgument(2, options.ToGPUParams());
        
        _context.Execute(kernel, source.Width * source.Height);
        
        // 結果取得
        return _context.ReadBuffer<Bitmap>(resultBuffer);
    }
}
```

### 6.2 マルチスレッド最適化
```csharp
public class ParallelImageProcessor
{
    public Bitmap ProcessInParallel(Bitmap source, PreprocessingOptions options)
    {
        int tileSize = 256;
        var tiles = SplitIntoTiles(source, tileSize);
        var processedTiles = new ConcurrentBag<ProcessedTile>();
        
        Parallel.ForEach(tiles, new ParallelOptions 
        { 
            MaxDegreeOfParallelism = Environment.ProcessorCount 
        }, 
        tile =>
        {
            var processed = ProcessTile(tile, options);
            processedTiles.Add(processed);
        });
        
        return StitchTiles(processedTiles, source.Width, source.Height);
    }
}
```

## 7. 使用例とベストプラクティス

### 7.1 自動品質判定と処理選択
```csharp
public class AutoPreprocessor
{
    private readonly Dictionary<DocumentCondition, PreprocessingOptions> _profiles;
    
    public Bitmap AutoProcess(Bitmap source)
    {
        // 1. 文書状態を分析
        var condition = AnalyzeDocumentCondition(source);
        
        // 2. 最適なプロファイルを選択
        var options = SelectOptimalProfile(condition);
        
        // 3. 段階的処理と品質確認
        var processor = new ImagePreprocessor();
        var result = processor.PreprocessImage(source, options);
        
        // 4. 品質が不十分な場合は追加処理
        var quality = new OCRQualityPredictor().PredictQuality(result);
        if (quality.EstimatedAccuracy < 0.85f)
        {
            result = ApplyAdditionalProcessing(result, quality);
        }
        
        return result;
    }
}
```

この包括的なガイドにより、様々な低品質文書に対して最適な前処理を適用し、OCR認識精度を最大限に向上させることができます。