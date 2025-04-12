from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
import json

class User:
    
    def __init__(
        self,
        id: Optional[int] = None,
        username: str = "",
        password: Optional[str] = None,
        name: str = "",
        email: str = "",
        role: str = "user",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.role = role
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':

        if not data or not isinstance(data, dict):
            return cls()
            

        created_at = data.get('created_at')
        if created_at and not isinstance(created_at, str):
            try:
                if isinstance(created_at, datetime):
                    created_at = created_at.isoformat()
                else:
                    created_at = str(created_at)
            except:
                created_at = datetime.now().isoformat()
                
        updated_at = data.get('updated_at')
        if updated_at and not isinstance(updated_at, str):
            try:
                if isinstance(updated_at, datetime):
                    updated_at = updated_at.isoformat()
                else:
                    updated_at = str(updated_at)
            except:
                updated_at = datetime.now().isoformat()
        
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            password=data.get('password'),
            name=data.get('name', ''),
            email=data.get('email', ''),
            role=data.get('role', 'user'),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if include_password and self.password:
            result['password'] = self.password
            
        return result
    
    def set_password(self, password: str) -> None:
        self.password = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        if not self.password:
            return False
            
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return hashed == self.password
    
    def is_admin(self) -> bool:
        return self.role == 'admin'
        
    def __str__(self):
        return f"User(id={self.id}, username={self.username}, role={self.role})"