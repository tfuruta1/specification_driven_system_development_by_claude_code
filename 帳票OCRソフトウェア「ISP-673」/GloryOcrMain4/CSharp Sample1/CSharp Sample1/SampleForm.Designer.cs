namespace CSharp_Sample1
{
    partial class SampleForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
			this.ocrStart = new System.Windows.Forms.Button();
			this.ocrEnd = new System.Windows.Forms.Button();
			this.groupBox1 = new System.Windows.Forms.GroupBox();
			this.ocrResultList = new System.Windows.Forms.ListBox();
			this.groupBox1.SuspendLayout();
			this.SuspendLayout();
			// 
			// ocrStart
			// 
			this.ocrStart.Location = new System.Drawing.Point(12, 12);
			this.ocrStart.Name = "ocrStart";
			this.ocrStart.Size = new System.Drawing.Size(91, 33);
			this.ocrStart.TabIndex = 0;
			this.ocrStart.Text = "OCR開始";
			this.ocrStart.UseVisualStyleBackColor = true;
			this.ocrStart.Click += new System.EventHandler(this.ocrStart_Click);
			// 
			// ocrEnd
			// 
			this.ocrEnd.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
			this.ocrEnd.DialogResult = System.Windows.Forms.DialogResult.Cancel;
			this.ocrEnd.Location = new System.Drawing.Point(408, 12);
			this.ocrEnd.Name = "ocrEnd";
			this.ocrEnd.Size = new System.Drawing.Size(84, 33);
			this.ocrEnd.TabIndex = 1;
			this.ocrEnd.Text = "OCR終了";
			this.ocrEnd.UseVisualStyleBackColor = true;
			this.ocrEnd.Click += new System.EventHandler(this.ocrEnd_Click);
			// 
			// groupBox1
			// 
			this.groupBox1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
			this.groupBox1.Controls.Add(this.ocrResultList);
			this.groupBox1.Location = new System.Drawing.Point(12, 67);
			this.groupBox1.Name = "groupBox1";
			this.groupBox1.Size = new System.Drawing.Size(480, 407);
			this.groupBox1.TabIndex = 4;
			this.groupBox1.TabStop = false;
			this.groupBox1.Text = "OCR結果";
			// 
			// ocrResultList
			// 
			this.ocrResultList.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
			this.ocrResultList.FormattingEnabled = true;
			this.ocrResultList.ItemHeight = 12;
			this.ocrResultList.Location = new System.Drawing.Point(6, 18);
			this.ocrResultList.Name = "ocrResultList";
			this.ocrResultList.Size = new System.Drawing.Size(468, 388);
			this.ocrResultList.TabIndex = 0;
			// 
			// SampleForm
			// 
			this.AcceptButton = this.ocrStart;
			this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.CancelButton = this.ocrEnd;
			this.ClientSize = new System.Drawing.Size(504, 489);
			this.Controls.Add(this.groupBox1);
			this.Controls.Add(this.ocrEnd);
			this.Controls.Add(this.ocrStart);
			this.MinimumSize = new System.Drawing.Size(512, 523);
			this.Name = "SampleForm";
			this.SizeGripStyle = System.Windows.Forms.SizeGripStyle.Show;
			this.Text = "OCRサンプル１（C#2010）";
			this.groupBox1.ResumeLayout(false);
			this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.Button ocrStart;
        private System.Windows.Forms.Button ocrEnd;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.ListBox ocrResultList;
    }
}