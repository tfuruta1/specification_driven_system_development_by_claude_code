# /aspnet-mvc-api - ASP.NET MVC/Web API エンタープライズ専用コマンド

## 概要
ASP.NET MVC と Web API の開発に特化した包括的なコマンドです。.NET Framework 4.x から .NET 8 まで、各バージョンに応じた最適な実装を提供します。

## バージョン別対応

### 🔍 バージョン検出と切り替え
```csharp
// TargetFramework検出による自動切り替え
#if NET8_0_OR_GREATER
    // .NET 8 最新機能
    builder.Services.AddProblemDetails();
    builder.Services.AddApiVersioning();
#elif NET6_0_OR_GREATER
    // .NET 6+ 機能
    builder.Services.AddEndpointsApiExplorer();
#elif NETCOREAPP3_1
    // .NET Core 3.1
    services.AddControllers();
#elif NET48
    // .NET Framework 4.8
    GlobalConfiguration.Configure(WebApiConfig.Register);
#endif
```

## .NET 8/7/6 - モダンWeb API実装

### 1. コントローラーベースAPI（.NET Core 3.1+）
```csharp
// Controllers/CustomerController.cs
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.RateLimiting;
using Asp.Versioning;

[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
[ApiVersion("1.0")]
[ApiVersion("2.0")]
[Authorize]
[EnableRateLimiting("api")]
[ResponseCache(Duration = 60, Location = ResponseCacheLocation.Client)]
public class CustomersController : ControllerBase
{
    private readonly ICustomerService _customerService;
    private readonly ILogger<CustomersController> _logger;
    private readonly IMapper _mapper;

    public CustomersController(
        ICustomerService customerService,
        ILogger<CustomersController> logger,
        IMapper mapper)
    {
        _customerService = customerService;
        _logger = logger;
        _mapper = mapper;
    }

    /// <summary>
    /// Get all customers with pagination
    /// </summary>
    /// <param name="parameters">Pagination and filter parameters</param>
    /// <returns>Paginated list of customers</returns>
    [HttpGet]
    [MapToApiVersion("1.0")]
    [ProducesResponseType(typeof(PagedResult<CustomerDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<PagedResult<CustomerDto>>> GetCustomers(
        [FromQuery] CustomerParameters parameters)
    {
        var customers = await _customerService.GetCustomersAsync(parameters);
        
        Response.Headers.Add("X-Pagination", JsonSerializer.Serialize(customers.Metadata));
        
        var customerDtos = _mapper.Map<IEnumerable<CustomerDto>>(customers);
        
        return Ok(new PagedResult<CustomerDto>
        {
            Items = customerDtos,
            Metadata = customers.Metadata
        });
    }

    /// <summary>
    /// Get customer by ID (Version 2.0 with additional data)
    /// </summary>
    [HttpGet("{id:guid}")]
    [MapToApiVersion("2.0")]
    [ProducesResponseType(typeof(CustomerDetailDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<CustomerDetailDto>> GetCustomerV2(Guid id)
    {
        var customer = await _customerService.GetCustomerWithDetailsAsync(id);
        
        if (customer == null)
        {
            return Problem(
                detail: $"Customer with ID {id} not found",
                statusCode: StatusCodes.Status404NotFound,
                title: "Customer Not Found");
        }
        
        return Ok(_mapper.Map<CustomerDetailDto>(customer));
    }

    /// <summary>
    /// Create a new customer
    /// </summary>
    [HttpPost]
    [MapToApiVersion("1.0")]
    [MapToApiVersion("2.0")]
    [Consumes("application/json")]
    [ProducesResponseType(typeof(CustomerDto), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ValidationProblemDetails), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<CustomerDto>> CreateCustomer(
        [FromBody] CreateCustomerDto createDto)
    {
        // Custom validation
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }
        
        var customer = _mapper.Map<Customer>(createDto);
        var created = await _customerService.CreateCustomerAsync(customer);
        var dto = _mapper.Map<CustomerDto>(created);
        
        return CreatedAtAction(
            nameof(GetCustomerV2),
            new { id = dto.Id, version = "2.0" },
            dto);
    }

    /// <summary>
    /// Bulk operations endpoint
    /// </summary>
    [HttpPost("bulk")]
    [MapToApiVersion("2.0")]
    [RequestSizeLimit(10_000_000)] // 10MB limit
    [RequestTimeout(milliseconds: 30000)] // 30 seconds timeout
    public async Task<ActionResult<BulkOperationResult>> BulkOperation(
        [FromBody] BulkOperationRequest request)
    {
        var result = new BulkOperationResult();
        
        using var transaction = await _customerService.BeginTransactionAsync();
        
        try
        {
            foreach (var operation in request.Operations)
            {
                try
                {
                    var opResult = operation.Type switch
                    {
                        OperationType.Create => await ProcessCreate(operation),
                        OperationType.Update => await ProcessUpdate(operation),
                        OperationType.Delete => await ProcessDelete(operation),
                        _ => throw new NotSupportedException($"Operation type {operation.Type} not supported")
                    };
                    
                    result.Successful.Add(opResult);
                }
                catch (Exception ex)
                {
                    result.Failed.Add(new FailedOperation
                    {
                        Operation = operation,
                        Error = ex.Message
                    });
                }
            }
            
            await transaction.CommitAsync();
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
        
        return Ok(result);
    }

    /// <summary>
    /// Server-Sent Events endpoint for real-time updates
    /// </summary>
    [HttpGet("stream")]
    [MapToApiVersion("2.0")]
    [Produces("text/event-stream")]
    public async IAsyncEnumerable<string> StreamCustomerUpdates(
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        await foreach (var update in _customerService.GetCustomerUpdatesAsync(cancellationToken))
        {
            yield return $"data: {JsonSerializer.Serialize(update)}\n\n";
            await Task.Delay(100, cancellationToken); // Rate limiting
        }
    }

    /// <summary>
    /// File upload endpoint
    /// </summary>
    [HttpPost("{id:guid}/documents")]
    [DisableRequestSizeLimit]
    [RequestFormLimits(MultipartBodyLengthLimit = 209715200)] // 200MB
    public async Task<ActionResult> UploadDocument(
        Guid id,
        [FromForm] IFormFile file,
        [FromServices] IFileStorageService fileStorage)
    {
        if (file == null || file.Length == 0)
        {
            return BadRequest("No file uploaded");
        }
        
        var allowedExtensions = new[] { ".pdf", ".doc", ".docx", ".xls", ".xlsx" };
        var extension = Path.GetExtension(file.FileName).ToLowerInvariant();
        
        if (!allowedExtensions.Contains(extension))
        {
            return BadRequest($"File type {extension} not allowed");
        }
        
        using var stream = file.OpenReadStream();
        var fileId = await fileStorage.SaveAsync(stream, file.FileName, file.ContentType);
        
        await _customerService.AttachDocumentAsync(id, fileId, file.FileName);
        
        return Ok(new { FileId = fileId, FileName = file.FileName });
    }
}

// Filters/GlobalExceptionFilter.cs (.NET Core 3.1+)
public class GlobalExceptionFilter : IExceptionFilter
{
    private readonly ILogger<GlobalExceptionFilter> _logger;
    private readonly IWebHostEnvironment _env;

    public GlobalExceptionFilter(ILogger<GlobalExceptionFilter> logger, IWebHostEnvironment env)
    {
        _logger = logger;
        _env = env;
    }

    public void OnException(ExceptionContext context)
    {
        var exception = context.Exception;
        _logger.LogError(exception, "Unhandled exception occurred");

        var problemDetails = new ProblemDetails
        {
            Status = StatusCodes.Status500InternalServerError,
            Title = "An error occurred while processing your request",
            Type = "https://tools.ietf.org/html/rfc7231#section-6.6.1"
        };

        if (_env.IsDevelopment())
        {
            problemDetails.Detail = exception.ToString();
        }
        else
        {
            problemDetails.Detail = "An error occurred. Please try again later.";
        }

        problemDetails.Instance = context.HttpContext.Request.Path;
        problemDetails.Extensions["traceId"] = Activity.Current?.Id ?? context.HttpContext.TraceIdentifier;

        context.Result = new ObjectResult(problemDetails)
        {
            StatusCode = StatusCodes.Status500InternalServerError
        };

        context.ExceptionHandled = true;
    }
}

// Middleware/RequestLoggingMiddleware.cs
public class RequestLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestLoggingMiddleware> _logger;

    public RequestLoggingMiddleware(RequestDelegate next, ILogger<RequestLoggingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var requestId = Guid.NewGuid().ToString();
        context.Items["RequestId"] = requestId;

        var stopwatch = Stopwatch.StartNew();

        try
        {
            // Log request
            _logger.LogInformation(
                "Request {RequestId} {Method} {Path} started",
                requestId,
                context.Request.Method,
                context.Request.Path);

            // Call the next middleware
            await _next(context);

            // Log response
            _logger.LogInformation(
                "Request {RequestId} completed with {StatusCode} in {ElapsedMilliseconds}ms",
                requestId,
                context.Response.StatusCode,
                stopwatch.ElapsedMilliseconds);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Request {RequestId} failed after {ElapsedMilliseconds}ms",
                requestId,
                stopwatch.ElapsedMilliseconds);
            
            throw;
        }
    }
}
```

