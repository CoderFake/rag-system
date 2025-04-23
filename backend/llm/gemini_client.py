import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", 
                google_api_key=api_key,
                max_output_tokens=2048
            )
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo LLM: {str(e)}")
            # Fallback khởi tạo với tham số tối thiểu
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", 
                google_api_key=api_key
            )
        
    def generate(self, prompt, system_prompt=None):
        """
        Tạo phản hồi với một prompt đơn giản.
        
        Args:
            prompt: Nội dung prompt
            system_prompt: System prompt tùy chọn
            
        Returns:
            Phản hồi từ mô hình
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
                
            messages.append(HumanMessage(content=prompt))
            
            response = self.llm.generate([messages])
            
            return response.generations[0][0].text
        except Exception as e:
            logger.error(f"Lỗi khi tạo phản hồi: {str(e)}")
            return f"Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này. Lỗi: {str(e)}"
        
    def generate_with_history(self, messages, system_prompt=None):
        """
        Tạo phản hồi với một lịch sử trò chuyện đầy đủ.
        
        Args:
            messages: Danh sách các tin nhắn dạng {"role": "user"|"assistant", "content": "text"}
            system_prompt: System prompt tùy chọn
            
        Returns:
            Phản hồi từ mô hình
        """
        try:
            langchain_messages = []
            
            if system_prompt:
                langchain_messages.append(SystemMessage(content=system_prompt))
            
            for msg in messages:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
            
            response = self.llm.generate([langchain_messages])
                
            return response.generations[0][0].text
        except Exception as e:
            logger.error(f"Lỗi khi tạo phản hồi với lịch sử: {str(e)}")
            try:
                last_user_message = None
                for msg in reversed(messages):
                    if msg["role"] == "user":
                        last_user_message = msg["content"]
                        break
                
                if last_user_message:
                    return self.generate(last_user_message, system_prompt)
                else:
                    return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này."
            except:
                return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này."
        
    def classify_query(self, query):
       
        system_prompt = """
        You are a query classifier that determines if a query requires retrieving 
        information from a knowledge base (RAG) or if it's just a conversational query (Chitchat).
        Respond with ONLY 'RAG' or 'Chitchat'.
        """
        
        try:
            result = self.generate(
                prompt=query,
                system_prompt=system_prompt
            ).strip().lower()
            
            if "rag" in result:
                return "RAG"
            else:
                return "Chitchat"
        except Exception as e:
            logger.error(f"Lỗi khi phân loại truy vấn: {str(e)}")
            return "Chitchat"