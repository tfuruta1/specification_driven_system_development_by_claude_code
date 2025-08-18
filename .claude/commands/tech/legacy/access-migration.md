# /access-migration - Microsoft Access移行専用コマンド

## 概要
Microsoft Accessデータベース（.mdb/.accdb）をSQL Server、PostgreSQL、MySQLなどのエンタープライズデータベースへ移行する専門コマンドです。

## 使用方法
```bash
/access-migration [source] [target] [options]

# 使用例
/access-migration database.accdb sqlserver --full
/access-migration database.mdb postgresql --schema-only
/access-migration database.accdb mysql --data-only
/access-migration database.mdb sqlserver --with-forms
```

## パラメータ

### ソースファイル
- `.mdb` - Access 97-2003形式
- `.accdb` - Access 2007以降形式

### ターゲットDB
- `sqlserver` - Microsoft SQL Server
- `postgresql` - PostgreSQL
- `mysql` - MySQL/MariaDB
- `sqlite` - SQLite（軽量移行）

### オプション
- `--full` - スキーマとデータ両方を移行
- `--schema-only` - テーブル構造のみ移行
- `--data-only` - データのみ移行
- `--with-forms` - フォームをWebアプリに変換
- `--with-reports` - レポートをSSRS/JasperReportsに変換
- `--with-macros` - マクロをストアドプロシージャに変換

## Access特有の要素と移行戦略

### 1. データ型マッピング
```csharp
public class AccessDataTypeMapper
{
    private readonly Dictionary<string, string> _sqlServerMapping = new()
    {
        // Access → SQL Server
        ["Yes/No"] = "BIT",
        ["Text"] = "NVARCHAR(255)",
        ["Memo"] = "NVARCHAR(MAX)",
        ["Number (Byte)"] = "TINYINT",
        ["Number (Integer)"] = "SMALLINT",
        ["Number (Long Integer)"] = "INT",
        ["Number (Single)"] = "REAL",
        ["Number (Double)"] = "FLOAT",
        ["Number (Decimal)"] = "DECIMAL(18,4)",
        ["Date/Time"] = "DATETIME2",
        ["Currency"] = "MONEY",
        ["AutoNumber"] = "INT IDENTITY(1,1)",
        ["OLE Object"] = "VARBINARY(MAX)",
        ["Hyperlink"] = "NVARCHAR(MAX)",
        ["Attachment"] = "VARBINARY(MAX)"
    };
    
    private readonly Dictionary<string, string> _postgresMapping = new()
    {
        // Access → PostgreSQL
        ["Yes/No"] = "BOOLEAN",
        ["Text"] = "VARCHAR(255)",
        ["Memo"] = "TEXT",
        ["Number (Integer)"] = "INTEGER",
        ["Number (Long Integer)"] = "BIGINT",
        ["Number (Double)"] = "DOUBLE PRECISION",
        ["Date/Time"] = "TIMESTAMP",
        ["Currency"] = "NUMERIC(19,4)",
        ["AutoNumber"] = "SERIAL",
        ["OLE Object"] = "BYTEA",
        ["Hyperlink"] = "TEXT"
    };
}
```

