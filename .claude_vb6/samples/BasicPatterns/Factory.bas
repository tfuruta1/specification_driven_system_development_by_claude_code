Attribute VB_Name = "modFactory"
'**********************************************************************
' モジュール名: modFactory
' 説明: Factoryパターンの実装例
' 作成日: 2025/02/08
' 文字コード: Shift-JIS (必須)
'**********************************************************************

Option Explicit

' データソースタイプ定義
Public Enum DataSourceType
    dstSQLServer = 1
    dstOracle = 2
    dstAccess = 3
    dstExcel = 4
    dstXML = 5
End Enum

' レポートタイプ定義
Public Enum ReportType
    rtPDF = 1
    rtExcel = 2
    rtHTML = 3
    rtCrystal = 4
End Enum

'**********************************************************************
' DAOファクトリー
'**********************************************************************
Public Function CreateDAO(EntityType As String, DataSource As DataSourceType) As Object
    Select Case UCase(EntityType)
        Case "CUSTOMER"
            Set CreateDAO = CreateCustomerDAO(DataSource)
            
        Case "ORDER"
            Set CreateDAO = CreateOrderDAO(DataSource)
            
        Case "PRODUCT"
            Set CreateDAO = CreateProductDAO(DataSource)
            
        Case "EMPLOYEE"
            Set CreateDAO = CreateEmployeeDAO(DataSource)
            
        Case Else
            Err.Raise vbObjectError + 1001, "CreateDAO", _
                     "不明なエンティティタイプ: " & EntityType
    End Select
End Function

'**********************************************************************
' 顧客DAOファクトリー
'**********************************************************************
Private Function CreateCustomerDAO(DataSource As DataSourceType) As Object
    Select Case DataSource
        Case dstSQLServer
            Set CreateCustomerDAO = New clsCustomerSQLServerDAO
            
        Case dstOracle
            Set CreateCustomerDAO = New clsCustomerOracleDAO
            
        Case dstAccess
            Set CreateCustomerDAO = New clsCustomerAccessDAO
            
        Case dstExcel
            Set CreateCustomerDAO = New clsCustomerExcelDAO
            
        Case dstXML
            Set CreateCustomerDAO = New clsCustomerXMLDAO
            
        Case Else
            Err.Raise vbObjectError + 1002, "CreateCustomerDAO", _
                     "サポートされていないデータソース"
    End Select
End Function

'**********************************************************************
' レポートファクトリー
'**********************************************************************
Public Function CreateReport(ReportName As String, OutputType As ReportType) As Object
    Dim report As Object
    
    Select Case OutputType
        Case rtPDF
            Set report = New clsPDFReport
            
        Case rtExcel
            Set report = New clsExcelReport
            
        Case rtHTML
            Set report = New clsHTMLReport
            
        Case rtCrystal
            Set report = New clsCrystalReport
            
        Case Else
            Err.Raise vbObjectError + 1003, "CreateReport", _
                     "サポートされていないレポートタイプ"
    End Select
    
    ' レポート初期化
    report.Initialize ReportName
    Set CreateReport = report
End Function

'**********************************************************************
' サービスファクトリー
'**********************************************************************
Public Function CreateService(ServiceType As String) As Object
    Select Case UCase(ServiceType)
        Case "AUTHENTICATION"
            Set CreateService = New clsAuthenticationService
            
        Case "AUTHORIZATION"
            Set CreateService = New clsAuthorizationService
            
        Case "LOGGING"
            Set CreateService = New clsLoggingService
            
        Case "EMAIL"
            Set CreateService = New clsEmailService
            
        Case "VALIDATION"
            Set CreateService = New clsValidationService
            
        Case "CACHE"
            Set CreateService = New clsCacheService
            
        Case Else
            Err.Raise vbObjectError + 1004, "CreateService", _
                     "不明なサービスタイプ: " & ServiceType
    End Select
End Function

'**********************************************************************
' コントロールファクトリー
'**********************************************************************
Public Function CreateCustomControl(ControlType As String, Parent As Object) As Object
    Dim ctrl As Object
    
    Select Case UCase(ControlType)
        Case "DATAGRID"
            Set ctrl = Parent.Controls.Add("MSDBGrid.DBGrid", "Grid" & GetNextControlID())
            ConfigureDataGrid ctrl
            
        Case "DATEPICKER"
            Set ctrl = Parent.Controls.Add("MSComCtl2.DTPicker", "DatePicker" & GetNextControlID())
            ConfigureDatePicker ctrl
            
        Case "COMBOBOX"
            Set ctrl = Parent.Controls.Add("VB.ComboBox", "Combo" & GetNextControlID())
            ConfigureComboBox ctrl
            
        Case "LISTVIEW"
            Set ctrl = Parent.Controls.Add("MSComctlLib.ListView", "ListView" & GetNextControlID())
            ConfigureListView ctrl
            
        Case Else
            Err.Raise vbObjectError + 1005, "CreateCustomControl", _
                     "不明なコントロールタイプ: " & ControlType
    End Select
    
    ctrl.Visible = True
    Set CreateCustomControl = ctrl
