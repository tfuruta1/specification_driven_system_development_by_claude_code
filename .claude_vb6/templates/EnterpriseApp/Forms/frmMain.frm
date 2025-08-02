VERSION 5.00
Object = "{831FDD16-0C5C-11D2-A9FC-0000F8754DA1}#2.0#0"; "MSCOMCTL.OCX"
Begin VB.MDIForm frmMain 
   BackColor       =   &H8000000C&
   Caption         =   "Enterprise Application"
   ClientHeight    =   8520
   ClientLeft      =   120
   ClientTop       =   765
   ClientWidth     =   14400
   LinkTopic       =   "MDIForm1"
   StartUpPosition =   2  'CenterScreen
   WindowState     =   2  'Maximized
   Begin MSComctlLib.StatusBar StatusBar1 
      Align           =   2  'Align Bottom
      Height          =   315
      Left            =   0
      TabIndex        =   1
      Top             =   8205
      Width           =   14400
      _ExtentX        =   25400
      _ExtentY        =   556
      _Version        =   393216
      BeginProperty Panels {8E3867A5-8586-11D1-B16A-00C0F0283628} 
         NumPanels       =   4
         BeginProperty Panel1 {8E3867AB-8586-11D1-B16A-00C0F0283628} 
            AutoSize        =   1
            Object.Width           =   19923
            Text            =   "Ready"
            TextSave        =   "Ready"
         EndProperty
         BeginProperty Panel2 {8E3867AB-8586-11D1-B16A-00C0F0283628} 
            Style           =   6
            TextSave        =   "2025/02/08"
         EndProperty
         BeginProperty Panel3 {8E3867AB-8586-11D1-B16A-00C0F0283628} 
            Style           =   5
            TextSave        =   "10:30"
         EndProperty
         BeginProperty Panel4 {8E3867AB-8586-11D1-B16A-00C0F0283628} 
            Object.Width           =   2540
            MinWidth        =   2540
            Text            =   "User: Admin"
            TextSave        =   "User: Admin"
         EndProperty
      EndProperty
   End
   Begin MSComctlLib.Toolbar Toolbar1 
      Align           =   1  'Align Top
      Height          =   660
      Left            =   0
      TabIndex        =   0
      Top             =   0
      Width           =   14400
      _ExtentX        =   25400
      _ExtentY        =   1164
      ButtonWidth     =   1032
      ButtonHeight    =   1005
      Appearance      =   1
      Style           =   1
      ImageList       =   "ImageList1"
      _Version        =   393216
      BeginProperty Buttons {66833FE8-8583-11D1-B16A-00C0F0283628} 
         NumButtons      =   8
         BeginProperty Button1 {66833FEA-8583-11D1-B16A-00C0F0283628} 
            Caption         =   "Customer"
            Key             =   "Customer"
            Object.ToolTipText     =   "Customer Management"
            ImageIndex      =   1
         EndProperty
         BeginProperty Button2 {66833FEA-8583-11D1-B16A-00C0F0283628} 
            Caption         =   "Order"
            Key             =   "Order"
            Object.ToolTipText     =   "Order Management"
            ImageIndex      =   2
         EndProperty
         BeginProperty Button3 {66833FEA-8583-11D1-B16A-00C0F0283628} 
            Style           =   3
         EndProperty
         BeginProperty Button4 {66833FEA-8583-11D1-B16A-00C0F0283628} 
            Caption         =   "Report"
            Key             =   "Report"
            Object.ToolTipText     =   "Reports"
            ImageIndex      =   3
         EndProperty
         BeginProperty Button5 {66833FEA-8583-11D1-B16A-00C0F0283628} 
            Style           =   3
         EndProperty
         BeginProperty Button6 {66833FEA-8583-11D1-B16A-00C0F0283628} 
            Caption         =   "Settings"
            Key             =   "Settings"
            Object.ToolTipText     =   "Settings"
            ImageIndex      =   4
         EndProperty
         BeginProperty Button7 {66833FEA-8583-11D1-B16A-00C0F0283628} 
            Style           =   3
         EndProperty
         BeginProperty Button8 {66833FEA-8583-11D1-B16A-00C0F0283628} 
            Caption         =   "Exit"
            Key             =   "Exit"
            Object.ToolTipText     =   "Exit Application"
            ImageIndex      =   5
         EndProperty
      EndProperty
   End
   Begin MSComctlLib.ImageList ImageList1 
      Left            =   13680
      Top             =   720
      _ExtentX        =   1005
      _ExtentY        =   1005
      BackColor       =   -2147483643
      ImageWidth      =   32
      ImageHeight     =   32
      MaskColor       =   12632256
      _Version        =   393216
      BeginProperty Images {2C247F25-8591-11D1-B16A-00C0F0283628} 
         NumListImages   =   5
         BeginProperty ListImage1 {2C247F27-8591-11D1-B16A-00C0F0283628} 
            Picture         =   "frmMain.frx":0000
            Key             =   "Customer"
         EndProperty
         BeginProperty ListImage2 {2C247F27-8591-11D1-B16A-00C0F0283628} 
            Picture         =   "frmMain.frx":031A
            Key             =   "Order"
         EndProperty
         BeginProperty ListImage3 {2C247F27-8591-11D1-B16A-00C0F0283628} 
            Picture         =   "frmMain.frx":0634
            Key             =   "Report"
         EndProperty
         BeginProperty ListImage4 {2C247F27-8591-11D1-B16A-00C0F0283628} 
            Picture         =   "frmMain.frx":094E
            Key             =   "Settings"
         EndProperty
         BeginProperty ListImage5 {2C247F27-8591-11D1-B16A-00C0F0283628} 
            Picture         =   "frmMain.frx":0C68
            Key             =   "Exit"
         EndProperty
      EndProperty
   End
   Begin VB.Menu mnuFile 
      Caption         =   "ファイル(&F)"
      Begin VB.Menu mnuFileNew 
         Caption         =   "新規(&N)"
         Shortcut        =   ^N
      End
      Begin VB.Menu mnuFileOpen 
         Caption         =   "開く(&O)..."
         Shortcut        =   ^O
      End
      Begin VB.Menu mnuFileSave 
         Caption         =   "保存(&S)"
         Shortcut        =   ^S
      End
      Begin VB.Menu mnuFileSep1 
         Caption         =   "-"
      End
      Begin VB.Menu mnuFilePrint 
         Caption         =   "印刷(&P)..."
         Shortcut        =   ^P
      End
      Begin VB.Menu mnuFileSep2 
         Caption         =   "-"
      End
      Begin VB.Menu mnuFileExit 
         Caption         =   "終了(&X)"
      End
   End
   Begin VB.Menu mnuEdit 
      Caption         =   "編集(&E)"
      Begin VB.Menu mnuEditCut 
         Caption         =   "切り取り(&T)"
         Shortcut        =   ^X
      End
      Begin VB.Menu mnuEditCopy 
         Caption         =   "コピー(&C)"
         Shortcut        =   ^C
      End
      Begin VB.Menu mnuEditPaste 
         Caption         =   "貼り付け(&P)"
         Shortcut        =   ^V
      End
   End
   Begin VB.Menu mnuMaster 
      Caption         =   "マスタ(&M)"
      Begin VB.Menu mnuMasterCustomer 
         Caption         =   "顧客管理(&C)"
      End
      Begin VB.Menu mnuMasterProduct 
         Caption         =   "商品管理(&P)"
      End
      Begin VB.Menu mnuMasterEmployee 
         Caption         =   "社員管理(&E)"
      End
   End
   Begin VB.Menu mnuTransaction 
      Caption         =   "取引(&T)"
      Begin VB.Menu mnuTransactionOrder 
         Caption         =   "受注管理(&O)"
      End
      Begin VB.Menu mnuTransactionInvoice 
         Caption         =   "請求管理(&I)"
      End
      Begin VB.Menu mnuTransactionPayment 
         Caption         =   "入金管理(&P)"
      End
   End
   Begin VB.Menu mnuReport 
      Caption         =   "レポート(&R)"
      Begin VB.Menu mnuReportDaily 
         Caption         =   "日次レポート(&D)"
      End
      Begin VB.Menu mnuReportMonthly 
         Caption         =   "月次レポート(&M)"
      End
      Begin VB.Menu mnuReportCustom 
         Caption         =   "カスタムレポート(&C)..."
      End
   End
   Begin VB.Menu mnuWindow 
      Caption         =   "ウィンドウ(&W)"
      WindowList      =   -1  'True
      Begin VB.Menu mnuWindowCascade 
         Caption         =   "重ねて表示(&C)"
      End
      Begin VB.Menu mnuWindowTileHorizontal 
         Caption         =   "上下に並べて表示(&H)"
      End
      Begin VB.Menu mnuWindowTileVertical 
         Caption         =   "左右に並べて表示(&V)"
      End
   End
   Begin VB.Menu mnuHelp 
      Caption         =   "ヘルプ(&H)"
      Begin VB.Menu mnuHelpContents 
         Caption         =   "ヘルプの内容(&C)"
         Shortcut        =   {F1}
      End
      Begin VB.Menu mnuHelpSep1 
         Caption         =   "-"
      End
      Begin VB.Menu mnuHelpAbout 
         Caption         =   "バージョン情報(&A)..."
      End
   End
