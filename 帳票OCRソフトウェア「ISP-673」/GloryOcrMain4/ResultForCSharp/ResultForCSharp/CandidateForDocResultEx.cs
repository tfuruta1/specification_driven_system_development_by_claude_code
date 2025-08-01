using System;

namespace ResultForCSharp
{
	/// <summary>
	/// 候補文字列
	/// 使用対象
	///   2-14 ParameterInfoEx
	///   5-17 DocumentResultEx
	/// </summary>
	public class CandidateForDocResultEx
	{
		/// <summary>
		/// 候補文字列
		/// </summary>
		private string candidateString_;
		/// <summary>
		/// 文字列のID
		/// </summary>
		private string candidateStringID_;
		/// <summary>
		/// 信頼度
		/// </summary>
		private int confidence_;

		public CandidateForDocResultEx()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public CandidateForDocResultEx(object obj)
		{
			if(obj == null)
				return;

			Array list = (Array)obj;

			candidateString_ = list.GetValue(0).ToString();
			candidateStringID_ = list.GetValue(1).ToString();
			confidence_ = (int)list.GetValue(2);
		}

		/// <summary>
		/// 候補文字列
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
		/// 文字列のID
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
	}
}
