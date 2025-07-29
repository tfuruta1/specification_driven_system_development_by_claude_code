# DevOps Command - 製造業システムDevOps・インフラ自動化

## 概要
FastAPI + SQLAlchemy製造業システムの包括的なDevOpsパイプライン構築、インフラ自動化、製造業特有の運用監視システムの実装を行います。製造ライン稼働継続性とリアルタイム性を重視した製造業DevOps戦略を提供します。

## 使用方法
```
/devops [製造業DevOpsタイプ] [環境] [オプション]
```

## 実行プロセス

### 1. 製造業DevOps要件分析

#### 1.1 製造業システム現状分析
```python
# 製造業システムの現状分析
async def analyze_manufacturing_system_status():
    return {
        'infrastructure': await analyze_manufacturing_infrastructure(),
        'deployment': await analyze_manufacturing_deployment(),
        'monitoring': await analyze_manufacturing_monitoring(),
        'operations': await analyze_manufacturing_operations(),
        'compliance': await analyze_manufacturing_compliance()
    }

# 製造業インフラ分析
async def analyze_manufacturing_infrastructure():
    return {
        'production_lines': await check_production_line_systems(),
        'database_systems': await check_manufacturing_databases(),
        'iot_connectivity': await check_iot_infrastructure(),
        'network_architecture': await check_manufacturing_network(),
        'security_systems': await check_manufacturing_security(),
        'backup_systems': await check_manufacturing_backup()
    }

# 製造業特有の運用要件
manufacturing_devops_requirements = {
    'high_availability': {
        'production_uptime': '99.9% (製造ライン稼働要件)',
        'database_availability': '99.95% (製造データ保護)',
        'iot_connectivity': '99.8% (センサーデータ継続)',
        'recovery_time': '< 5分 (製造停止最小化)'
    },
    'performance': {
        'api_response': '< 200ms (製造システム応答)',
        'database_latency': '< 50ms (リアルタイム要件)',
        'iot_data_processing': '< 1秒 (センサーデータ)',
        'batch_processing': '< 30分 (夜間バッチ)'
    },
    'security': {
        'network_segmentation': '製造ネットワーク分離',
        'access_control': 'ロールベース認証 (製造業職務)',
        'data_encryption': '製造データ暗号化',
        'audit_logging': '製造活動ログ記録'
    },
    'compliance': {
        'standards': ['ISO 9001', 'ISO 14001', 'FDA 21 CFR Part 11'],
        'data_retention': '製造記録7年保存',
        'traceability': '製品トレーサビリティ',
        'change_control': '製造システム変更管理'
    }
}
```

### 2. 製造業CI/CDパイプライン設計

