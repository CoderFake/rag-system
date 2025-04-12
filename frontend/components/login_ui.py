import streamlit as st
from typing import Dict, Any, Callable, Optional

def render_login_ui(auth, i18n_manager, on_login: Optional[Callable] = None):
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
                success, message = auth.authenticate(username, password)
                
                if success:
                    st.session_state.user = username
                    st.session_state.is_logged_in = True
                    st.session_state.user_role = auth.get_user_role(username)
                    
                    if remember:
                        expiry = datetime.now() + timedelta(days=7)
                        st.session_state.session_expiry = expiry.isoformat()
                    
                    st.success(message)
                    
                    if on_login:
                        on_login(username, auth.get_user_role(username))
                    
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error(message)
    
    st.markdown("---")
    st.markdown(i18n_manager.get_text("no_account_text"))
    
    if st.button(i18n_manager.get_text("register_button")):
        st.session_state.show_register = True


def render_register_ui(auth, i18n_manager):

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
                success, message = auth.create_user(
                    username=username,
                    password=password,
                    role="user",
                    name=display_name
                )
                
                if success:
                    st.success(message)
                    st.session_state.show_register = False
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error(message)
    
    if st.button(i18n_manager.get_text("back_to_login")):
        st.session_state.show_register = False
        st.experimental_rerun()