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
        
    def get_all_documents(self, page=1, limit=10, category=None):
        try:

            if not self.db_manager:
                logger.warning("Không có db_manager, không thể lấy danh sách tài liệu")
                return []
                

            logger.info(f"Đang lấy tài liệu trang {page}, limit {limit}, category: {category}")
            
            try:
                documents = self.db_manager.get_all_documents(
                    page=page,
                    limit=limit,
                    category=category
                )
                logger.info(f"Đã lấy {len(documents)} tài liệu từ MySQL")
                
                if not documents:
                    return []
                    
                return documents
            except Exception as e:
                logger.error(f"Lỗi khi lấy tài liệu từ MySQL: {str(e)}")

                return []
        except Exception as e:
            logger.error(f"Lỗi không xác định khi lấy tài liệu: {str(e)}")
            return []
    
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
                del chroma_metadata["tags"]
                    
            for doc in documents:
                if not hasattr(doc, 'metadata') or not isinstance(doc.metadata, dict):
                    doc.metadata = {}
                doc.metadata.update(chroma_metadata)
            
            for i, doc in enumerate(documents[:2]): 
                content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                logger.debug(f"Tài liệu {i+1} có nội dung: {content_preview}")
                
            chunked_docs = []
            for i, doc in enumerate(documents):
                if not doc.page_content or len(doc.page_content.strip()) == 0:
                    logger.warning("Bỏ qua trang/phần không có nội dung")
                    continue
                
                if hasattr(doc, 'metadata'):
                    doc.metadata['page_number'] = i + 1
                    doc.metadata['total_pages'] = len(documents)

                    doc.metadata['id'] = f"{doc_id}_page_{i+1}"
                    
                chunks = self.chroma_manager.chunk_document(doc.page_content, doc.metadata)
                if chunks and len(chunks) > 0:
                    chunked_docs.extend(chunks)
                    logger.info(f"Chia thành {len(chunks)} đoạn")
                else:
                    logger.warning(f"Không thể chia được đoạn nào từ trang/phần có {len(doc.page_content)} ký tự")
            
            if chunked_docs and len(chunked_docs) > 0:

                chunk_ids = set()
                for chunk in chunked_docs:
                    if 'id' not in chunk.metadata:
                        chunk.metadata['id'] = f"{doc_id}_chunk_{uuid.uuid4().hex}"

                    while chunk.metadata['id'] in chunk_ids:
                        chunk.metadata['id'] = f"{doc_id}_chunk_{uuid.uuid4().hex}"
                    chunk_ids.add(chunk.metadata['id'])

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