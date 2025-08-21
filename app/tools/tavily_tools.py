import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TavilyMCP:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"
    
    def should_search_price(self, user_query):
        """Detect if user is asking for current prices"""
        price_keywords = [
            "price", "cost", "rate", "kitna hai", "how much", "kitne ka", 
            "kitne mein", "price kya hai", "rate kya hai", "cost kitna"
        ]
        return any(keyword in user_query.lower() for keyword in price_keywords)
    
    def is_inappropriate_for_support(self, user_query):
        """Detect inappropriate queries for customer support"""
        inappropriate_keywords = [
            # Personal life
            "dating", "relationship", "girlfriend", "boyfriend", "marriage",
            # Unrelated topics  
            "politics", "religion", "sports", "movies", "celebrity",
            # Inappropriate content
            "sex", "adult", "xxx", "porn",
            # Technical unrelated
            "coding", "programming", "software development",
            # Random chat
            "how are you", "what's your name", "where do you live", "tell me joke"
        ]
        
        query_lower = user_query.lower()
        return any(keyword in query_lower for keyword in inappropriate_keywords)
    
    def search_product_price(self, product_name, location=""):
        """Search for current product prices using Tavily MCP"""
        if not self.api_key:
            return {"error": "Tavily API not configured", "fallback": True}
        
        price_query = f"{product_name} price Swiggy Instamart {location} current rate cost 2025"
        
        payload = {
            "api_key": self.api_key,
            "query": price_query,
            "search_depth": "basic",
            "include_answer": True,
            "max_results": 5
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price_info = self._extract_price_info(data, product_name)
                return {
                    "found": price_info["found"],
                    "price_text": price_info["text"]
                }
            else:
                return {"error": f"Search failed: {response.status_code}", "fallback": True}
        
        except Exception as e:
            return {"error": str(e), "fallback": True}
    
    def _extract_price_info(self, search_data, product_name):
        """Extract price information from search results"""
        price_text = ""
        found = False
        
        if search_data.get("answer"):
            answer = search_data["answer"]
            if any(currency in answer for currency in ["₹", "Rs", "INR", "rupees"]):
                price_text = answer[:200] + "..." if len(answer) > 200 else answer
                found = True
        
        if not found:
            price_text = f"Current price information for {product_name} not available"
        
        return {"found": found, "text": price_text}
