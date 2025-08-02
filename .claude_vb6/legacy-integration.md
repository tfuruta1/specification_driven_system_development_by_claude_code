# VB6 レガシーシステム統合ガイド

## 🔗 概要

VB6アプリケーションと既存レガシーシステムとの統合パターン、ベストプラクティス、実装例を提供します。メインフレーム、AS/400、UNIX系システム、既存データベースとの連携を網羅します。

## 🏛️ レガシーシステム統合パターン

### 1. データベース統合

#### SQL Server 6.5/7.0/2000 統合
```vb
' レガシーSQL Server接続
Public Class LegacySQLConnection
    Private m_Connection As ADODB.Connection
    
    Public Function Connect(ByVal server As String, ByVal database As String) As Boolean
        On Error GoTo ErrorHandler
        
        Set m_Connection = New ADODB.Connection
        
        ' SQL Server 2000以前対応接続文字列
        m_Connection.ConnectionString = "Provider=SQLOLEDB;" & _
                                      "Data Source=" & server & ";" & _
                                      "Initial Catalog=" & database & ";" & _
                                      "Integrated Security=SSPI;" & _
                                      "Network Library=dbnmpntw"  ' 名前付きパイプ
        
        m_Connection.CursorLocation = adUseClient
        m_Connection.Open
        
        Connect = True
        Exit Function
        
ErrorHandler:
        LogError "LegacySQLConnection", Err.Number, Err.Description
        Connect = False
    End Function
End Class
```

#### Oracle 8i/9i/10g 統合
```vb
' Oracle接続とストアドプロシージャ呼び出し
Public Class OracleIntegration
    Private m_Connection As ADODB.Connection
    
    Public Function ExecuteOracleProc(ByVal procName As String, _
                                    ByVal params As Collection) As ADODB.Recordset
        On Error GoTo ErrorHandler
        
        Dim cmd As New ADODB.Command
        Set cmd.ActiveConnection = m_Connection
        cmd.CommandType = adCmdStoredProc
        cmd.CommandText = procName
        
        ' Oracleパラメータ設定
        Dim param As Variant
        For Each param In params
            cmd.Parameters.Append cmd.CreateParameter( _
                param.Name, _
                param.Type, _
                param.Direction, _
                param.Size, _
                param.Value)
        Next
        
        ' REF CURSORの処理
        cmd.Parameters.Append cmd.CreateParameter( _
            "p_cursor", adVariant, adParamOutput)
        
        Set ExecuteOracleProc = cmd.Execute
        
        Exit Function
ErrorHandler:
        LogError "OracleIntegration", Err.Number, Err.Description
        Set ExecuteOracleProc = Nothing
    End Function
End Class
```

#### DB2/AS400 統合
```vb
' IBM DB2/AS400接続
Public Class AS400Connection
    Private m_Connection As ADODB.Connection
    
    Public Function ConnectToAS400(ByVal systemName As String) As Boolean
        On Error GoTo ErrorHandler
        
        ' IBM Client Access ODBC Driver使用
        m_Connection.ConnectionString = "Provider=IBMDA400;" & _
                                      "Data Source=" & systemName & ";" & _
                                      "User Id=" & GetAS400User() & ";" & _
                                      "Password=" & GetAS400Password() & ";" & _
                                      "Default Collection=QGPL;" & _
                                      "SSL=1"
        
        m_Connection.Open
        ConnectToAS400 = True
        
        Exit Function
ErrorHandler:
        ConnectToAS400 = False
    End Function
    
    Public Function CallRPGProgram(ByVal programName As String, _
                                 ByVal library As String, _
                                 ByVal params() As Variant) As Boolean
        ' RPGプログラム呼び出し
        Dim cmd As New ADODB.Command
        cmd.CommandText = "CALL " & library & "." & programName & "(?)"
        cmd.CommandType = adCmdText
        
        ' パラメータ設定
        Dim i As Integer
        For i = 0 To UBound(params)
            cmd.Parameters.Append cmd.CreateParameter( _
                "P" & i, adVarChar, adParamInputOutput, 50, params(i))
        Next
        
        cmd.Execute
        CallRPGProgram = True
    End Function
End Class
```

