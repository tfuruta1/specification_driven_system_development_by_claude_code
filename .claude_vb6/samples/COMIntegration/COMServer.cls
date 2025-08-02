VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "COMServer"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'**********************************************************************
' クラス名: COMServer
' 説明: COMサーバーコンポーネントの実装例
' 作成日: 2025/02/08
' 文字コード: Shift-JIS (必須)
' 
' COM登録方法:
' 1. VB6でActiveX DLLプロジェクトとしてビルド
' 2. regsvr32 MyCOMServer.dll で登録
'**********************************************************************

Option Explicit

' イベント宣言
Public Event ProcessCompleted(Result As String)
Public Event ProcessError(ErrorMessage As String)
Public Event ProgressUpdate(PercentComplete As Integer)

' プライベート変数
Private m_ServerName As String
Private m_Version As String
Private m_IsInitialized As Boolean
Private m_Logger As Object

' 定数
Private Const SERVER_VERSION As String = "1.0.0"
Private Const MAX_CONNECTIONS As Integer = 100

'**********************************************************************
' 初期化・終了処理
'**********************************************************************
Private Sub Class_Initialize()
    m_ServerName = "VB6 COM Server"
    m_Version = SERVER_VERSION
    m_IsInitialized = False
    
    ' ロガーの初期化
    On Error Resume Next
    Set m_Logger = CreateObject("Logger.FileLogger")
    On Error GoTo 0
End Sub

Private Sub Class_Terminate()
    ' リソースのクリーンアップ
    If Not m_Logger Is Nothing Then
        m_Logger.Close
        Set m_Logger = Nothing
    End If
    
    m_IsInitialized = False
End Sub

'**********************************************************************
' パブリックプロパティ
'**********************************************************************
Public Property Get ServerName() As String
    ServerName = m_ServerName
End Property

Public Property Get Version() As String
    Version = m_Version
End Property

Public Property Get IsInitialized() As Boolean
    IsInitialized = m_IsInitialized
End Property

'**********************************************************************
' パブリックメソッド
'**********************************************************************

'----------------------------------------------------------------------
' 初期化メソッド
'----------------------------------------------------------------------
Public Function Initialize(ConfigPath As String) As Boolean
    On Error GoTo ErrorHandler
    
    ' 設定ファイルの読み込み
    If LoadConfiguration(ConfigPath) Then
        m_IsInitialized = True
        LogInfo "Server initialized successfully"
        Initialize = True
    Else
        Initialize = False
    End If
    
    Exit Function
    
ErrorHandler:
    LogError "Initialize", Err.Number, Err.Description
    Initialize = False
End Function

'----------------------------------------------------------------------
' データ処理メソッド
'----------------------------------------------------------------------
Public Function ProcessData(InputData As Variant) As Variant
    Dim result As Variant
    Dim i As Integer
    
    On Error GoTo ErrorHandler
    
    ' 初期化チェック
    If Not m_IsInitialized Then
        Err.Raise vbObjectError + 1001, "COMServer.ProcessData", _
                 "サーバーが初期化されていません"
    End If
    
    ' プログレスイベント発行
    RaiseEvent ProgressUpdate(0)
    
    ' データ処理（サンプル）
    If IsArray(InputData) Then
        ReDim result(LBound(InputData) To UBound(InputData))
        
        For i = LBound(InputData) To UBound(InputData)
            result(i) = ProcessSingleItem(InputData(i))
            
            ' プログレス更新
            RaiseEvent ProgressUpdate(CInt((i / UBound(InputData)) * 100))
        Next i
    Else
        result = ProcessSingleItem(InputData)
    End If
    
    ' 完了イベント
    RaiseEvent ProcessCompleted("処理が完了しました")
    ProcessData = result
    
    Exit Function
    
ErrorHandler:
    RaiseEvent ProcessError(Err.Description)
    LogError "ProcessData", Err.Number, Err.Description
    ProcessData = Empty
End Function

'----------------------------------------------------------------------
' 非同期処理メソッド
'----------------------------------------------------------------------
Public Sub ProcessDataAsync(InputData As Variant, CallbackObject As Object)
    On Error GoTo ErrorHandler
    
    ' スレッドプールを使用した非同期処理
    Dim threadPool As Object
    Set threadPool = CreateObject("ThreadPool.Manager")
    
    threadPool.QueueTask Me, "ProcessData", InputData, CallbackObject
    
    Exit Sub
    
ErrorHandler:
    LogError "ProcessDataAsync", Err.Number, Err.Description
