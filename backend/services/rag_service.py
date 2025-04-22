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
            "vi": """
            Câu hỏi: {question}

            Thông tin tham khảo:
            {context}

            Hãy trả lời câu hỏi trên bằng tiếng Việt dựa trên thông tin tham khảo. 
            Trả lời phải bằng tiếng Việt, ngắn gọn và dễ hiểu.
            Nếu không có thông tin liên quan, trả lời bằng tiếng Việt: "Tôi không tìm thấy thông tin về vấn đề này trong dữ liệu đã cung cấp."
            """,

            "en": """
            Question: {question}

            Reference information:
            {context}

            Please answer the question in English based on the provided information.
            Keep your answer in English, concise and understandable.
            If no relevant information is found, respond in English: "I couldn't find information about this topic in the provided data."
            """
        }
        

        self.system_prompts = {
            "vi": "Bạn là trợ lý AI chuyên trả lời các câu hỏi bằng tiếng Việt. Luôn sử dụng tiếng Việt trong câu trả lời của bạn, ngay cả khi thông tin tham khảo bằng ngôn ngữ khác.",
            "en": "You are an AI assistant specialized in answering questions in English. Always use English in your responses, even if the reference information is in another language."
        }
    
    def _truncate_text(self, text: str, max_length: int = 1000) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def _select_best_chunks(self, docs: List[Document], max_chunks: int = 3) -> List[Document]:
        if len(docs) <= max_chunks:
            return docs
            

        if hasattr(docs[0], 'metadata') and 'score' in docs[0].metadata:
            sorted_docs = sorted(docs, key=lambda x: x.metadata.get('score', 0), reverse=True)
            return sorted_docs[:max_chunks]
            

        return docs[:max_chunks]
    
    def format_documents(self, docs: List[Document], max_length_per_doc: int = 300) -> str:
        formatted_texts = []
        
        for i, doc in enumerate(docs):

            source_info = ""
            if hasattr(doc, 'metadata'):
                title = doc.metadata.get('title', f'Document {i+1}')
                source_info = f"[{title}]"
            else:
                source_info = f"[Document {i+1}]"
                

            content = self._truncate_text(doc.page_content, max_length_per_doc)
            

            formatted_texts.append(f"{source_info}\n{content}")
            
        return "\n\n".join(formatted_texts)
    
    def _extract_valid_document_ids(self, docs: List[Document]) -> List[Dict[str, Any]]:
        valid_sources = []
        for doc in docs:
            if hasattr(doc, 'metadata') and doc.metadata:
                doc_id = doc.metadata.get('chunk_id')
                if not doc_id:
                    doc_id = doc.metadata.get('id')

                if doc_id:
                    source_data = {
                        "id": doc_id,
                        "title": doc.metadata.get('title', 'Unknown'),
                        "category": doc.metadata.get('category', 'general'),
                    }
                    if 'score' in doc.metadata:
                        source_data["relevance_score"] = doc.metadata.get('score')
                    valid_sources.append(source_data)
                
        return valid_sources
    
    def _ensure_vietnamese_response(self, response: str) -> str:

        en_vi_markers = {
            "I couldn't find": "Tôi không tìm thấy",
            "I don't have": "Tôi không có",
            "Based on the information": "Dựa trên thông tin",
            "According to the": "Theo",
            "Sorry": "Xin lỗi",
            "Please": "Vui lòng",
            "The information": "Thông tin",
            "Thank you": "Cảm ơn",
            "There is no": "Không có"
        }
        
        english_markers = ["the", "is", "are", "was", "were", "to", "for", "in", "on", "at", "by", "with", "information"]
        english_count = sum(1 for marker in english_markers if f" {marker} " in f" {response.lower()} ")

        if english_count >= 3 or any(marker in response for marker in en_vi_markers.keys()):
            try:

                translate_prompt = f"""
                Dịch văn bản sau từ tiếng Anh sang tiếng Việt:
                
                "{response}"
                
                Chỉ trả về bản dịch tiếng Việt, không thêm chú thích.
                """
                
                translated = self.llm_client.generate(
                    prompt=translate_prompt,
                    system_prompt="Bạn là chuyên gia dịch thuật Anh-Việt. Dịch chính xác và tự nhiên."
                )
                
                logger.info("Đã dịch phản hồi từ tiếng Anh sang tiếng Việt")
                return translated
            except Exception as e:
                logger.error(f"Lỗi khi dịch: {str(e)}")
                

                for en, vi in en_vi_markers.items():
                    response = response.replace(en, vi)
                
                return response
                
        return response
    
    def process_query(self, query: str, language: str = "vi") -> Dict[str, Any]:
        """Xử lý truy vấn để trả về kết quả từ kho kiến thức"""
        if language not in self.prompt_templates:
            language = "vi"
            
        logger.info(f"Processing RAG query: {query}")
        try:

            retriever = self.chroma_manager.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  
            )
            
            try:
                relevant_docs = retriever.invoke(query)
            except Exception as e:
                logger.warning(f"Error using invoke method: {str(e)}, falling back to old method")

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
            
            valid_sources = self._extract_valid_document_ids(relevant_docs)
            logger.info(f"Found {len(relevant_docs)} documents, {len(valid_sources)} have valid IDs")
            
            try:
                filtered_docs = self._select_best_chunks(relevant_docs, max_chunks=3)
                formatted_context = self.format_documents(filtered_docs, max_length_per_doc=300)
                
                prompt = self.prompt_templates[language].format(
                    question=query,
                    context=formatted_context
                )
                
                system_prompt = self.system_prompts[language]
                logger.debug(f"Prompt size: {len(prompt)} characters")
                
                response_text = self.llm_client.generate(
                    prompt=prompt,
                    system_prompt=system_prompt
                )
                
                if language == "vi":
                    response_text = self._ensure_vietnamese_response(response_text)
                
                logger.info(f"Generated RAG response for query: {query}")
                
                return {
                    "response": response_text,
                    "source_documents": valid_sources 
                }
            except Exception as e:
                logger.error(f"Error in RAG chain: {str(e)}")
                
                response_text = self.fallback_response(query, relevant_docs, language)
                
                if language == "vi":
                    response_text = self._ensure_vietnamese_response(response_text)
                
                return {
                    "response": response_text,
                    "source_documents": valid_sources
                }
            
        except Exception as e:
            logger.error(f"Error in RAG processing: {str(e)}")
            
            if language == "vi":
                error_message = f"Đã xảy ra lỗi khi xử lý truy vấn: {str(e)}"
            else:
                error_message = f"Error processing query: {str(e)}"
                
            return {
                "response": error_message,
                "source_documents": []
            }
    
    def fallback_response(self, query: str, context_docs: List[Document], language: str = "vi") -> str:

        minimal_docs = self._select_best_chunks(context_docs, max_chunks=2)
        minimal_context = self.format_documents(minimal_docs, max_length_per_doc=200)
        
        if language == "vi":
            prompt = f"Câu hỏi: {query}\nThông tin: {minimal_context}\n\nHãy trả lời bằng tiếng Việt:"
            system_prompt = "Bạn là trợ lý AI trả lời bằng tiếng Việt. Luôn sử dụng tiếng Việt không dùng tiếng Anh."
        else:
            prompt = f"Question: {query}\nInformation: {minimal_context}\n\nAnswer in English:"
            system_prompt = "You are an AI assistant responding in English."
        
        try:
            response = self.llm_client.generate(prompt=prompt, system_prompt=system_prompt)

            if language == "vi":
                response = self._ensure_vietnamese_response(response)
            return response
        except Exception as e:

            logger.error(f"Fallback response failed: {str(e)}")
            if language == "vi":
                return "Tôi gặp khó khăn khi trả lời câu hỏi này dựa trên thông tin có sẵn."
            else:
                return "I'm having trouble answering this question based on the available information."