import os
import json
import re

class RAGPolicyEngine:
    """RAG: Retrieval Augmented Generation for policy documents"""
    
    def __init__(self):
        self.policies = self.load_policy_files()
        print(f"RAG Policy Engine ready - {len(self.policies)} policies loaded")
    
    def load_policy_files(self):
        """Load and parse policy text files"""
        policy_files = {
            "refund_policy": "app/policies/refund_policy.txt",
            "privacy_policy": "app/policies/privacy_policy.txt", 
            "terms_policy": "app/policies/terms_policy.txt"
        }
        
        policies = []
        
        for policy_name, file_path in policy_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                sections = self._split_into_sections(content)
                
                for i, section in enumerate(sections):
                    policies.append({
                        "id": f"{policy_name}_{i}",
                        "policy_type": policy_name,
                        "content": section,
                        "keywords": self._extract_keywords(section)
                    })
                    
            except FileNotFoundError:
                print(f"Policy file not found: {file_path}")
                fallback = self._get_fallback_policy(policy_name)
                if fallback:
                    policies.extend(fallback)
        
        return policies
    
    def _split_into_sections(self, content):
        """Split policy content into sections"""
        sections = []
        lines = content.split('\n')
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if (re.match(r'^\d+\.', line) or 
                line.isupper() or 
                line.startswith('SWIGGY')):
                
                if current_section:
                    section_text = '\n'.join(current_section)
                    if len(section_text) > 50:
                        sections.append(section_text)
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            section_text = '\n'.join(current_section)
            if len(section_text) > 50:
                sections.append(section_text)
        
        return sections
    
    def _extract_keywords(self, text):
        """Extract keywords from text"""
        keywords = []
        text_lower = text.lower()
        
        policy_keywords = [
            "damage", "broken", "defect", "crack", "photo", "evidence",
            "missing", "not delivered", "lost", "incomplete",
            "wrong", "incorrect", "different", "mismatch",
            "refund", "replacement", "exchange", "return",
            "24 hours", "48 hours", "7 days", "immediate"
        ]
        
        for keyword in policy_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return keywords
    
    def _get_fallback_policy(self, policy_type):
        """Fallback policies if files don't exist"""
        fallbacks = {
            "refund_policy": [
                {
                    "id": "fallback_damage",
                    "policy_type": "refund_policy",
                    "content": "DAMAGED ITEMS: Items damaged during delivery eligible for full refund within 24 hours. Photo evidence required for all damage claims.",
                    "keywords": ["damage", "broken", "photo", "evidence", "24 hours", "refund"]
                },
                {
                    "id": "fallback_missing", 
                    "policy_type": "refund_policy",
                    "content": "MISSING ITEMS: Items not delivered get immediate refund or redelivery. Report missing items within 2 hours.",
                    "keywords": ["missing", "not delivered", "immediate", "refund"]
                }
            ]
        }
        
        return fallbacks.get(policy_type, [])
    
    def query_policy(self, query, issue_type=None, n_results=3):
        """RAG: Retrieve relevant policies based on query"""
        query_lower = query.lower()
        scored_policies = []
        
        for policy in self.policies:
            score = 0
            
            if query_lower in policy["content"].lower():
                score += 10
            
            for keyword in policy["keywords"]:
                if keyword in query_lower:
                    score += 5
            
            if issue_type:
                if issue_type in policy["keywords"]:
                    score += 15
                if issue_type in policy["content"].lower():
                    score += 10
            
            if score > 0:
                scored_policies.append({
                    "policy": policy,
                    "score": score
                })
        
        scored_policies.sort(key=lambda x: x["score"], reverse=True)
        top_policies = scored_policies[:n_results]
        
        if top_policies:
            context = []
            for item in top_policies:
                context.append({
                    "content": item["policy"]["content"],
                    "policy_type": item["policy"]["policy_type"],
                    "relevance_score": item["score"]
                })
            
            return {
                "found": True,
                "context": context,
                "query_processed": f"rag_search_{issue_type or 'general'}"
            }
        
        return {
            "found": False,
            "context": [],
            "message": "No specific policy found"
        }


