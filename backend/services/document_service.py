from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader
)
import os
import tempfile
from werkzeug.utils import secure_filename
import logging
import uuid

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, chroma_manager, db_manager=None):
        self.chroma_manager = chroma_manager
        self.db_manager = db_manager
        self.loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
            '.csv': CSVLoader
        }
        logger.info("Khởi tạo DocumentService thành công")
        
    def process_file(self, file, metadata=None):
        if metadata is None:
            metadata = {}
            
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in self.loaders:
            raise ValueError(f"Định dạng file không được hỗ trợ: {file_ext}")
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
            
        try:
            logger.info(f"Bắt đầu xử lý file: {filename}")
            
            loader_class = self.loaders[file_ext]
            loader = loader_class(tmp_path)
            documents = loader.load()
            
            tags_list = metadata.get("tags", [])
            tags_string = ", ".join(tags_list) if tags_list else ""
            
            doc_id = metadata.get("id", str(uuid.uuid4()))
            metadata["id"] = doc_id
            
            chroma_metadata = metadata.copy()
            if "tags" in chroma_metadata:
                chroma_metadata["tags_str"] = tags_string
                del chroma_metadata["tags"]
                    
            if metadata:
                for doc in documents:
                    if not isinstance(doc.metadata, dict):
                        doc.metadata = {}

                    doc.metadata.update(chroma_metadata)
                    
            chunked_docs = []
            for doc in documents:
                chunks = self.chroma_manager.chunk_document(doc.page_content, doc.metadata)
                chunked_docs.extend(chunks)
                
            self.chroma_manager.add_documents(chunked_docs)
            
            if self.db_manager and hasattr(self.db_manager, 'save_document'):
                from models.document import Document
                
                doc_obj = Document(
                    id=doc_id,
                    title=metadata.get("title", filename),
                    file_path=tmp_path, 
                    file_type=file_ext,
                    category=metadata.get("category", "general"),
                    tags=tags_list, 
                    user_id=metadata.get("user_id")
                )
                
                self.db_manager.save_document(doc_obj)
            
            logger.info(f"Đã xử lý thành công file: {filename}, tạo {len(chunked_docs)} chunks")
            
            return {
                "status": "success",
                "document_id": doc_id,
                "num_chunks": len(chunked_docs),
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Lỗi xử lý file {filename}: {str(e)}")
            raise
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    def get_all_documents(self, page=1, limit=10, category=None):
        if not self.db_manager or not hasattr(self.db_manager, 'get_all_documents'):
            logger.warning("Không có db_manager hoặc phương thức get_all_documents")
            return []
            
        try:
            return self.db_manager.get_all_documents(page, limit, category)
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách tài liệu: {str(e)}")
            return []
            
    def delete_document(self, document_id):
        success = False

        if self.db_manager and hasattr(self.db_manager, 'delete_document'):
            try:
                success = self.db_manager.delete_document(document_id)
            except Exception as e:
                logger.error(f"Lỗi khi xoá tài liệu từ database: {str(e)}")
                success = False
        
        return success
        
    def reindex_all(self):
        return True