### 2. メインフレーム統合

#### CICS トランザクション統合
```vb
' IBM CICS Gateway統合
Public Class CICSGateway
    Private m_Gateway As Object  ' IBM CICS Transaction Gateway COM
    
    Public Function ExecuteCICSTransaction(ByVal transID As String, _
                                         ByVal commarea As String) As String
        On Error GoTo ErrorHandler
        
        ' CICSゲートウェイ初期化
        Set m_Gateway = CreateObject("CICSTG.Gateway")
        
        With m_Gateway
            .ServerName = GetCICSServer()
            .Port = 2006
            .UserID = GetCICSUser()
            .Password = GetCICSPassword()
            
            ' ECI (External Call Interface) 呼び出し
            .TransactionID = transID
            .Commarea = commarea
            .CommareaLength = Len(commarea)
            
            .Execute
            
            ExecuteCICSTransaction = .Commarea
        End With
        
        Exit Function
ErrorHandler:
        LogError "CICSGateway", Err.Number, Err.Description
        ExecuteCICSTransaction = ""
    End Function
End Class
```

#### 3270 エミュレーション統合
```vb
' 3270画面スクレイピング
Public Class MainframeScreen
    Private m_Session As Object  ' EHLLAPI or HLLAPI session
    
    Public Function ReadScreen(ByVal row As Integer, _
                             ByVal col As Integer, _
                             ByVal length As Integer) As String
        On Error GoTo ErrorHandler
        
        Dim screenData As String * 1920  ' 24x80 screen
        
        ' EHLLAPI関数呼び出し
        Call CopyPresentationSpace(screenData)
        
        ' 指定位置からデータ抽出
        Dim position As Integer
        position = (row - 1) * 80 + col
        
        ReadScreen = Mid$(screenData, position, length)
        ReadScreen = Trim$(ReadScreen)
        
        Exit Function
ErrorHandler:
        ReadScreen = ""
    End Function
    
    Public Function SendKeys(ByVal keys As String) As Boolean
        ' メインフレームへのキー送信
        Call SendString(keys)
        Call SendAID("@E")  ' Enter key
        
        ' 応答待機
        WaitForReady
        SendKeys = True
    End Function
End Class
```

### 3. ファイルシステム統合

#### FTP/SFTP統合
```vb
' レガシーシステムとのファイル転送
Public Class LegacyFileTransfer
    Private m_FTP As Object  ' WinSCP COM or similar
    
    Public Function TransferFromMainframe(ByVal dataset As String, _
                                        ByVal localFile As String) As Boolean
        On Error GoTo ErrorHandler
        
        ' WinSCP COM使用例
        Set m_FTP = CreateObject("WinSCP.Session")
        
        ' セッション設定
        Dim sessionOptions As Object
        Set sessionOptions = CreateObject("WinSCP.SessionOptions")
        
        With sessionOptions
            .Protocol = 2  ' SFTP
            .HostName = GetMainframeHost()
            .UserName = GetMainframeUser()
            .Password = GetMainframePassword()
            .SshHostKeyFingerprint = GetHostKey()
        End With
        
        m_FTP.Open sessionOptions
        
        ' データセット転送（EBCDIC → ASCII変換含む）
        Dim transferOptions As Object
        Set transferOptions = CreateObject("WinSCP.TransferOptions")
        transferOptions.TransferMode = 1  ' ASCII mode for EBCDIC conversion
        
        m_FTP.GetFiles "//" & dataset, localFile, False, transferOptions
        
        TransferFromMainframe = True
        
        Exit Function
ErrorHandler:
        TransferFromMainframe = False
    End Function
End Class
```

