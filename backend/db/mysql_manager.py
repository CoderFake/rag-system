import mysql.connector
from mysql.connector import pooling
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class MySQLManager:
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            from config.settings import Config
            self.config = {
                'host': Config.MYSQL_HOST,
                'port': Config.MYSQL_PORT,
                'user': Config.MYSQL_USER,
                'password': Config.MYSQL_PASSWORD,
                'database': Config.MYSQL_DATABASE
            }
        else:
            self.config = config
            
        self._create_connection_pool()
        
    def _create_connection_pool(self, pool_size: int = 5):
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="rag_pool",
                pool_size=pool_size,
                **self.config
            )
            logger.info("MySQL connection pool created successfully")
        except Exception as e:
            logger.error(f"Error creating MySQL connection pool: {str(e)}")
            raise
    
    def get_connection(self):
        return self.connection_pool.get_connection()
    
    def execute_query(self, query: str, params: Optional[Union[Dict, List, Tuple]] = None, fetch: bool = False):
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return cursor.rowcount
                
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error executing query: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()

    def setup_database(self):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logger.info(f"Connected to MySQL version: {version}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if not tables:
                logger.warning("No tables found in database. Tables should be created by initialization scripts.")
            else:
                logger.info(f"Found {len(tables)} tables in database.")
                
            connection.close()
            return True
        except Exception as e:
            logger.error(f"Error checking database: {str(e)}")
            raise

    def create_user(self, username: str, password: str, name: str = "", email: str = "", role: str = "user") -> int:
        check_query = "SELECT id FROM users WHERE username = %s"
        existing = self.execute_query(check_query, (username,), fetch=True)
        
        if existing:
            raise ValueError(f"Tên đăng nhập '{username}' đã tồn tại")
            
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        insert_query = """
        INSERT INTO users (username, password, name, email, role)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        self.execute_query(insert_query, (username, hashed_password, name, email, role))
        

        user = self.execute_query("SELECT id FROM users WHERE username = %s", (username,), fetch=True)
        return user[0]['id'] if user else 0
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        result = self.execute_query(query, (username, hashed_password), fetch=True)
        
        if result and len(result) > 0:
            return result[0]
        else:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE id = %s"
        result = self.execute_query(query, (user_id,), fetch=True)
        
        if result and len(result) > 0:
            return result[0]
        else:
            return None
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> bool:
        valid_fields = {'name', 'email', 'role'}
        updates = []
        params = []
        

        if 'password' in data:
            data['password'] = hashlib.sha256(data['password'].encode()).hexdigest()
            updates.append("password = %s")
            params.append(data['password'])
        

        for field in valid_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])
        
        if not updates:
            return False
            

        params.append(user_id)
        

        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        
        rows_affected = self.execute_query(query, params)
        return rows_affected > 0
    
    def delete_user(self, user_id: int) -> bool:
        query = "DELETE FROM users WHERE id = %s"
        rows_affected = self.execute_query(query, (user_id,))
        return rows_affected > 0
        

    def save_document(self, document) -> str:
        from models.document import Document
        
        if not isinstance(document, Document):
            raise TypeError("document phải là một đối tượng Document")
            

        doc_exists = self.execute_query(
            "SELECT id FROM documents WHERE id = %s", 
            (document.id,), 
            fetch=True
        )
        
        if doc_exists:

            query = """
            UPDATE documents 
            SET title = %s, file_path = %s, file_type = %s, category = %s, 
                user_id = %s, updated_at = %s
            WHERE id = %s
            """
            
            self.execute_query(
                query, 
                (
                    document.title, 
                    document.file_path, 
                    document.file_type, 
                    document.category,
                    document.user_id,
                    datetime.now(),
                    document.id
                )
            )
            

            self.execute_query(
                "DELETE FROM document_tags WHERE document_id = %s",
                (document.id,)
            )
        else:

            query = """
            INSERT INTO documents 
            (id, title, file_path, file_type, category, user_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            now = datetime.now()
            
            self.execute_query(
                query, 
                (
                    document.id, 
                    document.title, 
                    document.file_path, 
                    document.file_type, 
                    document.category,
                    document.user_id,
                    now,
                    now
                )
            )
        

        if document.tags:
            tag_query = "INSERT INTO document_tags (document_id, tag) VALUES (%s, %s)"
            
            for tag in document.tags:
                self.execute_query(tag_query, (document.id, tag))
        
        return document.id
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:

        doc_query = "SELECT * FROM documents WHERE id = %s"
        doc_result = self.execute_query(doc_query, (document_id,), fetch=True)
        
        if not doc_result:
            return None
            
        document = doc_result[0]
        

        tag_query = "SELECT tag FROM document_tags WHERE document_id = %s"
        tag_result = self.execute_query(tag_query, (document_id,), fetch=True)
        
        tags = [item['tag'] for item in tag_result]
        document['tags'] = tags
        
        return document
    
    def get_all_documents(self, page: int = 1, limit: int = 10, category: Optional[str] = None) -> List[Dict[str, Any]]:
        offset = (page - 1) * limit
        params = []
        
        query = """
        SELECT d.*, GROUP_CONCAT(dt.tag) as tags_concat
        FROM documents d
        LEFT JOIN document_tags dt ON d.id = dt.document_id
        """
        
        if category:
            query += " WHERE d.category = %s"
            params.append(category)
            
        query += " GROUP BY d.id ORDER BY d.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = self.execute_query(query, params, fetch=True)
        

        for doc in results:
            tags_concat = doc.get('tags_concat')
            if tags_concat:
                doc['tags'] = tags_concat.split(',')
            else:
                doc['tags'] = []
                
            doc.pop('tags_concat', None)
            
        return results
    
    def delete_document(self, document_id: str) -> bool:
        query = "DELETE FROM documents WHERE id = %s"
        rows_affected = self.execute_query(query, (document_id,))
        return rows_affected > 0
    

    def save_query(self, query) -> str:
        from models.query import Query
        
        if not isinstance(query, Query):
            raise TypeError("query phải là một đối tượng Query")
            
        insert_query = """
        INSERT INTO queries 
        (id, text, user_id, session_id, language, query_type, enhanced_text, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        created_at = datetime.now()
        if isinstance(query.created_at, str):
            try:
                created_at = datetime.fromisoformat(query.created_at)
            except:
                pass
        
        self.execute_query(
            insert_query, 
            (
                query.id, 
                query.text, 
                query.user_id, 
                query.session_id, 
                query.language, 
                query.query_type,
                query.enhanced_text,
                created_at
            )
        )
        
        return query.id
    
    def save_response(self, response) -> str:
        from models.response import Response
        
        if not isinstance(response, Response):
            raise TypeError("response phải là một đối tượng Response")
            

        insert_query = """
        INSERT INTO responses 
        (id, query_id, text, query_text, response_type, session_id, user_id, language, processing_time, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        created_at = datetime.now()
        if isinstance(response.created_at, str):
            try:
                created_at = datetime.fromisoformat(response.created_at)
            except:
                pass
        
        self.execute_query(
            insert_query, 
            (
                response.id, 
                response.query_id, 
                response.text, 
                response.query_text, 
                response.response_type, 
                response.session_id, 
                response.user_id, 
                response.language,
                response.processing_time,
                created_at
            )
        )
        

        if response.source_documents:
            source_query = """
            INSERT INTO response_sources 
            (response_id, document_id, relevance_score)
            VALUES (%s, %s, %s)
            """
            
            for source in response.source_documents:
                doc_id = source.get('id')
                relevance = source.get('relevance_score', 0.0)
                
                if doc_id:
                    self.execute_query(source_query, (response.id, doc_id, relevance))
        
        return response.id
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        query = """
        (SELECT 'query' as type, q.id, q.text as content, q.created_at, NULL as query_id, q.user_id
         FROM queries q 
         WHERE q.session_id = %s)
        UNION
        (SELECT 'response' as type, r.id, r.text as content, r.created_at, r.query_id, r.user_id
         FROM responses r 
         WHERE r.session_id = %s)
        ORDER BY created_at ASC
        LIMIT %s
        """
        
        results = self.execute_query(query, (session_id, session_id, limit), fetch=True)
        

        for item in results:
            if item['type'] == 'response':
                sources_query = """
                SELECT d.id, d.title, d.category, rs.relevance_score
                FROM response_sources rs
                JOIN documents d ON rs.document_id = d.id
                WHERE rs.response_id = %s
                """
                
                sources = self.execute_query(sources_query, (item['id'],), fetch=True)
                item['sources'] = sources
                
        return results
    
    def add_feedback(self, response_id: str, user_id: Optional[int], feedback_type: str, value: str) -> int:
        query = """
        INSERT INTO feedback
        (response_id, user_id, feedback_type, value, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        self.execute_query(query, (response_id, user_id, feedback_type, value, datetime.now()))
        

        get_id_query = "SELECT LAST_INSERT_ID() as id"
        result = self.execute_query(get_id_query, fetch=True)
        
        return result[0]['id'] if result else 0