import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import json
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=2048
        )
        
        try:
            self.genai_model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                    "top_p": 0.95,
                    "top_k": 40
                }
            )
            logger.info("Khởi tạo Gemini model với function call thành công")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo model genai: {str(e)}")
            self.genai_model = None
        
    def generate(self, prompt, system_prompt=None, temperature=None):
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
            
        messages.append(HumanMessage(content=prompt))
        
        try:
            if temperature is not None:
                response = self.llm.generate([messages], temperature=temperature)
            else:
                response = self.llm.generate([messages])
                
            return response.generations[0][0].text
        except TypeError as e:
            if "unexpected keyword argument 'temperature'" in str(e):
                response = self.llm.generate([messages])
                return response.generations[0][0].text
            else:
                raise e
        except Exception as e:
            logger.error(f"Error in Gemini generate: {str(e)}")

            if self.genai_model:
                try:
                    complete_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                    response = self.genai_model.generate_content(complete_prompt)
                    return response.text
                except Exception as inner_e:
                    logger.error(f"Fallback also failed: {str(inner_e)}")
            raise e
        
    def function_call(self, prompt, system_prompt=None, functions=None, function_name=None):
        logger.debug(f"Attempting function call with prompt: {prompt[:50]}...")
        
        if not self.genai_model or not functions:
            return self._direct_classification(prompt, system_prompt)
        
        try:

            if functions and functions[0]["name"] == "classify_query":

                classification_prompt = """
                Bạn là chuyên gia phân loại truy vấn. Nhiệm vụ của bạn là phân loại câu hỏi sau vào loại RAG hoặc Chitchat.
                
                RAG (Truy vấn thông tin): Là câu hỏi yêu cầu tìm kiếm thông tin, kiến thức cụ thể từ cơ sở dữ liệu
                Chitchat (Trò chuyện): Là câu chào, hỏi thăm, trò chuyện thông thường không yêu cầu tra cứu thông tin
                
                Ví dụ:
                - "hello", "chào bạn", "bạn là ai" => Chitchat
                - "thông tin tuyển sinh", "điểm chuẩn 2023", "điều kiện nhập học" => RAG
                
                Phân loại: {query}
                
                Chỉ trả lời chính xác "RAG" hoặc "Chitchat" không kèm giải thích.
                """

                formatted_prompt = classification_prompt.format(query=prompt)
                response = self.generate(formatted_prompt, temperature=0)
                result = response.strip()
                
                if "rag" in result.lower():
                    logger.info(f"Direct classification for '{prompt[:30]}...': RAG")
                    return {"category": "RAG", "confidence": 0.9}
                else:
                    logger.info(f"Direct classification for '{prompt[:30]}...': Chitchat")
                    return {"category": "Chitchat", "confidence": 0.9}
            
            return self._direct_classification(prompt, system_prompt)
            
        except Exception as e:
            logger.error(f"Error in function_call: {str(e)}")
            return self._direct_classification(prompt, system_prompt)

    def _direct_classification(self, prompt, system_prompt=None):

        try:
            education_keywords = [
                "tuyển sinh", "đề án", "đại học", "cao đẳng", "học phí", "điểm chuẩn", 
                "ngành học", "khoa", "trường", "điều kiện", "xét tuyển", "tốt nghiệp",
                "đăng ký", "nhập học", "sinh viên", "học sinh", "giáo dục"
            ]
            
            prompt_lower = prompt.lower()
            for keyword in education_keywords:
                if keyword in prompt_lower:
                    logger.info(f"Keyword '{keyword}' found in query - classifying as RAG")
                    return {"category": "RAG", "confidence": 0.95}
            
            classification_prompt = """
            Phân loại câu hỏi sau vào loại RAG (tìm kiếm thông tin) hoặc Chitchat (trò chuyện)?
            
            Câu hỏi: {query}
            
            Chỉ trả lời "RAG" hoặc "Chitchat" không kèm giải thích.
            """
            formatted_prompt = classification_prompt.format(query=prompt)
            response = self.generate(formatted_prompt, temperature=0)
            
            result = response.strip().lower()
            
            if "rag" in result:
                return {"category": "RAG", "confidence": 0.8}
            else:
                return {"category": "Chitchat", "confidence": 0.8}
                
        except Exception as e:
            logger.error(f"Error in direct classification: {str(e)}")
            return {"category": "RAG", "confidence": 0.6}