#### EDI/フラットファイル処理
```vb
' EDIファイル（X12, EDIFACT）処理
Public Class EDIProcessor
    Public Function ParseEDI(ByVal ediFile As String) As Collection
        On Error GoTo ErrorHandler
        
        Dim segments As New Collection
        Dim fileNum As Integer
        fileNum = FreeFile
        
        Open ediFile For Input As #fileNum
        
        Dim line As String
        Do While Not EOF(fileNum)
            Line Input #fileNum, line
            
            ' セグメント解析
            If Left$(line, 3) = "ISA" Then
                ' Interchange Control Header
                ParseISASegment line, segments
            ElseIf Left$(line, 2) = "GS" Then
                ' Functional Group Header
                ParseGSSegment line, segments
            ElseIf Left$(line, 2) = "ST" Then
                ' Transaction Set Header
                ParseSTSegment line, segments
            End If
        Loop
        
        Close #fileNum
        Set ParseEDI = segments
        
        Exit Function
ErrorHandler:
        If fileNum > 0 Then Close #fileNum
        Set ParseEDI = Nothing
    End Function
End Class
```

### 4. メッセージング統合

#### IBM MQ (WebSphere MQ) 統合
```vb
' IBM MQとの統合
Public Class MQIntegration
    Private m_QueueManager As Object  ' MQQueueManager
    Private m_Queue As Object         ' MQQueue
    
    Public Function SendToMQ(ByVal queueName As String, _
                           ByVal message As String) As Boolean
        On Error GoTo ErrorHandler
        
        ' MQ COM オブジェクト作成
        Set m_QueueManager = CreateObject("MQAX200.MQQueueManager")
        m_QueueManager.Connect GetMQManager()
        
        ' キューオープン
        Set m_Queue = m_QueueManager.AccessQueue( _
            queueName, _
            MQOO_OUTPUT Or MQOO_FAIL_IF_QUIESCING)
        
        ' メッセージ送信
        Dim mqMessage As Object
        Set mqMessage = CreateObject("MQAX200.MQMessage")
        mqMessage.WriteString message
        mqMessage.Format = "MQSTR"
        
        Dim putOptions As Object
        Set putOptions = CreateObject("MQAX200.MQPutMessageOptions")
        
        m_Queue.Put mqMessage, putOptions
        
        SendToMQ = True
        
        Exit Function
ErrorHandler:
        SendToMQ = False
    End Function
End Class
```

### 5. Web サービス統合

#### SOAP Web サービス
```vb
' レガシーSOAPサービス呼び出し
Public Class SOAPClient
    Private m_XMLHTTP As Object
    
    Public Function CallSOAPService(ByVal endpoint As String, _
                                  ByVal soapAction As String, _
                                  ByVal soapBody As String) As String
        On Error GoTo ErrorHandler
        
        Set m_XMLHTTP = CreateObject("MSXML2.XMLHTTP")
        
        ' SOAP エンベロープ作成
        Dim soapEnvelope As String
        soapEnvelope = "<?xml version='1.0' encoding='utf-8'?>" & _
                      "<soap:Envelope " & _
                      "xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'>" & _
                      "<soap:Body>" & soapBody & "</soap:Body>" & _
                      "</soap:Envelope>"
        
        ' HTTP POST
        m_XMLHTTP.Open "POST", endpoint, False
        m_XMLHTTP.setRequestHeader "Content-Type", "text/xml; charset=utf-8"
        m_XMLHTTP.setRequestHeader "SOAPAction", soapAction
        m_XMLHTTP.send soapEnvelope
        
        ' レスポンス処理
        If m_XMLHTTP.Status = 200 Then
            CallSOAPService = m_XMLHTTP.responseText
        Else
            Err.Raise vbObjectError + 3000, "SOAPClient", _
                     "SOAP Error: " & m_XMLHTTP.Status
        End If
        
        Exit Function
ErrorHandler:
        CallSOAPService = ""
    End Function
End Class
```

### 6. 認証システム統合

