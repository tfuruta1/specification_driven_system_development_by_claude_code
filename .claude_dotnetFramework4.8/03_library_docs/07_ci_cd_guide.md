# .NET Framework 4.8 継続的インテグレーション/デプロイメント（CI/CD）完全ガイド

## 1. CI/CDパイプラインの全体像

### DevOpsパイプライン構成
```mermaid
graph LR
    A[コードプッシュ] --> B[ビルド]
    B --> C[単体テスト]
    C --> D[コード分析]
    D --> E[統合テスト]
    E --> F[成果物作成]
    F --> G[ステージング環境]
    G --> H[受入テスト]
    H --> I[本番環境]
```

### 環境構成
```yaml
environments:
  development:
    branch: develop
    auto_deploy: true
    approvals: none
    
  staging:
    branch: release/*
    auto_deploy: true
    approvals: 
      - qa_team
      
  production:
    branch: main
    auto_deploy: false
    approvals:
      - product_owner
      - operations_team
```

## 2. ビルドサーバー設定

### ビルドエージェント要件
```xml
<!-- .NET Framework 4.8 ビルド要件 -->
<requirements>
  <software>
    <item name="Visual Studio 2022 Build Tools" version="17.0+" />
    <item name=".NET Framework 4.8 Developer Pack" />
    <item name="Windows SDK" version="10.0.19041.0+" />
    <item name="NuGet CLI" version="6.0+" />
  </software>
  
  <tools>
    <item name="MSBuild" path="C:\Program Files\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe" />
    <item name="VSTest" path="C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\TestWindow\vstest.console.exe" />
    <item name="Code Coverage" path="C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Team Tools\Dynamic Code Coverage Tools\CodeCoverage.exe" />
  </tools>
</requirements>
```

## 3. Azure DevOps完全設定

