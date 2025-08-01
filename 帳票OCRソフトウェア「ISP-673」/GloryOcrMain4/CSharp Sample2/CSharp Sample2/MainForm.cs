using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using GloryOcr4Lib;
using System.Runtime.InteropServices;
using System.IO;

namespace CSharp_Sample2
{
    public partial class MainForm : Form
    {
        private enum MemoryFlags
        {
            GMEM_DDESHARE = 0x2000,
            GMEM_DISCARDABLE = 0x100,
            GMEM_DISCARDED = 0x4000,
            GMEM_INVALID_HANDLE = 0x8000,
            GMEM_FIXED = 0x0,
            GMEM_LOCKCOUNT = 0xFF,
            GMEM_MODIFY = 0x80,
            GMEM_MOVEABLE = 0x2,
            GMEM_NODISCARD = 0x20,
            GMEM_NOCOMPACT = 0x10,
            GMEM_NOT_BANKED = 0x1000,
            GMEM_LOWER = GMEM_NOT_BANKED,
            GMEM_NOTIFY = 0x4000,
            GMEM_SHARE = 0x2000,
            GMEM_VALID_FLAGS = 0x7F72,
            GMEM_ZEROINIT = 0x40,
            GPTR = (GMEM_FIXED | GMEM_ZEROINIT)
        }

        [DllImport("kernel32.dll", SetLastError = true)]
        static extern int GlobalAlloc(int wFlags, int dwBytes);
        [DllImport("kernel32.dll", SetLastError = true)]
        static extern IntPtr GlobalLock(int hMem);
        [DllImport("kernel32.dll", SetLastError = true)]
        static extern int GlobalUnlock(IntPtr hMem);
        [DllImport("kernel32.dll", SetLastError = true)]
        static extern int GlobalFree(int hMem);
        [DllImport("kernel32.dll", SetLastError = true)]
        static extern int GlobalSize(int hMem);

        private object Ocr_result = null;				// 読取結果
        private int F_index = 0;						// 選択フィールド番号
        private int S_index = 0;						// //文字置き換えインデックス

        GlyOcr Gocr = new GlyOcr();			// OCRオブジェクト生成

        // 辞書フォルダ
        private const string DIR1 = @"C:\Program Files\GLORY\GLYOCR4";
        // プロジェクトフォルダ
        private const string DIR2 = @"C:\Program Files\GLORY\GLYOCR4\FDic\サンプル";
        // イメージファイル名
        private const string SHEETNAME = @"C:\テストイメージ\入会申込書（記入済み）.jpg";

        private Bitmap bitmap1 = null;					// pictureBox1用イメージ
        private Rectangle[] rectangle1 = null;			// pictureBox1用枠描画座標
        private Bitmap bitmap2 = null;					// pictureBox2用イメージ
        private Rectangle[] rectangle2 = null;			// pictureBox2用枠描画座標
        private string[] str2 = null;					// pictureBox2用描画文字列
        private bool[] color2 = null;					// pictureBox2用文字描画色
        private Rectangle[] markrect2 = null;			// pictureBox2用マーク描画座標
        private bool[] markcolor2 = null;				// pictureBox2用マーク描画色

        private Point mouseDown;						// MouseDownポイント

        public MainForm()
        {
            InitializeComponent();
        }

        /// <summary>
        /// DIB⇒System.Bitmapオブジェクト
        /// </summary>
        /// <param name="imageMem"></param>
        /// <returns></returns>
        private Bitmap DIBToSystemBitmap(int imageMem)
        {
            int size = GlobalSize(imageMem);
            byte[] buff = new byte[size + 14];

            IntPtr handle = GlobalLock(imageMem);
            Marshal.Copy((IntPtr)handle, buff, 14, size);

            buff[0] = 0x42;	// B
            buff[1] = 0x4D;	// M
            byte[] bfSize = BitConverter.GetBytes(buff.Length);
            buff[2] = bfSize[0];
            buff[3] = bfSize[1];
            buff[4] = bfSize[2];
            buff[5] = bfSize[3];

            buff[6] = 0x00;
            buff[7] = 0x00;
            buff[8] = 0x00;
            buff[9] = 0x00;

            int offset = 1078;	// ビットマップヘッダサイズ
            byte[] bfOffset = BitConverter.GetBytes(offset);
            buff[10] = bfOffset[0];
            buff[11] = bfOffset[1];
            buff[12] = bfOffset[2];
            buff[13] = bfOffset[3];

            MemoryStream ms = new MemoryStream(buff);
            Bitmap bmp = new Bitmap(ms);

            GlobalUnlock(handle);

            return bmp;
        }

        /// <summary>
        /// 矩形描画座標計算
        /// </summary>
        /// <param name="area"></param>
        /// <returns></returns>
        private Rectangle CalcDrawRect(Rectangle area, double factor)
        {
            double left = (double)area.Left * factor;
            double top = (double)area.Top * factor;
            double width = (double)area.Width * factor;
            double height = (double)area.Height * factor;
            return new Rectangle((int)left, (int)top, (int)width, (int)height);
        }

        private void pictureBox1_Paint(object sender, PaintEventArgs e)
        {
            if (bitmap1 == null)
                return;

            //--------------------------------------------
            // 画像表示
            //--------------------------------------------

            // アスペクト比を計算
            double xx = (double)pictureBox1.Width / (double)bitmap1.Width;
            double yy = (double)pictureBox1.Height / (double)bitmap1.Height;
            double factor = 100;
            if (xx < yy)
            {
                factor = xx;
            }
            else
            {
                factor = yy;
            }
            xx = bitmap1.Width * factor;
            yy = bitmap1.Height * factor;
            RectangleF rectF = new RectangleF(0, 0, (float)xx, (float)yy);

            // 拡大縮小時の補間方法指定
            e.Graphics.InterpolationMode =
                System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
            // 描画
            e.Graphics.DrawImage(bitmap1, rectF);

            //--------------------------------------------
            // 枠表示
            //--------------------------------------------
            if (rectangle1 != null)
            {
                //Penオブジェクトの作成(幅3の赤色)
                Pen p = new Pen(Color.Red, 3);
                //長方形座標計算
                foreach (Rectangle obj in rectangle1)
                {
                    Rectangle rect = CalcDrawRect(obj, factor);
                    e.Graphics.DrawRectangle(p, rect);
                }
                //リソースを開放する
                p.Dispose();
            }
        }

