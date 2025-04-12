from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class Response:
   
    def __init__(
        self,
        id: Optional[str] = None,
        query_id: Optional[str] = None,
        text: str = "",
        query_text: str = "",
        source_documents: Optional[List[Dict[str, Any]]] = None,
        response_type: str = "rag",
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        language: str = "vi",
        feedback: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
        processing_time: Optional[float] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.query_id = query_id
        self.text = text
        self.query_text = query_text
        self.source_documents = source_documents or []
        self.response_type = response_type
        self.session_id = session_id
        self.user_id = user_id
        self.language = language
        self.feedback = feedback or {}
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.processing_time = processing_time
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Response':
        return cls(
            id=data.get("id"),
            query_id=data.get("query_id"),
            text=data.get("text", ""),
            query_text=data.get("query_text", ""),
            source_documents=data.get("source_documents", []),
            response_type=data.get("response_type", "rag"),
            session_id=data.get("session_id"),
            user_id=data.get("user_id"),
            language=data.get("language", "vi"),
            feedback=data.get("feedback", {}),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            processing_time=data.get("processing_time")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query_id": self.query_id,
            "text": self.text,
            "query_text": self.query_text,
            "source_documents": self.source_documents,
            "response_type": self.response_type,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "language": self.language,
            "feedback": self.feedback,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "processing_time": self.processing_time
        }
    
    def add_feedback(self, feedback_type: str, value: Any) -> None:
        if not self.feedback:
            self.feedback = {}
        self.feedback[feedback_type] = value
        self.feedback["updated_at"] = datetime.now().isoformat()
    
    def is_successful(self) -> bool:
        return bool(self.text.strip())