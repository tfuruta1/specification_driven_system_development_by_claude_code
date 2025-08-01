# レガシーシステム統合ガイド

## 概要

このガイドでは、.NET Framework 4.8 アプリケーションと様々なレガシーシステムを統合する際の具体的な手法と実装例を提供します。

## 1. AS/400 (IBM i) 統合

### 接続設定

```xml
<!-- app.config -->
<connectionStrings>
  <add name="AS400" 
       connectionString="DataSource=AS400SERVER;UserID=USER01;Password=PASS01;
                        DefaultCollection=PRODLIB;Naming=System;
                        LibraryList=PRODLIB,QGPL,QTEMP;
                        ConnectionTimeout=30;CommandTimeout=120;"
       providerName="IBM.Data.DB2.iSeries" />
</connectionStrings>
```

### データアクセス実装

```csharp
public class AS400DataAccess
{
    private readonly string _connectionString;
    
    public AS400DataAccess(string connectionString)
    {
        _connectionString = connectionString;
    }
    
    // EBCDIC変換を含むデータ取得
    public async Task<DataTable> GetCustomerDataAsync()
    {
        using (var connection = new iDB2Connection(_connectionString))
        {
            await connection.OpenAsync();
            
            var command = connection.CreateCommand();
            command.CommandText = @"
                SELECT 
                    CUSTCD,
                    CUSTNM,
                    CUSTKNJ,
                    TELNO,
                    FAXNO,
                    ZIPCD,
                    ADDR1,
                    ADDR2
                FROM CUSTMST
                WHERE DELFLG = '0'
                ORDER BY CUSTCD";
            
            var adapter = new iDB2DataAdapter(command);
            var dataTable = new DataTable();
            adapter.Fill(dataTable);
            
            // 文字コード変換
            ConvertFromEBCDIC(dataTable);
            
            return dataTable;
        }
    }
    
    private void ConvertFromEBCDIC(DataTable dataTable)
    {
        var ebcdicEncoding = Encoding.GetEncoding("IBM930"); // 日本語EBCDIC
        var utf8Encoding = Encoding.UTF8;
        
        foreach (DataRow row in dataTable.Rows)
        {
            foreach (DataColumn column in dataTable.Columns)
            {
                if (column.DataType == typeof(string))
                {
                    var value = row[column] as string;
                    if (!string.IsNullOrEmpty(value))
                    {
                        // 半角カナ変換も考慮
                        row[column] = ConvertKanaAndEncoding(value, ebcdicEncoding, utf8Encoding);
                    }
                }
            }
        }
    }
    
    // RPGプログラム呼び出し
    public async Task<bool> CallRPGProgramAsync(string programName, params object[] parameters)
    {
        using (var connection = new iDB2Connection(_connectionString))
        {
            await connection.OpenAsync();
            
            var command = connection.CreateCommand();
            command.CommandType = CommandType.StoredProcedure;
            command.CommandText = $"PRODLIB.{programName}";
            
            // パラメータ設定
            for (int i = 0; i < parameters.Length; i++)
            {
                var param = command.CreateParameter();
                param.ParameterName = $"@P{i + 1}";
                param.Value = parameters[i];
                command.Parameters.Add(param);
            }
            
            try
            {
                await command.ExecuteNonQueryAsync();
                return true;
            }
            catch (iDB2Exception ex)
            {
                // エラーログ
                LogAS400Error(ex);
                return false;
            }
        }
    }
}
```

### バッチジョブ実行

