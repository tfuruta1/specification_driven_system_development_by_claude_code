# VB6 安全な修正ガイド

## 1. 修正前の必須確認事項

### 1.1 影響範囲分析チェックリスト
```
□ 修正対象の識別
  □ ファイル名とパス
  □ プロシージャ/関数名
  □ 行番号範囲
  
□ 依存関係の確認
  □ 呼び出し元の特定
  □ 参照されているグローバル変数
  □ 使用されているCOMオブジェクト
  
□ データフローの理解
  □ 入力パラメータ
  □ 戻り値
  □ 副作用（DB更新、ファイル出力等）
```

### 1.2 バックアップ戦略
```batch
REM 修正前の自動バックアップスクリプト
@echo off
set PROJECT_PATH=C:\VB6Projects\MyApp
set BACKUP_PATH=C:\VB6Backup\MyApp_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%

xcopy "%PROJECT_PATH%" "%BACKUP_PATH%" /E /I /H /Y
echo Backup completed: %BACKUP_PATH%
```

## 2. 一般的な修正パターンと注意点

### 2.1 変数型の変更
```vb
' ❌ 危険な変更例
' 変更前
Dim customerID As Long

' 変更後（影響大）
Dim customerID As String  ' データベースや他のモジュールとの不整合リスク

' ✅ 安全な変更アプローチ
' 1. 新しい変数を追加
Dim customerID As Long        ' 既存
Dim customerIDStr As String   ' 新規

' 2. 段階的に移行
customerIDStr = CStr(customerID)

' 3. 十分なテスト後、古い変数を削除
```

### 2.2 エラーハンドリングの追加
```vb
' ❌ 既存ロジックを破壊する例
Public Function CalculatePrice(ByVal quantity As Long, ByVal unitPrice As Currency) As Currency
    On Error GoTo ErrorHandler  ' 追加
    
    ' 既存のOn Error Resume Nextに依存したコード
    On Error Resume Next
    Dim discount As Currency
    discount = GetDiscount()  ' エラーの場合0を期待
    
    CalculatePrice = quantity * unitPrice * (1 - discount)
    Exit Function
    
ErrorHandler:
    ' 新しいエラーハンドリング
    CalculatePrice = 0
End Function

' ✅ 安全な追加方法
Public Function CalculatePrice(ByVal quantity As Long, ByVal unitPrice As Currency) As Currency
    Dim discount As Currency
    
    ' 局所的なエラーハンドリング
    On Error Resume Next
    discount = GetDiscount()
    If Err.Number <> 0 Then
        discount = 0
        Err.Clear
    End If
    On Error GoTo 0  ' エラーハンドリングをリセット
    
    ' 全体のエラーハンドリング
    On Error GoTo ErrorHandler
    CalculatePrice = quantity * unitPrice * (1 - discount)
    Exit Function
    
ErrorHandler:
    LogError "CalculatePrice", Err.Number, Err.Description
    CalculatePrice = 0
End Function
```

### 2.3 グローバル変数の削減
```vb
' ❌ 危険なリファクタリング
' 変更前（多くの場所で使用）
Public g_CurrentUserID As Long

' 単純に削除すると全体が動作しなくなる

' ✅ 段階的な削減アプローチ
' Step 1: ラッパー関数の作成
Public Function GetCurrentUserID() As Long
    GetCurrentUserID = g_CurrentUserID
End Function

Public Sub SetCurrentUserID(ByVal userID As Long)
    g_CurrentUserID = userID
End Sub

' Step 2: 直接参照を関数呼び出しに置換
' Before: If g_CurrentUserID = 0 Then
' After:  If GetCurrentUserID() = 0 Then

' Step 3: 最終的にクラスベースに移行
' UserSession.cls
Private m_UserID As Long

Public Property Get UserID() As Long
    UserID = m_UserID
End Property

Public Property Let UserID(ByVal value As Long)
    m_UserID = value
End Property
```

## 3. パフォーマンス改善の安全な実施

