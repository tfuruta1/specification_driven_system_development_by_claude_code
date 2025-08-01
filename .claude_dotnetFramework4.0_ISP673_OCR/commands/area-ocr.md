# /area-ocr - エリアOCR機能実装

## 概要
ISP-673のIGlyOcrExインターフェースを使用したエリアOCR機能を実装します。座標指定による任意領域OCR、RPFファイル活用、バーコード認識を包括的にサポートします。

## 主な機能

### 1. エリアOCR (RecogField)
- RPFファイルベースOCR
- プロジェクト連携処理
- パラメータセット活用
- 高精度認識

### 2. 拡張エリアOCR (RecogFieldEx)
- 座標指定による自由領域OCR
- 詳細OCRパラメータ設定
- 英数カナOCR
- 日本語OCR
- バーコード認識

### 3. 辞書管理・リソース管理
- 文字認識辞書管理
- 知識辞書管理
- RPFファイル管理
- メモリリソース管理

## コマンド使用例

```cmd
# 基本エリアOCR実装
/area-ocr

# 拡張エリアOCR実装
/area-ocr --extended

# バーコード認識機能付き
/area-ocr --with-barcode

# 日本語OCR対応
/area-ocr --japanese

# UI統合版
/area-ocr --with-ui

# 高性能版
/area-ocr --high-performance
```

## 実装内容

### 1. AreaOcrEngine

