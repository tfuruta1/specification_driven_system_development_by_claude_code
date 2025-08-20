# Claude Code v10.0 Configuration
VERSION = "10.0"
PRINCIPLES = ["YAGNI", "DRY", "KISS"]

# Development Flows
FLOWS = {
    "new": "要件定義→設計→レビュー→テスト作成→実装→テスト→デモ",
    "existing": "解析→影響報告→修正要件→修正設計→レビュー→テスト作成→実装→テスト→最終確認→デモ"
}

# Simplified Commands (10 basic commands)
COMMANDS = [
    "init", "analyze", "plan", "implement", "test",
    "review", "deploy", "status", "clean", "help"
]
