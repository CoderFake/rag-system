import streamlit as st
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
import hashlib
import time

class UserAuth:
    def __init__(self, users_file: str = "users.json", i18n_manager = None):
        self.users_file = users_file
        self.i18n = i18n_manager
        self.users = self._load_users()
        
    def _load_users(self) -> Dict:
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        else:
            default_users = {
                "admin": {
                    "password": self._hash_password("admin123"),
                    "role": "admin",
                    "name": "Administrator",
                    "created_at": datetime.now().isoformat()
                }
            }
            self._save_users(default_users)
            return default_users
    
    def _save_users(self, users: Dict) -> None:
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        if username not in self.users:
            return False, self._get_text("user_not_found")
            
        hashed_password = self._hash_password(password)
        if self.users[username]["password"] != hashed_password:
            return False, self._get_text("invalid_password")
            
        return True, self._get_text("login_success")
    
    def create_user(self, username: str, password: str, role: str = "user", name: str = "") -> Tuple[bool, str]:
        if username in self.users:
            return False, self._get_text("user_exists")
            
        self.users[username] = {
            "password": self._hash_password(password),
            "role": role,
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_users(self.users)
        return True, self._get_text("user_created")
    
    def get_user_role(self, username: str) -> Optional[str]:
        if username in self.users:
            return self.users[username]["role"]
        return None
    
    def is_admin(self, username: str) -> bool:
        return self.get_user_role(username) == "admin"
    
    def _get_text(self, key: str) -> str:
       
        if self.i18n:
            return self.i18n.get_text(key)

        default_texts = {
            "user_not_found": "Không tìm thấy người dùng",
            "invalid_password": "Mật khẩu không đúng",
            "login_success": "Đăng nhập thành công",
            "user_exists": "Tên người dùng đã tồn tại",
            "user_created": "Tạo người dùng thành công",
            "admin_required": "Bạn cần quyền admin để thực hiện thao tác này"
        }
        
        return default_texts.get(key, key)