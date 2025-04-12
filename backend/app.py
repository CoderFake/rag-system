
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv


from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from services.rag_service import RAGService
from services.semantic_router_service import SemanticRouterService
from services.reflection_service import ReflectionService


from models.document import Document
from models.query import Query
from models.response import Response


from utils.file_utils import save_temporary_file
from utils.text_processor import clean_text


from config.settings import Config


load_dotenv()


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)


from llm.gemini_client import GeminiClient
from vector_store.chroma_client import ChromaManager


llm_client = GeminiClient(api_key=app.config["GEMINI_API_KEY"])


chroma_manager = ChromaManager(
    persist_directory=app.config["CHROMA_DB_PATH"],
    embedding_model=app.config["EMBEDDING_MODEL"]
)


document_service = DocumentService(chroma_manager)
embedding_service = EmbeddingService()
rag_service = RAGService(chroma_manager, llm_client)
semantic_router = SemanticRouterService(llm_client)
reflection_service = ReflectionService(llm_client)



@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "version": "1.0.0"})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "")
    session_id = data.get("session_id", "default")
    language = data.get("language", "vi") 
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
        
    enhanced_query = reflection_service.enhance_query(query)
    
    route_type, route_data = semantic_router.route_query(enhanced_query, {
        "session_id": session_id,
        "language": language
    })
    if route_type == "admission_query":
        result = rag_service.process_query(route_data["query"], language=language)
        
        return jsonify({
            "response": result["response"],
            "source_documents": [doc.metadata for doc in result.get("source_documents", [])],
            "route_type": "rag"
        })
    else:
        response = llm_client.generate(
            prompt=route_data["query"],
            system_prompt=f"Bạn là trợ lý AI hữu ích trả lời bằng {'tiếng Việt' if language == 'vi' else 'English'}."
        )
        
        return jsonify({
            "response": response,
            "source_documents": [],
            "route_type": "chitchat"
        })

@app.route("/api/admin/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
        
    metadata = {
        "title": request.form.get("title", ""),
        "category": request.form.get("category", "general"),
        "tags": request.form.get("tags", "").split(",") if request.form.get("tags") else [],
        "description": request.form.get("description", "")
    }
    
    try:
        result = document_service.process_file(file, metadata)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/documents", methods=["GET"])
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
def delete_document(document_id):
    try:
        result = document_service.delete_document(document_id)
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/reindex", methods=["POST"])
def reindex_documents():
    try:
        result = document_service.reindex_all()
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings", methods=["GET"])
def get_settings():
    try:
        settings = {
            "chunk_size": app.config["CHUNK_SIZE"],
            "chunk_overlap": app.config["CHUNK_OVERLAP"],
            "embedding_model": app.config["EMBEDDING_MODEL"],
            "supported_languages": ["vi", "en"]
        }
        
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings", methods=["POST"])
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

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host="0.0.0.0", port=5000)