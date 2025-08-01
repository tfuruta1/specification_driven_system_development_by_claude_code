using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.IO;


namespace CSharp_Sample2
{
    public partial class F_OCR_Name : Form
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

        private int Dib;					// フィールドイメージ
        private string Resu;				// 認識結果
        private int Ocr_Index;				// 表示候補文字列の順位
        private int S_index;				// 文字置き換えインデックス
        private bool Dsp_Mode;				// 表示モード　TRUE：セグメント領域表示   FALSE：セグメント領域表示しない
        private Array F_result;				// フィールド情報
        private Array Seg_result;			// 候補文字列情報

        private Bitmap bitmap1 = null;					// pictureBox1用イメージ
        private Rectangle[] rectangle1 = null;			// pictureBox1用枠描画座標
        private string[] str1 = null;					// pictureBox1用描画文字列
        private bool[] color1 = null;					// pictureBox1用文字描画色
        private Rectangle[] rectangle2 = null;			// pictureBox1用枠描画座標

        private Point mouseDown;						// MouseDownポイント

        public F_OCR_Name()
        {
            InitializeComponent();
        }
        public int Dib_
        {
            set
            {
                Dib = value;
            }
        }

        public Array F_result_
        {
            set
            {
                F_result = value;
            }
        }

        public Array Seg_result_
        {
            set
            {
                Seg_result = value;
            }
        }

        public string Resu_
        {
            get
            {
                return Resu;
            }
            set
            {
                Resu = value;
            }
        }

        private void F_OCR_Name_Load(object sender, System.EventArgs e)
        {
            Dsp_Mode = true;

            // フィールド名称
            this.Text = F_result.GetValue(1).ToString();

            // フィット表示1
            DspFilde_Fit1();

            Combo.BackColor = Color.White;

            // リジェクト
            if ((int)F_result.GetValue(6) != 0)
            {
                Combo.BackColor = Color.Yellow;
            }

            // 候補文字列数
            int StrNum = (int)F_result.GetValue(14) - 1;

            // 表示候補文字列の順位を１位にセット
            Ocr_Index = 0;
            DspResult();

            // 文字列候補をコンボボックスに入れる
            Array temp;
            for (int i = 0; i <= StrNum; i++)
            {
                temp = (Array)Seg_result.GetValue(i);
                Combo.Items.Insert(i, temp.GetValue(1).ToString());
            }

            // 結果を表示
            Combo.Text = Resu;
        }

