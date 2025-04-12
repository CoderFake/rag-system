import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from models.query import Query
from models.response import Response

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, semantic_router, reflection_service, rag_service, llm_client, db_manager=None):
        self.semantic_router = semantic_router
        self.reflection_service = reflection_service
        self.rag_service = rag_service
        self.llm_client = llm_client
        self.db_manager = db_manager
        
    def process_query(self, query_text: str, session_id: str = None, user_id: Optional[int] = None, language: str = "vi") -> Dict[str, Any]:
        
        start_time = time.time()
        
        try:

            query = Query(
                text=query_text,
                user_id=user_id,
                session_id=session_id,
                language=language,
                created_at=datetime.now().isoformat()
            )
            
            enhanced_query = self.reflection_service.enhance_query(query_text, language)
            query.enhanced_text = enhanced_query
            

            route_type, route_data = self.semantic_router.route_query(
                enhanced_query,
                {"session_id": session_id, "language": language}
            )
            
            query.query_type = "rag" if route_type == "admission_query" else "chitchat"
            
            if self.db_manager:
                self.db_manager.save_query(query)
            
            if route_type == "admission_query":

                result = self.rag_service.process_query(enhanced_query, language)
                
                response = Response(
                    query_id=query.id,
                    text=result["response"],
                    query_text=query_text,
                    source_documents=[doc.metadata for doc in result.get("source_documents", [])],
                    response_type="rag",
                    session_id=session_id,
                    user_id=user_id,
                    language=language,
                    processing_time=time.time() - start_time,
                    created_at=datetime.now().isoformat()
                )
            else:

                system_prompt = f"Bạn là trợ lý AI hữu ích trả lời bằng {'tiếng Việt' if language == 'vi' else 'English'}."
                chatbot_response = self.llm_client.generate(
                    prompt=query_text,
                    system_prompt=system_prompt
                )
                
                response = Response(
                    query_id=query.id,
                    text=chatbot_response,
                    query_text=query_text,
                    source_documents=[],
                    response_type="chitchat",
                    session_id=session_id,
                    user_id=user_id,
                    language=language,
                    processing_time=time.time() - start_time,
                    created_at=datetime.now().isoformat()
                )
            

            if self.db_manager:
                self.db_manager.save_response(response)
            
            return {
                "response": response.text,
                "source_documents": response.source_documents,
                "route_type": response.response_type,
                "query_id": query.id,
                "response_id": response.id
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            processing_time = time.time() - start_time
            
            error_message = "Đã xảy ra lỗi khi xử lý câu hỏi" if language == "vi" else "An error occurred while processing your question"
            
            return {
                "response": f"{error_message}: {str(e)}",
                "source_documents": [],
                "route_type": "error",
                "processing_time": processing_time
            }
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.db_manager:
            return []
            
        return self.db_manager.get_chat_history(session_id, limit)
    
    def add_feedback(self, response_id: str, user_id: Optional[int], feedback_type: str, value: str) -> bool:
        if not self.db_manager:
            return False
            
        try:
            self.db_manager.add_feedback(response_id, user_id, feedback_type, value)
            return True
        except Exception as e:
            logger.error(f"Error adding feedback: {str(e)}")
            return False