### 2. クエリ変換
```csharp
public class AccessQueryConverter
{
    public string ConvertToSqlServer(string accessSql)
    {
        var sql = accessSql;
        
        // Access特有の関数を変換
        sql = sql.Replace("IIf(", "CASE WHEN ");
        sql = sql.Replace("Now()", "GETDATE()");
        sql = sql.Replace("Date()", "CAST(GETDATE() AS DATE)");
        sql = sql.Replace("Year(", "YEAR(");
        sql = sql.Replace("Month(", "MONTH(");
        sql = sql.Replace("Day(", "DAY(");
        
        // 日付リテラルの変換
        sql = Regex.Replace(sql, @"#(\d{1,2})/(\d{1,2})/(\d{4})#", 
            "'$3-$1-$2'");
        
        // ワイルドカードの変換
        sql = sql.Replace("*", "%");
        sql = sql.Replace("?", "_");
        
        // TOP句の位置調整
        sql = Regex.Replace(sql, @"SELECT\s+TOP\s+(\d+)", 
            "SELECT TOP $1");
        
        return sql;
    }
    
    public string ConvertCrosstab(string accessCrosstab)
    {
        // TRANSFORM...PIVOT を SQL Server の PIVOT に変換
        var pattern = @"TRANSFORM\s+(.+?)\s+SELECT\s+(.+?)\s+FROM\s+(.+?)\s+PIVOT\s+(.+)";
        var match = Regex.Match(accessCrosstab, pattern, RegexOptions.Singleline);
        
        if (match.Success)
        {
            var aggregateFunction = match.Groups[1].Value;
            var selectColumns = match.Groups[2].Value;
            var fromClause = match.Groups[3].Value;
            var pivotColumn = match.Groups[4].Value;
            
            return $@"
                SELECT {selectColumns}, {pivotColumn}
                FROM (
                    SELECT {selectColumns}, {pivotColumn}, {aggregateFunction}
                    FROM {fromClause}
                ) AS SourceTable
                PIVOT (
                    {aggregateFunction}
                    FOR {pivotColumn} IN ([Value1], [Value2], [Value3])
                ) AS PivotTable";
        }
        
        return accessCrosstab;
    }
}
```

### 3. リレーションシップ移行
```sql
-- Access リレーションシップを外部キー制約に変換
ALTER TABLE Orders
ADD CONSTRAINT FK_Orders_Customers
FOREIGN KEY (CustomerID)
REFERENCES Customers(CustomerID)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- Access の参照整合性オプションを維持
-- 連鎖更新: ON UPDATE CASCADE
-- 連鎖削除: ON DELETE CASCADE
-- 既定値: ON DELETE SET DEFAULT
```

### 4. フォーム → Webアプリ変換
```csharp
public class AccessFormConverter
{
    public WebForm ConvertToWebForm(AccessForm accessForm)
    {
        var webForm = new WebForm
        {
            Name = accessForm.Name,
            Title = accessForm.Caption,
            Layout = ConvertLayout(accessForm.DefaultView)
        };
        
        foreach (var control in accessForm.Controls)
        {
            webForm.Controls.Add(ConvertControl(control));
        }
        
        // イベント変換
        foreach (var eventHandler in accessForm.Events)
        {
            webForm.Scripts.Add(ConvertEventToJavaScript(eventHandler));
        }
        
        return webForm;
    }
    
    private WebControl ConvertControl(AccessControl control)
    {
        return control.ControlType switch
        {
            "TextBox" => new TextInput
            {
                Id = control.Name,
                Value = control.DefaultValue,
                MaxLength = control.FieldSize
            },
            "ComboBox" => new SelectList
            {
                Id = control.Name,
                DataSource = control.RowSource,
                DisplayMember = control.ColumnWidths
            },
            "CommandButton" => new Button
            {
                Id = control.Name,
                Text = control.Caption,
                OnClick = control.OnClick
            },
            _ => new GenericControl { Id = control.Name }
        };
    }
}
```

### 5. レポート → SSRS変換
```xml
<!-- Access レポートをSSRS RDLに変換 -->
<Report xmlns="...">
  <DataSources>
    <DataSource Name="AccessData">
      <ConnectionProperties>
        <DataProvider>SQL</DataProvider>
        <ConnectString>Data Source=...;Initial Catalog=...</ConnectString>
      </ConnectionProperties>
    </DataSource>
  </DataSources>
  
  <DataSets>
    <DataSet Name="MainQuery">
      <Query>
        <DataSourceName>AccessData</DataSourceName>
        <CommandText>
          <!-- 変換されたAccessクエリ -->
          SELECT * FROM ConvertedTable
        </CommandText>
      </Query>
    </DataSet>
  </DataSets>
  
  <Body>
    <!-- Accessレポートレイアウトを再現 -->
  </Body>
</Report>
```

### 6. マクロ → ストアドプロシージャ変換
```sql
-- Access マクロアクション変換例
CREATE PROCEDURE sp_AccessMacroEquivalent
AS
BEGIN
    -- OpenForm → ビューまたはWebページへのリダイレクト
    -- RunSQL → 直接SQL実行
    EXEC sp_executesql N'UPDATE Table SET Field = Value'
    
    -- SetValue → UPDATE文
    UPDATE TargetTable SET TargetField = SourceValue
    
    -- MsgBox → PRINT または RAISERROR
    PRINT 'メッセージ'
    
    -- SendKeys → アプリケーション層で処理
    -- Beep → アプリケーション層で処理
END
```

