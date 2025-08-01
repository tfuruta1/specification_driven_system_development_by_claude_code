# Standardize Command - コード標準化

## 概要

エンタープライズ.NET Framework 4.8プロジェクト全体のコーディング規約を統一し、一貫性のあるコードベースを維持します。命名規則、フォーマット、ベストプラクティスの適用を自動化します。

## 使用方法

```
/standardize <標準化タイプ> [オプション]
```

### 標準化タイプ
- `naming` - 命名規則の統一
- `format` - コードフォーマット
- `structure` - プロジェクト構造の標準化
- `patterns` - デザインパターンの適用
- `security` - セキュリティ標準の適用
- `performance` - パフォーマンス最適化標準
- `all` - すべての標準化を実行

### オプション
- `--check` - 違反チェックのみ（修正なし）
- `--fix` - 自動修正を実行
- `--report` - 詳細レポートを生成
- `--config <path>` - カスタム規約設定ファイルを使用

## 実行例

### 1. 命名規則の統一

```bash
/standardize naming --fix

# 実行結果
命名規則標準化
==============

## 検出された違反
- パブリックメソッド名: 45件（camelCase → PascalCase）
- プライベートフィールド: 128件（_prefix不足）
- 定数: 23件（UPPER_CASE → PascalCase）
- インターフェース: 8件（Iプレフィックス不足）

## 自動修正完了
- 204件中198件を自動修正
- 6件は手動修正が必要
```

#### 命名規則チェッカーの実装

```csharp
public class NamingConventionAnalyzer : DiagnosticAnalyzer
{
    public const string DiagnosticId = "NC001";
    private const string Category = "Naming";
    
    // サポートする診断
    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
        ImmutableArray.Create(
            PublicMethodRule,
            PrivateFieldRule,
            InterfaceRule,
            ConstantRule);
    
    private static readonly DiagnosticDescriptor PublicMethodRule = new(
        DiagnosticId + "_Method",
        "パブリックメソッドはPascalCaseを使用",
        "メソッド '{0}' はPascalCaseである必要があります",
        Category,
        DiagnosticSeverity.Warning,
        isEnabledByDefault: true);
    
    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        
        // メソッド宣言の分析
        context.RegisterSyntaxNodeAction(AnalyzeMethod, SyntaxKind.MethodDeclaration);
        
        // フィールド宣言の分析
        context.RegisterSyntaxNodeAction(AnalyzeField, SyntaxKind.FieldDeclaration);
        
        // インターフェース宣言の分析
        context.RegisterSyntaxNodeAction(AnalyzeInterface, SyntaxKind.InterfaceDeclaration);
    }
    
    private void AnalyzeMethod(SyntaxNodeAnalysisContext context)
    {
        var methodDeclaration = (MethodDeclarationSyntax)context.Node;
        var methodSymbol = context.SemanticModel.GetDeclaredSymbol(methodDeclaration);
        
        if (methodSymbol?.DeclaredAccessibility == Accessibility.Public)
        {
            var methodName = methodSymbol.Name;
            
            if (!IsPascalCase(methodName))
            {
                var diagnostic = Diagnostic.Create(
                    PublicMethodRule,
                    methodDeclaration.Identifier.GetLocation(),
                    methodName);
                
                context.ReportDiagnostic(diagnostic);
            }
        }
    }
    
    private bool IsPascalCase(string name)
    {
        return !string.IsNullOrEmpty(name) && 
               char.IsUpper(name[0]) &&
               !name.Contains('_');
    }
}

// コードフィックスプロバイダー
[ExportCodeFixProvider(LanguageNames.CSharp, Name = nameof(NamingConventionCodeFixProvider))]
[Shared]
public class NamingConventionCodeFixProvider : CodeFixProvider
{
    public override ImmutableArray<string> FixableDiagnosticIds =>
        ImmutableArray.Create(NamingConventionAnalyzer.DiagnosticId);
    
    public override async Task RegisterCodeFixesAsync(CodeFixContext context)
    {
        var root = await context.Document.GetSyntaxRootAsync(context.CancellationToken);
        var diagnostic = context.Diagnostics.First();
        var diagnosticSpan = diagnostic.Location.SourceSpan;
        
        // 該当ノードを見つける
        var node = root.FindNode(diagnosticSpan);
        
        if (node is MethodDeclarationSyntax methodDeclaration)
        {
            var newName = ConvertToPascalCase(methodDeclaration.Identifier.Text);
            
            context.RegisterCodeFix(
                CodeAction.Create(
                    title: $"'{methodDeclaration.Identifier.Text}' を '{newName}' に変更",
                    createChangedDocument: c => RenameMethodAsync(
                        context.Document, 
                        methodDeclaration, 
                        newName, 
                        c),
                    equivalenceKey: nameof(NamingConventionCodeFixProvider)),
                diagnostic);
        }
    }
    
    private string ConvertToPascalCase(string name)
    {
        if (string.IsNullOrEmpty(name)) return name;
        
        // camelCase -> PascalCase
        if (char.IsLower(name[0]))
        {
            return char.ToUpper(name[0]) + name.Substring(1);
        }
        
        // snake_case -> PascalCase
        if (name.Contains('_'))
        {
            return string.Join("", name.Split('_')
                .Select(part => char.ToUpper(part[0]) + part.Substring(1).ToLower()));
        }
        
        return name;
    }
}
```