#### 2.1 製造業特化CI/CDアーキテクチャ
```yaml
# .github/workflows/manufacturing-cicd.yml
name: Manufacturing FastAPI + SQLAlchemy CI/CD

on:
  push:
    branches: [main, staging, development]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  POSTGRESQL_VERSION: '15'
  REDIS_VERSION: '7'

jobs:
  # 製造業品質ゲート
  manufacturing-quality-gate:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: manufacturing_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Manufacturing code quality checks
        run: |
          # Python code formatting
          black --check app/ tests/
          isort --check-only app/ tests/
          
          # Type checking
          mypy app/
          
          # Linting
          flake8 app/ tests/
          pylint app/
          
          # Security scanning
          bandit -r app/
          safety check
      
      - name: Manufacturing database tests
        run: |
          # Database migration tests
          alembic upgrade head
          alembic downgrade base
          alembic upgrade head
          
          # Database integrity tests
          python -m pytest tests/database/ -v
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/manufacturing_test
      
      - name: Manufacturing unit tests
        run: |
          pytest tests/unit/ -v --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/manufacturing_test
          REDIS_URL: redis://localhost:6379
      
      - name: Manufacturing integration tests
        run: |
          pytest tests/integration/ -v
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/manufacturing_test
          REDIS_URL: redis://localhost:6379
      
      - name: Manufacturing API tests
        run: |
          # FastAPI test client
          pytest tests/api/ -v
          
          # Load testing for manufacturing APIs
          locust --headless --users 100 --spawn-rate 10 --run-time 60s --host http://localhost:8000
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/manufacturing_test
      
      - name: Manufacturing compliance checks
        run: |
          # Documentation compliance
          python scripts/check_api_documentation.py
          
          # Data validation compliance
          python scripts/validate_manufacturing_models.py
          
          # Audit trail compliance
          python scripts/check_audit_trails.py

  # 製造業ステージング環境デプロイ
  deploy-manufacturing-staging:
    needs: manufacturing-quality-gate
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    environment: manufacturing-staging
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure Manufacturing AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Build Manufacturing Docker image
        run: |
          docker build -t manufacturing-api:staging \
            --build-arg ENVIRONMENT=staging \
            --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
            --build-arg VCS_REF=${{ github.sha }} \
            .
      
      - name: Push to ECR
        run: |
          aws ecr get-login-password --region us-east-1 | \
            docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}
          
          docker tag manufacturing-api:staging ${{ secrets.ECR_REGISTRY }}/manufacturing-api:staging
          docker push ${{ secrets.ECR_REGISTRY }}/manufacturing-api:staging
      
      - name: Deploy to Manufacturing ECS Staging
        run: |
          # Update ECS service with new image
          aws ecs update-service \
            --cluster manufacturing-staging \
            --service manufacturing-api-service \
            --force-new-deployment
          
          # Wait for deployment to complete
          aws ecs wait services-stable \
            --cluster manufacturing-staging \
            --services manufacturing-api-service
      
      - name: Manufacturing system health check
        run: |
          # Wait for service to be ready
          sleep 30
          
          # Health check endpoints
          curl -f ${{ secrets.STAGING_URL }}/health || exit 1
          curl -f ${{ secrets.STAGING_URL }}/health/database || exit 1
          curl -f ${{ secrets.STAGING_URL }}/health/redis || exit 1
          curl -f ${{ secrets.STAGING_URL }}/health/iot || exit 1
      
      - name: Manufacturing integration tests on staging
        run: |
          pytest tests/e2e/ -v --base-url=${{ secrets.STAGING_URL }}

  # 製造業本番環境デプロイ
  deploy-manufacturing-production:
    needs: manufacturing-quality-gate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: manufacturing-production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Manufacturing production deployment approval
        uses: trstringer/manual-approval@v1
        with:
          secret: ${{ github.token }}
          approvers: manufacturing-lead,devops-lead,quality-manager
          minimum-approvals: 2
          issue-title: "製造業本番環境デプロイ承認: ${{ github.sha }}"
      
      - name: Blue-Green deployment to production
        run: |
          # Deploy to green environment
          aws ecs update-service \
            --cluster manufacturing-production \
            --service manufacturing-api-green \
            --task-definition manufacturing-api:${{ github.sha }}
          
          # Health check on green environment
          ./scripts/health_check.sh ${{ secrets.GREEN_ENVIRONMENT_URL }}
          
          # Switch traffic from blue to green
          aws elbv2 modify-rule \
            --rule-arn ${{ secrets.ALB_RULE_ARN }} \
            --actions Type=forward,TargetGroupArn=${{ secrets.GREEN_TARGET_GROUP_ARN }}
          
          # Verify traffic switch
          sleep 60
          ./scripts/verify_production_traffic.sh
          
          # Scale down blue environment
          aws ecs update-service \
            --cluster manufacturing-production \
            --service manufacturing-api-blue \
            --desired-count 0
      
      - name: Manufacturing production monitoring
        run: |
          # Enable enhanced monitoring
          python scripts/enable_production_monitoring.py
          
          # Send success notification to manufacturing team
          python scripts/notify_manufacturing_team.py \
            --event="production-deployment" \
            --status="success" \
            --version="${{ github.sha }}"
```

### 3. 製造業インフラ自動化（Terraform）

