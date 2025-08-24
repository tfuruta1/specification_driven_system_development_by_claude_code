# /dotnet6-modern - .NET 6+ 

## 
.NET 6Minimal APIHot ReloadGlobal UsingSource GeneratorsNative AOT

## 
```bash
/dotnet6-modern [feature] [action] [options]

# 
/dotnet6-modern minimal-api create --with-swagger --auth-jwt
/dotnet6-modern performance optimize --native-aot --r2r
/dotnet6-modern source-generator create --incremental
/dotnet6-modern hot-reload enable --docker-support
/dotnet6-modern grpc implement --streaming --interceptors
```

## .NET 6+ 

### 1. Minimal API SYSTEMWebSYSTEM
```csharp
// Program.cs - Minimal API with full features
using Microsoft.AspNetCore.RateLimiting;
using System.Threading.RateLimiting;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new() 
    { 
        Title = "Enterprise API",
        Version = "v1",
        Description = "High-performance minimal API with .NET 6+"
    });
    
    // JWT Bearer
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        In = ParameterLocation.Header,
        Description = "Please enter JWT token",
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        BearerFormat = "JWT",
        Scheme = "bearer"
    });
});

// Authentication & Authorization
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]))
        };
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
    options.AddPolicy("MinimumAge", policy => 
        policy.Requirements.Add(new MinimumAgeRequirement(18)));
});

// Rate limiting
builder.Services.AddRateLimiter(options =>
{
    options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(
        httpContext => RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: httpContext.User?.Identity?.Name ?? httpContext.Request.Headers.Host.ToString(),
            factory: partition => new FixedWindowRateLimiterOptions
            {
                AutoReplenishment = true,
                PermitLimit = 100,
                QueueLimit = 50,
                Window = TimeSpan.FromMinutes(1)
            }));
    
    options.AddPolicy("api", httpContext =>
        RateLimitPartition.GetSlidingWindowLimiter(
            partitionKey: httpContext.Connection.RemoteIpAddress?.ToString(),
            factory: partition => new SlidingWindowRateLimiterOptions
            {
                AutoReplenishment = true,
                PermitLimit = 100,
                QueueLimit = 50,
                Window = TimeSpan.FromMinutes(1),
                SegmentsPerWindow = 6
            }));
});

// CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowSpecificOrigin",
        policy => policy
            .WithOrigins("https://localhost:3000")
            .AllowAnyHeader()
            .AllowAnyMethod()
            .AllowCredentials());
});

// Response compression
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
});

// Memory cache
builder.Services.AddMemoryCache();
builder.Services.AddDistributedMemoryCache();

// Health checks
builder.Services.AddHealthChecks()
    .AddCheck("self", () => HealthCheckResult.Healthy())
    .AddDbContextCheck<ApplicationDbContext>()
    .AddRedis(builder.Configuration.GetConnectionString("Redis"))
    .AddUrlGroup(new Uri("https://api.external.com/health"), "external-api");

// Application Insights
builder.Services.AddApplicationInsightsTelemetry();

// Custom services
builder.Services.AddScoped<ICustomerService, CustomerService>();
builder.Services.AddSingleton<ICacheService, RedisCacheService>();
builder.Services.AddHostedService<BackgroundTaskService>();

var app = builder.Build();

// Middleware pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseResponseCompression();
app.UseCors("AllowSpecificOrigin");
app.UseAuthentication();
app.UseAuthorization();
app.UseRateLimiter();

// Health check endpoints
app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = _ => true,
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false
});

// API Endpoints with versioning
var v1 = app.MapGroup("/api/v1")
    .RequireRateLimiting("api")
    .WithOpenApi();

// Customer endpoints
v1.MapGet("/customers", async (
    ICustomerService service,
    [AsParameters] PaginationRequest pagination,
    ILogger<Program> logger) =>
{
    logger.LogInformation("Getting customers with pagination: {@Pagination}", pagination);
    var result = await service.GetCustomersAsync(pagination);
    return Results.Ok(result);
})
.WithName("GetCustomers")
.WithSummary("Get all customers")
.WithDescription("Returns paginated list of customers")
.Produces<PaginatedResult<Customer>>(StatusCodes.Status200OK)
.ProducesProblem(StatusCodes.Status500InternalServerError);

v1.MapGet("/customers/{id:guid}", async Task<Results<Ok<Customer>, NotFound, ProblemHttpResult>> (
    Guid id,
    ICustomerService service,
    ILogger<Program> logger) =>
{
    try
    {
        var customer = await service.GetCustomerByIdAsync(id);
        return customer is null 
            ? TypedResults.NotFound() 
            : TypedResults.Ok(customer);
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "Error getting customer {Id}", id);
        return TypedResults.Problem("An error occurred while processing your request");
    }
})
.WithName("GetCustomerById")
.RequireAuthorization();

v1.MapPost("/customers", async (
    [FromBody] CreateCustomerRequest request,
    ICustomerService service,
    IValidator<CreateCustomerRequest> validator) =>
{
    var validationResult = await validator.ValidateAsync(request);
    if (!validationResult.IsValid)
    {
        return Results.ValidationProblem(validationResult.ToDictionary());
    }
    
    var customer = await service.CreateCustomerAsync(request);
    return Results.CreatedAtRoute("GetCustomerById", new { id = customer.Id }, customer);
})
.WithName("CreateCustomer")
.RequireAuthorization("AdminOnly")
.AddEndpointFilter<ValidationFilter<CreateCustomerRequest>>()
.AddEndpointFilter<AuditFilter>();

// Streaming endpoint
v1.MapGet("/stream", async (HttpContext context) =>
{
    context.Response.ContentType = "text/event-stream";
    
    for (int i = 0; i < 100; i++)
    {
        await context.Response.WriteAsync($"data: Message {i}\n\n");
        await context.Response.Body.FlushAsync();
        await Task.Delay(1000);
        
        if (context.RequestAborted.IsCancellationRequested)
            break;
    }
});

// WebSocket endpoint
app.UseWebSockets();
app.Map("/ws", async context =>
{
    if (context.WebSockets.IsWebSocketRequest)
    {
        using var webSocket = await context.WebSockets.AcceptWebSocketAsync();
        await HandleWebSocket(webSocket);
    }
    else
    {
        context.Response.StatusCode = StatusCodes.Status400BadRequest;
    }
});

app.Run();

// Records for request/response
public record PaginationRequest(int Page = 1, int PageSize = 10);
public record CreateCustomerRequest(string Name, string Email, string Phone);
public record PaginatedResult<T>(IEnumerable<T> Items, int TotalCount, int Page, int PageSize);

// Custom endpoint filters
public class ValidationFilter<T> : IEndpointFilter where T : class
{
    private readonly IValidator<T> _validator;
    
    public ValidationFilter(IValidator<T> validator)
    {
        _validator = validator;
    }
    
    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        var request = context.GetArgument<T>(0);
        var validationResult = await _validator.ValidateAsync(request);
        
        if (!validationResult.IsValid)
        {
            return TypedResults.ValidationProblem(validationResult.ToDictionary());
        }
        
        return await next(context);
    }
}

public class AuditFilter : IEndpointFilter
{
    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        var httpContext = context.HttpContext;
        var logger = httpContext.RequestServices.GetRequiredService<ILogger<AuditFilter>>();
        
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var result = await next(context);
            
            logger.LogInformation(
                "Request {Method} {Path} completed in {ElapsedMilliseconds}ms",
                httpContext.Request.Method,
                httpContext.Request.Path,
                stopwatch.ElapsedMilliseconds);
            
            return result;
        }
        catch (Exception ex)
        {
            logger.LogError(ex,
                "Request {Method} {Path} failed after {ElapsedMilliseconds}ms",
                httpContext.Request.Method,
                httpContext.Request.Path,
                stopwatch.ElapsedMilliseconds);
            
            throw;
        }
    }
}
```

