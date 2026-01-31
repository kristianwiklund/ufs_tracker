# UFS Maritime Notices Tracker - Complete Package

**Version**: 2.0  
**Date**: 2026-01-29  
**Author**: Kristian Wiklund  
**License**: MIT

---

## 📦 Package Contents

This package contains the complete UFS Tracker application with all recent improvements:

- ✅ Modular architecture (Phase 1 refactoring complete)
- ✅ Notice type classification (Permanent/Temporary/Preliminary)
- ✅ Visual badges for notice types
- ✅ Clickable affected charts
- ✅ Desktop application support
- ✅ External CSS/JS for maintainability
- ✅ Component-based templates

---

## 🚀 Quick Start

### Option 1: Web Application

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python app.py

# 3. Open browser to http://127.0.0.1:5000
```

### Option 2: Desktop Application (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run desktop app
python desktop_app.py
```

The application opens in a native window (no browser needed).

### Option 3: Use Startup Script

```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

---

## 📁 Directory Structure

```
ufs-tracker/
├── app.py                      # Main Flask application (300 lines)
├── desktop_app.py              # Desktop GUI wrapper
├── requirements.txt            # Python dependencies
├── start.sh                    # Startup script (Linux/Mac)
│
├── models/                     # Database layer
│   ├── __init__.py
│   └── database.py            # DB connection, schema, migrations
│
├── services/                   # Business logic
│   ├── __init__.py
│   └── scraper.py             # UFS scraping service
│
├── utils/                      # Utilities
│   ├── __init__.py
│   └── chart_parser.py        # Chart parsing functions
│
├── static/                     # Static assets
│   ├── css/
│   │   └── main.css           # Shared styles (420 lines)
│   └── js/
│       └── common.js          # Shared JavaScript (250 lines)
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── index.html             # Search page
│   ├── notices.html           # Notice list
│   ├── statistics.html        # Statistics
│   └── components/            # Reusable components
│       ├── header.html
│       ├── navigation.html
│       ├── footer.html
│       └── notice_badge.html
│
└── Documentation/
    ├── README.md              # Swedish documentation
    ├── USER_GUIDE.md          # Swedish user guide
    ├── BUILD.md               # Build instructions
    ├── QUICKSTART.md          # Quick start guide
    ├── RECREATION_PROMPT_v2.md # Complete specification
    ├── REVISED_PROPOSAL_v2.md  # Future features roadmap
    └── IMPLEMENTATION_SUMMARY.md # What was implemented
