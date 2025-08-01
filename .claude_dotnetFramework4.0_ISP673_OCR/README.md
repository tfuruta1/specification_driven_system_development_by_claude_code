# ISP-673 帳票OCRソフトウェア .NET Framework 4.0 統合プロジェクト

## 🎯 プロジェクト概要

ISP-673帳票OCRソフトウェアを活用した.NET Framework 4.0 Windows Formsアプリケーション開発プロジェクトです。Windows XP SP3、Windows Server 2003 R2以降の環境をサポートし、レガシーシステムとの高い互換性を維持しながら、高性能なOCR機能を統合します。

### 主要特徴

- **ISP-673 OCR完全統合** - GloryOcrMain4.dll COM DLLによる帳票認識・エリアOCR
- **Windows XP/2003完全対応** - 企業の既存環境での安定稼働
- **.NET Framework 4.0最適化** - x86プラットフォーム強制、COM相互運用
- **3つのOCRインターフェース** - IGlyOcr（標準）、IGlyOcrEx（エリアOCR）、IGlyOcrC（C言語用）
- **フォーム認識・画像処理** - 帳票判別、傾き補正、2値化、バーコード認識
- **マルチAI協調開発** - Claude Code + Gemini CLI + o3 MCPによる高品質実装

## 🚀 クイックスタート

### 前提条件
- Windows XP SP3 以降 / Windows Server 2003 R2 以降
- .NET Framework 4.0
- Visual Studio 2010 以降
- ISP-673 帳票OCRソフトウェア (GloryOcrMain4.dll)
- **必須**: x86プラットフォーム設定

### セットアップ
```bash
# プロジェクトディレクトリへ移動
cd .claude_dotnetFramework4.0_ISP673_OCR

# Claude Codeで開始
claude .

# OCR開発フロー開始
/spec ocr-development
```

## 📋 ISP-673 OCR専用コマンド (36個)

### Claude Code OCRコマンド (30個)
- `/spec` - 統合OCR開発フロー管理
- `/ocr-setup` - ISP-673 OCR環境セットアップ
- `/ocr-interface` - OCRインターフェース実装支援
- `/form-recognition` - 帳票認識機能実装
- `/area-ocr` - エリアOCR機能実装
- `/image-processing` - 画像処理機能実装
- `/barcode-recognition` - バーコード認識実装
- `/com-integration` - COM DLL統合サポート
- `/x86-build` - x86プラットフォーム最適化
- `/ocr-testing` - OCR機能テスト支援
- `/legacy-integration` - レガシーシステム統合
- `/performance-tuning` - OCR性能最適化
- `/error-handling` - OCRエラーハンドリング
- `/memory-management` - OCRメモリ管理
- `/deployment-ocr` - OCR環境デプロイメント
- `/analyze-ocr-image` - OCR対象画像を分析して最適な前処理方法を提案（マルチAI連携）
- `/implement-custom-preprocessing` - プロジェクト固有の前処理パターンを実装（マルチAI設計）
- `/test-preprocessing-quality` - 前処理結果の品質をマルチAIで評価
- `/optimize-preprocessing-params` - 前処理パラメータをマルチAIで最適化
- `/create-preprocessing-preset` - 文書タイプ別の前処理プリセットを作成
- `/benchmark-preprocessing` - 前処理性能をベンチマーク（処理速度・品質）
- `/implement-gpu-acceleration` - GPU加速による前処理の高速化実装
- `/analyze-ocr-results` - OCR結果を分析して前処理の改善点を特定
- `/create-preprocessing-pipeline` - 複数の前処理を組み合わせたパイプラインを構築
- `/train-ml-preprocessor` - 機械学習ベースの前処理パラメータ予測モデルを訓練
- `/integrate-preprocessing-ui` - 前処理UIコンポーネントをアプリケーションに統合
- `/export-preprocessing-config` - 前処理設定をエクスポート/インポート可能な形式に変換
- `/debug-preprocessing` - 前処理のデバッグとトラブルシューティング
- `/compare-preprocessing-methods` - 複数の前処理手法を比較評価
- `/generate-preprocessing-docs` - プロジェクト固有の前処理ドキュメントを生成

### Gemini CLI コマンド (3個)
- `/research` - OCR市場分析・ユーザー調査
- `/ocr-ux-strategy` - OCR UI/UX戦略
- `/product-plan` - OCRロードマップ策定

### o3 MCP コマンド (3個)
- `/ocr-architecture` - OCRシステムアーキテクチャ設計
- `/ocr-security` - OCRセキュリティ設計・監査
- `/ocr-devops` - OCR CI/CD・デプロイ自動化

## 🏗️ プロジェクト構造

```
.claude_dotnetFramework4.0_ISP673_OCR/
├── src/                              # ソースコード
│   ├── ISP673_OCRApp.sln            # ソリューションファイル
│   ├── ISP673_OCRApp/               # メインOCRアプリケーション
│   ├── ISP673_OCRApp.Core/          # OCRビジネスロジック
│   ├── ISP673_OCRApp.Data/          # OCRデータアクセス層
│   └── ISP673_OCRApp.Tests/         # OCRテストプロジェクト
├── commands/                         # OCR専用カスタムコマンド
├── docs/                            # ISP-673 OCRドキュメント
├── samples/                         # ISP-673サンプルコード統合
└── deployment/                      # OCRデプロイメント設定
```

## 💻 ISP-673 OCR技術スタック

