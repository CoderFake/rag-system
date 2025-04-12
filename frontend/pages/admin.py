import streamlit as st
from components.file_uploader import DocumentUploader
from components.loading_indicator import LoadingIndicator
from components.language_switcher import language_switcher
from utils.i18n import I18nManager

def admin_page():

    i18n_manager = I18nManager(locale_dir="./locales", default_locale="vi")
    loading_indicator = LoadingIndicator(i18n_manager)
    
    if "language" in st.session_state:
        i18n_manager.set_locale(st.session_state["language"])
    else:
        st.session_state["language"] = i18n_manager.current_locale
    
    st.set_page_config(
        page_title=i18n_manager.get_text("admin_title"),
        page_icon="🧠",
        layout="wide"
    )
    
    st.title(i18n_manager.get_text("admin_title"))
    
    with st.sidebar:
        language_switcher(i18n_manager)
    
    tab1, tab2, tab3 = st.tabs([
        i18n_manager.get_text("documents_manager"),
        i18n_manager.get_text("settings"),
        i18n_manager.get_text("system_logs")
    ])
    
    with tab1:
        document_uploader = DocumentUploader(
            document_service=st.session_state.get("document_service"),
            i18n_manager=i18n_manager,
            loading_indicator=loading_indicator
        )
        
        document_uploader.render()
    
    with tab2:
        st.header(i18n_manager.get_text("settings"))
        st.subheader(i18n_manager.get_text("chunking_settings"))
        chunk_size = st.slider(
            i18n_manager.get_text("chunk_size_label"),
            min_value=128,
            max_value=2048,
            value=512,
            step=64
        )
        
        chunk_overlap = st.slider(
            i18n_manager.get_text("chunk_overlap_label"),
            min_value=0,
            max_value=200,
            value=50,
            step=10
        )
        
        st.subheader(i18n_manager.get_text("llm_settings"))
        temperature = st.slider(
            i18n_manager.get_text("temperature_label"),
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
        
        if st.button(i18n_manager.get_text("save_settings")):
            st.session_state["chunk_size"] = chunk_size
            st.session_state["chunk_overlap"] = chunk_overlap
            st.session_state["temperature"] = temperature

            st.success(i18n_manager.get_text("settings_saved"))
    
    with tab3:
        st.header(i18n_manager.get_text("system_logs"))
        st.text("2025-04-12 10:15:23 INFO: Hệ thống khởi động")
        st.text("2025-04-12 10:15:25 INFO: Kết nối thành công đến ChromaDB")
        st.text("2025-04-12 10:16:02 INFO: Người dùng admin đăng nhập")
        st.text("2025-04-12 10:17:15 INFO: Tải lên tài liệu taichinh_2025.pdf")


if __name__ == "__main__":
    admin_page()