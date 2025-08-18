# /vb6-migration-enterprise - VB6エンタープライズ移行最適化

## 概要
VB6レガシーシステムの.NET Framework 4.8/.NET 8への段階的移行を支援する包括的コマンドです。**品質保証部主導**で部門協調による安全で効率的な移行を実現します。

## 🎯 部門別責任分担

### 品質保証部（移行責任・品質保証）
- VB6コード解析・アセスメント
- 移行計画策定・リスク評価
- 品質検証・テスト実行
- 移行後検証・性能比較

### システム開発部（技術実装）
- .NET実装・技術移行
- COMインターオペラビリティ
- データベース移行実装
- 新システム開発

### 経営企画部（戦略・計画）
- 移行戦略立案・ROI計算
- リソース計画・スケジュール管理
- アーキテクチャ設計・技術選定
- リスク管理・意思決定

### 人事部（運用・トレーニング）
- ユーザートレーニング・サポート
- 運用手順・マニュアル作成
- 変更管理・組織対応
- ナレッジ移転・技術継承

## 🚀 基本使用法

```bash
# 部門協調による包括的移行（推奨）
/vb6-migration-enterprise comprehensive --project="C:\\Legacy\\System"

# 品質保証部: 解析・評価
/vb6-migration-enterprise analysis --focus="assessment,risk_evaluation"

# システム開発部: 技術移行
/vb6-migration-enterprise implementation --focus="dotnet_migration,com_wrapper"

# 経営企画部: 戦略・計画
/vb6-migration-enterprise strategy --focus="planning,architecture,roi"
```

## 📋 移行フェーズ

### Phase 1: 分析・評価（品質保証部主導）

#### VB6システム解析
```powershell
# VB6プロジェクト包括解析
function Analyze-VB6Project {
    param(
        [string]$ProjectPath,
        [string]$OutputPath = "migration_analysis"
    )
    
    Write-Host "🔍 VB6システム解析開始: $ProjectPath" -ForegroundColor Green
    
    # プロジェクト構造解析
    $projects = Get-ChildItem -Path $ProjectPath -Filter "*.vbp" -Recurse
    $analysis = @{
        ProjectCount = $projects.Count
        Forms = @()
        Modules = @()
        Classes = @()
        Controls = @()
        Dependencies = @()
        ComplexityMetrics = @{}
    }
    
    foreach ($project in $projects) {
        Write-Host "  📁 解析中: $($project.Name)"
        
        # プロジェクトファイル解析
        $projectContent = Get-Content $project.FullName -Encoding Default
        
        # フォーム・モジュール抽出
        $forms = $projectContent | Where-Object { $_ -match "^Form=" } | ForEach-Object { 
            ($_ -split "=")[1].Trim() 
        }
        $modules = $projectContent | Where-Object { $_ -match "^Module=" } | ForEach-Object { 
            ($_ -split "=")[1].Split(";")[1].Trim() 
        }
        $classes = $projectContent | Where-Object { $_ -match "^Class=" } | ForEach-Object { 
            ($_ -split "=")[1].Split(";")[1].Trim() 
        }
        
        # 依存関係抽出
        $references = $projectContent | Where-Object { $_ -match "^Reference=" } | ForEach-Object {
            $ref = ($_ -split "=")[1]
            $guid = ($ref -split "#")[0]
            $version = ($ref -split "#")[1]
            $path = ($ref -split "#")[3]
            
            @{
                GUID = $guid
                Version = $version
                Path = $path
                IsRegistered = Test-ComRegistration -GUID $guid
            }
        }
        
        $analysis.Forms += $forms
        $analysis.Modules += $modules
        $analysis.Classes += $classes
        $analysis.Dependencies += $references
    }
    
    # 複雑度解析
    $analysis.ComplexityMetrics = Measure-VB6Complexity -ProjectPath $ProjectPath
    
    # レポート生成
    $analysis | ConvertTo-Json -Depth 5 | Out-File "$OutputPath\\vb6_analysis_report.json"
    
    return $analysis
}

# COM登録確認
function Test-ComRegistration {
    param([string]$GUID)
    
    try {
        $regPath = "HKLM:\\SOFTWARE\\Classes\\CLSID\\$GUID"
        return Test-Path $regPath
    }
    catch {
        return $false
    }
}

# 複雑度測定
function Measure-VB6Complexity {
    param([string]$ProjectPath)
    
    $sourceFiles = Get-ChildItem -Path $ProjectPath -Include "*.frm", "*.bas", "*.cls" -Recurse
    $metrics = @{
        TotalFiles = $sourceFiles.Count
        TotalLines = 0
        CyclomaticComplexity = 0
        TechnicalDebt = @()
    }
    
    foreach ($file in $sourceFiles) {
        $content = Get-Content $file.FullName -Encoding Default
        $metrics.TotalLines += $content.Count
        
        # 循環的複雑度計算（簡易版）
        $ifCount = ($content | Where-Object { $_ -match "\bIf\b" }).Count
        $loopCount = ($content | Where-Object { $_ -match "\b(For|While|Do)\b" }).Count
        $selectCount = ($content | Where-Object { $_ -match "\bSelect Case\b" }).Count
        
        $fileComplexity = 1 + $ifCount + $loopCount + $selectCount
        $metrics.CyclomaticComplexity += $fileComplexity
        
        # 技術的負債検出
        $debt = @()
        if ($content | Where-Object { $_ -match "GoTo|On Error Resume Next" }) {
            $debt += "Legacy control flow"
        }
        if ($content | Where-Object { $_ -match "Variant" }) {
            $debt += "Weak typing"
        }
        if ($content | Where-Object { $_ -match "CreateObject|GetObject" }) {
            $debt += "Late binding"
        }
        
        if ($debt.Count -gt 0) {
            $metrics.TechnicalDebt += @{
                File = $file.Name
                Issues = $debt
            }
        }
    }
    
    return $metrics
}
```