#### 3.1 製造業クラウドインフラ
```hcl
# infrastructure/main.tf - Manufacturing Infrastructure
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "manufacturing-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
  }
}

# VPC for Manufacturing Network
resource "aws_vpc" "manufacturing_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "Manufacturing VPC"
    Environment = var.environment
    Project = "Manufacturing-System"
  }
}

# Private Subnets for Manufacturing Applications
resource "aws_subnet" "manufacturing_private" {
  count = 2
  
  vpc_id            = aws_vpc.manufacturing_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "Manufacturing Private Subnet ${count.index + 1}"
    Type = "Private"
  }
}

# Public Subnets for Load Balancers
resource "aws_subnet" "manufacturing_public" {
  count = 2
  
  vpc_id                  = aws_vpc.manufacturing_vpc.id
  cidr_block              = "10.0.${count.index + 10}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "Manufacturing Public Subnet ${count.index + 1}"
    Type = "Public"
  }
}

# Manufacturing Database Subnet Group
resource "aws_db_subnet_group" "manufacturing_db" {
  name       = "manufacturing-db-subnet-group"
  subnet_ids = aws_subnet.manufacturing_private[*].id
  
  tags = {
    Name = "Manufacturing DB Subnet Group"
  }
}

# RDS PostgreSQL for Manufacturing Data
resource "aws_db_instance" "manufacturing_db" {
  identifier = "manufacturing-postgres"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class
  
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  
  db_name  = "manufacturing"
  username = var.db_username
  password = var.db_password
  
  db_subnet_group_name   = aws_db_subnet_group.manufacturing_db.name
  vpc_security_group_ids = [aws_security_group.manufacturing_db.id]
  
  backup_retention_period = 30  # 30 days for manufacturing compliance
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"
  
  performance_insights_enabled = true
  monitoring_interval         = 60
  monitoring_role_arn        = aws_iam_role.rds_monitoring.arn
  
  deletion_protection = var.environment == "production" ? true : false
  
  tags = {
    Name = "Manufacturing Database"
    Environment = var.environment
    Compliance = "ISO-9001"
  }
}

# Redis Cluster for Manufacturing Cache
resource "aws_elasticache_subnet_group" "manufacturing_cache" {
  name       = "manufacturing-cache-subnet-group"
  subnet_ids = aws_subnet.manufacturing_private[*].id
}

resource "aws_elasticache_replication_group" "manufacturing_redis" {
  replication_group_id       = "manufacturing-redis"
  description                = "Redis cluster for manufacturing applications"
  
  node_type                  = "cache.r7g.large"
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.manufacturing_cache.name
  security_group_ids = [aws_security_group.manufacturing_cache.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Name = "Manufacturing Redis Cluster"
    Environment = var.environment
  }
}

# ECS Cluster for Manufacturing Applications
resource "aws_ecs_cluster" "manufacturing" {
  name = "manufacturing-${var.environment}"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Name = "Manufacturing ECS Cluster"
    Environment = var.environment
  }
}

# ECS Task Definition for Manufacturing API
resource "aws_ecs_task_definition" "manufacturing_api" {
  family                   = "manufacturing-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn
  
  container_definitions = jsonencode([
    {
      name  = "manufacturing-api"
      image = "${aws_ecr_repository.manufacturing_api.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.manufacturing_db.endpoint}:5432/manufacturing"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${aws_elasticache_replication_group.manufacturing_redis.primary_endpoint_address}:6379"
        }
      ]
      
      secrets = [
        {
          name      = "JWT_SECRET_KEY"
          valueFrom = aws_ssm_parameter.jwt_secret.arn
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.manufacturing_api.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      
      healthCheck = {
        command = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval = 30
        timeout = 5
        retries = 3
      }
    }
  ])
  
  tags = {
    Name = "Manufacturing API Task Definition"
    Environment = var.environment
  }
}

# ECS Service for Manufacturing API
resource "aws_ecs_service" "manufacturing_api" {
  name            = "manufacturing-api"
  cluster         = aws_ecs_cluster.manufacturing.id
  task_definition = aws_ecs_task_definition.manufacturing_api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = aws_subnet.manufacturing_private[*].id
    security_groups  = [aws_security_group.manufacturing_api.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.manufacturing_api.arn
    container_name   = "manufacturing-api"
    container_port   = 8000
  }
  
  depends_on = [aws_lb_listener.manufacturing_api]
  
  tags = {
    Name = "Manufacturing API Service"
    Environment = var.environment
  }
}

# Application Load Balancer
resource "aws_lb" "manufacturing_api" {
  name               = "manufacturing-api-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.manufacturing_alb.id]
  subnets           = aws_subnet.manufacturing_public[*].id
  
  enable_deletion_protection = var.environment == "production" ? true : false
  
  tags = {
    Name = "Manufacturing API Load Balancer"
    Environment = var.environment
  }
}

# Target Group for Manufacturing API
resource "aws_lb_target_group" "manufacturing_api" {
  name        = "manufacturing-api-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.manufacturing_vpc.id
  target_type = "ip"
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
    protocol            = "HTTP"
  }
  
  tags = {
    Name = "Manufacturing API Target Group"
    Environment = var.environment
  }
}

# Variables
variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "RDS max allocated storage"
  type        = number
  default     = 100
}

variable "api_desired_count" {
  description = "Desired count of API containers"
  type        = number
  default     = 2
}
```

