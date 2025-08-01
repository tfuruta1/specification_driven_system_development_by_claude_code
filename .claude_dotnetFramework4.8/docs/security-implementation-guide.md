# セキュリティ実装ガイド

## 概要

.NET Framework 4.8 Windows Forms エンタープライズアプリケーションにおけるセキュリティ実装のベストプラクティスと具体的な実装例を提供します。

## 1. 認証（Authentication）

### 1.1 Windows認証

```csharp
public class WindowsAuthenticationService : IAuthenticationService
{
    private readonly ILogger<WindowsAuthenticationService> _logger;
    private readonly IUserRepository _userRepository;
    
    public async Task<AuthenticationResult> AuthenticateAsync()
    {
        try
        {
            // Windows認証情報の取得
            var windowsIdentity = WindowsIdentity.GetCurrent();
            
            if (windowsIdentity == null || !windowsIdentity.IsAuthenticated)
            {
                return AuthenticationResult.Failed("Windows認証に失敗しました");
            }
            
            // ドメイン\ユーザー名の解析
            var domainUser = windowsIdentity.Name; // DOMAIN\username
            var parts = domainUser.Split('\\');
            var domain = parts.Length > 1 ? parts[0] : string.Empty;
            var username = parts.Length > 1 ? parts[1] : parts[0];
            
            // Active Directoryから追加情報取得
            var adUser = await GetActiveDirectoryUserAsync(username, domain);
            
            // アプリケーションユーザーの取得または作成
            var appUser = await _userRepository.GetOrCreateUserAsync(new CreateUserDto
            {
                Username = username,
                Domain = domain,
                Email = adUser?.Email,
                FullName = adUser?.DisplayName,
                Department = adUser?.Department
            });
            
            // セキュリティトークンの生成
            var token = GenerateSecurityToken(appUser);
            
            _logger.LogInformation("ユーザー {Username} が認証されました", username);
            
            return AuthenticationResult.Success(appUser, token);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "認証処理中にエラーが発生しました");
            return AuthenticationResult.Failed("認証処理に失敗しました");
        }
    }
    
    private async Task<ActiveDirectoryUser> GetActiveDirectoryUserAsync(
        string username, string domain)
    {
        using (var context = new PrincipalContext(ContextType.Domain, domain))
        using (var user = UserPrincipal.FindByIdentity(context, username))
        {
            if (user == null) return null;
            
            return new ActiveDirectoryUser
            {
                Username = user.SamAccountName,
                DisplayName = user.DisplayName,
                Email = user.EmailAddress,
                Department = user.GetProperty("department"),
                Groups = user.GetGroups().Select(g => g.Name).ToList()
            };
        }
    }
    
    private SecurityToken GenerateSecurityToken(User user)
    {
        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Name, user.Username),
            new Claim(ClaimTypes.Email, user.Email ?? string.Empty),
            new Claim("Department", user.Department ?? string.Empty)
        };
        
        // ロールの追加
        foreach (var role in user.Roles)
        {
            claims.Add(new Claim(ClaimTypes.Role, role.Name));
        }
        
        var identity = new ClaimsIdentity(claims, "Windows");
        var principal = new ClaimsPrincipal(identity);
        
        return new SecurityToken
        {
            Principal = principal,
            IssuedAt = DateTime.UtcNow,
            ExpiresAt = DateTime.UtcNow.AddHours(8)
        };
    }
}
```

### 1.2 フォーム認証

