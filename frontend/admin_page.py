import streamlit as st
import os
import time
from datetime import datetime
from typing import Dict, List, Any

from components.language_switcher import language_switcher
from components.loading_indicator import LoadingIndicator
from utils.i18n import I18nManager
from utils.api_client import APIClient

class SimpleAdminPage:
    def __init__(self):
        api_url = os.getenv("API_URL", "http://localhost:5000")
        self.api_client = APIClient(base_url=api_url)
        self.i18n = I18nManager(locale_dir="./locales", default_locale="vi")
        
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
        
        self._check_authentication()
        
        if not st.session_state.get("admin_authenticated", False):
            self._render_login()
        else:
            self._render_admin_dashboard()
    
    def _check_authentication(self):
        if "admin_authenticated" not in st.session_state:
            st.session_state.admin_authenticated = False
    
    def _render_login(self):

        with st.sidebar:
            language_switcher(self.i18n)
        
        st.title("🔒 " + self.i18n.get_text("admin_login"))
        
        with st.form("admin_login_form"):
            password = st.text_input(
                self.i18n.get_text("admin_password"),
                type="password"
            )
            
            submit = st.form_submit_button(self.i18n.get_text("login_button"))
            
            if submit:

                if password == "admin123":
                    st.session_state.admin_authenticated = True
                    st.success(self.i18n.get_text("login_success"))
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error(self.i18n.get_text("login_error"))
    
    def _render_admin_dashboard(self):
        with st.sidebar:
            language_switcher(self.i18n)
            
            st.title(self.i18n.get_text("admin_title"))
            
            if st.button(self.i18n.get_text("logout")):
                st.session_state.admin_authenticated = False
                st.experimental_rerun()
        
        st.title("📚 " + self.i18n.get_text("knowledge_base_management"))
        
        st.header(self.i18n.get_text("upload_documents"))
        
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
                loading_container, progress_bar = self.loading_indicator.start_loading("loading_data")
                st.session_state.upload_progress = {file.name: 0 for file in uploaded_files}
                batch_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                metadata = {
                    "title": doc_title,
                    "category": doc_category,
                    "tags": [tag.strip() for tag in doc_tags.split(",")] if doc_tags else [],
                    "description": doc_description,
                    "upload_date": datetime.now().isoformat(),
                    "batch_id": batch_id
                }
                
                results = []
                total_files = len(uploaded_files)
                
                for i, file in enumerate(uploaded_files):
                    try:
                        file_metadata = metadata.copy()
                        file_metadata["filename"] = file.name
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
        
        st.header(self.i18n.get_text("document_list"))
        
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
                        self.i18n.get_text("upload_date_column"): doc.get("upload_date", ""),
                        self.i18n.get_text("tags_column"): ", ".join(doc.get("tags", []))
                    }
                    doc_list.append(doc_data)
                
                st.dataframe(doc_list)
                
                doc_to_delete = st.selectbox(
                    self.i18n.get_text("select_doc_to_delete"),
                    options=[doc["title"] for doc in documents],
                    index=0
                )
                
                if st.button(self.i18n.get_text("delete_document")):

                    doc_id = None
                    for doc in documents:
                        if doc.get("title") == doc_to_delete:
                            doc_id = doc.get("id")
                            break
                    
                    if doc_id:

                        if st.checkbox(self.i18n.get_text("confirm_delete")):

                            result = self.api_client.delete_document(doc_id)
                            if result.get("success"):
                                st.success(self.i18n.get_text("delete_success"))
                                time.sleep(1)
                                st.experimental_rerun()
                            else:
                                st.error(self.i18n.get_text("delete_error"))
        
        except Exception as e:
            st.error(f"Error fetching documents: {str(e)}")

if __name__ == "__main__":
    admin_page = SimpleAdminPage()
    admin_page.render()