        private void pictureBox2_Paint(object sender, PaintEventArgs e)
        {
            if (bitmap2 == null)
                return;

            //--------------------------------------------
            // 画像表示
            //--------------------------------------------

            // アスペクト比を計算
            double xx = (double)pictureBox2.Width / (double)bitmap2.Width;
            double yy = (double)pictureBox2.Height / (double)bitmap2.Height;
            double factor = 100;
            if (xx < yy)
            {
                factor = xx;
            }
            else
            {
                factor = yy;
            }
            xx = bitmap2.Width * factor;
            yy = bitmap2.Height * factor;
            RectangleF rectF = new RectangleF(0, 0, (float)xx, (float)yy);

            // 拡大縮小時の補間方法指定
            e.Graphics.InterpolationMode =
                System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
            // 描画
            e.Graphics.DrawImage(bitmap2, rectF);

            //--------------------------------------------
            // 文字 & 枠表示
            //--------------------------------------------
            if (rectangle2 != null)
            {
                //フォントオブジェクトの作成
                Font fnt = new Font("ＭＳ Ｐゴシック", 20);
                //Penオブジェクトの作成(幅1の赤色)
                Pen p = new Pen(Color.Red, 1);

                //長方形座標計算
                for (int i = 0; i < rectangle2.Length; i++)
                {
                    Rectangle rect = CalcDrawRect(rectangle2[i], factor);
                    e.Graphics.DrawRectangle(p, rect);

                    //文字列を表示する範囲を指定する
                    SizeF sizeF = e.Graphics.MeasureString(str2[i], fnt);
                    rect = new Rectangle(rect.X, rect.Y - (int)sizeF.Height - 1, (int)sizeF.Width, (int)sizeF.Height);

                    //rectの四角を描く
                    if (color2[i])
                    {
                        e.Graphics.FillRectangle(new SolidBrush(Color.FromArgb(0, 0, 255)), rect);
                    }
                    else
                    {
                        e.Graphics.FillRectangle(new SolidBrush(Color.FromArgb(255, 109, 29)), rect);
                    }
                    //文字を書く
                    e.Graphics.DrawString(str2[i], fnt, Brushes.White, rect);
                }

                //リソースを開放する
                p.Dispose();
                //リソースを開放する
                fnt.Dispose();
            }

            if (markrect2 != null)
            {
                //長方形座標計算
                for (int i = 0; i < markrect2.Length; i++)
                {
                    Pen pBlue = new Pen(Color.Blue, 5);
                    Pen pRed = new Pen(Color.Red, 1);

                    Rectangle rect = CalcDrawRect(markrect2[i], factor);
                    if (markcolor2[i])
                    {
                        e.Graphics.DrawRectangle(pBlue, rect);
                    }
                    else
                    {
                        e.Graphics.DrawRectangle(pRed, rect);
                    }
                    pBlue.Dispose();
                    pRed.Dispose();
                }
            }
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            //++　処理内容の設定　++
            //+　 処理内容を設定します。
            //+　 ProcType as long     0:OCR+帳票判別　1:帳票判別のみ　2:OCRのみ
            Gocr.ProcType = 0;


            //++　帳票ＯＣＲライブラリの初期化　++
            //+　 辞書フォルダとプロジェクトフォルダを指定します。
            //+   init("辞書フォルダ","プロジェクトフォルダ") as long
            int state = Gocr.init(DIR1, DIR2);
            if (state != 1)
            {
                MessageBox.Show(Gocr.get_RejectCode2String(state));
                return;
            }

            //++　グループの設定　++
            //+   処理するグループを設定し、帳票種類判別辞書、ＯＣＲパラメータを展開します。
            //+   SetGroup(処理するグループＩＤ) as long
            state = Gocr.SetGroup(2);
            if (state != 1)
            {
                MessageBox.Show(Gocr.get_RejectCode2String(state));
            }
        }

        /// <summary>
        /// [ＯＣＲ]   ＯＣＲを実行する
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void buttonOcr_Click(object sender, EventArgs e)
        {
            int state;		// エラーコード
            int docID = 0;	// 帳票ID

            // ＯＣＲ結果　初期化
            Ocr_result = null;

            F_index = -1;	// 選択フィールド番号

            //++  帳票ＯＣＲ  ++
            //+   帳票ＯＣＲを行います。
            //+   RecogDocumentFn(帳票ＩＤ出力用変数,イメージファイル名)
            state = Gocr.RecogDocumentFn(ref docID, SHEETNAME);

            if (state == 0)
            {
                // リジェクト
                //++  リジェクトコード  ++
                //+　 リジェクトコードを取得します。
                //+   DocumentRejectCode as long
                state = Gocr.DocumentRejectCode;
                MessageBox.Show(Gocr.get_RejectCode2String(state));
                return;
            }
            else if (state != 1)
            {
                // エラー
                MessageBox.Show(Gocr.get_RejectCode2String(state));
                return;
            }

            //++　全読取結果　++
            //+   全読取結果を取得します
            //+   DocumentResultEx as Variant
            Ocr_result = Gocr.DocumentResultEx;

            if (Ocr_result == null)
            {
                MessageBox.Show("結果格納失敗");
                return;
            }

            F_index = 0;	// 選択フィールド番号

            // 最初のフィールドを選択 Func
            Dsp_ID1();

        }

        /// <summary>
        /// 最初のフィールドを選択
        /// </summary>
        private void Dsp_ID1()
        {
            // 認識結果がない、選択フィールド番号が-1の場合は、フィールド選択しない
            if (Ocr_result == null || F_index == -1)
            {
                return;
            }

            // フィールド数
            Array list = (Array)Ocr_result;
            int fNum = (int)list.GetValue(7);

            // 選択フィールド番号が認識フィールド数より多い場合は、フィールド選択しない
            if (F_index > fNum)
            {
                return;
            }

            // フィールドイメージ＆結果表示 Func
            DspResult();
        }
        /// <summary>
        /// フィールドリペイント
        /// </summary>
        private void Dsp_RePaint()
        {
            // 認識結果がない、選択フィールド番号が-1の場合は、フィールド選択しない
            if (Ocr_result == null || F_index == -1)
            {
                return;
            }

            // フィールド結果保存 Func
            Save_Result();

            // フィールド数
            Array list = (Array)Ocr_result;
            int fNum = (int)list.GetValue(7);

            // 選択フィールド番号が認識フィールド数より多い場合は、フィールド選択しない
            if (F_index > fNum)
            {
                return;
            }

            // フィールドイメージ＆結果表示 Func
            DspResult();
        }

        /// <summary>
        /// [次ヘ]     次のフィールド結果を選択
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void buttonNext_Click(object sender, EventArgs e)
        {
            // 認識結果がない、選択フィールド番号が-1の場合は、フィールド選択しない
            if (Ocr_result == null || F_index == -1)
            {
                return;
            }

            // フィールド結果保存 Func
            Save_Result();

            // フィールド数
            Array list = (Array)Ocr_result;
            int fNum = (int)list.GetValue(7);

            // 選択フィールド番号が認識フィールド数より多い場合は、フィールド選択しない
            if (F_index + 1 >= fNum)
            {
                return;
            }
            F_index = F_index + 1;

            // フィールドイメージ＆結果表示 Func
            DspResult();

        }

        /// <summary>
        /// ［戻る]     １つ前のフィールド結果を選択
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>

        private void buttonReturn_Click(object sender, EventArgs e)
        {
            // 認識結果がない、選択フィールド番号が-1の場合は、フィールド選択しない
            if (Ocr_result == null || F_index == -1)
            {
                return;
            }

            // フィールド結果保存 Func
            Save_Result();

            // フィールド数
            Array list = (Array)Ocr_result;
            int fNum = (int)list.GetValue(7);

            // 選択フィールド番号が認識フィールド数より多い場合は、フィールド選択しない
            if (F_index - 1 < 0)
            {
                return;
            }

            F_index = F_index - 1;

            // フィールドイメージ＆結果表示 Func
            DspResult();

        }

