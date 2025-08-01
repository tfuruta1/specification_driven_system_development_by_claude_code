# VB6 → .NET Framework 4.8 移行パターン集

## 1. 基本的な構文変換パターン

### 1.1 変数宣言と型
```vb
' VB6
Dim customerName As String
Dim orderCount As Long
Dim totalAmount As Currency
Dim items() As String
ReDim items(10)

' .NET Framework 4.8 (VB.NET)
Dim customerName As String
Dim orderCount As Integer  ' または Long
Dim totalAmount As Decimal
Dim items() As String
ReDim items(10)

' C# (.NET Framework 4.8)
string customerName;
int orderCount;  // または long
decimal totalAmount;
string[] items = new string[11];  // 0-10の11要素
```

### 1.2 プロパティ実装
```vb
' VB6
Private m_CustomerID As Long

Public Property Get CustomerID() As Long
    CustomerID = m_CustomerID
End Property

Public Property Let CustomerID(ByVal value As Long)
    If value < 0 Then
        Err.Raise vbObjectError + 1000, , "Invalid ID"
    End If
    m_CustomerID = value
End Property

' .NET Framework 4.8 (VB.NET)
Private _customerID As Integer

Public Property CustomerID() As Integer
    Get
        Return _customerID
    End Get
    Set(ByVal value As Integer)
        If value < 0 Then
            Throw New ArgumentException("Invalid ID")
        End If
        _customerID = value
    End Set
End Property

' C# (.NET Framework 4.8)
private int _customerID;

public int CustomerID
{
    get { return _customerID; }
    set
    {
        if (value < 0)
            throw new ArgumentException("Invalid ID");
        _customerID = value;
    }
}
```

## 2. エラーハンドリングの移行

### 2.1 基本的なエラーハンドリング
```vb
' VB6
Public Function CalculateDiscount(ByVal amount As Currency) As Currency
    On Error GoTo ErrorHandler
    
    If amount < 0 Then
        Err.Raise vbObjectError + 1001, , "Amount cannot be negative"
    End If
    
    CalculateDiscount = amount * 0.1
    Exit Function
    
ErrorHandler:
    LogError Err.Number, Err.Description
    CalculateDiscount = 0
End Function

' .NET Framework 4.8 (VB.NET)
Public Function CalculateDiscount(ByVal amount As Decimal) As Decimal
    Try
        If amount < 0 Then
            Throw New ArgumentException("Amount cannot be negative")
        End If
        
        Return amount * 0.1D
        
    Catch ex As ArgumentException
        ' 特定の例外処理
        LogError(ex)
        Return 0
    Catch ex As Exception
        ' 一般的な例外処理
        LogError(ex)
        Return 0
    End Try
End Function

' C# (.NET Framework 4.8)
public decimal CalculateDiscount(decimal amount)
{
    try
    {
        if (amount < 0)
            throw new ArgumentException("Amount cannot be negative");
            
        return amount * 0.1m;
    }
    catch (ArgumentException ex)
    {
        LogError(ex);
        return 0;
    }
    catch (Exception ex)
    {
        LogError(ex);
        return 0;
    }
}
```

### 2.2 On Error Resume Next の移行
```vb
' VB6 - エラーを無視するパターン
On Error Resume Next
Dim value As Long
value = CLng(textBox1.Text)
If Err.Number <> 0 Then
    value = 0
    Err.Clear
End If

' .NET Framework 4.8 (VB.NET)
Dim value As Integer
If Not Integer.TryParse(TextBox1.Text, value) Then
    value = 0
End If

' C# (.NET Framework 4.8)
int value;
if (!int.TryParse(textBox1.Text, out value))
{
    value = 0;
}
```

## 3. データアクセスの移行