#### 移行評価アセスメント
```csharp
// Migration Assessment Engine
public class VB6MigrationAssessment
{
    public class MigrationReport
    {
        public double AutoMigrationPercentage { get; set; }
        public List<string> HighRiskComponents { get; set; }
        public List<string> RequiredManualWork { get; set; }
        public TimeSpan EstimatedDuration { get; set; }
        public decimal EstimatedCost { get; set; }
        public List<TechnicalRisk> Risks { get; set; }
    }
    
    public MigrationReport AssessMigrationFeasibility(string vb6ProjectPath)
    {
        var analysis = AnalyzeVB6Project(vb6ProjectPath);
        var report = new MigrationReport
        {
            HighRiskComponents = new List<string>(),
            RequiredManualWork = new List<string>(),
            Risks = new List<TechnicalRisk>()
        };
        
        // 自動移行率計算
        var autoMigratable = 0;
        var totalComponents = analysis.Components.Count;
        
        foreach (var component in analysis.Components)
        {
            var score = CalculateMigrationScore(component);
            if (score > 0.8) autoMigratable++;
            else if (score < 0.5) 
            {
                report.HighRiskComponents.Add(component.Name);
                report.RequiredManualWork.Add($"{component.Name}: {component.Issues}");
            }
        }
        
        report.AutoMigrationPercentage = (double)autoMigratable / totalComponents * 100;
        
        // リスク評価
        report.Risks.AddRange(AssessApiUsageRisks(analysis.ApiCalls));
        report.Risks.AddRange(AssessComDependencyRisks(analysis.ComReferences));
        report.Risks.AddRange(AssessDatabaseAccessRisks(analysis.DatabaseConnections));
        
        // 工数・コスト見積もり
        report.EstimatedDuration = EstimateMigrationDuration(analysis);
        report.EstimatedCost = EstimateMigrationCost(analysis);
        
        return report;
    }
    
    private double CalculateMigrationScore(ComponentAnalysis component)
    {
        var score = 1.0;
        
        // ペナルティ要因
        if (component.HasApiCalls) score -= 0.3;
        if (component.HasComInterop) score -= 0.4;
        if (component.HasComplexDataAccess) score -= 0.2;
        if (component.HasThirdPartyControls) score -= 0.5;
        if (component.CyclomaticComplexity > 10) score -= 0.2;
        
        return Math.Max(0, score);
    }
    
    private List<TechnicalRisk> AssessApiUsageRisks(List<ApiCall> apiCalls)
    {
        var risks = new List<TechnicalRisk>();
        var deprecatedApis = new[]
        {
            "GetWindowsDirectory", "GetSystemDirectory", "GetTempPath"
        };
        
        foreach (var api in apiCalls)
        {
            if (deprecatedApis.Contains(api.FunctionName))
            {
                risks.Add(new TechnicalRisk
                {
                    Level = RiskLevel.High,
                    Component = api.SourceFile,
                    Description = $"Deprecated API: {api.FunctionName}",
                    Mitigation = $"Replace with .NET equivalent: {GetDotNetEquivalent(api.FunctionName)}"
                });
            }
        }
        
        return risks;
    }
}
```

