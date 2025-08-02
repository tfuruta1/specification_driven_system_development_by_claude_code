Attribute VB_Name = "modErrorHandling"
'**********************************************************************
' モジュール名: modErrorHandling
' 説明: エラーハンドリングのベストプラクティス実装
' 作成日: 2025/02/08
' 文字コード: Shift-JIS (必須)
'**********************************************************************

Option Explicit

' エラーコード定義
Public Const ERR_DATABASE_CONNECTION As Long = vbObjectError + 1001
Public Const ERR_VALIDATION_FAILED As Long = vbObjectError + 1002
Public Const ERR_FILE_NOT_FOUND As Long = vbObjectError + 1003
Public Const ERR_PERMISSION_DENIED As Long = vbObjectError + 1004

' グローバルエラーハンドラー
Private g_ErrorLog As Collection

'**********************************************************************
' 関数名: InitializeErrorHandler
' 説明: エラーハンドラーの初期化
'**********************************************************************
Public Sub InitializeErrorHandler()
    Set g_ErrorLog = New Collection
End Sub

'**********************************************************************
' 関数名: HandleError
' 説明: 統一エラーハンドリング関数
' 引数: 
'   Source - エラー発生元
'   ShowMessage - ユーザーへのメッセージ表示有無
' 戻り値: False（エラー時の標準戻り値）
'**********************************************************************
Public Function HandleError(Source As String, Optional ShowMessage As Boolean = True) As Boolean
    Dim errorInfo As String
    Dim userMessage As String
    
    ' エラー情報の構築
    errorInfo = "エラー発生元: " & Source & vbCrLf & _
                "エラー番号: " & Err.Number & vbCrLf & _
                "エラー内容: " & Err.Description & vbCrLf & _
                "発生日時: " & Now
    
    ' ログに記録
    LogError Source, Err.Number, Err.Description
    
    ' ユーザー向けメッセージの生成
    Select Case Err.Number
        Case ERR_DATABASE_CONNECTION
            userMessage = "データベースに接続できません。" & vbCrLf & _
                         "ネットワーク接続を確認してください。"
        
        Case ERR_VALIDATION_FAILED
            userMessage = "入力内容に誤りがあります。" & vbCrLf & _
                         Err.Description
        
        Case ERR_FILE_NOT_FOUND
            userMessage = "指定されたファイルが見つかりません。"
        
        Case ERR_PERMISSION_DENIED
            userMessage = "この操作を実行する権限がありません。"
        
        Case -2147217843 ' SQL Server ログイン失敗
            userMessage = "データベースへのログインに失敗しました。"
        
        Case Else
            userMessage = "予期しないエラーが発生しました。" & vbCrLf & _
                         "エラー番号: " & Err.Number
    End Select
    
    ' ユーザーへの通知
    If ShowMessage Then
        MsgBox userMessage, vbCritical, "エラー"
    End If
    
    ' デバッグ情報の出力（開発時のみ）
    #If DEBUG_MODE Then
        Debug.Print errorInfo
    #End If
    
    HandleError = False
End Function

'**********************************************************************
' 関数名: LogError
' 説明: エラーログの記録
'**********************************************************************
Public Sub LogError(Source As String, ErrorNumber As Long, Description As String)
    Dim fso As Object
    Dim ts As Object
    Dim logPath As String
    Dim logEntry As String
    
    On Error Resume Next
    
    ' FileSystemObjectの作成
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' ログディレクトリの確認と作成
    logPath = App.Path & "\Logs"
    If Not fso.FolderExists(logPath) Then
        fso.CreateFolder logPath
    End If
    
    ' ログファイルパス
    logPath = logPath & "\Error_" & Format(Date, "yyyymmdd") & ".log"
    
    ' ログエントリの作成
    logEntry = Format(Now, "yyyy-mm-dd hh:nn:ss") & "|" & _
               App.EXEName & "|" & _
               Source & "|" & _
               ErrorNumber & "|" & _
               Replace(Description, vbCrLf, " ")
    
    ' ファイルへの書き込み
    Set ts = fso.OpenTextFile(logPath, 8, True) ' 8 = ForAppending
    ts.WriteLine logEntry
    ts.Close
    
    ' メモリ内ログにも保存（セッション中の参照用）
    If Not g_ErrorLog Is Nothing Then
        g_ErrorLog.Add logEntry
    End If
    
    ' オブジェクトの解放
    Set ts = Nothing
    Set fso = Nothing
