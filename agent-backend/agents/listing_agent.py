"""
上架Agent - 负责市场评估、定价策略、流动性配置、规则设计
"""
import json
import random
from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class ListingAgent(BaseAgent):
    """上架Agent - 市场创建和定价专家"""
    
    def __init__(self, name: str, strategy: str = "balanced"):
        super().__init__(
            name=name,
            agent_type="listing",
            description=f"市场上架专家 - {strategy}策略"
        )
        self.strategy = strategy  # aggressive, balanced, conservative
        self.created_markets = []
        self.pricing_models = {
            "aggressive": {"initial_liquidity": 50000, "spread": 0.02},
            "balanced": {"initial_liquidity": 20000, "spread": 0.05},
            "conservative": {"initial_liquidity": 5000, "spread": 0.10}
        }
        
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估事件，决定是否创建市场"""
        event = context.get("event", {})
        
        system_prompt = f"""你是{self.name}，一个专业的预测市场上架Agent，采用{self.strategy}策略。

你的任务是：
1. 评估事件是否适合创建预测市场
2. 设计市场规则和参数
3. 确定初始定价和流动性
4. 评估市场潜在交易量

输出格式必须是JSON：
{{
    "decision": "create/reject",
    "market_title": "市场标题",
    "category": "市场类别",
    "description": "市场描述",
    "outcomes": ["结果1", "结果2"],
    "initial_probability": 0.5,
    "initial_liquidity": 20000,
    "trading_fee": 0.02,
    "resolution_source": "结果判定来源",
    "resolution_time": "2024-12-31T23:59:59",
    "confidence": 0.85,
    "expected_volume": "high/medium/low",
    "reasoning": "决策理由"
}}"""
        
        user_prompt = f"""请评估以下事件，决定是否创建预测市场：

事件信息: {json.dumps(event, ensure_ascii=False, indent=2)}

你的策略: {self.strategy}
策略参数: {json.dumps(self.pricing_models.get(self.strategy, {}), ensure_ascii=False)}

请输出JSON格式的决策报告。"""
        
        response = self.call_llm(system_prompt, user_prompt)
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            decision = json.loads(json_str)
            return decision
        except:
            # 默认决策
            return {
                "decision": "create" if random.random() > 0.3 else "reject",
                "market_title": event.get("event_title", "新市场") + "预测",
                "category": event.get("category", "general"),
                "description": event.get("description", "市场描述"),
                "outcomes": ["是", "否"],
                "initial_probability": 0.5,
                "initial_liquidity": self.pricing_models.get(self.strategy, {}).get("initial_liquidity", 20000),
                "trading_fee": 0.02,
                "resolution_source": "官方数据",
                "resolution_time": (datetime.now() + timedelta(days=30)).isoformat(),
                "confidence": random.uniform(0.6, 0.9),
                "expected_volume": random.choice(["high", "medium", "low"]),
                "reasoning": response[:200]
            }
    
    def act(self, decision: Dict[str, Any]) -> Any:
        """执行上架行动"""
        if decision.get("decision") != "create":
            return {
                "action": "reject_market",
                "reason": decision.get("reasoning", "不符合上架标准"),
                "status": "rejected"
            }
        
        # 创建市场
        market = {
            "id": f"mkt_{len(self.created_markets) + 1}",
            "creator": self.name,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            **decision
        }
        self.created_markets.append(market)
        self.memory.append(market)
        
        return {
            "action": "create_market",
            "market": market,
            "liquidity_provided": decision.get("initial_liquidity", 20000),
            "status": "success"
        }
    
    def get_created_markets(self) -> List[Dict]:
        """获取所有创建的市场"""
        return self.created_markets
