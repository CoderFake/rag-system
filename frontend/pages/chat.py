import streamlit as st
from components.chat_ui import ChatUI
from components.loading_indicator import LoadingIndicator
from components.language_switcher import language_switcher
from utils.i18n import I18nManager
from utils.api_client import APIClient
import os

def chat_page():
  
    api_url = os.getenv("API_URL", "http://localhost:5000")
    api_client = APIClient(base_url=api_url)
    
    i18n_manager = I18nManager(locale_dir="./locales", default_locale="vi")
    loading_indicator = LoadingIndicator(i18n_manager)
    

    if "language" in st.session_state:
        i18n_manager.set_locale(st.session_state["language"])
    else:
        st.session_state["language"] = i18n_manager.current_locale
    

    st.set_page_config(
        page_title=i18n_manager.get_text("app_title"),
        page_icon="🧠",
        layout="wide"
    )
    

    with st.sidebar:

        st.image("https://via.placeholder.com/150x80?text=RAG+System", use_column_width=True)
        

        language_switcher(i18n_manager)
        

        st.markdown("### " + i18n_manager.get_text("about_system"))
        st.markdown(i18n_manager.get_text("system_description"))
        

        if st.button(i18n_manager.get_text("clear_chat")):
            st.session_state.messages = []
            st.experimental_rerun()
        

        st.divider()
        st.caption(f"Session ID: {st.session_state.get('session_id', 'N/A')}")
        st.caption(f"Language: {i18n_manager.current_locale}")
        

        if st.session_state.get("is_logged_in"):
            st.success(f"Logged in as: {st.session_state.get('user', 'Unknown')}")
            

            if st.button(i18n_manager.get_text("logout")):

                if "user" in st.session_state:
                    del st.session_state.user
                if "is_logged_in" in st.session_state:
                    del st.session_state.is_logged_in
                if "user_role" in st.session_state:
                    del st.session_state.user_role
                
                st.experimental_rerun()
        else:

            st.info(i18n_manager.get_text("login_prompt"))
            
            if st.button(i18n_manager.get_text("login_button")):
                st.session_state.show_login = True
                st.experimental_rerun()
    

    if st.session_state.get("show_login", False):
        from components.login_ui import render_login_ui, render_register_ui
        from user_auth import UserAuth
        

        auth = UserAuth(i18n_manager=i18n_manager)
        

        if st.session_state.get("show_register", False):
            render_register_ui(auth, i18n_manager)
        else:
            render_login_ui(auth, i18n_manager)
            

        if st.button(i18n_manager.get_text("back_to_chat")):
            st.session_state.show_login = False
            st.experimental_rerun()
    else:

        chat_ui = ChatUI(api_client, i18n_manager, loading_indicator)
        chat_ui.render()

if __name__ == "__main__":
    chat_page()