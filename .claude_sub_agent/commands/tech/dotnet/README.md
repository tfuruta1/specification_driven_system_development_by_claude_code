# 📚 .NET技術専用コマンド

## 概要
.NET Framework から最新の .NET 8 まで、各バージョンと技術スタックに特化した高品質な開発コマンド群です。プロジェクトのバージョンを自動検出し、最適なコマンドを提供します。

## .NETバージョン自動検出

プロジェクト解析時に以下のファイルから自動的にバージョンを検出：

### 検出方法
```xml
<!-- .csproj ファイルから検出 -->
<TargetFramework>net8.0</TargetFramework>           <!-- .NET 8 -->
<TargetFramework>net7.0</TargetFramework>           <!-- .NET 7 -->
<TargetFramework>net6.0</TargetFramework>           <!-- .NET 6 -->
<TargetFramework>net5.0</TargetFramework>           <!-- .NET 5 -->
<TargetFramework>netcoreapp3.1</TargetFramework>    <!-- .NET Core 3.1 -->
<TargetFramework>netcoreapp2.1</TargetFramework>    <!-- .NET Core 2.1 -->
<TargetFramework>net48</TargetFramework>            <!-- .NET Framework 4.8 -->
<TargetFramework>net472</TargetFramework>           <!-- .NET Framework 4.7.2 -->
<TargetFramework>net461</TargetFramework>           <!-- .NET Framework 4.6.1 -->
<TargetFramework>net40</TargetFramework>            <!-- .NET Framework 4.0 -->
```

## バージョン別推奨コマンド

### .NET 8 (最新 - 2023年11月リリース)
| コマンド | 推奨度 | 理由 |
|---------|--------|------|
| `/dotnet6-modern` | ★★★ | Native AOT、最新C#12機能 |
| `/blazor-fullstack` | ★★★ | Blazor United、SSR対応 |
| `/aspnet-minimal-api` | ★★★ | 最適化されたMinimal API |
| `/ef-core-8` | ★★★ | Complex Types、Raw SQL改善 |

### .NET 7 (2022年11月リリース)
| コマンド | 推奨度 | 理由 |
|---------|--------|------|
| `/dotnet6-modern` | ★★★ | Generic Math、正規表現改善 |
| `/blazor-fullstack` | ★★☆ | Custom Elements対応 |
| `/aspnet-minimal-api` | ★★★ | Rate Limiting、Output Cache |
| `/ef-core-7` | ★★★ | Bulk operations、JSON columns |

### .NET 6 (LTS - 2021年11月リリース)
| コマンド | 推奨度 | 理由 |
|---------|--------|------|
| `/dotnet6-modern` | ★★★ | Minimal API、Hot Reload |
| `/blazor-server` | ★★★ | 成熟したBlazor Server |
| `/aspnet-minimal-api` | ★★★ | 初期Minimal API実装 |
| `/ef-core-6` | ★★★ | Temporal tables、Compiled models |
| `/maui-mobile` | ★★☆ | 初期MAUI実装 |

### .NET 5 (2020年11月リリース - サポート終了)
| コマンド | 推奨度 | 理由 |
|---------|--------|------|
| `/aspnet-mvc-api` | ★★☆ | 従来のMVC/Web API |
| `/blazor-wasm` | ★★☆ | Blazor WebAssembly |
| `/ef-core-5` | ★★☆ | Many-to-many、Split queries |

### .NET Core 3.1 (LTS - 2019年12月リリース - サポート終了)
| コマンド | 推奨度 | 理由 |
|---------|--------|------|
| `/aspnet-mvc-api` | ★★★ | 安定したMVC/Web API |
| `/blazor-server` | ★★☆ | 初期Blazor Server |
| `/ef-core-3` | ★★☆ | LINQ改善、Cosmos DB対応 |
| `/wpf-enterprise` | ★★☆ | .NET Core上のWPF |

### .NET Framework 4.8 (2019年4月リリース)
| コマンド | 推奨度 | 理由 |
|---------|--------|------|
| `/dotnet48-optimize` | ★★★ | 最新Framework機能 |
| `/aspnet-mvc-classic` | ★★★ | 従来のASP.NET MVC |
| `/wcf-service` | ★★★ | WCFサービス |
| `/winforms-enterprise` | ★★★ | エンタープライズWinForms |
| `/wpf-enterprise` | ★★★ | エンタープライズWPF |
| `/ef6-optimize` | ★★★ | Entity Framework 6.x |

### .NET Framework 4.7.2 (2018年4月リリース)
| コマンド | 推奨度 | 理由 |
|---------|--------|------|
| `/dotnet48-optimize` | ★★☆ | 4.8相当機能（一部制限） |
| `/aspnet-mvc-classic` | ★★★ | ASP.NET MVC 5 |
| `/wcf-service` | ★★★ | WCFフル機能 |

### .NET Framework 4.6.1 (2015年11月リリース)
| コマンド | 推奨度 | 理由 |
|---------|--------|------|
| `/dotnet40-optimize` | ★★☆ | async/await対応 |
| `/aspnet-mvc-classic` | ★★☆ | ASP.NET MVC 5 |
| `/ef6-optimize` | ★★☆ | Entity Framework 6.x |

### .NET Framework 4.0 (2010年4月リリース)
| コマンド | 推奨度 | 理由 |
|---------|--------|------|
| `/dotnet40-optimize` | ★★★ | レガシー互換性重視 |
| `/aspnet-webforms` | ★★☆ | ASP.NET Web Forms |
| `/wcf-service` | ★★☆ | 基本的なWCF |

## バージョン別機能対応表

