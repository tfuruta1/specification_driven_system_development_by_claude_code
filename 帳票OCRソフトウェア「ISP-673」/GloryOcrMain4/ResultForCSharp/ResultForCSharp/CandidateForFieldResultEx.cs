using System;

namespace ResultForCSharp
{
	/// <summary>
	/// 候補文字列
	/// 使用対象
	///   5-20 GetFieldResultEx
	///   5-21 GetFieldCharResult
	/// </summary>
	public class CandidateForFieldResultEx
	{
		/// <summary>
		/// 順位
		/// </summary>
		private int rank_;
		/// <summary>
		/// 読み取り結果
		/// </summary>
		private string candidateString_;
		/// <summary>
		/// 読み取り結果のID
		/// </summary>
		private string candidateStringID_;
		/// <summary>
		/// 信頼度
		/// </summary>
		private int confidence_;
		/// <summary>
		/// 文字数
		/// </summary>
		private int characterCount_;
		/// <summary>
		/// １文字分の結果
		/// </summary>
		private CharacterInfo [] characterInfo_ = null;
		/// <summary>
		/// フリカナ
		/// </summary>
		private string furikana_;

		public CandidateForFieldResultEx()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public CandidateForFieldResultEx(object obj)
		{
			if(obj == null)
				return;

			Array list = (Array)obj;

			rank_ = (int)list.GetValue(0);
			candidateString_ = list.GetValue(1).ToString();
			candidateStringID_ = list.GetValue(2).ToString();
			confidence_ = (int)list.GetValue(3);
			characterCount_ = (int)list.GetValue(4);
			characterInfo_ = new CharacterInfo[characterCount_];
			Array charlist = (Array)list.GetValue(5);
			for(int i=0; i<characterCount_; i++)
			{
				object objChar = charlist.GetValue(i);
				characterInfo_[i] = new CharacterInfo(objChar);
			}
			furikana_ = list.GetValue(6).ToString();
		}

		/// <summary>
		/// 順位
		/// </summary>
		public int Rank
		{
			get
			{
				return rank_;
			}
			set
			{
				rank_ = value;
			}
		}

		/// <summary>
		/// 読み取り結果
		/// </summary>
		public string CandidateStr
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
		/// 読み取り結果のID
		/// </summary>
		public string CandidateStrID
		{
			get
			{
				return candidateStringID_;
			}
			set
			{
				candidateStringID_ = value;
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

		public string Furikana
		{
			get
			{
				return furikana_;
			}
			set
			{
				furikana_ = value;
			}
		}
	}
}