End Sub

'----------------------------------------------------------------------
' データベースアクセスメソッド
'----------------------------------------------------------------------
Public Function ExecuteQuery(SQL As String) As ADODB.Recordset
    Dim conn As ADODB.Connection
    Dim rs As ADODB.Recordset
    
    On Error GoTo ErrorHandler
    
    ' 接続を取得
    Set conn = GetDatabaseConnection()
    
    ' クエリ実行
    Set rs = New ADODB.Recordset
    rs.Open SQL, conn, adOpenStatic, adLockReadOnly
    
    ' 切断されたレコードセットを返す
    Set rs.ActiveConnection = Nothing
    conn.Close
    Set conn = Nothing
    
    Set ExecuteQuery = rs
    Exit Function
    
ErrorHandler:
    If Not conn Is Nothing Then
        If conn.State = adStateOpen Then conn.Close
        Set conn = Nothing
    End If
    LogError "ExecuteQuery", Err.Number, Err.Description
    Set ExecuteQuery = Nothing
End Function

'**********************************************************************
' COM+トランザクションサポート
'**********************************************************************
Public Function ExecuteTransaction(Operations As Collection) As Boolean
    Dim objContext As Object
    Dim operation As Variant
    Dim success As Boolean
    
    On Error GoTo ErrorHandler
    
    ' COM+コンテキストを取得
    Set objContext = GetObjectContext()
    
    success = True
    
    ' 各操作を実行
    For Each operation In Operations
        If Not ExecuteSingleOperation(operation) Then
            success = False
            Exit For
        End If
    Next
    
    ' トランザクションのコミット/ロールバック
    If success Then
        objContext.SetComplete
        ExecuteTransaction = True
    Else
        objContext.SetAbort
        ExecuteTransaction = False
    End If
    
    Exit Function
    
ErrorHandler:
    If Not objContext Is Nothing Then
        objContext.SetAbort
    End If
    LogError "ExecuteTransaction", Err.Number, Err.Description
    ExecuteTransaction = False
End Function

'**********************************************************************
' プライベートメソッド
'**********************************************************************
Private Function ProcessSingleItem(Item As Variant) As Variant
    ' サンプル処理: 数値を2倍にする
    If IsNumeric(Item) Then
        ProcessSingleItem = CDbl(Item) * 2
    Else
        ProcessSingleItem = UCase(CStr(Item))
    End If
End Function

Private Function LoadConfiguration(ConfigPath As String) As Boolean
    Dim fso As Object
    
    On Error GoTo ErrorHandler
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    If fso.FileExists(ConfigPath) Then
        ' 設定ファイルを読み込む
        ' 実際の実装では、INIファイルやXMLから設定を読み込む
        LoadConfiguration = True
    Else
        LoadConfiguration = False
    End If
    
    Set fso = Nothing
    Exit Function
    
ErrorHandler:
    LoadConfiguration = False
End Function

Private Function GetDatabaseConnection() As ADODB.Connection
    Dim conn As ADODB.Connection
    
    Set conn = New ADODB.Connection
    conn.ConnectionString = "Provider=SQLOLEDB;" & _
                           "Data Source=localhost;" & _
                           "Initial Catalog=TestDB;" & _
                           "Integrated Security=SSPI;"
    conn.Open
    
    Set GetDatabaseConnection = conn
End Function

Private Function ExecuteSingleOperation(operation As Variant) As Boolean
    ' 各操作の実行ロジック
    On Error Resume Next
    
    ' 操作を実行
    operation.Execute
    
    ExecuteSingleOperation = (Err.Number = 0)
End Function

'**********************************************************************
' ログ処理
'**********************************************************************
Private Sub LogInfo(Message As String)
    If Not m_Logger Is Nothing Then
        m_Logger.LogInfo Message
    End If
End Sub

Private Sub LogError(Source As String, ErrorNumber As Long, ErrorDesc As String)
    If Not m_Logger Is Nothing Then
        m_Logger.LogError Source, ErrorNumber, ErrorDesc
    End If
End Sub

'**********************************************************************
' COMインターフェース実装例
'**********************************************************************
' IDataProcessor インターフェースを実装する場合
' Implements IDataProcessor
' 
' Private Function IDataProcessor_Process(Data As Variant) As Variant
'     IDataProcessor_Process = ProcessData(Data)
' End Function
' 
' Private Property Get IDataProcessor_Version() As String
'     IDataProcessor_Version = m_Version
' End Property