### 2. Source Generators ANALYSIS AOTANALYSIS
```csharp
// SourceGenerators/JsonSerializerGenerator.cs
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Text;
using System.Text;

[Generator]
public class JsonSerializerGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        // Find all classes with [GenerateSerializer] attribute
        var classDeclarations = context.SyntaxProvider
            .CreateSyntaxProvider(
                predicate: static (s, _) => IsSyntaxTargetForGeneration(s),
                transform: static (ctx, _) => GetSemanticTargetForGeneration(ctx))
            .Where(static m => m is not null);
        
        // Generate code
        context.RegisterSourceOutput(classDeclarations,
            static (spc, source) => Execute(source, spc));
    }
    
    static bool IsSyntaxTargetForGeneration(SyntaxNode node)
        => node is ClassDeclarationSyntax c && c.AttributeLists.Count > 0;
    
    static ClassDeclarationSyntax? GetSemanticTargetForGeneration(GeneratorSyntaxContext context)
    {
        var classDeclaration = (ClassDeclarationSyntax)context.Node;
        
        foreach (var attributeList in classDeclaration.AttributeLists)
        {
            foreach (var attribute in attributeList.Attributes)
            {
                if (context.SemanticModel.GetSymbolInfo(attribute).Symbol is not IMethodSymbol attributeSymbol)
                    continue;
                
                var attributeContainingType = attributeSymbol.ContainingType;
                var fullName = attributeContainingType.ToDisplayString();
                
                if (fullName == "GenerateSerializerAttribute")
                    return classDeclaration;
            }
        }
        
        return null;
    }
    
    static void Execute(ClassDeclarationSyntax? classDeclaration, SourceProductionContext context)
    {
        if (classDeclaration is null)
            return;
        
        var className = classDeclaration.Identifier.Text;
        var namespaceName = GetNamespace(classDeclaration);
        
        var source = GenerateSerializerClass(namespaceName, className);
        context.AddSource($"{className}Serializer.g.cs", SourceText.From(source, Encoding.UTF8));
    }
    
    static string GenerateSerializerClass(string namespaceName, string className)
    {
        return $@"
using System;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace {namespaceName}
{{
    [JsonSerializable(typeof({className}))]
    [JsonSourceGenerationOptions(
        WriteIndented = false,
        PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
    public partial class {className}JsonContext : JsonSerializerContext
    {{
    }}
    
    public static class {className}Serializer
    {{
        private static readonly {className}JsonContext s_context = new();
        
        public static string Serialize({className} value)
        {{
            return JsonSerializer.Serialize(value, s_context.{className});
        }}
        
        public static {className}? Deserialize(string json)
        {{
            return JsonSerializer.Deserialize(json, s_context.{className});
        }}
        
        public static byte[] SerializeToUtf8Bytes({className} value)
        {{
            return JsonSerializer.SerializeToUtf8Bytes(value, s_context.{className});
        }}
        
        public static {className}? Deserialize(ReadOnlySpan<byte> utf8Json)
        {{
            return JsonSerializer.Deserialize(utf8Json, s_context.{className});
        }}
    }}
}}";
    }
}

// Native AOT Configuration
// Program.cs for Native AOT
using System.Text.Json.Serialization;

var builder = WebApplication.CreateSlimBuilder(args);

// Configure JSON serialization for AOT
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.TypeInfoResolverChain.Insert(0, AppJsonSerializerContext.Default);
});

var app = builder.Build();

// API endpoints optimized for AOT
var api = app.MapGroup("/api");

api.MapGet("/data", () => new DataResponse("Hello from AOT!", DateTime.UtcNow));

app.Run();

// JSON serialization context for AOT
[JsonSerializable(typeof(DataResponse))]
internal partial class AppJsonSerializerContext : JsonSerializerContext
{
}

public record DataResponse(string Message, DateTime Timestamp);

// PublishAot in project file
/*
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <PublishAot>true</PublishAot>
    <InvariantGlobalization>true</InvariantGlobalization>
    <PublishTrimmed>true</PublishTrimmed>
    <PublishReadyToRun>true</PublishReadyToRun>
    <PublishSingleFile>true</PublishSingleFile>
    <StripSymbols>true</StripSymbols>
  </PropertyGroup>
</Project>
*/
```

