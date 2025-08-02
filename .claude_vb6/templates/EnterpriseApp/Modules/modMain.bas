Attribute VB_Name = "modMain"
'**********************************************************************
' モジュール名: modMain
' 説明: アプリケーションエントリポイント
' 作成日: 2025/02/08
' 文字コード: Shift-JIS (必須)
'**********************************************************************

Option Explicit

' グローバル変数
Public g_CurrentUser As clsUser
Public g_ConfigManager As clsConfigManager
Public g_Logger As clsLogger

'**********************************************************************
' 関数名: Main
' 説明: アプリケーションエントリポイント
'**********************************************************************
Sub Main()
    On Error GoTo ErrorHandler
    
    ' アプリケーション初期化
    If Not InitializeApplication() Then
        MsgBox "アプリケーションの初期化に失敗しました。", _
               vbCritical, App.Title
        End
    End If
    
    ' ログイン画面表示
    Dim frmLogin As frmLogin
    Set frmLogin = New frmLogin
    frmLogin.Show vbModal
    
    ' ログイン成功チェック
    If g_CurrentUser Is Nothing Then
        ' キャンセルされた
        TerminateApplication
        End
    End If
    
    ' メインフォーム表示
    Dim frmMain As frmMain
    Set frmMain = New frmMain
    frmMain.Show
    
    Exit Sub
    
ErrorHandler:
    LogError "Main", Err.Number, Err.Description
    MsgBox "致命的なエラーが発生しました。" & vbCrLf & _
           Err.Description, vbCritical, App.Title
    TerminateApplication
    End
End Sub

'**********************************************************************
' 関数名: InitializeApplication
' 説明: アプリケーションの初期化
' 戻り値: Boolean - 成功/失敗
'**********************************************************************
Private Function InitializeApplication() As Boolean
    On Error GoTo ErrorHandler
    
    ' 二重起動チェック
    If App.PrevInstance Then
        MsgBox "アプリケーションは既に起動しています。", _
               vbInformation, App.Title
        InitializeApplication = False
        Exit Function
    End If
    
    ' 設定マネージャー初期化
    Set g_ConfigManager = New clsConfigManager
    If Not g_ConfigManager.Initialize(App.Path & "\config.ini") Then
        InitializeApplication = False
        Exit Function
    End If
    
    ' ロガー初期化
    Set g_Logger = New clsLogger
    g_Logger.Initialize App.Path & "\Logs"
    g_Logger.LogLevel = g_ConfigManager.GetValue("System", "LogLevel", "INFO")
    
    ' データベース接続テスト
    If Not TestDatabaseConnection() Then
        MsgBox "データベースに接続できません。", _
               vbCritical, App.Title
        InitializeApplication = False
        Exit Function
    End If
    
    ' 必要なディレクトリ作成
    CreateRequiredDirectories
    
    ' アプリケーション設定
    App.Title = g_ConfigManager.GetValue("Application", "Title", "Enterprise App")
    
    g_Logger.Log "INFO", "アプリケーションが起動しました"
    InitializeApplication = True
    Exit Function
    
ErrorHandler:
    InitializeApplication = False
End Function

'**********************************************************************
' 関数名: TerminateApplication
' 説明: アプリケーションの終了処理
'**********************************************************************
Public Sub TerminateApplication()
    On Error Resume Next
    
    ' ログ出力
    If Not g_Logger Is Nothing Then
        g_Logger.Log "INFO", "アプリケーションを終了します"
        g_Logger.Terminate
        Set g_Logger = Nothing
    End If
    
    ' オブジェクト解放
    Set g_CurrentUser = Nothing
    Set g_ConfigManager = Nothing
    
    ' データベース接続クローズ
    CloseAllDatabaseConnections
End Sub

'**********************************************************************
' 関数名: TestDatabaseConnection
' 説明: データベース接続テスト
' 戻り値: Boolean - 成功/失敗
'**********************************************************************
Private Function TestDatabaseConnection() As Boolean
    Dim conn As ADODB.Connection
    
    On Error GoTo ErrorHandler
    
    Set conn = New ADODB.Connection
    conn.ConnectionString = g_ConfigManager.GetValue("Database", "ConnectionString", "")
    conn.ConnectionTimeout = 15
    conn.Open
    
    ' 接続成功
    conn.Close
    Set conn = Nothing
    TestDatabaseConnection = True
    Exit Function
    
ErrorHandler:
    If Not conn Is Nothing Then
        If conn.State = adStateOpen Then conn.Close
        Set conn = Nothing
    End If
    TestDatabaseConnection = False
End Function

'**********************************************************************
' 関数名: CreateRequiredDirectories
' 説明: 必要なディレクトリを作成
'**********************************************************************
Private Sub CreateRequiredDirectories()
    Dim fso As FileSystemObject
    
    On Error Resume Next
    
    Set fso = New FileSystemObject
    
    ' ログディレクトリ
    If Not fso.FolderExists(App.Path & "\Logs") Then
        fso.CreateFolder App.Path & "\Logs"
    End If
    
    ' テンポラリディレクトリ
    If Not fso.FolderExists(App.Path & "\Temp") Then
        fso.CreateFolder App.Path & "\Temp"
    End If
    
    ' レポートディレクトリ
    If Not fso.FolderExists(App.Path & "\Reports") Then
        fso.CreateFolder App.Path & "\Reports"
    End If
    
    Set fso = Nothing
End Sub

'**********************************************************************
' 関数名: ShowAboutDialog
' 説明: バージョン情報ダイアログ表示
'**********************************************************************
Public Sub ShowAboutDialog()
    Dim msg As String
    
    msg = App.Title & vbCrLf & vbCrLf & _
          "バージョン: " & App.Major & "." & App.Minor & "." & App.Revision & vbCrLf & _
          App.LegalCopyright & vbCrLf & vbCrLf & _
          App.Comments
    
    MsgBox msg, vbInformation, "バージョン情報"
End Sub