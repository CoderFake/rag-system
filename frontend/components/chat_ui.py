import streamlit as st
from typing import Dict, List, Any, Optional
import time
import uuid

class ChatUI:
    def __init__(self, api_client, i18n_manager, loading_indicator):
        self.api_client = api_client
        self.i18n = i18n_manager
        self.loading_indicator = loading_indicator
        

        if "messages" not in st.session_state:
            st.session_state.messages = []
            

            st.session_state.messages.append({
                "role": "assistant", 
                "content": self.i18n.get_text("welcome_message"),
                "type": "text"
            })
            

        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            

        if not st.session_state.messages or len(st.session_state.messages) <= 1:
            self._load_chat_history()
    
    def render(self):
        st.title("💬 " + self.i18n.get_text("chat_title"))
        

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
        

        if st.session_state.messages and len(st.session_state.messages) > 1:
            last_msgs = [msg for msg in st.session_state.messages if msg["role"] == "assistant" and msg["type"] == "text"]
            if last_msgs:
                last_msg = last_msgs[-1]
                if "response_id" in last_msg and not last_msg.get("feedback_given"):
                    with st.container():
                        col1, col2, col3 = st.columns([1, 1, 10])
                        with col1:
                            if st.button("👍", key="thumbs_up"):
                                self._add_feedback(last_msg["response_id"], "thumbs_up")
                                last_msg["feedback_given"] = True
                                st.experimental_rerun()
                        with col2:
                            if st.button("👎", key="thumbs_down"):
                                self._add_feedback(last_msg["response_id"], "thumbs_down")
                                last_msg["feedback_given"] = True
                                st.experimental_rerun()
        

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
                

                assistant_message = {
                    "role": "assistant", 
                    "content": response["response"],
                    "type": "text",
                    "query_id": response.get("query_id"),
                    "response_id": response.get("response_id"),
                    "route_type": response.get("route_type", "rag")
                }
                
                st.session_state.messages.append(assistant_message)
                

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
    
    def _load_chat_history(self):
        try:
            result = self.api_client.get_chat_history(st.session_state.session_id)
            history = result.get("history", [])
            
            if not history:
                return
                

            st.session_state.messages = []
            
            for item in history:
                if item["type"] == "query":
                    st.session_state.messages.append({
                        "role": "user",
                        "content": item["content"],
                        "type": "text"
                    })
                elif item["type"] == "response":
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": item["content"],
                        "type": "text",
                        "response_id": item["id"],
                        "query_id": item["query_id"]
                    })
                    

                    if item.get("sources"):
                        sources_content = ""
                        for i, source in enumerate(item["sources"]):
                            title = source.get("title", "Unknown")
                            category = source.get("category", "N/A")
                            sources_content += f"**{i+1}. {title}**\n"
                            sources_content += f"Category: {category}\n\n"
                        
                        if sources_content:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": sources_content,
                                "type": "sources"
                            })
            

            if not st.session_state.messages:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": self.i18n.get_text("welcome_message"),
                    "type": "text"
                })
        except:

            if not st.session_state.messages:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": self.i18n.get_text("welcome_message"),
                    "type": "text"
                })
    
    def _add_feedback(self, response_id: str, feedback_type: str, value: str = ""):
        try:
            self.api_client.add_feedback(response_id, feedback_type, value)
            

            if feedback_type == "thumbs_up":
                st.success(self.i18n.get_text("feedback_thanks_positive"))
            else:
                st.warning(self.i18n.get_text("feedback_thanks_negative"))
                
        except Exception as e:
            st.error(f"{self.i18n.get_text('feedback_error')}: {str(e)}")
    
    def clear_chat(self):
        """Xóa lịch sử chat"""
        st.session_state.messages = []

        st.session_state.messages.append({
            "role": "assistant", 
            "content": self.i18n.get_text("welcome_message"),
            "type": "text"
        })
        
        st.experimental_rerun()