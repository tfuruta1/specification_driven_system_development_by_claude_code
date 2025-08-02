# VB6 エンタープライズアーキテクチャガイド

## 🏗️ アーキテクチャ概要

VB6エンタープライズアプリケーションのための包括的アーキテクチャガイドです。レガシーシステムとの統合、スケーラビリティ、保守性を重視した設計パターンを提供します。

## 📐 アーキテクチャパターン

### 1. 3層アーキテクチャ (推奨)

```
┌─────────────────────────────────────────────────────┐
│                  プレゼンテーション層                    │
│  ├─ フォーム (.frm)                                   │
│  ├─ ユーザーコントロール (.ctl)                        │
│  └─ ActiveXコントロール (.ocx)                        │
├─────────────────────────────────────────────────────┤
│                    ビジネスロジック層                    │
│  ├─ ビジネスオブジェクト (.cls)                        │
│  ├─ ビジネスルール                                    │
│  └─ トランザクション管理                              │
├─────────────────────────────────────────────────────┤
│                    データアクセス層                      │
│  ├─ DAOパターン実装                                   │
│  ├─ ADO/DAO/RDO接続管理                              │
│  └─ ストアドプロシージャ呼び出し                       │
└─────────────────────────────────────────────────────┘
```

### 2. MVP (Model-View-Presenter) パターン

```vb
' IView インターフェース
Public Interface ICustomerView
    Property CustomerName As String
    Property CustomerID As Long
    Sub ShowMessage(ByVal message As String)
    Sub ShowCustomerList(ByVal customers As Collection)
End Interface

' Presenter クラス
Public Class CustomerPresenter
    Private m_View As ICustomerView
    Private m_Model As CustomerModel
    
    Public Sub New(ByVal view As ICustomerView)
        Set m_View = view
        Set m_Model = New CustomerModel
    End Sub
    
    Public Sub LoadCustomer(ByVal customerID As Long)
        On Error GoTo ErrorHandler
        
        Dim customer As Customer
        Set customer = m_Model.GetCustomer(customerID)
        
        m_View.CustomerName = customer.Name
        m_View.CustomerID = customer.ID
        
        Exit Sub
ErrorHandler:
        m_View.ShowMessage "エラー: " & Err.Description
    End Sub
End Class
```

### 3. サービス指向アーキテクチャ (SOA)

```vb
' サービスインターフェース
Public Interface IOrderService
    Function CreateOrder(ByVal orderData As OrderDTO) As Long
    Function GetOrder(ByVal orderID As Long) As OrderDTO
    Function UpdateOrder(ByVal orderData As OrderDTO) As Boolean
    Function DeleteOrder(ByVal orderID As Long) As Boolean
End Interface

' サービス実装
Public Class OrderService
    Implements IOrderService
    
    Private m_OrderDAO As OrderDAO
    Private m_Logger As ILogger
    
    Private Function IOrderService_CreateOrder(ByVal orderData As OrderDTO) As Long
        On Error GoTo ErrorHandler
        
        ' トランザクション開始
        BeginTransaction
        
        ' ビジネスルール検証
        ValidateOrder orderData
        
        ' データ永続化
        Dim orderID As Long
        orderID = m_OrderDAO.Insert(orderData)
        
        ' 監査ログ
        m_Logger.LogInfo "Order created: " & orderID
        
        ' トランザクションコミット
        CommitTransaction
        
        IOrderService_CreateOrder = orderID
        Exit Function
        
ErrorHandler:
        RollbackTransaction
        m_Logger.LogError "CreateOrder failed: " & Err.Description
        Err.Raise Err.Number, Err.Source, Err.Description
    End Function
End Class
```

## 🔧 設計原則

### SOLID原則の適用

#### 1. 単一責任の原則 (SRP)
```vb
' 悪い例 - 複数の責任
Public Class Customer
    Public Sub Save()
        ' データベース保存ロジック
    End Sub
    
    Public Sub SendEmail()
        ' メール送信ロジック
    End Sub
    
    Public Sub CalculateDiscount()
        ' 割引計算ロジック
    End Sub
End Class

' 良い例 - 責任の分離
Public Class Customer
    ' 顧客エンティティのみ
End Class

Public Class CustomerRepository
    Public Sub Save(ByVal customer As Customer)
        ' データベース保存ロジック
    End Sub
End Class

Public Class EmailService
    Public Sub SendCustomerEmail(ByVal customer As Customer)
        ' メール送信ロジック
    End Sub
End Class

Public Class DiscountCalculator
    Public Function Calculate(ByVal customer As Customer) As Double
        ' 割引計算ロジック
    End Function
End Class
```