### 3.1 ADO → ADO.NET
```vb
' VB6 (ADO)
Dim conn As ADODB.Connection
Dim rs As ADODB.Recordset

Set conn = New ADODB.Connection
conn.Open "Provider=SQLOLEDB;Data Source=server;Initial Catalog=db;User ID=user;Password=pass"

Set rs = New ADODB.Recordset
rs.Open "SELECT * FROM Customers", conn, adOpenStatic, adLockReadOnly

Do While Not rs.EOF
    Debug.Print rs!CustomerName
    rs.MoveNext
Loop

rs.Close
conn.Close

' .NET Framework 4.8 (VB.NET)
Dim connectionString As String = "Data Source=server;Initial Catalog=db;User ID=user;Password=pass"

Using conn As New SqlConnection(connectionString)
    conn.Open()
    
    Using cmd As New SqlCommand("SELECT * FROM Customers", conn)
        Using reader As SqlDataReader = cmd.ExecuteReader()
            While reader.Read()
                Console.WriteLine(reader("CustomerName"))
            End While
        End Using
    End Using
End Using

' C# (.NET Framework 4.8)
string connectionString = "Data Source=server;Initial Catalog=db;User ID=user;Password=pass";

using (SqlConnection conn = new SqlConnection(connectionString))
{
    conn.Open();
    
    using (SqlCommand cmd = new SqlCommand("SELECT * FROM Customers", conn))
    using (SqlDataReader reader = cmd.ExecuteReader())
    {
        while (reader.Read())
        {
            Console.WriteLine(reader["CustomerName"]);
        }
    }
}
```

### 3.2 パラメータ化クエリ
```vb
' VB6 (SQL Injection リスクあり)
Dim sql As String
sql = "SELECT * FROM Customers WHERE CustomerID = " & customerID

' .NET Framework 4.8 (VB.NET) - 安全
Using cmd As New SqlCommand("SELECT * FROM Customers WHERE CustomerID = @CustomerID", conn)
    cmd.Parameters.AddWithValue("@CustomerID", customerID)
    ' 実行
End Using

' C# (.NET Framework 4.8) - 安全
using (SqlCommand cmd = new SqlCommand("SELECT * FROM Customers WHERE CustomerID = @CustomerID", conn))
{
    cmd.Parameters.AddWithValue("@CustomerID", customerID);
    // 実行
}
```

## 4. UIコントロールの移行

### 4.1 フォームイベント
```vb
' VB6
Private Sub Form_Load()
    ' 初期化処理
    Call InitializeForm
End Sub

Private Sub Form_Unload(Cancel As Integer)
    If MsgBox("終了しますか？", vbYesNo) = vbNo Then
        Cancel = True
    End If
End Sub

' .NET Framework 4.8 (Windows Forms)
Private Sub Form1_Load(sender As Object, e As EventArgs) Handles MyBase.Load
    ' 初期化処理
    InitializeForm()
End Sub

Private Sub Form1_FormClosing(sender As Object, e As FormClosingEventArgs) Handles MyBase.FormClosing
    If MessageBox.Show("終了しますか？", "確認", MessageBoxButtons.YesNo) = DialogResult.No Then
        e.Cancel = True
    End If
End Sub
```

### 4.2 コントロール配列の移行
```vb
' VB6 - コントロール配列
Private Sub cmdButton_Click(Index As Integer)
    Select Case Index
        Case 0
            ' Button 0 の処理
        Case 1
            ' Button 1 の処理
    End Select
End Sub

' .NET Framework 4.8 - イベントハンドラの共有
Private Sub Button_Click(sender As Object, e As EventArgs) Handles Button1.Click, Button2.Click
    Dim btn As Button = DirectCast(sender, Button)
    
    Select Case btn.Name
        Case "Button1"
            ' Button 1 の処理
        Case "Button2"
            ' Button 2 の処理
    End Select
End Sub

' または List<Button> を使用
Private buttons As New List(Of Button)()

Private Sub InitializeButtons()
    For i As Integer = 0 To 9
        Dim btn As New Button()
        btn.Name = "Button" & i
        btn.Tag = i
        AddHandler btn.Click, AddressOf DynamicButton_Click
        buttons.Add(btn)
    Next
End Sub

Private Sub DynamicButton_Click(sender As Object, e As EventArgs)
    Dim btn As Button = DirectCast(sender, Button)
    Dim index As Integer = CInt(btn.Tag)
    ' インデックスベースの処理
End Sub
```

## 5. COM相互運用

