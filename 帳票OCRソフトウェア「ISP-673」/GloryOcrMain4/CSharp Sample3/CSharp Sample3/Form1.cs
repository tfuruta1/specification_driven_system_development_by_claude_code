using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using GloryOcr4Lib;

namespace CSharp_Sample3
{
    public partial class Form1 : Form
    {
        // OCRエンジン
        private GlyOcr gloryOcrObj = new GlyOcr();
        private GlyOcrEx gloryOcrExObj = new GlyOcrEx();

        // ・ocrDicPath         OCRの辞書を読み込むためのフォルダ名をフルパスで指定
        // ・ocrProjectPath     プロジェクトを読み込むためフルパスを指定
        // ・oCRGroupID         OCRグループＩＤを設定
        // ・ocrImagePath       帳票イメージファイル名をフルパスで指定
        private const string ocrDicPath = @"C:\Program Files\GLORY\GLYOCR4";
        //private const string ocrProjectPath = @"C:\ProgramData\GLORY\GLYOCR3\FDic\サンプル";  // Windows Vista/7の場合
        private const string ocrProjectPath = @"C:\Program Files\GLORY\GLYOCR4\FDic\サンプル";
        private const int ocrGroupID = 2;
        private const string ocrImagePath = @"C:\テストイメージ\入会申込書（記入済み）.JPG";

        // ・OcrCDicPath       個別文字認識辞書を読み込むためのフォルダ名をフルパスで指定
        // ・OcrKDicPath       知識辞書を読み込むためのフォルダ名をフルパスを指定
        // ・OcrKDicName       知識辞書名
        // ・OcrImage1,OcrImage2       イメージファイル名をフルパスで指定

        // OnOcrSatrt2()は、英数カナＯＣＲ（field1.bmp）
        // OnOcrSatrt3()は、日本語（住所）ＯＣＲ（field2.bmp）

        private const string ocrCDicPath = @"C:\Program Files\GLORY\GLYOCR4\CDic";
        private const string ocrKDicPath = @"C:\Program Files\GLORY\GLYOCR4\KDic";
        private const string ocrKDicName = @"住所";
        private const string ocrImage1 = @"C:\テストイメージ\field1.jpg";
        private const string ocrImage2 = @"C:\テストイメージ\field2.jpg";

        public Form1()
        {
            InitializeComponent();
        }

        /// <summary>
        /// 帳票ＯＣＲ開始
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button1_Click(object sender, System.EventArgs e)
        {
            try
            {
                ocrResultList.Items.Clear();

                int ret = 0;
                string msg = "";

                // OCR初期化
                ret = gloryOcrObj.init(ocrDicPath, ocrProjectPath);
                if (ret != 1)
                {
                    msg = gloryOcrObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "OCR初期化", MessageBoxButtons.OK);
                    return;
                }

                // OCRグループ設定
                ret = gloryOcrObj.SetGroup(ocrGroupID);
                if (ret != 1)
                {
                    msg = gloryOcrObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "グループ設定", MessageBoxButtons.OK);
                    gloryOcrObj.exit();
                    return;
                }

                // OCR処理
                int id = 0;
                ret = gloryOcrObj.RecogDocumentFn(ref id, ocrImagePath);
                if (ret != 1)
                {
                    msg = gloryOcrObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "OCR処理", MessageBoxButtons.OK);
                    gloryOcrObj.exit();
                    return;
                }

                // 読み取り結果出力
                object result = null;
                result = gloryOcrObj.DocumentResult;
                if (result == null)
                {
                    MessageBox.Show("読み取り結果出力異常", "OCR処理", MessageBoxButtons.OK);
                    gloryOcrObj.exit();
                    return;
                }

                // 読み取り結果展開
                Array list = (Array)result;

                string dspStr;
                ocrResultList.Items.Add("====================================================================");

                // 帳票ＩＤ＆名称
                dspStr = "帳票ＩＤ：" + list.GetValue(0).ToString() + "   帳票名称：" + list.GetValue(1);
                ocrResultList.Items.Add(dspStr);

                // パラメータＩＤ＆名称
                dspStr = "パラメータＩＤ：" + list.GetValue(2).ToString() + "   パラメータ名称：" + list.GetValue(3);
                ocrResultList.Items.Add(dspStr);

                // フィールド数
                dspStr = "処理されたフィールド数：" + list.GetValue(7).ToString();

                ocrResultList.Items.Add("--------------------------------------------------------------------");

                // フィールド結果
                Array temp = (Array)list.GetValue(8);
                for (int i = 0; i < temp.Length; i++)
                {
                    Array fResult = (Array)temp.GetValue(i);

                    // フィールドＩＤ＆名称
                    dspStr = "フィールドＩＤ：" + fResult.GetValue(0).ToString() + "   フィールド名称：" + fResult.GetValue(1);
                    ocrResultList.Items.Add(dspStr);

                    // 読み取り結果
                    dspStr = "読み取り結果 :" + fResult.GetValue(7);
                    ocrResultList.Items.Add(dspStr);

                    ocrResultList.Items.Add("-----");
                }