### マルチステージパイプライン
```yaml
# azure-pipelines.yml
name: $(BuildDefinitionName)_$(Year:yyyy).$(Month).$(DayOfMonth)$(Rev:.r)

trigger:
  batch: true
  branches:
    include:
    - main
    - develop
    - release/*
    - feature/*
  paths:
    exclude:
    - docs/*
    - '*.md'
    - .gitignore

pr:
  branches:
    include:
    - main
    - develop
  paths:
    exclude:
    - docs/*
    - '*.md'

variables:
  - group: 'EnterpriseApp-Common'
  - name: solution
    value: 'EnterpriseApp.sln'
  - name: buildPlatform
    value: 'Any CPU'
  - name: buildConfiguration
    value: 'Release'
  - name: dotNetFrameworkVersion
    value: '4.8'

stages:
- stage: Build
  displayName: 'Build and Unit Test'
  jobs:
  - job: BuildJob
    displayName: 'Build Solution'
    pool:
      vmImage: 'windows-2022'
    steps:
    - task: PowerShell@2
      displayName: 'Set Build Number'
      inputs:
        targetType: 'inline'
        script: |
          $version = Get-Content version.txt
          Write-Host "##vso[build.updatebuildnumber]$version.$(Build.BuildId)"
    
    - task: NuGetToolInstaller@1
      displayName: 'Install NuGet'
      inputs:
        versionSpec: '6.x'
    
    - task: NuGetCommand@2
      displayName: 'Restore NuGet Packages'
      inputs:
        command: 'restore'
        restoreSolution: '$(solution)'
        feedsToUse: 'config'
        nugetConfigPath: 'nuget.config'
    
    - task: VSBuild@1
      displayName: 'Build Solution'
      inputs:
        solution: '$(solution)'
        msbuildArgs: '/p:DeployOnBuild=true /p:WebPublishMethod=Package /p:PackageAsSingleFile=true /p:SkipInvalidConfigurations=true /p:PackageLocation="$(build.artifactStagingDirectory)"'
        platform: '$(buildPlatform)'
        configuration: '$(buildConfiguration)'
        msbuildArchitecture: 'x64'
        createLogFile: true
        logFileVerbosity: 'diagnostic'
    
    - task: VSTest@2
      displayName: 'Run Unit Tests'
      inputs:
        testSelector: 'testAssemblies'
        testAssemblyVer2: |
          **\$(buildConfiguration)\*UnitTests.dll
          !**\*TestAdapter.dll
          !**\obj\**
        searchFolder: '$(System.DefaultWorkingDirectory)'
        resultsFolder: '$(Agent.TempDirectory)\TestResults'
        testFiltercriteria: 'TestCategory!=Integration'
        runInParallel: true
        codeCoverageEnabled: true
        testRunTitle: 'Unit Tests'
        platform: '$(buildPlatform)'
        configuration: '$(buildConfiguration)'
        diagnosticsEnabled: true
    
    - task: PublishTestResults@2
      displayName: 'Publish Test Results'
      condition: succeededOrFailed()
      inputs:
        testResultsFormat: 'VSTest'
        testResultsFiles: '**/*.trx'
        searchFolder: '$(Agent.TempDirectory)\TestResults'
        mergeTestResults: true
        testRunTitle: 'Unit Test Results'
    
    - task: PublishCodeCoverageResults@1
      displayName: 'Publish Code Coverage'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: '$(Agent.TempDirectory)\**\*.coverage'
        reportDirectory: '$(Agent.TempDirectory)\CoverageReport'
    
    - task: BuildQualityChecks@8
      displayName: 'Check Build Quality'
      inputs:
        checkCoverage: true
        coverageFailOption: 'fixed'
        coverageType: 'lines'
        coverageThreshold: '80'
        checkWarnings: true
        warningFailOption: 'fixed'
        warningThreshold: '0'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish Artifacts'
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)'
        ArtifactName: 'drop'
        publishLocation: 'Container'

- stage: CodeAnalysis
  displayName: 'Code Analysis and Security Scan'
  dependsOn: Build
  jobs:
  - job: AnalysisJob
    displayName: 'Run Code Analysis'
    pool:
      vmImage: 'windows-2022'
    steps:
    - task: SonarQubePrepare@5
      displayName: 'Prepare SonarQube Analysis'
      inputs:
        SonarQube: 'SonarQube-Connection'
        scannerMode: 'MSBuild'
        projectKey: 'EnterpriseApp'
        projectName: 'Enterprise Application'
        projectVersion: '$(Build.BuildNumber)'
        extraProperties: |
          sonar.cs.vstest.reportsPaths=$(Agent.TempDirectory)\TestResults\*.trx
          sonar.cs.vscoveragexml.reportsPaths=$(Agent.TempDirectory)\**\*.coverage
    
    - task: VSBuild@1
      displayName: 'Rebuild for Analysis'
      inputs:
        solution: '$(solution)'
        platform: '$(buildPlatform)'
        configuration: '$(buildConfiguration)'
        msbuildArgs: '/p:RunCodeAnalysis=true'
    
    - task: SonarQubeAnalyze@5
      displayName: 'Run SonarQube Analysis'
    
    - task: SonarQubePublish@5
      displayName: 'Publish SonarQube Results'
      inputs:
        pollingTimeoutSec: '300'
    
    - task: SecurityCodeScan@1
      displayName: 'Security Code Scan'
      inputs:
        toolVersion: 'Latest'
        failOnHighSeverity: true
    
    - task: WhiteSource@21
      displayName: 'WhiteSource Security Scan'
      inputs:
        cwd: '$(System.DefaultWorkingDirectory)'
        projectName: 'EnterpriseApp'

- stage: IntegrationTest
  displayName: 'Integration Testing'
  dependsOn: CodeAnalysis
  jobs:
  - job: IntegrationTestJob
    displayName: 'Run Integration Tests'
    pool:
      name: 'Enterprise-Test-Pool'
      demands:
      - SqlServer
      - IIS
    steps:
    - task: DownloadBuildArtifacts@0
      displayName: 'Download Build Artifacts'
      inputs:
        buildType: 'current'
        downloadType: 'single'
        artifactName: 'drop'
        downloadPath: '$(System.ArtifactsDirectory)'
    
    - task: SqlDacpacDeploymentOnMachineGroup@0
      displayName: 'Deploy Test Database'
      inputs:
        dacpacFile: '$(System.ArtifactsDirectory)\**\*.dacpac'
        serverName: '$(TestSqlServer)'
        databaseName: 'EnterpriseApp_IntegrationTest'
        authScheme: 'windowsAuthentication'
        deployType: 'DacpacTask'
        additionalArguments: '/p:CreateNewDatabase=True'
    
    - task: IISWebAppManagementOnMachineGroup@0
      displayName: 'Create Test Website'
      inputs:
        enableIIS: true
        websiteName: 'EnterpriseApp_IntegrationTest'
        websitePhysicalPath: '$(System.ArtifactsDirectory)\drop'
        addBinding: true
        bindings: '{"protocol":"http","ipAddress":"*","port":"8080","hostname":""}'
        createAppPool: true
        appPoolName: 'EnterpriseApp_IntegrationTest'
        dotNetVersion: 'v4.0'
        pipeLineMode: 'Integrated'
        appPoolIdentity: 'ApplicationPoolIdentity'
    
    - task: VSTest@2
      displayName: 'Run Integration Tests'
      inputs:
        testSelector: 'testAssemblies'
        testAssemblyVer2: |
          **\*IntegrationTests.dll
        searchFolder: '$(System.ArtifactsDirectory)'
        uiTests: true
        testFiltercriteria: 'TestCategory=Integration'
        runSettingsFile: '$(System.DefaultWorkingDirectory)\IntegrationTests.runsettings'
        overrideTestrunParameters: '-TestDbConnectionString "$(TestDbConnectionString)" -TestApiUrl "http://localhost:8080"'
    
    - task: PublishTestResults@2
      displayName: 'Publish Integration Test Results'
      condition: succeededOrFailed()
      inputs:
        testResultsFormat: 'VSTest'
        testResultsFiles: '**/*.trx'
        testRunTitle: 'Integration Test Results'

- stage: Package
  displayName: 'Create Deployment Packages'
  dependsOn: IntegrationTest
  jobs:
  - job: PackageJob
    displayName: 'Create Packages'
    pool:
      vmImage: 'windows-2022'
    steps:
    - task: DownloadBuildArtifacts@0
      displayName: 'Download Artifacts'
      inputs:
        buildType: 'current'
        downloadType: 'single'
        artifactName: 'drop'
        downloadPath: '$(System.ArtifactsDirectory)'
    
    - task: MSBuild@1
      displayName: 'Create ClickOnce Package'
      inputs:
        solution: '$(solution)'
        platform: '$(buildPlatform)'
        configuration: '$(buildConfiguration)'
        msbuildArguments: '/target:publish /p:PublishDir=$(Build.ArtifactStagingDirectory)\ClickOnce\ /p:InstallUrl=https://deploy.company.com/EnterpriseApp/ /p:UpdateUrl=https://deploy.company.com/EnterpriseApp/ /p:PublishUrl=$(Build.ArtifactStagingDirectory)\ClickOnce\ /p:Install=true /p:MapFileExtensions=true /p:ApplicationVersion=$(Build.BuildNumber) /p:UpdateEnabled=true /p:UpdateMode=Foreground'
    
    - task: PowerShell@2
      displayName: 'Create Chocolatey Package'
      inputs:
        targetType: 'inline'
        script: |
          $version = "$(Build.BuildNumber)"
          $nuspecContent = @"
          <?xml version="1.0" encoding="utf-8"?>
          <package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
            <metadata>
              <id>EnterpriseApp</id>
              <version>$version</version>
              <title>Enterprise Application</title>
              <authors>Your Company</authors>
              <description>Enterprise Integration Application</description>
            </metadata>
            <files>
              <file src="**\*.*" target="tools" />
            </files>
          </package>
          "@
          $nuspecContent | Out-File -FilePath "$(Build.ArtifactStagingDirectory)\enterpriseapp.nuspec"
          
          choco pack "$(Build.ArtifactStagingDirectory)\enterpriseapp.nuspec" --outputdirectory "$(Build.ArtifactStagingDirectory)\Chocolatey"
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish ClickOnce Package'
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)\ClickOnce'
        ArtifactName: 'ClickOnce'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish Chocolatey Package'
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)\Chocolatey'
        ArtifactName: 'Chocolatey'

- stage: DeployStaging
  displayName: 'Deploy to Staging'
  dependsOn: Package
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/develop'))
  jobs:
  - deployment: DeployToStaging
    displayName: 'Deploy to Staging Environment'
    pool:
      name: 'Enterprise-Deploy-Pool'
    environment: 'Staging'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: DownloadBuildArtifacts@0
            displayName: 'Download Artifacts'
            inputs:
              buildType: 'current'
              downloadType: 'specific'
              itemPattern: '**'
              downloadPath: '$(System.ArtifactsDirectory)'
          
          - task: PowerShell@2
            displayName: 'Pre-deployment Backup'
            inputs:
              targetType: 'inline'
              script: |
                $backupPath = "\\backup-server\EnterpriseApp\$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
                New-Item -ItemType Directory -Path $backupPath -Force
                Copy-Item -Path "\\staging-server\EnterpriseApp\*" -Destination $backupPath -Recurse
          
          - task: IISWebAppDeploymentOnMachineGroup@0
            displayName: 'Deploy to IIS'
            inputs:
              webSiteName: 'EnterpriseApp-Staging'
              package: '$(System.ArtifactsDirectory)\drop\*.zip'
              removeAdditionalFilesFlag: true
              takeAppOfflineFlag: true
              additionalArguments: '-skip:objectName=filePath,absolutePath=.*\\App_Data\\.*'
          
          - task: SqlDacpacDeploymentOnMachineGroup@0
            displayName: 'Update Database'
            inputs:
              dacpacFile: '$(System.ArtifactsDirectory)\**\*.dacpac'
              serverName: '$(StagingSqlServer)'
              databaseName: 'EnterpriseApp_Staging'
              authScheme: 'windowsAuthentication'
              deployType: 'DacpacTask'
              additionalArguments: '/p:GenerateSmartDefaults=True /p:BlockOnPossibleDataLoss=False'
          
          - task: PowerShell@2
            displayName: 'Run Smoke Tests'
            inputs:
              filePath: '$(System.ArtifactsDirectory)\Scripts\SmokeTests.ps1'
              arguments: '-Environment Staging -ApiUrl https://staging.company.com/api'
          
          - task: PowerShell@2
            displayName: 'Send Deployment Notification'
            inputs:
              targetType: 'inline'
              script: |
                $body = @{
                  text = "Deployment to Staging completed successfully"
                  buildNumber = "$(Build.BuildNumber)"
                  environment = "Staging"
                  deployedBy = "$(Build.RequestedFor)"
                }
                Invoke-RestMethod -Uri "$(TeamsWebhookUrl)" -Method Post -Body ($body | ConvertTo-Json) -ContentType "application/json"

- stage: DeployProduction
  displayName: 'Deploy to Production'
  dependsOn: DeployStaging
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToProduction
    displayName: 'Deploy to Production Environment'
    pool:
      name: 'Enterprise-Deploy-Pool'
    environment: 'Production'
    strategy:
      canary:
        increments: [10, 50, 100]
        deploy:
          steps:
          - task: PowerShell@2
            displayName: 'Health Check'
            inputs:
              targetType: 'inline'
              script: |
                $response = Invoke-WebRequest -Uri "https://app.company.com/api/health" -UseBasicParsing
                if ($response.StatusCode -ne 200) {
                  throw "Health check failed"
                }
```