```csharp
public partial class LoginForm : Form
{
    private readonly IAuthenticationService _authService;
    private readonly IPasswordHasher _passwordHasher;
    private int _failedAttempts = 0;
    private DateTime? _lockoutEndTime;
    
    public LoginForm(IAuthenticationService authService)
    {
        InitializeComponent();
        _authService = authService;
        _passwordHasher = new Argon2PasswordHasher();
    }
    
    private async void btnLogin_Click(object sender, EventArgs e)
    {
        // アカウントロックアウトチェック
        if (_lockoutEndTime.HasValue && _lockoutEndTime > DateTime.Now)
        {
            var remainingTime = _lockoutEndTime.Value - DateTime.Now;
            ShowError($"アカウントがロックされています。{remainingTime.TotalMinutes:F0}分後に再試行してください。");
            return;
        }
        
        // 入力検証
        if (!ValidateInput())
        {
            return;
        }
        
        try
        {
            SetUIState(false);
            
            var result = await _authService.AuthenticateAsync(
                txtUsername.Text, 
                txtPassword.Text);
            
            if (result.Success)
            {
                _failedAttempts = 0;
                AuditLog.LogSuccessfulLogin(txtUsername.Text);
                
                // メインフォームを開く
                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            else
            {
                _failedAttempts++;
                AuditLog.LogFailedLogin(txtUsername.Text, result.ErrorMessage);
                
                if (_failedAttempts >= 5)
                {
                    _lockoutEndTime = DateTime.Now.AddMinutes(15);
                    ShowError("ログイン試行回数が上限に達しました。15分後に再試行してください。");
                }
                else
                {
                    ShowError($"ログインに失敗しました。（残り{5 - _failedAttempts}回）");
                }
                
                // パスワードフィールドをクリア
                txtPassword.Clear();
                txtPassword.Focus();
            }
        }
        finally
        {
            SetUIState(true);
        }
    }
    
    private bool ValidateInput()
    {
        var errors = new List<string>();
        
        if (string.IsNullOrWhiteSpace(txtUsername.Text))
        {
            errors.Add("ユーザー名を入力してください。");
        }
        
        if (string.IsNullOrWhiteSpace(txtPassword.Text))
        {
            errors.Add("パスワードを入力してください。");
        }
        
        // SQLインジェクション対策
        if (ContainsSqlInjectionPattern(txtUsername.Text) || 
            ContainsSqlInjectionPattern(txtPassword.Text))
        {
            errors.Add("不正な文字が含まれています。");
            AuditLog.LogSecurityAlert("SQLインジェクション試行の可能性", txtUsername.Text);
        }
        
        if (errors.Any())
        {
            ShowError(string.Join("\n", errors));
            return false;
        }
        
        return true;
    }
    
    private bool ContainsSqlInjectionPattern(string input)
    {
        var patterns = new[]
        {
            @"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|EXECUTE)\b)",
            @"(--|;|'|""|\/\*|\*\/)",
            @"(xp_|sp_|@@)"
        };
        
        return patterns.Any(pattern => 
            Regex.IsMatch(input, pattern, RegexOptions.IgnoreCase));
    }
}
```

## 2. 認可（Authorization）

### 2.1 ロールベースアクセス制御（RBAC）

```csharp
// 権限属性の定義
[AttributeUsage(AttributeTargets.Method | AttributeTargets.Class)]
public class RequirePermissionAttribute : Attribute
{
    public string Permission { get; }
    public string[] Roles { get; }
    
    public RequirePermissionAttribute(string permission, params string[] roles)
    {
        Permission = permission;
        Roles = roles;
    }
}

// 権限チェックサービス
public class AuthorizationService : IAuthorizationService
{
    private readonly IUserContext _userContext;
    private readonly IPermissionRepository _permissionRepository;
    
    public async Task<bool> AuthorizeAsync(string permission)
    {
        var user = _userContext.CurrentUser;
        if (user == null) return false;
        
        // スーパーユーザーチェック
        if (user.Roles.Any(r => r.Name == "Administrator"))
        {
            return true;
        }
        
        // ロールベースの権限チェック
        var userPermissions = await _permissionRepository
            .GetPermissionsByRolesAsync(user.Roles.Select(r => r.Id));
            
        return userPermissions.Any(p => p.Code == permission);
    }
    
    public async Task<bool> AuthorizeAsync(RequirePermissionAttribute attribute)
    {
        // 権限チェック
        if (!string.IsNullOrEmpty(attribute.Permission))
        {
            if (!await AuthorizeAsync(attribute.Permission))
            {
                return false;
            }
        }
        
        // ロールチェック
        if (attribute.Roles?.Any() == true)
        {
            var user = _userContext.CurrentUser;
            if (!user.Roles.Any(r => attribute.Roles.Contains(r.Name)))
            {
                return false;
            }
        }
        
        return true;
    }
}

// フォームでの権限チェック
public partial class CustomerManagementForm : SecureForm
{
    protected override void OnLoad(EventArgs e)
    {
        base.OnLoad(e);
        
        // 権限に基づくUI制御
        btnAddCustomer.Visible = HasPermission("customer.create");
        btnEditCustomer.Visible = HasPermission("customer.update");
        btnDeleteCustomer.Visible = HasPermission("customer.delete");
        
        // 読み取り専用モード
        if (!HasPermission("customer.update"))
        {
            SetReadOnlyMode(true);
        }
    }
    
    [RequirePermission("customer.delete", "Administrator", "Manager")]
    private async void btnDeleteCustomer_Click(object sender, EventArgs e)
    {
        // 権限チェックは基底クラスで自動実行
        await DeleteSelectedCustomerAsync();
    }
}
```