#### 2. 開放閉鎖の原則 (OCP)
```vb
' 拡張可能な設計
Public Interface IPaymentProcessor
    Function ProcessPayment(ByVal amount As Currency) As Boolean
End Interface

Public Class CreditCardProcessor
    Implements IPaymentProcessor
    
    Private Function IPaymentProcessor_ProcessPayment(ByVal amount As Currency) As Boolean
        ' クレジットカード処理
    End Function
End Class

Public Class PayPalProcessor
    Implements IPaymentProcessor
    
    Private Function IPaymentProcessor_ProcessPayment(ByVal amount As Currency) As Boolean
        ' PayPal処理
    End Function
End Class
```

## 🏛️ エンタープライズパターン

### 1. Repository パターン
```vb
Public Interface IRepository(Of T)
    Function GetById(ByVal id As Long) As T
    Function GetAll() As Collection
    Function Add(ByVal entity As T) As Long
    Function Update(ByVal entity As T) As Boolean
    Function Delete(ByVal id As Long) As Boolean
End Interface

Public Class CustomerRepository
    Implements IRepository(Of Customer)
    
    Private m_Connection As ADODB.Connection
    
    Public Function GetById(ByVal id As Long) As Customer
        Dim sql As String
        sql = "SELECT * FROM Customers WHERE CustomerID = ?"
        
        Dim cmd As New ADODB.Command
        Set cmd.ActiveConnection = m_Connection
        cmd.CommandText = sql
        cmd.Parameters.Append cmd.CreateParameter("id", adInteger, adParamInput, , id)
        
        Dim rs As ADODB.Recordset
        Set rs = cmd.Execute
        
        If Not rs.EOF Then
            Set GetById = MapToCustomer(rs)
        End If
        
        rs.Close
    End Function
End Class
```

### 2. Unit of Work パターン
```vb
Public Class UnitOfWork
    Private m_Connection As ADODB.Connection
    Private m_Transaction As Boolean
    Private m_Repositories As Collection
    
    Public Sub BeginTransaction()
        m_Connection.BeginTrans
        m_Transaction = True
    End Sub
    
    Public Sub Commit()
        If m_Transaction Then
            m_Connection.CommitTrans
            m_Transaction = False
        End If
    End Sub
    
    Public Sub Rollback()
        If m_Transaction Then
            m_Connection.RollbackTrans
            m_Transaction = False
        End If
    End Sub
    
    Public Property Get CustomerRepository() As CustomerRepository
        ' 遅延初期化
        If m_CustomerRepository Is Nothing Then
            Set m_CustomerRepository = New CustomerRepository
            Set m_CustomerRepository.Connection = m_Connection
        End If
        Set CustomerRepository = m_CustomerRepository
    End Property
End Class
```

### 3. Factory パターン
```vb
Public Class DocumentFactory
    Public Function CreateDocument(ByVal docType As DocumentType) As IDocument
        Select Case docType
            Case dtInvoice
                Set CreateDocument = New InvoiceDocument
            Case dtPurchaseOrder
                Set CreateDocument = New PurchaseOrderDocument
            Case dtQuotation
                Set CreateDocument = New QuotationDocument
            Case Else
                Err.Raise vbObjectError + 1000, "DocumentFactory", "Unknown document type"
        End Select
    End Function
End Class
```

## 🔐 セキュリティアーキテクチャ

### 認証・認可
```vb
Public Class SecurityManager
    Private m_CurrentUser As User
    
    Public Function Authenticate(ByVal username As String, ByVal password As String) As Boolean
        On Error GoTo ErrorHandler
        
        ' パスワードハッシュ化
        Dim hashedPassword As String
        hashedPassword = HashPassword(password)
        
        ' データベース照合
        Dim user As User
        Set user = m_UserRepository.GetByCredentials(username, hashedPassword)
        
        If Not user Is Nothing Then
            Set m_CurrentUser = user
            
            ' 監査ログ
            LogSecurityEvent "LOGIN_SUCCESS", username
            
            Authenticate = True
        Else
            LogSecurityEvent "LOGIN_FAILED", username
            Authenticate = False
        End If
        
        Exit Function
ErrorHandler:
        LogSecurityEvent "LOGIN_ERROR", username & " - " & Err.Description
        Authenticate = False
    End Function
    
    Public Function HasPermission(ByVal resource As String, ByVal action As String) As Boolean
        If m_CurrentUser Is Nothing Then
            HasPermission = False
            Exit Function
        End If
        
        ' 権限チェック
        HasPermission = m_PermissionService.CheckPermission(m_CurrentUser, resource, action)
    End Function
End Class
```

