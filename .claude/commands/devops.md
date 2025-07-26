# /devops - DevOps・インフラ自動化コマンド

## 目的
o3 MCPのDevOpsエンジニアとして、ツールとの直接統合能力を活用し、CI/CD・インフラ自動化・運用監視システムの構築・管理を実行します。

## 対象AI
- **o3 MCP**: ツール直接統合、実環境操作、継続的改善プロセス実装能力を活用

## 入力パラメータ
- **必須**: `$DEVOPS_TYPE` - DevOpsタイプ（cicd, infrastructure, monitoring, deployment, automation）
- **任意**: `$ENVIRONMENT` - 環境（development, staging, production, all）
- **任意**: `$CLOUD_PROVIDER` - クラウドプロバイダー（aws, gcp, azure, vercel, netlify）
- **任意**: `$AUTOMATION_LEVEL` - 自動化レベル（basic, advanced, full_automation）

## 出力
- **インフラ設定ファイル**: `.tmp/infrastructure/`
- **CI/CD設定**: `.tmp/cicd/`
- **監視設定**: `.tmp/monitoring/`
- **自動化スクリプト**: `.tmp/automation/`
- **運用手順書**: `.tmp/operations_guide.md`

## ワークフロー

### Phase 1: 現状分析・要件定義
```markdown
## 現状分析フェーズ

### 1. 既存インフラ・運用状況調査
- 現在のインフラ構成・リソース使用状況
- デプロイ・リリースプロセス現状
- 監視・ログ・アラート設定状況
- 運用タスク・手動作業の特定

### 2. 要件・目標設定
- パフォーマンス・可用性目標
- セキュリティ・コンプライアンス要件
- 運用効率化・自動化目標
- コスト最適化・スケーラビリティ要件

### 3. ツール・技術スタック調査
- 既存ツールチェーン・統合状況
- 新規導入候補ツール・サービス
- チーム・組織のスキル・経験レベル
- 予算・ライセンス制約

### 4. リスク・制約分析
- 技術的リスク・依存関係
- 運用リスク・単一障害点
- セキュリティリスク・脅威分析
- 組織・プロセス制約
```

### Phase 2: 設計・計画策定
```markdown
## 設計・計画フェーズ

### 1. インフラアーキテクチャ設計
- ネットワーク・セキュリティ設計
- サーバー・ストレージ・データベース構成
- 負荷分散・冗長化・災害復旧設計
- スケーリング・容量計画

### 2. CI/CDパイプライン設計
- ソースコード管理・ブランチ戦略
- ビルド・テスト・品質ゲート設計
- デプロイ戦略・環境管理
- リリース・ロールバック戦略

### 3. 監視・運用戦略設計
- メトリクス・ログ・トレース戦略
- アラート・通知・エスカレーション設計
- ダッシュボード・レポート設計
- 運用手順・インシデント対応設計

### 4. 自動化・改善計画
- 定型作業・手動タスクの自動化
- インフラ・設定のコード化（IaC）
- セルフヒーリング・自動復旧
- 継続的改善・学習サイクル
```

### Phase 3: 実装・運用開始
```markdown
## 実装・運用フェーズ

### 1. インフラ構築・設定
- インフラリソースのプロビジョニング
- ネットワーク・セキュリティ設定
- 監視・ログエージェント導入
- バックアップ・災害復旧設定

### 2. CI/CDパイプライン実装
- パイプライン設定・スクリプト作成
- テスト・品質チェック統合
- デプロイ・リリース自動化
- 環境間データ同期・設定管理

### 3. 監視・アラート設定
- メトリクス収集・可視化
- ログ集約・検索・分析
- アラート・通知設定
- ダッシュボード・レポート作成

### 4. 運用・改善サイクル開始
- 運用手順・ドキュメント整備
- チーム・トレーニング・知識共有
- パフォーマンス・コスト最適化
- 定期レビュー・改善計画
```

