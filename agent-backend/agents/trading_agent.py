"""
交易Agent - 负责趋势分析、风险控制、策略执行、收益优化
"""
import json
import random
from typing import Dict, List, Any
from datetime import datetime
from .base_agent import BaseAgent

class TradingAgent(BaseAgent):
    """交易Agent - 策略执行和收益优化专家"""
    
    def __init__(self, name: str, strategy: str = "trend_following"):
        super().__init__(
            name=name,
            agent_type="trading",
            description=f"交易专家 - {strategy}策略"
        )
        self.strategy = strategy  # trend_following, mean_reversion, momentum, arbitrage
        self.portfolio = {"cash": 100000, "positions": {}}
        self.trades = []
        self.total_profit = 0.0
        
        # 策略参数
        self.strategy_params = {
            "trend_following": {"lookback": 20, "entry_threshold": 0.05, "exit_threshold": 0.02},
            "mean_reversion": {"lookback": 10, "z_score_threshold": 2.0, "exit_z_score": 0.5},
            "momentum": {"lookback": 5, "momentum_threshold": 0.03, "stop_loss": 0.05},
            "arbitrage": {"min_spread": 0.01, "max_position": 50000},
            "event_driven": {"confidence_threshold": 0.7, "position_size": 0.1}
        }
        
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场，决定交易策略"""
        market = context.get("market", {})
        price_history = context.get("price_history", [])
        current_price = context.get("current_price", 0.5)
        signals = context.get("signals", {})
        
        params = self.strategy_params.get(self.strategy, self.strategy_params["trend_following"])
        
        system_prompt = f"""你是{self.name}，一个专业的交易Agent，采用{self.strategy}策略。

你的任务是：
1. 分析价格走势和市场信号
2. 评估风险和收益
3. 决定买入、卖出或持有
4. 确定仓位大小

输出格式必须是JSON：
{{
    "action": "buy/sell/hold",
    "direction": "yes/no",
    "size": 1000,
    "price": 0.5,
    "stop_loss": 0.45,
    "take_profit": 0.6,
    "confidence": 0.8,
    "risk_level": "low/medium/high",
    "expected_return": 0.15,
    "reasoning": "决策理由",
    "signals_analysis": {{
        "trend": "up/down/sideways",
        "momentum": "strong/weak",
        "volatility": "high/medium/low"
    }}
}}"""
        
        user_prompt = f"""请分析以下市场数据，制定交易策略：

市场: {json.dumps(market, ensure_ascii=False, indent=2)}
当前价格: {current_price}
价格历史: {price_history[-10:] if price_history else "无"}
市场信号: {json.dumps(signals, ensure_ascii=False, indent=2)}
策略参数: {json.dumps(params, ensure_ascii=False)}

当前持仓: {json.dumps(self.portfolio, ensure_ascii=False)}

请输出JSON格式的交易决策。"""
        
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
            # 默认交易决策
            action = random.choice(["buy", "sell", "hold", "hold"])
            direction = random.choice(["yes", "no"])
            return {
                "action": action,
                "direction": direction,
                "size": random.randint(100, 2000),
                "price": current_price,
                "stop_loss": round(current_price * 0.9, 4),
                "take_profit": round(current_price * 1.2, 4),
                "confidence": random.uniform(0.6, 0.9),
                "risk_level": random.choice(["low", "medium", "low"]),
                "expected_return": random.uniform(0.05, 0.25),
                "reasoning": response[:200],
                "signals_analysis": {
                    "trend": random.choice(["up", "down", "sideways"]),
                    "momentum": random.choice(["strong", "weak"]),
                    "volatility": random.choice(["high", "medium", "low"])
                }
            }
    
    def act(self, decision: Dict[str, Any]) -> Any:
        """执行交易行动"""
        action = decision.get("action", "hold")
        
        if action == "hold":
            return {
                "action": "hold",
                "status": "success",
                "reason": "等待更好机会"
            }
        
        # 创建交易记录
        trade = {
            "id": f"trade_{len(self.trades) + 1}",
            "trader": self.name,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "direction": decision.get("direction"),
            "size": decision.get("size"),
            "price": decision.get("price"),
            "stop_loss": decision.get("stop_loss"),
            "take_profit": decision.get("take_profit"),
            "expected_return": decision.get("expected_return"),
            "confidence": decision.get("confidence")
        }
        self.trades.append(trade)
        
        # 更新持仓
        market_id = decision.get("market_id", "default")
        if market_id not in self.portfolio["positions"]:
            self.portfolio["positions"][market_id] = {"yes": 0, "no": 0}
        
        position = self.portfolio["positions"][market_id]
        size = decision.get("size", 0)
        
        if action == "buy":
            if decision.get("direction") == "yes":
                position["yes"] += size
            else:
                position["no"] += size
            self.portfolio["cash"] -= size * decision.get("price", 0)
        elif action == "sell":
            if decision.get("direction") == "yes":
                position["yes"] -= size
            else:
                position["no"] -= size
            self.portfolio["cash"] += size * decision.get("price", 0)
        
        return {
            "action": action,
            "trade": trade,
            "portfolio": self.portfolio,
            "status": "success"
        }
    
    def get_portfolio(self) -> Dict:
        """获取投资组合"""
        return {
            "portfolio": self.portfolio,
            "total_trades": len(self.trades),
            "total_profit": self.total_profit,
            "recent_trades": self.trades[-5:] if self.trades else []
        }
