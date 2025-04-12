import os
import tempfile
import uuid
import logging
from typing import Optional, Tuple, IO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

def save_temporary_file(file: FileStorage) -> Tuple[str, str]:
    filename = secure_filename(file.filename or "")
    extension = os.path.splitext(filename)[1].lower()
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
    file.save(temp_file.name)
    
    return temp_file.name, extension
    
def save_uploaded_file(file: FileStorage, upload_folder: str) -> Tuple[str, str]:
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
        
    original_filename = secure_filename(file.filename or "")
    extension = os.path.splitext(original_filename)[1].lower()
    
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    file.save(file_path)
    
    return file_path, extension

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def get_mime_type(extension: str) -> str:
    mime_types = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif'
    }
    
    return mime_types.get(extension, 'application/octet-stream')

def cleanup_temporary_file(file_path: str) -> None:
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up temporary file {file_path}: {str(e)}")
        
def get_file_size(file_path: str) -> int:
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0