## DevOpsタイプ別仕様

### 1. CI/CD構築（cicd）
```yaml
目的: 継続的統合・継続的デプロイメントパイプラインの構築
成果物:
  - CI/CDパイプライン設定ファイル
  - ビルド・テストスクリプト
  - デプロイ・リリーススクリプト
  - 品質ゲート・承認プロセス設定
技術要素:
  - GitHub Actions / GitLab CI / Jenkins
  - Docker / Kubernetes
  - 自動テスト・品質チェック統合
  - 段階的デプロイ・カナリアリリース
```

### 2. インフラ管理（infrastructure）
```yaml
目的: インフラストラクチャのコード化・自動化管理
成果物:
  - Infrastructure as Code（IaC）テンプレート
  - リソースプロビジョニングスクリプト
  - 環境管理・設定ファイル
  - 災害復旧・バックアップ設定
技術要素:
  - Terraform / CloudFormation / Pulumi
  - Ansible / Chef / Puppet
  - Docker / Kubernetes / Helm
  - クラウドサービス（AWS・GCP・Azure）
```

### 3. 監視・運用（monitoring）
```yaml
目的: システム監視・ログ管理・運用自動化の実装
成果物:
  - 監視・メトリクス設定
  - ログ集約・分析システム
  - アラート・通知設定
  - ダッシュボード・レポート
技術要素:
  - Prometheus / Grafana / Datadog
  - ELK Stack / Fluentd / Loki
  - PagerDuty / Slack統合
  - APM・トレーシング（Jaeger・Zipkin）
```

### 4. デプロイ戦略（deployment）
```yaml
目的: 安全・効率的なデプロイメント戦略の実装
成果物:
  - デプロイ戦略設計書
  - 段階的デプロイメント設定
  - ロールバック・復旧手順
  - 環境・リリース管理
技術要素:
  - Blue-Green / Canary / Rolling Deployment
  - Feature Flag / A/B Testing
  - Environment Management
  - Release Orchestration
```

### 5. 運用自動化（automation）
```yaml
目的: 運用タスクの自動化・効率化・品質向上
成果物:
  - 自動化スクリプト・ツール
  - 運用手順・プレイブック
  - セルフヒーリング・自動復旧
  - 定期メンテナンス・最適化
技術要素:
  - Scripting（Python・Bash・PowerShell）
  - Workflow Automation（Zapier・n8n）
  - Infrastructure Automation
  - Self-Healing・Auto-Scaling
```

## 成果物テンプレート

### CI/CD設定例（GitHub Actions）
```yaml
# .github/workflows/deploy.yml
name: Vue.js + Supabase CI/CD Pipeline

on:
  push:
    branches: [main, staging, development]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18'
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}

jobs:
  # 品質チェック・テスト
  quality-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Code quality checks
        run: |
          npm run lint
          npm run type-check
          npm run test:unit
          npm run test:e2e
      
      - name: Security audit
        run: npm audit --audit-level moderate
      
      - name: Build application
        run: npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist-files
          path: dist/

  # ステージング環境デプロイ
  deploy-staging:
    needs: quality-checks
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to Staging
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          scope: ${{ secrets.VERCEL_ORG_ID }}
      
      - name: Run integration tests
        run: npm run test:integration
        env:
          TEST_URL: ${{ steps.deploy.outputs.preview-url }}

  # 本番環境デプロイ
  deploy-production:
    needs: quality-checks
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist-files
          path: dist/
      
      - name: Deploy to Production
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          scope: ${{ secrets.VERCEL_ORG_ID }}
      
      - name: Health check
        run: |
          curl -f ${{ secrets.PRODUCTION_URL }}/health || exit 1
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
          text: "🚀 Production deployment completed successfully!"

  # セキュリティスキャン
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

### インフラ設定例（Terraform）
```hcl
# infrastructure/main.tf - Vercel + Supabase構成
terraform {
  required_providers {
    vercel = {
      source  = "vercel/vercel"
      version = "~> 0.15"
    }
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.0"
    }
  }
}

