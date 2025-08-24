# /modeltest - TESTAITEST

## TEST
TESTGemini CLITESTo3 MCPTESTClaude CodeTESTAITESTAI

## AI
- **Claude Code**: 
- **Gemini CLI**: 
- **o3 MCP**: MCP

## MCP

### o3-search-mcp 
```bash
# o3 MCPOpenAI API
claude mcp add o3 -s user \
  -e OPENAI_API_KEY=your_openai_api_key \
  -e SEARCH_CONTEXT_SIZE=medium \
  -e REASONING_EFFORT=medium \
  -- npx o3-search-mcp
```

### Gemini CLI MCP
```bash
# Gemini CLI MCP
claude mcp add gemini-cli -s user -- npx @choplin/mcp-gemini-cli --allow-npx
```

### 
```bash
# MCP
claude mcp list
```

### 
```bash
# MCPTEST
claude mcp remove o3
claude mcp remove gemini-cli

# TEST
```

## TEST
- **TEST**: `$TEST_SCOPE` - TESTbasic, comprehensive, performance, integrationTEST
- **TEST**: `$MODEL_TARGET` - all, gemini, o3_high, o3_standard, o3_low, claudeREPORT
- **REPORT**: `$OUTPUT_FORMAT` - TESTsummary, detailed, json, markdownTEST

## TEST
- **TEST**: `.tmp/modeltest_report_[timestamp].md`
- **TESTAITEST**: `.tmp/ai_test_results/`
- **TEST**: `.tmp/performance_metrics.json`
- **TEST**: `.tmp/optimization_recommendations.md`

## 

### Phase 1: 
```markdown
## 

### 1. Claude Code
- [ ] Claude Code API
- [ ] 
- [ ] 
- [ ] 

### 2. Gemini CLI
- [ ] Gemini CLI API
- [ ] 
- [ ] 
- [ ] 

### 3. o3 MCP
- [ ] o3 MCP API
- [ ] MCP
- [ ] 
- [ ] high/standard/low
```

### Phase 2: 
```markdown
## 

### 1. 
- [ ] Claude Code -> Gemini CLI 
- [ ] Gemini CLI -> o3 MCP 
- [ ] o3 MCP -> Claude Code 
- [ ] 

### 2. 
- [ ] /research -> /content-strategy 
- [ ] /product-plan -> /requirements 
- [ ] /design -> /architecture 
- [ ] /architecture -> /devops -> /security 

### 3. 
- [ ] (.tmp/)
- [ ] (.claude/)
- [ ] 
- [ ] 
```

### Phase 3: 
```markdown
## 

### 1. 
- [ ] Claude Code: 
- [ ] Gemini CLI: 
- [ ] o3 MCP: 
- [ ] 

### 2. 
- [ ] Claude Code: 
- [ ] Gemini CLI: 
- [ ] o3 MCP: 
- [ ] 

### 3. 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
```

### Phase 4: 
```markdown
## 

### 1. 
- [ ] Gemini CLI /research
- [ ] UXGemini CLI /content-strategy
- [ ] Claude Code /requirements
- [ ] o3 MCP /architecture
- [ ] Claude CodeANALYSIS
- [ ] ANALYSISo3 MCP /devopsANALYSIS

### 2. ANALYSIS
- [ ] ANALYSISClaude Code /analyzeANALYSIS
- [ ] ANALYSISGemini CLI /researchANALYSIS
- [ ] ANALYSISClaude Code /refactorANALYSIS
- [ ] o3 MCP /security
- [ ] o3 MCP /devopsANALYSIS

### 3. ANALYSIS
- [ ] ANALYSISo3 MCP monitoringANALYSIS
- [ ] ANALYSISClaude Code /analyzeANALYSIS
- [ ] ANALYSISClaude Code /fixANALYSIS
- [ ] ANALYSISGemini CLI /researchTEST
- [ ] TESTo3 MCP /securityTEST
```

## TEST

### TEST
```yaml
test_basic_connection:
  claude_code:
    command: "TEST"
    expected: "Vue.js + REST APITEST"
    timeout: 30s
    
  gemini_cli:
    command: ": []"
    expected: ""
    timeout: 60s
    
  o3_mcp:
    command: "TEST"
    expected: "TEST"
    timeout: 45s
```

### TEST
```yaml
test_integration_flow:
  scenario: "TEST"
  steps:
    1:
      ai: "gemini_cli"
      command: "/research user_behavior --data_source='analytics'"
      expected_output: ".tmp/research_report_*.md"
      
    2:
      ai: "gemini_cli"
      command: "/content-strategy persona --input='research_report'"
      expected_output: ".tmp/personas/"
      
    3:
      ai: "claude_code"
      command: "/requirements --input='persona_data'"
      expected_output: ".tmp/requirements.md"
      
    4:
      ai: "o3_mcp"
      command: "/architecture system_design --input='requirements'"
      expected_output: ".tmp/architecture_design.md"
      
  validation:
    - file_continuity: ""
    - data_consistency: ""
    - performance: " < 10"
```

