# 📚 VB6 開発ガイド - エンタープライズアプリケーション構築

**Visual Basic 6.0によるエンタープライズシステム開発の包括的ガイド**

## 📋 目次

1. [開発環境構築](#開発環境構築)
2. [プロジェクト構成](#プロジェクト構成)
3. [アーキテクチャ設計](#アーキテクチャ設計)
4. [データアクセス戦略](#データアクセス戦略)
5. [UIデザインパターン](#uiデザインパターン)
6. [エラーハンドリング](#エラーハンドリング)
7. [パフォーマンス最適化](#パフォーマンス最適化)
8. [セキュリティ実装](#セキュリティ実装)

## 🛠️ 開発環境構築

### IDE設定の最適化

```ini
; VB6 IDE最適設定
[Options]
RequireVariableDeclaration=True    ; Option Explicit自動挿入
TabWidth=4                         ; タブ幅
AutoIndent=True                    ; 自動インデント
ErrorTrapping=BreakOnUnhandledErrors ; エラー時の動作
CompileOnDemand=False              ; 完全コンパイル
BackgroundCompile=True             ; バックグラウンドコンパイル
```

### 推奨アドイン

1. **MZ-Tools 3.0**: コード解析、リファクタリング支援
2. **CodeSMART**: コード補完、ナビゲーション強化
3. **VB6 Code Advisor**: コード品質チェック
4. **API Viewer**: Windows API参照ツール

### プロジェクト参照設定

```vb
' 標準的な参照設定
' プロジェクト → 参照設定で以下を追加
- Microsoft ActiveX Data Objects 2.8 Library (ADO)
- Microsoft Scripting Runtime (FileSystemObject用)
- Microsoft XML, v6.0 (XML処理用)
- Microsoft Windows Common Controls 6.0 (SP6)
- Microsoft Windows Common Controls-2 6.0
```

## 📁 プロジェクト構成

### 標準的なプロジェクト構造

```
MyEnterpriseApp/
├── Main/                      # メインアプリケーション
│   ├── MyApp.vbp             # プロジェクトファイル
│   ├── Forms/                # フォーム
│   ├── Modules/              # 標準モジュール
│   ├── Classes/              # クラスモジュール
│   └── UserControls/         # ユーザーコントロール
├── Common/                   # 共通ライブラリ
│   ├── CommonLib.vbp         # 共通ライブラリプロジェクト
│   └── Utilities/            # ユーティリティクラス
├── DataAccess/              # データアクセスライブラリ
│   ├── DataAccess.vbp       # DATプロジェクト
│   └── DAO/                 # DAOクラス
├── BusinessLogic/           # ビジネスロジック
│   ├── BusinessLogic.vbp    # BLプロジェクト
│   └── Services/            # サービスクラス
└── Setup/                   # セットアップ
    └── Setup.vdp            # デプロイメントプロジェクト
```

### プロジェクトグループの活用

```ini
; MyEnterpriseApp.vbg (プロジェクトグループファイル)
VBGROUP 5.0
StartupProject=Main\MyApp.vbp
Project=Common\CommonLib.vbp
Project=DataAccess\DataAccess.vbp
Project=BusinessLogic\BusinessLogic.vbp
```

## 🏛️ アーキテクチャ設計

### 3層アーキテクチャの実装

#### プレゼンテーション層（Forms）
```vb
' frmCustomer.frm
Option Explicit

Private m_Presenter As clsCustomerPresenter

Private Sub Form_Load()
    ' Presenterの初期化
    Set m_Presenter = New clsCustomerPresenter
    m_Presenter.Initialize Me
    m_Presenter.LoadCustomers
End Sub

Private Sub cmdSave_Click()
    m_Presenter.SaveCustomer
End Sub

' ICustomerView インターフェースの実装
Implements ICustomerView

Private Property Let ICustomerView_CustomerName(ByVal Value As String)
    txtCustomerName.Text = Value
End Property

Private Property Get ICustomerView_CustomerName() As String
    ICustomerView_CustomerName = txtCustomerName.Text
End Property

Private Sub ICustomerView_DisplayCustomers(Customers As Collection)
    ' グリッドに表示
    Call PopulateGrid(Customers)
End Sub
```

#### ビジネスロジック層（Classes）
```vb
' clsCustomerService.cls
Option Explicit

Private m_DAO As clsCustomerDAO

Private Sub Class_Initialize()
    Set m_DAO = New clsCustomerDAO
End Sub

Public Function GetAllCustomers() As Collection
    Dim colCustomers As Collection
    Dim rsCustomers As ADODB.Recordset
    
    Set rsCustomers = m_DAO.GetAll()
    Set colCustomers = ConvertToCollection(rsCustomers)
    
    rsCustomers.Close
    Set rsCustomers = Nothing
    
    Set GetAllCustomers = colCustomers
End Function

Public Function SaveCustomer(Customer As clsCustomer) As Boolean
    On Error GoTo ErrorHandler
    
    ' ビジネスルールの検証
    If Not ValidateCustomer(Customer) Then
        Err.Raise vbObjectError + 1001, , "顧客情報が無効です"
    End If
    
    ' 保存処理
    If Customer.ID = 0 Then
        SaveCustomer = m_DAO.Insert(Customer)
    Else
        SaveCustomer = m_DAO.Update(Customer)
    End If
    
    Exit Function
    
ErrorHandler:
    LogError "SaveCustomer", Err.Number, Err.Description
    SaveCustomer = False
End Function
```

#### データアクセス層（Classes）
```vb
' clsCustomerDAO.cls
Option Explicit

Private m_Connection As ADODB.Connection

Private Sub Class_Initialize()
    Set m_Connection = GetConnection()
End Sub

Public Function GetAll() As ADODB.Recordset
    Dim cmd As ADODB.Command
    
    Set cmd = New ADODB.Command
    With cmd
        .ActiveConnection = m_Connection
        .CommandText = "sp_GetAllCustomers"
        .CommandType = adCmdStoredProc
        Set GetAll = .Execute
    End With
    
    Set cmd = Nothing
End Function

Public Function Insert(Customer As clsCustomer) As Boolean
    Dim cmd As ADODB.Command
    
    Set cmd = New ADODB.Command
    With cmd
        .ActiveConnection = m_Connection
        .CommandText = "sp_InsertCustomer"
        .CommandType = adCmdStoredProc
        
        ' パラメータ設定
        .Parameters.Append .CreateParameter("@Name", adVarChar, adParamInput, 100, Customer.Name)
        .Parameters.Append .CreateParameter("@Email", adVarChar, adParamInput, 100, Customer.Email)
        .Parameters.Append .CreateParameter("@Phone", adVarChar, adParamInput, 20, Customer.Phone)
        
        .Execute
    End With
    
    Insert = True
    Set cmd = Nothing
End Function
```

### デザインパターンの活用

#### Singletonパターン
```vb
' clsConfigManager.cls - 設定管理シングルトン
Option Explicit

Private m_Instance As clsConfigManager
Private m_Config As Dictionary

Public Function GetInstance() As clsConfigManager
    If m_Instance Is Nothing Then
        Set m_Instance = New clsConfigManager
    End If
    Set GetInstance = m_Instance
End Function

Private Sub Class_Initialize()
    Set m_Config = New Dictionary
    LoadConfiguration
End Sub

Private Sub LoadConfiguration()
    ' INIファイルから設定を読み込み
    m_Config.Add "ConnectionString", GetINIValue("Database", "ConnectionString")
    m_Config.Add "LogPath", GetINIValue("System", "LogPath")
    m_Config.Add "MaxRetries", GetINIValue("System", "MaxRetries")
End Sub

Public Property Get Value(Key As String) As Variant
    If m_Config.Exists(Key) Then
        Value = m_Config(Key)
    Else
        Value = Empty
    End If
End Property
```

#### Factoryパターン
```vb
' clsDAOFactory.cls - DAOファクトリ
Option Explicit

Public Enum DataSourceType
    dstSQLServer = 1
    dstOracle = 2
    dstAccess = 3
End Enum

Public Function CreateDAO(DAOType As String, DataSource As DataSourceType) As Object
    Select Case UCase(DAOType)
        Case "CUSTOMER"
            Select Case DataSource
                Case dstSQLServer
                    Set CreateDAO = New clsCustomerSQLServerDAO
                Case dstOracle
                    Set CreateDAO = New clsCustomerOracleDAO
                Case dstAccess
                    Set CreateDAO = New clsCustomerAccessDAO
            End Select
            
        Case "ORDER"
            Select Case DataSource
                Case dstSQLServer
                    Set CreateDAO = New clsOrderSQLServerDAO
                ' ... 他のデータソース
            End Select
    End Select
End Function
```

## 🗄️ データアクセス戦略

### 接続プーリングの実装
```vb
' modDatabase.bas - データベース接続管理
Option Explicit

Private m_ConnectionPool As Collection
Private Const MAX_POOL_SIZE As Integer = 10

Public Function GetConnection() As ADODB.Connection
    Dim conn As ADODB.Connection
    
    ' プールから利用可能な接続を取得
    Set conn = GetFromPool()
    
    If conn Is Nothing Then
        ' 新規接続を作成
        Set conn = CreateConnection()
    End If
    
    Set GetConnection = conn
End Function

Private Function CreateConnection() As ADODB.Connection
    Dim conn As ADODB.Connection
    
    Set conn = New ADODB.Connection
    conn.ConnectionString = GetConnectionString()
    conn.CursorLocation = adUseClient
    conn.Open
    
    Set CreateConnection = conn
End Function

Private Function GetFromPool() As ADODB.Connection
    Dim conn As ADODB.Connection
    Dim i As Integer
    
    If m_ConnectionPool Is Nothing Then
        Set m_ConnectionPool = New Collection
    End If
    
    ' 利用可能な接続を検索
    For i = m_ConnectionPool.Count To 1 Step -1
        Set conn = m_ConnectionPool(i)
        If conn.State = adStateOpen Then
            m_ConnectionPool.Remove i
            Set GetFromPool = conn
            Exit Function
        End If
    Next i
    
    Set GetFromPool = Nothing
End Function

Public Sub ReturnToPool(conn As ADODB.Connection)
    If m_ConnectionPool.Count < MAX_POOL_SIZE Then
        m_ConnectionPool.Add conn
    Else
        conn.Close
        Set conn = Nothing
    End If
End Sub
```

### トランザクション管理
```vb
' clsTransactionManager.cls
Option Explicit

Private m_Connection As ADODB.Connection
Private m_InTransaction As Boolean

Public Function BeginTransaction() As Boolean
    On Error GoTo ErrorHandler
    
    If Not m_InTransaction Then
        m_Connection.BeginTrans
        m_InTransaction = True
        BeginTransaction = True
    End If
    Exit Function
    
ErrorHandler:
    BeginTransaction = False
End Function

Public Function CommitTransaction() As Boolean
    On Error GoTo ErrorHandler
    
    If m_InTransaction Then
        m_Connection.CommitTrans
        m_InTransaction = False
        CommitTransaction = True
    End If
    Exit Function
    
ErrorHandler:
    CommitTransaction = False
End Function

Public Function RollbackTransaction() As Boolean
    On Error GoTo ErrorHandler
    
    If m_InTransaction Then
        m_Connection.RollbackTrans
        m_InTransaction = False
        RollbackTransaction = True
    End If
    Exit Function
    
ErrorHandler:
    RollbackTransaction = False
End Function
```

## 🎨 UIデザインパターン

### MDI（Multiple Document Interface）実装
```vb
' frmMDIMain.frm - MDI親フォーム
Option Explicit

Private Sub MDIForm_Load()
    ' メニューバー、ツールバー、ステータスバーの初期化
    InitializeUI
    
    ' 子フォームの管理
    LoadChildForms
End Sub

Private Sub mnuFileNew_Click()
    Dim frm As frmDocument
    Static DocumentCount As Integer
    
    DocumentCount = DocumentCount + 1
    Set frm = New frmDocument
    frm.Caption = "Document " & DocumentCount
    frm.Show
End Sub

Private Sub mnuWindowTileHorizontal_Click()
    Me.Arrange vbTileHorizontal
End Sub

Private Sub mnuWindowCascade_Click()
    Me.Arrange vbCascade
End Sub
```

### カスタムコントロールの作成
```vb
' ctlSearchBox.ctl - 検索ボックスコントロール
Option Explicit

' イベント定義
Public Event SearchClick(SearchText As String)
Public Event SearchTextChanged(SearchText As String)

' プロパティ
Private m_SearchText As String

Public Property Get SearchText() As String
    SearchText = m_SearchText
End Property

Public Property Let SearchText(ByVal Value As String)
    m_SearchText = Value
    txtSearch.Text = Value
    PropertyChanged "SearchText"
End Property

Private Sub cmdSearch_Click()
    RaiseEvent SearchClick(txtSearch.Text)
End Sub

Private Sub txtSearch_Change()
    m_SearchText = txtSearch.Text
    RaiseEvent SearchTextChanged(txtSearch.Text)
End Sub

Private Sub UserControl_Resize()
    ' コントロールのリサイズ処理
    txtSearch.Width = UserControl.Width - cmdSearch.Width - 60
    cmdSearch.Left = txtSearch.Width + 60
End Sub
```

## 🛡️ エラーハンドリング

### 標準エラーハンドリングテンプレート
```vb
' modErrorHandler.bas - エラーハンドリングモジュール
Option Explicit

Public Sub LogError(Source As String, Number As Long, Description As String)
    Dim fso As FileSystemObject
    Dim ts As TextStream
    Dim logPath As String
    
    On Error Resume Next
    
    Set fso = New FileSystemObject
    logPath = App.Path & "\Logs\Error_" & Format(Date, "yyyymmdd") & ".log"
    
    ' ログディレクトリの作成
    If Not fso.FolderExists(App.Path & "\Logs") Then
        fso.CreateFolder App.Path & "\Logs"
    End If
    
    ' エラーログの書き込み
    Set ts = fso.OpenTextFile(logPath, ForAppending, True)
    ts.WriteLine Now & "|" & Source & "|" & Number & "|" & Description
    ts.Close
    
    Set ts = Nothing
    Set fso = Nothing
End Sub

Public Function HandleError(Source As String, Optional ShowUser As Boolean = True) As Boolean
    Dim msg As String
    
    ' エラーログ記録
    LogError Source, Err.Number, Err.Description
    
    ' ユーザー通知
    If ShowUser Then
        Select Case Err.Number
            Case -2147217843
                msg = "データベース接続エラーが発生しました。"
            Case -2147217865
                msg = "指定されたレコードが見つかりません。"
            Case Else
                msg = "エラーが発生しました。" & vbCrLf & _
                      "エラー番号: " & Err.Number & vbCrLf & _
                      "詳細: " & Err.Description
        End Select
        
        MsgBox msg, vbCritical, "エラー"
    End If
    
    HandleError = False
End Function
```

## ⚡ パフォーマンス最適化

### データベースアクセスの最適化
```vb
' 効率的なレコードセット処理
Public Function GetCustomersOptimized() As Collection
    Dim rs As ADODB.Recordset
    Dim col As Collection
    Dim customer As clsCustomer
    
    Set col = New Collection
    Set rs = New ADODB.Recordset
    
    ' 切断されたレコードセットを使用
    With rs
        .CursorLocation = adUseClient
        .CursorType = adOpenStatic
        .LockType = adLockReadOnly
        .Open "SELECT ID, Name, Email FROM Customers", GetConnection()
        
        ' 接続を切断
        Set .ActiveConnection = Nothing
    End With
    
    ' GetRowsメソッドで高速読み込み
    If Not rs.EOF Then
        Dim varData As Variant
        varData = rs.GetRows()
        
        Dim i As Long
        For i = 0 To UBound(varData, 2)
            Set customer = New clsCustomer
            customer.ID = varData(0, i)
            customer.Name = varData(1, i)
            customer.Email = varData(2, i)
            col.Add customer
        Next i
    End If
    
    rs.Close
    Set rs = Nothing
    Set GetCustomersOptimized = col
End Function
```

### メモリ管理の最適化
```vb
' オブジェクトプールの実装
Private m_ObjectPool As Collection

Public Function GetCustomerObject() As clsCustomer
    Dim obj As clsCustomer
    
    If m_ObjectPool Is Nothing Then
        Set m_ObjectPool = New Collection
    End If
    
    If m_ObjectPool.Count > 0 Then
        ' プールから取得
        Set obj = m_ObjectPool(1)
        m_ObjectPool.Remove 1
        obj.Clear ' オブジェクトをクリア
    Else
        ' 新規作成
        Set obj = New clsCustomer
    End If
    
    Set GetCustomerObject = obj
End Function

Public Sub ReturnCustomerObject(obj As clsCustomer)
    If m_ObjectPool.Count < 100 Then ' プールサイズ制限
        m_ObjectPool.Add obj
    Else
        Set obj = Nothing
    End If
End Sub
```

## 🔒 セキュリティ実装

### パスワードハッシュ化
```vb
' modSecurity.bas - セキュリティモジュール
Option Explicit

Private Declare Function CryptAcquireContext Lib "advapi32.dll" _
    Alias "CryptAcquireContextA" (phProv As Long, _
    ByVal pszContainer As String, ByVal pszProvider As String, _
    ByVal dwProvType As Long, ByVal dwFlags As Long) As Long

Public Function HashPassword(Password As String) As String
    ' MD5ハッシュの実装（簡略版）
    Dim objMD5 As Object
    Dim bytHash() As Byte
    Dim i As Integer
    Dim strHash As String
    
    Set objMD5 = CreateObject("System.Security.Cryptography.MD5CryptoServiceProvider")
    bytHash = objMD5.ComputeHash_2(StrConv(Password, vbFromUnicode))
    
    For i = 0 To UBound(bytHash)
        strHash = strHash & Right("0" & Hex(bytHash(i)), 2)
    Next i
    
    HashPassword = strHash
    Set objMD5 = Nothing
End Function

Public Function ValidateInput(InputText As String, InputType As String) As Boolean
    Select Case InputType
        Case "Email"
            ValidateInput = IsValidEmail(InputText)
        Case "AlphaNumeric"
            ValidateInput = IsAlphaNumeric(InputText)
        Case "Number"
            ValidateInput = IsNumeric(InputText)
        Case Else
            ValidateInput = True
    End Select
End Function

Private Function IsValidEmail(Email As String) As Boolean
    Dim regEx As Object
    Set regEx = CreateObject("VBScript.RegExp")
    
    regEx.Pattern = "^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$"
    IsValidEmail = regEx.Test(Email)
    
    Set regEx = Nothing
End Function
```

### SQLインジェクション対策
```vb
' パラメータ化クエリの使用
Public Function GetCustomerByID(CustomerID As Long) As clsCustomer
    Dim cmd As ADODB.Command
    Dim rs As ADODB.Recordset
    
    Set cmd = New ADODB.Command
    With cmd
        .ActiveConnection = GetConnection()
        .CommandText = "SELECT * FROM Customers WHERE ID = ?"
        .CommandType = adCmdText
        
        ' パラメータの追加（SQLインジェクション対策）
        .Parameters.Append .CreateParameter("ID", adInteger, adParamInput, , CustomerID)
        
        Set rs = .Execute
    End With
    
    If Not rs.EOF Then
        Set GetCustomerByID = MapToCustomer(rs)
    End If
    
    rs.Close
    Set rs = Nothing
    Set cmd = Nothing
End Function
```

---

このガイドは、VB6によるエンタープライズアプリケーション開発の基礎から応用まで、実践的な内容を網羅しています。