End Function

'**********************************************************************
' 設定ヘルパー関数
'**********************************************************************
Private Sub ConfigureDataGrid(Grid As Object)
    With Grid
        .AllowAddNew = True
        .AllowDelete = True
        .AllowUpdate = True
        .RecordSelectors = True
        .DefColWidth = 1500
    End With
End Sub

Private Sub ConfigureDatePicker(DatePicker As Object)
    With DatePicker
        .Format = 3 ' dtpCustom
        .CustomFormat = "yyyy/MM/dd"
        .UpDown = False
    End With
End Sub

Private Sub ConfigureComboBox(Combo As Object)
    With Combo
        .Style = 2 ' Dropdown List
        .Sorted = True
    End With
End Sub

Private Sub ConfigureListView(ListView As Object)
    With ListView
        .View = 3 ' lvwReport
        .GridLines = True
        .FullRowSelect = True
        .HideSelection = False
    End With
End Sub

'**********************************************************************
' ユーティリティ関数
'**********************************************************************
Private Function GetNextControlID() As Long
    Static controlCounter As Long
    controlCounter = controlCounter + 1
    GetNextControlID = controlCounter
End Function

'**********************************************************************
' 拡張ファクトリー: ビルダーパターン組み合わせ
'**********************************************************************
Public Function CreateComplexObject(ObjectType As String) As Object
    Dim builder As Object
    
    Select Case UCase(ObjectType)
        Case "INVOICE"
            Set builder = New clsInvoiceBuilder
            
        Case "REPORT"
            Set builder = New clsReportBuilder
            
        Case "FORM"
            Set builder = New clsFormBuilder
            
        Case Else
            Err.Raise vbObjectError + 1006, "CreateComplexObject", _
                     "不明なオブジェクトタイプ: " & ObjectType
    End Select
    
    ' ビルダーを使用してオブジェクトを構築
    Set CreateComplexObject = builder.Build()
End Function

'**********************************************************************
' 抽象ファクトリーパターン実装例
'**********************************************************************
' IAbstractFactory インターフェース（別ファイルで定義）
' Public Function CreateProductA() As Object
' Public Function CreateProductB() As Object

' ConcreteFactory1.cls の実装例
' Implements IAbstractFactory
'
' Private Function IAbstractFactory_CreateProductA() As Object
'     Set IAbstractFactory_CreateProductA = New ProductA1
' End Function
'
' Private Function IAbstractFactory_CreateProductB() As Object
'     Set IAbstractFactory_CreateProductB = New ProductB1
' End Function

'**********************************************************************
' 使用例
'**********************************************************************
Public Sub DemoFactoryUsage()
    Dim customerDAO As Object
    Dim report As Object
    Dim service As Object
    Dim customers As Collection
    
    On Error GoTo ErrorHandler
    
    ' DAOの作成
    Set customerDAO = CreateDAO("Customer", dstSQLServer)
    Set customers = customerDAO.GetAll()
    
    ' レポートの作成と実行
    Set report = CreateReport("CustomerList", rtPDF)
    report.SetDataSource customers
    report.Generate "C:\Reports\CustomerList.pdf"
    
    ' サービスの利用
    Set service = CreateService("Logging")
    service.Log "レポートが生成されました", "INFO"
    
    MsgBox "処理が完了しました", vbInformation
    
    Exit Sub
    
ErrorHandler:
    MsgBox "エラーが発生しました: " & Err.Description, vbCritical
End Sub

'**********************************************************************
' 設定駆動ファクトリー
'**********************************************************************
Public Function CreateFromConfig(ConfigKey As String) As Object
    Dim config As clsConfigManager
    Dim className As String
    
    ' 設定からクラス名を取得
    Set config = GetConfigManager()
    className = config.Value("Factory." & ConfigKey & ".ClassName")
    
    If className = "" Then
        Err.Raise vbObjectError + 1007, "CreateFromConfig", _
                 "設定が見つかりません: " & ConfigKey
    End If
    
    ' 動的にオブジェクトを作成
    Set CreateFromConfig = CreateObject(className)
End Function