# Vercel Project
resource "vercel_project" "vue_app" {
  name      = var.project_name
  framework = "vite"
  
  git_repository = {
    type = "github"
    repo = var.github_repo
  }
  
  environment = [
    {
      key    = "VITE_SUPABASE_URL"
      value  = var.supabase_url
      target = ["production", "preview", "development"]
    },
    {
      key    = "VITE_SUPABASE_ANON_KEY"
      value  = var.supabase_anon_key
      target = ["production", "preview", "development"]
    }
  ]
}

# Vercel Domain
resource "vercel_project_domain" "main" {
  project_id = vercel_project.vue_app.id
  domain     = var.domain_name
}

# Supabase Project
resource "supabase_project" "main" {
  organization_id = var.supabase_org_id
  name            = var.project_name
  database_password = var.database_password
  region          = var.supabase_region
}

# Database Schema
resource "supabase_table" "users" {
  project_ref = supabase_project.main.id
  name        = "users"
  
  column {
    name = "id"
    type = "uuid"
    primary_key = true
    default = "gen_random_uuid()"
  }
  
  column {
    name = "email"
    type = "text"
    unique = true
    nullable = false
  }
  
  column {
    name = "created_at"
    type = "timestamp"
    default = "now()"
  }
}

# Row Level Security
resource "supabase_policy" "users_policy" {
  project_ref = supabase_project.main.id
  table_name  = "users"
  name        = "Users can view own data"
  definition  = "auth.uid() = id"
  command     = "SELECT"
}

# Variables
variable "project_name" {
  description = "Project name"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository"
  type        = string
}

variable "domain_name" {
  description = "Custom domain name"
  type        = string
}

variable "supabase_url" {
  description = "Supabase project URL"
  type        = string
}

variable "supabase_anon_key" {
  description = "Supabase anonymous key"
  type        = string
  sensitive   = true
}

# Outputs
output "vercel_url" {
  value = vercel_project.vue_app.production_deployment_url
}

output "supabase_url" {
  value = supabase_project.main.url
}
```

### 監視設定例（Prometheus + Grafana）
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alertmanager:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Application metrics
  - job_name: 'vue-app'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/metrics'
    scrape_interval: 30s
  
  # Supabase metrics (via custom exporter)
  - job_name: 'supabase'
    static_configs:
      - targets: ['supabase-exporter:8080']
    scrape_interval: 60s
  
  # Infrastructure metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
  
  # Database metrics
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

---
# monitoring/alert_rules.yml
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} req/sec"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"
  
  - name: infrastructure
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is {{ $value }}%"
      
      - alert: LowDiskSpace
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk space is {{ $value }}% full"

---
# monitoring/docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
  
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  grafana-storage:
```

## 連携コマンド
- **← /architecture**: アーキテクチャ設計に基づくインフラ実装
- **→ /security**: セキュリティ要件を反映した運用設計
- **→ /analyze**: システム監視データを基にしたパフォーマンス分析
- **→ /fix**: 運用課題・インシデントの自動修復

## 品質チェックリスト
- [ ] 可用性・パフォーマンス目標の達成
- [ ] セキュリティ・コンプライアンス要件の満足
- [ ] 自動化・効率化による運用負荷軽減
- [ ] 監視・アラートによる早期問題検知
- [ ] 災害復旧・事業継続性の確保
- [ ] コスト最適化・リソース効率化

## 使用例

### CI/CDパイプライン構築
```bash
/devops cicd --environment="all" --cloud_provider="vercel" --automation_level="advanced"
```

### インフラ自動化
```bash
/devops infrastructure --environment="production" --cloud_provider="aws" --automation_level="full_automation"
```

### 監視システム構築
```bash
/devops monitoring --environment="production" --automation_level="advanced"
```