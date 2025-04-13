import logging
from typing import Dict, Any, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticRouterService:
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        
        self.classification_prompt_vi = """
        Phân loại câu hỏi sau vào một trong hai loại:
        - RAG: Câu hỏi yêu cầu tìm kiếm thông tin cụ thể, tra cứu dữ liệu, hoặc kiến thức chuyên môn
        - Chitchat: Lời chào, hỏi thăm, trò chuyện thông thường, tương tác đơn giản
        
        Ví dụ phân loại:
        "hello" -> Chitchat
        "chào bạn" -> Chitchat
        "bạn khỏe không" -> Chitchat
        "bạn là ai" -> Chitchat
        
        "quy trình nhập học là gì" -> RAG
        "điểm chuẩn đại học năm 2023" -> RAG
        "thông tin về kỳ thi tốt nghiệp" -> RAG
        "thủ tục đăng ký xét tuyển đại học" -> RAG
        "đề án tuyển sinh đại học 2023" -> RAG
        "điều kiện xét tuyển" -> RAG
        "học phí ngành y khoa" -> RAG
        "thông tin về đề án tuyển sinh" -> RAG
        
        Câu hỏi cần phân loại: "{query}"
        
        Phân loại (chỉ trả lời RAG hoặc Chitchat, không thêm giải thích):
        """
        
        self.classification_prompt_en = """
        Classify the following query into one of two categories:
        - RAG: Questions requiring specific information lookup, data search, or specialized knowledge
        - Chitchat: Greetings, small talk, general conversation, simple interactions
        
        Classification examples:
        "hello" -> Chitchat
        "hi there" -> Chitchat
        "how are you" -> Chitchat
        "who are you" -> Chitchat
        
        "what is the admission process" -> RAG
        "university entrance scores 2023" -> RAG
        "information about graduation exam" -> RAG
        "university application procedure" -> RAG
        "college admission plan 2023" -> RAG
        "admission requirements" -> RAG
        "tuition for medical school" -> RAG
        "information about admission plan" -> RAG
        
        Query to classify: "{query}"
        
        Classification (only answer RAG or Chitchat, no explanation):
        """
        

        self.functions = [
            {
                "name": "classify_query",
                "description": "Classifies a user query as either RAG (requires information retrieval) or Chitchat (general conversation)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["RAG", "Chitchat"],
                            "description": "The category of the query: RAG for information retrieval or Chitchat for general conversation"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level in the classification (0.0 to 1.0)"
                        },
                        "reasoning": {
                            "type": "string", 
                            "description": "Brief explanation of why this classification was chosen"
                        }
                    },
                    "required": ["category"]
                }
            }
        ]
        
        self.education_keywords = [
            "tuyển sinh", "đề án", "đại học", "cao đẳng", "học phí", "điểm chuẩn", 
            "ngành học", "khoa", "trường", "điều kiện", "xét tuyển", "tốt nghiệp",
            "đăng ký", "nhập học", "sinh viên", "học sinh", "giáo dục"
        ]
    
    def route_query(self, query: str, context: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        if context is None:
            context = {}
            
        language = context.get("language", "vi")
        

        query_lower = query.lower()
        for keyword in self.education_keywords:
            if keyword in query_lower:
                logger.info(f"Từ khóa giáo dục '{keyword}' xuất hiện trong câu hỏi -> phân loại RAG")
                return "admission_query", {
                    "query": query,
                    "context": context
                }
        
        try:
            try:
                if hasattr(self.llm_client, 'function_call'):

                    result = self.llm_client.function_call(
                        query, 
                        system_prompt="Phân loại truy vấn này là RAG (tìm kiếm thông tin) hay Chitchat (trò chuyện thông thường)",
                        functions=self.functions,
                        function_name="classify_query"
                    )
                    
                    category = result.get("category", "Chitchat")
                    logger.info(f"Query classification (function call): '{query}' -> '{category}' with confidence {result.get('confidence', 'N/A')}")
                    
                    if category == "RAG":
                        return "admission_query", {
                            "query": query,
                            "context": context
                        }
                    else:
                        return "chitchat_query", {
                            "query": query,
                            "context": context
                        }
            except Exception as func_error:
                logger.warning(f"Lỗi khi sử dụng function call: {str(func_error)}, chuyển sang prompt thông thường")
            
            prompt_template = self.classification_prompt_vi if language == "vi" else self.classification_prompt_en
            prompt = prompt_template.format(query=query)
            
            try:

                classification = self.llm_client.generate(
                    prompt=prompt,
                    temperature=0.0 
                ).strip().lower()
                
                logger.info(f"Query classification (standard): '{query}' -> '{classification}'")
                
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
            except Exception as gen_error:
                logger.warning(f"Lỗi khi sử dụng generate: {str(gen_error)}, kiểm tra từ khóa final fallback")
                
                educational_terms = ["tuyển", "sinh", "đại", "học", "điểm", "đề án", "khoa"]
                for term in educational_terms:
                    if term in query_lower:
                        logger.info(f"Từ khóa đơn '{term}' xuất hiện trong câu hỏi -> phân loại RAG (fallback)")
                        return "admission_query", {
                            "query": query,
                            "context": context
                        }
                

                return "chitchat_query", {
                    "query": query,
                    "context": context
                }
                
        except Exception as e:
            logger.error(f"Error in query classification: {str(e)}")
            
            if any(term in query_lower for term in ["tuyển", "sinh", "học", "trường", "đề án"]):
                return "admission_query", {
                    "query": query,
                    "context": context
                }
            
            return "chitchat_query", {
                "query": query,
                "context": context
            }