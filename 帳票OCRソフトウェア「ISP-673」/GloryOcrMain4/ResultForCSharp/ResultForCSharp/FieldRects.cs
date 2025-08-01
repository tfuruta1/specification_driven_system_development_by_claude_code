using System;
using System.Drawing;

namespace ResultForCSharp
{
	/// <summary>
	/// 読み取り領域
	/// 使用対象
	///   5-23 GetDocumentImage
	///   5-24 GetDocumentImageFn
	///   5-25 GetDocumentImageP
	/// </summary>
	public class FieldRects
	{
		/// <summary>
		/// 領域
		/// </summary>
		Rectangle [] rects_ = null;

		public FieldRects()
		{
		}

		/// <summary>
		/// コンストラクタ
		/// </summary>
		/// <param name="obj">VARIANTオブジェクト</param>
		public FieldRects(object obj)
		{
			if(obj == null)
				return;

			Array list = (Array)obj;
			rects_ = new Rectangle[list.Length];

			for(int i=0; i<list.Length; i++)
			{
				Array field = (Array)list.GetValue(i);
				int left = (int)field.GetValue(0);
				int top = (int)field.GetValue(1);
				int width = (int)field.GetValue(2);
				int height = (int)field.GetValue(3);

				rects_[i] = new Rectangle(left, top, width, height);
			}
		}

		/// <summary>
		/// 領域
		/// </summary>
		public Rectangle [] Fields
		{
			get
			{
				return rects_;
			}
			set
			{
				rects_ = value;
			}
		}
	}
}