End
Attribute VB_Name = "frmMain"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
'**********************************************************************
' フォーム名: frmMain
' 説明: MDIメインフォーム
' 作成日: 2025/02/08
' 文字コード: Shift-JIS (必須)
'**********************************************************************

Option Explicit

'**********************************************************************
' フォームイベント
'**********************************************************************
Private Sub MDIForm_Load()
    ' フォーム初期化
    InitializeForm
    
    ' ステータスバー更新
    UpdateStatusBar
End Sub

Private Sub MDIForm_Unload(Cancel As Integer)
    ' 終了確認
    If MsgBox("アプリケーションを終了しますか？", _
              vbQuestion + vbYesNo, App.Title) = vbNo Then
        Cancel = 1
        Exit Sub
    End If
    
    ' アプリケーション終了処理
    TerminateApplication
End Sub

'**********************************************************************
' ツールバーイベント
'**********************************************************************
Private Sub Toolbar1_ButtonClick(ByVal Button As MSComctlLib.Button)
    Select Case Button.Key
        Case "Customer"
            ShowCustomerForm
        Case "Order"
            ShowOrderForm
        Case "Report"
            ShowReportMenu
        Case "Settings"
            ShowSettingsDialog
        Case "Exit"
            mnuFileExit_Click
    End Select
