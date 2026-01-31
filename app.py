"""
UFS Maritime Notices Tracker - Main Application
Refactored with modular architecture
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import argparse
from datetime import datetime

# Import our modules
from models.database import init_db, get_db, migrate_add_notice_types
from services.scraper import scrape_ufs_notices, get_chart_mappings, set_debug_mode
from utils.chart_parser import parse_notice_type

app = Flask(__name__)
app.config['DATABASE'] = 'ufs_notices.db'

# Make datetime.now() available inside all Jinja2 templates
app.jinja_env.globals['now'] = datetime.now

# Global debug flag
DEBUG_MODE = False

def debug_print(*args, **kwargs):
    """Print debug information if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        print(*args, **kwargs)

#################################################
# DATABASE OPERATIONS
#################################################

def save_notices_to_db(notices, chart_identifier):
    """
    Save scraped notices to database and create implementation status entries
    """
    if isinstance(notices, dict) and 'error' in notices:
        return notices
    
    conn = get_db()
    c = conn.cursor()
    saved_count = 0
    
    for notice in notices:
        # Check if notice already exists
        c.execute('SELECT id FROM notices WHERE notice_number = ?', (notice['notice_number'],))
        existing = c.fetchone()
        
        if existing:
            notice_id = existing['id']
            debug_print(f"Notice {notice['notice_number']} already exists with ID {notice_id}")
        else:
            # Insert new notice
            c.execute('''
                INSERT INTO notices (
                    notice_number, title, affected_charts, sjokort_nummer, batsportkort,
                    published_date, area, content, url, scraped_date,
                    notice_type, expiry_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                notice['notice_number'],
                notice['title'],
                notice['affected_charts'],
                notice.get('sjokort_nummer', ''),
                notice.get('batsportkort', ''),
                notice['published_date'],
                notice.get('area', ''),
                notice.get('content', ''),
                notice['url'],
                notice['scraped_date'],
                notice.get('notice_type', 'permanent'),
                notice.get('expiry_date')
            ))
            notice_id = c.lastrowid
            saved_count += 1
            debug_print(f"Saved notice {notice['notice_number']} with ID {notice_id}")
        
        # Create or update implementation status for this chart
        c.execute('''
            INSERT OR IGNORE INTO implementation_status (notice_id, chart_identifier, implemented)
            VALUES (?, ?, 0)
        ''', (notice_id, chart_identifier))
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'total_found': len(notices),
        'saved': saved_count,
        'message': f'Hittade {len(notices)} notiser, sparade {saved_count} nya'
    }

def get_notices_for_chart(chart_identifier, show_implemented=False):
    """Get all notices for a specific chart"""
    conn = get_db()
    c = conn.cursor()
    
    query = '''
        SELECT n.*, i.implemented, i.implemented_date, i.notes, i.priority
        FROM notices n
        JOIN implementation_status i ON n.id = i.notice_id
        WHERE i.chart_identifier = ?
    '''
    
    if not show_implemented:
        query += ' AND i.implemented = 0'
    
    query += ' ORDER BY n.published_date DESC, n.notice_number DESC'
    
    c.execute(query, (chart_identifier,))
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

#################################################
# ROUTES
#################################################

@app.route('/')
def index():
    """Main search page"""
    return render_template('index.html')

@app.route('/get_available_charts')
def get_available_charts():
    """Get list of all available charts from UFS"""
    sjokort_map, batsportkort_map = get_chart_mappings()
    
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
        ORDER BY chart_identifier
    ''')
    
    charts = [row['chart_identifier'] for row in c.fetchall()]
    conn.close()
    
    return jsonify(charts)

