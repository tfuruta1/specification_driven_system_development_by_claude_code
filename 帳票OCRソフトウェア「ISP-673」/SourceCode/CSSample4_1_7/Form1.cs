using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;

namespace CSSample4_1_7
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
                // OCRのみ使用　（注）init前にセットしてください
                Ocr.ProcType = ProcTypeTypes.Ocr;

                // 個別文字認識辞書"Cdic"、知識辞書"Kdic"のあるディレクトリ、
                // プロジェクトのディレクトリを指定します。
                Ocr.init(@"C:\TestFile\TEST4-1-7");

                // 利用するOCRパラメータIDをリスト設定します。
                int[] id = new int[3];
                id[0] = 101;
                id[1] = 102;
                id[2] = 103;
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
                string ImageFn = @"C:\TestFile\TEST4-1-7\テストイメージ\TEST4-1-7.jpg";   // イメージファイル名

                // １パス目ＯＣＲ（個人 or 法人）
                int DocId = 101;
                DocumentResult docRes = Ocr.RecogDocument(ref DocId, ImageFn);
                if (docRes.Status != 0)
                {
                    MessageBox.Show("OCR　リジェクト");
                    return;
                }

                // 認識を切り分ける対象となる項目の結果を取得
                string fieldResult = "";
                foreach (FieldResult filedResTmp in docRes.FieldResults)
                {
                    if (filedResTmp.FieldID == 1)
                    {
                        fieldResult = filedResTmp.Result;
                        break;
                    }
                }
                if (string.IsNullOrEmpty(fieldResult))
                {
                    MessageBox.Show("認識リジェクト");
                    return;
                }

                // 結果に応じて場合分けして処理（２パス目）
                if (fieldResult == "個人")
                {
                    DocId = 102;
                    docRes = Ocr.RecogDocument(ref DocId, ImageFn);
                }
                else if (fieldResult == "法人")
                {
                    DocId = 103;
                    docRes = Ocr.RecogDocument(ref DocId, ImageFn);
                }
                else
                {
                    MessageBox.Show("認識リジェクト");
                    return;
                }

                // 認識結果表示
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
