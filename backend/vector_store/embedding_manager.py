from services.embedding_service import EmbeddingService
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager:

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.service = EmbeddingService(model_name=model_name)
    
    def get_document_embeddings(self, texts: List[str]) -> List[List[float]]:

        return self.service.get_embeddings(texts)
    
    def get_query_embedding(self, query: str) -> List[float]:

        return self.service.get_embedding(query)
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:

        return self.service.calculate_similarity(embedding1, embedding2)
        
    def get_top_similar_documents(self, query_embedding: List[float], 
                                 document_embeddings: List[List[float]], 
                                 top_k: int = 5) -> List[Dict[str, Any]]:

        if not query_embedding or not document_embeddings:
            return []
        
        similarities = [
            self.calculate_similarity(query_embedding, doc_embedding)
            for doc_embedding in document_embeddings
        ]

        import numpy as np
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = [
            {"index": int(idx), "similarity": float(similarities[idx])}
            for idx in top_indices
        ]
        
        return results