```csharp
public class AreaOcrEngine : IDisposable
{
    private readonly GlyOcrEx _gOcrEx;
    private readonly ILogger _logger;
    private readonly AreaOcrConfig _config;
    private bool _charDicLoaded;
    private bool _knowledgeDicLoaded;

    public AreaOcrEngine(AreaOcrConfig config, ILogger logger)
    {
        _config = config ?? throw new ArgumentNullException(nameof(config));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _gOcrEx = new GlyOcrEx();
    }

    public async Task<bool> InitializeAsync()
    {
        return await Task.Factory.StartNew(() =>
        {
            try
            {
                // 文字認識辞書読み込み
                int charDicResult = _gOcrEx.LoadCharDic(_config.CharacterDictionaryPath);
                if (charDicResult != 0)
                {
                    _logger.Error($"文字辞書読み込み失敗: エラーコード={charDicResult}");
                    return false;
                }
                _charDicLoaded = true;

                // 知識辞書読み込み（日本語OCR使用時）
                if (_config.UseJapaneseOcr && !string.IsNullOrEmpty(_config.KnowledgeDictionaryPath))
                {
                    int knowledgeDicResult = _gOcrEx.LoadKnowledgeDic(_config.KnowledgeDictionaryPath);
                    if (knowledgeDicResult != 0)
                    {
                        _logger.Error($"知識辞書読み込み失敗: エラーコード={knowledgeDicResult}");
                        return false;
                    }
                    _knowledgeDicLoaded = true;
                }

                _logger.Info("エリアOCR初期化成功");
                return true;
            }
            catch (Exception ex)
            {
                _logger.Error($"エリアOCR初期化例外: {ex.Message}");
                return false;
            }
        });
    }

    public AreaOcrResult RecognizeArea(string imagePath, AreaOcrParameters parameters)
    {
        if (!_charDicLoaded)
            throw new InvalidOperationException("文字辞書が読み込まれていません");

        if (!File.Exists(imagePath))
            throw new FileNotFoundException($"画像ファイルが見つかりません: {imagePath}");

        try
        {
            // 拡張エリアOCR実行
            var info = CreateInfoArray(imagePath, parameters);
            int handle = 0;
            int result = _gOcrEx.RecogFieldEx(out handle, info);

            var areaResult = new AreaOcrResult
            {
                Success = result == 0,
                Handle = handle,
                ImagePath = imagePath,
                ProcessedAt = DateTime.Now,
                Parameters = parameters
            };

            if (areaResult.Success && handle != 0)
            {
                ExtractResultFromHandle(areaResult, handle);
            }
            else
            {
                areaResult.ErrorCode = result;
                areaResult.ErrorMessage = GetErrorMessage(result);
            }

            _logger.Info($"エリアOCR完了: {imagePath} -> 結果={result}");
            return areaResult;
        }
        catch (Exception ex)
        {
            _logger.Error($"エリアOCRエラー: {imagePath} - {ex.Message}");
            return AreaOcrResult.CreateErrorResult(ex.Message);
        }
    }

    public AreaOcrResult RecognizeAreaWithRpf(string imagePath, string rpfPath, int parameterId)
    {
        if (!_charDicLoaded)
            throw new InvalidOperationException("文字辞書が読み込まれていません");

        try
        {
            // RPFファイル読み込み
            int loadResult = _gOcrEx.LoadRpfFile(rpfPath);
            if (loadResult != 0)
                throw new OcrException($"RPFファイル読み込み失敗: {loadResult}");

            // エリアOCR実行
            var info = new object[] { imagePath, 0, 0 }; // 基本情報のみ
            int handle = 0;
            int result = _gOcrEx.RecogField(out handle, parameterId, 1, info);

            var areaResult = new AreaOcrResult
            {
                Success = result == 0,
                Handle = handle,
                ImagePath = imagePath,
                RpfPath = rpfPath,
                ParameterId = parameterId,
                ProcessedAt = DateTime.Now
            };

            if (areaResult.Success && handle != 0)
            {
                ExtractResultFromHandle(areaResult, handle);
            }

            // RPFファイル開放
            _gOcrEx.UnLoadRpfFile();

            return areaResult;
        }
        catch (Exception ex)
        {
            _logger.Error($"RPFエリアOCRエラー: {imagePath} - {ex.Message}");
            return AreaOcrResult.CreateErrorResult(ex.Message);
        }
    }

    private object[] CreateInfoArray(string imagePath, AreaOcrParameters parameters)
    {
        var info = new object[20];
        
        // 基本設定
        info[0] = imagePath;                    // イメージファイル名
        info[1] = parameters.Resolution;         // 入力解像度
        info[2] = parameters.Direction;          // 処理方向
        info[3] = parameters.Rectangle.X;       // 矩形X座標
        info[4] = parameters.Rectangle.Y;       // 矩形Y座標
        info[5] = parameters.Rectangle.Width;   // 矩形幅
        info[6] = parameters.Rectangle.Height;  // 矩形高さ
        info[7] = (int)parameters.ProcessType;  // 処理内容
        
        // フレーム設定
        info[8] = parameters.FrameCount;        // 枠の個数/最大文字数
        info[9] = (int)parameters.FrameType;    // 枠の種類
        info[10] = (int)parameters.WriteMethod; // 記入方法
        info[11] = (int)parameters.CharacterType; // 字種
        
        // 日本語OCR設定
        if (parameters.ProcessType == ProcessType.JapaneseOcr)
        {
            info[12] = parameters.KnowledgeDictionaryName; // 知識辞書名称
            info[13] = parameters.LimitedCharacters;       // 限定文字列
        }
        
        // バーコード設定
        if (parameters.ProcessType == ProcessType.Barcode)
        {
            info[14] = (int)parameters.BarcodeType;        // バーコード種類
            info[15] = parameters.BarcodeDirection;        // バーコード方向
        }
        
        // その他設定
        info[16] = (int)parameters.ProcessingSpeed;       // 処理速度
        info[17] = parameters.Threshold;                  // 閾値
        info[18] = parameters.NoiseReduction ? 1 : 0;     // ノイズ除去
        info[19] = parameters.SkewCorrection ? 1 : 0;     // 傾き補正
        
        return info;
    }

    private void ExtractResultFromHandle(AreaOcrResult result, int handle)
    {
        if (handle == 0) return;

        try
        {
            // グローバルメモリロック
            IntPtr lockedPtr = GlobalLock(handle);
            if (lockedPtr == IntPtr.Zero)
            {
                result.ErrorMessage = "メモリロック失敗";
                return;
            }

            // 結果データ解析（ISP-673の結果構造に依存）
            // ここでハンドルから結果文字列を抽出
            result.RecognizedText = ExtractTextFromMemory(lockedPtr);
            result.Confidence = ExtractConfidenceFromMemory(lockedPtr);
            
            // グローバルメモリアンロック
            GlobalUnlock(handle);
            
            _logger.Debug($"エリアOCR結果抽出: テキスト='{result.RecognizedText}', 信頼度={result.Confidence}%");
        }
        catch (Exception ex)
        {
            _logger.Error($"結果抽出エラー: {ex.Message}");
            result.ErrorMessage = $"結果抽出失敗: {ex.Message}";
        }
        finally
        {
            // メモリ開放
            if (handle != 0)
            {
                GlobalFree(handle);
                result.Handle = 0;
            }
        }
    }

    private string ExtractTextFromMemory(IntPtr ptr)
    {
        // ISP-673の結果構造に基づいてテキストを抽出
        // 実際の実装では結果構造のドキュメントに基づいて実装
        return Marshal.PtrToStringAnsi(ptr) ?? string.Empty;
    }

    private int ExtractConfidenceFromMemory(IntPtr ptr)
    {
        // 信頼度情報の抽出（構造体の定義に依存）
        return 95; // プレースホルダー
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalLock(int hMem);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GlobalUnlock(int hMem);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern int GlobalFree(int hMem);

    public void Dispose()
    {
        try
        {
            if (_knowledgeDicLoaded)
            {
                _gOcrEx?.UnloadKnowledgeDic();
                _knowledgeDicLoaded = false;
            }

            if (_charDicLoaded)
            {
                _gOcrEx?.UnloadCharDic();
                _charDicLoaded = false;
            }

            _logger.Info("エリアOCRエンジン正常終了");
        }
        catch (Exception ex)
        {
            _logger.Error($"エリアOCRエンジン終了エラー: {ex.Message}");
        }
    }
}
```

