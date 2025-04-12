from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import jwt
from flask import request, current_app, jsonify
import functools
import logging
import json

logger = logging.getLogger(__name__)

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class JWTManager:
    def __init__(self, secret_key: str, expires_delta: int = 24*60*60, refresh_expires_delta: int = 7*24*60*60):
        self.secret_key = secret_key
        self.expires_delta = expires_delta
        self.refresh_expires_delta = refresh_expires_delta
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:

        user_data_serializable = json.loads(json.dumps(user_data, cls=JSONEncoder))
        
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=self.expires_delta),
            'iat': datetime.utcnow(),
            'sub': user_data.get('id', 0),
            'data': user_data_serializable
        }
        
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=self.refresh_expires_delta),
            'iat': datetime.utcnow(),
            'sub': user_data.get('id', 0),
            'type': 'refresh'
        }
        
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=['HS256']
        )
    
    def get_token_from_header(self) -> Optional[str]:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
            
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
            
        return parts[1]
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        token = self.get_token_from_header()
        if not token:
            return None
            
        try:
            payload = self.decode_token(token)
            return payload.get('data')
        except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.InvalidTokenError) as e:
            logger.error(f"JWT error: {str(e)}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, str, Optional[str]]:
        try:
            payload = self.decode_token(refresh_token)
            
            if payload.get('type') != 'refresh':
                return False, "Token không phải refresh token", None
                
            user_id = payload.get('sub')
            
            from models.user import User
            from db.mysql_manager import MySQLManager
            
            db = MySQLManager()
            user_data = db.get_user_by_id(user_id)
            
            if not user_data:
                return False, "Người dùng không tồn tại", None
                

            user = User.from_dict(user_data)
            user_dict = user.to_dict()
            
            new_token = self.create_access_token(user_dict)
            
            return True, "Token đã được làm mới", new_token
            
        except jwt.exceptions.ExpiredSignatureError:
            return False, "Refresh token đã hết hạn", None
        except jwt.exceptions.InvalidTokenError as e:
            logger.error(f"Invalid token error: {str(e)}")
            return False, "Refresh token không hợp lệ", None
        except Exception as e:
            logger.error(f"Unexpected error refreshing token: {str(e)}")
            return False, f"Lỗi không xác định: {str(e)}", None


def jwt_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        jwt_manager = current_app.jwt_manager
        
        token = jwt_manager.get_token_from_header()
        
        if not token:
            return jsonify({"error": "Missing token"}), 401
            
        try:
            payload = jwt_manager.decode_token(token)

            request.current_user = payload.get('data')
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.exceptions.InvalidTokenError as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
        except Exception as e:
            return jsonify({"error": f"Error processing token: {str(e)}"}), 500
            
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        jwt_manager = current_app.jwt_manager
        
        token = jwt_manager.get_token_from_header()
        
        if not token:
            return jsonify({"error": "Missing token"}), 401
            
        try:
            payload = jwt_manager.decode_token(token)
            user_data = payload.get('data', {})
            
            if user_data.get('role') != 'admin':
                return jsonify({"error": "Không có quyền thực hiện hành động này"}), 403
                
            request.current_user = user_data
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.exceptions.InvalidTokenError as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
        except Exception as e:
            return jsonify({"error": f"Error processing token: {str(e)}"}), 500
            
        return f(*args, **kwargs)
    return decorated