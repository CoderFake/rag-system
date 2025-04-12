from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # ChromaDB
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    # Document Processing
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    
    # Embedding Model
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")