# Tasks Command - エンタープライズタスク分割

## 概要

エンタープライズシステム開発における大規模な要件を、実装可能な単位のタスクに分割し、優先順位付けと工数見積もりを行うコマンドです。TodoWrite統合により、効率的なタスク管理を実現します。

## 使用方法

```
/tasks [オプション]
```

### オプション
- `--breakdown` - タスク分解（エピック→ストーリー→タスク）
- `--estimate` - 工数見積もり
- `--prioritize` - 優先順位付け
- `--schedule` - スケジュール作成
- `--assign` - タスク割り当て
- `--all` - 全タスク管理プロセス実行（デフォルト）

## 実行フロー

### タスク管理プロセス
```mermaid
graph LR
    A[要件分析] --> B[エピック定義]
    B --> C[ストーリー分割]
    C --> D[タスク詳細化]
    D --> E[見積もり]
    E --> F[優先順位付け]
    F --> G[スケジューリング]
    G --> H[TodoWrite登録]
```

## タスク階層構造

### エピック・ストーリー・タスク
```csharp
// タスク階層モデル
public class Epic
{
    public string Id { get; set; }
    public string Title { get; set; }
    public string Description { get; set; }
    public BusinessValue BusinessValue { get; set; }
    public List<UserStory> Stories { get; set; }
    public int TotalStoryPoints => Stories.Sum(s => s.StoryPoints);
}

public class UserStory
{
    public string Id { get; set; }
    public string EpicId { get; set; }
    public string Title { get; set; }
    public string AsA { get; set; }         // As a [role]
    public string IWantTo { get; set; }     // I want to [action]
    public string SoThat { get; set; }      // So that [benefit]
    public List<AcceptanceCriteria> Criteria { get; set; }
    public int StoryPoints { get; set; }
    public Priority Priority { get; set; }
    public List<DevelopmentTask> Tasks { get; set; }
}

public class DevelopmentTask
{
    public string Id { get; set; }
    public string StoryId { get; set; }
    public string Title { get; set; }
    public string Description { get; set; }
    public TaskType Type { get; set; }
    public int EstimatedHours { get; set; }
    public TaskStatus Status { get; set; }
    public List<string> Dependencies { get; set; }
    public string AssignedTo { get; set; }
}
```

### タスクタイプ定義
```csharp
public enum TaskType
{
    Design,              // 設計タスク
    Implementation,      // 実装タスク
    DatabaseWork,        // DB関連作業
    Integration,         // 統合作業
    Testing,            // テスト作業
    Documentation,      // ドキュメント作成
    Refactoring,        // リファクタリング
    BugFix,             // バグ修正
    Research            // 調査・検証
}

public enum Priority
{
    Critical,   // 緊急かつ重要
    High,       // 重要
    Medium,     // 通常
    Low         // 低優先度
}
```

## タスク分解パターン

### 機能別分解
```markdown
## Epic: 顧客管理システム

### Story 1: 顧客情報の登録
- **Task 1.1**: 顧客エンティティ設計 (Design, 4h)
- **Task 1.2**: データベーステーブル作成 (DatabaseWork, 2h)
- **Task 1.3**: リポジトリ実装 (Implementation, 6h)
- **Task 1.4**: 顧客登録フォーム作成 (Implementation, 8h)
- **Task 1.5**: バリデーション実装 (Implementation, 4h)
- **Task 1.6**: 単体テスト作成 (Testing, 4h)

### Story 2: 顧客情報の検索
- **Task 2.1**: 検索条件設計 (Design, 3h)
- **Task 2.2**: 検索クエリ最適化 (DatabaseWork, 4h)
- **Task 2.3**: 検索サービス実装 (Implementation, 6h)
- **Task 2.4**: 検索画面作成 (Implementation, 8h)
- **Task 2.5**: ページング実装 (Implementation, 4h)
- **Task 2.6**: 統合テスト作成 (Testing, 6h)
```

