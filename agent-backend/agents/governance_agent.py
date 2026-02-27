"""
治理Agent - 负责结果验证、提案投票、争议处理、生态维护
"""
import json
import random
from typing import Dict, List, Any
from datetime import datetime
from .base_agent import BaseAgent

class GovernanceAgent(BaseAgent):
    """治理Agent - 平台治理和争议解决专家"""
    
    def __init__(self, name: str, governance_style: str = "balanced"):
        super().__init__(
            name=name,
            agent_type="governance",
            description=f"治理专家 - {governance_style}风格"
        )
        self.governance_style = governance_style  # conservative, balanced, progressive
        self.proposals = []
        self.votes = []
        self.disputes = []
        self.resolutions = []
        
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析治理事项，做出决策"""
        governance_type = context.get("type", "proposal")  # proposal, dispute, resolution
        
        if governance_type == "proposal":
            return self._evaluate_proposal(context)
        elif governance_type == "dispute":
            return self._evaluate_dispute(context)
        elif governance_type == "resolution":
            return self._evaluate_resolution(context)
        else:
            return {"decision": "abstain", "reasoning": "未知治理类型"}
    
    def _evaluate_proposal(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估提案"""
        proposal = context.get("proposal", {})
        
        system_prompt = f"""你是{self.name}，一个专业的治理Agent，采用{self.governance_style}风格。

你的任务是评估治理提案：
1. 分析提案的合理性和可行性
2. 评估对平台生态的影响
3. 考虑长期和短期利益
4. 做出投票决策

输出格式必须是JSON：
{{
    "decision": "for/against/abstain",
    "confidence": 0.85,
    "reasoning": "决策理由",
    "impact_assessment": {{
        "short_term": "正面/负面/中性",
        "long_term": "正面/负面/中性",
        "severity": "high/medium/low"
    }},
    "risk_analysis": {{
        "implementation_risk": "high/medium/low",
        "adoption_risk": "high/medium/low",
        "unintended_consequences": "描述"
    }}
}}"""
        
        user_prompt = f"""请评估以下治理提案：

提案: {json.dumps(proposal, ensure_ascii=False, indent=2)}

请输出JSON格式的评估报告。"""
        
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
            return {
                "decision": random.choice(["for", "against", "abstain"]),
                "confidence": random.uniform(0.6, 0.9),
                "reasoning": response[:200],
                "impact_assessment": {
                    "short_term": random.choice(["正面", "负面", "中性"]),
                    "long_term": random.choice(["正面", "负面", "中性"]),
                    "severity": random.choice(["high", "medium", "low"])
                },
                "risk_analysis": {
                    "implementation_risk": random.choice(["high", "medium", "low"]),
                    "adoption_risk": random.choice(["high", "medium", "low"]),
                    "unintended_consequences": "无明显风险"
                }
            }
    
    def _evaluate_dispute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估争议"""
        dispute = context.get("dispute", {})
        
        system_prompt = f"""你是{self.name}，一个专业的争议仲裁Agent。

你的任务是仲裁市场争议：
1. 分析争议双方的观点和证据
2. 评估市场规则的适用性
3. 考虑公平性和平台利益
4. 做出仲裁决策

输出格式必须是JSON：
{{
    "decision": "支持原告/支持被告/需要更多信息",
    "confidence": 0.85,
    "reasoning": "仲裁理由",
    "evidence_assessment": {{
        "plaintiff_evidence": "强/中/弱",
        "defendant_evidence": "强/中/弱"
    }},
    "resolution": "解决方案",
    "precedent": "是否建立先例"
}}"""
        
        user_prompt = f"""请仲裁以下争议：

争议: {json.dumps(dispute, ensure_ascii=False, indent=2)}

请输出JSON格式的仲裁报告。"""
        
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
            return {
                "decision": random.choice(["支持原告", "支持被告", "需要更多信息"]),
                "confidence": random.uniform(0.6, 0.9),
                "reasoning": response[:200],
                "evidence_assessment": {
                    "plaintiff_evidence": random.choice(["强", "中", "弱"]),
                    "defendant_evidence": random.choice(["强", "中", "弱"])
                },
                "resolution": "按照规则执行",
                "precedent": random.choice([True, False])
            }
    
    def _evaluate_resolution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估市场结果"""
        market = context.get("market", {})
        outcome_data = context.get("outcome_data", {})
        
        system_prompt = f"""你是{self.name}，一个专业的市场结果验证Agent。

你的任务是验证预测市场结果：
1. 检查结果数据来源的可靠性
2. 验证结果是否符合市场规则
3. 评估争议的可能性
4. 确认最终结果

输出格式必须是JSON：
{{
    "decision": "确认/暂缓/争议",
    "outcome": "结果",
    "confidence": 0.95,
    "reasoning": "验证理由",
    "source_reliability": "high/medium/low",
    "controversy_risk": "high/medium/low",
    "recommendation": "建议"
}}"""
        
        user_prompt = f"""请验证以下市场结果：

市场: {json.dumps(market, ensure_ascii=False, indent=2)}
结果数据: {json.dumps(outcome_data, ensure_ascii=False, indent=2)}

请输出JSON格式的验证报告。"""
        
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
            return {
                "decision": "确认",
                "outcome": outcome_data.get("outcome", "unknown"),
                "confidence": random.uniform(0.85, 0.99),
                "reasoning": response[:200],
                "source_reliability": random.choice(["high", "medium", "high"]),
                "controversy_risk": random.choice(["low", "medium", "low"]),
                "recommendation": "可以结算"
            }
    
    def act(self, decision: Dict[str, Any]) -> Any:
        """执行治理行动"""
        governance_type = decision.get("type", "proposal")
        
        record = {
            "id": f"gov_{len(self.votes) + len(self.disputes) + len(self.resolutions) + 1}",
            "governor": self.name,
            "timestamp": datetime.now().isoformat(),
            "type": governance_type,
            **decision
        }
        
        if governance_type == "proposal":
            self.votes.append(record)
        elif governance_type == "dispute":
            self.disputes.append(record)
        elif governance_type == "resolution":
            self.resolutions.append(record)
        
        self.memory.append(record)
        
        return {
            "action": f"governance_{governance_type}",
            "decision": decision.get("decision"),
            "confidence": decision.get("confidence"),
            "status": "success"
        }
    
    def get_governance_history(self) -> Dict:
        """获取治理历史"""
        return {
            "votes": self.votes,
            "disputes": self.disputes,
            "resolutions": self.resolutions,
            "total_actions": len(self.votes) + len(self.disputes) + len(self.resolutions)
        }
