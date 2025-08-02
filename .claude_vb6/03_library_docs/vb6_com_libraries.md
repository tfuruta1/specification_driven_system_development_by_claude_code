# VB6 COMライブラリ・コンポーネントドキュメント

## 標準COMコンポーネント

### Microsoft Common Controls (MSCOMCTL.OCX)

#### 概要
- **ファイル名**: MSCOMCTL.OCX
- **CLSID**: {831FDD16-0C5C-11D2-A9FC-0000F8754DA1}
- **バージョン**: 6.0 (SP6)
- **用途**: TreeView、ListView、Toolbar、StatusBarなど

#### 主要コントロール
1. **TreeView**: 階層表示
2. **ListView**: 詳細リスト表示
3. **Toolbar**: ツールバー
4. **StatusBar**: ステータスバー
5. **ImageList**: イメージ管理
6. **ProgressBar**: 進捗表示

### Microsoft Common Controls 2 (MSCOMCT2.OCX)

#### 概要
- **ファイル名**: MSCOMCT2.OCX
- **CLSID**: {86CF1D34-0C5F-11D2-A9FC-0000F8754DA1}
- **バージョン**: 6.0
- **用途**: 日付時刻コントロール、アニメーションなど

#### 主要コントロール
1. **DTPicker**: 日付時刻選択
2. **MonthView**: カレンダー表示
3. **UpDown**: 数値増減
4. **Animation**: AVIアニメーション

### Microsoft Common Dialog (COMDLG32.OCX)

#### 概要
- **ファイル名**: COMDLG32.OCX
- **CLSID**: {F9043C88-F6F2-101A-A3C9-08002B2F49FB}
- **バージョン**: 6.0
- **用途**: 標準ダイアログ表示

#### 機能
1. **ShowOpen**: ファイルを開く
2. **ShowSave**: 名前を付けて保存
3. **ShowColor**: 色選択
4. **ShowFont**: フォント選択
5. **ShowPrinter**: 印刷設定

## データアクセスライブラリ

### ADO (ActiveX Data Objects)

#### 概要
- **ファイル名**: msado15.dll (ADO 2.8)
- **参照名**: Microsoft ActiveX Data Objects 2.8 Library
- **用途**: データベースアクセス

#### 主要オブジェクト
```vb
' Connection
Dim conn As ADODB.Connection
Set conn = New ADODB.Connection
conn.ConnectionString = "Provider=SQLOLEDB;..."
conn.Open

' Recordset
Dim rs As ADODB.Recordset
Set rs = New ADODB.Recordset
rs.Open "SELECT * FROM Customers", conn

' Command
Dim cmd As ADODB.Command
Set cmd = New ADODB.Command
cmd.ActiveConnection = conn
cmd.CommandText = "sp_GetCustomers"
cmd.CommandType = adCmdStoredProc
```

### DAO (Data Access Objects)

#### 概要
- **ファイル名**: dao360.dll
- **参照名**: Microsoft DAO 3.6 Object Library
- **用途**: Accessデータベースアクセス

#### 主要オブジェクト
```vb
' Database
Dim db As DAO.Database
Set db = OpenDatabase("C:\Data\MyDB.mdb")

' Recordset
Dim rs As DAO.Recordset
Set rs = db.OpenRecordset("Customers")

' TableDef
Dim td As DAO.TableDef
Set td = db.CreateTableDef("NewTable")
```

## グラフィックス・チャートコンポーネント

### MSChart Control

#### 概要
- **ファイル名**: MSCHRT20.OCX
- **CLSID**: {3A2B370C-BA0A-11D1-B137-0000F8753F5D}
- **用途**: 2D/3Dグラフ表示

#### グラフタイプ
1. 棒グラフ
2. 折れ線グラフ
3. 円グラフ
4. 散布図
5. エリアグラフ

### MSFlexGrid/MSHFlexGrid

#### 概要
- **ファイル名**: MSFLXGRD.OCX / MSHFLXGD.OCX
- **用途**: グリッド表示、階層グリッド

#### 特徴
- セル結合
- ソート機能
- 階層表示（MSHFlexGrid）
- カスタム描画

## ネットワークコンポーネント

### Microsoft Winsock Control

#### 概要
- **ファイル名**: MSWINSCK.OCX
- **CLSID**: {248DD896-BB45-11CF-9ABC-0080C7E7B78D}
- **用途**: TCP/IP通信

#### 使用例
```vb
' TCPサーバー
Private Sub Winsock1_ConnectionRequest(ByVal requestID As Long)
    Winsock1.Close
    Winsock1.Accept requestID
End Sub

' TCPクライアント
Winsock1.Connect "192.168.1.100", 8080
```

