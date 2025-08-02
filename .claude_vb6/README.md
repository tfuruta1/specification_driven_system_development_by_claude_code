# 🔍 Visual Basic 6.0 レガシーシステム解析・移行・開発プロジェクト

**エンタープライズVB6システムの解析・保守・開発・.NET移行支援統合プラットフォーム**

## 📋 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [技術スタック](#技術スタック)
3. [プロジェクト構造](#プロジェクト構造)
4. [開発環境セットアップ](#開発環境セットアップ)
5. [アーキテクチャパターン](#アーキテクチャパターン)
6. [開発ワークフロー](#開発ワークフロー)
7. [ベストプラクティス](#ベストプラクティス)
8. [デプロイメント戦略](#デプロイメント戦略)

## 🎯 プロジェクト概要

このプロジェクトは、Visual Basic 6.0を使用したエンタープライズレガシーシステムの包括的な開発・保守・移行支援プラットフォームです。既存VB6資産の最大活用と、段階的な.NET Framework 4.8への移行を支援します。

### 主要機能

#### 開発支援
- **新規VB6アプリケーション開発**: エンタープライズ業務システム構築
- **3層アーキテクチャ**: UI層・ビジネスロジック層・データアクセス層
- **デザインパターン適用**: MVP、Factory、Singletonパターン
- **統合開発環境**: Visual Studio 6.0 Enterprise Edition対応

#### 解析・保守
- **コード解析**: 依存関係分析、複雑度測定、技術的負債評価
- **安全な修正**: 影響範囲分析、自動テスト生成、リグレッション防止
- **パフォーマンス最適化**: ボトルネック特定、メモリリーク修正
- **ドキュメント生成**: 自動API文書化、設計書逆生成

#### 移行支援
- **.NET Framework 4.8移行**: 段階的移行戦略、並行実行環境
- **COM相互運用**: 既存COM資産の活用、ラッパー生成
- **データベース移行**: ADO→ADO.NET、ストアドプロシージャ移行
- **UI近代化**: Windows Forms移行、WPF統合オプション

## 🏗️ 技術スタック

### VB6開発環境
```
開発環境: Visual Basic 6.0 Enterprise Edition (SP6)
ランタイム: VB6 Runtime SP6
言語仕様: Visual Basic 6.0
文字コード: Shift-JIS (SJIS) ※必須
IDE: Visual Studio 6.0 Enterprise
```

### アーキテクチャコンポーネント
```
UIフレームワーク: Windows Forms (VB6 Native)
データアクセス: ADO 2.8 / DAO 3.6 / RDO 2.0
レポート: Crystal Reports 8.5 / Active Reports 2.0
通信: DCOM / Windows Sockets (Winsock)
COM/ActiveX: Microsoft Common Controls 6.0 (SP6)
```

### データベース対応
```
プライマリ: SQL Server 2000/2005/2008
セカンダリ: Oracle 10g/11g
ローカル: Microsoft Access 2003/2007
レガシー: AS/400 (ODBC接続)
```

### 開発ツール・ライブラリ
```
バージョン管理: Visual SourceSafe 6.0 / Git (移行推奨)
ビルドツール: VB6 Command Line Compiler
テストツール: VB6 Testing Framework (自社開発)
静的解析: Code Advisor for Visual Basic 6
パッケージング: Package & Deployment Wizard
インストーラー: InstallShield Express / Wise Installation System
```

## 📁 プロジェクト構造

```
.claude_vb6/
├── README.md                        # プロジェクト概要（このファイル）
├── CLAUDE.md                        # マルチAI協調ガイド
├── commands/                        # カスタムコマンド（24個）
│   └── custom_commands.json         # コマンド定義
├── 00_project/                      # プロジェクト設計ドキュメント
│   ├── 01_project_concept.md        # プロジェクトコンセプト
│   ├── 02_vb6_architecture.md       # VB6アーキテクチャ設計
│   └── 03_migration_strategy.md     # 移行戦略ドキュメント
├── 01_analysis_docs/                # 解析ドキュメント
│   ├── code_analysis_guide.md       # コード解析ガイド
│   ├── dependency_mapping.md        # 依存関係マッピング
│   ├── risk_assessment_template.md  # リスク評価テンプレート
│   └── vb6_encoding_guide.md        # SJIS文字コードガイド
├── 02_maintenance_docs/             # 保守ドキュメント
│   ├── safe_modification_guide.md   # 安全な修正ガイド
│   ├── testing_strategy.md          # テスト戦略
│   ├── troubleshooting_guide.md    # トラブルシューティング
│   └── compile_troubleshooting_guide.md # コンパイルエラー対応
├── 03_migration_docs/               # 移行ドキュメント
│   ├── migration_patterns.md        # 移行パターン集
│   ├── dotnet48_mapping.md         # .NET 4.8マッピング
│   └── compatibility_matrix.md     # 互換性マトリクス
├── src/                            # ソースコード
│   ├── LegacyBusinessApp/          # メインアプリケーション
│   │   ├── LegacyBusinessApp.vbp   # プロジェクトファイル
│   │   ├── LegacyBusinessApp.vbg   # プロジェクトグループ
│   │   └── Forms/                  # フォーム
│   │       ├── frmMain.frm         # メインフォーム
│   │       ├── frmCustomer.frm     # 顧客管理フォーム
│   │       └── frmReport.frm       # レポートフォーム
│   ├── Common/                     # 共通モジュール
│   │   ├── modGlobal.bas          # グローバル変数・定数
│   │   ├── modUtility.bas         # ユーティリティ関数
│   │   ├── modError.bas           # エラーハンドリング
│   │   └── modLogging.bas         # ログ機能
│   ├── DataAccess/                # データアクセス層
│   │   ├── clsDatabase.cls        # データベース接続クラス
│   │   ├── clsCustomerDAO.cls     # 顧客DAOクラス
│   │   └── clsOrderDAO.cls        # 注文DAOクラス
│   ├── BusinessLogic/             # ビジネスロジック層
│   │   ├── clsCustomerBL.cls      # 顧客ビジネスロジック
│   │   ├── clsOrderBL.cls         # 注文ビジネスロジック
│   │   └── clsValidation.cls      # 検証ロジック
│   ├── UI/                        # UIコンポーネント
│   │   ├── ctlCustomGrid.ctl      # カスタムグリッドコントロール
│   │   ├── ctlDatePicker.ctl      # 日付選択コントロール
│   │   └── ctlSearchBox.ctl       # 検索ボックスコントロール
│   └── Reports/                   # レポート
│       ├── rptCustomerList.dsr    # 顧客一覧レポート
│       └── rptMonthlyReport.dsr   # 月次レポート
├── samples/                       # サンプルコード
│   ├── BasicPatterns/             # 基本パターン
│   ├── DatabaseAccess/            # データベースアクセス
│   ├── ErrorHandling/             # エラーハンドリング
│   └── COMIntegration/            # COM統合
├── tests/                         # テストプロジェクト
│   ├── UnitTests/                 # 単体テスト
│   ├── IntegrationTests/          # 統合テスト
│   └── TestData/                  # テストデータ
├── deployment/                    # デプロイメント
│   ├── installer/                 # インストーラー設定
│   │   ├── setup.iss             # Inno Setupスクリプト
│   │   └── dependencies.txt      # 依存関係リスト
│   ├── runtime/                  # ランタイム配布
│   │   └── vb6runtime_sp6.exe   # VB6ランタイム
│   └── dependencies/             # 依存ファイル
│       ├── MDAC_2.8.exe         # Microsoft Data Access Components
│       └── mscomctl.ocx         # Common Controls
├── docs/                         # プロジェクトドキュメント
│   ├── UserManual.doc           # ユーザーマニュアル
│   ├── DeveloperGuide.doc       # 開発者ガイド
│   └── APIReference.doc         # APIリファレンス
├── analysis_tools/              # 解析ツール
│   ├── vb6_parser/             # VB6パーサー
│   ├── dependency_analyzer/     # 依存関係分析
│   └── metrics_calculator/      # メトリクス計算
└── migration_tools/            # 移行ツール
    ├── code_converter/         # コード変換ツール
    ├── test_generator/         # テスト生成ツール
    └── validation_suite/       # 検証スイート
```

## 🚀 開発環境セットアップ

### 必須環境
```
OS: Windows 10/11 (32bit/64bit)
IDE: Visual Basic 6.0 Enterprise Edition SP6
.NET: .NET Framework 4.8 (移行時)
RAM: 4GB以上推奨
HDD: 2GB以上の空き容量
```

### セットアップ手順

1. **Visual Basic 6.0のインストール**
```cmd
# Visual Studio 6.0 Enterprise Editionをインストール
# Service Pack 6を適用
# KB2708437セキュリティ更新プログラムを適用
```

2. **必須コンポーネントの登録**
```cmd
# 管理者権限で実行
regsvr32 "C:\Windows\System32\MSCOMCTL.OCX"
regsvr32 "C:\Windows\System32\MSCOMCT2.OCX"
regsvr32 "C:\Windows\System32\MSDATGRD.OCX"
```

3. **開発環境の設定**
```
# VB6 IDEの設定
ツール → オプション
- エディタ: 「変数の宣言を強制する」をチェック
- エディタ形式: タブサイズ 4、インデント 4
- 全般: 「エラー発生時に中断」を選択
```

## 🏛️ アーキテクチャパターン

### 3層アーキテクチャ
```vb
' プレゼンテーション層 (Forms)
Private Sub cmdSave_Click()
    Dim objBL As clsCustomerBL
    Set objBL = New clsCustomerBL
    
    If objBL.SaveCustomer(txtName.Text, txtEmail.Text) Then
        MsgBox "保存しました", vbInformation
    End If
    
    Set objBL = Nothing
End Sub

' ビジネスロジック層 (Classes)
Public Function SaveCustomer(ByVal Name As String, _
                           ByVal Email As String) As Boolean
    Dim objDAO As clsCustomerDAO
    Set objDAO = New clsCustomerDAO
    
    ' ビジネスルールの検証
    If Not IsValidEmail(Email) Then
        Err.Raise vbObjectError + 1001, , "メールアドレスが無効です"
    End If
    
    SaveCustomer = objDAO.Insert(Name, Email)
    Set objDAO = Nothing
End Function

' データアクセス層 (Classes)
Public Function Insert(ByVal Name As String, _
                      ByVal Email As String) As Boolean
    Dim cmd As ADODB.Command
    Set cmd = New ADODB.Command
    
    With cmd
        .ActiveConnection = GetConnection()
        .CommandText = "sp_InsertCustomer"
        .CommandType = adCmdStoredProc
        .Parameters.Append .CreateParameter("@Name", adVarChar, adParamInput, 50, Name)
        .Parameters.Append .CreateParameter("@Email", adVarChar, adParamInput, 100, Email)
        .Execute
    End With
    
    Insert = True
    Set cmd = Nothing
End Function
```

### MVPパターン実装
```vb
' View Interface
Public Interface ICustomerView
    Property Get CustomerName() As String
    Property Let CustomerName(ByVal Value As String)
    Property Get Email() As String
    Property Let Email(ByVal Value As String)
    Sub ShowMessage(ByVal Message As String)
    Sub ShowError(ByVal ErrorMessage As String)
End Interface

' Presenter
Private mView As ICustomerView
Private mModel As clsCustomerModel

Public Sub Initialize(View As ICustomerView)
    Set mView = View
    Set mModel = New clsCustomerModel
End Sub

Public Sub SaveCustomer()
    On Error GoTo ErrorHandler
    
    If mModel.Save(mView.CustomerName, mView.Email) Then
        mView.ShowMessage "保存完了"
    End If
    Exit Sub
    
ErrorHandler:
    mView.ShowError Err.Description
End Sub
```

## 🔄 開発ワークフロー

### 新規開発フロー
```bash
# 1. プロジェクト初期化
/vb6-project-init "MyEnterpriseApp"

# 2. アーキテクチャ設計
/vb6-architecture --pattern="3-tier"

# 3. データベース設計
/vb6-database-design --target="SQLServer2005"

# 4. コード生成
/vb6-generate-code --layer="all"

# 5. テスト実装
/vb6-test-implementation --coverage=80
```

### 保守・改修フロー
```bash
# 1. 影響範囲分析
/analyze-vb6-code "C:\LegacyApp" --deep-scan

# 2. 修正計画
/fix-vb6 --analyze-impact "変更内容"

# 3. テスト生成
/vb6-generate-tests --type="regression"

# 4. 安全な実装
/vb6-safe-modify --backup --test
```

## 📋 ベストプラクティス

### コーディング規約
```vb
' ファイルヘッダー（必須）
'**********************************************************************
' モジュール名: modCustomer
' 説明: 顧客関連の共通処理
' 作成者: 開発チーム
' 作成日: 2025/02/08
' 更新履歴:
'   2025/02/08 - 初版作成
'**********************************************************************

Option Explicit  ' 必須：変数宣言を強制

' 定数定義（大文字、アンダースコア区切り）
Private Const MAX_RETRY_COUNT As Integer = 3
Private Const CONNECTION_TIMEOUT As Integer = 30

' 変数命名規則
' - ローカル変数: キャメルケース (customerName)
' - モジュール変数: m_プレフィックス (m_CustomerList)
' - グローバル変数: g_プレフィックス (g_CurrentUser)
' - 定数: 大文字スネークケース (MAX_LENGTH)

' 関数命名規則
' - Public関数: パスカルケース (GetCustomerName)
' - Private関数: パスカルケース (ValidateInput)
' - イベントハンドラ: オブジェクト名_イベント名 (cmdSave_Click)
```

### エラーハンドリング標準
```vb
Public Function ProcessOrder(ByVal OrderID As Long) As Boolean
    On Error GoTo ErrorHandler
    
    ' ローカル変数宣言
    Dim conn As ADODB.Connection
    Dim isInTransaction As Boolean
    
    ' 初期化
    ProcessOrder = False
    isInTransaction = False
    
    ' メイン処理
    Set conn = GetConnection()
    conn.BeginTrans
    isInTransaction = True
    
    ' ビジネスロジック実行
    ' ...
    
    ' 正常終了
    conn.CommitTrans
    ProcessOrder = True
    
CleanUp:
    ' リソース解放
    If Not conn Is Nothing Then
        If isInTransaction Then conn.RollbackTrans
        If conn.State = adStateOpen Then conn.Close
        Set conn = Nothing
    End If
    Exit Function
    
ErrorHandler:
    ' エラーログ記録
    LogError "ProcessOrder", Err.Number, Err.Description
    
    ' ユーザー通知
    Select Case Err.Number
        Case -2147217843  ' ログイン失敗
            MsgBox "データベース接続に失敗しました", vbCritical
        Case Else
            MsgBox "エラーが発生しました: " & Err.Description, vbCritical
    End Select
    
    Resume CleanUp
End Function
```

### パフォーマンス最適化
```vb
' ❌ 悪い例：繰り返しのデータベースアクセス
For i = 1 To 1000
    Set rs = conn.Execute("SELECT * FROM Customers WHERE ID = " & i)
    ' 処理...
Next

' ✅ 良い例：一括取得
Set rs = conn.Execute("SELECT * FROM Customers WHERE ID BETWEEN 1 AND 1000")
Do While Not rs.EOF
    ' 処理...
    rs.MoveNext
Loop

' ❌ 悪い例：文字列連結の繰り返し
Dim result As String
For i = 1 To 10000
    result = result & GetData(i) & vbCrLf
Next

' ✅ 良い例：配列を使用
Dim arr() As String
ReDim arr(10000)
For i = 1 To 10000
    arr(i) = GetData(i)
Next
result = Join(arr, vbCrLf)
```

## 🚀 デプロイメント戦略

### パッケージング
```ini
; Package & Deployment Wizard設定
[Setup]
Title=Legacy Business Application
Version=1.0.0
DefaultDir=$(ProgramFiles)\LegacyApp
Compress=Yes

[Files]
; 実行ファイル
File1=LegacyBusinessApp.exe
; 依存DLL
File2=MSVBVM60.DLL
File3=MSCOMCTL.OCX
; 設定ファイル
File4=Config.ini
```

### インストーラー作成（Inno Setup）
```pascal
[Setup]
AppName=Legacy Business Application
AppVersion=1.0
DefaultDirName={pf}\LegacyBusinessApp
DefaultGroupName=Legacy Business App
Compression=lzma
SolidCompression=yes
; Windows XP以降をサポート
MinVersion=5.1

[Files]
Source: "LegacyBusinessApp.exe"; DestDir: "{app}"
Source: "*.dll"; DestDir: "{app}"
Source: "*.ocx"; DestDir: "{sys}"; Flags: regserver

[Registry]
; COMコンポーネント登録
Root: HKCR; Subkey: "CLSID\{{GUID}}"; ValueType: string; ValueName: ""; ValueData: "MyComponent"

[Run]
; VB6ランタイムインストール
Filename: "{app}\vb6runtime_sp6.exe"; Parameters: "/q"; StatusMsg: "VB6ランタイムをインストール中..."
```

### CI/CD パイプライン
```yaml
# GitHub Actions設定例
name: VB6 Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup VB6
      run: |
        # VB6コンパイラのセットアップ
        choco install vb6 -y
        
    - name: Compile VB6
      run: |
        "C:\Program Files (x86)\Microsoft Visual Studio\VB98\VB6.EXE" /make "src\LegacyBusinessApp\LegacyBusinessApp.vbp" /out build.log
        
    - name: Run Tests
      run: |
        # VB6テストの実行
        .\tests\run_tests.bat
        
    - name: Create Installer
      run: |
        # Inno Setupでインストーラー作成
        iscc deployment\installer\setup.iss
        
    - name: Upload Artifacts
      uses: actions/upload-artifact@v2
      with:
        name: installer
        path: Output\*.exe
```

---

このREADMEは、VB6プロジェクトの包括的なガイドとして、開発から保守、移行まですべてのフェーズをカバーしています。