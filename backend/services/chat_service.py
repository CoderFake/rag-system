import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


from models.query import Query
from models.response import Response


from config.settings import Config

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, semantic_router, reflection_service, rag_service, llm_client, db_manager=None):
        self.semantic_router = semantic_router
        self.reflection_service = reflection_service
        self.rag_service = rag_service
        self.llm_client = llm_client
        self.db_manager = db_manager
        
        logger.info(f"ChatService khởi tạo với LLM provider: {Config.LLM_PROVIDER}")

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
            
            try:
                enhanced_query = self.reflection_service.enhance_query(query_text, language)
                query.enhanced_text = enhanced_query
            except Exception as e:
                logger.error(f"Error enhancing query: {str(e)}")
                enhanced_query = query_text
                query.enhanced_text = query_text
            
            route_type, route_data = self.semantic_router.route_query(
                enhanced_query,
                {"session_id": session_id, "language": language}
            )
            
            query.query_type = "rag" if route_type == "admission_query" else "chitchat"
            
            if self.db_manager:
                try:
                    self.db_manager.save_query(query)
                except Exception as e:
                    logger.error(f"Error saving query to database: {str(e)}")
            
            if route_type == "admission_query":

                rag_result = self.rag_service.process_query(enhanced_query, language)
            
                response = Response(
                    query_id=query.id,
                    text=rag_result["response"],
                    query_text=query_text,
                    source_documents=rag_result.get("source_documents", []),
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
                    prompt=enhanced_query, 
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
                try:
                    self._save_response_safely(response)
                except Exception as e:
                    logger.error(f"Error saving response to database: {str(e)}")
            
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
    
    def _save_response_safely(self, response: Response) -> bool:
        try:
            source_documents = response.source_documents
            response.source_documents = [] 
            
            response_id = self.db_manager.save_response(response)
            
            if source_documents and len(source_documents) > 0:
                self._save_sources_safely(response.id, source_documents)
                
            return True
        except Exception as e:
            logger.error(f"Error in _save_response_safely: {str(e)}")
            return False
    
    def _save_sources_safely(self, response_id: str, sources: List[Dict[str, Any]]) -> None:
        if not self.db_manager:
            return
            
        for source in sources:
            try:
                document_id = source.get("id")
                if not document_id:
                    continue
                    
                doc_exists = self.db_manager.execute_query(
                    "SELECT id FROM documents WHERE id = %s", 
                    (document_id,), 
                    fetch=True
                )

                if doc_exists:
                    relevance_score = source.get("relevance_score", 0.0)
                    self.db_manager.execute_query(
                        "INSERT INTO response_sources (response_id, document_id, relevance_score) VALUES (%s, %s, %s)",
                        (response_id, document_id, relevance_score)
                    )
                else:
                    logger.warning(f"Document ID {document_id} not found in database, skipping source")
            except Exception as e:
                logger.error(f"Error saving source {source.get('id')}: {str(e)}")
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.db_manager:
            return []
            
        try:
            return self.db_manager.get_chat_history(session_id, limit)
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    def add_feedback(self, response_id: str, user_id: Optional[int], feedback_type: str, value: str) -> bool:
        if not self.db_manager:
            return False
            
        try:
            self.db_manager.add_feedback(response_id, user_id, feedback_type, value)
            return True
        except Exception as e:
            logger.error(f"Error adding feedback: {str(e)}")
            return False