### 2. .NET Framework 4.8/4.7.2 - 従来のASP.NET Web API
```csharp
// Controllers/CustomerController.cs (.NET Framework)
using System.Web.Http;
using System.Web.Http.Description;
using System.Web.Http.OData;

namespace EnterpriseAPI.Controllers
{
    [RoutePrefix("api/customers")]
    [Authorize]
    public class CustomerController : ApiController
    {
        private readonly ICustomerService _customerService;
        private readonly ILogger _logger;

        public CustomerController(ICustomerService customerService, ILogger logger)
        {
            _customerService = customerService;
            _logger = logger;
        }

        // GET api/customers
        [HttpGet]
        [Route("")]
        [EnableQuery(PageSize = 100)] // OData query support
        [ResponseType(typeof(IEnumerable<CustomerDto>))]
        public async Task<IHttpActionResult> GetCustomers(
            int page = 1, 
            int pageSize = 10,
            string sortBy = "Name",
            bool ascending = true)
        {
            try
            {
                var parameters = new CustomerParameters
                {
                    Page = page,
                    PageSize = pageSize,
                    SortBy = sortBy,
                    Ascending = ascending
                };

                var customers = await _customerService.GetCustomersAsync(parameters);
                
                // Add pagination headers
                HttpContext.Current.Response.Headers.Add("X-Total-Count", customers.TotalCount.ToString());
                HttpContext.Current.Response.Headers.Add("X-Page", page.ToString());
                HttpContext.Current.Response.Headers.Add("X-Page-Size", pageSize.ToString());

                return Ok(customers);
            }
            catch (Exception ex)
            {
                _logger.Error("Error getting customers", ex);
                return InternalServerError(ex);
            }
        }

        // GET api/customers/5
        [HttpGet]
        [Route("{id:guid}")]
        [ResponseType(typeof(CustomerDto))]
        public async Task<IHttpActionResult> GetCustomer(Guid id)
        {
            var customer = await _customerService.GetCustomerAsync(id);
            
            if (customer == null)
            {
                return NotFound();
            }
            
            return Ok(customer);
        }

        // POST api/customers
        [HttpPost]
        [Route("")]
        [ResponseType(typeof(CustomerDto))]
        public async Task<IHttpActionResult> CreateCustomer([FromBody] CreateCustomerDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            try
            {
                var customer = await _customerService.CreateCustomerAsync(dto);
                return CreatedAtRoute("DefaultApi", new { id = customer.Id }, customer);
            }
            catch (BusinessException ex)
            {
                return BadRequest(ex.Message);
            }
            catch (Exception ex)
            {
                _logger.Error("Error creating customer", ex);
                return InternalServerError(ex);
            }
        }

        // PUT api/customers/5
        [HttpPut]
        [Route("{id:guid}")]
        [ResponseType(typeof(void))]
        public async Task<IHttpActionResult> UpdateCustomer(Guid id, [FromBody] UpdateCustomerDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            if (id != dto.Id)
            {
                return BadRequest("ID mismatch");
            }

            try
            {
                await _customerService.UpdateCustomerAsync(dto);
                return StatusCode(HttpStatusCode.NoContent);
            }
            catch (NotFoundException)
            {
                return NotFound();
            }
        }

        // DELETE api/customers/5
        [HttpDelete]
        [Route("{id:guid}")]
        [ResponseType(typeof(void))]
        public async Task<IHttpActionResult> DeleteCustomer(Guid id)
        {
            try
            {
                await _customerService.DeleteCustomerAsync(id);
                return StatusCode(HttpStatusCode.NoContent);
            }
            catch (NotFoundException)
            {
                return NotFound();
            }
        }

        // Batch operations
        [HttpPost]
        [Route("batch")]
        [ResponseType(typeof(BatchResult))]
        public async Task<IHttpActionResult> BatchOperation([FromBody] BatchRequest request)
        {
            var result = new BatchResult();
            
            foreach (var operation in request.Operations)
            {
                try
                {
                    switch (operation.Method.ToUpper())
                    {
                        case "POST":
                            var created = await _customerService.CreateCustomerAsync(
                                JsonConvert.DeserializeObject<CreateCustomerDto>(operation.Body));
                            result.Responses.Add(new BatchResponse
                            {
                                Id = operation.Id,
                                Status = 201,
                                Body = created
                            });
                            break;
                            
                        case "PUT":
                            await _customerService.UpdateCustomerAsync(
                                JsonConvert.DeserializeObject<UpdateCustomerDto>(operation.Body));
                            result.Responses.Add(new BatchResponse
                            {
                                Id = operation.Id,
                                Status = 204
                            });
                            break;
                            
                        case "DELETE":
                            await _customerService.DeleteCustomerAsync(Guid.Parse(operation.Id));
                            result.Responses.Add(new BatchResponse
                            {
                                Id = operation.Id,
                                Status = 204
                            });
                            break;
                    }
                }
                catch (Exception ex)
                {
                    result.Responses.Add(new BatchResponse
                    {
                        Id = operation.Id,
                        Status = 500,
                        Error = ex.Message
                    });
                }
            }
            
            return Ok(result);
        }
    }

    // Filters/AuthorizeAttribute.cs (.NET Framework)
    public class CustomAuthorizeAttribute : AuthorizeAttribute
    {
        private readonly string[] _allowedRoles;

        public CustomAuthorizeAttribute(params string[] roles)
        {
            _allowedRoles = roles;
        }

        protected override bool IsAuthorized(HttpActionContext actionContext)
        {
            var user = actionContext.RequestContext.Principal;
            
            if (!user.Identity.IsAuthenticated)
            {
                return false;
            }

            if (_allowedRoles.Length > 0)
            {
                return _allowedRoles.Any(role => user.IsInRole(role));
            }

            return true;
        }

        protected override void HandleUnauthorizedRequest(HttpActionContext actionContext)
        {
            if (!actionContext.RequestContext.Principal.Identity.IsAuthenticated)
            {
                actionContext.Response = actionContext.Request.CreateResponse(
                    HttpStatusCode.Unauthorized,
                    new { message = "Authentication required" });
            }
            else
            {
                actionContext.Response = actionContext.Request.CreateResponse(
                    HttpStatusCode.Forbidden,
                    new { message = "Insufficient permissions" });
            }
        }
    }

    // App_Start/WebApiConfig.cs (.NET Framework)
    public static class WebApiConfig
    {
        public static void Register(HttpConfiguration config)
        {
            // Web API configuration and services
            config.DependencyResolver = new UnityResolver(UnityConfig.Container);

            // Web API routes
            config.MapHttpAttributeRoutes();

            config.Routes.MapHttpRoute(
                name: "DefaultApi",
                routeTemplate: "api/{controller}/{id}",
                defaults: new { id = RouteParameter.Optional }
            );

            // Enable CORS
            var cors = new EnableCorsAttribute("*", "*", "*");
            config.EnableCors(cors);

            // OData
            config.AddODataQueryFilter();

            // Formatters
            config.Formatters.JsonFormatter.SerializerSettings.ContractResolver = 
                new CamelCasePropertyNamesContractResolver();
            config.Formatters.JsonFormatter.SerializerSettings.DateFormatHandling = 
                DateFormatHandling.IsoDateFormat;

            // Remove XML formatter
            config.Formatters.Remove(config.Formatters.XmlFormatter);

            // Global filters
            config.Filters.Add(new CustomExceptionFilterAttribute());
            config.Filters.Add(new ValidateModelAttribute());

            // Message handlers
            config.MessageHandlers.Add(new LoggingHandler());
            config.MessageHandlers.Add(new CompressionHandler());
        }
    }
}
```

