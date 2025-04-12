from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader
)
import os
import tempfile
from werkzeug.utils import secure_filename

class DocumentService:
    def __init__(self, chroma_manager):
        self.chroma_manager = chroma_manager
        self.loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
            '.csv': CSVLoader
        }
        
    def process_file(self, file, metadata=None):
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in self.loaders:
            raise ValueError(f"Unsupported file type: {file_ext}")
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
            
        try:
            loader_class = self.loaders[file_ext]
            loader = loader_class(tmp_path)
            documents = loader.load()
            
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
                    
            chunked_docs = []
            for doc in documents:
                chunks = self.chroma_manager.chunk_document(doc.page_content, doc.metadata)
                chunked_docs.extend(chunks)
                
            self.chroma_manager.add_documents(chunked_docs)
            
            return {
                "status": "success",
                "num_chunks": len(chunked_docs),
                "filename": filename
            }
            
        finally:
            os.unlink(tmp_path)