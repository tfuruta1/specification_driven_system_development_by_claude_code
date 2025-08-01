using System;

namespace ResultForCSharp
{
	/// <summary>
	/// 帳票情報
	/// 使用対象
	///   2-11 DocumentListEx
	/// </summary>
	public class DocumentInfo
	{
		/// <summary>
		/// 帳票ID
		/// </summary>
		private int docID_;
		/// <summary>
		/// 帳票名称
		/// </summary>
		private string docName_;
		/// <summary>
		/// パラメータID
		/// </summary>
		private int paraID_;
		/// <summary>
		/// パラメータ名称
		/// </summary>
		private string paraName_;
		/// <summary>
		/// 高さ
		/// </summary>
		private int height_;
		/// <summary>
		/// 幅
		/// </summary>
		private int width_;

		public DocumentInfo()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public DocumentInfo(int docID, string docName, int paraID, string paraName, int height, int width)
		{
			docID_ = docID;
			docName_ = docName;
			paraID_ = paraID;
			paraName_ = paraName;
			height_ = height;
			width_ = width;
		}

		/// <summary>
		/// 帳票ID
		/// </summary>
		public int DocID
		{
			get
			{
				return docID_;
			}
			set
			{
				docID_ = value;
			}
		}

		/// <summary>
		/// 帳票名称
		/// </summary>
		public string DocName
		{
			get
			{
				return docName_;
			}
			set
			{
				docName_ = value;
			}
		}

		/// <summary>
		/// パラメータID
		/// </summary>
		public int ParaID
		{
			get
			{
				return paraID_;
			}
			set
			{
				paraID_ = value;
			}
		}

		/// <summary>
		/// パラメータ名称
		/// </summary>
		public string ParaName
		{
			get
			{
				return paraName_;
			}
			set
			{
				paraName_ = value;
			}
		}

		/// <summary>
		/// 帳票の高さ
		/// </summary>
		public int Height
		{
			get
			{
				return height_;
			}
			set
			{
				height_ = value;
			}
		}

		/// <summary>
		/// 帳票の幅
		/// </summary>
		public int Width
		{
			get
			{
				return width_;
			}
			set
			{
				width_ = value;
			}
		}
	}
}
