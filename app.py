#!/usr/bin/env python3
"""
UFS Maritime Notices Tracker
A standalone web application to scrape and track implementation of maritime notices
from Swedish Maritime Administration
"""

import sqlite3
import requests
import re
import argparse
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)
app.config['DATABASE'] = 'ufs_notices.db'

# Global debug flag
DEBUG_MODE = False

def debug_print(*args, **kwargs):
    """Print only if debug mode is enabled"""
    if DEBUG_MODE:
        print(*args, **kwargs)

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
            scraped_date TEXT
        )
    ''')
    
    # Create an index on notice_number for faster lookups (but not unique to allow empty values)
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_notice_number ON notices(notice_number)
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS implementation_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notice_id INTEGER,
            chart_identifier TEXT,
            implemented BOOLEAN DEFAULT 0,
            implemented_date TEXT,
            notes TEXT,
            FOREIGN KEY (notice_id) REFERENCES notices(id),
            UNIQUE(notice_id, chart_identifier)
        )
    ''')
    
    # Migration: Add chart_identifier column if it doesn't exist
    try:
        c.execute("ALTER TABLE implementation_status ADD COLUMN chart_identifier TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
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

def get_chart_mappings():
    """
    Scrape the UFS search page to get the mappings between chart names/numbers and their IDs.
    Returns a tuple of (sjokort_map, batsportkort_map)
    """
    search_url = "https://ufs.sjofartsverket.se/Notice/Search"
    
    try:
        debug_print(f"Fetching chart mappings from {search_url}")
        response = requests.get(search_url, timeout=10)
        
        if response.status_code != 200:
            debug_print(f"Failed to fetch search page: {response.status_code}")
            return {}, {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get sjökort mappings from SearchFormModel_ChartNumbers
        sjokort_map = {}
        sjokort_select = soup.find('select', {'id': 'SearchFormModel_ChartNumbers'})
        if sjokort_select:
            options = sjokort_select.find_all('option')
            for option in options:
                value = option.get('value', '')
                text = option.get_text(strip=True)
                if value and text and value != '':  # Skip empty options
                    sjokort_map[text] = value
            debug_print(f"Found {len(sjokort_map)} sjökort mappings")
        else:
            debug_print("Could not find SearchFormModel_ChartNumbers selector")
        
        # Get båtsportkort mappings from SearchFormModel_SmallCraftChart
        batsportkort_map = {}
        batsportkort_select = soup.find('select', {'id': 'SearchFormModel_SmallCraftChart'})
        if batsportkort_select:
            options = batsportkort_select.find_all('option')
            for option in options:
                value = option.get('value', '')
                text = option.get_text(strip=True)
                if value and text and value != '':  # Skip empty options
                    batsportkort_map[text] = value
            debug_print(f"Found {len(batsportkort_map)} båtsportkort mappings")
        else:
            debug_print("Could not find SearchFormModel_SmallCraftChart selector")
        
        return sjokort_map, batsportkort_map
    
    except Exception as e:
        debug_print(f"Error fetching chart mappings: {e}")
        return {}, {}

def get_batsportkort_id(chart_name, batsportkort_map):
    """
    Map båtsportkort chart name to its ID using the provided mapping.
    
    If the input is already a number, return it as-is.
    Otherwise, look up the ID from the mapping.
    """
    # If it's already a number, return it
    if chart_name.isdigit():
        return chart_name
    
    # Try exact match first
    if chart_name in batsportkort_map:
        debug_print(f"Mapped '{chart_name}' to ID '{batsportkort_map[chart_name]}'")
        return batsportkort_map[chart_name]
    
    # Try case-insensitive match
    for name, chart_id in batsportkort_map.items():
        if name.lower() == chart_name.lower():
            debug_print(f"Mapped '{chart_name}' to ID '{chart_id}' (case-insensitive)")
            return chart_id
    
    # If no match found, return the input as-is
    debug_print(f"No mapping found for '{chart_name}', using as-is")
    return chart_name

def get_sjokort_id(chart_number, sjokort_map):
    """
    Map sjökort chart number to its ID using the provided mapping.
    
    If the input is in the mapping, return the ID.
    Otherwise, return the input as-is.
    """
    # Try exact match
    if chart_number in sjokort_map:
        debug_print(f"Mapped sjökort '{chart_number}' to ID '{sjokort_map[chart_number]}'")
        return sjokort_map[chart_number]
    
    # Try as string if it was provided as number
    chart_str = str(chart_number)
    if chart_str in sjokort_map:
        debug_print(f"Mapped sjökort '{chart_str}' to ID '{sjokort_map[chart_str]}'")
        return sjokort_map[chart_str]
    
    # If no match found, return the input as-is
    debug_print(f"No mapping found for sjökort '{chart_number}', using as-is")
    return chart_number
def scrape_ufs_notices(sjokort_nummer=None, batsportkort=None, days_back=30):
    """
    Scrape notices from UFS website
    Returns a list of notice dictionaries
    """
    base_url = "https://ufs.sjofartsverket.se/Notice/Search/"
    
    # First, get the chart mappings from the search page
    sjokort_map, batsportkort_map = get_chart_mappings()
    
    # Prepare query parameters (URL parameters, not form data)
    params = {}
    
    if batsportkort:
        # For båtsportkort, convert name to ID using the scraped mapping
        chart_id = get_batsportkort_id(batsportkort, batsportkort_map)
        params['SearchFormModel.SmallCraftChart'] = chart_id
    
    if sjokort_nummer:
        # For sjökort (nautical charts), convert to ID using the scraped mapping
        chart_id = get_sjokort_id(sjokort_nummer, sjokort_map)
        params['SearchFormModel.Chart'] = chart_id
    
    # Set time period
    # 0 = All time, 1 = Last week, 2 = Last month, etc.
    params['SearchFormModel.SearchTimePeriod'] = '0'  # All time
    
    try:
        # Make GET request with query parameters
        session = requests.Session()
        
        debug_print(f"Making request to: {base_url}")
        debug_print(f"Parameters: {params}")
        
        response = session.get(base_url, params=params, timeout=10)
        
        debug_print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f'Failed to access website: {response.status_code}'
            # Save response for debugging
            if DEBUG_MODE:
                debug_file = f'/tmp/ufs_error_{response.status_code}.html'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                debug_print(f"Saved error response to {debug_file}")
            return {'error': error_msg, 'status_code': response.status_code}
        
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
            
            # Save the HTML for debugging
            if DEBUG_MODE:
                debug_file = '/tmp/ufs_no_table.html'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                debug_print(f"Saved response with no table to {debug_file}")
            
            # Return error with some debugging info
            return {'error': 'Could not find results table on page. The page structure may have changed.',
                    'params': params}
        
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            
            debug_print(f"Found table with {len(rows)} rows")
            
            for idx, row in enumerate(rows):
                cells = row.find_all('td')
                debug_print(f"\n{'='*60}")
                debug_print(f"Row {idx}: {len(cells)} cells")
                
                # Check for links in the entire row first
                all_links = row.find_all('a')
                debug_print(f"  Found {len(all_links)} link(s) in row")
                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    debug_print(f"    Link: href='{href}' text='{text}'")
                
                # Print all cells to understand the structure
                for cell_idx, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    debug_print(f"  Cell {cell_idx}: '{cell_text}'")
                    link = cell.find('a')
                    if link:
                        debug_print(f"    -> Has link: href={link.get('href', 'no href')} text={link.get_text(strip=True)}")
                
                if len(cells) >= 3:
                    # Extract notice number from link
                    notice_number = None
                    detail_url = None
                    
                    # Look for notice number in any link in the row
                    for link in all_links:
                        href = link.get('href', '')
                        if 'notice=' in href:
                            try:
                                notice_number = href.split('notice=')[1].split('&')[0]
                                detail_url = f'https://ufs.sjofartsverket.se/Current/NoticeDetails?notice={notice_number}&from=search'
                                debug_print(f"  ✓ Extracted notice number from link: {notice_number}")
                                break
                            except:
                                pass
                        elif 'NoticeDetails/' in href:
                            try:
                                notice_number = href.split('NoticeDetails/')[1].split('/')[0].split('?')[0]
                                detail_url = f'https://ufs.sjofartsverket.se/Current/NoticeDetails?notice={notice_number}&from=search'
                                debug_print(f"  ✓ Extracted notice number from link path: {notice_number}")
                                break
                            except:
                                pass
                    
                    # The actual structure based on your example:
                    # Cell 0: affected charts (e.g., "612Bsp Stockholm N 2024/s39")
                    # Cell 1: publication date (e.g., "2026-01-14")
                    # Cell 2: title/description (e.g., "Stockholms skärgård...")
                    # Cell 3: empty or additional info
                    
                    affected_charts = cells[0].get_text(strip=True) if len(cells) > 0 else ''
                    published_date = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                    title = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                    
                    debug_print(f"  Final interpretation:")
                    debug_print(f"    Notice: {notice_number or 'NOT FOUND'}")
                    debug_print(f"    Charts: {affected_charts[:60]}...")
                    debug_print(f"    Date: {published_date}")
                    debug_print(f"    Title: {title[:60]}...")
                    
                    if not notice_number:
                        debug_print(f"  ⚠️ WARNING: Could not extract notice number!")
                    
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
                    debug_print(f"  ✓ Added notice to list (total so far: {len(notices)})")
                else:
                    debug_print(f"Row {idx}: Skipped - only {len(cells)} cells (need at least 3)")
        
        # Log what we found for debugging
        debug_print(f"Scraped {len(notices)} notices from UFS")
        if notices:
            debug_print(f"Sample notice: {notices[0]}")
        
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
    
    debug_print(f"\n=== Starting to save {len(notices)} notices to database ===")
    
    for idx, notice in enumerate(notices):
        try:
            debug_print(f"\nProcessing notice {idx + 1}/{len(notices)}: {notice.get('notice_number', 'NO NUMBER')} - {notice.get('title', '')[:50]}...")
            
            # Check if notice already exists
            existing = None
            if notice['notice_number'] and notice['notice_number'].strip():
                # If we have a notice number, check by that
                c.execute('SELECT id FROM notices WHERE notice_number = ?', 
                         (notice['notice_number'],))
                existing = c.fetchone()
                debug_print(f"  Checking for existing by notice_number={notice['notice_number']}: {'Found' if existing else 'Not found'}")
            else:
                # If no notice number, check by title and published date to avoid true duplicates
                c.execute('''SELECT id FROM notices 
                            WHERE title = ? AND published_date = ? 
                            AND (notice_number = '' OR notice_number IS NULL)
                            LIMIT 1''', 
                         (notice['title'], notice['published_date']))
                existing = c.fetchone()
                debug_print(f"  Checking for existing by title+date: {'Found' if existing else 'Not found'}")
            
            if existing:
                debug_print(f"  Notice exists (id={existing['id']}), updating...")
                # Update existing notice
                c.execute('''
                    UPDATE notices 
                    SET title = ?, affected_charts = ?, published_date = ?, 
                        content = ?, url = ?, scraped_date = ?,
                        notice_number = ?
                    WHERE id = ?
                ''', (
                    notice['title'],
                    notice.get('affected_charts', ''),
                    notice['published_date'],
                    notice.get('content', ''),
                    notice.get('url', ''),
                    scraped_date,
                    notice['notice_number'],
                    existing['id']
                ))
                
                # Create implementation status entry for this chart if it doesn't exist
                chart_identifier = notice.get('batsportkort') or notice.get('sjokort_nummer') or 'unknown'
                c.execute('''
                    INSERT OR IGNORE INTO implementation_status 
                    (notice_id, chart_identifier, implemented)
                    VALUES (?, ?, 0)
                ''', (existing['id'], chart_identifier))
                
                updated_count += 1
                debug_print(f"  ✓ Updated (chart={chart_identifier})")
            else:
                debug_print(f"  New notice, inserting...")
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
                    # Create implementation status entry for this notice-chart combination
                    notice_id = c.lastrowid
                    
                    # Determine the chart identifier (what chart was searched for)
                    chart_identifier = notice.get('batsportkort') or notice.get('sjokort_nummer') or 'unknown'
                    
                    # Insert or ignore if already exists
                    c.execute('''
                        INSERT OR IGNORE INTO implementation_status 
                        (notice_id, chart_identifier, implemented)
                        VALUES (?, ?, 0)
                    ''', (notice_id, chart_identifier))
                    
                    saved_count += 1
                    debug_print(f"  ✓ Inserted (id={notice_id}, chart={chart_identifier})")
                else:
                    skipped_count += 1
                    debug_print(f"  ✗ Insert returned 0 rows affected")
        except Exception as e:
            debug_print(f"  ✗ Error saving notice: {e}")
            debug_print(f"  Notice data: {notice}")
            skipped_count += 1
    
    conn.commit()
    conn.close()
    
    debug_print(f"\n=== Database save complete ===")
    debug_print(f"Saved {saved_count} new notices")
    debug_print(f"Updated {updated_count} existing notices")
    debug_print(f"Skipped {skipped_count} notices due to errors")
    debug_print(f"Total processed: {saved_count + updated_count + skipped_count}/{len(notices)}")
    
    return saved_count

# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/get_available_charts')
def get_available_charts():
    """Get list of all available charts from UFS website"""
    sjokort_map, batsportkort_map = get_chart_mappings()
    
    # Combine both into a single list with type indicator
    all_charts = []
    
    # Add sjökort
    for name, chart_id in sjokort_map.items():
        all_charts.append({
            'id': chart_id,
            'name': name,
            'type': 'sjokort',
            'display': f"Sjökort {name}"
        })
    
    # Add båtsportkort
    for name, chart_id in batsportkort_map.items():
        all_charts.append({
            'id': chart_id,
            'name': name,
            'type': 'batsportkort',
            'display': name
        })
    
    # Sort by display name
    all_charts.sort(key=lambda x: x['display'])
    
    return jsonify(all_charts)

@app.route('/get_tracked_charts')
def get_tracked_charts():
    """Get list of charts that have been searched/tracked"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        SELECT DISTINCT chart_identifier
        FROM implementation_status
        WHERE chart_identifier != ''
        ORDER BY chart_identifier
    ''')
    
    charts = [row[0] for row in c.fetchall()]
    conn.close()
    
    return jsonify(charts)

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
    """List all notices with implementation status for a specific chart"""
    conn = get_db()
    c = conn.cursor()
    
    # Get filter parameters
    chart_identifier = request.args.get('chart_identifier', '')
    show_implemented = request.args.get('show_implemented', '1')
    
    if not chart_identifier:
        # If no chart specified, show empty page with message
        conn.close()
        return render_template('notices.html', 
                             notices=[], 
                             chart_identifier='',
                             show_implemented=show_implemented)
    
    # Show notices for the specific chart with their implementation status
    query = '''
        SELECT n.id, n.notice_number, n.title, n.affected_charts, n.sjokort_nummer, n.batsportkort,
               n.published_date, n.content, n.url, n.scraped_date,
               i.implemented, i.implemented_date, i.notes, i.chart_identifier
        FROM notices n
        INNER JOIN implementation_status i ON n.id = i.notice_id
        WHERE i.chart_identifier = ?
    '''
    params = [chart_identifier]
    
    if show_implemented == '0':
        query += ' AND (i.implemented = 0 OR i.implemented IS NULL)'
    
    query += ' ORDER BY n.published_date DESC'
    
    c.execute(query, params)
    notices = c.fetchall()
    
    conn.close()
    
    return render_template('notices.html', notices=notices, 
                         chart_identifier=chart_identifier,
                         show_implemented=show_implemented)

@app.route('/update_status/<int:notice_id>', methods=['POST'])
def update_status(notice_id):
    """Update implementation status of a notice for a specific chart"""
    data = request.get_json()
    implemented = data.get('implemented', False)
    notes = data.get('notes', '')
    chart_identifier = data.get('chart_identifier', '')
    
    conn = get_db()
    c = conn.cursor()
    
    implemented_date = datetime.now().isoformat() if implemented else None
    
    # Check if status entry exists for this notice-chart combination
    c.execute('''
        SELECT id FROM implementation_status 
        WHERE notice_id = ? AND chart_identifier = ?
    ''', (notice_id, chart_identifier))
    status = c.fetchone()
    
    if status:
        c.execute('''
            UPDATE implementation_status 
            SET implemented = ?, implemented_date = ?, notes = ?
            WHERE notice_id = ? AND chart_identifier = ?
        ''', (implemented, implemented_date, notes, notice_id, chart_identifier))
    else:
        c.execute('''
            INSERT INTO implementation_status 
            (notice_id, chart_identifier, implemented, implemented_date, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (notice_id, chart_identifier, implemented, implemented_date, notes))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/statistics')
def statistics():
    """Show statistics and search history"""
    conn = get_db()
    c = conn.cursor()
    
    # Total notices tracked (total implementation_status entries)
    c.execute('SELECT COUNT(*) FROM implementation_status')
    total_trackings = c.fetchone()[0]
    
    # Total unique notices
    c.execute('SELECT COUNT(DISTINCT notice_id) FROM implementation_status')
    total_notices = c.fetchone()[0]
    
    # Implemented notice-chart combinations
    c.execute('SELECT COUNT(*) FROM implementation_status WHERE implemented = 1')
    implemented = c.fetchone()[0]
    
    # Statistics by chart - showing notices and implementation status
    c.execute('''
        SELECT 
            i.chart_identifier,
            COUNT(DISTINCT i.notice_id) as total_notices,
            SUM(CASE WHEN i.implemented = 1 THEN 1 ELSE 0 END) as implemented_notices
        FROM implementation_status i
        GROUP BY i.chart_identifier
        ORDER BY total_notices DESC
    ''')
    by_chart = c.fetchall()
    
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
                         total_trackings=total_trackings,
                         implemented=implemented,
                         by_chart=by_chart,
                         recent_searches=recent_searches)

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='UFS Maritime Notices Tracker')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    # Set global debug mode
    DEBUG_MODE = args.debug
    
    # Initialize database
    init_db()
    
    # Run the app
    print("=" * 60)
    print("UFS Maritime Notices Tracker")
    print("=" * 60)
    if DEBUG_MODE:
        print("DEBUG MODE ENABLED")
    print("Starting server on http://0.0.0.0:5000")
    print("Access from this machine: http://127.0.0.1:5000")
    print("Access from network: http://<your-ip>:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
