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
                logger.info(f"Đã tải thành công file, số lượng trang/phần: {len(documents)}")
            except Exception as load_error:
                logger.error(f"Lỗi khi tải file: {str(load_error)}")

                if file_ext == '.pdf':
                    logger.info("Thử lại với phương pháp trích xuất PDF khác")
                    from langchain_community.document_loaders import UnstructuredPDFLoader
                    try:
                        loader = UnstructuredPDFLoader(tmp_path)
                        documents = loader.load()
                        logger.info(f"Đã tải thành công file với UnstructuredPDFLoader: {len(documents)} phần")
                    except Exception as e:
                        logger.error(f"Vẫn không thể tải PDF: {str(e)}")
                        raise ValueError(f"Không thể đọc file PDF: {str(e)}")
                else:
                    raise
            
            if not documents or len(documents) == 0:
                logger.warning(f"Không có trang/phần nào được tải từ file {filename}, thử phương pháp khác")

                try:
                    with open(tmp_path, 'rb') as file_content:
                        content = file_content.read()
                        
                    if file_ext == '.pdf':
                        import pdfplumber
                        text_content = ""
                        with pdfplumber.open(tmp_path) as pdf:
                            for page in pdf.pages:
                                text = page.extract_text() or ""
                                text_content += text + "\n\n"
                        
                        if text_content.strip():
                            from langchain.schema import Document as LangchainDocument
                            documents = [LangchainDocument(page_content=text_content, metadata={})]
                            logger.info(f"Đã trích xuất text từ PDF với pdfplumber: {len(text_content)} ký tự")
                        else:
                            logger.warning("Không thể trích xuất text từ PDF")
                except Exception as e:
                    logger.error(f"Lỗi khi đọc file như text: {str(e)}")
                    raise ValueError(f"Không thể đọc nội dung file: {str(e)}")
            
            if not documents or len(documents) == 0:
                logger.error(f"Không thể trích xuất bất kỳ nội dung nào từ file {filename}")
                raise ValueError("Không thể trích xuất nội dung từ file này")
            

            tags_list = metadata.get("tags", [])
            tags_string = ", ".join(tags_list) if tags_list else ""
            doc_id = metadata.get("id", str(uuid.uuid4()))
            metadata["id"] = doc_id
            
            chroma_metadata = metadata.copy()
            if "tags" in chroma_metadata:
                chroma_metadata["tags_str"] = tags_string

                if isinstance(tags_list, list):
                    chroma_metadata["tags_json"] = json.dumps(tags_list)
                
                del chroma_metadata["tags"]
                    
            if metadata:
                for doc in enumerate(documents):
                    if not hasattr(doc, 'metadata') or not isinstance(doc.metadata, dict):
                        doc.metadata = {}
                    doc.metadata.update(chroma_metadata)
            

            for i, doc in enumerate(documents[:2]): 
                content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                logger.debug(f"Tài liệu {i+1} có nội dung: {content_preview}")
                
            chunked_docs = []
            for doc in documents:

                if not doc.page_content or len(doc.page_content.strip()) == 0:
                    logger.warning("Bỏ qua trang/phần không có nội dung")
                    continue
                

                doc_metadata = {}
                if hasattr(doc, 'metadata') and doc.metadata:
                    doc_metadata = doc.metadata
                elif chroma_metadata:
                    doc_metadata = chroma_metadata


                if "id" not in doc_metadata:
                    doc_metadata["id"] = doc_id


                chunks = self.chroma_manager.chunk_document(doc.page_content, doc_metadata)
                if chunks and len(chunks) > 0:

                    for chunk in chunks:
                        if not hasattr(chunk, 'metadata') or not chunk.metadata:
                            chunk.metadata = doc_metadata
                        elif "id" not in chunk.metadata:
                            chunk.metadata["id"] = doc_id
                    
                    chunked_docs.extend(chunks)
                    logger.info(f"Chia thành {len(chunks)} đoạn")
                else:
                    logger.warning(f"Không thể chia được đoạn nào từ trang/phần có {len(doc.page_content)} ký tự")
            

            if chunked_docs and len(chunked_docs) > 0:

                for chunk in chunked_docs:
                    if not hasattr(chunk, 'metadata') or not chunk.metadata:
                        chunk.metadata = {"id": doc_id}
                    elif "id" not in chunk.metadata:
                        chunk.metadata["id"] = doc_id
                

                self.chroma_manager.add_documents(chunked_docs)
            else:
                logger.error("Không có đoạn văn nào để thêm vào ChromaDB")
                raise ValueError("Không thể chia tài liệu thành các đoạn hợp lệ")
            

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
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
    def get_all_documents(self, page=1, limit=10, category=None):
        if not self.db_manager or not hasattr(self.db_manager, 'get_all_documents'):
            logger.warning("Không có db_manager hoặc phương thức get_all_documents")
            return []
            
        try:
            documents = self.db_manager.get_all_documents(page, limit, category)
            
            for doc in documents:
                doc_id = doc.get("id")
                if doc_id:
                    try:
                        doc["chunk_count"] = self._get_document_chunk_count(doc_id)
                    except Exception as e:
                        logger.warning(f"Không thể lấy số lượng chunk cho tài liệu {doc_id}: {str(e)}")
                        doc["chunk_count"] = 0
            
            return documents
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách tài liệu: {str(e)}")
            return []
            
    def _get_document_chunk_count(self, document_id: str) -> int:
        try:
            collection = self.chroma_manager.client.get_collection("langchain")
            if not collection:
                return 0
                
            results = collection.get(
                where={"id": {"$eq": document_id}}
            )
            
            if results and "ids" in results:
                return len(results["ids"])
            return 0
        except Exception as e:
            logger.error(f"Lỗi khi đếm chunks: {str(e)}")
            return 0
            
    def delete_document(self, document_id):
        success_db = False
        success_chroma = False

        if self.db_manager and hasattr(self.db_manager, 'delete_document'):
            try:
                success_db = self.db_manager.delete_document(document_id)
                logger.info(f"Đã xóa tài liệu {document_id} từ database: {success_db}")
            except Exception as e:
                logger.error(f"Lỗi khi xoá tài liệu từ database: {str(e)}")
                success_db = False
        
        try:
            collection = self.chroma_manager.client.get_collection("langchain")
            if collection:
                results = collection.get(
                    where={"id": {"$eq": document_id}}
                )
                if results and "ids" in results and len(results["ids"]) > 0:
                    collection.delete(ids=results["ids"])
                    logger.info(f"Đã xóa {len(results['ids'])} chunks từ ChromaDB")
                    success_chroma = True
                else:
                    logger.warning(f"Không tìm thấy chunks nào cho tài liệu {document_id} trong ChromaDB")
                    success_chroma = True 
        except Exception as e:
            logger.error(f"Lỗi khi xoá tài liệu từ ChromaDB: {str(e)}")
            success_chroma = False
        

        return success_db or success_chroma
        
    def reindex_all(self):
        try:

            if not self.db_manager or not hasattr(self.db_manager, 'get_all_documents'):
                logger.error("Không thể reindex: không có db_manager hoặc phương thức get_all_documents")
                return False
                
            all_docs = self.db_manager.get_all_documents(page=1, limit=1000)
            
            if not all_docs:
                logger.warning("Không có tài liệu nào để reindex")
                return True
                
            logger.info(f"Bắt đầu reindex {len(all_docs)} tài liệu")
            
            try:
                self.chroma_manager.delete_collection()
                logger.info("Đã xóa collection hiện tại để reindex")
            except Exception as e:
                logger.warning(f"Không thể xóa collection: {str(e)}")
            
            success_count = 0
            for doc in all_docs:
                try:
                    doc_id = doc.get("id")
                    file_path = doc.get("file_path")
                    
                    if not doc_id or not file_path or not os.path.exists(file_path):
                        logger.warning(f"Bỏ qua tài liệu {doc_id}: file_path không hợp lệ hoặc không tồn tại")
                        continue
                        
                    metadata = {
                        "id": doc_id,
                        "title": doc.get("title", ""),
                        "category": doc.get("category", "general"),
                        "tags": doc.get("tags", []),
                        "user_id": doc.get("user_id")
                    }
                    
                    file_ext = os.path.splitext(file_path)[1].lower()
                    if file_ext in self.loaders:
                        loader_class = self.loaders[file_ext]
                        loader = loader_class(file_path)
                        documents = loader.load()
                        

                        chunked_docs = []
                        for document in documents:
                            chunks = self.chroma_manager.chunk_document(document.page_content, metadata)
                            if chunks and len(chunks) > 0:
                                chunked_docs.extend(chunks)
                        
                        if chunked_docs:
                            self.chroma_manager.add_documents(chunked_docs)
                            success_count += 1
                    else:
                        logger.warning(f"Bỏ qua tài liệu {doc_id}: định dạng {file_ext} không được hỗ trợ")
                        
                except Exception as e:
                    logger.error(f"Lỗi khi reindex tài liệu {doc.get('id')}: {str(e)}")
            
            logger.info(f"Hoàn tất reindex: {success_count}/{len(all_docs)} tài liệu thành công")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi reindex tất cả tài liệu: {str(e)}")
            return False