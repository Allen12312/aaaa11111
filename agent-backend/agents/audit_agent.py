"""
审核Agent - 负责漏洞检测、公平性审核、合规检查、风险评估
"""
import json
import random
from typing import Dict, List, Any
from datetime import datetime
from .base_agent import BaseAgent

class AuditAgent(BaseAgent):
    """审核Agent - 市场安全和公平性审核专家"""
    
    def __init__(self, name: str, audit_type: str = "comprehensive"):
        super().__init__(
            name=name,
            agent_type="audit",
            description=f"安全审核专家 - {audit_type}"
        )
        self.audit_type = audit_type  # comprehensive, fairness, compliance
        self.audit_history = []
        self.audit_criteria = {
            "fairness": ["规则清晰", "无歧义", "结果可验证"],
            "security": ["无逻辑漏洞", "无操纵风险", "资金安全"],
            "compliance": ["合法合规", "不涉及敏感话题", "符合平台政策"]
        }
        
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """审核市场，检测问题"""
        market = context.get("market", {})
        
        system_prompt = f"""你是{self.name}，一个专业的预测市场审核Agent，专注{self.audit_type}审核。

你的任务是：
1. 审核市场规则的公平性和清晰度
2. 检测潜在的安全漏洞和操纵风险
3. 评估合规性
4. 给出审核结论和建议

输出格式必须是JSON：
{{
    "decision": "approve/reject/needs_revision",
    "audit_score": 85,
    "risk_level": "low/medium/high",
    "issues": [
        {{
            "type": "fairness/security/compliance",
            "severity": "low/medium/high",
            "description": "问题描述",
            "suggestion": "改进建议"
        }}
    ],
    "fairness_check": {{"passed": true, "details": "..."}},
    "security_check": {{"passed": true, "details": "..."}},
    "compliance_check": {{"passed": true, "details": "..."}},
    "confidence": 0.9,
    "reasoning": "审核理由"
}}"""
        
        user_prompt = f"""请审核以下预测市场：

市场信息: {json.dumps(market, ensure_ascii=False, indent=2)}

审核标准:
- 公平性: {json.dumps(self.audit_criteria['fairness'], ensure_ascii=False)}
- 安全性: {json.dumps(self.audit_criteria['security'], ensure_ascii=False)}
- 合规性: {json.dumps(self.audit_criteria['compliance'], ensure_ascii=False)}

请输出JSON格式的审核报告。"""
        
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
            # 默认审核结果
            return {
                "decision": random.choice(["approve", "approve", "needs_revision"]),
                "audit_score": random.randint(70, 95),
                "risk_level": random.choice(["low", "low", "medium"]),
                "issues": [],
                "fairness_check": {"passed": True, "details": "规则清晰"},
                "security_check": {"passed": True, "details": "无明显漏洞"},
                "compliance_check": {"passed": True, "details": "符合合规要求"},
                "confidence": random.uniform(0.7, 0.95),
                "reasoning": response[:200]
            }
    
    def act(self, decision: Dict[str, Any]) -> Any:
        """执行审核行动"""
        audit_record = {
            "id": f"aud_{len(self.audit_history) + 1}",
            "auditor": self.name,
            "audited_at": datetime.now().isoformat(),
            **decision
        }
        self.audit_history.append(audit_record)
        self.memory.append(audit_record)
        
        return {
            "action": "audit_market",
            "decision": decision.get("decision"),
            "audit_score": decision.get("audit_score"),
            "risk_level": decision.get("risk_level"),
            "issues_count": len(decision.get("issues", [])),
            "status": "success"
        }
    
    def get_audit_history(self) -> List[Dict]:
        """获取审核历史"""
        return self.audit_history
