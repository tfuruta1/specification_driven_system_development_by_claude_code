# /azure-integration - Azure

## 
Microsoft AzureAzure App ServiceFunctionsStorageCosmos DBService BusApplication InsightsAzure

## Azure SDK 
```csharp
// NuGet packages based on .NET version
#if NET8_0_OR_GREATER
    <PackageReference Include="Azure.Identity" Version="1.10.*" />
    <PackageReference Include="Azure.Storage.Blobs" Version="12.19.*" />
    <PackageReference Include="Microsoft.Azure.Cosmos" Version="3.37.*" />
#elif NET6_0_OR_GREATER
    <PackageReference Include="Azure.Identity" Version="1.8.*" />
    <PackageReference Include="Azure.Storage.Blobs" Version="12.14.*" />
#else
    // .NET Framework - Legacy SDKs
    <PackageReference Include="WindowsAzure.Storage" Version="9.3.3" />
    <PackageReference Include="Microsoft.Azure.ServiceBus" Version="5.2.0" />
#endif
```

## AzureSYSTEM

### 1. Azure IdentitySYSTEM
```csharp
// Services/AzureAuthenticationService.cs
using Azure.Core;
using Azure.Identity;
using Microsoft.Extensions.Configuration;

public class AzureAuthenticationService
{
    private readonly IConfiguration _configuration;
    private readonly DefaultAzureCredential _credential;
    private readonly ChainedTokenCredential _chainedCredential;
    
    public AzureAuthenticationService(IConfiguration configuration)
    {
        _configuration = configuration;
        
        // Development and Production authentication chain
        _chainedCredential = new ChainedTokenCredential(
            new ManagedIdentityCredential(), // For Azure hosted services
            new EnvironmentCredential(),      // For local development with env vars
            new AzureCliCredential(),         // For local development with Azure CLI
            new VisualStudioCredential(),     // For Visual Studio authentication
            new InteractiveBrowserCredential() // Fallback to browser auth
        );
        
        // Default credential with options
        var options = new DefaultAzureCredentialOptions
        {
            ExcludeEnvironmentCredential = false,
            ExcludeManagedIdentityCredential = false,
            ExcludeSharedTokenCacheCredential = true,
            ExcludeVisualStudioCredential = false,
            ExcludeVisualStudioCodeCredential = true,
            ExcludeAzureCliCredential = false,
            ExcludeInteractiveBrowserCredential = !configuration.GetValue<bool>("Azure:AllowInteractive"),
            TenantId = configuration["Azure:TenantId"]
        };
        
        _credential = new DefaultAzureCredential(options);
    }
    
    public TokenCredential GetCredential() => _credential;
    
    public async Task<string> GetAccessTokenAsync(string[] scopes)
    {
        var tokenRequestContext = new TokenRequestContext(scopes);
        var token = await _credential.GetTokenAsync(tokenRequestContext);
        return token.Token;
    }
    
    // Service Principal authentication for CI/CD
    public TokenCredential GetServicePrincipalCredential()
    {
        return new ClientSecretCredential(
            _configuration["Azure:TenantId"],
            _configuration["Azure:ClientId"],
            _configuration["Azure:ClientSecret"]
        );
    }
}

// Program.cs - Azure services registration
builder.Services.AddSingleton<AzureAuthenticationService>();

// Azure Key Vault configuration
builder.Configuration.AddAzureKeyVault(
    new Uri($"https://{builder.Configuration["KeyVault:Name"]}.vault.azure.net/"),
    new DefaultAzureCredential());

// Application Insights
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.ConnectionString = builder.Configuration["ApplicationInsights:ConnectionString"];
    options.EnableAdaptiveSampling = true;
    options.EnableQuickPulseMetricStream = true;
});

// Azure Service Bus
builder.Services.AddSingleton<ServiceBusClient>(sp =>
{
    var authService = sp.GetRequiredService<AzureAuthenticationService>();
    return new ServiceBusClient(
        builder.Configuration["ServiceBus:Namespace"],
        authService.GetCredential());
});

// Azure Storage
builder.Services.AddSingleton<BlobServiceClient>(sp =>
{
    var authService = sp.GetRequiredService<AzureAuthenticationService>();
    return new BlobServiceClient(
        new Uri($"https://{builder.Configuration["Storage:AccountName"]}.blob.core.windows.net"),
        authService.GetCredential());
});

// Cosmos DB
builder.Services.AddSingleton<CosmosClient>(sp =>
{
    var authService = sp.GetRequiredService<AzureAuthenticationService>();
    return new CosmosClient(
        builder.Configuration["CosmosDb:AccountEndpoint"],
        authService.GetCredential(),
        new CosmosClientOptions
        {
            ApplicationName = "EnterpriseApp",
            ConnectionMode = ConnectionMode.Direct,
            ConsistencyLevel = ConsistencyLevel.Session,
            EnableContentResponseOnWrite = false,
            MaxRetryAttemptsOnRateLimitedRequests = 9,
            MaxRetryWaitTimeOnRateLimitedRequests = TimeSpan.FromSeconds(30)
        });
});
```