### 2. コードフォーマット標準化

```bash
/standardize format --fix

# 実行結果
コードフォーマット標準化
========================

## フォーマット項目
- インデント: スペース4つに統一
- 中括弧: 新しい行に配置
- using文: アルファベット順にソート
- 空白行: メソッド間に1行
- 行長: 120文字以内

## 修正ファイル数: 156
```

#### フォーマット標準化の実装

```csharp
public class CodeFormatterService
{
    private readonly Workspace _workspace;
    private readonly FormattingOptions _options;
    
    public CodeFormatterService()
    {
        _options = new FormattingOptions
        {
            IndentationSize = 4,
            UseTabs = false,
            NewLineForBraces = NewLineOption.All,
            MaxLineLength = 120,
            SortUsings = true,
            RemoveUnnecessaryUsings = true
        };
    }
    
    public async Task<FormattingResult> FormatSolutionAsync(string solutionPath)
    {
        var solution = await _workspace.OpenSolutionAsync(solutionPath);
        var result = new FormattingResult();
        
        foreach (var project in solution.Projects)
        {
            foreach (var document in project.Documents)
            {
                var formattedDoc = await FormatDocumentAsync(document);
                
                if (formattedDoc.HasChanges)
                {
                    result.ModifiedFiles.Add(document.FilePath);
                    
                    if (!_options.DryRun)
                    {
                        await SaveDocumentAsync(formattedDoc);
                    }
                }
            }
        }
        
        return result;
    }
    
    private async Task<FormattedDocument> FormatDocumentAsync(Document document)
    {
        var root = await document.GetSyntaxRootAsync();
        var formattedRoot = root;
        
        // 1. using文の整理とソート
        formattedRoot = await OrganizeUsingsAsync(document, formattedRoot);
        
        // 2. インデントとスペーシング
        formattedRoot = Formatter.Format(formattedRoot, _workspace, _options);
        
        // 3. 中括弧の位置調整
        formattedRoot = AdjustBracePositions(formattedRoot);
        
        // 4. 長い行の折り返し
        formattedRoot = WrapLongLines(formattedRoot);
        
        // 5. 空白行の調整
        formattedRoot = AdjustBlankLines(formattedRoot);
        
        return new FormattedDocument
        {
            Original = document,
            FormattedRoot = formattedRoot,
            HasChanges = !root.IsEquivalentTo(formattedRoot)
        };
    }
    
    private SyntaxNode AdjustBracePositions(SyntaxNode root)
    {
        var rewriter = new BracePositionRewriter(_options);
        return rewriter.Visit(root);
    }
}

// 中括弧位置の調整
public class BracePositionRewriter : CSharpSyntaxRewriter
{
    private readonly FormattingOptions _options;
    
    public override SyntaxNode VisitMethodDeclaration(MethodDeclarationSyntax node)
    {
        if (node.Body != null && _options.NewLineForBraces == NewLineOption.All)
        {
            var openBrace = node.Body.OpenBraceToken;
            
            // 開き中括弧が同じ行にある場合、新しい行に移動
            if (!HasNewLineBefore(openBrace))
            {
                var newOpenBrace = openBrace
                    .WithLeadingTrivia(
                        SyntaxFactory.CarriageReturnLineFeed,
                        SyntaxFactory.Whitespace(GetIndentation(node)));
                
                var newBody = node.Body.WithOpenBraceToken(newOpenBrace);
                node = node.WithBody(newBody);
            }
        }
        
        return base.VisitMethodDeclaration(node);
    }
}
```

