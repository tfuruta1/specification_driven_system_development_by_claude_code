# Analyze Command - エンタープライズプロジェクト分析

## 概要

既存の.NET Framework 4.8プロジェクトを分析し、コード品質、アーキテクチャの健全性、パフォーマンスボトルネック、セキュリティリスクを特定します。

## 使用方法

```
/analyze [オプション]
```

### オプション
- `--architecture` - アーキテクチャ分析（Clean Architecture準拠チェック）
- `--quality` - コード品質分析（複雑度、重複、技術的負債）
- `--performance` - パフォーマンス分析（ボトルネック検出）
- `--security` - セキュリティ脆弱性スキャン
- `--legacy` - レガシーコード検出と移行可能性評価
- `--all` - 全分析実行（デフォルト）

## 実行例

### 包括的分析
```bash
/analyze --all

# 実行結果
エンタープライズプロジェクト分析レポート
========================================

## アーキテクチャ分析
✓ Clean Architecture準拠度: 85%
⚠ 懸念事項:
  - Presentationレイヤーからの直接DB参照: 3箇所
  - ドメインロジックの流出: 2箇所
  
## コード品質
- 循環的複雑度: 平均 4.2（良好）
- コード重複率: 12%（要改善）
- 技術的負債: 120時間相当

## パフォーマンス
⚠ ボトルネック検出:
  - CustomerRepository.GetAll(): N+1問題
  - ReportGenerator: 同期的ファイルI/O
  
## セキュリティ
🔴 高リスク: SQLインジェクション脆弱性（2箇所）
⚠ 中リスク: 暗号化されていない接続文字列（1箇所）

## レガシーコード
- 旧式API使用: 15箇所
- .NET 4.8非推奨機能: 8箇所
- 移行推奨度: 高
```

## 分析項目詳細

### 1. アーキテクチャ分析

#### Clean Architecture準拠チェック
```csharp
public class ArchitectureAnalyzer
{
    public ArchitectureReport Analyze(Solution solution)
    {
        var violations = new List<ArchitectureViolation>();
        
        // 依存関係の方向性チェック
        CheckDependencyDirection(solution, violations);
        
        // レイヤー間の不適切な参照
        CheckLayerViolations(solution, violations);
        
        // ドメインモデルの純粋性
        CheckDomainPurity(solution, violations);
        
        return new ArchitectureReport
        {
            ComplianceScore = CalculateComplianceScore(violations),
            Violations = violations,
            Recommendations = GenerateRecommendations(violations)
        };
    }
    
    private void CheckLayerViolations(Solution solution, List<ArchitectureViolation> violations)
    {
        // Presentationレイヤーからインフラストラクチャへの直接参照
        var presentationProjects = solution.Projects
            .Where(p => p.Name.Contains("Presentation"));
            
        foreach (var project in presentationProjects)
        {
            var infrastructureReferences = project.References
                .Where(r => r.Name.Contains("Infrastructure") || 
                           r.Name.Contains("Data"));
                           
            foreach (var reference in infrastructureReferences)
            {
                violations.Add(new ArchitectureViolation
                {
                    Type = ViolationType.LayerViolation,
                    Severity = Severity.High,
                    Location = $"{project.Name} -> {reference.Name}",
                    Message = "プレゼンテーション層からインフラストラクチャ層への直接参照",
                    Suggestion = "Use Caseまたはインターフェースを介した参照に変更"
                });
            }
        }
    }
}
```

#### 循環参照検出
```csharp
public class CircularDependencyDetector
{
    public List<CircularDependency> DetectCircularDependencies(ProjectGraph graph)
    {
        var cycles = new List<CircularDependency>();
        var visited = new HashSet<string>();
        var recursionStack = new HashSet<string>();
        
        foreach (var project in graph.Projects)
        {
            if (!visited.Contains(project.Name))
            {
                DetectCyclesRecursive(project, visited, recursionStack, cycles, new Stack<string>());
            }
        }
        
        return cycles;
    }
}
```

### 2. コード品質分析

