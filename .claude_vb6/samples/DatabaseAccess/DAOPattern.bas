Attribute VB_Name = "modDAOPattern"
'**********************************************************************
' モジュール名: modDAOPattern
' 説明: データアクセスオブジェクト(DAO)パターンの実装
' 作成日: 2025/02/08
' 文字コード: Shift-JIS (必須)
'**********************************************************************

Option Explicit

'**********************************************************************
' 抽象DAOインターフェース定義
'**********************************************************************
' IBaseDAO.cls として別ファイルで定義
' Public Function GetAll() As Collection
' Public Function GetByID(ID As Long) As Object
' Public Function Insert(Entity As Object) As Boolean
' Public Function Update(Entity As Object) As Boolean
' Public Function Delete(ID As Long) As Boolean
' Public Function Find(Criteria As String) As Collection

'**********************************************************************
' ジェネリックDAO基底クラス
'**********************************************************************
' clsBaseDAO.cls として別ファイルで実装
'
' Option Explicit
' Implements IBaseDAO
' 
' Protected m_Connection As ADODB.Connection
' Protected m_TableName As String
' Protected m_PrimaryKey As String
' 
' Private Sub Class_Initialize()
'     Set m_Connection = GetConnection()
' End Sub
' 
' Private Sub Class_Terminate()
'     If Not m_Connection Is Nothing Then
'         If m_Connection.State = adStateOpen Then
'             m_Connection.Close
'         End If
'         Set m_Connection = Nothing
'     End If
' End Sub
' 
' Protected Function ExecuteQuery(SQL As String) As ADODB.Recordset
'     Dim rs As ADODB.Recordset
'     Set rs = New ADODB.Recordset
'     rs.Open SQL, m_Connection, adOpenStatic, adLockReadOnly
'     Set rs.ActiveConnection = Nothing
'     Set ExecuteQuery = rs
' End Function
' 
' Protected Function ExecuteNonQuery(SQL As String) As Long
'     Dim recordsAffected As Long
'     m_Connection.Execute SQL, recordsAffected, adExecuteNoRecords
'     ExecuteNonQuery = recordsAffected
' End Function

'**********************************************************************
' 具体的なDAO実装例: 顧客DAO
'**********************************************************************
' clsCustomerDAO.cls として別ファイルで実装
'
' Option Explicit
' Implements IBaseDAO
' 
' Private m_Connection As ADODB.Connection
' Private Const TABLE_NAME As String = "Customers"
' Private Const PRIMARY_KEY As String = "CustomerID"
' 
' Private Sub Class_Initialize()
'     Set m_Connection = GetConnection()
' End Sub
' 
' Private Function IBaseDAO_GetAll() As Collection
'     Dim sql As String
'     Dim rs As ADODB.Recordset
'     Dim col As Collection
'     Dim customer As clsCustomer
'     
'     sql = "SELECT * FROM " & TABLE_NAME & " ORDER BY CustomerName"
'     Set rs = ExecuteQuery(sql)
'     Set col = New Collection
'     
'     Do While Not rs.EOF
'         Set customer = MapToCustomer(rs)
'         col.Add customer, CStr(customer.CustomerID)
'         rs.MoveNext
'     Loop
'     
'     rs.Close
'     Set rs = Nothing
'     Set IBaseDAO_GetAll = col
' End Function
' 
' Private Function IBaseDAO_GetByID(ID As Long) As Object
'     Dim sql As String
'     Dim rs As ADODB.Recordset
'     Dim customer As clsCustomer
'     
'     sql = "SELECT * FROM " & TABLE_NAME & " WHERE " & PRIMARY_KEY & " = " & ID
'     Set rs = ExecuteQuery(sql)
'     
'     If Not rs.EOF Then
'         Set customer = MapToCustomer(rs)
'     End If
'     
'     rs.Close
'     Set rs = Nothing
'     Set IBaseDAO_GetByID = customer
' End Function
' 
' Private Function IBaseDAO_Insert(Entity As Object) As Boolean
'     Dim customer As clsCustomer
'     Dim sql As String
'     Dim cmd As ADODB.Command
'     
'     Set customer = Entity
'     
'     ' パラメータ化クエリでSQLインジェクション対策
'     Set cmd = New ADODB.Command
'     With cmd
'         .ActiveConnection = m_Connection
'         .CommandText = "INSERT INTO " & TABLE_NAME & _
'                       " (CustomerName, Email, Phone, Address, City, PostalCode, Country) " & _
'                       "VALUES (?, ?, ?, ?, ?, ?, ?)"
'         .CommandType = adCmdText
'         
'         .Parameters.Append .CreateParameter("Name", adVarChar, adParamInput, 100, customer.CustomerName)
'         .Parameters.Append .CreateParameter("Email", adVarChar, adParamInput, 100, customer.Email)
'         .Parameters.Append .CreateParameter("Phone", adVarChar, adParamInput, 20, customer.Phone)
'         .Parameters.Append .CreateParameter("Address", adVarChar, adParamInput, 200, customer.Address)
'         .Parameters.Append .CreateParameter("City", adVarChar, adParamInput, 50, customer.City)
'         .Parameters.Append .CreateParameter("PostalCode", adVarChar, adParamInput, 10, customer.PostalCode)
'         .Parameters.Append .CreateParameter("Country", adVarChar, adParamInput, 50, customer.Country)
'         
'         .Execute
'     End With
'     
'     IBaseDAO_Insert = True
'     Set cmd = Nothing
' End Function
' 
' Private Function MapToCustomer(rs As ADODB.Recordset) As clsCustomer
'     Dim customer As clsCustomer
'     Set customer = New clsCustomer
'     
'     With customer
'         .CustomerID = rs("CustomerID")
'         .CustomerName = rs("CustomerName") & ""
'         .Email = rs("Email") & ""
'         .Phone = rs("Phone") & ""
'         .Address = rs("Address") & ""
'         .City = rs("City") & ""
'         .PostalCode = rs("PostalCode") & ""
'         .Country = rs("Country") & ""
'         .IsActive = rs("IsActive")
'         .CreatedDate = rs("CreatedDate")
'         .ModifiedDate = rs("ModifiedDate")
'     End With
'     
'     Set MapToCustomer = customer
' End Function