End Sub

'**********************************************************************
' 関数名: RaiseCustomError
' 説明: カスタムエラーの発生
'**********************************************************************
Public Sub RaiseCustomError(ErrorCode As Long, Source As String, Description As String)
    Err.Raise ErrorCode, Source, Description
End Sub

'**********************************************************************
' 関数名: GetLastErrors
' 説明: 最近のエラーログを取得
'**********************************************************************
Public Function GetLastErrors(Count As Long) As String
    Dim i As Long
    Dim startIndex As Long
    Dim result As String
    
    If g_ErrorLog Is Nothing Then
        GetLastErrors = "エラーログが初期化されていません"
        Exit Function
    End If
    
    startIndex = IIf(g_ErrorLog.Count - Count + 1 > 1, g_ErrorLog.Count - Count + 1, 1)
    
    For i = startIndex To g_ErrorLog.Count
        result = result & g_ErrorLog(i) & vbCrLf
    Next i
    
    GetLastErrors = result
End Function

'**********************************************************************
' 関数名: ClearErrorLog
' 説明: メモリ内エラーログのクリア
'**********************************************************************
Public Sub ClearErrorLog()
    Set g_ErrorLog = New Collection
End Sub

'**********************************************************************
' サンプル使用例
'**********************************************************************
Public Sub SampleErrorHandling()
    On Error GoTo ErrorHandler
    
    ' 通常の処理
    Dim conn As Object
    Set conn = CreateObject("ADODB.Connection")
    
    ' エラーが発生する可能性のある処理
    conn.Open "Invalid Connection String"
    
    ' 正常終了
    Exit Sub
    
ErrorHandler:
    ' エラーハンドリング
    HandleError "SampleErrorHandling"
    
    ' 必要に応じてクリーンアップ
    If Not conn Is Nothing Then
        If conn.State = 1 Then conn.Close
        Set conn = Nothing
    End If
End Sub

'**********************************************************************
' 関数名: AdvancedErrorHandling
' 説明: 高度なエラーハンドリングパターン
'**********************************************************************
Public Function AdvancedErrorHandling() As Boolean
    On Error GoTo ErrorHandler
    
    Dim isTransactionActive As Boolean
    Dim conn As Object
    Dim cmd As Object
    
    ' 初期化
    AdvancedErrorHandling = False
    isTransactionActive = False
    
    ' データベース接続
    Set conn = CreateObject("ADODB.Connection")
    conn.Open GetConnectionString()
    
    ' トランザクション開始
    conn.BeginTrans
    isTransactionActive = True
    
    ' 複数の処理を実行
    Set cmd = CreateObject("ADODB.Command")
    cmd.ActiveConnection = conn
    
    ' 処理1
    cmd.CommandText = "INSERT INTO Table1 ..."
    cmd.Execute
    
    ' 処理2（エラーが発生する可能性）
    cmd.CommandText = "UPDATE Table2 ..."
    cmd.Execute
    
    ' すべて成功したらコミット
    conn.CommitTrans
    isTransactionActive = False
    
    AdvancedErrorHandling = True
    
CleanUp:
    ' リソースの解放
    On Error Resume Next
    
    If Not cmd Is Nothing Then Set cmd = Nothing
    
    If Not conn Is Nothing Then
        If isTransactionActive Then conn.RollbackTrans
        If conn.State = 1 Then conn.Close
        Set conn = Nothing
    End If
    
    Exit Function
    
ErrorHandler:
    ' エラー処理
    Select Case Err.Number
        Case -2147217873 ' 主キー違反
            LogError "AdvancedErrorHandling", Err.Number, "重複データエラー: " & Err.Description
            MsgBox "このデータは既に登録されています。", vbExclamation
        
        Case Else
            HandleError "AdvancedErrorHandling"
    End Select
    
    ' クリーンアップへ
    Resume CleanUp
End Function

'**********************************************************************
' 関数名: GetConnectionString
' 説明: 接続文字列の取得（サンプル）
'**********************************************************************
Private Function GetConnectionString() As String
    GetConnectionString = "Provider=SQLOLEDB;Data Source=localhost;" & _
                         "Initial Catalog=TestDB;Integrated Security=SSPI;"
End Function