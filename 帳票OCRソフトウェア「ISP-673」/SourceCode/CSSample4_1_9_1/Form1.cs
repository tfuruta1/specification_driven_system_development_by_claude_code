using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;

namespace CSSample4_1_9_1
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
                // 「帳票判別のみ使用」に設定
                Ocr.ProcType = ProcTypeTypes.Form;

                // 個別文字認識辞書"Cdic"、知識辞書"Kdic"のあるディレクトリ、
                //   プロジェクトのディレクトリを指定します。
                Ocr.init(@"C:\Program Files\GLORY\GLYOCR4\FDic\サンプル");

                // 帳票判別辞書のロード
                Ocr.LoadDocDict();
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
                string ImageFn = @"C:\TestFile\TEST4-1-9.jpg";		// イメージファイル名
                string ResultFn = @"C:\TestFile\TEST4-1-9(帳票端継承用).xml";	// 結果出力ファイル名 (注：既に存在する場合は一旦削除する必要があります。)
                ResultFileTypes kind = ResultFileTypes.Xml;						// xml形式で出力

                // 結果出力設定
                Ocr.SetResultFile(kind, ResultFn);

                // 帳票判別
                int pID = 0;
                DocumentResult docRes = Ocr.RecogDocument(ref pID, ImageFn);

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
