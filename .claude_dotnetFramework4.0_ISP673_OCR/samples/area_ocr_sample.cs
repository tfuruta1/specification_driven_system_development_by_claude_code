// ISP-673 エリアOCRサンプルコード
// .NET Framework 4.0 / x86プラットフォーム対応

using System;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using GloryOcr4Lib;

namespace ISP673_OCRApp.Samples
{
    /// <summary>
    /// ISP-673 エリアOCRサンプル
    /// IGlyOcrExインターフェースを使用した任意領域OCR実装
    /// </summary>
    public class AreaOcrSample : IDisposable
    {
        private GlyOcrEx _gOcrEx;
        private bool _charDicLoaded = false;
        private bool _knowledgeDicLoaded = false;

        // GlobalFree API宣言
        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern int GlobalFree(int hMem);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern IntPtr GlobalLock(int hMem);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool GlobalUnlock(int hMem);

        /// <summary>
        /// エリアOCRエンジンの初期化
        /// </summary>
        /// <param name="charDicPath">文字認識辞書パス</param>
        /// <param name="knowledgeDicPath">知識辞書パス（日本語OCR用、null可）</param>
        /// <returns>初期化成功可否</returns>
        public bool Initialize(string charDicPath, string knowledgeDicPath = null)
        {
            try
            {
                _gOcrEx = new GlyOcrEx();

                // 文字認識辞書読み込み
                int charDicResult = _gOcrEx.LoadCharDic(charDicPath);
                if (charDicResult != 0)
                {
                    Console.WriteLine($"文字辞書読み込み失敗: エラーコード={charDicResult}");
                    return false;
                }
                _charDicLoaded = true;
                Console.WriteLine($"文字辞書読み込み成功: {charDicPath}");

                // 知識辞書読み込み（オプション）
                if (!string.IsNullOrEmpty(knowledgeDicPath) && File.Exists(knowledgeDicPath))
                {
                    int knowledgeDicResult = _gOcrEx.LoadKnowledgeDic(knowledgeDicPath);
                    if (knowledgeDicResult != 0)
                    {
                        Console.WriteLine($"知識辞書読み込み失敗: エラーコード={knowledgeDicResult}");
                        return false;
                    }
                    _knowledgeDicLoaded = true;
                    Console.WriteLine($"知識辞書読み込み成功: {knowledgeDicPath}");
                }

                Console.WriteLine("エリアOCR初期化成功");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"初期化例外: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// 英数カナエリアOCR実行
        /// </summary>
        /// <param name="imagePath">画像ファイルパス</param>
        /// <param name="rectangle">認識領域</param>
        /// <param name="maxChars">最大文字数</param>
        /// <param name="resolution">解像度</param>
        /// <returns>認識結果</returns>
        public AreaOcrResult RecognizeEnglishNumeric(string imagePath, Rectangle rectangle, int maxChars = 20, int resolution = 300)
        {
            if (!_charDicLoaded)
                throw new InvalidOperationException("文字辞書が読み込まれていません");

            var result = new AreaOcrResult();

            try
            {
                // パラメータ配列作成
                var info = new object[20];
                info[0] = imagePath;                    // イメージファイル名
                info[1] = resolution;                   // 入力解像度
                info[2] = 0;                           // 処理方向（0=横書き）
                info[3] = rectangle.X;                 // 矩形X座標
                info[4] = rectangle.Y;                 // 矩形Y座標
                info[5] = rectangle.Width;             // 矩形幅
                info[6] = rectangle.Height;            // 矩形高さ
                info[7] = 1;                           // 処理内容（1=英数カナOCR）
                info[8] = maxChars;                    // 最大文字数
                info[9] = 1;                           // 枠の種類（1=枠なし）
                info[10] = 1;                          // 記入方法（1=印字）
                info[11] = 1;                          // 字種（1=英数字）

                // エリアOCR実行
                int handle = 0;
                int ocrResult = _gOcrEx.RecogFieldEx(out handle, info);

                result.Success = ocrResult == 0;
                result.Handle = handle;
                result.ErrorCode = ocrResult;
                result.Rectangle = rectangle;

                if (result.Success && handle != 0)
                {
                    ExtractTextFromHandle(result, handle);
                    Console.WriteLine($"英数カナOCR成功: '{result.RecognizedText}' (信頼度: {result.Confidence}%)");
                }
                else
                {
                    result.ErrorMessage = $"英数カナOCR失敗: エラーコード={ocrResult}";
                    Console.WriteLine(result.ErrorMessage);
                }
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = $"英数カナOCR例外: {ex.Message}";
                Console.WriteLine(result.ErrorMessage);
            }
            finally
            {
                // メモリ開放
                if (result.Handle != 0)
                {
                    GlobalFree(result.Handle);
                    result.Handle = 0;
                }
            }

            return result;
        }

        /// <summary>
        /// 日本語エリアOCR実行
        /// </summary>
        /// <param name="imagePath">画像ファイルパス</param>
        /// <param name="rectangle">認識領域</param>
        /// <param name="knowledgeDicName">知識辞書名</param>
        /// <param name="maxChars">最大文字数</param>
        /// <param name="resolution">解像度</param>
        /// <returns>認識結果</returns>
        public AreaOcrResult RecognizeJapanese(string imagePath, Rectangle rectangle, string knowledgeDicName, int maxChars = 50, int resolution = 300)
        {
            if (!_charDicLoaded)
                throw new InvalidOperationException("文字辞書が読み込まれていません");

            if (!_knowledgeDicLoaded)
                throw new InvalidOperationException("知識辞書が読み込まれていません");

            var result = new AreaOcrResult();

            try
            {
                // パラメータ配列作成
                var info = new object[20];
                info[0] = imagePath;                    // イメージファイル名
                info[1] = resolution;                   // 入力解像度
                info[2] = 0;                           // 処理方向（0=横書き）
                info[3] = rectangle.X;                 // 矩形X座標
                info[4] = rectangle.Y;                 // 矩形Y座標
                info[5] = rectangle.Width;             // 矩形幅
                info[6] = rectangle.Height;            // 矩形高さ
                info[7] = 2;                           // 処理内容（2=日本語OCR）
                info[8] = maxChars;                    // 最大文字数
                info[9] = 1;                           // 枠の種類（1=枠なし）
                info[10] = 1;                          // 記入方法（1=印字）
                info[11] = 7;                          // 字種（7=ひらがな・カタカナ・漢字・英数字）
                info[12] = knowledgeDicName;           // 知識辞書名称
                info[13] = "";                         // 限定文字列（空文字＝制限なし）

                // 日本語OCR実行
                int handle = 0;
                int ocrResult = _gOcrEx.RecogFieldEx(out handle, info);

                result.Success = ocrResult == 0;
                result.Handle = handle;
                result.ErrorCode = ocrResult;
                result.Rectangle = rectangle;

                if (result.Success && handle != 0)
                {
                    ExtractTextFromHandle(result, handle);
                    Console.WriteLine($"日本語OCR成功: '{result.RecognizedText}' (信頼度: {result.Confidence}%)");
                }
                else
                {
                    result.ErrorMessage = $"日本語OCR失敗: エラーコード={ocrResult}";
                    Console.WriteLine(result.ErrorMessage);
                }
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = $"日本語OCR例外: {ex.Message}";
                Console.WriteLine(result.ErrorMessage);
            }
            finally
            {
                // メモリ開放
                if (result.Handle != 0)
                {
                    GlobalFree(result.Handle);
                    result.Handle = 0;
                }
            }

            return result;
        }

        /// <summary>
        /// バーコード認識
        /// </summary>
        /// <param name="imagePath">画像ファイルパス</param>
        /// <param name="rectangle">認識領域</param>
        /// <param name="barcodeType">バーコード種類（1=Code39, 2=Code128, etc.）</param>
        /// <param name="resolution">解像度</param>
        /// <returns>認識結果</returns>
        public AreaOcrResult RecognizeBarcode(string imagePath, Rectangle rectangle, int barcodeType = 2, int resolution = 300)
        {
            var result = new AreaOcrResult();

            try
            {
                // パラメータ配列作成
                var info = new object[20];
                info[0] = imagePath;                    // イメージファイル名
                info[1] = resolution;                   // 入力解像度
                info[2] = 0;                           // 処理方向
                info[3] = rectangle.X;                 // 矩形X座標
                info[4] = rectangle.Y;                 // 矩形Y座標
                info[5] = rectangle.Width;             // 矩形幅
                info[6] = rectangle.Height;            // 矩形高さ
                info[7] = 4;                           // 処理内容（4=バーコード）
                info[14] = barcodeType;                // バーコード種類
                info[15] = 0;                          // バーコード方向（0=水平方向）

                // バーコード認識実行
                int handle = 0;
                int ocrResult = _gOcrEx.RecogFieldEx(out handle, info);

                result.Success = ocrResult == 0;
                result.Handle = handle;
                result.ErrorCode = ocrResult;
                result.Rectangle = rectangle;

                if (result.Success && handle != 0)
                {
                    ExtractTextFromHandle(result, handle);
                    Console.WriteLine($"バーコード認識成功: '{result.RecognizedText}'");
                }
                else
                {
                    result.ErrorMessage = $"バーコード認識失敗: エラーコード={ocrResult}";
                    Console.WriteLine(result.ErrorMessage);
                }
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = $"バーコード認識例外: {ex.Message}";
                Console.WriteLine(result.ErrorMessage);
            }
            finally
            {
                // メモリ開放
                if (result.Handle != 0)
                {
                    GlobalFree(result.Handle);
                    result.Handle = 0;
                }
            }

            return result;
        }

        /// <summary>
        /// ハンドルからテキスト結果を抽出
        /// </summary>
        private void ExtractTextFromHandle(AreaOcrResult result, int handle)
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

                // 結果テキスト抽出（実際の実装はISP-673の結果構造に依存）
                // ここではサンプル実装として簡易的な処理
                result.RecognizedText = Marshal.PtrToStringAnsi(lockedPtr) ?? "";
                result.Confidence = 95; // 信頼度はプレースホルダー

                // グローバルメモリアンロック
                GlobalUnlock(handle);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"結果抽出エラー: {ex.Message}");
                result.ErrorMessage = $"結果抽出失敗: {ex.Message}";
            }
        }

