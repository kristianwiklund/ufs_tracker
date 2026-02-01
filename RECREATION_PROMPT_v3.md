# UFS Maritime Notices Tracker — Complete Recreation Prompt v3.0

**Version**: 3.0  
**Date**: 2026-02-01  
**Status**: Production — Onefile builds, persistent DB, three-tier notice-type classification

---

## Changelog from v2.0

- ✅ Modular architecture: `models/`, `services/`, `utils/` packages
- ✅ Three-tier notice-type classification (suffix → detail page → heuristic)
- ✅ `extract_notice_suffix()` reads `(T)`/`(P)` from visible table-cell text
- ✅ `fetch_notice_class_type()` fetches each detail page and parses `Class/type` field
- ✅ Notice-type badges (🟢 permanent, 🔴 T temporary, 🟡 P preliminary) with expiry awareness
- ✅ Dedicated Documentation tab (`/help`) with correction workflows and ink-note guidelines
- ✅ Database moved to persistent OS-native location (survives onefile updates)
- ✅ Legacy database auto-migration on first run after upgrade
- ✅ PyInstaller onefile mode for both Desktop and Console builds
- ✅ GitHub Actions workflow updated for single-file packaging
- ✅ `chart_editions` table added to schema
- ✅ `priority` and `is_voyage_chart` columns added to `implementation_status`

---

## 1. Project Overview

A Python Flask web application (with optional pywebview desktop GUI) that scrapes, stores, and tracks maritime notices (*Underrättelser för Sjöfarande*) from the Swedish Maritime Administration's UFS database at `https://ufs.sjofartsverket.se`.

Two run modes:
1. **Console/Browser** — `python app.py` → Flask on `127.0.0.1:5000`, open in browser
2. **Desktop GUI** — `python desktop_app.py` → native window via pywebview

---

## 2. Directory Layout

```
ufs-tracker/
├── app.py                          # Flask app, routes, DB helpers
├── desktop_app.py                  # pywebview desktop wrapper
├── requirements.txt
├── UFS-Tracker.spec                # PyInstaller spec — Console (onefile)
├── UFS-Tracker-Desktop.spec        # PyInstaller spec — Desktop (onefile)
├── .github/workflows/
│   └── build-windows.yml           # GitHub Actions CI
├── models/
│   ├── __init__.py                 # (empty)
│   └── database.py                 # DB path resolution, schema, migrations
├── services/
│   ├── __init__.py                 # (empty)
│   └── scraper.py                  # UFS scraping + notice-type classification
├── utils/
│   ├── __init__.py                 # (empty)
│   └── chart_parser.py             # Chart-ref parsing, expiry extraction
├── templates/
│   ├── base.html                   # Shared layout shell
│   ├── index.html                  # Search page
│   ├── notices.html                # Notice list
│   ├── statistics.html             # Stats overview
│   ├── help.html                   # Documentation / correction guide
│   └── components/
│       ├── header.html
│       ├── navigation.html         # Nav tabs + GitHub About link
│       ├── footer.html             # © + MIT + GitHub links
│       └── notice_badge.html       # Jinja macro: type badge per notice
└── static/
    ├── css/
    │   └── main.css
    └── js/
        └── common.js               # Shared utilities + chart-link logic
```

---

## 3. Technology Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.11, Flask 3.0 |
| Database | SQLite (via `sqlite3`) |
| Scraping | `requests` 2.31 + `beautifulsoup4` 4.12 |
| Frontend | Vanilla HTML/CSS/JS — no external libs |
| Desktop | `pywebview ≥ 5.0` |
| Packaging | PyInstaller (onefile mode) |

`requirements.txt`:
```
Flask==3.0.0
requests==2.31.0
beautifulsoup4==4.12.2
pywebview>=5.0.0
```

---

## 4. Database (`models/database.py`)

### 4.1 Persistent Path Resolution

The database must survive PyInstaller onefile rebuilds.  It is stored in the OS-native application-data directory, **not** next to the executable.

```python
def _get_app_data_dir():
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    elif sys.platform == 'darwin':
        base = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    else:                                           # Linux / Unix
        base = os.environ.get('XDG_DATA_HOME',
               os.path.join(os.path.expanduser('~'), '.local', 'share'))
    path = os.path.join(base, 'UFS-Tracker')
    os.makedirs(path, exist_ok=True)
    return path
```

Resulting paths:
| OS | Path |
|---|---|
| Windows | `%APPDATA%\UFS-Tracker\ufs_notices.db` |
| Linux | `~/.local/share/UFS-Tracker/ufs_notices.db` |
| macOS | `~/Library/Application Support/UFS-Tracker/ufs_notices.db` |