### 3. バージョン別機能対応マトリックス

| 機能 | .NET 8 | .NET 6 | .NET Core 3.1 | .NET Framework 4.8 |
|------|--------|--------|---------------|-------------------|
| Minimal API | ✅ | ✅ | ❌ | ❌ |
| API Versioning | ✅ Native | ✅ Package | ✅ Package | ✅ Custom |
| OpenAPI/Swagger | ✅ Built-in | ✅ Swashbuckle | ✅ Swashbuckle | ✅ Swashbuckle |
| Rate Limiting | ✅ Built-in | ⚠️ Custom | ⚠️ Custom | ⚠️ Custom |
| Problem Details | ✅ RFC 7807 | ✅ RFC 7807 | ⚠️ Custom | ❌ |
| gRPC | ✅ | ✅ | ✅ | ❌ |
| GraphQL | ✅ HotChocolate | ✅ HotChocolate | ✅ GraphQL.NET | ✅ GraphQL.NET |
| OData | ✅ v8 | ✅ v8 | ✅ v7 | ✅ v7 |
| SignalR | ✅ Core | ✅ Core | ✅ Core | ✅ Legacy |
| Health Checks | ✅ | ✅ | ✅ | ⚠️ Custom |
| Output Caching | ✅ | ❌ | ❌ | ⚠️ Custom |

