using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using GloryOcr4Lib;

namespace CSharp_Sample1
{
    public partial class SampleForm : Form
    {
        //--------------------------------------------------------------------------------------------------
        // OCRオブジェクト作成
        // <解説>
        //  帳票OCRの機能を使用するときは、「ﾌﾟﾛｼﾞｪｸﾄ(P)」プルダウンメニューの「参照の追加(R)」項目で指定した
        //  帳票OCRのオブジェクトを作成しなければなりません。
        //  以下は帳票OCRのオブジェクトを作成しています。
        //--------------------------------------------------------------------------------------------------
        GlyOcr gloryOcrObj = new GlyOcr();

        //--------------------------------------------------------------------------------------------------
        // 定数定義
        // <注意>
        //  定数定義は以下のものを示しています。
        //
        //  ・ocrDicPath         OCRの辞書を読み込むためのフォルダ名をフルパスで指定
        //  ・ocrProjectPath     プロジェクトを読み込むためフルパスを指定
        //  ・ocrGroupID         OCRグループＩＤを設定
        //  ・ocrBlankCut        帳票イメージの背景を切り取るか否かを設定(0:否|1:切り取り)
        //  ・ocrImagePath       帳票イメージファイル名をフルパスで指定
        //--------------------------------------------------------------------------------------------------
        private const string ocrDicPath = @"C:\Program Files\GLORY\GLYOCR4";
        //private const string ocrProjectPath = @"C:\ProgramData\GLORY\GLYOCR3\FDic\サンプル";  // Windows Vista/7の場合
        private const string ocrProjectPath = @"C:\Program Files\GLORY\GLYOCR4\FDic\サンプル";
        private const int ocrGroupID = 2;
        private const int ocrBlankCut = 1;
        private const string ocrImagePath = @"C:\テストイメージ\入会申込書（記入済み）.JPG";


        public SampleForm()
        {
            InitializeComponent();
        }

        /// <summary>
        /// 帳票OCR終了
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void ocrEnd_Click(object sender, EventArgs e)
        {
            this.Dispose();
        }

        /// <summary>
        /// 帳票判別とOCR処理
        /// <解説>
        /// 初期化から帳票判別とOCR処理、終期化までの一連の処理を行わせます。
        /// このモジュールでは以下の帳票OCRのメソッド及びプロパティを使用しています。
        /// 
        /// ・SetProcType              帳票OCRで行う処理内容を指定します。
        /// ・init                     帳票OCRの初期化を行います。
        /// ・SetGroup                 帳票OCRのグループ設定を行います。
        /// ・BlankFlg                 帳票イメージの背景を切り取るかどうか設定しています。
        /// ・RecogDocumetFn           ファイルから読み込んだ帳票イメージにOCR処理をかけます。
        /// ・GetDocumentID            帳票判別で特定した帳票のＩＤを返します。
        /// ・GetDocumentName          帳票判別で特定した帳票の名称を返します。
        /// ・GetDocumentRejectCode    帳票判別結果を返します。
        /// ・GetFieldNum              OCR処理で読み取ったフィールド数を返します。
        /// ・GetFieldID               OCR処理で読み取ったフィールドＩＤを返します。
        /// ・GetFieldName             OCR処理で読み取ったフィールド名称を返します。
        /// ・GetFieldPosition         OCR処理で読み取ったフィールド位置を返します。
        /// ・GetFieldRejectCode       OCR処理で読み取ったフィールドの判定結果を返します。
        /// ・GetFieldResult           OCR処理で読み取ったフィールドの読み取り結果を返します。
        /// ・exit                     帳票OCRの終期化を行います。
        /// 
        /// <注意>
        /// 帳票OCRの各メソッド及びプロパティの解説は帳票OCR取り扱い説明書を参照してください。
        /// 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void ocrStart_Click(object sender, EventArgs e)
        {
            int ret;
            int ocrID = 0;
            int fieldMax;
            int fieldID = 0;
            int fx;
            int fy;
            int fwidth;
            int fheight;

            // OCR初期化
            ret = gloryOcrObj.init(ocrDicPath, ocrProjectPath);
            if (ret != 1)
            {
                MessageBox.Show("OCR初期化異常", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }

            // OCRグループ設定
            ret = gloryOcrObj.SetGroup(ocrGroupID);
            if (ret != 1)
            {
                MessageBox.Show("OCRグループ設定異常", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
                gloryOcrObj.exit();
                return;
            }

            // 背景切り取り指定(背景切り取り実行と指定)
            gloryOcrObj.BlankFlg = ocrBlankCut;

            // OCR処理
            ret = gloryOcrObj.RecogDocumentFn(ref ocrID, ocrImagePath);
            if (ret < 1)
            {
                MessageBox.Show("OCR処理異常", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
                gloryOcrObj.exit();
                return;
            }

            // 処理結果をリストボックスに出力

            // 帳票判別結果
            ocrResultList.Items.Clear();
            ocrResultList.Items.Add("//--------------------------------------------------------------------");

            // 帳票判別結果の帳票ＩＤ取得
            ocrResultList.Items.Add("帳票ＩＤ：" + gloryOcrObj.DocumentID.ToString());

            // 帳票判別結果の帳票名称取得
            ocrResultList.Items.Add("帳票名称：" + gloryOcrObj.DocumentName);

            // 帳票判別結果の帳票ステータス取得
            ocrResultList.Items.Add("帳票ステータス：" + gloryOcrObj.DocumentRejectCode.ToString());

            // 読み取ったフィールド数を取得
            fieldMax = gloryOcrObj.FieldNum;
            ocrResultList.Items.Add("帳票フィールド数：" + fieldMax.ToString());

            // フィールドの結果取り出し
            for (int i = 1; i <= fieldMax; i++)
            {
                // フィールドＩＤ取得
                fieldID = gloryOcrObj.get_FieldID(i);
                if (fieldID < 0)
                {
                    MessageBox.Show("フィールドＩＤ取得異常", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    gloryOcrObj.exit();
                    return;
                }
                ocrResultList.Items.Add("//--------------------------------------------------------------------");
                ocrResultList.Items.Add("フィールドＩＤ：" + fieldID.ToString());

                // フィールド名称取得
                ocrResultList.Items.Add("フィールド名称：" + gloryOcrObj.get_FieldName(fieldID));

                // 指定フィールドの入力画像中の位置の取得
                ret = gloryOcrObj.GetFieldPosition(fieldID, out fx, out fy, out fwidth, out fheight);
                if (fieldID < 0)
                {
                    MessageBox.Show("フィールドの入力画像中の位置の取得異常", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    gloryOcrObj.exit();
                    return;
                }
                ocrResultList.Items.Add("フィールドＸ：" + fx.ToString());
                ocrResultList.Items.Add("フィールドＹ：" + fy.ToString());
                ocrResultList.Items.Add("フィールド幅：" + fwidth.ToString());
                ocrResultList.Items.Add("フィールド高：" + fheight.ToString());

                // フィールドステータス取得
                ocrResultList.Items.Add("フィールド認識ステータス：" + gloryOcrObj.get_FieldRejectCode(fieldID));
                // フィールド読み取り結果取得
                ocrResultList.Items.Add("フィールド読み取り結果：" + gloryOcrObj.get_FieldResult(fieldID));
            }

            // OCR終期化
            gloryOcrObj.exit();
        }
    }
}
