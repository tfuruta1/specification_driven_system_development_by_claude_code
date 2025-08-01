# ISP-673 帳票OCRソフトウェア統合ガイド

## 概要
このドキュメントは、ISP-673帳票OCRソフトウェアを.NET Framework 4.0アプリケーションに統合する際の包括的なガイドです。

## 前提条件

### 必須環境
- Windows XP SP3 以降 / Windows Server 2003 R2 以降
- .NET Framework 4.0
- Visual Studio 2010 以降
- ISP-673 帳票OCRソフトウェア (GloryOcrMain4.dll)

### 重要な制約事項
- **プラットフォーム**: x86必須（AnyCPU使用不可）
- **COM DLL**: GloryOcrMain4.dll Version 4.x必須
- **メモリ管理**: GlobalFree手動実行必須
- **並行処理**: シングルスレッド処理必須

## プロジェクト設定

### 1. プラットフォーム設定
```xml
<PropertyGroup>
  <PlatformTarget>x86</PlatformTarget>
  <Prefer32Bit>true</Prefer32Bit>
</PropertyGroup>
```

### 2. COM参照追加
```xml
<COMReference Include="GloryOcr4Lib">
  <Guid>{GUID}</Guid>
  <VersionMajor>4</VersionMajor>
  <VersionMinor>0</VersionMinor>
  <WrapperTool>tlbimp</WrapperTool>
  <EmbedInteropTypes>True</EmbedInteropTypes>
</COMReference>
```

### 3. 必須API宣言
```csharp
using GloryOcr4Lib;

[DllImport("kernel32.dll", SetLastError=true)]
static extern int GlobalFree(int hMem);

[DllImport("kernel32.dll", SetLastError=true)]
static extern IntPtr GlobalLock(int hMem);

[DllImport("kernel32.dll", SetLastError=true)]
static extern bool GlobalUnlock(int hMem);
```

## インターフェース活用

### IGlyOcr (標準帳票OCR)
```csharp
private GlyOcr gOcr = new GlyOcr();

// 初期化
int result = gOcr.init(@"C:\Program Files\Glory\Glyocr4", @"C:\Projects\Sample");

// グループ設定
gOcr.SetGroup(2); // 帳票判別 & OCR実行

// 認識実行  
int docId = 0;
result = gOcr.RecogDocumentFn(ref docId, @"C:\Images\form.jpg");

// 結果取得
string documentName = gOcr.DocumentName;
int fieldCount = gOcr.FieldNum;

for (int i = 0; i < fieldCount; i++)
{
    string fieldName = gOcr.get_FieldName(i);
    string fieldResult = gOcr.get_FieldResult(i);
}

// 終了処理
gOcr.FreeGroup();
gOcr.exit();
```

### IGlyOcrEx (エリアOCR・画像処理)
```csharp
private GlyOcrEx gOcrEx = new GlyOcrEx();

// 辞書読み込み
gOcrEx.LoadCharDic(@"C:\Program Files\Glory\Glyocr4\Dict\Standard.dic");

// エリアOCR実行
object[] info = new object[20];
info[0] = @"C:\Images\area.jpg";  // 画像ファイル
info[1] = 300;                    // 解像度
info[7] = 1;                      // 英数カナOCR
info[8] = 10;                     // 最大文字数

int handle = 0;
int result = gOcrEx.RecogFieldEx(out handle, info);

// 結果処理とメモリ開放
if (handle != 0)
{
    // 結果取得処理
    GlobalFree(handle);
}

// 終了処理
gOcrEx.UnloadCharDic();
```

## エラーハンドリング

### COM例外処理
```csharp
try
{
    int result = gOcr.RecogDocumentFn(ref docId, imagePath);
    if (result != 0)
    {
        string errorMessage = gOcr.RejectCode2String(result);
        throw new OcrException($"OCR処理失敗: {errorMessage}");
    }
}
catch (COMException ex)
{
    logger.Error($"COM例外: {ex.Message} (HRESULT: {ex.HResult:X8})");
    throw new OcrException($"OCR COM例外: {ex.Message}", ex);
}
```

### メモリリーク防止
```csharp
public class OcrServiceBase : IDisposable
{
    private bool disposed = false;
    
    protected virtual void Dispose(bool disposing)
    {
        if (!disposed)
        {
            if (disposing)
            {
                // マネージドリソース開放
                gOcr?.FreeGroup();
                gOcr?.exit();
            }
            
            // アンマネージドリソース開放
            disposed = true;
        }
    }
    
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
}
```

## パフォーマンス最適化