### 4.2 Legacy Migration

On first run after upgrading from a one-dir build, `_migrate_legacy_db()` checks for `ufs_notices.db` next to the executable and moves it to the persistent location so no data is lost.  The move only happens when the target does not already exist.

```python
DATABASE_PATH = os.path.join(_get_app_data_dir(), 'ufs_notices.db')
_migrate_legacy_db(DATABASE_PATH)   # runs once at import time
```

### 4.3 Schema

```sql
CREATE TABLE notices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_number   TEXT,
    title           TEXT,
    affected_charts TEXT,
    sjokort_nummer  TEXT,
    batsportkort    TEXT,
    published_date  TEXT,
    area            TEXT,
    content         TEXT,
    url             TEXT,
    scraped_date    TEXT,
    notice_type     TEXT,          -- 'permanent' | 'temporary' | 'preliminary'
    expiry_date     TEXT,          -- ISO date, only for temporary notices
    superseded_by   INTEGER,
    is_cancelled    BOOLEAN DEFAULT 0
);

CREATE TABLE implementation_status (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_id       INTEGER REFERENCES notices(id),
    chart_identifier TEXT,
    implemented     BOOLEAN DEFAULT 0,
    implemented_date TEXT,
    notes           TEXT,
    priority        INTEGER DEFAULT 5,
    is_voyage_chart BOOLEAN DEFAULT 0,
    UNIQUE(notice_id, chart_identifier)
);

CREATE TABLE search_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    search_term     TEXT,
    search_type     TEXT,
    search_date     TEXT,
    results_count   INTEGER
);

CREATE TABLE chart_editions (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    chart_identifier        TEXT NOT NULL,
    edition_number          TEXT,
    edition_date            TEXT,
    corrected_up_to_notice  INTEGER,
    last_updated            TEXT,
    UNIQUE(chart_identifier)
);
```

Indexes created on: `notices.notice_number`, `notices.published_date`, `notices.scraped_date`, `notices.notice_type`, `implementation_status.chart_identifier`, `implementation_status.implemented`, `implementation_status.priority`.

---

## 5. Scraper (`services/scraper.py`)

### 5.1 Chart-Mapping Cache

The UFS search page (`/Notice/Search`) contains two `<select>` elements:
- `#SearchFormModel_ChartNumbers` — sjökort
- `#SearchFormModel_SmallCraftChart` — båtsportkort

These are scraped once per hour (module-level `CHART_MAPPINGS_CACHE` dict with a timestamp).  The cache falls back to stale data on network errors.

### 5.2 Main Scrape Flow (`scrape_ufs_notices`)

1. Resolve chart name → internal ID via cached mappings.
2. GET `https://ufs.sjofartsverket.se/Notice/Search/` with params:
   - `SearchFormModel.ChartNumbers` or `SearchFormModel.SmallCraftChart`
   - `SearchFormModel.SearchTimePeriod=0` (all time)
3. Locate the correct table (heading "Notiser för gällande sjökort" → next `<table>`; fall back to caption, id, class).
4. Parse each `<tr>` via `parse_notice_row()`.
5. **Classify** each notice (see §5.3).
6. If the notice is temporary, run `extract_expiry_date()` on title + content.
7. Return list of notice dicts (or `{'error': …}` on failure).

Safety limit: 500 rows max.

### 5.3 Three-Tier Notice-Type Classification

This is the most important scraping logic.  UFS does **not** encode the type in the `href`; the href only contains a bare numeric ID (e.g., `notice=19818`).  The classification pipeline runs in priority order and stops at the first match:

#### Tier 1 — Visible suffix in table cell (`extract_notice_suffix`)

The rendered page shows the notice number with an optional parenthesised suffix, e.g. `19818(T)`.  A regex scans every `<td>` in the row:

```python
re.search(r'\d{4,6}\s*\(([TP])\)', cell_text)
```

Returns `'T'`, `'P'`, or `None`.  This is the fastest path — no extra HTTP requests.

#### Tier 2 — Detail-page `Class/type` field (`fetch_notice_class_type`)

If no suffix was found in the table, the scraper fetches the individual notice detail page:

```
https://ufs.sjofartsverket.se/en/Current/NoticeDetails?notice=XXXXX&from=search
```

The authoritative type is in an `<h6>` element, in either English or Swedish:

| Language | Label | Temporary value | Preliminary value |
|---|---|---|---|
| English | `Class/type:` | starts with `Temporary` | starts with `Preliminary` |
| Swedish | `Typ av notis:` | starts with `Temporär` | starts with `Preliminär` |

