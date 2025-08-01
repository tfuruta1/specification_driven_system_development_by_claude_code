using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;

namespace CSSample4_2_1
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
                // 個別文字認識辞書のあるディレクトリを指定して展開
                Ocr.LoadCharDic(null);

                // RPFファイル、知識辞書、パラメータＩＤ、解像度を指定して展開
                Ocr.LoadRpfFile(@"C:\Program Files\GLORY\GLYOCR4\FDic\サンプル\Rpf", @"C:\Program Files\GLORY\GLYOCR4\KDic", 101, 240);
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
                // RPF ファイルの開放
                Ocr.UnLoadRpfFile();
                // 個別文字認識辞書の開放
                Ocr.UnloadCharDic();
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
                // エリアＯＣＲ１(パラメータＩＤ=0001-01、フィールドＩＤ=1）
                FieldResult fieldRes = Ocr.RecogField(101, 1, @"C:\TestFile\TEST4-2-1.bmp", 0.0, RotateTypes.NoRotate, ProcSpeedTypes.Normal);
                if (fieldRes.Status == 0)
                {
                    MessageBox.Show("エリアＯＣＲ１　アクセプト [" + fieldRes.Result + "]");
                }
                else
                {
                    MessageBox.Show("エリアＯＣＲ１　リジェクト");
                }
            }
            catch (GOcrException ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
    }
}
