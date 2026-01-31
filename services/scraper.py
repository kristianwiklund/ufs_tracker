"""
UFS Scraper Service
Handles scraping notices from the Swedish Maritime Administration website
"""
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
from utils.chart_parser import parse_notice_type, extract_expiry_date

# Cache for chart mappings (expires after 1 hour)
CHART_MAPPINGS_CACHE = {'data': None, 'timestamp': None}
CACHE_DURATION = 3600  # 1 hour in seconds

DEBUG_MODE = False

def set_debug_mode(enabled):
    """Enable or disable debug output"""
    global DEBUG_MODE
    DEBUG_MODE = enabled

def debug_print(*args, **kwargs):
    """Print debug information if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        print(*args, **kwargs)

def get_chart_mappings():
    """
    Scrape the UFS search page to get the mappings between chart names/numbers and their IDs.
    Returns a tuple of (sjokort_map, batsportkort_map)
    Cached for 1 hour to avoid repeated scraping.
    """
    global CHART_MAPPINGS_CACHE
    
    # Check if cache is valid
    current_time = time.time()
    if (CHART_MAPPINGS_CACHE['data'] is not None and 
        CHART_MAPPINGS_CACHE['timestamp'] is not None and
        current_time - CHART_MAPPINGS_CACHE['timestamp'] < CACHE_DURATION):
        debug_print("Using cached chart mappings")
        return CHART_MAPPINGS_CACHE['data']
    
    debug_print("Fetching fresh chart mappings from UFS website")
    search_url = "https://ufs.sjofartsverket.se/Notice/Search"
    
    try:
        debug_print(f"Fetching chart mappings from {search_url}")
        response = requests.get(search_url, timeout=10)
        
        if response.status_code != 200:
            debug_print(f"Failed to fetch search page: {response.status_code}")
            return {}, {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get sjökort mappings
        sjokort_map = {}
        sjokort_select = soup.find('select', {'id': 'SearchFormModel_ChartNumbers'})
        if sjokort_select:
            for option in sjokort_select.find_all('option'):
                value = option.get('value', '')
                text = option.get_text(strip=True)
                if value and text and value != '':
                    sjokort_map[text] = value
            debug_print(f"Found {len(sjokort_map)} sjökort mappings")
        
        # Get båtsportkort mappings
        batsportkort_map = {}
        batsportkort_select = soup.find('select', {'id': 'SearchFormModel_SmallCraftChart'})
        if batsportkort_select:
            for option in batsportkort_select.find_all('option'):
                value = option.get('value', '')
                text = option.get_text(strip=True)
                if value and text and value != '':
                    batsportkort_map[text] = value
            debug_print(f"Found {len(batsportkort_map)} båtsportkort mappings")
        
        # Cache the results
        CHART_MAPPINGS_CACHE['data'] = (sjokort_map, batsportkort_map)
        CHART_MAPPINGS_CACHE['timestamp'] = current_time
        
        return sjokort_map, batsportkort_map
    
    except Exception as e:
        debug_print(f"Error fetching chart mappings: {e}")
        if CHART_MAPPINGS_CACHE['data'] is not None:
            debug_print("Returning stale cached data due to error")
            return CHART_MAPPINGS_CACHE['data']
        return {}, {}

def get_chart_id(chart_name, chart_map):
    """Map chart name to its ID using the provided mapping"""
    if not chart_name:
        return None
    
    chart_name_str = str(chart_name)
    
    # Try exact match first (even for numbers)
    if chart_name_str in chart_map:
        return chart_map[chart_name_str]
    
    # Try case-insensitive match
    for name, chart_id in chart_map.items():
        if name.lower() == chart_name_str.lower():
            return chart_id
    
    # If it's a number and no match found, try it as-is
    # (fallback for direct ID usage)
    if chart_name_str.isdigit():
        debug_print(f"WARNING: No mapping found for chart '{chart_name_str}', using as direct ID")
        return chart_name_str
    
    # Return as-is if no match (last resort)
    debug_print(f"WARNING: No mapping found for chart '{chart_name_str}', using as-is")
    return chart_name_str

def scrape_ufs_notices(sjokort_nummer=None, batsportkort=None, max_rows=500):
    """
    Scrape notices from UFS website
    
    Args:
        sjokort_nummer: Sjökort chart number
        batsportkort: Båtsportkort chart name
        max_rows: Maximum number of rows to process (safety limit)
    
    Returns:
        List of notice dictionaries or dict with error
    """
    base_url = "https://ufs.sjofartsverket.se/Notice/Search/"
    
    # Validate inputs
    if not sjokort_nummer and not batsportkort:
        return {'error': 'Must specify either sjökort or båtsportkort'}
    
    # Get chart mappings
    sjokort_map, batsportkort_map = get_chart_mappings()
    
    # Prepare query parameters
    params = {}
    
    if batsportkort:
        chart_id = get_chart_id(batsportkort, batsportkort_map)
        params['SearchFormModel.SmallCraftChart'] = chart_id
        debug_print(f"Searching for båtsportkort: '{batsportkort}'")
        debug_print(f"Mapped to ID: '{chart_id}'")
        debug_print(f"Total båtsportkort available: {len(batsportkort_map)}")
    
    if sjokort_nummer:
        chart_id = get_chart_id(sjokort_nummer, sjokort_map)
        params['SearchFormModel.ChartNumbers'] = chart_id
        debug_print(f"Searching for sjökort: '{sjokort_nummer}'")
        debug_print(f"Mapped to ID: '{chart_id}'")
        debug_print(f"Total sjökort available: {len(sjokort_map)}")
        if sjokort_nummer in sjokort_map:
            debug_print(f"Direct match found: {sjokort_map[sjokort_nummer]}")
        else:
            debug_print(f"No direct match. Trying as-is.")
            debug_print(f"First 10 sjökort mappings: {dict(list(sjokort_map.items())[:10])}")
    
    # Verify we have parameters
    if 'SearchFormModel.SmallCraftChart' not in params and 'SearchFormModel.ChartNumbers' not in params:
        return {'error': 'Could not map chart name to ID'}
    
    params['SearchFormModel.SearchTimePeriod'] = '0'  # All time
    
    try:
        session = requests.Session()
        debug_print(f"Making request to: {base_url}")
        debug_print(f"Parameters: {params}")
        
        response = session.get(base_url, params=params, timeout=10)
        debug_print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            return {'error': f'Failed to access website: {response.status_code}'}
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        notices = []
        
        # Find the table
        table = find_notices_table(soup)
        
        if not table:
            return {'error': 'Could not find results table', 'params': params}
        
        rows = table.find_all('tr')[1:]  # Skip header
        debug_print(f"Found table with {len(rows)} rows")
        
        # Safety limit
        if len(rows) > max_rows:
            debug_print(f"WARNING: Found {len(rows)} rows, limiting to {max_rows}")
            rows = rows[:max_rows]
        
        # Process each row
        for idx, row in enumerate(rows):
            notice = parse_notice_row(row, idx)
            if notice:
                # Add notice type classification
                type_info = parse_notice_type(notice.get('notice_number', ''))
                notice.update(type_info)
                
                # Try to extract expiry date for temporary notices
                if type_info['is_temporary']:
                    expiry = extract_expiry_date(
                        notice.get('title', ''),
                        notice.get('content', '')
                    )
                    notice['expiry_date'] = expiry
                
                notices.append(notice)
        
        return notices
        
    except Exception as e:
        debug_print(f"Error scraping UFS: {e}")
        return {'error': str(e)}

def find_notices_table(soup):
    """Find the correct notices table in the page"""
    # Try to find by heading
    heading = soup.find(['h2', 'h3', 'h4'], string=re.compile(r'Notiser för gällande sjökort', re.IGNORECASE))
    if heading:
        debug_print(f"Found heading: '{heading.get_text()}' ({heading.name})")
        table = heading.find_next('table')
        if table:
            debug_print(f"Found table after heading")
            return table
    
    # Try by caption
    debug_print("No table found by heading, trying caption...")
    captions = soup.find_all('caption')
    for caption in captions:
        if re.search(r'Notiser för gällande sjökort', caption.get_text(), re.IGNORECASE):
            table = caption.find_parent('table')
            if table:
                debug_print(f"Found table by caption")
                return table
    
    # Try by id or class
    table = soup.find('table', {'id': re.compile(r'notice|result', re.IGNORECASE)})
    if table:
        debug_print("Found table by id")
        return table
    
    # Last resort
    table = soup.find('table', {'class': 'table'})
    if table:
        debug_print("Found table by class")
        return table
    
    return None

def parse_notice_row(row, idx):
    """Parse a single notice row from the table"""
    cells = row.find_all('td')
    debug_print(f"\nRow {idx}: {len(cells)} cells")
    
    if len(cells) < 3:
        debug_print(f"  Skipping row {idx}: not enough cells")
        return None
    
    # Extract notice number from link
    notice_number = extract_notice_number(row)
    
    # Parse cells (format: affected_charts, date, title, empty)
    affected_charts = cells[0].get_text(strip=True) if len(cells) > 0 else ''
    published_date = cells[1].get_text(strip=True) if len(cells) > 1 else ''
    title = cells[2].get_text(strip=True) if len(cells) > 2 else ''
    
    # Construct detail URL
    url = f"https://ufs.sjofartsverket.se/Current/NoticeDetails?notice={notice_number}&from=search" if notice_number else ''
    
    notice = {
        'notice_number': notice_number,
        'title': title,
        'affected_charts': affected_charts,
        'published_date': published_date,
        'url': url,
        'scraped_date': datetime.now().isoformat(),
        'content': '',  # Would need to fetch detail page
        'area': '',
        'sjokort_nummer': '',
        'batsportkort': ''
    }
    
    debug_print(f"  Notice: {notice_number} - {title[:50]}...")
    return notice

def extract_notice_number(row):
    """Extract notice number from row links or cells"""
    # Try to find in links
    links = row.find_all('a')
    for link in links:
        href = link.get('href', '')
        match = re.search(r'notice=(\d+)', href)
        if match:
            return match.group(1)
    
    # Try to find in cell text
    cells = row.find_all('td')
    for cell in cells:
        text = cell.get_text(strip=True)
        match = re.search(r'\b(\d{4,6}[PT]?)\b', text)
        if match:
            number = match.group(1)
            if 10000 <= int(re.sub(r'[PT]', '', number)) <= 25000:
                return number
    
    return ''
