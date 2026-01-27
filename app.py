#!/usr/bin/env python3
"""
UFS Maritime Notices Tracker
A standalone web application to scrape and track implementation of maritime notices
from Swedish Maritime Administration
"""

import sqlite3
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)
app.config['DATABASE'] = 'ufs_notices.db'

# Database initialization
def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(app.config['DATABASE'])
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
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def scrape_ufs_notices(sjokort_nummer=None, batsportkort=None, days_back=30):
    """
    Scrape notices from UFS website
    Returns a list of notice dictionaries
    """
    base_url = "https://ufs.sjofartsverket.se/notice/search/"
    
    # Prepare form data
    form_data = {}
    
    if sjokort_nummer:
        form_data['Sjokort'] = sjokort_nummer
    
    if batsportkort:
        form_data['Batsportkort'] = batsportkort
    
    # Set time period (last 30 days by default)
    form_data['PublicationTime'] = '6'  # Last quarter
    
    try:
        # First request to get the form
        session = requests.Session()
        response = session.get(base_url, timeout=10)
        
        if response.status_code != 200:
            return {'error': f'Failed to access website: {response.status_code}'}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract form token if present
        form = soup.find('form')
        if form:
            token_input = form.find('input', {'name': '__RequestVerificationToken'})
            if token_input:
                form_data['__RequestVerificationToken'] = token_input.get('value')
        
        # Submit search
        #print(base_url,form_data)
        search_response = session.post(base_url, data=form_data, timeout=10)
        
        if search_response.status_code != 200:
            return {'error': f'Search failed: {search_response.status_code}'}
        
        # Parse results
        results_soup = BeautifulSoup(search_response.text, 'html.parser')
        
        notices = []
        
        # Find the results table
        table = results_soup.find('table', {'class': 'table'}) or results_soup.find('table')
        
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    notice = {
                        'notice_number': cells[0].get_text(strip=True),
                        'title': cells[1].get_text(strip=True),
                        'published_date': cells[2].get_text(strip=True),
                        'sjokort_nummer': sjokort_nummer or '',
                        'batsportkort': batsportkort or '',
                        'area': '',
                        'content': '',
                        'url': ''
                    }
                    
                    # Try to get detail link
                    link = cells[1].find('a')
                    if link and link.get('href'):
                        detail_url = link.get('href')
                        if not detail_url.startswith('http'):
                            detail_url = 'https://ufs.sjofartsverket.se' + detail_url
                        notice['url'] = detail_url
                        
                        # Fetch detail page for full content
                        try:
                            detail_response = session.get(detail_url, timeout=10)
                            if detail_response.status_code == 200:
                                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                                content_div = detail_soup.find('div', {'class': 'notice-content'}) or detail_soup.find('div', {'class': 'content'})
                                if content_div:
                                    notice['content'] = content_div.get_text(strip=True)
                        except:
                            pass
                    
                    notices.append(notice)
        
        return notices
    
    except requests.RequestException as e:
        return {'error': f'Network error: {str(e)}'}
    except Exception as e:
        return {'error': f'Scraping error: {str(e)}'}

def save_notices_to_db(notices):
    """Save scraped notices to database"""
    conn = get_db()
    c = conn.cursor()
    
    saved_count = 0
    scraped_date = datetime.now().isoformat()
    
    for notice in notices:
        try:
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
                notice.get('area', ''),
                notice.get('content', ''),
                notice.get('url', ''),
                scraped_date
            ))
            
            if c.rowcount > 0:
                # Create implementation status entry
                notice_id = c.lastrowid
                c.execute('''
                    INSERT INTO implementation_status (notice_id, implemented)
                    VALUES (?, 0)
                ''', (notice_id,))
                saved_count += 1
        except Exception as e:
            print(f"Error saving notice: {e}")
    
    conn.commit()
    conn.close()
    
    return saved_count

# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle search request"""
    sjokort = request.form.get('sjokort_nummer', '').strip()
    batsportkort = request.form.get('batsportkort', '').strip()
    
    if not sjokort and not batsportkort:
        return jsonify({'error': 'Please specify either sjökortnummer or båtsportkort'})
    
    # Scrape notices
    notices = scrape_ufs_notices(sjokort_nummer=sjokort, batsportkort=batsportkort)
    
    if isinstance(notices, dict) and 'error' in notices:
        return jsonify(notices)
    
    # Save to database
    saved_count = save_notices_to_db(notices)
    
    # Save search history
    conn = get_db()
    c = conn.cursor()
    search_term = sjokort or batsportkort
    search_type = 'sjokort' if sjokort else 'batsportkort'
    c.execute('''
        INSERT INTO search_history (search_term, search_type, search_date, results_count)
        VALUES (?, ?, ?, ?)
    ''', (search_term, search_type, datetime.now().isoformat(), len(notices)))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'total_found': len(notices),
        'saved': saved_count,
        'message': f'Found {len(notices)} notices, saved {saved_count} new ones'
    })

