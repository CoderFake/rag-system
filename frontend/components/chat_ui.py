import streamlit as st
from typing import Dict, List, Any, Optional
import time

class ChatUI:
    def __init__(self, api_client, i18n_manager, loading_indicator):
        self.api_client = api_client
        self.i18n = i18n_manager
        self.loading_indicator = loading_indicator
        

        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        if "session_id" not in st.session_state:
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
    
    def render(self):
        st.title("💬 " + self.i18n.get_text("chat_title"))
        

        if not st.session_state.messages:
            welcome_message = self.i18n.get_text("welcome_message")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": welcome_message,
                "type": "text"
            })
        

        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            msg_type = message.get("type", "text")
            
            with st.chat_message(role):
                if msg_type == "text":
                    st.write(content)
                elif msg_type == "error":
                    st.error(content)
                elif msg_type == "sources":
                    with st.expander(self.i18n.get_text("sources_label")):
                        st.write(content)
        

        if prompt := st.chat_input(self.i18n.get_text("chat_placeholder")):

            st.session_state.messages.append({
                "role": "user", 
                "content": prompt,
                "type": "text"
            })
            

            with st.chat_message("user"):
                st.write(prompt)
            

            self._process_query(prompt)
    
    def _process_query(self, query: str):
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            loading_container, _ = self.loading_indicator.start_loading("processing_query")
            
            try:
                response = self.api_client.chat(
                    query=query,
                    session_id=st.session_state.session_id,
                    language=self.i18n.current_locale
                )
                
                loading_container.empty()
                
                message_placeholder.write(response["response"])
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["response"],
                    "type": "text"
                })
                
                if response.get("source_documents"):
                    sources_content = ""
                    for i, source in enumerate(response["source_documents"]):
                        title = source.get("title", "Unknown")
                        category = source.get("category", "N/A")
                        sources_content += f"**{i+1}. {title}**\n"
                        sources_content += f"Category: {category}\n\n"
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": sources_content,
                        "type": "sources"
                    })
                    
                    with st.expander(self.i18n.get_text("sources_label")):
                        st.write(sources_content)
                
            except Exception as e:

                loading_container.empty()
                

                error_msg = self.i18n.get_text("error_message")
                full_error = f"{error_msg}: {str(e)}"
                
                message_placeholder.error(full_error)
                

                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_error,
                    "type": "error"
                })
    
    def clear_chat(self):
        st.session_state.messages = []
        

        welcome_message = self.i18n.get_text("welcome_message")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": welcome_message,
            "type": "text"
        })
        
        st.experimental_rerun()