#### 複雑度分析
```csharp
public class ComplexityAnalyzer
{
    public ComplexityReport AnalyzeComplexity(MethodDeclarationSyntax method)
    {
        var walker = new CyclomaticComplexityWalker();
        walker.Visit(method);
        
        return new ComplexityReport
        {
            MethodName = method.Identifier.Text,
            CyclomaticComplexity = walker.Complexity,
            CognitiveComplexity = CalculateCognitiveComplexity(method),
            LineCount = method.GetText().Lines.Count,
            ParameterCount = method.ParameterList.Parameters.Count,
            Risk = DetermineRisk(walker.Complexity)
        };
    }
    
    private ComplexityRisk DetermineRisk(int complexity)
    {
        return complexity switch
        {
            <= 10 => ComplexityRisk.Low,
            <= 20 => ComplexityRisk.Medium,
            <= 50 => ComplexityRisk.High,
            _ => ComplexityRisk.VeryHigh
        };
    }
}
```

#### コード重複検出
```csharp
public class DuplicationDetector
{
    private const int MinimumTokenCount = 50;
    
    public List<CodeDuplication> DetectDuplications(Solution solution)
    {
        var duplications = new List<CodeDuplication>();
        var tokenSequences = new Dictionary<string, List<Location>>();
        
        foreach (var project in solution.Projects)
        {
            foreach (var document in project.Documents)
            {
                var tokens = GetTokenSequence(document);
                FindDuplicateSequences(tokens, tokenSequences, duplications);
            }
        }
        
        return duplications;
    }
}
```

### 3. パフォーマンス分析

#### N+1問題検出
```csharp
public class NPlusOneDetector
{
    public List<NPlusOneProblem> DetectNPlusOneProblems(SemanticModel model)
    {
        var problems = new List<NPlusOneProblem>();
        var loopAnalyzer = new LoopAnalyzer();
        
        // ループ内でのデータベースアクセスを検出
        var loops = loopAnalyzer.FindLoops(model.SyntaxTree.GetRoot());
        
        foreach (var loop in loops)
        {
            var dbAccesses = FindDatabaseAccesses(loop, model);
            
            if (dbAccesses.Any())
            {
                problems.Add(new NPlusOneProblem
                {
                    Location = loop.GetLocation(),
                    LoopType = GetLoopType(loop),
                    DatabaseAccesses = dbAccesses,
                    EstimatedImpact = CalculateImpact(loop, dbAccesses),
                    Suggestion = GenerateSuggestion(dbAccesses)
                });
            }
        }
        
        return problems;
    }
}
```

#### 非効率なLINQクエリ検出
```csharp
public class InefficientLinqDetector
{
    public List<InefficientQuery> DetectInefficientQueries(SyntaxTree tree)
    {
        var inefficientPatterns = new[]
        {
            new Pattern("Count() > 0", "Any()"),
            new Pattern("Where().First()", "First()"),
            new Pattern("Select().ToList().Count", "Count()"),
            new Pattern("OrderBy().First()", "Min()/Max()"),
            new Pattern("ToList().ForEach()", "foreach")
        };
        
        var results = new List<InefficientQuery>();
        
        foreach (var pattern in inefficientPatterns)
        {
            var matches = FindPattern(tree, pattern);
            results.AddRange(matches.Select(m => new InefficientQuery
            {
                Pattern = pattern.Current,
                Suggestion = pattern.Optimized,
                Location = m.GetLocation(),
                EstimatedImprovement = pattern.ImprovementFactor
            }));
        }
        
        return results;
    }
}
```

### 4. セキュリティ分析

#### SQLインジェクション検出
```csharp
public class SqlInjectionDetector
{
    public List<SecurityVulnerability> DetectSqlInjection(SemanticModel model)
    {
        var vulnerabilities = new List<SecurityVulnerability>();
        var stringConcatenations = FindStringConcatenations(model);
        
        foreach (var concatenation in stringConcatenations)
        {
            if (IsSqlQuery(concatenation) && ContainsUserInput(concatenation))
            {
                vulnerabilities.Add(new SecurityVulnerability
                {
                    Type = VulnerabilityType.SqlInjection,
                    Severity = Severity.Critical,
                    Location = concatenation.GetLocation(),
                    Description = "SQL文字列に直接ユーザー入力を結合しています",
                    Remediation = "パラメータ化クエリまたはストアドプロシージャを使用してください"
                });
            }
        }
        
        return vulnerabilities;
    }
}
```

