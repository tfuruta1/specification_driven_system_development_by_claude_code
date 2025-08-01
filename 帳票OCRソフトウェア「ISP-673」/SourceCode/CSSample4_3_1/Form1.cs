using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;

namespace CSSample4_3_1
{
    public partial class Form1 : Form
    {

        private GOcr Ocr = new GOcr();

        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            try
            {
                // エリアＯＣＲ２
                FieldResult fieldRes = Ocr.RecogFieldCode(
                                            @"C:\TestFile\TEST4-3-1.bmp",   // イメージファイル名
                                            200,                            // 入力解像度(dpi)
                                            RotateTypes.NoRotate,           // 処理方向（0:正位方向 1:左90度回転 2:右90度回転 3:180度回転）
                                            100,                            // 最大桁数（ＱＲの場合は無効）
                                            CodeTypeTypes.JAN,              // コードの種類（1:JANコード）
                                            CheckDigitTypeTypes.Modulus10_3,// ﾁｪｯｸﾃﾞｼﾞｯﾄ (1:モジュラス10/3）
                                            CodeProcModeTypes.Normal,       // 処理モード
                                            0                               // タイムアウト（ms）
                                            );
                string msg;
                if (fieldRes.Status == 0)
                {
                    msg = fieldRes.Result;
                }
                else
                {
                    msg = "リジェクト：" + Ocr.GetRejectCode2String(fieldRes.Status);
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
