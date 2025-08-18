# /version-migration-guide - .NETバージョン別移行ガイド

## 概要
.NET Framework 4.0から.NET 8まで、すべてのバージョンに対応した包括的な移行ガイドです。各バージョンの特徴、アップグレードパス、移行戦略、互換性問題の解決方法を提供します。

## バージョン全体マップ

```
.NET Framework (Windows Only)
├── 4.0 (2010) → 4.5 (2012) → 4.6.1 (2015) → 4.7.2 (2018) → 4.8 (2019)
│
.NET Core (Cross-Platform) 
├── 1.0 (2016) → 2.0 (2017) → 2.1 LTS (2018) → 3.1 LTS (2019)
│
.NET (Unified Platform)
└── 5.0 (2020) → 6.0 LTS (2021) → 7.0 (2022) → 8.0 LTS (2023) → 9.0 (2024)
```

## 詳細バージョン分析

### .NET Framework 4.0 → 4.8

#### .NET Framework 4.0 (2010年4月)
```csharp
// 特徴: 初期のモダン.NET
- CLR Version: 4.0
- C# Version: 4.0
- 主要機能: Dynamic, Task Parallel Library, Code Contracts
- サポート状況: ❌ 終了 (2016年1月)

// 典型的なコード
public class LegacyService
{
    public void ProcessData()
    {
        // TPL基本形
        Task.Factory.StartNew(() =>
        {
            // 処理
        });
        
        // Dynamic型
        dynamic obj = GetDynamicObject();
        obj.PropertyName = "値";
    }
}

// 移行時の問題点
- async/await未対応
- NuGet初期版のみ
- LINQ制限あり
- Entity Framework 4.1が最新
```

#### .NET Framework 4.5 (2012年8月)
```csharp
// 特徴: async/await導入
- CLR Version: 4.0 (インプレース更新)
- C# Version: 5.0
- 主要機能: async/await, .NET for Windows Store apps
- サポート状況: ❌ 終了 (2016年1月)

// async/await パターン
public async Task<Customer> GetCustomerAsync(int id)
{
    using (var client = new HttpClient())
    {
        var response = await client.GetAsync($"api/customers/{id}");
        var json = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<Customer>(json);
    }
}

// 移行時の考慮事項
- 4.0からのインプレース更新
- 既存コードの互換性維持
- async/awaitへの段階的移行
```

#### .NET Framework 4.6.1 (2015年11月)
```csharp
// 特徴: .NET Standardサポート開始
- CLR Version: 4.0
- C# Version: 6.0
- 主要機能: .NET Standard 1.0-1.3, WCF改善
- サポート状況: ⚠️ 延長サポート (2027年1月まで)

// C# 6.0機能
public class ModernCustomer
{
    public string Name { get; set; } = string.Empty; // Auto-property initializer
    public DateTime Created { get; } = DateTime.Now; // Get-only property
    
    public string GetDisplayName() => $"{Name} ({Created:yyyy-MM-dd})"; // Expression body
    
    public void ProcessCustomer()
    {
        var result = Name?.ToUpper() ?? "Unknown"; // Null conditional
        Console.WriteLine($"Processing: {result}"); // String interpolation
    }
}
```

#### .NET Framework 4.7.2 (2018年4月)
```csharp
// 特徴: .NET Standard 2.0完全対応
- CLR Version: 4.0
- C# Version: 7.3
- 主要機能: .NET Standard 2.0, TLS 1.2デフォルト
- サポート状況: ✅ サポート中 (2029年1月まで)

// .NET Standard 2.0ライブラリが使用可能
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

public class StandardCompatibleService
{
    private readonly ILogger<StandardCompatibleService> _logger;
    
    public StandardCompatibleService(ILogger<StandardCompatibleService> logger)
    {
        _logger = logger;
    }
    
    // C# 7.3機能
    public void ProcessData<T>(in T data) where T : unmanaged
    {
        // in parameter, unmanaged constraint
        _logger.LogInformation($"Processing {typeof(T).Name}");
    }
}
```

