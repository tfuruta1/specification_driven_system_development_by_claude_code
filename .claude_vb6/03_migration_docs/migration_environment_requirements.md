# VB6移行ツール環境要件ガイド

## 1. 概要

VB6から.NET Framework 4.8への移行作業において、必要となる環境は作業フェーズによって異なります。本ガイドでは、各フェーズで必要な環境と、環境がない場合の代替策を説明します。

## 2. フェーズ別環境要件

### 2.1 解析フェーズ - 静的コード解析

**必要環境**: .NET Framework 4.8環境のみ

**実行可能な作業**:
- VB6ソースコード（.vbp、.frm、.bas、.cls）の解析
- コード複雑度の測定
- 依存関係の基本的な分析
- 未使用コードの検出
- 移行可能性の初期評価

**理由**: VB6のプロジェクトファイルやソースコードはテキスト形式のため、.NETベースの解析ツールで読み取り・解析が可能です。

```bash
# .NET環境のみで実行可能なコマンド
/analyze-vb6-code "C:\Legacy\Project"
/dependency-analysis "C:\Legacy\Project"
/find-obsolete-code "C:\Legacy\Project"
/code-metrics "C:\Legacy\Project"
```

### 2.2 詳細調査フェーズ - COM/実行時解析

**必要環境**: .NET Framework 4.8 + VB6ランタイム（一部VB6 IDE）

**実行可能な作業**:
- COMコンポーネントの登録状況確認
- OCX/DLLの実際のインターフェース解析
- サードパーティコンポーネントの依存関係
- 実行時の動作確認

**必要なVB6コンポーネント**:
```
- msvbvm60.dll (VB6ランタイム)
- 使用されているOCXファイル
  - MSCOMCTL.OCX (Common Controls)
  - COMDLG32.OCX (Common Dialog)
  - MSFLXGRD.OCX (FlexGrid)
  - その他プロジェクト固有のOCX
```

```bash
# VB6ランタイムが必要なコマンド
/com-inventory "C:\Legacy\Project" --check-registration
/database-schema-extract "C:\Legacy\Project" --test-connection
/ui-controls-map "C:\Legacy\Project" --validate-ocx
```

### 2.3 移行実行フェーズ

**推奨環境**: .NET Framework 4.8 + Visual Studio + VB6 IDE（オプション）

**実行可能な作業**:
- ソースコードの自動変換
- .NETプロジェクトの生成
- 移行後のコンパイル確認
- 並行実行テスト（VB6環境が必要）

## 3. 環境構成パターン

### 3.1 最小構成（基本的な移行作業）

```yaml
OS: Windows 10/11
開発環境:
  - .NET Framework 4.8
  - Visual Studio 2019/2022 Community以上
  - 移行ツール（.NETベース）
  
実行可能な作業:
  - ソースコード解析: 100%
  - 基本的なコード変換: 100%
  - COM解析: 30%（宣言部のみ）
  - 実行時検証: 0%
```

### 3.2 推奨構成（実用的な移行作業）

```yaml
OS: Windows 10/11
開発環境:
  - .NET Framework 4.8
  - Visual Studio 2019/2022 Professional以上
  - VB6ランタイム (msvbvm60.dll)
  - 主要なVB6標準OCXコンポーネント
  
追加ツール:
  - Process Monitor (DLL/レジストリアクセス監視)
  - Dependency Walker (DLL依存関係確認)
  
実行可能な作業:
  - ソースコード解析: 100%
  - 基本的なコード変換: 100%
  - COM解析: 80%（標準コンポーネント）
  - 実行時検証: 50%（基本動作）
```

### 3.3 理想構成（完全な移行と検証）

```yaml
OS: Windows 10/11（VB6用仮想環境推奨）
開発環境:
  - .NET Framework 4.8
  - Visual Studio 2019/2022 Enterprise
  - Visual Basic 6.0 SP6 IDE
  - 対象プロジェクトの全依存コンポーネント
  
追加環境:
  - Windows XP/7仮想マシン（レガシー環境テスト用）
  - 自動テストツール
  - パフォーマンス測定ツール
  
実行可能な作業:
  - ソースコード解析: 100%
  - 基本的なコード変換: 100%
  - COM解析: 100%
  - 実行時検証: 100%
```

