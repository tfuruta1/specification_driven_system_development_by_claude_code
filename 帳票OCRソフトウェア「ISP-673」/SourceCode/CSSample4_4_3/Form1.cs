using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;
using System.IO;
using System.Runtime.InteropServices;
using System.Drawing.Imaging;

namespace CSSample4_4_3
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            try
            {
                // 入力イメージファイルをメモリ領域に読み込みます。
                Bitmap image = new Bitmap(@"C:\TestFile\TEST4-4.bmp");

                // 傾き補正＆黒枠除去
                Bitmap bmp = (Bitmap)GOcrUtil.GetDocumentImageEx(image, 0.5);

                // ピクチャボックスにイメージを表示します
                pictureBox1.Image = bmp;
                pictureBox1.SizeMode = PictureBoxSizeMode.Zoom;

                // 出力イメージをPNG形式で保存します
                bmp.Save(@"C:\TestFile\4-4-3(出力).png", ImageFormat.Png);
            }
            catch (GOcrException ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
    }
}