## 4. GitHub Actions詳細設定

### 完全なワークフロー
```yaml
# .github/workflows/ci-cd.yml
name: Enterprise App CI/CD

on:
  push:
    branches: [ main, develop, 'release/**' ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

env:
  DOTNET_VERSION: '4.8.x'
  BUILD_CONFIGURATION: 'Release'
  
jobs:
  build-test:
    name: Build and Test
    runs-on: windows-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Full history for versioning
    
    - name: Setup MSBuild
      uses: microsoft/setup-msbuild@v1.1
      with:
        msbuild-architecture: x64
    
    - name: Setup NuGet
      uses: NuGet/setup-nuget@v1
      with:
        nuget-version: '6.x'
    
    - name: Setup VSTest
      uses: darenm/Setup-VSTest@v1.2
    
    - name: Cache NuGet packages
      uses: actions/cache@v3
      with:
        path: ~/.nuget/packages
        key: ${{ runner.os }}-nuget-${{ hashFiles('**/packages.config') }}
        restore-keys: |
          ${{ runner.os }}-nuget-
    
    - name: Restore dependencies
      run: nuget restore
    
    - name: Build solution
      run: msbuild /p:Configuration=${{ env.BUILD_CONFIGURATION }} /p:Platform="Any CPU" /p:Version=${{ github.run_number }}
    
    - name: Run unit tests
      run: |
        vstest.console.exe **\bin\${{ env.BUILD_CONFIGURATION }}\*Tests.dll /Logger:trx /ResultsDirectory:TestResults /Parallel
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: TestResults
    
    - name: Generate code coverage
      run: |
        dotnet tool install --global dotnet-coverage
        dotnet-coverage collect "vstest.console.exe **\bin\${{ env.BUILD_CONFIGURATION }}\*Tests.dll" -f cobertura -o coverage.xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-${{ github.run_number }}
    
    - name: Create application package
      run: |
        msbuild /t:Package /p:Configuration=${{ env.BUILD_CONFIGURATION }} /p:PackageLocation="${{ github.workspace }}\artifacts"
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: build-artifacts
        path: artifacts/

  code-analysis:
    name: Code Analysis
    runs-on: windows-latest
    needs: build-test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run CodeQL Analysis
      uses: github/codeql-action/analyze@v2
      with:
        languages: csharp
    
    - name: Run Dependency Check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        project: 'EnterpriseApp'
        path: '.'
        format: 'HTML'
    
    - name: Upload dependency check results
      uses: actions/upload-artifact@v3
      with:
        name: dependency-check-report
        path: reports/

  deploy-staging:
    name: Deploy to Staging
    runs-on: windows-latest
    needs: [build-test, code-analysis]
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.company.com
    
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: build-artifacts
        path: ./deploy
    
    - name: Deploy to IIS
      uses: cschleiden/webdeploy-action@v1
      with:
        webSiteName: 'EnterpriseApp-Staging'
        package: './deploy/*.zip'
        targetServerUrl: ${{ secrets.STAGING_SERVER_URL }}
        targetServerUsername: ${{ secrets.STAGING_USERNAME }}
        targetServerPassword: ${{ secrets.STAGING_PASSWORD }}
    
    - name: Run smoke tests
      run: |
        $response = Invoke-WebRequest -Uri "https://staging.company.com/api/health" -UseBasicParsing
        if ($response.StatusCode -ne 200) {
          exit 1
        }

  deploy-production:
    name: Deploy to Production
    runs-on: windows-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://app.company.com
    
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: build-artifacts
        path: ./deploy
    
    - name: Create release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: v${{ github.run_number }}
        release_name: Release v${{ github.run_number }}
        draft: false
        prerelease: false
    
    - name: Deploy to production
      uses: cschleiden/webdeploy-action@v1
      with:
        webSiteName: 'EnterpriseApp'
        package: './deploy/*.zip'
        targetServerUrl: ${{ secrets.PROD_SERVER_URL }}
        targetServerUsername: ${{ secrets.PROD_USERNAME }}
        targetServerPassword: ${{ secrets.PROD_PASSWORD }}
```

