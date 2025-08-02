# VB6 文字コード取り扱いガイド

## 🚨 重要: VB6ソースコードの文字コード仕様

Visual Basic 6.0のソースコードは**必ずShift-JIS (SJIS)**文字コードで保存されています。これはVB6の仕様であり、他の文字コードで保存するとVB6 IDEで文字化けが発生します。

## 📋 対象ファイル拡張子

以下のVB6関連ファイルはすべてSJISで保存する必要があります：

- `.bas` - 標準モジュール
- `.cls` - クラスモジュール  
- `.frm` - フォームファイル
- `.vbp` - プロジェクトファイル
- `.vbg` - プロジェクトグループ
- `.dob` - UserDocumentファイル
- `.dsr` - デザイナファイル
- `.ctl` - ユーザーコントロール
- `.pag` - プロパティページ

## ⚠️ 文字化けを防ぐために

### 読み込み時
```python
# Python例
with open('Module1.bas', 'r', encoding='shift-jis') as f:
    content = f.read()
```

```csharp
// C#例
string content = File.ReadAllText("Module1.bas", Encoding.GetEncoding("shift-jis"));
```

### 書き込み時
```python
# Python例
with open('Module1.bas', 'w', encoding='shift-jis') as f:
    f.write(content)
```

```csharp
// C#例
File.WriteAllText("Module1.bas", content, Encoding.GetEncoding("shift-jis"));
```

## 🔧 Git設定

VB6プロジェクトをGitで管理する場合の推奨設定：

### .gitattributes
```
*.bas text encoding=shift-jis
*.cls text encoding=shift-jis
*.frm text encoding=shift-jis
*.vbp text encoding=shift-jis
*.vbg text encoding=shift-jis
*.dob text encoding=shift-jis
*.dsr text encoding=shift-jis
*.ctl text encoding=shift-jis
*.pag text encoding=shift-jis
```

### core.autocrlf設定
```bash
# Windows環境での推奨設定
git config core.autocrlf true
```

## 📝 エディタ設定

### Visual Studio Code
`.vscode/settings.json`:
```json
{
  "[vb]": {
    "files.encoding": "shiftjis"
  }
}
```

### Sublime Text
プロジェクト設定:
```json
{
  "folders": [{
    "path": ".",
    "file_encoding": "shift-jis"
  }]
}
```

## 🚫 避けるべきこと

1. **UTF-8で保存しない** - VB6 IDEで日本語が文字化けします
2. **BOM付きで保存しない** - VB6はBOMを認識しません
3. **改行コードの混在** - CRLFで統一してください
4. **エンコーディング自動検出に頼らない** - 明示的にSJISを指定

## ✅ ベストプラクティス

1. **バックアップを取る** - エンコーディング変換前に必ずバックアップ
2. **一括変換ツールの使用** - 複数ファイルを扱う場合は専用ツールを使用
3. **CI/CDでの検証** - エンコーディングが正しいことを自動テストで確認
4. **チーム内での共有** - 開発チーム全員が文字コード設定を統一

## 🔍 トラブルシューティング

### 文字化けが発生した場合
1. ファイルのバックアップから復元
2. 文字コード変換ツール（nkf、iconv等）でSJISに変換
3. VB6 IDEで開いて正しく表示されることを確認

### 判別が難しい文字
- 全角スペース、波ダッシュなどは特に注意
- コメント内の特殊文字も文字化けの原因になりやすい

---

**重要**: このガイドラインに従うことで、VB6プロジェクトの文字化けを防ぎ、安定した開発環境を維持できます。