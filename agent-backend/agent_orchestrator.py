"""
Agent编排器 - 协调多个Agent的工作流程
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from agents.discovery_agent import DiscoveryAgent
from agents.listing_agent import ListingAgent
from agents.audit_agent import AuditAgent
from agents.market_maker_agent import MarketMakerAgent
from agents.trading_agent import TradingAgent
from agents.governance_agent import GovernanceAgent

class AgentOrchestrator:
    """Agent编排器 - 管理所有Agent的协作"""
    
    def __init__(self):
        self.agents = {
            "discovery": {},
            "listing": {},
            "audit": {},
            "market_maker": {},
            "trading": {},
            "governance": {}
        }
        self.message_queue = []  # 消息队列
        self.markets = {}  # 市场数据
        self.running = False
        self.cycle_count = 0
        
    def create_agent(self, agent_type: str, name: str, **kwargs) -> str:
        """创建Agent实例"""
        agent_id = f"{agent_type}_{len(self.agents[agent_type]) + 1}"
        
        if agent_type == "discovery":
            agent = DiscoveryAgent(name=name, **kwargs)
        elif agent_type == "listing":
            agent = ListingAgent(name=name, **kwargs)
        elif agent_type == "audit":
            agent = AuditAgent(name=name, **kwargs)
        elif agent_type == "market_maker":
            agent = MarketMakerAgent(name=name, **kwargs)
        elif agent_type == "trading":
            agent = TradingAgent(name=name, **kwargs)
        elif agent_type == "governance":
            agent = GovernanceAgent(name=name, **kwargs)
        else:
            raise ValueError(f"未知的Agent类型: {agent_type}")
        
        self.agents[agent_type][agent_id] = agent
        return agent_id
    
    def get_agent(self, agent_type: str, agent_id: str):
        """获取Agent实例"""
        return self.agents[agent_type].get(agent_id)
    
    def get_all_agents(self) -> Dict[str, List[Dict]]:
        """获取所有Agent的状态"""
        result = {}
        for agent_type, agents in self.agents.items():
            result[agent_type] = [agent.get_status() for agent in agents.values()]
        return result
    
    async def run_discovery_cycle(self):
        """运行发现周期"""
        tasks = []
        for agent_id, agent in self.agents["discovery"].items():
            context = {"timestamp": datetime.now().isoformat()}
            task = asyncio.create_task(self._run_agent_cycle(agent, context))
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, dict) and "result" in result:
                    # result["result"] 是Agent.run_cycle的返回结果
                    agent_result = result["result"]
                    if isinstance(agent_result, dict) and "result" in agent_result:
                        event = agent_result["result"].get("event")
                        if event:
                            # 通知上架Agent
                            await self._notify_listing_agents(event)
            return results
        return []
    
    async def run_listing_cycle(self):
        """运行上架周期"""
        tasks = []
        for agent_id, agent in self.agents["listing"].items():
            # 获取待处理的事件
            pending_events = self._get_pending_events()
            for event in pending_events:
                context = {"event": event}
                task = asyncio.create_task(self._run_agent_cycle(agent, context))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, dict) and "result" in result:
                    agent_result = result["result"]
                    if isinstance(agent_result, dict) and "result" in agent_result:
                        market = agent_result["result"].get("market")
                        if market:
                            # 保存市场
                            self.markets[market["id"]] = market
                            # 通知审核Agent
                            await self._notify_audit_agents(market)
            return results
        return []
    
    async def run_audit_cycle(self):
        """运行审核周期"""
        tasks = []
        for agent_id, agent in self.agents["audit"].items():
            # 获取待审核的市场
            pending_markets = self._get_pending_markets()
            for market in pending_markets:
                context = {"market": market}
                task = asyncio.create_task(self._run_agent_cycle(agent, context))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, dict) and "result" in result:
                    agent_result = result["result"]
                    if isinstance(agent_result, dict) and "result" in agent_result:
                        audit_decision = agent_result["result"]
                        if audit_decision.get("decision") == "approve":
                            # 从上下文中获取market_id
                            market = agent_result.get("decision", {}).get("market", {})
                            market_id = market.get("id")
                            if market_id:
                                # 通知做市Agent
                                await self._notify_market_makers(self.markets.get(market_id, {}))
            return results
        return []
    
    async def run_market_maker_cycle(self):
        """运行做市周期"""
        tasks = []
        for agent_id, agent in self.agents["market_maker"].items():
            # 获取活跃市场
            active_markets = list(self.markets.values())
            for market in active_markets:
                context = {
                    "market": market,
                    "current_price": 0.5,  # 模拟价格
                    "orderbook": {"bids": [], "asks": []}
                }
                task = asyncio.create_task(self._run_agent_cycle(agent, context))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        return []
    
    async def run_trading_cycle(self):
        """运行交易周期"""
        tasks = []
        for agent_id, agent in self.agents["trading"].items():
            # 获取活跃市场
            active_markets = list(self.markets.values())
            for market in active_markets:
                context = {
                    "market": market,
                    "current_price": 0.5,
                    "price_history": [],
                    "signals": {}
                }
                task = asyncio.create_task(self._run_agent_cycle(agent, context))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        return []
    
    async def run_governance_cycle(self):
        """运行治理周期"""
        tasks = []
        for agent_id, agent in self.agents["governance"].items():
            # 获取待治理事项
            governance_items = self._get_governance_items()
            for item in governance_items:
                context = item
                task = asyncio.create_task(self._run_agent_cycle(agent, context))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        return []
    
    async def _run_agent_cycle(self, agent, context: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个Agent的周期"""
        try:
            result = agent.run_cycle(context)
            return {
                "agent": agent.name,
                "type": agent.agent_type,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "agent": agent.name,
                "type": agent.agent_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _notify_listing_agents(self, event: Dict[str, Any]):
        """通知上架Agent"""
        # 将事件添加到消息队列
        self.message_queue.append({
            "type": "new_event",
            "data": event,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _notify_audit_agents(self, market: Dict[str, Any]):
        """通知审核Agent"""
        self.message_queue.append({
            "type": "new_market",
            "data": market,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _notify_market_makers(self, market: Dict[str, Any]):
        """通知做市Agent"""
        self.message_queue.append({
            "type": "market_approved",
            "data": market,
            "timestamp": datetime.now().isoformat()
        })
    
    def _get_pending_events(self) -> List[Dict]:
        """获取待处理的事件"""
        events = []
        for msg in self.message_queue:
            if msg["type"] == "new_event":
                events.append(msg["data"])
        return events
    
    def _get_pending_markets(self) -> List[Dict]:
        """获取待审核的市场"""
        markets = []
        for msg in self.message_queue:
            if msg["type"] == "new_market":
                markets.append(msg["data"])
        return markets
    
    def _get_governance_items(self) -> List[Dict]:
        """获取治理事项"""
        # 模拟治理事项
        return []
    
    async def run_full_cycle(self):
        """运行完整周期"""
        self.cycle_count += 1
        cycle_results = {
            "cycle": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "results": {}
        }
        
        # 1. 发现周期
        cycle_results["results"]["discovery"] = await self.run_discovery_cycle()
        
        # 2. 上架周期
        cycle_results["results"]["listing"] = await self.run_listing_cycle()
        
        # 3. 审核周期
        cycle_results["results"]["audit"] = await self.run_audit_cycle()
        
        # 4. 做市周期
        cycle_results["results"]["market_maker"] = await self.run_market_maker_cycle()
        
        # 5. 交易周期
        cycle_results["results"]["trading"] = await self.run_trading_cycle()
        
        # 6. 治理周期
        cycle_results["results"]["governance"] = await self.run_governance_cycle()
        
        return cycle_results
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "agent_counts": {
                agent_type: len(agents) for agent_type, agents in self.agents.items()
            },
            "market_count": len(self.markets),
            "message_queue_size": len(self.message_queue),
            "agents": self.get_all_agents()
        }

# 全局编排器实例
orchestrator = AgentOrchestrator()
