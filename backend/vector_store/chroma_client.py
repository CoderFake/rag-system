from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb

class ChromaManager:
    def __init__(self, persist_directory, embedding_model="models/embedding-001"):
        self.embeddings = VertexAIEmbeddings(model_name=embedding_model)
        
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
        
    def add_documents(self, documents, metadatas=None):
        """Add documents to ChromaDB"""
        texts = [doc.page_content for doc in documents]
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        
    def chunk_document(self, text, metadata=None):
        """Split document into chunks"""
        chunks = self.text_splitter.create_documents([text], [metadata] if metadata else None)
        return chunks
        
    def similarity_search(self, query, k=5):
        """Perform similarity search"""
        return self.vector_store.similarity_search(query, k=k)
        
    def hybrid_search(self, query, k=5):
        """Perform hybrid search (both keyword and semantic)"""
        return self.similarity_search(query, k)
        
    def delete_collection(self, collection_name="langchain"):
        """Delete a collection"""
        self.client.delete_collection(collection_name)
        
    def list_collections(self):
        """List all collections"""
        return self.client.list_collections()