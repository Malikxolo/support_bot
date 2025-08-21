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
        
        # Admin requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_requests (
                request_id TEXT PRIMARY KEY,
                ticket_id TEXT,
                order_id TEXT,
                issue_summary TEXT,
                policy_status TEXT,
                photo_evidence TEXT,
                chat_summary TEXT,
                rag_rat_decision TEXT,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Support tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                ticket_id TEXT PRIMARY KEY,
                order_id TEXT,
                issue_type TEXT,
                status TEXT DEFAULT 'open',
                priority TEXT DEFAULT 'medium',
                rag_rat_reasoning TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
    
    def create_admin_request_with_rag_rat(self, ticket_id, order_id, issue_summary, rag_rat_decision, photo_evidence, chat_summary):
        """Create admin request with RAG + RAT reasoning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        request_id = f"ADM{str(uuid.uuid4())[:6].upper()}"
        
        cursor.execute("""
            INSERT INTO admin_requests (
                request_id, ticket_id, order_id, issue_summary, 
                policy_status, photo_evidence, chat_summary, rag_rat_decision
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (request_id, ticket_id, order_id, issue_summary, 
              rag_rat_decision.get("recommendation", "unknown"), 
              photo_evidence, chat_summary, 
              str(rag_rat_decision)))
        
        conn.commit()
        conn.close()
        
        return request_id