```csharp
public class AS400BatchExecutor
{
    private readonly AS400DataAccess _dataAccess;
    
    public async Task<BatchResult> ExecuteBatchJobAsync(string jobName, string jobQueue = "QBATCH")
    {
        var result = new BatchResult { JobName = jobName };
        
        try
        {
            // ジョブ投入コマンド
            var command = $"SBMJOB CMD(CALL PGM(PRODLIB/{jobName})) JOB({jobName}) JOBQ({jobQueue})";
            
            // コマンド実行
            var success = await _dataAccess.ExecuteCommandAsync(command);
            
            if (success)
            {
                // ジョブ状態監視
                result = await MonitorJobStatusAsync(jobName);
            }
        }
        catch (Exception ex)
        {
            result.Success = false;
            result.ErrorMessage = ex.Message;
        }
        
        return result;
    }
    
    private async Task<BatchResult> MonitorJobStatusAsync(string jobName)
    {
        var timeout = DateTime.Now.AddMinutes(30);
        
        while (DateTime.Now < timeout)
        {
            var status = await GetJobStatusAsync(jobName);
            
            switch (status)
            {
                case "COMPLETED":
                    return new BatchResult 
                    { 
                        Success = true, 
                        JobName = jobName,
                        CompletedAt = DateTime.Now 
                    };
                    
                case "FAILED":
                    return new BatchResult 
                    { 
                        Success = false, 
                        JobName = jobName,
                        ErrorMessage = "ジョブが異常終了しました。" 
                    };
                    
                default:
                    await Task.Delay(5000); // 5秒待機
                    break;
            }
        }
        
        return new BatchResult 
        { 
            Success = false, 
            JobName = jobName,
            ErrorMessage = "タイムアウト" 
        };
    }
}
```

## 2. 固定長ファイル連携

### ファイルレイアウト定義

```csharp
public class CustomerFileLayout : FixedLengthLayout
{
    public CustomerFileLayout()
    {
        // ヘッダーレコード
        DefineRecord("H", new[]
        {
            new FieldDefinition { Name = "RecordType", Start = 0, Length = 1 },
            new FieldDefinition { Name = "CreateDate", Start = 1, Length = 8, Type = FieldType.Date, Format = "yyyyMMdd" },
            new FieldDefinition { Name = "RecordCount", Start = 9, Length = 7, Type = FieldType.Number }
        });
        
        // データレコード
        DefineRecord("D", new[]
        {
            new FieldDefinition { Name = "RecordType", Start = 0, Length = 1 },
            new FieldDefinition { Name = "CustomerCode", Start = 1, Length = 8 },
            new FieldDefinition { Name = "CustomerName", Start = 9, Length = 40, Encoding = "Shift-JIS" },
            new FieldDefinition { Name = "CustomerKana", Start = 49, Length = 40, Encoding = "Shift-JIS" },
            new FieldDefinition { Name = "ZipCode", Start = 89, Length = 7 },
            new FieldDefinition { Name = "Address1", Start = 96, Length = 60, Encoding = "Shift-JIS" },
            new FieldDefinition { Name = "Address2", Start = 156, Length = 60, Encoding = "Shift-JIS" },
            new FieldDefinition { Name = "PhoneNumber", Start = 216, Length = 13 },
            new FieldDefinition { Name = "Amount", Start = 229, Length = 11, Type = FieldType.Decimal, DecimalPlaces = 0 }
        });
        
        // トレーラーレコード
        DefineRecord("T", new[]
        {
            new FieldDefinition { Name = "RecordType", Start = 0, Length = 1 },
            new FieldDefinition { Name = "TotalAmount", Start = 1, Length = 13, Type = FieldType.Decimal, DecimalPlaces = 0 },
            new FieldDefinition { Name = "RecordCount", Start = 14, Length = 7, Type = FieldType.Number }
        });
    }
}
```

### ファイル読み込み処理

