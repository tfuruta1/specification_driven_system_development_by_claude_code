/**
 * フルスタック連携用データ同期・バリデーションユーティリティ
 * Vue3 + FastAPI間の完全同期を支援する機能群
 */

import axios from 'axios';
import { z } from 'zod';
import { debounce } from 'lodash';

/**
 * スキーマ同期バリデーター
 * フロントエンド・バックエンド間のスキーマ整合性を検証
 */
export class SchemaSyncValidator {
  constructor(apiBaseUrl = 'http://localhost:9995') {
    this.apiClient = axios.create({
      baseURL: apiBaseUrl,
      timeout: 10000
    });
  }

  /**
   * OpenAPI仕様とフロントエンド型定義の整合性チェック
   */
  async validateSchemaConsistency(openApiSpec, frontendTypes) {
    const inconsistencies = [];
    
    // OpenAPI Componentsとフロントエンド型の比較
    const openApiSchemas = openApiSpec.components?.schemas || {};
    
    for (const [schemaName, openApiSchema] of Object.entries(openApiSchemas)) {
      const frontendType = frontendTypes[schemaName];
      
      if (!frontendType) {
        inconsistencies.push({
          type: 'missing_frontend_type',
          schema: schemaName,
          message: `Frontend type definition missing for ${schemaName}`
        });
        continue;
      }
      
      // プロパティレベルの整合性チェック
      const propertyInconsistencies = this.validateProperties(
        openApiSchema.properties || {},
        frontendType.properties || {},
        schemaName
      );
      
      inconsistencies.push(...propertyInconsistencies);
    }
    
    return {
      isConsistent: inconsistencies.length === 0,
      inconsistencies,
      summary: {
        total_schemas: Object.keys(openApiSchemas).length,
        consistent_schemas: Object.keys(openApiSchemas).length - inconsistencies.filter(i => i.type === 'missing_frontend_type').length,
        consistency_rate: ((Object.keys(openApiSchemas).length - inconsistencies.filter(i => i.type === 'missing_frontend_type').length) / Object.keys(openApiSchemas).length * 100).toFixed(2)
      }
    };
  }

  /**
   * プロパティレベルの整合性チェック
   */
  validateProperties(openApiProps, frontendProps, schemaName) {
    const inconsistencies = [];
    
    for (const [propName, openApiProp] of Object.entries(openApiProps)) {
      const frontendProp = frontendProps[propName];
      
      if (!frontendProp) {
        inconsistencies.push({
          type: 'missing_frontend_property',
          schema: schemaName,
          property: propName,
          message: `Property ${propName} missing in frontend type ${schemaName}`
        });
        continue;
      }
      
      // 型の一致チェック
      const expectedType = this.mapOpenApiTypeToTypeScript(openApiProp);
      if (expectedType !== frontendProp.type) {
        inconsistencies.push({
          type: 'type_mismatch',
          schema: schemaName,
          property: propName,
          expected: expectedType,
          actual: frontendProp.type,
          message: `Type mismatch for ${schemaName}.${propName}: expected ${expectedType}, got ${frontendProp.type}`
        });
      }
    }
    
    return inconsistencies;
  }

  /**
   * OpenAPI型からTypeScript型へのマッピング
   */
  mapOpenApiTypeToTypeScript(openApiProp) {
    const typeMap = {
      'integer': 'number',
      'number': 'number',
      'string': 'string',
      'boolean': 'boolean',
      'array': 'Array',
      'object': 'Record<string, any>'
    };
    
    if (openApiProp.enum) {
      return openApiProp.enum.map(v => `'${v}'`).join(' | ');
    }
    
    if (openApiProp.format === 'date-time') {
      return 'string'; // ISO 8601 format
    }
    
    return typeMap[openApiProp.type] || 'any';
  }