### Phase 2: 段階的移行実装（システム開発部主導）

#### データアクセス層移行
```csharp
// VB6 → .NET Data Access Migration
public class DataAccessMigration
{
    public void MigrateAdoToEntityFramework(string connectionString, string outputPath)
    {
        // VB6 ADO接続文字列解析
        var adoConnection = ParseAdoConnectionString(connectionString);
        
        // Entity Framework接続文字列生成
        var efConnectionString = ConvertToEntityFrameworkConnection(adoConnection);
        
        // DbContextクラス生成
        GenerateDbContext(adoConnection.DatabaseSchema, outputPath);
        
        // Repository パターン実装
        GenerateRepositoryClasses(adoConnection.Tables, outputPath);
    }
    
    private void GenerateDbContext(DatabaseSchema schema, string outputPath)
    {
        var code = $@"
using Microsoft.EntityFrameworkCore;
using System;
using System.ComponentModel.DataAnnotations;

namespace {schema.Namespace}
{{
    public class {schema.Name}Context : DbContext
    {{
        public {schema.Name}Context(DbContextOptions<{schema.Name}Context> options)
            : base(options) {{ }}
        
        {string.Join(Environment.NewLine + "        ", 
            schema.Tables.Select(t => $"public DbSet<{t.Name}> {t.Name} {{ get; set; }}"))}
        
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {{
            {string.Join(Environment.NewLine + "            ", 
                GenerateEntityConfigurations(schema.Tables))}
        }}
    }}
}}";
        
        File.WriteAllText(Path.Combine(outputPath, $"{schema.Name}Context.cs"), code);
    }
    
    private void GenerateRepositoryClasses(List<Table> tables, string outputPath)
    {
        foreach (var table in tables)
        {
            var repositoryCode = $@"
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace {table.Namespace}
{{
    public interface I{table.Name}Repository
    {{
        Task<IEnumerable<{table.Name}>> GetAllAsync();
        Task<{table.Name}> GetByIdAsync({table.PrimaryKey.Type} id);
        Task<{table.Name}> CreateAsync({table.Name} entity);
        Task<{table.Name}> UpdateAsync({table.Name} entity);
        Task DeleteAsync({table.PrimaryKey.Type} id);
    }}
    
    public class {table.Name}Repository : I{table.Name}Repository
    {{
        private readonly {table.Schema.Name}Context _context;
        
        public {table.Name}Repository({table.Schema.Name}Context context)
        {{
            _context = context;
        }}
        
        public async Task<IEnumerable<{table.Name}>> GetAllAsync()
        {{
            return await _context.{table.Name}
                {(table.HasSoftDelete ? ".Where(x => !x.IsDeleted)" : "")}
                .ToListAsync();
        }}
        
        public async Task<{table.Name}> GetByIdAsync({table.PrimaryKey.Type} id)
        {{
            return await _context.{table.Name}
                {(table.HasSoftDelete ? ".Where(x => !x.IsDeleted)" : "")}
                .FirstOrDefaultAsync(x => x.{table.PrimaryKey.Name} == id);
        }}
        
        public async Task<{table.Name}> CreateAsync({table.Name} entity)
        {{
            _context.{table.Name}.Add(entity);
            await _context.SaveChangesAsync();
            return entity;
        }}
        
        public async Task<{table.Name}> UpdateAsync({table.Name} entity)
        {{
            _context.Entry(entity).State = EntityState.Modified;
            await _context.SaveChangesAsync();
            return entity;
        }}
        
        public async Task DeleteAsync({table.PrimaryKey.Type} id)
        {{
            var entity = await GetByIdAsync(id);
            if (entity != null)
            {{
                {(table.HasSoftDelete ? 
                    "entity.IsDeleted = true; entity.DeletedAt = DateTime.UtcNow;" :
                    "_context.{table.Name}.Remove(entity);")}
                await _context.SaveChangesAsync();
            }}
        }}
    }}
}}";
            
            File.WriteAllText(
                Path.Combine(outputPath, $"{table.Name}Repository.cs"), 
                repositoryCode
            );
        }
    }
}
```