### 4. 製造業監視システム（Prometheus + Grafana）

#### 4.1 製造業メトリクス監視
```yaml
# monitoring/manufacturing-prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "manufacturing_alert_rules.yml"

alertmanager:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Manufacturing API metrics
  - job_name: 'manufacturing-api'
    static_configs:
      - targets: ['manufacturing-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s
  
  # Manufacturing Database metrics
  - job_name: 'manufacturing-postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s
  
  # Manufacturing Redis metrics
  - job_name: 'manufacturing-redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s
  
  # Manufacturing IoT Gateway metrics
  - job_name: 'manufacturing-iot'
    static_configs:
      - targets: ['iot-gateway:8080']
    metrics_path: '/iot/metrics'
    scrape_interval: 10s
  
  # Production Line metrics
  - job_name: 'production-lines'
    static_configs:
      - targets: ['line-monitor:9090']
    scrape_interval: 5s  # High frequency for real-time monitoring
  
  # Quality Control System metrics
  - job_name: 'quality-control'
    static_configs:
      - targets: ['quality-system:8081']
    metrics_path: '/quality/metrics'
    scrape_interval: 20s

---
# monitoring/manufacturing_alert_rules.yml
groups:
  - name: manufacturing_critical
    rules:
      - alert: ProductionLineDown
        expr: production_line_status == 0
        for: 30s
        labels:
          severity: critical
          department: production
        annotations:
          summary: "製造ライン {{ $labels.line_id }} が停止しています"
          description: "ライン {{ $labels.line_id }} が30秒間停止状態です。即座の対応が必要です。"
      
      - alert: QualityCheckFailure
        expr: rate(quality_check_failures_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
          department: quality
        annotations:
          summary: "品質チェック失敗率が異常です"
          description: "品質チェック失敗率が {{ $value }} req/sec を超えています"
      
      - alert: ManufacturingDatabaseDown
        expr: manufacturing_db_up == 0
        for: 1m
        labels:
          severity: critical
          department: it
        annotations:
          summary: "製造業データベースが停止"
          description: "製造業データベースに接続できません。全システムに影響します。"
      
      - alert: IoTSensorDataLoss
        expr: rate(iot_sensor_data_received[5m]) < 0.8
        for: 3m
        labels:
          severity: high
          department: production
        annotations:
          summary: "IoTセンサーデータの受信異常"
          description: "センサーデータ受信が通常の80%を下回っています"

  - name: manufacturing_performance
    rules:
      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(manufacturing_api_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
          department: it
        annotations:
          summary: "製造業API応答速度低下"
          description: "API応答時間の95%タイルが {{ $value }}秒です"
      
      - alert: ProductionEfficiencyLow
        expr: production_efficiency_percentage < 85
        for: 10m
        labels:
          severity: warning
          department: production
        annotations:
          summary: "生産効率低下"
          description: "生産効率が {{ $value }}% に低下しています（目標: 85%以上）"
      
      - alert: EquipmentTemperatureHigh
        expr: equipment_temperature_celsius > 80
        for: 5m
        labels:
          severity: warning
          department: maintenance
        annotations:
          summary: "設備温度異常"
          description: "設備 {{ $labels.equipment_id }} の温度が {{ $value }}°C です"

  - name: manufacturing_compliance
    rules:
      - alert: AuditLogMissing
        expr: increase(audit_log_entries[1h]) == 0
        for: 1h
        labels:
          severity: high
          department: compliance
        annotations:
          summary: "監査ログが記録されていません"
          description: "過去1時間で監査ログエントリが0件です"
      
      - alert: DataBackupFailed
        expr: manufacturing_backup_success == 0
        for: 5m
        labels:
          severity: high
          department: it
        annotations:
          summary: "製造データバックアップ失敗"
          description: "製造データのバックアップが失敗しました"

---
# monitoring/grafana/manufacturing-dashboard.json
{
  "dashboard": {
    "title": "Manufacturing Operations Dashboard",
    "panels": [
      {
        "title": "Production Line Status",
        "type": "stat",
        "targets": [
          {
            "expr": "production_line_status",
            "legendFormat": "Line {{line_id}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      },
      {
        "title": "Production Efficiency",
        "type": "gauge",
        "targets": [
          {
            "expr": "production_efficiency_percentage",
            "legendFormat": "Efficiency %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "green", "value": 85}
              ]
            }
          }
        }
      },
      {
        "title": "Quality Metrics",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(quality_check_passed_total[5m])",
            "legendFormat": "Passed"
          },
          {
            "expr": "rate(quality_check_failed_total[5m])",
            "legendFormat": "Failed"
          }
        ]
      },
      {
        "title": "Equipment Health",
        "type": "heatmap",
        "targets": [
          {
            "expr": "equipment_health_score",
            "legendFormat": "Equipment {{equipment_id}}"
          }
        ]
      },
      {
        "title": "API Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(manufacturing_api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(manufacturing_api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      }
    ]
  }
}
```

