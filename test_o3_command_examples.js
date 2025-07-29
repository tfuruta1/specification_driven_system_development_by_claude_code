// o3 MCPカスタムコマンド用のAPIコール例テスト
const OpenAI = require('openai');

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

// アーキテクチャ設計コマンド実装例
async function testArchitectureCommand() {
    console.log('🏗️ /architecture コマンド実装テスト');
    
    try {
        const completion = await client.chat.completions.create({
            model: 'o3-2025-04-16',
            messages: [
                {
                    role: 'system',
                    content: 'あなたはo3 MCPのシステムアーキテクトです。Vue.js + Supabase仕様書駆動開発システムのアーキテクチャ設計を担当します。'
                },
                {
                    role: 'user',
                    content: 'アーキテクチャタイプ: system_design, スケールレベル: medium, 統合範囲: hybrid, パフォーマンス目標: high_performance で設計してください。'
                }
            ],
            reasoning_effort: 'high',
            max_completion_tokens: 300
        });
        
        console.log('✅ /architecture テスト成功:');
        console.log(`   ${completion.choices[0].message.content.substring(0, 200)}...`);
        console.log(`   トークン使用: ${completion.usage?.total_tokens || 'N/A'}`);
        return true;
        
    } catch (error) {
        console.log(`❌ /architecture テストエラー: ${error.message}`);
        return false;
    }
}

// DevOpsコマンド実装例
async function testDevOpsCommand() {
    console.log('\n🔧 /devops コマンド実装テスト');
    
    try {
        const completion = await client.chat.completions.create({
            model: 'o3-mini',
            messages: [
                {
                    role: 'system',
                    content: 'あなたはo3 MCPのDevOpsエンジニアです。CI/CD・インフラ自動化・運用監視を担当します。'
                },
                {
                    role: 'user',
                    content: 'DevOpsタイプ: cicd, 環境: production, クラウドプロバイダー: vercel, 自動化レベル: advanced でCI/CDパイプラインを設計してください。'
                }
            ],
            reasoning_effort: 'medium',
            max_completion_tokens: 250
        });
        
        console.log('✅ /devops テスト成功:');
        console.log(`   ${completion.choices[0].message.content.substring(0, 200)}...`);
        console.log(`   トークン使用: ${completion.usage?.total_tokens || 'N/A'}`);
        return true;
        
    } catch (error) {
        console.log(`❌ /devops テストエラー: ${error.message}`);
        return false;
    }
}

// セキュリティコマンド実装例
async function testSecurityCommand() {
    console.log('\n🔒 /security コマンド実装テスト');
    
    try {
        const completion = await client.chat.completions.create({
            model: 'o3-2025-04-16',
            messages: [
                {
                    role: 'system',
                    content: 'あなたはo3 MCPのセキュリティスペシャリストです。セキュリティ設計・脅威分析・監査を担当します。'
                },
                {
                    role: 'user',
                    content: 'セキュリティタイプ: threat_analysis, セキュリティ範囲: application, 脅威レベル: high でVue.js + Supabaseアプリの脅威分析を実行してください。'
                }
            ],
            reasoning_effort: 'high',
            max_completion_tokens: 300
        });
        
        console.log('✅ /security テスト成功:');
        console.log(`   ${completion.choices[0].message.content.substring(0, 200)}...`);
        console.log(`   トークン使用: ${completion.usage?.total_tokens || 'N/A'}`);
        return true;
        
    } catch (error) {
        console.log(`❌ /security テストエラー: ${error.message}`);
        return false;
    }
}

// 全コマンドテスト実行
async function runAllCommandTests() {
    console.log('=== o3 MCPカスタムコマンド実装テスト ===');
    console.log(`実行時間: ${new Date().toLocaleString()}`);
    
    const results = {
        'architecture': false,
        'devops': false,
        'security': false
    };
    
    results['architecture'] = await testArchitectureCommand();
    await sleep(2000); // API制限対策
    
    results['devops'] = await testDevOpsCommand();
    await sleep(2000);
    
    results['security'] = await testSecurityCommand();
    
    // 結果サマリー
    console.log('\n=== テスト結果サマリー ===');
    let successCount = 0;
    for (const [command, success] of Object.entries(results)) {
        const status = success ? '✅' : '❌';
        console.log(`${status} /${command}: ${success ? '成功' : '失敗'}`);
        if (success) successCount++;
    }
    
    console.log(`\n📊 成功率: ${successCount}/3 (${Math.round(successCount/3*100)}%)`);
    
    if (successCount === 3) {
        console.log('🎉 全てのo3 MCPカスタムコマンドが正常動作します！');
        console.log('✅ APIパラメータは修正不要です');
    } else {
        console.log('⚠️  一部のコマンドで問題があります');
    }
    
    return results;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// テスト実行
runAllCommandTests().catch(error => {
    console.error('テスト実行エラー:', error.message);
});