### 2. BarcodeRecognitionService

```csharp
public class BarcodeRecognitionService
{
    private readonly AreaOcrEngine _engine;
    private readonly ILogger _logger;

    public BarcodeRecognitionService(AreaOcrEngine engine, ILogger logger)
    {
        _engine = engine ?? throw new ArgumentNullException(nameof(engine));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public AreaOcrResult RecognizeBarcode(string imagePath, BarcodeParameters parameters)
    {
        var areaParameters = new AreaOcrParameters
        {
            ProcessType = ProcessType.Barcode,
            Rectangle = parameters.Rectangle,
            BarcodeType = parameters.BarcodeType,
            BarcodeDirection = parameters.Direction,
            Resolution = parameters.Resolution
        };

        var result = _engine.RecognizeArea(imagePath, areaParameters);
        
        if (result.Success)
        {
            result.BarcodeType = parameters.BarcodeType;
            result.BarcodeData = result.RecognizedText;
            
            // バーコードデータ検証
            ValidateBarcodeData(result, parameters);
        }

        return result;
    }

    public List<AreaOcrResult> RecognizeMultipleBarcodes(string imagePath, List<BarcodeParameters> barcodeList)
    {
        var results = new List<AreaOcrResult>();

        foreach (var barcodeParam in barcodeList)
        {
            try
            {
                var result = RecognizeBarcode(imagePath, barcodeParam);
                results.Add(result);
            }
            catch (Exception ex)
            {
                _logger.Error($"マルチバーコード認識エラー: {ex.Message}");
                results.Add(AreaOcrResult.CreateErrorResult(ex.Message));
            }
        }

        return results;
    }

    private void ValidateBarcodeData(AreaOcrResult result, BarcodeParameters parameters)
    {
        if (string.IsNullOrEmpty(result.BarcodeData))
        {
            result.ValidationWarnings.Add("バーコードデータが空です");
            return;
        }

        // バーコード種別固有の検証
        switch (parameters.BarcodeType)
        {
            case BarcodeType.Code39:
                ValidateCode39(result);
                break;
            case BarcodeType.Code128:
                ValidateCode128(result);
                break;
            case BarcodeType.QRCode:
                ValidateQRCode(result);
                break;
        }
    }

    private void ValidateCode39(AreaOcrResult result)
    {
        // Code39の検証ロジック
        if (!Regex.IsMatch(result.BarcodeData, @"^[A-Z0-9\-\.\s\$\/\+%]+$"))
        {
            result.ValidationWarnings.Add("Code39の文字セットに含まれない文字があります");
        }
    }

    private void ValidateCode128(AreaOcrResult result)
    {
        // Code128の検証ロジック
        if (result.BarcodeData.Length < 1)
        {
            result.ValidationWarnings.Add("Code128データが短すぎます");
        }
    }

    private void ValidateQRCode(AreaOcrResult result)
    {
        // QRコードの検証ロジック
        if (result.BarcodeData.Length > 7089)
        {
            result.ValidationWarnings.Add("QRコードデータが長すぎます");
        }
    }
}
```

