using System;
using System.Configuration;
using System.IO;
using System.Windows.Forms;
using GloryOcr4Lib;
using ISP673_OCRApp.Forms;
using ISP673_OCRApp.Infrastructure;
using log4net;
using Microsoft.Practices.Unity;

namespace ISP673_OCRApp
{
    /// <summary>
    /// ISP-673 帳票OCRソフトウェア統合アプリケーション
    /// .NET Framework 4.0 Windows XP/2003 Compatible OCR Application
    /// </summary>
    static class Program
    {
        private static readonly ILog Logger = LogManager.GetLogger(typeof(Program));
        private static IUnityContainer _container;
        
        /// <summary>
        /// アプリケーションのメイン エントリ ポイントです。
        /// </summary>
        [STAThread]
        static void Main()
        {
            try
            {
                // Initialize application
                InitializeApplication();
                
                // Configure Unity DI Container
                ConfigureDependencyInjection();
                
                // Setup global exception handling
                SetupGlobalExceptionHandling();
                
                // Configure Windows Forms
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);
                
                // Check Windows XP compatibility mode
                CheckWindowsXPCompatibility();
                
                // Verify ISP-673 OCR environment
                VerifyOcrEnvironment();
                
                // Initialize and run main form
                var mainForm = _container.Resolve<MainForm>();
                Application.Run(mainForm);
                
                Logger.Info("Application shutdown completed successfully");
            }
            catch (Exception ex)
            {
                Logger.Fatal("Fatal error during application startup", ex);
                MessageBox.Show(
                    string.Format("アプリケーションの起動中に致命的なエラーが発生しました。\n\nエラー詳細: {0}\n\n管理者にお問い合わせください。", ex.Message),
                    "致命的エラー",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
            finally
            {
                // Cleanup resources
                CleanupApplication();
            }
        }
        
        /// <summary>
        /// アプリケーションの初期化
        /// </summary>
        private static void InitializeApplication()
        {
            // Configure log4net
            log4net.Config.XmlConfigurator.Configure();
            
            Logger.Info("=== ISP-673 OCR Application Starting ===");
            Logger.Info(string.Format("Application Version: {0}", GetApplicationVersion()));
            Logger.Info(string.Format("OS Version: {0}", Environment.OSVersion));
            Logger.Info(string.Format(".NET Version: {0}", Environment.Version));
            Logger.Info(string.Format("Working Directory: {0}", Environment.CurrentDirectory));
            
            // Create logs directory if it doesn't exist
            var logsDirectory = Path.Combine(Application.StartupPath, "logs");
            if (!Directory.Exists(logsDirectory))
            {
                Directory.CreateDirectory(logsDirectory);
                Logger.Info(string.Format("Created logs directory: {0}", logsDirectory));
            }
        }
        
        /// <summary>
        /// Unity DI コンテナの設定
        /// </summary>
        private static void ConfigureDependencyInjection()
        {
            try
            {
                _container = UnityConfig.Configure();
                Logger.Info("Unity DI container configured successfully");
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to configure Unity DI container", ex);
                throw new ApplicationException("DI container configuration failed", ex);
            }
        }
        
        /// <summary>
        /// グローバル例外ハンドリングの設定
        /// </summary>
        private static void SetupGlobalExceptionHandling()
        {
            // .NET Framework 4.0 compatible exception handling
            Application.ThreadException += Application_ThreadException;
            AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;
            
            Logger.Info("Global exception handling configured");
        }
        
        /// <summary>
        /// Windows XP互換性チェック
        /// </summary>
        private static void CheckWindowsXPCompatibility()
        {
            var isXPCompatMode = ConfigurationManager.AppSettings["WindowsXPCompatibilityMode"];
            if (string.Equals(isXPCompatMode, "true", StringComparison.OrdinalIgnoreCase))
            {
                Logger.Info("Windows XP compatibility mode enabled");
                
                // Windows XP specific settings
                if (Environment.OSVersion.Version.Major <= 5) // Windows XP/2003
                {
                    Logger.Info("Windows XP/2003 detected - applying compatibility settings");
                    
                    // Apply XP-specific settings
                    Application.VisualStyleState = System.Windows.Forms.VisualStyles.VisualStyleState.NoneEnabled;
                }
            }
        }
        
        /// <summary>
        /// ISP-673 OCR環境の検証
        /// </summary>
        private static void VerifyOcrEnvironment()
        {
            try
            {
                Logger.Info("Verifying ISP-673 OCR environment...");
                
                // プラットフォーム確認（x86必須）
                if (IntPtr.Size != 4)
                {
                    throw new PlatformNotSupportedException("ISP-673 OCRは32bit (x86) プラットフォームでのみ動作します。");
                }
                Logger.Info("Platform check passed: x86 (32-bit)");
                
                // COM DLL存在確認
                var dllPath = GetOcrDllPath();
                if (!File.Exists(dllPath))
                {
                    Logger.Warn($"GloryOcrMain4.dll not found at: {dllPath}");
                    Logger.Info("Attempting to use registered COM component");
                }
                else
                {
                    Logger.Info($"GloryOcrMain4.dll found at: {dllPath}");
                }
                
                // COM オブジェクト作成テスト
                try
                {
                    var testOcr = new GlyOcr();
                    Logger.Info("COM object creation test passed: IGlyOcr");
                    
                    var testOcrEx = new GlyOcrEx();
                    Logger.Info("COM object creation test passed: IGlyOcrEx");
                }
                catch (Exception ex)
                {
                    Logger.Error("COM object creation failed", ex);
                    throw new ApplicationException("ISP-673 OCR COM DLLが正しく登録されていません。管理者として 'regsvr32 GloryOcrMain4.dll' を実行してください。", ex);
                }
                
                Logger.Info("ISP-673 OCR environment verification completed successfully");
            }
            catch (Exception ex)
            {
                Logger.Fatal("ISP-673 OCR environment verification failed", ex);
                MessageBox.Show(
                    $"ISP-673 OCR環境の検証に失敗しました。\n\nエラー詳細: {ex.Message}\n\n以下を確認してください:\n1. ISP-673がインストール済みか\n2. x86プラットフォームでビルドされているか\n3. GloryOcrMain4.dllが登録済みか",
                    "OCR環境エラー",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
                throw;
            }
        }
        
        /// <summary>
        /// OCR DLLパスの取得
        /// </summary>
        private static string GetOcrDllPath()
        {
            // 一般的なインストールパス
            var commonPaths = new[]
            {
                @"C:\Program Files\Glory\Glyocr4\GloryOcrMain4.dll",
                @"C:\Program Files (x86)\Glory\Glyocr4\GloryOcrMain4.dll"
            };
            
            foreach (var path in commonPaths)
            {
                if (File.Exists(path))
                    return path;
            }
            
            return commonPaths[0]; // デフォルトパス
        }
        
        /// <summary>
        /// UIスレッド例外ハンドラー
        /// </summary>
        private static void Application_ThreadException(object sender, System.Threading.ThreadExceptionEventArgs e)
        {
            Logger.Error("Unhandled UI thread exception", e.Exception);
            
            var result = MessageBox.Show(
                string.Format("予期しないエラーが発生しました。\n\nエラー詳細: {0}\n\nアプリケーションを続行しますか？", e.Exception.Message),
                "エラー",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Warning);
                
            if (result == DialogResult.No)
            {
                Application.Exit();
            }
        }
        
        /// <summary>
        /// アプリケーションドメイン例外ハンドラー
        /// </summary>
        private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            var exception = e.ExceptionObject as Exception;
            if (exception != null)
            {
                Logger.Fatal("Unhandled application domain exception", exception);
            }
            else
            {
                Logger.Fatal(string.Format("Unhandled application domain exception: {0}", e.ExceptionObject));
            }
            
            if (e.IsTerminating)
            {
                Logger.Fatal("Application is terminating due to unhandled exception");
            }
        }
        
        /// <summary>
        /// アプリケーションバージョンの取得
        /// </summary>
        private static string GetApplicationVersion()
        {
            try
            {
                var version = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
                return version.ToString();
            }
            catch
            {
                return "Unknown";
            }
        }
        
        /// <summary>
        /// アプリケーションのクリーンアップ
        /// </summary>
        private static void CleanupApplication()
        {
            try
            {
                // Dispose Unity container
                if (_container != null)
                {
                    _container.Dispose();
                    Logger.Info("Unity container disposed");
                }
                
                Logger.Info("=== ISP-673 OCR Application Shutdown ===");
            }
            catch (Exception ex)
            {
                // Log cleanup errors but don't throw
                try
                {
                    Logger.Error("Error during application cleanup", ex);
                }
                catch
                {
                    // If even logging fails, ignore silently
                }
            }
        }
    }
}