### 2. Azure Storage
```csharp
// Services/AzureStorageService.cs
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using Azure.Storage.Sas;

public class AzureStorageService : IStorageService
{
    private readonly BlobServiceClient _blobServiceClient;
    private readonly ILogger<AzureStorageService> _logger;
    private readonly IConfiguration _configuration;
    
    public AzureStorageService(
        BlobServiceClient blobServiceClient,
        ILogger<AzureStorageService> logger,
        IConfiguration configuration)
    {
        _blobServiceClient = blobServiceClient;
        _logger = logger;
        _configuration = configuration;
    }
    
    public async Task<string> UploadFileAsync(
        Stream fileStream,
        string fileName,
        string containerName,
        Dictionary<string, string>? metadata = null)
    {
        try
        {
            var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
            
            // Ensure container exists
            await containerClient.CreateIfNotExistsAsync(PublicAccessType.None);
            
            // Generate unique blob name
            var blobName = $"{Guid.NewGuid()}/{fileName}";
            var blobClient = containerClient.GetBlobClient(blobName);
            
            // Upload options
            var options = new BlobUploadOptions
            {
                Metadata = metadata,
                HttpHeaders = new BlobHttpHeaders
                {
                    ContentType = GetContentType(fileName),
                    CacheControl = "max-age=3600"
                },
                TransferOptions = new StorageTransferOptions
                {
                    MaximumConcurrency = 8,
                    MaximumTransferSize = 4 * 1024 * 1024 // 4MB chunks
                }
            };
            
            // Upload with progress tracking
            var response = await blobClient.UploadAsync(fileStream, options);
            
            _logger.LogInformation($"File uploaded successfully: {blobName}");
            
            return blobClient.Uri.ToString();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Failed to upload file: {fileName}");
            throw;
        }
    }
    
    public async Task<Stream> DownloadFileAsync(string blobUri)
    {
        var blobClient = new BlobClient(new Uri(blobUri), _blobServiceClient.GetCredential());
        var download = await blobClient.DownloadStreamingAsync();
        return download.Value.Content;
    }
    
    public string GenerateSasUrl(string blobUri, TimeSpan expiry, BlobSasPermissions permissions = BlobSasPermissions.Read)
    {
        var blobClient = new BlobClient(new Uri(blobUri), _blobServiceClient.GetCredential());
        
        if (!blobClient.CanGenerateSasUri)
        {
            throw new InvalidOperationException("Cannot generate SAS for this blob");
        }
        
        var sasBuilder = new BlobSasBuilder
        {
            BlobContainerName = blobClient.BlobContainerName,
            BlobName = blobClient.Name,
            Resource = "b",
            ExpiresOn = DateTimeOffset.UtcNow.Add(expiry)
        };
        
        sasBuilder.SetPermissions(permissions);
        
        return blobClient.GenerateSasUri(sasBuilder).ToString();
    }
    
    public async Task<bool> DeleteFileAsync(string blobUri)
    {
        var blobClient = new BlobClient(new Uri(blobUri), _blobServiceClient.GetCredential());
        var response = await blobClient.DeleteIfExistsAsync();
        return response.Value;
    }
    
    // Batch operations for efficiency
    public async Task<IEnumerable<string>> UploadBatchAsync(
        IEnumerable<(Stream stream, string fileName)> files,
        string containerName)
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
        await containerClient.CreateIfNotExistsAsync();
        
        var uploadTasks = files.Select(async file =>
        {
            var blobName = $"{Guid.NewGuid()}/{file.fileName}";
            var blobClient = containerClient.GetBlobClient(blobName);
            await blobClient.UploadAsync(file.stream);
            return blobClient.Uri.ToString();
        });
        
        return await Task.WhenAll(uploadTasks);
    }
    
    private string GetContentType(string fileName)
    {
        var extension = Path.GetExtension(fileName).ToLowerInvariant();
        return extension switch
        {
            ".pdf" => "application/pdf",
            ".jpg" or ".jpeg" => "image/jpeg",
            ".png" => "image/png",
            ".gif" => "image/gif",
            ".mp4" => "video/mp4",
            ".json" => "application/json",
            ".xml" => "application/xml",
            ".txt" => "text/plain",
            _ => "application/octet-stream"
        };
    }
}
```

