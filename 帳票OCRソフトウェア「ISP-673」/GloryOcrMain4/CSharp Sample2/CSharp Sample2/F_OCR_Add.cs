using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using GloryOcr4Lib;

namespace CSharp_Sample2
{
    public partial class F_OCR_Add : Form
    {

        private const string CDICDIR = @"C:\Program Files\GLORY\GLYOCR4\CDic";
        private const string KDICDIR = @"C:\Program Files\GLORY\GLYOCR4\KDic";

        GlyOcrEx Gocr = new GlyOcrEx();			// OCRオブジェクト生成
        private string address;

        public F_OCR_Add()
        {
            InitializeComponent();
        }

        /// <summary>
        /// ［変換］
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Comd_Change_Click(object sender, System.EventArgs e)
        {
            string adr;

            adr = textZip.Text.Replace("-", "");
            if (adr.Length != 7)
            {
                textAdd.Text = "正しい郵便番号を入力してください";
                return;
            }

            //住所取得
            adr = Gocr.get_AddString(adr);

            adr = adr.Replace(" ", "");

            textAdd.Text = adr;
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Comd_Ok_Click(object sender, System.EventArgs e)
        {
            if (textAdd.Text == "該当なし" || textAdd.Text == "正しい郵便番号を入力してください")
            {
                address = "-1";
            }
            else
            {
                address = textAdd.Text + " ";
            }
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Comd_Cancel_Click(object sender, System.EventArgs e)
        {
            address = "-1";
        }

        private void textZip_KeyPress(object sender, System.Windows.Forms.KeyPressEventArgs e)
        {
            if ((e.KeyChar < '0' || e.KeyChar > '9') && e.KeyChar != '\b' && e.KeyChar != '-')
            {
                e.Handled = true;
            }
        }

        /// <summary>
        /// 住所
        /// </summary>
        public string Address
        {
            get
            {
                return address;
            }
        }

        private void F_OCR_Add_Load(object sender, EventArgs e)
        {
            int state;
            state = Gocr.LoadCharDic(CDICDIR);
            if (state != 1)
            {
                MessageBox.Show(Gocr.get_RejectCode2String(state));
            }
            state = Gocr.LoadKnowledgeDic(KDICDIR, "住所");
            if (state != 1)
            {
                MessageBox.Show(Gocr.get_RejectCode2String(state));
            }

        }

    }
}