  /**
   * バックエンドAPIとの実時間整合性チェック
   */
  async validateRuntimeConsistency(endpoint, sampleData) {
    try {
      // バックエンドのバリデーションエンドポイントでチェック
      const response = await this.apiClient.post(`${endpoint}/validate`, sampleData);
      
      return {
        isValid: true,
        validationResult: response.data
      };
    } catch (error) {
      return {
        isValid: false,
        errors: error.response?.data?.error?.details || [error.message],
        statusCode: error.response?.status
      };
    }
  }
}

/**
 * データ同期マネージャー
 * フロントエンド・バックエンド間のデータ同期を管理
 */
export class DataSyncManager {
  constructor(config = {}) {
    this.config = {
      syncInterval: 30000, // 30秒間隔
      retryAttempts: 3,
      retryDelay: 1000,
      enableRealtime: true,
      ...config
    };
    
    this.syncState = new Map();
    this.syncCallbacks = new Map();
    this.websocket = null;
    
    if (this.config.enableRealtime) {
      this.initializeWebSocket();
    }
  }

  /**
   * WebSocket接続初期化（リアルタイム同期用）
   */
  initializeWebSocket() {
    const wsUrl = this.config.websocketUrl || 'ws://localhost:9995/ws';
    
    this.websocket = new WebSocket(wsUrl);
    
    this.websocket.onopen = () => {
      console.log('DataSync WebSocket connected');
    };
    
    this.websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleRealtimeSync(message);
    };
    
    this.websocket.onclose = () => {
      console.log('DataSync WebSocket disconnected, attempting reconnect...');
      setTimeout(() => this.initializeWebSocket(), 5000);
    };
    