## 

### 
```markdown
# AI

## 
- ****: [timestamp]
- ****: [basic/comprehensive/performance/integration]
- **CONFIG**: [all/specific models]
- **CONFIG**: [OS, versions, configurations]

## ERRORAIERROR

### Claude Code
- **ERROR**: [OK] ERROR / [WARNING] ERROR / [ERROR] ERROR
- **ERROR**: [ERROR/ERROR/ERROR] ms
- **ERROR**: 
  - ERROR: [OK]
  - ERROR: [OK]
  - WARNING: [OK]
- **ERROR**: [ERROR]

### Gemini CLI
- **ERROR**: [OK] ERROR / [WARNING] ERROR / [ERROR] ERROR
- **ERROR**: [ERROR/ERROR/ERROR] ms
- **ERROR**:
  - ERROR: [OK]
  - ERROR: [OK]
  - WARNING: [OK]
  - ERROR: [OK]
- **ERROR**: [ERROR]

### o3 MCP
- **ERROR**: [OK] ERROR / [WARNING] ERROR / [ERROR] ERROR
- **ERROR**:
  - o3-high: [OK] ERROR (ERROR: [time]ms)
  - o3-standard: [OK] ERROR (: [time]ms)  
  - o3-low: [OK]  (: [time]ms)
- ****:
  - MCP: [OK]
  - : [OK]
  - : [OK]
- ****: [MCP]

## 

### 
|  |  |  |  |  |
|---------|------|----------|-------------|------|
| Claude -> Gemini | [OK] | 1.2s | [OK] |  |
| Gemini -> o3 | [OK] | 2.1s | [OK] |  |
| o3 -> Claude | [OK] | 0.8s | [OK] |  |
|  | [OK] | 4.5s | [OK] |  |

### 
|  |  |  |  |  |
|----------------|------|-----------|-----------|------|
| /research -> /content-strategy | [OK] | 3.2s | [OK]  |  |
| /product-plan -> /requirements | [OK] | 2.8s | [OK]  |  |
| /design -> /architecture | [OK] | 4.1s | [OK]  |  |
| /architecture -> /devops | [OK] | 5.2s | [OK]  |  |

## 

### 
```json
{
  "claude_code": {
    "average_response_time": "1.2s",
    "max_response_time": "3.1s",
    "min_response_time": "0.3s",
    "percentile_95": "2.8s"
  },
  "gemini_cli": {
    "average_response_time": "2.8s",
    "max_response_time": "8.2s",
    "min_response_time": "0.8s",
    "percentile_95": "6.1s"
  },
  "o3_mcp": {
    "o3_high": {
      "average_response_time": "3.2s",
      "max_response_time": "12.1s",
      "min_response_time": "1.1s"
    },
    "o3_standard": {
      "average_response_time": "1.8s",
      "max_response_time": "5.2s",
      "min_response_time": "0.6s"
    },
    "o3_low": {
      "average_response_time": "0.9s",
      "max_response_time": "2.1s",
      "min_response_time": "0.3s"
    }
  }
}
```

### 
- **Claude Code**:  95%,  92%
- **Gemini CLI**:  98%,  96%
- **o3 MCP**:  94%,  89%

## 

### 
1. **[] - [: High/Medium/Low]**
   - : []
   - : []
   - : []
   - : []

2. **[] - []**
   - []

### 
- **Gemini CLI**: 3
- **o3 MCP**: >10s 
- ****: >30

## 

###  High
1. **[]**
   - : []
   - : []
   - : []
   - : []

###  Medium1
1. **[]**
   - []

###  Low1
1. **[WARNING]**
   - [ERROR]

## ERROR

### ERRORAIERROR
- **ERROR**: [OK] ERROR / [WARNING] ERROR / [ERROR] ERROR
- **ERROR**: [ERROR/ERROR/ERROR]
- **ERROR**: [ERROR]

### ERROR
1. [ERROR]
2. []
3. []

## TEST

### TEST
[TEST]

### TEST
[TEST]
```

## TEST

### TEST
```bash
/modeltest basic
```

### TEST
```bash
/modeltest comprehensive --output_format="detailed"
```

### TEST
```bash
/modeltest --model_target="gemini,o3_high" --test_scope="performance"
```

### TEST
```bash
/modeltest performance --output_format="json"
```

## TEST
- **TEST**: TEST
- **TEST**: TESTAI/research, /architecture, /security
- ****: 

## 
- [ ] AI
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

AI