# UFS Maritime Notices Tracker - Complete Recreation Prompt v2.0

**Version**: 2.0  
**Date**: 2026-01-29  
**Status**: Production Ready - Includes Desktop App, Branding, Release Automation, and Interactive Features

This document contains the complete specification to recreate the UFS Maritime Notices Tracker from scratch, including all features implemented as of January 2026.

## Changelog from v1.0

- ✅ Added desktop application with pywebview
- ✅ Added branding (GitHub About button, footer with copyright)
- ✅ Added automated release workflow
- ✅ Fixed double-ZIP issue in builds
- ✅ Added chart mappings cache (1 hour expiration)
- ✅ Added 500-row safety limit
- ✅ Fixed sjökort search parameter (ChartNumbers vs Chart)
- ✅ Added clickable affected charts feature
- ✅ Per-chart implementation tracking
- ✅ Dynamic chart selection dropdowns

## Project Overview

Create a Python Flask web application with optional desktop GUI that scrapes, stores, and tracks maritime notices (Underrättelser för sjöfarande) from the Swedish Maritime Administration's UFS database at https://ufs.sjofartsverket.se/Notice/Search/.

The application can run in two modes:
1. **Web Mode**: Flask server accessed via web browser (python app.py)
2. **Desktop Mode**: Native desktop application using pywebview (python desktop_app.py)

## Core Requirements

### 1. Technology Stack
- **Backend**: Python Flask web framework
- **Database**: SQLite for persistent storage
- **Web Scraping**: Requests + BeautifulSoup4
- **Frontend**: Pure HTML, CSS, and JavaScript (no external dependencies)
- **Desktop GUI**: pywebview for standalone desktop application
- **Server**: Listen on 127.0.0.1:5000 (localhost only for security)
- **Build Tool**: PyInstaller for creating standalone executables

### 2. Key Features

