Attribute VB_Name = "modADOPattern"
'**********************************************************************
' モジュール名: modADOPattern
' 説明: ADOを使用したデータベースアクセスパターン
' 作成日: 2025/02/08
' 文字コード: Shift-JIS (必須)
'**********************************************************************

Option Explicit

' ADO定数
' 参照設定: Microsoft ActiveX Data Objects 2.8 Library

' 接続文字列の例
Private Const CONN_STRING_SQLSERVER As String = _
    "Provider=SQLOLEDB;" & _
    "Data Source=localhost;" & _
    "Initial Catalog=TestDB;" & _
    "Integrated Security=SSPI;"

Private Const CONN_STRING_ACCESS As String = _
    "Provider=Microsoft.Jet.OLEDB.4.0;" & _
    "Data Source=C:\Data\MyDatabase.mdb;"

Private Const CONN_STRING_ORACLE As String = _
    "Provider=OraOLEDB.Oracle;" & _
    "Data Source=OracleDB;" & _
    "User ID=scott;Password=tiger;"

'**********************************************************************
' 関数名: GetConnection
' 説明: データベース接続を取得
' 引数: ConnectionType - 接続タイプ
' 戻り値: ADODB.Connection
'**********************************************************************
Public Function GetConnection(Optional ConnectionType As String = "SQLSERVER") As ADODB.Connection
    Dim conn As ADODB.Connection
    Dim connString As String
    
    On Error GoTo ErrorHandler
    
    ' 接続タイプに応じた接続文字列を選択
    Select Case UCase(ConnectionType)
        Case "SQLSERVER"
            connString = CONN_STRING_SQLSERVER
        Case "ACCESS"
            connString = CONN_STRING_ACCESS
        Case "ORACLE"
            connString = CONN_STRING_ORACLE
        Case Else
            Err.Raise vbObjectError + 1001, , "不明な接続タイプ: " & ConnectionType
    End Select
    
    ' 接続を作成
    Set conn = New ADODB.Connection
    With conn
        .ConnectionString = connString
        .CursorLocation = adUseClient
        .ConnectionTimeout = 30
        .CommandTimeout = 30
        .Open
    End With
    
    Set GetConnection = conn
    Exit Function
    
ErrorHandler:
    If Not conn Is Nothing Then
        If conn.State = adStateOpen Then conn.Close
        Set conn = Nothing
    End If
    Err.Raise Err.Number, "GetConnection", Err.Description
End Function

'**********************************************************************
' 関数名: ExecuteQuery
' 説明: SELECTクエリを実行
' 引数: SQL - SQL文
'       Connection - データベース接続
' 戻り値: ADODB.Recordset
'**********************************************************************
Public Function ExecuteQuery(SQL As String, Connection As ADODB.Connection) As ADODB.Recordset
    Dim rs As ADODB.Recordset
    
    On Error GoTo ErrorHandler
    
    Set rs = New ADODB.Recordset
    With rs
        .CursorLocation = adUseClient
        .CursorType = adOpenStatic
        .LockType = adLockReadOnly
        .Open SQL, Connection
    End With
    
    ' 切断されたレコードセットを返す
    Set rs.ActiveConnection = Nothing
    Set ExecuteQuery = rs
    Exit Function
    
ErrorHandler:
    If Not rs Is Nothing Then
        If rs.State = adStateOpen Then rs.Close
        Set rs = Nothing
    End If
    Err.Raise Err.Number, "ExecuteQuery", Err.Description
End Function

'**********************************************************************
' 関数名: ExecuteCommand
' 説明: INSERT/UPDATE/DELETEコマンドを実行
' 引数: SQL - SQL文
'       Connection - データベース接続
' 戻り値: 影響を受けたレコード数
'**********************************************************************
Public Function ExecuteCommand(SQL As String, Connection As ADODB.Connection) As Long
    Dim recordsAffected As Long
    
    On Error GoTo ErrorHandler
    
    Connection.Execute SQL, recordsAffected, adExecuteNoRecords
    ExecuteCommand = recordsAffected
    Exit Function
    
ErrorHandler:
    Err.Raise Err.Number, "ExecuteCommand", Err.Description
End Function

