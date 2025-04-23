import logging
from typing import Dict, Any, Tuple, List


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticRouterService:
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        
        self.classification_prompt_vi = """
        Bạn là một hệ thống phân loại truy vấn. Nhiệm vụ của bạn là xác định xem một truy vấn 
        có yêu cầu truy xuất thông tin từ kho kiến thức (RAG) hay chỉ là một cuộc trò chuyện thông thường (Chitchat).
        
        Lịch sử trò chuyện:
        {chat_history}
        
        Truy vấn của người dùng: "{query}"
        
        Nếu truy vấn yêu cầu tìm kiếm thông tin, kiến thức, dữ liệu cụ thể hoặc yêu cầu trả lời dựa trên tài liệu, 
        hoặc nếu truy vấn có liên quan đến lịch sử trò chuyện và cần thông tin từ cơ sở dữ liệu,
        hãy phân loại là "RAG".
        
        Nếu truy vấn chỉ là lời chào, hỏi thăm, trò chuyện cá nhân, yêu cầu giúp đỡ chung chung, 
        hãy phân loại là "Chitchat".
        
        Chỉ trả lời "RAG" hoặc "Chitchat", không thêm bất kỳ giải thích nào.
        """
        
        self.classification_prompt_en = """
        You are a query classification system. Your task is to determine if a query
        requires retrieving information from a knowledge base (RAG) or is just general conversation (Chitchat).
        
        Conversation history:
        {chat_history}
        
        User query: "{query}"
        
        If the query asks for specific information, knowledge, data, or requires answers based on documents,
        or if the query relates to the conversation history and needs information from the knowledge base,
        classify it as "RAG".
        
        If the query is just a greeting, personal conversation, general help request, 
        classify it as "Chitchat".
        
        Only respond with "RAG" or "Chitchat", without any explanation.
        """
    
    def format_chat_history(self, chat_history: List[Dict[str, Any]], language: str = "vi") -> str:
        if not chat_history:
            return "Không có lịch sử trò chuyện." if language == "vi" else "No conversation history."
            
        formatted_history = ""
        
        for msg in chat_history:
            if msg['type'] == 'query':
                prefix = "Người dùng: " if language == "vi" else "User: "
                formatted_history += f"{prefix}{msg['content']}\n"
            else:
                prefix = "AI: " if language == "vi" else "AI: "
                formatted_history += f"{prefix}{msg['content']}\n"
                
        return formatted_history
    
    def route_query(self, query: str, context: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        if context is None:
            context = {}
            
        language = context.get("language", "vi")
        chat_history = context.get("chat_history", [])
        
        try:
            prompt_template = self.classification_prompt_vi if language == "vi" else self.classification_prompt_en
            
            formatted_history = self.format_chat_history(chat_history, language)
            
            prompt = prompt_template.format(
                query=query,
                chat_history=formatted_history
            )
            
            classification = self.llm_client.generate(
                prompt=prompt,
            ).strip().lower()
            
            logger.info(f"Query classification: '{query}' -> '{classification}'")
            
            if "rag" in classification:
                return "admission_query", {
                    "query": query,
                    "context": context
                }
            else:
                return "chitchat_query", {
                    "query": query,
                    "context": context
                }
                
        except Exception as e:
            logger.error(f"Error in query classification: {str(e)}")
            
            return "chitchat_query", {
                "query": query,
                "context": context
            }