#### .NET Framework 4.8 (2019年4月)
```csharp
// 特徴: .NET Framework最終版
- CLR Version: 4.0
- C# Version: 7.3
- 主要機能: High DPI改善, JIT最適化, 暗号化改善
- サポート状況: ✅ サポート中 (2029年1月まで)

// 新機能活用例
public class Framework48Features
{
    // 暗号化改善
    public string EncryptData(string data)
    {
        using (var aes = Aes.Create())
        {
            aes.Mode = CipherMode.GCM; // .NET 4.8で追加
            // 暗号化処理
            return Convert.ToBase64String(aes.Key);
        }
    }
    
    // JIT最適化（自動適用）
    public int OptimizedCalculation(int[] numbers)
    {
        return numbers.Sum(); // JITによる自動SIMD最適化
    }
}
```

### .NET Core系列

#### .NET Core 2.1 LTS (2018年5月)
```csharp
// 特徴: 初のLTS、性能大幅改善
- Runtime: .NET Core 2.1
- C# Version: 7.3
- サポート状況: ❌ 終了 (2021年8月)

// Span<T>とMemory<T>
public class PerformanceOptimized
{
    public void ProcessBuffer(ReadOnlySpan<byte> buffer)
    {
        // Zero-allocation processing
        foreach (var chunk in buffer.Slice(0, Math.Min(buffer.Length, 1024)))
        {
            // 処理
        }
    }
    
    // HTTP/2サポート
    public async Task<string> CallApiAsync()
    {
        using var client = new HttpClient();
        client.DefaultRequestVersion = new Version(2, 0);
        return await client.GetStringAsync("https://api.example.com");
    }
}
```

#### .NET Core 3.1 LTS (2019年12月)
```csharp
// 特徴: .NET Core最終版、デスクトップアプリ対応
- Runtime: .NET Core 3.1
- C# Version: 8.0
- サポート状況: ❌ 終了 (2022年12月)

// C# 8.0機能
public class CoreThreeFeatures
{
    // Nullable reference types
    public Customer? FindCustomer(string? name)
    {
        if (name is null) return null;
        
        // Pattern matching
        return name switch
        {
            { Length: > 10 } => new Customer { Name = name },
            _ => null
        };
    }
    
    // Async streams
    public async IAsyncEnumerable<Customer> GetCustomersAsync(
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        await foreach (var customer in LoadCustomersAsync().WithCancellation(cancellationToken))
        {
            yield return customer;
        }
    }
    
    // Default interface implementation
    public interface ILoggable
    {
        void WriteLog(string message) => Console.WriteLine($"[{DateTime.Now}] {message}");
    }
}
```

### .NET 5+ (統合プラットフォーム)

#### .NET 5.0 (2020年11月)
```csharp
// 特徴: 統合プラットフォーム第1弾
- Runtime: .NET 5.0
- C# Version: 9.0
- サポート状況: ❌ 終了 (2022年5月)

// C# 9.0機能
public record Customer(int Id, string Name, string Email)
{
    // Record with positional parameters
    public bool IsValid => !string.IsNullOrEmpty(Name) && Email.Contains('@');
}

public class Net5Features
{
    // Top-level statements (Program.cs)
    // using System;
    // Console.WriteLine("Hello .NET 5!");
    
    // Pattern matching improvements
    public decimal CalculateDiscount(object input) => input switch
    {
        Customer { Name: var name } when name.StartsWith("VIP") => 0.20m,
        Customer customer => customer.IsValid ? 0.10m : 0m,
        int quantity when quantity > 100 => 0.15m,
        _ => 0m
    };
    
    // Target-typed new
    Customer customer = new(1, "John", "john@example.com");
}
```

#### .NET 6.0 LTS (2021年11月)
```csharp
// 特徴: 統合完了、Minimal API
- Runtime: .NET 6.0
- C# Version: 10.0
- サポート状況: ✅ LTS (2024年11月まで)

// Minimal API
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/customers/{id:int}", async (int id, ICustomerService service) =>
{
    var customer = await service.GetCustomerAsync(id);
    return customer is not null ? Results.Ok(customer) : Results.NotFound();
});

// Global using statements
global using System;
global using System.Collections.Generic;
global using System.Linq;
global using Microsoft.Extensions.DependencyInjection;

// File-scoped namespace
namespace MyApp.Services;

public class CustomerService
{
    // Constant interpolated strings
    private const string ApiUrl = $"https://api.example.com/v1";
    
    // Record struct
    public readonly record struct CustomerInfo(int Id, string Name);
    
    // CallerArgumentExpression
    public void ValidateCustomer(Customer customer, [CallerArgumentExpression("customer")] string? paramName = null)
    {
        ArgumentNullException.ThrowIfNull(customer, paramName);
    }
}
```