### 3.1 データベースアクセスの最適化
```vb
' ❌ リスクのある最適化
' 変更前
Dim rs As ADODB.Recordset
Set rs = conn.Execute("SELECT * FROM Customers")
Do While Not rs.EOF
    ProcessCustomer rs
    rs.MoveNext
Loop

' 変更後（メモリ不足のリスク）
Dim customers() As Customer
customers = LoadAllCustomers()  ' 大量データでメモリ不足

' ✅ 安全な最適化
' バッチ処理の導入
Const BATCH_SIZE As Long = 1000
Dim offset As Long
Dim rs As ADODB.Recordset

Do
    Set rs = conn.Execute("SELECT * FROM Customers " & _
                         "ORDER BY CustomerID " & _
                         "OFFSET " & offset & " ROWS " & _
                         "FETCH NEXT " & BATCH_SIZE & " ROWS ONLY")
    
    If rs.EOF Then Exit Do
    
    Do While Not rs.EOF
        ProcessCustomer rs
        rs.MoveNext
    Loop
    
    offset = offset + BATCH_SIZE
    rs.Close
    DoEvents  ' UIの応答性維持
Loop
```

### 3.2 文字列処理の最適化
```vb
' ❌ 互換性を破壊する変更
' 変更前（遅いが安定）
Dim result As String
For i = 1 To 10000
    result = result & GetData(i) & vbCrLf
Next

' 変更後（高速だが環境依存）
Dim sb As StringBuilder  ' .NET参照が必要

' ✅ VB6ネイティブな最適化
' 配列を使用した高速化
Dim parts() As String
ReDim parts(10000)

For i = 1 To 10000
    parts(i) = GetData(i)
Next

Dim result As String
result = Join(parts, vbCrLf)
```

## 4. COM/ActiveX関連の修正

### 4.1 遅延バインディングから事前バインディングへ
```vb
' ❌ エラーを見逃しやすい変更
' 変更前（遅延バインディング）
Dim obj As Object
Set obj = CreateObject("Excel.Application")
obj.Visible = True

' 変更後（参照設定忘れでエラー）
Dim xlApp As Excel.Application
Set xlApp = New Excel.Application

' ✅ 安全な移行方法
' 条件付きコンパイルを使用
#Const USE_EARLY_BINDING = True

#If USE_EARLY_BINDING Then
    Dim xlApp As Excel.Application
    Set xlApp = New Excel.Application
#Else
    Dim xlApp As Object
    Set xlApp = CreateObject("Excel.Application")
#End If

xlApp.Visible = True
```

### 4.2 COMオブジェクトの解放
```vb
' ✅ 確実な解放パターン
Public Sub SafeExcelOperation()
    Dim xlApp As Excel.Application
    Dim xlBook As Excel.Workbook
    Dim xlSheet As Excel.Worksheet
    
    On Error GoTo Cleanup
    
    Set xlApp = New Excel.Application
    Set xlBook = xlApp.Workbooks.Add
    Set xlSheet = xlBook.Worksheets(1)
    
    ' 処理実行
    xlSheet.Cells(1, 1).Value = "Hello"
    
Cleanup:
    ' 逆順で解放
    If Not xlSheet Is Nothing Then Set xlSheet = Nothing
    If Not xlBook Is Nothing Then
        xlBook.Close SaveChanges:=False
        Set xlBook = Nothing
    End If
    If Not xlApp Is Nothing Then
        xlApp.Quit
        Set xlApp = Nothing
    End If
    
    ' エラーがあれば再発生
    If Err.Number <> 0 Then
        Err.Raise Err.Number, Err.Source, Err.Description
    End If
End Sub
```

## 5. テスト駆動修正アプローチ