## 共通設定とベストプラクティス

### API設計原則
```yaml
# RESTful API設計
Resources:
  - Collection: /api/customers
  - Item: /api/customers/{id}
  - Sub-resource: /api/customers/{id}/orders
  
HTTP Methods:
  GET: 取得（冪等）
  POST: 作成
  PUT: 完全更新（冪等）
  PATCH: 部分更新（冪等）
  DELETE: 削除（冪等）
  
Status Codes:
  200: OK
  201: Created
  204: No Content
  400: Bad Request
  401: Unauthorized
  403: Forbidden
  404: Not Found
  409: Conflict
  422: Unprocessable Entity
  500: Internal Server Error
```

### セキュリティ設定
```csharp
// すべてのバージョン共通
public class SecurityConfiguration
{
    public static void Configure(IServiceCollection services)
    {
        // CORS
        services.AddCors(options =>
        {
            options.AddPolicy("Production",
                builder => builder
                    .WithOrigins("https://app.example.com")
                    .WithMethods("GET", "POST", "PUT", "DELETE")
                    .WithHeaders("Authorization", "Content-Type")
                    .AllowCredentials());
        });

        // Authentication
        services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddJwtBearer(options =>
            {
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = true,
                    ValidateAudience = true,
                    ValidateLifetime = true,
                    ValidateIssuerSigningKey = true,
                    ClockSkew = TimeSpan.Zero
                };
            });

        // Authorization
        services.AddAuthorization(options =>
        {
            options.AddPolicy("ApiUser", policy => policy.RequireClaim("api_access", "true"));
            options.AddPolicy("Admin", policy => policy.RequireRole("Admin"));
        });

        // Anti-forgery
        services.AddAntiforgery(options =>
        {
            options.HeaderName = "X-XSRF-TOKEN";
        });

        // Data Protection
        services.AddDataProtection()
            .PersistKeysToFileSystem(new DirectoryInfo(@".\keys"))
            .SetApplicationName("EnterpriseAPI");
    }
}
```