Anything else → `'permanent'`.  Returns `None` on HTTP error or missing field (triggers Tier 3).

#### Tier 3 — Number-suffix heuristic (`parse_notice_type` in `chart_parser.py`)

Legacy fallback.  Checks whether `notice_number` ends with `T` or `P`.  In practice this almost never fires because the notice_number stored is always the bare numeric ID extracted from the href.  It exists as a safety net.

#### Classification result

After classification, each notice dict gets three keys:
- `notice_type` — `'permanent'`, `'temporary'`, or `'preliminary'`
- `is_temporary` — boolean
- `is_preliminary` — boolean

The internal `_suffix` key (used only during classification) is popped before the notice is appended to the results list.

### 5.4 Notice-Number Extraction (`extract_notice_number`)

Priority order:
1. Find any `<a>` in the row whose `href` matches `notice=(\d+)` — return that number.
2. Scan all `<td>` texts for a 4–6 digit number in the range 10 000–25 000.
3. Return empty string (never drop the row).

---

## 6. Chart Parser (`utils/chart_parser.py`)

| Function | Purpose |
|---|---|
| `parse_notice_type(notice_number)` | Heuristic: trailing `T`/`P` on the string → type dict |
| `extract_chart_identifier(chart_ref)` | Strip page numbers; split concatenated `111Bsp …` refs |
| `split_concatenated_charts(chart_ref)` | Return list of `(display, identifier)` tuples |
| `parse_page_numbers(chart_ref)` | Extract `/s25, s47` page refs |
| `extract_expiry_date(title, content)` | Regex for ISO date or Swedish `DD/MM YYYY` in text |
| `get_chart_display_name(id, type)` | Format for UI display |

---

## 7. Flask Application (`app.py`)

### 7.1 Startup

```
python app.py [--debug] [--port N] [--host H]
```

On start: `init_db()` → `migrate_add_notice_types()` → `app.run(...)`.

`datetime.now` is registered as a Jinja2 global so templates can compare dates.

### 7.2 Routes

| Method | Path | Description |
|---|---|---|
| GET | `/` | Search page |
| GET | `/get_available_charts` | JSON list of all charts from UFS |
| GET | `/get_tracked_charts` | JSON list of chart_identifiers in `implementation_status` |
| POST | `/search` | Scrape + save; returns `{success, total_found, saved, message}` |
| GET | `/notices` | Render notice list for a chart (`?chart_identifier=…&show_implemented=0\|1`) |
| POST | `/update_status/<id>` | Toggle implemented + notes for a notice-chart pair |
| GET | `/statistics` | Per-chart stats with progress bars |
| GET | `/help` | Documentation and correction-workflow guide |

### 7.3 `save_notices_to_db`

- Deduplicates on `notice_number` (SELECT before INSERT).
- Stores `notice_type` and `expiry_date` from the scraper output.
- Creates an `implementation_status` row (`INSERT OR IGNORE`) for the searched chart.

---

## 8. Desktop Wrapper (`desktop_app.py`)

Starts Flask in a daemon thread, polls `http://127.0.0.1:5000` until ready (up to 15 s), then opens a pywebview window (1400×900, min 800×600).

---

## 9. Templates

### 9.1 `base.html`

Skeleton: `<head>` with `main.css`, `<body>` with header → navigation → `.content` block → footer, then `common.js` and any page-specific JS.

### 9.2 `components/notice_badge.html`

Included inside each notice card.  Reads `notice.notice_type` and `notice.expiry_date`:

- **Temporary + expiry in the past** → grey `badge-expired` with strikethrough, label "🔴 T (Utgången)"
- **Temporary + no expiry or future** → red `badge-temporary`, label "🔴 T"
- **Preliminary** → amber `badge-preliminary`, label "🟡 P"
- **Permanent** (default) → green `badge-permanent`, label "🟢"

Uses the `now()` Jinja global registered in `app.py` for date comparison.

### 9.3 `notices.html`

- Dropdown populated from `/get_tracked_charts`.
- "Visa implementerade" checkbox auto-reloads the page.
- Each notice card includes the badge, clickable affected-charts (blue if tracked, grey if not), and an implementation checkbox + notes field.

### 9.4 `help.html`

Four sections:
1. **How to use** — step-by-step search and tracking workflows.
2. **Notice types** — three type-legend cards (permanent/temporary/preliminary) with ink and erasure rules.
3. **How to apply corrections** — numbered workflow steps (receive → check → apply → note → document); extra steps for T and P notices.
4. **Quick-reference table** — type, badge, tool, erasure, priority.
5. **Sources** — links to UFS, Sjöfartsverket, UKHO, IMO, IALA, GitHub.