## 5. Jenkins Pipeline詳細

### Jenkinsfile（宣言的パイプライン）
```groovy
@Library('enterprise-shared-library') _

pipeline {
    agent {
        label 'windows && dotnet48'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
        skipDefaultCheckout()
        parallelsAlwaysFailFast()
    }
    
    parameters {
        choice(
            name: 'DEPLOY_ENVIRONMENT',
            choices: ['none', 'staging', 'production'],
            description: 'Target deployment environment'
        )
        booleanParam(
            name: 'RUN_INTEGRATION_TESTS',
            defaultValue: true,
            description: 'Run integration tests'
        )
        string(
            name: 'VERSION_OVERRIDE',
            defaultValue: '',
            description: 'Override version number (leave empty for auto)'
        )
    }
    
    environment {
        MSBUILD = "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\MSBuild\\Current\\Bin\\MSBuild.exe"
        NUGET = "C:\\Tools\\nuget.exe"
        VSTEST = "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\Common7\\IDE\\CommonExtensions\\Microsoft\\TestWindow\\vstest.console.exe"
        VERSION = "${params.VERSION_OVERRIDE ?: env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                
                script {
                    // Git情報の取得
                    env.GIT_COMMIT_SHORT = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    env.GIT_BRANCH_NAME = sh(script: "git rev-parse --abbrev-ref HEAD", returnStdout: true).trim()
                }
            }
        }
        
        stage('Version') {
            steps {
                script {
                    def version = readFile('version.txt').trim()
                    env.FULL_VERSION = "${version}.${env.VERSION}"
                    
                    powershell """
                        (Get-Content AssemblyInfo.cs) -replace 'AssemblyVersion\\(".*"\\)', 'AssemblyVersion("${env.FULL_VERSION}")' | Set-Content AssemblyInfo.cs
                        (Get-Content AssemblyInfo.cs) -replace 'AssemblyFileVersion\\(".*"\\)', 'AssemblyFileVersion("${env.FULL_VERSION}")' | Set-Content AssemblyInfo.cs
                    """
                }
            }
        }
        
        stage('Build') {
            steps {
                bat "\"${env.NUGET}\" restore"
                
                bat "\"${env.MSBUILD}\" /p:Configuration=Release /p:Platform=\"Any CPU\" /p:Version=${env.FULL_VERSION} /m"
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        bat "\"${env.VSTEST}\" **\\bin\\Release\\*UnitTests.dll /Logger:trx /ResultsDirectory:TestResults\\Unit"
                    }
                    post {
                        always {
                            mstest testResultsFile: 'TestResults/Unit/*.trx'
                        }
                    }
                }
                
                stage('Code Analysis') {
                    steps {
                        withSonarQubeEnv('SonarQube') {
                            bat "\"${env.MSBUILD}\" /t:Rebuild /p:Configuration=Release sonar.login=${SONAR_AUTH_TOKEN}"
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        dependencyCheck additionalArguments: '--scan . --format HTML', odcInstallation: 'DependencyCheck'
                        
                        publishHTML(target: [
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'dependency-check-report',
                            reportFiles: 'dependency-check-report.html',
                            reportName: 'Dependency Check Report'
                        ])
                    }
                }
            }
        }
        
        stage('Integration Tests') {
            when {
                expression { params.RUN_INTEGRATION_TESTS }
            }
            steps {
                script {
                    // テスト環境のセットアップ
                    bat """
                        sqlcmd -S localhost -d master -Q "CREATE DATABASE TestDB_${env.BUILD_NUMBER}"
                        sqlcmd -S localhost -d TestDB_${env.BUILD_NUMBER} -i schema.sql
                    """
                    
                    try {
                        bat "\"${env.VSTEST}\" **\\bin\\Release\\*IntegrationTests.dll /Logger:trx /ResultsDirectory:TestResults\\Integration"
                    } finally {
                        // クリーンアップ
                        bat "sqlcmd -S localhost -d master -Q \"DROP DATABASE TestDB_${env.BUILD_NUMBER}\""
                    }
                }
            }
        }
        
        stage('Package') {
            steps {
                // ClickOnceパッケージ作成
                bat "\"${env.MSBUILD}\" /t:Publish /p:Configuration=Release /p:Platform=\"Any CPU\" /p:PublishDir=Publish\\ClickOnce\\ /p:ApplicationVersion=${env.FULL_VERSION}"
                
                // インストーラー作成
                bat "\"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe\" /DVersion=${env.FULL_VERSION} installer.iss"
                
                // アーカイブ
                zip zipFile: "EnterpriseApp-${env.FULL_VERSION}.zip", archive: true, dir: 'bin\\Release'
            }
        }
        
        stage('Deploy') {
            when {
                expression { params.DEPLOY_ENVIRONMENT != 'none' }
            }
            steps {
                script {
                    if (params.DEPLOY_ENVIRONMENT == 'staging') {
                        deployToEnvironment('staging', env.FULL_VERSION)
                    } else if (params.DEPLOY_ENVIRONMENT == 'production') {
                        input message: 'Deploy to production?', ok: 'Deploy'
                        deployToEnvironment('production', env.FULL_VERSION)
                    }
                }
            }
        }
    }
    
    post {
        success {
            emailext(
                subject: "Build Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                    <h2>Build Successful</h2>
                    <p>Version: ${env.FULL_VERSION}</p>
                    <p>Branch: ${env.GIT_BRANCH_NAME}</p>
                    <p>Commit: ${env.GIT_COMMIT_SHORT}</p>
                    <p>Build URL: ${env.BUILD_URL}</p>
                """,
                to: 'team@company.com',
                mimeType: 'text/html'
            )
            
            // Slackに通知
            slackSend(
                color: 'good',
                message: "Build Success: ${env.JOB_NAME} #${env.BUILD_NUMBER} - Version ${env.FULL_VERSION}"
            )
        }
        
        failure {
            emailext(
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build failed. Check console output at ${env.BUILD_URL}",
                to: 'team@company.com'
            )
            
            slackSend(
                color: 'danger',
                message: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER} - ${env.BUILD_URL}"
            )
        }
        
        always {
            // ワークスペースのクリーンアップ
            cleanWs()
        }
    }
}

def deployToEnvironment(environment, version) {
    echo "Deploying version ${version} to ${environment}"
    
    withCredentials([usernamePassword(credentialsId: "${environment}-deploy-creds", usernameVariable: 'USER', passwordVariable: 'PASS')]) {
        bat """
            msdeploy -verb:sync -source:package="EnterpriseApp-${version}.zip" -dest:auto,computerName="${environment}.company.com",userName="${USER}",password="${PASS}" -setParam:name="IIS Web Application Name",value="EnterpriseApp-${environment}"
        """
    }
    
    // 配置後のヘルスチェック
    retry(3) {
        bat "curl -f https://${environment}.company.com/api/health"
    }
}
```

