from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
import logging


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
            
    return admin_bp