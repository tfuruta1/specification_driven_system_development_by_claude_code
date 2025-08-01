using System;

namespace ResultForCSharp
{
	/// <summary>
	/// １帳票分の登録内容
	/// 使用対象
	///   2-14 ParameterInfoEx
	///   5-17 DocumentResultEx
	/// </summary>
	public class DocumentResultEx
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
		/// ステータス
		/// </summary>
		private int status_;
		/// <summary>
		/// 帳票の向き
		/// </summary>
		private int direction_;
		/// <summary>
		/// 帳票の４頂点
		/// </summary>
		private System.Drawing.Point [] point_ = null;
		/// <summary>
		/// フィールド数
		/// </summary>
		private int fieldCount_;
		/// <summary>
		/// フィールド情報
		/// </summary>
		private FieldForDocResultEx [] fieldInfoes_ = null;

		public DocumentResultEx()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public DocumentResultEx(object obj)
		{
			if(obj == null)
			{
				return;
			}

			Array list = (Array)obj;

			// 帳票の登録内容
			docID_ = (int)list.GetValue(0);
			docName_ = list.GetValue(1).ToString();
			paraID_ = (int)list.GetValue(2);
			paraName_ = list.GetValue(3).ToString();
			status_ = (int)list.GetValue(4);
			direction_ = (int)list.GetValue(5);

			Array pointList = (Array)list.GetValue(6);
			if(pointList != null)
			{
				point_ = new System.Drawing.Point[4];
				point_[0].X = (int)pointList.GetValue(0);
				point_[0].Y = (int)pointList.GetValue(1);
				point_[1].X = (int)pointList.GetValue(2);
				point_[1].Y = (int)pointList.GetValue(3);
				point_[2].X = (int)pointList.GetValue(4);
				point_[2].Y = (int)pointList.GetValue(5);
				point_[3].X = (int)pointList.GetValue(6);
				point_[3].Y = (int)pointList.GetValue(7);
			}

			fieldCount_ = (int)list.GetValue(7);

			// フィールドの登録内容
			fieldInfoes_ = new FieldForDocResultEx[fieldCount_];

			Array fieldlist = (Array)list.GetValue(8);
			for(int i=0; i<fieldCount_; i++)
			{
				object objField = fieldlist.GetValue(i);
				fieldInfoes_[i] = new FieldForDocResultEx(objField);
			}
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
		/// ステータス
		/// </summary>
		public int Status
		{
			get
			{
				return status_;
			}
			set
			{
				status_ = value;
			}
		}


		/// <summary>
		/// 帳票の向き
		/// </summary>
		public int Direction
		{
			get
			{
				return direction_;
			}
			set
			{
				direction_ = value;
			}
		}

		/// <summary>
		/// 帳票の４頂点
		/// </summary>
		public System.Drawing.Point [] Point
		{
			get
			{
				return point_;
			}
			set
			{
				point_ = value;
			}
		}

		/// <summary>
		/// フィールド数
		/// </summary>
		public int FieldCount
		{
			get
			{
				return fieldCount_;
			}
			set
			{
				fieldCount_ = value;
			}
		}

		/// <summary>
		/// フィールド情報
		/// </summary>
		public FieldForDocResultEx []  FieldInfoes
		{
			get
			{
				return fieldInfoes_;
			}
			set
			{
				fieldInfoes_ = value;
			}
		}
	}
}
