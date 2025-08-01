# /legacy-integration - レガシーシステム統合支援コマンド

**Windows XP/2003・既存システム・企業環境統合専用**

## 📋 コマンド概要

.NET Framework 4.0アプリケーションとレガシーシステム、既存企業環境との統合を支援します。COMコンポーネント、ActiveDirectory、レガシーDB、Windows Service、既存メインフレームシステムなどとの完全統合を実現します。

## 🚀 使用方法

### 基本構文
```bash
/legacy-integration [integration_type] [options]
```

### 主要統合タイプ

#### 1. COMコンポーネント統合
```bash
/legacy-integration com_interop [com_type]
```
**COMタイプ**:
- `activex` - ActiveXコントロール統合
- `ole_automation` - OLE Automationサーバー統合
- `typelib` - タイプライブラリインポート
- `early_binding` - 早期バインディング実装

#### 2. ActiveDirectory 統合
```bash
/legacy-integration active_directory [ad_feature]
```
**AD機能**:
- `authentication` - ドメイン認証統合
- `user_management` - ユーザー・グループ管理
- `group_policy` - グループポリシー連携
- `ldap_query` - LDAPクエリ統合

#### 3. レガシーDB統合
```bash
/legacy-integration legacy_database [db_type]
```
**DBタイプ**:
- `sql_server_2000` - SQL Server 2000/2005統合
- `oracle_10g` - Oracle Database 10g/11g統合
- `access_mdb` - Microsoft Access MDB統合
- `dbase_foxpro` - dBASE/FoxPro統合
- `mainframe_db2` - メインフレームDB2統合

#### 4. Windows Service 統合
```bash
/legacy-integration windows_service [service_type]
```
**サービスタイプ**:
- `background_service` - バックグラウンドサービス連携
- `named_pipes` - 名前付きパイプ通信
- `file_watcher` - ファイル監視サービス
- `ipc_communication` - IPC通信連携

## 🎯 COM統合実装例

### ActiveXコントロール統合
```csharp
// .NET Framework 4.0 ActiveX統合パターン
using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

// COMラッパークラス
public class LegacyComWrapper : IDisposable
{
    private object _comObject;
    private bool _disposed = false;
    
    public LegacyComWrapper(string progId)
    {
        try
        {
            Type comType = Type.GetTypeFromProgID(progId);
            if (comType != null)
            {
                _comObject = Activator.CreateInstance(comType);
            }
            else
            {
                throw new COMException($"COMオブジェクトが見つかりません: {progId}");
            }
        }
        catch (COMException ex)
        {
            throw new InvalidOperationException($"COM初期化エラー: {ex.Message}", ex);
        }
    }
    
    public object InvokeMethod(string methodName, params object[] parameters)
    {
        try
        {
            return _comObject.GetType().InvokeMember(
                methodName,
                BindingFlags.InvokeMethod,
                null,
                _comObject,
                parameters
            );
        }
        catch (Exception ex)
        {
            throw new InvalidOperationException($"COMメソッド呼び出しエラー: {methodName} - {ex.Message}", ex);
        }
    }
    
    public object GetProperty(string propertyName)
    {
        try
        {
            return _comObject.GetType().InvokeMember(
                propertyName,
                BindingFlags.GetProperty,
                null,
                _comObject,
                null
            );
        }
        catch (Exception ex)
        {
            throw new InvalidOperationException($"COMプロパティ取得エラー: {propertyName} - {ex.Message}", ex);
        }
    }
    
    public void SetProperty(string propertyName, object value)
    {
        try
        {
            _comObject.GetType().InvokeMember(
                propertyName,
                BindingFlags.SetProperty,
                null,
                _comObject,
                new object[] { value }
            );
        }
        catch (Exception ex)
        {
            throw new InvalidOperationException($"COMプロパティ設定エラー: {propertyName} - {ex.Message}", ex);
        }
    }
    
    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing && _comObject != null)
            {
                // COMオブジェクトのリリース
                Marshal.ReleaseComObject(_comObject);
                _comObject = null;
            }
            _disposed = true;
        }
    }
    
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
}

// COM統合サービスクラス
public class LegacySystemService
{
    private readonly string _progId;
    
    public LegacySystemService(string progId)
    {
        _progId = progId;
    }
    
    public void ExecuteLegacyOperation(string operation, object[] parameters, 
        Action<object> onSuccess, Action<Exception> onError)
    {
        // BackgroundWorkerで非同期実行 (.NET 4.0対応)
        var worker = new BackgroundWorker();
        worker.DoWork += (sender, e) =>
        {
            try
            {
                using (var comWrapper = new LegacyComWrapper(_progId))
                {
                    var result = comWrapper.InvokeMethod(operation, parameters);
                    e.Result = result;
                }
            }
            catch (Exception ex)
            {
                e.Result = ex;
            }
        };
        
        worker.RunWorkerCompleted += (sender, e) =>
        {
            if (e.Result is Exception)
            {
                onError((Exception)e.Result);
            }
            else
            {
                onSuccess(e.Result);
            }
        };
        
        worker.RunWorkerAsync();
    }
}
```