### レイヤー別分解
```csharp
// Clean Architecture レイヤー別タスク生成
public class LayerBasedTaskGenerator
{
    public List<DevelopmentTask> GenerateTasksForStory(UserStory story)
    {
        var tasks = new List<DevelopmentTask>();
        
        // Domain Layer タスク
        tasks.Add(new DevelopmentTask
        {
            Title = $"{story.Title} - ドメインモデル設計",
            Type = TaskType.Design,
            EstimatedHours = 4
        });
        
        tasks.Add(new DevelopmentTask
        {
            Title = $"{story.Title} - エンティティ実装",
            Type = TaskType.Implementation,
            EstimatedHours = 6
        });
        
        // Application Layer タスク
        tasks.Add(new DevelopmentTask
        {
            Title = $"{story.Title} - ユースケース実装",
            Type = TaskType.Implementation,
            EstimatedHours = 8
        });
        
        // Infrastructure Layer タスク
        tasks.Add(new DevelopmentTask
        {
            Title = $"{story.Title} - リポジトリ実装",
            Type = TaskType.Implementation,
            EstimatedHours = 6
        });
        
        // Presentation Layer タスク
        tasks.Add(new DevelopmentTask
        {
            Title = $"{story.Title} - UI実装",
            Type = TaskType.Implementation,
            EstimatedHours = 10
        });
        
        // Cross-cutting タスク
        tasks.Add(new DevelopmentTask
        {
            Title = $"{story.Title} - ログ・例外処理",
            Type = TaskType.Implementation,
            EstimatedHours = 3
        });
        
        // Testing タスク
        tasks.Add(new DevelopmentTask
        {
            Title = $"{story.Title} - テスト実装",
            Type = TaskType.Testing,
            EstimatedHours = 8
        });
        
        return tasks;
    }
}
```

## 工数見積もり

### 見積もりテクニック
```csharp
// 三点見積もり法
public class ThreePointEstimation
{
    public EstimationResult Estimate(
        int optimistic,    // 楽観的見積もり
        int mostLikely,    // 最も可能性の高い見積もり
        int pessimistic)   // 悲観的見積もり
    {
        // PERT（Program Evaluation and Review Technique）
        double expected = (optimistic + 4 * mostLikely + pessimistic) / 6.0;
        double standardDeviation = (pessimistic - optimistic) / 6.0;
        
        return new EstimationResult
        {
            Expected = Math.Round(expected, 1),
            StandardDeviation = Math.Round(standardDeviation, 1),
            Confidence68Percent = new Range(
                expected - standardDeviation,
                expected + standardDeviation),
            Confidence95Percent = new Range(
                expected - 2 * standardDeviation,
                expected + 2 * standardDeviation)
        };
    }
}

// ストーリーポイント見積もり
public class StoryPointEstimator
{
    private readonly Dictionary<string, int> _referenceStories;
    
    public int EstimateStoryPoints(UserStory story)
    {
        // フィボナッチ数列: 1, 2, 3, 5, 8, 13, 21
        var complexity = CalculateComplexity(story);
        var effort = CalculateEffort(story);
        var uncertainty = CalculateUncertainty(story);
        
        var totalScore = complexity + effort + uncertainty;
        
        // スコアをストーリーポイントにマッピング
        if (totalScore <= 3) return 1;
        if (totalScore <= 5) return 2;
        if (totalScore <= 8) return 3;
        if (totalScore <= 13) return 5;
        if (totalScore <= 21) return 8;
        if (totalScore <= 34) return 13;
        return 21;
    }
}
```

### 見積もりテンプレート
```markdown
## タスク見積もりシート

### タスク情報
- **タスク名**: 顧客検索API実装
- **タイプ**: Implementation
- **担当者**: 未定

### 見積もり内訳
| 作業項目 | 楽観 | 標準 | 悲観 | 期待値 |
|---------|------|------|------|--------|
| API設計 | 2h | 3h | 5h | 3.2h |
| 実装 | 4h | 6h | 10h | 6.3h |
| テスト | 2h | 3h | 4h | 3.0h |
| ドキュメント | 1h | 2h | 3h | 2.0h |
| **合計** | **9h** | **14h** | **22h** | **14.5h** |

### リスク要因
- [ ] 既存システムとの連携複雑性
- [ ] パフォーマンス要件の厳しさ
- [ ] 技術的な不確実性

### バッファ
- 技術リスクバッファ: 20%
- 統合リスクバッファ: 15%
- **最終見積もり**: 16.7h
```

## 優先順位付け

### MoSCoWメソッド
```csharp
public class MoSCoWPrioritizer
{
    public PrioritizedBacklog Prioritize(List<UserStory> stories)
    {
        var backlog = new PrioritizedBacklog();
        
        foreach (var story in stories)
        {
            var priority = DeterminePriority(story);
            
            switch (priority)
            {
                case MoSCoWPriority.Must:
                    backlog.MustHave.Add(story);
                    break;
                case MoSCoWPriority.Should:
                    backlog.ShouldHave.Add(story);
                    break;
                case MoSCoWPriority.Could:
                    backlog.CouldHave.Add(story);
                    break;
                case MoSCoWPriority.Wont:
                    backlog.WontHave.Add(story);
                    break;
            }
        }
        
        return backlog;
    }
    
    private MoSCoWPriority DeterminePriority(UserStory story)
    {
        // ビジネス価値、リスク、依存関係を考慮
        var score = 0;
        
        // ビジネス価値スコア (0-10)
        score += story.BusinessValue;
        
        // 技術的リスクスコア (0-5)
        score += story.TechnicalRisk;
        
        // 依存関係スコア (0-5)
        score += story.Dependencies.Count * 2;
        
        if (score >= 15) return MoSCoWPriority.Must;
        if (score >= 10) return MoSCoWPriority.Should;
        if (score >= 5) return MoSCoWPriority.Could;
        return MoSCoWPriority.Wont;
    }
}
```