        private void F_OCR_Name_FormClosed(object sender, FormClosedEventArgs e)
        {
            Resu = Combo.Text;
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
            // 文字 & 枠表示
            //--------------------------------------------
            if (Dsp_Mode == false)
            {
                return;
            }

            if (rectangle1 != null)
            {
                //フォントオブジェクトの作成
                Font fnt = new Font("ＭＳ Ｐゴシック", 20);
                //Penオブジェクトの作成(幅1の赤色)
                Pen p = new Pen(Color.Red, 1);

                //長方形座標計算
                for (int i = 0; i < rectangle1.Length; i++)
                {
                    Rectangle rect = CalcDrawRect(rectangle1[i], factor);
                    e.Graphics.DrawRectangle(p, rect);

                    //文字列を表示する範囲を指定する
                    SizeF sizeF = e.Graphics.MeasureString(str1[i], fnt);
                    rect = new Rectangle(rect.X, rect.Y - (int)sizeF.Height - 1, (int)sizeF.Width, (int)sizeF.Height);

                    //rectの四角を描く
                    if (color1[i])
                    {
                        e.Graphics.FillRectangle(new SolidBrush(Color.FromArgb(0, 0, 255)), rect);
                    }
                    else
                    {
                        e.Graphics.FillRectangle(new SolidBrush(Color.FromArgb(255, 109, 29)), rect);
                    }
                    //文字を書く
                    e.Graphics.DrawString(str1[i], fnt, Brushes.White, rect);
                }

                //リソースを開放する
                p.Dispose();
                //リソースを開放する
                fnt.Dispose();
            }

            if (rectangle2 != null)
            {
                //Penオブジェクトの作成(幅1の赤色)
                Pen p = new Pen(Color.FromArgb(2, 106, 202), 5);

                //長方形座標計算
                for (int i = 0; i < rectangle2.Length; i++)
                {
                    Rectangle rect = CalcDrawRect(rectangle2[i], factor);
                    e.Graphics.DrawRectangle(p, rect);
                }

                //リソースを開放する
                p.Dispose();
            }
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

        //=========================================
        //            フィット表示1
        //=========================================
        private void DspFilde_Fit1()
        {
            bitmap1 = DIBToSystemBitmap(Dib);
            pictureBox1.Invalidate();
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%
        //%     　       Combo
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        private void Combo_KeyUp(object sender, System.Windows.Forms.KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Right || e.KeyCode == Keys.Left)
            {
                Select_Seg();
            }

            if (e.KeyCode == Keys.Up || e.KeyCode == Keys.Down)
            {
                Ocr_Index = Combo.SelectedIndex;
                DspResult();
            }
        }

        private void Combo_KeyDown(object sender, System.Windows.Forms.KeyEventArgs e)
        {
            //押下キーボードにより分岐
            switch (e.KeyCode)
            {
                case Keys.F10:				// F10
                    // 答えを消す
                    Combo.Text = "";
                    Dsp_Mode = false;
                    pictureBox1.Invalidate();
                    break;
                case Keys.F11:				// F11
                    //表示モード切替　TRUE:セグメント領域表示　FALSE:表示なし
                    if (Dsp_Mode == true)
                    {
                        Dsp_Mode = false;
                    }
                    else
                    {
                        Dsp_Mode = true;
                    }
                    pictureBox1.Invalidate();
                    Ocr_Index = Combo.SelectedIndex;
                    DspResult();
                    break;
                case Keys.Return:			// Return
                    this.Close();
                    break;
                case Keys.PageUp:			// PageUp
                    this.Close();
                    break;
                case Keys.PageDown:		// PageDown
                    this.Close();
                    break;
                case Keys.Escape:			// Escape
                    Combo.Text = "-1";
                    this.Close();
                    break;
            }
        }

        private void Combo_SelectedValueChanged(object sender, System.EventArgs e)
        {
            //表示コンボインデックス
            Ocr_Index = Combo.SelectedIndex;

            //フィールド表示 Func
            rectangle2 = null;
            DspResult();
        }

        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        //%
        //%     　       PictureBox
        //%
        //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        private void pictureBox1_MouseDown(object sender, System.Windows.Forms.MouseEventArgs e)
        {
            mouseDown = new Point(e.X, e.Y);

            float xx;		//マウスダウンX座標
            float yy;		//マウスダウンY座標

            // 左クリックのみ有効
            if (e.Button == MouseButtons.Left)
            {
                return;
            }

            //マウスダウンした位置をLEAD上に換算
            if (((float)bitmap1.Width / (float)pictureBox1.Width) >= ((float)bitmap1.Height / (float)pictureBox1.Height))
            {
                xx = e.X * bitmap1.Width / pictureBox1.Width;
                yy = e.Y * bitmap1.Width / pictureBox1.Width;
            }
            else
            {
                xx = e.X * bitmap1.Height / pictureBox1.Height;
                yy = e.Y * bitmap1.Height / pictureBox1.Height;
            }

            //クリックした領域がどのセグメントかを調べる Func
            Char_Click(xx, yy);
        }

        //=====================================
        //       ＯＣＲ結果表示
        //=====================================
        private void DspResult()
        {
            Array temp;
            int SegNum;			//セグメント数
            Array Str_info;		//セグメント情報

            //フィット表示1
            DspFilde_Fit1();

            if (Dsp_Mode == false)
            {
                return;
            }

            temp = (Array)Seg_result.GetValue(Ocr_Index);
            SegNum = (int)temp.GetValue(4);
            Str_info = (Array)temp.GetValue(5);
            Combo.Text = (string)temp.GetValue(1);

            rectangle1 = new Rectangle[SegNum];
            str1 = new string[SegNum];
            color1 = new bool[SegNum];

            for (int i = 0; i < SegNum; i++)
            {
                temp = (Array)Str_info.GetValue(i);

                // 枠座標計算
                int x = (int)temp.GetValue(3);
                int y = (int)temp.GetValue(4);
                int w = (int)temp.GetValue(5);
                int h = (int)temp.GetValue(6);
                rectangle1[i] = new Rectangle(x, y, w, h);

                // 結果を１文字ごとに分割
                str1[i] = Can_Char(i);

                if ((int)temp.GetValue(2) > 2)
                {
                    color1[i] = true;
                }
                else
                {
                    color1[i] = false;
                }
            }
        }

        //=============================================
        //         結果を１文字ごとに分割
        //
        //       (O)　Can_Char　　 分割認識結果（１文字）
        //       (I)　index　 　　 セグメントインデックス
        //=============================================
        private string Can_Char(int index)
        {
            string wk = Combo.Text;

            wk = wk.Replace(" ", "");
            return wk.Substring(index, 1);
        }

        //===================================================================
        //  クリックした領域がどのセグメントかを調べる
        //
        //       (I)　xx　　クリック点（X座標）
        //       (I)　yy　　クリック点（Y座標）
        //===================================================================
        private void Char_Click(float xx, float yy)
        {
            int SegNum;			//セグメント数
            int Fid;			//フィールドID
            float sx;			//セグメント領域始点（X座標）
            float sy;			//セグメント領域始点（Y座標）
            float ex;			//セグメント領域終点（X座標）
            float ey;			//セグメント領域終点（Y座標）
            Array temp;			//セグメント情報
            Array Seg_info;		//セグメント情報

            Array ar = (Array)Seg_result;
            temp = (Array)ar.GetValue(Ocr_Index);
            Seg_info = (Array)temp.GetValue(5);
            SegNum = (int)temp.GetValue(4);

            for (int i = 0; i < SegNum; i++)
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
                        Fid = (int)F_result.GetValue(0);

                        In_Menu(i, Fid);

                        return;
                    }
                }
            }
        }

        //+++++++++++++++++++++++++++++++++++++++++++++
        //   候補文字をポップアップメニューへ
        //+++++++++++++++++++++++++++++++++++++++++++++

        //================================================================
        //           メニューに候補文字を入れて表示
        //
        //       (I)　figure　選択セグメント
        //       (I)　Fid　　 フィールドID
        //================================================================
        private void In_Menu(int figure, int Cnum)
        {
            Array temp;
            Array temp2;
            Array temp3;
            string Char;			//候補文字（１文字）
            int Snum;				//候補文字数
            string str;				//候補文字


            S_index = figure + 1;

            temp = (Array)Seg_result.GetValue(Ocr_Index);
            temp2 = (Array)temp.GetValue(5);
            temp3 = (Array)temp2.GetValue(figure);

            Snum = (int)temp3.GetValue(0);
            str = temp3.GetValue(1).ToString();

            //初期化
            Init_Menu();

            //メニューに候補文字を入れて表示
            if (Snum >= 1)    //１位
            {
                Char = str.Substring(0, 1);

                menuItem1.Visible = true;			// 項目
                menuItem1.Text = Char;
            }
            if (Snum >= 2)    //２位
            {
                Char = str.Substring(1, 1);

                menuItem2.Visible = true;			// 項目
                menuItem2.Text = Char;
                menuItem11.Visible = true;			// 区分線
            }
            if (Snum >= 3)    //３位
            {
                Char = str.Substring(2, 1);

                menuItem3.Visible = true;
                menuItem3.Text = Char;
                menuItem12.Visible = true;
            }
            if (Snum >= 4)    //４位
            {
                Char = str.Substring(3, 1);

                menuItem4.Visible = true;
                menuItem4.Text = Char;
                menuItem13.Visible = true;
            }
            if (Snum >= 5)    //５位
            {
                Char = str.Substring(4, 1);

                menuItem5.Visible = true;
                menuItem5.Text = Char;
                menuItem14.Visible = true;
            }
            if (Snum >= 6)    //６位
            {
                Char = str.Substring(5, 1);

                menuItem6.Visible = true;
                menuItem6.Text = Char;
                menuItem15.Visible = true;
            }
            if (Snum >= 7)    //７位
            {
                Char = str.Substring(6, 1);

                menuItem7.Visible = true;
                menuItem7.Text = Char;
                menuItem16.Visible = true;
            }
            if (Snum >= 8)    //８位
            {
                Char = str.Substring(7, 1);

                menuItem8.Visible = true;
                menuItem8.Text = Char;
                menuItem17.Visible = true;
            }
            if (Snum >= 9)    //９位
            {
                Char = str.Substring(8, 1);

                menuItem9.Visible = true;
                menuItem9.Text = Char;
                menuItem18.Visible = true;
            }
            if (Snum >= 10)    //１０位
            {
                Char = str.Substring(9, 1);

                menuItem10.Visible = true;
                menuItem10.Text = Char;
                menuItem19.Visible = true;
            }

            contextMenu1.Show(pictureBox1, mouseDown);
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
            string str;			//修正結果
            int sj;				//文字置き換えインデックス

            //選択文字、選択文字列が空白だった場合、変換処理終了
            if (Select_Char == "" || Select_Char == "　" || Select_Char == " ")
            {
                return;
            }

            sj = S_index - 1;

            str = Combo.Text;

            //文字置き換えインデックスクリア
            S_index = -1;

            if (str.IndexOf(" ") <= sj && str.IndexOf(" ") > 0)
            {
                sj = sj + 1;
                if (str.Length < sj)
                {
                    str = str + Select_Char;
                }
                else
                {
                    str = str.Remove(sj, 1);
                    str = str.Insert(sj, Select_Char);
                }
            }
            else if (str.Length < sj)
            {
                str = str + Select_Char;
            }
            else
            {
                str = str.Remove(sj, 1);
                str = str.Insert(sj, Select_Char);
            }

            //修正結果表示
            Combo.Text = str;

            // 再表示
            DspResult();
        }

        //=============================================
        //         セグメント選択　[→][←]
        //=============================================
        private void Select_Seg()
        {
            int index;			//カーソルインデックス
            Array temp;
            Array temp2;
            Array Str_info;		//セグメント情報

            //カーソルインデックスを取得
            index = Combo.SelectionStart;
            if (index >= Combo.Text.Length)
            {
                return;
            }

            int idx = index;
            string str = Combo.Text;
            for (int i = 0; i <= index; i++)
            {
                if (str.Substring(i, 1) == " ")
                {
                    idx--;
                }
            }

            //文字数よりカーソルインデックスの方が大きければ選択表示しない
            temp = (Array)Seg_result.GetValue(Ocr_Index);
            if ((int)temp.GetValue(4) <= idx)
            {
                return;
            }
            temp2 = (Array)temp.GetValue(5);
            Str_info = (Array)temp2.GetValue(idx);

            // 選択中　表示
            Dsp_StrRect(Str_info);
        }

        //===============================================
        //               選択中　表示
        //
        //      (I)　Str_info　セグメント情報
        //===============================================
        private void Dsp_StrRect(Array Str_info)
        {
            rectangle2 = new Rectangle[1];

            // 枠座標計算
            int x = (int)Str_info.GetValue(3);
            int y = (int)Str_info.GetValue(4);
            int w = (int)Str_info.GetValue(5);
            int h = (int)Str_info.GetValue(6);
            rectangle2[0] = new Rectangle(x, y, w, h);

            pictureBox1.Invalidate();
        }

        private void F_OCR_Name_Resize(object sender, EventArgs e)
        {
            this.Refresh();
        }


    }
}
