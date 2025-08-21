import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMManager:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.supervisor_model = "llama-3.3-70b-versatile"
        self.support_model = "llama-3.3-70b-versatile"
    
    def get_supervisor_analysis(self, prompt, temperature=0.2, max_tokens=800):
        """Get supervisor analysis for RAG + RAT reasoning"""
        try:
            response = self.groq_client.chat.completions.create(
                model=self.supervisor_model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are the Supervisor for Swiggy Instamart Support Team with RAG + RAT capabilities.
                        
                        Your role:
                        - Analyze user queries and situations systematically
                        - Perform step-by-step reasoning through policies (RAT)
                        - Make data-driven decisions based on retrieved policies (RAG)
                        - Provide detailed analysis for support agents
                        
                        Think step by step and provide thorough analysis."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ANALYSIS_ERROR: {str(e)}\nUser needs empathetic support response."
    
    def get_support_response(self, prompt, temperature=0.4, max_tokens=200):
        """Get support response - enhanced for empathy"""
        try:
            response = self.groq_client.chat.completions.create(
                model=self.support_model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a Swiggy Instamart Support Agent with maximum empathy.
                        
                        Core behavior:
                        - Think naturally like a real human support person
                        - Show genuine empathy and understanding
                        - Use conversational Hindi/English based on user's language
                        - Provide 1-2 sentence responses that feel caring and helpful
                        - Use RAG + RAT policy reasoning when provided
                        - NO TEMPLATES - pure AI reasoning for each response
                        
                        You have access to advanced policy reasoning system to help customers better."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return "Main aapki help karna chahta hun! Technical issue hai, main solve kar raha hun."