### 3. AreaOcrParameterBuilder

```csharp
public class AreaOcrParameterBuilder
{
    private AreaOcrParameters _parameters;

    public AreaOcrParameterBuilder()
    {
        _parameters = new AreaOcrParameters();
    }

    public static AreaOcrParameterBuilder Create()
    {
        return new AreaOcrParameterBuilder();
    }

    public AreaOcrParameterBuilder ForEnglishNumeric()
    {
        _parameters.ProcessType = ProcessType.EnglishNumericOcr;
        _parameters.CharacterType = CharacterType.AlphaNumeric;
        return this;
    }

    public AreaOcrParameterBuilder ForJapanese(string knowledgeDictionary = null)
    {
        _parameters.ProcessType = ProcessType.JapaneseOcr;
        _parameters.CharacterType = CharacterType.Japanese;
        _parameters.KnowledgeDictionaryName = knowledgeDictionary;
        return this;
    }

    public AreaOcrParameterBuilder ForBarcode(BarcodeType barcodeType)
    {
        _parameters.ProcessType = ProcessType.Barcode;
        _parameters.BarcodeType = barcodeType;
        return this;
    }

    public AreaOcrParameterBuilder InRectangle(int x, int y, int width, int height)
    {
        _parameters.Rectangle = new Rectangle(x, y, width, height);
        return this;
    }

    public AreaOcrParameterBuilder WithResolution(int resolution)
    {
        _parameters.Resolution = resolution;
        return this;
    }

    public AreaOcrParameterBuilder WithFrameCount(int count)
    {
        _parameters.FrameCount = count;
        return this;
    }

    public AreaOcrParameterBuilder WithNoiseReduction(bool enable = true)
    {
        _parameters.NoiseReduction = enable;
        return this;
    }

    public AreaOcrParameterBuilder WithSkewCorrection(bool enable = true)
    {
        _parameters.SkewCorrection = enable;
        return this;
    }

    public AreaOcrParameterBuilder WithHighAccuracy()
    {
        _parameters.ProcessingSpeed = ProcessingSpeed.HighAccuracy;
        return this;
    }

    public AreaOcrParameterBuilder WithHighSpeed()
    {
        _parameters.ProcessingSpeed = ProcessingSpeed.HighSpeed;
        return this;
    }

    public AreaOcrParameters Build()
    {
        return _parameters;
    }
}
```

## 使用例

```csharp
// 英数カナOCR
var englishParams = AreaOcrParameterBuilder.Create()
    .ForEnglishNumeric()
    .InRectangle(100, 200, 300, 50)
    .WithResolution(300)
    .WithHighAccuracy()
    .Build();

var result = engine.RecognizeArea("form.jpg", englishParams);

// 日本語OCR
var japaneseParams = AreaOcrParameterBuilder.Create()
    .ForJapanese("standard.dic")
    .InRectangle(50, 300, 400, 100)
    .WithNoiseReduction()
    .Build();

var japaneseResult = engine.RecognizeArea("japanese_form.jpg", japaneseParams);

// バーコード認識
var barcodeParams = AreaOcrParameterBuilder.Create()
    .ForBarcode(BarcodeType.Code128)
    .InRectangle(200, 50, 200, 80)
    .Build();

var barcodeResult = engine.RecognizeArea("barcode.jpg", barcodeParams);
```

## 成功時の出力

```
✅ エリアOCR機能実装完了

実装内容:
✅ AreaOcrEngine - エリアOCRエンジン
✅ BarcodeRecognitionService - バーコード認識
✅ AreaOcrParameterBuilder - パラメータビルダー

機能:
✅ 座標指定エリアOCR
✅ RPFファイル連携OCR
✅ バーコード認識 (Code39/128/QR)
✅ 日本語OCR対応
✅ 英数カナOCR

安全性:
✅ 適切なメモリ管理
✅ COM相互運用安全実装
✅ エラーハンドリング

🚀 Next: /image-processing で画像処理機能を実装
```