### Microsoft Internet Controls

#### 概要
- **ファイル名**: shdocvw.dll
- **参照名**: Microsoft Internet Controls
- **用途**: Webブラウザコントロール

## XML処理ライブラリ

### MSXML

#### 概要
- **ファイル名**: msxml6.dll
- **参照名**: Microsoft XML, v6.0
- **用途**: XML解析、DOM操作、XSLT変換

#### 使用例
```vb
' XML読み込み
Dim xmlDoc As MSXML2.DOMDocument60
Set xmlDoc = New MSXML2.DOMDocument60
xmlDoc.Load "data.xml"

' HTTPリクエスト
Dim xmlHttp As MSXML2.XMLHTTP60
Set xmlHttp = New MSXML2.XMLHTTP60
xmlHttp.Open "GET", "http://api.example.com/data", False
xmlHttp.Send
```

## レポートコンポーネント

### Crystal Reports

#### 概要
- **ファイル名**: crystl32.ocx
- **用途**: 帳票作成・印刷

#### 主要機能
- データベース連携
- パラメータ付きレポート
- エクスポート（PDF、Excel、Word）
- プレビュー機能

## Office連携コンポーネント

### Microsoft Excel Object Library

#### 概要
- **参照名**: Microsoft Excel XX.0 Object Library
- **用途**: Excel自動化

#### 使用例
```vb
Dim xlApp As Excel.Application
Dim xlBook As Excel.Workbook
Dim xlSheet As Excel.Worksheet

Set xlApp = CreateObject("Excel.Application")
Set xlBook = xlApp.Workbooks.Add
Set xlSheet = xlBook.Worksheets(1)

xlSheet.Cells(1, 1).Value = "Hello VB6"
xlApp.Visible = True
```

## セキュリティ関連

### CAPICOM

#### 概要
- **ファイル名**: capicom.dll
- **用途**: 暗号化、デジタル署名、証明書管理

#### 機能
- ハッシュ計算
- 対称暗号化
- デジタル署名
- 証明書ストアアクセス

## サードパーティコンポーネント

### 一般的なサードパーティコンポーネント
1. **ComponentOne**: 高機能グリッド、チャート
2. **Infragistics**: UIコンポーネントスイート
3. **DevExpress**: プロフェッショナルUI
4. **Codejock**: リボンUI、ドッキング
5. **FarPoint Spread**: Excel互換グリッド

### コンポーネント依存関係管理

#### 登録確認スクリプト
```vbscript
' check_components.vbs
On Error Resume Next

Dim components
components = Array( _
    Array("MSCOMCTL.OCX", "{831FDD16-0C5C-11D2-A9FC-0000F8754DA1}"), _
    Array("MSCOMCT2.OCX", "{86CF1D34-0C5F-11D2-A9FC-0000F8754DA1}"), _
    Array("COMDLG32.OCX", "{F9043C88-F6F2-101A-A3C9-08002B2F49FB}") _
)

Dim shell
Set shell = CreateObject("WScript.Shell")

For Each comp In components
    shell.RegRead "HKCR\CLSID\" & comp(1) & "\"
    If Err.Number = 0 Then
        WScript.Echo "[√] " & comp(0) & " is registered"
    Else
        WScript.Echo "[X] " & comp(0) & " is NOT registered"
        Err.Clear
    End If
Next
```

## トラブルシューティング

### 一般的な問題と解決策

| 問題 | 原因 | 解決策 |
|------|------|----------|
| "Component not registered" | OCX/DLL未登録 | regsvr32で登録 |
| "Class not registered" | CLSID登録エラー | レジストリ修復 |
| "Type mismatch" | バージョン不一致 | 正しいバージョンを使用 |
| "Permission denied" | UAC/権限不足 | 管理者権限で実行 |

### コンポーネント登録コマンド
```batch
REM OCX登録
regsvr32 "C:\Windows\System32\MSCOMCTL.OCX"

REM DLL登録
regsvr32 "C:\MyApp\MyCustom.dll"

REM 登録解除
regsvr32 /u "C:\Windows\System32\MSCOMCTL.OCX"
```

## ベストプラクティス

1. **バージョン管理**
   - 使用するコンポーネントのバージョンを文書化
   - バイナリ互換性の確認

2. **依存関係明確化**
   - 必要なコンポーネント一覧の作成
   - インストーラーへの含め方

3. **Registration-Free COM**
   - 可能な限りマニフェストを使用
   - レジストリ依存の削減

4. **エラーハンドリング**
   - CreateObject時のエラー処理
   - 代替コンポーネントの準備