# VB6 コード解析ガイド

## 1. 静的コード解析の重要性

既存VB6システムの保守・移行において、コードの現状を正確に把握することが成功の鍵となります。本ガイドでは、VB6コードの体系的な解析手法を解説します。

## 2. 解析項目と評価基準

### 2.1 コード複雑度メトリクス

#### 循環的複雑度（Cyclomatic Complexity）
```vb
' 複雑度が高い例（複雑度: 11）
Public Function ProcessOrder(ByVal orderType As String, ByVal amount As Currency) As Boolean
    If orderType = "NORMAL" Then
        If amount > 10000 Then
            If CheckCredit() Then
                If CheckStock() Then
                    ' 処理...
                Else
                    ' エラー処理
                End If
            Else
                ' エラー処理
            End If
        Else
            ' 通常処理
        End If
    ElseIf orderType = "EXPRESS" Then
        ' 急送処理
    ElseIf orderType = "SPECIAL" Then
        ' 特別処理
    End If
End Function
```

**評価基準:**
- 1-10: 良好（テスト容易）
- 11-20: 要注意（リファクタリング検討）
- 21以上: 危険（分割必須）

#### ネストレベル
```vb
' ネストが深い例（レベル: 5）
For i = 1 To 100
    If condition1 Then
        For j = 1 To 50
            If condition2 Then
                Do While condition3
                    ' 処理
                Loop
            End If
        Next j
    End If
Next i
```

**評価基準:**
- 1-3: 良好
- 4-5: 要注意
- 6以上: 危険

### 2.2 技術的負債の測定

#### グローバル変数の使用
```vb
' アンチパターン例
Public g_UserName As String
Public g_ConnectionString As String
Public g_CurrentRecord As Long
Public g_TempData() As Variant
```

**リスク評価:**
- 状態管理の複雑化
- テスト困難性の増大
- 並行処理での問題

#### GoTo文の使用
```vb
' レガシーコードでよく見られるパターン
Sub OldStyleErrorHandling()
    On Error GoTo ErrorHandler
    
    GoTo SkipInit  ' 悪い例
    
Initialize:
    ' 初期化処理
    
SkipInit:
    ' メイン処理
    GoTo Cleanup   ' 悪い例
    
ErrorHandler:
    ' エラー処理
    Resume Cleanup
    
Cleanup:
    ' クリーンアップ
End Sub
```

### 2.3 依存関係の複雑さ

#### 循環参照の検出
```
ProjectA.vbp
  └─> References: ProjectB.dll
  
ProjectB.vbp
  └─> References: ProjectA.dll  ← 循環参照！
```

#### 外部依存の評価
```
高リスク依存:
- 廃止されたOCX/DLL
- ベンダー固有のコンポーネント
- 32ビット限定のCOM

中リスク依存:
- Microsoft標準OCX
- Windows API

低リスク依存:
- VB6標準機能のみ
```

## 3. 解析ツールの実装

### 3.1 基本的なコードパーサー
```vb
' VB6CodeAnalyzer.cls
Public Function AnalyzeComplexity(ByVal codeFile As String) As ComplexityReport
    Dim lines() As String
    Dim complexity As Long
    Dim nestLevel As Long
    Dim maxNestLevel As Long
    
    lines = ReadFileLines(codeFile)
    
    For Each line In lines
        ' If文の検出
        If InStr(line, "If ") > 0 And InStr(line, "Then") > 0 Then
            complexity = complexity + 1
            nestLevel = nestLevel + 1
            If nestLevel > maxNestLevel Then maxNestLevel = nestLevel
        End If
        
        ' ElseIf文の検出
        If InStr(line, "ElseIf ") > 0 Then
            complexity = complexity + 1
        End If
        
        ' ループの検出
        If InStr(line, "For ") > 0 Or InStr(line, "Do ") > 0 Or InStr(line, "While ") > 0 Then
            complexity = complexity + 1
            nestLevel = nestLevel + 1
            If nestLevel > maxNestLevel Then maxNestLevel = nestLevel
        End If
        
        ' End文でネストレベル減少
        If InStr(line, "End If") > 0 Or InStr(line, "Next") > 0 Or InStr(line, "Loop") > 0 Then
            nestLevel = nestLevel - 1
        End If
    Next
    
    ' レポート生成
    Set AnalyzeComplexity = CreateReport(complexity, maxNestLevel)
End Function
```

