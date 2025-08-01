# /ocr-setup - ISP-673 OCR環境セットアップ

## 概要
ISP-673帳票OCRソフトウェアの開発環境を自動セットアップし、GloryOcrMain4.dll COM DLLとの統合を確立します。

## 主な機能

### 1. ISP-673 OCR環境検証
- GloryOcrMain4.dllの存在確認
- COM登録状態確認
- ISP-673ランタイムライブラリ確認
- 辞書ファイル・RPFファイル配置確認

### 2. プロジェクト設定自動化
- x86プラットフォーム設定の強制適用
- COM参照（GloryOcr4Lib）の自動追加
- 必要なnamespace宣言追加
- GlobalFree API宣言追加

### 3. OCR基本インフラ構築
- OCRサービス基底クラス生成
- COM相互運用ヘルパー生成
- メモリ管理ユーティリティ生成
- エラーハンドリング基盤構築

## コマンド使用例

```cmd
# 基本セットアップ
/ocr-setup

# 詳細検証モード
/ocr-setup --verify-all

# 既存設定の強制更新
/ocr-setup --force-update

# サンプルコード生成も含める
/ocr-setup --with-samples
```

## セットアップ内容

### プロジェクト設定の自動適用
```xml
<PropertyGroup>
  <PlatformTarget>x86</PlatformTarget>
  <Prefer32Bit>true</Prefer32Bit>
</PropertyGroup>

<COMReference Include="GloryOcr4Lib">
  <Guid>{GUID}</Guid>
  <VersionMajor>4</VersionMajor>
  <VersionMinor>0</VersionMinor>
  <WrapperTool>tlbimp</WrapperTool>
  <EmbedInteropTypes>True</EmbedInteropTypes>
</COMReference>
```

### 必要なAPI宣言の自動追加
```csharp
using GloryOcr4Lib;
using System.Runtime.InteropServices;

[DllImport("kernel32.dll", SetLastError=true)]
static extern int GlobalFree(int hMem);

[DllImport("kernel32.dll", SetLastError=true)]
static extern IntPtr GlobalLock(int hMem);

[DllImport("kernel32.dll", SetLastError=true)]
static extern bool GlobalUnlock(int hMem);
```

### OCR基本サービスクラス生成
- `IOcrService.cs` - OCRサービスインターフェース
- `OcrServiceBase.cs` - OCR基底サービス
- `ComInteropHelper.cs` - COM相互運用ヘルパー
- `MemoryManager.cs` - OCRメモリ管理
- `OcrException.cs` - OCR専用例外クラス

## 検証項目

### 環境検証
- [ ] GloryOcrMain4.dll存在確認
- [ ] COM登録確認（レジストリ）
- [ ] 辞書ディレクトリ確認
- [ ] サンプルプロジェクト確認

### プロジェクト設定検証
- [ ] x86プラットフォーム設定
- [ ] COM参照設定
- [ ] using宣言
- [ ] API宣言

### ビルド検証
- [ ] コンパイル成功
- [ ] COM相互運用正常
- [ ] x86ターゲット確認
- [ ] 依存性解決確認

## トラブルシューティング

### よくある問題と解決策

1. **COM DLL未登録エラー**
   ```cmd
   regsvr32 "C:\Program Files\Glory\Glyocr4\GloryOcrMain4.dll"
   ```

2. **64bitプラットフォームエラー**
   ```xml
   <PlatformTarget>x86</PlatformTarget>
   ```

3. **COM参照エラー**
   - Visual Studioの再起動
   - COM参照の削除・再追加

4. **GlobalFree未定義エラー**
   ```csharp
   [DllImport("kernel32.dll")]
   static extern int GlobalFree(int hMem);
   ```

## 成功時の出力

```
✅ ISP-673 OCR環境セットアップ完了

環境検証:
✅ GloryOcrMain4.dll 検出
✅ COM登録確認
✅ 辞書ファイル確認

プロジェクト設定:
✅ x86プラットフォーム設定
✅ COM参照追加
✅ API宣言追加

OCR基本インフラ:
✅ OCRサービス基底クラス生成
✅ COM相互運用ヘルパー生成
✅ メモリ管理ユーティリティ生成

🚀 Next: /ocr-interface でOCRインターフェース実装を開始
```