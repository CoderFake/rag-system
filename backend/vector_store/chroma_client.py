from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import logging
import os
import time
import json

logger = logging.getLogger(__name__)

class ChromaManager:
    def __init__(self, persist_directory, embedding_model="sentence-transformers/all-MiniLM-L6-v2"):
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
            
            if os.path.exists(persist_directory):
                try:
                    self.client = chromadb.PersistentClient(path=persist_directory)
                    
                    self.vector_store = Chroma(
                        persist_directory=persist_directory,
                        embedding_function=self.embeddings,
                        client=self.client
                    )
                except Exception as e:
                    logger.warning(f"Lỗi khi kết nối với ChromaDB hiện tại: {str(e)}")
                    import shutil
                    backup_dir = f"{persist_directory}_backup_{int(time.time())}"
                    logger.info(f"Tạo bản sao lưu ChromaDB tại: {backup_dir}")
                    shutil.move(persist_directory, backup_dir)
                    os.makedirs(persist_directory, exist_ok=True)
                    
                    self.client = chromadb.PersistentClient(path=persist_directory)
                    self.vector_store = Chroma(
                        persist_directory=persist_directory,
                        embedding_function=self.embeddings,
                        client=self.client
                    )
            else:
                os.makedirs(persist_directory, exist_ok=True)
                self.client = chromadb.PersistentClient(path=persist_directory)
                self.vector_store = Chroma(
                    persist_directory=persist_directory,
                    embedding_function=self.embeddings,
                    client=self.client
                )
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=512,
                chunk_overlap=50,
                length_function=len,
                is_separator_regex=False
            )
            
            logger.info(f"ChromaManager khởi tạo thành công với mô hình: {embedding_model}")
            
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo ChromaManager: {str(e)}")
            raise
        
    def add_documents(self, documents, metadatas=None):
        try:
            if not documents:
                logger.warning("Danh sách tài liệu trống, không có gì để thêm vào ChromaDB")
                return []
                
            valid_docs = []
            valid_metadatas = []
            
            for i, doc in enumerate(documents):
                if hasattr(doc, 'page_content') and doc.page_content and doc.page_content.strip():
                    valid_docs.append(doc)
                    if metadatas and i < len(metadatas):
                        valid_metadatas.append(metadatas[i])
                    elif hasattr(doc, 'metadata'):
                        valid_metadatas.append(doc.metadata)
                    else:
                        valid_metadatas.append({})
            
            if not valid_docs:
                logger.warning("Sau khi lọc, không còn tài liệu hợp lệ để thêm vào ChromaDB")
                return []
            
            texts = [doc.page_content for doc in valid_docs]
            metadata_list = valid_metadatas if valid_metadatas else [doc.metadata for doc in valid_docs]
            
            for i, metadata in enumerate(metadata_list):
                if "id" not in metadata:
                    metadata["id"] = f"doc_{int(time.time())}_{i}"
                
                for key in list(metadata.keys()): 
                    if isinstance(metadata[key], (list, dict, tuple, set)):
                        try:
                            metadata[key + "_str"] = json.dumps(metadata[key])
                        except Exception:
                            pass
                        del metadata[key]  
            
            result = self.vector_store.add_texts(texts=texts, metadatas=metadata_list)
            logger.info(f"Đã thêm {len(texts)} tài liệu vào ChromaDB")
            return result
            
        except Exception as e:
            logger.error(f"Lỗi khi thêm tài liệu: {str(e)}")
            raise
        
    def chunk_document(self, text, metadata=None):
        try:
            if not text or not text.strip():
                logger.warning("Văn bản trống, không thể tách thành chunks")
                return []
                
            if metadata is None:
                metadata = {}
                
            metadata_copy = metadata.copy() if metadata else {}
            
            if "id" not in metadata_copy:
                metadata_copy["id"] = f"doc_{int(time.time())}"
            
            safe_metadata = {}
            for key, value in metadata_copy.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    safe_metadata[key] = value
                elif isinstance(value, (list, dict, tuple, set)):
                    try:
                        safe_metadata[key + "_str"] = json.dumps(value)
                    except Exception:
                        pass
            
            chunks = self.text_splitter.create_documents([text], [safe_metadata])
            
            valid_chunks = []
            for chunk in chunks:
                if chunk.page_content and chunk.page_content.strip():
                    valid_chunks.append(chunk)
            
            if not valid_chunks:
                logger.warning("Không có chunk hợp lệ sau khi tách văn bản")
                return []
            
            document_id = safe_metadata.get("id", f"doc_{int(time.time())}")
            for i, chunk in enumerate(valid_chunks):
                if not hasattr(chunk, 'metadata') or not chunk.metadata:
                    chunk.metadata = {}
                
                if "id" not in chunk.metadata:
                    chunk.metadata["id"] = f"{document_id}_chunk_{i}"
                    
                if "document_id" not in chunk.metadata:
                    chunk.metadata["document_id"] = document_id
                    
                chunk.metadata["chunk_index"] = i
            
            logger.debug(f"Đã chia tài liệu thành {len(valid_chunks)} chunks hợp lệ")
            return valid_chunks
        except Exception as e:
            logger.error(f"Lỗi khi chia tài liệu thành chunks: {str(e)}")
            raise
        
    def similarity_search(self, query, k=5):
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.debug(f"Tìm kiếm tương tự cho '{query[:50]}...' - Tìm thấy {len(results)} kết quả")
            return results
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm tương tự: {str(e)}")
            raise
        
    def hybrid_search(self, query, k=5):
        return self.similarity_search(query, k)
        
    def delete_collection(self, collection_name="langchain"):
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Đã xóa collection: {collection_name}")
        except Exception as e:
            logger.error(f"Lỗi khi xóa collection: {str(e)}")
            raise
        
    def list_collections(self):
        try:
            collections = self.client.list_collections()
            logger.debug(f"Danh sách collections: {collections}")
            return collections
        except Exception as e:
            logger.error(f"Lỗi khi liệt kê collections: {str(e)}")
            raise
            
    def delete_by_document_id(self, document_id):
        try:
            collection = self.client.get_collection(name="langchain")
            
            try:
                query_results = collection.query(
                    query_texts=[""], 
                    where={"document_id": document_id},
                    include=["documents", "metadatas", "embeddings"]
                )
                
                if query_results and query_results.get("ids") and query_results["ids"][0]:
                    chunk_ids = query_results["ids"][0]
                    if chunk_ids:
                        collection.delete(ids=chunk_ids)
                        logger.info(f"Đã xóa {len(chunk_ids)} chunks thuộc tài liệu {document_id}")
                        return True
            except Exception as e:
                logger.warning(f"Lỗi khi truy vấn collections: {str(e)}")
                
            all_metadatas = collection.get()["metadatas"]
            all_ids = collection.get()["ids"]
            
            chunk_ids = []
            for i, metadata in enumerate(all_metadatas):
                if metadata.get("document_id") == document_id:
                    chunk_ids.append(all_ids[i])
            
            if chunk_ids:
                collection.delete(ids=chunk_ids)
                logger.info(f"Đã xóa {len(chunk_ids)} chunks thuộc tài liệu {document_id}")
                return True
                    
            logger.warning(f"Không tìm thấy chunks nào cho tài liệu {document_id}")
            return False
        except Exception as e:
            logger.error(f"Lỗi khi xóa tài liệu từ vector store: {str(e)}")
            return False