#### Dynamic Chart Selection
- Scrape the UFS search page (https://ufs.sjofartsverket.se/Notice/Search) to dynamically fetch:
  - All available sjökort (nautical charts) from selector `#SearchFormModel_ChartNumbers`
  - All available båtsportkort (small craft charts) from selector `#SearchFormModel_SmallCraftChart`
- Map display names to their internal IDs for search queries
- Combine both chart types into a unified dropdown selector

#### Search Functionality
- Main search page with single dropdown containing all charts (both sjökort and båtsportkort)
- Charts displayed with format: "Sjökort [number]" for sjökort, and plain name for båtsportkort
- On form submission:
  - Use GET request to https://ufs.sjofartsverket.se/Notice/Search/ with URL parameters
  - For sjökort: `SearchFormModel.Chart=[chart_id]`
  - For båtsportkort: `SearchFormModel.SmallCraftChart=[chart_id]`
  - Set `SearchFormModel.SearchTimePeriod=0` (all time)

#### Notice Scraping Logic
- Target ONLY the table under heading "Notiser för gällande sjökort"
- Ignore other tables (e.g., "Tillkännagivanden och notiser utan anknytning till gällande sjökort")
- Extract from each row (4 cells):
  - **Cell 0**: Affected charts (e.g., "612Bsp Stockholm N 2024/s39")
  - **Cell 1**: Publication date (e.g., "2026-01-14")
  - **Cell 2**: Title/description (e.g., "Stockholms skärgård. Mälby...")
  - **Cell 3**: Usually empty
- Extract notice number from link href in the row (pattern: `notice=19697`)
- If no link found, search all cells for a 4-6 digit number
- Construct detail URL: `https://ufs.sjofartsverket.se/Current/NoticeDetails?notice=[notice_number]&from=search`

#### Per-Chart Implementation Tracking
- Track implementation status separately for each chart
- Same notice can appear in multiple chart searches with independent tracking
- Create `implementation_status` entry with chart_identifier for each notice-chart combination
- Only track charts that have been actively searched
- Disable checkboxes and notes when no chart is selected

### 3. Database Schema

#### Table: `notices`
```sql
CREATE TABLE notices (
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
CREATE INDEX idx_notice_number ON notices(notice_number)
```

#### Table: `implementation_status`
```sql
CREATE TABLE implementation_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_id INTEGER,
    chart_identifier TEXT,
    implemented BOOLEAN DEFAULT 0,
    implemented_date TEXT,
    notes TEXT,
    FOREIGN KEY (notice_id) REFERENCES notices(id),
    UNIQUE(notice_id, chart_identifier)
)
```

#### Table: `search_history`
```sql
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_term TEXT,
    search_type TEXT,
    search_date TEXT,
    results_count INTEGER
)
```

### 4. Routes and Endpoints

#### GET `/`
- Render main search page
- Load available charts dynamically via JavaScript

#### GET `/get_available_charts`
- Scrape UFS search page
- Return JSON array of all charts with structure:
```json
[
  {
    "id": "chart_id",
    "name": "chart_name",
    "type": "sjokort|batsportkort",
    "display": "Display Name"
  }
]
```

#### GET `/get_tracked_charts`
- Return JSON array of chart_identifiers that have been searched/tracked
- Query: `SELECT DISTINCT chart_identifier FROM implementation_status`

#### POST `/search`
- Accept FormData with either `sjokort_nummer` or `batsportkort`
- Scrape notices from UFS
- Save to database with per-chart implementation_status entries
- Return JSON: `{success: true, total_found: N, saved: M, message: "..."}`

#### GET `/notices?chart_identifier=[chart]&show_implemented=[0|1]`
- If no chart_identifier: show empty page with disabled checkboxes
- Otherwise: show notices for that specific chart with implementation status
- Auto-reload when chart selection or show_implemented checkbox changes

#### POST `/update_status/<notice_id>`
- Accept JSON: `{implemented: bool, notes: string, chart_identifier: string}`
- Update implementation_status for specific notice-chart combination

#### GET `/statistics`
- Show per-chart statistics with columns:
  - Chart name
  - Total notices
  - Implemented count
  - Remaining count
  - Progress bar (percentage)

### 5. Frontend Pages

#### index.html (Hem)
- Single dropdown selector for all charts
- Fetches charts on page load via `/get_available_charts`
- Displays loading spinner during search
- Shows success/error messages
- Redirects to `/notices?chart_identifier=[chart]` after successful search
- Container max-width: 1400px
- Navigation tabs: width=130px, min-width=130px, centered

#### notices.html (Visa notiser)
- Dropdown showing only tracked charts (via `/get_tracked_charts`)
- Auto-reloads when chart selection changes
- Auto-reloads when "Visa implementerade" checkbox changes
- If no chart selected:
  - Shows warning: "⚠️ Välj ett kort för att kunna markera notiser som implementerade"
  - Disables all checkboxes and notes inputs
- Each notice card shows:
  - Notice number (clickable link to detail page)
  - Title (clickable link to detail page)
  - **Affected charts (Berörda kort)** - INTERACTIVE FEATURE:
    - Parse the affected_charts field (e.g., "111Bsp Mälaren - Hjälmaren 2024/s25, s47, s48, 621")
    - Split on commas to get individual chart references
    - Handle concatenated charts (e.g., "111Bsp Mälaren..." = chart "111" + "Bsp Mälaren...")
    - For each chart reference:
      - Extract chart identifier (strip page numbers like "/s25, s47")
      - Keep page numbers for display purposes
      - Check if chart exists in tracked_charts list
      - If tracked: Display as clickable link with CSS class "chart-link"
      - If not tracked: Display as plain text with muted color
    - Chart identifier extraction patterns:
      - "111Bsp Mälaren - Hjälmaren 2024/s25" → Split into "111" and "Bsp Mälaren - Hjälmaren 2024"
      - "Bsp Stockholm N 2024/s39" → "Bsp Stockholm N 2024"
      - "621" → "621"
      - Page numbers (/s25, s47) kept for display but removed for matching
    - On click of tracked chart:
      - Reload page with `chart_identifier=[clicked_chart]`
      - This switches the view to show notices for that chart
    - Styling:
      - Clickable charts: Blue color (#667eea), underline on hover, pointer cursor, tooltip
      - Non-tracked charts: Gray color (#999), no hover effect, tooltip explaining not downloaded
      - Separate charts with commas and spaces
      - Display page numbers with chart name but don't use for matching
  - Affected charts
  - Publication date
  - Scraped date
  - Content (scrollable, max-height: 200px)
  - Checkbox for "Implementerad"
  - Notes input field
  - "Visa detaljer" button
- Container max-width: 1400px

#### statistics.html (Statistik)
- Overview cards: total notices, implemented, remaining
- Progress bar showing overall completion
- Table showing per-chart breakdown:
  - Chart identifier
  - Total notices for that chart
  - Implemented count
  - Remaining count
  - Progress bar per chart
- Recent searches history
- Container max-width: 1400px

### 6. Debug Mode

#### Command Line Flag
- Add `--debug` flag using argparse
- Default: debug disabled
- Usage: `python app.py --debug`

#### Debug Behavior
- All debug output via `debug_print()` function that checks `DEBUG_MODE` global
- When enabled, prints:
  - HTTP requests and responses
  - Table structure and cell contents
  - Notice extraction details
  - Database operations
  - Chart mapping results
- Saves error responses to `/tmp/ufs_error_XXX.html`
- Saves pages without tables to `/tmp/ufs_no_table.html`

### 7. Styling Guidelines

#### Color Scheme
- Primary gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Header: `#2c3e50`
- Navigation: `#34495e`
- Active nav: `#667eea`
- Success green: `#4caf50`
- Warning orange: `#ff9800`

#### Layout
- All pages: max-width 1400px, centered
- Cards: white background, border-radius 8-10px, subtle shadows
- Navigation: 3 equal-width tabs (130px each, centered text)
- Responsive design that works on desktop and mobile

#### Typography
- Font: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
- Headers: bold, appropriate sizing
- Body text: readable line-height (1.6)

### 8. Additional Files

#### requirements.txt
```
Flask==3.0.0
requests==2.31.0
beautifulsoup4==4.12.2
```

#### start.sh
```bash
#!/bin/bash
echo "UFS Maritime Notices Tracker"
pip install -q -r requirements.txt --break-system-packages
python app.py "$@"
```

#### README.md
- In Swedish
- Installation instructions
- Usage guide
- Database structure documentation
- Troubleshooting section
- Debug mode documentation

#### USER_GUIDE.md
- Detailed Swedish user guide
- Step-by-step usage instructions
- Screenshots/descriptions of each feature

### 9. Important Implementation Details

#### Chart ID Mapping
- NEVER hardcode chart IDs
- Always fetch fresh from UFS website
- Cache mappings per request, not globally

#### Notice Number Extraction
- Priority 1: Extract from link href (`notice=XXXXX`)
- Priority 2: Search all cells for 4-6 digit number in range 10000-25000
- Never drop rows - save even without notice number (empty string)

#### Database Integrity
- No UNIQUE constraint on notice_number (allows empty strings)
- UNIQUE constraint on (notice_id, chart_identifier) pair
- Use INSERT OR IGNORE for implementation_status

#### Error Handling
- Graceful degradation when UFS website is unavailable
- Clear error messages for users
- Debug mode for troubleshooting

#### JavaScript Auto-Reload
- Chart selection change → reload page with new chart
- Show implemented toggle → reload page with new filter
- Pass chart_identifier in all status updates

### 10. Critical Requirements Summary

✅ Dynamic chart fetching from UFS website
✅ Correct table identification ("Notiser för gällande sjökort")
✅ Accurate 4-column scraping (affected_charts, date, title, empty)
✅ Notice number extraction from links
✅ Per-chart implementation tracking
✅ Disabled UI when no chart selected
✅ Auto-reload on filter changes
✅ Consistent 1400px width across all pages
✅ Debug mode with --debug flag
✅ All content in Swedish
✅ Server listens on 0.0.0.0:5000

### 11. File Structure
```
.
├── app.py                      # Main Flask application
├── desktop_app.py              # Desktop GUI wrapper using pywebview
├── requirements.txt            # Python dependencies (includes pywebview)
├── start.sh                    # Startup script (Linux/Mac)
├── build-windows.bat           # Build script for Windows executables
├── build-linux.sh              # Build script for Linux executables
├── README.md                   # Swedish documentation
├── USER_GUIDE.md              # Swedish user guide
├── BUILD.md                    # Build instructions
├── RECREATION_PROMPT.md       # This file
├── ufs_notices.db             # SQLite database (created automatically)
├── .github/
│   └── workflows/
│       ├── build-windows.yml  # GitHub Actions Windows build
│       └── build-android.yml  # GitHub Actions Android build
├── templates/
│   ├── index.html             # Search page
│   ├── notices.html           # Notice list page
│   └── statistics.html        # Statistics page
└── .gitignore
```

### 12. Desktop Application (desktop_app.py)

Create a standalone desktop application wrapper that:

**Purpose**: Provides a native desktop experience without requiring a web browser

**Key Features**:
- Uses pywebview to create a native application window
- Runs Flask server in a background daemon thread
- Smart startup detection - waits for Flask to be ready before showing window
- Window configuration:
  - Title: "UFS Maritime Notices Tracker"
  - Size: 1400x900 (resizable)
  - Minimum size: 800x600
  - URL: http://127.0.0.1:5000
  - No confirm on close

**Implementation Requirements**:
```python
import webview
import threading
import urllib.request
import urllib.error
from app import app as flask_app, init_db

def start_flask():
    """Run Flask in background thread"""
    init_db()
    flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def wait_for_flask(max_attempts=30, delay=0.5):
    """Wait for Flask to be ready by polling the endpoint"""
    for i in range(max_attempts):
        try:
            response = urllib.request.urlopen('http://127.0.0.1:5000', timeout=1)
            if response.status == 200:
                return True
        except:
            time.sleep(delay)
    return False

def main():
    # Start Flask thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask
    if not wait_for_flask():
        print("ERROR: Could not start Flask server")
        sys.exit(1)
    
    # Create and start webview window
    window = webview.create_window(
        title='UFS Maritime Notices Tracker',
        url='http://127.0.0.1:5000',
        width=1400,
        height=900,
        resizable=True,
        min_size=(800, 600)
    )
    webview.start(debug=False)
```

### 13. Build System

#### Two Executable Variants:

**1. Desktop Application (Recommended)**:
- File: `UFS-Tracker.exe` (Windows) or `UFS-Tracker` (Linux/Mac)
- Built from: `desktop_app.py`
- PyInstaller flags: `--onefile --noconsole`
- Opens in native desktop window via pywebview
- No console window, no browser needed

**2. Console/Browser Application**:
- File: `UFS-Tracker-Console.exe` (Windows)
- Built from: `app.py`
- PyInstaller flags: `--onefile --console`
- Shows console window, opens in web browser
- Useful for debugging

#### Windows Build Command (Desktop):
```bash
pyinstaller --name=UFS-Tracker --onefile --noconsole \
  --add-data "templates;templates" \
  --hidden-import=flask --hidden-import=requests \
  --hidden-import=bs4 --hidden-import=sqlite3 \
  --hidden-import=webview --collect-all=webview \
  desktop_app.py
```

#### Windows Build Command (Console):
```bash
pyinstaller --name=UFS-Tracker-Console --onefile --console \
  --add-data "templates;templates" \
  --hidden-import=flask --hidden-import=requests \
  --hidden-import=bs4 --hidden-import=sqlite3 \
  app.py
```

### 14. Branding Elements

All pages must include:

**Navigation Bar**:
- Three main tabs: Hem, Visa notiser, Statistik (width: 130px each, centered)
- About button (right-aligned with `margin-left: auto`)
  - GitHub Octocat icon (SVG)
  - "About" text
  - External link arrow icon
  - Links to: https://github.com/kristianwiklund/ufs_tracker
  - Opens in new tab with `target="_blank" rel="noopener noreferrer"`
  - Semi-transparent background (rgba(255, 255, 255, 0.1))

**Footer** (on all pages):
- Dark background (#2c3e50)
- Centered content (max-width: 1400px)
- Line 1: `© 2026 Kristian Wiklund` (link to https://github.com/kristianwiklund)
- Line 2: `Licensed under MIT License | View on GitHub`
- MIT License link: https://github.com/kristianwiklund/ufs_tracker/blob/main/LICENSE
- GitHub repo link: https://github.com/kristianwiklund/ufs_tracker
- Links styled in brand color (#667eea)

### 15. Testing Checklist

After recreation, verify:
- [ ] Web mode: `python app.py` works and opens in browser
- [ ] Desktop mode: `python desktop_app.py` opens native window
- [ ] Search page loads all charts from UFS website
- [ ] Search for "Bsp Stockholm N 2024" finds ~70+ notices
- [ ] Search for "sjökort 111" works correctly (uses ChartNumbers parameter)
- [ ] Notice numbers are correct (e.g., 19811, not 2024)
- [ ] Clicking notice number/title opens UFS detail page
- [ ] Notices page shows dropdown with only searched charts
- [ ] Checkboxes disabled when no chart selected
- [ ] Can mark notices as implemented per chart
- [ ] Same notice can have different status for different charts
- [ ] Statistics page shows per-chart breakdown with progress bars
- [ ] All three pages have same width (1400px)
- [ ] About button appears in navigation (right-aligned with GitHub icon)
- [ ] Footer appears on all pages with copyright and GitHub links
- [ ] Debug mode works with --debug flag
- [ ] Windows builds: Both Desktop and Console executables work
- [ ] GitHub Actions builds complete successfully
- [ ] Chart mappings cache works (1 hour expiration)
- [ ] Max 500 row safety limit prevents hangs

---

**END OF RECREATION PROMPT**
