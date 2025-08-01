using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;

namespace CSSample4_4_1
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
                // ２値化
                int back;
                int thresh;
                Image image = GOcrUtil.GetBinaryImage(
                                            out back,
                                            out thresh,
                                            @"C:\TestFile\TEST4-4.bmp", // 入力イメージファイル名
                                            11, // ２値化方法（１１：動的しきい値決定法）
                                            0,  // 付加情報１
                                            2   // 付加情報１
                                            );
                // 圧縮保存
                GOcrUtil.OutputImageFile(@"C:\TestFile\4-4-1(出力).TIF", ImageSaveTypeTypes.TIFF, image);
                MessageBox.Show("画像処理 ＴＩＦＦ圧縮保存に成功しました");
            }
            catch (GOcrException ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
    }
}
