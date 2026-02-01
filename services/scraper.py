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

# Delay between consecutive Tier-2 detail-page fetches (seconds).
# Keeps us from hammering UFS when many notices need individual classification.
TIER2_DELAY = 0.3

# ---------------------------------------------------------------------------
# Scrape-progress state — written by the scraper, read by /search/progress.
# A single global dict is fine: only one scrape runs at a time (Flask dev
# server is single-threaded; production deployments would need per-request
# state, but that is out of scope here).
# ---------------------------------------------------------------------------
_scrape_progress = {
    'active':      False,   # True while a scrape is in flight
    'phase':       '',      # human-readable label for the current phase
    'current':     0,       # notices processed so far in the current phase
    'total':       0,       # total notices in the current phase
    'tier2_queue': 0,       # how many notices still need a Tier-2 fetch
}

def get_scrape_progress():
    """Return a snapshot of current scrape progress (called by the route)."""
    return dict(_scrape_progress)

def _set_progress(active=None, phase=None, current=None, total=None, tier2_queue=None):
    """Atomically update whichever progress fields are provided."""
    if active       is not None: _scrape_progress['active']      = active
    if phase        is not None: _scrape_progress['phase']       = phase
    if current      is not None: _scrape_progress['current']     = current
    if total        is not None: _scrape_progress['total']       = total
    if tier2_queue  is not None: _scrape_progress['tier2_queue'] = tier2_queue

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
        
        # ------------------------------------------------------------------
        # Phase 1 — parse all rows, classify via Tier 1 (suffix) only.
        # No extra HTTP requests.  Notices that need Tier 2 are collected
        # into `needs_detail` for Phase 2.
        # ------------------------------------------------------------------
        _set_progress(active=True, phase='Hämtar notiser från UFS…', current=0, total=len(rows), tier2_queue=0)

        notices = []
        needs_detail = []   # indices into `notices` that still need Tier 2

        for idx, row in enumerate(rows):
            notice = parse_notice_row(row, idx)
            if notice:
                suffix = notice.pop('_suffix', None)
                if suffix == 'T':
                    notice['notice_type']    = 'temporary'
                    notice['is_temporary']   = True
                    notice['is_preliminary'] = False
                    debug_print(f"  Classified {notice['notice_number']} as temporary (suffix)")
                elif suffix == 'P':
                    notice['notice_type']    = 'preliminary'
                    notice['is_temporary']   = False
                    notice['is_preliminary'] = True
                    debug_print(f"  Classified {notice['notice_number']} as preliminary (suffix)")
                else:
                    # Mark as unclassified for now; Phase 2 will fill it in.
                    notice['notice_type']    = None
                    notice['is_temporary']   = False
                    notice['is_preliminary'] = False
                    needs_detail.append(len(notices))

                notices.append(notice)

            _set_progress(current=idx + 1)

        debug_print(f"Phase 1 complete: {len(notices)} notices, {len(needs_detail)} need Tier 2")

        # ------------------------------------------------------------------
        # Phase 2 — fetch detail pages only for notices that Tier 1 could
        # not classify.  Each fetch is followed by a short delay to avoid
        # hammering UFS.
        # ------------------------------------------------------------------
        if needs_detail:
            _set_progress(phase='Klassifierar notiser…', current=0, total=len(needs_detail), tier2_queue=len(needs_detail))

            for step, notice_idx in enumerate(needs_detail):
                notice = notices[notice_idx]
                detail_type = fetch_notice_class_type(notice['notice_number'])

                if detail_type:
                    notice['notice_type']    = detail_type
                    notice['is_temporary']   = (detail_type == 'temporary')
                    notice['is_preliminary'] = (detail_type == 'preliminary')
                    debug_print(f"  Classified {notice['notice_number']} as {detail_type} (detail page)")
                else:
                    # Tier 3 — heuristic fallback
                    type_info = parse_notice_type(notice.get('notice_number', ''))
                    notice.update(type_info)
                    debug_print(f"  Classified {notice['notice_number']} as {type_info['notice_type']} (heuristic fallback)")

                _set_progress(current=step + 1, tier2_queue=len(needs_detail) - step - 1)

                # Throttle: delay before the next detail fetch (skip after the last one)
                if step < len(needs_detail) - 1:
                    time.sleep(TIER2_DELAY)

        # ------------------------------------------------------------------
        # Post-classification: extract expiry dates for temporary notices
        # ------------------------------------------------------------------
        for notice in notices:
            if notice.get('is_temporary'):
                expiry = extract_expiry_date(
                    notice.get('title', ''),
                    notice.get('content', '')
                )
                notice['expiry_date'] = expiry

        _set_progress(active=False, phase='Klart', current=0, total=0, tier2_queue=0)
        return notices
        
    except Exception as e:
        _set_progress(active=False, phase='Fel', current=0, total=0, tier2_queue=0)
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

    # Extract (T)/(P) suffix from visible cell text (if present)
    suffix = extract_notice_suffix(row)
    
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
        'batsportkort': '',
        '_suffix': suffix,  # internal; used for classification, not stored to DB
    }
    
    debug_print(f"  Notice: {notice_number} suffix={suffix} - {title[:50]}...")
    return notice

def extract_notice_number(row):
    """
    Extract notice number from row links or cells.

    Returns the bare numeric ID.  The (T)/(P) suffix, if present in the
    visible text, is stored separately — see extract_notice_suffix().
    """
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
        match = re.search(r'\b(\d{4,6})[PT]?\b', text)
        if match:
            number = match.group(1)
            if 10000 <= int(number) <= 25000:
                return number

    return ''


def extract_notice_suffix(row):
    """
    Look for a (T) or (P) suffix next to the notice number in the visible
    cell text.  The href only contains the bare numeric ID, but the rendered
    text on the P&T page shows e.g. "19818(T)".

    Returns 'T', 'P', or None.
    """
    cells = row.find_all('td')
    for cell in cells:
        text = cell.get_text(strip=True)
        # Match bare number followed immediately by (T) or (P)
        match = re.search(r'\d{4,6}\s*\(([TP])\)', text)
        if match:
            return match.group(1)
    return None


def fetch_notice_class_type(notice_number):
    """
    Fetch the detail page for a single notice and parse the authoritative
    Class/type field.

    Returns 'temporary', 'preliminary', or 'permanent', or None on failure.
    """
    url = f"https://ufs.sjofartsverket.se/en/Current/NoticeDetails?notice={notice_number}&from=search"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            debug_print(f"  Detail page for {notice_number} returned {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # The field is rendered as a <h6> containing bold text like:
        #   <h6><strong>Class/type:</strong> Temporary/Amendment</h6>
        # or in Swedish:
        #   <h6><strong>Typ av notis:</strong> Temporär/Underrättelse</h6>
        for h6 in soup.find_all('h6'):
            text = h6.get_text(strip=True)
            # English
            if text.lower().startswith('class/type:'):
                value = text.split(':', 1)[1].strip().lower()
                if value.startswith('temporary'):
                    return 'temporary'
                elif value.startswith('preliminary'):
                    return 'preliminary'
                else:
                    return 'permanent'
            # Swedish
            if text.lower().startswith('typ av notis:'):
                value = text.split(':', 1)[1].strip().lower()
                if value.startswith('temporär'):
                    return 'temporary'
                elif value.startswith('preliminär'):
                    return 'preliminary'
                else:
                    return 'permanent'

        debug_print(f"  Could not find Class/type field for notice {notice_number}")
        return None

    except Exception as e:
        debug_print(f"  Error fetching detail page for {notice_number}: {e}")
        return None
