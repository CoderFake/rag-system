import streamlit as st
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from components.language_switcher import language_switcher
from components.loading_indicator import LoadingIndicator
from utils.i18n import I18nManager
from utils.api_client import APIClient

class SimpleAdminPage:
    def __init__(self, api_client, i18n_manager):
        self.api_client = api_client
        self.i18n = i18n_manager
        
        if "language" in st.session_state:
            self.i18n.set_locale(st.session_state["language"])
        else:
            st.session_state["language"] = self.i18n.current_locale
            
        self.loading_indicator = LoadingIndicator(self.i18n)
        
        if "upload_status" not in st.session_state:
            st.session_state.upload_status = None
            
        if "upload_progress" not in st.session_state:
            st.session_state.upload_progress = {}
            
    def render(self):
        st.set_page_config(
            page_title=self.i18n.get_text("admin_title"),
            page_icon="⚙️",
            layout="wide"
        )
        
        st.title("⚙️ " + self.i18n.get_text("admin_title"))
        
        with st.sidebar:
            language_switcher(self.i18n)
        

        tab1, tab2, tab3 = st.tabs([
            self.i18n.get_text("documents_manager"),
            self.i18n.get_text("settings"),
            self.i18n.get_text("system_logs")
        ])
        
        with tab1:
            self._render_document_manager()
        
        with tab2:
            self._render_settings()
        
        with tab3:
            self._render_system_logs()
    
    def _render_document_manager(self):
        st.header(self.i18n.get_text("knowledge_base_management"))
        
        st.subheader(self.i18n.get_text("upload_documents"))
        
        with st.form("upload_form", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                self.i18n.get_text("upload_prompt"), 
                accept_multiple_files=True,
                type=["pdf", "docx", "txt", "csv"]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                doc_title = st.text_input(self.i18n.get_text("doc_title_label"))
            with col2:
                doc_category = st.selectbox(
                    self.i18n.get_text("doc_category_label"),
                    options=["general", "technical", "policy", "faq"]
                )
                
            doc_tags = st.text_input(
                self.i18n.get_text("doc_tags_label"), 
                placeholder=self.i18n.get_text("doc_tags_placeholder")
            )
            
            doc_description = st.text_area(self.i18n.get_text("doc_description_label"))
            submit_button = st.form_submit_button(self.i18n.get_text("upload_button"))
            
            if submit_button and uploaded_files:
                self._process_uploads(uploaded_files, {
                    "title": doc_title,
                    "category": doc_category,
                    "tags": [tag.strip() for tag in doc_tags.split(",")] if doc_tags else [],
                    "description": doc_description
                })
        
        st.subheader(self.i18n.get_text("document_list"))
        

        try:
            documents = self.api_client.get_documents()
            
            if not documents:
                st.info(self.i18n.get_text("no_documents"))
            else:

                doc_list = []
                for doc in documents:
                    doc_data = {
                        "ID": doc.get("id", ""),
                        self.i18n.get_text("title_column"): doc.get("title", ""),
                        self.i18n.get_text("category_column"): doc.get("category", ""),
                        self.i18n.get_text("upload_date_column"): doc.get("created_at", "")[:19].replace("T", " "),
                        self.i18n.get_text("tags_column"): ", ".join(doc.get("tags", []))
                    }
                    doc_list.append(doc_data)
                
                st.dataframe(doc_list)
                

                col1, col2 = st.columns(2)
                
                with col1:

                    st.subheader(self.i18n.get_text("delete_document"))
                    doc_to_delete = st.selectbox(
                        self.i18n.get_text("select_doc_to_delete"),
                        options=[f"{doc.get('title', '')} ({doc.get('id', '')})" for doc in documents],
                        index=0
                    )
                    
                    doc_id = doc_to_delete.split("(")[-1].split(")")[0] if doc_to_delete else None
                    
                    if st.button(self.i18n.get_text("delete_document")):
                        if doc_id and st.checkbox(self.i18n.get_text("confirm_delete")):
                            try:
                                result = self.api_client.delete_document(doc_id)
                                if result.get("success"):
                                    st.success(self.i18n.get_text("delete_success"))
                                    time.sleep(1)
                                    st.experimental_rerun()
                                else:
                                    st.error(self.i18n.get_text("delete_error"))
                            except Exception as e:
                                st.error(f"{self.i18n.get_text('delete_error')}: {str(e)}")
                
                with col2:

                    st.subheader(self.i18n.get_text("reindex"))
                    if st.button(self.i18n.get_text("reindex_button")):
                        loading_container, progress_bar = self.loading_indicator.start_loading("reindexing")
                        
                        try:
                            result = self.api_client.reindex()
                            
                            if result.get("success"):
                                self.loading_indicator.complete_loading(loading_container, "reindex_success")
                            else:
                                with loading_container.container():
                                    st.error(self.i18n.get_text("reindex_error"))
                                    
                        except Exception as e:
                            with loading_container.container():
                                st.error(f"{self.i18n.get_text('reindex_error')}: {str(e)}")
        
        except Exception as e:
            st.error(f"{self.i18n.get_text('error')}: {str(e)}")
    
    def _process_uploads(self, files, metadata):
        loading_container, progress_bar = self.loading_indicator.start_loading("loading_data")
        st.session_state.upload_progress = {file.name: 0 for file in files}
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        metadata["batch_id"] = batch_id
        
        results = []
        total_files = len(files)
        
        for i, file in enumerate(files):
            try:
                file_metadata = metadata.copy()
                

                if not file_metadata["title"]:
                    file_metadata["title"] = file.name
                
                message_placeholder = st.empty()
                message_placeholder.info(f"{self.i18n.get_text('processing_file')}: {file.name}")
                
                progress_percentage = int((i / total_files) * 100)
                self.loading_indicator.update_progress(progress_bar, progress_percentage)
                
                result = self.api_client.process_file(file, file_metadata)
                results.append(result)
                
                st.session_state.upload_progress[file.name] = 100
                
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
                st.session_state.upload_progress[file.name] = -1
        
        self.loading_indicator.update_progress(progress_bar, 100)
        self.loading_indicator.complete_loading(loading_container, "processing_complete")
        
        st.success(self.i18n.get_text("upload_success_msg").format(count=len(results)))
    
    def _render_settings(self):
        st.header(self.i18n.get_text("settings"))
        
        try:

            settings = self.api_client.get_settings()
            

            st.subheader(self.i18n.get_text("chunking_settings"))
            
            chunk_size = st.slider(
                self.i18n.get_text("chunk_size_label"),
                min_value=128,
                max_value=2048,
                value=settings.get("chunk_size", 512),
                step=64
            )
            
            chunk_overlap = st.slider(
                self.i18n.get_text("chunk_overlap_label"),
                min_value=0,
                max_value=200,
                value=settings.get("chunk_overlap", 50),
                step=10
            )
            

            st.subheader(self.i18n.get_text("llm_settings"))
            
            temperature = st.slider(
                self.i18n.get_text("temperature_label"),
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1
            )
            
            if st.button(self.i18n.get_text("save_settings")):
                try:
                    result = self.api_client.update_settings({
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "temperature": temperature
                    })
                    
                    if result.get("success"):
                        st.success(self.i18n.get_text("settings_saved"))
                    else:
                        st.error(self.i18n.get_text("settings_error"))
                        
                except Exception as e:
                    st.error(f"{self.i18n.get_text('settings_error')}: {str(e)}")
        
        except Exception as e:
            st.error(f"{self.i18n.get_text('error')}: {str(e)}")
            
    def _render_system_logs(self):
        st.header(self.i18n.get_text("system_logs"))
        

        log_examples = [
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO: Hệ thống khởi động",
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO: Kết nối thành công đến ChromaDB",
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO: Kết nối thành công đến MySQL",
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO: Người dùng admin đăng nhập",
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO: Tải lên tài liệu taichinh_2025.pdf"
        ]
        
        for log in log_examples:
            st.text(log)
        
        st.info(self.i18n.get_text("log_placeholder_info"))


if __name__ == "__main__":
    api_url = os.getenv("API_URL", "http://localhost:5000")
    api_client = APIClient(base_url=api_url)
    i18n_manager = I18nManager(locale_dir="./locales", default_locale="vi")
    
    admin_page = SimpleAdminPage(api_client, i18n_manager)
    admin_page.render()