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
            
            chat_history = []
            if self.db_manager and session_id:
                chat_history = self.db_manager.get_chat_history(session_id, limit=5) 
            
            route_type, route_data = self.semantic_router.route_query(
                enhanced_query,
                {
                    "session_id": session_id, 
                    "language": language,
                    "chat_history": chat_history 
                }
            )
            
            query.query_type = "rag" if route_type == "admission_query" else "chitchat"
            
            if self.db_manager:
                query_id = self.db_manager.save_query(query)
                query.id = query_id
            
            if route_type == "admission_query":
                result = self.rag_service.process_query(
                    enhanced_query, 
                    language, 
                    chat_history=chat_history
                )
                
                valid_sources = []
                if self.db_manager and result.get("source_documents"):
                    for doc in result.get("source_documents", []):
                        doc_id = None
                        if hasattr(doc, 'metadata'):
                            doc_id = doc.metadata.get('document_id') or doc.metadata.get('id')
                        elif isinstance(doc, dict):
                            doc_id = doc.get('document_id') or doc.get('id')
                        
                        if doc_id:
                            try:
                                document = self.db_manager.get_document(doc_id)
                                if document:
                                    if hasattr(doc, 'metadata'):
                                        valid_sources.append({
                                            'id': doc_id,
                                            'title': doc.metadata.get('title', 'Unknown'),
                                            'category': doc.metadata.get('category', 'general'),
                                            'relevance_score': 0.9
                                        })
                                    elif isinstance(doc, dict):
                                        valid_sources.append({
                                            'id': doc_id,
                                            'title': doc.get('title', 'Unknown'),
                                            'category': doc.get('category', 'general'),
                                            'relevance_score': doc.get('relevance_score', 0.9)
                                        })
                                else:
                                    logger.warning(f"Tài liệu với ID {doc_id} không tồn tại trong cơ sở dữ liệu")
                            except Exception as e:
                                logger.error(f"Lỗi khi kiểm tra document_id {doc_id}: {str(e)}")
                        else:
                            logger.warning(f"Không thể trích xuất document_id từ source_document")
                
                response = Response(
                    query_id=query.id,
                    text=result["response"],
                    query_text=query_text,
                    source_documents=valid_sources,  
                    response_type="rag",
                    session_id=session_id,
                    user_id=user_id,
                    language=language,
                    processing_time=time.time() - start_time,
                    created_at=datetime.now().isoformat()
                )
                
            else:
                system_prompt = f"Bạn là trợ lý AI hữu ích trả lời bằng {'tiếng Việt' if language == 'vi' else 'English'}."
                
                try:
                    messages = []
                    for msg in chat_history:
                        if msg['type'] == 'query':
                            messages.append({"role": "user", "content": msg['content']})
                        else:
                            messages.append({"role": "assistant", "content": msg['content']})
                    
                    messages.append({"role": "user", "content": query_text})
                    
                    chatbot_response = self.llm_client.generate_with_history(
                        messages=messages,
                        system_prompt=system_prompt
                    )
                except (AttributeError, TypeError) as e:
                    formatted_history = ""
                    for msg in chat_history:
                        if msg['type'] == 'query':
                            formatted_history += f"Người dùng: {msg['content']}\n"
                        else:
                            formatted_history += f"AI: {msg['content']}\n"
                    
                    if formatted_history:
                        full_prompt = f"Lịch sử trò chuyện:\n{formatted_history}\n\nNgười dùng: {query_text}\n\nAI:"
                    else:
                        full_prompt = query_text
                    
                    chatbot_response = self.llm_client.generate(
                        prompt=full_prompt,
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
                    self.db_manager.save_response(response)
                except Exception as db_error:
                    logger.error(f"Lỗi khi lưu response vào database: {str(db_error)}")
            
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