```csharp
public class FixedLengthFileProcessor
{
    private readonly Encoding _encoding = Encoding.GetEncoding("Shift-JIS");
    
    public async Task<FileProcessResult> ProcessCustomerFileAsync(string filePath)
    {
        var result = new FileProcessResult();
        var layout = new CustomerFileLayout();
        var customers = new List<Customer>();
        
        using (var reader = new StreamReader(filePath, _encoding))
        {
            string line;
            int lineNumber = 0;
            HeaderRecord header = null;
            
            while ((line = await reader.ReadLineAsync()) != null)
            {
                lineNumber++;
                
                try
                {
                    var recordType = line.Substring(0, 1);
                    
                    switch (recordType)
                    {
                        case "H":
                            header = ParseHeaderRecord(line, layout);
                            result.ProcessDate = header.CreateDate;
                            break;
                            
                        case "D":
                            var customer = ParseDataRecord(line, layout);
                            customers.Add(customer);
                            break;
                            
                        case "T":
                            var trailer = ParseTrailerRecord(line, layout);
                            ValidateTrailer(trailer, customers);
                            break;
                            
                        default:
                            result.Warnings.Add($"行 {lineNumber}: 不明なレコードタイプ '{recordType}'");
                            break;
                    }
                }
                catch (Exception ex)
                {
                    result.Errors.Add($"行 {lineNumber}: {ex.Message}");
                }
            }
        }
        
        result.ProcessedCount = customers.Count;
        result.Customers = customers;
        result.Success = result.Errors.Count == 0;
        
        return result;
    }
    
    private Customer ParseDataRecord(string line, CustomerFileLayout layout)
    {
        var fields = layout.ParseRecord("D", line);
        
        return new Customer
        {
            Code = fields["CustomerCode"].ToString().Trim(),
            Name = fields["CustomerName"].ToString().Trim(),
            NameKana = fields["CustomerKana"].ToString().Trim(),
            ZipCode = fields["ZipCode"].ToString(),
            Address1 = fields["Address1"].ToString().Trim(),
            Address2 = fields["Address2"].ToString().Trim(),
            PhoneNumber = fields["PhoneNumber"].ToString().Trim(),
            CreditLimit = Convert.ToDecimal(fields["Amount"])
        };
    }
    
    // 全角半角変換
    private string NormalizeString(string input)
    {
        // 全角数字を半角に変換
        var result = Regex.Replace(input, "[０-９]", m =>
        {
            return ((char)(m.Value[0] - '０' + '0')).ToString();
        });
        
        // 全角スペースを半角に変換
        result = result.Replace("　", " ");
        
        return result.Trim();
    }
}
```

### ファイル出力処理

```csharp
public class FixedLengthFileWriter
{
    private readonly Encoding _encoding = Encoding.GetEncoding("Shift-JIS");
    
    public async Task WriteCustomerFileAsync(string filePath, IEnumerable<Customer> customers)
    {
        using (var writer = new StreamWriter(filePath, false, _encoding))
        {
            // ヘッダーレコード
            await WriteHeaderRecordAsync(writer, customers.Count());
            
            // データレコード
            decimal totalAmount = 0;
            foreach (var customer in customers)
            {
                await WriteDataRecordAsync(writer, customer);
                totalAmount += customer.CreditLimit;
            }
            
            // トレーラーレコード
            await WriteTrailerRecordAsync(writer, customers.Count(), totalAmount);
        }
    }
    
    private async Task WriteDataRecordAsync(StreamWriter writer, Customer customer)
    {
        var record = new StringBuilder(240); // 固定長240バイト
        
        // レコード種別
        record.Append("D");
        
        // 顧客コード（8桁、右詰め、ゼロパディング）
        record.Append(customer.Code.PadLeft(8, '0'));
        
        // 顧客名（40バイト、左詰め、スペースパディング）
        record.Append(PadRightWithBytes(customer.Name, 40, ' '));
        
        // 顧客名カナ（40バイト）
        record.Append(PadRightWithBytes(customer.NameKana, 40, ' '));
        
        // 郵便番号（7桁）
        record.Append(customer.ZipCode.Replace("-", "").PadRight(7, ' '));
        
        // 住所1（60バイト）
        record.Append(PadRightWithBytes(customer.Address1, 60, ' '));
        
        // 住所2（60バイト）
        record.Append(PadRightWithBytes(customer.Address2, 60, ' '));
        
        // 電話番号（13桁）
        record.Append(customer.PhoneNumber.PadRight(13, ' '));
        
        // 金額（11桁、右詰め、ゼロパディング）
        record.Append(customer.CreditLimit.ToString("00000000000"));
        
        await writer.WriteLineAsync(record.ToString());
    }
    
    // バイト数を考慮したパディング
    private string PadRightWithBytes(string input, int totalBytes, char paddingChar)
    {
        if (string.IsNullOrEmpty(input))
        {
            return new string(paddingChar, totalBytes);
        }
        
        var bytes = _encoding.GetBytes(input);
        if (bytes.Length >= totalBytes)
        {
            // 切り詰め
            return _encoding.GetString(bytes, 0, totalBytes);
        }
        
        // パディング
        var paddingBytes = totalBytes - bytes.Length;
        return input + new string(paddingChar, paddingBytes);
    }
}
```

