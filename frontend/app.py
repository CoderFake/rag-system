import streamlit as st
import os
from datetime import datetime
import uuid

from components.chat_ui import ChatUI
from components.loading_indicator import LoadingIndicator
from components.language_switcher import language_switcher
from components.login_ui import render_login_ui, render_register_ui

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
    
if "messages" not in st.session_state:
    st.session_state.messages = []


i18n_manager.set_locale(st.session_state.language)

st.set_page_config(
    page_title=i18n_manager.get_text("app_title"),
    page_icon="🧠",
    layout="wide"
)

if "token" in st.session_state:
    api_client.set_token(
        st.session_state.token,
        st.session_state.get("refresh_token")
    )

def check_user_auth():
    if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
        return False
        
    try:

        profile = api_client.get_profile()
        if "user" in profile:
            return True
    except:

        if "is_logged_in" in st.session_state:
            del st.session_state.is_logged_in
        if "user" in st.session_state:
            del st.session_state.user
        if "token" in st.session_state:
            del st.session_state.token
        if "refresh_token" in st.session_state:
            del st.session_state.refresh_token
        api_client.clear_token()
        
    return False


def logout():
    if "is_logged_in" in st.session_state:
        del st.session_state.is_logged_in
    if "user" in st.session_state:
        del st.session_state.user
    if "token" in st.session_state:
        del st.session_state.token
    if "refresh_token" in st.session_state:
        del st.session_state.refresh_token
    if "user_role" in st.session_state:
        del st.session_state.user_role
    api_client.clear_token()
    st.experimental_rerun()

def on_login_success(user, token, refresh_token):
    st.session_state.is_logged_in = True
    st.session_state.user = user
    st.session_state.token = token
    st.session_state.refresh_token = refresh_token
    st.session_state.user_role = user.get("role", "user")
    
    api_client.set_token(token, refresh_token)
    
    st.session_state.show_login = False
    st.session_state.show_register = False
    st.experimental_rerun()

with st.sidebar:
    st.image("https://via.placeholder.com/150x80?text=RAG+System", use_column_width=True)
    language_switcher(i18n_manager)
    st.title(i18n_manager.get_text("app_title"))
    
    if check_user_auth():
        st.success(f"🧑‍💻 {st.session_state.user.get('name', st.session_state.user.get('username', 'User'))}")
        
        if st.session_state.user_role == "admin":
            st.info(i18n_manager.get_text("admin_role"))
    
    options = [i18n_manager.get_text("chat_page")]
    
    if check_user_auth() and st.session_state.user_role == "admin":
        options.append(i18n_manager.get_text("admin_page"))
    
    selected_page = st.radio(
        i18n_manager.get_text("navigation"),
        options=options
    )
    
    if selected_page == i18n_manager.get_text("chat_page"):
        st.session_state.page = "chat"
    else:
        st.session_state.page = "admin"
    
    st.divider()
    
    if check_user_auth():
        if st.button(i18n_manager.get_text("logout")):
            logout()
    else:
        if st.button(i18n_manager.get_text("login_button")):
            st.session_state.show_login = True
            st.session_state.page = "chat"
            st.experimental_rerun()
    
    if st.session_state.page == "chat" and "messages" in st.session_state:
        if st.button(i18n_manager.get_text("clear_chat")):
            st.session_state.messages = []
            st.experimental_rerun()
    
    st.caption(f"Session ID: {st.session_state.get('session_id', 'N/A')}")
    st.caption(f"Language: {i18n_manager.current_locale}")

if st.session_state.get("show_login", False):
    from auth.jwt_manager import JWTManager
    
    if st.session_state.get("show_register", False):
        def handle_register(username, name, password):
            try:
                result = api_client.register(
                    username=username,
                    password=password,
                    name=name
                )
                
                st.success(i18n_manager.get_text("user_created"))
                
                login_result = api_client.login(username, password)
                
                if "access_token" in login_result:
                    on_login_success(
                        login_result.get("user"),
                        login_result.get("access_token"),
                        login_result.get("refresh_token")
                    )
                    
            except Exception as e:
                st.error(str(e))
                
        render_register_ui(i18n_manager, handle_register)
    else:
        def handle_login(username, password, remember):
            try:
                result = api_client.login(username, password)
                
                if "access_token" in result:
                    on_login_success(
                        result.get("user"),
                        result.get("access_token"),
                        result.get("refresh_token")
                    )
                else:
                    st.error(i18n_manager.get_text("login_error"))
                    
            except Exception as e:
                st.error(str(e))
                
        render_login_ui(i18n_manager, handle_login)
        
    if st.button(i18n_manager.get_text("back_to_chat")):
        st.session_state.show_login = False
        st.experimental_rerun()
        

elif st.session_state.page == "chat":

    chat_ui = ChatUI(api_client, i18n_manager, loading_indicator)
    chat_ui.render()
    
elif st.session_state.page == "admin":

    if check_user_auth() and st.session_state.user_role == "admin":
        admin_page = SimpleAdminPage(api_client, i18n_manager)
        admin_page.render()
    else:
        st.warning(i18n_manager.get_text("admin_required"))
        
        if st.button(i18n_manager.get_text("login_button")):
            st.session_state.show_login = True
            st.experimental_rerun()

st.caption("© 2025 RAG System| " + i18n_manager.get_text("footer_text"))

if __name__ == "__main__":
    pass