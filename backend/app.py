from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from services.rag_service import RAGService
from services.semantic_router_service import SemanticRouterService
from services.reflection_service import ReflectionService
from services.chat_service import ChatService

from models.document import Document
from models.query import Query
from models.response import Response
from models.user import User

from utils.file_utils import save_temporary_file, save_uploaded_file
from utils.text_processor import clean_text, detect_language

from config.settings import Config
from auth.jwt_manager import JWTManager, jwt_required, admin_required
from db.mysql_manager import MySQLManager

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

load_dotenv()

app = Flask(__name__)
CORS(app)
app.json_encoder = CustomJSONEncoder
app.config.from_object(Config)

from llm.gemini_client import GeminiClient
from llm.ollama_client import OllamaClient
from vector_store.chroma_client import ChromaManager
from vector_store.embedding_manager import EmbeddingManager
from vector_store.query_processor import QueryProcessor

from auth.jwt_manager import JWTManager
jwt_manager = JWTManager(
    secret_key=app.config["JWT_SECRET_KEY"],
    expires_delta=app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    refresh_expires_delta=app.config["JWT_REFRESH_TOKEN_EXPIRES"]
)
app.jwt_manager = jwt_manager

db_manager = MySQLManager()

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


llm_client = None


has_gemini = bool(app.config.get("GEMINI_API_KEY"))
if not has_gemini:
    app.logger.warning("Không tìm thấy GEMINI_API_KEY trong cấu hình. Gemini sẽ không hoạt động.")


if Config.LLM_PROVIDER.lower() == 'ollama':
    try:

        gemini_fallback = None
        if has_gemini:
            gemini_fallback = GeminiClient(api_key=app.config["GEMINI_API_KEY"])
            

        llm_client = OllamaClient(fallback_client=gemini_fallback)
        app.logger.info(f"Đã khởi tạo Ollama client với model {Config.OLLAMA_MODEL_NAME}" + 
                      (", có Gemini fallback" if gemini_fallback else ", không có fallback"))
    except Exception as e:

        app.logger.error(f"Không thể khởi tạo Ollama client: {str(e)}.")
        if has_gemini:
            app.logger.info("Sử dụng Gemini thay thế do lỗi Ollama.")
            llm_client = GeminiClient(api_key=app.config["GEMINI_API_KEY"])
        else:
            app.logger.error("Không thể fallback sang Gemini do thiếu API key.")
elif has_gemini:

    llm_client = GeminiClient(api_key=app.config["GEMINI_API_KEY"])
    app.logger.info("Sử dụng Gemini client làm LLM chính")
else:
    app.logger.error("Không có LLM client nào được cấu hình đúng. Hệ thống sẽ không hoạt động đúng.")


if llm_client is None:
    class DummyLLMClient:
        def generate(self, prompt, system_prompt=None, temperature=None):
            return "Lỗi: Không thể kết nối đến mô hình ngôn ngữ. Vui lòng kiểm tra cấu hình GEMINI_API_KEY hoặc Ollama."
    llm_client = DummyLLMClient()
    app.logger.warning("Sử dụng DummyLLMClient do không có LLM client hợp lệ")

embedding_service = EmbeddingService(model_name=app.config["EMBEDDING_MODEL"])

chroma_manager = ChromaManager(
    persist_directory=app.config["CHROMA_DB_PATH"],
    embedding_model=app.config["EMBEDDING_MODEL"]
)

embedding_manager = EmbeddingManager(model_name=app.config["EMBEDDING_MODEL"])

query_processor = QueryProcessor(chroma_manager, embedding_manager)

document_service = DocumentService(chroma_manager, db_manager=db_manager)
rag_service = RAGService(chroma_manager, llm_client)
semantic_router = SemanticRouterService(llm_client)
reflection_service = ReflectionService(llm_client)
chat_service = ChatService(semantic_router, reflection_service, rag_service, llm_client, db_manager)

app.jwt_manager = jwt_manager
app.db_manager = db_manager

