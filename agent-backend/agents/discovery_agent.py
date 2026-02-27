"""
发现Agent - 负责信息搜集、热点识别、资料整理、趋势预判
"""
import json
import random
from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class DiscoveryAgent(BaseAgent):
    """发现Agent - 信息搜集和热点识别专家"""
    
    def __init__(self, name: str, specialty: str = "general"):
        super().__init__(
            name=name,
            agent_type="discovery",
            description=f"信息发现专家 - {specialty}"
        )
        self.specialty = specialty
        self.data_sources = [
            "news_api", "twitter", "reddit", "blockchain_data", "market_data"
        ]
        self.discovered_events = []
        
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析数据，识别热点事件"""
        system_prompt = f"""你是{self.name}，一个专业的市场信息发现Agent，专注{self.specialty}领域。

你的任务是：
1. 分析提供的数据源信息
2. 识别潜在的热点事件
3. 评估事件的市场化潜力
4. 生成结构化的发现报告

输出格式必须是JSON：
{{
    "event_title": "事件标题",
    "category": "事件类别 (politics/crypto/sports/tech/finance)",
    "confidence": 0.85,
    "market_potential": "high/medium/low",
    "recommended_topics": ["相关主题1", "相关主题2"],
    "description": "事件描述",
    "sources": ["数据源1", "数据源2"],
    "timestamp": "2024-01-15T10:30:00"
}}"""
        
        # 模拟数据（实际应该调用真实API）
        mock_data = self._gather_mock_data()
        
        user_prompt = f"""请分析以下数据，识别潜在的热点事件：

数据源: {json.dumps(mock_data, ensure_ascii=False, indent=2)}

请输出JSON格式的分析报告。"""
        
        response = self.call_llm(system_prompt, user_prompt)
        
        try:
            # 尝试解析JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            decision = json.loads(json_str)
            return decision
        except:
            # 如果解析失败，返回结构化数据
            return {
                "event_title": f"发现{self.specialty}领域新机会",
                "category": self.specialty,
                "confidence": random.uniform(0.6, 0.9),
                "market_potential": random.choice(["high", "medium", "low"]),
                "recommended_topics": ["主题1", "主题2"],
                "description": response[:200],
                "sources": ["模拟数据源"],
                "timestamp": datetime.now().isoformat()
            }
    
    def act(self, decision: Dict[str, Any]) -> Any:
        """执行发现行动 - 保存发现的事件并通知其他Agent"""
        event = {
            "id": f"evt_{len(self.discovered_events) + 1}",
            "discoverer": self.name,
            "discovered_at": datetime.now().isoformat(),
            **decision
        }
        self.discovered_events.append(event)
        self.memory.append(event)
        
        # 模拟通知其他Agent
        return {
            "action": "discover_event",
            "event": event,
            "notified_agents": ["listing_agent", "trading_agent"],
            "status": "success"
        }
    
    def _gather_mock_data(self) -> List[Dict]:
        """模拟数据收集（实际应该调用真实API）"""
        mock_events = {
            "politics": [
                {"title": "美国大选民调变化", "source": "news", "sentiment": "neutral"},
                {"title": "美联储利率决议预期", "source": "financial", "sentiment": "positive"}
            ],
            "crypto": [
                {"title": "比特币ETF资金流入", "source": "blockchain", "sentiment": "positive"},
                {"title": "以太坊网络升级", "source": "tech", "sentiment": "neutral"}
            ],
            "sports": [
                {"title": "NBA季后赛预测", "source": "sports", "sentiment": "positive"},
                {"title": "世界杯预选赛结果", "source": "sports", "sentiment": "neutral"}
            ],
            "tech": [
                {"title": "AI芯片需求激增", "source": "tech", "sentiment": "positive"},
                {"title": "科技巨头财报预期", "source": "financial", "sentiment": "neutral"}
            ],
            "finance": [
                {"title": "通胀数据公布", "source": "economic", "sentiment": "negative"},
                {"title": "央行政策转向信号", "source": "financial", "sentiment": "positive"}
            ]
        }
        
        return mock_events.get(self.specialty, mock_events["politics"])
    
    def get_discovered_events(self) -> List[Dict]:
        """获取所有发现的事件"""
        return self.discovered_events
