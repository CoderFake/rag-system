from flask import Blueprint, request, jsonify, current_app
import logging
from db.mysql_manager import MySQLManager
from models.user import User
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def init_auth_routes(jwt_manager):
    
    @auth_bp.route('/login', methods=["POST"])
    def login():
        data = request.json
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Thiếu tên đăng nhập hoặc mật khẩu"}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        db = MySQLManager()
        
        try:
            user_data = db.authenticate_user(username, password)
            
            if not user_data:
                return jsonify({"error": "Tên đăng nhập hoặc mật khẩu không đúng"}), 401
                

            user = User.from_dict(user_data)
            user_dict = user.to_dict()
            
            access_token = jwt_manager.create_access_token(user_dict)
            refresh_token = jwt_manager.create_refresh_token(user_dict)
            
            return jsonify({
                "user": user_dict,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            })
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return jsonify({"error": f"Đã xảy ra lỗi khi đăng nhập: {str(e)}"}), 500
    
    @auth_bp.route('/register', methods=["POST"])
    def register():
        data = request.json
        
        if not data:
            return jsonify({"error": "Dữ liệu không hợp lệ"}), 400
            
        username = data.get('username')
        password = data.get('password')
        name = data.get('name', '')
        email = data.get('email', '')
        
        if not username or not password:
            return jsonify({"error": "Tên đăng nhập và mật khẩu là bắt buộc"}), 400
            
        db = MySQLManager()
        
        try:

            existing_user = db.execute_query(
                "SELECT id FROM users WHERE username = %s", 
                (username,), 
                fetch=True
            )
            
            if existing_user:
                return jsonify({"error": "Tên đăng nhập đã tồn tại"}), 409
                

            user_id = db.create_user(
                username=username,
                password=password,
                name=name,
                email=email,
                role="user"
            )
            

            user_data = db.get_user_by_id(user_id)
            
            if not user_data:
                return jsonify({"error": "Lỗi khi tạo người dùng"}), 500
                
            user = User.from_dict(user_data)
                
            return jsonify({
                "message": "Đăng ký thành công",
                "user": user.to_dict()
            })
            
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @auth_bp.route('/refresh', methods=["POST"])
    def refresh_token():
        data = request.json
        
        if not data or not data.get('refresh_token'):
            return jsonify({"error": "Refresh token là bắt buộc"}), 400
            
        refresh_token = data.get('refresh_token')
        
        try:
            success, message, new_token = jwt_manager.refresh_access_token(refresh_token)
            
            if not success:
                return jsonify({"error": message}), 401
                
            return jsonify({
                "access_token": new_token,
                "token_type": "bearer"
            })
            
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return jsonify({"error": "Đã xảy ra lỗi khi làm mới token"}), 500
    
    from auth.jwt_manager import jwt_required, admin_required
    
    @auth_bp.route('/profile', methods=["GET"])
    @jwt_required
    def get_profile():
        current_user = request.current_user
        
        if not current_user:
            return jsonify({"error": "Không tìm thấy thông tin người dùng"}), 401
            
        return jsonify({"user": current_user})
    
    @auth_bp.route('/users', methods=["GET"])
    @admin_required
    def get_users():
        db = MySQLManager()
        
        try:
            users_data = db.execute_query(
                "SELECT id, username, name, email, role, created_at FROM users", 
                fetch=True
            )
            

            for user in users_data:
                for key, value in user.items():
                    if isinstance(value, datetime):
                        user[key] = value.isoformat()
            
            return jsonify({"users": users_data})
            
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            return jsonify({"error": "Đã xảy ra lỗi khi lấy danh sách người dùng"}), 500
            
    return auth_bp