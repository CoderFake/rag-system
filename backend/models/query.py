from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class Query:
  
    def __init__(
        self,
        id: Optional[str] = None,
        text: str = "",
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        language: str = "vi",
        query_type: str = "rag",
        enhanced_text: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.text = text
        self.user_id = user_id
        self.session_id = session_id
        self.language = language
        self.query_type = query_type
        self.enhanced_text = enhanced_text
        self.embedding = embedding or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now().isoformat()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Query':
        return cls(
            id=data.get("id"),
            text=data.get("text", ""),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            language=data.get("language", "vi"),
            query_type=data.get("query_type", "rag"),
            enhanced_text=data.get("enhanced_text"),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "language": self.language,
            "query_type": self.query_type,
            "enhanced_text": self.enhanced_text,
            "metadata": self.metadata,
            "created_at": self.created_at
        }
    
    def get_effective_text(self) -> str:
        return self.enhanced_text if self.enhanced_text else self.text