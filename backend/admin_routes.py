from flask import Blueprint, request, jsonify
import os
import logging
from dotenv import dotenv_values, set_key 
from config.settings import Config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def init_routes(document_service):

    @admin_bp.route('/upload', methods=["POST"])
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
            logger.error(f"Error uploading file: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @admin_bp.route('/documents', methods=["GET"])
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
            logger.error(f"Error getting documents: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @admin_bp.route('/documents/<document_id>', methods=["DELETE"])
    def delete_document(document_id):
        try:
            result = document_service.delete_document(document_id)
            return jsonify({"success": result})
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @admin_bp.route('/reindex', methods=["POST"])
    def reindex_documents():
        try:
            result = document_service.reindex_all()
            return jsonify({"success": result})
        except Exception as e:
            logger.error(f"Error reindexing documents: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @admin_bp.route('/settings', methods=['GET'])
    def get_settings():
        try:
            settings_data = {
                "chunk_size": Config.CHUNK_SIZE,
                "chunk_overlap": Config.CHUNK_OVERLAP,
                "embedding_model": Config.EMBEDDING_MODEL,
                "llm_provider": Config.LLM_PROVIDER,
                "ollama_base_url": Config.OLLAMA_BASE_URL,
                "ollama_model_name": Config.OLLAMA_MODEL_NAME,
            }
            return jsonify(settings_data)
        except Exception as e:
            logger.error(f"Error getting settings: {str(e)}")
            return jsonify({"error": "Failed to retrieve settings"}), 500

    @admin_bp.route('/settings', methods=['PUT'])
    def update_settings():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        env_file_path = '.env'
        try:
            updated_keys = []

            for key, value in data.items():
                env_key = key.upper() 
                if hasattr(Config, env_key): 
                   set_key(env_file_path, env_key, str(value))
                   updated_keys.append(env_key)
                   if hasattr(Config, env_key):
                       try:
                           original_type = type(getattr(Config, env_key))
                           setattr(Config, env_key, original_type(value))
                       except Exception:
                            setattr(Config, env_key, str(value))
                else:
                    logger.warning(f"Attempted to update unknown setting: {key}")

            if not updated_keys:
                 return jsonify({"message": "No valid settings provided for update."}), 400


            return jsonify({
                "success": True,
                "message": f"Settings updated ({', '.join(updated_keys)}). Backend restart may be required for all changes to take effect."
            })

        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
            return jsonify({"error": "Failed to update settings"}), 500


            
    return admin_bp
