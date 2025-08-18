# /ocr-integration - OCR統合専用コマンド（ISP-673/GloryOCR）

## 概要
ISP-673 GloryOCR、Tesseract、Azure Cognitive Services OCRなど、様々なOCRエンジンとの統合を専門的に扱うコマンドです。

## 使用方法
```bash
/ocr-integration [engine] [action] [options]

# 使用例
/ocr-integration isp673 setup --x86
/ocr-integration isp673 process invoice.tif --area-ocr
/ocr-integration tesseract setup --lang=jpn
/ocr-integration azure configure --api-key=xxx
```

## パラメータ

### エンジン
- `isp673` - ISP-673 GloryOCR（帳票専用）
- `tesseract` - Tesseract OCR（オープンソース）
- `azure` - Azure Cognitive Services
- `aws` - AWS Textract
- `google` - Google Cloud Vision

### アクション
- `setup` - OCRエンジンセットアップ
- `process` - OCR処理実行
- `configure` - 設定調整
- `test` - 認識テスト
- `optimize` - 精度最適化

## ISP-673 GloryOCR統合

### 1. DLL設定（x86必須）
```xml
<!-- app.config -->
<configuration>
  <startup>
    <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.0"/>
  </startup>
  <runtime>
    <gcAllowVeryLargeObjects enabled="true"/>
  </runtime>
</configuration>

<!-- プロジェクト設定 -->
<PropertyGroup>
  <PlatformTarget>x86</PlatformTarget>
  <Prefer32Bit>true</Prefer32Bit>
</PropertyGroup>
```

### 2. P/Invoke定義
```csharp
public static class GloryOcrApi
{
    // 初期化
    [DllImport("GloryOcrMain4.dll", CallingConvention = CallingConvention.StdCall)]
    public static extern int GloryOcrInit(string configPath);
    
    // OCRハンドル作成
    [DllImport("GloryOcrMain4.dll")]
    public static extern IntPtr GloryOcrCreate();
    
    // 画像設定
    [DllImport("GloryOcrMain4.dll")]
    public static extern int GloryOcrSetImage(IntPtr handle, string imagePath);
    
    // エリアOCR設定
    [DllImport("GloryOcrMain4.dll")]
    public static extern int GloryOcrSetArea(
        IntPtr handle, 
        int x, int y, 
        int width, int height);
    
    // 認識実行
    [DllImport("GloryOcrMain4.dll")]
    public static extern int GloryOcrRecognize(
        IntPtr handle, 
        StringBuilder text, 
        int maxLength);
    
    // バーコード認識
    [DllImport("GloryOcrMain4.dll")]
    public static extern int GloryOcrReadBarcode(
        IntPtr handle,
        int barcodeType,
        StringBuilder result,
        int maxLength);
    
    // 解放
    [DllImport("GloryOcrMain4.dll")]
    public static extern void GloryOcrDestroy(IntPtr handle);
}
```

### 3. 帳票OCR実装
```csharp
public class InvoiceOcr
{
    private readonly Dictionary<string, Rectangle> _areas = new()
    {
        ["invoice_number"] = new Rectangle(100, 50, 200, 30),
        ["date"] = new Rectangle(400, 50, 150, 30),
        ["customer_name"] = new Rectangle(100, 120, 300, 30),
        ["amount"] = new Rectangle(400, 350, 150, 30),
        ["tax"] = new Rectangle(400, 380, 150, 30),
        ["total"] = new Rectangle(400, 410, 150, 30)
    };
    
    public InvoiceData ProcessInvoice(string imagePath)
    {
        IntPtr handle = IntPtr.Zero;
        try
        {
            // 初期化
            GloryOcrApi.GloryOcrInit(@"C:\ISP673\Config");
            handle = GloryOcrApi.GloryOcrCreate();
            
            // 画像設定
            GloryOcrApi.GloryOcrSetImage(handle, imagePath);
            
            // 前処理
            ApplyPreprocessing(handle);
            
            var invoice = new InvoiceData();
            
            // エリアごとにOCR実行
            foreach (var area in _areas)
            {
                GloryOcrApi.GloryOcrSetArea(
                    handle,
                    area.Value.X,
                    area.Value.Y,
                    area.Value.Width,
                    area.Value.Height
                );
                
                var text = new StringBuilder(1000);
                GloryOcrApi.GloryOcrRecognize(handle, text, text.Capacity);
                
                SetInvoiceField(invoice, area.Key, text.ToString());
            }
            
            // バーコード読み取り
            var barcode = new StringBuilder(100);
            GloryOcrApi.GloryOcrReadBarcode(handle, 1, barcode, barcode.Capacity);
            invoice.BarcodeData = barcode.ToString();
            
            return invoice;
        }
        finally
        {
            if (handle != IntPtr.Zero)
                GloryOcrApi.GloryOcrDestroy(handle);
        }
    }
    
    private void ApplyPreprocessing(IntPtr handle)
    {
        // ノイズ除去、傾き補正、二値化などの前処理
    }
}
```