## 6. ビルドとテストの自動化スクリプト

### build.ps1（ローカルビルドスクリプト）
```powershell
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "1.0.0",
    
    [Parameter(Mandatory=$false)]
    [switch]$RunTests,
    
    [Parameter(Mandatory=$false)]
    [switch]$Package,
    
    [Parameter(Mandatory=$false)]
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

# パスの設定
$SolutionPath = "EnterpriseApp.sln"
$MSBuild = "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
$VSTest = "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\TestWindow\vstest.console.exe"
$NuGet = ".\tools\nuget.exe"

function Write-Step {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

# クリーン
if ($Clean) {
    Write-Step "Cleaning solution"
    & $MSBuild $SolutionPath /t:Clean /p:Configuration=$Configuration
    Remove-Item -Path ".\packages" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path ".\TestResults" -Recurse -Force -ErrorAction SilentlyContinue
}

# NuGet restore
Write-Step "Restoring NuGet packages"
& $NuGet restore $SolutionPath

# ビルド
Write-Step "Building solution"
& $MSBuild $SolutionPath /p:Configuration=$Configuration /p:Platform="Any CPU" /p:Version=$Version /m

if ($LASTEXITCODE -ne 0) {
    throw "Build failed"
}

# テスト実行
if ($RunTests) {
    Write-Step "Running unit tests"
    
    $testAssemblies = Get-ChildItem -Path ".\*\bin\$Configuration\*Tests.dll" -Recurse
    
    foreach ($assembly in $testAssemblies) {
        Write-Host "Testing: $($assembly.Name)"
        & $VSTest $assembly.FullName /Logger:trx /ResultsDirectory:TestResults
        
        if ($LASTEXITCODE -ne 0) {
            throw "Tests failed for $($assembly.Name)"
        }
    }
    
    # テスト結果のサマリー
    Write-Step "Test Summary"
    $trxFiles = Get-ChildItem -Path ".\TestResults\*.trx"
    foreach ($trx in $trxFiles) {
        [xml]$results = Get-Content $trx.FullName
        $summary = $results.TestRun.ResultSummary.Counters
        Write-Host "$($trx.Name): Total=$($summary.total), Passed=$($summary.passed), Failed=$($summary.failed)"
    }
}

# パッケージング
if ($Package) {
    Write-Step "Creating packages"
    
    # ClickOnce
    & $MSBuild $SolutionPath /t:Publish /p:Configuration=$Configuration /p:PublishDir=".\Publish\ClickOnce\" /p:ApplicationVersion=$Version
    
    # ZIP
    $zipPath = ".\Publish\EnterpriseApp-$Version.zip"
    Compress-Archive -Path ".\bin\$Configuration\*" -DestinationPath $zipPath -Force
    
    Write-Host "Packages created in .\Publish\"
}

Write-Step "Build completed successfully!"
```

