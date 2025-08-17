# /vb6-migration - VB6移行専用コマンド

## 概要
Visual Basic 6.0アプリケーションを.NET Framework/.NET Coreへ移行するための専門コマンドです。VB6特有の問題に特化した解析と変換を提供します。

## 使用方法
```bash
/vb6-migration [action] [target] [options]

# 使用例
/vb6-migration analyze MyProject.vbp --deep
/vb6-migration convert MyProject.vbp --target=net48
/vb6-migration assess MyProject.vbp --report
/vb6-migration dependencies MyProject.vbp --com-check
```

## パラメータ

### アクション
- `analyze` - VB6プロジェクト解析
- `convert` - コード変換実行
- `assess` - 移行評価レポート
- `dependencies` - 依存関係分析
- `test` - 変換後テスト生成

### ターゲット
- `net48` - .NET Framework 4.8
- `net6` - .NET 6/7/8
- `netcore` - .NET Core 3.1
- `vbnet` - VB.NET（段階的移行）

## VB6特有の問題と対処

### 1. ActiveXコントロール依存
```vb
' VB6: ActiveXコントロール使用
Private Sub Form_Load()
    MSComm1.CommPort = 1
    MSComm1.Settings = "9600,N,8,1"
    MSComm1.PortOpen = True
End Sub
```

```csharp
// 変換後: .NETシリアルポート
private void Form_Load(object sender, EventArgs e)
{
    serialPort1.PortName = "COM1";
    serialPort1.BaudRate = 9600;
    serialPort1.Parity = Parity.None;
    serialPort1.DataBits = 8;
    serialPort1.StopBits = StopBits.One;
    serialPort1.Open();
}
```

### 2. ADOからADO.NETへの変換
```vb
' VB6: ADODB使用
Dim rs As ADODB.Recordset
Set rs = New ADODB.Recordset
rs.Open "SELECT * FROM Users", conn, adOpenStatic
```

```csharp
// 変換後: ADO.NET
using (var cmd = new SqlCommand("SELECT * FROM Users", conn))
using (var reader = cmd.ExecuteReader())
{
    while (reader.Read())
    {
        // データ処理
    }
}
```

### 3. Variant型の処理
```vb
' VB6: Variant型
Dim value As Variant
value = "Text"
value = 123
value = #1/1/2025#
```

```csharp
// 変換後: dynamic または適切な型
dynamic value;
value = "Text";
value = 123;
value = new DateTime(2025, 1, 1);

// または型安全な実装
object value;
if (value is string text) { /* 処理 */ }
if (value is int number) { /* 処理 */ }
```

### 4. On Error文のtry-catch変換
```vb
' VB6: On Error
On Error GoTo ErrorHandler
    ' 処理
    Exit Sub
ErrorHandler:
    MsgBox Err.Description
```

```csharp
// 変換後: try-catch
try
{
    // 処理
}
catch (Exception ex)
{
    MessageBox.Show(ex.Message);
}
```

## 依存関係分析

### COMコンポーネント検出
```yaml
COM Dependencies Analysis:
  Microsoft.Office.Interop.Excel:
    - Version: 14.0.0.0
    - Action: NuGetパッケージ置換
    
  MSCOMCTL.OCX:
    - Version: 6.0
    - Action: .NETコントロール置換
    
  Custom.DLL:
    - Version: Unknown
    - Action: COM Interop維持または再実装
```

### API宣言の変換
```vb
' VB6: Windows API
Private Declare Function GetWindowText Lib "user32" _
    Alias "GetWindowTextA" (ByVal hwnd As Long, _
    ByVal lpString As String, ByVal cch As Long) As Long
```

```csharp
// 変換後: P/Invoke
[DllImport("user32.dll", CharSet = CharSet.Auto)]
private static extern int GetWindowText(IntPtr hWnd, 
    StringBuilder lpString, int nMaxCount);
```

## フォーム変換戦略

### VB6フォーム → Windows Forms
```xml
<!-- 変換マッピング -->
<FormConversion>
  <Control vb6="TextBox" net="TextBox"/>
  <Control vb6="CommandButton" net="Button"/>
  <Control vb6="ListBox" net="ListBox"/>
  <Control vb6="MSFlexGrid" net="DataGridView"/>
  <Control vb6="CommonDialog" net="OpenFileDialog/SaveFileDialog"/>
</FormConversion>
```

### イベント変換
```vb
' VB6
Private Sub Command1_Click()
End Sub
```

```csharp
// .NET
private void button1_Click(object sender, EventArgs e)
{
}
```

## 段階的移行戦略

### Phase 1: COM Interop
```csharp
// VB6 DLLをそのまま参照
[ComImport]
[Guid("VB6-GUID-HERE")]
public interface IVB6Component
{
    string ProcessData(string input);
}
```

### Phase 2: 部分移行
```csharp
// 重要な部分から.NETに移行
public class MigratedComponent : IVB6Component
{
    public string ProcessData(string input)
    {
        // 新しい.NET実装
        return ModernImplementation(input);
    }
}
```

### Phase 3: 完全移行
- VB6コード完全削除
- .NETネイティブ実装
- 最新フレームワーク活用

## 評価レポート例
```markdown
# VB6移行評価レポート

## プロジェクト分析
- プロジェクト: InventorySystem.vbp
- フォーム数: 45
- モジュール数: 23
- クラス数: 15
- コード行数: 68,000

## 移行可能性評価
| カテゴリ | 自動変換率 | リスク |
|---------|-----------|--------|
| UIフォーム | 75% | 中 |
| ビジネスロジック | 85% | 低 |
| データアクセス | 40% | 高 |
| COMコンポーネント | 20% | 高 |

## 推定工数
- 自動変換: 1週間
- 手動修正: 6週間
- テスト: 4週間
- 合計: 11週間

## 主要リスク
1. Crystal Reports依存 → SSRS移行必要
2. サードパーティOCX → 代替品調査必要
3. Windows API多用 → P/Invoke変換必要
```

## トラブルシューティング

| 問題 | 原因 | 解決策 |
|------|------|--------|
| 配列境界 | VB6は0または1開始 | 明示的な境界指定 |
| Null処理 | VB6のNull特殊性 | DBNull.Value使用 |
| 文字列処理 | 固定長文字列 | String.PadRight使用 |
| デフォルトプロパティ | VB6の暗黙参照 | 明示的プロパティ指定 |

## 出力ファイル
- 変換後コード: `./converted/`
- 移行レポート: `./reports/migration_report.html`
- エラーログ: `./logs/conversion_errors.log`
- マッピングファイル: `./mapping/control_mapping.xml`

## 管理責任
- **管理部門**: システム開発部
- **専門性**: VB6特有の問題に特化

## 関連コマンド
- `/vb6-analyze` - VB6コード詳細解析
- `/com-interop` - COM相互運用設定
- `/winforms-migration` - Windows Forms移行

---
*このコマンドはシステム開発部が管理します。VB6特有の問題に特化しています。*