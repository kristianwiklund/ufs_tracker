"""
Chart parsing utilities
Handles extraction and parsing of chart identifiers from various formats
"""
import re

def parse_notice_type(notice_number):
    """
    Determine notice type from notice number
    
    Args:
        notice_number: Notice number string (e.g., "18369", "18370T", "18371P")
    
    Returns:
        dict with type, is_temporary, is_preliminary
    """
    if not notice_number:
        return {
            'notice_type': 'permanent',
            'is_temporary': False,
            'is_preliminary': False
        }
    
    notice_str = str(notice_number).upper()
    
    if notice_str.endswith('T'):
        return {
            'notice_type': 'temporary',
            'is_temporary': True,
            'is_preliminary': False
        }
    elif notice_str.endswith('P'):
        return {
            'notice_type': 'preliminary',
            'is_temporary': False,
            'is_preliminary': True
        }
    else:
        return {
            'notice_type': 'permanent',
            'is_temporary': False,
            'is_preliminary': False
        }

def extract_chart_identifier(chart_ref):
    """
    Extract chart identifier from a chart reference string
    
    Handles formats like:
    - "111Bsp Mälaren - Hjälmaren 2024/s25" → "Bsp Mälaren - Hjälmaren 2024"
    - "Bsp Stockholm N 2024/s39" → "Bsp Stockholm N 2024"
    - "621" → "621"
    
    Args:
        chart_ref: Chart reference string
    
    Returns:
        Cleaned chart identifier (without page numbers)
    """
    # Remove page references like "/s25, s47, s48"
    cleaned = chart_ref.split('/')[0].strip()
    
    # Pattern 1: Number concatenated with Bsp (e.g., "111Bsp Mälaren - Hjälmaren 2024")
    number_bsp_match = re.match(r'^(\d+)(Bsp.+)$', cleaned, re.IGNORECASE)
    if number_bsp_match:
        # Return the Bsp part only (the båtsportkort)
        return number_bsp_match.group(2).strip()
    
    # Pattern 2: Just "Bsp..." (e.g., "Bsp Stockholm N 2024")
    bsp_match = re.match(r'^(Bsp[^,]+)', cleaned, re.IGNORECASE)
    if bsp_match:
        return bsp_match.group(1).strip()
    
    # Pattern 3: Just a number like "621" or "111"
    if re.match(r'^\d+$', cleaned):
        return cleaned
    
    # Pattern 4: Already a chart name
    return cleaned

def split_concatenated_charts(chart_ref):
    """
    Split concatenated chart references (e.g., "111Bsp Mälaren 2024")
    
    Args:
        chart_ref: Chart reference string
    
    Returns:
        list of (display_text, identifier) tuples
    """
    # Extract main part and page numbers
    page_match = re.match(r'^([^/]+)(/.*)$', chart_ref)
    main_part = page_match.group(1) if page_match else chart_ref
    page_numbers = page_match.group(2) if page_match else ''
    
    # Check for concatenation (number + Bsp name)
    number_bsp_match = re.match(r'^(\d+)(Bsp.+)$', main_part, re.IGNORECASE)
    
    if number_bsp_match:
        # Split into two charts
        chart_number = number_bsp_match.group(1)
        bsp_name = number_bsp_match.group(2).strip()
        
        return [
            (chart_number, chart_number),
            (bsp_name + page_numbers, bsp_name)
        ]
    else:
        # Single chart
        identifier = extract_chart_identifier(chart_ref)
        return [(chart_ref, identifier)]

def parse_page_numbers(chart_ref):
    """
    Extract page numbers from chart reference
    
    Args:
        chart_ref: Chart reference like "Bsp Mälaren 2024/s25, s47, s48"
    
    Returns:
        list of page numbers: ["s25", "s47", "s48"]
    """
    page_match = re.search(r'/(.+)$', chart_ref)
    if not page_match:
        return []
    
    pages_str = page_match.group(1)
    # Split by comma and clean
    pages = [p.strip() for p in pages_str.split(',')]
    return pages

def extract_expiry_date(title, content=None):
    """
    Extract an expiry date from notice title or content.

    Only dates that are preceded by an expiry-indicating keyword are matched.
    This prevents publication dates or other incidental dates in the body from
    being mistaken for an expiry.

    Supported keyword phrases (case-insensitive):
        Swedish:  "gäller till", "giltig till", "gäller från … till"
        English:  "valid until", "valid from … until", "expires"
        Generic:  bare "till" immediately before a date (Swedish notices)

    Supported date formats (after the keyword):
        YYYY-MM-DD          →  returned as-is
        DD/MM YYYY          →  converted to YYYY-MM-DD
        DD Mon YYYY         →  converted to YYYY-MM-DD  (Mon = Jan…Dec or
                                Jan…Dec in Swedish: jan, feb, mar, apr,
                                maj, jun, jul, aug, sep, okt, nov, dec)

    Returns:
        ISO date string (YYYY-MM-DD) or None
    """
    text = f"{title} {content or ''}"

    # Swedish month abbreviations → zero-padded month number
    SWEDISH_MONTHS = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'maj': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'okt': '10', 'nov': '11', 'dec': '12',
    }
    # English month abbreviations (same keys work for English too, but add
    # the ones that differ)
    ENGLISH_MONTHS = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
    }
    ALL_MONTHS = {**SWEDISH_MONTHS, **ENGLISH_MONTHS}

    # Keyword prefix that must appear before the date.
    # The pattern uses a non-capturing group so the date capture groups
    # are numbered cleanly.  \S+ in the "from … till" variants allows an
    # arbitrary start-date between the two keywords.
    KEYWORD = (
        r'(?:'
        r'gäller\s+till'
        r'|giltig\s+till'
        r'|gäller\s+från\s+\S+\s+till'
        r'|valid\s+until'
        r'|valid\s+from\s+\S+\s+until'
        r'|expires'
        r'|till'          # bare "till" — common in short Swedish phrases
        r')\s+'
    )

    # --- Pattern 1: keyword + YYYY-MM-DD ---
    m = re.search(KEYWORD + r'(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
    if m:
        return m.group(1)

    # --- Pattern 2: keyword + DD/MM YYYY ---
    m = re.search(KEYWORD + r'(\d{1,2})/(\d{1,2})\s+(\d{4})', text, re.IGNORECASE)
    if m:
        day, month, year = m.group(1), m.group(2), m.group(3)
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    # --- Pattern 3: keyword + DD Mon YYYY  (e.g. "31 Dec 2024") ---
    mon_pattern = '|'.join(ALL_MONTHS.keys())
    m = re.search(
        KEYWORD + r'(\d{1,2})\s+(' + mon_pattern + r')\s+(\d{4})',
        text, re.IGNORECASE
    )
    if m:
        day   = m.group(1).zfill(2)
        month = ALL_MONTHS[m.group(2).lower()]
        year  = m.group(3)
        return f"{year}-{month}-{day}"

    return None

def get_chart_display_name(chart_identifier, chart_type=None):
    """
    Get human-readable display name for a chart
    
    Args:
        chart_identifier: Chart ID
        chart_type: 'sjokort' or 'batsportkort'
    
    Returns:
        Formatted display name
    """
    if chart_type == 'sjokort' or re.match(r'^\d+$', chart_identifier):
        return f"Sjökort {chart_identifier}"
    elif chart_identifier.lower().startswith('bsp'):
        return chart_identifier
    else:
        return chart_identifier