'**********************************************************************
' 関数名: ExecuteStoredProc
' 説明: ストアドプロシージャを実行
' 引数: ProcName - プロシージャ名
'       Parameters - パラメータ配列
'       Connection - データベース接続
' 戻り値: ADODB.Recordset
'**********************************************************************
Public Function ExecuteStoredProc(ProcName As String, _
                                Parameters() As Variant, _
                                Connection As ADODB.Connection) As ADODB.Recordset
    Dim cmd As ADODB.Command
    Dim rs As ADODB.Recordset
    Dim i As Integer
    
    On Error GoTo ErrorHandler
    
    Set cmd = New ADODB.Command
    With cmd
        .ActiveConnection = Connection
        .CommandText = ProcName
        .CommandType = adCmdStoredProc
        
        ' パラメータを自動更新
        .Parameters.Refresh
        
        ' パラメータ値を設定
        For i = 0 To UBound(Parameters)
            If i + 1 < .Parameters.Count Then
                .Parameters(i + 1).Value = Parameters(i)
            End If
        Next i
        
        ' 実行
        Set rs = .Execute
    End With
    
    Set ExecuteStoredProc = rs
    Set cmd = Nothing
    Exit Function
    
ErrorHandler:
    If Not cmd Is Nothing Then Set cmd = Nothing
    If Not rs Is Nothing Then
        If rs.State = adStateOpen Then rs.Close
        Set rs = Nothing
    End If
    Err.Raise Err.Number, "ExecuteStoredProc", Err.Description
End Function

'**********************************************************************
' 関数名: BeginTransaction
' 説明: トランザクションを開始
' 引数: Connection - データベース接続
' 戻り値: トランザクションレベル
'**********************************************************************
Public Function BeginTransaction(Connection As ADODB.Connection) As Long
    BeginTransaction = Connection.BeginTrans()
End Function

'**********************************************************************
' 関数名: CommitTransaction
' 説明: トランザクションをコミット
' 引数: Connection - データベース接続
'**********************************************************************
Public Sub CommitTransaction(Connection As ADODB.Connection)
    Connection.CommitTrans
End Sub

'**********************************************************************
' 関数名: RollbackTransaction
' 説明: トランザクションをロールバック
' 引数: Connection - データベース接続
'**********************************************************************
Public Sub RollbackTransaction(Connection As ADODB.Connection)
    Connection.RollbackTrans
End Sub

'**********************************************************************
' 関数名: GetParameterizedCommand
' 説明: パラメータ化クエリの作成（SQLインジェクション対策）
' 引数: SQL - SQL文（?をプレースホルダーとして使用）
'       Connection - データベース接続
' 戻り値: ADODB.Command
'**********************************************************************
Public Function GetParameterizedCommand(SQL As String, _
                                      Connection As ADODB.Connection) As ADODB.Command
    Dim cmd As ADODB.Command
    
    Set cmd = New ADODB.Command
    With cmd
        .ActiveConnection = Connection
        .CommandText = SQL
        .CommandType = adCmdText
        .Prepared = True
    End With
    
    Set GetParameterizedCommand = cmd
End Function

'**********************************************************************
' 関数名: AddParameter
' 説明: コマンドにパラメータを追加
' 引数: Command - ADODB.Commandオブジェクト
'       Name - パラメータ名
'       DataType - データ型
'       Size - サイズ
'       Value - 値
'**********************************************************************
Public Sub AddParameter(Command As ADODB.Command, _
                       Name As String, _
                       DataType As DataTypeEnum, _
                       Size As Long, _
                       Value As Variant)
    Dim param As ADODB.Parameter
    
    Set param = Command.CreateParameter(Name, DataType, adParamInput, Size, Value)
    Command.Parameters.Append param
End Sub

'**********************************************************************
' 関数名: GetScalarValue
' 説明: 単一値を取得
' 引数: SQL - SQL文
'       Connection - データベース接続
' 戻り値: スカラー値
'**********************************************************************
Public Function GetScalarValue(SQL As String, Connection As ADODB.Connection) As Variant
    Dim rs As ADODB.Recordset
    
    On Error GoTo ErrorHandler
    
    Set rs = ExecuteQuery(SQL, Connection)
    
    If Not rs.EOF Then
        GetScalarValue = rs.Fields(0).Value
    Else
        GetScalarValue = Null
    End If
    
    rs.Close
    Set rs = Nothing
    Exit Function
    
