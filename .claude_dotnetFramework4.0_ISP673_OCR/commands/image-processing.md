# /image-processing - 画像処理機能実装

## 概要
ISP-673のIGlyOcrExインターフェースを使用した画像処理機能を実装します。2値化、傾き補正、ノイズ除去、黒枠除去など、OCR前処理に必要な画像処理を包括的にサポートします。

## 主な機能

### 1. 2値化処理
- 自動閾値2値化
- 手動閾値2値化
- アダプティブ2値化
- TIFF圧縮保存

### 2. 傾き補正・文書整形
- 自動傾き検出・補正
- 黒枠除去
- 文書領域抽出
- 画質改善

### 3. ノイズ除去・画質改善
- ノイズ除去フィルタ
- モルフォロジー処理
- エッジ強調
- コントラスト調整

## コマンド使用例

```cmd
# 基本画像処理実装
/image-processing

# 高度な前処理機能付き
/image-processing --advanced

# バッチ処理対応
/image-processing --batch

# UI統合版
/image-processing --with-ui

# 高性能版
/image-processing --optimized
```

## 実装内容

### 1. ImageProcessingEngine

```csharp
public class ImageProcessingEngine : IDisposable
{
    private readonly GlyOcrEx _gOcrEx;
    private readonly ILogger _logger;
    private readonly ImageProcessingConfig _config;

    public ImageProcessingEngine(ImageProcessingConfig config, ILogger logger)
    {
        _config = config ?? throw new ArgumentNullException(nameof(config));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _gOcrEx = new GlyOcrEx();
    }

    public ProcessedImage BinarizeImage(string inputPath, BinarizationParameters parameters)
    {
        if (!File.Exists(inputPath))
            throw new FileNotFoundException($"入力画像が見つかりません: {inputPath}");

        try
        {
            int handle = 0;
            int result = _gOcrEx.GetBinaryImage(
                out handle,
                inputPath,
                parameters.Threshold,
                (int)parameters.Method,
                parameters.NoiseReduction ? 1 : 0);

            var processedImage = new ProcessedImage
            {
                Handle = handle,
                Success = result == 0,
                OriginalPath = inputPath,
                ProcessType = ProcessType.Binarization,
                ProcessedAt = DateTime.Now,
                Parameters = parameters
            };

            if (!processedImage.Success)
            {
                processedImage.ErrorCode = result;
                processedImage.ErrorMessage = GetErrorMessage(result);
                _logger.Error($"2値化処理失敗: {inputPath} - エラーコード={result}");
            }
            else
            {
                _logger.Info($"2値化処理成功: {inputPath} - ハンドル={handle}");
            }

            return processedImage;
        }
        catch (Exception ex)
        {
            _logger.Error($"2値化処理例外: {inputPath} - {ex.Message}");
            return ProcessedImage.CreateErrorResult(ex.Message);
        }
    }

    public ProcessedImage CorrectDocumentSkew(string inputPath, SkewCorrectionParameters parameters)
    {
        if (!File.Exists(inputPath))
            throw new FileNotFoundException($"入力画像が見つかりません: {inputPath}");

        try
        {
            int handle = 0;
            int result = _gOcrEx.GetDocumentImageEx(
                out handle,
                inputPath,
                parameters.EnableSkewCorrection ? 1 : 0,
                parameters.RemoveBlackBorder ? 1 : 0,
                parameters.ExtractDocumentArea ? 1 : 0,
                parameters.EnhanceQuality ? 1 : 0);

            var processedImage = new ProcessedImage
            {
                Handle = handle,
                Success = result == 0,
                OriginalPath = inputPath,
                ProcessType = ProcessType.SkewCorrection,
                ProcessedAt = DateTime.Now,
                Parameters = parameters
            };

            if (!processedImage.Success)
            {
                processedImage.ErrorCode = result;
                processedImage.ErrorMessage = GetErrorMessage(result);
                _logger.Error($"傾き補正失敗: {inputPath} - エラーコード={result}");
            }
            else
            {
                _logger.Info($"傾き補正成功: {inputPath} - ハンドル={handle}");
            }

            return processedImage;
        }
        catch (Exception ex)
        {
            _logger.Error($"傾き補正例外: {inputPath} - {ex.Message}");
            return ProcessedImage.CreateErrorResult(ex.Message);
        }
    }

    public ProcessedImage ApplyNoiseReduction(string inputPath, NoiseReductionParameters parameters)
    {
        if (!File.Exists(inputPath))
            throw new FileNotFoundException($"入力画像が見つかりません: {inputPath}");

        try
        {
            int handle = 0;
            int result = _gOcrEx.GetNoiseReductionImage(
                out handle,
                inputPath,
                (int)parameters.FilterType,
                parameters.Strength,
                parameters.PreserveFineDetails ? 1 : 0);

            var processedImage = new ProcessedImage
            {
                Handle = handle,
                Success = result == 0,
                OriginalPath = inputPath,
                ProcessType = ProcessType.NoiseReduction,
                ProcessedAt = DateTime.Now,
                Parameters = parameters
            };

            if (!processedImage.Success)
            {
                processedImage.ErrorCode = result;
                processedImage.ErrorMessage = GetErrorMessage(result);
            }

            return processedImage;
        }
        catch (Exception ex)
        {
            _logger.Error($"ノイズ除去例外: {inputPath} - {ex.Message}");
            return ProcessedImage.CreateErrorResult(ex.Message);
        }
    }

    public void SaveProcessedImage(ProcessedImage image, string outputPath, ImageFormat format, CompressionParameters compression = null)
    {
        if (image?.Handle == 0)
            throw new ArgumentException("無効な画像ハンドル");

        try
        {
            compression = compression ?? CompressionParameters.Default;

            int result = _gOcrEx.OutputImageFile(
                image.Handle,
                outputPath,
                (int)format,
                compression.Quality,
                compression.CompressionType);

            if (result != 0)
            {
                throw new OcrException($"画像保存失敗: エラーコード={result}");
            }

            image.OutputPath = outputPath;
            image.OutputFormat = format;
            
            _logger.Info($"画像保存成功: {outputPath}");
        }
        catch (Exception ex)
        {
            _logger.Error($"画像保存例外: {outputPath} - {ex.Message}");
            throw;
        }
        finally
        {
            // メモリ開放
            if (image.Handle != 0)
            {
                GlobalFree(image.Handle);
                image.Handle = 0;
            }
        }
    }

    public Bitmap ConvertHandleToBitmap(int handle)
    {
        if (handle == 0)
            throw new ArgumentException("無効なハンドル");

        IntPtr lockedPtr = IntPtr.Zero;
        try
        {
            lockedPtr = GlobalLock(handle);
            if (lockedPtr == IntPtr.Zero)
                throw new OcrException("メモリロック失敗");

            // DIBヘッダー解析
            var bitmapInfo = Marshal.PtrToStructure<BitmapInfoHeader>(lockedPtr);
            
            // ビットマップ作成
            var bitmap = CreateBitmapFromDIB(lockedPtr, bitmapInfo);
            
            return bitmap;
        }
        finally
        {
            if (lockedPtr != IntPtr.Zero)
                GlobalUnlock(handle);
        }
    }

    private Bitmap CreateBitmapFromDIB(IntPtr dibPtr, BitmapInfoHeader header)
    {
        // DIBからBitmapオブジェクトを作成
        // ISP-673のDIB形式に基づいて実装
        var bitmap = new Bitmap(header.Width, Math.Abs(header.Height), PixelFormat.Format24bppRgb);
        
        // 画像データをコピー
        var bitmapData = bitmap.LockBits(
            new Rectangle(0, 0, bitmap.Width, bitmap.Height),
            ImageLockMode.WriteOnly,
            PixelFormat.Format24bppRgb);

        try
        {
            var imageDataPtr = IntPtr.Add(dibPtr, Marshal.SizeOf<BitmapInfoHeader>());
            var stride = bitmapData.Stride;
            var imageStride = ((header.Width * header.BitCount + 31) / 32) * 4;

            for (int y = 0; y < Math.Abs(header.Height); y++)
            {
                var srcPtr = IntPtr.Add(imageDataPtr, y * imageStride);
                var dstPtr = IntPtr.Add(bitmapData.Scan0, y * stride);
                CopyMemory(dstPtr, srcPtr, Math.Min(stride, imageStride));
            }
        }
        finally
        {
            bitmap.UnlockBits(bitmapData);
        }

        return bitmap;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalLock(int hMem);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GlobalUnlock(int hMem);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern int GlobalFree(int hMem);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern void CopyMemory(IntPtr dest, IntPtr src, int count);

    public void Dispose()
    {
        _gOcrEx = null;
        _logger?.Info("画像処理エンジン終了");
    }
}
```

