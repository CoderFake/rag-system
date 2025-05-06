# File: backend/services/reflection_service.py

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
        
        QUAN TRỌNG: KHÔNG THAY ĐỔI Ý NGHĨA BAN ĐẦU của câu hỏi. 
        KHÔNG THÊM CÁC THÔNG TIN/CHỦ ĐỀ MỚI mà người dùng không hỏi.
        CHỈ mở rộng câu hỏi bằng cách thêm từ khóa liên quan trực tiếp.
        
        Nếu câu hỏi đã rõ ràng và cụ thể, HÃY GIỮ NGUYÊN.
        
        Chỉ trả về truy vấn đã cải thiện, không thêm bất kỳ chú thích nào.
        """
        
        self.reflection_prompt_en = """
        You are helping to improve a user's query to make the information retrieval system work better.
        
        The original user query is: "{query}"
        
        IMPORTANT: DO NOT CHANGE THE ORIGINAL MEANING of the question.
        DO NOT ADD NEW INFORMATION/TOPICS that the user didn't ask about.
        ONLY expand the query by adding directly relevant keywords.
        
        If the question is already clear and specific, LEAVE IT AS IS.
        
        Only return the improved query, without any commentary.
        """
    
    def enhance_query(self, query: str, language: str = "vi") -> str:
        words = query.split()
        if len(words) <= 10 and any(w in query.lower() for w in ['là ai', 'là gì', 'who is', 'what is']):
            logger.info(f"Truy vấn đã đủ rõ ràng, giữ nguyên: {query}")
            return query
        
        if len(words) <= 3:
            return query
            
        try:
            prompt_template = self.reflection_prompt_vi if language == "vi" else self.reflection_prompt_en
            
            prompt = prompt_template.format(query=query)
            
            enhanced_query = self.llm_client.generate(
                prompt=prompt,
                temperature=0.1  
            )
            
            if len(enhanced_query) > len(query) * 2:
                logger.warning(f"Enhanced query quá dài, sử dụng truy vấn gốc: {query}")
                return query
            
            logger.info(f"Truy vấn gốc: '{query}' -> Truy vấn đã cải thiện: '{enhanced_query}'")
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Lỗi khi cải thiện truy vấn: {str(e)}")
            return query