### ActiveDirectory 統合
```csharp
// .NET Framework 4.0 ActiveDirectory統合
using System;
using System.DirectoryServices;
using System.Security.Principal;
using System.Collections.Generic;

public class ActiveDirectoryService
{
    private readonly string _domain;
    private readonly string _ldapPath;
    
    public ActiveDirectoryService(string domain)
    {
        _domain = domain;
        _ldapPath = $"LDAP://{domain}";
    }
    
    // ドメイン認証
    public bool AuthenticateUser(string username, string password)
    {
        try
        {
            using (var entry = new DirectoryEntry(_ldapPath, username, password))
            {
                // 認証テスト
                object nativeObject = entry.NativeObject;
                return true;
            }
        }
        catch (Exception)
        {
            return false;
        }
    }
    
    // ユーザー情報取得
    public UserInfo GetUserInfo(string username)
    {
        try
        {
            using (var searcher = new DirectorySearcher(new DirectoryEntry(_ldapPath)))
            {
                searcher.Filter = $"(&(objectClass=user)(sAMAccountName={username}))";
                searcher.PropertiesToLoad.AddRange(new[] { 
                    "displayName", "mail", "department", "title", "memberOf" 
                });
                
                var result = searcher.FindOne();
                if (result != null)
                {
                    return new UserInfo
                    {
                        Username = username,
                        DisplayName = GetProperty(result, "displayName"),
                        Email = GetProperty(result, "mail"),
                        Department = GetProperty(result, "department"),
                        Title = GetProperty(result, "title"),
                        Groups = GetUserGroups(result)
                    };
                }
            }
        }
        catch (Exception ex)
        {
            throw new InvalidOperationException($"ADユーザー情報取得エラー: {ex.Message}", ex);
        }
        
        return null;
    }
    
    private string GetProperty(SearchResult result, string propertyName)
    {
        if (result.Properties.Contains(propertyName) && 
            result.Properties[propertyName].Count > 0)
        {
            return result.Properties[propertyName][0].ToString();
        }
        return string.Empty;
    }
    
    private List<string> GetUserGroups(SearchResult result)
    {
        var groups = new List<string>();
        if (result.Properties.Contains("memberOf"))
        {
            foreach (string groupDN in result.Properties["memberOf"])
            {
                // DNからグループ名を抽出
                var cnStart = groupDN.IndexOf("CN=");
                if (cnStart >= 0)
                {
                    var cnEnd = groupDN.IndexOf(",", cnStart);
                    if (cnEnd > cnStart)
                    {
                        var groupName = groupDN.Substring(cnStart + 3, cnEnd - cnStart - 3);
                        groups.Add(groupName);
                    }
                }
            }
        }
        return groups;
    }
}

// ユーザー情報クラス
public class UserInfo
{
    public string Username { get; set; }
    public string DisplayName { get; set; }
    public string Email { get; set; }
    public string Department { get; set; }
    public string Title { get; set; }
    public List<string> Groups { get; set; }
    
    public UserInfo()
    {
        Groups = new List<string>();
    }
}
```