### 2.2 データレベルセキュリティ

```csharp
public class SecureCustomerRepository : ICustomerRepository
{
    private readonly IDbContext _context;
    private readonly IUserContext _userContext;
    
    public async Task<IEnumerable<Customer>> GetCustomersAsync()
    {
        var query = _context.Customers.AsQueryable();
        
        // データレベルのフィルタリング
        var currentUser = _userContext.CurrentUser;
        
        // 部門レベルの制限
        if (currentUser.Roles.All(r => r.Name != "Administrator"))
        {
            if (currentUser.Department != null)
            {
                query = query.Where(c => c.Department == currentUser.Department);
            }
        }
        
        // 地域レベルの制限
        if (currentUser.AssignedRegions?.Any() == true)
        {
            query = query.Where(c => currentUser.AssignedRegions.Contains(c.Region));
        }
        
        // 機密レベルの制限
        query = query.Where(c => c.SecurityLevel <= currentUser.SecurityClearance);
        
        return await query.ToListAsync();
    }
    
    public async Task<Customer> GetCustomerByIdAsync(int id)
    {
        var customer = await _context.Customers.FindAsync(id);
        
        if (customer == null) return null;
        
        // アクセス権限チェック
        if (!await CanAccessCustomerAsync(customer))
        {
            throw new UnauthorizedAccessException(
                "このデータへのアクセス権限がありません。");
        }
        
        return customer;
    }
    
    private async Task<bool> CanAccessCustomerAsync(Customer customer)
    {
        var currentUser = _userContext.CurrentUser;
        
        // 管理者は全データアクセス可能
        if (currentUser.HasRole("Administrator")) return true;
        
        // 部門チェック
        if (customer.Department != currentUser.Department) return false;
        
        // セキュリティレベルチェック
        if (customer.SecurityLevel > currentUser.SecurityClearance) return false;
        
        // カスタムルール（例：担当者のみアクセス可能）
        if (customer.AssignedTo != null && customer.AssignedTo != currentUser.Id)
        {
            return currentUser.HasPermission("customer.view.all");
        }
        
        return true;
    }
}
```

## 3. データ暗号化

### 3.1 保存データの暗号化

```csharp
public class EncryptionService : IEncryptionService
{
    private readonly byte[] _key;
    private readonly byte[] _iv;
    
    public EncryptionService(IConfiguration configuration)
    {
        // キーの安全な管理（Windows Data Protection APIを使用）
        var protectedKey = configuration["Encryption:Key"];
        _key = ProtectedData.Unprotect(
            Convert.FromBase64String(protectedKey),
            null,
            DataProtectionScope.LocalMachine);
            
        _iv = Convert.FromBase64String(configuration["Encryption:IV"]);
    }
    
    public string Encrypt(string plainText)
    {
        if (string.IsNullOrEmpty(plainText)) return plainText;
        
        using (var aes = Aes.Create())
        {
            aes.Key = _key;
            aes.IV = _iv;
            aes.Mode = CipherMode.CBC;
            aes.Padding = PaddingMode.PKCS7;
            
            using (var encryptor = aes.CreateEncryptor())
            using (var ms = new MemoryStream())
            {
                using (var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
                using (var sw = new StreamWriter(cs))
                {
                    sw.Write(plainText);
                }
                
                return Convert.ToBase64String(ms.ToArray());
            }
        }
    }
    
    public string Decrypt(string cipherText)
    {
        if (string.IsNullOrEmpty(cipherText)) return cipherText;
        
        try
        {
            var buffer = Convert.FromBase64String(cipherText);
            
            using (var aes = Aes.Create())
            {
                aes.Key = _key;
                aes.IV = _iv;
                aes.Mode = CipherMode.CBC;
                aes.Padding = PaddingMode.PKCS7;
                
                using (var decryptor = aes.CreateDecryptor())
                using (var ms = new MemoryStream(buffer))
                using (var cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read))
                using (var sr = new StreamReader(cs))
                {
                    return sr.ReadToEnd();
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "復号化エラー");
            throw new CryptographicException("データの復号化に失敗しました。", ex);
        }
    }
}

// Entity Frameworkでの透過的暗号化
public class EncryptedStringConverter : ValueConverter<string, string>
{
    private readonly IEncryptionService _encryptionService;
    
    public EncryptedStringConverter(IEncryptionService encryptionService)
        : base(
            v => encryptionService.Encrypt(v),
            v => encryptionService.Decrypt(v))
    {
        _encryptionService = encryptionService;
    }
}

// モデル設定
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    var encryptionConverter = new EncryptedStringConverter(_encryptionService);
    
    // 機密フィールドの暗号化
    modelBuilder.Entity<Customer>()
        .Property(e => e.CreditCardNumber)
        .HasConversion(encryptionConverter);
        
    modelBuilder.Entity<Customer>()
        .Property(e => e.SocialSecurityNumber)
        .HasConversion(encryptionConverter);
}
```