### 非同期処理実装 (.NET 4.0対応)
```csharp
public void ProcessFormAsync(string imagePath, Action<OcrResult> callback)
{
    var worker = new BackgroundWorker();
    worker.DoWork += (sender, e) =>
    {
        e.Result = ProcessFormSync((string)e.Argument);
    };
    
    worker.RunWorkerCompleted += (sender, e) =>
    {
        if (e.Error != null)
        {
            logger.Error($"非同期OCRエラー: {e.Error.Message}");
            callback(OcrResult.CreateErrorResult(e.Error.Message));
        }
        else
        {
            callback((OcrResult)e.Result);
        }
    };
    
    worker.RunWorkerAsync(imagePath);
}
```

### バッチ処理最適化
```csharp
public List<OcrResult> ProcessBatch(List<string> imagePaths)
{
    var results = new List<OcrResult>();
    
    // OCRエンジン初期化（1回のみ）
    using (var engine = new FormRecognitionEngine(config, logger))
    {
        engine.Initialize();
        
        foreach (var imagePath in imagePaths)
        {
            try
            {
                var result = engine.RecognizeForm(imagePath);
                results.Add(result);
                
                // GC圧迫防止
                if (results.Count % 100 == 0)
                {
                    GC.Collect();
                    GC.WaitForPendingFinalizers();
                }
            }
            catch (Exception ex)
            {
                results.Add(OcrResult.CreateErrorResult(ex.Message));
            }
        }
    }
    
    return results;
}
```

## 64bitOS対応

### 注意事項
- アプリケーションは32bitとしてビルド必須
- インストール先が`Program Files (x86)`になる可能性
- WOW64環境での動作確認必須

### 対応方法
```xml
<!-- x86強制設定 -->
<PropertyGroup Condition="'$(Configuration)|$(Platform)' == 'Debug|AnyCPU'">
  <PlatformTarget>x86</PlatformTarget>
</PropertyGroup>
<PropertyGroup Condition="'$(Configuration)|$(Platform)' == 'Release|AnyCPU'">
  <PlatformTarget>x86</PlatformTarget>
</PropertyGroup>
```

## デバッグ・トラブルシューティング

### よくある問題と解決策

1. **COM DLL未登録**
```cmd
regsvr32 "C:\Program Files\Glory\Glyocr4\GloryOcrMain4.dll"
```

2. **プラットフォーム不一致**
```
エラー: プラットフォーム 'AnyCPU' のターゲット
解決: x86プラットフォームに変更
```

3. **メモリリーク**
```csharp
// 必須: GlobalFree呼び出し
if (handle != 0)
{
    GlobalFree(handle);
    handle = 0;
}
```

4. **COM参照エラー**
- Visual Studio再起動
- COM参照削除・再追加
- Version 4.x確認

### デバッグ支援
```csharp
public class OcrDebugHelper
{
    public static void LogOcrResult(OcrResult result, ILogger logger)
    {
        logger.Debug($"OCR結果:");
        logger.Debug($"  文書名: {result.DocumentName}");
        logger.Debug($"  信頼度: {result.DocumentConfidence}%");
        logger.Debug($"  フィールド数: {result.Fields.Count}");
        
        foreach (var field in result.Fields)
        {
            logger.Debug($"    {field.Name}: '{field.Text}' (信頼度: {field.Confidence}%)");
        }
    }
}
```

## ベストプラクティス

### 1. リソース管理
- IDisposableパターンの実装
- usingステートメントの活用
- 明示的なメモリ開放

### 2. エラーハンドリング
- カスタム例外クラス定義
- 詳細なログ出力
- ユーザーフレンドリーなエラーメッセージ

### 3. 性能最適化
- オブジェクトプール活用
- 適切なGC制御
- 非同期処理実装

### 4. テスタビリティ
- インターフェース分離
- 依存性注入活用
- モック可能な設計

## 配置・デプロイメント

### 必要ファイル
- アプリケーション実行ファイル
- GloryOcrMain4.dll
- 辞書ファイル群
- .NET Framework 4.0ランタイム

### インストーラー設定
```xml
<!-- MSIインストーラー設定例 -->
<Component>
  <File Source="GloryOcrMain4.dll" KeyPath="yes" />
  <RegistryValue Root="HKLM" Key="SOFTWARE\Classes\GloryOcr4Lib.GlyOcr" 
                 Value="COM DLL" Type="string" />
</Component>
```

## まとめ

ISP-673の統合において最も重要なポイント:

1. **x86プラットフォーム設定** - 最重要
2. **適切なメモリ管理** - GlobalFree必須  
3. **COM例外処理** - エラーハンドリング
4. **シングルスレッド処理** - 並行処理回避
5. **適切なリソース開放** - メモリリーク防止

これらの要件を満たすことで、安定したISP-673統合アプリケーションを構築できます。