        /// <summary>
        /// フィールド結果保存
        /// </summary>
        private void Save_Result()
        {
            Array F_result;	// フィールド情報

            // フィールド結果保存
            Array list = (Array)Ocr_result;
            Array temp = (Array)list.GetValue(8);
            F_result = (Array)temp.GetValue(F_index);
            F_result.SetValue(textResult.Text, 7);
            temp.SetValue(F_result, F_index);
            list.SetValue(temp, 8);
        }

        /// <summary>
        /// フィールドイメージ＆結果表示（推奨表示パターン）
        /// 認識モードごとに表示方法を変える
        /// </summary>
        private void DspResult()
        {
            rectangle2 = null;
            str2 = null;
            color2 = null;
            markrect2 = null;
            markcolor2 = null;

            Array F_result;							// フィールド情報
            Array temp;

            Array ar = (Array)Ocr_result;
            temp = (Array)ar.GetValue(8);			// フィールド情報
            F_result = (Array)temp.GetValue(F_index);

            // 帳票・フィールド領域表示
            DspSheet();

            // --結果表示--

            // 認識モード：英数カタカナOCR　かつ　定型情報なし　または　フリー記入の場合、「？」を含む場合は結果を表示しない
            // 認識モード：認識なし　の場合、結果は何も表示しない
            if ((int)F_result.GetValue(10) == 1 && ((int)F_result.GetValue(11) == 0 || (int)F_result.GetValue(11) == 2))
            {
                string str = F_result.GetValue(7).ToString();
                if (str.IndexOf("?") == -1)
                {
                    textResult.Text = str;
                }
                else
                {
                    textResult.Text = "";
                }
            }
            else if ((int)F_result.GetValue(10) == 0)
            {
                textResult.Text = "";
            }
            else
            {
                textResult.Text = F_result.GetValue(7).ToString();
            }

            // 認識モード＝マーク位置検出 のとき、結果入力禁止
            if ((int)F_result.GetValue(10) == 3)
            {
                textResult.ReadOnly = true;
            }
            else
            {
                textResult.ReadOnly = false;
            }

            // --フィールドイメージ表示--

            // 認識モードによる分岐
            switch ((int)F_result.GetValue(10))
            {
                case 0:					// 認識なし
                    // 表示 Func
                    Goto_Another(F_result);
                    break;
                case 1:					// 英数カタカナＯＣＲ
                    // 定型情報の有無・種類による分岐
                    if ((int)F_result.GetValue(11) == 0)
                    {
                        // 定型情報なし
                        Goto_Another(F_result);
                    }
                    else if ((int)F_result.GetValue(11) == 1)
                    {
                        // 個別枠あり
                        Goto_OCR_EN_Frame(F_result);
                    }
                    else if ((int)F_result.GetValue(11) == 2)
                    {
                        // フリー記入
                        Goto_OCR_KN(F_result);
                    }
                    break;
                case 2:					// 知識辞書・日本語ＯＣＲ
                    Goto_OCR_KN(F_result);
                    break;
                case 3:					// マーク位置検出
                    // 全結果出力又は、マーク位置検出 表示への分岐
                    if ((int)F_result.GetValue(12) == 0 && (int)F_result.GetValue(13) == 0)
                    {
                        // 全結果出力　表示 Func
                        Goto_OMR_OnOff(F_result);
                    }
                    else
                    {
                        // マーク位置検出　表示 Func
                        Goto_OMR(F_result);
                    }
                    break;
                case 4:					// バーコード
                    Goto_Another(F_result);
                    break;
            }

            if ((int)F_result.GetValue(10) == 2 && (int)F_result.GetValue(13) == 3)
            {
                buttonDetails.Text = "詳細";
                buttonDetails.Enabled = true;
            }
            else if ((int)F_result.GetValue(10) == 2 && (int)F_result.GetValue(13) == 2)
            {
                buttonDetails.Text = "〒";
                buttonDetails.Enabled = true;
            }
            else
            {
                buttonDetails.Enabled = false;
            }
        }