class RATReasoningEngine:
    """RAT: Retrieval Augmented Thinking for step-by-step policy reasoning"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        print("RAT Reasoning Engine initialized")
    
    def think_through_policy(self, retrieved_policies, issue_type, order_data, user_query):
        """RAT: Multi-step reasoning through retrieved policies"""
        
        #Analyze
        situation_analysis = self._analyze_situation(issue_type, order_data, user_query)
        
        #Apply policy
        policy_reasoning = self._reason_through_policies(retrieved_policies, situation_analysis)
        
        #Determine final recommendation
        final_decision = self._make_final_decision(policy_reasoning, situation_analysis)
        
        return {
            "thinking_process": {
                "situation_analysis": situation_analysis,
                "policy_reasoning": policy_reasoning,
                "final_decision": final_decision
            },
            "recommendation": final_decision["recommendation"],
            "reasoning": final_decision["reasoning"],
            "confidence": final_decision["confidence"]
        }
    
    def _analyze_situation(self, issue_type, order_data, user_query):
        """RAT Step 1: Analyze the current situation"""
        
        analysis_prompt = f"""
        <rat_situation_analysis>
        ISSUE_TYPE: {issue_type}
        ORDER_DATA: {order_data}
        USER_QUERY: {user_query}
        
        Think step by step about this situation:
        
        STEP 1 - ISSUE CLASSIFICATION: What exactly is the user's problem?
        STEP 2 - TIMING ANALYSIS: When did this issue occur? Is it within policy time limits?
        STEP 3 - EVIDENCE ANALYSIS: What evidence is available or needed?
        STEP 4 - ORDER CONTEXT: What are the order details and their relevance?
        STEP 5 - USER EXPECTATIONS: What does the user likely want as resolution?
        
        Provide clear analysis for each step.
        </rat_situation_analysis>
        """
        
        try:
            analysis = self.llm_manager.get_supervisor_analysis(analysis_prompt, max_tokens=600)
            return analysis
        except:
            return f"Basic situation analysis: {issue_type} issue with order {order_data.get('order_id', 'unknown')}"
    
    def _reason_through_policies(self, retrieved_policies, situation_analysis):
        """RAT Step 2: Reason through applicable policies"""
        
        policies_text = "\n".join([p["content"] for p in retrieved_policies])
        
        reasoning_prompt = f"""
        <rat_policy_reasoning>
        SITUATION_ANALYSIS: {situation_analysis}
        APPLICABLE_POLICIES: {policies_text}
        
        Now think through the policies step by step:
        
        STEP 1 - POLICY APPLICABILITY: Which specific policies apply to this situation?
        STEP 2 - CONDITION CHECKING: Are all policy conditions met (time limits, evidence, etc.)?
        STEP 3 - EXCEPTION ANALYSIS: Are there any exceptions or edge cases?
        STEP 4 - PRECEDENCE RULES: If multiple policies apply, which takes priority?
        STEP 5 - COMPLIANCE STATUS: Is this case within policy or requires escalation?
        
        Think through each step systematically.
        </rat_policy_reasoning>
        """
        
        try:
            reasoning = self.llm_manager.get_supervisor_analysis(reasoning_prompt, max_tokens=700)
            return reasoning
        except:
            return f"Policy reasoning: Standard policies apply for {retrieved_policies[0]['policy_type'] if retrieved_policies else 'general'} cases"
    
    def _make_final_decision(self, policy_reasoning, situation_analysis):
        """RAT Step 3: Make final decision based on reasoning"""
        
        decision_prompt = f"""
        <rat_final_decision>
        SITUATION: {situation_analysis}
        POLICY_REASONING: {policy_reasoning}
        
        Based on the analysis and reasoning, make a final decision:
        
        STEP 1 - DECISION: What should be done? (refund/replacement/escalation/etc.)
        STEP 2 - JUSTIFICATION: Why is this the right decision?
        STEP 3 - NEXT_ACTIONS: What specific actions need to be taken?
        STEP 4 - CONFIDENCE: How confident are we in this decision? (high/medium/low)
        STEP 5 - ALTERNATIVE_OPTIONS: What other options could be considered?
        
        Provide clear, actionable decision with reasoning.
        </rat_final_decision>
        """
        
        try:
            decision = self.llm_manager.get_supervisor_analysis(decision_prompt, max_tokens=500)
            
            confidence = "medium"
            if "high confidence" in decision.lower():
                confidence = "high"
            elif "low confidence" in decision.lower():
                confidence = "low"
            
            return {
                "reasoning": decision,
                "recommendation": self._extract_recommendation(decision),
                "confidence": confidence
            }
        except:
            return {
                "reasoning": "Standard resolution recommended based on policy guidelines",
                "recommendation": "provide_support",
                "confidence": "medium"
            }
    
    def _extract_recommendation(self, decision_text):
        """Extract actionable recommendation from decision"""
        decision_lower = decision_text.lower()
        
        if "refund" in decision_lower:
            return "process_refund"
        elif "replacement" in decision_lower or "replace" in decision_lower:
            return "offer_replacement"
        elif "escalation" in decision_lower or "escalate" in decision_lower:
            return "escalate_to_admin"
        elif "photo" in decision_lower or "evidence" in decision_lower:
            return "request_evidence"
        else:
            return "provide_support"


class PolicyReasoningSystem:
    """Combined RAG + RAT system for intelligent policy handling"""
    
    def __init__(self, llm_manager):
        self.rag_engine = RAGPolicyEngine()  # For retrieval
        self.rat_engine = RATReasoningEngine(llm_manager)  # For reasoning
        print("Combined RAG + RAT Policy System ready")
    
    def process_policy_query(self, issue_type, order_data, user_query):
        """Full RAG + RAT pipeline"""
        
        # RAG Retrieving
        rag_result = self.rag_engine.query_policy(user_query, issue_type, n_results=3)
        
        if not rag_result["found"]:
            return {
                "system": "RAG only",
                "recommendation": "manual_review",
                "reasoning": "No applicable policies found in knowledge base",
                "confidence": "low"
            }
        
        # RAT Thinking
        rat_result = self.rat_engine.think_through_policy(
            rag_result["context"], 
            issue_type, 
            order_data, 
            user_query
        )
        
        return {
            "system": "RAG + RAT",
            "retrieved_policies": rag_result["context"],
            "thinking_process": rat_result["thinking_process"],
            "recommendation": rat_result["recommendation"],
            "reasoning": rat_result["reasoning"],
            "confidence": rat_result["confidence"]
        }
    
    def is_system_ready(self):
        """Check if both RAG and RAT systems are ready"""
        return self.rag_engine.is_system_ready()