### OCR専用フレームワーク・ライブラリ
- **.NET Framework 4.0** (C# 4.0) - x86プラットフォーム
- **GloryOcrMain4.dll** - ISP-673 COM DLL
- **Windows Forms** - OCR UIフレームワーク
- **COM Interop** - COMオブジェクトとの相互運用
- **Unity Container 2.1** - 依存性注入
- **log4net 2.0.3** - OCRロギング
- **System.Drawing** - 画像処理

### ISP-673 OCRインターフェース
- **IGlyOcr** - 標準帳票OCR機能（推奨）
- **IGlyOcrEx** - エリアOCR・画像処理機能
- **IGlyOcrC** - C言語特化（C#では使用不可）

### OCRアーキテクチャパターン
- **MVP (Model-View-Presenter)** - OCR UIアーキテクチャ
- **Factory Pattern** - OCRインターフェース生成
- **Strategy Pattern** - OCR処理方式切り替え
- **Observer Pattern** - OCR処理イベント駆動
- **Command Pattern** - OCRコマンド処理

## 🔧 ISP-673 OCR開発制約事項

### x86プラットフォーム必須設定
```xml
<PropertyGroup>
  <PlatformTarget>x86</PlatformTarget>
  <Prefer32Bit>true</Prefer32Bit>
</PropertyGroup>
```

### COM参照設定
- **GloryOcr4 ライブラリ** - COM参照必須
- **Version 4.x** - 古いVersion 3.xは選択禁止
- **using GloryOcr4Lib;** - namespace宣言

### OCR処理制限事項
| 機能 | 制限事項 | 対応方法 |
|------|----------|----------|
| メモリ管理 | GlobalFree必須 | イメージ使用後のメモリ開放 |
| プラットフォーム | x86のみ | AnyCPU使用禁止 |
| 64bitOS | WOW64で動作 | Program Files (x86)対応 |
| 並行処理 | 非対応 | シングルスレッド処理 |

## 📊 ISP-673 OCR性能・品質指標

- **OCR処理時間**: 1秒/ページ以内 (A4帳票)
- **認識精度**: 99%以上 (標準帳票)
- **メモリ使用量**: 150MB以下 (OCR処理時)
- **起動時間**: 3秒以内 (Windows XP環境)
- **応答時間**: 200ms以内 (UI操作)
- **コードカバレッジ**: 85%以上

## 🎯 ISP-673 OCR主要機能

### 1. 帳票OCR (IGlyOcr)
- 帳票種類自動判別
- OCR文字認識
- 帳票判別辞書活用
- グループ処理対応

### 2. エリアOCR (IGlyOcrEx)
- 任意領域OCR
- RPFファイル活用
- 座標指定認識
- バーコード認識

### 3. 画像処理 (IGlyOcrEx)
- 2値化処理
- 傾き補正
- 黒枠除去
- ノイズ除去

### 4. 認識結果処理
- 候補結果取得
- 信頼度評価
- リジェクト処理
- 詳細結果分析

## 🛡️ OCRセキュリティ対策

- **画像データ暗号化** - AES 256bit
- **認識結果保護** - メモリ暗号化
- **アクセス制御** - Windows認証連携
- **監査ログ** - OCR処理履歴記録
- **データ消去** - メモリクリア処理

## 📦 ISP-673 OCRデプロイメント

### 配布方法
1. **MSI インストーラー** - GloryOcrMain4.dll同梱
2. **XCopy デプロイ** - 手動DLL配置
3. **ClickOnce** - 自動更新対応（DLL事前配置必要）
4. **SCCM/WSUS** - 企業一括配布

### 対応環境
- Windows XP SP3 (x86) - ISP-673推奨環境
- Windows Server 2003 R2 SP2 (x86)
- Windows Vista / 7 / 8 / 8.1 / 10 / 11 (x86/x64)
- Windows Server 2008 / 2012 / 2016 / 2019 / 2022 (x86/x64)

### 必要ランタイム
- .NET Framework 4.0
- Visual C++ 2010 再頒布可能パッケージ
- ISP-673 認識エンジン

## 📚 ISP-673 OCRドキュメント

### OCR統合ガイド
- [ISP-673 OCR統合コンセプト](00_project/01_ocr_integration_concept.md)
- [OCR技術スタックガイドライン](00_project/02_ocr_tech_stack_guidelines.md)
- [OCRアーキテクチャ設計](01_development_docs/01_ocr_architecture_design.md)

### 実装ガイド
- [COM DLL統合ガイド](03_library_docs/01_com_dll_integration_guide.md)
- [x86プラットフォーム設定ガイド](03_library_docs/02_x86_platform_guide.md)
- [OCRインターフェース実装ガイド](03_library_docs/03_ocr_interface_guide.md)
- [画像処理実装ガイド](03_library_docs/04_image_processing_guide.md)

### サンプルコード
- [基本帳票OCRサンプル](samples/basic_form_ocr_sample.md)
- [エリアOCRサンプル](samples/area_ocr_sample.md)
- [画像処理サンプル](samples/image_processing_sample.md)
- [バーコード認識サンプル](samples/barcode_recognition_sample.md)

## 🤝 サポート

- **技術サポート**: ISP-673 OCR統合技術サポート
- **コミュニティ**: 帳票OCR開発者フォーラム
- **ドキュメント**: ISP-673統合開発ガイド・ベストプラクティス

---

**🚀 Next Step**: `/spec ocr-development` コマンドでISP-673 OCR統合開発を開始