| 機能 | .NET 8 | .NET 7 | .NET 6 | .NET 5 | .NET Core 3.1 | .NET 4.8 | .NET 4.0 |
|------|--------|--------|--------|--------|---------------|----------|----------|
| C# バージョン | 12 | 11 | 10 | 9 | 8 | 7.3 | 4.0 |
| Minimal API | ✅ 完全 | ✅ 改善 | ✅ 初期 | ❌ | ❌ | ❌ | ❌ |
| Native AOT | ✅ 完全 | ✅ 実験的 | ❌ | ❌ | ❌ | ❌ | ❌ |
| Source Generators | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Hot Reload | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Blazor | ✅ United | ✅ 改善 | ✅ 成熟 | ✅ WASM | ✅ Server | ❌ | ❌ |
| async/await | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Span<T> | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ 制限 | ❌ |
| LINQ | ✅ 完全 | ✅ 完全 | ✅ 完全 | ✅ 完全 | ✅ 完全 | ✅ | ✅ |
| Nullable Reference | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Record Types | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Pattern Matching | ✅ 完全 | ✅ 拡張 | ✅ 改善 | ✅ | ✅ | ⚠️ 基本 | ❌ |
| Global Usings | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| File-scoped namespace | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

## コマンド一覧

### 🎯 モダン開発（.NET 6+）
| コマンド | 説明 | 対象バージョン |
|---------|------|---------------|
| `/dotnet6-modern` | .NET 6+最新機能活用 | .NET 6-8 |
| `/aspnet-minimal-api` | Minimal API開発 | .NET 6-8 |
| `/blazor-fullstack` | Blazor統合開発 | .NET 6-8 |
| `/maui-mobile` | MAUIクロスプラットフォーム | .NET 6-8 |

### 🏢 エンタープライズ（全バージョン）
| コマンド | 説明 | 対象バージョン |
|---------|------|---------------|
| `/aspnet-mvc-api` | ASP.NET MVC/Web API | .NET Core 2.1+ |
| `/aspnet-mvc-classic` | ASP.NET MVC (Framework) | .NET 4.0-4.8 |
| `/ef-core-optimize` | Entity Framework Core | .NET Core 2.1+ |
| `/ef6-optimize` | Entity Framework 6.x | .NET 4.0-4.8 |

### 🖥️ デスクトップ
| コマンド | 説明 | 対象バージョン |
|---------|------|---------------|
| `/wpf-enterprise` | WPFエンタープライズ | .NET Core 3.1+, .NET 4.0-4.8 |
| `/winforms-enterprise` | WinFormsビジネス | .NET Core 3.1+, .NET 4.0-4.8 |
| `/dotnet48-optimize` | .NET Framework 4.8 | .NET 4.8 |
| `/dotnet40-optimize` | .NET Framework 4.0 | .NET 4.0-4.5 |

### ☁️ クラウド・分散
| コマンド | 説明 | 対象バージョン |
|---------|------|---------------|
| `/azure-integration` | Azure統合 | すべて |
| `/signalr-realtime` | SignalRリアルタイム | .NET Core 2.1+ |
| `/grpc-service` | gRPCサービス | .NET Core 3.1+ |
| `/microservices` | マイクロサービス | .NET Core 3.1+ |

### 🔧 共通ツール
| コマンド | 説明 | 対象バージョン |
|---------|------|---------------|
| `/dependency-injection` | DI/IoCコンテナ | すべて |
| `/unit-testing` | 単体テスト | すべて |
| `/performance-profiling` | パフォーマンス分析 | すべて |
| `/nuget-management` | NuGet管理 | すべて |

## 使用例

### プロジェクト解析と自動コマンド選択
```bash
# プロジェクト解析
/analyze-project

# 出力例（.NET 8プロジェクトの場合）
検出バージョン: .NET 8.0
推奨コマンド:
  - /dotnet6-modern (Native AOT、最新C#12)
  - /blazor-fullstack (Blazor United対応)
  - /ef-core-8 (最新EF Core機能)

# 出力例（.NET Framework 4.8プロジェクトの場合）
検出バージョン: .NET Framework 4.8
推奨コマンド:
  - /dotnet48-optimize (Framework最適化)
  - /aspnet-mvc-classic (ASP.NET MVC 5)
  - /ef6-optimize (Entity Framework 6.x)
警告: このバージョンは新規開発には推奨されません
```

## バージョンアップグレードパス

### .NET Framework → .NET 6/8
```bash
/migration-assessment --from=net48 --to=net8

# 移行可能性評価
- Windows依存: 中
- WCF使用: あり → CoreWCFへ移行必要
- COM相互運用: あり → 制限付きサポート
- 推奨移行戦略: 段階的移行
```

### .NET Core 3.1 → .NET 6 (LTS)
```bash
/upgrade-guide --from=netcoreapp3.1 --to=net6.0

# アップグレード手順
1. TargetFramework変更
2. パッケージ更新
3. 非推奨API置換
4. Minimal API検討
```

## ベストプラクティス

### 新規プロジェクト
- **推奨**: .NET 8（最新機能）または .NET 6 LTS（長期サポート）
- **避ける**: .NET Framework（レガシー専用）

### 既存プロジェクト
- **.NET Framework**: 可能な限り.NET 6/8へ移行
- **.NET Core 3.1**: .NET 6 LTSへアップグレード
- **.NET 5**: .NET 6以降へ即座にアップグレード

## 管理責任
- **管理部門**: システム開発部
- **方針**: バージョン固有の最適化とモダナイゼーション支援

---
*.NET技術コマンドは、各バージョンの特性を最大限活用するため個別に管理されています。*