using System;

namespace ResultForCSharp
{
	/// <summary>
	/// １フィールド分の登録内容
	/// 使用対象
	///   2-14 ParameterInfoEx
	///   5-17 DocumentResultEx
	/// </summary>
	public class FieldForDocResultEx
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
		/// <summary>
		/// 信頼度
		/// </summary>
		private int confidence_;
		/// <summary>
		/// 認識モード１
		/// </summary>
		private int mode1_;
		/// <summary>
		/// 認識モード２
		/// </summary>
		private int mode2_;
		/// <summary>
		/// 認識モード３
		/// </summary>
		private int mode3_;
		/// <summary>
		/// 認識モード４
		/// </summary>
		private int mode4_;
		/// <summary>
		/// 候補文字列数
		/// </summary>
		private int candidateCount_;
		/// <summary>
		/// 候補文字列
		/// </summary>
		private CandidateForDocResultEx [] candidateString_ = null;
		/// <summary>
		/// 文字数
		/// </summary>
		private int characterCount_;
		/// <summary>
		/// 文字情報
		/// </summary>
		private CharacterInfo [] characterInfo_ = null;

		public FieldForDocResultEx()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public FieldForDocResultEx(object obj)
		{
			if(obj == null)
				return;

			Array list = (Array)obj;

			fieldID_ = Convert.ToInt32(list.GetValue(0));
			fieldName_ = list.GetValue(1).ToString();
			left_ = (int)list.GetValue(2);
			top_ = (int)list.GetValue(3);
			width_ = (int)list.GetValue(4);
			height_ = (int)list.GetValue(5);
			status_ = (int)list.GetValue(6);
			result_ = list.GetValue(7).ToString();
			resultID_ = list.GetValue(8).ToString();
			confidence_ = (int)list.GetValue(9);
			mode1_ = (int)list.GetValue(10);
			mode2_ = (int)list.GetValue(11);
			mode3_ = (int)list.GetValue(12);
			mode4_ = (int)list.GetValue(13);

			// 候補文字列
			candidateCount_ = (int)list.GetValue(14);
			candidateString_ = new CandidateForDocResultEx[candidateCount_];
			Array strlist = (Array)list.GetValue(15);
			for(int i=0; i<candidateCount_; i++)
			{
				object objStr = strlist.GetValue(i);
				candidateString_[i] = new CandidateForDocResultEx(objStr);
			}

			// 文字情報
			characterCount_ = (int)list.GetValue(16);
			characterInfo_ = new CharacterInfo[characterCount_];
			Array charlist = (Array)list.GetValue(17);
			for(int i=0; i<characterCount_; i++)
			{
				object objChar = charlist.GetValue(i);
				characterInfo_[i] = new CharacterInfo(objChar);
			}
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

		/// <summary>
		/// 信頼度
		/// </summary>
		public int Confidence
		{
			get
			{
				return confidence_;
			}
			set
			{
				confidence_ = value;
			}
		}
	
		/// <summary>
		/// 認識モード１
		/// </summary>
		public int Mode1
		{
			get
			{
				return mode1_;
			}
			set
			{
				mode1_ = value;
			}
		}
	
		/// <summary>
		/// 認識モード２
		/// </summary>
		public int Mode2
		{
			get
			{
				return mode2_;
			}
			set
			{
				mode2_ = value;
			}
		}
	
		/// <summary>
		/// 認識モード３
		/// </summary>
		public int Mode3
		{
			get
			{
				return mode3_;
			}
			set
			{
				mode3_ = value;
			}
		}
	
		/// <summary>
		/// 認識モード４
		/// </summary>
		public int Mode4
		{
			get
			{
				return mode4_;
			}
			set
			{
				mode4_ = value;
			}
		}
	
		/// <summary>
		/// 候補文字列数
		/// </summary>
		public int CandidateCount
		{
			get
			{
				return candidateCount_;
			}
			set
			{
				candidateCount_ = value;
			}
		}
	
		/// <summary>
		/// 候補文字列
		/// </summary>
		public CandidateForDocResultEx []  CandidateString
		{
			get
			{
				return candidateString_;
			}
			set
			{
				candidateString_ = value;
			}
		}

		/// <summary>
		/// 文字数
		/// </summary>
		public int CharacterCount
		{
			get
			{
				return characterCount_;
			}
			set
			{
				characterCount_ = value;
			}
		}

		/// <summary>
		/// １文字の情報
		/// </summary>
		public CharacterInfo []  CharacterInfo
		{
			get
			{
				return characterInfo_;
			}
			set
			{
				characterInfo_ = value;
			}
		}
	}
}
