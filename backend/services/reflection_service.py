
import logging
from typing import Dict, Any


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReflectionService:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        

        self.reflection_prompt_vi = """
        Bạn đang giúp cải thiện một truy vấn của người dùng để hệ thống tìm kiếm thông tin hoạt động tốt hơn.
        
        Truy vấn gốc của người dùng là: "{query}"
        
        Hãy phân tích truy vấn và:
        1. Xác định các khái niệm chính
        2. Xác định mục đích chính của truy vấn
        3. Xác định bất kỳ điểm mơ hồ hoặc không rõ ràng nào
        
        Sau đó, hãy viết lại truy vấn với các từ khóa phong phú hơn, cụ thể hơn và hoàn chỉnh hơn.
        Chỉ trả về truy vấn đã cải thiện, không thêm bất kỳ chú thích nào.
        """
        

        self.reflection_prompt_en = """
        You are helping to improve a user's query to make the information retrieval system work better.
        
        The original user query is: "{query}"
        
        Please analyze the query and:
        1. Identify the main concepts
        2. Identify the main purpose of the query
        3. Identify any ambiguities or unclear points
        
        Then, rewrite the query with richer, more specific and complete keywords.
        Only return the improved query, without any commentary.
        """
    
    def enhance_query(self, query: str, language: str = "vi") -> str:
        if len(query.split()) <= 3:
            return query
            
        try:

            prompt_template = self.reflection_prompt_vi if language == "vi" else self.reflection_prompt_en
            

            prompt = prompt_template.format(query=query)
            

            enhanced_query = self.llm_client.generate(
                prompt=prompt,
                temperature=0.3
            )
            
            if len(enhanced_query) > len(query) * 3:

                logger.warning("Enhanced query too long, using original query")
                return query
                
            logger.info(f"Enhanced query: {enhanced_query}")
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Error in query enhancement: {str(e)}")

            return query