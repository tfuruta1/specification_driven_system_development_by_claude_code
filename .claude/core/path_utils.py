"""
パスユーティリティモジュール
Windows/Unix環境の差異を吸収
"""

import os
from pathlib import Path
from typing import Union, List


class PathUtils:
    """クロスプラットフォーム対応のパスユーティリティ"""
    
    @staticmethod
    def normalize_path(path: Union[str, Path]) -> Path:
        """
        パスを正規化（OS依存の差異を吸収）
        
        Args:
            path: 正規化するパス
            
        Returns:
            Path: 正規化されたPathオブジェクト
        """
        if isinstance(path, str):
            # Windows/Unix両対応の区切り文字処理
            path = path.replace('\\', os.sep).replace('/', os.sep)
        return Path(path).resolve()
    
    @staticmethod
    def join_paths(*paths: Union[str, Path]) -> Path:
        """
        複数のパスを結合（OS依存の差異を吸収）
        
        Args:
            *paths: 結合するパス群
            
        Returns:
            Path: 結合されたパス
        """
        if not paths:
            return Path.cwd()
        
        result = PathUtils.normalize_path(paths[0])
        for path in paths[1:]:
            result = result / path
        return result
    
    @staticmethod
    def get_relative_path(path: Union[str, Path], base: Union[str, Path] = None) -> Path:
        """
        相対パスを取得
        
        Args:
            path: 対象パス
            base: 基準パス（省略時は現在のディレクトリ）
            
        Returns:
            Path: 相対パス
        """
        path = PathUtils.normalize_path(path)
        base = PathUtils.normalize_path(base) if base else Path.cwd()
        
        try:
            return path.relative_to(base)
        except ValueError:
            # 異なるドライブなど相対パス化できない場合は絶対パスを返す
            return path
    
    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """
        ディレクトリの存在を保証（なければ作成）
        
        Args:
            path: ディレクトリパス
            
        Returns:
            Path: 作成/確認されたディレクトリパス
        """
        path = PathUtils.normalize_path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def list_files(directory: Union[str, Path], 
                   pattern: str = "*",
                   recursive: bool = False) -> List[Path]:
        """
        ディレクトリ内のファイルをリスト
        
        Args:
            directory: 検索ディレクトリ
            pattern: ファイルパターン（glob形式）
            recursive: 再帰的に検索するか
            
        Returns:
            List[Path]: マッチしたファイルのリスト
        """
        directory = PathUtils.normalize_path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return []
        
        if recursive:
            return sorted(directory.rglob(pattern))
        else:
            return sorted(directory.glob(pattern))
    
    @staticmethod
    def get_project_root() -> Path:
        """
        プロジェクトルートディレクトリを取得
        
        Returns:
            Path: プロジェクトルートパス
        """
        current = Path.cwd()
        
        # .gitディレクトリを探して遡る
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        
        # 見つからない場合は現在のディレクトリ
        return Path.cwd()
    
    @staticmethod
    def get_claude_dir() -> Path:
        """
        .claudeディレクトリを取得
        
        Returns:
            Path: .claudeディレクトリパス
        """
        root = PathUtils.get_project_root()
        return root / '.claude'
    
    @staticmethod
    def format_path_for_display(path: Union[str, Path], 
                               relative_to_project: bool = True) -> str:
        """
        表示用にパスをフォーマット
        
        Args:
            path: フォーマットするパス
            relative_to_project: プロジェクトルートからの相対パスで表示
            
        Returns:
            str: 表示用のパス文字列
        """
        path = PathUtils.normalize_path(path)
        
        if relative_to_project:
            try:
                root = PathUtils.get_project_root()
                path = path.relative_to(root)
            except ValueError:
                pass
        
        # Windows環境でもスラッシュ区切りで統一表示
        return str(path).replace(os.sep, '/')


# シングルトンインスタンス
path_utils = PathUtils()