from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.schema import Document
from typing import Dict, List, Any, Tuple
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, chroma_manager, llm_client):
        self.chroma_manager = chroma_manager
        self.llm_client = llm_client
        
        self.prompt_templates = {
            "vi": PromptTemplate.from_template(
                """
                Dưới đây là lịch sử trò chuyện giữa người dùng và AI, cùng với câu hỏi hiện tại và các đoạn văn bản liên quan.
                
                {chat_history}
                
                Câu hỏi hiện tại: {question}
                
                Đoạn văn bản liên quan:
                {context}
                
                Hãy trả lời ngắn gọn, đầy đủ và chính xác bằng tiếng Việt. Sử dụng thông tin từ đoạn văn bản và lịch sử trò chuyện để đảm bảo câu trả lời nhất quán.
                Nếu thông tin không được cung cấp trong đoạn văn bản, nhưng bạn có thể trả lời từ kiến thức có sẵn, hãy nói "Tôi không tìm thấy thông tin cụ thể về vấn đề này trong dữ liệu đã cung cấp, nhưng..." và tiếp tục với câu trả lời của bạn.
                Nếu hoàn toàn không có thông tin, hãy nói "Tôi không tìm thấy thông tin về vấn đề này trong dữ liệu đã cung cấp."
                """
            ),
            "en": PromptTemplate.from_template(
                """
                Below is a conversation history between a user and AI, along with the current question and related text passages.
                
                {chat_history}
                
                Current question: {question}
                
                Relevant passages:
                {context}
                
                Please provide a concise, complete, and accurate answer in English. Use information from both the passages and the conversation history to ensure a consistent answer.
                If the information is not provided in the passages, but you can answer from your knowledge, say "I couldn't find specific information about this in the provided data, but..." and continue with your answer.
                If there is no information at all, say "I couldn't find information about this in the provided data."
                """
            )
        }
    
    def format_documents(self, docs: List[Document]) -> str:
        return "\n\n".join(f"Đoạn {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs))
    
    def format_chat_history(self, chat_history: List[Dict[str, Any]], language: str = "vi") -> str:
        if not chat_history:
            return "Không có lịch sử trò chuyện trước đó." if language == "vi" else "No previous conversation history."
            
        formatted_history = "LỊCH SỬ TRÒ CHUYỆN:\n" if language == "vi" else "CONVERSATION HISTORY:\n"
        
        for msg in chat_history:
            if msg['type'] == 'query':
                prefix = "Người dùng: " if language == "vi" else "User: "
                formatted_history += f"{prefix}{msg['content']}\n"
            else:
                prefix = "AI: " if language == "vi" else "AI: "
                formatted_history += f"{prefix}{msg['content']}\n"
                
        return formatted_history
    
    def process_query(self, query: str, language: str = "vi", chat_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        if chat_history is None:
            chat_history = []

        if language not in self.prompt_templates:
            language = "vi"
            
        logger.info(f"Processing RAG query: {query}")
        
        try:
            formatted_chat_history = self.format_chat_history(chat_history, language)

            retriever = self.chroma_manager.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            relevant_docs = retriever.get_relevant_documents(query)
            
            if not relevant_docs:
                if language == "vi":
                    return {
                        "response": "Tôi không tìm thấy thông tin liên quan trong kho kiến thức. Bạn có thể đặt câu hỏi khác hoặc cung cấp thêm thông tin chi tiết.",
                        "source_documents": []
                    }
                else:
                    return {
                        "response": "I couldn't find relevant information in the knowledge base. You can ask a different question or provide more details.",
                        "source_documents": []
                    }
            
            formatted_docs = self.format_documents(relevant_docs)
            prompt_template = self.prompt_templates[language]
            
            full_prompt = prompt_template.format(
                question=query,
                context=formatted_docs,
                chat_history=formatted_chat_history
            )
            
            response = self.llm_client.generate(
                prompt=full_prompt
            )
            
            logger.info(f"Generated RAG response for query: {query}")
            
            return {
                "response": response,
                "source_documents": relevant_docs
            }
            
        except Exception as e:
            logger.error(f"Error in RAG processing: {str(e)}")
            
            if language == "vi":
                error_message = f"Xảy ra lỗi khi xử lý truy vấn: {str(e)}"
            else:
                error_message = f"Error processing query: {str(e)}"
                
            return {
                "response": error_message,
                "source_documents": []
            }
    
    def enhance_with_context(self, query: str, context_docs: List[Document], language: str = "vi", chat_history: List[Dict[str, Any]] = None) -> str:
        if chat_history is None:
            chat_history = []
            
        formatted_context = self.format_documents(context_docs)
        formatted_chat_history = self.format_chat_history(chat_history, language)
        
        prompt_template = self.prompt_templates[language]
        
        prompt = prompt_template.format(
            question=query,
            context=formatted_context,
            chat_history=formatted_chat_history
        )
        
        response = self.llm_client.generate(prompt=prompt)
        
        return response