#### .NET 7.0 (2022年11月)
```csharp
// 特徴: パフォーマンス向上、Generic Math
- Runtime: .NET 7.0
- C# Version: 11.0
- サポート状況: ❌ 終了 (2024年5月)

// Generic Math
public static T Add<T>(T left, T right) where T : INumber<T>
{
    return left + right;
}

// Raw string literals
public const string SqlQuery = """
    SELECT c.Id, c.Name, c.Email,
           COUNT(o.Id) as OrderCount
    FROM Customers c
    LEFT JOIN Orders o ON c.Id = o.CustomerId
    GROUP BY c.Id, c.Name, c.Email
    ORDER BY OrderCount DESC
    """;

// Required members
public class CustomerDto
{
    public required int Id { get; init; }
    public required string Name { get; init; }
    public string? Email { get; init; }
    
    [SetsRequiredMembers]
    public CustomerDto(int id, string name)
    {
        Id = id;
        Name = name;
    }
}

// List patterns
public string ProcessItems(int[] items) => items switch
{
    [] => "Empty",
    [var single] => $"Single: {single}",
    [var first, .., var last] => $"Multiple: {first} to {last}",
    _ => "Unknown"
};
```

#### .NET 8.0 LTS (2023年11月)
```csharp
// 特徴: 最新LTS、Native AOT、Blazor United
- Runtime: .NET 8.0
- C# Version: 12.0
- サポート状況: ✅ LTS (2026年11月まで)

// Primary constructors
public class CustomerService(ILogger<CustomerService> logger, ICustomerRepository repository)
{
    public async Task<Customer> GetCustomerAsync(int id)
    {
        logger.LogInformation("Getting customer {Id}", id);
        return await repository.GetByIdAsync(id);
    }
}

// Collection expressions
private readonly List<string> _names = ["Alice", "Bob", "Charlie"];
private readonly Dictionary<string, int> _scores = [];

// Alias any type
using CustomerList = List<Customer>;
using UserId = int;

public Customer? FindCustomer(UserId id, CustomerList customers)
{
    return customers.FirstOrDefault(c => c.Id == id);
}

// Default lambda parameters
var multiply = (int x, int y = 1) => x * y;

// Native AOT ready code
[DynamicallyAccessedMembers(DynamicallyAccessedMemberTypes.All)]
public class AotCompatibleService
{
    public void ProcessData<T>() where T : new()
    {
        var instance = new T(); // AOT compatible
        // 処理
    }
}
```

## 移行戦略ガイド

### 1. .NET Framework → .NET 6+ 移行

#### フェーズ1: 評価と準備
```powershell
# .NET移行可能性評価ツール
dotnet tool install -g try-convert
try-convert --project MyProject.csproj --keep-current-tfms

# APIの互換性チェック
dotnet tool install -g Microsoft.DotNet.ApiPort
ApiPort.exe analyze -f MyApplication.exe -r html
```

#### フェーズ2: 段階的移行
```xml
<!-- Multi-targeting approach -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFrameworks>net48;net6.0</TargetFrameworks>
  </PropertyGroup>
  
  <!-- Conditional compilation -->
  <ItemGroup Condition="'$(TargetFramework)' == 'net48'">
    <PackageReference Include="System.Text.Json" Version="6.0.0" />
  </ItemGroup>
  
  <ItemGroup Condition="'$(TargetFramework)' == 'net6.0'">
    <FrameworkReference Include="Microsoft.AspNetCore.App" />
  </ItemGroup>
</Project>
```

