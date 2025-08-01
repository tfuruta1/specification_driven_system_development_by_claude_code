// ISP-673 基本帳票OCRサンプルコード
// .NET Framework 4.0 / x86プラットフォーム対応

using System;
using System.IO;
using System.Runtime.InteropServices;
using GloryOcr4Lib;

namespace ISP673_OCRApp.Samples
{
    /// <summary>
    /// ISP-673 基本帳票OCRサンプル
    /// IGlyOcrインターフェースを使用した標準的な帳票認識実装
    /// </summary>
    public class BasicFormOcrSample : IDisposable
    {
        private GlyOcr _gOcr;
        private bool _initialized = false;

        /// <summary>
        /// OCRエンジンの初期化
        /// </summary>
        /// <param name="libraryPath">ISP-673ライブラリパス</param>
        /// <param name="projectPath">プロジェクトパス</param>
        /// <returns>初期化成功可否</returns>
        public bool Initialize(string libraryPath, string projectPath)
        {
            try
            {
                _gOcr = new GlyOcr();
                
                // OCRエンジン初期化
                int result = _gOcr.init(libraryPath, projectPath);
                if (result != 0)
                {
                    Console.WriteLine($"OCR初期化失敗: エラーコード={result}");
                    return false;
                }
                
                _initialized = true;
                Console.WriteLine("OCR初期化成功");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"初期化例外: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// 帳票認識実行（帳票判別 + OCR）
        /// </summary>
        /// <param name="imagePath">画像ファイルパス</param>
        /// <param name="groupId">グループID（1=帳票判別のみ, 2=帳票判別+OCR）</param>
        /// <returns>認識結果</returns>
        public FormOcrResult RecognizeForm(string imagePath, int groupId = 2)
        {
            if (!_initialized)
                throw new InvalidOperationException("OCRが初期化されていません");

            if (!File.Exists(imagePath))
                throw new FileNotFoundException($"画像ファイルが見つかりません: {imagePath}");

            var result = new FormOcrResult();
            
            try
            {
                // グループ設定
                int groupResult = _gOcr.SetGroup(groupId);
                if (groupResult != 0)
                {
                    result.ErrorMessage = $"グループ設定失敗: {groupResult}";
                    return result;
                }

                // 認識実行
                int docId = 0;
                int recognitionResult = _gOcr.RecogDocumentFn(ref docId, imagePath);
                
                result.DocumentId = docId;
                result.Success = recognitionResult == 0;
                result.ErrorCode = recognitionResult;

                if (result.Success)
                {
                    // 基本情報取得
                    result.DocumentName = _gOcr.DocumentName;
                    result.DocumentConfidence = _gOcr.DocumentConfidence;
                    result.RejectCode = _gOcr.DocumentRejectCode;
                    
                    if (result.RejectCode != 0)
                    {
                        result.RejectReason = _gOcr.RejectCode2String(result.RejectCode);
                    }

                    // フィールド結果取得
                    ExtractFieldResults(result);
                    
                    Console.WriteLine($"認識成功: 文書={result.DocumentName}, 信頼度={result.DocumentConfidence}%");
                }
                else
                {
                    result.ErrorMessage = $"認識失敗: エラーコード={recognitionResult}";
                    Console.WriteLine(result.ErrorMessage);
                }
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = $"認識例外: {ex.Message}";
                Console.WriteLine(result.ErrorMessage);
            }

            return result;
        }

        /// <summary>
        /// フィールド結果の抽出
        /// </summary>
        private void ExtractFieldResults(FormOcrResult result)
        {
            try
            {
                int fieldCount = _gOcr.FieldNum;
                Console.WriteLine($"フィールド数: {fieldCount}");

                for (int i = 0; i < fieldCount; i++)
                {
                    var field = new FieldResult
                    {
                        Index = i,
                        Id = _gOcr.get_FieldID(i),
                        Name = _gOcr.get_FieldName(i),
                        Text = _gOcr.get_FieldResult(i),
                        Confidence = _gOcr.get_FieldConfidence(i),
                        RejectCode = _gOcr.get_FieldRejectCode(i)
                    };

                    result.Fields.Add(field);
                    
                    Console.WriteLine($"  フィールド[{i}]: {field.Name} = '{field.Text}' (信頼度: {field.Confidence}%)");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"フィールド結果取得エラー: {ex.Message}");
            }
        }

        /// <summary>
        /// OCRのみ実行（帳票判別なし）
        /// </summary>
        /// <param name="imagePath">画像ファイルパス</param>
        /// <param name="documentId">帳票ID + パラメータNo (例: 101 = 帳票ID:1, パラメータNo:1)</param>
        /// <returns>認識結果</returns>
        public FormOcrResult RecognizeOcrOnly(string imagePath, int documentId)
        {
            if (!_initialized)
                throw new InvalidOperationException("OCRが初期化されていません");

            var result = new FormOcrResult();

            try
            {
                // OCRのみ実行モード設定
                _gOcr.ProcType = 2; // OCRのみ

                int docId = documentId;
                int recognitionResult = _gOcr.RecogDocumentFn(ref docId, imagePath);

                result.DocumentId = docId;
                result.Success = recognitionResult == 0;
                result.ErrorCode = recognitionResult;

                if (result.Success)
                {
                    ExtractFieldResults(result);
                    Console.WriteLine($"OCRのみ実行成功: 文書ID={documentId}");
                }
                else
                {
                    result.ErrorMessage = $"OCRのみ実行失敗: エラーコード={recognitionResult}";
                    Console.WriteLine(result.ErrorMessage);
                }
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = $"OCRのみ実行例外: {ex.Message}";
                Console.WriteLine(result.ErrorMessage);
            }

            return result;
        }

        /// <summary>
        /// リソース開放
        /// </summary>
        public void Dispose()
        {
            if (_initialized)
            {
                try
                {
                    _gOcr?.FreeGroup();
                    _gOcr?.exit();
                    Console.WriteLine("OCRエンジン正常終了");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"OCRエンジン終了エラー: {ex.Message}");
                }
                finally
                {
                    _initialized = false;
                }
            }
            _gOcr = null;
        }
    }