### 3. SYSTEM
```csharp
// Performance/HighPerformanceService.cs
using System.Buffers;
using System.IO.Pipelines;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Threading.Channels;

public class HighPerformanceService
{
    private readonly ArrayPool<byte> _arrayPool = ArrayPool<byte>.Shared;
    private readonly MemoryPool<byte> _memoryPool = MemoryPool<byte>.Shared;
    
    // Span-based string manipulation
    public ReadOnlySpan<char> ProcessString(ReadOnlySpan<char> input)
    {
        Span<char> buffer = stackalloc char[256];
        var written = 0;
        
        foreach (var ch in input)
        {
            if (char.IsLetterOrDigit(ch))
            {
                buffer[written++] = char.ToUpper(ch);
                
                if (written >= buffer.Length)
                    break;
            }
        }
        
        return buffer.Slice(0, written);
    }
    
    // Memory-efficient collection processing
    public async Task ProcessLargeDataAsync(Stream input, Stream output)
    {
        var pipe = new Pipe();
        
        // Producer
        var writing = FillPipeAsync(input, pipe.Writer);
        
        // Consumer
        var reading = ReadPipeAsync(pipe.Reader, output);
        
        await Task.WhenAll(reading, writing);
    }
    
    private async Task FillPipeAsync(Stream input, PipeWriter writer)
    {
        const int minimumBufferSize = 512;
        
        while (true)
        {
            var memory = writer.GetMemory(minimumBufferSize);
            
            try
            {
                int bytesRead = await input.ReadAsync(memory);
                
                if (bytesRead == 0)
                    break;
                
                writer.Advance(bytesRead);
            }
            catch (Exception ex)
            {
                writer.Complete(ex);
                return;
            }
            
            var result = await writer.FlushAsync();
            
            if (result.IsCompleted)
                break;
        }
        
        writer.Complete();
    }
    
    private async Task ReadPipeAsync(PipeReader reader, Stream output)
    {
        while (true)
        {
            var result = await reader.ReadAsync();
            var buffer = result.Buffer;
            
            foreach (var segment in buffer)
            {
                await output.WriteAsync(segment);
            }
            
            reader.AdvanceTo(buffer.End);
            
            if (result.IsCompleted)
                break;
        }
        
        reader.Complete();
    }
    
    // Channel-based producer-consumer
    public async Task ProcessWithChannelsAsync<T>(
        IAsyncEnumerable<T> source,
        Func<T, Task<T>> processor,
        int maxConcurrency = 10)
    {
        var channel = Channel.CreateUnbounded<T>();
        
        // Producer
        var producer = Task.Run(async () =>
        {
            await foreach (var item in source)
            {
                await channel.Writer.WriteAsync(item);
            }
            channel.Writer.Complete();
        });
        
        // Multiple consumers
        var consumers = Enumerable.Range(0, maxConcurrency)
            .Select(_ => Task.Run(async () =>
            {
                await foreach (var item in channel.Reader.ReadAllAsync())
                {
                    await processor(item);
                }
            }))
            .ToArray();
        
        await Task.WhenAll(producer);
        await Task.WhenAll(consumers);
    }
    
    // SIMD optimizations
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public static void VectorizedSum(ReadOnlySpan<float> source, Span<float> destination)
    {
        int vectorSize = Vector<float>.Count;
        int i = 0;
        
        // Process vectorized portion
        for (; i <= source.Length - vectorSize; i += vectorSize)
        {
            var vector = new Vector<float>(source.Slice(i, vectorSize));
            vector.CopyTo(destination.Slice(i, vectorSize));
        }
        
        // Process remaining elements
        for (; i < source.Length; i++)
        {
            destination[i] = source[i];
        }
    }
    
    // Custom memory allocator
    public class PooledMemoryStream : Stream
    {
        private byte[] _buffer;
        private readonly ArrayPool<byte> _pool;
        private int _length;
        private int _position;
        
        public PooledMemoryStream(int initialCapacity = 256)
        {
            _pool = ArrayPool<byte>.Shared;
            _buffer = _pool.Rent(initialCapacity);
        }
        
        public override void Write(byte[] buffer, int offset, int count)
        {
            EnsureCapacity(_position + count);
            Buffer.BlockCopy(buffer, offset, _buffer, _position, count);
            _position += count;
            _length = Math.Max(_length, _position);
        }
        
        private void EnsureCapacity(int capacity)
        {
            if (_buffer.Length < capacity)
            {
                var newBuffer = _pool.Rent(capacity * 2);
                Buffer.BlockCopy(_buffer, 0, newBuffer, 0, _length);
                _pool.Return(_buffer);
                _buffer = newBuffer;
            }
        }
        
        protected override void Dispose(bool disposing)
        {
            if (disposing && _buffer != null)
            {
                _pool.Return(_buffer);
                _buffer = null!;
            }
            base.Dispose(disposing);
        }
        
        // Other Stream members implementation...
        public override bool CanRead => true;
        public override bool CanSeek => true;
        public override bool CanWrite => true;
        public override long Length => _length;
        public override long Position 
        { 
            get => _position; 
            set => _position = (int)value; 
        }
        
        public override void Flush() { }
        
        public override int Read(byte[] buffer, int offset, int count)
        {
            int available = _length - _position;
            int toRead = Math.Min(available, count);
            Buffer.BlockCopy(_buffer, _position, buffer, offset, toRead);
            _position += toRead;
            return toRead;
        }
        
        public override long Seek(long offset, SeekOrigin origin)
        {
            switch (origin)
            {
                case SeekOrigin.Begin:
                    _position = (int)offset;
                    break;
                case SeekOrigin.Current:
                    _position += (int)offset;
                    break;
                case SeekOrigin.End:
                    _position = _length + (int)offset;
                    break;
            }
            return _position;
        }
        
        public override void SetLength(long value)
        {
            _length = (int)value;
        }
    }
}

// Benchmarking
[MemoryDiagnoser]
[SimpleJob(RuntimeMoniker.Net60)]
[SimpleJob(RuntimeMoniker.Net70)]
[SimpleJob(RuntimeMoniker.Net80)]
public class PerformanceBenchmarks
{
    private byte[] _data = null!;
    private readonly ArrayPool<byte> _pool = ArrayPool<byte>.Shared;
    
    [GlobalSetup]
    public void Setup()
    {
        _data = new byte[1024 * 1024]; // 1MB
        Random.Shared.NextBytes(_data);
    }
    
    [Benchmark(Baseline = true)]
    public byte[] AllocateArray()
    {
        var array = new byte[1024];
        ProcessArray(array);
        return array;
    }
    
    [Benchmark]
    public void UseArrayPool()
    {
        var array = _pool.Rent(1024);
        try
        {
            ProcessArray(array);
        }
        finally
        {
            _pool.Return(array);
        }
    }
    
    [Benchmark]
    public void UseStackalloc()
    {
        Span<byte> buffer = stackalloc byte[1024];
        ProcessSpan(buffer);
    }
    
    private void ProcessArray(byte[] array)
    {
        for (int i = 0; i < array.Length; i++)
        {
            array[i] = (byte)(array[i] ^ 0xFF);
        }
    }
    
    private void ProcessSpan(Span<byte> span)
    {
        for (int i = 0; i < span.Length; i++)
        {
            span[i] = (byte)(span[i] ^ 0xFF);
        }
    }
}
```

