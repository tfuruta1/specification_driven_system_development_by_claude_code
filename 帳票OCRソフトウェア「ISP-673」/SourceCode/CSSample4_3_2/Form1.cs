using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Glory.DocOcr;

namespace CSSample4_3_2
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
                // エリアＯＣＲ２
                FieldResult fieldRes = Ocr.RecogFieldEx(
                                        @"C:\TestFile\TEST4-3-2_1.bmp", // イメージファイル名
                                        240,                        // 入力解像度(dpi)
                                        RotateTypes.NoRotate,       // 処理方向（0:正位方向 1:左90度回転 2:右90度回転 3:180度回転）
                                        RecogFieldExModeTypes.ANKS, // 処理内容
                                        7,                          // 枠の個数／最大文字数（長整数）
                                        FrameTypeTypes.SeparateBox, // 枠の種類（長整数）
                                        WriteMethodTypes.HandWrite, // 記入方法（長整数）
                                        1,                          // 字種（長整数）
                                        "",                         // 知識辞書名称 
                                        "",                         // 限定文字列
                                        ProcSpeedTypes.Normal       // 処理速度
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

        private void button2_Click(object sender, EventArgs e)
        {
            try
            {
                // エリアＯＣＲ２
                FieldResult fieldRes = Ocr.RecogFieldEx(
                                        @"C:\TestFile\TEST4-3-2_2.bmp", // イメージファイル名
                                        240,                        // 入力解像度(dpi)
                                        RotateTypes.NoRotate,       // 処理方向（0:正位方向 1:左90度回転 2:右90度回転 3:180度回転）
                                        RecogFieldExModeTypes.ANKS, // 処理内容
                                        7,                          // 枠の個数／最大文字数（長整数）
                                        FrameTypeTypes.Ladder,      // 枠の種類（長整数）
                                        WriteMethodTypes.HandWrite, // 記入方法（長整数）
                                        0xB,                        // 字種（長整数）
                                        "",                         // 知識辞書名称 
                                        "0123456789GFIKSTPU#$-",    // 限定文字列
                                        ProcSpeedTypes.Normal       // 処理速度
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

        private void button3_Click(object sender, EventArgs e)
        {
            try
            {
                // エリアＯＣＲ２
                FieldResult fieldRes = Ocr.RecogFieldEx(
                                        @"C:\TestFile\TEST4-3-2_3.bmp", // イメージファイル名
                                        240,                        // 入力解像度(dpi)
                                        RotateTypes.NoRotate,       // 処理方向（0:正位方向 1:左90度回転 2:右90度回転 3:180度回転）
                                        RecogFieldExModeTypes.ANKS, // 処理内容
                                        25,                         // 枠の個数／最大文字数（長整数）
                                        FrameTypeTypes.NoFrame,     // 枠の種類（長整数）
                                        WriteMethodTypes.Print,     // 記入方法（長整数）
                                        0x1F,                       // 字種（長整数）
                                        "",                         // 知識辞書名称 
                                        "",                         // 限定文字列
                                        ProcSpeedTypes.Normal       // 処理速度
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

        private void button4_Click(object sender, EventArgs e)
        {
            try
            {
                // エリアＯＣＲ２
                FieldResult fieldRes = Ocr.RecogFieldEx(
                                        @"C:\TestFile\TEST4-3-2_4.bmp", // イメージファイル名
                                        240,                        // 入力解像度(dpi)
                                        RotateTypes.NoRotate,       // 処理方向（0:正位方向 1:左90度回転 2:右90度回転 3:180度回転）
                                        RecogFieldExModeTypes.ANKS, // 処理内容
                                        10,                         // 枠の個数／最大文字数（長整数）
                                        FrameTypeTypes.NoFrame,     // 枠の種類（長整数）
                                        WriteMethodTypes.Print,     // 記入方法（長整数）
                                        0x4000,                     // 字種（長整数）
                                        "",                         // 知識辞書名称 
                                        "",                         // 限定文字列
                                        ProcSpeedTypes.Normal       // 処理速度
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