#### COM相互運用ラッパー
```csharp
// COM Interop Wrapper Generator
public class ComInteropWrapper
{
    public void GenerateComWrapper(string vb6ComDll, string outputPath)
    {
        // VB6 COM DLL解析
        var comInfo = AnalyzeComComponent(vb6ComDll);
        
        // .NET Interop アセンブリ生成
        GenerateInteropAssembly(comInfo, outputPath);
        
        // マネージドラッパークラス生成
        GenerateManagedWrapper(comInfo, outputPath);
    }
    
    private void GenerateManagedWrapper(ComComponentInfo comInfo, string outputPath)
    {
        var wrapperCode = $@"
using System;
using System.Runtime.InteropServices;
using System.Runtime.CompilerServices;

namespace {comInfo.Namespace}.Interop
{{
    /// <summary>
    /// Managed wrapper for VB6 COM component: {comInfo.ComponentName}
    /// </summary>
    public class {comInfo.ComponentName}Wrapper : IDisposable
    {{
        private {comInfo.InterfaceName} _comObject;
        private bool _disposed = false;
        
        public {comInfo.ComponentName}Wrapper()
        {{
            try
            {{
                _comObject = new {comInfo.ClassName}();
            }}
            catch (COMException ex)
            {{
                throw new InvalidOperationException(
                    $""Failed to create COM object {comInfo.ComponentName}: {{ex.Message}}"", ex);
            }}
        }}
        
        {string.Join(Environment.NewLine + "        ", 
            GenerateMethodWrappers(comInfo.Methods))}
        
        public void Dispose()
        {{
            Dispose(true);
            GC.SuppressFinalize(this);
        }}
        
        protected virtual void Dispose(bool disposing)
        {{
            if (!_disposed)
            {{
                if (disposing && _comObject != null)
                {{
                    Marshal.ReleaseComObject(_comObject);
                    _comObject = null;
                }}
                _disposed = true;
            }}
        }}
        
        ~{comInfo.ComponentName}Wrapper()
        {{
            Dispose(false);
        }}
    }}
}}";
        
        File.WriteAllText(
            Path.Combine(outputPath, $"{comInfo.ComponentName}Wrapper.cs"),
            wrapperCode
        );
    }
    
    private List<string> GenerateMethodWrappers(List<ComMethod> methods)
    {
        var wrappers = new List<string>();
        
        foreach (var method in methods)
        {
            var paramList = string.Join(", ", 
                method.Parameters.Select(p => $"{p.Type} {p.Name}"));
            
            var wrapper = $@"
        /// <summary>
        /// Wrapper for COM method: {method.Name}
        /// </summary>
        public {method.ReturnType} {method.Name}({paramList})
        {{
            try
            {{
                {(method.ReturnType != "void" ? "return " : "")}_comObject.{method.Name}({string.Join(", ", method.Parameters.Select(p => p.Name))});
            }}
            catch (COMException ex)
            {{
                throw new InvalidOperationException(
                    $""COM method {method.Name} failed: {{ex.Message}}"", ex);
            }}
        }}";
            
            wrappers.Add(wrapper);
        }
        
        return wrappers;
    }
}
```