### 3. Azure Cosmos DB
```csharp
// Services/CosmosDbService.cs
using Microsoft.Azure.Cosmos;
using Microsoft.Azure.Cosmos.Linq;

public class CosmosDbService<T> : IDocumentDbService<T> where T : IEntity
{
    private readonly CosmosClient _cosmosClient;
    private readonly Container _container;
    private readonly ILogger<CosmosDbService<T>> _logger;
    
    public CosmosDbService(
        CosmosClient cosmosClient,
        IConfiguration configuration,
        ILogger<CosmosDbService<T>> logger)
    {
        _cosmosClient = cosmosClient;
        _logger = logger;
        
        var databaseName = configuration["CosmosDb:DatabaseName"];
        var containerName = configuration[$"CosmosDb:Containers:{typeof(T).Name}"];
        
        _container = _cosmosClient.GetContainer(databaseName, containerName);
    }
    
    public async Task<T> GetAsync(string id, string partitionKey)
    {
        try
        {
            var response = await _container.ReadItemAsync<T>(
                id,
                new PartitionKey(partitionKey));
            
            return response.Resource;
        }
        catch (CosmosException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
        {
            return default;
        }
    }
    
    public async Task<IEnumerable<T>> QueryAsync(
        string query,
        Dictionary<string, object>? parameters = null)
    {
        var queryDefinition = new QueryDefinition(query);
        
        if (parameters != null)
        {
            foreach (var param in parameters)
            {
                queryDefinition.WithParameter($"@{param.Key}", param.Value);
            }
        }
        
        var results = new List<T>();
        using var iterator = _container.GetItemQueryIterator<T>(queryDefinition);
        
        while (iterator.HasMoreResults)
        {
            var response = await iterator.ReadNextAsync();
            results.AddRange(response);
            
            // Log RU consumption
            _logger.LogDebug($"Query consumed {response.RequestCharge} RUs");
        }
        
        return results;
    }
    
    public async Task<PagedResult<T>> QueryPagedAsync(
        Expression<Func<T, bool>> predicate,
        int pageSize,
        string? continuationToken = null)
    {
        var queryable = _container.GetItemLinqQueryable<T>(
            requestOptions: new QueryRequestOptions
            {
                MaxItemCount = pageSize
            },
            continuationToken: continuationToken)
            .Where(predicate);
        
        var iterator = queryable.ToFeedIterator();
        var response = await iterator.ReadNextAsync();
        
        return new PagedResult<T>
        {
            Items = response.Resource,
            ContinuationToken = response.ContinuationToken,
            RequestCharge = response.RequestCharge
        };
    }
    
    public async Task<T> CreateAsync(T item)
    {
        var response = await _container.CreateItemAsync(
            item,
            new PartitionKey(item.PartitionKey));
        
        _logger.LogInformation($"Created item with {response.RequestCharge} RUs");
        
        return response.Resource;
    }
    
    public async Task<T> UpsertAsync(T item)
    {
        var response = await _container.UpsertItemAsync(
            item,
            new PartitionKey(item.PartitionKey));
        
        return response.Resource;
    }
    
    public async Task<bool> DeleteAsync(string id, string partitionKey)
    {
        try
        {
            await _container.DeleteItemAsync<T>(
                id,
                new PartitionKey(partitionKey));
            return true;
        }
        catch (CosmosException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
        {
            return false;
        }
    }
    
    // Bulk operations for performance
    public async Task<BulkOperationResponse<T>> BulkCreateAsync(IEnumerable<T> items)
    {
        var tasks = items.Select(item =>
            _container.CreateItemAsync(item, new PartitionKey(item.PartitionKey)))
            .ToList();
        
        var responses = await Task.WhenAll(tasks);
        
        var totalRUs = responses.Sum(r => r.RequestCharge);
        var successCount = responses.Count(r => r.StatusCode == HttpStatusCode.Created);
        
        return new BulkOperationResponse<T>
        {
            SuccessCount = successCount,
            FailureCount = responses.Length - successCount,
            TotalRequestCharge = totalRUs
        };
    }
    
    // Change feed processor for real-time updates
    public async Task StartChangeFeedProcessorAsync(
        string processorName,
        Func<IReadOnlyCollection<T>, CancellationToken, Task> handleChanges)
    {
        var leaseContainer = _cosmosClient.GetContainer(
            _container.Database.Id,
            $"{_container.Id}-leases");
        
        var processor = _container
            .GetChangeFeedProcessorBuilder<T>(processorName, handleChanges)
            .WithInstanceName(Environment.MachineName)
            .WithLeaseContainer(leaseContainer)
            .WithStartTime(DateTime.UtcNow.AddMinutes(-5))
            .Build();
        
        await processor.StartAsync();
    }
}
```