```

---

## 🔧 Requirements

- **Python**: 3.8 or later
- **Operating System**: Windows, Linux, or macOS
- **Dependencies**: Listed in requirements.txt
  - Flask
  - Requests
  - BeautifulSoup4
  - pywebview (for desktop mode)

---

## 📖 Documentation

### Essential Reading

1. **README.md** - Swedish documentation, overview
2. **USER_GUIDE.md** - Swedish user guide, how to use
3. **QUICKSTART.md** - Get started quickly

### For Developers

1. **RECREATION_PROMPT_v2.md** - Complete technical specification
2. **IMPLEMENTATION_SUMMARY.md** - What was implemented in Phase 1 & 2
3. **REVISED_PROPOSAL_v2.md** - Future roadmap and features
4. **BUILD.md** - How to build executables

### For Advanced Users

1. **ANALYSIS_AND_OPTIMIZATION.md** - Original analysis
2. **RELEASING.md** - How to create releases

---

## 🎯 Features

### Current Features (v2.0)

✅ **Notice Type Classification**
- Automatic detection of Permanent, Temporary (T), and Preliminary (P) notices
- Visual badges: 🟢 Permanent | 🔴 T | 🟡 P
- Expiry date extraction for temporary notices

✅ **Clickable Affected Charts**
- Parse "Berörda kort" field
- Clickable links for tracked charts
- Smart handling of concatenated charts (e.g., "111Bsp Mälaren 2024")

✅ **Per-Chart Tracking**
- Track implementation status separately for each chart
- Add notes per chart
- Statistics per chart

✅ **Modular Architecture**
- Clean separation of concerns
- Easy to maintain and extend
- 70% less code duplication

✅ **Desktop & Web Modes**
- Desktop app with native window (pywebview)
- Web app for browser access
- Both use same backend

### Planned Features (Next Releases)

See **REVISED_PROPOSAL_v2.md** for detailed roadmap:

**Immediate** (v2.1):
- Correction log system (NP133A style)
- "Corrected up to" tracking
- User identification
- Chart edition warnings

**Short-term** (v2.2):
- Bulk operations
- PDF/CSV export
- Priority/voyage chart system
- Verification workflow

**Medium-term** (v2.3+):
- Advanced filtering
- New edition detection
- Multi-user authentication
- Cloud sync

---

## 🏗️ Building Executables

### Windows

```bash
# Build both Desktop and Console versions
build-windows.bat
```

Creates:
- `UFS-Tracker.exe` - Desktop app (recommended)
- `UFS-Tracker-Console.exe` - Console/browser mode

### Linux

```bash
# Make executable and run
chmod +x build-linux.sh
./build-linux.sh
```

---

## 🧪 Testing

### Manual Testing

1. Run the application
2. Search for a chart (e.g., "Bsp Stockholm N 2024")
3. Verify notices are fetched
4. Check notice type badges display correctly
5. Mark a notice as implemented
6. Check statistics page

### With Demo Data

```bash
# Initialize with demo data
python init_demo.py
```

---

## 🔍 Troubleshooting

### Application won't start

**Check Python version**:
```bash
python --version  # Should be 3.8+
```

**Install dependencies**:
```bash
pip install -r requirements.txt
```

### Desktop app shows black screen

**Check pywebview installation**:
```bash
pip install pywebview --upgrade
```

### Database errors

**Reinitialize database**:
```bash
# Backup first!
cp ufs_notices.db ufs_notices_backup.db

# Delete and restart
rm ufs_notices.db
python app.py
```

### Scraper not finding notices

**Check network connection** - UFS website must be accessible

**Try debug mode**:
```bash
python app.py --debug
```

---

## 🤝 Contributing

This is an open-source project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📜 License

MIT License - See LICENSE file for details

Copyright © 2026 Kristian Wiklund

---

## 🔗 Links

- **GitHub**: https://github.com/kristianwiklund/ufs_tracker
- **Issues**: https://github.com/kristianwiklund/ufs_tracker/issues
- **UFS Website**: https://ufs.sjofartsverket.se

---

## 💡 Tips

### For Best Performance

1. Use desktop mode for best experience
2. Search for specific charts (not all at once)
3. Regularly check for new notices
4. Keep database backed up

### For Multiple Users

1. Use web mode on a shared server
2. Or share desktop app via network drive
3. Database is SQLite (single file, easy to share)

### For Chart Management

1. Track chart editions in statistics
2. Use notes field for important info
3. Export data regularly
4. Plan for ~6 corrections per chart before replacement

---

## 🆘 Support

For help:

1. Check **USER_GUIDE.md**
2. Check **QUICKSTART.md**
3. Review **REVISED_PROPOSAL_v2.md** for planned features
4. Open an issue on GitHub

---

## 🎓 Learning More

### About Nautical Chart Corrections

- UKHO Admiralty Publications (NP294, NP133A)
- IALA recommendations
- IMO guidelines

### About This Application

- **RECREATION_PROMPT_v2.md** - Complete technical specification
- **IMPLEMENTATION_SUMMARY.md** - Development history
- **REVISED_PROPOSAL_v2.md** - Future plans

---

**Last Updated**: 2026-01-29  
**Package Version**: 2.0  
**Status**: Production Ready (Base Features)

Enjoy using UFS Maritime Notices Tracker! ⚓📊