    this.websocket.onerror = (error) => {
      console.error('DataSync WebSocket error:', error);
    };
  }

  /**
   * リアルタイム同期メッセージハンドラ
   */
  handleRealtimeSync(message) {
    const { type, entity, data, timestamp } = message;
    
    switch (type) {
      case 'entity_updated':
        this.notifySyncCallbacks(entity, 'update', data);
        break;
      case 'entity_deleted':
        this.notifySyncCallbacks(entity, 'delete', data);
        break;
      case 'schema_changed':
        this.notifySyncCallbacks('schema', 'change', data);
        break;
    }
  }

  /**
   * 同期コールバック通知
   */
  notifySyncCallbacks(entity, action, data) {
    const callbacks = this.syncCallbacks.get(entity) || [];
    callbacks.forEach(callback => {
      try {
        callback({ action, data, timestamp: new Date().toISOString() });
      } catch (error) {
        console.error('Sync callback error:', error);
      }
    });
  }

  /**
   * エンティティ同期の登録
   */
  registerSync(entity, store, config = {}) {
    const syncConfig = {
      autoSync: true,
      bidirectional: false,
      conflictResolution: 'server_wins',
      ...config
    };
    
    this.syncState.set(entity, {
      store,
      config: syncConfig,
      lastSync: null,
      pendingChanges: []
    });
    
    // ストアの変更監視
    if (syncConfig.bidirectional) {
      this.watchStoreChanges(entity, store);
    }
    
    // 定期同期開始
    if (syncConfig.autoSync) {
      this.startPeriodicSync(entity);
    }
  }

  /**
   * ストア変更の監視
   */
  watchStoreChanges(entity, store) {
    // Piniaストアの$subscribeを使用して変更を監視
    store.$subscribe((mutation, state) => {
      const syncState = this.syncState.get(entity);
      
      syncState.pendingChanges.push({
        type: mutation.type,
        payload: mutation.payload,
        timestamp: new Date().toISOString()
      });
      
      // デバウンス付きで同期実行
      this.debouncedSync(entity);
    });
  }

  /**
   * デバウンス付き同期実行
   */
  debouncedSync = debounce((entity) => {
    this.syncEntity(entity);
  }, 1000);

  /**
   * 定期同期開始
   */
  startPeriodicSync(entity) {
    const interval = setInterval(() => {
      this.syncEntity(entity);
    }, this.config.syncInterval);
    
    const syncState = this.syncState.get(entity);
    syncState.syncInterval = interval;
  }

  /**
   * エンティティ同期実行
   */
  async syncEntity(entity) {
    const syncState = this.syncState.get(entity);
    if (!syncState) return;
    
    const { store, config, pendingChanges } = syncState;
    
    try {
      // サーバーから最新データ取得
      const serverData = await this.fetchServerData(entity);
      
      // 競合解決
      if (pendingChanges.length > 0) {
        const resolvedData = await this.resolveConflicts(
          entity,
          serverData,
          pendingChanges,
          config.conflictResolution
        );
        
        // ストア更新
        store.$patch(resolvedData);
        
        // 保留中の変更をクリア
        syncState.pendingChanges = [];
      } else {
        // 単純な更新
        store.$patch(serverData);
      }
      
      syncState.lastSync = new Date().toISOString();
      
    } catch (error) {
      console.error(`Sync failed for entity ${entity}:`, error);
      this.retrySync(entity);
    }
  }

  /**
   * サーバーデータ取得
   */
  async fetchServerData(entity) {
    // 実装は具体的なAPIエンドポイントに依存
    const response = await axios.get(`/api/v1/${entity}/sync`);
    return response.data;
  }

  /**
   * 競合解決
   */
  async resolveConflicts(entity, serverData, localChanges, strategy) {
    switch (strategy) {
      case 'server_wins':
        return serverData;
      
      case 'client_wins':
        // ローカル変更をサーバーに送信
        await this.pushLocalChanges(entity, localChanges);
        return this.applyLocalChanges(serverData, localChanges);
      
      case 'merge':
        return this.mergeChanges(serverData, localChanges);
      
      case 'manual':
        return this.requestManualResolution(entity, serverData, localChanges);
      
      default:
        return serverData;
    }
  }

  /**
   * ローカル変更のサーバーへの送信
   */
  async pushLocalChanges(entity, changes) {
    for (const change of changes) {
      try {
        await axios.post(`/api/v1/${entity}/sync/changes`, change);
      } catch (error) {
        console.error('Failed to push local change:', error);
      }
    }
  }

  /**
   * 同期リトライ
   */
  async retrySync(entity, attempt = 1) {
    if (attempt > this.config.retryAttempts) {
      console.error(`Sync retry limit exceeded for entity ${entity}`);
      return;
    }
    
    await new Promise(resolve => 
      setTimeout(resolve, this.config.retryDelay * attempt)
    );
    
    try {
      await this.syncEntity(entity);
    } catch (error) {
      this.retrySync(entity, attempt + 1);
    }
  }
}

/**
 * バリデーションルール同期器
 * フロントエンド・バックエンド間のバリデーションルールを統一
 */
export class ValidationSyncManager {
  constructor() {
    this.validationSchemas = new Map();
    this.zodSchemas = new Map();
  }

  /**
   * バックエンドPydanticスキーマからZodスキーマ生成
   */
  generateZodSchema(pydanticSchema) {
    const zodFields = {};
    
    for (const [fieldName, fieldConfig] of Object.entries(pydanticSchema.fields || {})) {
      zodFields[fieldName] = this.convertPydanticFieldToZod(fieldConfig);
    }
    
    return z.object(zodFields);
  }

  /**
   * Pydanticフィールドの Zod変換
   */
  convertPydanticFieldToZod(fieldConfig) {
    let zodField;
    
    // 基本型マッピング
    switch (fieldConfig.type) {
      case 'str':
        zodField = z.string();
        break;
      case 'int':
        zodField = z.number().int();
        break;
      case 'float':
        zodField = z.number();
        break;
      case 'bool':
        zodField = z.boolean();
        break;
      case 'datetime':
        zodField = z.string().datetime();
        break;
      default:
        zodField = z.any();
    }
    
    // 制約の適用
    if (fieldConfig.constraints) {
      const constraints = fieldConfig.constraints;
      
      if (constraints.min_length !== undefined) {
        zodField = zodField.min(constraints.min_length);
      }
      
      if (constraints.max_length !== undefined) {
        zodField = zodField.max(constraints.max_length);
      }
      
      if (constraints.pattern) {
        zodField = zodField.regex(new RegExp(constraints.pattern));
      }
      
      if (constraints.ge !== undefined) {
        zodField = zodField.min(constraints.ge);
      }
      
      if (constraints.le !== undefined) {
        zodField = zodField.max(constraints.le);
      }
    }
    
    // 必須・オプショナル
    if (!fieldConfig.required) {
      zodField = zodField.optional();
    }
    
    return zodField;
  }