### 3.2 通信の暗号化

```csharp
public class SecureApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ICertificateService _certService;
    
    public SecureApiClient(ICertificateService certService)
    {
        _certService = certService;
        
        var handler = new HttpClientHandler();
        
        // SSL/TLS設定
        handler.SslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13;
        
        // サーバー証明書の検証
        handler.ServerCertificateCustomValidationCallback = ValidateServerCertificate;
        
        // クライアント証明書の設定
        var clientCert = _certService.GetClientCertificate();
        if (clientCert != null)
        {
            handler.ClientCertificates.Add(clientCert);
        }
        
        _httpClient = new HttpClient(handler);
    }
    
    private bool ValidateServerCertificate(
        HttpRequestMessage request,
        X509Certificate2 certificate,
        X509Chain chain,
        SslPolicyErrors sslPolicyErrors)
    {
        // 開発環境では自己署名証明書を許可
        if (Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") == "Development")
        {
            return true;
        }
        
        // 証明書チェーンの検証
        if (sslPolicyErrors == SslPolicyErrors.None)
        {
            return true;
        }
        
        // 既知の証明書のピンニング
        var allowedThumbprints = new[]
        {
            "A1B2C3D4E5F6...", // 本番サーバーの証明書サムプリント
            "F6E5D4C3B2A1..."  // バックアップサーバーの証明書サムプリント
        };
        
        return allowedThumbprints.Contains(certificate.Thumbprint);
    }
    
    public async Task<T> SecurePostAsync<T>(string endpoint, object data)
    {
        // リクエストの署名
        var signature = GenerateRequestSignature(data);
        _httpClient.DefaultRequestHeaders.Add("X-Signature", signature);
        
        // データの暗号化（必要に応じて）
        var encryptedData = _encryptionService.EncryptObject(data);
        
        var response = await _httpClient.PostAsJsonAsync(endpoint, encryptedData);
        response.EnsureSuccessStatusCode();
        
        var responseData = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<T>(responseData);
    }
}
```

## 4. 入力検証とサニタイゼーション

### 4.1 入力検証