### 3. プロジェクト構造の標準化

```bash
/standardize structure --report

# 実行結果
プロジェクト構造標準化レポート
==============================

## Clean Architecture準拠チェック
✓ Domain層の独立性: OK
⚠ Application層にインフラ参照: 2件
✗ Presentation層からDomain直接参照: 5件

## 推奨される修正
1. CustomerForm.cs -> ICustomerService経由でアクセス
2. OrderForm.cs -> IOrderService経由でアクセス
```

#### プロジェクト構造標準化

```csharp
public class ProjectStructureStandardizer
{
    private readonly SolutionStructureTemplate _template;
    
    public async Task<StructureAnalysisResult> AnalyzeStructureAsync(
        string solutionPath)
    {
        var solution = await MSBuildWorkspace.Create().OpenSolutionAsync(solutionPath);
        var result = new StructureAnalysisResult();
        
        // レイヤー構造の検証
        ValidateLayerArchitecture(solution, result);
        
        // フォルダ構造の検証
        ValidateFolderStructure(solution, result);
        
        // 依存関係の検証
        ValidateDependencies(solution, result);
        
        // 名前空間の一貫性
        ValidateNamespaces(solution, result);
        
        return result;
    }
    
    private void ValidateLayerArchitecture(Solution solution, StructureAnalysisResult result)
    {
        var layers = new[]
        {
            new Layer("Domain", new[] { "Entities", "ValueObjects", "DomainServices", "Interfaces" }),
            new Layer("Application", new[] { "UseCases", "DTOs", "Interfaces", "Services" }),
            new Layer("Infrastructure", new[] { "Data", "ExternalServices", "Configuration" }),
            new Layer("Presentation", new[] { "Forms", "ViewModels", "Controllers" })
        };
        
        foreach (var layer in layers)
        {
            var layerProject = solution.Projects
                .FirstOrDefault(p => p.Name.EndsWith($".{layer.Name}"));
            
            if (layerProject == null)
            {
                result.AddViolation(new StructureViolation
                {
                    Type = ViolationType.MissingLayer,
                    Message = $"{layer.Name}層のプロジェクトが見つかりません",
                    Severity = Severity.Error
                });
                continue;
            }
            
            // 必須フォルダーの確認
            foreach (var requiredFolder in layer.RequiredFolders)
            {
                var folderExists = layerProject.Documents
                    .Any(d => d.Folders.Contains(requiredFolder));
                
                if (!folderExists)
                {
                    result.AddViolation(new StructureViolation
                    {
                        Type = ViolationType.MissingFolder,
                        Message = $"{layer.Name}層に'{requiredFolder}'フォルダが必要です",
                        Severity = Severity.Warning,
                        SuggestedFix = $"mkdir {Path.Combine(layerProject.FilePath, requiredFolder)}"
                    });
                }
            }
        }
    }
    
    public async Task ApplyStructureFixes(
        string solutionPath,
        StructureAnalysisResult analysisResult)
    {
        foreach (var violation in analysisResult.Violations.Where(v => v.CanAutoFix))
        {
            switch (violation.Type)
            {
                case ViolationType.MissingFolder:
                    CreateRequiredFolder(violation);
                    break;
                    
                case ViolationType.WrongNamespace:
                    await FixNamespaceAsync(violation);
                    break;
                    
                case ViolationType.InvalidDependency:
                    await RemoveInvalidDependencyAsync(violation);
                    break;
            }
        }
    }
}
```

