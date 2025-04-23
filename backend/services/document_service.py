from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader
)
import os
import tempfile
import shutil
from werkzeug.utils import secure_filename
import logging
import uuid
from datetime import datetime
import json

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
            
            try:
                documents = loader.load()
            except Exception as e:
                logger.error(f"Lỗi khi đọc file {filename}: {str(e)}")
                documents = []
            
            if not documents:
                logger.warning(f"Không thể trích xuất nội dung từ file {filename}")
                raise ValueError(f"Không thể trích xuất nội dung từ file {filename}")
                
            valid_documents = []
            for doc in documents:
                if hasattr(doc, 'page_content') and doc.page_content and doc.page_content.strip():
                    valid_documents.append(doc)
            
            if not valid_documents:
                logger.warning(f"Sau khi lọc, không còn nội dung hợp lệ trong file {filename}")
                raise ValueError(f"Không có nội dung hợp lệ trong file {filename}")
            
            doc_id = metadata.get("id", str(uuid.uuid4()))
            metadata["id"] = doc_id
            
            if "tags" in metadata and isinstance(metadata["tags"], list):
                metadata["tags_str"] = json.dumps(metadata["tags"])
            else:
                metadata["tags_str"] = "[]"
                
            for doc in valid_documents:
                if not isinstance(doc.metadata, dict):
                    doc.metadata = {}
                doc.metadata.update(metadata)
                
            chunked_docs = []
            chunk_count = 0
            
            for doc in valid_documents:
                chunks = self.chroma_manager.chunk_document(doc.page_content, doc.metadata)
                
                if not chunks:
                    logger.warning(f"Không thể tạo chunks từ nội dung của file {filename}")
                    continue
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{chunk_count + i}"
                    
                    safe_metadata = {
                        "id": chunk_id,      
                        "document_id": doc_id, 
                        "chunk_index": i,   
                        "title": metadata.get("title", filename),
                        "file_path": tmp_path,
                        "file_type": file_ext,
                        "category": metadata.get("category", "general"),
                        "tags_str": metadata.get("tags_str", "[]") 
                    }
                    
                    chunk.metadata = safe_metadata
                
                chunked_docs.extend(chunks)
                chunk_count += len(chunks)
            
            if not chunked_docs:
                logger.warning(f"Không thể tạo bất kỳ chunk nào từ file {filename}")
                raise ValueError(f"Không thể tạo chunks từ file {filename}")
                
            results = self.chroma_manager.add_documents(chunked_docs)
            
            if not results:
                logger.warning(f"Không thể thêm chunks vào vector store cho file {filename}")
            
            if self.db_manager and hasattr(self.db_manager, 'save_document'):
                from models.document import Document
                
                doc_obj = Document(
                    id=doc_id,
                    title=metadata.get("title", filename),
                    file_path=tmp_path, 
                    file_type=file_ext,
                    category=metadata.get("category", "general"),
                    tags=metadata.get("tags", []), 
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
        
        try:
            vector_store_success = self.chroma_manager.delete_by_document_id(document_id)
            logger.info(f"Xoá các chunk từ vector store: {vector_store_success}")
            if not success and vector_store_success:
                success = True
        except Exception as e:
            logger.error(f"Lỗi khi xoá các chunk từ vector store: {str(e)}")

        return success
        
    def reindex_all(self):

        try:
            if not self.db_manager:
                logger.warning("Không có db_manager, không thể đánh chỉ mục lại")
                return False
                
            all_documents = self.db_manager.get_all_documents(limit=9999)
            
            if not all_documents:
                logger.warning("Không có tài liệu nào trong cơ sở dữ liệu")
                return True
                
            try:
                self.chroma_manager.delete_collection()
                logger.info("Đã xoá collection cũ")
            except Exception as e:
                logger.error(f"Lỗi khi xoá collection: {str(e)}")
            
            chunked_docs = []
            
            for doc in all_documents:
                try:
                    if not os.path.exists(doc.get('file_path', '')):
                        logger.warning(f"File không tồn tại: {doc.get('file_path')}, bỏ qua tài liệu {doc.get('id')}")
                        continue
                        
                    file_ext = os.path.splitext(doc.get('file_path', ''))[1].lower()
                    if file_ext not in self.loaders:
                        logger.warning(f"Định dạng không được hỗ trợ: {file_ext}, bỏ qua tài liệu {doc.get('id')}")
                        continue
                        
                    metadata = {
                        "id": doc.get('id'),
                        "title": doc.get('title', ''),
                        "file_path": doc.get('file_path', ''),
                        "file_type": doc.get('file_type', ''),
                        "category": doc.get('category', 'general'),
                        "user_id": doc.get('user_id')
                    }
                    
                    tags = doc.get('tags', [])
                    if isinstance(tags, list):
                        metadata["tags_str"] = json.dumps(tags)
                    else:
                        metadata["tags_str"] = "[]"
                    
                    loader_class = self.loaders[file_ext]
                    try:
                        loader = loader_class(doc.get('file_path'))
                        documents = loader.load()
                        
                        valid_documents = []
                        for document in documents:
                            if hasattr(document, 'page_content') and document.page_content and document.page_content.strip():
                                valid_documents.append(document)
                        
                        if not valid_documents:
                            logger.warning(f"Không có nội dung hợp lệ trong tài liệu {doc.get('id')}")
                            continue
                            
                        for doc_content in valid_documents:
                            doc_content.metadata.update(metadata)
                            chunks = self.chroma_manager.chunk_document(doc_content.page_content, doc_content.metadata)
                            if chunks:
                                chunked_docs.extend(chunks)
                                
                    except Exception as e:
                        logger.error(f"Lỗi khi đọc tài liệu {doc.get('id')}: {str(e)}")
                        continue
                        
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý tài liệu {doc.get('id')}: {str(e)}")
                    continue
            
            if chunked_docs:
                self.chroma_manager.add_documents(chunked_docs)
                logger.info(f"Đã đánh chỉ mục lại {len(chunked_docs)} chunks từ {len(all_documents)} tài liệu")
                return True
            else:
                logger.warning("Không có chunk nào được tạo, đánh chỉ mục thất bại")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi đánh chỉ mục lại: {str(e)}")
            return False