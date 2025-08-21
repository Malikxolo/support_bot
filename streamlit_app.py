import streamlit as st
import time
from app.database.models import DatabaseModels
from app.agents.cs_agents import SupportAgents
from app.tools.rag_tools import PolicyReasoningSystem
from app.tools.database_tools import DatabaseTools
from app.tools.photo_analysis import PhotoAnalysisTools

# Page config
st.set_page_config(page_title="Swiggy Support", page_icon="🛟", layout="wide")

# components
@st.cache_resource
def init_components():
    try:
        db_models = DatabaseModels()
        support_agents = SupportAgents()
        db_tools = DatabaseTools()
        photo_tools = PhotoAnalysisTools()
        return db_models, support_agents, db_tools, photo_tools
    except Exception as e:
        st.error(f"Init error: {str(e)}")
        return None, None, None, None

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.current_order = None
    st.session_state.current_ticket = None
    st.session_state.awaiting_photo = False
    st.session_state.issue_type = None
    st.session_state.first_interaction = True

def add_message_with_delay(content, delay=1.5):
    """Add message with natural typing delay"""
    if len(st.session_state.messages) > 1:
        time.sleep(delay)
    
    st.session_state.messages.append({"role": "assistant", "content": content})
    
    with st.chat_message("assistant"):
        st.markdown(content)

def main():
    st.title("🛟 Swiggy Support")
    
    components = init_components()
    if not all(components):
        st.error("System initialization failed")
        return
    
    db_models, support_agents, db_tools, photo_tools = components
    
    if st.session_state.first_interaction:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hi! Swiggy support se baat kar rahe ho. Kya problem hai?"
        })
        st.session_state.first_interaction = False
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Photo upload area
    if st.session_state.awaiting_photo:
        st.info("📸 Please upload a clear photo of the damaged item")
        uploaded_file = st.file_uploader(
            "Upload damage photo", 
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Max file size: 10MB"
        )
        
        if uploaded_file:
            validation = photo_tools.validate_photo_upload(uploaded_file)
            
            if not validation["valid"]:
                st.error(f"Upload error: {', '.join(validation['errors'])}")
            else:
                with st.spinner("Processing your photo..."):
                    save_result = db_tools.save_uploaded_photo(uploaded_file, st.session_state.current_ticket)
                    
                    if save_result["success"]:
                        analysis_result = photo_tools.analyze_damage_photo(save_result["file_path"])
                        
                        if analysis_result["success"]:
                            analysis = analysis_result["analysis"]
                            
                            photo_msg = "Photo mil gaya! Analysis kar raha hun..."
                            add_message_with_delay(photo_msg)
                            
                            if analysis["damage_detected"]:
                                damage_msg = f"Damage confirm ho gaya - {analysis['damage_severity']} level. Policy check kar raha hun..."
                                add_message_with_delay(damage_msg, 2.5)
                                
                                policy_decision = support_agents.get_policy_decision_with_reasoning(
                                    "damage",
                                    st.session_state.current_order,
                                    f"photo damage {analysis['damage_severity']}"
                                )
                                
                                if policy_decision["recommendation"] == "process_refund":
                                    resolution_msg = f"Policy ke according full refund approve ho gaya! ₹{st.session_state.current_order['amount']} refund process kar raha hun. 2-3 days mein account mein aa jayega."
                                elif policy_decision["recommendation"] == "offer_replacement":
                                    resolution_msg = "Replacement arrange kar raha hun. Same day delivery hoga!"
                                else:
                                    resolution_msg = "Admin approval leke solution dunga. Wait karo please."
                                
                                add_message_with_delay(resolution_msg, 3.0)
                            else:
                                no_damage_msg = "Photo mein clear damage nahi dikh raha, but customer satisfaction important hai. Replacement arrange kar raha hun."
                                add_message_with_delay(no_damage_msg, 2.0)
                        
                        st.session_state.awaiting_photo = False
                        st.rerun()
    
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Thinking..."):
            try:
                query_result = support_agents.classify_and_handle_query(
                    prompt,
                    st.session_state.messages,
                    {
                        "current_order": st.session_state.current_order,
                        "issue_type": st.session_state.issue_type,
                        "current_ticket": st.session_state.current_ticket
                    }
                )
                
                if query_result.get("needs_ai_response"):
                    response = support_agents.get_ai_response_with_context(
                        query_result,
                        prompt,
                        st.session_state.messages,
                        {
                            "current_order": st.session_state.current_order,
                            "issue_type": st.session_state.issue_type,
                            "current_ticket": st.session_state.current_ticket
                        }
                    )
                    
                    add_message_with_delay(response)
                    
                    order_id = support_agents.extract_order_id(prompt)
                    if order_id and not st.session_state.current_order:
                        st.session_state.current_order = support_agents.generate_order_data(order_id)
                        st.session_state.current_ticket = f"TKT{order_id}"
                    
                    detected_issue = support_agents.detect_issue_type(prompt, st.session_state.messages)
                    if detected_issue:
                        st.session_state.issue_type = detected_issue
                    
                    # for damage cases
                    if (st.session_state.issue_type == "damage" and 
                        st.session_state.current_order and 
                        not st.session_state.awaiting_photo):
                        photo_request = "Damage ki photo share karo please, main verify kar ke solution dunga!"
                        add_message_with_delay(photo_request, 2.0)
                        st.session_state.awaiting_photo = True
                
                st.rerun()
                
            except Exception as e:
                error_msg = "Technical problem aa gayi! Main help kar raha hun."
                add_message_with_delay(error_msg)
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