### 4. セキュリティ標準の適用

```bash
/standardize security --fix

# 実行結果
セキュリティ標準化
==================

## 検出されたセキュリティ問題
1. SQLインジェクション脆弱性: 3件
2. 平文パスワード保存: 1件
3. 不適切な例外情報露出: 5件
4. 未検証の入力: 8件

## 自動修正
- パラメータ化クエリへの変換: 3件
- 入力検証の追加: 8件
```

#### セキュリティ標準化の実装

```csharp
public class SecurityStandardizer
{
    private readonly SecurityRules _rules;
    
    public async Task<SecurityAnalysisResult> AnalyzeSecurityAsync(Solution solution)
    {
        var result = new SecurityAnalysisResult();
        var analyzers = new ISecurityAnalyzer[]
        {
            new SqlInjectionAnalyzer(),
            new PasswordStorageAnalyzer(),
            new ExceptionExposureAnalyzer(),
            new InputValidationAnalyzer(),
            new CryptographyAnalyzer()
        };
        
        foreach (var project in solution.Projects)
        {
            foreach (var document in project.Documents)
            {
                var root = await document.GetSyntaxRootAsync();
                var semanticModel = await document.GetSemanticModelAsync();
                
                foreach (var analyzer in analyzers)
                {
                    var violations = await analyzer.AnalyzeAsync(root, semanticModel);
                    result.AddViolations(document.FilePath, violations);
                }
            }
        }
        
        return result;
    }
}

// SQLインジェクション検出と修正
public class SqlInjectionAnalyzer : ISecurityAnalyzer
{
    public async Task<IEnumerable<SecurityViolation>> AnalyzeAsync(
        SyntaxNode root, 
        SemanticModel model)
    {
        var violations = new List<SecurityViolation>();
        
        // 文字列連結によるSQL構築を検出
        var sqlConcatenations = root.DescendantNodes()
            .OfType<BinaryExpressionSyntax>()
            .Where(b => b.Kind() == SyntaxKind.AddExpression)
            .Where(b => ContainsSqlKeywords(b) && ContainsUserInput(b, model));
        
        foreach (var concat in sqlConcatenations)
        {
            violations.Add(new SecurityViolation
            {
                Type = SecurityViolationType.SqlInjection,
                Location = concat.GetLocation(),
                Message = "SQLインジェクションの脆弱性: 文字列連結によるSQL構築",
                Severity = Severity.Critical,
                SuggestedFix = GenerateParameterizedQuery(concat, model)
            });
        }
        
        return violations;
    }
    
    private CodeFix GenerateParameterizedQuery(
        BinaryExpressionSyntax concatenation, 
        SemanticModel model)
    {
        // 元のSQL文字列を解析
        var sqlParts = ExtractSqlParts(concatenation);
        var parameters = ExtractParameters(concatenation, model);
        
        // パラメータ化クエリを生成
        var parameterizedSql = BuildParameterizedSql(sqlParts, parameters);
        
        return new CodeFix
        {
            Title = "パラメータ化クエリに変換",
            NewCode = $@"
using (var command = new SqlCommand({parameterizedSql.Query}, connection))
{{
{string.Join("\n", parameterizedSql.Parameters.Select(p => 
    $"    command.Parameters.AddWithValue(\"{p.Name}\", {p.Value});"))}
    
    command.ExecuteNonQuery();
}}"
        };
    }
}

// 入力検証の標準化
public class InputValidationStandardizer
{
    public async Task StandardizeInputValidationAsync(Document document)
    {
        var root = await document.GetSyntaxRootAsync();
        var rewriter = new InputValidationRewriter();
        var newRoot = rewriter.Visit(root);
        
        return document.WithSyntaxRoot(newRoot);
    }
}

public class InputValidationRewriter : CSharpSyntaxRewriter
{
    public override SyntaxNode VisitMethodDeclaration(MethodDeclarationSyntax node)
    {
        // パブリックメソッドのパラメータに検証を追加
        if (node.Modifiers.Any(m => m.Kind() == SyntaxKind.PublicKeyword))
        {
            var parameters = node.ParameterList.Parameters;
            var validationStatements = new List<StatementSyntax>();
            
            foreach (var parameter in parameters)
            {
                var paramName = parameter.Identifier.Text;
                var paramType = parameter.Type;
                
                // 文字列パラメータの検証
                if (IsStringType(paramType))
                {
                    validationStatements.Add(
                        SyntaxFactory.ParseStatement(
                            $@"if (string.IsNullOrWhiteSpace({paramName}))
                                throw new ArgumentException(""'{paramName}' cannot be null or empty"", nameof({paramName}));"));
                }
                
                // オブジェクトパラメータのnullチェック
                else if (IsReferenceType(paramType))
                {
                    validationStatements.Add(
                        SyntaxFactory.ParseStatement(
                            $@"if ({paramName} == null)
                                throw new ArgumentNullException(nameof({paramName}));"));
                }
            }
            
            if (validationStatements.Any() && node.Body != null)
            {
                var newBody = node.Body.WithStatements(
                    node.Body.Statements.InsertRange(0, validationStatements));
                node = node.WithBody(newBody);
            }
        }
        
        return base.VisitMethodDeclaration(node);
    }
}
```