### 4. Azure FunctionsIN PROGRESS
```csharp
// Functions/OrderProcessingFunction.cs
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;

public class OrderProcessingFunction
{
    private readonly IOrderService _orderService;
    private readonly ILogger<OrderProcessingFunction> _logger;
    
    public OrderProcessingFunction(
        IOrderService orderService,
        ILogger<OrderProcessingFunction> logger)
    {
        _orderService = orderService;
        _logger = logger;
    }
    
    // HTTP Trigger
    [Function("ProcessOrder")]
    public async Task<HttpResponseData> ProcessOrderHttp(
        [HttpTrigger(AuthorizationLevel.Function, "post", Route = "orders/process")] 
        HttpRequestData req)
    {
        _logger.LogInformation("Processing order via HTTP trigger");
        
        var order = await req.ReadFromJsonAsync<Order>();
        
        if (order == null)
        {
            var badRequest = req.CreateResponse(HttpStatusCode.BadRequest);
            await badRequest.WriteStringAsync("Invalid order data");
            return badRequest;
        }
        
        var result = await _orderService.ProcessOrderAsync(order);
        
        var response = req.CreateResponse(HttpStatusCode.OK);
        await response.WriteAsJsonAsync(result);
        
        return response;
    }
    
    // Service Bus Trigger
    [Function("ProcessOrderQueue")]
    public async Task ProcessOrderQueue(
        [ServiceBusTrigger("orders", Connection = "ServiceBusConnection")] 
        Order order,
        FunctionContext context)
    {
        var logger = context.GetLogger("ProcessOrderQueue");
        logger.LogInformation($"Processing order {order.Id} from Service Bus");
        
        try
        {
            await _orderService.ProcessOrderAsync(order);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, $"Failed to process order {order.Id}");
            throw; // Message will be retried or moved to DLQ
        }
    }
    
    // Cosmos DB Trigger
    [Function("OrderChangeFeed")]
    public async Task ProcessOrderChanges(
        [CosmosDBTrigger(
            databaseName: "OrderDb",
            containerName: "Orders",
            Connection = "CosmosDBConnection",
            LeaseContainerName = "leases",
            CreateLeaseContainerIfNotExists = true)]
        IReadOnlyList<Order> orders)
    {
        if (orders != null && orders.Count > 0)
        {
            _logger.LogInformation($"Processing {orders.Count} order changes");
            
            foreach (var order in orders)
            {
                await _orderService.HandleOrderChangeAsync(order);
            }
        }
    }
    
    // Timer Trigger
    [Function("DailyOrderReport")]
    public async Task GenerateDailyReport(
        [TimerTrigger("0 0 2 * * *")] TimerInfo timerInfo) // 2 AM daily
    {
        _logger.LogInformation($"Generating daily report at: {DateTime.UtcNow}");
        
        var report = await _orderService.GenerateDailyReportAsync(DateTime.UtcNow.AddDays(-1));
        
        // Send report via email or store in blob
        await SendReportAsync(report);
    }
    
    // Durable Functions Orchestration
    [Function("OrderOrchestrator")]
    public async Task<OrderResult> RunOrchestrator(
        [OrchestrationTrigger] TaskOrchestrationContext context)
    {
        var order = context.GetInput<Order>();
        
        // Step 1: Validate order
        var isValid = await context.CallActivityAsync<bool>("ValidateOrder", order);
        if (!isValid)
        {
            return new OrderResult { Success = false, Message = "Invalid order" };
        }
        
        // Step 2: Check inventory (with retry)
        var retryOptions = new TaskOptions
        {
            Retry = new RetryPolicy(
                maxNumberOfAttempts: 3,
                firstRetryInterval: TimeSpan.FromSeconds(5))
        };
        
        var inventoryAvailable = await context.CallActivityAsync<bool>(
            "CheckInventory", order, retryOptions);
        
        if (!inventoryAvailable)
        {
            return new OrderResult { Success = false, Message = "Insufficient inventory" };
        }
        
        // Step 3: Process payment
        var paymentResult = await context.CallActivityAsync<PaymentResult>(
            "ProcessPayment", order);
        
        if (!paymentResult.Success)
        {
            // Compensate: Release inventory
            await context.CallActivityAsync("ReleaseInventory", order);
            return new OrderResult { Success = false, Message = "Payment failed" };
        }
        
        // Step 4: Ship order
        await context.CallActivityAsync("ShipOrder", order);
        
        return new OrderResult 
        { 
            Success = true, 
            Message = "Order processed successfully",
            OrderId = order.Id
        };
    }
}

// Program.cs for Azure Functions
var host = new HostBuilder()
    .ConfigureFunctionsWorkerDefaults()
    .ConfigureServices((context, services) =>
    {
        // Add Application Insights
        services.AddApplicationInsightsTelemetryWorkerService();
        services.ConfigureFunctionsApplicationInsights();
        
        // Add Azure services
        services.AddSingleton<CosmosClient>(sp =>
        {
            return new CosmosClient(
                context.Configuration["CosmosDb:AccountEndpoint"],
                new DefaultAzureCredential());
        });
        
        // Add business services
        services.AddScoped<IOrderService, OrderService>();
    })
    .Build();

host.Run();
```