        /// <summary>
        /// 帳票・フィールド領域表示
        /// </summary>
        private void DspSheet()
        {
            // イメージロード
            bitmap1 = new Bitmap(SHEETNAME);

            Array ar1 = (Array)Ocr_result;
            Array ar2 = (Array)ar1.GetValue(8);
            Array F_result = (Array)ar2.GetValue(F_index);

            rectangle1 = new Rectangle[1];

            int x = (int)F_result.GetValue(2);
            int y = (int)F_result.GetValue(3);
            int w = (int)F_result.GetValue(4);
            int h = (int)F_result.GetValue(5);
            rectangle1[0] = new Rectangle(x, y, w, h);

            pictureBox1.Invalidate();
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%      英数カタカナＯＣＲ（個別枠あり）
        //%--------------------------------------------------------------------
        //%  推奨表示パターン
        //%
        //%　フィールドイメージは文字・背景・定型情報除去の３値イメージを使用
        //%　セグメント領域、結果を表示（結果はセグメント単位で表示）
        //%　セグメント領域内右クリックで、認識候補文字の選択ができる
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //================================================================
        //       (I)　F_result　 　　フィールド情報
        //================================================================
        private void Goto_OCR_EN_Frame(Array F_result)
        {
            int state;		//エラーコード
            int MyDib;		//フィールドイメージ
            int Fid;		//フィールドID

            Fid = (int)F_result.GetValue(0);	// フィールドID

            //++ フィールドイメージ取得 ++
            //+　フィールドイメージを取得します。
            //+　GetRecogFieldImage(フィールドID,モード,フィールドイメージ)　モード　0：濃淡　1：２値　2：３値
            state = Gocr.GetRecogFieldImage(Fid, 2, out MyDib);

            if (state != 1)
            {
                MessageBox.Show(Gocr.get_RejectCode2String(state));
                return;
            }

            //フィールドイメージ表示　Func
            DspFildeImage(MyDib);

            //セグメント領域と結果表示　Func
            DspSegResult(Fid);

            //イメージ解放
            GlobalFree(MyDib);
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%      英数カタカナ（個別枠なし）・
        //%      知識辞書・漢字ＯＣＲ（住所・名前・一般辞書・ユーザー定義辞書）
        //%--------------------------------------------------------------------
        //%　推奨表示パターン
        //%
        //%  フィールドイメージは定型情報なしの場合は濃淡イメージ、
        //%　定型情報がある場合は文字・背景・定型情報除去の３値イメージを使用
        //%　イメージ上右クリックで、認識候補文字列の選択ができる
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //================================================================
        //       (I)　F_result　 　　フィールド情報
        //================================================================
        private void Goto_OCR_KN(Array F_result)
        {
            int state;		//エラーコード
            int MyDib;		//フィールドイメージ
            int Fid;		//フィールドID

            Fid = (int)F_result.GetValue(0);	// フィールドID

            //定型情報　0：なし　0以外：あり　　　　定型情報がある場合、定型情報を除去したイメージを取得できる
            //　　　　　　　　　　　　　　　　　　  定型情報がない場合、濃淡イメージしか取得できない
            switch ((int)F_result.GetValue(10))
            {
                case 0:
                    //++ フィールドイメージ取得 ++
                    //+　フィールドイメージを取得します。
                    //+　GetRecogFieldImage(フィールドID,モード,イメージ取得用)　モード　0：濃淡　1：２値　2：３値
                    state = Gocr.GetRecogFieldImage(Fid, 0, out MyDib);
                    break;
                default:
                    //++ フィールドイメージ取得 ++
                    //+　フィールドイメージを取得します。
                    //+　GetRecogFieldImage(フィールドID,モード,イメージ取得用)　モード　0：濃淡　1：２値　2：３値
                    state = Gocr.GetRecogFieldImage(Fid, 2, out MyDib);
                    break;
            }

            if (state != 1)
            {
                MessageBox.Show(Gocr.get_RejectCode2String(state));
                return;
            }

            //フィールドイメージ表示　Func
            DspFildeImage(MyDib);

            //イメージ解放
            GlobalFree(MyDib);
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%      マーク位置検出（マーク位置検出）
        //%--------------------------------------------------------------------
        //%　推奨表示パターン
        //%
        //%  フィールドイメージは定型情報なしの場合は濃淡イメージ、
        //%　定型情報がある場合は文字・背景・定型情報除去の３値イメージを使用
        //%　マーク位置を表示　検出位置には太枠で表示
        //%　修正は、イメージ上左クリックで行う
        //%　クリックの度チェック／チェックはずすが切り替わる
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //================================================================
        //       (I)　F_result　 　　フィールド情報
        //================================================================
        private void Goto_OMR(Array F_result)
        {
            int state;		//エラーコード
            int MyDib;		//フィールドイメージ
            int Fid;		//フィールドID
            int Mnum;		//マーク個数

            bool[] Omr_Resu;	//検出領域

            Fid = (int)F_result.GetValue(0);	// フィールドID
            Mnum = (int)F_result.GetValue(11);	// マーク個数

            //++ フィールドイメージ取得 ++
            //+　フィールドイメージを取得します。
            //+　GetRecogFieldImage(フィールドID,モード,イメージ取得用)　モード　0：濃淡　1：２値　2：３値
            state = Gocr.GetRecogFieldImage(Fid, 2, out MyDib);

            if (state != 1)
            {
                //++ フィールドイメージ取得 ++
                //+　フィールドイメージを取得します。
                //+　GetRecogFieldImage(フィールドID,モード,イメージ取得用)　モード　0：濃淡　1：２値　2：３値
                state = Gocr.GetRecogFieldImage(Fid, 0, out MyDib);

                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }
            }

            //フィールドイメージ表示　Func
            DspFildeImage(MyDib);

            //マーク位置検出領域取得 Func
            Omr_Resu = Find_Check_OMR(textResult.Text, Mnum, Fid);

            //マーク記入領域表示
            DspOMRResult(Fid, Mnum, Omr_Resu);

            //イメージ解放
            GlobalFree(MyDib);
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%      マーク位置検出（全結果表示）
        //%--------------------------------------------------------------------
        //%　推奨表示パターン
        //%
        //%  フィールドイメージは定型情報なしの場合は濃淡イメージ、
        //%　定型情報がある場合は文字・背景・定型情報除去の３値イメージを使用
        //%　マーク位置を表示　検出位置には太枠で表示
        //%　修正は、イメージ上左クリックで行う
        //%　クリックの度ＯＮ／ＯＦＦが切り替わる
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //================================================================
        //       (I)　F_result　 　　フィールド情報
        //================================================================
        private void Goto_OMR_OnOff(Array F_result)
        {
            int state;		//エラーコード
            int MyDib;		//フィールドイメージ
            int Fid;		//フィールドID
            int Mnum;		//マーク個数

            bool[] Omr_Resu;	//検出領域

            Fid = (int)F_result.GetValue(0);	// フィールドID
            Mnum = (int)F_result.GetValue(11);	// マーク個数

            //++ フィールドイメージ取得 ++
            //+　フィールドイメージを取得します。
            //+　GetRecogFieldImage(フィールドID,モード,イメージ取得用)　モード　0：濃淡　1：２値　2：３値
            state = Gocr.GetRecogFieldImage(Fid, 2, out MyDib);

            if (state != 1)
            {
                //++ フィールドイメージ取得 ++
                //+　フィールドイメージを取得します。
                //+　GetRecogFieldImage(フィールドID,モード,イメージ取得用)　モード　0：濃淡　1：２値　2：３値
                state = Gocr.GetRecogFieldImage(Fid, 0, out MyDib);

                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }
            }

            //フィールドイメージ表示　Func
            DspFildeImage(MyDib);

            //マーク位置検出領域取得 Func
            Omr_Resu = Find_Check_ONOFF(textResult.Text, Mnum);

            //マーク記入領域表示
            DspOMRResult(Fid, Mnum, Omr_Resu);

            //イメージ解放
            GlobalFree(MyDib);
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%      英数カタカナ（定型情報なし）・バーコード　・　認識処理なし
        //%--------------------------------------------------------------------
        //%　推奨表示パターン
        //%
        //%  フィールドイメージは濃淡イメージを使用
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //================================================================
        //       (I)　F_result　 　　フィールド情報
        //================================================================
        private void Goto_Another(Array F_result)
        {
            int state;		//エラーコード
            int MyDib;		//フィールドイメージ
            int Fid;		//フィールドID

            Fid = (int)F_result.GetValue(0);	// フィールドID

            //++ フィールドイメージ取得 ++
            //+　フィールドイメージを取得します。
            //+　GetRecogFieldImage(フィールドID,モード,イメージ取得用)　モード　0：濃淡　1：２値　2：３値
            //　 ---バーコード認識／認識処理なし／定型情報なし の場合は濃淡イメージの取得のみ可能
            state = Gocr.GetRecogFieldImage(Fid, 0, out MyDib);

            if (state != 1)
            {
                MessageBox.Show(Gocr.get_RejectCode2String(state));
                return;
            }

            //フィールドイメージ表示　Func
            DspFildeImage(MyDib);

            //イメージ解放
            GlobalFree(MyDib);
        }

        //================================================================
        //          フィールドイメージ表示（フィット表示）
        //
        //       (I)　MyDib　 　　フィールドイメージ
        //================================================================
        private void DspFildeImage(int MyDib)
        {
            bitmap2 = DIBToSystemBitmap(MyDib);
            pictureBox2.Invalidate();
        }

        //================================================================
        //       セグメント領域と結果表示
        //
        //       (I)　Fid　 　　フィールドID
        //================================================================
        private void DspSegResult(int Fid)
        {
            int state;		//エラーコード
            Array Resu;		//文字列候補情報
            Array S_Temp;	//セグメント情報
            int SegNum;		//セグメント数
            string Char_;	//セグメント結果

            //++ １候補文字列のセグメント結果取得 ++
            //+　第Ｎ位の候補文字列のセグメント結果を取得します。
            //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
            object result;
            state = Gocr.GetFieldCharResult(Fid, 1, out result);

            if (state != 1)
            {
                MessageBox.Show(Gocr.get_RejectCode2String(state));
                return;
            }

            Resu = (Array)result;
            SegNum = (int)Resu.GetValue(4);

            rectangle2 = new Rectangle[SegNum];
            str2 = new string[SegNum];
            color2 = new bool[SegNum];

            Array temp = (Array)Resu.GetValue(5);
            for (int i = 0; i < SegNum; i++)
            {
                S_Temp = (Array)temp.GetValue(i);

                // 枠座標計算
                int x = (int)S_Temp.GetValue(3);
                int y = (int)S_Temp.GetValue(4);
                int w = (int)S_Temp.GetValue(5);
                int h = (int)S_Temp.GetValue(6);
                rectangle2[i] = new Rectangle(x, y, w, h);

                //認識結果を１文字ごとに分割 Func
                Char_ = (string)S_Temp.GetValue(1);
                if (Char_ != "")
                {
                    Char_ = Char_.Substring(0, 1);
                }

                if (Char_ != " " && Char_ != "　")
                {
                    str2[i] = Char_;
                    if ((int)S_Temp.GetValue(2) > 2)
                    {
                        color2[i] = true;
                    }
                    else
                    {
                        color2[i] = false;
                    }
                }
            }
            pictureBox2.Invalidate();
        }

        //================================================================
        //         認識結果を１文字ごとに分割
        //
        //       (O)　Dive_Char　　 分割認識結果（１文字）
        //       (I)　index　 　　　セグメントインデックス
        //================================================================
        private string Dive_Char(int index)
        {
            string wk = textResult.Text;

            Array obj = (Array)Ocr_result;
            Array temp = (Array)obj.GetValue(8);
            Array F_result = (Array)temp.GetValue(F_index);

            if ((int)F_result.GetValue(10) == 2 && (int)F_result.GetValue(13) == 2)
            {
                //日本語ＯＣＲ + 氏名
                wk = wk.Replace(" ", "");
                return wk.Substring(index, (int)1);
            }
            else
            {
                return wk.Substring(index, (int)1);
            }
        }

        //================================================================
        //       マーク記入領域表示
        //
        //       (I)　Fid　 　　　フィールドID
        //       (I)　Mnum　　　　マーク数
        //       (I)　Omr_Resu　　マーク情報
        //================================================================
        private void DspOMRResult(int Fid, int Mnum, bool[] Omr_Resu)
        {
            object Resu;		//マーク情報
            if (Mnum < 1)
            {
                return;
            }

            markrect2 = new Rectangle[Mnum];
            markcolor2 = new bool[Mnum];

            //ＯＭＲ領域とその結果を表示
            for (int i = 0; i < Mnum; i++)
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                int state = Gocr.GetFieldCharResult(Fid, i + 1, out Resu);

                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                Array temp = (Array)Resu;
                temp = (Array)temp.GetValue(5);
                Array M_temp = (Array)temp.GetValue(0);

                int x = (int)M_temp.GetValue(3);
                int y = (int)M_temp.GetValue(4);
                int w = (int)M_temp.GetValue(5);
                int h = (int)M_temp.GetValue(6);
                markrect2[i] = new Rectangle(x, y, w, h);
                markcolor2[i] = Omr_Resu[i];
            }
        }

        //================================================================
        //　マーク位置検出結果より検出された領域を抽出（マーク位置検出）
        //　①結果を分割
        //
        //       (O)　Find_Check_OMR マーク結果
        //       (I)　result　　　　　認識結果
        //       (I)　Mnum　　　　　　マーク数
        //       (I)　Fid　 　　　　　フィールドID
        //================================================================
        private bool[] Find_Check_OMR(string result, int Mnum, int Fid)
        {
            bool[] Omr_Resu = new bool[Mnum];	// 検索結果
            int s_idx;							//検索開始インデックス
            int e_idx;							//検索終了インデックス
            int s_len;							//文字列の長さ
            string str;							//分割結果
            int index;							//インデックス

            for (int i = 0; i < Mnum; i++)
            {
                Omr_Resu[i] = false;
            }

            if (result == "")
            {
                return Omr_Resu;
            }

            s_idx = 0;
            e_idx = result.IndexOf(",");

            if (e_idx > 0)
            {
                while (true)
                {
                    s_len = e_idx - s_idx;
                    str = result.Substring(s_idx, s_len);

                    // ②結果より領域を探す Func
                    index = Seek_Mark(str, Mnum, Fid);
                    if (index != -1)
                    {
                        Omr_Resu[index] = true;
                    }

                    s_idx = e_idx + 1;
                    e_idx = result.IndexOf(",");
                    if (e_idx <= 1)
                    {
                        str = result.Substring(s_idx);

                        // ②結果より領域を探す Func
                        index = Seek_Mark(str, Mnum, Fid);
                        if (index != -1)
                        {
                            Omr_Resu[index] = true;
                        }
                        break;
                    }
                }
            }
            else
            {
                if (result.Length > 0)
                {
                    str = result;

                    // ②結果より領域を探す Func
                    index = Seek_Mark(str, Mnum, Fid);
                    if (index != -1)
                    {
                        Omr_Resu[index] = true;
                    }
                }
            }
            return Omr_Resu;
        }

        //================================================================
        //　マーク位置検出結果より検出された領域を抽出（マーク位置検出）
        //　②結果より領域を探す
        //
        //       (O)　Seek_Mark マークインデックス
        //       (I)　str　　 　抽出結果
        //       (I)　Mnum　　　マーク数
        //       (I)　Fid　 　　フィールドID
        //================================================================
        private int Seek_Mark(string str, int Mnum, int Fid)
        {
            object Resu;		//マーク情報
            int state;			//エラーコード

            for (int i = 0; i < Mnum; i++)
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, i + 1, out Resu);

                Array ar = (Array)Resu;
                if (ar.GetValue(1).ToString() == str)
                {
                    return i;
                }
            }

            return -1;
        }