### 5. パフォーマンス標準の適用

```bash
/standardize performance --check

# 実行結果
パフォーマンス標準チェック
==========================

## 検出された問題
1. 同期的I/O: 12件
2. 非効率なLINQ: 8件
3. 大量データの一括読み込み: 3件
4. 文字列連結in ループ: 5件

## 推奨される最適化
- async/await パターンの使用
- AsEnumerable()の削除
- ページング実装
- StringBuilderの使用
```

#### パフォーマンス標準化

```csharp
public class PerformanceStandardizer
{
    public async Task<PerformanceReport> StandardizePerformanceAsync(
        Solution solution)
    {
        var report = new PerformanceReport();
        var optimizers = new IPerformanceOptimizer[]
        {
            new AsyncPatternOptimizer(),
            new LinqOptimizer(),
            new StringOptimizer(),
            new CollectionOptimizer(),
            new DatabaseQueryOptimizer()
        };
        
        foreach (var project in solution.Projects)
        {
            foreach (var document in project.Documents)
            {
                var optimizedDoc = document;
                
                foreach (var optimizer in optimizers)
                {
                    var result = await optimizer.OptimizeAsync(optimizedDoc);
                    if (result.HasChanges)
                    {
                        optimizedDoc = result.OptimizedDocument;
                        report.AddOptimization(document.FilePath, result);
                    }
                }
                
                if (!optimizedDoc.Equals(document))
                {
                    await SaveDocumentAsync(optimizedDoc);
                }
            }
        }
        
        return report;
    }
}

// 非同期パターン最適化
public class AsyncPatternOptimizer : IPerformanceOptimizer
{
    public async Task<OptimizationResult> OptimizeAsync(Document document)
    {
        var root = await document.GetSyntaxRootAsync();
        var rewriter = new AsyncMethodRewriter();
        var newRoot = rewriter.Visit(root);
        
        return new OptimizationResult
        {
            HasChanges = !root.IsEquivalentTo(newRoot),
            OptimizedDocument = document.WithSyntaxRoot(newRoot),
            OptimizationType = "非同期パターン最適化",
            ImprovementEstimate = "レスポンス時間: 30-50%改善"
        };
    }
}

public class AsyncMethodRewriter : CSharpSyntaxRewriter
{
    public override SyntaxNode VisitMethodDeclaration(MethodDeclarationSyntax node)
    {
        // I/O操作を含むメソッドを非同期化
        if (ContainsIoOperations(node) && !IsAsync(node))
        {
            // メソッドシグネチャを非同期に変更
            var asyncNode = node
                .WithModifiers(node.Modifiers.Add(SyntaxFactory.Token(SyntaxKind.AsyncKeyword)))
                .WithReturnType(WrapInTask(node.ReturnType));
            
            // メソッド本体のI/O呼び出しを非同期に変換
            var asyncBody = ConvertToAsyncBody(node.Body);
            asyncNode = asyncNode.WithBody(asyncBody);
            
            return asyncNode;
        }
        
        return base.VisitMethodDeclaration(node);
    }
    
    private bool ContainsIoOperations(MethodDeclarationSyntax method)
    {
        return method.Body?.DescendantNodes()
            .OfType<InvocationExpressionSyntax>()
            .Any(inv => IsIoOperation(inv)) ?? false;
    }
    
    private bool IsIoOperation(InvocationExpressionSyntax invocation)
    {
        var methodName = GetMethodName(invocation);
        var ioMethods = new[]
        {
            "ReadAllText", "WriteAllText", "ReadAllLines",
            "ExecuteReader", "ExecuteScalar", "ExecuteNonQuery",
            "GetResponse", "GetResponseStream"
        };
        
        return ioMethods.Contains(methodName);
    }
}
```