### 2. BatchImageProcessor

```csharp
public class BatchImageProcessor
{
    private readonly ImageProcessingEngine _engine;
    private readonly ILogger _logger;
    private readonly CancellationTokenSource _cancellationTokenSource;

    public event EventHandler<ImageProcessProgressEventArgs> ProgressChanged;
    public event EventHandler<ProcessedImage> ImageProcessed;

    public BatchImageProcessor(ImageProcessingEngine engine, ILogger logger)
    {
        _engine = engine ?? throw new ArgumentNullException(nameof(engine));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _cancellationTokenSource = new CancellationTokenSource();
    }

    public async Task<BatchProcessResult> ProcessImagesAsync(
        IEnumerable<string> imagePaths,
        ImageProcessingPipeline pipeline,
        string outputDirectory,
        IProgress<ImageProcessProgressEventArgs> progress = null)
    {
        var imageList = imagePaths.ToList();
        var batchResult = new BatchProcessResult
        {
            TotalFiles = imageList.Count,
            StartTime = DateTime.Now,
            OutputDirectory = outputDirectory
        };

        if (!Directory.Exists(outputDirectory))
            Directory.CreateDirectory(outputDirectory);

        try
        {
            for (int i = 0; i < imageList.Count; i++)
            {
                if (_cancellationTokenSource.Token.IsCancellationRequested)
                    break;

                var imagePath = imageList[i];
                var fileName = Path.GetFileNameWithoutExtension(imagePath);
                var progressArgs = new ImageProcessProgressEventArgs
                {
                    CurrentIndex = i,
                    TotalCount = imageList.Count,
                    CurrentFile = Path.GetFileName(imagePath),
                    PercentComplete = (int)((double)i / imageList.Count * 100)
                };

                progress?.Report(progressArgs);
                ProgressChanged?.Invoke(this, progressArgs);

                try
                {
                    var processedImage = await ProcessSingleImageAsync(imagePath, pipeline);
                    
                    if (processedImage.Success)
                    {
                        var outputPath = Path.Combine(outputDirectory, $"{fileName}_processed.tif");
                        _engine.SaveProcessedImage(processedImage, outputPath, ImageFormat.Tiff);
                        
                        batchResult.SuccessCount++;
                        batchResult.ProcessedImages.Add(outputPath);
                    }
                    else
                    {
                        batchResult.FailureCount++;
                        batchResult.Errors.Add($"{imagePath}: {processedImage.ErrorMessage}");
                    }

                    ImageProcessed?.Invoke(this, processedImage);
                }
                catch (Exception ex)
                {
                    batchResult.FailureCount++;
                    batchResult.Errors.Add($"{imagePath}: {ex.Message}");
                    _logger.Error($"画像処理エラー [{imagePath}]: {ex.Message}");
                }
            }
        }
        finally
        {
            batchResult.EndTime = DateTime.Now;
            batchResult.ProcessingTime = batchResult.EndTime - batchResult.StartTime;
        }

        return batchResult;
    }

    private async Task<ProcessedImage> ProcessSingleImageAsync(string imagePath, ImageProcessingPipeline pipeline)
    {
        return await Task.Factory.StartNew(() =>
        {
            ProcessedImage currentImage = null;

            try
            {
                // パイプライン処理
                foreach (var step in pipeline.Steps)
                {
                    switch (step.Type)
                    {
                        case ProcessingStepType.Binarization:
                            currentImage = _engine.BinarizeImage(
                                currentImage?.OutputPath ?? imagePath, 
                                step.BinarizationParameters);
                            break;

                        case ProcessingStepType.SkewCorrection:
                            currentImage = _engine.CorrectDocumentSkew(
                                currentImage?.OutputPath ?? imagePath,
                                step.SkewCorrectionParameters);
                            break;

                        case ProcessingStepType.NoiseReduction:
                            currentImage = _engine.ApplyNoiseReduction(
                                currentImage?.OutputPath ?? imagePath,
                                step.NoiseReductionParameters);
                            break;
                    }

                    if (!currentImage.Success)
                        break;
                }

                return currentImage ?? ProcessedImage.CreateErrorResult("処理ステップが定義されていません");
            }
            catch (Exception ex)
            {
                return ProcessedImage.CreateErrorResult(ex.Message);
            }
        });
    }

    public void Cancel()
    {
        _cancellationTokenSource.Cancel();
    }
}
```

