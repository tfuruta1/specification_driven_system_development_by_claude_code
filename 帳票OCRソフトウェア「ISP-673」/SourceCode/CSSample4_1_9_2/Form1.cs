using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;
using System.Xml;

namespace CSSample4_1_9_2
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
                // 「ＯＣＲのみ使用」に設定
                Ocr.ProcType = ProcTypeTypes.Ocr;

                // 個別文字認識辞書"Cdic"、知識辞書"Kdic"のあるディレクトリ、
                // プロジェクトのディレクトリを指定します。
                Ocr.init(@"C:\Program Files\GLORY\GLYOCR4\FDic\サンプル");

                // 利用するOCRパラメータIDをリスト設定します。
                int[] id = new int[4];
                id[0] = 101;
                id[1] = 201;
                id[2] = 301;
                id[3] = 401;
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
                string ImageFn = @"C:\TestFile\TEST4-1-9.jpg";		// イメージファイル名
                string ResultFn = @"C:\TestFile\TEST4-1-9(帳票端継承用).xml";		// 結果出力ファイル名

                // 結果ファイルより帳票IDを取得
                int dID = GetDocID(ResultFn);

                // 結果ファイルより帳票の向きを取得
                int rotate = GetDocRotate(ResultFn);

                // 結果ファイルより帳票の４頂点を取得
                int[] cor = new int[8];
                GetDocCor(ResultFn, cor);

                // 帳票の向きを設定
                Ocr.ProcRotate = (RotateTypes)rotate;

                // 帳票の４頂点を設定
                Ocr.SetDocumentCorner(
                        new Point(cor[0], cor[1]), new Point(cor[2], cor[3]),
                        new Point(cor[4], cor[5]), new Point(cor[6], cor[7]));

                // ＯＣＲ
                DocumentResult docRes = Ocr.RecogDocument(ref dID, ImageFn);

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

        private int GetDocID(string filename)
        {
            XmlDocument xml = new XmlDocument();
            xml.Load(filename);
            foreach (XmlNode root in xml.ChildNodes)
            {
                if (root.Name == "読み取り結果")
                {
                    foreach (XmlNode rslt in root.ChildNodes)
                    {
                        if (rslt.Name == "DocResult")
                        {
                            return int.Parse(rslt.Attributes["ID"].Value);
                        }
                    }
                }
            }
            return 0;
        }

        private int GetDocRotate(string filename)
        {
            XmlDocument xml = new XmlDocument();
            xml.Load(filename);
            foreach (XmlNode root in xml.ChildNodes)
            {
                if (root.Name == "読み取り結果")
                {
                    foreach (XmlNode rslt in root.ChildNodes)
                    {
                        if (rslt.Name == "DocResult")
                        {
                            foreach (XmlNode item in rslt.ChildNodes)
                            {
                                if (item.Name == "DocRotate")
                                {
                                    return int.Parse(item.InnerText);
                                }
                            }
                        }
                    }
                }
            }
            return 0;
        }

        private void GetDocCor(string filename, int[] cor)
        {
            XmlDocument xml = new XmlDocument();
            xml.Load(filename);
            foreach (XmlNode root in xml.ChildNodes)
            {
                if (root.Name == "読み取り結果")
                {
                    foreach (XmlNode rslt in root.ChildNodes)
                    {
                        if (rslt.Name == "DocResult")
                        {
                            foreach (XmlNode item in rslt.ChildNodes)
                            {
                                if (item.Name == "DocCorner")
                                {
                                    foreach (XmlNode corner in item.ChildNodes)
                                    {
                                        switch (corner.Name)
                                        {
                                            case "TopLeft":
                                                cor[0] = int.Parse(corner.Attributes["x"].Value);
                                                cor[1] = int.Parse(corner.Attributes["y"].Value);
                                                break;
                                            case "TopRight":
                                                cor[2] = int.Parse(corner.Attributes["x"].Value);
                                                cor[3] = int.Parse(corner.Attributes["y"].Value);
                                                break;
                                            case "BottomRight":
                                                cor[4] = int.Parse(corner.Attributes["x"].Value);
                                                cor[5] = int.Parse(corner.Attributes["y"].Value);
                                                break;
                                            case "BottomLeft":
                                                cor[6] = int.Parse(corner.Attributes["x"].Value);
                                                cor[7] = int.Parse(corner.Attributes["y"].Value);
                                                break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