@app.route('/notices')
def list_notices():
    """List all notices with implementation status"""
    conn = get_db()
    c = conn.cursor()
    
    # Get filter parameters
    sjokort = request.args.get('sjokort', '')
    batsportkort = request.args.get('batsportkort', '')
    show_implemented = request.args.get('show_implemented', '1')
    
    query = '''
        SELECT n.id, n.notice_number, n.title, n.sjokort_nummer, n.batsportkort,
               n.published_date, n.content, n.url, n.scraped_date,
               i.implemented, i.implemented_date, i.notes
        FROM notices n
        LEFT JOIN implementation_status i ON n.id = i.notice_id
        WHERE 1=1
    '''
    params = []
    
    if sjokort:
        query += ' AND n.sjokort_nummer = ?'
        params.append(sjokort)
    
    if batsportkort:
        query += ' AND n.batsportkort = ?'
        params.append(batsportkort)
    
    if show_implemented == '0':
        query += ' AND (i.implemented = 0 OR i.implemented IS NULL)'
    
    query += ' ORDER BY n.published_date DESC'
    
    c.execute(query, params)
    notices = c.fetchall()
    
    conn.close()
    
    return render_template('notices.html', notices=notices, 
                         sjokort=sjokort, batsportkort=batsportkort,
                         show_implemented=show_implemented)

@app.route('/update_status/<int:notice_id>', methods=['POST'])
def update_status(notice_id):
    """Update implementation status of a notice"""
    data = request.get_json()
    implemented = data.get('implemented', False)
    notes = data.get('notes', '')
    
    conn = get_db()
    c = conn.cursor()
    
    implemented_date = datetime.now().isoformat() if implemented else None
    
    # Check if status entry exists
    c.execute('SELECT id FROM implementation_status WHERE notice_id = ?', (notice_id,))
    status = c.fetchone()
    
    if status:
        c.execute('''
            UPDATE implementation_status 
            SET implemented = ?, implemented_date = ?, notes = ?
            WHERE notice_id = ?
        ''', (implemented, implemented_date, notes, notice_id))
    else:
        c.execute('''
            INSERT INTO implementation_status (notice_id, implemented, implemented_date, notes)
            VALUES (?, ?, ?, ?)
        ''', (notice_id, implemented, implemented_date, notes))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/statistics')
def statistics():
    """Show statistics and search history"""
    conn = get_db()
    c = conn.cursor()
    
    # Total notices
    c.execute('SELECT COUNT(*) FROM notices')
    total_notices = c.fetchone()[0]
    
    # Implemented notices
    c.execute('SELECT COUNT(*) FROM implementation_status WHERE implemented = 1')
    implemented = c.fetchone()[0]
    
    # By sjökort
    c.execute('''
        SELECT sjokort_nummer, COUNT(*) as count
        FROM notices
        WHERE sjokort_nummer != ''
        GROUP BY sjokort_nummer
        ORDER BY count DESC
    ''')
    by_sjokort = c.fetchall()
    
    # By båtsportkort
    c.execute('''
        SELECT batsportkort, COUNT(*) as count
        FROM notices
        WHERE batsportkort != ''
        GROUP BY batsportkort
        ORDER BY count DESC
    ''')
    by_batsportkort = c.fetchall()
    
    # Recent searches
    c.execute('''
        SELECT search_term, search_type, search_date, results_count
        FROM search_history
        ORDER BY search_date DESC
        LIMIT 10
    ''')
    recent_searches = c.fetchall()
    
    conn.close()
    
    return render_template('statistics.html',
                         total_notices=total_notices,
                         implemented=implemented,
                         by_sjokort=by_sjokort,
                         by_batsportkort=by_batsportkort,
                         recent_searches=recent_searches)

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the app
    print("=" * 60)
    print("UFS Maritime Notices Tracker")
    print("=" * 60)
    print("Starting server on http://127.0.0.1:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=7997)
