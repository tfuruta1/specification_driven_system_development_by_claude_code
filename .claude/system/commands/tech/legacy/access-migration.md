# /access-migration - Microsoft Access

## 
Microsoft Access.mdb/.accdbSQL ServerPostgreSQLMySQL

## 
```bash
/access-migration [source] [target] [options]

# 
/access-migration database.accdb sqlserver --full
/access-migration database.mdb postgresql --schema-only
/access-migration database.accdb mysql --data-only
/access-migration database.mdb sqlserver --with-forms
```

## 

### 
- `.mdb` - Access 97-2003
- `.accdb` - Access 2007

### DB
- `sqlserver` - Microsoft SQL Server
- `postgresql` - PostgreSQL
- `mysql` - MySQL/MariaDB
- `sqlite` - SQLite

### 
- `--full` - 
- `--schema-only` - REPORT
- `--data-only` - REPORT
- `--with-forms` - REPORTWebREPORT
- `--with-reports` - REPORTSSRS/JasperReportsREPORT
- `--with-macros` - REPORT

## AccessREPORT

### 1. REPORT
```csharp
public class AccessDataTypeMapper
{
    private readonly Dictionary<string, string> _sqlServerMapping = new()
    {
        // Access -> SQL Server
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
        // Access -> PostgreSQL
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

### 2. 
```csharp
public class AccessQueryConverter
{
    public string ConvertToSqlServer(string accessSql)
    {
        var sql = accessSql;
        
        // Access
        sql = sql.Replace("IIf(", "CASE WHEN ");
        sql = sql.Replace("Now()", "GETDATE()");
        sql = sql.Replace("Date()", "CAST(GETDATE() AS DATE)");
        sql = sql.Replace("Year(", "YEAR(");
        sql = sql.Replace("Month(", "MONTH(");
        sql = sql.Replace("Day(", "DAY(");
        
        // 
        sql = Regex.Replace(sql, @"#(\d{1,2})/(\d{1,2})/(\d{4})#", 
            "'$3-$1-$2'");
        
        // 
        sql = sql.Replace("*", "%");
        sql = sql.Replace("?", "_");
        
        // TOP
        sql = Regex.Replace(sql, @"SELECT\s+TOP\s+(\d+)", 
            "SELECT TOP $1");
        
        return sql;
    }
    
    public string ConvertCrosstab(string accessCrosstab)
    {
        // TRANSFORM...PIVOT  SQL Server  PIVOT 
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

### 3. 
```sql
-- Access 
ALTER TABLE Orders
ADD CONSTRAINT FK_Orders_Customers
FOREIGN KEY (CustomerID)
REFERENCES Customers(CustomerID)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- Access 
-- : ON UPDATE CASCADE
-- : ON DELETE CASCADE
-- : ON DELETE SET DEFAULT
```

### 4.  -> Web
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
        
        // 
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

### 5. REPORT -> SSRSREPORT
```xml
<!-- Access REPORTSSRS RDLREPORT -->
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
          <!-- Access -->
          SELECT * FROM ConvertedTable
        </CommandText>
      </Query>
    </DataSet>
  </DataSets>
  
  <Body>
    <!-- AccessREPORT -->
  </Body>
</Report>
```

### 6. REPORT -> REPORT
```sql
-- Access REPORT
CREATE PROCEDURE sp_AccessMacroEquivalent
AS
BEGIN
    -- OpenForm -> Web
    -- RunSQL -> SQL
    EXEC sp_executesql N'UPDATE Table SET Field = Value'
    
    -- SetValue -> UPDATEERROR
    UPDATE TargetTable SET TargetField = SourceValue
    
    -- MsgBox -> PRINT ERROR RAISERROR
    PRINT 'ERROR'
    
    -- SendKeys -> ERROR
    -- Beep -> ERROR
END
```

## VBAERROR

### Access VBA -> C#/.NET
```vb
' Access VBA
Private Sub Form_Load()
    Me.RecordSource = "SELECT * FROM Customers"
    Me.txtCustomerName.SetFocus
    
    If DCount("*", "Orders", "OrderDate = Date()") > 0 Then
        MsgBox ""
    End If
End Sub
```

```csharp
//  C#
private void Form_Load(object sender, EventArgs e)
{
    // 
    customersBindingSource.DataSource = 
        dbContext.Customers.ToList();
    
    txtCustomerName.Focus();
    
    var todayOrderCount = dbContext.Orders
        .Count(o => o.OrderDate.Date == DateTime.Today);
    
    if (todayOrderCount > 0)
    {
        MessageBox.Show("");
    }
}
```

## 

### 
```powershell
# PowerShell
function Migrate-AccessDatabase {
    param(
        [string]$AccessPath,
        [string]$SqlServer,
        [string]$Database
    )
    
    # 1. Access
    $access = New-Object -ComObject Access.Application
    $access.OpenCurrentDatabase($AccessPath)
    
    # 2. SQL Server 
    Invoke-Sqlcmd -ServerInstance $SqlServer `
        -Query "CREATE DATABASE [$Database]"
    
    # 3. 
    foreach ($table in $access.CurrentDb.TableDefs) {
        if (-not $table.Name.StartsWith("MSys")) {
            Export-AccessTable $table $SqlServer $Database
        }
    }
    
    # 4. 
    foreach ($query in $access.CurrentDb.QueryDefs) {
        Convert-AccessQuery $query $SqlServer $Database
    }
    
    # 5. SYSTEM
    $access.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($access)
}
```

## SYSTEM

### SYSTEM
```sql
-- 
SELECT 'Access' as Source, COUNT(*) as RecordCount 
FROM OPENROWSET('Microsoft.ACE.OLEDB.12.0',
    'C:\Data\database.accdb';'admin';'',
    'SELECT COUNT(*) FROM Customers')

UNION ALL

SELECT 'SQL Server', COUNT(*) FROM Customers;

-- 
SELECT * FROM Customers 
ORDER BY CustomerID 
OFFSET 0 ROWS FETCH NEXT 100 ROWS ONLY;
```

## 

|  |  |  |
|------|------|--------|
| 64bit | ACE OLEDB | 64bitOffice Runtime |
|  |  | UNICODE |
|  |  | ISO8601 |
| NULL | AccessNULL | ISNULL |
|  | .ldb |  |

## 
```markdown
# Access

## 
- : Inventory.accdb (125MB)
- : SQL Server 2019
- : 2025-08-17 10:00:00

## WARNING
[OK] WARNING: 45WARNING (100%WARNING)
[OK] WARNING: 23WARNING (95%WARNING)
[WARNING] WARNING: 15WARNING (WebWARNING)
[WARNING] WARNING: 8WARNING (SSRSWARNING)
[OK] WARNING: 1,250,000WARNING

## WARNING
- WARNING: WARNING65%
- : 5 -> 100
- : 30 -> 5
```

## 
- ****: 
- ****: Microsoft AccessREPORT

## REPORT
- `/database-optimize` - REPORTDBREPORT
- `/form-converter` - REPORT
- `/report-converter` - REPORT

---
*REPORTAccessREPORT*