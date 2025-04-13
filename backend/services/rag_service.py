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
            "vi": """Câu hỏi: {question}

            Thông tin tham khảo:
            {context}

            Trả lời ngắn gọn dựa trên thông tin trên. Nếu không có thông tin liên quan, nói "Tôi không tìm thấy thông tin về vấn đề này."
            """,

            "en": """Question: {question}

            Reference information:
            {context}

            Answer concisely based on the information above. If no relevant information is found, say "I couldn't find information about this topic."
            """
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
    
    def process_query(self, query: str, language: str = "vi") -> Dict[str, Any]:
        if language not in self.prompt_templates:
            language = "vi"
            
        logger.info(f"Processing RAG query with languge: {query}", language)
        
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
                
                logger.debug(f"Prompt size: {len(prompt)} characters")
                
                response_text = self.llm_client.generate(prompt=prompt)
                
                logger.info(f"Generated RAG response for query: {query}")
                
                return {
                    "response": response_text,
                    "source_documents": valid_sources  
                }
            except Exception as e:
                logger.error(f"Error in RAG chain: {str(e)}")
                
                return {
                    "response": self.fallback_response(query, relevant_docs, language),
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
            prompt = f"Câu hỏi: {query}\nThông tin: {minimal_context}\nTrả lời:"
        else:
            prompt = f"Question: {query}\nInformation: {minimal_context}\nAnswer:"
        
        try:
            return self.llm_client.generate(prompt=prompt)
        except Exception as e:
            logger.error(f"Fallback response failed: {str(e)}")
            if language == "vi":
                return "Tôi gặp khó khăn khi trả lời câu hỏi này dựa trên thông tin có sẵn."
            else:
                return "I'm having trouble answering this question based on the available information."