### 5. Azure Service Bus
```csharp
// Services/AzureServiceBusService.cs
using Azure.Messaging.ServiceBus;

public class AzureServiceBusService : IMessageBusService
{
    private readonly ServiceBusClient _client;
    private readonly ILogger<AzureServiceBusService> _logger;
    private readonly Dictionary<string, ServiceBusProcessor> _processors = new();
    
    public AzureServiceBusService(
        ServiceBusClient client,
        ILogger<AzureServiceBusService> logger)
    {
        _client = client;
        _logger = logger;
    }
    
    public async Task SendMessageAsync<T>(T message, string queueOrTopicName) where T : class
    {
        await using var sender = _client.CreateSender(queueOrTopicName);
        
        var serviceBusMessage = new ServiceBusMessage(JsonSerializer.Serialize(message))
        {
            ContentType = "application/json",
            MessageId = Guid.NewGuid().ToString(),
            Subject = typeof(T).Name,
            ApplicationProperties =
            {
                ["MessageType"] = typeof(T).FullName,
                ["Timestamp"] = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
            }
        };
        
        await sender.SendMessageAsync(serviceBusMessage);
        _logger.LogInformation($"Message sent to {queueOrTopicName}");
    }
    
    public async Task SendBatchAsync<T>(IEnumerable<T> messages, string queueOrTopicName) where T : class
    {
        await using var sender = _client.CreateSender(queueOrTopicName);
        
        var messageBatch = await sender.CreateMessageBatchAsync();
        
        foreach (var message in messages)
        {
            var serviceBusMessage = new ServiceBusMessage(JsonSerializer.Serialize(message));
            
            if (!messageBatch.TryAddMessage(serviceBusMessage))
            {
                // Send current batch and create new one
                await sender.SendMessagesAsync(messageBatch);
                messageBatch.Dispose();
                messageBatch = await sender.CreateMessageBatchAsync();
                messageBatch.TryAddMessage(serviceBusMessage);
            }
        }
        
        if (messageBatch.Count > 0)
        {
            await sender.SendMessagesAsync(messageBatch);
        }
    }
    
    public async Task RegisterHandlerAsync<T>(
        string queueOrTopicName,
        Func<T, CancellationToken, Task> handler,
        string? subscriptionName = null) where T : class
    {
        var processorKey = $"{queueOrTopicName}_{subscriptionName ?? "default"}";
        
        if (_processors.ContainsKey(processorKey))
        {
            throw new InvalidOperationException($"Handler already registered for {processorKey}");
        }
        
        ServiceBusProcessor processor;
        
        if (string.IsNullOrEmpty(subscriptionName))
        {
            // Queue processor
            processor = _client.CreateProcessor(queueOrTopicName, new ServiceBusProcessorOptions
            {
                AutoCompleteMessages = false,
                MaxConcurrentCalls = 10,
                PrefetchCount = 20
            });
        }
        else
        {
            // Topic subscription processor
            processor = _client.CreateProcessor(queueOrTopicName, subscriptionName, new ServiceBusProcessorOptions
            {
                AutoCompleteMessages = false,
                MaxConcurrentCalls = 10,
                PrefetchCount = 20
            });
        }
        
        processor.ProcessMessageAsync += async args =>
        {
            try
            {
                var body = args.Message.Body.ToString();
                var message = JsonSerializer.Deserialize<T>(body);
                
                await handler(message!, args.CancellationToken);
                await args.CompleteMessageAsync(args.Message);
                
                _logger.LogInformation($"Message processed from {queueOrTopicName}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error processing message from {queueOrTopicName}");
                
                // Dead letter the message after max retries
                if (args.Message.DeliveryCount >= 5)
                {
                    await args.DeadLetterMessageAsync(args.Message, ex.Message);
                }
                else
                {
                    await args.AbandonMessageAsync(args.Message);
                }
            }
        };
        
        processor.ProcessErrorAsync += args =>
        {
            _logger.LogError(args.Exception, $"Error in Service Bus processor for {queueOrTopicName}");
            return Task.CompletedTask;
        };
        
        await processor.StartProcessingAsync();
        _processors[processorKey] = processor;
    }
    
    public async Task StopAllProcessorsAsync()
    {
        foreach (var processor in _processors.Values)
        {
            await processor.StopProcessingAsync();
            await processor.DisposeAsync();
        }
        _processors.Clear();
    }
}
```