---

## 10. Static Assets

### 10.1 `css/main.css`

Key design tokens:
- Body background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Container: white, max-width 1400 px, `border-radius 10px`, heavy box-shadow
- Header/nav: `#2c3e50` / `#34495e`
- Active nav tab: `#667eea`
- Badge colours: permanent `#27ae60`, temporary `#e74c3c`, preliminary `#f39c12`, expired `#95a5a6`
- Notice cards: left-border accent (`#667eea`; green when implemented), hover lifts 2 px
- Responsive breakpoint at 768 px

### 10.2 `js/common.js`

Shared utilities loaded on every page:

| Function | Role |
|---|---|
| `loadTrackedCharts()` | Fetch `/get_tracked_charts` → global array |
| `navigateToChart(id)` | Reload notices page for a chart |
| `processAffectedChartsHTML(text, tracked)` | Parse affected-charts string; return HTML with clickable links for tracked charts |
| `extractChartIdentifier(ref)` | JS mirror of the Python function |
| `createChartElementHTML(display, id, tracked)` | `<a class="chart-link">` if tracked, else `<span class="chart-not-tracked">` |
| `updateImplementationStatus(id, impl, notes, chart)` | POST to `/update_status/<id>` |
| `getNoticeTypeBadge(type, expiry)` | Return badge HTML (used if badges need to be created dynamically) |
| `showAlert(msg, type)` | Slide-in toast notification |

---

## 11. PyInstaller Specs

Both specs use **onefile** mode (no `COLLECT` block; all binaries/datas passed directly to `EXE`).

`bootloader_ignore_signals=True` on **both** — critical for the noconsole Desktop build on Windows (prevents the app from hanging on signal delivery before the GUI thread starts).

The Desktop spec additionally collects all webview data/binaries/hiddenimports via `collect_all('webview')` and passes them into `Analysis` *before* it runs (avoids the 2-tuple vs 3-tuple TOC crash).

---

## 12. GitHub Actions (`build-windows.yml`)

1. Checkout → Python 3.11 → `pip install -r requirements.txt` + `pyinstaller`
2. `pyinstaller UFS-Tracker.spec` (Console)
3. `pyinstaller UFS-Tracker-Desktop.spec` (Desktop)
4. Package step: both are now single `.exe` files at `dist/`; copied flat into `UFS-Tracker-Windows/`. `.bat` launchers reference them by name directly.
5. Upload artifact.
6. On tag `v*`: zip → GitHub Release.

---

## 13. Important Implementation Notes

- **Notice numbers in the database are always bare numeric IDs** (extracted from the `href`).  The `(T)`/`(P)` suffix only appears in the visible cell text and is consumed by `extract_notice_suffix()` during scraping — it is never stored.
- **Tier 2 (detail-page fetch) is expensive** — one HTTP request per notice that lacks a visible suffix.  In practice most temporary/preliminary notices do show the suffix in the table, so Tier 2 fires infrequently.
- **The `app.config['DATABASE']` key was removed** — nothing read it.  All code uses `DATABASE_PATH` from `models.database`.
- **`backup_database()`** writes relative to CWD by default; callers should pass an absolute path if running as a packaged exe.
- **Chart mappings cache** is module-level in `scraper.py`; in onefile mode the module is reimported each launch so the cache starts cold.  The 1-hour TTL matters only for long-running console sessions.

---

## 14. Testing Checklist

- [ ] `python app.py` → browser at `http://127.0.0.1:5000`
- [ ] `python desktop_app.py` → native 1400×900 window
- [ ] Search dropdown loads all charts from UFS
- [ ] Search for sjökort 6141 → notices appear, badges correct
- [ ] A known temporary notice (e.g. 19818) shows 🔴 T badge
- [ ] A known permanent notice shows 🟢 badge
- [ ] Clicking notice # opens UFS detail page in new tab
- [ ] Affected-chart links: tracked charts are blue+clickable, untracked are grey
- [ ] Per-chart checkbox toggle works independently
- [ ] Statistics page shows correct per-chart progress
- [ ] Help/Documentation tab renders all sections
- [ ] `--debug` flag enables scraper console output
- [ ] PyInstaller Desktop build: single exe, no console window, app starts
- [ ] PyInstaller Console build: single exe, console window, browser opens
- [ ] After build, database is created in `%APPDATA%\UFS-Tracker\` (Windows)
- [ ] Legacy DB next to exe is auto-migrated on first run
- [ ] GitHub Actions workflow completes and produces downloadable zip

---

*END OF RECREATION PROMPT v3.0*
