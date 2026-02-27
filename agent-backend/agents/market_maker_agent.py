"""
做市Agent - 负责流动性提供、价差管理、库存平衡、价格稳定
"""
import json
import random
from typing import Dict, List, Any
from datetime import datetime
from .base_agent import BaseAgent

class MarketMakerAgent(BaseAgent):
    """做市Agent - 流动性提供和价格稳定专家"""
    
    def __init__(self, name: str, strategy: str = "balanced"):
        super().__init__(
            name=name,
            agent_type="market_maker",
            description=f"做市专家 - {strategy}策略"
        )
        self.strategy = strategy  # aggressive, balanced, conservative
        self.positions = {}  # 持仓
        self.orders = []  # 订单历史
        self.profit_loss = 0.0
        
        # 策略参数
        self.strategy_params = {
            "aggressive": {"spread": 0.01, "max_position": 100000, "rebalance_threshold": 0.05},
            "balanced": {"spread": 0.03, "max_position": 50000, "rebalance_threshold": 0.10},
            "conservative": {"spread": 0.05, "max_position": 20000, "rebalance_threshold": 0.15}
        }
        
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场状态，决定做市策略"""
        market = context.get("market", {})
        current_price = context.get("current_price", 0.5)
        orderbook = context.get("orderbook", {"bids": [], "asks": []})
        
        params = self.strategy_params.get(self.strategy, self.strategy_params["balanced"])
        
        system_prompt = f"""你是{name}，一个专业的做市Agent，采用{self.strategy}策略。

你的任务是：
1. 分析市场状态和订单簿
2. 确定买卖报价和数量
3. 管理库存风险
4. 优化价差收益

输出格式必须是JSON：
{{
    "action": "provide_liquidity/adjust_position/withdraw",
    "bid_price": 0.48,
    "bid_size": 1000,
    "ask_price": 0.52,
    "ask_size": 1000,
    "target_inventory": 0.5,
    "current_inventory": 0.3,
    "inventory_adjustment": 0.2,
    "expected_profit": 50,
    "risk_level": "low",
    "confidence": 0.85,
    "reasoning": "决策理由"
}}"""
        
        user_prompt = f"""请分析以下市场状态，制定做市策略：

市场: {json.dumps(market, ensure_ascii=False, indent=2)}
当前价格: {current_price}
订单簿: {json.dumps(orderbook, ensure_ascii=False, indent=2)}
策略参数: {json.dumps(params, ensure_ascii=False)}

请输出JSON格式的做市决策。"""
        
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
            # 默认做市决策
            spread = params["spread"]
            return {
                "action": "provide_liquidity",
                "bid_price": round(current_price * (1 - spread/2), 4),
                "bid_size": random.randint(500, 2000),
                "ask_price": round(current_price * (1 + spread/2), 4),
                "ask_size": random.randint(500, 2000),
                "target_inventory": 0.5,
                "current_inventory": random.uniform(0.3, 0.7),
                "inventory_adjustment": random.uniform(-0.2, 0.2),
                "expected_profit": random.randint(20, 100),
                "risk_level": random.choice(["low", "medium"]),
                "confidence": random.uniform(0.7, 0.9),
                "reasoning": response[:200]
            }
    
    def act(self, decision: Dict[str, Any]) -> Any:
        """执行做市行动"""
        action = decision.get("action", "provide_liquidity")
        
        if action == "withdraw":
            return {
                "action": "withdraw_liquidity",
                "status": "success",
                "reason": "风险管理"
            }
        
        # 创建订单
        order = {
            "id": f"ord_{len(self.orders) + 1}",
            "market_maker": self.name,
            "created_at": datetime.now().isoformat(),
            "action": action,
            "bid": {
                "price": decision.get("bid_price"),
                "size": decision.get("bid_size")
            },
            "ask": {
                "price": decision.get("ask_price"),
                "size": decision.get("ask_size")
            },
            "expected_profit": decision.get("expected_profit"),
            "inventory_adjustment": decision.get("inventory_adjustment")
        }
        self.orders.append(order)
        
        # 更新持仓
        market_id = decision.get("market_id", "default")
        if market_id not in self.positions:
            self.positions[market_id] = {"yes_tokens": 0, "no_tokens": 0, "profit": 0}
        
        # 计算预期收益
        self.profit_loss += decision.get("expected_profit", 0)
        
        return {
            "action": action,
            "order": order,
            "liquidity_provided": decision.get("bid_size", 0) + decision.get("ask_size", 0),
            "spread": decision.get("ask_price", 0) - decision.get("bid_price", 0),
            "status": "success"
        }
    
    def get_positions(self) -> Dict:
        """获取持仓信息"""
        return {
            "positions": self.positions,
            "total_orders": len(self.orders),
            "profit_loss": self.profit_loss
        }