## 出力形式

### 製造業DevOps実装計画（.tmp/manufacturing_devops_plan.md）
```markdown
# 製造業DevOps実装計画

## 1. プロジェクト概要
- **対象システム**: FastAPI + SQLAlchemy製造業管理システム
- **実装範囲**: CI/CD、インフラ自動化、監視、運用自動化
- **コンプライアンス**: ISO 9001、FDA 21 CFR Part 11対応
- **実装期間**: 6-8週間

## 2. 製造業DevOps要件
### 高可用性要件
- 製造ライン稼働率: 99.9%
- データベース可用性: 99.95%
- API応答時間: < 200ms
- 復旧時間: < 5分

### セキュリティ要件
- ネットワーク分離（製造ネットワーク/管理ネットワーク）
- 暗号化通信（TLS 1.3）
- アクセス制御（RBAC）
- 監査ログ（全操作記録）

## 3. 実装計画

### Phase 1: 基盤構築（2週間）
- [ ] AWS VPC・ネットワーク構成
- [ ] RDS PostgreSQL設定
- [ ] Redis Cluster構築
- [ ] ECR・ECS環境構築
- [ ] 基本的な監視設定

### Phase 2: CI/CD構築（2週間）
- [ ] GitHub Actions設定
- [ ] 製造業品質ゲート実装
- [ ] Blue-Green deployment
- [ ] 自動テスト統合
- [ ] 承認プロセス設定

### Phase 3: 監視・アラート（1週間）
- [ ] Prometheus設定
- [ ] Grafana ダッシュボード
- [ ] 製造業特化アラート
- [ ] PagerDuty統合
- [ ] Slack通知設定

### Phase 4: 運用自動化（1週間）
- [ ] 自動スケーリング
- [ ] 自動バックアップ
- [ ] ログローテーション
- [ ] セキュリティパッチ自動適用
- [ ] コンプライアンスレポート自動生成

## 4. 成果物
- インフラ定義ファイル（Terraform）
- CI/CDパイプライン設定
- 監視・アラート設定
- 運用手順書
- 災害復旧計画書
```

## TodoWrite連携

製造業DevOps実装タスクを自動生成：

```python
manufacturing_devops_tasks = [
    {
        'id': 'manufacturing-devops-001',
        'content': '製造業システム現状分析と要件定義',
        'status': 'completed',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-devops-002',
        'content': '製造業インフラアーキテクチャ設計',
        'status': 'in_progress',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-devops-003',
        'content': '製造業CI/CDパイプライン実装',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-devops-004',
        'content': '製造業監視システム構築',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-devops-005',
        'content': '製造業セキュリティ設定',
        'status': 'pending',
        'priority': 'high'
    },
    {
        'id': 'manufacturing-devops-006',
        'content': '製造業コンプライアンス対応',
        'status': 'pending',
        'priority': 'medium'
    },
    {
        'id': 'manufacturing-devops-007',
        'content': '製造業運用自動化実装',
        'status': 'pending',
        'priority': 'medium'
    },
    {
        'id': 'manufacturing-devops-008',
        'content': '製造業災害復旧テスト',
        'status': 'pending',
        'priority': 'medium'
    }
]
```

## まとめ

このコマンドは製造業特有の要件を満たすDevOpsパイプラインを提供します：

1. **製造業高可用性**: 生産ライン停止を最小化する冗長化とフェイルオーバー
2. **リアルタイム監視**: IoTセンサー、生産ライン、品質管理の統合監視
3. **コンプライアンス対応**: ISO・FDA要件を満たす監査ログとデータ保護
4. **自動化運用**: 製造業特化の自動スケーリングと障害復旧

製造業システムの継続性と品質を保証する包括的なDevOps環境を構築できます。