### 5.1 VB6 COMコンポーネントの.NETからの呼び出し
```csharp
// C# - VB6 COM DLLの参照
// 1. プロジェクトに COM 参照を追加
// 2. または tlbimp.exe でラッパー生成

using VB6BusinessLogic;  // COM参照

public class ComInteropExample
{
    public void UseVB6Component()
    {
        // COMオブジェクトの作成
        var vb6Object = new VB6BusinessClass();
        
        try
        {
            // メソッド呼び出し
            string result = vb6Object.ProcessData("input");
            
            // プロパティアクセス
            vb6Object.CustomerID = 123;
        }
        finally
        {
            // COM オブジェクトの解放
            if (vb6Object != null)
            {
                System.Runtime.InteropServices.Marshal.ReleaseComObject(vb6Object);
                vb6Object = null;
            }
        }
    }
}
```

### 5.2 .NETコンポーネントのCOM公開
```csharp
// C# - COMに公開する.NETクラス
using System.Runtime.InteropServices;

[ComVisible(true)]
[Guid("12345678-1234-1234-1234-123456789012")]
[ClassInterface(ClassInterfaceType.AutoDual)]
public class NetBusinessClass
{
    public string ProcessData(string input)
    {
        return "Processed: " + input;
    }
    
    public int CustomerID { get; set; }
}

// regasm.exe でCOM登録
// regasm MyAssembly.dll /tlb /codebase
```

## 6. 非同期処理の移行

### 6.1 BackgroundWorkerパターン (VB6タイマー → .NET)
```vb
' VB6 - Timer使用
Private Sub Timer1_Timer()
    Timer1.Enabled = False
    ' 長時間処理
    ProcessLongRunningTask
    Timer1.Enabled = True
End Sub

' .NET Framework 4.8 - BackgroundWorker
Private WithEvents bgWorker As New BackgroundWorker()

Private Sub StartProcess()
    bgWorker.WorkerReportsProgress = True
    bgWorker.RunWorkerAsync()
End Sub

Private Sub bgWorker_DoWork(sender As Object, e As DoWorkEventArgs) Handles bgWorker.DoWork
    ' バックグラウンドスレッドで実行
    ProcessLongRunningTask()
    bgWorker.ReportProgress(50)
End Sub

Private Sub bgWorker_ProgressChanged(sender As Object, e As ProgressChangedEventArgs) Handles bgWorker.ProgressChanged
    ' UIスレッドで実行
    ProgressBar1.Value = e.ProgressPercentage
End Sub
```

## 7. 設定管理の移行

### 7.1 INIファイル → App.config
```vb
' VB6 - INIファイル
Private Declare Function GetPrivateProfileString Lib "kernel32" Alias "GetPrivateProfileStringA" _
    (ByVal lpAppName As String, ByVal lpKeyName As String, ByVal lpDefault As String, _
     ByVal lpReturnedString As String, ByVal nSize As Long, ByVal lpFileName As String) As Long

Function ReadINI(Section As String, Key As String) As String
    Dim Buffer As String * 256
    GetPrivateProfileString Section, Key, "", Buffer, 256, App.Path & "\config.ini"
    ReadINI = Left$(Buffer, InStr(Buffer, Chr$(0)) - 1)
End Function
```

```xml
<!-- .NET Framework 4.8 - App.config -->
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <appSettings>
    <add key="DatabaseServer" value="localhost" />
    <add key="DatabaseName" value="MyDB" />
  </appSettings>
  <connectionStrings>
    <add name="DefaultConnection" 
         connectionString="Data Source=localhost;Initial Catalog=MyDB;Integrated Security=True" />
  </connectionStrings>
</configuration>
```

```csharp
// C# - 設定の読み取り
string dbServer = ConfigurationManager.AppSettings["DatabaseServer"];
string connStr = ConfigurationManager.ConnectionStrings["DefaultConnection"].ConnectionString;
```

## 8. 移行時の注意点とベストプラクティス

### 8.1 段階的移行戦略
1. **Phase 1**: データアクセス層を.NETで再実装
2. **Phase 2**: ビジネスロジックを.NETに移行
3. **Phase 3**: UIを Windows Forms/WPF で再構築

### 8.2 互換性維持のテクニック
- Microsoft.VisualBasic.dll の活用
- COM相互運用による段階的移行
- 並行運用期間の設定

### 8.3 パフォーマンス考慮事項
- Variant型 → 強い型付けへの変換
- 遅延バインディング → 事前バインディング
- 文字列連結 → StringBuilder使用

この移行パターン集を参考に、VB6アプリケーションを安全かつ効率的に.NET Framework 4.8へ移行できます。