    /// <summary>
    /// 帳票OCR結果
    /// </summary>
    public class FormOcrResult
    {
        public bool Success { get; set; }
        public int DocumentId { get; set; }
        public string DocumentName { get; set; }
        public int DocumentConfidence { get; set; }
        public int RejectCode { get; set; }
        public string RejectReason { get; set; }
        public int ErrorCode { get; set; }
        public string ErrorMessage { get; set; }
        public List<FieldResult> Fields { get; set; } = new List<FieldResult>();
    }

    /// <summary>
    /// フィールド結果
    /// </summary>
    public class FieldResult
    {
        public int Index { get; set; }
        public int Id { get; set; }
        public string Name { get; set; }
        public string Text { get; set; }
        public int Confidence { get; set; }
        public int RejectCode { get; set; }
    }

    /// <summary>
    /// サンプル実行クラス
    /// </summary>
    public class Program
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("=== ISP-673 基本帳票OCRサンプル ===");

            using (var ocrSample = new BasicFormOcrSample())
            {
                // 初期化
                string libraryPath = @"C:\Program Files\Glory\Glyocr4";
                string projectPath = @"C:\Program Files\Glory\Glyocr4\FDic\サンプル";
                
                if (!ocrSample.Initialize(libraryPath, projectPath))
                {
                    Console.WriteLine("初期化失敗");
                    return;
                }

                // 帳票認識実行
                string imagePath = @"C:\TestImages\sample_form.jpg";
                
                if (File.Exists(imagePath))
                {
                    var result = ocrSample.RecognizeForm(imagePath);
                    
                    if (result.Success)
                    {
                        Console.WriteLine("\n=== 認識結果 ===");
                        Console.WriteLine($"文書名: {result.DocumentName}");
                        Console.WriteLine($"信頼度: {result.DocumentConfidence}%");
                        Console.WriteLine($"フィールド数: {result.Fields.Count}");

                        foreach (var field in result.Fields)
                        {
                            Console.WriteLine($"  {field.Name}: '{field.Text}' ({field.Confidence}%)");
                        }
                    }
                    else
                    {
                        Console.WriteLine($"認識失敗: {result.ErrorMessage}");
                    }
                }
                else
                {
                    Console.WriteLine($"テスト画像が見つかりません: {imagePath}");
                }
            }

            Console.WriteLine("\nEnterキーで終了...");
            Console.ReadLine();
        }
    }
}