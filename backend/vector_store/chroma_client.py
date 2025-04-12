from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import logging
import os
import time

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
            texts = [doc.page_content for doc in documents]
            metadata_list = [doc.metadata for doc in documents] if not metadatas else metadatas
            
            result = self.vector_store.add_texts(texts=texts, metadatas=metadata_list)
            logger.info(f"Đã thêm {len(texts)} tài liệu vào ChromaDB")
            return result
        except Exception as e:
            logger.error(f"Lỗi khi thêm tài liệu: {str(e)}")
            raise
        
    def chunk_document(self, text, metadata=None):
        try:
            chunks = self.text_splitter.create_documents([text], [metadata] if metadata else None)
            logger.debug(f"Đã chia tài liệu thành {len(chunks)} chunks")
            return chunks
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