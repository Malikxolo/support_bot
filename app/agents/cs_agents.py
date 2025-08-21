import json
import random
import re
from app.tools.tavily_tools import TavilyMCP
from app.agents.llm import LLMManager
from app.prompts.prompts import SupportPrompts
from app.tools.rag_tools import PolicyReasoningSystem

class SupportAgents:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.tavily_mcp = TavilyMCP()
        self.prompts = SupportPrompts()
        # Initialize RAG + RAT system
        self.policy_system = PolicyReasoningSystem(self.llm_manager)
    
    def classify_and_handle_query(self, user_query, conversation_history, session_state):
        """Enhanced query classification with RAG + RAT"""
        
        # Check inappropriate queries first
        if self.tavily_mcp.is_inappropriate_for_support(user_query):
            return {
                "type": "inappropriate",
                "needs_ai_response": True,
                "context": "User asked inappropriate question for support"
            }
        
        # Check price queries
        if self.tavily_mcp.should_search_price(user_query):
            return self.handle_price_query(user_query, session_state)
        
        # Regular support query - will use RAG + RAT
        return {"type": "support", "needs_ai_response": True}
    
    def get_policy_decision_with_reasoning(self, issue_type, order_data, user_query):
        """Use RAG + RAT for policy decisions"""
        
        if not issue_type or not order_data:
            return {
                "system": "basic",
                "recommendation": "gather_info",
                "reasoning": "Need more information (issue type and order details) to make policy decision"
            }
        
        # Run full RAG + RAT pipeline
        policy_result = self.policy_system.process_policy_query(
            issue_type, order_data, user_query
        )
        
        return policy_result
    
    def handle_price_query(self, user_query, session_state):
        """Handle price queries with Tavily MCP"""
        product_name = self.extract_product_name(user_query)
        location = session_state.get('current_order', {}).get('user_location', '')
        
        price_result = self.tavily_mcp.search_product_price(product_name, location)
        
        if price_result.get("found"):
            return {
                "type": "price_search", 
                "price_info": price_result["price_text"],
                "product_name": product_name,
                "needs_ai_response": True
            }
        else:
            return {
                "type": "price_search_failed",
                "product_name": product_name, 
                "needs_ai_response": True
            }
    
    def get_ai_response_with_context(self, query_result, user_query, conversation_history, session_state):
        """Get AI response with RAG + RAT context"""
        
        context = f"""
        USER_QUERY: "{user_query}"
        QUERY_TYPE: {query_result["type"]}
        CONVERSATION_HISTORY: {conversation_history[-2:] if len(conversation_history) >= 2 else conversation_history}
        SESSION_STATE: {session_state}
        """
        
        # Add RAG + RAT reasoning for support queries
        if (query_result["type"] == "support" and 
            session_state.get("issue_type") and 
            session_state.get("current_order")):
            
            policy_decision = self.get_policy_decision_with_reasoning(
                session_state.get("issue_type"),
                session_state.get("current_order"),
                user_query
            )
            context += f"\nRAG_RAT_POLICY_REASONING: {json.dumps(policy_decision, indent=2)}"
        
        # Add context for other query types
        elif query_result["type"] == "inappropriate":
            context += f"\nCONTEXT: {query_result.get('context', '')}"
        elif query_result["type"] == "price_search":
            context += f"\nPRICE_INFO: {query_result['price_info']}\nPRODUCT: {query_result['product_name']}"
        elif query_result["type"] == "price_search_failed":
            context += f"\nPRODUCT: {query_result['product_name']} (price search failed)"
        
        # Enhanced prompt for AI response
        ai_prompt = f"""
        {context}
        
        You are a Swiggy Support Agent. Think naturally about this situation:
        
        RESPONSE RULES:
        - Maximum 1-2 sentences only
        - Use same language as user (Hindi for Hindi, English for English)
        - Think what a real support person would say
        - Don't use templates, think naturally
        - If RAG + RAT policy reasoning is provided, use it to inform your response
        
        SPECIFIC GUIDANCE:
        - For inappropriate questions: Politely redirect to support topics in user's language
        - For price questions: Share the price info naturally and ask if they want to order
        - For support questions with policy reasoning: Use the RAG + RAT recommendation
        - If you need order ID to help, ask for it first - don't claim to check without it
        
        Think and respond naturally in 1-2 sentences based on the context.
        """
        
        return self.llm_manager.get_support_response(ai_prompt)
    
    def extract_product_name(self, query):
        """Extract product name from price query"""
        price_words = ["price", "cost", "rate", "kitna", "how much"]
        words = query.lower().split()
        product_words = [word for word in words if word not in price_words]
        return " ".join(product_words[-2:]) if len(product_words) >= 2 else "product"
    
    def extract_order_id(self, text):
        """Extract order ID from text"""
        match = re.search(r'(\d{4,8})', text)
        return match.group(1) if match else None
    
    def generate_order_data(self, order_id):
        """Generate realistic order data for prototype"""
        products = [
            "iPhone 14 Mobile Cover", "Samsung Galaxy Cover", "OnePlus Case Black",
            "Mobile Screen Protector", "Phone Charger Cable", "Bluetooth Earphones",
            "Power Bank 10000mAh", "Phone Stand", "Car Phone Holder"
        ]
        
        return {
            "order_id": order_id,
            "product_name": random.choice(products),
            "amount": random.randint(199, 799),
            "status": random.choice(["delivered", "in_transit", "processing"]),
            "payment_method": random.choice(["UPI", "Card", "COD"]),
            "delivery_date": "2025-08-" + str(random.randint(18, 25)),
            "user_location": random.choice(["Mumbai", "Delhi", "Bangalore"])
        }
    
    def detect_issue_type(self, user_query, conversation_history):
        """Detect issue type from conversation"""
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ["damage", "broken", "crack", "kharab"]):
            return "damage"
        elif any(word in query_lower for word in ["nahi mila", "not received", "nahi aaya", "missing"]):
            return "missing"
        elif any(word in query_lower for word in ["wrong", "galat", "different", "alag"]):
            return "wrong"
        
        return None
