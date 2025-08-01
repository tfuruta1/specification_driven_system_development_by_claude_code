# /ocr-interface - OCRインターフェース実装支援

## 概要
ISP-673のIGlyOcr、IGlyOcrExインターフェースを使用したOCRサービス実装を支援します。COM相互運用とメモリ管理を適切に実装します。

## 主な機能

### 1. IGlyOcr (標準帳票OCR) 実装支援
- 初期化・終了処理実装
- グループ処理実装
- 帳票認識実装
- 結果取得実装

### 2. IGlyOcrEx (エリアOCR・画像処理) 実装支援
- 辞書管理実装
- エリアOCR実装
- 画像処理実装
- メモリ管理実装

### 3. COM相互運用安全実装
- COMオブジェクトライフサイクル管理
- メモリリーク防止
- 例外安全実装
- リソース自動開放

## コマンド使用例

```cmd
# 標準帳票OCR実装
/ocr-interface --type=form

# エリアOCR実装
/ocr-interface --type=area

# 画像処理実装
/ocr-interface --type=image

# 全インターフェース実装
/ocr-interface --all

# テストコード含む実装
/ocr-interface --with-tests
```

## 実装パターン

### 1. FormRecognitionService (IGlyOcr)

```csharp
public class FormRecognitionService : IDisposable
{
    private GlyOcr _gOcr;
    private bool _initialized = false;

    public void Initialize(string libraryPath, string projectPath)
    {
        _gOcr = new GlyOcr();
        int result = _gOcr.init(libraryPath, projectPath);
        if (result != 0)
            throw new OcrException($"初期化失敗: {result}");
        _initialized = true;
    }

    public OcrResult RecognizeDocument(string imagePath, int groupId = 2)
    {
        if (!_initialized)
            throw new InvalidOperationException("OCRが初期化されていません");

        _gOcr.SetGroup(groupId);
        int docId = 0;
        int result = _gOcr.RecogDocumentFn(ref docId, imagePath);
        
        return CreateOcrResult(docId, result);
    }

    private OcrResult CreateOcrResult(int docId, int result)
    {
        var ocrResult = new OcrResult
        {
            DocumentId = docId,
            Success = result == 0,
            DocumentName = _gOcr.DocumentName,
            RejectCode = _gOcr.DocumentRejectCode
        };

        // フィールド結果取得
        for (int i = 0; i < _gOcr.FieldNum; i++)
        {
            var field = new FieldResult
            {
                Id = _gOcr.get_FieldID(i),
                Name = _gOcr.get_FieldName(i),
                Text = _gOcr.get_FieldResult(i)
            };
            ocrResult.Fields.Add(field);
        }

        return ocrResult;
    }

    public void Dispose()
    {
        if (_initialized)
        {
            _gOcr?.FreeGroup();
            _gOcr?.exit();
            _initialized = false;
        }
        _gOcr = null;
    }
}
```

### 2. AreaOcrService (IGlyOcrEx)

```csharp
public class AreaOcrService : IDisposable
{
    private GlyOcrEx _gOcrEx;
    private bool _charDicLoaded = false;

    public void LoadCharacterDictionary(string dicPath)
    {
        _gOcrEx = new GlyOcrEx();
        int result = _gOcrEx.LoadCharDic(dicPath);
        if (result != 0)
            throw new OcrException($"文字辞書読み込み失敗: {result}");
        _charDicLoaded = true;
    }

    public AreaOcrResult RecognizeArea(string imagePath, OcrParameters parameters)
    {
        if (!_charDicLoaded)
            throw new InvalidOperationException("文字辞書が読み込まれていません");

        var info = CreateInfoArray(imagePath, parameters);
        int handle = 0;
        int result = _gOcrEx.RecogFieldEx(out handle, info);

        var areaResult = new AreaOcrResult
        {
            Success = result == 0,
            Handle = handle,
            Text = ExtractTextFromHandle(handle)
        };

        // メモリ開放
        if (handle != 0)
            GlobalFree(handle);

        return areaResult;
    }

    private object[] CreateInfoArray(string imagePath, OcrParameters parameters)
    {
        var info = new object[20];
        info[0] = imagePath;              // イメージファイル名
        info[1] = parameters.Resolution;   // 入力解像度
        info[2] = parameters.Direction;    // 処理方向
        info[7] = parameters.ProcessType;  // 処理内容
        info[8] = parameters.FrameCount;   // 枠の個数
        info[9] = parameters.FrameType;    // 枠の種類
        info[10] = parameters.WriteMethod; // 記入方法
        info[11] = parameters.CharType;    // 字種
        // ... その他のパラメータ設定
        return info;
    }

    [DllImport("kernel32.dll", SetLastError=true)]
    static extern int GlobalFree(int hMem);

    public void Dispose()
    {
        if (_charDicLoaded)
        {
            _gOcrEx?.UnloadCharDic();
            _charDicLoaded = false;
        }
        _gOcrEx = null;
    }
}
```