## 標準化設定ファイル

### カスタム規約の定義

```json
{
  "standardization": {
    "naming": {
      "publicMethods": "PascalCase",
      "privateFields": "_camelCase",
      "constants": "PascalCase",
      "interfaces": "I{Name}",
      "asyncMethods": "{Name}Async"
    },
    "formatting": {
      "indentSize": 4,
      "useTabs": false,
      "maxLineLength": 120,
      "braceStyle": "nextLine",
      "spaceAfterKeywords": true
    },
    "structure": {
      "layerSeparation": true,
      "requiredLayers": ["Domain", "Application", "Infrastructure", "Presentation"],
      "folderNamingConvention": "PascalCase"
    },
    "security": {
      "requireInputValidation": true,
      "forbiddenPatterns": ["password.*=.*\"", "exec\\s*\\("],
      "requiredPatterns": ["using.*SqlParameter", "\\[Authorize\\]"]
    },
    "performance": {
      "preferAsync": true,
      "maxMethodLength": 50,
      "maxCyclomaticComplexity": 10
    }
  }
}
```

## 継続的な標準化

### ビルドプロセスへの統合

```xml
<!-- .csproj ファイルに追加 -->
<Project>
  <Target Name="StandardizeCode" BeforeTargets="Build">
    <Exec Command="dotnet tool run standardize all --check" />
  </Target>
  
  <ItemGroup>
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.0.1" />
    <PackageReference Include="StyleCop.Analyzers" Version="1.1.118" PrivateAssets="all" />
  </ItemGroup>
  
  <PropertyGroup>
    <CodeAnalysisRuleSet>$(MSBuildThisFileDirectory)Enterprise.ruleset</CodeAnalysisRuleSet>
  </PropertyGroup>
</Project>
```

### Git フックの設定

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "コード標準化チェックを実行中..."

# 標準化チェック
dotnet tool run standardize all --check

if [ $? -ne 0 ]; then
    echo "コード標準化エラーが検出されました。"
    echo "修正するには以下を実行してください:"
    echo "  dotnet tool run standardize all --fix"
    exit 1
fi

echo "標準化チェック完了"
```

## まとめ

このコマンドにより、エンタープライズプロジェクト全体のコード品質を標準化し、以下を実現します：

1. **一貫性のあるコードベース** - 統一された命名規則とフォーマット
2. **保守性の向上** - 標準化されたプロジェクト構造
3. **セキュリティの強化** - セキュリティベストプラクティスの自動適用
4. **パフォーマンスの最適化** - 標準的な最適化パターンの適用
5. **チーム開発の効率化** - 明確なコーディング標準による協業促進