#### Active Directory 統合
```vb
' Active Directory認証
Public Class ADAuthentication
    Public Function AuthenticateUser(ByVal username As String, _
                                   ByVal password As String, _
                                   ByVal domain As String) As Boolean
        On Error GoTo ErrorHandler
        
        ' LDAP接続
        Dim ldapPath As String
        ldapPath = "LDAP://" & domain
        
        Dim ldapObject As Object
        Set ldapObject = GetObject("LDAP:")
        
        ' 認証試行
        Dim userDN As String
        userDN = "CN=" & username & ",CN=Users,DC=" & _
                Replace(domain, ".", ",DC=")
        
        Dim authObject As Object
        Set authObject = ldapObject.OpenDSObject(ldapPath, _
                                                userDN, _
                                                password, _
                                                ADS_SECURE_AUTHENTICATION)
        
        AuthenticateUser = Not (authObject Is Nothing)
        
        Exit Function
ErrorHandler:
        AuthenticateUser = False
    End Function
    
    Public Function GetUserGroups(ByVal username As String) As Collection
        ' ユーザーのADグループ取得
        Dim groups As New Collection
        
        Dim user As Object
        Set user = GetObject("WinNT://" & GetDomain() & "/" & username)
        
        Dim group As Object
        For Each group In user.Groups
            groups.Add group.Name
        Next
        
        Set GetUserGroups = groups
    End Function
End Class
```

### 7. レガシーCOM統合

#### 既存COM/DCOM呼び出し
```vb
' レガシーCOMコンポーネント統合
Public Class LegacyCOMWrapper
    Private m_COMObject As Object
    
    Public Function InitializeCOM(ByVal progID As String, _
                                Optional ByVal serverName As String = "") As Boolean
        On Error GoTo ErrorHandler
        
        If Len(serverName) > 0 Then
            ' リモートDCOM
            Set m_COMObject = CreateObject(progID, serverName)
        Else
            ' ローカルCOM
            Set m_COMObject = CreateObject(progID)
        End If
        
        InitializeCOM = True
        
        Exit Function
ErrorHandler:
        ' COM登録確認
        If Err.Number = 429 Then
            MsgBox "COMコンポーネント '" & progID & "' が登録されていません。", _
                   vbCritical, "COM Error"
        End If
        InitializeCOM = False
    End Function
    
    Public Function CallMethod(ByVal methodName As String, _
                             ParamArray params() As Variant) As Variant
        On Error GoTo ErrorHandler
        
        ' 遅延バインディングでメソッド呼び出し
        Select Case UBound(params)
            Case -1
                CallMethod = CallByName(m_COMObject, methodName, VbMethod)
            Case 0
                CallMethod = CallByName(m_COMObject, methodName, VbMethod, params(0))
            Case 1
                CallMethod = CallByName(m_COMObject, methodName, VbMethod, _
                                      params(0), params(1))
            ' 必要に応じて追加
        End Select
        
        Exit Function
ErrorHandler:
        Err.Raise Err.Number, "LegacyCOMWrapper", Err.Description
    End Function
End Class
```

## 🔧 統合ベストプラクティス

### エラーハンドリング
```vb
' 統合エラーハンドリング
Public Class IntegrationErrorHandler
    Private m_ErrorLog As ErrorLogger
    
    Public Sub HandleIntegrationError(ByVal source As String, _
                                    ByVal errorCode As Long, _
                                    ByVal description As String)
        ' エラー分類
        Select Case errorCode
            Case -2147467259  ' 0x80004005 - 一般的なCOMエラー
                HandleCOMError source, description
            Case -2147217843  ' 0x800A0E4D - ADOエラー
                HandleDatabaseError source, description
            Case -2146825287  ' 0x800C0009 - WinHTTPエラー
                HandleNetworkError source, description
            Case Else
                HandleGenericError source, errorCode, description
        End Select
        
        ' 統合システムへの通知
        NotifyIntegrationFailure source, errorCode, description
    End Sub
    
    Private Sub HandleDatabaseError(ByVal source As String, _
                                  ByVal description As String)
        ' データベース固有のエラー処理
        If InStr(description, "timeout") > 0 Then
            ' タイムアウトの場合はリトライ
            m_ErrorLog.LogWarning source, "Database timeout - will retry"
        ElseIf InStr(description, "deadlock") > 0 Then
            ' デッドロックの場合は遅延後リトライ
            m_ErrorLog.LogWarning source, "Deadlock detected - delaying retry"
            Sleep 1000  ' 1秒待機
        Else
            m_ErrorLog.LogError source, description
        End If
    End Sub
End Class
```

