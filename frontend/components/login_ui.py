import streamlit as st
from typing import Dict, Any, Callable, Optional

def render_login_ui(i18n_manager, on_login: Optional[Callable] = None):
    st.title(i18n_manager.get_text("login_title"))

    with st.form("login_form"):
        username = st.text_input(i18n_manager.get_text("username"))
        password = st.text_input(i18n_manager.get_text("password"), type="password")
        remember = st.checkbox(i18n_manager.get_text("remember_me"))
        
        submit_button = st.form_submit_button(i18n_manager.get_text("login_button"))
        
        if submit_button:
            if not username or not password:
                st.error(i18n_manager.get_text("all_fields_required"))
            else:
                if on_login:
                    on_login(username, password, remember)
    
    st.markdown("---")
    st.markdown(i18n_manager.get_text("no_account_text"))
    
    if st.button(i18n_manager.get_text("register_button")):
        st.session_state.show_register = True
        st.experimental_rerun()


def render_register_ui(i18n_manager, on_register: Optional[Callable] = None):
    st.title(i18n_manager.get_text("register_title"))
    
    with st.form("register_form"):
        username = st.text_input(i18n_manager.get_text("username"))
        display_name = st.text_input(i18n_manager.get_text("display_name"))
        password = st.text_input(i18n_manager.get_text("password"), type="password")
        confirm_password = st.text_input(i18n_manager.get_text("confirm_password"), type="password")
        
        submit_button = st.form_submit_button(i18n_manager.get_text("register_button"))
        
        if submit_button:
            if not username or not password or not confirm_password:
                st.error(i18n_manager.get_text("all_fields_required"))
            elif password != confirm_password:
                st.error(i18n_manager.get_text("passwords_not_match"))
            else:
                if on_register:
                    on_register(username, display_name, password)
                
    if st.button(i18n_manager.get_text("back_to_login")):
        st.session_state.show_register = False
        st.experimental_rerun()