## パフォーマンス最適化

### レスポンス圧縮（全バージョン）
```csharp
#if NET6_0_OR_GREATER
// .NET 6+
services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
});
#else
// .NET Framework
public class CompressionHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var response = await base.SendAsync(request, cancellationToken);
        
        if (response.Content != null)
        {
            var encoding = request.Headers.AcceptEncoding
                .FirstOrDefault(x => x.Value == "gzip" || x.Value == "deflate");
                
            if (encoding != null)
            {
                response.Content = new CompressedContent(response.Content, encoding.Value);
            }
        }
        
        return response;
    }
}
#endif
```

## 出力レポート
```markdown
# ASP.NET MVC/Web API 最適化レポート

## 実施項目
✅ API バージョニング: 実装済み
✅ OpenAPI/Swagger: 統合完了
✅ 認証・認可: JWT実装
✅ エラーハンドリング: 標準化
✅ パフォーマンス: 最適化済み

## パフォーマンス指標
- レスポンス時間: <100ms (P95)
- スループット: 10,000 req/s
- 同時接続数: 5,000
- CPU使用率: 40% (平均)
- メモリ使用量: 500MB

## 推奨事項
1. .NET 8への移行（.NET Framework案件）
2. Minimal API採用検討
3. gRPC/GraphQL評価
4. コンテナ化とK8s対応
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: ASP.NET MVC/Web API全バージョン対応

---
*このコマンドはASP.NET MVC/Web APIの全バージョンに対応した開発に特化しています。*