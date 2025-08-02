VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "clsCustomer"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
'**********************************************************************
' クラス名: clsCustomer
' 説明: 顧客エンティティクラス
' 作成日: 2025/02/08
' 文字コード: Shift-JIS (必須)
'**********************************************************************

Option Explicit

' プライベート変数
Private m_CustomerID As Long
Private m_CustomerCode As String
Private m_CustomerName As String
Private m_CustomerNameKana As String
Private m_ContactPerson As String
Private m_Department As String
Private m_Email As String
Private m_Phone As String
Private m_Fax As String
Private m_Mobile As String
Private m_PostalCode As String
Private m_Address1 As String
Private m_Address2 As String
Private m_City As String
Private m_Prefecture As String
Private m_Country As String
Private m_CreditLimit As Currency
Private m_PaymentTerms As Integer
Private m_DiscountRate As Single
Private m_TaxExempt As Boolean
Private m_Notes As String
Private m_IsActive As Boolean
Private m_CreatedDate As Date
Private m_CreatedBy As String
Private m_ModifiedDate As Date
Private m_ModifiedBy As String

' 定数
Private Const DEFAULT_PAYMENT_TERMS As Integer = 30
Private Const DEFAULT_CREDIT_LIMIT As Currency = 1000000

'**********************************************************************
' 初期化・終了処理
'**********************************************************************
Private Sub Class_Initialize()
    ' デフォルト値設定
    m_CustomerID = 0
    m_CustomerCode = ""
    m_CustomerName = ""
    m_Country = "Japan"
    m_CreditLimit = DEFAULT_CREDIT_LIMIT
    m_PaymentTerms = DEFAULT_PAYMENT_TERMS
    m_DiscountRate = 0
    m_TaxExempt = False
    m_IsActive = True
    m_CreatedDate = Now
    m_ModifiedDate = Now
End Sub

'**********************************************************************
' プロパティ
'**********************************************************************

' CustomerID
Public Property Get CustomerID() As Long
    CustomerID = m_CustomerID
End Property

Public Property Let CustomerID(ByVal Value As Long)
    m_CustomerID = Value
End Property

' CustomerCode
Public Property Get CustomerCode() As String
    CustomerCode = m_CustomerCode
End Property

Public Property Let CustomerCode(ByVal Value As String)
    m_CustomerCode = Trim(Value)
End Property

' CustomerName
Public Property Get CustomerName() As String
    CustomerName = m_CustomerName
End Property

Public Property Let CustomerName(ByVal Value As String)
    m_CustomerName = Trim(Value)
End Property

' CustomerNameKana
Public Property Get CustomerNameKana() As String
    CustomerNameKana = m_CustomerNameKana
End Property

Public Property Let CustomerNameKana(ByVal Value As String)
    m_CustomerNameKana = Trim(Value)
End Property

' ContactPerson
Public Property Get ContactPerson() As String
    ContactPerson = m_ContactPerson
End Property

Public Property Let ContactPerson(ByVal Value As String)
    m_ContactPerson = Trim(Value)
End Property

' Email
Public Property Get Email() As String
    Email = m_Email
End Property

Public Property Let Email(ByVal Value As String)
    m_Email = LCase(Trim(Value))
End Property

' Phone
Public Property Get Phone() As String
    Phone = m_Phone
End Property

Public Property Let Phone(ByVal Value As String)
    m_Phone = FormatPhoneNumber(Value)
End Property

' Address
Public Property Get FullAddress() As String
    Dim addr As String
    
    addr = m_PostalCode
    If addr <> "" Then addr = addr & " "
    
    If m_Prefecture <> "" Then addr = addr & m_Prefecture & " "
    If m_City <> "" Then addr = addr & m_City & " "
    If m_Address1 <> "" Then addr = addr & m_Address1 & " "
    If m_Address2 <> "" Then addr = addr & m_Address2
    
    FullAddress = Trim(addr)
End Property

' CreditLimit
Public Property Get CreditLimit() As Currency
    CreditLimit = m_CreditLimit
End Property

Public Property Let CreditLimit(ByVal Value As Currency)
    If Value >= 0 Then
        m_CreditLimit = Value
    End If
End Property

' IsActive
Public Property Get IsActive() As Boolean
    IsActive = m_IsActive
End Property

Public Property Let IsActive(ByVal Value As Boolean)
    m_IsActive = Value
End Property

'**********************************************************************
' メソッド
'**********************************************************************

