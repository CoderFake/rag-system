import requests
import json
import time
from typing import Dict, List, Any, Optional, Union

class APIClient:
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.refresh_token = None
        
    def set_token(self, token: str, refresh_token: Optional[str] = None):
        self.token = token
        if refresh_token:
            self.refresh_token = refresh_token
    
    def clear_token(self):
        self.token = None
        self.refresh_token = None
    
    def _get_headers(self):
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict:
        try:
            if response.status_code == 401 and self.refresh_token:

                new_token = self._refresh_token()
                if new_token:

                    response.request.headers["Authorization"] = f"Bearer {new_token}"
                    return self._handle_response(requests.request(
                        method=response.request.method,
                        url=response.request.url,
                        headers=response.request.headers,
                        data=response.request.body
                    ))
            
            if response.status_code >= 400:
                error_data = response.json() if response.content else {"error": response.reason}
                raise Exception(error_data.get("error", "Unknown error"))
                
            return response.json()
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {response.text}")
    
    def _refresh_token(self) -> Optional[str]:
        if not self.refresh_token:
            return None
            
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/refresh",
                json={"refresh_token": self.refresh_token},
                headers={"Content-Type": "application/json"}
            )
            
            data = response.json()
            if response.status_code == 200:
                self.token = data.get("access_token")
                return self.token
        except:
            pass
            
        return None
    

    def login(self, username: str, password: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        data = self._handle_response(response)

        if "access_token" in data:
            self.token = data["access_token"]
            self.refresh_token = data.get("refresh_token")
            
        return data
    
    def register(self, username: str, password: str, name: str = "", email: str = "") -> Dict:
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={
                "username": username,
                "password": password,
                "name": name,
                "email": email
            },
            headers={"Content-Type": "application/json"}
        )
        
        return self._handle_response(response)
    
    def get_profile(self) -> Dict:
        response = requests.get(
            f"{self.base_url}/api/auth/profile",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def health_check(self) -> Dict:
        response = requests.get(f"{self.base_url}/api/health")
        return self._handle_response(response)
    
    def chat(self, query: str, session_id: str = "default", language: str = "vi") -> Dict:
        payload = {
            "query": query,
            "session_id": session_id,
            "language": language
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat", 
            json=payload,
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def get_chat_history(self, session_id: str = "default", limit: int = 50) -> Dict:
        params = {
            "session_id": session_id,
            "limit": limit
        }
        
        response = requests.get(
            f"{self.base_url}/api/chat/history",
            params=params,
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def add_feedback(self, response_id: str, feedback_type: str, value: str = "") -> Dict:
        payload = {
            "response_id": response_id,
            "type": feedback_type,
            "value": value
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat/feedback",
            json=payload,
            headers=self._get_headers()
        )
        return self._handle_response(response)
    

    def get_documents(self, page: int = 1, limit: int = 10, category: Optional[str] = None) -> List[Dict]:
        params = {"page": page, "limit": limit}
        if category:
            params["category"] = category
            
        response = requests.get(
            f"{self.base_url}/api/admin/documents", 
            params=params,
            headers=self._get_headers()
        )
        
        data = self._handle_response(response)
        return data.get("documents", [])
    
    def delete_document(self, document_id: str) -> Dict:
        response = requests.delete(
            f"{self.base_url}/api/admin/documents/{document_id}",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def reindex(self) -> Dict:
        response = requests.post(
            f"{self.base_url}/api/admin/reindex",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def get_settings(self) -> Dict:
        response = requests.get(
            f"{self.base_url}/api/settings",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def update_settings(self, settings: Dict) -> Dict:
        response = requests.post(
            f"{self.base_url}/api/settings", 
            json=settings,
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def process_file(self, file, metadata: Dict) -> Dict:
        files = {"file": (file.name, file)}
        
        data = {}
        for key, value in metadata.items():
            if isinstance(value, list):
                data[key] = ",".join(value)
            else:
                data[key] = value
        
        try:
            response = requests.post(
                f"{self.base_url}/api/admin/upload",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {self.token}"} if self.token else {}
            )
            
            return self._handle_response(response)
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            raise