### 3.2 グローバル変数検出器
```vb
Public Function FindGlobalVariables(ByVal projectPath As String) As Collection
    Dim globals As New Collection
    Dim modules As Collection
    Dim line As String
    
    Set modules = GetProjectModules(projectPath)
    
    For Each module In modules
        Dim lines() As String
        lines = ReadFileLines(module)
        
        For Each line In lines
            ' Public変数の検出
            If InStr(line, "Public ") > 0 And _
               (InStr(line, " As ") > 0 Or InStr(line, "()") > 0) Then
                globals.Add ExtractVariableName(line)
            End If
            
            ' Global変数の検出（古い構文）
            If InStr(line, "Global ") > 0 And InStr(line, " As ") > 0 Then
                globals.Add ExtractVariableName(line)
            End If
        Next
    Next
    
    Set FindGlobalVariables = globals
End Function
```

## 4. 移行可能性評価

### 4.1 自動移行可能なパターン
```vb
' ✅ 簡単に移行可能
Dim customerName As String
customerName = "John Doe"

' ✅ 標準的なループ
For i = 1 To 10
    Debug.Print i
Next i

' ✅ 基本的なエラーハンドリング
On Error Resume Next
```

### 4.2 手動対応が必要なパターン
```vb
' ❌ コントロール配列
Private Sub cmdButton_Click(Index As Integer)
    Select Case Index
        Case 0: ' 処理1
        Case 1: ' 処理2
    End Select
End Sub

' ❌ GoSub/Return
GoSub ProcessData
Exit Sub
ProcessData:
    ' 処理
Return

' ❌ Variant型の暗黙的な型変換
Dim value As Variant
value = "123"
value = value + 456  ' 文字列→数値の暗黙変換
```

### 4.3 移行リスク評価マトリクス

| 要素 | 低リスク | 中リスク | 高リスク |
|------|----------|----------|----------|
| データ型 | 基本型のみ | Variant使用 | 大量のVariant |
| エラー処理 | 構造化 | On Error Resume Next | GoTo多用 |
| API使用 | なし | 標準API | カスタムAPI |
| COM依存 | なし | MS標準 | サードパーティ |
| UI | 単純Form | 複雑レイアウト | カスタム描画 |

## 5. 解析レポートのテンプレート

### 5.1 エグゼクティブサマリー
```
プロジェクト: SalesManagement.vbp
解析日: 2024/01/15
総ライン数: 45,230
モジュール数: 156
フォーム数: 42

【品質スコア】
- コード品質: C (要改善)
- 保守性: D (困難)
- 移行容易性: B (中程度)

【主要リスク】
1. グローバル変数の過度な使用（234個）
2. 高複雑度メソッド（15個が複雑度20以上）
3. 廃止予定COMコンポーネント依存（3個）
```

### 5.2 詳細分析結果
```
【複雑度TOP 10】
1. ProcessMonthlyBatch() - 複雑度: 42
2. CalculateCommission() - 複雑度: 35
3. ValidateOrderData() - 複雑度: 28
...

【グローバル変数使用箇所】
- g_UserID: 145箇所
- g_ConnectionString: 89箇所
- g_TempArray(): 67箇所
...

【移行難易度評価】
- 自動移行可能: 65%
- 要手動修正: 25%
- 再設計必要: 10%
```

## 6. 解析結果に基づく改善提案

### 6.1 即時対応可能な改善
1. **On Error Resume Next の削除**
   - 影響: 低
   - 効果: エラーの可視化
   
2. **未使用コードの削除**
   - 影響: 低
   - 効果: 保守性向上

### 6.2 段階的改善計画
1. **フェーズ1: クリーンアップ**
   - デッドコード削除
   - コメント整理
   - 命名規則統一

2. **フェーズ2: 構造改善**
   - グローバル変数の削減
   - 高複雑度メソッドの分割
   - エラーハンドリング改善

3. **フェーズ3: 移行準備**
   - COM依存の整理
   - データアクセス層の分離
   - UIロジックの分離

この解析ガイドに従って体系的な分析を行うことで、VB6レガシーシステムの現状を正確に把握し、適切な保守・移行戦略を立案できます。