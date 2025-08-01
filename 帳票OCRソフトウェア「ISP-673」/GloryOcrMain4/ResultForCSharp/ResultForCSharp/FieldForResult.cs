using System;

namespace ResultForCSharp
{
	/// <summary>
	/// １フィールド分の登録内容
	/// 使用対象
	///   2-13 ParameterInfo
	///   5-12 Result
	/// </summary>
	public class FieldForResult
	{
		/// <summary>
		/// フィールドID
		/// </summary>
		private int fieldID_;
		/// <summary>
		/// フィールド名称
		/// </summary>
		private string fieldName_;
		/// <summary>
		/// 始点Y座標
		/// </summary>
		private int top_;
		/// <summary>
		/// 始点X座標
		/// </summary>
		private int left_;
		/// <summary>
		/// 幅
		/// </summary>
		private int width_;
		/// <summary>
		/// 高さ
		/// </summary>
		private int height_;
		/// <summary>
		/// ステータス
		/// </summary>
		private int status_;
		/// <summary>
		/// 結果
		/// </summary>
		private string result_;
		/// <summary>
		/// 結果のID
		/// </summary>
		private string resultID_;

		public FieldForResult()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public FieldForResult(object obj)
		{
			if(obj == null)
				return;

			Array list = (Array)obj;

			fieldID_ =(int)list.GetValue(0);
			fieldName_ = list.GetValue(1).ToString();
			left_ = (int)list.GetValue(2);
			top_ = (int)list.GetValue(3);
			width_ = (int)list.GetValue(4);
			height_ = (int)list.GetValue(5);
			status_ = (int)list.GetValue(6);
			result_ = list.GetValue(7).ToString();
			resultID_ = list.GetValue(8).ToString();
		}

		/// <summary>
		/// フィールドID
		/// </summary>
		public int FieldID
		{
			get
			{
				return fieldID_;
			}
			set
			{
				fieldID_ = value;
			}
		}

		/// <summary>
		/// フィールド名称
		/// </summary>
		public string FieldName
		{
			get
			{
				return fieldName_;
			}
			set
			{
				fieldName_ = value;
			}
		}

		/// <summary>
		/// 始点Y座標
		/// </summary>
		public int Top
		{
			get
			{
				return top_;
			}
			set
			{
				top_ = value;
			}
		}
	
		/// <summary>
		/// 始点X座標
		/// </summary>
		public int Left
		{
			get
			{
				return left_;
			}
			set
			{
				left_ = value;
			}

		}

		/// <summary>
		/// 高さ
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
		/// 幅
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
		/// 結果
		/// </summary>
		public string Result
		{
			get
			{
				return result_;
			}
			set
			{
				result_ = value;
			}
		}

		/// <summary>
		/// 結果のID
		/// </summary>
		public string ResultID
		{
			get
			{
				return resultID_;
			}
			set
			{
				resultID_ = value;
			}
		}
	}
}