```csharp
public class InputValidator
{
    private readonly Dictionary<string, List<IValidationRule>> _rules;
    
    public InputValidator()
    {
        _rules = new Dictionary<string, List<IValidationRule>>();
        ConfigureRules();
    }
    
    private void ConfigureRules()
    {
        // ユーザー名の検証ルール
        AddRule("Username", new RequiredRule());
        AddRule("Username", new LengthRule(3, 50));
        AddRule("Username", new RegexRule(@"^[a-zA-Z0-9_\-\.]+$", 
            "ユーザー名には英数字、アンダースコア、ハイフン、ピリオドのみ使用できます。"));
        AddRule("Username", new NoSqlInjectionRule());
        
        // メールアドレスの検証ルール
        AddRule("Email", new RequiredRule());
        AddRule("Email", new EmailRule());
        AddRule("Email", new LengthRule(5, 255));
        
        // パスワードの検証ルール
        AddRule("Password", new RequiredRule());
        AddRule("Password", new PasswordStrengthRule());
        AddRule("Password", new NoCommonPasswordRule());
        
        // 金額の検証ルール
        AddRule("Amount", new RangeRule<decimal>(0, 999999999.99m));
        AddRule("Amount", new DecimalPlacesRule(2));
    }
    
    public ValidationResult Validate(string fieldName, object value)
    {
        if (!_rules.ContainsKey(fieldName))
        {
            return ValidationResult.Success();
        }
        
        var errors = new List<string>();
        
        foreach (var rule in _rules[fieldName])
        {
            if (!rule.Validate(value, out string error))
            {
                errors.Add(error);
            }
        }
        
        return errors.Any() 
            ? ValidationResult.Failed(errors) 
            : ValidationResult.Success();
    }
}

// カスタム検証ルール
public class NoSqlInjectionRule : IValidationRule
{
    private readonly string[] _dangerousPatterns = new[]
    {
        @"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|EXECUTE)\b)",
        @"(--|;|'|""|\/\*|\*\/)",
        @"(xp_|sp_|@@)",
        @"(\bOR\b.*=.*)",
        @"(\bAND\b.*=.*)"
    };
    
    public bool Validate(object value, out string error)
    {
        error = null;
        var input = value?.ToString() ?? string.Empty;
        
        foreach (var pattern in _dangerousPatterns)
        {
            if (Regex.IsMatch(input, pattern, RegexOptions.IgnoreCase))
            {
                error = "入力に不正な文字列が含まれています。";
                
                // セキュリティログに記録
                SecurityLogger.LogPotentialSqlInjection(input, pattern);
                
                return false;
            }
        }
        
        return true;
    }
}

public class PasswordStrengthRule : IValidationRule
{
    public bool Validate(object value, out string error)
    {
        error = null;
        var password = value?.ToString() ?? string.Empty;
        
        var requirements = new List<string>();
        
        if (password.Length < 8)
            requirements.Add("8文字以上");
            
        if (!Regex.IsMatch(password, @"[A-Z]"))
            requirements.Add("大文字を含む");
            
        if (!Regex.IsMatch(password, @"[a-z]"))
            requirements.Add("小文字を含む");
            
        if (!Regex.IsMatch(password, @"[0-9]"))
            requirements.Add("数字を含む");
            
        if (!Regex.IsMatch(password, @"[!@#$%^&*(),.?"":{}|<>]"))
            requirements.Add("記号を含む");
            
        if (requirements.Any())
        {
            error = $"パスワードは次の条件を満たす必要があります: {string.Join("、", requirements)}";
            return false;
        }
        
        return true;
    }
}
```

### 4.2 出力エンコーディング

```csharp
public static class SecurityEncoder
{
    // HTMLエンコーディング
    public static string HtmlEncode(string input)
    {
        if (string.IsNullOrEmpty(input)) return input;
        
        return System.Net.WebUtility.HtmlEncode(input);
    }
    
    // URLエンコーディング
    public static string UrlEncode(string input)
    {
        if (string.IsNullOrEmpty(input)) return input;
        
        return Uri.EscapeDataString(input);
    }
    
    // ファイル名のサニタイゼーション
    public static string SanitizeFileName(string fileName)
    {
        if (string.IsNullOrEmpty(fileName)) return fileName;
        
        // 危険な文字を除去
        var invalidChars = Path.GetInvalidFileNameChars();
        var sanitized = string.Join("_", fileName.Split(invalidChars));
        
        // パストラバーサル対策
        sanitized = sanitized.Replace("..", "");
        sanitized = sanitized.Replace("/", "");
        sanitized = sanitized.Replace("\\", "");
        
        // 長さ制限
        if (sanitized.Length > 255)
        {
            var extension = Path.GetExtension(sanitized);
            var nameWithoutExtension = Path.GetFileNameWithoutExtension(sanitized);
            sanitized = nameWithoutExtension.Substring(0, 255 - extension.Length) + extension;
        }
        
        return sanitized;
    }
    
    // SQLパラメータのサニタイゼーション（パラメータ化クエリを推奨）
    public static string SanitizeSqlIdentifier(string identifier)
    {
        if (string.IsNullOrEmpty(identifier)) return identifier;
        
        // 英数字とアンダースコアのみ許可
        if (!Regex.IsMatch(identifier, @"^[a-zA-Z0-9_]+$"))
        {
            throw new ArgumentException("無効な識別子です。");
        }
        
        // 予約語チェック
        var reservedWords = new[] { "SELECT", "INSERT", "UPDATE", "DELETE", "DROP" };
        if (reservedWords.Contains(identifier.ToUpper()))
        {
            throw new ArgumentException("予約語は使用できません。");
        }
        
        return identifier;
    }
}
```

