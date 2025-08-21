import sqlite3

class DatabaseModels:
    def __init__(self, db_path="support_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with RAG + RAT support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                product_name TEXT,
                amount INTEGER,
                status TEXT,
                payment_method TEXT,
                delivery_date TEXT,
                user_location TEXT
            )
        """)
        
        # Conversations with RAG + RAT context
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                message TEXT,
                sender TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                language TEXT,
                rag_rat_context TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized with RAG + RAT support")