## Tesseract OCR統合

### セットアップと使用
```csharp
public class TesseractIntegration
{
    private readonly TesseractEngine _engine;
    
    public TesseractIntegration()
    {
        // 日本語対応
        _engine = new TesseractEngine(@"./tessdata", "jpn", EngineMode.Default);
        
        // 精度向上設定
        _engine.SetVariable("tessedit_char_whitelist", "0123456789あ-ん一-龯");
        _engine.SetVariable("preserve_interword_spaces", "1");
    }
    
    public string ProcessImage(string imagePath)
    {
        using var img = Pix.LoadFromFile(imagePath);
        using var page = _engine.Process(img);
        
        var text = page.GetText();
        var confidence = page.GetMeanConfidence();
        
        if (confidence < 0.7)
        {
            // 前処理を強化して再試行
            using var processed = PreprocessImage(img);
            using var page2 = _engine.Process(processed);
            text = page2.GetText();
        }
        
        return text;
    }
}
```

## Azure Cognitive Services OCR

### 高度なOCR機能
```csharp
public class AzureOcrIntegration
{
    private readonly ComputerVisionClient _client;
    
    public AzureOcrIntegration(string apiKey, string endpoint)
    {
        _client = new ComputerVisionClient(
            new ApiKeyServiceClientCredentials(apiKey))
        {
            Endpoint = endpoint
        };
    }
    
    public async Task<OcrResult> ProcessDocumentAsync(string imagePath)
    {
        using var stream = File.OpenRead(imagePath);
        
        // Read API（大量テキスト対応）
        var operation = await _client.ReadInStreamAsync(stream);
        var operationId = operation.OperationLocation.Split('/').Last();
        
        // 結果取得
        ReadOperationResult result;
        do
        {
            await Task.Delay(1000);
            result = await _client.GetReadResultAsync(Guid.Parse(operationId));
        }
        while (result.Status == OperationStatusCodes.Running);
        
        return ExtractText(result);
    }
    
    public async Task<FormData> ProcessFormAsync(string imagePath)
    {
        // Form Recognizer（帳票専用）
        var formClient = new FormRecognizerClient(
            new Uri(_endpoint),
            new AzureKeyCredential(_apiKey));
        
        using var stream = File.OpenRead(imagePath);
        var response = await formClient.StartRecognizeInvoicesAsync(stream);
        var result = await response.WaitForCompletionAsync();
        
        return ExtractFormData(result.Value);
    }
}
```

## OCR精度最適化

### 前処理技術
```csharp
public class OcrPreprocessor
{
    public Bitmap PreprocessImage(Bitmap original)
    {
        var processed = original;
        
        // 1. グレースケール変換
        processed = ConvertToGrayscale(processed);
        
        // 2. ノイズ除去
        processed = RemoveNoise(processed);
        
        // 3. 傾き補正
        var angle = DetectSkew(processed);
        if (Math.Abs(angle) > 0.5)
        {
            processed = RotateImage(processed, -angle);
        }
        
        // 4. 二値化（大津の手法）
        processed = ApplyOtsuThreshold(processed);
        
        // 5. モルフォロジー演算
        processed = ApplyMorphology(processed);
        
        return processed;
    }
    
    private Bitmap ApplyOtsuThreshold(Bitmap image)
    {
        // 大津の二値化アルゴリズム実装
        var histogram = CalculateHistogram(image);
        var threshold = CalculateOtsuThreshold(histogram);
        return ApplyThreshold(image, threshold);
    }
}
```

## 出力フォーマット

### OCR結果構造
```json
{
  "status": "success",
  "engine": "ISP-673",
  "confidence": 0.95,
  "processingTime": 1250,
  "pages": [
    {
      "pageNumber": 1,
      "text": "認識されたテキスト",
      "areas": [
        {
          "id": "invoice_number",
          "text": "INV-2025-001",
          "confidence": 0.98,
          "bounds": {
            "x": 100,
            "y": 50,
            "width": 200,
            "height": 30
          }
        }
      ],
      "barcodes": [
        {
          "type": "QR",
          "data": "https://example.com/invoice/123",
          "position": {"x": 450, "y": 50}
        }
      ]
    }
  ]
}
```

## トラブルシューティング

| 問題 | 原因 | 解決策 |
|------|------|--------|
| DLL読み込みエラー | x64で実行 | PlatformTarget=x86設定 |
| 文字化け | 文字コード | UTF-8変換、適切な言語設定 |
| 低精度 | 画像品質 | 前処理強化、高解像度スキャン |
| メモリリーク | ハンドル未解放 | using文使用、明示的Dispose |

## 管理責任
- **管理部門**: システム開発部
- **専門性**: OCR技術に特化

## 関連コマンド
- `/image-processing` - 画像前処理
- `/form-recognition` - 帳票認識
- `/barcode-reading` - バーコード読み取り

---
*このコマンドはシステム開発部が管理します。OCR技術に特化しています。*