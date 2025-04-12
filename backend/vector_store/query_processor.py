import logging
from typing import List, Dict, Any, Optional
from .embedding_manager import EmbeddingManager

logger = logging.getLogger(__name__)

class QueryProcessor:

    def __init__(self, chroma_manager, embedding_manager=None):

        self.chroma_manager = chroma_manager
        self.embedding_manager = embedding_manager or EmbeddingManager()
        logger.info("Khởi tạo QueryProcessor thành công")
    
    def process_query(self, query: str, top_k: int = 5, use_hybrid: bool = False):
        try:
            if not query:
                logger.warning("Truy vấn trống")
                return []
                
            logger.info(f"Xử lý truy vấn: '{query[:50]}...'")
            
            if use_hybrid:
                return self.chroma_manager.hybrid_search(query, k=top_k)
            else:
                return self.chroma_manager.similarity_search(query, k=top_k)
                
        except Exception as e:
            logger.error(f"Lỗi khi xử lý truy vấn: {str(e)}")
            raise
    
    def rank_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        try:
            if not results:
                return []

            query_embedding = self.embedding_manager.get_query_embedding(query)
            
            ranked_results = []
            for result in results:

                doc_content = result.page_content if hasattr(result, 'page_content') else ""

                doc_embedding = self.embedding_manager.get_embedding(doc_content)
                
                similarity = self.embedding_manager.calculate_similarity(
                    query_embedding, doc_embedding
                )
                
                result_dict = {
                    "document": result,
                    "similarity": similarity
                }
                ranked_results.append(result_dict)
            
            ranked_results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return ranked_results
            
        except Exception as e:
            logger.error(f"Lỗi khi xếp hạng kết quả: {str(e)}")
            return results