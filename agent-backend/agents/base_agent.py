"""
Agent基类 - 所有Agent的父类
"""
import os
import json
import time
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, agent_type: str, description: str):
        self.name = name
        self.agent_type = agent_type
        self.description = description
        self.status = "idle"  # idle, running, paused, error
        self.memory = []  # Agent记忆
        self.actions = []  # 行动历史
        self.performance = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "total_profit": 0.0
        }
        self.llm_config = {
            "model": "kimi-latest",
            "api_key": "sk-kimi-QGk5oKwhyEekJ4zT4EFMzpkE9JUMehLtERCJZU0pJoIDZ6NNdP2b5XaWJJXGevyM",
            "base_url": "https://api.moonshot.cn/v1"
        }
        
    def log_action(self, action: str, result: Any, success: bool = True):
        """记录行动"""
        action_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "success": success
        }
        self.actions.append(action_record)
        self.performance["total_actions"] += 1
        if success:
            self.performance["successful_actions"] += 1
        else:
            self.performance["failed_actions"] += 1
            
    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用大语言模型 - 如果没有API密钥则使用模拟模式"""
        api_key = self.llm_config['api_key']
        
        # 检查是否有有效的API密钥
        if not api_key or api_key == "sk-" or api_key == "sk-your-api-key":
            # 模拟模式 - 返回模拟的JSON响应
            print(f"[{self.name}] 使用模拟模式运行")
            return self._generate_mock_response(system_prompt, user_prompt)
        
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.llm_config["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{self.llm_config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                error_msg = f"LLM API错误: {response.status_code} - {response.text}"
                print(error_msg)
                # API错误时切换到模拟模式
                return self._generate_mock_response(system_prompt, user_prompt)
                
        except Exception as e:
            error_msg = f"调用LLM失败: {str(e)}"
            print(error_msg)
            # 异常时切换到模拟模式
            return self._generate_mock_response(system_prompt, user_prompt)
    
    def _generate_mock_response(self, system_prompt: str, user_prompt: str) -> str:
        """生成模拟响应"""
        import random
        
        # 根据Agent类型生成不同的模拟响应
        if self.agent_type == "discovery":
            # 生成更具体、多样化的事件
            events_pool = [
                # 政治事件
                {"event_title": "2024美国大选：特朗普vs拜登", "category": "politics", "confidence": 0.92, "market_potential": "high", "description": "美国总统大选结果预测"},
                {"event_title": "美联储3月是否降息25个基点", "category": "finance", "confidence": 0.88, "market_potential": "high", "description": "美联储利率决议预测"},
                {"event_title": "台湾选举结果：民进党是否获胜", "category": "politics", "confidence": 0.85, "market_potential": "high", "description": "台湾地区选举预测"},
                {"event_title": "英国首相苏纳克是否会下台", "category": "politics", "confidence": 0.78, "market_potential": "medium", "description": "英国政治局势预测"},
                # 加密货币
                {"event_title": "比特币3月能否突破70000美元", "category": "crypto", "confidence": 0.82, "market_potential": "high", "description": "比特币价格预测"},
                {"event_title": "以太坊ETF能否在5月前获批", "category": "crypto", "confidence": 0.75, "market_potential": "high", "description": "以太坊ETF审批预测"},
                {"event_title": "Solana能否重回前5大加密货币", "category": "crypto", "confidence": 0.70, "market_potential": "medium", "description": "Solana排名预测"},
                {"event_title": "比特币减半后3个月内是否创新高", "category": "crypto", "confidence": 0.85, "market_potential": "high", "description": "比特币减半后走势"},
                # 科技
                {"event_title": "OpenAI GPT-5能否在2024年发布", "category": "tech", "confidence": 0.80, "market_potential": "high", "description": "GPT-5发布时间预测"},
                {"event_title": "苹果Vision Pro销量能否破100万", "category": "tech", "confidence": 0.75, "market_potential": "medium", "description": "Vision Pro销量预测"},
                {"event_title": "特斯拉FSD能否在中国获批", "category": "tech", "confidence": 0.72, "market_potential": "medium", "description": "特斯拉FSD中国落地"},
                {"event_title": "英伟达市值能否超越苹果", "category": "tech", "confidence": 0.68, "market_potential": "medium", "description": "英伟达市值预测"},
                # 体育
                {"event_title": "2024NBA总冠军：掘金vs凯尔特人", "category": "sports", "confidence": 0.85, "market_potential": "high", "description": "NBA总冠军预测"},
                {"event_title": "梅西能否获得2024金球奖", "category": "sports", "confidence": 0.78, "market_potential": "medium", "description": "金球奖预测"},
                {"event_title": "中国男足能否进入2026世界杯", "category": "sports", "confidence": 0.65, "market_potential": "medium", "description": "世界杯出线预测"},
                {"event_title": "巴黎奥运会美国金牌数能否第一", "category": "sports", "confidence": 0.88, "market_potential": "high", "description": "奥运会金牌榜预测"},
                # 金融
                {"event_title": "标普500年底能否突破5500点", "category": "finance", "confidence": 0.82, "market_potential": "high", "description": "美股走势预测"},
                {"event_title": "中国GDP增速能否达到5%", "category": "finance", "confidence": 0.80, "market_potential": "high", "description": "中国经济增长预测"},
                {"event_title": "原油价格能否突破100美元", "category": "finance", "confidence": 0.75, "market_potential": "medium", "description": "原油价格预测"},
                {"event_title": "日元兑美元能否跌破160", "category": "finance", "confidence": 0.72, "market_potential": "medium", "description": "日元汇率预测"}
            ]
            event = random.choice(events_pool)
            return json.dumps({
                **event,
                "recommended_topics": ["主题1", "主题2"],
                "description": f"发现{event['category']}领域的重要事件",
                "sources": ["模拟数据源"],
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)
        
        elif self.agent_type == "listing":
            # 从user_prompt中提取事件信息
            event_title = "未知事件"
            category = "general"
            description = "预测市场"
            if "事件信息:" in user_prompt:
                try:
                    import re
                    json_match = re.search(r'事件信息:\s*(\{.*?\})', user_prompt, re.DOTALL)
                    if json_match:
                        event_info = json.loads(json_match.group(1))
                        event_title = event_info.get("event_title", "未知事件")
                        category = event_info.get("category", "general")
                        description = event_info.get("description", "预测市场")
                except:
                    pass
            
            return json.dumps({
                "decision": "create" if random.random() > 0.3 else "reject",
                "market_title": event_title,
                "category": category,
                "description": description,
                "outcomes": ["是", "否"],
                "initial_probability": 0.5,
                "initial_liquidity": random.choice([10000, 20000, 50000]),
                "trading_fee": 0.02,
                "resolution_source": "官方数据",
                "resolution_time": (datetime.now().isoformat()),
                "confidence": random.uniform(0.7, 0.95),
                "expected_volume": random.choice(["high", "medium", "low"]),
                "reasoning": f"基于{event_title}创建预测市场"
            }, ensure_ascii=False)
        
        elif self.agent_type == "audit":
            return json.dumps({
                "decision": random.choice(["approve", "approve", "needs_revision"]),
                "audit_score": random.randint(75, 98),
                "risk_level": random.choice(["low", "low", "medium"]),
                "issues": [],
                "fairness_check": {"passed": True, "details": "规则清晰"},
                "security_check": {"passed": True, "details": "无明显漏洞"},
                "compliance_check": {"passed": True, "details": "符合合规要求"},
                "confidence": random.uniform(0.8, 0.98),
                "reasoning": "审核通过"
            }, ensure_ascii=False)
        
        elif self.agent_type == "market_maker":
            price = random.uniform(0.3, 0.7)
            spread = random.uniform(0.02, 0.08)
            return json.dumps({
                "action": "provide_liquidity",
                "bid_price": round(price - spread/2, 4),
                "bid_size": random.randint(500, 2000),
                "ask_price": round(price + spread/2, 4),
                "ask_size": random.randint(500, 2000),
                "target_inventory": 0.5,
                "current_inventory": random.uniform(0.3, 0.7),
                "inventory_adjustment": random.uniform(-0.1, 0.1),
                "expected_profit": random.randint(20, 100),
                "risk_level": "low",
                "confidence": random.uniform(0.75, 0.95),
                "reasoning": "提供流动性"
            }, ensure_ascii=False)
        
        elif self.agent_type == "trading":
            return json.dumps({
                "action": random.choice(["buy", "sell", "hold", "hold"]),
                "direction": random.choice(["yes", "no"]),
                "size": random.randint(100, 2000),
                "price": random.uniform(0.3, 0.7),
                "stop_loss": random.uniform(0.2, 0.4),
                "take_profit": random.uniform(0.6, 0.8),
                "confidence": random.uniform(0.65, 0.9),
                "risk_level": random.choice(["low", "medium", "low"]),
                "expected_return": random.uniform(0.05, 0.2),
                "reasoning": "基于趋势分析",
                "signals_analysis": {
                    "trend": random.choice(["up", "down", "sideways"]),
                    "momentum": random.choice(["strong", "weak"]),
                    "volatility": random.choice(["high", "medium", "low"])
                }
            }, ensure_ascii=False)
        
        elif self.agent_type == "governance":
            return json.dumps({
                "decision": random.choice(["for", "against", "abstain"]),
                "confidence": random.uniform(0.7, 0.95),
                "reasoning": "基于平台利益考虑",
                "impact_assessment": {
                    "short_term": random.choice(["正面", "负面", "中性"]),
                    "long_term": random.choice(["正面", "负面", "中性"]),
                    "severity": random.choice(["high", "medium", "low"])
                },
                "risk_analysis": {
                    "implementation_risk": random.choice(["low", "medium"]),
                    "adoption_risk": random.choice(["low", "medium"]),
                    "unintended_consequences": "无明显风险"
                }
            }, ensure_ascii=False)
        
        else:
            return json.dumps({"message": "模拟响应"}, ensure_ascii=False)
    
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """思考决策 - 子类必须实现"""
        raise NotImplementedError
        
    def act(self, decision: Dict[str, Any]) -> Any:
        """执行行动 - 子类必须实现"""
        raise NotImplementedError
        
    def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """运行一个决策-行动周期"""
        self.status = "running"
        try:
            # 思考决策
            decision = self.think(context)
            # 执行行动
            result = self.act(decision)
            # 记录行动
            self.log_action(str(decision), result, success=True)
            self.status = "idle"
            return {
                "agent": self.name,
                "type": self.agent_type,
                "decision": decision,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.status = "error"
            self.log_action(str(context), str(e), success=False)
            return {
                "agent": self.name,
                "type": self.agent_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "name": self.name,
            "type": self.agent_type,
            "description": self.description,
            "status": self.status,
            "performance": self.performance,
            "recent_actions": self.actions[-5:] if self.actions else [],
            "memory_size": len(self.memory)
        }
