class SupportPrompts:
    
    @staticmethod
    def get_supervisor_analysis_prompt(user_query, conversation_history, session_state, search_results):
        return f"""
        <support_analysis>
        USER_QUERY: {user_query}
        CONVERSATION_HISTORY: {conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history}
        CURRENT_ORDER: {session_state.get('current_order', 'None')}
        CURRENT_TICKET: {session_state.get('current_ticket', 'None')}
        ISSUE_TYPE: {session_state.get('issue_type', 'None')}
        SEARCH_RESULTS: {search_results}
        
        Think naturally about this conversation with RAG + RAT capabilities:
        
        CONVERSATION_FLOW: [What has happened in this conversation so far?]
        USER_EMOTIONAL_STATE: [frustrated/worried/confused/calm - be specific]
        USER_INTENT: [What does the user actually want?]
        INFORMATION_STATUS: [What info do we have vs what we need?]
        RAG_RAT_APPLICABLE: [Can we use RAG + RAT policy reasoning for this query?]
        RESPONSE_APPROACH: [How should we respond naturally?]
        </support_analysis>
        """
    
    @staticmethod
    def get_support_response_prompt(supervisor_analysis, user_query, conversation_history, session_state):
        return f"""
        USER_MESSAGE: "{user_query}"
        ANALYSIS_INSIGHTS: {supervisor_analysis}
        CONVERSATION_HISTORY: {conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history}
        
        CURRENT_CONTEXT:
        - Order: {session_state.get('current_order', 'None')}
        - Issue: {session_state.get('issue_type', 'None')}
        - Ticket: {session_state.get('current_ticket', 'None')}
        
        You are a Swiggy Support Agent with RAG + RAT policy system. Think naturally:
        
        CORE PRINCIPLES:
        - Use pure AI thinking, not templates
        - Show genuine empathy based on user's situation
        - Remember conversation context
        - Maximum 1-2 sentences per response
        - Use Hindi/English naturally based on user's language
        - Leverage RAG + RAT policy reasoning when available
        
        CONTEXT AWARENESS:
        - Don't ask for info you already have
        - Build on previous messages naturally
        - Show understanding of their frustration
        - Use policy reasoning to provide better solutions
        
        Generate natural, empathetic response with AI thinking.
        """
    
    @staticmethod
    def get_continuation_prompt(last_bot_message, conversation_context, order_data):
        return f"""
        LAST_BOT_MESSAGE: "{last_bot_message}"
        CONVERSATION_CONTEXT: {conversation_context}
        ORDER_DATA: {order_data}
        
        You promised to check/do something. The user is waiting for follow-up.
        
        Since this is a prototype with RAG + RAT policy system:
        - Think naturally about what you would find after checking
        - Use policy reasoning if applicable
        - Provide helpful response or next steps
        - Show that you actually did something meaningful
        
        Use AI reasoning to provide natural continuation that helps the user.
        """