  /**
   * Vue3フォームバリデーション関数生成
   */
  generateVueValidationRules(pydanticSchema) {
    const validationRules = {};
    
    for (const [fieldName, fieldConfig] of Object.entries(pydanticSchema.fields || {})) {
      validationRules[fieldName] = this.convertToVueRules(fieldConfig);
    }
    
    return validationRules;
  }

  /**
   * Vue用バリデーションルール変換
   */
  convertToVueRules(fieldConfig) {
    const rules = [];
    
    // 必須チェック
    if (fieldConfig.required) {
      rules.push({
        required: true,
        message: fieldConfig.error_messages?.required || `${fieldConfig.name || 'Field'} is required`,
        trigger: 'blur'
      });
    }
    
    // 長さチェック
    if (fieldConfig.constraints?.min_length !== undefined) {
      rules.push({
        min: fieldConfig.constraints.min_length,
        message: fieldConfig.error_messages?.min_length || `Minimum length is ${fieldConfig.constraints.min_length}`,
        trigger: 'blur'
      });
    }
    
    if (fieldConfig.constraints?.max_length !== undefined) {
      rules.push({
        max: fieldConfig.constraints.max_length,
        message: fieldConfig.error_messages?.max_length || `Maximum length is ${fieldConfig.constraints.max_length}`,
        trigger: 'blur'
      });
    }
    
    // パターンチェック
    if (fieldConfig.constraints?.pattern) {
      rules.push({
        pattern: new RegExp(fieldConfig.constraints.pattern),
        message: fieldConfig.error_messages?.pattern || 'Invalid format',
        trigger: 'blur'
      });
    }
    
    // 数値範囲チェック
    if (fieldConfig.constraints?.ge !== undefined) {
      rules.push({
        type: 'number',
        min: fieldConfig.constraints.ge,
        message: fieldConfig.error_messages?.ge || `Value must be at least ${fieldConfig.constraints.ge}`,
        trigger: 'blur'
      });
    }
    
    return rules;
  }

  /**
   * バリデーション同期実行
   */
  async syncValidationRules(entity, backendSchema) {
    // Zodスキーマ生成
    const zodSchema = this.generateZodSchema(backendSchema);
    this.zodSchemas.set(entity, zodSchema);
    
    // Vue バリデーションルール生成
    const vueRules = this.generateVueValidationRules(backendSchema);
    this.validationSchemas.set(entity, vueRules);
    
    return {
      zodSchema,
      vueRules,
      syncTimestamp: new Date().toISOString()
    };
  }

  /**
   * エンティティ バリデーション実行
   */
  validateEntity(entity, data) {
    const zodSchema = this.zodSchemas.get(entity);
    
    if (!zodSchema) {
      throw new Error(`No validation schema found for entity: ${entity}`);
    }
    
    try {
      const validatedData = zodSchema.parse(data);
      return {
        isValid: true,
        data: validatedData
      };
    } catch (error) {
      return {
        isValid: false,
        errors: error.errors.map(err => ({
          path: err.path.join('.'),
          message: err.message,
          code: err.code
        }))
      };
    }
  }
}

/**
 * 連携テストマネージャー
 * フロントエンド・バックエンド間の統合テストを管理
 */
