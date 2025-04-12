from langchain_google_vertexai import VertexAIEmbeddings
from typing import List, Any, Dict, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "models/embedding-001"):
        self.embedding_model = VertexAIEmbeddings(model_name=model_name)
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        try:
            embeddings = self.embedding_model.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        if not text:
            return []
            
        try:
            embedding = self.embedding_model.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        if not embedding1 or not embedding2:
            return 0.0
            

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)