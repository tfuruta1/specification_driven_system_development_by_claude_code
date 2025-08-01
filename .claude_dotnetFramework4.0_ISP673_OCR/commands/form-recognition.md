# /form-recognition - 帳票認識機能実装

## 概要
ISP-673のIGlyOcrインターフェースを使用した帳票認識機能を実装します。帳票種類自動判別、OCR実行、結果処理を包括的にサポートします。

## 主な機能

### 1. 帳票種類自動判別
- 登録済み帳票辞書による自動判別
- 信頼度評価
- 候補結果管理
- リジェクト処理

### 2. OCR実行エンジン
- 単体帳票処理
- バッチ処理
- 非同期処理（BackgroundWorker）
- 進捗報告

### 3. 結果処理・検証
- フィールド別結果取得
- 候補結果分析
- 信頼度評価
- 後処理・検証

## コマンド使用例

```cmd
# 基本帳票認識実装
/form-recognition

# バッチ処理機能付き
/form-recognition --batch

# UI統合版
/form-recognition --with-ui

# 高度な検証機能付き
/form-recognition --advanced-validation

# パフォーマンス最適化版
/form-recognition --optimized
```

## 実装内容

### 1. FormRecognitionEngine

```csharp
public class FormRecognitionEngine : IDisposable
{
    private readonly GlyOcr _gOcr;
    private readonly ILogger _logger;
    private readonly FormRecognitionConfig _config;
    private bool _initialized;

    public FormRecognitionEngine(FormRecognitionConfig config, ILogger logger)
    {
        _config = config ?? throw new ArgumentNullException(nameof(config));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _gOcr = new GlyOcr();
    }

    public async Task<bool> InitializeAsync()
    {
        return await Task.Factory.StartNew(() =>
        {
            try
            {
                int result = _gOcr.init(_config.LibraryPath, _config.ProjectPath);
                if (result != 0)
                {
                    _logger.Error($"OCR初期化失敗: エラーコード={result}");
                    return false;
                }

                _initialized = true;
                _logger.Info("OCR初期化成功");
                return true;
            }
            catch (Exception ex)
            {
                _logger.Error($"OCR初期化例外: {ex.Message}");
                return false;
            }
        });
    }

    public FormRecognitionResult RecognizeForm(string imagePath, RecognitionOptions options = null)
    {
        if (!_initialized)
            throw new InvalidOperationException("OCRエンジンが初期化されていません");

        if (!File.Exists(imagePath))
            throw new FileNotFoundException($"画像ファイルが見つかりません: {imagePath}");

        options = options ?? RecognitionOptions.Default;

        try
        {
            // グループ設定
            int groupResult = _gOcr.SetGroup(options.GroupId);
            if (groupResult != 0)
                throw new OcrException($"グループ設定失敗: {groupResult}");

            // 処理タイプ設定
            _gOcr.ProcType = (int)options.ProcessType;

            // 認識実行
            int docId = 0;
            int recognitionResult = _gOcr.RecogDocumentFn(ref docId, imagePath);

            // 結果作成
            var result = CreateRecognitionResult(docId, recognitionResult, imagePath);
            
            _logger.Info($"帳票認識完了: {imagePath} -> 文書ID={docId}, 結果={recognitionResult}");
            
            return result;
        }
        catch (Exception ex)
        {
            _logger.Error($"帳票認識エラー: {imagePath} - {ex.Message}");
            return FormRecognitionResult.CreateErrorResult(ex.Message);
        }
    }

    private FormRecognitionResult CreateRecognitionResult(int docId, int result, string imagePath)
    {
        var recognition = new FormRecognitionResult
        {
            DocumentId = docId,
            Success = result == 0,
            ImagePath = imagePath,
            ProcessedAt = DateTime.Now,
            DocumentName = _gOcr.DocumentName,
            DocumentConfidence = _gOcr.DocumentConfidence,
            RejectCode = _gOcr.DocumentRejectCode,
            RejectReason = _gOcr.RejectCode2String(_gOcr.DocumentRejectCode)
        };

        // フィールド結果取得
        if (recognition.Success)
        {
            ExtractFieldResults(recognition);
            ExtractDetailedResults(recognition);
        }

        return recognition;
    }

    private void ExtractFieldResults(FormRecognitionResult recognition)
    {
        for (int i = 0; i < _gOcr.FieldNum; i++)
        {
            var field = new FormFieldResult
            {
                Index = i,
                Id = _gOcr.get_FieldID(i),
                Name = _gOcr.get_FieldName(i),
                Text = _gOcr.get_FieldResult(i),
                Confidence = _gOcr.get_FieldConfidence(i),
                RejectCode = _gOcr.get_FieldRejectCode(i)
            };

            // 詳細結果取得
            try
            {
                var detailedResult = _gOcr.GetFieldResultEx(i, 0);
                if (detailedResult != null)
                {
                    field.DetailedResult = detailedResult;
                    field.CandidateCount = detailedResult.CandidateNum;
                }
            }
            catch (Exception ex)
            {
                _logger.Warn($"詳細結果取得失敗 Field[{i}]: {ex.Message}");
            }

            recognition.Fields.Add(field);
        }
    }

    private void ExtractDetailedResults(FormRecognitionResult recognition)
    {
        try
        {
            var documentResult = _gOcr.DocumentResultEx;
            if (documentResult != null)
            {
                recognition.DocumentDetailResult = documentResult;
                recognition.HasDetailedResults = true;
            }
        }
        catch (Exception ex)
        {
            _logger.Warn($"文書詳細結果取得失敗: {ex.Message}");
        }
    }

    public void Dispose()
    {
        if (_initialized)
        {
            try
            {
                _gOcr?.FreeGroup();
                _gOcr?.exit();
                _logger.Info("OCRエンジン正常終了");
            }
            catch (Exception ex)
            {
                _logger.Error($"OCRエンジン終了エラー: {ex.Message}");
            }
            finally
            {
                _initialized = false;
            }
        }
    }
}
```

