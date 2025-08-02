Attribute VB_Name = "modSingleton"
'**********************************************************************
' モジュール名: modSingleton
' 説明: Singletonパターンの実装例
' 作成日: 2025/02/08
' 文字コード: Shift-JIS (必須)
'**********************************************************************

Option Explicit

' Singletonインスタンス保持用
Private m_ConfigInstance As clsConfigManager
Private m_LoggerInstance As clsLogger
Private m_DBPoolInstance As clsDatabasePool

'**********************************************************************
' 関数名: GetConfigManager
' 説明: 設定マネージャーのSingletonインスタンス取得
' 戻り値: clsConfigManager
'**********************************************************************
Public Function GetConfigManager() As clsConfigManager
    If m_ConfigInstance Is Nothing Then
        Set m_ConfigInstance = New clsConfigManager
        m_ConfigInstance.Initialize
    End If
    Set GetConfigManager = m_ConfigInstance
End Function

'**********************************************************************
' 関数名: GetLogger
' 説明: ロガーのSingletonインスタンス取得
' 戻り値: clsLogger
'**********************************************************************
Public Function GetLogger() As clsLogger
    If m_LoggerInstance Is Nothing Then
        Set m_LoggerInstance = New clsLogger
        m_LoggerInstance.Initialize App.Path & "\Logs"
    End If
    Set GetLogger = m_LoggerInstance
End Function

'**********************************************************************
' 関数名: GetDatabasePool
' 説明: データベース接続プールのSingletonインスタンス取得
' 戻り値: clsDatabasePool
'**********************************************************************
Public Function GetDatabasePool() As clsDatabasePool
    If m_DBPoolInstance Is Nothing Then
        Set m_DBPoolInstance = New clsDatabasePool
        m_DBPoolInstance.Initialize 10 ' 最大接続数
    End If
    Set GetDatabasePool = m_DBPoolInstance
End Function

'**********************************************************************
' 関数名: ReleaseAllSingletons
' 説明: すべてのSingletonインスタンスを解放
'**********************************************************************
Public Sub ReleaseAllSingletons()
    If Not m_ConfigInstance Is Nothing Then
        m_ConfigInstance.Terminate
        Set m_ConfigInstance = Nothing
    End If
    
    If Not m_LoggerInstance Is Nothing Then
        m_LoggerInstance.Terminate
        Set m_LoggerInstance = Nothing
    End If
    
    If Not m_DBPoolInstance Is Nothing Then
        m_DBPoolInstance.Terminate
        Set m_DBPoolInstance = Nothing
    End If
End Sub

'**********************************************************************
' Singleton実装例: clsConfigManager
'**********************************************************************
' clsConfigManager.cls として別ファイルで実装
'
' Option Explicit
' 
' Private m_Config As Dictionary
' Private m_ConfigFile As String
' 
' Public Sub Initialize()
'     Set m_Config = New Dictionary
'     m_ConfigFile = App.Path & "\config.ini"
'     LoadConfiguration
' End Sub
' 
' Private Sub LoadConfiguration()
'     ' INIファイルから設定を読み込み
'     m_Config.Add "DatabaseServer", GetINIValue("Database", "Server", m_ConfigFile)
'     m_Config.Add "DatabaseName", GetINIValue("Database", "Name", m_ConfigFile)
'     m_Config.Add "LogLevel", GetINIValue("System", "LogLevel", m_ConfigFile)
'     m_Config.Add "MaxRetryCount", CLng(GetINIValue("System", "MaxRetryCount", m_ConfigFile))
' End Sub
' 
' Public Property Get Value(Key As String) As Variant
'     If m_Config.Exists(Key) Then
'         Value = m_Config(Key)
'     Else
'         Value = Empty
'     End If
' End Property
' 
' Public Sub SetValue(Key As String, Value As Variant)
'     If m_Config.Exists(Key) Then
'         m_Config(Key) = Value
'     Else
'         m_Config.Add Key, Value
'     End If
'     SaveConfiguration
' End Sub
' 
' Private Sub SaveConfiguration()
'     ' INIファイルに設定を保存
'     Dim key As Variant
'     For Each key In m_Config.Keys
'         WriteINIValue "Config", CStr(key), CStr(m_Config(key)), m_ConfigFile
'     Next
' End Sub
' 
' Public Sub Terminate()
'     SaveConfiguration
'     Set m_Config = Nothing
' End Sub

