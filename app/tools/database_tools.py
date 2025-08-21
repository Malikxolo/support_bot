import sqlite3
import uuid
import os
from datetime import datetime

class DatabaseTools:
    def __init__(self):
        self.db_path = "support_bot.db"
        self.init_tables()
    
    def init_tables(self):
        """Initialize required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Photos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_photos (
                photo_id TEXT PRIMARY KEY,
                ticket_id TEXT,
                file_path TEXT,
                original_filename TEXT,
                upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                analysis_result TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_uploaded_photo(self, uploaded_file, ticket_id):
        """Save uploaded photo"""
        try:
            upload_dir = "app/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            photo_id = str(uuid.uuid4())
            file_extension = uploaded_file.name.split('.')[-1]
            file_path = os.path.join(upload_dir, f"{photo_id}.{file_extension}")
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO support_photos (photo_id, ticket_id, file_path, original_filename)
                VALUES (?, ?, ?, ?)
            """, (photo_id, ticket_id, file_path, uploaded_file.name))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "photo_id": photo_id,
                "file_path": file_path
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return request_id
