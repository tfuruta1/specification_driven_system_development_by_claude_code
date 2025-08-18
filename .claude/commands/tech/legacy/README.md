# 📚 レガシー技術専用コマンド

## 概要
レガシーシステムは技術ごとに特殊性が高いため、個別の専門コマンドとして管理します。各コマンドは特定のレガシー技術に深く特化しています。

## レガシー専用コマンド一覧

### 🔧 個別レガシー技術コマンド
| コマンド | 説明 | 対象技術 | 特殊性 |
|---------|------|----------|--------|
| `/vb6-migration` | VB6移行専用 | Visual Basic 6.0 | ActiveX、COM、ADODB特有の問題 |
| `/ocr-integration` | OCR統合専用 | ISP-673、Tesseract等 | x86必須、DLL依存、画像処理 |
| `/access-migration` | Access移行専用 | MS Access (.mdb/.accdb) | JET/ACE、フォーム、マクロ変換 |

### 🚧 今後追加予定のレガシーコマンド
| コマンド | 説明 | 対象技術 | 優先度 |
|---------|------|----------|--------|
| `/cobol-migration` | COBOL移行 | COBOL | 中 |
| `/foxpro-migration` | FoxPro移行 | Visual FoxPro | 低 |
| `/delphi-migration` | Delphi移行 | Delphi/Pascal | 低 |
| `/powerbuilder-migration` | PowerBuilder移行 | PowerBuilder | 低 |

## なぜ統合しないのか？

### 技術的理由
1. **特殊な依存関係**
   - VB6: COM/ActiveX依存
   - OCR: ネイティブDLL依存（x86必須）
   - Access: JET/ACEエンジン依存

2. **独自のデータ形式**
   - VB6: .frm、.vbp、.bas形式
   - Access: .mdb/.accdb独自形式
   - OCR: TIFF、PDF等の画像形式

3. **特殊な変換ロジック**
   - VB6: On Error → try-catch変換
   - Access: クロス集計クエリ → PIVOT変換
   - OCR: 画像前処理アルゴリズム

### 管理上の理由
1. **専門性の維持**
   - 各技術に特化した深い知識が必要
   - 統合すると複雑度が爆発的に増加
   - 個別最適化が困難に

2. **保守性の確保**
   - 問題の切り分けが容易
   - 技術ごとの更新が独立
   - ドキュメントの明確化

## 使用ガイドライン

### レガシー移行の基本フロー
```mermaid
graph TD
    A[レガシーシステム特定] --> B{技術判定}
    B -->|VB6| C[/vb6-migration]
    B -->|Access| D[/access-migration]
    B -->|OCR必要| E[/ocr-integration]
    B -->|その他| F[個別対応]
    
    C --> G[移行実行]
    D --> G
    E --> G
    F --> G
    
    G --> H[検証・テスト]
    H --> I[本番移行]
```

### コマンド選択基準
```yaml
VB6システムの場合:
  - 主要技術: Visual Basic 6.0
  - 使用コマンド: /vb6-migration
  - 考慮事項: COM依存、ActiveXコントロール

Accessアプリの場合:
  - 主要技術: Microsoft Access
  - 使用コマンド: /access-migration
  - 考慮事項: フォーム、レポート、マクロ

帳票OCRシステムの場合:
  - 主要技術: OCR（ISP-673等）
  - 使用コマンド: /ocr-integration
  - 考慮事項: x86制約、画像品質
```

## 実行例

### VB6プロジェクトの移行
```bash
# 1. 分析フェーズ
/vb6-migration analyze MyProject.vbp --deep

# 2. 評価レポート生成
/vb6-migration assess MyProject.vbp --report

# 3. 実際の変換
/vb6-migration convert MyProject.vbp --target=net48
```

### Accessデータベースの移行
```bash
# 1. スキーマ移行
/access-migration database.accdb sqlserver --schema-only

# 2. データ移行
/access-migration database.accdb sqlserver --data-only

# 3. フォーム変換
/access-migration database.accdb sqlserver --with-forms
```

### OCRシステムの統合
```bash
# 1. セットアップ
/ocr-integration isp673 setup --x86

# 2. テスト実行
/ocr-integration isp673 test sample.tif

# 3. 本番処理
/ocr-integration isp673 process invoice.tif --area-ocr
```

## トラブルシューティング共通項目

### 文字コード問題
- **症状**: 日本語文字化け
- **原因**: Shift-JIS → UTF-8変換
- **対処**: 明示的なエンコーディング指定

### 32bit/64bit問題
- **症状**: DLLロードエラー
- **原因**: アーキテクチャ不一致
- **対処**: プラットフォーム設定確認

### 権限問題
- **症状**: アクセス拒否
- **原因**: レガシーシステムの権限モデル
- **対処**: 管理者権限で実行

## ベストプラクティス

### 段階的移行
1. **パイロット移行**: 小規模な部分から開始
2. **並行稼働**: 新旧システムの並行運用
3. **段階的切り替え**: 機能単位での切り替え
4. **完全移行**: 最終的な切り替え

### リスク管理
- 必ず完全バックアップを取得
- ロールバック計画を準備
- テスト環境での十分な検証
- ユーザー教育の実施

## 管理責任
- **管理部門**: システム開発部
- **方針**: 各レガシー技術の特殊性を尊重した個別管理
- **サポート**: 技術ごとの専門知識を維持

---
*レガシー技術コマンドは、それぞれの技術の特殊性を考慮して個別に管理されています。*