export class IntegrationTestManager {
  constructor(config = {}) {
    this.config = {
      apiBaseUrl: 'http://localhost:9995',
      timeout: 30000,
      retryAttempts: 3,
      ...config
    };
    
    this.testResults = [];
    this.apiClient = axios.create({
      baseURL: this.config.apiBaseUrl,
      timeout: this.config.timeout
    });
  }

  /**
   * API契約テスト実行
   */
  async runContractTests(testScenarios) {
    const results = [];
    
    for (const scenario of testScenarios) {
      const result = await this.executeContractTest(scenario);
      results.push(result);
    }
    
    return {
      totalTests: results.length,
      passed: results.filter(r => r.passed).length,
      failed: results.filter(r => !r.passed).length,
      results
    };
  }

  /**
   * 個別契約テスト実行
   */
  async executeContractTest(scenario) {
    const { name, endpoint, test_cases } = scenario;
    const testResults = [];
    
    for (const testCase of test_cases) {
      try {
        const result = await this.executeTestCase(endpoint, testCase);
        testResults.push(result);
      } catch (error) {
        testResults.push({
          scenario: testCase.scenario,
          passed: false,
          error: error.message
        });
      }
    }
    
    return {
      scenario: name,
      endpoint,
      totalCases: testResults.length,
      passed: testResults.filter(r => r.passed).length,
      failed: testResults.filter(r => !r.passed).length,
      testResults
    };
  }

  /**
   * テストケース実行
   */
  async executeTestCase(endpoint, testCase) {
    const { scenario, request, expected_response } = testCase;
    
    // HTTPリクエスト実行
    const [method, path] = endpoint.split(' ');
    
    let response;
    try {
      switch (method.toUpperCase()) {
        case 'GET':
          response = await this.apiClient.get(path, { params: request.params });
          break;
        case 'POST':
          response = await this.apiClient.post(path, request.body);
          break;
        case 'PUT':
          response = await this.apiClient.put(path, request.body);
          break;
        case 'DELETE':
          response = await this.apiClient.delete(path);
          break;
        default:
          throw new Error(`Unsupported HTTP method: ${method}`);
      }
    } catch (error) {
      response = error.response;
    }
    
    // レスポンス検証
    const validationResult = this.validateResponse(response, expected_response);
    
    return {
      scenario,
      passed: validationResult.isValid,
      response: {
        status: response?.status,
        data: response?.data
      },
      validation: validationResult
    };
  }

  /**
   * レスポンス検証
   */
  validateResponse(response, expectedResponse) {
    const validations = [];
    
    // ステータスコード検証
    if (response?.status !== expectedResponse.status) {
      validations.push({
        type: 'status_mismatch',
        expected: expectedResponse.status,
        actual: response?.status,
        message: `Status code mismatch: expected ${expectedResponse.status}, got ${response?.status}`
      });
    }
    
    // 必須フィールド検証
    if (expectedResponse.required_fields) {
      for (const field of expectedResponse.required_fields) {
        if (!(field in (response?.data || {}))) {
          validations.push({
            type: 'missing_field',
            field,
            message: `Required field '${field}' is missing from response`
          });
        }
      }
    }
    
    // スキーマ検証（簡易版）
    if (expectedResponse.schema_validation && response?.data) {
      const schemaValidation = this.validateSchema(
        response.data,
        expectedResponse.schema_validation
      );
      
      if (!schemaValidation.isValid) {
        validations.push(...schemaValidation.errors);
      }
    }
    
    return {
      isValid: validations.length === 0,
      validations
    };
  }

  /**
   * スキーマ検証（簡易版）
   */
  validateSchema(data, schemaName) {
    // 実際の実装では、事前に登録されたスキーマと照合
    // ここでは簡易的な検証を行う
    
    const errors = [];
    
    if (typeof data !== 'object' || data === null) {
      errors.push({
        type: 'schema_violation',
        message: `Expected object for schema ${schemaName}, got ${typeof data}`
      });
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

// デフォルトエクスポート
export default {
  SchemaSyncValidator,
  DataSyncManager,
  ValidationSyncManager,
  IntegrationTestManager
};