@app.route("/api/health", methods=["GET"])
def health_check():

    llm_info = "Unknown"
    if Config.LLM_PROVIDER.lower() == 'ollama':
        if isinstance(llm_client, OllamaClient):
            if hasattr(llm_client, 'model_ready') and llm_client.model_ready:
                llm_info = f"Ollama ({Config.OLLAMA_MODEL_NAME})"
            else:
                llm_info = f"Ollama ({Config.OLLAMA_MODEL_NAME}) - đang tải"
                if hasattr(llm_client, 'fallback_client') and llm_client.fallback_client:
                    llm_info += ", sử dụng Gemini tạm thời"
        elif isinstance(llm_client, GeminiClient):
            llm_info = "Gemini (Ollama fallback)"
    elif isinstance(llm_client, GeminiClient):
        llm_info = "Gemini"
    
    return jsonify({
        "status": "healthy", 
        "version": "1.0.0",
        "llm_provider": llm_info,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "")
    session_id = data.get("session_id", "default")
    language = data.get("language", "vi")
    
    user_id = None
    token = jwt_manager.get_token_from_header()
    if token:
        try:
            payload = jwt_manager.decode_token(token)
            user_data = payload.get('data', {})
            user_id = user_data.get('id')
        except:
            pass
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    if not language:
        language = detect_language(query)
    
    result = chat_service.process_query(
        query_text=query,
        session_id=session_id,
        user_id=user_id,
        language=language
    )
    
    return jsonify(result)

@app.route("/api/chat/history", methods=["GET"])
def get_chat_history():
    session_id = request.args.get("session_id", "default")
    limit = int(request.args.get("limit", 50))
    
    history = chat_service.get_chat_history(session_id, limit)
    
    return jsonify({"history": history})

@app.route("/api/chat/feedback", methods=["POST"])
def add_feedback():
    data = request.json
    response_id = data.get("response_id")
    feedback_type = data.get("type", "thumbs_up")
    value = data.get("value", "")
    
    if not response_id:
        return jsonify({"error": "Response ID is required"}), 400
    
    user_id = None
    token = jwt_manager.get_token_from_header()
    if token:
        try:
            payload = jwt_manager.decode_token(token)
            user_data = payload.get('data', {})
            user_id = user_data.get('id')
        except:
            pass
    
    success = chat_service.add_feedback(
        response_id=response_id,
        user_id=user_id,
        feedback_type=feedback_type,
        value=value
    )
    
    if success:
        return jsonify({"message": "Feedback đã được lưu thành công"})
    else:
        return jsonify({"error": "Đã xảy ra lỗi khi lưu feedback"}), 500

@app.route("/api/admin/upload", methods=["POST"])
@admin_required
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "Thiếu file"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Chưa chọn file"}), 400
        
    metadata = {
        "title": request.form.get("title", ""),
        "category": request.form.get("category", "general"),
        "tags": request.form.get("tags", "").split(",") if request.form.get("tags") else [],
        "description": request.form.get("description", "")
    }
    
    current_user = request.current_user
    if current_user:
        metadata["user_id"] = current_user.get("id")
    
    try:
        result = document_service.process_file(file, metadata)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/documents", methods=["GET"])
@admin_required
def get_documents():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        category = request.args.get("category")
        
        documents = document_service.get_all_documents(
            page=page,
            limit=limit,
            category=category
        )
        
        return jsonify({
            "documents": documents,
            "total": len(documents),
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/documents/<document_id>", methods=["DELETE"])
@admin_required
def delete_document(document_id):
    try:
        result = document_service.delete_document(document_id)
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/reindex", methods=["POST"])
@admin_required
def reindex_documents():
    try:
        result = document_service.reindex_all()
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings", methods=["GET"])
def get_settings():
    try:
        llm_info = {
            "provider": Config.LLM_PROVIDER,
            "status": "unknown"
        }
        
        if Config.LLM_PROVIDER.lower() == 'ollama':
            if isinstance(llm_client, OllamaClient):
                llm_info["provider"] = "ollama"
                llm_info["model"] = Config.OLLAMA_MODEL_NAME
                
                if hasattr(llm_client, 'model_ready') and llm_client.model_ready:
                    llm_info["status"] = "ready"
                else:
                    llm_info["status"] = "loading"
                    if hasattr(llm_client, 'fallback_client') and llm_client.fallback_client:
                        llm_info["fallback"] = "gemini"
            elif isinstance(llm_client, GeminiClient):
                llm_info["provider"] = "gemini"
                llm_info["status"] = "ready"
                llm_info["note"] = "Ollama failed, using Gemini"
        elif isinstance(llm_client, GeminiClient):
            llm_info["provider"] = "gemini"
            llm_info["status"] = "ready"
                
        settings = {
            "chunk_size": app.config["CHUNK_SIZE"],
            "chunk_overlap": app.config["CHUNK_OVERLAP"],
            "embedding_model": app.config["EMBEDDING_MODEL"],
            "llm_provider": Config.LLM_PROVIDER,
            "ollama_base_url": Config.OLLAMA_BASE_URL,
            "ollama_model_name": Config.OLLAMA_MODEL_NAME,
            "llm_status": llm_info,
            "supported_languages": ["vi", "en"]
        }
        
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings", methods=["POST"])
@admin_required
def update_settings():
    try:
        data = request.json
        
        if "chunk_size" in data:
            app.config["CHUNK_SIZE"] = int(data["chunk_size"])
        
        if "chunk_overlap" in data:
            app.config["CHUNK_OVERLAP"] = int(data["chunk_overlap"])
            
        chroma_manager.text_splitter.chunk_size = app.config["CHUNK_SIZE"]
        chroma_manager.text_splitter.chunk_overlap = app.config["CHUNK_OVERLAP"]
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from auth.auth_routes import init_auth_routes
auth_blueprint = init_auth_routes(jwt_manager)
app.register_blueprint(auth_blueprint)

from admin_routes import init_routes
admin_blueprint = init_routes(document_service)
app.register_blueprint(admin_blueprint)

with app.app_context():
    try:
        db_manager.setup_database()
    except Exception as e:
        app.logger.error(f"Error setting up database: {str(e)}")

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host="0.0.0.0", port=5000)