'**********************************************************************
' Singleton実装例: clsLogger
'**********************************************************************
' clsLogger.cls として別ファイルで実装
'
' Option Explicit
' 
' Private m_LogPath As String
' Private m_LogLevel As Integer
' Private m_FileHandle As Integer
' 
' Public Enum LogLevel
'     llDebug = 0
'     llInfo = 1
'     llWarning = 2
'     llError = 3
'     llCritical = 4
' End Enum
' 
' Public Sub Initialize(LogPath As String)
'     m_LogPath = LogPath
'     m_LogLevel = llInfo
'     
'     ' ログディレクトリの作成
'     Dim fso As Object
'     Set fso = CreateObject("Scripting.FileSystemObject")
'     If Not fso.FolderExists(m_LogPath) Then
'         fso.CreateFolder m_LogPath
'     End If
'     Set fso = Nothing
' End Sub
' 
' Public Sub Log(Level As LogLevel, Message As String, Optional Source As String = "")
'     If Level < m_LogLevel Then Exit Sub
'     
'     Dim logFile As String
'     Dim logEntry As String
'     
'     logFile = m_LogPath & "\" & Format(Date, "yyyymmdd") & ".log"
'     
'     logEntry = Format(Now, "yyyy-mm-dd hh:nn:ss") & "|" & _
'                GetLevelString(Level) & "|" & _
'                IIf(Source <> "", Source & "|", "") & _
'                Message
'     
'     ' ファイルに書き込み
'     m_FileHandle = FreeFile
'     Open logFile For Append As #m_FileHandle
'     Print #m_FileHandle, logEntry
'     Close #m_FileHandle
' End Sub
' 
' Private Function GetLevelString(Level As LogLevel) As String
'     Select Case Level
'         Case llDebug: GetLevelString = "DEBUG"
'         Case llInfo: GetLevelString = "INFO"
'         Case llWarning: GetLevelString = "WARN"
'         Case llError: GetLevelString = "ERROR"
'         Case llCritical: GetLevelString = "CRITICAL"
'     End Select
' End Function
' 
' Public Property Let LogLevel(Value As LogLevel)
'     m_LogLevel = Value
' End Property
' 
' Public Property Get LogLevel() As LogLevel
'     LogLevel = m_LogLevel
' End Property
' 
' Public Sub Terminate()
'     ' クリーンアップ処理
' End Sub

'**********************************************************************
' Singleton実装例: clsDatabasePool
'**********************************************************************
' clsDatabasePool.cls として別ファイルで実装
'
' Option Explicit
' 
' Private m_ConnectionPool As Collection
' Private m_MaxPoolSize As Integer
' Private m_ConnectionString As String
' 
' Public Sub Initialize(MaxPoolSize As Integer)
'     Set m_ConnectionPool = New Collection
'     m_MaxPoolSize = MaxPoolSize
'     
'     ' 設定から接続文字列を取得
'     Dim config As clsConfigManager
'     Set config = GetConfigManager()
'     
'     m_ConnectionString = "Provider=SQLOLEDB;" & _
'                         "Data Source=" & config.Value("DatabaseServer") & ";" & _
'                         "Initial Catalog=" & config.Value("DatabaseName") & ";" & _
'                         "Integrated Security=SSPI;"
' End Sub
' 
' Public Function GetConnection() As ADODB.Connection
'     Dim conn As ADODB.Connection
'     Dim i As Integer
'     
'     ' プールから利用可能な接続を探す
'     For i = m_ConnectionPool.Count To 1 Step -1
'         Set conn = m_ConnectionPool(i)
'         If conn.State = adStateOpen Then
'             m_ConnectionPool.Remove i
'             Set GetConnection = conn
'             Exit Function
'         End If
'     Next i
'     
'     ' 新規接続を作成
'     Set conn = New ADODB.Connection
'     conn.ConnectionString = m_ConnectionString
'     conn.CursorLocation = adUseClient
'     conn.Open
'     
'     Set GetConnection = conn
' End Function
' 
' Public Sub ReturnConnection(conn As ADODB.Connection)
'     If m_ConnectionPool.Count < m_MaxPoolSize Then
'         If conn.State = adStateOpen Then
'             m_ConnectionPool.Add conn
'         End If
'     Else
'         conn.Close
'         Set conn = Nothing
'     End If
' End Sub
' 
' Public Sub Terminate()
'     Dim conn As ADODB.Connection
'     
'     ' すべての接続を閉じる
'     Do While m_ConnectionPool.Count > 0
'         Set conn = m_ConnectionPool(1)
'         If conn.State = adStateOpen Then conn.Close
'         Set conn = Nothing
'         m_ConnectionPool.Remove 1
'     Loop
'     
'     Set m_ConnectionPool = Nothing
' End Sub

'**********************************************************************
' 使用例
'**********************************************************************
Public Sub DemoSingletonUsage()
    Dim config As clsConfigManager
    Dim logger As clsLogger
    Dim dbPool As clsDatabasePool
    Dim conn As ADODB.Connection
    
    On Error GoTo ErrorHandler
    
    ' 設定マネージャーの使用
    Set config = GetConfigManager()
    Debug.Print "Database Server: " & config.Value("DatabaseServer")
    
    ' ロガーの使用
    Set logger = GetLogger()
    logger.Log llInfo, "アプリケーションを開始しました", "DemoSingletonUsage"
    
    ' データベース接続プールの使用
    Set dbPool = GetDatabasePool()
    Set conn = dbPool.GetConnection()
    
    ' データベース操作
    ' ...
    
    ' 接続をプールに返却
    dbPool.ReturnConnection conn
    
    logger.Log llInfo, "処理が完了しました", "DemoSingletonUsage"
    
    Exit Sub
    
    ErrorHandler:
    If Not logger Is Nothing Then
        logger.Log llError, "エラーが発生しました: " & Err.Description, "DemoSingletonUsage"
    End If
End Sub