### 3. ImageProcessingPipelineBuilder

```csharp
public class ImageProcessingPipelineBuilder
{
    private readonly List<ProcessingStep> _steps = new List<ProcessingStep>();

    public static ImageProcessingPipelineBuilder Create()
    {
        return new ImageProcessingPipelineBuilder();
    }

    public ImageProcessingPipelineBuilder AddBinarization(int threshold = -1, BinarizationMethod method = BinarizationMethod.Auto)
    {
        _steps.Add(new ProcessingStep
        {
            Type = ProcessingStepType.Binarization,
            BinarizationParameters = new BinarizationParameters
            {
                Threshold = threshold,
                Method = method,
                NoiseReduction = true
            }
        });
        return this;
    }

    public ImageProcessingPipelineBuilder AddSkewCorrection(bool removeBlackBorder = true, bool extractDocArea = false)
    {
        _steps.Add(new ProcessingStep
        {
            Type = ProcessingStepType.SkewCorrection,
            SkewCorrectionParameters = new SkewCorrectionParameters
            {
                EnableSkewCorrection = true,
                RemoveBlackBorder = removeBlackBorder,
                ExtractDocumentArea = extractDocArea,
                EnhanceQuality = true
            }
        });
        return this;
    }

    public ImageProcessingPipelineBuilder AddNoiseReduction(NoiseFilterType filterType = NoiseFilterType.Median, int strength = 3)
    {
        _steps.Add(new ProcessingStep
        {
            Type = ProcessingStepType.NoiseReduction,
            NoiseReductionParameters = new NoiseReductionParameters
            {
                FilterType = filterType,
                Strength = strength,
                PreserveFineDetails = true
            }
        });
        return this;
    }

    public ImageProcessingPipeline Build()
    {
        return new ImageProcessingPipeline { Steps = _steps.ToList() };
    }

    // プリセットパイプライン
    public static ImageProcessingPipeline StandardOcrPreprocessing()
    {
        return Create()
            .AddSkewCorrection(removeBlackBorder: true)
            .AddBinarization(method: BinarizationMethod.Otsu)
            .AddNoiseReduction(NoiseFilterType.Median, 2)
            .Build();
    }

    public static ImageProcessingPipeline HighQualityPreprocessing()
    {
        return Create()
            .AddSkewCorrection(removeBlackBorder: true, extractDocArea: true)
            .AddNoiseReduction(NoiseFilterType.Gaussian, 1)
            .AddBinarization(method: BinarizationMethod.Adaptive)
            .Build();
    }

    public static ImageProcessingPipeline FastPreprocessing()
    {
        return Create()
            .AddBinarization(method: BinarizationMethod.Fixed, threshold: 128)
            .Build();
    }
}
```