### レガシーDB統合 (SQL Server 2000対応)
```csharp
// .NET Framework 4.0 レガシーSQL Server統合
using System;
using System.Data;
using System.Data.SqlClient;
using System.Collections.Generic;

public class LegacySqlServerRepository
{
    private readonly string _connectionString;
    
    public LegacySqlServerRepository(string connectionString)
    {
        _connectionString = connectionString;
    }
    
    // SQL Server 2000/2005対応クエリ実行
    public DataTable ExecuteQuery(string sql, Dictionary<string, object> parameters = null)
    {
        var dataTable = new DataTable();
        
        using (var connection = new SqlConnection(_connectionString))
        using (var command = new SqlCommand(sql, connection))
        {
            // パラメータ設定
            if (parameters != null)
            {
                foreach (var param in parameters)
                {
                    command.Parameters.AddWithValue($"@{param.Key}", param.Value ?? DBNull.Value);
                }
            }
            
            connection.Open();
            using (var adapter = new SqlDataAdapter(command))
            {
                adapter.Fill(dataTable);
            }
        }
        
        return dataTable;
    }
    
    // ストアドプロシージャ実行 (.NET 4.0対応)
    public object ExecuteStoredProcedure(string procedureName, 
        Dictionary<string, object> inputParams = null,
        Dictionary<string, SqlDbType> outputParams = null)
    {
        using (var connection = new SqlConnection(_connectionString))
        using (var command = new SqlCommand(procedureName, connection))
        {
            command.CommandType = CommandType.StoredProcedure;
            
            // 入力パラメータ設定
            if (inputParams != null)
            {
                foreach (var param in inputParams)
                {
                    command.Parameters.AddWithValue($"@{param.Key}", param.Value ?? DBNull.Value);
                }
            }
            
            // 出力パラメータ設定
            if (outputParams != null)
            {
                foreach (var param in outputParams)
                {
                    var sqlParam = command.Parameters.Add($"@{param.Key}", param.Value);
                    sqlParam.Direction = ParameterDirection.Output;
                }
            }
            
            // 戻り値パラメータ
            var returnParam = command.Parameters.Add("@ReturnValue", SqlDbType.Int);
            returnParam.Direction = ParameterDirection.ReturnValue;
            
            connection.Open();
            command.ExecuteNonQuery();
            
            // 結果返却
            var result = new Dictionary<string, object>();
            result["ReturnValue"] = returnParam.Value;
            
            if (outputParams != null)
            {
                foreach (var param in outputParams)
                {
                    result[param.Key] = command.Parameters[$"@{param.Key}"].Value;
                }
            }
            
            return result;
        }
    }
}
```

## 🔧 詳細オプション

### Windows XP/2003 対応チェック
```bash
/legacy-integration compatibility_check --target_os=xp_2003
```
**チェック項目**:
- .NET Framework 4.0 ランタイム存在確認
- Windows XP SP3 以上のバージョン確認
- 必要なCOMコンポーネント登録状況
- ActiveDirectoryサービス接続確認

### セキュリティ対策
```bash
/legacy-integration security_hardening [security_level]
```
**セキュリティレベル**:
- `basic` - 基本的なCOMセキュリティ設定
- `enterprise` - 企業レベルセキュリティ対策
- `strict` - 厳格なセキュリティポリシー適用

### パフォーマンス最適化
```bash
/legacy-integration performance_optimize [optimization_type]
```
**最適化タイプ**:
- `com_pooling` - COMオブジェクトプーリング
- `connection_pooling` - DBコネクションプーリング
- `memory_management` - メモリ管理最適化
- `thread_optimization` - スレッド最適化

## 📊 トラブルシューティング

### 一般的な統合問題
1. **COMオブジェクト未登録**: `regsvr32`でCOMコンポーネント登録
2. **権限不足**: 管理者権限でアプリ実行
3. **ActiveDirectory接続エラー**: ネットワーク接続・ファイアウォール設定確認
4. **レガシーDB接続失敗**: ドライバーバージョン・接続文字列確認

## 📝 生成ファイル

- `src/Infrastructure/Legacy/` - レガシー統合クラス
- `src/Services/Integration/` - 統合サービス + COMラッパー
- `src/Data/Legacy/` - レガシーDBアクセス層
- `config/legacy_systems.config` - レガシーシステム設定
- `docs/integration/` - 統合手順書・トラブルシューティングガイド
- `tests/Integration/` - 統合テストコード

## 🔗 関連コマンド

- `/security` - セキュリティ設計・ドメイン認証
- `/devops` - レガシー環境デプロイ戦略
- `/winforms-patterns` - COM統合Windows Formsパターン
- `/analyze` - 統合状況分析・パフォーマンス計測
- `/fix` - 統合エラー・接続問題修正

---

**💡 重要**: レガシーシステム統合は、特にCOMコンポーネントのメモリリークに注意が必要です。`Marshal.ReleaseComObject`を必ず呼び出し、using文で確実にリソースを解放してください。