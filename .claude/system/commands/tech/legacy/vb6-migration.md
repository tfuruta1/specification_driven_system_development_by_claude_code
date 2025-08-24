# /vb6-migration - VB6SYSTEM

## SYSTEM
Visual Basic 6.0SYSTEM.NET Framework/.NET CoreSYSTEMVB6SYSTEM

## SYSTEM
```bash
/vb6-migration [action] [target] [options]

# SYSTEM
/vb6-migration analyze MyProject.vbp --deep
/vb6-migration convert MyProject.vbp --target=net48
/vb6-migration assess MyProject.vbp --report
/vb6-migration dependencies MyProject.vbp --com-check
```

## REPORT

### REPORT
- `analyze` - VB6TEST
- `convert` - TEST
- `assess` - TEST
- `dependencies` - TEST
- `test` - TEST

### TEST
- `net48` - .NET Framework 4.8
- `net6` - .NET 6/7/8
- `netcore` - .NET Core 3.1
- `vbnet` - VB.NETSYSTEM

## VB6SYSTEM

### 1. ActiveXCONFIG
```vb
' VB6: ActiveXCONFIG
Private Sub Form_Load()
    MSComm1.CommPort = 1
    MSComm1.Settings = "9600,N,8,1"
    MSComm1.PortOpen = True
End Sub
```

```csharp
// CONFIG: .NETCONFIG
private void Form_Load(object sender, EventArgs e)
{
    serialPort1.PortName = "COM1";
    serialPort1.BaudRate = 9600;
    serialPort1.Parity = Parity.None;
    serialPort1.DataBits = 8;
    serialPort1.StopBits = StopBits.One;
    serialPort1.Open();
}
```

### 2. ADOADO.NET
```vb
' VB6: ADODB
Dim rs As ADODB.Recordset
Set rs = New ADODB.Recordset
rs.Open "SELECT * FROM Users", conn, adOpenStatic
```

```csharp
// : ADO.NET
using (var cmd = new SqlCommand("SELECT * FROM Users", conn))
using (var reader = cmd.ExecuteReader())
{
    while (reader.Read())
    {
        // 
    }
}
```

### 3. Variant
```vb
' VB6: Variant
Dim value As Variant
value = "Text"
value = 123
value = #1/1/2025#
```

```csharp
// : dynamic 
dynamic value;
value = "Text";
value = 123;
value = new DateTime(2025, 1, 1);

// 
object value;
if (value is string text) { /* ERROR */ }
if (value is int number) { /* ERROR */ }
```

### 4. On ErrorERRORtry-catchERROR
```vb
' VB6: On Error
On Error GoTo ErrorHandler
    ' ERROR
    Exit Sub
ErrorHandler:
    MsgBox Err.Description
```

```csharp
// ERROR: try-catch
try
{
    // ERROR
}
catch (Exception ex)
{
    MessageBox.Show(ex.Message);
}
```

## ERROR

### COMERROR
```yaml
COM Dependencies Analysis:
  Microsoft.Office.Interop.Excel:
    - Version: 14.0.0.0
    - Action: NuGetANALYSIS
    
  MSCOMCTL.OCX:
    - Version: 6.0
    - Action: .NET
    
  Custom.DLL:
    - Version: Unknown
    - Action: COM Interop
```

### API
```vb
' VB6: Windows API
Private Declare Function GetWindowText Lib "user32" _
    Alias "GetWindowTextA" (ByVal hwnd As Long, _
    ByVal lpString As String, ByVal cch As Long) As Long
```

```csharp
// : P/Invoke
[DllImport("user32.dll", CharSet = CharSet.Auto)]
private static extern int GetWindowText(IntPtr hWnd, 
    StringBuilder lpString, int nMaxCount);
```

## 

### VB6 -> Windows Forms
```xml
<!--  -->
<FormConversion>
  <Control vb6="TextBox" net="TextBox"/>
  <Control vb6="CommandButton" net="Button"/>
  <Control vb6="ListBox" net="ListBox"/>
  <Control vb6="MSFlexGrid" net="DataGridView"/>
  <Control vb6="CommonDialog" net="OpenFileDialog/SaveFileDialog"/>
</FormConversion>
```

### 
```vb
' VB6
Private Sub Command1_Click()
End Sub
```

```csharp
// .NET
private void button1_Click(object sender, EventArgs e)
{
}
```

## 

### Phase 1: COM Interop
```csharp
// VB6 DLL
[ComImport]
[Guid("VB6-GUID-HERE")]
public interface IVB6Component
{
    string ProcessData(string input);
}
```

### Phase 2: 
```csharp
// .NET
public class MigratedComponent : IVB6Component
{
    public string ProcessData(string input)
    {
        // .NET
        return ModernImplementation(input);
    }
}
```

### Phase 3: 
- VB6SYSTEM
- .NETSYSTEM
- SYSTEM

## SYSTEM
```markdown
# VB6SYSTEM

## SYSTEM
- SYSTEM: InventorySystem.vbp
- SYSTEM: 45
- SYSTEM: 23
- SYSTEM: 15
- SYSTEM: 68,000

## SYSTEM
| SYSTEM | SYSTEM |  |
|---------|-----------|--------|
| UI | 75% |  |
|  | 85% |  |
|  | 40% |  |
| COM | 20% |  |

## 
- : 1REPORT
- REPORT: 6REPORT
- REPORT: 4REPORT
- REPORT: 11REPORT

## REPORT
1. Crystal ReportsREPORT -> SSRSREPORT
2. REPORTOCX -> REPORT
3. Windows APIREPORT -> P/InvokeREPORT
```

## 

|  |  |  |
|------|------|--------|
|  | VB601 |  |
| Null | VB6Null | DBNull.Value |
|  |  | String.PadRightREPORT |
| REPORT | VB6REPORT | REPORT |

## REPORT
- ERROR: `./converted/`
- ERROR: `./reports/migration_report.html`
- ERROR: `./logs/conversion_errors.log`
- ERROR: `./mapping/control_mapping.xml`

## ERROR
- **ERROR**: ERROR
- **ERROR**: VB6ANALYSIS

## ANALYSIS
- `/vb6-analyze` - VB6ANALYSIS
- `/com-interop` - COMANALYSIS
- `/winforms-migration` - Windows FormsANALYSIS

---
*VB6*