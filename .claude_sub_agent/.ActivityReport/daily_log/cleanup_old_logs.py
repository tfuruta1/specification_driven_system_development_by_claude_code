#!/usr/bin/env python3
"""
階層型エージェントシステム - 作業日誌自動削除スクリプト
1ヶ月以上経過した作業日誌を自動削除します
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import re

class WorkingLogCleaner:
    """作業日誌のクリーンアップを管理するクラス"""
    
    def __init__(self, log_directory=None, retention_days=30):
        """
        初期化
        
        Args:
            log_directory: ログディレクトリのパス（Noneの場合は現在のディレクトリ）
            retention_days: ログ保持日数（デフォルト30日）
        """
        if log_directory is None:
            self.log_dir = Path(__file__).parent
        else:
            self.log_dir = Path(log_directory)
        
        self.retention_days = retention_days
        self.cutoff_date = datetime.now() - timedelta(days=retention_days)
        self.log_pattern = re.compile(r'(\d{4})-(\d{2})-(\d{2})_workingLog\.md')
        
    def get_log_date(self, filename):
        """
        ファイル名から日付を抽出
        
        Args:
            filename: ログファイル名
            
        Returns:
            datetime: ログの日付（解析できない場合はNone）
        """
        match = self.log_pattern.match(filename)
        if match:
            year, month, day = map(int, match.groups())
            try:
                return datetime(year, month, day)
            except ValueError:
                return None
        return None
    
    def find_old_logs(self):
        """
        削除対象の古いログファイルを検索
        
        Returns:
            list: 削除対象ファイルのリスト
        """
        old_logs = []
        
        for file_path in self.log_dir.glob('*_workingLog.md'):
            # テンプレートファイルはスキップ
            if file_path.name == 'TEMPLATE_workingLog.md':
                continue
                
            log_date = self.get_log_date(file_path.name)
            if log_date and log_date < self.cutoff_date:
                old_logs.append({
                    'path': file_path,
                    'date': log_date,
                    'age_days': (datetime.now() - log_date).days
                })
        
        return sorted(old_logs, key=lambda x: x['date'])
    
    def create_deletion_report(self, old_logs):
        """
        削除レポートを作成
        
        Args:
            old_logs: 削除対象ログのリスト
            
        Returns:
            str: レポート内容
        """
        report = []
        report.append(f"# 作業日誌クリーンアップレポート")
        report.append(f"**実行日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**保持期間**: {self.retention_days}日")
        report.append(f"**削除基準日**: {self.cutoff_date.strftime('%Y-%m-%d')}")
        report.append("")
        
        if old_logs:
            report.append(f"## 削除対象ファイル（{len(old_logs)}件）")
            report.append("")
            report.append("| ファイル名 | 作成日 | 経過日数 | サイズ |")
            report.append("|-----------|--------|---------|--------|")
            
            total_size = 0
            for log in old_logs:
                size = log['path'].stat().st_size
                total_size += size
                size_kb = size / 1024
                report.append(
                    f"| {log['path'].name} | "
                    f"{log['date'].strftime('%Y-%m-%d')} | "
                    f"{log['age_days']}日 | "
                    f"{size_kb:.1f}KB |"
                )
            
            report.append("")
            report.append(f"**合計サイズ**: {total_size/1024:.1f}KB")
        else:
            report.append("## 削除対象なし")
            report.append("保持期間内のログのみが存在します。")
        
        return "\n".join(report)
    
    def delete_old_logs(self, dry_run=False):
        """
        古いログファイルを削除
        
        Args:
            dry_run: True の場合、実際には削除せずレポートのみ生成
            
        Returns:
            dict: 実行結果
        """
        old_logs = self.find_old_logs()
        report = self.create_deletion_report(old_logs)
        
        result = {
            'found': len(old_logs),
            'deleted': 0,
            'errors': [],
            'report': report
        }
        
        if not dry_run and old_logs:
            for log in old_logs:
                try:
                    log['path'].unlink()
                    result['deleted'] += 1
                    print(f"削除: {log['path'].name} ({log['age_days']}日経過)")
                except Exception as e:
                    error_msg = f"削除失敗: {log['path'].name} - {str(e)}"
                    result['errors'].append(error_msg)
                    print(f"エラー: {error_msg}")
        
        # レポートファイルを保存
        report_path = self.log_dir / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        try:
            report_path.write_text(report, encoding='utf-8')
            print(f"\nレポート保存: {report_path.name}")
        except Exception as e:
            print(f"レポート保存失敗: {str(e)}")
        
        return result

def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='階層型エージェントシステムの作業日誌を自動削除'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='ログ保持日数（デフォルト: 30日）'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には削除せず、削除対象のみ表示'
    )
    parser.add_argument(
        '--dir',
        type=str,
        default=None,
        help='ログディレクトリのパス（デフォルト: 現在のディレクトリ）'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("階層型エージェントシステム - 作業日誌クリーンアップ")
    print("=" * 60)
    print(f"保持期間: {args.days}日")
    print(f"モード: {'ドライラン' if args.dry_run else '実行'}")
    print(f"対象ディレクトリ: {args.dir or '現在のディレクトリ'}")
    print("=" * 60)
    print()
    
    cleaner = WorkingLogCleaner(
        log_directory=args.dir,
        retention_days=args.days
    )
    
    result = cleaner.delete_old_logs(dry_run=args.dry_run)
    
    print()
    print("=" * 60)
    print("実行結果:")
    print(f"  検出: {result['found']}件")
    print(f"  削除: {result['deleted']}件")
    if result['errors']:
        print(f"  エラー: {len(result['errors'])}件")
        for error in result['errors']:
            print(f"    - {error}")
    print("=" * 60)
    
    if args.dry_run and result['found'] > 0:
        print("\n※ ドライランモードのため、実際の削除は行われていません")
        print("  実際に削除するには --dry-run オプションを外して実行してください")
    
    return 0 if not result['errors'] else 1

if __name__ == '__main__':
    sys.exit(main())