### 5.1 修正前のテストケース作成
```vb
' TestCustomerModule.bas
Public Sub TestCustomerValidation()
    Dim testsPassed As Long
    Dim testsFailed As Long
    
    ' テスト1: 正常系
    If ValidateCustomer("John Doe", "john@example.com") = True Then
        testsPassed = testsPassed + 1
    Else
        testsFailed = testsFailed + 1
        Debug.Print "Test 1 Failed: Normal case"
    End If
    
    ' テスト2: 空の名前
    If ValidateCustomer("", "john@example.com") = False Then
        testsPassed = testsPassed + 1
    Else
        testsFailed = testsFailed + 1
        Debug.Print "Test 2 Failed: Empty name"
    End If
    
    ' テスト3: 無効なメール
    If ValidateCustomer("John Doe", "invalid-email") = False Then
        testsPassed = testsPassed + 1
    Else
        testsFailed = testsFailed + 1
        Debug.Print "Test 3 Failed: Invalid email"
    End If
    
    Debug.Print "Tests Passed: " & testsPassed & "/" & (testsPassed + testsFailed)
End Sub
```

### 5.2 リグレッションテストの自動化
```vb
' RegressionTest.cls
Private Type TestResult
    TestName As String
    Expected As Variant
    Actual As Variant
    Passed As Boolean
End Type

Private m_Results() As TestResult
Private m_TestCount As Long

Public Sub RunAllTests()
    ReDim m_Results(0)
    m_TestCount = 0
    
    ' 各モジュールのテスト実行
    TestCustomerModule
    TestOrderModule
    TestInventoryModule
    
    ' レポート生成
    GenerateReport
End Sub

Private Sub AddTestResult(ByVal testName As String, _
                         ByVal expected As Variant, _
                         ByVal actual As Variant)
    m_TestCount = m_TestCount + 1
    ReDim Preserve m_Results(m_TestCount)
    
    With m_Results(m_TestCount)
        .TestName = testName
        .Expected = expected
        .Actual = actual
        .Passed = (expected = actual)
    End With
End Sub
```

## 6. 修正後の検証手順

### 6.1 機能検証チェックリスト
```
□ 単体テスト
  □ 修正箇所の直接テスト
  □ 境界値テスト
  □ エラーケーステスト
  
□ 統合テスト
  □ 呼び出し元からのテスト
  □ データフロー全体のテスト
  □ UIからの操作テスト
  
□ 性能テスト
  □ 処理時間の計測
  □ メモリ使用量の確認
  □ 大量データでのテスト
```

### 6.2 ロールバック手順
```vb
' ロールバック用スクリプト
Public Sub RollbackChanges(ByVal backupPath As String)
    On Error GoTo ErrorHandler
    
    ' 1. 現在のファイルを一時保存
    Dim tempPath As String
    tempPath = App.Path & "\Temp_" & Format(Now, "yyyymmddhhnnss")
    CreateFolder tempPath
    CopyProjectFiles App.Path, tempPath
    
    ' 2. バックアップから復元
    CopyProjectFiles backupPath, App.Path
    
    MsgBox "ロールバック完了。元のファイルは " & tempPath & " に保存されています。"
    Exit Sub
    
ErrorHandler:
    MsgBox "ロールバック失敗: " & Err.Description, vbCritical
End Sub
```

## 7. よくあるトラブルと対処法

### 7.1 修正後の不具合パターン

| 症状 | 原因 | 対処法 |
|------|------|--------|
| 型の不一致エラー | Variant型の暗黙変換に依存 | 明示的な型変換を追加 |
| オブジェクトエラー | Nothing チェック漏れ | Is Nothing チェックを追加 |
| 無限ループ | DoEvents削除による影響 | 適切な位置にDoEvents復活 |
| メモリリーク | オブジェクト解放漏れ | Set = Nothing を確認 |

### 7.2 緊急時の対応手順
1. **即座に元に戻す**
2. **エラーログを収集**
3. **最小限の修正で再試行**
4. **段階的なリリース**

この安全な修正ガイドに従うことで、VB6レガシーシステムの保守作業におけるリスクを最小限に抑え、安定性を保ちながら必要な改善を実施できます。