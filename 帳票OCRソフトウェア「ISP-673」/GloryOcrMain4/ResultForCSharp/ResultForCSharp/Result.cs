using System;

namespace ResultForCSharp
{
	/// <summary>
	/// １帳票分の登録内容
	/// 使用対象
	///   2-13 ParameterInfo
	///   5-12 Result
	/// </summary>
	public class Result
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
		/// ステータス
		/// </summary>
		private int status_;
		/// <summary>
		/// フィールド数
		/// </summary>
		private int fieldCount_;
		/// <summary>
		/// フィールド情報
		/// </summary>
		private FieldForResult [] fieldInfoes_ = null;

		public Result()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public Result(object obj)
		{
			if(obj == null)
			{
				return;
			}

			Array list = (Array)obj;

			// 帳票の登録内容
			docID_ = (int)list.GetValue(0);
			docName_ = list.GetValue(1).ToString();
			status_ = (int)list.GetValue(2);
			fieldCount_ = (int)list.GetValue(3);

			// フィールドの登録内容
			fieldInfoes_ = new FieldForResult[fieldCount_];

			Array fieldlist = (Array)list.GetValue(4);
			for(int i=0; i<fieldCount_; i++)
			{
				object objField = fieldlist.GetValue(i);
				fieldInfoes_[i] = new FieldForResult(objField);
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
		public FieldForResult []  FieldInfoes
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