### 2. BatchFormProcessor

```csharp
public class BatchFormProcessor
{
    private readonly FormRecognitionEngine _engine;
    private readonly ILogger _logger;
    private readonly CancellationTokenSource _cancellationTokenSource;

    public event EventHandler<BatchProgressEventArgs> ProgressChanged;
    public event EventHandler<FormRecognitionResult> FormProcessed;

    public BatchFormProcessor(FormRecognitionEngine engine, ILogger logger)
    {
        _engine = engine ?? throw new ArgumentNullException(nameof(engine));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _cancellationTokenSource = new CancellationTokenSource();
    }

    public async Task<BatchProcessResult> ProcessBatchAsync(
        IEnumerable<string> imagePaths, 
        RecognitionOptions options = null,
        IProgress<BatchProgressEventArgs> progress = null)
    {
        var imageList = imagePaths.ToList();
        var batchResult = new BatchProcessResult 
        { 
            TotalFiles = imageList.Count,
            StartTime = DateTime.Now
        };

        try
        {
            for (int i = 0; i < imageList.Count; i++)
            {
                if (_cancellationTokenSource.Token.IsCancellationRequested)
                    break;

                var imagePath = imageList[i];
                var progressArgs = new BatchProgressEventArgs
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
                    var result = await Task.Factory.StartNew(() => 
                        _engine.RecognizeForm(imagePath, options));

                    batchResult.Results.Add(result);
                    
                    if (result.Success)
                        batchResult.SuccessCount++;
                    else
                        batchResult.FailureCount++;

                    FormProcessed?.Invoke(this, result);
                }
                catch (Exception ex)
                {
                    batchResult.FailureCount++;
                    var errorResult = FormRecognitionResult.CreateErrorResult(ex.Message);
                    errorResult.ImagePath = imagePath;
                    batchResult.Results.Add(errorResult);
                    
                    _logger.Error($"バッチ処理エラー [{imagePath}]: {ex.Message}");
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

    public void Cancel()
    {
        _cancellationTokenSource.Cancel();
    }
}
```

### 3. FormRecognitionValidator