#### フェーズ3: 互換性対応
```csharp
// 条件付きコンパイル
public class CompatibilityLayer
{
#if NET48
    public void ConfigureServices(ContainerBuilder builder)
    {
        // Autofac for .NET Framework
        builder.RegisterType<ServiceImplementation>().As<IService>();
    }
#else
    public void ConfigureServices(IServiceCollection services)
    {
        // Built-in DI for .NET 6+
        services.AddScoped<IService, ServiceImplementation>();
    }
#endif

    // 共通コード
    public Task<Customer> GetCustomerAsync(int id)
    {
        // 両方のフレームワークで動作するコード
        return Task.FromResult(new Customer { Id = id });
    }
}
```

### 2. 大規模システム移行戦略

#### ストラングラーフィグパターン
```csharp
// Legacy system proxy
public class LegacySystemProxy : ICustomerService
{
    private readonly LegacyCustomerService _legacyService;
    private readonly ModernCustomerService _modernService;
    private readonly IFeatureToggle _featureToggle;
    
    public async Task<Customer> GetCustomerAsync(int id)
    {
        if (await _featureToggle.IsEnabledAsync("UseModernCustomerService", id))
        {
            return await _modernService.GetCustomerAsync(id);
        }
        else
        {
            return await _legacyService.GetCustomerAsync(id);
        }
    }
}
```

#### データベース移行
```sql
-- 段階的移行のためのビュー作成
CREATE VIEW dbo.CustomerView AS
SELECT 
    Id,
    Name,
    Email,
    CreatedDate,
    'Legacy' as Source
FROM dbo.LegacyCustomers
WHERE MigratedDate IS NULL

UNION ALL

SELECT 
    Id,
    Name,
    Email,
    CreatedDate,
    'Modern' as Source
FROM dbo.ModernCustomers;
```

## バージョン別推奨移行パス

### 短期（6ヶ月以内）
```
.NET Framework 4.8 → .NET 6.0 LTS
└── 理由: 安定性とLTSサポート

.NET Framework 4.7.2以下 → .NET 6.0 LTS
└── 理由: セキュリティとパフォーマンス

.NET Core 3.1 → .NET 6.0 LTS
└── 理由: LTS継続
```

### 中期（1年以内）
```
.NET 6.0 LTS → .NET 8.0 LTS
└── 理由: 最新LTS機能活用

レガシーアプリ → .NET 8.0 LTS
└── 理由: モダン化とAOT対応
```

### 長期（2年以内）
```
全システム → .NET 8.0 LTS
└── 理由: 統一プラットフォーム

クラウドネイティブ移行
└── .NET 8.0 + Kubernetes + Azure
```

## 移行チェックリスト

### 技術的考慮事項
- [ ] API互換性確認（ApiPort）
- [ ] NuGetパッケージ互換性
- [ ] サードパーティライブラリ対応
- [ ] データベース接続文字列
- [ ] 設定ファイル形式変更
- [ ] ログフレームワーク移行
- [ ] 認証・認可の変更
- [ ] デプロイメント手順見直し

### パフォーマンステスト
- [ ] 起動時間測定
- [ ] メモリ使用量比較
- [ ] スループット測定
- [ ] レスポンス時間測定
- [ ] 負荷テスト実行

### セキュリティ確認
- [ ] TLS 1.2以上対応
- [ ] 暗号化アルゴリズム更新
- [ ] 認証フレームワーク更新
- [ ] セキュリティヘッダー設定
- [ ] 脆弱性スキャン実行

## 出力レポート
```markdown
# .NETバージョン移行レポート

## 現状分析
- 現在のバージョン: .NET Framework 4.7.2
- 対象アプリケーション数: 15個
- 総コード行数: 500,000行
- 外部依存関係: 45個

## 移行計画
- 移行先バージョン: .NET 8.0 LTS
- 予想期間: 8ヶ月
- リスクレベル: 中
- 投資対効果: 高

## 期待効果
- パフォーマンス: 40%向上
- メモリ使用量: 30%削減
- セキュリティ: 大幅改善
- 保守性: 50%向上
- ランニングコスト: 25%削減

## リスクと対策
1. 互換性問題 → 段階的移行
2. パフォーマンス劣化 → 綿密なテスト
3. スキル不足 → 研修計画
4. ダウンタイム → ブルーグリーン展開
```

## 管理責任
- **管理部門**: システム開発部・経営企画部
- **専門性**: .NETプラットフォーム移行戦略

---
*このガイドは.NETの全バージョンに対応した移行戦略の立案に特化しています。*