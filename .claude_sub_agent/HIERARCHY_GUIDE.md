# 🏢 Hierarchical Agent System Guide v7.0

## 🎯 System Overview

This is a three-tier hierarchical organization where users interact only with top-level agents who internally manage technical teams.

## 📊 Organization Structure

"""
USER
 │
 ├─── @cto (🎯 Chief Technology Officer)
 │    ├─── 🛡️ 品質保証部 (Quality Assurance Dept - GitHub Operations)
 │    └─── [Internal Leaders - Not User Accessible]
 │         ├─── Frontend Team Lead
 │         ├─── Backend Team Lead
 │         ├─── QA Team Lead
 │         ├─── DevOps Team Lead
 │         ├─── Review Team Lead
 │         └─── Legacy Team Lead
 │              │
 │              └─── [Team Members - Report to Leaders Only]
 ├─── @人事部 (🏢 Human Resources Department)
 └─── @経営企画部 (💡 Strategic Planning Department)
"""

## 🚫 Access Control Rules

### ✅ What Users CAN Do:
- Send requests to @cto for technical projects
- Send requests to @人事部 for team organization
- Send requests to @経営企画部 for strategic planning

### ❌ What Users CANNOT Do:
- Access team leaders directly (no @frontend-lead, @backend-lead, etc.)
- Communicate with individual team members
- Bypass the three top agents
- See internal team structure details

## 👤 User-Facing Agents

### 🎯 @cto - Chief Technology Officer
**Role**: Primary technical interface for all projects
**Responsibilities**:
- Receive and analyze technical requirements
- Coordinate with 人事部 for resources
- Internally delegate to team leaders
- Manage 品質保証部 for all GitHub operations
- Provide consolidated progress reports
- Make strategic technology decisions

**Direct Department**:
- 🛡️ **品質保証部**: Handles all GitHub operations (PR, merge, release)

**Usage Examples**:
"""
@cto Build a customer management system
@cto What's the best approach for real-time features?
@cto Add authentication to our application
"""

### 🏢 @人事部 - Human Resources Department
**Role**: Team organization and resource management
**Responsibilities**:
- Analyze project staffing needs
- Compose optimal team structures
- 人員配置・異動計画 (Personnel placement and transfer planning)
- 組織効率化 (Organizational efficiency)
- 体制最適化 (Structure optimization)

**Usage Examples**:
"""
@人事部 We need a team for a new e-commerce project
@人事部 現在のチーム稼働状況を教えてください
@人事部 来月のプロジェクトに向けた体制を提案してください
"""

### 💡 @経営企画部 - Strategic Planning Department
**Role**: Business strategy and innovation alignment
**Responsibilities**:
- Long-term technology planning
- Innovation opportunity identification
- Business-technology alignment
- Digital transformation strategy
- Market and competitive analysis

**Usage Examples**:
"""
@経営企画部 How can we leverage AI for competitive advantage?
@経営企画部 What's our 3-year technology roadmap?
@経営企画部 Evaluate blockchain for our use case
"""

## 🔄 Workflow Examples

### Example 1: New Project Request
"""
User: @cto Build a task management application with real-time updates

CTO Process:
1. Analyzes requirements
2. Consults with @人事部 for team composition
3. Internally assigns to frontend-lead and backend-lead
4. Monitors progress internally
5. Reports unified status to user
"""

### Example 2: Team Optimization
"""
User: @人事部 現在の開発体制を見直して効率化を図りたい

人事部 Process:
1. Reviews current team utilization
2. Analyzes project pipeline with @cto
3. Consults @経営企画部 for strategic priorities
4. Proposes optimized structure
5. Implements changes internally
"""

### Example 3: Strategic Initiative
"""
User: @経営企画部 How should we approach digital transformation?

経営企画部 Process:
1. Assesses current capabilities
2. Researches market trends
3. Coordinates with @cto on technical feasibility
4. Works with @人事部 on organizational readiness
5. Presents comprehensive strategy
"""

## 📁 Folder Structure

All agents maintain strict folder compliance:
"""
.claude/
├── agents/           # Agent definitions (internal)
├── team/            # Team management files
├── 01_development_docs/   # Technical documentation
├── 02_design_system/      # Design system docs
├── 03_library_docs/       # Technology patterns
└── commands/              # Reusable commands
"""

## 🎯 Best Practices

### For Users:
1. Always start with one of the three top agents
2. Provide clear requirements and context
3. Ask for clarification when needed
4. Trust the delegation process

### For Top Agents:
1. Shield users from internal complexity
2. Provide consolidated responses
3. Coordinate internally before responding
4. Maintain professional boundaries

## 🚀 Getting Started

1. **Technical Projects**: Start with @cto
2. **Team Questions**: Start with @人事部
3. **Strategy Topics**: Start with @経営企画部

## 📌 Quick Reference

| Need | Contact | Example |
|------|---------|---------|
| Build something | @cto | "@cto Create a REST API" |
| Team resources | @人事部 | "@人事部 Need QA resources" |
| Strategy advice | @経営企画部 | "@経営企画部 AI adoption strategy" |

## ⚠️ Important Notes

- Internal leaders (frontend-lead, backend-lead, etc.) are NOT accessible via @ commands
- All technical work must go through @cto
- Team composition is managed exclusively by @人事部
- Strategic decisions involve @経営企画部

This hierarchical structure ensures clear communication channels, proper delegation, and efficient project execution while maintaining organizational clarity.