namespace CSharp_Sample2
{
    partial class F_OCR_Add
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
            this.Comd_Cancel = new System.Windows.Forms.Button();
            this.Comd_Ok = new System.Windows.Forms.Button();
            this.textAdd = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.textZip = new System.Windows.Forms.TextBox();
            this.Comd_Change = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.SuspendLayout();
            // 
            // Comd_Cancel
            // 
            this.Comd_Cancel.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.Comd_Cancel.Location = new System.Drawing.Point(579, 56);
            this.Comd_Cancel.Name = "Comd_Cancel";
            this.Comd_Cancel.Size = new System.Drawing.Size(130, 40);
            this.Comd_Cancel.TabIndex = 9;
            this.Comd_Cancel.Text = "キャンセル";
            this.Comd_Cancel.Click += new System.EventHandler(this.Comd_Cancel_Click);
            // 
            // Comd_Ok
            // 
            this.Comd_Ok.DialogResult = System.Windows.Forms.DialogResult.OK;
            this.Comd_Ok.Location = new System.Drawing.Point(579, 10);
            this.Comd_Ok.Name = "Comd_Ok";
            this.Comd_Ok.Size = new System.Drawing.Size(130, 40);
            this.Comd_Ok.TabIndex = 8;
            this.Comd_Ok.Text = "OK";
            this.Comd_Ok.Click += new System.EventHandler(this.Comd_Ok_Click);
            // 
            // textAdd
            // 
            this.textAdd.Font = new System.Drawing.Font("MS UI Gothic", 24F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.textAdd.Location = new System.Drawing.Point(12, 105);
            this.textAdd.Name = "textAdd";
            this.textAdd.Size = new System.Drawing.Size(697, 39);
            this.textAdd.TabIndex = 11;
            // 
            // label2
            // 
            this.label2.Location = new System.Drawing.Point(7, 83);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(56, 23);
            this.label2.TabIndex = 10;
            this.label2.Text = "住所";
            // 
            // textZip
            // 
            this.textZip.Font = new System.Drawing.Font("MS UI Gothic", 24F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.textZip.Location = new System.Drawing.Point(111, 19);
            this.textZip.Name = "textZip";
            this.textZip.Size = new System.Drawing.Size(264, 39);
            this.textZip.TabIndex = 5;
            // 
            // Comd_Change
            // 
            this.Comd_Change.Location = new System.Drawing.Point(383, 19);
            this.Comd_Change.Name = "Comd_Change";
            this.Comd_Change.Size = new System.Drawing.Size(75, 40);
            this.Comd_Change.TabIndex = 7;
            this.Comd_Change.Text = "変換";
            this.Comd_Change.Click += new System.EventHandler(this.Comd_Change_Click);
            // 
            // label1
            // 
            this.label1.Location = new System.Drawing.Point(7, 27);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(100, 23);
            this.label1.TabIndex = 6;
            this.label1.Text = "郵便番号";
            // 
            // F_OCR_Add
            // 
            this.AcceptButton = this.Comd_Ok;
            this.AutoScaleDimensions = new System.Drawing.SizeF(11F, 21F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.CancelButton = this.Comd_Cancel;
            this.ClientSize = new System.Drawing.Size(721, 156);
            this.Controls.Add(this.Comd_Cancel);
            this.Controls.Add(this.Comd_Ok);
            this.Controls.Add(this.textAdd);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.textZip);
            this.Controls.Add(this.Comd_Change);
            this.Controls.Add(this.label1);
            this.Font = new System.Drawing.Font("ＭＳ Ｐゴシック", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Margin = new System.Windows.Forms.Padding(6, 5, 6, 5);
            this.Name = "F_OCR_Add";
            this.Text = "郵便番号を住所に変換";
            this.Load += new System.EventHandler(this.F_OCR_Add_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button Comd_Cancel;
        private System.Windows.Forms.Button Comd_Ok;
        private System.Windows.Forms.TextBox textAdd;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox textZip;
        private System.Windows.Forms.Button Comd_Change;
        private System.Windows.Forms.Label label1;
    }
}