ErrorHandler:
    If Not rs Is Nothing Then
        If rs.State = adStateOpen Then rs.Close
        Set rs = Nothing
    End If
    Err.Raise Err.Number, "GetScalarValue", Err.Description
End Function

'**********************************************************************
' 関数名: RecordsetToCollection
' 説明: レコードセットをコレクションに変換
' 引数: rs - ADODB.Recordset
'       ClassName - オブジェクトクラス名
' 戻り値: Collection
'**********************************************************************
Public Function RecordsetToCollection(rs As ADODB.Recordset, _
                                    ClassName As String) As Collection
    Dim col As Collection
    Dim obj As Object
    Dim fld As ADODB.Field
    
    Set col = New Collection
    
    Do While Not rs.EOF
        ' オブジェクトを動的に作成
        Set obj = CreateObject(ClassName)
        
        ' フィールド値をマッピング
        For Each fld In rs.Fields
            CallByName obj, fld.Name, VbLet, fld.Value
        Next fld
        
        col.Add obj
        rs.MoveNext
    Loop
    
    Set RecordsetToCollection = col
End Function

'**********************************************************************
' 関数名: BulkInsert
' 説明: バルクインサートの実行
' 引数: TableName - テーブル名
'       Data - データ配列
'       Connection - データベース接続
' 戻り値: 挿入されたレコード数
'**********************************************************************
Public Function BulkInsert(TableName As String, _
                          Data As Variant, _
                          Connection As ADODB.Connection) As Long
    Dim rs As ADODB.Recordset
    Dim i As Long, j As Long
    Dim recordCount As Long
    
    On Error GoTo ErrorHandler
    
    ' トランザクション開始
    BeginTransaction Connection
    
    ' レコードセットを開く
    Set rs = New ADODB.Recordset
    rs.Open TableName, Connection, adOpenDynamic, adLockOptimistic, adCmdTable
    
    ' データを挿入
    For i = LBound(Data, 1) To UBound(Data, 1)
        rs.AddNew
        For j = LBound(Data, 2) To UBound(Data, 2)
            rs.Fields(j).Value = Data(i, j)
        Next j
        rs.Update
        recordCount = recordCount + 1
    Next i
    
    ' コミット
    CommitTransaction Connection
    
    rs.Close
    Set rs = Nothing
    
    BulkInsert = recordCount
    Exit Function
    
ErrorHandler:
    RollbackTransaction Connection
    If Not rs Is Nothing Then
        If rs.State = adStateOpen Then rs.Close
        Set rs = Nothing
    End If
    Err.Raise Err.Number, "BulkInsert", Err.Description
End Function

'**********************************************************************
' 使用例
'**********************************************************************
Public Sub DemoADOUsage()
    Dim conn As ADODB.Connection
    Dim rs As ADODB.Recordset
    Dim cmd As ADODB.Command
    Dim recordsAffected As Long
    
    On Error GoTo ErrorHandler
    
    ' 接続を取得
    Set conn = GetConnection("SQLSERVER")
    
    ' 1. シンプルなSELECT
    Set rs = ExecuteQuery("SELECT * FROM Customers WHERE City = 'Tokyo'", conn)
    Debug.Print "Record Count: " & rs.RecordCount
    rs.Close
    
    ' 2. パラメータ化クエリ（SQLインジェクション対策）
    Set cmd = GetParameterizedCommand("SELECT * FROM Customers WHERE CustomerID = ?", conn)
    AddParameter cmd, "CustomerID", adInteger, 4, 12345
    Set rs = cmd.Execute
    
    ' 3. トランザクション処理
    BeginTransaction conn
    
    recordsAffected = ExecuteCommand("UPDATE Customers SET City = 'Osaka' WHERE CustomerID = 12345", conn)
    Debug.Print "Updated Records: " & recordsAffected
    
    If recordsAffected > 0 Then
        CommitTransaction conn
        Debug.Print "Transaction Committed"
    Else
        RollbackTransaction conn
        Debug.Print "Transaction Rolled Back"
    End If
    
    ' クリーンアップ
    conn.Close
    Set conn = Nothing
    
    Exit Sub
    
ErrorHandler:
    If Not conn Is Nothing Then
        If conn.State = adStateOpen Then
            RollbackTransaction conn
            conn.Close
        End If
        Set conn = Nothing
    End If
    
    MsgBox "Error: " & Err.Description, vbCritical
End Sub