                // ＯＣＲ終期化
                gloryOcrObj.exit();
            }
            catch (Exception)
            {
                MessageBox.Show("プログラムを終了します。", "エラー発生", MessageBoxButtons.OK);
            }
        }

        /// <summary>
        /// エリアＯＣＲ（英数カナＯＣＲ）
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button2_Click(object sender, System.EventArgs e)
        {
            try
            {
                ocrResultList.Items.Clear();

                int ret = 0;
                string msg = "";

                // 個別文字認識辞書の展開
                ret = gloryOcrExObj.LoadCharDic(ocrCDicPath);
                if (ret != 1)
                {
                    msg = gloryOcrExObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "個別文字認識辞書展開処理", MessageBoxButtons.OK);
                    return;
                }

                // フィールドOCR
                // 読み取りのための情報作成
                // パラメータ作成
                Array info = Array.CreateInstance(typeof(object), 15);

                info.SetValue(ocrImage1, 0);		// イメージファイル名
                info.SetValue((int)0, 1);			// イメージバッファハンドル
                info.SetValue((int)0, 2);			// イメージ高さ
                info.SetValue((int)0, 3);			// イメージ幅
                info.SetValue((int)0, 4);			// イメージ種類
                info.SetValue((int)240, 5);			// 解像度
                info.SetValue((int)0, 6);			// 処理方向
                info.SetValue((int)1, 7);			// 処理内容
                info.SetValue((int)7, 8);			// 枠の個数
                info.SetValue((int)3, 9);			// 枠の種類
                info.SetValue((int)2, 10);			// 記入方法
                info.SetValue((int)1, 11);			// 字種
                info.SetValue((string)"", 12);		// 知識辞書名
                info.SetValue((string)"", 13);		// 限定
                info.SetValue((int)1, 14);			// 処理速度

                // エリアＯＣＲ
                object result = null;
                ret = gloryOcrExObj.RecogFieldEx(out result, info);

                if (ret < 1)
                {
                    msg = gloryOcrExObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "エリアＯＣＲ１", MessageBoxButtons.OK);
                    gloryOcrExObj.UnloadCharDic();
                }
                else if (ret > 1)
                {
                    msg = gloryOcrExObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "エリアＯＣＲ１", MessageBoxButtons.OK);
                }

                // 読み取り結果展開
                Array list = (Array)result;

                // 読み取り結果出力
                string dspStr;
                ocrResultList.Items.Add("====================================================================");
                ocrResultList.Items.Add("");

                dspStr = "読み取り結果：" + list.GetValue(7) + " [" + list.GetValue(8) + "]  信頼度：" + list.GetValue(9).ToString();
                ocrResultList.Items.Add(dspStr);

                // 終期化
                gloryOcrExObj.UnloadCharDic();	// 個別文字認識辞書の解放
            }
            catch (Exception)
            {
                MessageBox.Show("プログラムを終了します。", "エラー発生", MessageBoxButtons.OK);
            }
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button3_Click(object sender, System.EventArgs e)
        {
            try
            {
                ocrResultList.Items.Clear();

                int ret = 0;
                string msg = "";

                // 個別文字認識辞書の展開
                ret = gloryOcrExObj.LoadCharDic(ocrCDicPath);
                if (ret != 1)
                {
                    msg = gloryOcrExObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "個別文字認識辞書展開処理", MessageBoxButtons.OK);
                    return;
                }

                // 知識辞書の展開
                ret = gloryOcrExObj.LoadKnowledgeDic(ocrKDicPath, ocrKDicName);
                if (ret != 1)
                {
                    msg = gloryOcrExObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "知識辞書展開処理", MessageBoxButtons.OK);
                    gloryOcrExObj.UnloadCharDic();
                    return;
                }

                // フィールドOCR
                // 読み取りのための情報作成
                // パラメータ作成
                Array info = Array.CreateInstance(typeof(object), 15);

                info.SetValue(ocrImage2, 0);				// イメージファイル名
                info.SetValue((int)0, 1);					// イメージバッファハンドル
                info.SetValue((int)0, 2);					// イメージ高さ
                info.SetValue((int)0, 3);					// イメージ幅
                info.SetValue((int)0, 4);					// イメージ種類
                info.SetValue((int)240, 5);					// 解像度
                info.SetValue((int)0, 6);					// 処理方向
                info.SetValue((int)2, 7);					// 処理内容
                info.SetValue((int)20, 8);					// 枠の個数
                info.SetValue((int)0, 9);					// 枠の種類
                info.SetValue((int)3, 10);					// 記入方法
                info.SetValue((int)0, 11);					// 字種
                info.SetValue((string)ocrKDicName, 12);		// 知識辞書名
                info.SetValue((string)"", 13);				// 限定
                info.SetValue((int)1, 14);					// 処理速度

                // エリアＯＣＲ
                object result = null;
                ret = gloryOcrExObj.RecogFieldEx(out result, info);

                if (ret < 1)
                {
                    msg = gloryOcrExObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "エリアＯＣＲ２", MessageBoxButtons.OK);
                    gloryOcrExObj.UnloadCharDic();
                    gloryOcrExObj.UnloadKnowledgeDic();
                }
                else if (ret > 1)
                {
                    msg = gloryOcrExObj.get_RejectCode2String(ret);
                    MessageBox.Show(msg, "エリアＯＣＲ２", MessageBoxButtons.OK);
                }

                // 読み取り結果展開
                Array list = (Array)result;

                // 読み取り結果出力
                string dspStr;
                ocrResultList.Items.Add("====================================================================");
                ocrResultList.Items.Add("");

                dspStr = "読み取り結果：" + list.GetValue(7) + " [" + list.GetValue(8) + "]  信頼度：" + list.GetValue(9).ToString();
                ocrResultList.Items.Add(dspStr);

                // 終期化
                gloryOcrExObj.UnloadKnowledgeDic();	// 知識辞書の解放
                gloryOcrExObj.UnloadCharDic();		// 個別文字認識辞書の解放
            }
            catch (Exception)
            {
                MessageBox.Show("プログラムを終了します。", "エラー発生", MessageBoxButtons.OK);
            }
        }

        private void button4_Click(object sender, System.EventArgs e)
        {
            this.Dispose();
        }

    }
}