## 📊 パフォーマンス最適化

### 1. 接続プーリング
```vb
Public Class ConnectionPool
    Private m_Connections As Collection
    Private m_MaxConnections As Integer
    
    Public Function GetConnection() As ADODB.Connection
        Dim conn As ADODB.Connection
        
        ' 利用可能な接続を探す
        For Each conn In m_Connections
            If conn.State = adStateClosed Then
                conn.Open
                Set GetConnection = conn
                Exit Function
            End If
        Next
        
        ' 新規接続作成
        If m_Connections.Count < m_MaxConnections Then
            Set conn = CreateNewConnection()
            m_Connections.Add conn
            Set GetConnection = conn
        Else
            Err.Raise vbObjectError + 2000, "ConnectionPool", "Maximum connections reached"
        End If
    End Function
    
    Public Sub ReturnConnection(ByVal conn As ADODB.Connection)
        ' 接続をプールに返す（閉じない）
        conn.Close
    End Sub
End Class
```

### 2. 遅延読み込み
```vb
Public Class Order
    Private m_OrderID As Long
    Private m_OrderDetails As Collection
    Private m_DetailsLoaded As Boolean
    
    Public Property Get OrderDetails() As Collection
        ' 必要時のみ詳細を読み込む
        If Not m_DetailsLoaded Then
            LoadOrderDetails
            m_DetailsLoaded = True
        End If
        Set OrderDetails = m_OrderDetails
    End Property
    
    Private Sub LoadOrderDetails()
        Set m_OrderDetails = m_OrderDetailRepository.GetByOrderID(m_OrderID)
    End Sub
End Class
```

## 🔄 非同期処理パターン

### コールバックパターン
```vb
Public Interface IAsyncCallback
    Sub OnComplete(ByVal result As Variant)
    Sub OnError(ByVal errorInfo As String)
End Interface

Public Class AsyncDataLoader
    Public Sub LoadDataAsync(ByVal query As String, ByVal callback As IAsyncCallback)
        ' タイマーを使用した非同期実行
        Dim asyncTimer As Timer
        Set asyncTimer = New Timer
        
        With asyncTimer
            .Interval = 1
            .Tag = query & "|" & ObjPtr(callback)
            .Enabled = True
        End With
    End Sub
    
    Private Sub Timer_Timer()
        On Error GoTo ErrorHandler
        
        ' 非同期処理実行
        Dim result As ADODB.Recordset
        Set result = ExecuteQuery(ParseQuery(Timer.Tag))
        
        ' コールバック呼び出し
        Dim callback As IAsyncCallback
        Set callback = GetCallbackFromTag(Timer.Tag)
        callback.OnComplete result
        
        Timer.Enabled = False
        Exit Sub
        
ErrorHandler:
        callback.OnError Err.Description
        Timer.Enabled = False
    End Sub
End Class
```

## 📋 アーキテクチャチェックリスト

### 設計時
- [ ] レイヤー分離が明確か
- [ ] インターフェースベースの設計か
- [ ] 依存関係が適切か
- [ ] エラーハンドリングが統一されているか
- [ ] トランザクション境界が明確か

### 実装時
- [ ] 命名規則に従っているか
- [ ] コメントが適切か
- [ ] エラーハンドリングが実装されているか
- [ ] リソース管理が適切か
- [ ] パフォーマンスを考慮しているか

### レビュー時
- [ ] SOLID原則に従っているか
- [ ] セキュリティ要件を満たしているか
- [ ] テスタビリティが高いか
- [ ] 保守性が高いか
- [ ] ドキュメントが整備されているか

## 🚀 次のステップ

1. `/vb6-analyze-code` - 既存コードの分析
2. `/vb6-refactor-to-patterns` - パターン適用リファクタリング
3. `/vb6-create-project` - 新規プロジェクト作成
4. `/vb6-migration-assessment` - 移行評価

---

詳細な実装例は、各パターンのサンプルコードを参照してください。