```csharp
public class FormRecognitionValidator
{
    private readonly ValidationRules _rules;
    private readonly ILogger _logger;

    public FormRecognitionValidator(ValidationRules rules, ILogger logger)
    {
        _rules = rules ?? throw new ArgumentNullException(nameof(rules));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public ValidationResult ValidateResult(FormRecognitionResult result)
    {
        var validation = new ValidationResult
        {
            IsValid = true,
            ValidationTime = DateTime.Now
        };

        // 基本検証
        ValidateBasicResult(result, validation);

        // フィールド検証
        ValidateFields(result, validation);

        // 信頼度検証
        ValidateConfidence(result, validation);

        // カスタム検証
        ValidateCustomRules(result, validation);

        return validation;
    }

    private void ValidateBasicResult(FormRecognitionResult result, ValidationResult validation)
    {
        if (!result.Success)
        {
            validation.AddError("認識処理が失敗しました", result.RejectReason);
            validation.IsValid = false;
        }

        if (result.DocumentConfidence < _rules.MinDocumentConfidence)
        {
            validation.AddWarning("文書信頼度が低いです", 
                $"信頼度: {result.DocumentConfidence}% (最低: {_rules.MinDocumentConfidence}%)");
        }
    }

    private void ValidateFields(FormRecognitionResult result, ValidationResult validation)
    {
        foreach (var field in result.Fields)
        {
            var fieldRule = _rules.GetFieldRule(field.Name);
            if (fieldRule == null) continue;

            // 必須チェック
            if (fieldRule.Required && string.IsNullOrEmpty(field.Text))
            {
                validation.AddError($"必須フィールド '{field.Name}' が空です", field.Name);
                validation.IsValid = false;
            }

            // 信頼度チェック
            if (field.Confidence < fieldRule.MinConfidence)
            {
                validation.AddWarning($"フィールド '{field.Name}' の信頼度が低いです",
                    $"信頼度: {field.Confidence}% (最低: {fieldRule.MinConfidence}%)");
            }

            // 形式チェック
            if (!string.IsNullOrEmpty(field.Text) && !string.IsNullOrEmpty(fieldRule.Pattern))
            {
                if (!Regex.IsMatch(field.Text, fieldRule.Pattern))
                {
                    validation.AddError($"フィールド '{field.Name}' の形式が正しくありません",
                        $"値: '{field.Text}', 期待パターン: '{fieldRule.Pattern}'");
                    validation.IsValid = false;
                }
            }
        }
    }

    private void ValidateConfidence(FormRecognitionResult result, ValidationResult validation)
    {
        var lowConfidenceFields = result.Fields
            .Where(f => f.Confidence < _rules.MinFieldConfidence)
            .ToList();

        if (lowConfidenceFields.Count > _rules.MaxLowConfidenceFields)
        {
            validation.AddWarning("信頼度の低いフィールドが多数存在します",
                $"低信頼度フィールド数: {lowConfidenceFields.Count}");
        }
    }
}
```

## 生成されるクラス構成

### コアクラス
- `FormRecognitionEngine` - 帳票認識エンジン
- `BatchFormProcessor` - バッチ処理エンジン
- `FormRecognitionValidator` - 結果検証エンジン

### データクラス
- `FormRecognitionResult` - 認識結果
- `FormFieldResult` - フィールド結果
- `BatchProcessResult` - バッチ処理結果
- `ValidationResult` - 検証結果

### 設定クラス
- `FormRecognitionConfig` - 認識設定
- `RecognitionOptions` - 認識オプション
- `ValidationRules` - 検証ルール

### イベント引数
- `BatchProgressEventArgs` - バッチ進捗イベント
- `FormProcessedEventArgs` - 処理完了イベント

## パフォーマンス最適化

### メモリ管理
- オブジェクトプール活用
- 大量処理時のGC最適化
- リソース適切開放

### 処理最適化
- 非同期処理活用
- 並列処理制限
- キャッシュ機能

## 成功時の出力

```
✅ 帳票認識機能実装完了

実装内容:
✅ FormRecognitionEngine - 認識エンジン
✅ BatchFormProcessor - バッチ処理
✅ FormRecognitionValidator - 結果検証

機能:
✅ 帳票種類自動判別
✅ 非同期OCR処理
✅ バッチ処理対応
✅ 信頼度評価
✅ 結果検証

パフォーマンス:
✅ メモリ最適化
✅ 非同期処理対応
✅ 進捗報告機能

🚀 Next: /area-ocr でエリアOCR機能を実装
```