        //================================================================
        //　マーク位置検出結果より検出された領域を抽出（全結果表示）
        //
        //       (O)　Find_Check_ONOFF マーク結果
        //       (I)　result　　　　　　認識結果
        //       (I)　Mnum　　　　　　　マーク数
        //================================================================
        private bool[] Find_Check_ONOFF(string result, int Mnum)
        {
            bool[] Omr_Resu = new bool[Mnum];	// 検索結果
            int s_idx;							//検索開始インデックス
            int e_idx;							//検索終了インデックス
            int s_len;							//文字列の長さ
            string str;							//分割結果

            for (int i = 0; i < Mnum; i++)
            {
                Omr_Resu[i] = false;
            }

            if (result == "")
            {
                return Omr_Resu;
            }

            s_idx = 0;
            e_idx = result.IndexOf(",");

            int j;
            for (j = 0; j < Mnum - 1; j++)
            {
                s_len = e_idx - s_idx;
                str = result.Substring(s_idx, s_len);

                if (str == "ON")
                {
                    Omr_Resu[j] = true;
                }

                s_idx = e_idx + 1;
                e_idx = result.IndexOf(" ", s_idx);
            }

            str = result.Substring(s_idx);
            if (str == "ON")
            {
                Omr_Resu[j] = true;
            }

            return Omr_Resu;
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%
        //%      ［詳細］    名前認識－－別ダイアログを開く（認識詳細情報を表示）
        //%      ［〒］  　　住所認識－－別ダイアログを開く（郵便番号を住所に変換）
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        private void buttonDetails_Click(object sender, System.EventArgs e)
        {
            Array F_result;		// フィールド情報
            int Fid;			// フィールドID

            if (Ocr_result == null || F_index < 0)
            {
                return;
            }

            Array ar = (Array)Ocr_result;
            Array temp = (Array)ar.GetValue(8);
            F_result = (Array)temp.GetValue(F_index);
            Fid = (int)F_result.GetValue(0);			//フィールドID

            if ((int)F_result.GetValue(10) != 2)
            {
                return;
            }

            if ((int)F_result.GetValue(13) == 2 && buttonDetails.Text == "〒")
            {
                //住所認識の場合－＞郵便番号変換ダイアログを開く
                F_OCR_Add dlg = new F_OCR_Add();
                dlg.ShowDialog();

                if (dlg.Address != "-1")
                {
                    textResult.Text = dlg.Address;
                }
                 
            }
            else if ((int)F_result.GetValue(13) == 3 && buttonDetails.Text == "詳細")
            {
                //名前認識の場合－＞詳細表示ダイアログを開く

                int state;				//エラーコード
                int MyDib;				//フィールドイメージ
                int StrNum;				//候補文字列数
                object Resu;			//候補文字列情報
                Array Seg_result;		//フィールド情報

                //定型情報　0：なし　0以外：あり　　　　定型情報がある場合、定型情報を除去したイメージを取得できる
                //　　　　　　　　　　　　　　　　　　  定型情報がない場合、濃淡イメージしか取得できない
                if ((int)F_result.GetValue(11) == 0)
                {
                    //++ フィールドイメージ取得 ++
                    //+　フィールドイメージを取得します。
                    //+　GetRecogFieldImage(フィールドID,モード,イメージ取得用)　モード　0：濃淡　1：２値　2：３値
                    state = Gocr.GetRecogFieldImage(Fid, 0, out MyDib);
                }
                else
                {
                    //++ フィールドイメージ取得 ++
                    //+　フィールドイメージを取得します。
                    //+　GetRecogFieldImage(フィールドID,モード,イメージ取得用)　モード　0：濃淡　1：２値　2：３値
                    state = Gocr.GetRecogFieldImage(Fid, 2, out MyDib);
                }

                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                StrNum = (int)F_result.GetValue(14);    //候補文字列数
                Seg_result = Array.CreateInstance(typeof(object), StrNum);

                for (int i = 0; i < StrNum; i++)
                {
                    //++ １候補文字列のセグメント結果取得 ++
                    //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                    //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                    state = Gocr.GetFieldCharResult(Fid, i + 1, out Resu);

                    if (state != 1)
                    {
                        MessageBox.Show(Gocr.get_RejectCode2String(state));
                        return;
                    }

                    Seg_result.SetValue(Resu, i);
                }

                F_OCR_Name dlg = new F_OCR_Name();
                dlg.Dib_ = MyDib;
                dlg.F_result_ = F_result;
                dlg.Seg_result_ = Seg_result;
                dlg.Resu_ = textResult.Text;

                dlg.ShowDialog();

                //イメージ解放
                GlobalFree(MyDib);

                if (dlg.Resu_ != "-1")
                {
                    textResult.Text = dlg.Resu_;
                }
            }
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%
        //%                  pictureBox2
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //MouseDown
        private void pictureBox2_MouseDown(object sender, System.Windows.Forms.MouseEventArgs e)
        {
            mouseDown = new Point(e.X, e.Y);

            float xx;		//マウスダウンX座標
            float yy;		//マウスダウンY座標

            //認識結果がなければ終わり
            if (Ocr_result == null)
            {
                return;
            }

            //認識フィールド数が０より小さければ終了
            Array ar = (Array)Ocr_result;
            if ((int)ar.GetValue(7) < 0)
            {
                return;
            }

            //マウスダウンした位置をLEAD上に換算
            if (((float)bitmap2.Width / (float)pictureBox2.Width) >= ((float)bitmap2.Height / (float)pictureBox2.Height))
            {
                xx = e.X * bitmap2.Width / pictureBox2.Width;
                yy = e.Y * bitmap2.Width / pictureBox2.Width;
            }
            else
            {
                xx = e.X * bitmap2.Height / pictureBox2.Height;
                yy = e.Y * bitmap2.Height / pictureBox2.Height;
            }

            // FID取得
            Array temp = (Array)ar.GetValue(8);
            Array F_result = (Array)temp.GetValue(F_index);
            int Fid = (int)F_result.GetValue(0);

            //左右クリックで分岐
            if (e.Button == MouseButtons.Left)			//左クリック
            {
                //ＯＭＲならば
                if ((int)F_result.GetValue(10) == 3)
                {
                    int Mnum = (int)F_result.GetValue(11);		// マーク数

                    //全結果出力又は、マーク位置検出 表示への分岐
                    if ((int)F_result.GetValue(12) == 0 && (int)F_result.GetValue(13) == 0)
                    {
                        //全結果出力　表示 Func
                        Check_Mark_OnOff(xx, yy, Fid, Mnum);
                    }
                    else
                    {
                        //マーク位置検出　表示 Func
                        Check_Mark(xx, yy, Fid, Mnum);
                    }
                }
            }
            else if (e.Button == MouseButtons.Right)		//右クリック
            {
                //認識モードで分岐
                if ((int)F_result.GetValue(10) == 1)			//英数カタカナOCR
                {
                    //クリックした領域がどのセグメントかを調べる
                    Char_Click(xx, yy, Fid);
                }
                else if ((int)F_result.GetValue(10) == 2)	//知識処理・日本語OCR
                {
                    //文字列候補数
                    int StrNum = (int)F_result.GetValue(14);
                    //メニューに候補文字列を入れて表示 Fnc
                    In_Menu_Str(Fid, StrNum);
                }
            }
        }

        //================================================================
        //  クリックした点のマーク位置を調べる　（マーク位置検出）
        //
        //       (I)　xx　　クリック点（X座標）
        //       (I)　yy　　クリック点（Y座標）
        //       (I)　Fid 　フィールドID
        //       (I)　Mnum　マーク数
        //================================================================
        private void Check_Mark(float xx, float yy, int Fid, int Mnum)
        {
            int state;			//エラーコード
            float sx;			//マーク領域始点（X座標）
            float sy;			//マーク領域始点（Y座標）
            float ex;			//マーク領域終点（X座標）
            float ey;			//マーク領域終点（Y座標）
            object Resu;		//マーク情報
            Array M_temp;		//マーク情報
            bool[] Omr_Resu;	//検出領域
            string result;		//修正結果

            for (int i = 0; i < Mnum; i++)
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, i + 1, out Resu);
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                Array ar = (Array)Resu;
                Array temp = (Array)ar.GetValue(5);
                M_temp = (Array)temp.GetValue(0);

                sx = Convert.ToSingle(M_temp.GetValue(3));
                sy = Convert.ToSingle(M_temp.GetValue(4));
                ex = sx + Convert.ToSingle(M_temp.GetValue(5));
                ey = sy + Convert.ToSingle(M_temp.GetValue(6));

                if (xx >= sx && xx <= ex)
                {
                    if (yy >= sy && yy <= ey)
                    {
                        //マーク位置検出領域取得 Func
                        Omr_Resu = Find_Check_OMR(textResult.Text, Mnum, Fid);

                        if (Omr_Resu[i] == true)
                        {
                            Omr_Resu[i] = false;
                        }
                        else
                        {
                            Omr_Resu[i] = true;
                        }

                        result = "";

                        for (int k = 0; k < Mnum; k++)
                        {
                            if (Omr_Resu[k] == true)
                            {
                                //++ １候補文字列のセグメント結果取得 ++
                                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                                state = Gocr.GetFieldCharResult(Fid, k + 1, out Resu);
                                if (state != 1)
                                {
                                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                                }

                                ar = (Array)Resu;
                                if (result == "")
                                {
                                    result = ar.GetValue(1).ToString();
                                }
                                else
                                {
                                    result = result + "," + ar.GetValue(1).ToString();
                                }
                            }
                        }
                        //修正結果を表示
                        textResult.Text = result;

                        ar = (Array)Ocr_result;
                        temp = (Array)ar.GetValue(8);
                        Array F_result = (Array)temp.GetValue(F_index);

                        //マーク位置検出（マーク位置検出） Func  (再表示)
                        Goto_OMR(F_result);

                        return;
                    }
                }
            }
        }

