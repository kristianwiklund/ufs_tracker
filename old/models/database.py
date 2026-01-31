"""
Database module for UFS Tracker
Handles database connection, initialization, and schema management
"""
import sqlite3
from datetime import datetime

DATABASE_PATH = 'ufs_notices.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all required tables and indexes"""
    conn = get_db()
    c = conn.cursor()
    
    # Notices table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notice_number TEXT,
            title TEXT,
            affected_charts TEXT,
            sjokort_nummer TEXT,
            batsportkort TEXT,
            published_date TEXT,
            area TEXT,
            content TEXT,
            url TEXT,
            scraped_date TEXT,
            notice_type TEXT,
            expiry_date TEXT,
            superseded_by INTEGER,
            is_cancelled BOOLEAN DEFAULT 0
        )
    ''')
    
    # Implementation status table
    c.execute('''
        CREATE TABLE IF NOT EXISTS implementation_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notice_id INTEGER,
            chart_identifier TEXT,
            implemented BOOLEAN DEFAULT 0,
            implemented_date TEXT,
            notes TEXT,
            priority INTEGER DEFAULT 5,
            is_voyage_chart BOOLEAN DEFAULT 0,
            FOREIGN KEY (notice_id) REFERENCES notices(id),
            UNIQUE(notice_id, chart_identifier)
        )
    ''')
    
    # Search history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT,
            search_type TEXT,
            search_date TEXT,
            results_count INTEGER
        )
    ''')
    
    # Chart editions table (new)
    c.execute('''
        CREATE TABLE IF NOT EXISTS chart_editions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_identifier TEXT NOT NULL,
            edition_number TEXT,
            edition_date TEXT,
            corrected_up_to_notice INTEGER,
            last_updated TEXT,
            UNIQUE(chart_identifier)
        )
    ''')
    
    # Create indexes for better performance
    create_indexes(c)
    
    conn.commit()
    conn.close()

def create_indexes(cursor):
    """Create database indexes for improved query performance"""
    indexes = [
        ('idx_notice_number', 'notices', 'notice_number'),
        ('idx_notices_published_date', 'notices', 'published_date'),
        ('idx_notices_scraped_date', 'notices', 'scraped_date'),
        ('idx_notices_type', 'notices', 'notice_type'),
        ('idx_implementation_chart', 'implementation_status', 'chart_identifier'),
        ('idx_implementation_implemented', 'implementation_status', 'implemented'),
        ('idx_implementation_priority', 'implementation_status', 'priority'),
    ]
    
    for index_name, table_name, column_name in indexes:
        try:
            cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})')
        except sqlite3.OperationalError:
            # Index might already exist
            pass

def migrate_add_notice_types():
    """Migration: Add notice type columns to existing database"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if columns already exist
    c.execute("PRAGMA table_info(notices)")
    columns = [col[1] for col in c.fetchall()]
    
    if 'notice_type' not in columns:
        c.execute('ALTER TABLE notices ADD COLUMN notice_type TEXT')
        c.execute('ALTER TABLE notices ADD COLUMN expiry_date TEXT')
        c.execute('ALTER TABLE notices ADD COLUMN superseded_by INTEGER')
        c.execute('ALTER TABLE notices ADD COLUMN is_cancelled BOOLEAN DEFAULT 0')
        
        # Update existing notices with types based on notice_number
        c.execute('''
            UPDATE notices 
            SET notice_type = CASE
                WHEN notice_number LIKE '%T' THEN 'temporary'
                WHEN notice_number LIKE '%P' THEN 'preliminary'
                ELSE 'permanent'
            END
        ''')
    
    # Check implementation_status columns
    c.execute("PRAGMA table_info(implementation_status)")
    columns = [col[1] for col in c.fetchall()]
    
    if 'priority' not in columns:
        c.execute('ALTER TABLE implementation_status ADD COLUMN priority INTEGER DEFAULT 5')
        c.execute('ALTER TABLE implementation_status ADD COLUMN is_voyage_chart BOOLEAN DEFAULT 0')
    
    conn.commit()
    conn.close()

def backup_database(backup_path=None):
    """Create a backup of the database"""
    if backup_path is None:
        backup_path = f'ufs_notices_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    import shutil
    shutil.copy2(DATABASE_PATH, backup_path)
    return backup_path