## 7. 環境固有の設定管理

### 設定変換（Web.config Transform）
```xml
<!-- Web.Release.config -->
<configuration xmlns:xdt="http://schemas.microsoft.com/XML-Document-Transform">
  <connectionStrings>
    <add name="DefaultConnection" 
         connectionString="Data Source=prod-server;Initial Catalog=EnterpriseDB;Integrated Security=True" 
         xdt:Transform="SetAttributes" xdt:Locator="Match(name)"/>
  </connectionStrings>
  
  <appSettings>
    <add key="Environment" value="Production" xdt:Transform="SetAttributes" xdt:Locator="Match(key)"/>
    <add key="EnableDebugLogging" value="false" xdt:Transform="SetAttributes" xdt:Locator="Match(key)"/>
  </appSettings>
  
  <system.web>
    <compilation xdt:Transform="RemoveAttributes(debug)" />
    <customErrors mode="On" xdt:Transform="Replace">
      <error statusCode="404" redirect="~/Error/NotFound" />
      <error statusCode="500" redirect="~/Error/ServerError" />
    </customErrors>
  </system.web>
</configuration>
```

## 8. 監視とアラート

### Application Insights統合
```csharp
public class TelemetryInitializer : ITelemetryInitializer
{
    public void Initialize(ITelemetry telemetry)
    {
        telemetry.Context.Component.Version = Assembly.GetExecutingAssembly().GetName().Version.ToString();
        telemetry.Context.GlobalProperties["Environment"] = ConfigurationManager.AppSettings["Environment"];
        telemetry.Context.GlobalProperties["BuildNumber"] = ConfigurationManager.AppSettings["BuildNumber"];
    }
}

// Global.asax.cs
protected void Application_Start()
{
    TelemetryConfiguration.Active.TelemetryInitializers.Add(new TelemetryInitializer());
    TelemetryConfiguration.Active.InstrumentationKey = ConfigurationManager.AppSettings["ApplicationInsightsKey"];
}
```

これらのCI/CD設定により、.NET Framework 4.8アプリケーションの継続的な開発とデプロイメントが実現できます。