## VBAコード移行

### Access VBA → C#/.NET
```vb
' Access VBA
Private Sub Form_Load()
    Me.RecordSource = "SELECT * FROM Customers"
    Me.txtCustomerName.SetFocus
    
    If DCount("*", "Orders", "OrderDate = Date()") > 0 Then
        MsgBox "本日の注文があります"
    End If
End Sub
```

```csharp
// 変換後 C#
private void Form_Load(object sender, EventArgs e)
{
    // データバインディング
    customersBindingSource.DataSource = 
        dbContext.Customers.ToList();
    
    txtCustomerName.Focus();
    
    var todayOrderCount = dbContext.Orders
        .Count(o => o.OrderDate.Date == DateTime.Today);
    
    if (todayOrderCount > 0)
    {
        MessageBox.Show("本日の注文があります");
    }
}
```

## 移行実行プロセス

### 完全自動移行スクリプト
```powershell
# PowerShell移行スクリプト
function Migrate-AccessDatabase {
    param(
        [string]$AccessPath,
        [string]$SqlServer,
        [string]$Database
    )
    
    # 1. Access接続
    $access = New-Object -ComObject Access.Application
    $access.OpenCurrentDatabase($AccessPath)
    
    # 2. SQL Server データベース作成
    Invoke-Sqlcmd -ServerInstance $SqlServer `
        -Query "CREATE DATABASE [$Database]"
    
    # 3. テーブル移行
    foreach ($table in $access.CurrentDb.TableDefs) {
        if (-not $table.Name.StartsWith("MSys")) {
            Export-AccessTable $table $SqlServer $Database
        }
    }
    
    # 4. クエリ移行
    foreach ($query in $access.CurrentDb.QueryDefs) {
        Convert-AccessQuery $query $SqlServer $Database
    }
    
    # 5. クリーンアップ
    $access.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($access)
}
```

## 移行後の検証

### データ整合性チェック
```sql
-- レコード数比較
SELECT 'Access' as Source, COUNT(*) as RecordCount 
FROM OPENROWSET('Microsoft.ACE.OLEDB.12.0',
    'C:\Data\database.accdb';'admin';'',
    'SELECT COUNT(*) FROM Customers')

UNION ALL

SELECT 'SQL Server', COUNT(*) FROM Customers;

-- データ内容比較（サンプリング）
SELECT * FROM Customers 
ORDER BY CustomerID 
OFFSET 0 ROWS FETCH NEXT 100 ROWS ONLY;
```

## トラブルシューティング

| 問題 | 原因 | 解決策 |
|------|------|--------|
| 64bit環境エラー | ACE OLEDBプロバイダー | 64bit版Office Runtime |
| 日本語文字化け | 文字コード | UNICODE変換 |
| 日付フォーマット | 地域設定依存 | ISO8601形式使用 |
| NULL値エラー | Access独自NULL処理 | ISNULL関数使用 |
| 排他制御エラー | .ldbファイル | 単独使用モードで開く |

## 出力レポート
```markdown
# Access移行完了レポート

## 移行サマリー
- ソース: Inventory.accdb (125MB)
- ターゲット: SQL Server 2019
- 移行日時: 2025-08-17 10:00:00

## 移行結果
✅ テーブル: 45個 (100%成功)
✅ ビュー（クエリ）: 23個 (95%成功)
⚠️ フォーム: 15個 (Webフォームテンプレート生成)
⚠️ レポート: 8個 (SSRS定義ファイル生成)
✅ データ: 1,250,000レコード

## パフォーマンス改善
- クエリ実行時間: 平均65%高速化
- 同時接続数: 5 → 100ユーザー
- バックアップ時間: 30分 → 5分
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: Microsoft Access特有の問題に特化

## 関連コマンド
- `/database-optimize` - 移行後のDB最適化
- `/form-converter` - フォーム変換詳細
- `/report-converter` - レポート変換詳細

---
*このコマンドはシステム開発部が管理します。Access特有の問題に特化しています。*