End Sub

'**********************************************************************
' メニューイベント
'**********************************************************************
Private Sub mnuFileExit_Click()
    Unload Me
End Sub

Private Sub mnuMasterCustomer_Click()
    ShowCustomerForm
End Sub

Private Sub mnuTransactionOrder_Click()
    ShowOrderForm
End Sub

Private Sub mnuReportDaily_Click()
    ShowDailyReport
End Sub

Private Sub mnuReportMonthly_Click()
    ShowMonthlyReport
End Sub

Private Sub mnuWindowCascade_Click()
    Me.Arrange vbCascade
End Sub

Private Sub mnuWindowTileHorizontal_Click()
    Me.Arrange vbTileHorizontal
End Sub

Private Sub mnuWindowTileVertical_Click()
    Me.Arrange vbTileVertical
End Sub

Private Sub mnuHelpAbout_Click()
    ShowAboutDialog
End Sub

'**********************************************************************
' プライベートメソッド
'**********************************************************************
Private Sub InitializeForm()
    ' フォームタイトル設定
    Me.Caption = App.Title & " - [" & g_CurrentUser.UserName & "]"
    
    ' メニューの有効/無効設定
    SetMenuSecurity
End Sub

Private Sub UpdateStatusBar()
    ' ステータスバー更新
    StatusBar1.Panels(1).Text = "Ready"
    StatusBar1.Panels(4).Text = "User: " & g_CurrentUser.UserName
End Sub

Private Sub SetMenuSecurity()
    ' ユーザー権限に基づいたメニュー制御
    If g_CurrentUser.UserLevel < 2 Then
        mnuMasterEmployee.Enabled = False
    End If
End Sub

Private Sub ShowCustomerForm()
    Dim frm As frmCustomer
    Set frm = New frmCustomer
    frm.Show
End Sub

Private Sub ShowOrderForm()
    Dim frm As frmOrder
    Set frm = New frmOrder
    frm.Show
End Sub

Private Sub ShowReportMenu()
    ' レポートメニュー表示
    PopupMenu mnuReport
End Sub

Private Sub ShowSettingsDialog()
    ' 設定ダイアログ表示
    MsgBox "設定ダイアログ", vbInformation
End Sub

Private Sub ShowDailyReport()
    Dim frm As frmReport
    Set frm = New frmReport
    frm.ReportType = "Daily"
    frm.Show
End Sub

Private Sub ShowMonthlyReport()
    Dim frm As frmReport
    Set frm = New frmReport
    frm.ReportType = "Monthly"
    frm.Show
End Sub