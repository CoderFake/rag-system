import streamlit as st
import time
from datetime import datetime
import os
import threading
from concurrent.futures import ThreadPoolExecutor

class DocumentUploader:
    """
    Component cho phép upload tài liệu với loading indicator
    """
    
    def __init__(self, document_service, i18n_manager, loading_indicator):
        self.document_service = document_service
        self.i18n = i18n_manager
        self.loading_indicator = loading_indicator
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.progress_dict = {}  # Theo dõi tiến trình xử lý
        
    def render(self):
        """Hiển thị form upload tài liệu"""
        st.header(self.i18n.get_text("admin_documents_title"))
        
        # Form upload
        with st.form(key="upload_form", clear_on_submit=True):
            # Chọn file
            uploaded_files = st.file_uploader(
                self.i18n.get_text("upload_prompt"), 
                accept_multiple_files=True,
                type=["pdf", "docx", "txt", "csv"]
            )
            
            # Metadata
            col1, col2 = st.columns(2)
            with col1:
                doc_title = st.text_input(self.i18n.get_text("doc_title_label"))
            with col2:
                doc_category = st.selectbox(
                    self.i18n.get_text("doc_category_label"),
                    options=["general", "technical", "policy", "faq"]
                )
                
            doc_tags = st.text_input(self.i18n.get_text("doc_tags_label"), 
                                    placeholder=self.i18n.get_text("doc_tags_placeholder"))
            
            # Nút submit
            submit_button = st.form_submit_button(self.i18n.get_text("upload_button"))
        
        # Xử lý khi form được submit
        if submit_button and uploaded_files:
            # Container cho loading indicator
            loading_container, progress_bar = self.loading_indicator.start_loading("loading_data")
            
            # Khởi tạo tiến trình cho mỗi file
            self.progress_dict = {file.name: 0 for file in uploaded_files}
            
            # ID xử lý cho batch này
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Xây dựng metadata
            metadata = {
                "title": doc_title,
                "category": doc_category,
                "tags": [tag.strip() for tag in doc_tags.split(",")] if doc_tags else [],
                "upload_date": datetime.now().isoformat(),
                "batch_id": batch_id
            }
            
            # Tạo list công việc xử lý
            processing_tasks = []
            
            for file in uploaded_files:
                # Thêm công việc xử lý vào danh sách
                processing_tasks.append((file, metadata.copy()))
            
            # Bắt đầu thread xử lý
            thread = threading.Thread(
                target=self._process_files_batch,
                args=(processing_tasks, loading_container, progress_bar)
            )
            thread.start()
            
            # Hiển thị cập nhật tiến trình
            self._update_progress_ui(loading_container, progress_bar, len(processing_tasks))
    
    def _process_files_batch(self, processing_tasks, loading_container, progress_bar):
        """
        Xử lý batch các file trong thread riêng biệt
        
        Args:
            processing_tasks: List các tuple (file, metadata)
            loading_container: Container cho loading indicator
            progress_bar: Progress bar để cập nhật
        """
        results = []
        total_files = len(processing_tasks)
        
        for i, (file, metadata) in enumerate(processing_tasks):
            try:
                file_metadata = metadata.copy()
                file_metadata["filename"] = file.name
                file_metadata["file_size"] = file.size
                file_metadata["file_type"] = os.path.splitext(file.name)[1].lower()
                
                result = self.document_service.process_file(file, file_metadata)
                results.append(result)
                
                self.progress_dict[file.name] = 100
                
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
                self.progress_dict[file.name] = -1 
        
        self.loading_indicator.complete_loading(loading_container, "processing_complete")
        
        st.success(self.i18n.get_text("upload_success_msg").format(count=len(results)))
    
    def _update_progress_ui(self, loading_container, progress_bar, total_files):

        placeholder = st.empty()
        
        while any(progress < 100 and progress >= 0 for progress in self.progress_dict.values()):
            valid_progresses = [p for p in self.progress_dict.values() if p >= 0]
            if valid_progresses:
                avg_progress = sum(valid_progresses) / len(valid_progresses)
            else:
                avg_progress = 0
                
            self.loading_indicator.update_progress(progress_bar, avg_progress)
            
            progress_text = ""
            for filename, progress in self.progress_dict.items():
                if progress < 0:
                    status = "❌ " + self.i18n.get_text("error_status")
                elif progress < 100:
                    status = "⏳ " + self.i18n.get_text("processing_status")
                else:
                    status = "✅ " + self.i18n.get_text("complete_status")
                    
                progress_text += f"{filename}: {status} ({progress}%)\n"
                
            with placeholder.container():
                st.text(progress_text)
                
            time.sleep(0.2)
            
        placeholder.empty()