        /// <summary>
        /// リソース開放
        /// </summary>
        public void Dispose()
        {
            try
            {
                if (_knowledgeDicLoaded)
                {
                    _gOcrEx?.UnloadKnowledgeDic();
                    _knowledgeDicLoaded = false;
                    Console.WriteLine("知識辞書開放");
                }

                if (_charDicLoaded)
                {
                    _gOcrEx?.UnloadCharDic();
                    _charDicLoaded = false;
                    Console.WriteLine("文字辞書開放");
                }

                Console.WriteLine("エリアOCRエンジン正常終了");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"エリアOCRエンジン終了エラー: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// エリアOCR結果
    /// </summary>
    public class AreaOcrResult
    {
        public bool Success { get; set; }
        public int Handle { get; set; }
        public string RecognizedText { get; set; } = "";
        public int Confidence { get; set; }
        public Rectangle Rectangle { get; set; }
        public int ErrorCode { get; set; }
        public string ErrorMessage { get; set; } = "";
    }

    /// <summary>
    /// サンプル実行クラス
    /// </summary>
    public class AreaOcrProgram
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("=== ISP-673 エリアOCRサンプル ===");

            using (var areaOcr = new AreaOcrSample())
            {
                // 初期化
                string charDicPath = @"C:\Program Files\Glory\Glyocr4\Dict\Standard.dic";
                string knowledgeDicPath = @"C:\Program Files\Glory\Glyocr4\Dict\Japanese.dic";

                if (!areaOcr.Initialize(charDicPath, knowledgeDicPath))
                {
                    Console.WriteLine("初期化失敗");
                    return;
                }

                string imagePath = @"C:\TestImages\area_sample.jpg";

                if (File.Exists(imagePath))
                {
                    // 英数カナOCRテスト
                    Console.WriteLine("\n--- 英数カナOCRテスト ---");
                    var englishRect = new Rectangle(100, 100, 200, 30);
                    var englishResult = areaOcr.RecognizeEnglishNumeric(imagePath, englishRect, 10);

                    if (englishResult.Success)
                    {
                        Console.WriteLine($"認識結果: '{englishResult.RecognizedText}'");
                        Console.WriteLine($"信頼度: {englishResult.Confidence}%");
                    }

                    // 日本語OCRテスト
                    Console.WriteLine("\n--- 日本語OCRテスト ---");
                    var japaneseRect = new Rectangle(100, 200, 300, 40);
                    var japaneseResult = areaOcr.RecognizeJapanese(imagePath, japaneseRect, "standard");

                    if (japaneseResult.Success)
                    {
                        Console.WriteLine($"認識結果: '{japaneseResult.RecognizedText}'");
                        Console.WriteLine($"信頼度: {japaneseResult.Confidence}%");
                    }

                    // バーコード認識テスト
                    Console.WriteLine("\n--- バーコード認識テスト ---");
                    var barcodeRect = new Rectangle(50, 300, 250, 80);
                    var barcodeResult = areaOcr.RecognizeBarcode(imagePath, barcodeRect, 2); // Code128

                    if (barcodeResult.Success)
                    {
                        Console.WriteLine($"バーコードデータ: '{barcodeResult.RecognizedText}'");
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