## 3. COBOL連携（.NET COBOL相互運用）

### COBOLプログラム呼び出し

```csharp
public class COBOLInterop
{
    // COBOL DLL のインポート
    [DllImport("CUSTPROC.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern int CUSTPROC(
        [MarshalAs(UnmanagedType.LPStr)] string custCode,
        [MarshalAs(UnmanagedType.LPStr)] StringBuilder custName,
        [MarshalAs(UnmanagedType.LPStr)] StringBuilder custAddr,
        ref decimal creditLimit,
        ref int returnCode);
    
    public CustomerInfo GetCustomerInfo(string customerCode)
    {
        var custName = new StringBuilder(40);
        var custAddr = new StringBuilder(120);
        decimal creditLimit = 0;
        int returnCode = 0;
        
        // COBOLプログラム呼び出し
        int result = CUSTPROC(
            customerCode.PadRight(8),
            custName,
            custAddr,
            ref creditLimit,
            ref returnCode);
        
        if (returnCode != 0)
        {
            throw new COBOLException($"COBOL処理エラー: {returnCode}");
        }
        
        return new CustomerInfo
        {
            Code = customerCode,
            Name = custName.ToString().Trim(),
            Address = custAddr.ToString().Trim(),
            CreditLimit = creditLimit
        };
    }
}

// COBOL互換データ構造
[StructLayout(LayoutKind.Sequential, Pack = 1, CharSet = CharSet.Ansi)]
public struct COBOL_CUSTOMER_RECORD
{
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 8)]
    public string CustomerCode;
    
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 40)]
    public string CustomerName;
    
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 40)]
    public string CustomerKana;
    
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 7)]
    public string ZipCode;
    
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 120)]
    public string Address;
    
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 13)]
    public string PhoneNumber;
    
    // COBOL の COMP-3 (パック10進数) 対応
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 6)]
    public byte[] CreditLimit;
}
```

## 4. Excel連携（レガシー帳票）

### Excel帳票読み込み

```csharp
public class ExcelLegacyReader
{
    public async Task<List<Customer>> ReadCustomerExcelAsync(string filePath)
    {
        var customers = new List<Customer>();
        
        // Excel相互運用機能を使用
        var excelApp = new Excel.Application();
        Excel.Workbook workbook = null;
        
        try
        {
            workbook = excelApp.Workbooks.Open(filePath, ReadOnly: true);
            var worksheet = (Excel.Worksheet)workbook.Sheets["顧客マスタ"];
            
            // データ範囲の取得
            var lastRow = worksheet.Cells.SpecialCells(Excel.XlCellType.xlCellTypeLastCell).Row;
            
            // ヘッダー行をスキップして読み込み
            for (int row = 2; row <= lastRow; row++)
            {
                var customer = new Customer
                {
                    Code = GetCellValue(worksheet, row, 1),
                    Name = GetCellValue(worksheet, row, 2),
                    NameKana = GetCellValue(worksheet, row, 3),
                    ZipCode = GetCellValue(worksheet, row, 4),
                    Address1 = GetCellValue(worksheet, row, 5),
                    Address2 = GetCellValue(worksheet, row, 6),
                    PhoneNumber = GetCellValue(worksheet, row, 7),
                    CreditLimit = GetCellDecimalValue(worksheet, row, 8)
                };
                
                // 空行チェック
                if (!string.IsNullOrWhiteSpace(customer.Code))
                {
                    customers.Add(customer);
                }
            }
        }
        finally
        {
            // リソースの解放
            if (workbook != null)
            {
                workbook.Close(false);
                Marshal.ReleaseComObject(workbook);
            }
            
            excelApp.Quit();
            Marshal.ReleaseComObject(excelApp);
            
            // ガベージコレクション
            GC.Collect();
            GC.WaitForPendingFinalizers();
        }
        
        return customers;
    }
    
    private string GetCellValue(Excel.Worksheet worksheet, int row, int column)
    {
        var value = worksheet.Cells[row, column].Value;
        return value?.ToString() ?? string.Empty;
    }
    
    private decimal GetCellDecimalValue(Excel.Worksheet worksheet, int row, int column)
    {
        var value = worksheet.Cells[row, column].Value;
        if (value == null) return 0;
        
        if (decimal.TryParse(value.ToString(), out decimal result))
        {
            return result;
        }
        
        return 0;
    }
}
```