#### 暗号化チェック
```csharp
public class EncryptionAnalyzer
{
    public List<EncryptionIssue> AnalyzeEncryption(Project project)
    {
        var issues = new List<EncryptionIssue>();
        
        // 接続文字列の暗号化チェック
        CheckConnectionStrings(project, issues);
        
        // 機密データの平文保存チェック
        CheckSensitiveDataStorage(project, issues);
        
        // 弱い暗号アルゴリズムの使用チェック
        CheckWeakAlgorithms(project, issues);
        
        return issues;
    }
}
```

### 5. レガシーコード分析

#### 旧式API使用検出
```csharp
public class LegacyApiDetector
{
    private readonly Dictionary<string, ModernAlternative> _legacyApis = new()
    {
        ["System.Web.HttpContext"] = new("Microsoft.AspNetCore.Http.HttpContext", ".NET Core移行推奨"),
        ["System.Data.SqlClient"] = new("Microsoft.Data.SqlClient", "新しいSqlClientパッケージ"),
        ["System.Configuration.ConfigurationManager"] = new("Microsoft.Extensions.Configuration", "構成の抽象化"),
        ["System.Web.Mail"] = new("System.Net.Mail", "廃止されたAPI")
    };
    
    public List<LegacyApiUsage> DetectLegacyApis(Solution solution)
    {
        var usages = new List<LegacyApiUsage>();
        
        foreach (var project in solution.Projects)
        {
            var compilation = project.GetCompilationAsync().Result;
            
            foreach (var syntaxTree in compilation.SyntaxTrees)
            {
                var semanticModel = compilation.GetSemanticModel(syntaxTree);
                var apiUsages = FindApiUsages(syntaxTree, semanticModel);
                
                foreach (var usage in apiUsages)
                {
                    if (_legacyApis.ContainsKey(usage.TypeName))
                    {
                        var alternative = _legacyApis[usage.TypeName];
                        usages.Add(new LegacyApiUsage
                        {
                            Api = usage.TypeName,
                            Location = usage.Location,
                            ModernAlternative = alternative.Name,
                            MigrationNote = alternative.Note,
                            EstimatedEffort = EstimateMigrationEffort(usage)
                        });
                    }
                }
            }
        }
        
        return usages;
    }
}
```

## レポート生成

### HTML形式レポート
```csharp
public class AnalysisReportGenerator
{
    public void GenerateHtmlReport(ComprehensiveAnalysisResult result, string outputPath)
    {
        var html = new StringBuilder();
        
        html.AppendLine("<!DOCTYPE html>");
        html.AppendLine("<html><head>");
        html.AppendLine("<title>エンタープライズプロジェクト分析レポート</title>");
        html.AppendLine(GetStyleSheet());
        html.AppendLine("</head><body>");
        
        // エグゼクティブサマリー
        GenerateExecutiveSummary(html, result);
        
        // 詳細分析結果
        GenerateArchitectureSection(html, result.Architecture);
        GenerateQualitySection(html, result.Quality);
        GeneratePerformanceSection(html, result.Performance);
        GenerateSecuritySection(html, result.Security);
        GenerateLegacySection(html, result.Legacy);
        
        // 改善ロードマップ
        GenerateImprovementRoadmap(html, result);
        
        html.AppendLine("</body></html>");
        
        File.WriteAllText(outputPath, html.ToString());
    }
}
```

## 継続的分析

### 自動分析の設定
```xml
<!-- .csproj ファイルに追加 -->
<Target Name="CodeAnalysis" AfterTargets="Build">
  <Exec Command="dotnet tool run analyze --all --output $(OutputPath)analysis-report.html" />
</Target>
```

### CI/CD統合
```yaml
# Azure DevOps Pipeline
- task: DotNetCoreCLI@2
  displayName: 'Run Code Analysis'
  inputs:
    command: 'custom'
    custom: 'tool'
    arguments: 'run analyze --all --threshold error'
```

## まとめ

このコマンドにより、エンタープライズ.NET Frameworkプロジェクトの包括的な分析を実行し、以下を実現します：

1. **アーキテクチャの健全性確保** - Clean Architecture準拠の継続的チェック
2. **コード品質の可視化** - 技術的負債の定量化と管理
3. **パフォーマンス問題の早期発見** - ボトルネックの特定と改善提案
4. **セキュリティリスクの低減** - 脆弱性の自動検出と修正ガイダンス
5. **計画的なモダナイゼーション** - レガシーコードの段階的な改善