## 5. 監査ログ

### 5.1 監査ログの実装

```csharp
public class AuditLogger : IAuditLogger
{
    private readonly IDbContext _context;
    private readonly IUserContext _userContext;
    private readonly IConfiguration _configuration;
    
    public async Task LogAsync(AuditEvent auditEvent)
    {
        var entry = new AuditLogEntry
        {
            EventType = auditEvent.EventType,
            EntityType = auditEvent.EntityType,
            EntityId = auditEvent.EntityId,
            Action = auditEvent.Action,
            Username = _userContext.CurrentUser?.Username ?? "System",
            UserId = _userContext.CurrentUser?.Id,
            Timestamp = DateTime.UtcNow,
            IpAddress = GetClientIpAddress(),
            MachineName = Environment.MachineName,
            ApplicationName = _configuration["Application:Name"],
            OldValues = JsonSerializer.Serialize(auditEvent.OldValues),
            NewValues = JsonSerializer.Serialize(auditEvent.NewValues),
            AdditionalInfo = JsonSerializer.Serialize(auditEvent.AdditionalInfo)
        };
        
        // 重要度の高いイベントは即座に保存
        if (auditEvent.Severity == AuditSeverity.Critical)
        {
            await _context.AuditLogs.AddAsync(entry);
            await _context.SaveChangesAsync();
            
            // アラート送信
            await SendSecurityAlertAsync(entry);
        }
        else
        {
            // バッチ処理用のキューに追加
            AuditQueue.Enqueue(entry);
        }
    }
    
    // Entity Framework インターセプター
    public class AuditInterceptor : SaveChangesInterceptor
    {
        private readonly IAuditLogger _auditLogger;
        
        public override async ValueTask<InterceptionResult<int>> SavingChangesAsync(
            DbContextEventData eventData,
            InterceptionResult<int> result,
            CancellationToken cancellationToken = default)
        {
            var context = eventData.Context;
            var auditEntries = new List<AuditEvent>();
            
            foreach (var entry in context.ChangeTracker.Entries())
            {
                if (entry.Entity is IAuditable && 
                    entry.State != EntityState.Unchanged)
                {
                    var auditEvent = CreateAuditEvent(entry);
                    auditEntries.Add(auditEvent);
                }
            }
            
            // 監査ログの非同期記録
            foreach (var auditEvent in auditEntries)
            {
                await _auditLogger.LogAsync(auditEvent);
            }
            
            return result;
        }
        
        private AuditEvent CreateAuditEvent(EntityEntry entry)
        {
            var auditEvent = new AuditEvent
            {
                EntityType = entry.Entity.GetType().Name,
                EntityId = GetEntityId(entry.Entity),
                Action = entry.State.ToString()
            };
            
            // 変更前後の値を記録
            if (entry.State == EntityState.Modified)
            {
                auditEvent.OldValues = entry.OriginalValues.Properties
                    .ToDictionary(p => p.Name, p => entry.OriginalValues[p]);
                auditEvent.NewValues = entry.CurrentValues.Properties
                    .ToDictionary(p => p.Name, p => entry.CurrentValues[p]);
            }
            
            return auditEvent;
        }
    }
}
```

### 5.2 セキュリティイベントログ