'----------------------------------------------------------------------
' 検証メソッド
'----------------------------------------------------------------------
Public Function Validate() As Boolean
    Dim errors As Collection
    Set errors = New Collection
    
    ' 必須フィールドチェック
    If m_CustomerCode = "" Then
        errors.Add "顧客コードが入力されていません"
    End If
    
    If m_CustomerName = "" Then
        errors.Add "顧客名が入力されていません"
    End If
    
    ' Emailフォーマットチェック
    If m_Email <> "" And Not IsValidEmail(m_Email) Then
        errors.Add "メールアドレスの形式が不正です"
    End If
    
    ' 数値範囲チェック
    If m_PaymentTerms < 0 Or m_PaymentTerms > 365 Then
        errors.Add "支払条件は0〜365日の範囲で入力してください"
    End If
    
    If m_DiscountRate < 0 Or m_DiscountRate > 100 Then
        errors.Add "割引率は0〜100%の範囲で入力してください"
    End If
    
    ' エラーがある場合
    If errors.Count > 0 Then
        Dim msg As String
        Dim error As Variant
        For Each error In errors
            msg = msg & "- " & error & vbCrLf
        Next
        
        MsgBox "以下のエラーがあります:" & vbCrLf & vbCrLf & msg, _
               vbExclamation, "入力エラー"
        Validate = False
    Else
        Validate = True
    End If
End Function

'----------------------------------------------------------------------
' 保存メソッド
'----------------------------------------------------------------------
Public Function Save() As Boolean
    Dim dao As clsCustomerDAO
    
    On Error GoTo ErrorHandler
    
    ' 検証
    If Not Validate() Then
        Save = False
        Exit Function
    End If
    
    ' DAOを使用して保存
    Set dao = New clsCustomerDAO
    
    If m_CustomerID = 0 Then
        ' 新規登録
        m_CreatedBy = g_CurrentUser.UserName
        m_CreatedDate = Now
        Save = dao.Insert(Me)
    Else
        ' 更新
        m_ModifiedBy = g_CurrentUser.UserName
        m_ModifiedDate = Now
        Save = dao.Update(Me)
    End If
    
    Set dao = Nothing
    Exit Function
    
ErrorHandler:
    Save = False
    MsgBox "Save Error: " & Err.Description, vbCritical
End Function

'----------------------------------------------------------------------
' 削除メソッド
'----------------------------------------------------------------------
Public Function Delete() As Boolean
    Dim dao As clsCustomerDAO
    
    On Error GoTo ErrorHandler
    
    If m_CustomerID = 0 Then
        Delete = False
        Exit Function
    End If
    
    ' 削除確認
    If MsgBox("この顧客を削除しますか？", _
              vbQuestion + vbYesNo, "削除確認") = vbNo Then
        Delete = False
        Exit Function
    End If
    
    Set dao = New clsCustomerDAO
    Delete = dao.Delete(m_CustomerID)
    Set dao = Nothing
    
    Exit Function
    
ErrorHandler:
    Delete = False
    MsgBox "Delete Error: " & Err.Description, vbCritical
End Function

'----------------------------------------------------------------------
' クローンメソッド
'----------------------------------------------------------------------
Public Function Clone() As clsCustomer
    Dim newCustomer As clsCustomer
    Set newCustomer = New clsCustomer
    
    ' プロパティをコピー（ID以外）
    With newCustomer
        .CustomerCode = m_CustomerCode & "_COPY"
        .CustomerName = m_CustomerName
        .CustomerNameKana = m_CustomerNameKana
        .ContactPerson = m_ContactPerson
        .Email = m_Email
        .Phone = m_Phone
        ' ... 他のプロパティもコピー
    End With
    
    Set Clone = newCustomer
End Function

'**********************************************************************
' プライベート関数
'**********************************************************************
Private Function IsValidEmail(Email As String) As Boolean
    Dim regEx As Object
    Set regEx = CreateObject("VBScript.RegExp")
    
    regEx.Pattern = "^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$"
    IsValidEmail = regEx.Test(Email)
    
    Set regEx = Nothing
End Function

Private Function FormatPhoneNumber(Phone As String) As String
    ' 電話番号のフォーマット
    Dim cleaned As String
    cleaned = Replace(Phone, "-", "")
    cleaned = Replace(cleaned, " ", "")
    cleaned = Replace(cleaned, "(", "")
    cleaned = Replace(cleaned, ")", "")
    
    ' シンプルなフォーマットを適用
    If Len(cleaned) = 10 Then
        FormatPhoneNumber = Left(cleaned, 3) & "-" & _
                           Mid(cleaned, 4, 3) & "-" & _
                           Right(cleaned, 4)
    ElseIf Len(cleaned) = 11 Then
        FormatPhoneNumber = Left(cleaned, 3) & "-" & _
                           Mid(cleaned, 4, 4) & "-" & _
                           Right(cleaned, 4)
    Else
        FormatPhoneNumber = Phone
    End If
End Function