@app.route('/search', methods=['POST'])
def search():
    """Search for notices"""
    sjokort_nummer = request.form.get('sjokort_nummer')
    batsportkort = request.form.get('batsportkort')
    chart_identifier = request.form.get('chart_identifier')
    
    # Determine which chart was searched
    if not chart_identifier:
        chart_identifier = sjokort_nummer if sjokort_nummer else batsportkort
    
    # Scrape notices
    notices = scrape_ufs_notices(
        sjokort_nummer=sjokort_nummer,
        batsportkort=batsportkort
    )
    
    # Save to database
    result = save_notices_to_db(notices, chart_identifier)
    
    if result.get('success'):
        # Record in search history
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO search_history (search_term, search_type, search_date, results_count)
            VALUES (?, ?, ?, ?)
        ''', (chart_identifier, 'chart', datetime.now().isoformat(), result['total_found']))
        conn.commit()
        conn.close()
    
    return jsonify(result)

@app.route('/notices')
def list_notices():
    """List notices for a chart"""
    chart_identifier = request.args.get('chart_identifier', '')
    show_implemented = request.args.get('show_implemented', '0') == '1'
    
    notices = []
    if chart_identifier:
        notices = get_notices_for_chart(chart_identifier, show_implemented)
    
    return render_template('notices.html',
                         notices=notices,
                         chart_identifier=chart_identifier,
                         show_implemented=show_implemented)

@app.route('/update_status/<int:notice_id>', methods=['POST'])
def update_status(notice_id):
    """Update implementation status for a notice"""
    data = request.get_json()
    implemented = data.get('implemented', False)
    notes = data.get('notes', '')
    chart_identifier = data.get('chart_identifier', '')
    
    conn = get_db()
    c = conn.cursor()
    
    implemented_date = datetime.now().isoformat() if implemented else None
    
    c.execute('''
        UPDATE implementation_status
        SET implemented = ?, implemented_date = ?, notes = ?
        WHERE notice_id = ? AND chart_identifier = ?
    ''', (implemented, implemented_date, notes, notice_id, chart_identifier))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/help')
def help_page():
    """Documentation and correction instructions"""
    return render_template('help.html')

@app.route('/statistics')
def statistics():
    """Show statistics"""
    conn = get_db()
    c = conn.cursor()
    
    # Overall stats
    c.execute('SELECT COUNT(*) as total FROM notices')
    total_notices = c.fetchone()['total']
    
    c.execute('SELECT COUNT(*) as implemented FROM implementation_status WHERE implemented = 1')
    implemented_count = c.fetchone()['implemented']
    
    # Per-chart stats
    c.execute('''
        SELECT 
            chart_identifier,
            COUNT(*) as total,
            SUM(CASE WHEN implemented = 1 THEN 1 ELSE 0 END) as implemented
        FROM implementation_status
        GROUP BY chart_identifier
        ORDER BY chart_identifier
    ''')
    
    chart_stats = []
    for row in c.fetchall():
        total = row['total']
        impl = row['implemented']
        chart_stats.append({
            'chart': row['chart_identifier'],
            'total': total,
            'implemented': impl,
            'remaining': total - impl,
            'percentage': round((impl / total * 100) if total > 0 else 0, 1)
        })
    
    # Recent searches
    c.execute('''
        SELECT * FROM search_history
        ORDER BY search_date DESC
        LIMIT 10
    ''')
    recent_searches = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return render_template('statistics.html',
                         total_notices=total_notices,
                         implemented_count=implemented_count,
                         chart_stats=chart_stats,
                         recent_searches=recent_searches)

#################################################
# MAIN
#################################################

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='UFS Maritime Notices Tracker')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    
    args = parser.parse_args()
    
    # Set debug mode
    DEBUG_MODE = args.debug
    set_debug_mode(args.debug)
    
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Run migrations
    print("Running migrations...")
    migrate_add_notice_types()
    
    print(f"\nStarting UFS Tracker on {args.host}:{args.port}")
    print(f"Debug mode: {'ON' if args.debug else 'OFF'}")
    print(f"\nOpen your browser to: http://{args.host}:{args.port}\n")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