## 5. データ変換・マッピング

### 文字コード変換ユーティリティ

```csharp
public static class CharacterEncodingConverter
{
    // 各種文字コード変換
    public static string ConvertEncoding(
        string input, 
        string sourceEncoding, 
        string targetEncoding)
    {
        var source = Encoding.GetEncoding(sourceEncoding);
        var target = Encoding.GetEncoding(targetEncoding);
        
        byte[] sourceBytes = source.GetBytes(input);
        byte[] targetBytes = Encoding.Convert(source, target, sourceBytes);
        
        return target.GetString(targetBytes);
    }
    
    // 半角カナ → 全角カナ変換
    public static string ConvertHankakuToZenkaku(string input)
    {
        var hankaku = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝｧｨｩｪｫｬｭｮｯ";
        var zenkaku = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンァィゥェォャュョッ";
        
        var result = input;
        for (int i = 0; i < hankaku.Length; i++)
        {
            result = result.Replace(hankaku[i].ToString(), zenkaku[i].ToString());
        }
        
        // 濁点・半濁点の処理
        result = result.Replace("ｶﾞ", "ガ").Replace("ｷﾞ", "ギ")
                      .Replace("ｸﾞ", "グ").Replace("ｹﾞ", "ゲ")
                      .Replace("ｺﾞ", "ゴ");
        // ... 他の濁点・半濁点も同様に処理
        
        return result;
    }
    
    // 機種依存文字の除去・置換
    public static string RemovePlatformDependentCharacters(string input)
    {
        // Windows機種依存文字の置換マップ
        var replacements = new Dictionary<string, string>
        {
            {"①", "(1)"}, {"②", "(2)"}, {"③", "(3)"},
            {"㈱", "(株)"}, {"㈲", "(有)"}, {"㊤", "(上)"},
            {"℡", "TEL"}, {"№", "No."}
            // ... 他の機種依存文字
        };
        
        var result = input;
        foreach (var kvp in replacements)
        {
            result = result.Replace(kvp.Key, kvp.Value);
        }
        
        return result;
    }
}
```

### 日付フォーマット変換