'**********************************************************************
' Repositoryパターンの実装
'**********************************************************************
' clsCustomerRepository.cls として別ファイルで実装
'
' Option Explicit
' 
' Private m_DAO As IBaseDAO
' Private m_Cache As Collection
' Private m_CacheExpiry As Date
' Private Const CACHE_DURATION_MINUTES As Integer = 5
' 
' Private Sub Class_Initialize()
'     Set m_DAO = New clsCustomerDAO
'     Set m_Cache = New Collection
' End Sub
' 
' Public Function GetActiveCustomers() As Collection
'     Dim allCustomers As Collection
'     Dim activeCustomers As Collection
'     Dim customer As clsCustomer
'     
'     ' キャッシュチェック
'     If IsCacheValid() Then
'         Set GetActiveCustomers = m_Cache
'         Exit Function
'     End If
'     
'     Set allCustomers = m_DAO.GetAll()
'     Set activeCustomers = New Collection
'     
'     ' アクティブな顧客のみフィルタリング
'     For Each customer In allCustomers
'         If customer.IsActive Then
'             activeCustomers.Add customer
'         End If
'     Next
'     
'     ' キャッシュ更新
'     Set m_Cache = activeCustomers
'     m_CacheExpiry = DateAdd("n", CACHE_DURATION_MINUTES, Now)
'     
'     Set GetActiveCustomers = activeCustomers
' End Function
' 
' Public Function GetCustomersByCity(City As String) As Collection
'     Dim criteria As String
'     criteria = "City = '" & Replace(City, "'", "''") & "'"
'     Set GetCustomersByCity = m_DAO.Find(criteria)
' End Function
' 
' Public Function SaveCustomer(customer As clsCustomer) As Boolean
'     Dim result As Boolean
'     
'     If customer.CustomerID = 0 Then
'         result = m_DAO.Insert(customer)
'     Else
'         result = m_DAO.Update(customer)
'     End If
'     
'     ' キャッシュ無効化
'     InvalidateCache
'     
'     SaveCustomer = result
' End Function
' 
' Private Function IsCacheValid() As Boolean
'     IsCacheValid = (m_Cache.Count > 0) And (Now < m_CacheExpiry)
' End Function
' 
' Private Sub InvalidateCache()
'     Set m_Cache = New Collection
'     m_CacheExpiry = DateAdd("s", -1, Now)
' End Sub

