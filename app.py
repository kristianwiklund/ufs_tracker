#!/usr/bin/env python3
"""
UFS Maritime Notices Tracker
A standalone web application to scrape and track implementation of maritime notices
from Swedish Maritime Administration
"""

import sqlite3
import requests
import re
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
            affected_charts TEXT,
            sjokort_nummer TEXT,
            batsportkort TEXT,
            published_date TEXT,
            area TEXT,
            content TEXT,
            url TEXT,
            scraped_date TEXT,
            UNIQUE(notice_number)
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
    
    # Migration: Add affected_charts column if it doesn't exist
    try:
        c.execute("ALTER TABLE notices ADD COLUMN affected_charts TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_batsportkort_id(chart_name):
    """
    Map båtsportkort chart names to their IDs used in the UFS search.
    The IDs are used in the URL parameter SearchFormModel.SmallCraftChart
    
    Common chart mappings:
    - Bsp Stockholm N 2024 -> 5231
    - Bsp Stockholm M 2024 -> (need to find ID)
    - etc.
    
    If the input is already a number, return it as-is.
    Otherwise, try to extract or look up the ID.
    """
    # If it's already a number, return it
    if chart_name.isdigit():
        return chart_name
    
    # TODO: Build a complete mapping of chart names to IDs
    # For now, this is a placeholder that users can expand
    chart_id_map = {
        'Bsp Stockholm N 2024': '5231',
        'Bsp Stockholm M 2024': '5230',  # Example, needs verification
    }
    
    # Try exact match first
    if chart_name in chart_id_map:
        return chart_id_map[chart_name]
    
    # Try case-insensitive match
    for name, chart_id in chart_id_map.items():
        if name.lower() == chart_name.lower():
            return chart_id
    
    # If no match found, return the input as-is
    # (user might be entering the ID directly)
    return chart_name

def scrape_ufs_notices(sjokort_nummer=None, batsportkort=None, days_back=30):
    """
    Scrape notices from UFS website
    Returns a list of notice dictionaries
    """
    base_url = "https://ufs.sjofartsverket.se/Notice/Search/"
    
    # Prepare query parameters (URL parameters, not form data)
    params = {}
    
    if batsportkort:
        # For båtsportkort, convert name to ID if needed
        chart_id = get_batsportkort_id(batsportkort)
        params['SearchFormModel.SmallCraftChart'] = chart_id
    
    if sjokort_nummer:
        # For sjökort (nautical charts)
        params['SearchFormModel.Chart'] = sjokort_nummer
    
    # Set time period
    # 0 = All time, 1 = Last week, 2 = Last month, etc.
    params['SearchFormModel.SearchTimePeriod'] = '0'  # All time
    
    try:
        # Make GET request with query parameters
        session = requests.Session()
        response = session.get(base_url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {'error': f'Failed to access website: {response.status_code}'}
        
        # Parse results
        soup = BeautifulSoup(response.text, 'html.parser')
        
        notices = []
        
        # Find the specific table for "Notiser för gällande sjökort"
        # Look for a heading or caption that identifies this table
        table = None
        
        # Try to find by heading
        heading = soup.find(['h2', 'h3', 'h4'], string=re.compile(r'Notiser för gällande sjökort', re.IGNORECASE))
        if heading:
            # Find the next table after this heading
            table = heading.find_next('table')
        
        # If not found by heading, try to find by table caption
        if not table:
            captions = soup.find_all('caption')
            for caption in captions:
                if re.search(r'Notiser för gällande sjökort', caption.get_text(), re.IGNORECASE):
                    table = caption.find_parent('table')
                    break
        
        # If still not found, try finding the table by id or class that might indicate it's the main results
        if not table:
            table = soup.find('table', {'id': re.compile(r'notice|result', re.IGNORECASE)})
        
        # Last resort: find first table with class 'table'
        if not table:
            table = soup.find('table', {'class': 'table'})
        
        if not table:
            # No table found - might be a different page structure or no results
            # Check if there's a "no results" message
            no_results = soup.find(string=re.compile(r'(inga|no).*(resultat|results)', re.IGNORECASE))
            if no_results:
                return []  # Return empty list, not an error
            
            # Return error with some debugging info
            return {'error': 'Could not find results table on page. The page structure may have changed.', 
                    'html_sample': str(soup)[:500]}
        
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            
            print(f"Found table with {len(rows)} rows")
            
            for idx, row in enumerate(rows):
                cells = row.find_all('td')
                print(f"Row {idx}: {len(cells)} cells")
                
                if len(cells) >= 3:  # Need at least 3 cells: affected charts, title, date
                    # Extract basic information
                    affected_charts = cells[0].get_text(strip=True) if len(cells) > 0 else ''
                    title = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                    published_date = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                    
                    print(f"  Affected charts: {affected_charts[:50]}...")
                    print(f"  Title: {title[:50]}...")
                    print(f"  Date: {published_date}")
                    
                    # Try to extract notice number from the detail link
                    notice_number = None
                    detail_url = None
                    
                    # Look for a link in the title cell (usually the second cell)
                    link = cells[1].find('a') if len(cells) > 1 else None
                    if link and link.get('href'):
                        href = link.get('href')
                        print(f"  Found link: {href}")
                        # Try to extract notice number from various URL patterns
                        if 'notice=' in href:
                            try:
                                notice_number = href.split('notice=')[1].split('&')[0]
                                print(f"  Extracted notice number from param: {notice_number}")
                            except:
                                pass
                        elif 'NoticeDetails/' in href:
                            try:
                                # Handle pattern like /Current/NoticeDetails/19697
                                notice_number = href.split('NoticeDetails/')[1].split('/')[0].split('?')[0]
                                print(f"  Extracted notice number from path: {notice_number}")
                            except:
                                pass
                        
                        # Construct full URL
                        if notice_number:
                            detail_url = f'https://ufs.sjofartsverket.se/Current/NoticeDetails?notice={notice_number}&from=search'
                        elif not href.startswith('http'):
                            detail_url = 'https://ufs.sjofartsverket.se' + href
                        else:
                            detail_url = href
                    else:
                        print(f"  No link found in title cell")
                    
                    # If we still don't have a notice number, try to extract it from other cells
                    if not notice_number:
                        # Sometimes the notice number might be in the text somewhere
                        for cell_idx, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            # Look for patterns like "19697" or "UfS 19697"
                            match = re.search(r'UfS?\s*(\d{4,6})', text, re.IGNORECASE)
                            if not match:
                                match = re.search(r'\b(\d{4,6})\b', text)
                            if match:
                                notice_number = match.group(1)
                                detail_url = f'https://ufs.sjofartsverket.se/Current/NoticeDetails?notice={notice_number}&from=search'
                                print(f"  Extracted notice number from cell {cell_idx} text: {notice_number}")
                                break
                    
                    if not notice_number:
                        print(f"  WARNING: Could not extract notice number for row {idx}")
                    
                    notice = {
                        'notice_number': notice_number or '',
                        'affected_charts': affected_charts,
                        'title': title,
                        'published_date': published_date,
                        'sjokort_nummer': sjokort_nummer or '',
                        'batsportkort': batsportkort or '',
                        'area': '',
                        'content': '',
                        'url': detail_url or ''
                    }
                    
                    # Fetch detail page for full content
                    if detail_url:
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
                    print(f"  Added notice to list (total so far: {len(notices)})")
                else:
                    print(f"Row {idx}: Skipped - only {len(cells)} cells")
        
        # Log what we found for debugging
        print(f"Scraped {len(notices)} notices from UFS")
        if notices:
            print(f"Sample notice: {notices[0]}")
        
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
    updated_count = 0
    skipped_count = 0
    scraped_date = datetime.now().isoformat()
    
    print(f"\n=== Starting to save {len(notices)} notices to database ===")
    
    for idx, notice in enumerate(notices):
        try:
            print(f"\nProcessing notice {idx + 1}/{len(notices)}: {notice.get('notice_number', 'NO NUMBER')} - {notice.get('title', '')[:50]}...")
            
            # Check if notice already exists
            c.execute('SELECT id FROM notices WHERE notice_number = ? AND notice_number != ""', 
                     (notice['notice_number'],))
            existing = c.fetchone()
            
            if existing and notice['notice_number']:
                print(f"  Notice exists (id={existing['id']}), updating...")
                # Update existing notice
                c.execute('''
                    UPDATE notices 
                    SET title = ?, affected_charts = ?, published_date = ?, 
                        content = ?, url = ?, scraped_date = ?
                    WHERE id = ?
                ''', (
                    notice['title'],
                    notice.get('affected_charts', ''),
                    notice['published_date'],
                    notice.get('content', ''),
                    notice.get('url', ''),
                    scraped_date,
                    existing['id']
                ))
                updated_count += 1
                print(f"  ✓ Updated")
            else:
                print(f"  New notice, inserting...")
                # Insert new notice
                c.execute('''
                    INSERT INTO notices 
                    (notice_number, title, affected_charts, sjokort_nummer, batsportkort, published_date, 
                     area, content, url, scraped_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    notice['notice_number'],
                    notice['title'],
                    notice.get('affected_charts', ''),
                    notice['sjokort_nummer'],
                    notice['batsportkort'],
                    notice['published_date'],
                    notice.get('area', ''),
                    notice.get('content', ''),
                    notice.get('url', ''),
                    scraped_date
                ))
                
                if c.rowcount > 0:
                    # Create implementation status entry for new notice
                    notice_id = c.lastrowid
                    c.execute('''
                        INSERT INTO implementation_status (notice_id, implemented)
                        VALUES (?, 0)
                    ''', (notice_id,))
                    saved_count += 1
                    print(f"  ✓ Inserted (id={notice_id})")
                else:
                    skipped_count += 1
                    print(f"  ✗ Insert returned 0 rows affected")
        except Exception as e:
            print(f"  ✗ Error saving notice: {e}")
            print(f"  Notice data: {notice}")
            skipped_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n=== Database save complete ===")
    print(f"Saved {saved_count} new notices")
    print(f"Updated {updated_count} existing notices")
    print(f"Skipped {skipped_count} notices due to errors")
    print(f"Total processed: {saved_count + updated_count + skipped_count}/{len(notices)}")
    
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
        SELECT n.id, n.notice_number, n.title, n.affected_charts, n.sjokort_nummer, n.batsportkort,
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
    print("Starting server on http://0.0.0.0:5000")
    print("Access from this machine: http://127.0.0.1:5000")
    print("Access from network: http://<your-ip>:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