        //================================================================
        //  クリックした点のマーク位置を調べる　（全結果出力）
        //
        //       (I)　xx　　クリック点（X座標）
        //       (I)　yy　　クリック点（Y座標）
        //       (I)　Fid 　フィールドID
        //       (I)　Mnum　マーク数
        //================================================================
        private void Check_Mark_OnOff(float xx, float yy, int Fid, int Mnum)
        {
            int state;			//エラーコード
            float sx;			//マーク領域始点（X座標）
            float sy;			//マーク領域始点（Y座標）
            float ex;			//マーク領域終点（X座標）
            float ey;			//マーク領域終点（Y座標）
            object Resu;		//マーク情報
            Array M_temp;		//マーク情報
            bool[] Omr_Resu;	//検出領域
            string result;		//修正結果
            string str;			//ON/OFF


            for (int i = 0; i < Mnum; i++)
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, i + 1, out Resu);

                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                }

                Array ar = (Array)Resu;
                Array temp = (Array)ar.GetValue(5);
                M_temp = (Array)temp.GetValue(0);

                sx = Convert.ToSingle(M_temp.GetValue(3));
                sy = Convert.ToSingle(M_temp.GetValue(4));
                ex = sx + Convert.ToSingle(M_temp.GetValue(5));
                ey = sy + Convert.ToSingle(M_temp.GetValue(6));

