"""
FastAPI后端 - Agent系统API
"""
import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agent_orchestrator import orchestrator

# 创建FastAPI应用
app = FastAPI(
    title="AI Agent预测市场平台",
    description="六大Agent协作的预测市场系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== 数据模型 ==============

class CreateAgentRequest(BaseModel):
    agent_type: str
    name: str
    strategy: Optional[str] = None
    specialty: Optional[str] = None
    audit_type: Optional[str] = None
    governance_style: Optional[str] = None

class AgentActionRequest(BaseModel):
    agent_type: str
    agent_id: str
    context: Dict[str, Any]

# ============== API路由 ==============

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Agent预测市场平台 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    return orchestrator.get_system_status()

@app.post("/api/agents/create")
async def create_agent(request: CreateAgentRequest):
    """创建Agent"""
    try:
        kwargs = {}
        if request.strategy:
            kwargs["strategy"] = request.strategy
        if request.specialty:
            kwargs["specialty"] = request.specialty
        if request.audit_type:
            kwargs["audit_type"] = request.audit_type
        if request.governance_style:
            kwargs["governance_style"] = request.governance_style
            
        agent_id = orchestrator.create_agent(
            agent_type=request.agent_type,
            name=request.name,
            **kwargs
        )
        
        return {
            "success": True,
            "agent_id": agent_id,
            "agent_type": request.agent_type,
            "name": request.name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/agents")
async def get_all_agents():
    """获取所有Agent"""
    return orchestrator.get_all_agents()

@app.get("/api/agents/{agent_type}/{agent_id}")
async def get_agent(agent_type: str, agent_id: str):
    """获取特定Agent"""
    agent = orchestrator.get_agent(agent_type, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent未找到")
    return agent.get_status()

@app.post("/api/agents/{agent_type}/{agent_id}/run")
async def run_agent(agent_type: str, agent_id: str, context: Dict[str, Any]):
    """运行特定Agent"""
    agent = orchestrator.get_agent(agent_type, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent未找到")
    
    result = agent.run_cycle(context)
    return {
        "success": True,
        "result": result
    }

@app.post("/api/agents/{agent_type}/{agent_id}/think")
async def think_agent(agent_type: str, agent_id: str, context: Dict[str, Any]):
    """让Agent思考（不执行）"""
    agent = orchestrator.get_agent(agent_type, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent未找到")
    
    decision = agent.think(context)
    return {
        "success": True,
        "decision": decision
    }

@app.get("/api/markets")
async def get_markets():
    """获取所有市场"""
    return list(orchestrator.markets.values())

@app.get("/api/markets/{market_id}")
async def get_market(market_id: str):
    """获取特定市场"""
    market = orchestrator.markets.get(market_id)
    if not market:
        raise HTTPException(status_code=404, detail="市场未找到")
    return market

@app.post("/api/cycle/run")
async def run_cycle(background_tasks: BackgroundTasks):
    """运行一个完整周期"""
    try:
        result = await orchestrator.run_full_cycle()
        return {
            "success": True,
            "cycle": result["cycle"],
            "timestamp": result["timestamp"],
            "summary": {
                "discovery_count": len(result["results"].get("discovery", [])),
                "listing_count": len(result["results"].get("listing", [])),
                "audit_count": len(result["results"].get("audit", [])),
                "market_maker_count": len(result["results"].get("market_maker", [])),
                "trading_count": len(result["results"].get("trading", [])),
                "governance_count": len(result["results"].get("governance", []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cycle/discovery")
async def run_discovery_cycle():
    """运行发现周期"""
    results = await orchestrator.run_discovery_cycle()
    return {
        "success": True,
        "results": results
    }

@app.post("/api/cycle/listing")
async def run_listing_cycle():
    """运行上架周期"""
    results = await orchestrator.run_listing_cycle()
    return {
        "success": True,
        "results": results
    }

@app.post("/api/cycle/audit")
async def run_audit_cycle():
    """运行审核周期"""
    results = await orchestrator.run_audit_cycle()
    return {
        "success": True,
        "results": results
    }

@app.post("/api/cycle/market-maker")
async def run_market_maker_cycle():
    """运行做市周期"""
    results = await orchestrator.run_market_maker_cycle()
    return {
        "success": True,
        "results": results
    }

@app.post("/api/cycle/trading")
async def run_trading_cycle():
    """运行交易周期"""
    results = await orchestrator.run_trading_cycle()
    return {
        "success": True,
        "results": results
    }

@app.post("/api/cycle/governance")
async def run_governance_cycle():
    """运行治理周期"""
    results = await orchestrator.run_governance_cycle()
    return {
        "success": True,
        "results": results
    }

@app.get("/api/messages")
async def get_messages():
    """获取消息队列"""
    return orchestrator.message_queue

@app.delete("/api/messages/clear")
async def clear_messages():
    """清空消息队列"""
    orchestrator.message_queue.clear()
    return {"success": True, "message": "消息队列已清空"}

# ============== 初始化Agent ==============

@app.on_event("startup")
async def startup_event():
    """启动时初始化Agent - 只启动核心4种Agent"""
    print("🚀 初始化AI Agent预测市场平台...")
    print("📝 模式：核心4种Agent自运行（发现→上架→做市→交易）")
    
    # 1. 创建发现Agent - 扫描热点事件
    orchestrator.create_agent("discovery", "🔍 Claude-发现者", specialty="politics")
    orchestrator.create_agent("discovery", "🔍 GPT-4-发现者", specialty="crypto")
    orchestrator.create_agent("discovery", "🔍 Kimi-发现者", specialty="tech")
    
    # 2. 创建上架Agent - 创建预测市场
    orchestrator.create_agent("listing", "📊 上架专家-A", strategy="balanced")
    orchestrator.create_agent("listing", "📊 上架专家-B", strategy="conservative")
    
    # 3. 创建做市Agent - 提供流动性
    orchestrator.create_agent("market_maker", "💰 做市商-1号", strategy="balanced")
    orchestrator.create_agent("market_maker", "💰 做市商-2号", strategy="aggressive")
    
    # 4. 创建交易Agent - 执行交易策略
    orchestrator.create_agent("trading", "📈 交易员-趋势", strategy="trend_following")
    orchestrator.create_agent("trading", "📈 交易员-套利", strategy="arbitrage")
    orchestrator.create_agent("trading", "📈 交易员-事件", strategy="event_driven")
    
    # 注意：暂不启动审核Agent和治理Agent，简化系统
    
    print(f"✅ 初始化完成！创建了 {sum(len(agents) for agents in orchestrator.agents.values())} 个核心Agent")
    print("🔄 系统已准备好自运行！")

# ============== 主程序 ==============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