### Phase 3: UI移行（システム開発部・人事部協調）

#### WinForms移行支援
```csharp
// VB6 Form → WinForms Migration
public class FormMigrationEngine
{
    public void MigrateVB6Form(string vb6FormPath, string outputPath)
    {
        // VB6フォーム解析
        var formInfo = ParseVB6Form(vb6FormPath);
        
        // WinForms設計
        GenerateWinForm(formInfo, outputPath);
        
        // イベントハンドラー移行
        GenerateEventHandlers(formInfo.Events, outputPath);
    }
    
    private void GenerateWinForm(VB6FormInfo formInfo, string outputPath)
    {
        var designerCode = $@"
partial class {formInfo.Name}
{{
    private System.ComponentModel.IContainer components = null;
    {string.Join(Environment.NewLine + "    ", 
        formInfo.Controls.Select(c => $"private {MapControlType(c.Type)} {c.Name};"))}
    
    protected override void Dispose(bool disposing)
    {{
        if (disposing && (components != null))
        {{
            components.Dispose();
        }}
        base.Dispose(disposing);
    }}
    
    private void InitializeComponent()
    {{
        this.SuspendLayout();
        
        {string.Join(Environment.NewLine + "        ", 
            GenerateControlInitialization(formInfo.Controls))}
        
        // Form properties
        this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
        this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
        this.ClientSize = new System.Drawing.Size({formInfo.Width}, {formInfo.Height});
        this.Name = ""{formInfo.Name}"";
        this.Text = ""{formInfo.Caption}"";
        
        this.ResumeLayout(false);
        this.PerformLayout();
    }}
}}";
        
        File.WriteAllText(
            Path.Combine(outputPath, $"{formInfo.Name}.Designer.cs"),
            designerCode
        );
    }
}
```

## 📊 移行メトリクス

### 品質指標
- **移行精度**: 95%以上
- **機能カバレッジ**: 100%
- **パフォーマンス**: VB6比120%以上
- **安定性**: 障害率1%以下

### 効率指標
- **自動移行率**: 70%以上
- **手動作業削減**: 60%以上
- **テスト工数削減**: 50%以上
- **総移行期間短縮**: 40%以上

## 🔧 移行手順

### Phase 1: 準備・分析（品質保証部主導）
```bash
# VB6システム解析
/vb6-migration-enterprise analysis --scope="code,dependencies,complexity"

# 移行評価
/vb6-migration-enterprise assessment --detailed-report --cost-estimate
```

### Phase 2: 段階移行（システム開発部主導）
```bash
# データアクセス層移行
/vb6-migration-enterprise migrate --phase="data_access" --target="net48"

# ビジネスロジック移行
/vb6-migration-enterprise migrate --phase="business_logic" --preserve-com

# UI層移行
/vb6-migration-enterprise migrate --phase="ui" --target="winforms"
```

### Phase 3: 検証・運用（品質保証部・人事部協調）
```bash
# 機能検証
/vb6-migration-enterprise validate --scope="functional,performance"

# 並行運用テスト
/vb6-migration-enterprise parallel-test --duration="30days"

# 運用移行
/vb6-migration-enterprise cutover --rollback-plan
```

## 🎯 継続サポート

### 移行後サポート
- 性能監視・最適化提案
- 障害対応・トラブルシューティング
- 追加機能開発サポート

### 技術継承
- .NET技術トレーニング
- ベストプラクティス共有
- 保守マニュアル作成

---

**🎯 目標**: VB6レガシーシステムを最新.NETへ安全・効率的に移行し、エンタープライズレベルの品質とパフォーマンスを実現する。