// OpenAI o3モデル動作確認テスト
const OpenAI = require('openai');

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

// o3-mini モデルテスト (low, medium, high)
async function testO3Mini(reasoningEffort = 'medium') {
    console.log(`\n🧪 o3-mini テスト (reasoning effort: ${reasoningEffort})`);
    
    try {
        const completion = await client.chat.completions.create({
            model: 'o3-mini',
            messages: [
                {
                    role: 'user', 
                    content: 'このテストはVue.js + Supabase仕様書駆動開発システムのo3 MCP統合確認です。簡潔に応答してください。'
                }
            ],
            reasoning_effort: reasoningEffort,
            max_completion_tokens: 150
        });
        
        console.log(`✅ o3-mini (${reasoningEffort}) 応答成功:`);
        console.log(`   ${completion.choices[0].message.content}`);
        console.log(`   使用トークン: ${completion.usage?.total_tokens || 'N/A'}`);
        return true;
        
    } catch (error) {
        console.log(`❌ o3-mini (${reasoningEffort}) エラー: ${error.message}`);
        return false;
    }
}

// o3標準モデルテスト
async function testO3Standard(reasoningEffort = 'medium') {
    console.log(`\n🧪 o3-2025-04-16 テスト (reasoning effort: ${reasoningEffort})`);
    
    try {
        const completion = await client.chat.completions.create({
            model: 'o3-2025-04-16',
            messages: [
                {
                    role: 'user',
                    content: 'システムアーキテクチャ分析: Vue.js + Supabaseの最適な構成を簡潔に推奨してください。'
                }
            ],
            reasoning_effort: reasoningEffort,
            max_completion_tokens: 200
        });
        
        console.log(`✅ o3-2025-04-16 (${reasoningEffort}) 応答成功:`);
        console.log(`   ${completion.choices[0].message.content}`);
        console.log(`   使用トークン: ${completion.usage?.total_tokens || 'N/A'}`);
        return true;
        
    } catch (error) {
        console.log(`❌ o3-2025-04-16 (${reasoningEffort}) エラー: ${error.message}`);
        return false;
    }
}

// 全レベルテスト実行
async function runAllTests() {
    console.log('=== OpenAI o3 モデル動作確認テスト ===');
    console.log(`実行時間: ${new Date().toLocaleString()}`);
    
    const results = {
        'o3-mini-low': false,
        'o3-mini-medium': false, 
        'o3-mini-high': false,
        'o3-standard-low': false,
        'o3-standard-medium': false,
        'o3-standard-high': false
    };
    
    // o3-mini テスト (low, medium, high)
    results['o3-mini-low'] = await testO3Mini('low');
    await sleep(1000); // API制限対策
    
    results['o3-mini-medium'] = await testO3Mini('medium');
    await sleep(1000);
    
    results['o3-mini-high'] = await testO3Mini('high');
    await sleep(1000);
    
    // o3-2025-04-16 テスト (low, medium, high)
    results['o3-standard-low'] = await testO3Standard('low');
    await sleep(1000);
    
    results['o3-standard-medium'] = await testO3Standard('medium');
    await sleep(1000);
    
    results['o3-standard-high'] = await testO3Standard('high');
    
    // 結果サマリー
    console.log('\n=== テスト結果サマリー ===');
    let successCount = 0;
    for (const [test, success] of Object.entries(results)) {
        const status = success ? '✅' : '❌';
        console.log(`${status} ${test}: ${success ? '成功' : '失敗'}`);
        if (success) successCount++;
    }
    
    console.log(`\n📊 成功率: ${successCount}/6 (${Math.round(successCount/6*100)}%)`);
    
    if (successCount === 6) {
        console.log('🎉 全てのo3モデル・レベルが正常動作しています！');
        console.log('🚀 マルチAI開発システム（Claude Code + Gemini CLI + o3 MCP）準備完了');
    } else if (successCount > 0) {
        console.log('⚠️  一部のモデル・レベルで制限があります');
        console.log('💡 API制限またはアクセス権限を確認してください');
    } else {
        console.log('❌ o3モデルにアクセスできません');
        console.log('🔑 API키 권한 또는 사용량 제한을 확인해주세요');
    }
    
    return results;
}

// 유틸리티 함수
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 메인 실행
runAllTests().then(results => {
    console.log('\n📝 다음 단계: 성공한 모델들을 MCP 설정에 통합');
}).catch(error => {
    console.error('테스트 실행 오류:', error.message);
});