```csharp
public static class SecurityEventLogger
{
    private static readonly ILogger _logger = LogManager.GetCurrentClassLogger();
    
    public static void LogSuccessfulLogin(string username)
    {
        var logEvent = new LogEventInfo(LogLevel.Info, "Security", "ログイン成功");
        logEvent.Properties["EventType"] = "LOGIN_SUCCESS";
        logEvent.Properties["Username"] = username;
        logEvent.Properties["Timestamp"] = DateTime.UtcNow;
        logEvent.Properties["IpAddress"] = GetClientIpAddress();
        
        _logger.Log(logEvent);
    }
    
    public static void LogFailedLogin(string username, string reason)
    {
        var logEvent = new LogEventInfo(LogLevel.Warn, "Security", "ログイン失敗");
        logEvent.Properties["EventType"] = "LOGIN_FAILED";
        logEvent.Properties["Username"] = username;
        logEvent.Properties["Reason"] = reason;
        logEvent.Properties["Timestamp"] = DateTime.UtcNow;
        logEvent.Properties["IpAddress"] = GetClientIpAddress();
        
        _logger.Log(logEvent);
    }
    
    public static void LogUnauthorizedAccess(string resource, string username)
    {
        var logEvent = new LogEventInfo(LogLevel.Warn, "Security", "不正アクセス試行");
        logEvent.Properties["EventType"] = "UNAUTHORIZED_ACCESS";
        logEvent.Properties["Resource"] = resource;
        logEvent.Properties["Username"] = username;
        logEvent.Properties["Timestamp"] = DateTime.UtcNow;
        
        _logger.Log(logEvent);
        
        // 即座にアラート
        AlertService.SendSecurityAlert(
            $"不正アクセス試行: {username} が {resource} へアクセスを試みました。");
    }
    
    public static void LogDataExport(string entityType, int recordCount, string username)
    {
        var logEvent = new LogEventInfo(LogLevel.Info, "Security", "データエクスポート");
        logEvent.Properties["EventType"] = "DATA_EXPORT";
        logEvent.Properties["EntityType"] = entityType;
        logEvent.Properties["RecordCount"] = recordCount;
        logEvent.Properties["Username"] = username;
        logEvent.Properties["Timestamp"] = DateTime.UtcNow;
        
        _logger.Log(logEvent);
        
        // 大量データエクスポートの監視
        if (recordCount > 10000)
        {
            AlertService.SendSecurityAlert(
                $"大量データエクスポート: {username} が {entityType} {recordCount}件をエクスポート");
        }
    }
}
```

## 6. セキュアな設定管理

### 6.1 設定の暗号化

```csharp
public class SecureConfigurationProvider : ConfigurationProvider
{
    private readonly IDataProtector _protector;
    
    public SecureConfigurationProvider(IDataProtectionProvider dataProtectionProvider)
    {
        _protector = dataProtectionProvider.CreateProtector("AppSettings");
    }
    
    public override void Load()
    {
        var configPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),
            "YourApp",
            "appsettings.encrypted.json");
            
        if (!File.Exists(configPath))
        {
            Data = new Dictionary<string, string>();
            return;
        }
        
        var encryptedJson = File.ReadAllText(configPath);
        var json = _protector.Unprotect(encryptedJson);
        
        Data = JsonSerializer.Deserialize<Dictionary<string, string>>(json);
    }
    
    public void SaveSecurely(Dictionary<string, string> settings)
    {
        var json = JsonSerializer.Serialize(settings);
        var encryptedJson = _protector.Protect(json);
        
        var configPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),
            "YourApp",
            "appsettings.encrypted.json");
            
        Directory.CreateDirectory(Path.GetDirectoryName(configPath));
        File.WriteAllText(configPath, encryptedJson);
        
        // ファイルのアクセス権限を制限
        var fileSecurity = File.GetAccessControl(configPath);
        fileSecurity.SetAccessRuleProtection(true, false);
        
        var currentUser = WindowsIdentity.GetCurrent();
        fileSecurity.SetAccessRule(new FileSystemAccessRule(
            currentUser.User,
            FileSystemRights.Read | FileSystemRights.Write,
            AccessControlType.Allow));
            
        File.SetAccessControl(configPath, fileSecurity);
    }
}
```

## まとめ

エンタープライズアプリケーションのセキュリティ実装において重要なポイント：

1. **多層防御** - 単一の対策に頼らず、複数の防御層を実装
2. **最小権限の原則** - 必要最小限の権限のみを付与
3. **監査証跡** - すべての重要な操作を記録
4. **暗号化** - 保存時と転送時の両方でデータを保護
5. **定期的な更新** - セキュリティパッチと脆弱性対策の継続

これらの実装例を参考に、アプリケーションの要件に応じた適切なセキュリティ対策を実施してください。