                if (xx >= sx && xx <= ex)
                {
                    if (yy >= sy && yy <= ey)
                    {
                        //マーク位置検出領域取得 Func
                        Omr_Resu = Find_Check_ONOFF(textResult.Text, Mnum);

                        if (Omr_Resu[i] == true)
                        {
                            str = "ON";
                        }
                        else
                        {
                            str = "OFF";
                        }

                        result = "";

                        for (int k = 0; k < Mnum; k++)
                        {
                            if (Omr_Resu[k] == true)
                            {
                                //++ １候補文字列のセグメント結果取得 ++
                                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                                state = Gocr.GetFieldCharResult(Fid, k + 1, out Resu);
                                if (state != 1)
                                {
                                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                                }

                                if (result == "")
                                {
                                    result = str;
                                }
                                else
                                {
                                    result = result + " " + str;
                                }
                            }
                        }
                        //修正結果を表示
                        textResult.Text = result;

                        ar = (Array)Ocr_result;
                        temp = (Array)ar.GetValue(8);
                        Array F_result = (Array)temp.GetValue(F_index);

                        //マーク位置検出（全結果出力） Func  (再表示)
                        Goto_OMR_OnOff(F_result);

                        return;
                    }
                }
            }
        }

        //===================================================================
        //  クリックした領域がどのセグメントかを調べる （英数カタカナ+個別枠あり）
        //
        //       (I)　xx　クリック点（X座標）
        //       (I)　yy　クリック点（Y座標）
        //       (I)　Fid フィールドID
        //===================================================================
        private void Char_Click(float xx, float yy, int Fid)
        {
            int state;			//エラーコード
            int SegNum;			//セグメント数
            int Cnum;			//候補文字数
            string Can_Resu;	//候補文字
            float sx;			//セグメント領域始点（X座標）
            float sy;			//セグメント領域始点（Y座標）
            float ex;			//セグメント領域終点（X座標）
            float ey;			//セグメント領域終点（Y座標）
            object Resu;		//候補文字列情報
            Array temp;			//セグメント情報
            Array Seg_info;		//セグメント情報

            //++ １候補文字列のセグメント結果取得 ++
            //+　第Ｎ位の候補文字列のセグメント結果を取得します。
            //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
            state = Gocr.GetFieldCharResult(Fid, 1, out Resu);

            if (state != 1)
            {
                MessageBox.Show(Gocr.get_RejectCode2String(state));
                return;
            }

            Array ar = (Array)Resu;
            SegNum = (int)ar.GetValue(4) - 1;
            Seg_info = (Array)ar.GetValue(5);

            for (int i = 0; i <= SegNum; i++)
            {
                temp = (Array)Seg_info.GetValue(i);

                sx = Convert.ToSingle(temp.GetValue(3));
                sy = Convert.ToSingle(temp.GetValue(4));
                ex = sx + Convert.ToSingle(temp.GetValue(5));
                ey = sy + Convert.ToSingle(temp.GetValue(6));

                if (xx >= sx && xx <= ex)
                {
                    if (yy >= sy && yy <= ey)
                    {
                        if ((int)temp.GetValue(0) < 1)
                        {
                            return;
                        }

                        //文字置き換えインデックスセット
                        S_index = i + 1;

                        Cnum = (int)temp.GetValue(0);
                        Can_Resu = temp.GetValue(1).ToString();

                        //メニューに候補文字を入れて表示 Func
                        In_Menu_Char(Can_Resu, Cnum);

                        return;
                    }
                }
            }
        }

        //+++++++++++++++++++++++++++++++++++++++++++++
        //   候補文字・候補文字列をポップアップメニューへ
        //+++++++++++++++++++++++++++++++++++++++++++++

        //================================================================
        //       メニューに候補文字を入れて表示
        //
        //       (I)　Can_Resu　候補文字全て
        //       (I)　Cnum　　　候補文字数
        //================================================================
        private void In_Menu_Char(string Can_Resu, int Cnum)
        {
            string str;

            //候補文字数が０以下ならばポップアップメニューを表示しない
            if (Cnum <= 0)
            {
                return;
            }

            //ポップアップメニューの初期化
            Init_Menu();

            //メニューに候補文字を入れて表示
            if (Cnum >= 1)    //１位
            {
                str = Can_Resu.Substring(0, 1);

                menuItem1.Visible = true;			// 項目
                menuItem1.Text = str;
            }
            if (Cnum >= 2)    //２位
            {
                str = Can_Resu.Substring(1, 1);

                menuItem2.Visible = true;			// 項目
                menuItem2.Text = str;
                menuItem11.Visible = true;			// 区分線
            }
            if (Cnum >= 3)    //３位
            {
                str = Can_Resu.Substring(2, 1);

                menuItem3.Visible = true;
                menuItem3.Text = str;
                menuItem12.Visible = true;
            }
            if (Cnum >= 4)    //４位
            {
                str = Can_Resu.Substring(3, 1);

                menuItem4.Visible = true;
                menuItem4.Text = str;
                menuItem13.Visible = true;
            }
            if (Cnum >= 5)    //５位
            {
                str = Can_Resu.Substring(4, 1);

                menuItem5.Visible = true;
                menuItem5.Text = str;
                menuItem14.Visible = true;
            }
            if (Cnum >= 6)    //６位
            {
                str = Can_Resu.Substring(5, 1);

                menuItem6.Visible = true;
                menuItem6.Text = str;
                menuItem15.Visible = true;
            }
            if (Cnum >= 7)    //７位
            {
                str = Can_Resu.Substring(6, 1);

                menuItem7.Visible = true;
                menuItem7.Text = str;
                menuItem16.Visible = true;
            }
            if (Cnum >= 8)    //８位
            {
                str = Can_Resu.Substring(7, 1);

                menuItem8.Visible = true;
                menuItem8.Text = str;
                menuItem17.Visible = true;
            }
            if (Cnum >= 9)    //９位
            {
                str = Can_Resu.Substring(8, 1);

                menuItem9.Visible = true;
                menuItem9.Text = str;
                menuItem18.Visible = true;
            }
            if (Cnum >= 10)    //１０位
            {
                str = Can_Resu.Substring(9, 1);

                menuItem10.Visible = true;
                menuItem10.Text = str;
                menuItem19.Visible = true;
            }
            contextMenu1.Show(pictureBox2, mouseDown);
            contextMenu1.Show(pictureBox2, mouseDown);
        }

        //================================================================
        //           メニューに候補文字列を入れて表示
        //
        //           (I)　Fid　　 フィールドID
        //           (I)　StrNum　候補文字列数
        //================================================================
        private void In_Menu_Str(int Fid, int StrNum)
        {
            object Resu;	//候補文字列情報
            int state;		//エラーコード
            Array ar;

            //候補文字数が０以下ならばポップアップメニューを表示しない
            if (StrNum <= 0)
            {
                return;
            }

            //ポップアップメニューの初期化
            Init_Menu();

            //メニューに候補文字を入れて表示
            if (StrNum >= 1)		//１位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 1, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem1.Visible = true;			// 項目
                menuItem1.Text = ar.GetValue(1).ToString();
            }
            if (StrNum >= 2)    //２位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 2, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem2.Visible = true;			// 項目
                menuItem2.Text = ar.GetValue(1).ToString();
                menuItem11.Visible = true;			// 区分線
            }
            if (StrNum >= 3)    //３位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 3, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem3.Visible = true;
                menuItem3.Text = ar.GetValue(1).ToString();
                menuItem12.Visible = true;
            }
            if (StrNum >= 4)    //４位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 4, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem4.Visible = true;
                menuItem4.Text = ar.GetValue(1).ToString();
                menuItem13.Visible = true;
            }
            if (StrNum >= 5)    //５位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 5, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem5.Visible = true;
                menuItem5.Text = ar.GetValue(1).ToString();
                menuItem14.Visible = true;
            }
            if (StrNum >= 6)    //６位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 6, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem6.Visible = true;
                menuItem6.Text = ar.GetValue(1).ToString();
                menuItem15.Visible = true;
            }
            if (StrNum >= 7)    //７位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 7, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem7.Visible = true;
                menuItem7.Text = ar.GetValue(1).ToString();
                menuItem16.Visible = true;
            }
            if (StrNum >= 8)    //８位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 8, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem8.Visible = true;
                menuItem8.Text = ar.GetValue(1).ToString();
                menuItem17.Visible = true;
            }
            if (StrNum >= 9)    //９位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 9, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem9.Visible = true;
                menuItem9.Text = ar.GetValue(1).ToString();
                menuItem18.Visible = true;
            }
            if (StrNum >= 10)    //１０位
            {
                //++ １候補文字列のセグメント結果取得 ++
                //+　第Ｎ位の候補文字列のセグメント結果を取得します。
                //+　GetFieldCharResult(フィールドID,第Ｎ位,セグメント結果)
                state = Gocr.GetFieldCharResult(Fid, 10, out Resu);
                ar = (Array)Resu;
                if (state != 1)
                {
                    MessageBox.Show(Gocr.get_RejectCode2String(state));
                    return;
                }

                menuItem10.Visible = true;
                menuItem10.Text = ar.GetValue(1).ToString();
                menuItem19.Visible = true;
            }

            contextMenu1.Show(pictureBox2, mouseDown);
        }

        //================================================================
        //           ポップアップメニューの初期化
        //================================================================
        private void Init_Menu()
        {
            menuItem1.Visible = false;
            menuItem2.Visible = false;
            menuItem3.Visible = false;
            menuItem4.Visible = false;
            menuItem5.Visible = false;
            menuItem6.Visible = false;
            menuItem7.Visible = false;
            menuItem8.Visible = false;
            menuItem9.Visible = false;
            menuItem10.Visible = false;
            menuItem11.Visible = false;
            menuItem12.Visible = false;
            menuItem13.Visible = false;
            menuItem14.Visible = false;
            menuItem15.Visible = false;
            menuItem16.Visible = false;
            menuItem17.Visible = false;
            menuItem18.Visible = false;
            menuItem19.Visible = false;
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%
        //%              ポップアップメニュー
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        private void menuItem1_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem1.Text);
        }

        private void menuItem2_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem2.Text);
        }

        private void menuItem3_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem3.Text);
        }

        private void menuItem4_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem4.Text);
        }

        private void menuItem5_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem5.Text);
        }

        private void menuItem6_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem6.Text);
        }

        private void menuItem7_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem7.Text);
        }

        private void menuItem8_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem8.Text);
        }

        private void menuItem9_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem9.Text);
        }

        private void menuItem10_Click(object sender, System.EventArgs e)
        {
            //答え変換 Func
            Result_Change(menuItem10.Text);
        }

        //================================================================
        //               答え変換
        //
        //          (I)　Select_Char　選択文字／文字列
        //================================================================
        private void Result_Change(string Select_Char)
        {
            string str;				//認識結果
            int sj;					//文字置き換えインデックス
            Array temp;				//フィールド情報
            Array F_result;			//フィールド情報

            //選択文字、選択文字列が空白だった場合、変換処理終了
            if (Select_Char == "" || Select_Char == "　" || Select_Char == " ")
            {
                return;
            }

            Array ar = (Array)Ocr_result;
            temp = (Array)ar.GetValue(8);
            F_result = (Array)temp.GetValue(F_index);

            //認識モードにより分岐
            if ((int)F_result.GetValue(10) == 1)			//英数カタカナOCR
            {
                sj = S_index - 1;
                str = textResult.Text;

                //文字置き換えインデックスクリア
                S_index = -1;

                //選択した文字に置き換え
                if (str.Length < sj)
                {
                    str = str + Select_Char;
                }
                else
                {
                    str = str.Remove(sj, 1);
                    str = str.Insert(sj, Select_Char);
                }

                //結果表示
                textResult.Text = str;

                //英数カタカナＯＣＲ（個別枠あり） Func  (再表示)
                Goto_OCR_EN_Frame(F_result);
            }
            else if ((int)F_result.GetValue(10) == 2)	//知識辞書・漢字OCR
            {
                //選択した文字列に置き換え、表示
                textResult.Text = Select_Char;
            }
        }

        private void MainForm_Resize(object sender, EventArgs e)
        {
            pictureBox1.Refresh();
            pictureBox2.Refresh();
        }
    }
}
