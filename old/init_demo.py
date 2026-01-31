#!/usr/bin/env python3
"""
Demo script to initialize and verify the database structure
"""

import sqlite3
from datetime import datetime

def init_demo_database():
    """Initialize database with demo data"""
    
    # Create database
    conn = sqlite3.connect('ufs_notices.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notice_number TEXT,
            title TEXT,
            sjokort_nummer TEXT,
            batsportkort TEXT,
            published_date TEXT,
            area TEXT,
            content TEXT,
            url TEXT,
            scraped_date TEXT,
            UNIQUE(notice_number, sjokort_nummer, batsportkort)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS implementation_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notice_id INTEGER,
            implemented BOOLEAN DEFAULT 0,
            implemented_date TEXT,
            notes TEXT,
            FOREIGN KEY (notice_id) REFERENCES notices(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT,
            search_type TEXT,
            search_date TEXT,
            results_count INTEGER
        )
    ''')
    
    # Insert some demo data
    demo_notices = [
        {
            'notice_number': 'T123/24',
            'title': 'Byte av sjömärke vid Stockholms inlopp',
            'sjokort_nummer': '61',
            'batsportkort': 'Bsp Stockholm N 2024',
            'published_date': '2024-11-15',
            'area': 'Stockholm',
            'content': 'Sjömärket vid position 59°20.5N 018°05.2E har bytts ut. Nytt ljuskarakteristik: Fl(3)G 10s',
            'url': 'https://ufs.sjofartsverket.se/notice/details/T123/24',
            'scraped_date': datetime.now().isoformat()
        },
        {
            'notice_number': 'P456/24',
            'title': 'Ny fyr installerad vid Vaxholm',
            'sjokort_nummer': '61',
            'batsportkort': '',
            'published_date': '2024-12-01',
            'area': 'Stockholm',
            'content': 'En ny fyr har installerats vid position 59°24.3N 018°21.1E. Ljuskarakteristik: FlY 5s',
            'url': 'https://ufs.sjofartsverket.se/notice/details/P456/24',
            'scraped_date': datetime.now().isoformat()
        },
        {
            'notice_number': 'T789/24',
            'title': 'Upphävd varning för sjöfart - Göteborg',
            'sjokort_nummer': '933',
            'batsportkort': 'BSP Västkusten N 2025',
            'published_date': '2024-10-20',
            'area': 'Göteborg',
            'content': 'Den tidigare utfärdade varningen för grunt vatten vid position 57°42.1N 011°58.3E är upphävd.',
            'url': 'https://ufs.sjofartsverket.se/notice/details/T789/24',
            'scraped_date': datetime.now().isoformat()
        }
    ]
    
    for notice in demo_notices:
        c.execute('''
            INSERT OR IGNORE INTO notices 
            (notice_number, title, sjokort_nummer, batsportkort, published_date, 
             area, content, url, scraped_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            notice['notice_number'],
            notice['title'],
            notice['sjokort_nummer'],
            notice['batsportkort'],
            notice['published_date'],
            notice['area'],
            notice['content'],
            notice['url'],
            notice['scraped_date']
        ))
        
        notice_id = c.lastrowid
        
        # Add implementation status
        if notice_id:
            # First notice is implemented
            implemented = 1 if notice['notice_number'] == 'T123/24' else 0
            impl_date = datetime.now().isoformat() if implemented else None
            notes = 'Ändringen är inritad på papperkortet' if implemented else ''
            
            c.execute('''
                INSERT INTO implementation_status (notice_id, implemented, implemented_date, notes)
                VALUES (?, ?, ?, ?)
            ''', (notice_id, implemented, impl_date, notes))
    
    # Add demo search history
    c.execute('''
        INSERT INTO search_history (search_term, search_type, search_date, results_count)
        VALUES (?, ?, ?, ?)
    ''', ('61', 'sjokort', datetime.now().isoformat(), 2))
    
    c.execute('''
        INSERT INTO search_history (search_term, search_type, search_date, results_count)
        VALUES (?, ?, ?, ?)
    ''', ('BSP Västkusten N 2025', 'batsportkort', datetime.now().isoformat(), 1))
    
    conn.commit()
    
    # Verify data
    print("\n" + "="*60)
    print("DATABASE INITIALIZED SUCCESSFULLY")
    print("="*60)
    
    c.execute('SELECT COUNT(*) FROM notices')
    notice_count = c.fetchone()[0]
    print(f"\n✓ Total notices: {notice_count}")
    
    c.execute('SELECT COUNT(*) FROM implementation_status WHERE implemented = 1')
    impl_count = c.fetchone()[0]
    print(f"✓ Implemented: {impl_count}")
    print(f"✓ Pending: {notice_count - impl_count}")
    
    print("\n" + "-"*60)
    print("DEMO NOTICES:")
    print("-"*60)
    
    c.execute('''
        SELECT n.notice_number, n.title, n.sjokort_nummer, i.implemented
        FROM notices n
        LEFT JOIN implementation_status i ON n.id = i.notice_id
    ''')
    
    for row in c.fetchall():
        status = "✓ Implemented" if row[3] else "○ Pending"
        print(f"\n{row[0]}: {row[1]}")
        print(f"  Sjökort: {row[2]}")
        print(f"  Status: {status}")
    
    print("\n" + "="*60)
    print("Ready to use! Start the app with: python app.py")
    print("="*60 + "\n")
    
    conn.close()

if __name__ == '__main__':
    init_demo_database()
