import streamlit as st
import time

class LoadingIndicator:
    """
    Component hiển thị trạng thái loading và tiến trình xử lý
    """
    
    def __init__(self, i18n_manager):
        self.i18n_manager = i18n_manager
        
    def start_loading(self, message_key="loading_data"):

        message = self.i18n_manager.get_text(message_key)
        
        loading_container = st.empty()
        
        with loading_container.container():
            st.warning(f"⏳ {message}")
            progress_bar = st.progress(0)
            
        return loading_container, progress_bar
        
    def update_progress(self, progress_bar, value, progress_key="processing_progress"):
        """
        Cập nhật tiến trình của progress bar
        
        Args:
            progress_bar: Progress bar object để cập nhật
            value: Giá trị tiến trình (0-100)
            progress_key: Khóa i18n cho thông báo tiến trình
        """
        progress_bar.progress(value / 100)
        
    def complete_loading(self, loading_container, success_key="processing_complete"):
        """
        Hoàn thành quá trình loading và hiển thị thông báo thành công
        
        Args:
            loading_container: Container chứa loading indicator
            success_key: Khóa i18n cho thông báo thành công
        """
        message = self.i18n_manager.get_text(success_key)
        
        with loading_container.container():
            st.success(f"✅ {message}")
            
        time.sleep(3)
        loading_container.empty()