### 4. C#
```csharp
// ModernCSharpFeatures.cs

// Global usings (in GlobalUsings.cs file)
global using System;
global using System.Collections.Generic;
global using System.Linq;
global using System.Threading.Tasks;
global using Microsoft.Extensions.DependencyInjection;
global using Microsoft.Extensions.Logging;

// File-scoped namespaces
namespace ModernApp.Services;

// Record types with positional parameters
public record Customer(
    Guid Id,
    string Name,
    string Email,
    DateTime CreatedAt,
    CustomerStatus Status = CustomerStatus.Active)
{
    // Additional members
    public string DisplayName => $"{Name} ({Email})";
    
    // Init-only properties
    public Address? Address { get; init; }
    
    // Validation
    public bool IsValid => !string.IsNullOrEmpty(Name) && !string.IsNullOrEmpty(Email);
}

// Record struct for value types
public readonly record struct Money(decimal Amount, string Currency)
{
    public static Money Zero => new(0, "USD");
    
    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new InvalidOperationException("Cannot add different currencies");
        
        return this with { Amount = Amount + other.Amount };
    }
    
    public override string ToString() => $"{Amount:C} {Currency}";
}

// Pattern matching enhancements
public class PatternMatchingExamples
{
    // Switch expressions with patterns
    public static string DescribeValue(object value) => value switch
    {
        null => "null",
        "" => "empty string",
        string s when s.Length < 10 => $"short string: {s}",
        string s => $"long string: {s[..10]}...",
        int n when n < 0 => $"negative: {n}",
        int n when n == 0 => "zero",
        int n => $"positive: {n}",
        DateTime { Year: 2024, Month: 12 } => "December 2024",
        DateTime dt => dt.ToString("yyyy-MM-dd"),
        IEnumerable<int> numbers => $"collection with {numbers.Count()} items",
        { } => value.ToString() ?? "unknown"
    };
    
    // Property patterns
    public static decimal CalculateDiscount(Customer customer) => customer switch
    {
        { Status: CustomerStatus.VIP, CreatedAt: var date } when (DateTime.Now - date).Days > 365 
            => 0.20m,
        { Status: CustomerStatus.VIP } => 0.15m,
        { Status: CustomerStatus.Active, Address: { Country: "Japan" } } => 0.10m,
        { Status: CustomerStatus.Active } => 0.05m,
        _ => 0m
    };
    
    // Tuple patterns
    public static string CombineResults(Result<int> r1, Result<int> r2) => (r1, r2) switch
    {
        (Success<int> s1, Success<int> s2) => $"Both succeeded: {s1.Value + s2.Value}",
        (Success<int> s, Failure<int> f) or (Failure<int> f, Success<int> s) 
            => $"Partial success: {s.Value}, Error: {f.Error}",
        (Failure<int> f1, Failure<int> f2) => $"Both failed: {f1.Error}, {f2.Error}",
        _ => "Unknown state"
    };
    
    // List patterns (C# 11)
    public static string DescribeArray(int[] array) => array switch
    {
        [] => "Empty array",
        [var single] => $"Single element: {single}",
        [var first, var second] => $"Two elements: {first}, {second}",
        [var first, .., var last] => $"Multiple elements from {first} to {last}",
        _ => "Unknown pattern"
    };
}

// Generic math (C# 11)
public interface ICalculator<T> where T : INumber<T>
{
    T Add(T a, T b);
    T Multiply(T a, T b);
    T Power(T @base, int exponent);
}

public class Calculator<T> : ICalculator<T> where T : INumber<T>
{
    public T Add(T a, T b) => a + b;
    
    public T Multiply(T a, T b) => a * b;
    
    public T Power(T @base, int exponent)
    {
        T result = T.One;
        for (int i = 0; i < exponent; i++)
        {
            result *= @base;
        }
        return result;
    }
}

// Required members (C# 11)
public class Configuration
{
    public required string ConnectionString { get; init; }
    public required int MaxRetries { get; init; }
    public int Timeout { get; init; } = 30;
    
    [SetsRequiredMembers]
    public Configuration(string connectionString, int maxRetries)
    {
        ConnectionString = connectionString;
        MaxRetries = maxRetries;
    }
}

// Raw string literals (C# 11)
public class SqlQueries
{
    public const string ComplexQuery = """
        SELECT 
            c.Id,
            c.Name,
            c.Email,
            COUNT(o.Id) as OrderCount,
            SUM(o.Total) as TotalSpent
        FROM Customers c
        LEFT JOIN Orders o ON c.Id = o.CustomerId
        WHERE c.Status = 'Active'
          AND c.CreatedAt >= @startDate
        GROUP BY c.Id, c.Name, c.Email
        HAVING COUNT(o.Id) > 0
        ORDER BY TotalSpent DESC
        """;
    
    public const string JsonTemplate = """
        {
            "name": "{name}",
            "email": "{email}",
            "metadata": {
                "created": "{created}",
                "tags": [
                    "customer",
                    "active"
                ]
            }
        }
        """;
}

// Primary constructors (C# 12)
public class CustomerService(
    ILogger<CustomerService> logger,
    ICustomerRepository repository,
    ICacheService cache)
{
    // Fields are automatically created from primary constructor parameters
    
    public async Task<Customer?> GetCustomerAsync(Guid id)
    {
        logger.LogInformation("Getting customer {Id}", id);
        
        // Check cache first
        var cached = await cache.GetAsync<Customer>($"customer:{id}");
        if (cached is not null)
            return cached;
        
        // Get from repository
        var customer = await repository.GetByIdAsync(id);
        
        if (customer is not null)
        {
            await cache.SetAsync($"customer:{id}", customer, TimeSpan.FromMinutes(5));
        }
        
        return customer;
    }
}

// Collection expressions (C# 12)
public class CollectionExamples
{
    // Simplified collection initialization
    private readonly int[] _numbers = [1, 2, 3, 4, 5];
    private readonly List<string> _names = ["Alice", "Bob", "Charlie"];
    private readonly HashSet<int> _uniqueNumbers = [1, 2, 3, 3, 4, 5]; // Duplicates removed
    
    // Spread operator
    public int[] CombineArrays(int[] first, int[] second)
    {
        return [.. first, .. second, 100]; // Spread both arrays and add 100
    }
    
    // Pattern matching with collections
    public void ProcessItems(List<string> items)
    {
        var processed = items switch
        {
            ["start", .. var middle, "end"] => middle,
            [var first, .. var rest] when first.StartsWith("cmd_") => rest,
            _ => items
        };
    }
}

// Interceptors (C# 12 - experimental)
[InterceptsLocation("Program.cs", line: 42, column: 5)]
public static void InterceptedMethod(this ILogger logger, string message)
{
    // This method intercepts calls to logger at specific location
    logger.LogInformation("[INTERCEPTED] {Message}", message);
}
```

## 
```markdown
# .NET 6+  

## 
[OK] Minimal API: 
[OK] Native AOT: 
[OK] Source Generators: 
[OK] : 
[OK] C# 12: 

## 
- : 50msAOT
- : 15MB80%
- : 100μs/req
- : 10MB

## 
- : 60%Minimal API
- : 70%
- Hot Reload: 
- : 3

## 
1. .NET 8 
2. Aspire 
3. ContainerK8s
```

## 
- ****: 
- ****: .NET 6+ Native AOTAPI

---
*.NET 6*