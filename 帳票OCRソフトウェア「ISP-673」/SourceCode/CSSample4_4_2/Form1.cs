using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;

namespace CSSample4_4_2
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
                Image image = GOcrUtil.GetDocumentImageEx(@"C:\TestFile\TEST4-4.bmp", 0.5);

                // 圧縮保存
                GOcrUtil.OutputImageFile(@"C:\TestFile\4-4-2(出力).JPG", ImageSaveTypeTypes.JPEG, image);
                MessageBox.Show("画像処理 ＪＰＥＧ圧縮保存に成功しました");
            }
            catch (GOcrException ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
    }
}
