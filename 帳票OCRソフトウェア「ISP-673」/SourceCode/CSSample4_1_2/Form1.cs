using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;

namespace CSSample4_1_2
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
                // ライブラリの初期化
                Ocr.init(@"C:\Program Files\GLORY\GLYOCR4\FDic\サンプル");

                // グループの設定（処理するグループIDを指定します。）
                Ocr.SetGroup(1);		// グループID
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
                Ocr.ProcType = ProcTypeTypes.Form;	// 処理内容を「帳票判別のみ」に設定します。
                // 帳票判別＆ＯＣＲ
                int DocId = 0;
                DocumentResult docRes = Ocr.RecogDocument(ref DocId, @"C:\TestFile\TEST4-1.jpg");		// イメージファイル名

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