## Application Insights

### 
```csharp
// Telemetry/CustomTelemetryInitializer.cs
public class CustomTelemetryInitializer : ITelemetryInitializer
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    
    public CustomTelemetryInitializer(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }
    
    public void Initialize(ITelemetry telemetry)
    {
        var httpContext = _httpContextAccessor.HttpContext;
        
        if (httpContext != null)
        {
            // Add custom properties
            telemetry.Context.GlobalProperties["Environment"] = 
                Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Unknown";
            
            if (httpContext.User.Identity?.IsAuthenticated == true)
            {
                telemetry.Context.User.Id = httpContext.User.FindFirst("sub")?.Value;
                telemetry.Context.User.AuthenticatedUserId = httpContext.User.Identity.Name;
            }
            
            // Add correlation ID
            if (httpContext.Request.Headers.TryGetValue("X-Correlation-ID", out var correlationId))
            {
                telemetry.Context.Operation.ParentId = correlationId;
            }
        }
        
        // Add version info
        telemetry.Context.Component.Version = Assembly.GetExecutingAssembly()
            .GetCustomAttribute<AssemblyFileVersionAttribute>()?.Version;
    }
}

// Services/ApplicationInsightsService.cs
public class ApplicationInsightsService
{
    private readonly TelemetryClient _telemetryClient;
    
    public ApplicationInsightsService(TelemetryClient telemetryClient)
    {
        _telemetryClient = telemetryClient;
    }
    
    public void TrackCustomEvent(string eventName, Dictionary<string, string>? properties = null, Dictionary<string, double>? metrics = null)
    {
        _telemetryClient.TrackEvent(eventName, properties, metrics);
    }
    
    public void TrackCustomMetric(string metricName, double value, Dictionary<string, string>? properties = null)
    {
        _telemetryClient.GetMetric(metricName).TrackValue(value, properties?.Values.ToArray());
    }
    
    public IOperationHolder<RequestTelemetry> StartOperation(string operationName)
    {
        return _telemetryClient.StartOperation<RequestTelemetry>(operationName);
    }
    
    public void TrackDependency(string dependencyName, string commandName, DateTimeOffset startTime, TimeSpan duration, bool success)
    {
        _telemetryClient.TrackDependency(dependencyName, commandName, startTime, duration, success);
    }
}
```

## SUCCESS
```markdown
# AzureSUCCESS

## SUCCESS
[OK] SUCCESS: DefaultAzureCredential
[OK] Storage: Blob Storage
[OK] Cosmos DB: Change Feed
[OK] Service Bus: 
[OK] Functions: Durable Functions
[OK] Application Insights: 

## 
- : <100ms (Managed Identity)
- Blob Upload: 100MB/s ()
- Cosmos DB RU: 40%
- Service Bus: 10,000 msg/s

## 
- Storage: 30%
- Cosmos DB: 50%
- Functions: Consumption Plan

## 
1. Managed Identity
2. Azure Monitor
3. Cost Management
4. Disaster Recovery
```

## 
- ****: 
- ****: Azure

---
*Microsoft Azure*