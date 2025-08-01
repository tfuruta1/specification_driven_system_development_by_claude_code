using System;

namespace ResultForCSharp
{
	/// <summary>
	/// 帳票情報リスト
	/// 使用対象
	///   2-11 DocumentListEx
	/// </summary>
	public class DocumentListEx
	{
		/// <summary>
		/// 帳票情報
		/// </summary>
		DocumentInfo [] Documents_ = null;

		public DocumentListEx()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public DocumentListEx(object obj)
		{
			if(obj == null)
				return;

			Array list = (Array)obj;
			Documents_ = new DocumentInfo[list.Length];

			for(int i=0; i<list.Length; i++)
			{
				Documents_[i] = new DocumentInfo();

				Array document = (Array)list.GetValue(i);
				Documents_[i].DocID = (int)document.GetValue(0);
				Documents_[i].DocName = document.GetValue(1).ToString();
				Documents_[i].ParaID = (int)document.GetValue(2);
				Documents_[i].ParaName = document.GetValue(3).ToString();
				Documents_[i].Width = (int)document.GetValue(4);
				Documents_[i].Height = (int)document.GetValue(5);
			}
		}

		/// <summary>
		/// 帳票情報
		/// </summary>
		public DocumentInfo [] Documents
		{
			get
			{
				return Documents_;
			}
			set
			{
				Documents_ = value;
			}
		}

	}
}
