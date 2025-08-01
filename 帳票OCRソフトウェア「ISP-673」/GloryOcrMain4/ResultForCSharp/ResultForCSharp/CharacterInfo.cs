using System;

namespace ResultForCSharp
{
	/// <summary>
	/// １文字分の情報
	/// 使用対象
	///   2-14 ParameterInfoEx
	///   5-17 DocumentResultEx
	///   5-20 GetFieldResultEx
	///   5-21 GetFieldCharResult
	/// </summary>
	public class CharacterInfo
	{
		/// <summary>
		/// 候補数
		/// </summary>
		private int count_;
		/// <summary>
		/// 候補数分の文字
		/// </summary>
		private string str_;
		/// <summary>
		/// 信頼レベル
		/// </summary>
		private int level_;
		/// <summary>
		/// 始点X座標
		/// </summary>
		private int left_;
		/// <summary>
		/// 始点Y座標
		/// </summary>
		private int top_;
		/// <summary>
		/// 幅
		/// </summary>
		private int width_;
		/// <summary>
		/// 高さ
		/// </summary>
		private int height_;

		public CharacterInfo()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public CharacterInfo(object obj)
		{
			if(obj == null)
				return;

			Array list = (Array)obj;

			count_ = Convert.ToInt32(list.GetValue(0));
			str_ = list.GetValue(1).ToString();
			level_ = (int)list.GetValue(2);
			left_ = (int)list.GetValue(3);
			top_ = (int)list.GetValue(4);
			width_ = (int)list.GetValue(5);
			height_ = (int)list.GetValue(6);
		}

		/// <summary>
		/// 候補数
		/// </summary>
		public int Count
		{
			get
			{
				return count_;
			}
			set
			{
				count_ = value;
			}
		}
	
		/// <summary>
		/// 候補数分の文字
		/// </summary>
		public string Str
		{
			get
			{
				return str_;
			}
			set
			{
				str_ = value;
			}
		}
	
		/// <summary>
		/// 信頼レベル
		/// </summary>
		public int Level
		{
			get
			{
				return level_;
			}
			set
			{
				level_ = value;
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
	
	}
}
