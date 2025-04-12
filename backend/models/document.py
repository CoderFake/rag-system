from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import uuid

class Document:
    
    def __init__(
        self,
        id: Optional[str] = None,
        title: str = "",
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        file_path: Optional[str] = None,
        file_type: Optional[str] = None,
        category: str = "general",
        tags: Optional[List[str]] = None,
        user_id: Optional[int] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.metadata = metadata or {}
        self.embedding = embedding or []
        self.file_path = file_path
        self.file_type = file_type
        self.category = category
        self.tags = tags or []
        self.user_id = user_id
        
        if created_at is None:
            self.created_at = datetime.now().isoformat()
        elif isinstance(created_at, datetime):
            self.created_at = created_at.isoformat()
        else:
            self.created_at = created_at
            
        if updated_at is None:
            self.updated_at = datetime.now().isoformat()
        elif isinstance(updated_at, datetime):
            self.updated_at = updated_at.isoformat()
        else:
            self.updated_at = updated_at
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding", []),
            file_path=data.get("file_path"),
            file_type=data.get("file_type"),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            user_id=data.get("user_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "category": self.category,
            "tags": self.tags,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_langchain_document(self) -> 'Document':
        from langchain.schema import Document as LangchainDocument
        
        metadata = self.metadata.copy()
        metadata.update({
            "id": self.id,
            "title": self.title,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "category": self.category,
            "tags": self.tags,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        })
        
        return LangchainDocument(
            page_content=self.content,
            metadata=metadata
        )
    
    @classmethod
    def from_langchain_document(cls, doc: Any) -> 'Document':
        metadata = doc.metadata.copy() if hasattr(doc, 'metadata') else {}
        

        doc_id = metadata.pop("id", str(uuid.uuid4()))
        title = metadata.pop("title", "")
        file_path = metadata.pop("file_path", None)
        file_type = metadata.pop("file_type", None)
        category = metadata.pop("category", "general")
        tags = metadata.pop("tags", [])
        user_id = metadata.pop("user_id", None)
        created_at = metadata.pop("created_at", datetime.now().isoformat())
        updated_at = metadata.pop("updated_at", datetime.now().isoformat())
        
        return cls(
            id=doc_id,
            title=title,
            content=doc.page_content if hasattr(doc, 'page_content') else "",
            metadata=metadata,
            file_path=file_path,
            file_type=file_type,
            category=category,
            tags=tags,
            user_id=user_id,
            created_at=created_at,
            updated_at=updated_at
        )