### トランザクション管理
```vb
' 分散トランザクション管理
Public Class DistributedTransaction
    Private m_LocalDB As ADODB.Connection
    Private m_RemoteDB As ADODB.Connection
    Private m_MQSession As Object
    
    Public Function ExecuteDistributed() As Boolean
        On Error GoTo ErrorHandler
        
        ' ローカルトランザクション開始
        m_LocalDB.BeginTrans
        
        ' リモートトランザクション開始
        m_RemoteDB.BeginTrans
        
        ' 処理実行
        UpdateLocalData
        UpdateRemoteData
        SendMQMessage
        
        ' すべて成功したらコミット
        m_LocalDB.CommitTrans
        m_RemoteDB.CommitTrans
        
        ExecuteDistributed = True
        Exit Function
        
ErrorHandler:
        ' ロールバック
        If m_LocalDB.State = adStateOpen Then
            m_LocalDB.RollbackTrans
        End If
        If m_RemoteDB.State = adStateOpen Then
            m_RemoteDB.RollbackTrans
        End If
        
        ExecuteDistributed = False
    End Function
End Class
```

### パフォーマンス最適化
```vb
' バッチ処理最適化
Public Class BatchProcessor
    Private m_BatchSize As Long
    Private m_ProcessedCount As Long
    
    Public Sub ProcessLegacyData()
        Dim rs As ADODB.Recordset
        Set rs = GetLegacyData()
        
        ' バッチ処理
        Dim batch As New Collection
        Do While Not rs.EOF
            batch.Add rs.Fields("Data").Value
            
            If batch.Count >= m_BatchSize Then
                ProcessBatch batch
                Set batch = New Collection
                
                ' 進捗更新
                m_ProcessedCount = m_ProcessedCount + m_BatchSize
                RaiseEvent Progress(m_ProcessedCount)
                
                ' CPUを他のプロセスに譲る
                DoEvents
            End If
            
            rs.MoveNext
        Loop
        
        ' 残りを処理
        If batch.Count > 0 Then
            ProcessBatch batch
        End If
        
        rs.Close
    End Sub
End Class
```

## 📋 統合チェックリスト

### 事前準備
- [ ] レガシーシステムの仕様書確認
- [ ] 接続情報の取得（ホスト、ポート、認証）
- [ ] 必要なドライバ/クライアントのインストール
- [ ] ファイアウォール設定の確認
- [ ] テスト環境の準備

### 実装時
- [ ] エラーハンドリングの実装
- [ ] タイムアウト設定
- [ ] リトライロジック
- [ ] ログ出力
- [ ] トランザクション管理

### テスト
- [ ] 接続テスト
- [ ] データ整合性テスト
- [ ] パフォーマンステスト
- [ ] 障害テスト（ネットワーク断、タイムアウト）
- [ ] セキュリティテスト

### 運用
- [ ] 監視設定
- [ ] バックアップ/リカバリ手順
- [ ] 障害対応手順書
- [ ] パフォーマンスモニタリング
- [ ] 定期メンテナンス計画

## 🚀 次のステップ

1. `/vb6-check-dependencies` - 依存関係の確認
2. `/vb6-com-inventory` - COM/ActiveX調査
3. `/vb6-api-usage-scan` - Win32 API使用調査
4. `/vb6-migration-assessment` - 移行評価

---

詳細な実装例は、各統合パターンのサンプルコードを参照してください。