## データ構造

### ProcessedImage
```csharp
public class ProcessedImage
{
    public int Handle { get; set; }
    public bool Success { get; set; }
    public string OriginalPath { get; set; }
    public string OutputPath { get; set; }
    public ProcessType ProcessType { get; set; }
    public ImageFormat OutputFormat { get; set; }
    public DateTime ProcessedAt { get; set; }
    public object Parameters { get; set; }
    public int ErrorCode { get; set; }
    public string ErrorMessage { get; set; }
}
```

### BitmapInfoHeader
```csharp
[StructLayout(LayoutKind.Sequential)]
public struct BitmapInfoHeader
{
    public int Size;
    public int Width;
    public int Height;
    public short Planes;
    public short BitCount;
    public int Compression;
    public int SizeImage;
    public int XPixelsPerMeter;
    public int YPixelsPerMeter;
    public int ColorsUsed;
    public int ColorsImportant;
}
```

## 使用例

```csharp
// 基本的な前処理パイプライン
var pipeline = ImageProcessingPipelineBuilder
    .StandardOcrPreprocessing();

var batchProcessor = new BatchImageProcessor(engine, logger);
var result = await batchProcessor.ProcessImagesAsync(
    imageFiles, 
    pipeline, 
    outputDirectory);

// カスタムパイプライン
var customPipeline = ImageProcessingPipelineBuilder.Create()
    .AddSkewCorrection(removeBlackBorder: true)
    .AddBinarization(method: BinarizationMethod.Otsu)
    .AddNoiseReduction(NoiseFilterType.Median)
    .Build();
```

## 成功時の出力

```
✅ 画像処理機能実装完了

実装内容:
✅ ImageProcessingEngine - 画像処理エンジン
✅ BatchImageProcessor - バッチ処理
✅ ImageProcessingPipelineBuilder - パイプライン構築

処理機能:
✅ 2値化処理 (自動/手動閾値)
✅ 傾き補正・黒枠除去
✅ ノイズ除去・画質改善
✅ DIB to Bitmap変換

バッチ処理:
✅ パイプライン処理
✅ 進捗報告
✅ エラーハンドリング

メモリ管理:
✅ 適切なGlobalFree呼び出し
✅ COM相互運用安全実装
✅ リソース自動開放

🚀 Next: /ocr-testing でOCR機能テストを実装
```