ISP-673 帳票OCRソフトウェアのC#による活用マニュアルをMarkdown形式で以下にまとめます。この情報は主に「ISP-673 帳票OCRソフトウェア 補足マニュアル（認識エンジン組み込み編）バージョン4 For Microsoft Visual Studio 2015/2013/2012/2010/2008 (Visual C#)」に基づいています。
ISP-673 帳票OCRソフトウェア C#による活用マニュアル
このドキュメントは、「ISP-673 帳票OCRソフトウェア」の認識エンジンをC#アプリケーションに組み込む際の具体的な実装方法と注意点について説明します。
1. インターフェースについて
認識エンジンの機能は、COM準拠のDLLであるGloryOcrMain4.dllを介して提供され、主に以下の3種類のインターフェースがあります:
• IGlyOcr: 標準的な「帳票OCR」機能を提供します。通常はこのインターフェースを使用します。
• IGlyOcrC: C言語での使用に特化しており、VARIANTを使用せずにプログラミングが可能です。Visual BasicおよびVisual C#では使用できません。
• IGlyOcrEx: エリアOCR機能や画像処理機能を提供します。
IGlyOcrとIGlyOcrExは同時に使用できます。
2. 導入方法 (Visual C#)
Visual Studio 2015 / 2013 / 2012 / 2010 / 2008での導入手順は以下の通りです。
1. 新規プロジェクトの作成または既存プロジェクトの開く。
2. 構成マネージャーの設定:
    ◦ 「ビルド」メニューから「構成マネージャー」を実行します。
    ◦ 「アクティブ ソリューション プラットフォーム」とプロジェクトの「プラットフォーム」を**「x86」**に設定し、「閉じる」をクリックします。
    ◦ 注意: 対象プロジェクトのソリューションプラットフォームが「x86」であることを確認してください。
3. 参照設定の追加:
    ◦ 「ソリューションエクスプローラー」で「参照設定」を右クリックし、「参照の追加」を実行します。
    ◦ 「COM」の一覧から**「GloryOcr4 ライブラリ」**を選択し、「OK」をクリックします。
    ◦ 注意: Version3.xなどの古い認識エンジンがインストールされている場合、「GloryOcr3.0 Library」といった選択肢も表示されることがありますが、これらは選択しないでください。
4. Namespaceの使用宣言:
    ◦ コードの冒頭にusing GloryOcr4Lib;を追加します。
5. 変数の宣言:
    ◦ メインフォームのクラススコープ変数として、必要なインターフェースを宣言します。
        ▪ 例: private GlyOcr gOcr = new GlyOcr();
        ▪ 例: private GlyOcrEx gOcrEx = new GlyOcrEx();
        ▪ どちらか一方のみ使用する場合は、不要な方の宣言は不要です。using宣言を行わない場合は、GloryOcr4Lib.GlyOcrのように完全修飾名で宣言します。
6. APIの使用:
    ◦ 宣言した変数を介して、各APIを呼び出します。
        ▪ 例: int retVal; retVal = gOcr.init(@"C:\Program Files\Glory\Glyocr4", @"C:\Proj\サンプル");
3. インターフェース使用例
3.1. 帳票OCR (IGlyOcr)
GlyOcrインターフェースを使用します。処理内容は、事前に登録ツールで作成したプロジェクトでの設定（帳票判別辞書、OCRパラメータ、グループ設定など）に依存します。
• 初期化と終了:
    ◦ initメソッドでライブラリを初期化し、辞書およびプロジェクトのディレクトリを指定します。
        ▪ 例: retVal = gOcr.init(@"C:\Program Files\Glory\Glyocr4", @"C:\Program Files\Glory\Glyocr4\FDic\サンプル");
    ◦ 終了時にはFreeGroup()でグループを開放し、exit()でライブラリを終期化します。
• グループの使用:
    ◦ SetGroupメソッドで処理するグループIDを設定します。
        ▪ 例: retVal = gOcr.SetGroup(2); (帳票判別 & OCR実行)
        ▪ 例: retVal = gOcr.SetGroup(1); (帳票判別のみ実行)
    ◦ グループに登録できるのは、帳票判別辞書が作成されている帳票のみです。
• 処理内容の設定:
    ◦ ProcTypeプロパティで処理内容を設定します。
        ▪ 0: 帳票種類判別 + OCR (デフォルト)
        ▪ 1: 帳票種類判別のみ実行
        ▪ 2: OCRのみ実行
• 認識処理の実行:
    ◦ RecogDocumentFn (ファイル名入力)、RecogDocumentMem (メモリポインタ入力)、RecogDocumentHan (グローバルハンドル入力)のいずれかのメソッドを使用します。
        ▪ 例: retVal = gOcr.RecogDocumentFn(ref DocId, @"C:\TestFile\TEST4-1.jpg");
    ◦ OCRのみ実行する場合、帳票IDは「帳票ID (4桁) + パラメータNo (2桁)」の数値で指定します (例: 帳票ID 0001、パラメータNo 01の場合、101)。
• グループを使用しない場合:
    ◦ initの前にProcTypeを0以外に設定する必要があります。
    ◦ LoadDocDict()で帳票判別辞書をロードできます（帳票判別のみ実行する場合）。
    ◦ LoadOcrParameter(lst)で任意のOCRパラメータをリストで指定してロードできます（OCRのみ実行する場合）。
    ◦ 注意: 「帳票判別&OCR」の場合、1つの帳票に対して複数のOCRパラメータをロードするとリジェクトされます。
• 認識結果の取得:
    ◦ DocumentID、DocumentName、DocumentRejectCode、FieldNumなどのプロパティ、またはget_FieldID、get_FieldName、get_FieldResultメソッドで取得します。
    ◦ より詳細な結果はDocumentResultEx、DocumentResultプロパティ、またはGetFieldResultEx、GetFieldCharResultメソッドで取得します。
    ◦ RejectCode2Stringメソッドでリジェクトコードの内容を取得できます。
• 2パスOCR (応用例): 1回目のOCR結果に基づいて2回目のOCRパラメータを切り替えるような高度な応用が可能です。
• 帳票判別とOCRの独立実行 (応用例): 帳票判別とOCRを完全に分離し、非同期で実行できます。判別がリジェクトされた場合に特定のOCRパラメータで処理を行うなどの応用が可能です。
3.2. エリアOCR1 (IGlyOcrEx)
GlyOcrExインターフェースのRecogFieldメソッドを使用します。この機能は、プロジェクトに登録された特定のOCRパラメータ（フィールド）に基づいた処理を行います。
• 前準備:
    ◦ LoadCharDicで個別文字認識辞書を展開します。
    ◦ LoadRpfFileでRPFファイル（OCRパラメータ）を展開します。
• 終了時:
    ◦ UnLoadRpfFile()でRPFファイルを開放し、UnloadCharDic()で個別文字認識辞書を開放します。
• 注意: init、exit、SetGroupなどの帳票OCRで必要な初期化・終期化・グループ設定は不要です。
• 実行例:
    ◦ info配列にイメージファイル名や斜行角度などの情報を設定します。
    ◦ retVal = gOcrEx.RecogField(out tmp, 101, 1, info);を呼び出します。
3.3. エリアOCR2 (IGlyOcrEx)
GlyOcrExインターフェースのRecogFieldExメソッドを使用します。この機能はプロジェクトの作成が不要で、処理内容はRecogFieldExメソッドの引数で設定します。
• 前準備:
    ◦ LoadCharDicで個別文字認識辞書を展開します。
    ◦ 日本語OCRの場合は、LoadKnowledgeDicで知識辞書を展開します。
• 終了時:
    ◦ UnloadCharDic()で個別文字認識辞書を開放し、日本語OCRの場合はUnloadKnowledgeDic()で知識辞書を開放します。
• 注意: バーコード認識のみを行う場合は、辞書の展開は不要です。帳票OCRで必要な初期化・終期化・グループ設定は不要です。
• 実行例:
    ◦ info配列に、イメージファイル名、入力解像度、処理方向、処理内容、枠の個数/最大文字数、枠の種類、記入方法、字種、知識辞書名称、限定文字列、処理速度などの詳細な情報を設定します。
    ◦ バーコード認識: info.SetValue(CInt(4), 7)で処理内容をバーコードに設定し、コードの種類などを指定します。
    ◦ 英数カナOCR: info.SetValue(CInt(1), 7)で処理内容を英数カナOCRに設定し、枠の種類や字種などを指定します。
    ◦ 日本語OCR: info.SetValue(CInt(2), 7)で処理内容を日本語OCRに設定し、知識辞書名や字種などを指定します。
    ◦ retVal = gOcrEx.RecogFieldEx(out tmp, info);を呼び出します。
3.4. 画像処理 (IGlyOcrEx)
GlyOcrExインターフェースに含まれる各種メソッドを使用します。様々な種類の2値化、傾き補正などの処理が可能です。
• 注意: OCR処理と異なり、辞書の展開などの前準備は不要です。
• メモリ管理: 各APIで生成されたイメージは内部で確保されたメモリブロックに格納され、そのハンドルがアプリケーションに返されます。イメージ使用後は、**GlobalFree**などを用いてアプリケーション側で開放する必要があります。
    ◦ C#: [DllImport("kernel32.dll", SetLastError=true)] static extern int GlobalFree (int hMem);を宣言して使用します。
• 実行例:
    ◦ 2値化処理 & MMR圧縮保存: GetBinaryImageで2値化を行い、OutputImageFileでTIFF形式で保存します。
    ◦ 傾き補正・黒枠除去 & JPEG圧縮保存: GetDocumentImageExで帳票の切り出しと傾き補正を行い、OutputImageFileでJPEG形式で保存します。
    ◦ イメージハンドル操作: イメージデータをメモリ上で直接受け渡す方法で、DIBハンドルからBitmapを作成し、表示・保存する方法を示します。GlobalLockとGlobalUnlockを使用します。
4. 認識結果について
RecogDocumentXXで処理を行った結果は、主に以下のプロパティ・メソッドで取得できます(IGlyOcrインターフェース)。
• DocumentResultEx: 候補を含めたすべての結果を取得します。
• DocumentResult: すべての結果を取得します。
• GetFieldResultEx: 指定フィールドの結果を取得します。
• GetFieldCharResult: 指定フィールド（順位）の1文字ごとの結果を取得します。
互換性のためにResultやGetFieldResultも残されていますが、詳細な結果が不要な場合に使用できます。認識結果の「読み」のみが必要な場合は、FieldNum、FieldResultなどのプロパティで簡単に取得できます。認識結果の詳細は取扱説明書を参照してください。
5. ビルド時の警告について
認識エンジンを参照設定したソリューションをビルドまたはリビルドする際に、IGlyOcrCインターフェースに関連する警告が表示される場合があります。これらの警告はIGlyOcrインターフェースおよびIGlyOcrExインターフェースの使用には影響しません。
また、サンプルコードで使用されている一部の文字列関数は、バッファオーバーフローの可能性から非推奨とされているため、C4996警告が表示されることがあります。これらはそのまま使用しても問題ありませんが、警告を解消するには、関数名に_sを付加した関数（例: _stprintfを_stprintf_sに）を使用するか、_CRT_SECURE_NO_WARNINGSを定義してください。
6. 64ビットOSでの利用について
認識エンジンは64ビットOSでも使用可能ですが、以下の点に注意が必要です。
• プロジェクトのプラットフォームを**「Win32」**に設定し、32ビットアプリケーションとしてビルドしてください。
• インストール先フォルダが「C:\Program Files (x86)」となっている場合があります。必要に応じてフォルダ名を変更してください。
--------------------------------------------------------------------------------