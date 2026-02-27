# 🤖 AI Agent预测市场平台 - 系统说明

## 📁 文件结构

```
/mnt/okcomputer/output/
├── agent-backend/              # Python后端
│   ├── agents/                 # Agent实现
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Agent基类
│   │   ├── discovery_agent.py  # 发现Agent
│   │   ├── listing_agent.py    # 上架Agent
│   │   ├── audit_agent.py      # 审核Agent
│   │   ├── market_maker_agent.py # 做市Agent
│   │   ├── trading_agent.py    # 交易Agent
│   │   └── governance_agent.py # 治理Agent
│   ├── agent_orchestrator.py   # Agent编排器
│   └── main.py                 # FastAPI后端
├── app/                        # React前端
│   ├── src/
│   │   ├── App.tsx            # 主界面
│   │   └── App.css            # 样式
│   └── dist/                  # 构建输出
├── start_system.py            # 一键启动脚本
└── AGENT_SYSTEM_README.md     # 本文件
```

## 🚀 快速启动

### 1. 安装依赖

后端依赖（已预装）：
```bash
pip install fastapi uvicorn requests beautifulsoup4
```

前端依赖（已安装）：
```bash
cd app && npm install
```

### 2. 配置API密钥（可选）

编辑 `agent-backend/main.py`，设置DeepSeek API密钥：
```python
os.environ["DEEPSEEK_API_KEY"] = "your-api-key"
```

**注意**：如果不设置API密钥，系统会使用模拟数据运行。

### 3. 启动系统

```bash
python3 /mnt/okcomputer/output/start_system.py
```

或者手动启动：

**终端1 - 启动后端：**
```bash
cd /mnt/okcomputer/output/agent-backend
python3 main.py
```

**终端2 - 启动前端：**
```bash
cd /mnt/okcomputer/output/app/dist
python3 -m http.server 3000
```

### 4. 访问系统

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🎯 系统功能

### 六大Agent

| Agent | 功能 | 状态 |
|-------|------|------|
| **发现Agent** | 信息搜集、热点识别、资料整理、趋势预判 | ✅ 已实现 |
| **上架Agent** | 市场评估、定价策略、流动性配置、规则设计 | ✅ 已实现 |
| **审核Agent** | 漏洞检测、公平性审核、合规检查、风险评估 | ✅ 已实现 |
| **做市Agent** | 流动性提供、价差管理、库存平衡、价格稳定 | ✅ 已实现 |
| **交易Agent** | 趋势分析、风险控制、策略执行、收益优化 | ✅ 已实现 |
| **治理Agent** | 结果验证、提案投票、争议处理、生态维护 | ✅ 已实现 |

### 前端界面

- **Agent管理**: 查看所有Agent状态、性能指标
- **预测市场**: 浏览Agent创建的市场
- **运行日志**: 实时查看Agent操作记录
- **周期运行**: 一键启动完整协作周期

### API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/status` | GET | 获取系统状态 |
| `/api/agents` | GET | 获取所有Agent |
| `/api/agents/create` | POST | 创建新Agent |
| `/api/markets` | GET | 获取所有市场 |
| `/api/cycle/run` | POST | 运行完整周期 |
| `/api/cycle/discovery` | POST | 运行发现周期 |
| `/api/cycle/listing` | POST | 运行上架周期 |
| `/api/cycle/audit` | POST | 运行审核周期 |
| `/api/cycle/market-maker` | POST | 运行做市周期 |
| `/api/cycle/trading` | POST | 运行交易周期 |
| `/api/cycle/governance` | POST | 运行治理周期 |

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
│                   React前端 (localhost:3000)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       API层                                  │
│              FastAPI (localhost:8000)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent编排层                               │
│              AgentOrchestrator                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │发现Agent│ │上架Agent│ │审核Agent│ │做市Agent│ ...       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      LLM API层                              │
│         DeepSeek / GPT-4o / Claude API                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Agent协作流程

```
1. 发现Agent扫描信息源 → 发现热点事件
         ↓
2. 上架Agent评估事件 → 创建预测市场
         ↓
3. 审核Agent检查市场 → 审核通过/拒绝
         ↓
4. 做市Agent提供流动性 → 设置买卖报价
         ↓
5. 交易Agent分析市场 → 执行交易策略
         ↓
6. 治理Agent监督平台 → 处理争议、验证结果
```

## 🛠️ 开发指南

### 创建新Agent

```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name, "my_type", "描述")
    
    def think(self, context: dict) -> dict:
        # 实现决策逻辑
        return {"decision": "action"}
    
    def act(self, decision: dict) -> any:
        # 实现执行逻辑
        return {"status": "success"}
```

### 添加新API接口

在 `main.py` 中添加：

```python
@app.post("/api/my-endpoint")
async def my_endpoint():
    # 实现逻辑
    return {"success": True}
```

## 📊 性能监控

每个Agent自动记录：
- 总行动次数
- 成功/失败次数
- 总收益
- 最近行动历史

## ⚠️ 注意事项

1. **API密钥**: 默认使用模拟数据，如需真实LLM响应，请配置DeepSeek API密钥
2. **端口占用**: 确保3000和8000端口未被占用
3. **Python版本**: 需要Python 3.8+
4. **Node版本**: 需要Node.js 18+

## 📝 后续优化

- [ ] 接入真实新闻API
- [ ] 实现区块链交互
- [ ] 添加Agent间通信机制
- [ ] 实现真实交易策略
- [ ] 添加用户投资功能
- [ ] 实现Agent进化系统

## 🤝 贡献

欢迎提交Issue和PR！

## 📄 许可证

MIT License
