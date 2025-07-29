// OpenAI o3モデル接続テスト
const OpenAI = require('openai');

// o3モデルの設定テスト関数
async function testO3Setup() {
    console.log('=== OpenAI o3 MCP セットアップテスト ===');
    
    // API키가 설정되지 않은 경우의 테스트
    try {
        const client = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY || 'test-key-not-set'
        });
        
        console.log('✅ OpenAI SDK 초기화 성공');
        console.log('📋 사용 가능한 o3 reasoning effort 레벨:');
        console.log('   - low: 빠른 추론, 낮은 비용');
        console.log('   - medium: 표준 추론 (기본값)');
        console.log('   - high: 깊은 추론, 높은 정확도');
        
        // API 키 확인
        if (!process.env.OPENAI_API_KEY) {
            console.log('⚠️  OPENAI_API_KEY 환경변수가 설정되지 않았습니다.');
            console.log('📝 설정 방법:');
            console.log('   Windows PowerShell: $env:OPENAI_API_KEY = "sk-your-key-here"');
            console.log('   Windows CMD: set OPENAI_API_KEY=sk-your-key-here');
            console.log('   또는 .env 파일 생성');
            console.log('');
            console.log('🔗 API 키 취득: https://platform.openai.com/api-keys');
            return false;
        }
        
        console.log('✅ OPENAI_API_KEY 설정 확인됨');
        return true;
        
    } catch (error) {
        console.error('❌ OpenAI SDK 설정 오류:', error.message);
        return false;
    }
}

// o3 모델별 설정 표시
function showO3ModelConfigs() {
    console.log('\n=== o3 모델 설정 정보 ===');
    
    const o3Configs = {
        'o3-mini': {
            description: '빠른 추론 모델',
            reasoningEfforts: ['low', 'medium', 'high'],
            useCase: '일반적인 작업, 빠른 응답'
        },
        'o3-2025-04-16': {
            description: '고성능 추론 모델', 
            reasoningEfforts: ['low', 'medium', 'high'],
            useCase: '복잡한 문제 해결, 깊은 분석'
        },
        'o3-pro': {
            description: '최고 성능 추론 모델',
            reasoningEfforts: ['high'],
            useCase: '최고 난이도 문제, 전문적 분석',
            cost: '고비용 ($20/M input, $80/M output tokens)'
        }
    };
    
    for (const [model, config] of Object.entries(o3Configs)) {
        console.log(`\n📊 ${model}:`);
        console.log(`   설명: ${config.description}`);
        console.log(`   추론 레벨: ${config.reasoningEfforts.join(', ')}`);
        console.log(`   사용 사례: ${config.useCase}`);
        if (config.cost) {
            console.log(`   비용: ${config.cost}`);
        }
    }
}

// MCP 설정 가이드 표시
function showMCPSetupGuide() {
    console.log('\n=== MCP (Model Context Protocol) 설정 가이드 ===');
    console.log('🔧 Claude Code에서 o3 MCP 서버 설정:');
    console.log('');
    console.log('1. MCP 서버 설정 파일 생성이 필요합니다.');
    console.log('2. 환경변수 OPENAI_API_KEY 설정이 필요합니다.');
    console.log('3. 각 reasoning effort에 따른 비용 고려가 필요합니다.');
    console.log('');
    console.log('📝 다음 단계: API 키 설정 후 동작 테스트 진행');
}

// 메인 실행
async function main() {
    const setupSuccess = await testO3Setup();
    showO3ModelConfigs();
    showMCPSetupGuide();
    
    if (setupSuccess) {
        console.log('\n🎉 o3 MCP 기본 설정 완료!');
        console.log('📋 다음: API 키 설정 후 동작 테스트');
    } else {
        console.log('\n⚠️  API 키 설정이 필요합니다.');
    }
}

main().catch(console.error);