### 価値対工数マトリクス
```csharp
// 価値対工数による優先順位付け
public class ValueEffortMatrix
{
    public List<PrioritizedItem> Analyze(List<UserStory> stories)
    {
        var items = new List<PrioritizedItem>();
        
        foreach (var story in stories)
        {
            var value = CalculateBusinessValue(story);
            var effort = story.TotalEstimatedHours;
            var ratio = value / (double)effort;
            
            var quadrant = DetermineQuadrant(value, effort);
            
            items.Add(new PrioritizedItem
            {
                Story = story,
                Value = value,
                Effort = effort,
                ValueEffortRatio = ratio,
                Quadrant = quadrant,
                RecommendedAction = GetRecommendation(quadrant)
            });
        }
        
        return items.OrderByDescending(i => i.ValueEffortRatio).ToList();
    }
    
    private Quadrant DetermineQuadrant(int value, int effort)
    {
        if (value >= 7 && effort <= 20) return Quadrant.QuickWins;      // 高価値・低労力
        if (value >= 7 && effort > 20) return Quadrant.MajorProjects;   // 高価値・高労力
        if (value < 7 && effort <= 20) return Quadrant.FillIns;         // 低価値・低労力
        return Quadrant.Thankless;                                       // 低価値・高労力
    }
}
```

## スケジューリング

### スプリント計画
```csharp
// スプリント計画生成
public class SprintPlanner
{
    private readonly int _sprintCapacityHours;
    private readonly int _teamVelocity;
    
    public List<Sprint> PlanSprints(
        PrioritizedBacklog backlog, 
        DateTime startDate, 
        int numberOfSprints)
    {
        var sprints = new List<Sprint>();
        var remainingStories = new List<UserStory>();
        
        // Must Have から順に割り当て
        remainingStories.AddRange(backlog.MustHave);
        remainingStories.AddRange(backlog.ShouldHave);
        remainingStories.AddRange(backlog.CouldHave);
        
        for (int i = 0; i < numberOfSprints; i++)
        {
            var sprint = new Sprint
            {
                Number = i + 1,
                StartDate = startDate.AddDays(i * 14),
                EndDate = startDate.AddDays((i + 1) * 14 - 1),
                Capacity = _sprintCapacityHours
            };
            
            var currentCapacity = 0;
            var storesToRemove = new List<UserStory>();
            
            foreach (var story in remainingStories)
            {
                if (currentCapacity + story.TotalEstimatedHours <= _sprintCapacityHours)
                {
                    sprint.Stories.Add(story);
                    currentCapacity += story.TotalEstimatedHours;
                    storesToRemove.Add(story);
                }
            }
            
            foreach (var story in storesToRemove)
            {
                remainingStories.Remove(story);
            }
            
            sprint.PlannedHours = currentCapacity;
            sprints.Add(sprint);
        }
        
        return sprints;
    }
}
```

### ガントチャート生成
```csharp
// ガントチャートデータ生成
public class GanttChartGenerator
{
    public GanttChartData GenerateChart(List<DevelopmentTask> tasks)
    {
        var chart = new GanttChartData();
        
        // 依存関係の解決
        var scheduledTasks = ScheduleTasksWithDependencies(tasks);
        
        foreach (var task in scheduledTasks)
        {
            chart.Items.Add(new GanttItem
            {
                TaskId = task.Id,
                TaskName = task.Title,
                StartDate = task.ScheduledStart,
                EndDate = task.ScheduledEnd,
                Progress = task.Progress,
                Dependencies = task.Dependencies,
                AssignedTo = task.AssignedTo,
                Color = GetColorByTaskType(task.Type)
            });
        }
        
        return chart;
    }
    
    private List<ScheduledTask> ScheduleTasksWithDependencies(
        List<DevelopmentTask> tasks)
    {
        // トポロジカルソートで依存関係を考慮したスケジューリング
        var sorted = TopologicalSort(tasks);
        var scheduled = new List<ScheduledTask>();
        var taskEndDates = new Dictionary<string, DateTime>();
        
        foreach (var task in sorted)
        {
            var startDate = DateTime.Now;
            
            // 依存タスクの完了日を考慮
            foreach (var dep in task.Dependencies)
            {
                if (taskEndDates.ContainsKey(dep))
                {
                    var depEndDate = taskEndDates[dep];
                    if (depEndDate > startDate)
                    {
                        startDate = depEndDate.AddDays(1);
                    }
                }
            }
            
            var endDate = AddWorkingHours(startDate, task.EstimatedHours);
            taskEndDates[task.Id] = endDate;
            
            scheduled.Add(new ScheduledTask
            {
                Task = task,
                ScheduledStart = startDate,
                ScheduledEnd = endDate
            });
        }
        
        return scheduled;
    }
}
```

