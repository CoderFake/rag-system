
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
                Dưới đây là một câu hỏi và các đoạn văn bản liên quan. Hãy sử dụng thông tin từ các đoạn văn bản này để trả lời câu hỏi.
                
                Câu hỏi: {question}
                
                Đoạn văn bản liên quan:
                {context}
                
                Hãy trả lời ngắn gọn, đầy đủ và chính xác bằng tiếng Việt. Nếu thông tin không được cung cấp trong đoạn văn bản, hãy nói "Tôi không tìm thấy thông tin về vấn đề này trong dữ liệu đã cung cấp."
                """
            ),
            "en": PromptTemplate.from_template(
                """
                Below is a question and related text passages. Please use the information from these passages to answer the question.
                
                Question: {question}
                
                Relevant passages:
                {context}
                
                Please provide a concise, complete, and accurate answer in English. If the information is not provided in the passages, say "I couldn't find information about this in the provided data."
                """
            )
        }
    
    def format_documents(self, docs: List[Document]) -> str:
        return "\n\n".join(f"Đoạn {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs))
    
    def process_query(self, query: str, language: str = "vi") -> Dict[str, Any]:

        if language not in self.prompt_templates:
            language = "vi"
            
        logger.info(f"Processing RAG query: {query}")
        
        try:

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
            

            rag_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | self.prompt_templates[language]
                | self.llm_client.llm
            )
            
            response = rag_chain.invoke(query)
            
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
    
    def enhance_with_context(self, query: str, context_docs: List[Document], language: str = "vi") -> str:
        formatted_context = self.format_documents(context_docs)
        
        prompt = self.prompt_templates[language].format(
            question=query,
            context=formatted_context
        )
        
        response = self.llm_client.generate(prompt=prompt)
        
        return response