'**********************************************************************
' Unit of Workパターンの実装
'**********************************************************************
' clsUnitOfWork.cls として別ファイルで実装
'
' Option Explicit
' 
' Private m_Connection As ADODB.Connection
' Private m_InTransaction As Boolean
' Private m_Repositories As Collection
' 
' Private Sub Class_Initialize()
'     Set m_Connection = GetConnection()
'     Set m_Repositories = New Collection
'     m_InTransaction = False
' End Sub
' 
' Public Property Get CustomerRepository() As clsCustomerRepository
'     Dim key As String
'     key = "Customer"
'     
'     If Not RepositoryExists(key) Then
'         Dim repo As clsCustomerRepository
'         Set repo = New clsCustomerRepository
'         repo.SetConnection m_Connection
'         m_Repositories.Add repo, key
'     End If
'     
'     Set CustomerRepository = m_Repositories(key)
' End Property
' 
' Public Property Get OrderRepository() As clsOrderRepository
'     ' 同様の実装
' End Property
' 
' Public Sub BeginTransaction()
'     If Not m_InTransaction Then
'         m_Connection.BeginTrans
'         m_InTransaction = True
'     End If
' End Sub
' 
' Public Sub Commit()
'     If m_InTransaction Then
'         m_Connection.CommitTrans
'         m_InTransaction = False
'     End If
' End Sub
' 
' Public Sub Rollback()
'     If m_InTransaction Then
'         m_Connection.RollbackTrans
'         m_InTransaction = False
'     End If
' End Sub
' 
' Private Function RepositoryExists(key As String) As Boolean
'     Dim obj As Object
'     On Error Resume Next
'     Set obj = m_Repositories(key)
'     RepositoryExists = (Err.Number = 0)
'     On Error GoTo 0
' End Function

'**********************************************************************
' DAOファクトリー
'**********************************************************************
Public Function CreateDAO(EntityType As String, _
                         Optional ConnectionString As String = "") As Object
    Dim dao As Object
    
    Select Case UCase(EntityType)
        Case "CUSTOMER"
            Set dao = New clsCustomerDAO
            
        Case "ORDER"
            Set dao = New clsOrderDAO
            
        Case "PRODUCT"
            Set dao = New clsProductDAO
            
        Case "EMPLOYEE"
            Set dao = New clsEmployeeDAO
            
        Case Else
            Err.Raise vbObjectError + 2001, "CreateDAO", _
                     "不明なエンティティタイプ: " & EntityType
    End Select
    
    ' カスタム接続文字列が指定されている場合
    If ConnectionString <> "" Then
        dao.SetConnectionString ConnectionString
    End If
    
    Set CreateDAO = dao
End Function

'**********************************************************************
' 使用例
'**********************************************************************
Public Sub DemoDAOPattern()
    Dim uow As clsUnitOfWork
    Dim customer As clsCustomer
    Dim customers As Collection
    
    On Error GoTo ErrorHandler
    
    ' Unit of Workの開始
    Set uow = New clsUnitOfWork
    uow.BeginTransaction
    
    ' 新規顧客の作成
    Set customer = New clsCustomer
    With customer
        .CustomerName = "テスト顧客"
        .Email = "test@example.com"
        .Phone = "03-1234-5678"
        .City = "Tokyo"
        .IsActive = True
    End With
    
    ' 保存
    If uow.CustomerRepository.SaveCustomer(customer) Then
        Debug.Print "顧客が保存されました"
    End If
    
    ' アクティブな顧客を取得
    Set customers = uow.CustomerRepository.GetActiveCustomers()
    Debug.Print "アクティブな顧客数: " & customers.Count
    
    ' コミット
    uow.Commit
    
    MsgBox "処理が完了しました", vbInformation
    
    Exit Sub
    
ErrorHandler:
    If Not uow Is Nothing Then
        uow.Rollback
    End If
    MsgBox "Error: " & Err.Description, vbCritical
End Sub

'**********************************************************************
' スペシフィケーションパターンの実装
'**********************************************************************
' ISpecification.cls として別ファイルで定義
' Public Function IsSatisfiedBy(Entity As Object) As Boolean
' Public Function And_(Other As ISpecification) As ISpecification
' Public Function Or_(Other As ISpecification) As ISpecification
' Public Function Not_() As ISpecification

' ActiveCustomerSpecification.cls の実装例
' Implements ISpecification
' 
' Private Function ISpecification_IsSatisfiedBy(Entity As Object) As Boolean
'     Dim customer As clsCustomer
'     Set customer = Entity
'     ISpecification_IsSatisfiedBy = customer.IsActive
' End Function

' HighValueCustomerSpecification.cls の実装例
' Implements ISpecification
' 
' Private m_MinimumOrderAmount As Currency
' 
' Public Sub Initialize(MinimumAmount As Currency)
'     m_MinimumOrderAmount = MinimumAmount
' End Sub
' 
' Private Function ISpecification_IsSatisfiedBy(Entity As Object) As Boolean
'     Dim customer As clsCustomer
'     Set customer = Entity
'     ISpecification_IsSatisfiedBy = (customer.TotalOrderAmount >= m_MinimumOrderAmount)
' End Function