
import streamlit as st
import os
from datetime import datetime
import uuid

from components.chat_ui import ChatUI
from components.loading_indicator import LoadingIndicator
from components.language_switcher import language_switcher

from utils.i18n import I18nManager
from utils.api_client import APIClient

from admin_page import SimpleAdminPage

API_URL = os.getenv("API_URL", "http://localhost:5000")

api_client = APIClient(base_url=API_URL)
i18n_manager = I18nManager(locale_dir="./locales", default_locale="vi")
loading_indicator = LoadingIndicator(i18n_manager)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if "language" not in st.session_state:
    st.session_state.language = "vi"
    
if "page" not in st.session_state:
    st.session_state.page = "chat"

i18n_manager.set_locale(st.session_state.language)

st.set_page_config(
    page_title=i18n_manager.get_text("app_title"),
    page_icon="🧠",
    layout="wide"
)


with st.sidebar:

    st.image("https://via.placeholder.com/150x80?text=RAG+System", use_column_width=True)
    language_switcher(i18n_manager)
    st.title(i18n_manager.get_text("app_title"))
    
    selected_page = st.radio(
        i18n_manager.get_text("navigation"),
        options=[
            i18n_manager.get_text("chat_page"),
            i18n_manager.get_text("admin_page")
        ]
    )
    
    if selected_page == i18n_manager.get_text("chat_page"):
        st.session_state.page = "chat"
    else:
        st.session_state.page = "admin"
    
    st.divider()
    st.caption(f"Session ID: {st.session_state.get('session_id', 'N/A')}")
    st.caption(f"Language: {i18n_manager.current_locale}")
    
    if st.session_state.page == "chat" and "messages" in st.session_state:
        if st.button(i18n_manager.get_text("clear_chat")):
            st.session_state.messages = []
            st.experimental_rerun()


if st.session_state.page == "chat":

    if "messages" not in st.session_state:
        st.session_state.messages = []

        st.session_state.messages.append({
            "role": "assistant", 
            "content": i18n_manager.get_text("welcome_message"),
            "type": "text"
        })
    
    chat_ui = ChatUI(api_client, i18n_manager, loading_indicator)
    chat_ui.render()
    
else:
    admin_page = SimpleAdminPage()
    admin_page.render()

st.caption("© 2025 RAG System with Gemini AI | " + i18n_manager.get_text("footer_text"))

if __name__ == "__main__":
    pass