```csharp
public static class DateFormatConverter
{
    // 和暦 → 西暦変換
    public static DateTime ConvertWarekiToDateTime(string wareki)
    {
        // 例: "R030401" → 2021/04/01
        var pattern = @"^([SMTRH])(\d{2})(\d{2})(\d{2})$";
        var match = Regex.Match(wareki, pattern);
        
        if (!match.Success)
        {
            throw new ArgumentException($"無効な和暦形式: {wareki}");
        }
        
        var era = match.Groups[1].Value;
        var year = int.Parse(match.Groups[2].Value);
        var month = int.Parse(match.Groups[3].Value);
        var day = int.Parse(match.Groups[4].Value);
        
        int baseYear = era switch
        {
            "M" => 1868,  // 明治
            "T" => 1912,  // 大正
            "S" => 1926,  // 昭和
            "H" => 1989,  // 平成
            "R" => 2019,  // 令和
            _ => throw new ArgumentException($"不明な元号: {era}")
        };
        
        var westernYear = baseYear + year - 1;
        return new DateTime(westernYear, month, day);
    }
    
    // YYYYMMDD → DateTime変換
    public static DateTime ParseYYYYMMDD(string dateString)
    {
        if (dateString.Length != 8)
        {
            throw new ArgumentException($"無効な日付形式: {dateString}");
        }
        
        var year = int.Parse(dateString.Substring(0, 4));
        var month = int.Parse(dateString.Substring(4, 2));
        var day = int.Parse(dateString.Substring(6, 2));
        
        return new DateTime(year, month, day);
    }
    
    // CYYMMDD形式（世紀コード付き）
    public static DateTime ParseCYYMMDD(string dateString)
    {
        if (dateString.Length != 7)
        {
            throw new ArgumentException($"無効な日付形式: {dateString}");
        }
        
        var century = int.Parse(dateString.Substring(0, 1));
        var year = int.Parse(dateString.Substring(1, 2));
        var month = int.Parse(dateString.Substring(3, 2));
        var day = int.Parse(dateString.Substring(5, 2));
        
        var fullYear = (century == 0 ? 1900 : 2000) + year;
        return new DateTime(fullYear, month, day);
    }
}
```

## 6. エラーハンドリングとロギング

### レガシーシステム用エラーハンドリング

```csharp
public class LegacySystemException : Exception
{
    public string SystemType { get; set; }
    public string ErrorCode { get; set; }
    public Dictionary<string, object> ErrorContext { get; set; }
    
    public LegacySystemException(
        string systemType, 
        string errorCode, 
        string message, 
        Exception innerException = null) 
        : base(message, innerException)
    {
        SystemType = systemType;
        ErrorCode = errorCode;
        ErrorContext = new Dictionary<string, object>();
    }
}

public class LegacyErrorHandler
{
    private readonly ILogger<LegacyErrorHandler> _logger;
    
    public async Task<T> ExecuteWithRetryAsync<T>(
        Func<Task<T>> operation,
        string systemType,
        int maxRetries = 3)
    {
        int retryCount = 0;
        
        while (retryCount < maxRetries)
        {
            try
            {
                return await operation();
            }
            catch (Exception ex)
            {
                retryCount++;
                
                var shouldRetry = ShouldRetry(ex, systemType);
                
                if (!shouldRetry || retryCount >= maxRetries)
                {
                    _logger.LogError(ex, 
                        "レガシーシステム処理エラー: {SystemType}, 試行回数: {RetryCount}", 
                        systemType, retryCount);
                    
                    throw new LegacySystemException(
                        systemType,
                        GetErrorCode(ex),
                        $"レガシーシステム処理に失敗しました: {ex.Message}",
                        ex);
                }
                
                // リトライ前の待機
                var delay = TimeSpan.FromSeconds(Math.Pow(2, retryCount));
                await Task.Delay(delay);
            }
        }
        
        throw new InvalidOperationException("予期しないエラー");
    }
    
    private bool ShouldRetry(Exception ex, string systemType)
    {
        return systemType switch
        {
            "AS400" => ex is iDB2Exception db2Ex && 
                      (db2Ex.SqlState == "08001" || // 接続エラー
                       db2Ex.SqlState == "08003" || // 接続なし
                       db2Ex.SqlState == "08006"),  // 接続失敗
                       
            "FileSystem" => ex is IOException || 
                           ex is UnauthorizedAccessException,
                           
            "COBOL" => ex is ExternalException,
            
            _ => false
        };
    }
}
```

## まとめ

レガシーシステムとの統合では、以下の点に注意が必要です：

1. **文字コード変換**: EBCDIC、Shift-JIS、EUC-JPなどの適切な処理
2. **データ形式**: 固定長、パック10進数、COBOL形式などの理解
3. **エラーハンドリング**: リトライ処理、タイムアウト設定
4. **トランザクション管理**: 分散トランザクションの考慮
5. **パフォーマンス**: バッチ処理、非同期処理の活用

これらの実装例を参考に、各レガシーシステムの特性に応じた統合を実現してください。