## TodoWrite統合

### 自動タスク登録
```csharp
// TodoWriteへの自動登録
public class TodoWriteIntegration
{
    private readonly ITodoWriteService _todoService;
    
    public async Task RegisterTasksAsync(List<DevelopmentTask> tasks)
    {
        var todos = new List<TodoItem>();
        
        foreach (var task in tasks)
        {
            var todo = new TodoItem
            {
                Id = Guid.NewGuid().ToString(),
                Content = FormatTodoContent(task),
                Status = MapTaskStatus(task.Status),
                Priority = MapTaskPriority(task.Priority)
            };
            
            todos.Add(todo);
        }
        
        // TodoWriteに一括登録
        await _todoService.BulkCreateAsync(todos);
    }
    
    private string FormatTodoContent(DevelopmentTask task)
    {
        return $"[{task.Type}] {task.Title} ({task.EstimatedHours}h) - {task.StoryId}";
    }
    
    private TodoStatus MapTaskStatus(TaskStatus status)
    {
        return status switch
        {
            TaskStatus.NotStarted => TodoStatus.Pending,
            TaskStatus.InProgress => TodoStatus.InProgress,
            TaskStatus.Completed => TodoStatus.Completed,
            _ => TodoStatus.Pending
        };
    }
}
```

## 出力成果物

### タスク管理ドキュメント
```
tasks/
├── epic_list.md                # エピック一覧
├── user_stories/               # ユーザーストーリー
│   ├── epic_001/
│   │   ├── story_001.md
│   │   ├── story_002.md
│   │   └── story_003.md
│   └── epic_002/
├── task_breakdown.md           # タスク分解WBS
├── estimation_report.md        # 見積もりレポート
├── priority_matrix.md          # 優先順位マトリクス
├── sprint_plan.md             # スプリント計画
├── gantt_chart.html           # ガントチャート
└── resource_allocation.md     # リソース配分表
```

### タスク一覧サンプル
```markdown
## Sprint 1 タスク一覧

### 高優先度タスク (Must Have)
| ID | タスク名 | タイプ | 見積 | 担当 | 状態 |
|----|---------|--------|------|------|------|
| T001 | 顧客エンティティ設計 | Design | 4h | Alice | 完了 |
| T002 | 顧客テーブル作成 | Database | 2h | Bob | 進行中 |
| T003 | 顧客リポジトリ実装 | Implementation | 6h | Carol | 未着手 |

### 依存関係
- T003 は T001 に依存
- T003 は T002 に依存

### 進捗サマリー
- 完了: 1タスク (4h)
- 進行中: 1タスク (2h)
- 未着手: 1タスク (6h)
- **進捗率**: 33.3%
```

## 実行例

```bash
/tasks --all

# 実行結果
✓ 要件分析完了
✓ 5個のエピックを定義
✓ 23個のユーザーストーリーを作成
✓ 156個のタスクに分解
✓ 工数見積もり完了（合計: 1,248時間）
✓ 優先順位付け完了
✓ 6スプリントの計画を作成
✓ TodoWriteに156タスクを登録

生成されたドキュメント:
- tasks/epic_list.md
- tasks/user_stories/ (23 files)
- tasks/task_breakdown.md
- tasks/sprint_plan.md
```

## ベストプラクティス

### 1. 適切な粒度
- タスクは1日以内で完了可能なサイズに
- ストーリーは1スプリント以内
- エピックは1-3ヶ月程度

### 2. 明確な完了条件
- 各タスクに具体的な成果物を定義
- 受入基準の明確化
- テスト可能な条件設定

### 3. 継続的な見直し
- スプリントレトロスペクティブ
- 見積もり精度の改善
- 優先順位の再評価

## まとめ

このコマンドにより、大規模なエンタープライズシステム開発を管理可能な単位に分解し、効率的なプロジェクト管理を実現します。TodoWrite統合により、日々のタスク管理もシームレスに行えます。