from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import logging
import os
import time
import uuid

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
                chunk_size=1000,              
                chunk_overlap=200,         
                length_function=len,                
                separators=["\n\n", "\n", ". ", " ", ""], 
                keep_separator=True,             
                is_separator_regex=False       
            )
            
            logger.info(f"ChromaManager khởi tạo thành công với mô hình: {embedding_model}")
            
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo ChromaManager: {str(e)}")
            raise
        
    def add_documents(self, documents, metadatas=None):
        try:
            if not documents or len(documents) == 0:
                logger.warning("Không có tài liệu nào để thêm vào ChromaDB")
                return []

            total_chars = sum(len(doc.page_content) for doc in documents)
            logger.info(f"Chuẩn bị thêm {len(documents)} tài liệu với tổng {total_chars} ký tự")
            
            valid_docs = []
            for doc in documents:
                if not doc.page_content or len(doc.page_content.strip()) == 0:
                    logger.warning("Bỏ qua tài liệu trống")
                    continue
                valid_docs.append(doc)
                
            if len(valid_docs) == 0:
                logger.warning("Không có tài liệu hợp lệ nào để thêm vào ChromaDB")
                return []
                
            texts = [doc.page_content for doc in valid_docs]
            metadata_list = [doc.metadata.copy() if hasattr(doc, 'metadata') and doc.metadata else {} for doc in valid_docs]
            
            ids = []
            for i, doc in enumerate(valid_docs):

                if hasattr(doc, 'metadata') and doc.metadata and 'id' in doc.metadata:
                    doc_id = doc.metadata['id']
                    metadata_list[i]['document_id'] = doc_id

                    unique_id = f"{doc_id}_{uuid.uuid4().hex[:8]}"
                else:
                    unique_id = str(uuid.uuid4())
                ids.append(unique_id)

                metadata_list[i]['id'] = unique_id
            
            if len(ids) != len(set(ids)):
                duplicates = set([x for x in ids if ids.count(x) > 1])
                logger.warning(f"Phát hiện ID trùng lặp sau khi tạo: {duplicates}. Đang tạo ID mới.")
                
                for i, doc_id in enumerate(ids):
                    if doc_id in duplicates:
                        new_id = str(uuid.uuid4())
                        ids[i] = new_id
                        metadata_list[i]['id'] = new_id
            
            logger.debug(f"Một số ID mẫu: {ids[:3] if len(ids) > 3 else ids}")
            
            avg_length = sum(len(t) for t in texts) / len(texts) if texts else 0
            logger.info(f"Độ dài trung bình của text: {avg_length:.1f} ký tự")
            
            result = self.vector_store.add_texts(texts=texts, metadatas=metadata_list, ids=ids)
            logger.info(f"Đã thêm {len(texts)} tài liệu vào ChromaDB")
            return result
        except Exception as e:
            logger.error(f"Lỗi khi thêm tài liệu: {str(e)}")
            raise
        
    def chunk_document(self, text, metadata=None):
        try:
            if not text or len(text.strip()) == 0:
                logger.warning("Cố gắng chia tài liệu trống")
                return []
                
            logger.debug(f"Chia tài liệu có độ dài {len(text)} ký tự")
    
            text = text.replace('\x00', ' ')  
            text = text.replace('. ', '.\n') 
            chunks = self.text_splitter.create_documents([text], [metadata.copy() if metadata else None])
            
            if not chunks or len(chunks) == 0:
                logger.warning(f"Không thể chia tài liệu thành chunks với RecursiveCharacterTextSplitter")

                from langchain.text_splitter import CharacterTextSplitter
                simple_splitter = CharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=100,
                    separator="\n"
                )
                chunks = simple_splitter.create_documents([text], [metadata.copy() if metadata else None])
    
            orig_doc_id = metadata.get('id', str(uuid.uuid4())) if metadata else str(uuid.uuid4())
            
            for i, chunk in enumerate(chunks):
                if not chunk.metadata:
                    chunk.metadata = {}
                
                chunk.metadata['document_id'] = orig_doc_id
                chunk.metadata['id'] = f"{orig_doc_id}_chunk_{i}_{uuid.uuid4().hex[:8]}"
                chunk.metadata['chunk_index'] = i
                chunk.metadata['total_chunks'] = len(chunks)
                
                if metadata:
                    for key, value in metadata.items():
                        if key != 'id' and key not in chunk.metadata:
                            chunk.metadata[key] = value
            
            logger.info(f"Đã chia tài liệu thành {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Lỗi khi chia tài liệu thành chunks: {str(e)}")

            from langchain.schema import Document as LangchainDocument
            fallback_doc = LangchainDocument(page_content=text, metadata=metadata.copy() if metadata else {})
            fallback_doc.metadata['id'] = metadata.get('id', str(uuid.uuid4())) if metadata else str(uuid.uuid4())
            return [fallback_doc]
        
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
            
    def delete_documents(self, ids):
        try:
            self.vector_store.delete(ids)
            logger.info(f"Đã xóa {len(ids)} tài liệu")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa tài liệu: {str(e)}")
            return False