### 3. ImageProcessingService (IGlyOcrEx)

```csharp
public class ImageProcessingService : IDisposable
{
    private GlyOcrEx _gOcrEx;

    public ImageProcessingService()
    {
        _gOcrEx = new GlyOcrEx();
    }

    public ProcessedImage BinarizeImage(string inputPath, BinarizeParameters parameters)
    {
        int handle = 0;
        int result = _gOcrEx.GetBinaryImage(
            out handle, 
            inputPath, 
            parameters.Threshold,
            parameters.Method);

        if (result != 0)
            throw new OcrException($"2値化処理失敗: {result}");

        var processedImage = new ProcessedImage
        {
            Handle = handle,
            Success = true
        };

        return processedImage;
    }

    public ProcessedImage CorrectSkew(string inputPath, CorrectParameters parameters)
    {
        int handle = 0;
        int result = _gOcrEx.GetDocumentImageEx(
            out handle,
            inputPath,
            parameters.SkewCorrection,
            parameters.RemoveBlackBorder);

        if (result != 0)
            throw new OcrException($"傾き補正失敗: {result}");

        return new ProcessedImage { Handle = handle, Success = true };
    }

    public void SaveProcessedImage(ProcessedImage image, string outputPath, ImageFormat format)
    {
        int result = _gOcrEx.OutputImageFile(
            image.Handle,
            outputPath,
            (int)format);

        if (result != 0)
            throw new OcrException($"画像保存失敗: {result}");

        // メモリ開放
        GlobalFree(image.Handle);
        image.Handle = 0;
    }

    public void Dispose()
    {
        _gOcrEx = null;
    }
}
```

## 生成されるクラス・インターフェース

### インターフェース
- `IFormRecognitionService` - 帳票認識サービス
- `IAreaOcrService` - エリアOCRサービス  
- `IImageProcessingService` - 画像処理サービス

### 実装クラス
- `FormRecognitionService` - 帳票認識実装
- `AreaOcrService` - エリアOCR実装
- `ImageProcessingService` - 画像処理実装

### データクラス
- `OcrResult` - OCR結果
- `AreaOcrResult` - エリアOCR結果
- `ProcessedImage` - 処理済み画像
- `OcrParameters` - OCRパラメータ
- `FieldResult` - フィールド結果

### ヘルパークラス
- `ComInteropHelper` - COM相互運用支援
- `MemoryManager` - メモリ管理
- `OcrParameterBuilder` - パラメータ構築

## 安全性・品質保証

### メモリ管理
- 自動リソース開放 (IDisposable)
- GlobalFree呼び出し確認
- メモリリーク検出

### エラーハンドリング
- COM例外の適切な処理
- 戻り値チェック
- カスタム例外定義

### テストサポート
- モックオブジェクト生成
- 単体テスト生成
- 統合テスト生成

## 成功時の出力

```
✅ OCRインターフェース実装完了

実装内容:
✅ FormRecognitionService (IGlyOcr)
✅ AreaOcrService (IGlyOcrEx) 
✅ ImageProcessingService (IGlyOcrEx)

安全性機能:
✅ 自動メモリ管理
✅ COM例外ハンドリング
✅ リソース自動開放

テストコード:
✅ 単体テスト生成
✅ 統合テスト生成

🚀 Next: /form-recognition で帳票認識機能を実装
```