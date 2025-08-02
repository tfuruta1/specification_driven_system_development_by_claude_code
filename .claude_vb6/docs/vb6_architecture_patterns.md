# 🏛️ VB6 アーキテクチャパターンガイド

**Visual Basic 6.0におけるエンタープライズアーキテクチャパターンの実装**

## 📋 目次

1. [アーキテクチャ概要](#アーキテクチャ概要)
2. [レイヤードアーキテクチャ](#レイヤードアーキテクチャ)
3. [MVPパターン](#mvpパターン)
4. [サービス指向アーキテクチャ](#サービス指向アーキテクチャ)
5. [イベント駆動アーキテクチャ](#イベント駆動アーキテクチャ)
6. [マイクロサービス風アーキテクチャ](#マイクロサービス風アーキテクチャ)
7. [エンタープライズ統合パターン](#エンタープライズ統合パターン)

## 🎯 アーキテクチャ概要

### VB6におけるアーキテクチャの制約と対策

```vb
' VB6の制約
' - 真の継承がない（インターフェース継承のみ）
' - ジェネリクスがない
' - ネイティブなマルチスレッドサポートがない
' - 限定的なコレクションサポート

' 対策
' - インターフェースベースの設計
' - ファクトリーパターンの活用
' - COMスレッドモデルの理解と活用
' - カスタムコレクションクラスの実装
```

## 🏗️ レイヤードアーキテクチャ

### 5層アーキテクチャの実装

```
┌─────────────────────────────────────┐
│    プレゼンテーション層（Forms）      │
├─────────────────────────────────────┤
│    アプリケーション層（Controllers）   │
├─────────────────────────────────────┤
│    ビジネスロジック層（Services）     │
├─────────────────────────────────────┤
│    データアクセス層（DAO）            │
├─────────────────────────────────────┤
│    インフラストラクチャ層（Utilities） │
└─────────────────────────────────────┘
```

### 各層の実装例

#### インフラストラクチャ層
```vb
' ILogger.cls - ロギングインターフェース
Option Explicit

Public Sub LogInfo(Message As String)
End Sub

Public Sub LogError(Source As String, ErrorNumber As Long, Description As String)
End Sub

Public Sub LogDebug(Message As String)
End Sub

' FileLogger.cls - ファイルロガー実装
Option Explicit
Implements ILogger

Private m_LogPath As String

Private Sub Class_Initialize()
    m_LogPath = App.Path & "\Logs\"
    CreateLogDirectory
End Sub

Private Sub ILogger_LogInfo(Message As String)
    WriteLog "INFO", Message
End Sub

Private Sub ILogger_LogError(Source As String, ErrorNumber As Long, Description As String)
    WriteLog "ERROR", Source & " - " & ErrorNumber & ": " & Description
End Sub

Private Sub WriteLog(Level As String, Message As String)
    Dim fso As FileSystemObject
    Dim ts As TextStream
    Dim fileName As String
    
    Set fso = New FileSystemObject
    fileName = m_LogPath & Format(Date, "yyyymmdd") & ".log"
    
    Set ts = fso.OpenTextFile(fileName, ForAppending, True)
    ts.WriteLine Format(Now, "yyyy-mm-dd hh:nn:ss") & " [" & Level & "] " & Message
    ts.Close
    
    Set ts = Nothing
    Set fso = Nothing
End Sub
```

#### データアクセス層
```vb
' IRepository.cls - リポジトリインターフェース
Option Explicit

Public Function GetAll() As Collection
End Function

Public Function GetByID(ID As Long) As Object
End Function

Public Function Save(Entity As Object) As Boolean
End Function

Public Function Delete(ID As Long) As Boolean
End Function

' CustomerRepository.cls - 顧客リポジトリ実装
Option Explicit
Implements IRepository

Private m_Connection As ADODB.Connection
Private m_Logger As ILogger

Private Sub Class_Initialize()
    Set m_Connection = DatabaseManager.GetConnection()
    Set m_Logger = LoggerFactory.GetLogger()
End Sub

Private Function IRepository_GetAll() As Collection
    Dim col As Collection
    Dim rs As ADODB.Recordset
    Dim customer As Customer
    
    On Error GoTo ErrorHandler
    
    Set col = New Collection
    Set rs = m_Connection.Execute("SELECT * FROM Customers ORDER BY Name")
    
    Do While Not rs.EOF
        Set customer = MapToCustomer(rs)
        col.Add customer, CStr(customer.ID)
        rs.MoveNext
    Loop
    
    rs.Close
    Set rs = Nothing
    
    Set IRepository_GetAll = col
    Exit Function
    
ErrorHandler:
    m_Logger.LogError "CustomerRepository.GetAll", Err.Number, Err.Description
    Set IRepository_GetAll = New Collection
End Function

Private Function MapToCustomer(rs As ADODB.Recordset) As Customer
    Dim customer As Customer
    Set customer = New Customer
    
    With customer
        .ID = rs("CustomerID")
        .Name = rs("CustomerName") & ""
        .Email = rs("Email") & ""
        .Phone = rs("Phone") & ""
        .Address = rs("Address") & ""
        .City = rs("City") & ""
        .PostalCode = rs("PostalCode") & ""
        .Country = rs("Country") & ""
        .IsActive = rs("IsActive")
        .CreatedDate = rs("CreatedDate")
    End With
    
    Set MapToCustomer = customer
End Function
```

#### ビジネスロジック層
```vb
' ICustomerService.cls - 顧客サービスインターフェース
Option Explicit

Public Function GetActiveCustomers() As Collection
End Function

Public Function CreateCustomer(customerData As CustomerDTO) As Boolean
End Function

Public Function UpdateCustomerStatus(CustomerID As Long, IsActive As Boolean) As Boolean
End Function

Public Function ValidateCustomer(customer As Customer) As ValidationResult
End Function

' CustomerService.cls - 顧客サービス実装
Option Explicit
Implements ICustomerService

Private m_Repository As IRepository
Private m_Logger As ILogger
Private m_Validator As IValidator

Private Sub Class_Initialize()
    Set m_Repository = RepositoryFactory.GetRepository("Customer")
    Set m_Logger = LoggerFactory.GetLogger()
    Set m_Validator = New CustomerValidator
End Sub

Private Function ICustomerService_GetActiveCustomers() As Collection
    Dim allCustomers As Collection
    Dim activeCustomers As Collection
    Dim customer As Customer
    
    Set activeCustomers = New Collection
    Set allCustomers = m_Repository.GetAll()
    
    ' ビジネスロジック：アクティブな顧客のみフィルタリング
    For Each customer In allCustomers
        If customer.IsActive Then
            activeCustomers.Add customer
        End If
    Next
    
    m_Logger.LogInfo "Retrieved " & activeCustomers.Count & " active customers"
    Set ICustomerService_GetActiveCustomers = activeCustomers
End Function

Private Function ICustomerService_CreateCustomer(customerData As CustomerDTO) As Boolean
    Dim customer As Customer
    Dim validationResult As ValidationResult
    
    On Error GoTo ErrorHandler
    
    ' DTOからエンティティへの変換
    Set customer = MapDTOToCustomer(customerData)
    
    ' ビジネスルールの検証
    Set validationResult = m_Validator.Validate(customer)
    If Not validationResult.IsValid Then
        Err.Raise vbObjectError + 1001, , validationResult.GetErrorMessage()
    End If
    
    ' 追加のビジネスロジック
    customer.CreatedDate = Now
    customer.IsActive = True
    
    ' 保存
    ICustomerService_CreateCustomer = m_Repository.Save(customer)
    
    If ICustomerService_CreateCustomer Then
        m_Logger.LogInfo "Customer created: " & customer.Name
        ' イベント発行（必要に応じて）
        RaiseEvent CustomerCreated(customer)
    End If
    
    Exit Function
    
ErrorHandler:
    m_Logger.LogError "CustomerService.CreateCustomer", Err.Number, Err.Description
    ICustomerService_CreateCustomer = False
End Function
```

#### アプリケーション層
```vb
' CustomerController.cls - 顧客コントローラー
Option Explicit

Private m_Service As ICustomerService
Private m_View As ICustomerView
Private m_Logger As ILogger

Public Sub Initialize(View As ICustomerView)
    Set m_View = View
    Set m_Service = ServiceFactory.GetService("Customer")
    Set m_Logger = LoggerFactory.GetLogger()
End Sub

Public Sub LoadCustomers()
    On Error GoTo ErrorHandler
    
    Dim customers As Collection
    Set customers = m_Service.GetActiveCustomers()
    
    m_View.DisplayCustomers customers
    m_View.SetStatus "顧客データを読み込みました (" & customers.Count & "件)"
    
    Exit Sub
    
ErrorHandler:
    m_View.ShowError "顧客データの読み込みに失敗しました: " & Err.Description
    m_Logger.LogError "CustomerController.LoadCustomers", Err.Number, Err.Description
End Sub

Public Sub SaveCustomer()
    On Error GoTo ErrorHandler
    
    Dim customerData As CustomerDTO
    Set customerData = m_View.GetCustomerData()
    
    If m_Service.CreateCustomer(customerData) Then
        m_View.ShowMessage "顧客を登録しました"
        LoadCustomers ' リストを更新
    Else
        m_View.ShowError "顧客の登録に失敗しました"
    End If
    
    Exit Sub
    
ErrorHandler:
    m_View.ShowError Err.Description
End Sub
```

## 👥 MVPパターン

### MVP（Model-View-Presenter）の実装

```vb
' IView.cls - 基本ビューインターフェース
Option Explicit

Public Sub ShowMessage(Message As String)
End Sub

Public Sub ShowError(ErrorMessage As String)
End Sub

Public Sub SetEnabled(ControlName As String, Enabled As Boolean)
End Sub

' ICustomerView.cls - 顧客ビューインターフェース
Option Explicit
Implements IView

Public Function GetCustomerData() As CustomerDTO
End Function

Public Sub SetCustomerData(customer As Customer)
End Sub

Public Sub DisplayCustomers(customers As Collection)
End Sub

Public Sub ClearForm()
End Sub

' CustomerPresenter.cls - 顧客プレゼンター
Option Explicit

Private WithEvents m_View As frmCustomer
Private m_Model As CustomerModel
Private m_CurrentCustomer As Customer

Public Sub Initialize(View As frmCustomer, Model As CustomerModel)
    Set m_View = View
    Set m_Model = Model
    
    ' 初期データの読み込み
    RefreshView
End Sub

Private Sub m_View_SaveRequested()
    On Error GoTo ErrorHandler
    
    ' ビューからデータを取得
    Dim customerData As CustomerDTO
    Set customerData = m_View.GetCustomerData()
    
    ' モデルで保存
    If m_Model.SaveCustomer(customerData) Then
        m_View.ShowMessage "保存しました"
        RefreshView
    End If
    
    Exit Sub
    
ErrorHandler:
    m_View.ShowError Err.Description
End Sub

Private Sub m_View_DeleteRequested(CustomerID As Long)
    If MsgBox("削除してもよろしいですか？", vbYesNo + vbQuestion) = vbYes Then
        If m_Model.DeleteCustomer(CustomerID) Then
            m_View.ShowMessage "削除しました"
            RefreshView
        End If
    End If
End Sub

Private Sub RefreshView()
    Dim customers As Collection
    Set customers = m_Model.GetAllCustomers()
    m_View.DisplayCustomers customers
End Sub
```

## 🔌 サービス指向アーキテクチャ

### COMベースのサービス実装

```vb
' IBusinessService.cls - ビジネスサービスインターフェース
Option Explicit

Public Function ExecuteOperation(OperationName As String, Parameters As Dictionary) As ServiceResult
End Function

' OrderService.cls - 注文サービス（COM+コンポーネント）
Option Explicit
Implements IBusinessService

Private Function IBusinessService_ExecuteOperation(OperationName As String, Parameters As Dictionary) As ServiceResult
    Dim result As ServiceResult
    Set result = New ServiceResult
    
    Select Case OperationName
        Case "CreateOrder"
            Set result = CreateOrder(Parameters)
        Case "UpdateOrderStatus"
            Set result = UpdateOrderStatus(Parameters)
        Case "CalculateOrderTotal"
            Set result = CalculateOrderTotal(Parameters)
        Case Else
            result.Success = False
            result.ErrorMessage = "Unknown operation: " & OperationName
    End Select
    
    Set IBusinessService_ExecuteOperation = result
End Function

Private Function CreateOrder(Parameters As Dictionary) As ServiceResult
    Dim result As ServiceResult
    Dim tran As Transaction
    
    Set result = New ServiceResult
    
    On Error GoTo ErrorHandler
    
    ' COM+トランザクション開始
    Set tran = GetObjectContext.CreateInstance("Transaction.Manager")
    tran.Begin
    
    ' 注文作成ロジック
    Dim orderID As Long
    orderID = CreateOrderRecord(Parameters)
    
    ' 在庫確認と更新
    If Not UpdateInventory(Parameters("Items")) Then
        Err.Raise vbObjectError + 2001, , "在庫が不足しています"
    End If
    
    ' 注文明細作成
    CreateOrderDetails orderID, Parameters("Items")
    
    ' コミット
    tran.Commit
    
    result.Success = True
    result.Data = orderID
    
    Exit Function
    
ErrorHandler:
    tran.Rollback
    result.Success = False
    result.ErrorMessage = Err.Description
    
    Set CreateOrder = result
End Function
```

### サービスファサードの実装

```vb
' ServiceFacade.cls - サービスファサード
Option Explicit

Private m_Services As Dictionary

Private Sub Class_Initialize()
    Set m_Services = New Dictionary
    RegisterServices
End Sub

Private Sub RegisterServices()
    ' サービスの登録
    m_Services.Add "Customer", "CustomerService.Manager"
    m_Services.Add "Order", "OrderService.Manager"
    m_Services.Add "Inventory", "InventoryService.Manager"
    m_Services.Add "Shipping", "ShippingService.Manager"
End Sub

Public Function CallService(ServiceName As String, OperationName As String, Parameters As Dictionary) As ServiceResult
    Dim service As IBusinessService
    Dim result As ServiceResult
    
    On Error GoTo ErrorHandler
    
    ' サービスのインスタンス化
    If m_Services.Exists(ServiceName) Then
        Set service = CreateObject(m_Services(ServiceName))
    Else
        Err.Raise vbObjectError + 3001, , "Service not found: " & ServiceName
    End If
    
    ' サービス呼び出し
    Set result = service.ExecuteOperation(OperationName, Parameters)
    
    ' ログ記録
    LogServiceCall ServiceName, OperationName, result.Success
    
    Set CallService = result
    Exit Function
    
ErrorHandler:
    Set result = New ServiceResult
    result.Success = False
    result.ErrorMessage = Err.Description
    Set CallService = result
End Function
```

## 📡 イベント駆動アーキテクチャ

### イベントバスの実装

```vb
' IEventHandler.cls - イベントハンドラーインターフェース
Option Explicit

Public Sub HandleEvent(EventData As Dictionary)
End Sub

' EventBus.cls - イベントバス実装
Option Explicit

Private m_Handlers As Dictionary
Private m_AsyncQueue As Collection

Private Sub Class_Initialize()
    Set m_Handlers = New Dictionary
    Set m_AsyncQueue = New Collection
End Sub

Public Sub Subscribe(EventName As String, Handler As IEventHandler)
    Dim handlers As Collection
    
    If m_Handlers.Exists(EventName) Then
        Set handlers = m_Handlers(EventName)
    Else
        Set handlers = New Collection
        m_Handlers.Add EventName, handlers
    End If
    
    handlers.Add Handler
End Sub

Public Sub Publish(EventName As String, EventData As Dictionary)
    If Not m_Handlers.Exists(EventName) Then Exit Sub
    
    Dim handlers As Collection
    Dim handler As IEventHandler
    
    Set handlers = m_Handlers(EventName)
    
    ' 同期的にイベントを処理
    For Each handler In handlers
        On Error Resume Next
        handler.HandleEvent EventData
        On Error GoTo 0
    Next
End Sub

Public Sub PublishAsync(EventName As String, EventData As Dictionary)
    ' 非同期イベントをキューに追加
    Dim eventItem As Dictionary
    Set eventItem = New Dictionary
    
    eventItem.Add "EventName", EventName
    eventItem.Add "EventData", EventData
    eventItem.Add "Timestamp", Now
    
    m_AsyncQueue.Add eventItem
    
    ' タイマーで処理（簡易実装）
    ProcessAsyncEvents
End Sub

Private Sub ProcessAsyncEvents()
    ' Windows タイマーAPIを使用した非同期処理
    ' または、別スレッドでの処理（COM+使用）
End Sub
```

### ドメインイベントの実装

```vb
' DomainEvent.cls - ドメインイベント基底クラス
Option Explicit

Public EventID As String
Public EventType As String
Public OccurredAt As Date
Public AggregateID As String
Public UserID As String
Public Data As Dictionary

Private Sub Class_Initialize()
    EventID = CreateGUID()
    OccurredAt = Now
    Set Data = New Dictionary
End Sub

' CustomerCreatedEvent.cls - 顧客作成イベント
Option Explicit

Private m_BaseEvent As DomainEvent

Private Sub Class_Initialize()
    Set m_BaseEvent = New DomainEvent
    m_BaseEvent.EventType = "CustomerCreated"
End Sub

Public Property Get CustomerID() As Long
    CustomerID = m_BaseEvent.Data("CustomerID")
End Property

Public Property Let CustomerID(Value As Long)
    m_BaseEvent.Data("CustomerID") = Value
End Property

Public Property Get CustomerName() As String
    CustomerName = m_BaseEvent.Data("CustomerName")
End Property

Public Property Let CustomerName(Value As String)
    m_BaseEvent.Data("CustomerName") = Value
End Property
```

## 🎯 マイクロサービス風アーキテクチャ

### COMコンポーネントベースのサービス分離

```vb
' ServiceRegistry.cls - サービスレジストリ
Option Explicit

Private m_Services As Dictionary
Private m_ServiceEndpoints As Dictionary

Private Sub Class_Initialize()
    Set m_Services = New Dictionary
    Set m_ServiceEndpoints = New Dictionary
    LoadServiceConfiguration
End Sub

Private Sub LoadServiceConfiguration()
    ' サービス設定の読み込み（INIファイルまたはレジストリから）
    m_ServiceEndpoints.Add "CustomerService", "http://localhost:8081/customer"
    m_ServiceEndpoints.Add "OrderService", "http://localhost:8082/order"
    m_ServiceEndpoints.Add "InventoryService", "http://localhost:8083/inventory"
    
    ' COMサービスの登録
    m_Services.Add "CustomerService", "Customer.Service"
    m_Services.Add "OrderService", "Order.Service"
    m_Services.Add "InventoryService", "Inventory.Service"
End Sub

Public Function GetService(ServiceName As String) As Object
    If m_Services.Exists(ServiceName) Then
        ' ローカルCOMサービス
        Set GetService = CreateObject(m_Services(ServiceName))
    Else
        ' リモートサービスプロキシ
        Dim proxy As ServiceProxy
        Set proxy = New ServiceProxy
        proxy.Initialize ServiceName, m_ServiceEndpoints(ServiceName)
        Set GetService = proxy
    End If
End Function
```

### サービス間通信

```vb
' ServiceProxy.cls - サービスプロキシ
Option Explicit

Private m_ServiceName As String
Private m_Endpoint As String
Private m_HttpClient As WinHttp.WinHttpRequest

Public Sub Initialize(ServiceName As String, Endpoint As String)
    m_ServiceName = ServiceName
    m_Endpoint = Endpoint
    Set m_HttpClient = New WinHttp.WinHttpRequest
End Sub

Public Function CallMethod(MethodName As String, Parameters As Dictionary) As Dictionary
    Dim url As String
    Dim jsonRequest As String
    Dim jsonResponse As String
    
    On Error GoTo ErrorHandler
    
    ' URLの構築
    url = m_Endpoint & "/" & MethodName
    
    ' JSONリクエストの作成
    jsonRequest = DictionaryToJSON(Parameters)
    
    ' HTTP POST
    With m_HttpClient
        .Open "POST", url, False
        .SetRequestHeader "Content-Type", "application/json"
        .Send jsonRequest
        
        If .Status = 200 Then
            jsonResponse = .ResponseText
            Set CallMethod = JSONToDictionary(jsonResponse)
        Else
            Err.Raise vbObjectError + 4001, , "Service call failed: " & .StatusText
        End If
    End With
    
    Exit Function
    
ErrorHandler:
    Dim errorResult As Dictionary
    Set errorResult = New Dictionary
    errorResult.Add "Success", False
    errorResult.Add "Error", Err.Description
    Set CallMethod = errorResult
End Function
```

## 🔗 エンタープライズ統合パターン

### メッセージングパターン

```vb
' IMessageQueue.cls - メッセージキューインターフェース
Option Explicit

Public Sub SendMessage(QueueName As String, Message As String)
End Sub

Public Function ReceiveMessage(QueueName As String, TimeoutSeconds As Long) As String
End Function

' MSMQAdapter.cls - Microsoft Message Queue アダプター
Option Explicit
Implements IMessageQueue

Private Sub IMessageQueue_SendMessage(QueueName As String, Message As String)
    Dim qInfo As MSMQ.MSMQQueueInfo
    Dim q As MSMQ.MSMQQueue
    Dim msg As MSMQ.MSMQMessage
    
    Set qInfo = New MSMQ.MSMQQueueInfo
    qInfo.PathName = ".\Private$\" & QueueName
    
    Set q = qInfo.Open(MQ_SEND_ACCESS, MQ_DENY_NONE)
    
    Set msg = New MSMQ.MSMQMessage
    msg.Label = "VB6 Message"
    msg.Body = Message
    msg.Send q
    
    q.Close
End Sub

Private Function IMessageQueue_ReceiveMessage(QueueName As String, TimeoutSeconds As Long) As String
    Dim qInfo As MSMQ.MSMQQueueInfo
    Dim q As MSMQ.MSMQQueue
    Dim msg As MSMQ.MSMQMessage
    
    Set qInfo = New MSMQ.MSMQQueueInfo
    qInfo.PathName = ".\Private$\" & QueueName
    
    Set q = qInfo.Open(MQ_RECEIVE_ACCESS, MQ_DENY_NONE)
    
    Set msg = q.Receive(, , , TimeoutSeconds * 1000)
    
    If Not msg Is Nothing Then
        IMessageQueue_ReceiveMessage = msg.Body
    Else
        IMessageQueue_ReceiveMessage = ""
    End If
    
    q.Close
End Function
```

### サーキットブレーカーパターン

```vb
' CircuitBreaker.cls - サーキットブレーカー実装
Option Explicit

Private Enum CircuitState
    Closed = 0
    Open = 1
    HalfOpen = 2
End Enum

Private m_State As CircuitState
Private m_FailureCount As Long
Private m_LastFailureTime As Date
Private m_Threshold As Long
Private m_Timeout As Long

Private Sub Class_Initialize()
    m_State = Closed
    m_FailureCount = 0
    m_Threshold = 5
    m_Timeout = 60 ' 秒
End Sub

Public Function Call(Target As Object, MethodName As String, Parameters As Variant) As Variant
    On Error GoTo ErrorHandler
    
    ' サーキットが開いている場合
    If m_State = Open Then
        If DateDiff("s", m_LastFailureTime, Now) > m_Timeout Then
            m_State = HalfOpen
        Else
            Err.Raise vbObjectError + 5001, , "Circuit breaker is open"
        End If
    End If
    
    ' メソッド呼び出し
    Call = CallByName(Target, MethodName, VbMethod, Parameters)
    
    ' 成功時の処理
    If m_State = HalfOpen Then
        m_State = Closed
        m_FailureCount = 0
    End If
    
    Exit Function
    
ErrorHandler:
    m_FailureCount = m_FailureCount + 1
    m_LastFailureTime = Now
    
    If m_FailureCount >= m_Threshold Then
        m_State = Open
    End If
    
    Err.Raise Err.Number, Err.Source, Err.Description
End Function
```

---

このガイドは、VB6でエンタープライズレベルのアーキテクチャパターンを実装するための包括的な参考資料です。