## 4. VB6環境がない場合の対処法

### 4.1 仮想環境の活用

```powershell
# Hyper-Vで Windows 7 仮想マシンを作成
New-VM -Name "VB6Dev" -MemoryStartupBytes 4GB -VHDPath "C:\VMs\VB6Dev.vhdx"

# 仮想マシン内でVB6環境を構築
# 1. Windows 7/10をインストール
# 2. VB6 SP6をインストール
# 3. 必要なOCX/DLLを登録
```

### 4.2 段階的移行アプローチ

```mermaid
graph LR
    A[Phase 1: 静的解析<br/>.NET環境のみ] --> B[Phase 2: 部分移行<br/>非COM部分のみ]
    B --> C[Phase 3: COM調査<br/>VB6環境準備]
    C --> D[Phase 4: 完全移行<br/>全機能移行]
```

### 4.3 代替ツールの活用

| ツール | 用途 | VB6環境要否 |
|--------|------|-------------|
| Microsoft Assessment Tool | 移行評価 | 不要 |
| VB Migration Partner | 自動変換 | 不要* |
| Mobilize.Net VBUC | 自動変換 | 不要* |
| Manual Analysis | 手動解析 | 不要 |

*基本的な変換は不要だが、COM解析には一部必要

## 5. 環境セットアップ手順

### 5.1 .NET開発環境のセットアップ

```powershell
# 1. .NET Framework 4.8 のインストール確認
Get-ItemProperty "HKLM:SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" | Select Release

# 2. Visual Studio のインストール（Chocolateyを使用）
choco install visualstudio2022community -y

# 3. 必要なワークロードの追加
vs_installer.exe modify --installPath "C:\Program Files\Microsoft Visual Studio\2022\Community" `
  --add Microsoft.VisualStudio.Workload.NetWeb `
  --add Microsoft.VisualStudio.Workload.ManagedDesktop
```

### 5.2 VB6ランタイムのセットアップ（必要な場合）

```batch
REM 1. VB6ランタイムのダウンロード
REM https://www.microsoft.com/en-us/download/details.aspx?id=24417

REM 2. 基本的なOCXの登録
regsvr32 /s "C:\Windows\System32\MSCOMCTL.OCX"
regsvr32 /s "C:\Windows\System32\COMDLG32.OCX"
regsvr32 /s "C:\Windows\System32\MSFLXGRD.OCX"

REM 3. 登録確認
reg query HKCR\CLSID | findstr "MSComctlLib"
```

## 6. 推奨ワークフロー

### 6.1 環境なしからのスタート

1. **.NET環境のみで開始**
   ```bash
   # 初期解析
   /analyze-vb6-code "C:\Legacy\Project"
   /migration-assessment "C:\Legacy\Project"
   ```

2. **解析結果から必要環境を判定**
   ```bash
   # COM依存度チェック
   /com-inventory "C:\Legacy\Project" --list-required
   ```

3. **必要に応じて環境追加**
   - 標準OCXのみ → VB6ランタイムを追加
   - カスタムCOM多数 → VB6 IDE環境を準備

### 6.2 リスク最小化アプローチ

```yaml
低リスク作業（.NET環境のみ）:
  - データアクセス層の移行
  - ビジネスロジックの移行
  - ユーティリティ関数の移行

中リスク作業（VB6ランタイム推奨）:
  - 標準UIコントロールの移行
  - 基本的なCOM相互運用

高リスク作業（完全なVB6環境必須）:
  - カスタムOCXの移行
  - サードパーティコンポーネント
  - 実行時動作の完全検証
```

## 7. まとめ

- **基本的な移行**: .NET Framework 4.8環境のみで開始可能
- **実用的な移行**: VB6ランタイムがあると作業効率が大幅に向上
- **完全な移行**: プロジェクトの複雑さに応じてVB6 IDE環境も検討
- **推奨アプローチ**: 段階的に環境を拡充していく方式

移行プロジェクトの規模、予算、期限に応じて、適切な環境構成を選択してください。