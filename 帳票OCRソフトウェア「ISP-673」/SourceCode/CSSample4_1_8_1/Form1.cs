using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;

namespace CSSample4_1_8_1
{
    public partial class Form1 : Form
    {

        private GOcr Ocr = new GOcr();

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            try
            {
                // 仮に帳票判別のみ使用に設定　（注）init前にセットしてください
                Ocr.ProcType = ProcTypeTypes.Form;
                // 個別文字認識辞書"Cdic"、知識辞書"Kdic"のあるディレクトリ、
                // プロジェクトのディレクトリを指定します。
                Ocr.init(@"C:\TestFile\TEST4-1-8");

                // 帳票判別辞書のロード
                Ocr.LoadDocDict();

                // 利用するOCRパラメータIDをリスト設定します。
                int[] id = new int[3];
                id[0] = 101;
                id[1] = 201;
                id[2] = 999901;
                // OCRパラメータのロード
                Ocr.LoadOcrParameter(id);
            }
            catch (GOcrException ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
            try
            {
                // グループの開放
                Ocr.FreeGroup();
                // ライブラリの終期化
                Ocr.exit();
            }
            catch (GOcrException ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            try
            {
                // 引数セット
                string ImageFn = @"C:\TestFile\TEST4-1-8\テストイメージ\TEST4-1-8.jpg";	// イメージファイル名

                // ★★ 処理フロー１の場合 ★★
                // 帳票判別
                int pID = 0;
                Ocr.ProcType = ProcTypeTypes.Form;		// 処理内容を「帳票判別のみ」に設定
                DocumentResult docRes = Ocr.RecogDocument(ref pID, ImageFn);

                // 帳票判別結果に応じてＯＣＲ
                Ocr.ProcType = ProcTypeTypes.Ocr;		// 処理内容を「OCRのみ」に設定
                if (docRes.Status == 0)
                {
                    // 判別アクセプト時は判別結果として得られた帳票ＩＤでＯＣＲ処理
                    docRes = Ocr.RecogDocument(ref pID, ImageFn);
                }
                else
                {
                    // 判別リジェクト時は特定のＯＣＲパラメータＩＤでＯＣＲ処理
                    pID = 999901;
                    docRes = Ocr.RecogDocument(ref pID, ImageFn);
                }

                // OCR結果表示
                string msg;
                if (docRes.Status == 0)
                {
                    msg = "【認識結果】" + Environment.NewLine;
                    // 帳票判別結果の帳票ＩＤ取得
                    msg = msg + "帳票ＩＤ：" + docRes.DocID + Environment.NewLine;
                    // 帳票判別結果の帳票名称取得
                    msg = msg + "帳票名称：" + docRes.DocName + Environment.NewLine;
                    // 帳票判別結果の帳票ステータス取得
                    msg = msg + "帳票ステータス：" + docRes.Status + Environment.NewLine;

                    // フィールドの結果取り出し
                    foreach (FieldResult filedRes in docRes.FieldResults)
                    {
                        // フィールドＩＤ取得
                        msg = msg + "フィールドＩＤ：" + filedRes.FieldID + Environment.NewLine;
                        // フィールド名称取得
                        msg = msg + "フィールド名称：" + filedRes.FieldName + Environment.NewLine;
                        // フィールド読み取り結果取得
                        msg = msg + "フィールド読み取り結果：" + filedRes.Result + Environment.NewLine;
                    }
                }
                else
                {
                    msg = "リジェクト：" + Ocr.GetRejectCode2String(docRes.Status);
                }
                MessageBox.Show(msg);
            }
            catch (GOcrException ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
    }
}
